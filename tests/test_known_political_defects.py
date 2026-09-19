import importlib
import sys

import pytest

import politics_lib
from politics_lib import load_france


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


@pytest.mark.xfail(raises=NameError, reason="The monolithic database references an entity before definition")
def test_legacy_political_database_imports():
  try:
    importlib.import_module("politics_database")
  except NameError as error:
    assert "centre_national_des_independants_et_paysans" in str(error)
    raise
