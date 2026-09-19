import pytest
from svgpathtools import Path

from lineage_diagram.bundle import Bundle
from lineage_diagram.diagram import Diagram
from lineage_diagram.lineage import Lineage
from lineage_diagram.segments import IndependentSegment
from lineage_diagram.utils import find_t_at_x
from tools.fixture_cases import (
  assembled_termination,
  bundle_join_leave,
  bundle_reorder,
  bundle_transfer,
  independent_transform,
  moving_orbit,
  orbit_attached_independent_transition,
  orbit_reorder,
  overlapping_shifts,
)
from tools.geometry_diagnostics import diagnose_fixture


def _violations(report, kind):
  return [violation for violation in report["violations"] if violation["kind"] == kind]


def test_bundle_reorder_is_continuous_and_has_one_membership():
  report = diagnose_fixture(bundle_reorder())
  assert not _violations(report, "segment-seam")
  assert not _violations(report, "overlapping-memberships")
  assert not _violations(report, "multiple-active-memberships")


def test_orbit_reorder_is_continuous_and_has_one_membership():
  report = diagnose_fixture(orbit_reorder())
  assert not _violations(report, "segment-seam")
  assert not _violations(report, "overlapping-memberships")
  assert not _violations(report, "multiple-active-memberships")


def test_termination_closes_assembly_membership():
  report = diagnose_fixture(assembled_termination())
  assert not _violations(report, "membership-after-termination")


def test_transfer_emits_one_member_geometry_per_x():
  report = diagnose_fixture(bundle_transfer())
  assert not _violations(report, "multiple-active-memberships")


def test_leave_while_independent_is_rejected_immediately():
  diagram = Diagram(200, 100)
  bundle = Bundle(diagram, 0, 50, 4)
  lineage = Lineage(diagram, "red", 0, 50, 10)
  with pytest.raises(ValueError, match="independent"):
    lineage.leave(20, 40, bundle, 60)


def test_bundle_split_replaces_parent_slot_before_layout():
  diagram = Diagram(240, 120, resolution=100)
  bundle = Bundle(diagram, 0, 60, 3)
  top = Lineage.create_in_assembly(diagram, "gold", 0, 8, bundle)
  parent = Lineage.create_in_assembly(diagram, "blue", 0, 20, bundle)
  bottom = Lineage.create_in_assembly(diagram, "green", 0, 8, bundle)
  first, second = parent.split(80, 120, [
    {"color": "red", "target_w": 10, "in_assembly": bundle},
    {"color": "purple", "target_w": 10, "in_assembly": bundle},
  ])

  active = [membership.lineage for membership in bundle.get_memberships_at(121)]
  assert active == [top, first, second, bottom]


def test_state_query_matches_rendered_baseline_during_overlapping_shift():
  fixture = overlapping_shifts()
  lineage = fixture.lineages["lineage"]
  baseline: Path = lineage.get_baseline_path()
  for x in (90, 130, 170, 220):
    rendered_y = baseline.point(find_t_at_x(baseline, x)).imag
    assert lineage._get_y_at(x) == pytest.approx(rendered_y, abs=1e-6)


@pytest.mark.parametrize(
  "builder",
  [independent_transform, bundle_join_leave, moving_orbit],
  ids=lambda builder: builder.__name__,
)
def test_geometry_samples_event_boundaries_exactly(builder):
  report = diagnose_fixture(builder())
  assert not _violations(report, "event-boundary-missing")


def test_dependency_cycle_is_rejected():
  diagram = Diagram(200, 100)
  first = Lineage(diagram, "red", 0, 40, 10)
  second = Lineage(diagram, "blue", 0, 60, 10)
  from lineage_diagram.orbit import Orbit

  first_orbit = Orbit(diagram, first)
  second_orbit = Orbit(diagram, second)
  first.join(20, 30, second_orbit, 1)
  second.join(20, 30, first_orbit, 1)

  with pytest.raises(ValueError, match="Cyclic lineage dependency"):
    diagram.compile()


def test_orbit_uses_main_independent_segment_geometry_during_transition():
  fixture = orbit_attached_independent_transition()
  main = fixture.lineages["main"]
  satellite = fixture.lineages["satellite"]
  fixture.diagram.compile()

  leave_segment = next(
    segment for segment in main._computed_segments
    if isinstance(segment, IndependentSegment) and segment.start_x == 100 and segment.end_x == 160
  )
  expected_upper, expected_lower = leave_segment.get_geometry_at(130)
  actual_upper, actual_lower = main.get_geometry_at(130)
  orbit = fixture.diagram._orbits[0]
  satellite_upper, satellite_lower = orbit._get_member_geometry_at(130, satellite)
  expected_normal = (expected_upper - expected_lower) / abs(expected_upper - expected_lower)
  expected_satellite_center = (
    (expected_upper + expected_lower) / 2
    + expected_normal * (main.get_width_at(130) / 2 + orbit.margin + satellite.get_width_at(130) / 2)
  )

  assert actual_upper == pytest.approx(expected_upper)
  assert actual_lower == pytest.approx(expected_lower)
  assert (satellite_upper + satellite_lower) / 2 == pytest.approx(expected_satellite_center)
