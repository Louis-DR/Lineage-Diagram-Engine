import argparse
import ast
import json
from collections import Counter
from pathlib import Path
from typing import Any


ENTITY_TYPES = {"PoliticalParty", "PoliticalFederation", "PoliticalAlliance"}
CONSTRUCTOR_RELATIONSHIPS = {"merge_from", "secede_from", "inside_entity", "initial_members"}
RELATION_METHODS = {
  "dissolve",
  "join",
  "leave",
  "merge_into",
  "secede_into",
  "shift_political_position",
}
RESULT_METHODS = {
  "set_results_presidential_election",
  "set_results_legislative_election",
  "set_results_senatorial_election",
  "set_results_european_election",
}


def _call_name(call: ast.Call) -> str | None:
  if isinstance(call.func, ast.Name):
    return call.func.id
  if isinstance(call.func, ast.Attribute):
    return call.func.attr
  return None


def _literal_keyword(call: ast.Call, name: str):
  for keyword in call.keywords:
    if keyword.arg == name and isinstance(keyword.value, ast.Constant):
      return keyword.value.value
  return None


def _assigned_name(node: ast.AST) -> str | None:
  target = None
  if isinstance(node, ast.Assign) and len(node.targets) == 1:
    target = node.targets[0]
  elif isinstance(node, ast.AnnAssign):
    target = node.target
  return target.id if isinstance(target, ast.Name) else None


def _parse(path: Path) -> tuple[ast.Module | None, dict | None]:
  if not path.exists():
    return None, {"kind": "missing-file", "message": f"Source file not found: {path}"}
  decoding_error = None
  source = None
  for encoding in ("utf-8", "cp1252"):
    try:
      source = path.read_text(encoding=encoding)
      break
    except UnicodeDecodeError as error:
      decoding_error = str(error)
  if source is None:
    return None, {"kind": "decode-error", "message": decoding_error}
  try:
    return ast.parse(source, filename=str(path)), None
  except SyntaxError as error:
    return None, {
      "kind": "syntax-error",
      "line": error.lineno,
      "offset": error.offset,
      "message": error.msg,
    }


def _extract_file(path: Path) -> dict[str, Any]:
  tree, error = _parse(path)
  result = {
    "path": str(path),
    "parse_error": error,
    "entities": [],
    "relationships": [],
    "results": [],
    "imports": [],
  }
  if tree is None:
    return result

  for node in ast.walk(tree):
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
      value = node.value
      if isinstance(value, ast.Call) and _call_name(value) in ENTITY_TYPES:
        result["entities"].append({
          "variable": _assigned_name(node),
          "type": _call_name(value),
          "symbol": _literal_keyword(value, "symbol"),
          "constructor_relationships": {
            keyword.arg: ast.unparse(keyword.value)
            for keyword in value.keywords
            if keyword.arg in CONSTRUCTOR_RELATIONSHIPS
          },
          "line": node.lineno,
        })
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
      method = node.func.attr
      owner = ast.unparse(node.func.value)
      if method in RELATION_METHODS:
        result["relationships"].append({
          "owner": owner,
          "method": method,
          "arguments": [ast.unparse(argument) for argument in node.args],
          "keywords": {
            keyword.arg: ast.unparse(keyword.value)
            for keyword in node.keywords
            if keyword.arg is not None
          },
          "line": node.lineno,
        })
      elif method in RESULT_METHODS:
        result["results"].append({
          "owner": owner,
          "method": method,
          "line": node.lineno,
        })
    elif isinstance(node, ast.ImportFrom):
      result["imports"].append({
        "module": node.module,
        "level": node.level,
        "names": [alias.name for alias in node.names],
        "line": node.lineno,
      })
  return result


def _import_graph(files: list[dict]) -> dict[str, list[str]]:
  modules = {Path(file["path"]).stem for file in files}
  graph = {module: [] for module in sorted(modules)}
  for file in files:
    source = Path(file["path"]).stem
    for imported in file["imports"]:
      module = imported["module"]
      if module:
        target = module.rsplit(".", 1)[-1]
        if target in modules and target != source:
          graph[source].append(target)
  return {module: sorted(set(targets)) for module, targets in graph.items()}


def _cycles(graph: dict[str, list[str]]) -> list[list[str]]:
  cycles = set()
  visiting = []
  visited = set()

  def canonical(cycle: list[str]) -> tuple[str, ...]:
    body = cycle[:-1]
    rotations = [tuple(body[index:] + body[:index]) for index in range(len(body))]
    selected = min(rotations)
    return selected + (selected[0],)

  def visit(module: str):
    if module in visiting:
      start = visiting.index(module)
      cycles.add(canonical(visiting[start:] + [module]))
      return
    if module in visited:
      return
    visiting.append(module)
    for dependency in graph.get(module, []):
      visit(dependency)
    visiting.pop()
    visited.add(module)

  for module in graph:
    visit(module)
  return [list(cycle) for cycle in sorted(cycles)]


