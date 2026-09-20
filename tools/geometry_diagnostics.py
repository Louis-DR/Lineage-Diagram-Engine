import argparse
import json
import math
from pathlib import Path
from typing import Any

from lineage_diagram.segments import IndependentSegment
from lineage_diagram.timeline import BoundarySide, NumericTimeline
from tools.fixture_cases import EngineFixture, build_all_fixtures


def _point_data(point: complex) -> list[float]:
  return [float(point.real), float(point.imag)]


def _overlap(start_a: float, end_a: float, start_b: float, end_b: float) -> bool:
  return max(start_a, start_b) < min(end_a, end_b) - 1e-9


def _orientation(a: complex, b: complex, c: complex) -> float:
  return (b.real - a.real) * (c.imag - a.imag) - (b.imag - a.imag) * (c.real - a.real)


def _segments_intersect(a: complex, b: complex, c: complex, d: complex) -> bool:
  o1 = _orientation(a, b, c)
  o2 = _orientation(a, b, d)
  o3 = _orientation(c, d, a)
  o4 = _orientation(c, d, b)
  return ((o1 > 1e-9 and o2 < -1e-9) or (o1 < -1e-9 and o2 > 1e-9)) and (
    (o3 > 1e-9 and o4 < -1e-9) or (o3 < -1e-9 and o4 > 1e-9)
  )


def _point_segment_distance(point: complex, first: complex, second: complex) -> float:
  span = second - first
  if abs(span) <= 1e-12:
    return abs(point - first)
  ratio = (
    (point.real - first.real) * span.real
    + (point.imag - first.imag) * span.imag
  ) / (abs(span) ** 2)
  ratio = max(0.0, min(1.0, ratio))
  return abs(point - (first + span * ratio))


def _first_self_intersection(points: list[complex]) -> tuple[int, int] | None:
  if len(points) < 4:
    return None
  edge_count = len(points)
  for first in range(edge_count):
    a = points[first]
    b = points[(first + 1) % edge_count]
    for second in range(first + 2, edge_count):
      if first == 0 and second == edge_count - 1:
        continue
      c = points[second]
      d = points[(second + 1) % edge_count]
      if _segments_intersect(a, b, c, d):
        return first, second
  return None


def _dependency_cycles(diagram) -> list[list[str]]:
  names = {lineage: f"lineage-{index}" for index, lineage in enumerate(diagram._lineages)}
  dependencies = {lineage: set() for lineage in diagram._lineages}
  for orbit in diagram._orbits:
    for membership in orbit.memberships:
      dependencies[membership.lineage].add(orbit.main_lineage)

  cycles = []
  visiting = []
  visited = set()

  def visit(lineage):
    if lineage in visiting:
      start = visiting.index(lineage)
      cycles.append([names[item] for item in visiting[start:] + [lineage]])
      return
    if lineage in visited:
      return
    visiting.append(lineage)
    for dependency in dependencies.get(lineage, ()):
      visit(dependency)
    visiting.pop()
    visited.add(lineage)

  for lineage in diagram._lineages:
    visit(lineage)
  return cycles


def _required_geometry_xs(lineage, assemblies, seen=None) -> list[float]:
  seen = set() if seen is None else set(seen)
  if lineage in seen:
    return []
  seen.add(lineage)
  visual_end_x = lineage.visual_end_x if lineage.visual_end_x is not None else lineage.end_x
  values = {float(lineage.start_x)}
  if visual_end_x is not None:
    values.add(float(visual_end_x))
  for event in (*lineage._shift_events, *lineage._scale_events, *lineage.membership_events):
    values.add(float(event.from_x))
    values.add(float(event.to_x))
  for assembly in assemblies:
    memberships = [membership for membership in assembly.memberships if membership.lineage is lineage]
    if not memberships:
      continue
    main_lineage = getattr(assembly, "main_lineage", None)
    if main_lineage is not None:
      anchor_xs = _required_geometry_xs(main_lineage, assemblies, seen)
      values.update(
        anchor_x
        for anchor_x in anchor_xs
        if any(
          membership.start_x + membership.fade_in_duration <= anchor_x
          <= membership.end_x - membership.fade_out_duration
          for membership in memberships
        )
      )
    for shift in getattr(assembly, "_shift_events", ()):
      if any(_overlap(shift.from_x, shift.to_x, membership.start_x, membership.end_x) for membership in memberships):
        values.add(float(shift.from_x))
        values.add(float(shift.to_x))
  return sorted(
    value for value in values
    if lineage.start_x - 1e-9 <= value <= (visual_end_x if visual_end_x is not None else lineage.diagram.view_width) + 1e-9
  )


