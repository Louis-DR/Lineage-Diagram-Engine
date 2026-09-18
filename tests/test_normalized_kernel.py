import pytest

from lineage_diagram.bundle import Bundle
from lineage_diagram.diagram import Diagram
from lineage_diagram.lineage import Lineage
from lineage_diagram.paths import ScaleEvent
from lineage_diagram.timeline import BoundarySide, ColorTimeline, NumericTimeline
from tools.fixture_cases import bundle_reorder, overlapping_shifts


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
