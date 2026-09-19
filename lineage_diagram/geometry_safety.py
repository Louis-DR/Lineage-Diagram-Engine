from dataclasses import dataclass
import math
from typing import TYPE_CHECKING, Literal

from .segments import IndependentSegment

if TYPE_CHECKING:
  from .diagram import Diagram


@dataclass(frozen=True)
class CurvatureSafetyPolicy:
  mode: Literal["reject", "warn", "report", "off"] = "warn"
  max_offset_radius_fraction: float = 0.80
  samples_per_curve: int = 64
  x_order_tolerance: float = 1e-3


@dataclass(frozen=True)
class GeometryDiagnostic:
  kind: str
  details: dict

  def as_dict(self) -> dict:
    return {"kind": self.kind, **self.details}


@dataclass(frozen=True)
class GeometryValidationReport:
  diagnostics: tuple[GeometryDiagnostic, ...]

  @property
  def is_safe(self) -> bool:
    return not self.diagnostics


class UnsafeNormalOffsetError(ValueError):
  def __init__(self, diagnostics: tuple[GeometryDiagnostic, ...]):
    self.diagnostics = diagnostics
    super().__init__(format_geometry_diagnostics(diagnostics, prefix="Unsafe normal offsets"))


def format_geometry_diagnostics(
    diagnostics: tuple[GeometryDiagnostic, ...],
    *,
    prefix: str = "Unsafe geometry",
  ) -> str:
  """Summarize the worst actionable offset diagnostic for console output."""
  if not diagnostics:
    return f"{prefix}: none"

  def priority(diagnostic: GeometryDiagnostic):
    details = diagnostic.details
    return (
      diagnostic.kind != "unsafe-normal-offset",
      -details.get("offset_radius_ratio", 0.0),
      details.get("delta_x", 0.0),
    )

  diagnostic = min(diagnostics, key=priority)
  details = diagnostic.details
  summary = (
    f"{prefix}: {len(diagnostics)} violation(s); "
    f"{details.get('producer', 'geometry')}:{details.get('lineage', 'unknown')}"
  )
  transition = details.get("source_transition")
  if transition:
    summary += (
      f" during shift {transition['from_x']:g}->{transition['to_x']:g}"
      f" to y={transition['to_y']:g}"
    )
  if "x" in details:
    summary += f" at x={details['x']:.3f}"
  elif "from_x" in details:
    summary += f" at x={details['from_x']:.3f}->{details['to_x']:.3f}"
  if "offset_radius_ratio" in details:
    summary += (
      f"; edge={details['edge']}, offset={details['signed_offset']:.3f},"
      f" radius={details['radius']:.3f} (need >= {details['minimum_safe_radius']:.3f}),"
      f" ratio={details['offset_radius_ratio']:.3f} > {details['policy_limit']:.3f}"
    )
  elif "delta_x" in details:
    summary += f"; edge={details['edge']}, x delta={details['delta_x']:.3f}"
  return summary


def _curvature(before: complex, point: complex, after: complex) -> float:
  first = point - before
  second = after - point
  chord = after - before
  denominator = abs(first) * abs(second) * abs(chord)
  if denominator <= 1e-12:
    return 0.0
  cross = first.real * second.imag - first.imag * second.real
  return 2 * cross / denominator


def _normal_at(segment, t: float) -> complex:
  return segment.normal(t)


def _sample_path(segment, sample_count: int):
  return [segment.point(index / sample_count) for index in range(sample_count + 1)]