def _source_summary(files: list[dict]) -> dict[str, Any]:
  entities = [entity | {"path": file["path"]} for file in files for entity in file["entities"]]
  relationship_signatures = []
  for file in files:
    for relationship in file["relationships"]:
      relationship_signatures.append(
        f"{relationship['owner']}.{relationship['method']}("
        f"{', '.join([*relationship['arguments'], *[f'{key}={value}' for key, value in sorted(relationship['keywords'].items())]])})"
      )
  for entity in entities:
    for relationship, value in entity["constructor_relationships"].items():
      relationship_signatures.append(f"{entity['variable']}:{relationship}={value}")
  symbols = [entity["symbol"] for entity in entities if entity["symbol"] is not None]
  duplicate_symbols = sorted(symbol for symbol, count in Counter(symbols).items() if count > 1)
  counts = Counter(entity["type"] for entity in entities)
  relationship_counts = Counter(
    relationship["method"] for file in files for relationship in file["relationships"]
  )
  constructor_relationship_counts = Counter(
    relationship
    for entity in entities
    for relationship in entity["constructor_relationships"]
  )
  result_counts = Counter(result["method"] for file in files for result in file["results"])
  return {
    "file_count": len(files),
    "parse_errors": [
      {"path": file["path"], "error": file["parse_error"]}
      for file in files
      if file["parse_error"]
    ],
    "entity_counts": dict(sorted(counts.items())),
    "relationship_counts": dict(sorted(relationship_counts.items())),
    "constructor_relationship_counts": dict(sorted(constructor_relationship_counts.items())),
    "result_counts": dict(sorted(result_counts.items())),
    "symbols": sorted(symbols),
    "duplicate_symbols": duplicate_symbols,
    "relationship_signatures": sorted(relationship_signatures),
    "entities": entities,
  }


def inventory(root: Path) -> dict[str, Any]:
  france_dir = root / "politics_lib" / "france"
  modular_files = [_extract_file(path) for path in sorted(france_dir.glob("*.py"))]
  monolith_file = _extract_file(root / "politics_database.py")
  generated_file = _extract_file(root / "generated_political_diagram.py")

  modular = _source_summary(modular_files)
  monolith = _source_summary([monolith_file])
  graph = _import_graph(modular_files)
  modular_symbols = set(modular["symbols"])
  monolith_symbols = set(monolith["symbols"])
  modular_relationships = set(modular["relationship_signatures"])
  monolith_relationships = set(monolith["relationship_signatures"])

  return {
    "root": str(root),
    "modular": modular,
    "monolith": monolith,
    "comparison": {
      "only_in_modular": sorted(modular_symbols - monolith_symbols),
      "only_in_monolith": sorted(monolith_symbols - modular_symbols),
      "shared": len(modular_symbols & monolith_symbols),
      "relationships_only_in_modular": sorted(modular_relationships - monolith_relationships),
      "relationships_only_in_monolith": sorted(monolith_relationships - modular_relationships),
      "shared_relationships": len(modular_relationships & monolith_relationships),
    },
    "import_graph": graph,
    "import_cycles": _cycles(graph),
    "generated_python": {
      "path": generated_file["path"],
      "parse_error": generated_file["parse_error"],
    },
    "files": modular_files,
  }


def _markdown(data: dict[str, Any]) -> str:
  modular = data["modular"]
  monolith = data["monolith"]
  comparison = data["comparison"]

  lines = [
    "# Political Data Inventory",
    "",
    "This report is generated statically with `python -m tools.political_inventory`; it does not import the broken political packages.",
    "",
    "## Sources",
    "",
    f"- Modular files: {modular['file_count']}",
    f"- Modular entities: {sum(modular['entity_counts'].values())}",
    f"- Monolithic entities: {sum(monolith['entity_counts'].values())}",
    f"- Shared symbols: {comparison['shared']}",
    f"- Symbols only in modular data: {len(comparison['only_in_modular'])}",
    f"- Symbols only in monolithic data: {len(comparison['only_in_monolith'])}",
    f"- Shared relationship signatures: {comparison['shared_relationships']}",
    f"- Relationship signatures only in modular data: {len(comparison['relationships_only_in_modular'])}",
    f"- Relationship signatures only in monolithic data: {len(comparison['relationships_only_in_monolith'])}",
    "",
    "## Modular Entities",
    "",
  ]
  for kind, count in modular["entity_counts"].items():
    lines.append(f"- {kind}: {count}")

  lines.extend(["", "## Import Cycles", ""])
  if data["import_cycles"]:
    for cycle in data["import_cycles"]:
      lines.append(f"- `{' -> '.join(cycle)}`")
  else:
    lines.append("- None detected")

  lines.extend(["", "## Divergence", ""])
  lines.append(f"- Only modular: `{', '.join(comparison['only_in_modular']) or 'none'}`")
  lines.append(f"- Only monolithic: `{', '.join(comparison['only_in_monolith']) or 'none'}`")

  lines.extend(["", "## Generated Python", ""])
  error = data["generated_python"]["parse_error"]
  if error:
    lines.append(f"- Parse failure: `{error}`")
  else:
    lines.append("- Parses successfully")

  lines.extend([
    "",
    "## Interpretation",
    "",
    "The modular files are the migration source of truth. The monolith remains a reconciliation input until every divergent symbol and relationship has been classified.",
    "",
  ])
  return "\n".join(lines)


def main() -> int:
  parser = argparse.ArgumentParser(description="Inventory political data without importing it.")
  source_root = Path.cwd() if (Path.cwd() / "politics_lib" / "france").exists() else Path(__file__).resolve().parents[1]
  parser.add_argument("--root", type=Path, default=source_root)
  parser.add_argument("--output", type=Path, default=Path("artifacts/political-inventory.json"))
  parser.add_argument("--markdown", type=Path)
  args = parser.parse_args()

  data = inventory(args.root.resolve())
  args.output.parent.mkdir(parents=True, exist_ok=True)
  args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
  if args.markdown:
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(_markdown(data), encoding="utf-8")

  print(f"Political inventory written to {args.output}")
  print(
    f"Modular entities: {sum(data['modular']['entity_counts'].values())}; "
    f"monolithic entities: {sum(data['monolith']['entity_counts'].values())}; "
    f"import cycles: {len(data['import_cycles'])}."
  )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
