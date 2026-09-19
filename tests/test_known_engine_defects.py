import pytest
from svgpathtools import Path

from lineage_diagram.bundle import Bundle
from lineage_diagram.diagram import Diagram
from lineage_diagram.lineage import Lineage
from lineage_diagram.segments import IndependentSegment
from lineage_diagram.timeline import BoundarySide
from lineage_diagram.geometry_safety import CurvatureSafetyPolicy, UnsafeNormalOffsetError
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
  overcommitted_split_merge_widths,
  overlapping_shifts,
  safe_independent_normal_offset,
  tight_bundle_outer_normal_offset,
  tight_independent_normal_offset,
  tight_orbit_satellite_normal_offset,
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


def test_split_and_merge_packet_helpers_allocate_exact_container_width():
  split_widths, split_centers = Lineage._calculate_split_layout(20, 80, [15, 15])

  assert split_widths == pytest.approx([10, 10])
  assert split_centers == pytest.approx([75, 85])
  assert sum(split_widths) == pytest.approx(20)

  unequal_widths, _ = Lineage._calculate_split_layout(24, 80, [3, 9])
  zero_widths, _ = Lineage._calculate_split_layout(20, 80, [0, 0])
  assert unequal_widths == pytest.approx([6, 18])
  assert zero_widths == pytest.approx([10, 10])


def test_overcommitted_split_and_merge_packets_tile_their_container_edges():
  fixture = overcommitted_split_merge_widths()
  parent = fixture.lineages["parent"]
  upper = fixture.lineages["upper"]
  lower = fixture.lineages["lower"]
  merged = fixture.lineages["merged"]
  fixture.diagram.compile()

  parent_frame = parent.frame_at(60, BoundarySide.LEFT)
  split_frames = [upper.frame_at(60), lower.frame_at(60)]
  merge_frames = [upper.frame_at(300, BoundarySide.LEFT), lower.frame_at(300, BoundarySide.LEFT)]
  merged_frame = merged.frame_at(300)

  def interval(frame):
    return sorted((frame.lower.imag, frame.upper.imag))

  for container, participants in ((parent_frame, split_frames), (merged_frame, merge_frames)):
    container_interval = interval(container)
    participant_intervals = sorted((interval(frame) for frame in participants), key=lambda item: item[0])
    assert participant_intervals[0][0] == pytest.approx(container_interval[0], abs=1e-3)
    assert participant_intervals[0][1] == pytest.approx(participant_intervals[1][0], abs=1e-3)
    assert participant_intervals[1][1] == pytest.approx(container_interval[1], abs=1e-3)
    assert sum(frame.width for frame in participants) == pytest.approx(container.width, abs=1e-3)


def test_continuing_split_and_merge_into_use_packet_conserving_widths():
  diagram = Diagram(360, 160, resolution=120)
  parent = Lineage(diagram, "blue", 0, 80, 20)
  child = Lineage.create_split_from(
    parent, 60, 160, "red", 15, 110,
    parent_target_w=15,
    parent_target_y=50,
  )
  source = Lineage(diagram, "green", 0, 50, 15)
  target = Lineage(diagram, "gold", 0, 110, 15)
  source.merge_into(target, 200, 300, 20, target_y=80)
  diagram.compile()

  split_frames = [parent.frame_at(60), child.frame_at(60)]
  merge_frames = [source.frame_at(300, BoundarySide.LEFT), target.frame_at(300, BoundarySide.LEFT)]

  assert sum(frame.width for frame in split_frames) == pytest.approx(20, abs=1e-3)
  assert sum(frame.width for frame in merge_frames) == pytest.approx(20, abs=1e-3)


def test_tight_independent_normal_offset_warns_with_measured_context():
  fixture = tight_independent_normal_offset()
  report = fixture.diagram.validate_geometry()
  diagnostics = [diagnostic.as_dict() for diagnostic in report.diagnostics]
  unsafe = next(diagnostic for diagnostic in diagnostics if diagnostic["kind"] == "unsafe-normal-offset")

  assert unsafe["producer"] == "independent-segment"
  assert unsafe["lineage"] == fixture.lineages["lineage"].id
  assert unsafe["offset_radius_ratio"] > unsafe["policy_limit"] == 0.8
  assert unsafe["x"] not in fixture.event_xs
  assert unsafe["source_transition"] == {"from_x": 20, "to_x": 60, "to_y": 130}
  assert unsafe["minimum_safe_radius"] == pytest.approx(abs(unsafe["signed_offset"]) / 0.8)
  with pytest.warns(RuntimeWarning, match=r"during shift 20->60 to y=130") as warnings:
    fixture.diagram.compile()
  assert "radius=" in str(warnings[0].message)

  fixture.diagram.curvature_policy = CurvatureSafetyPolicy(mode="reject")
  with pytest.raises(UnsafeNormalOffsetError, match="Unsafe normal offsets"):
    fixture.diagram.compile()


def test_safe_independent_normal_offset_compiles_under_the_default_policy():
  fixture = safe_independent_normal_offset()
  assert fixture.diagram.validate_geometry().is_safe
  fixture.diagram.compile()


@pytest.mark.parametrize(
  ("builder", "producer"),
  [
    (tight_bundle_outer_normal_offset, "bundle"),
    (tight_orbit_satellite_normal_offset, "orbit"),
  ],
  ids=("bundle", "orbit"),
)
def test_assembly_normal_offset_diagnostics_identify_the_producer(builder, producer):
  report = builder().diagram.validate_geometry()
  unsafe = [
    diagnostic.as_dict() for diagnostic in report.diagnostics
    if diagnostic.kind == "unsafe-normal-offset" and diagnostic.details["producer"] == producer
  ]

  assert unsafe
  assert all(diagnostic["membership"] for diagnostic in unsafe)
  assert all(diagnostic["offset_radius_ratio"] > 0.8 for diagnostic in unsafe)