def _path_offset_diagnostics(
    *,
    producer: str,
    producer_id: str,
    baseline_path,
    offset_entries_at,
    source_transition_at=None,
    policy: CurvatureSafetyPolicy,
  ) -> list[GeometryDiagnostic]:
  diagnostics = []
  worst = {}

  for segment_index, segment in enumerate(baseline_path):
    start = segment.point(0)
    end = segment.point(1)
    if abs(end.real - start.real) <= 1e-9:
      # Vertical steps are explicit discontinuities. The renderer omits them
      # instead of constructing a normal offset through the corner.
      continue

    points = _sample_path(segment, policy.samples_per_curve)
    edge_points = {}
    for index in range(1, len(points) - 1):
      point = points[index]
      curvature = _curvature(points[index - 1], point, points[index + 1])
      for entry in offset_entries_at(point.real):
        ratio = abs(entry["offset"] * curvature)
        key = (entry["lineage"], entry.get("membership"), entry["edge"], segment_index)
        existing = worst.get(key)
        if existing is None or ratio > existing["ratio"]:
          worst[key] = {
            **entry,
            "source_transition": source_transition_at(point.real) if source_transition_at else None,
            "x": point.real,
            "center": [point.real, point.imag],
            "curvature": curvature,
            "ratio": ratio,
          }

    for index, point in enumerate(points):
      for entry in offset_entries_at(point.real):
        normal = _normal_at(segment, index / policy.samples_per_curve)
        edge_points.setdefault((entry["lineage"], entry.get("membership"), entry["edge"]), []).append(
          point + normal * entry["offset"]
        )

    for key, points_for_edge in edge_points.items():
      for before, after in zip(points_for_edge, points_for_edge[1:]):
        if after.real < before.real - policy.x_order_tolerance:
          lineage, membership, edge = key
          diagnostics.append(GeometryDiagnostic("normal-offset-x-backtrack", {
            "producer": producer,
            "producer_id": producer_id,
            "lineage": lineage,
            "membership": membership,
            "edge": edge,
            "from_x": before.real,
            "to_x": after.real,
            "delta_x": after.real - before.real,
            "source_transition": source_transition_at(before.real) if source_transition_at else None,
          }))
          break

  for entry in worst.values():
    if entry["ratio"] <= policy.max_offset_radius_fraction:
      continue
    curvature = entry["curvature"]
    diagnostics.append(GeometryDiagnostic("unsafe-normal-offset", {
      "producer": producer,
      "producer_id": producer_id,
      "lineage": entry["lineage"],
      "assembly": entry.get("assembly"),
      "membership": entry.get("membership"),
      "source_transition": entry.get("source_transition"),
      "edge": entry["edge"],
      "x": entry["x"],
      "center": entry["center"],
      "signed_offset": entry["offset"],
      "effective_width": entry["width"],
      "curvature": curvature,
      "radius": math.inf if curvature == 0 else 1 / abs(curvature),
      "minimum_safe_radius": abs(entry["offset"]) / policy.max_offset_radius_fraction,
      "offset_radius_ratio": entry["ratio"],
      "policy_limit": policy.max_offset_radius_fraction,
    }))
  return diagnostics


def _independent_diagnostics(diagram: "Diagram", policy: CurvatureSafetyPolicy) -> list[GeometryDiagnostic]:
  diagnostics = []
  for lineage in diagram._lineages:
    for segment_index, segment in enumerate(lineage._computed_segments):
      if not isinstance(segment, IndependentSegment):
        continue
      baseline_path = segment.get_baseline_path()

      def offsets_at(x):
        width = segment.get_width_at(x)
        return [
          {"lineage": lineage.id, "edge": "upper", "offset": width / 2, "width": width},
          {"lineage": lineage.id, "edge": "lower", "offset": -width / 2, "width": width},
        ]

      def source_transition_at(x):
        active_events = [
          event for event in segment._shift_events
          if event.from_x <= x <= event.to_x
        ]
        if not active_events:
          return None
        event = active_events[-1]
        return {
          "from_x": event.from_x,
          "to_x": event.to_x,
          "to_y": event.to_y,
        }

      diagnostics.extend(_path_offset_diagnostics(
        producer="independent-segment",
        producer_id=f"{lineage.id}/segment-{segment_index}",
        baseline_path=baseline_path,
        offset_entries_at=offsets_at,
        source_transition_at=source_transition_at,
        policy=policy,
      ))
  return diagnostics


