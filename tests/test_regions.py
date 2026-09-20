import xml.etree.ElementTree as ET

import pytest
from svgpathtools import QuadraticBezier, parse_path

from lineage_diagram import Bundle, Diagram, Lineage, Orbit, Region, RegionHatch, RegionStroke
from lineage_diagram.timeline import BoundarySide
from tools.fixture_cases import dynamic_region
from tools.geometry_diagnostics import diagnose_fixture


SVG_NAMESPACE = {"svg": "http://www.w3.org/2000/svg"}


def _point_segment_distance(point, first, second):
  span = second - first
  if abs(span) <= 1e-12:
    return abs(point - first)
  ratio = ((point - first).real * span.real + (point - first).imag * span.imag) / (abs(span) ** 2)
  ratio = max(0.0, min(1.0, ratio))
  return abs(point - (first + span * ratio))


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
  assert region._bounds_at(20, BoundarySide.RIGHT) == pytest.approx((30, 50), abs=2e-2)
  assert region._bounds_at(140, BoundarySide.RIGHT)[1] > region._bounds_at(20, BoundarySide.RIGHT)[1]
  assert after_svg.index('id="region-0"') < after_svg.index('id="lineage-0"')


def test_region_membership_change_is_local_to_the_event_coordinate():
  diagram = Diagram(200, 140, resolution=80)
  first = Lineage(diagram, "red", 0, 35, 10)
  second = Lineage(diagram, "blue", 0, 100, 10)
  region = Region(diagram, padding=5, corner_radius=0, event_corner_radius=3)
  region.add_member(first, 0, 180)
  region.add_member(second, 100, 160)
  diagram.compile()

  event_points = [point for point in region.components[0].points if point.x == 100]
  assert len(event_points) == 2
  assert (event_points[0].upper_y, event_points[0].lower_y) == pytest.approx((25, 45), abs=2e-2)
  assert (event_points[1].upper_y, event_points[1].lower_y) == pytest.approx((25, 110), abs=2e-2)
  assert all(point.lower_y == pytest.approx(45, abs=2e-2) for point in region.components[0].points if point.x < 100)
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


def test_region_offsets_rendered_curved_edges_perpendicularly():
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
  region_upper, region_lower = region._bounds_at(x, BoundarySide.RIGHT)
  assert region_upper < min(rendered_ys) - 6
  assert region_lower > max(rendered_ys) + 6


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


def test_unrelated_diagram_event_does_not_split_a_smooth_region_envelope():
  diagram = Diagram(180, 120, resolution=100)
  tracked = Lineage(diagram, "red", 0, 35, 10)
  tracked.shift_to(20, 160, 85)
  unrelated = Lineage(diagram, "blue", 0, 105, 10)
  unrelated.scale_to(83, 83, 24)
  region = Region(diagram, padding=5, event_corner_radius=4)
  region.add_member(tracked, 10, 170)
  diagram.compile()

  event_points = [point for point in region.components[0].points if point.x == 83]
  assert len(event_points) == 1
  assert region._bounds_at(83, BoundarySide.LEFT) == pytest.approx(
    region._bounds_at(83, BoundarySide.RIGHT)
  )


def test_region_preserves_both_sides_of_zero_duration_scale_event():
  diagram = Diagram(160, 100, resolution=80)
  lineage = Lineage(diagram, "red", 0, 40, 10)
  lineage.scale_to(80, 80, 24)
  region = Region(diagram, padding=5, event_corner_radius=0)
  region.add_member(lineage, 10, 150)
  diagram.compile()

  widths = [
    abs(sample.upper - sample.lower)
    for sample in lineage._compiled_samples
    if sample.source_x == 80
  ]
  event_points = [point for point in region.components[0].points if point.x == 80]

  assert widths == pytest.approx([10, 24])
  assert len(event_points) == 2
  assert (event_points[0].upper_y, event_points[0].lower_y) == pytest.approx((30, 50), abs=2e-2)
  assert (event_points[1].upper_y, event_points[1].lower_y) == pytest.approx((23, 57), abs=2e-2)


