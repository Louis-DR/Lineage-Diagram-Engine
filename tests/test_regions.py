import xml.etree.ElementTree as ET

import pytest

from lineage_diagram import Bundle, Diagram, Lineage, Orbit, Region, RegionHatch, RegionStroke
from lineage_diagram.timeline import BoundarySide
from tools.fixture_cases import dynamic_region
from tools.geometry_diagnostics import diagnose_fixture


SVG_NAMESPACE = {"svg": "http://www.w3.org/2000/svg"}


def test_region_tracks_member_geometry_without_mutating_lineage_svg():
  diagram = Diagram(200, 120, resolution=80)
  lineage = Lineage(diagram, "red", 0, 40, 10)
  lineage.shift_to(60, 100, 80)
  lineage.scale_to(120, 160, 24)
  before = ET.fromstring(diagram.to_svg()).find("svg:path[@id='lineage-0']", SVG_NAMESPACE).attrib["d"]

  region = Region(diagram, padding=5, fill="#ff0000")
  region.add_member(lineage, 0, 180)
  after_svg = diagram.to_svg()
  after_root = ET.fromstring(after_svg)
  after = after_root.find("svg:path[@id='lineage-0']", SVG_NAMESPACE).attrib["d"]

  assert before == after
  assert region._bounds_at(20, BoundarySide.RIGHT) == pytest.approx((30, 50))
  assert region._bounds_at(140, BoundarySide.RIGHT)[1] > region._bounds_at(20, BoundarySide.RIGHT)[1]
  assert after_svg.index('id="region-0"') < after_svg.index('id="lineage-0"')


def test_region_membership_change_is_local_to_the_event_coordinate():
  diagram = Diagram(200, 140, resolution=80)
  first = Lineage(diagram, "red", 0, 35, 10)
  second = Lineage(diagram, "blue", 0, 100, 10)
  region = Region(diagram, padding=5, corner_radius=4, event_corner_radius=3)
  region.add_member(first, 0, 180)
  region.add_member(second, 100, 160)
  diagram.compile()

  event_points = [point for point in region.components[0].points if point.x == 100]
  assert [(point.upper_y, point.lower_y) for point in event_points] == pytest.approx([
    (25, 45),
    (25, 110),
  ])
  assert all(point.lower_y == pytest.approx(45) for point in region.components[0].points if point.x < 100)
  assert " Q " in region.components[0].path_d


def test_region_empty_interval_creates_separate_components():
  diagram = Diagram(200, 100, resolution=60)
  lineage = Lineage(diagram, "red", 0, 50, 10)
  region = Region(diagram)
  region.add_member(lineage, 10, 60)
  region.add_member(lineage, 100, 160)

  diagram.compile()

  assert len(region.components) == 2
  assert region.components[0].points[0].x == 10
  assert region.components[0].points[-1].x == 60
  assert region.components[1].points[0].x == 100


def test_lineage_region_membership_promotes_to_bundle_then_returns_to_lineage():
  diagram = Diagram(200, 140, resolution=80)
  bundle = Bundle(diagram, 0, 80, 4)
  resident = Lineage.create_in_assembly(diagram, "blue", 0, 12, bundle)
  visitor = Lineage(diagram, "red", 0, 70, 10)
  visitor.join(40, 60, bundle, index=0)
  visitor.leave(100, 120, bundle, 70)
  region = Region(diagram, padding=3)
  region.add_member(visitor, 0, 180)
  diagram.compile()

  assert region._target_lineages(visitor, 50, BoundarySide.RIGHT) == [visitor]
  assert set(region._target_lineages(visitor, 70, BoundarySide.RIGHT)) == {visitor, resident}
  assert region._target_lineages(visitor, 110, BoundarySide.RIGHT) == [visitor]


def test_lineage_region_membership_promotes_to_whole_orbit():
  diagram = Diagram(200, 140, resolution=80)
  main = Lineage(diagram, "black", 0, 70, 12)
  orbit = Orbit(diagram, main, 3)
  first = Lineage.create_in_assembly(diagram, "red", 0, 8, orbit, index=1)
  second = Lineage.create_in_assembly(diagram, "blue", 0, 8, orbit, index=-1)
  region = Region(diagram)
  region.add_member(first, 0, 180)
  diagram.compile()

  assert set(region._target_lineages(first, 80, BoundarySide.RIGHT)) == {main, first, second}


def test_region_styles_emit_gradient_stroke_and_hatch_with_stable_ids():
  diagram = Diagram(200, 100, resolution=40)
  lineage = Lineage(diagram, "red", 0, 50, 10)
  region = Region(
    diagram,
    fill="#ff0000",
    fill_opacity=0.25,
    stroke=RegionStroke("#000000", width=2, opacity=0.8, dasharray=(5, 3)),
    hatch=RegionHatch("#ffffff", opacity=0.3, width=1, spacing=7, angle=30),
  )
  region.add_member(lineage, 0, 180)
  region.shade(40, 100, "#0000ff")
  region.fade(80, 140, 0.1)

  first = diagram.to_svg()
  second = diagram.to_svg()
  root = ET.fromstring(first)

  assert first == second
  assert root.find(".//svg:g[@id='region-0']", SVG_NAMESPACE) is not None
  assert root.find(".//svg:linearGradient[@id='gradient-region-0']", SVG_NAMESPACE) is not None
  assert root.find(".//svg:pattern[@id='pattern-region-0']", SVG_NAMESPACE) is not None
  fill = root.find(".//svg:path[@id='region-0-component-0-fill']", SVG_NAMESPACE)
  hatch = root.find(".//svg:path[@id='region-0-component-0-hatch']", SVG_NAMESPACE)
  outline = root.find(".//svg:path[@id='region-0-component-0-outline']", SVG_NAMESPACE)
  assert fill.attrib["stroke"] == "none"
  assert outline.attrib["stroke-dasharray"] == "5 3"
  assert hatch is not None