def _bundle_diagnostics(diagram: "Diagram", policy: CurvatureSafetyPolicy) -> list[GeometryDiagnostic]:
  diagnostics = []
  for bundle in diagram._bundles:
    baseline_path = bundle.get_baseline_path()

    def offsets_at(x):
      memberships, offsets, widths = bundle._layout_at(x)
      entries = []
      for membership in memberships:
        width = widths[membership.lineage]
        center_offset = offsets[membership.lineage]
        membership_id = f"{bundle.id}/{membership.lineage.id}"
        entries.extend((
          {
            "lineage": membership.lineage.id,
            "assembly": bundle.id,
            "membership": membership_id,
            "edge": "upper",
            "offset": center_offset + width / 2,
            "width": width,
          },
          {
            "lineage": membership.lineage.id,
            "assembly": bundle.id,
            "membership": membership_id,
            "edge": "lower",
            "offset": center_offset - width / 2,
            "width": width,
          },
        ))
      return entries

    diagnostics.extend(_path_offset_diagnostics(
      producer="bundle",
      producer_id=bundle.id,
      baseline_path=baseline_path,
      offset_entries_at=offsets_at,
      policy=policy,
    ))
  return diagnostics


def _orbit_diagnostics(diagram: "Diagram", policy: CurvatureSafetyPolicy) -> list[GeometryDiagnostic]:
  diagnostics = []
  for orbit in diagram._orbits:
    active_ranges = [
      (membership.start_x, membership.end_x)
      for membership in orbit.memberships
    ]
    if not active_ranges:
      continue
    start_x = max(orbit.main_lineage.start_x, min(start for start, _ in active_ranges))
    end_x = min(
      orbit.main_lineage.end_x if orbit.main_lineage.end_x is not None else diagram.view_width,
      max(end for _, end in active_ranges),
    )
    if end_x <= start_x:
      continue
    sample_count = policy.samples_per_curve
    centers = []
    for index in range(sample_count + 1):
      x = start_x + (end_x - start_x) * index / sample_count
      upper, lower = orbit.main_lineage.get_geometry_at(x)
      centers.append((x, (upper + lower) / 2))
    worst = {}
    for index in range(1, len(centers) - 1):
      x, center = centers[index]
      curvature = _curvature(centers[index - 1][1], center, centers[index + 1][1])
      memberships, offsets = orbit._layout_at(x)
      for membership in memberships:
        width = membership.lineage.get_width_at(x) * orbit._get_factor(membership, x)
        center_offset = offsets[membership.lineage]
        membership_id = f"{orbit.id}/{membership.lineage.id}"
        for edge, offset in (("upper", center_offset + width / 2), ("lower", center_offset - width / 2)):
          ratio = abs(offset * curvature)
          key = (membership.lineage.id, membership_id, edge)
          if key not in worst or ratio > worst[key]["ratio"]:
            worst[key] = {
              "lineage": membership.lineage.id,
              "membership": membership_id,
              "edge": edge,
              "offset": offset,
              "width": width,
              "x": x,
              "center": [center.real, center.imag],
              "curvature": curvature,
              "ratio": ratio,
            }
    for entry in worst.values():
      if entry["ratio"] <= policy.max_offset_radius_fraction:
        continue
      curvature = entry["curvature"]
      diagnostics.append(GeometryDiagnostic("unsafe-normal-offset", {
        "producer": "orbit",
        "producer_id": orbit.id,
        "lineage": entry["lineage"],
        "assembly": orbit.id,
        "membership": entry["membership"],
        "edge": entry["edge"],
        "x": entry["x"],
        "center": entry["center"],
        "signed_offset": entry["offset"],
        "effective_width": entry["width"],
        "curvature": curvature,
        "radius": math.inf if curvature == 0 else 1 / abs(curvature),
        "minimum_safe_radius": abs(entry["offset"]) / policy.max_offset_radius_fraction,
        "offset_radius_ratio": entry["ratio"],
        "policy_limit": policy.max_offset_radius_fraction,
      }))
  return diagnostics


def validate_compiled_geometry(diagram: "Diagram", policy: CurvatureSafetyPolicy) -> GeometryValidationReport:
  if policy.mode == "off":
    return GeometryValidationReport(())
  diagnostics = (
    _independent_diagnostics(diagram, policy)
    + _bundle_diagnostics(diagram, policy)
    + _orbit_diagnostics(diagram, policy)
  )
  return GeometryValidationReport(tuple(diagnostics))