def diagnose_fixture(
  fixture: EngineFixture,
  *,
  seam_tolerance: float = 1e-3,
  backtrack_tolerance: float = 1e-3,
  check_self_intersections: bool = False,
) -> dict[str, Any]:
  names = {lineage: name for name, lineage in fixture.lineages.items()}
  violations = []
  lineage_reports = {}
  region_reports = {}
  assemblies = [*fixture.diagram._bundles, *fixture.diagram._orbits]

  cycles = _dependency_cycles(fixture.diagram)
  for cycle in cycles:
    violations.append({"kind": "dependency-cycle", "cycle": cycle})
  if cycles:
    return {
      "fixture": fixture.name,
      "description": fixture.description,
      "view": [fixture.diagram.view_width, fixture.diagram.view_height],
      "event_xs": list(fixture.event_xs),
      "lineages": {},
      "regions": {},
      "violations": violations,
      "summary": {"violation_count": len(violations), "by_kind": {"dependency-cycle": len(violations)}},
    }

  geometry_report = fixture.diagram.validate_geometry()
  violations.extend(diagnostic.as_dict() for diagnostic in geometry_report.diagnostics)
  draw_order = sorted(fixture.diagram._lineages, key=lambda lineage: lineage.z)

  for lineage in draw_order:
    name = names.get(lineage, f"lineage-{fixture.diagram._lineages.index(lineage)}")
    compiled = []
    all_upper = []
    all_lower = []

    for segment_index, segment in enumerate(lineage._computed_segments):
      upper, lower = segment.compile()
      upper = list(upper)
      lower = list(lower)
      compiled.append((segment, upper, lower))
      all_upper.extend(upper)
      all_lower.extend(lower)

      if isinstance(segment, IndependentSegment):
        for point_index, (top, bottom) in enumerate(zip(upper, lower)):
          center = (top + bottom) / 2
          actual_width = abs(top - bottom)
          next_center = (
            (upper[point_index + 1] + lower[point_index + 1]) / 2
            if point_index + 1 < len(upper)
            else None
          )
          # An explicit zero-duration transform emits adjacent left/right
          # samples at one x. The first sample is the left-side state.
          side = (
            BoundarySide.LEFT
            if next_center is not None and abs(next_center.real - center.real) <= 1e-6
            else BoundarySide.RIGHT
          )
          expected_width = NumericTimeline(lineage.start_w, lineage._scale_events, "to_w").value_at(center.real, side)
          if not math.isfinite(actual_width):
            violations.append({
              "kind": "non-finite-rendered-width",
              "lineage": name,
              "segment": segment_index,
              "point": point_index,
              "x": center.real if math.isfinite(center.real) else repr(center.real),
              "value": repr(actual_width),
            })
          elif math.isfinite(expected_width):
            width_error = abs(actual_width - expected_width)
            if width_error > max(1e-3, abs(expected_width) * 1e-5):
              violations.append({
                "kind": "width-error",
                "lineage": name,
                "segment": segment_index,
                "point": point_index,
                "x": center.real,
                "expected": expected_width,
                "actual": actual_width,
                "error": width_error,
              })

      for edge_name, points in (("upper", upper), ("lower", lower)):
        for point_index, point in enumerate(points):
          if not math.isfinite(point.real) or not math.isfinite(point.imag):
            violations.append({
              "kind": "non-finite-coordinate",
              "lineage": name,
              "segment": segment_index,
              "edge": edge_name,
              "point": point_index,
              "x": point.real if math.isfinite(point.real) else repr(point.real),
              "value": [repr(point.real), repr(point.imag)],
            })
        for point_index, (before, after) in enumerate(zip(points, points[1:])):
          delta_x = after.real - before.real
          if delta_x < -backtrack_tolerance:
            violations.append({
              "kind": "x-backtrack",
              "lineage": name,
              "segment": segment_index,
              "edge": edge_name,
              "point": point_index,
              "from_x": before.real,
              "to_x": after.real,
              "distance": abs(delta_x),
            })

    seams = []
    for seam_index, (before, after) in enumerate(zip(compiled, compiled[1:])):
      _, before_upper, before_lower = before
      _, after_upper, after_lower = after
      if not before_upper or not before_lower or not after_upper or not after_lower:
        continue
      upper_error = abs(after_upper[0] - before_upper[-1])
      lower_error = abs(after_lower[0] - before_lower[-1])
      before_center = (before_upper[-1] + before_lower[-1]) / 2
      after_center = (after_upper[0] + after_lower[0]) / 2
      center_error = abs(after_center - before_center)
      seam = {
        "index": seam_index,
        "x": float(getattr(after[0], "start_x", after_center.real)),
        "center_error": center_error,
        "upper_error": upper_error,
        "lower_error": lower_error,
      }
      seams.append(seam)
      if max(center_error, upper_error, lower_error) > seam_tolerance:
        violations.append({"kind": "segment-seam", "lineage": name, **seam})

    if check_self_intersections and all_upper and all_lower:
      polygon = all_upper + list(reversed(all_lower))
      intersection = _first_self_intersection(polygon)
      if intersection is not None:
        violations.append({
          "kind": "polygon-self-intersection",
          "lineage": name,
          "edges": list(intersection),
        })

    required_xs = _required_geometry_xs(lineage, assemblies)
    sampled_center_xs = [
      ((top + bottom) / 2).real
      for _, upper, lower in compiled
      for top, bottom in zip(upper, lower)
      if math.isfinite(((top + bottom) / 2).real)
    ]
    for required_x in required_xs:
      nearest_error = min((abs(sampled_x - required_x) for sampled_x in sampled_center_xs), default=math.inf)
      if nearest_error > 1e-6:
        violations.append({
          "kind": "event-boundary-missing",
          "lineage": name,
          "x": required_x,
          "nearest_error": nearest_error if math.isfinite(nearest_error) else None,
        })

    width_sample_xs = set(required_xs)
    for event in lineage._scale_events:
      width_sample_xs.add((float(event.from_x) + float(event.to_x)) / 2)
    for sample_x in sorted(width_sample_xs):
      width = lineage.get_width_at(sample_x)
      if not math.isfinite(width):
        violations.append({
          "kind": "non-finite-width",
          "lineage": name,
          "x": sample_x,
          "value": repr(width),
        })
      elif width < 0:
        violations.append({
          "kind": "negative-width",
          "lineage": name,
          "x": sample_x,
          "value": width,
          "error": abs(width),
        })

    for segment, _, _ in compiled:
      if isinstance(segment, IndependentSegment) or not hasattr(segment, "bundle"):
        continue
      assembly = segment.bundle
      cached_samples = [
        sample for sample in assembly._compiled_member_samples.get(lineage, ())
        if segment.start_x <= sample.source_x <= segment.end_x
      ]
      for sample in cached_samples:
        sample_x, top, bottom = sample.source_x, sample.upper, sample.lower
        memberships = [
          membership for membership in assembly.get_memberships_at(sample_x)
          if membership.lineage is lineage
        ]
        if len(memberships) != 1:
          continue
        actual_width = abs(top - bottom)
        expected_width = lineage.get_width_at(sample_x) * assembly._get_factor(memberships[0], sample_x)
        if not math.isfinite(actual_width):
          violations.append({
            "kind": "non-finite-rendered-width",
            "lineage": name,
            "x": sample_x,
            "value": repr(actual_width),
          })
        elif math.isfinite(expected_width):
          width_error = abs(actual_width - expected_width)
          if width_error > max(1e-3, abs(expected_width) * 1e-5):
            violations.append({
              "kind": "width-error",
              "lineage": name,
              "x": sample_x,
              "expected": expected_width,
              "actual": actual_width,
              "error": width_error,
            })

    coordinates = [
      point for point in all_upper + all_lower
      if math.isfinite(point.real) and math.isfinite(point.imag)
    ]
    if coordinates:
      bounds = {
        "min_x": min(point.real for point in coordinates),
        "max_x": max(point.real for point in coordinates),
        "min_y": min(point.imag for point in coordinates),
        "max_y": max(point.imag for point in coordinates),
      }
    else:
      bounds = None

    lineage_reports[name] = {
      "segment_count": len(compiled),
      "upper_point_count": len(all_upper),
      "lower_point_count": len(all_lower),
      "bounds": bounds,
      "seams": seams,
      "required_geometry_xs": required_xs,
    }

  all_memberships = []
  for assembly_index, assembly in enumerate(assemblies):
    memberships_by_lineage = {}
    for membership in assembly.memberships:
      all_memberships.append((assembly_index, membership))
      memberships_by_lineage.setdefault(membership.lineage, []).append(membership)
      if membership.lineage.end_x is not None and membership.end_x > membership.lineage.end_x + 1e-9:
        violations.append({
          "kind": "membership-after-termination",
          "lineage": names.get(membership.lineage, "unknown"),
          "assembly": assembly_index,
          "lineage_end_x": membership.lineage.end_x,
          "membership_end_x": membership.end_x,
        })

    for lineage, memberships in memberships_by_lineage.items():
      for first_index, first in enumerate(memberships):
        for second in memberships[first_index + 1:]:
          if _overlap(first.start_x, first.end_x, second.start_x, second.end_x):
            violations.append({
              "kind": "overlapping-memberships",
              "lineage": names.get(lineage, "unknown"),
              "assembly": assembly_index,
              "first": [first.start_x, first.end_x],
              "second": [second.start_x, second.end_x],
            })

  for first_index, (first_assembly, first) in enumerate(all_memberships):
    for second_assembly, second in all_memberships[first_index + 1:]:
      if first_assembly == second_assembly or first.lineage is not second.lineage:
        continue
      if _overlap(first.start_x, first.end_x, second.start_x, second.end_x):
        overlap_start = max(first.start_x, second.start_x)
        overlap_end = min(first.end_x, second.end_x)
        violations.append({
          "kind": "overlapping-layout-parents",
          "lineage": names.get(first.lineage, "unknown"),
          "x": (overlap_start + overlap_end) / 2,
          "first_assembly": first_assembly,
          "second_assembly": second_assembly,
          "overlap": [overlap_start, overlap_end],
          "duration": overlap_end - overlap_start,
        })

  epsilon = 1e-4
  for event_x in fixture.event_xs:
    for sample_x in (event_x - epsilon, event_x, event_x + epsilon):
      for lineage, name in names.items():
        active = 0
        for assembly in assemblies:
          active += sum(
            membership.lineage is lineage
            and membership.start_x <= sample_x
            and sample_x <= membership.end_x
            for membership in assembly.memberships
          )
        if active > 1:
          violations.append({
            "kind": "multiple-active-memberships",
            "lineage": name,
            "x": sample_x,
            "count": active,
          })

  for region in fixture.diagram._regions:
    component_reports = []
    sampled_xs = []
    minimum_clearance = math.inf
    for component_index, component in enumerate(region.components):
      points = list(component.points)
      sampled_xs.extend(point.x for point in points)
      for point_index, point in enumerate(points):
        if not all(math.isfinite(value) for value in (point.x, point.upper_y, point.lower_y)):
          violations.append({
            "kind": "non-finite-region-coordinate",
            "region": region.id,
            "component": component_index,
            "point": point_index,
            "value": [repr(point.x), repr(point.upper_y), repr(point.lower_y)],
          })
          continue
        if point.upper_y > point.lower_y:
          violations.append({
            "kind": "inverted-region-envelope",
            "region": region.id,
            "component": component_index,
            "point": point_index,
            "x": point.x,
            "upper_y": point.upper_y,
            "lower_y": point.lower_y,
          })
        if point_index and point.x < points[point_index - 1].x - backtrack_tolerance:
          violations.append({
            "kind": "region-x-backtrack",
            "region": region.id,
            "component": component_index,
            "point": point_index,
            "from_x": points[point_index - 1].x,
            "to_x": point.x,
          })

        active_lineages = {}
        for membership in region.memberships:
          if not region._membership_active(membership, point.x, point.side):
            continue
          for lineage in region._target_lineages(membership.target, point.x, point.side):
            active_lineages[lineage.id] = lineage
        if not active_lineages:
          violations.append({
            "kind": "region-envelope-without-members",
            "region": region.id,
            "component": component_index,
            "point": point_index,
            "x": point.x,
          })
        else:
          for boundary_name, boundary_point in (
              ("upper", complex(point.x, point.upper_y)),
              ("lower", complex(point.x, point.lower_y)),
            ):
            nearest = None
            for lineage in active_lineages.values():
              samples = lineage._compiled_samples
              discontinuities = {
                second.source_x
                for first, second in zip(samples, samples[1:])
                if abs(first.source_x - second.source_x) <= 1e-9
                and (
                  abs(first.upper - second.upper) > 1e-9
                  or abs(first.lower - second.lower) > 1e-9
                )
              }
              edges = []
              for first, second in zip(samples, samples[1:]):
                if (
                    abs(first.source_x - second.source_x) <= 1e-9
                    and second.source_x in discontinuities
                  ):
                  continue
                if point.x in discontinuities:
                  if point.side == BoundarySide.LEFT and min(first.source_x, second.source_x) >= point.x:
                    continue
                  if point.side == BoundarySide.RIGHT and max(first.source_x, second.source_x) <= point.x:
                    continue
                edges.extend(((first.upper, second.upper), (first.lower, second.lower)))
              if samples:
                edges.extend((
                  (samples[0].upper, samples[0].lower),
                  (samples[-1].upper, samples[-1].lower),
                ))
              for first, second in edges:
                distance = _point_segment_distance(boundary_point, first, second)
                candidate = (distance, lineage.id)
                if nearest is None or candidate < nearest:
                  nearest = candidate
            if nearest is None:
              continue
            minimum_clearance = min(minimum_clearance, nearest[0])
            error = region._clearance - nearest[0]
            if error > max(seam_tolerance, 2e-2):
              violations.append({
                "kind": "region-clearance-error",
                "region": region.id,
                "component": component_index,
                "point": point_index,
                "lineage": nearest[1],
                "boundary": boundary_name,
                "x": point.x,
                "required_clearance": region._clearance,
                "measured_clearance": nearest[0],
                "error": error,
              })

      polygon = [
        *[complex(point.x, point.upper_y) for point in points],
        *[complex(point.x, point.lower_y) for point in reversed(points)],
      ]
      if check_self_intersections and polygon:
        intersection = _first_self_intersection(polygon)
        if intersection is not None:
          violations.append({
            "kind": "region-self-intersection",
            "region": region.id,
            "component": component_index,
            "edges": list(intersection),
          })
      component_reports.append({
        "point_count": len(points),
        "min_x": min((point.x for point in points), default=None),
        "max_x": max((point.x for point in points), default=None),
      })

    membership_boundaries = sorted({
      value
      for membership in region.memberships
      for value in (
        membership.start_x,
        membership.end_x if membership.end_x is not None else fixture.diagram.view_width,
      )
      if (
        region._bounds_at(value, BoundarySide.LEFT) is not None
        or region._bounds_at(value, BoundarySide.RIGHT) is not None
      )
    })
    for boundary in membership_boundaries:
      nearest_error = min((abs(sampled_x - boundary) for sampled_x in sampled_xs), default=math.inf)
      if nearest_error > 1e-6:
        violations.append({
          "kind": "region-event-boundary-missing",
          "region": region.id,
          "x": boundary,
          "nearest_error": nearest_error if math.isfinite(nearest_error) else None,
        })
    region_reports[region.id] = {
      "component_count": len(region.components),
      "components": component_reports,
      "required_geometry_xs": membership_boundaries,
      "minimum_clearance": minimum_clearance if math.isfinite(minimum_clearance) else None,
    }

  counts = {}
  for violation in violations:
    kind = violation["kind"]
    counts[kind] = counts.get(kind, 0) + 1

  return {
    "fixture": fixture.name,
    "description": fixture.description,
    "view": [fixture.diagram.view_width, fixture.diagram.view_height],
    "event_xs": list(fixture.event_xs),
    "lineages": lineage_reports,
    "regions": region_reports,
    "violations": violations,
    "summary": {"violation_count": len(violations), "by_kind": counts},
  }


def main() -> int:
  parser = argparse.ArgumentParser(description="Generate geometry diagnostics for engine fixtures.")
  parser.add_argument("--output", type=Path, default=Path("artifacts/diagnostics/geometry.json"))
  parser.add_argument("--self-intersections", action="store_true")
  args = parser.parse_args()

  reports = [
    diagnose_fixture(fixture, check_self_intersections=args.self_intersections)
    for fixture in build_all_fixtures()
  ]
  payload = {
    "fixtures": reports,
    "summary": {
      "fixture_count": len(reports),
      "violation_count": sum(report["summary"]["violation_count"] for report in reports),
    },
  }
  args.output.parent.mkdir(parents=True, exist_ok=True)
  args.output.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
  print(f"Geometry report written to {args.output}")
  print(f"Detected {payload['summary']['violation_count']} violations across {len(reports)} fixtures.")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