def test_same_lineage_can_belong_to_multiple_regions():
  diagram = Diagram(100, 80, resolution=20)
  lineage = Lineage(diagram, "red", 0, 40, 10)
  first = Region(diagram)
  second = Region(diagram)
  first.add_member(lineage, 0, 80)
  second.add_member(lineage, 20, 60)

  diagram.compile()

  assert first.components
  assert second.components
  assert first.id != second.id


def test_region_fixture_has_no_structural_geometry_violation():
  report = diagnose_fixture(dynamic_region())

  assert report["regions"]["region-0"]["component_count"] == 1
  assert report["violations"] == []


def test_region_uses_vertical_intersections_of_rendered_curved_edges():
  diagram = Diagram(200, 140, resolution=160)
  lineage = Lineage(diagram, "red", 0, 40, 18)
  lineage.shift_to(40, 140, 90)
  region = Region(diagram, padding=6)
  region.add_member(lineage, 0, 180)
  diagram.compile()

  x = 80
  upper, lower = region._compiled_edges[lineage]

  def intersections(points):
    values = []
    for first, second in zip(points, points[1:]):
      if min(first.real, second.real) <= x <= max(first.real, second.real) and first.real != second.real:
        ratio = (x - first.real) / (second.real - first.real)
        values.append(first.imag + (second.imag - first.imag) * ratio)
    return values

  rendered_ys = [*intersections(upper), *intersections(lower)]
  assert region._bounds_at(x, BoundarySide.RIGHT) == pytest.approx((
    min(rendered_ys) - 6,
    max(rendered_ys) + 6,
  ))


def test_region_stops_tracking_a_split_parent_at_its_visual_end():
  diagram = Diagram(180, 120, resolution=80)
  bundle = Bundle(diagram, 0, 60, 3)
  parent = Lineage.create_in_assembly(diagram, "red", 0, 20, bundle)
  parent.split(50, 80, [
    {"color": "blue", "target_w": 10, "target_y": 35},
    {"color": "green", "target_w": 10, "target_y": 85},
  ])
  region = Region(diagram)
  region.add_member(parent, 0, 150)
  diagram.compile()

  assert parent.visual_end_x == 50
  assert region.components[0].points[-1].x == 50
  assert region._bounds_at(60, BoundarySide.RIGHT) is None


def test_region_preserves_small_authored_steps():
  diagram = Diagram(120, 80, resolution=50)
  lineage = Lineage(diagram, "red", 0, 40, 10)
  lineage.shift_to(50, 50, 40.0005)
  region = Region(diagram, event_corner_radius=0)
  region.add_member(lineage, 0, 100)
  diagram.compile()

  event_points = [point for point in region.components[0].points if point.x == 50]
  assert len(event_points) == 2
  assert event_points[1].upper_y - event_points[0].upper_y == pytest.approx(0.0005)


def test_region_zero_duration_styles_emit_duplicate_gradient_stops():
  diagram = Diagram(200, 100, resolution=40)
  lineage = Lineage(diagram, "red", 0, 50, 10)
  region = Region(diagram, fill="#ff0000", fill_opacity=0.3)
  region.add_member(lineage, 0, 180)
  region.shade(50, 50, "#0000ff")
  region.fade(50, 50, 0.1)

  root = ET.fromstring(diagram.to_svg())
  stops = root.findall(".//svg:linearGradient[@id='gradient-region-0']/svg:stop", SVG_NAMESPACE)
  event_stops = [stop for stop in stops if stop.attrib["offset"] == "25.0%"]
  assert [(stop.attrib["stop-color"], stop.attrib["stop-opacity"]) for stop in event_stops] == [
    ("#ff0000", "0.3"),
    ("#0000ff", "0.1"),
  ]


def test_region_rounding_is_clamped_to_padding():
  diagram = Diagram(100, 80, resolution=20)
  lineage = Lineage(diagram, "red", 0, 40, 10)
  region = Region(diagram, padding=0, corner_radius=20, event_corner_radius=20)
  region.add_member(lineage, 10, 80)
  diagram.compile()

  assert " Q " not in region.components[0].path_d


def test_region_z_order_is_stable_and_style_values_are_xml_escaped():
  diagram = Diagram(100, 80, resolution=20)
  lineage = Lineage(diagram, "red", 0, 40, 10)
  later = Region(diagram, fill="red&blue", stroke=RegionStroke("black&white"), z=10)
  earlier = Region(diagram, fill="#ffffff", z=-10)
  later.add_member(lineage, 0, 80)
  earlier.add_member(lineage, 0, 80)

  svg = diagram.to_svg()
  root = ET.fromstring(svg)

  assert svg.index('id="region-1"') < svg.index('id="region-0"') < svg.index('id="lineage-0"')
  assert root.find(".//svg:path[@id='region-0-component-0-fill']", SVG_NAMESPACE).attrib["fill"] == "red&blue"
  assert root.find(".//svg:path[@id='region-0-component-0-outline']", SVG_NAMESPACE).attrib["stroke"] == "black&white"
