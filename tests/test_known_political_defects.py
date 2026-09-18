import importlib

import pytest


@pytest.mark.xfail(raises=ImportError, reason="The modular political dataset has a circular import")
def test_modular_political_dataset_imports():
  try:
    importlib.import_module("politics_lib")
  except ImportError as error:
    assert "partially initialized module" in str(error)
    raise


@pytest.mark.xfail(raises=NameError, reason="The monolithic database references an entity before definition")
def test_legacy_political_database_imports():
  try:
    importlib.import_module("politics_database")
  except NameError as error:
    assert "centre_national_des_independants_et_paysans" in str(error)
    raise
