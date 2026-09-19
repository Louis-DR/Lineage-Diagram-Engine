import importlib
import sys

import pytest

import politics_lib
from politics_lib import load_france
from politics_lib.date import Date
from lineage_diagram.paths import MembershipEventType


def test_modular_political_dataset_imports():
  assert not any(name.startswith("politics_lib.france.") for name in sys.modules)
  system = load_france()
  assert len(system.political_parties) == 76
  assert len(system.political_federations) == 2


def test_modular_loader_assigns_stable_ids_and_resolves_historical_aliases():
  system = load_france()

  assert len(system.entities_by_id) == 78
  assert len(set(system.entities_by_id)) == 78
  assert system.aliases["democratie_liberale"] == system.aliases["republicains_independants"]
  assert system.aliases["les_republicains"] == system.aliases["union_pour_un_mouvement_populaire"]
  assert system.aliases["rassemblement_national"] == system.aliases["front_national"]


def test_modular_loader_rebuilds_without_accumulating_state():
  first = load_france()
  first_party = first.entities_by_id[first.aliases["parti_radical"]]
  second = load_france()
  second_party = second.entities_by_id[second.aliases["parti_radical"]]

  assert first_party is not second_party
  assert len(second.political_parties) == 76
  assert len(second.entities_by_id) == 78


def test_dissolution_closes_active_memberships():
  system = load_france()
  independents = system.entities_by_id[system.aliases["republicains_independants"]]

  assert independents.dissolution_date is not None
  assert all(membership["to"] is not None for membership in independents.federation_memberships)


def test_inside_entity_membership_starts_at_the_party_creation_date():
  system = load_france()
  convention = system.entities_by_id[system.aliases["la_convention"]]
  federation = system.entities_by_id[system.aliases["la_convention_federation"]]
  membership = next(
    membership for membership in convention.federation_memberships
    if membership["federation"] is federation
  )

  assert membership["from"] == Date(2023, 2, 1)
  assert convention.inside_entity is federation


def test_political_transfer_releases_the_previous_assembly_slot(monkeypatch):
  import render_political_diagram as renderer

  monkeypatch.setattr(renderer.PoliticalDiagram, "generate", lambda self, path: None)
  diagram = renderer.main()
  udf_start_x = renderer.date_to_x(Date(1978, 2, 1))
  ump_join_from_x = renderer.date_to_x(Date(2002, 4, 23)) - 12
  udf_bundle = next(bundle for bundle in diagram._bundles if bundle.start_x == udf_start_x)
  lineage = next(
    lineage for lineage in diagram._lineages
    if any(
      event.type == MembershipEventType.JOIN
      and event.assembly is udf_bundle
      for event in lineage.membership_events
    )
    and any(
      event.type == MembershipEventType.JOIN
      and event.assembly is not udf_bundle
      and event.from_x == ump_join_from_x
      for event in lineage.membership_events
    )
  )
  orbit_join = next(
    event for event in lineage.membership_events
    if event.type == MembershipEventType.JOIN
    and event.assembly is not udf_bundle
    and event.from_x == ump_join_from_x
  )

  assert lineage not in [membership.lineage for membership in udf_bundle.get_memberships_at(orbit_join.to_x)]
  assert lineage.state_at(orbit_join.to_x + 1).assembly_id == orbit_join.assembly.id


@pytest.mark.xfail(raises=NameError, reason="The monolithic database references an entity before definition")
def test_legacy_political_database_imports():
  try:
    importlib.import_module("politics_database")
  except NameError as error:
    assert "centre_national_des_independants_et_paysans" in str(error)
    raise
