"""Deterministically load the provisional French source in two passes.

The source files remain historical authoring input during migration.  This
loader records their declarations without importing peer modules, then resolves
all cross-module references after every entity exists.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import constants
from .base import PoliticalAlliance, PoliticalFederation, PoliticalParty, PoliticalSystem
from .date import Date


FRANCE_MODULES = (
  "political_system",
  "anarchisme",
  "trotskisme",
  "communisme",
  "socialisme",
  "insoumission",
  "ecosocialiste",
  "radicalisme",
  "centralisme",
  "gaullisme",
  "agrarisme",
  "nationalisme",
)

ENTITY_TYPES = {
  "PoliticalParty": PoliticalParty,
  "PoliticalFederation": PoliticalFederation,
  "PoliticalAlliance": PoliticalAlliance,
}
TOPOLOGY_METHODS = {"dissolve", "join", "leave", "merge_into", "secede_into"}


class DatasetValidationError(ValueError):
  pass


@dataclass(frozen=True)
class Reference:
  name: str


@dataclass(eq=False)
class EntityDeclaration:
  kind: str
  arguments: tuple[Any, ...]
  keywords: dict[str, Any]
  order: int
  variable: str | None = None
  stable_id: str | None = None


@dataclass(frozen=True)
class MethodCall:
  owner: Any
  method: str
  arguments: tuple[Any, ...]
  keywords: dict[str, Any]
  order: int


@dataclass(eq=False)
class EntityHandle:
  builder: "FranceBuilder"
  declaration: EntityDeclaration

  def __getattr__(self, method: str):
    def record(*arguments, **keywords):
      self.builder.calls.append(MethodCall(self, method, arguments, keywords, self.builder.next_order()))
      return self
    return record


@dataclass
class FranceBuilder:
  declarations: list[EntityDeclaration] = field(default_factory=list)
  calls: list[MethodCall] = field(default_factory=list)
  aliases: dict[str, EntityHandle] = field(default_factory=dict)
  _order: int = 0

  def next_order(self) -> int:
    self._order += 1
    return self._order

  def entity_factory(self, kind: str):
    def create(*arguments, **keywords):
      declaration = EntityDeclaration(kind, arguments, keywords, self.next_order())
      self.declarations.append(declaration)
      return EntityHandle(self, declaration)
    return create

  def system(self):
    builder = self

    class SystemHandle:
      def __getattr__(self, method: str):
        def record(*arguments, **keywords):
          builder.calls.append(MethodCall(None, method, arguments, keywords, builder.next_order()))
        return record

    return SystemHandle()


class _RemoveImports(ast.NodeTransformer):
  def visit_Import(self, node):
    return None

  def visit_ImportFrom(self, node):
    return None


def _assigned_names(tree: ast.Module) -> set[str]:
  names = set()
  for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
      names.update(target.id for target in node.targets if isinstance(target, ast.Name))
    elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
      names.add(node.target.id)
  return names


def _entity_assignment_names(tree: ast.Module) -> set[str]:
  names = set()
  for node in ast.walk(tree):
    if not isinstance(node, (ast.Assign, ast.AnnAssign)) or not isinstance(node.value, ast.Call):
      continue
    if isinstance(node.value.func, ast.Name) and node.value.func.id in ENTITY_TYPES:
      targets = node.targets if isinstance(node, ast.Assign) else [node.target]
      names.update(target.id for target in targets if isinstance(target, ast.Name))
  return names


def _source_trees() -> list[tuple[str, Path, ast.Module]]:
  root = Path(__file__).with_name("france")
  trees = []
  for module in FRANCE_MODULES:
    path = root / f"{module}.py"
    trees.append((module, path, ast.parse(path.read_text(encoding="utf-8"), filename=str(path))))
  return trees


def _collect() -> FranceBuilder:
  trees = _source_trees()
  all_names = set().union(*(_assigned_names(tree) for _, _, tree in trees))
  builder = FranceBuilder()
  for _, path, tree in trees:
    namespace = dict(vars(constants))
    namespace.update({
      "Date": Date,
      "PoliticalParty": builder.entity_factory("PoliticalParty"),
      "PoliticalFederation": builder.entity_factory("PoliticalFederation"),
      "PoliticalAlliance": builder.entity_factory("PoliticalAlliance"),
      "PoliticalSystem": builder.system,
    })
    namespace.update({name: builder.aliases.get(name, Reference(name)) for name in all_names})
    executable = _RemoveImports().visit(tree)
    ast.fix_missing_locations(executable)
    exec(compile(executable, str(path), "exec"), namespace)
    for name, value in namespace.items():
      if isinstance(value, EntityHandle):
        builder.aliases[name] = value
    for name in _entity_assignment_names(tree):
      value = namespace.get(name)
      if isinstance(value, EntityHandle) and value.declaration.variable is None:
        value.declaration.variable = name

  counters = {"PoliticalParty": 0, "PoliticalFederation": 0, "PoliticalAlliance": 0}
  prefixes = {"PoliticalParty": "party", "PoliticalFederation": "federation", "PoliticalAlliance": "alliance"}
  for declaration in builder.declarations:
    if declaration.variable is None:
      raise DatasetValidationError("Entity declaration has no source variable")
    counters[declaration.kind] += 1
    declaration.stable_id = f"fr-{prefixes[declaration.kind]}-{counters[declaration.kind]:03d}"
  return builder


def _resolve(value: Any, aliases: dict[str, EntityHandle], entities: dict[EntityDeclaration, Any]):
  if isinstance(value, EntityHandle):
    return entities[value.declaration]
  if isinstance(value, Reference):
    try:
      return entities[aliases[value.name].declaration]
    except KeyError as error:
      raise DatasetValidationError(f"Unresolved political reference: {value.name}") from error
  if isinstance(value, list):
    return [_resolve(item, aliases, entities) for item in value]
  if isinstance(value, tuple):
    return tuple(_resolve(item, aliases, entities) for item in value)
  if isinstance(value, dict):
    return {_resolve(key, aliases, entities): _resolve(item, aliases, entities) for key, item in value.items()}
  return value


def _relationship_date(call: MethodCall, entities: dict[EntityDeclaration, Any]) -> Date:
  if call.method in {"merge_from", "secede_from", "inside_entity", "initial_members"}:
    raise AssertionError("Constructor relationships are normalized separately")
  if not call.arguments:
    raise DatasetValidationError(f"Relationship {call.method} has no date")
  date = _resolve(call.arguments[0], {}, entities)
  if not isinstance(date, Date):
    raise DatasetValidationError(f"Relationship {call.method} has invalid date {date!r}")
  return date


def _close_memberships(system: PoliticalSystem):
  for party in system.political_parties.values():
    if party.dissolution_date is None:
      continue
    for memberships in (party.satellite_memberships, party.federation_memberships, party.alliance_memberships):
      for membership in memberships:
        if membership.get("to") is None:
          membership["to"] = party.dissolution_date


def load_france() -> PoliticalSystem:
  """Build the French dataset without importing data modules or relying on import order."""
  builder = _collect()
  system = PoliticalSystem()
  system.reset()
  entities: dict[EntityDeclaration, Any] = {}

  for declaration in builder.declarations:
    kwargs = dict(declaration.keywords)
    kwargs.pop("merge_from", None)
    kwargs.pop("secede_from", None)
    kwargs.pop("inside_entity", None)
    kwargs.pop("initial_members", None)
    if kwargs["symbol"] in system.political_parties or kwargs["symbol"] in system.political_federations:
      raise DatasetValidationError(f"Duplicate entity symbol: {kwargs['symbol']}")
    entity = ENTITY_TYPES[declaration.kind](*declaration.arguments, **kwargs)
    entity.id = declaration.stable_id
    if entity.id in system.entities_by_id:
      raise DatasetValidationError(f"Duplicate stable ID: {entity.id}")
    entities[declaration] = entity
    system.entities_by_id[entity.id] = entity

  for alias, handle in builder.aliases.items():
    entity = entities.get(handle.declaration)
    if entity is not None:
      system.aliases[alias] = entity.id
  for entity in system.entities_by_id.values():
    system.aliases[entity.symbol] = entity.id

  # System calendars and entity facts must exist before transfer calculations.
  for call in sorted(builder.calls, key=lambda item: item.order):
    if call.owner is None:
      getattr(system, call.method)(*call.arguments, **call.keywords)
    elif call.method not in TOPOLOGY_METHODS:
      entity = entities[call.owner.declaration]
      getattr(entity, call.method)(
        *[_resolve(value, builder.aliases, entities) for value in call.arguments],
        **{name: _resolve(value, builder.aliases, entities) for name, value in call.keywords.items()},
      )

  topology: list[tuple[Date, int, Any]] = []
  for declaration in builder.declarations:
    target = entities[declaration]
    relationships = declaration.keywords
    for source, ratio in _resolve(relationships.get("merge_from", {}), builder.aliases, entities).items() if isinstance(relationships.get("merge_from"), dict) else []:
      topology.append((target.creation_date, declaration.order, ("merge", source, target, float(ratio))))
    for source in _resolve(relationships.get("merge_from", []), builder.aliases, entities) if isinstance(relationships.get("merge_from"), list) else []:
      topology.append((target.creation_date, declaration.order, ("merge", source, target, 1.0)))
    for source, spec in _resolve(relationships.get("secede_from", {}), builder.aliases, entities).items():
      spec = spec if isinstance(spec, dict) else {"ratio": spec}
      topology.append((target.creation_date, declaration.order, ("secede", source, target, spec)))
    host = relationships.get("inside_entity")
    if host is not None:
      topology.append((target.creation_date, declaration.order, (
        "inside", target, _resolve(host, builder.aliases, entities), target.creation_date,
      )))
    for member in _resolve(relationships.get("initial_members", []), builder.aliases, entities):
      topology.append((target.creation_date, declaration.order, ("join", member, target, target.creation_date)))

  for call in builder.calls:
    if call.owner is not None and call.method in TOPOLOGY_METHODS:
      topology.append((_relationship_date(call, entities), call.order, call))

  for _, _, event in sorted(topology, key=lambda item: (item[0], item[1])):
    if isinstance(event, MethodCall):
      owner = entities[event.owner.declaration]
      if event.arguments and event.arguments[0] < owner.creation_date:
        raise DatasetValidationError(
          f"{owner.id} has {event.method} before creation at {event.arguments[0]}"
        )
      getattr(owner, event.method)(
        *[_resolve(value, builder.aliases, entities) for value in event.arguments],
        **{name: _resolve(value, builder.aliases, entities) for name, value in event.keywords.items()},
      )
      continue
    kind, source, target, *payload = event
    if kind == "merge":
      source.merge_into(target.creation_date, target, payload[0])
    elif kind == "secede":
      spec = payload[0]
      source.secede_into(target.creation_date, target, float(spec.get("ratio", 0.0)), spec.get("source_new_position"))
    elif kind == "inside":
      source.inside_entity = target
      source.join(payload[0], target)
    else:
      source.join(payload[0], target)

  _close_memberships(system)
  return system
