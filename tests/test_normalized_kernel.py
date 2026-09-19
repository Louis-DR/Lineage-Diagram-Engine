import pytest

from lineage_diagram.bundle import Bundle
from lineage_diagram.diagram import Diagram
from lineage_diagram.lineage import Lineage
from lineage_diagram.paths import ScaleEvent
from lineage_diagram.timeline import BoundarySide, ColorTimeline, NumericTimeline
from tools.fixture_cases import (
  bundle_merge_replacement,
  bundle_reorder,
  continuing_merge_boundary,
  orbit_merge_split,
  overlapping_shifts,
  simultaneous_bundle_join_leave,
)


def test_stable_ids_and_diagram_state_queries():
  diagram = Diagram(200, 100)
  first = Lineage(diagram, "red", 0, 30, 10)
  second = Lineage(diagram, "blue", 0, 70, 10)

  assert first.id == "lineage-0"
  assert second.id == "lineage-1"
  assert diagram.state_at(first.id, 40).lineage_id == first.id


def test_state_query_uses_normalized_overlapping_position_timeline():
  fixture = overlapping_shifts()
  lineage = fixture.lineages["lineage"]
  fixture.diagram.compile()

  for x in (90, 130, 170, 220):
    assert lineage.state_at(x).y == pytest.approx(lineage.frame_at(x).center.imag)


def test_zero_duration_width_has_explicit_boundary_sides():
  diagram = Diagram(200, 100)
  lineage = Lineage(diagram, "red", 0, 50, 10)
  lineage.scale_to(80, 80, 24)

  assert lineage.state_at(80, BoundarySide.LEFT).width == 10
  assert lineage.state_at(80, BoundarySide.RIGHT).width == 24


def test_overlapping_scale_preserves_prefix_and_resumes_interrupted_target():
  original = NumericTimeline(10, [ScaleEvent(60, 260, 30)], "to_w")
  interrupted = NumericTimeline(10, [
    ScaleEvent(60, 260, 30),
    ScaleEvent(120, 190, 8),
  ], "to_w")

  assert interrupted.value_at(90) == pytest.approx(original.value_at(90))
  assert interrupted.value_at(190) == pytest.approx(8)
  assert interrupted.value_at(260) == pytest.approx(30)


def test_overlapping_color_resumes_interrupted_target_with_ordered_stops():
  class Event:
    def __init__(self, from_x, to_x, color):
      self.from_x = from_x
      self.to_x = to_x
      self.color = color

  original = ColorTimeline("#ff0000", [Event(60, 260, "#0000ff")])
  interrupted = ColorTimeline("#ff0000", [
    Event(60, 260, "#0000ff"),
    Event(120, 190, "#00ff00"),
  ])

  assert interrupted.value_at(90) == original.value_at(90)
  assert interrupted.value_at(190) == "#00ff00"
  assert interrupted.value_at(260) == "#0000ff"
  assert [x for x, _ in interrupted.stops(360)] == sorted(x for x, _ in interrupted.stops(360))


def test_reorder_interpolates_every_bundle_member():
  fixture = bundle_reorder()
  fixture.diagram.compile()
  first = fixture.lineages["first"]
  second = fixture.lineages["second"]
  third = fixture.lineages["third"]

  for lineage in (first, second, third):
    before = lineage.frame_at(100, BoundarySide.LEFT).center.imag
    middle = lineage.frame_at(130).center.imag
    after = lineage.frame_at(160).center.imag
    assert middle == pytest.approx((before + after) / 2, abs=1e-4)

  assert second.frame_at(100, BoundarySide.LEFT).center != second.frame_at(160).center
  assert third.frame_at(100, BoundarySide.LEFT).center != third.frame_at(160).center


def test_leave_validation_uses_stable_membership():
  diagram = Diagram(200, 100)
  bundle = Bundle(diagram, 0, 50, 4)
  lineage = Lineage(diagram, "red", 0, 50, 10)

  with pytest.raises(ValueError, match="independent"):
    lineage.leave(20, 40, bundle, 60)


