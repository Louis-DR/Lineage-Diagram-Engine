import xml.etree.ElementTree as ET

import pytest

from tools.fixture_cases import FIXTURE_BUILDERS
from tools.fixture_cases import EngineFixture
from tools.geometry_diagnostics import diagnose_fixture
from lineage_diagram.bundle import Bundle
from lineage_diagram.diagram import Diagram
from lineage_diagram.lineage import Lineage


@pytest.mark.parametrize("builder", FIXTURE_BUILDERS, ids=lambda builder: builder.__name__)
def test_fixture_renders_valid_svg(builder):
  fixture = builder()
  if fixture.expected_geometry_warning:
    with pytest.warns(RuntimeWarning, match="Unsafe geometry"):
      svg = fixture.diagram.to_svg()
  else:
    svg = fixture.diagram.to_svg()
  root = ET.fromstring(svg)

  assert root.tag.endswith("svg")
  assert root.attrib["viewBox"] == f"0 0 {fixture.diagram.view_width} {fixture.diagram.view_height}"
  assert len(root.findall("{http://www.w3.org/2000/svg}path")) == len(fixture.diagram._lineages)


@pytest.mark.parametrize(
  "builder",
  [
    FIXTURE_BUILDERS[0],
    FIXTURE_BUILDERS[1],
    FIXTURE_BUILDERS[2],
    FIXTURE_BUILDERS[3],
    FIXTURE_BUILDERS[4],
    FIXTURE_BUILDERS[5],
    FIXTURE_BUILDERS[8],
    FIXTURE_BUILDERS[10],
    FIXTURE_BUILDERS[12],
  ],
  ids=lambda builder: builder.__name__,
)
def test_established_fixture_has_no_structural_violation(builder):
  report = diagnose_fixture(builder())
  known_sampling_defects = {"event-boundary-missing"}
  unexpected = [
    violation for violation in report["violations"]
    if violation["kind"] not in known_sampling_defects
  ]
  assert unexpected == []


def test_to_svg_recompiles_without_accumulating_points():
  fixture = FIXTURE_BUILDERS[0]()
  first = fixture.diagram.to_svg()
  second = fixture.diagram.to_svg()
  assert first == second


def test_diagnostics_report_negative_nominal_width():
  diagram = Diagram(100, 80, resolution=20)
  lineage = Lineage(diagram, "red", 0, 40, -10)
  fixture = EngineFixture("negative-width", "Invalid negative width.", diagram, {"lineage": lineage}, ())
  report = diagnose_fixture(fixture)
  assert any(violation["kind"] == "negative-width" for violation in report["violations"])


def test_diagnostics_report_cross_assembly_overlap_without_event_hint():
  diagram = Diagram(100, 80, resolution=20)
  lineage = Lineage(diagram, "red", 0, 40, 10)
  first = Bundle(diagram, 0, 25, 2)
  second = Bundle(diagram, 0, 55, 2)
  first.add_member(lineage, 20, 60)
  second.add_member(lineage, 30, 70)
  fixture = EngineFixture("two-parents", "Invalid duplicate parent.", diagram, {"lineage": lineage}, ())
  report = diagnose_fixture(fixture)
  assert any(violation["kind"] == "overlapping-layout-parents" for violation in report["violations"])