def test_assembled_region_preserves_both_sides_of_scale_step():
  diagram = Diagram(160, 120, resolution=80)
  bundle = Bundle(diagram, 0, 60, 3)
  bundle.shift_to(20, 140, 75)
  lineage = Lineage.create_in_assembly(diagram, "red", 0, 10, bundle)
  lineage.scale_to(80, 80, 14)
  region = Region(diagram, padding=5, event_corner_radius=0)
  region.add_member(lineage, 10, 150)
  diagram.compile()

  widths = [
    abs(sample.upper - sample.lower)
    for sample in lineage._compiled_samples
    if sample.source_x == 80
  ]
  event_points = [point for point in region.components[0].points if point.x == 80]

  assert widths == pytest.approx([10, 14])
  assert len(event_points) == 2


def test_curved_region_canonicalizes_scale_step_to_authored_x():
  diagram = Diagram(180, 140, resolution=100)
  lineage = Lineage(diagram, "red", 0, 35, 10)
  lineage.shift_to(20, 160, 65)
  lineage.scale_to(83, 83, 14)
  region = Region(diagram, padding=5, event_corner_radius=0)
  region.add_member(lineage, 10, 170)
  diagram.compile()

  widths = [
    abs(sample.upper - sample.lower)
    for sample in lineage._compiled_samples
    if sample.source_x == 83
  ]
  event_points = [point for point in region.components[0].points if point.x == 83]

  assert widths == pytest.approx([10, 14])
  assert len(event_points) == 2
  assert region._bounds_at(83, BoundarySide.LEFT) != pytest.approx(
    region._bounds_at(83, BoundarySide.RIGHT)
  )


def test_bundle_position_step_emits_only_authored_event_sides():
  diagram = Diagram(180, 140, resolution=100)
  bundle = Bundle(diagram, 0, 40, 0)
  lineage = Lineage.create_in_assembly(diagram, "red", 0, 10, bundle)
  bundle.shift_to(80, 80, 100)
  region = Region(diagram, padding=5, event_corner_radius=0)
  region.add_member(lineage, 10, 170)
  diagram.compile()

  samples = [sample for sample in lineage._compiled_samples if sample.source_x == 80]
  centers = [((sample.upper + sample.lower) / 2).imag for sample in samples]
  event_points = [point for point in region.components[0].points if point.x == 80]

  assert centers == pytest.approx([40, 100], abs=1e-3)
  assert len(event_points) == 2


def test_orbit_main_position_step_preserves_satellite_event_sides():
  diagram = Diagram(180, 160, resolution=100)
  main = Lineage(diagram, "black", 0, 50, 12)
  orbit = Orbit(diagram, main, 3)
  satellite = Lineage.create_in_assembly(diagram, "red", 0, 8, orbit, index=1)
  main.shift_to(80, 80, 110)
  region = Region(diagram, padding=5, event_corner_radius=0)
  region.add_member(satellite, 10, 170)
  diagram.compile()

  samples = [sample for sample in satellite._compiled_samples if sample.source_x == 80]
  centers = [((sample.upper + sample.lower) / 2).imag for sample in samples]
  event_points = [point for point in region.components[0].points if point.x == 80]

  assert len(centers) == 2
  assert centers[1] - centers[0] == pytest.approx(60, abs=1e-3)
  assert len(event_points) == 2


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


def test_region_padding_is_perpendicular_to_visible_stroked_edge():
  diagram = Diagram(200, 140, resolution=120, lineage_stroke_width=4)
  lineage = Lineage(diagram, "red", 0, 30, 10)
  lineage.shift_to(20, 180, 110)
  region = Region(diagram, padding=6, corner_radius=0)
  lineage.join_region(region, 10)
  lineage.leave_region(region, 190)
  diagram.compile()

  point = min(region.components[0].points, key=lambda item: abs(item.x - 100))
  region_upper = complex(point.x, point.upper_y)
  upper = [sample.upper for sample in lineage._compiled_samples]
  distance = min(
    _point_segment_distance(region_upper, first, second)
    for first, second in zip(upper, upper[1:])
  )

  assert distance >= 8 - 1e-4
  assert region.components[0].points[0].x == 10
  assert region.components[0].points[-1].x == 190


def test_region_padding_follows_a_rapidly_scaling_visible_edge():
  diagram = Diagram(180, 140, resolution=160)
  lineage = Lineage(diagram, "red", 0, 70, 10)
  lineage.scale_to(80, 100, 50)
  region = Region(diagram, padding=6, corner_radius=0)
  region.add_member(lineage, 20, 160)
  diagram.compile()

  x = 90
  region_upper = complex(x, region._bounds_at(x, BoundarySide.RIGHT)[0])
  upper = [sample.upper for sample in lineage._compiled_samples]
  distance = min(
    _point_segment_distance(region_upper, first, second)
    for first, second in zip(upper, upper[1:])
  )
  rendered_y = min(Region._polyline_intersections(upper, x, BoundarySide.RIGHT))

  assert distance >= 6 - 1e-4
  assert rendered_y - region_upper.imag > 6