def test_continuing_merge_renders_the_right_side_of_zero_duration_position_step():
  fixture = continuing_merge_boundary()
  source = fixture.lineages["source"]
  baseline = source.get_baseline_path()

  outgoing_run = next(
    segment for segment in baseline
    if segment.start.real == 150 and segment.end.real > segment.start.real
  )

  assert outgoing_run.start.imag == pytest.approx(source._get_y_at(150.001))
  fixture.diagram.compile()
  assert source.frame_at(150.001).center.imag == pytest.approx(source._get_y_at(150.001))


def test_bundle_merge_replaces_parent_slots_without_neighbor_swap_or_early_child_membership():
  fixture = bundle_merge_replacement()
  diagram = fixture.diagram
  bundle = diagram._bundles[0]
  blue = fixture.lineages["blue"]
  red = fixture.lineages["red"]
  green = fixture.lineages["green"]
  yellow = fixture.lineages["yellow"]
  merged = fixture.lineages["merged"]

  assert [membership.lineage for membership in bundle.get_memberships_at(125)] == [green, yellow]
  child_membership = next(membership for membership in bundle.memberships if membership.lineage is merged)
  assert child_membership.start_x == merged.start_x == 150

  def centers_at(x):
    memberships, offsets, _ = bundle._layout_at(x)
    return {membership.lineage: offsets[membership.lineage] for membership in memberships}

  before = centers_at(99.999)
  during = centers_at(125)
  after = centers_at(150.001)

  assert before[blue] < before[red] < before[green] < before[yellow]
  assert during[blue] < during[red] < during[green] < during[yellow]
  assert during[green] < during[yellow]
  assert after[green] < after[yellow]

  diagram.compile()
  assert green.frame_at(150, BoundarySide.LEFT).center.imag == pytest.approx(
    green.frame_at(150, BoundarySide.RIGHT).center.imag,
    abs=1e-4,
  )


def test_simultaneous_bundle_join_leave_interpolates_persistent_member_without_jump():
  fixture = simultaneous_bundle_join_leave()
  bundle = fixture.diagram._bundles[0]
  yellow = fixture.lineages["yellow"]

  def center_at(x):
    _, offsets, _ = bundle._layout_at(x)
    return offsets[yellow]

  before = center_at(99.999)
  just_after = center_at(100.001)
  middle = center_at(125)
  after = center_at(150.001)

  assert just_after == pytest.approx(before, abs=1e-6)
  assert before < middle < after

  fixture.diagram.compile()
  green = fixture.lineages["green"]
  leaving_segment = next(
    segment for segment in green._computed_segments
    if segment.start_x == 100 and segment.end_x == 150 and not hasattr(segment, "bundle")
  )
  assert green.frame_at(100, BoundarySide.LEFT).center.imag == pytest.approx(
    leaving_segment.get_baseline_path().point(0).imag,
    abs=1e-4,
  )


def test_orbit_merge_and_split_keep_lower_side_indices_and_newest_inner_tie_order():
  fixture = orbit_merge_split()
  orbit = fixture.diagram._orbits[0]
  merged = fixture.lineages["merged"]
  split_blue = fixture.lineages["split-blue"]
  split_red = fixture.lineages["split-red"]
  split_upper_blue = fixture.lineages["split-upper-blue"]
  split_upper_red = fixture.lineages["split-upper-red"]

  reservations = [reservation for reservation in orbit._reservations if reservation.lineage is merged]
  assert reservations[0].index == -1
  assert all(
    reservation.index == -1
    for reservation in orbit._reservations
    if reservation.lineage in {split_blue, split_red, merged}
  )

  _, offsets = orbit._layout_at(250.001)
  assert offsets[split_red] > offsets[split_blue]
  assert offsets[split_upper_blue] > offsets[split_upper_red]

  fixture.diagram.compile()
  main_y = fixture.lineages["main"].frame_at(200).center.imag
  lower_start_distances = {
    lineage: abs(lineage.frame_at(200).center.imag - main_y)
    for lineage in (split_blue, split_red)
  }
  upper_start_distances = {
    lineage: abs(lineage.frame_at(200).center.imag - main_y)
    for lineage in (split_upper_blue, split_upper_red)
  }
  assert lower_start_distances[split_red] < lower_start_distances[split_blue]
  assert upper_start_distances[split_upper_blue] > upper_start_distances[split_upper_red]
