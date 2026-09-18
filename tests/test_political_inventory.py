from pathlib import Path

from tools.political_inventory import inventory


ROOT = Path(__file__).resolve().parents[1]


def test_inventory_does_not_import_broken_dataset():
  data = inventory(ROOT)
  assert data["modular"]["entity_counts"]["PoliticalParty"] >= 70
  assert data["modular"]["entity_counts"]["PoliticalFederation"] == 2
  assert data["modular"]["entity_counts"].get("PoliticalAlliance", 0) == 0
  assert data["modular"]["constructor_relationship_counts"]["merge_from"] > 0
  assert data["modular"]["constructor_relationship_counts"]["secede_from"] > 0


def test_inventory_finds_cross_module_cycle():
  data = inventory(ROOT)
  cycle_modules = {module for cycle in data["import_cycles"] for module in cycle}
  assert {"radicalisme", "centralisme", "gaullisme"} <= cycle_modules


def test_inventory_records_invalid_generated_python():
  data = inventory(ROOT)
  assert data["generated_python"]["parse_error"]["kind"] == "syntax-error"


def test_inventory_preserves_relationship_keyword_arguments():
  data = inventory(ROOT)
  assert any("visual_width=" in signature for signature in data["modular"]["relationship_signatures"])


def test_modular_and_monolithic_sources_are_not_silently_equivalent():
  data = inventory(ROOT)
  comparison = data["comparison"]
  assert comparison["only_in_modular"] or comparison["only_in_monolith"]
  assert comparison["relationships_only_in_modular"] or comparison["relationships_only_in_monolith"]