def test_region_cap_radius_is_independent_of_diagram_resolution():
  starts = []
  for resolution in (20, 400):
    diagram = Diagram(100, 80, resolution=resolution)
    lineage = Lineage(diagram, "red", 0, 40, 10)
    region = Region(diagram, padding=6, corner_radius=4, event_corner_radius=0)
    region.add_member(lineage, 10, 90)
    diagram.compile()
    starts.append(parse_path(region.components[0].path_d).start.real)

  assert starts == pytest.approx([14, 14], abs=1e-4)


def test_region_target_side_membership_api_delegates_to_region():
  diagram = Diagram(100, 80, resolution=20)
  lineage = Lineage(diagram, "red", 0, 40, 10)
  bundle = Bundle(diagram, 0, 40, 2)
  orbit = Orbit(diagram, lineage, 2)
  region = Region(diagram)

  lineage_membership = lineage.join_region(region, 10)
  lineage.leave_region(region, 20)
  bundle_membership = bundle.join_region(region, 30)
  bundle.leave_region(region, 40)
  orbit_membership = orbit.join_region(region, 50)
  orbit.leave_region(region, 60)

  assert lineage_membership.target is lineage
  assert bundle_membership.target is bundle
  assert orbit_membership.target is orbit
  assert [(item.start_x, item.end_x) for item in region.memberships] == [
    (10, 20),
    (30, 40),
    (50, 60),
  ]


def test_region_rounds_sharp_envelope_source_changes_but_not_dense_samples():
  crossing = Diagram(200, 140, resolution=160)
  first = Lineage(crossing, "red", 0, 30, 10)
  second = Lineage(crossing, "blue", 0, 110, 10)
  first.shift_to(20, 180, 110)
  second.shift_to(20, 180, 30)
  crossing_region = Region(
    crossing,
    padding=6,
    corner_radius=4,
    event_corner_radius=0,
  )
  crossing_region.add_member(first, 10, 190)
  crossing_region.add_member(second, 10, 190)
  crossing.compile()

  smooth = Diagram(200, 140, resolution=400)
  lineage = Lineage(smooth, "red", 0, 30, 10)
  lineage.shift_to(20, 180, 110)
  smooth_region = Region(smooth, padding=6, corner_radius=4, event_corner_radius=0)
  smooth_region.add_member(lineage, 10, 190)
  smooth.compile()

  crossing_curves = sum(
    isinstance(segment, QuadraticBezier)
    for segment in parse_path(crossing_region.components[0].path_d)
  )
  smooth_curves = sum(
    isinstance(segment, QuadraticBezier)
    for segment in parse_path(smooth_region.components[0].path_d)
  )
  assert crossing_curves > smooth_curves
  assert smooth_curves == 4

  rendered_edges = []
  for member in (first, second):
    samples = member._compiled_samples
    rendered_edges.extend(
      (before, after)
      for points in (
        [sample.upper for sample in samples],
        [sample.lower for sample in samples],
      )
      for before, after in zip(points, points[1:])
    )
  for segment_index, segment in enumerate(parse_path(crossing_region.components[0].path_d)):
    for index in range(9):
      point = segment.point(index / 8)
      if point.real <= 14.1 or point.real >= 185.9:
        continue
      distance = min(_point_segment_distance(point, first, second) for first, second in rendered_edges)
      assert distance >= 2 - 5e-2, (segment_index, type(segment).__name__, index, point, distance)


def test_high_resolution_region_does_not_copy_every_member_edge_coordinate():
  diagram = Diagram(1000, 220, resolution=1000)
  lineages = [
    Lineage(diagram, color, 0, y, 10)
    for color, y in (("red", 40), ("blue", 80), ("green", 120), ("black", 160))
  ]
  lineages[0].shift_to(200, 800, 70)
  lineages[-1].scale_to(350, 650, 30)
  region = Region(diagram, padding=6, corner_radius=4)
  for lineage in lineages:
    region.add_member(lineage, 50, 950)

  diagram.compile()

  assert len(region.components[0].points) < 5000
