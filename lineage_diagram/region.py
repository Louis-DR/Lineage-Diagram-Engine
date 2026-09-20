import html
import math

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .paths import ScaleEvent, ShadeEvent
from .sampling import diagram_event_xs
from .timeline import BoundarySide, ColorTimeline, NumericTimeline

if TYPE_CHECKING:
  from .bundle import Bundle
  from .diagram import Diagram
  from .lineage import Lineage
  from .orbit import Orbit


@dataclass(frozen=True)
class RegionStroke:
  color: str
  width: float = 1.0
  opacity: float = 1.0
  dasharray: tuple[float, ...] = ()

  def __post_init__(self):
    if not math.isfinite(self.width) or self.width < 0:
      raise ValueError("Region stroke width must be finite and nonnegative")
    if not math.isfinite(self.opacity) or not 0 <= self.opacity <= 1:
      raise ValueError("Region stroke opacity must be between 0 and 1")
    if any(not math.isfinite(value) or value <= 0 for value in self.dasharray):
      raise ValueError("Region stroke dash lengths must be finite and positive")


@dataclass(frozen=True)
class RegionHatch:
  color: str
  opacity: float = 0.2
  width: float = 1.0
  spacing: float = 8.0
  angle: float = 45.0

  def __post_init__(self):
    if not math.isfinite(self.opacity) or not 0 <= self.opacity <= 1:
      raise ValueError("Region hatch opacity must be between 0 and 1")
    if not math.isfinite(self.width) or self.width <= 0:
      raise ValueError("Region hatch width must be finite and positive")
    if not math.isfinite(self.spacing) or self.spacing <= 0:
      raise ValueError("Region hatch spacing must be finite and positive")
    if not math.isfinite(self.angle):
      raise ValueError("Region hatch angle must be finite")


@dataclass
class RegionMembership:
  target: "Lineage | Bundle | Orbit"
  start_x: float
  end_x: float | None = None


@dataclass(frozen=True)
class RegionEnvelopePoint:
  x: float
  upper_y: float
  lower_y: float
  side: BoundarySide
  upper_source: str | None = None
  lower_source: str | None = None


@dataclass(frozen=True)
class RegionComponent:
  points: tuple[RegionEnvelopePoint, ...]
  path_d: str


@dataclass(frozen=True)
class _BoundarySegment:
  first: complex
  second: complex
  source: str
  first_source_x: float
  second_source_x: float

  @property
  def tangent(self) -> complex:
    span = self.second - self.first
    return span / abs(span) if abs(span) > 1e-12 else 1 + 0j


@dataclass(frozen=True)
class _RegionEnvelope:
  upper_y: float
  lower_y: float
  upper_source: str
  lower_source: str


def _active_at(start_x: float, end_x: float, x: float, side: BoundarySide) -> bool:
  if side == BoundarySide.LEFT:
    return start_x < x <= end_x
  return start_x <= x < end_x


def _lineage_active_at(lineage: "Lineage", x: float, side: BoundarySide) -> bool:
  end_candidates = [lineage.diagram.view_width]
  if lineage.end_x is not None:
    end_candidates.append(lineage.end_x)
  if lineage.visual_end_x is not None:
    end_candidates.append(lineage.visual_end_x)
  end_x = min(end_candidates)
  return _active_at(lineage.start_x, end_x, x, side)


def _same_envelope(first: tuple[float, float] | None, second: tuple[float, float] | None) -> bool:
  if first is None or second is None:
    return first is second
  return abs(first[0] - second[0]) <= 1e-9 and abs(first[1] - second[1]) <= 1e-9


def _distance(first: complex, second: complex) -> float:
  return abs(first - second)


def _towards(origin: complex, target: complex, distance: float) -> complex:
  span = target - origin
  length = abs(span)
  if length <= 1e-12:
    return origin
  return origin + span * (distance / length)


def _polygon_vertical_intersections(points: tuple[complex, ...], x: float) -> list[float]:
  values = []
  for first, second in zip(points, (*points[1:], points[0])):
    delta_x = second.real - first.real
    if abs(delta_x) <= 1e-12:
      if abs(x - first.real) <= 1e-9:
        values.extend((first.imag, second.imag))
      continue
    if min(first.real, second.real) - 1e-9 <= x <= max(first.real, second.real) + 1e-9:
      ratio = (x - first.real) / delta_x
      if -1e-9 <= ratio <= 1 + 1e-9:
        values.append(first.imag + (second.imag - first.imag) * ratio)
  return values


def _capsule_vertical_interval(
    segment: _BoundarySegment,
    x: float,
    radius: float,
    side: BoundarySide,
  ) -> tuple[float, float] | None:
  """Intersect a vertical line with a segment dilated by a round disk."""
  first = segment.first
  second = segment.second
  if (
      abs(segment.first_source_x - segment.second_source_x) <= 1e-12
      and abs(x - segment.first_source_x) <= 1e-9
    ):
    selected = first if side == BoundarySide.LEFT else second
    if abs(x - selected.real) > radius + 1e-9:
      return None
    span = math.sqrt(max(0.0, radius ** 2 - (x - selected.real) ** 2))
    return selected.imag - span, selected.imag + span

  values = []
  span = second - first
  length = abs(span)
  if length <= 1e-12:
    if abs(x - first.real) <= radius + 1e-9:
      delta_y = math.sqrt(max(0.0, radius ** 2 - (x - first.real) ** 2))
      return first.imag - delta_y, first.imag + delta_y
    return None

  normal = complex(-span.imag, span.real) / length
  offset = normal * radius
  values.extend(_polygon_vertical_intersections(
    (first + offset, second + offset, second - offset, first - offset),
    x,
  ))
  for endpoint in (first, second):
    delta_x = x - endpoint.real
    if abs(delta_x) <= radius + 1e-9:
      delta_y = math.sqrt(max(0.0, radius ** 2 - delta_x ** 2))
      values.extend((endpoint.imag - delta_y, endpoint.imag + delta_y))
  if not values:
    return None
  return min(values), max(values)


def _rounded_polygon_path(
    points: tuple[RegionEnvelopePoint, ...],
    corner_radius: float,
    event_corner_radius: float,
  ) -> str:
  upper = [complex(point.x, point.upper_y) for point in points]
  lower = [complex(point.x, point.lower_y) for point in reversed(points)]
  sources = [point.upper_source for point in points]
  sources.extend(point.lower_source for point in reversed(points))
  entries = [[point, 0.0, source] for point, source in zip((*upper, *lower), sources)]
  upper_count = len(upper)

  # Start and end caps are the ordinary rounded corners.
  for index in (0, upper_count - 1, upper_count, len(entries) - 1):
    entries[index][1] = max(entries[index][1], corner_radius)

  # Duplicate timeline coordinates encode an intentional membership step.
  for start, end in ((0, upper_count), (upper_count, len(entries))):
    for index in range(start + 1, end):
      if (
          abs(entries[index - 1][0].real - entries[index][0].real) <= 1e-9
          and _distance(entries[index - 1][0], entries[index][0]) > 1e-12
        ):
        entries[index - 1][1] = max(entries[index - 1][1], event_corner_radius)
        entries[index][1] = max(entries[index][1], event_corner_radius)

  compact = []
  for point, radius, source in entries:
    if compact and _distance(compact[-1][0], point) <= 1e-12:
      compact[-1][1] = max(compact[-1][1], radius)
    else:
      compact.append([point, radius, source])
  if len(compact) > 1 and _distance(compact[0][0], compact[-1][0]) <= 1e-12:
    compact[0][1] = max(compact[0][1], compact[-1][1])
    compact.pop()
  if len(compact) < 3:
    return ""

  # Mark genuine source handoffs and sharp contour turns, never ordinary dense samples.
  for index, entry in enumerate(compact):
    if entry[1] > 0:
      continue
    previous = compact[index - 1]
    following = compact[(index + 1) % len(compact)]
    incoming_direction = entry[0] - previous[0]
    outgoing_direction = following[0] - entry[0]
    if abs(incoming_direction) <= 1e-12 or abs(outgoing_direction) <= 1e-12:
      continue
    incoming_direction /= abs(incoming_direction)
    outgoing_direction /= abs(outgoing_direction)
    turn = math.acos(max(-1.0, min(1.0, (
      incoming_direction.real * outgoing_direction.real
      + incoming_direction.imag * outgoing_direction.imag
    ))))
    source_changed = previous[2] != entry[2] or entry[2] != following[2]
    if turn >= math.radians(12) and source_changed:
      entry[1] = corner_radius

  count = len(compact)
  corners = [index for index, entry in enumerate(compact) if entry[1] > 0]
  if not corners:
    commands = [f"M {compact[0][0].real} {compact[0][0].imag}"]
    commands.extend(f"L {entry[0].real} {entry[0].imag}" for entry in compact[1:])
    commands.append("Z")
    return " ".join(commands)

  edge_lengths = [
    _distance(compact[index][0], compact[(index + 1) % count][0])
    for index in range(count)
  ]
  desired_trim = {}
  turns = {}
  for index in corners:
    point = compact[index][0]
    incoming_direction = point - compact[index - 1][0]
    outgoing_direction = compact[(index + 1) % count][0] - point
    if abs(incoming_direction) <= 1e-12 or abs(outgoing_direction) <= 1e-12:
      desired_trim[index] = 0.0
      turns[index] = 0.0
      continue
    incoming_direction /= abs(incoming_direction)
    outgoing_direction /= abs(outgoing_direction)
    turn = math.acos(max(-1.0, min(1.0, (
      incoming_direction.real * outgoing_direction.real
      + incoming_direction.imag * outgoing_direction.imag
    ))))
    turns[index] = turn
    desired_trim[index] = compact[index][1] * math.tan(turn / 2) if turn > 1e-9 else 0.0

  # Competing fillets share the available contour run deterministically.
  trims = dict(desired_trim)
  for position, first_index in enumerate(corners):
    second_index = corners[(position + 1) % len(corners)]
    distance = 0.0
    index = first_index
    while index != second_index:
      distance += edge_lengths[index]
      index = (index + 1) % count
    requested = trims[first_index] + trims[second_index]
    if requested > distance and requested > 1e-12:
      factor = distance / requested
      trims[first_index] *= factor
      trims[second_index] *= factor

  consumed = set()

  def trim_point(index: int, direction: int, distance: float) -> complex:
    point = compact[index][0]
    remaining = distance
    current = index
    while remaining > 1e-12:
      following = (current + direction) % count
      next_point = compact[following][0]
      edge_length = _distance(point, next_point)
      if edge_length >= remaining and edge_length > 1e-12:
        return point + (next_point - point) * (remaining / edge_length)
      remaining -= edge_length
      if following not in corners:
        consumed.add(following)
      current = following
      point = next_point
      if current in corners and current != index:
        break
    return point

  incoming = {}
  outgoing = {}
  for index in corners:
    incoming[index] = trim_point(index, -1, trims[index])
    outgoing[index] = trim_point(index, 1, trims[index])

  first_corner = corners[0]
  start = outgoing[first_corner]
  commands = [f"M {start.real} {start.imag}"]
  index = (first_corner + 1) % count
  while index != first_corner:
    if index in corners:
      in_point = incoming[index]
      out_point = outgoing[index]
      commands.append(f"L {in_point.real} {in_point.imag}")
      if trims[index] > 1e-12 and _distance(in_point, out_point) > 1e-12:
        corner = compact[index][0]
        commands.append(f"Q {corner.real} {corner.imag} {out_point.real} {out_point.imag}")
    elif index not in consumed:
      point = compact[index][0]
      commands.append(f"L {point.real} {point.imag}")
    index = (index + 1) % count

  in_point = incoming[first_corner]
  out_point = outgoing[first_corner]
  commands.append(f"L {in_point.real} {in_point.imag}")
  if trims[first_corner] > 1e-12 and _distance(in_point, out_point) > 1e-12:
    corner = compact[first_corner][0]
    commands.append(f"Q {corner.real} {corner.imag} {out_point.real} {out_point.imag}")
  commands.append("Z")
  return " ".join(commands)


class Region:
  """A post-layout envelope around time-varying diagram structures."""

  def __init__(
      self,
      diagram: "Diagram",
      *,
      padding: float = 4.0,
      fill: str = "#808080",
      fill_opacity: float = 0.2,
      corner_radius: float = 4.0,
      event_corner_radius: float = 2.0,
      stroke: RegionStroke | None = None,
      hatch: RegionHatch | None = None,
      z: float = 0.0,
    ):
    for name, value in (
      ("padding", padding),
      ("corner_radius", corner_radius),
      ("event_corner_radius", event_corner_radius),
      ("z", z),
    ):
      if not math.isfinite(value):
        raise ValueError(f"Region {name} must be finite")
    if padding < 0 or corner_radius < 0 or event_corner_radius < 0:
      raise ValueError("Region padding and corner radii must be nonnegative")
    if not math.isfinite(fill_opacity) or not 0 <= fill_opacity <= 1:
      raise ValueError("Region fill opacity must be between 0 and 1")

    self.diagram = diagram
    self.padding = float(padding)
    self.fill = fill
    self.fill_opacity = float(fill_opacity)
    self.corner_radius = float(corner_radius)
    self.event_corner_radius = float(event_corner_radius)
    self.stroke = stroke
    self.hatch = hatch
    self.z = float(z)
    self._memberships: list[RegionMembership] = []
    self._shade_events: list[ShadeEvent] = []
    self._opacity_events: list[ScaleEvent] = []
    self._components: list[RegionComponent] = []
    self._compiled_edges: dict["Lineage", tuple[list[complex], list[complex]]] = {}
    self._compiled_boundaries: dict["Lineage", tuple[_BoundarySegment, ...]] = {}
    self._boundary_buckets: dict["Lineage", tuple[float, dict[int, tuple[_BoundarySegment, ...]]]] = {}
    self._lineage_discontinuities: dict["Lineage", set[float]] = {}
    self._event_xs: set[float] = set()
    diagram.add_region(self)

  @property
  def memberships(self) -> tuple[RegionMembership, ...]:
    return tuple(self._memberships)

  @property
  def components(self) -> tuple[RegionComponent, ...]:
    return tuple(self._components)

  def _validate_target(self, target: "Lineage | Bundle | Orbit") -> None:
    from .bundle import Bundle
    from .lineage import Lineage
    from .orbit import Orbit

    if not isinstance(target, (Lineage, Bundle, Orbit)):
      raise TypeError("Region members must be Lineage, Bundle, or Orbit instances")
    if target.diagram is not self.diagram:
      raise ValueError("Region members must belong to the same diagram")

  def add_member(
      self,
      target: "Lineage | Bundle | Orbit",
      start_x: float,
      end_x: float | None = None,
    ) -> RegionMembership:
    self._validate_target(target)
    effective_end = self.diagram.view_width if end_x is None else float(end_x)
    if not all(math.isfinite(value) for value in (start_x, effective_end)):
      raise ValueError("Region membership coordinates must be finite")
    if effective_end <= start_x:
      raise ValueError("Region membership end must follow its start")
    if any(
      membership.target is target
      and max(membership.start_x, start_x) < min(
        membership.end_x if membership.end_x is not None else self.diagram.view_width,
        effective_end,
      )
      for membership in self._memberships
    ):
      raise ValueError("Region memberships for one target may not overlap")
    membership = RegionMembership(target, float(start_x), None if end_x is None else effective_end)
    self._memberships.append(membership)
    return membership

  def join(self, target: "Lineage | Bundle | Orbit", at_x: float) -> RegionMembership:
    return self.add_member(target, at_x)

  def leave(self, target: "Lineage | Bundle | Orbit", at_x: float) -> None:
    if not math.isfinite(at_x):
      raise ValueError("Region membership coordinates must be finite")
    active = next((
      membership for membership in reversed(self._memberships)
      if membership.target is target
      and membership.start_x < at_x
      and membership.end_x is None
    ), None)
    if active is None:
      raise ValueError("Cannot leave a Region while the target is not an active member")
    active.end_x = float(at_x)

  def shade(self, from_x: float, to_x: float, color: str):
    if not all(math.isfinite(value) for value in (from_x, to_x)) or to_x < from_x:
      raise ValueError("Region shade end must not precede its finite start")
    self._shade_events.append(ShadeEvent(from_x, to_x, color))

  def fade(self, from_x: float, to_x: float, opacity: float):
    if not all(math.isfinite(value) for value in (from_x, to_x)) or to_x < from_x:
      raise ValueError("Region fade end must not precede its finite start")
    if not math.isfinite(opacity) or not 0 <= opacity <= 1:
      raise ValueError("Region fill opacity must be between 0 and 1")
    self._opacity_events.append(ScaleEvent(from_x, to_x, opacity))

  def _membership_active(self, membership: RegionMembership, x: float, side: BoundarySide) -> bool:
    end_x = membership.end_x if membership.end_x is not None else self.diagram.view_width
    return _active_at(membership.start_x, end_x, x, side)

  def _assembly_lineages(self, assembly, x: float, side: BoundarySide) -> list["Lineage"]:
    from .bundle import Bundle
    from .orbit import Orbit

    if isinstance(assembly, Bundle) and not _active_at(
      assembly.start_x, assembly.end_x, x, side
    ):
      return []
    lineages = []
    if isinstance(assembly, Orbit) and _lineage_active_at(assembly.main_lineage, x, side):
      lineages.append(assembly.main_lineage)
    for membership in assembly.memberships:
      if _active_at(membership.start_x, membership.end_x, x, side):
        if _lineage_active_at(membership.lineage, x, side):
          lineages.append(membership.lineage)
    return lineages

  def _target_lineages(self, target, x: float, side: BoundarySide) -> list["Lineage"]:
    from .bundle import Bundle
    from .lineage import Lineage
    from .orbit import Orbit

    if isinstance(target, Lineage):
      if not _lineage_active_at(target, x, side):
        return []
      layout_parent = target.layout_parent_at(x, side)
      if layout_parent is not None:
        return self._assembly_lineages(layout_parent, x, side)
      return [target]
    if isinstance(target, (Bundle, Orbit)):
      return self._assembly_lineages(target, x, side)
    return []

  @staticmethod
  def _polyline_intersections(points: list[complex], x: float, side: BoundarySide) -> list[float]:
    values = []
    for first, second in zip(points, points[1:]):
      delta_x = second.real - first.real
      if abs(delta_x) <= 1e-12:
        if abs(x - first.real) <= 1e-9:
          values.append(first.imag if side == BoundarySide.LEFT else second.imag)
        continue
      if delta_x > 0:
        contains_x = (
          first.real < x <= second.real
          if side == BoundarySide.LEFT
          else first.real <= x < second.real
        )
      else:
        contains_x = min(first.real, second.real) <= x <= max(first.real, second.real)
      if contains_x:
        ratio = (x - first.real) / delta_x
        if -1e-9 <= ratio <= 1 + 1e-9:
          values.append(first.imag + (second.imag - first.imag) * ratio)
    return values

  @staticmethod
  def _cap_intersections(first: complex, second: complex, x: float) -> list[float]:
    delta_x = second.real - first.real
    if abs(delta_x) <= 1e-12:
      return [first.imag, second.imag] if abs(x - first.real) <= 1e-9 else []
    if min(first.real, second.real) - 1e-9 <= x <= max(first.real, second.real) + 1e-9:
      ratio = (x - first.real) / delta_x
      if -1e-9 <= ratio <= 1 + 1e-9:
        return [first.imag + (second.imag - first.imag) * ratio]
    return []

  def _compile_lineage_boundary(self, lineage: "Lineage") -> tuple[_BoundarySegment, ...]:
    if lineage in self._compiled_boundaries:
      return self._compiled_boundaries[lineage]
    if not lineage._compiled_samples:
      lineage.compile_geometry()
    samples = lineage._compiled_samples
    self._lineage_discontinuities[lineage] = {
      second.source_x
      for first, second in zip(samples, samples[1:])
      if abs(first.source_x - second.source_x) <= 1e-9
      and (
        abs(first.upper - second.upper) > 1e-9
        or abs(first.lower - second.lower) > 1e-9
      )
    }
    upper = [sample.upper for sample in samples]
    lower = [sample.lower for sample in samples]
    self._compiled_edges[lineage] = (upper, lower)
    segments = []
    for edge, points in (("upper", upper), ("lower", lower)):
      for index, (first, second) in enumerate(zip(points, points[1:])):
        segments.append(_BoundarySegment(
          first,
          second,
          f"{lineage.id}:{edge}",
          samples[index].source_x,
          samples[index + 1].source_x,
        ))
    if samples:
      segments.extend((
        _BoundarySegment(
          samples[0].upper,
          samples[0].lower,
          f"{lineage.id}:start-cap",
          samples[0].source_x,
          samples[0].source_x,
        ),
        _BoundarySegment(
          samples[-1].upper,
          samples[-1].lower,
          f"{lineage.id}:end-cap",
          samples[-1].source_x,
          samples[-1].source_x,
        ),
      ))
    self._compiled_boundaries[lineage] = tuple(segments)
    bucket_size = max(
      1.0,
      self._buffer_radius,
      self.diagram.view_width / max(1, self.diagram.resolution - 1) * 4,
    )
    buckets = {}
    for segment in segments:
      first_bucket = math.floor((min(segment.first.real, segment.second.real) - self._buffer_radius) / bucket_size)
      last_bucket = math.floor((max(segment.first.real, segment.second.real) + self._buffer_radius) / bucket_size)
      for bucket in range(first_bucket, last_bucket + 1):
        buckets.setdefault(bucket, []).append(segment)
    self._boundary_buckets[lineage] = (
      bucket_size,
      {key: tuple(value) for key, value in buckets.items()},
    )
    return self._compiled_boundaries[lineage]

  @property
  def _clearance(self) -> float:
    return self.padding + self.diagram.lineage_stroke_width / 2

  @property
  def _buffer_radius(self) -> float:
    # A small outward guard keeps sampled chords outside the contract radius.
    if self._clearance == 0:
      return 0.0
    return self._clearance + 1e-2

  def _lineage_vertical_bounds(
      self,
      lineage: "Lineage",
      x: float,
      side: BoundarySide,
    ) -> tuple[float, float, str, str]:
    radius = self._buffer_radius
    intervals = []
    self._compile_lineage_boundary(lineage)
    bucket_size, buckets = self._boundary_buckets[lineage]
    candidates = buckets.get(math.floor(x / bucket_size), ())
    is_event = x in self._lineage_discontinuities.get(lineage, ())
    for index, segment in enumerate(candidates):
      if x < min(segment.first.real, segment.second.real) - radius - 1e-9:
        continue
      if x > max(segment.first.real, segment.second.real) + radius + 1e-9:
        continue
      if is_event and abs(segment.first_source_x - segment.second_source_x) > 1e-12:
        if side == BoundarySide.LEFT and min(segment.first_source_x, segment.second_source_x) >= x:
          continue
        if side == BoundarySide.RIGHT and max(segment.first_source_x, segment.second_source_x) <= x:
          continue
      interval = _capsule_vertical_interval(segment, x, radius, side)
      if interval is not None:
        intervals.append((float(interval[0]), float(interval[1]), segment.source, index))
    if intervals:
      upper = min(intervals, key=lambda item: (item[0], item[2], item[3]))
      lower = max(intervals, key=lambda item: (item[1], item[2], -item[3]))
      return upper[0], lower[1], upper[2], lower[2]

    frame = lineage.frame_at(x, side)
    upper = float(min(frame.upper.imag, frame.lower.imag) - radius)
    lower = float(max(frame.upper.imag, frame.lower.imag) + radius)
    return upper, lower, f"{lineage.id}:frame", f"{lineage.id}:frame"

  def _envelope_at(self, x: float, side: BoundarySide) -> _RegionEnvelope | None:
    lineages = {}
    for membership in self._memberships:
      if not self._membership_active(membership, x, side):
        continue
      for lineage in self._target_lineages(membership.target, x, side):
        lineages[lineage.id] = lineage
    if not lineages:
      return None

    candidates = []
    for lineage in (lineages[key] for key in sorted(lineages)):
      candidates.append(self._lineage_vertical_bounds(lineage, x, side))
    upper = min(candidates, key=lambda item: (item[0], item[2]))
    lower = max(candidates, key=lambda item: (item[1], item[3]))
    return _RegionEnvelope(upper[0], lower[1], upper[2], lower[3])

  def _bounds_at(self, x: float, side: BoundarySide) -> tuple[float, float] | None:
    envelope = self._envelope_at(x, side)
    if envelope is None:
      return None
    return envelope.upper_y, envelope.lower_y

  def _possible_lineages(self) -> set["Lineage"]:
    from .bundle import Bundle
    from .lineage import Lineage
    from .orbit import Orbit

    lineages = set()
    assemblies = set()
    for membership in self._memberships:
      if isinstance(membership.target, Lineage):
        lineages.add(membership.target)
        for assembly in (*self.diagram._bundles, *self.diagram._orbits):
          if any(item.lineage is membership.target for item in assembly.memberships):
            assemblies.add(assembly)
      elif isinstance(membership.target, (Bundle, Orbit)):
        assemblies.add(membership.target)
    for assembly in assemblies:
      if isinstance(assembly, Orbit):
        lineages.add(assembly.main_lineage)
      lineages.update(membership.lineage for membership in assembly.memberships)
    return lineages

  def compile(self):
    self._components = []
    self._compiled_edges = {}
    self._compiled_boundaries = {}
    self._boundary_buckets = {}
    self._lineage_discontinuities = {}
    self._event_xs = set(diagram_event_xs(self.diagram))
    if not self._memberships:
      return

    possible_lineages = self._possible_lineages()
    for lineage in possible_lineages:
      self._compile_lineage_boundary(lineage)

    membership_xs = {
      value
      for membership in self._memberships
      for value in (
        membership.start_x,
        membership.end_x if membership.end_x is not None else self.diagram.view_width,
      )
    }
    event_xs = self._event_xs | membership_xs
    self._event_xs = event_xs
    resolution = max(2, int(self.diagram.resolution))
    active_start_x = max(0, min(membership.start_x for membership in self._memberships))
    active_end_x = min(self.diagram.view_width, max(
      membership.end_x if membership.end_x is not None else self.diagram.view_width
      for membership in self._memberships
    ))
    sample_xs = {
      self.diagram.view_width * index / (resolution - 1)
      for index in range(resolution)
    }
    radius = self._buffer_radius
    geometry_xs = set()
    for lineage in possible_lineages:
      samples = lineage._compiled_samples
      for edge in ("upper", "lower"):
        points = [getattr(sample, edge) for sample in samples]
        critical_indices = {0, len(points) - 1} if points else set()
        for index in range(1, len(points) - 1):
          before = points[index] - points[index - 1]
          after = points[index + 1] - points[index]
          if abs(before) <= 1e-12 or abs(after) <= 1e-12:
            critical_indices.add(index)
            continue
          before /= abs(before)
          after /= abs(after)
          cosine = max(-1.0, min(1.0, before.real * after.real + before.imag * after.imag))
          if math.acos(cosine) >= math.radians(5):
            critical_indices.add(index)
        for index in critical_indices:
          point_x = points[index].real
          geometry_xs.update((point_x - radius, point_x, point_x + radius))
    xs = sorted(
      x for x in event_xs | sample_xs | geometry_xs
      if active_start_x <= x <= active_end_x
    )

    source_xs = set()
    for first_x, second_x in zip(xs, xs[1:]):
      first = self._envelope_at(first_x, BoundarySide.RIGHT)
      second_side = BoundarySide.LEFT if second_x in event_xs else BoundarySide.RIGHT
      second = self._envelope_at(second_x, second_side)
      if first is None or second is None:
        continue
      for attribute in ("upper_source", "lower_source"):
        first_source = getattr(first, attribute)
        if first_source == getattr(second, attribute):
          continue
        low, high = first_x, second_x
        for _ in range(30):
          middle = (low + high) / 2
          envelope = self._envelope_at(middle, BoundarySide.RIGHT)
          if envelope is not None and getattr(envelope, attribute) == first_source:
            low = middle
          else:
            high = middle
        source_xs.add((low + high) / 2)
    xs = sorted({*xs, *source_xs})

    # Refine where a chord would cut inside the buffered envelope or where the
    # winning edge curves. This keeps clearance independent of Region sampling.
    for _ in range(14):
      additions = set()
      for first_x, second_x in zip(xs, xs[1:]):
        if second_x - first_x <= 1e-5:
          continue
        first = self._envelope_at(first_x, BoundarySide.RIGHT)
        second_side = BoundarySide.LEFT if second_x in event_xs else BoundarySide.RIGHT
        second = self._envelope_at(second_x, second_side)
        middle_x = (first_x + second_x) / 2
        middle = self._envelope_at(middle_x, BoundarySide.RIGHT)
        if (first is None) != (middle is None) or (middle is None) != (second is None):
          additions.add(middle_x)
          continue
        if first is None or middle is None or second is None:
          continue
        ratio = (middle_x - first_x) / (second_x - first_x)
        chord_upper = first.upper_y + (second.upper_y - first.upper_y) * ratio
        chord_lower = first.lower_y + (second.lower_y - first.lower_y) * ratio
        cuts_inward = (
          chord_upper > middle.upper_y + 5e-3
          or chord_lower < middle.lower_y - 5e-3
        )
        if cuts_inward:
          additions.add(middle_x)
      if not additions:
        break
      xs = sorted({*xs, *additions})

    raw_components: list[list[RegionEnvelopePoint]] = []
    current: list[RegionEnvelopePoint] | None = None

    def append_envelope(x: float, envelope: _RegionEnvelope, side: BoundarySide):
      nonlocal current
      point = RegionEnvelopePoint(
        x,
        envelope.upper_y,
        envelope.lower_y,
        side,
        envelope.upper_source,
        envelope.lower_source,
      )
      if current is None:
        current = [point]
      elif current[-1] != point:
        current.append(point)

    def finish_component():
      nonlocal current
      if current is not None and len({point.x for point in current}) >= 2:
        raw_components.append(current)
      current = None

    for x in xs:
      if x in event_xs:
        left = self._envelope_at(x, BoundarySide.LEFT)
        right = self._envelope_at(x, BoundarySide.RIGHT)
        if left is not None:
          append_envelope(x, left, BoundarySide.LEFT)
        elif current is not None:
          finish_component()

        if right is None:
          finish_component()
        elif left is None:
          append_envelope(x, right, BoundarySide.RIGHT)
        elif not _same_envelope(
          (left.upper_y, left.lower_y),
          (right.upper_y, right.lower_y),
        ):
          append_envelope(x, right, BoundarySide.RIGHT)
      else:
        envelope = self._envelope_at(x, BoundarySide.RIGHT)
        if envelope is None:
          finish_component()
        else:
          append_envelope(x, envelope, BoundarySide.RIGHT)
    finish_component()

    self._components = [
      RegionComponent(
        tuple(points),
        _rounded_polygon_path(
          tuple(points),
          min(self.corner_radius, self.padding),
          min(self.event_corner_radius, self.padding),
        ),
      )
      for points in raw_components
    ]

  def _gradient_definition(self) -> tuple[str, str, float]:
    if not self._shade_events and not self._opacity_events:
      return "", self.fill, self.fill_opacity

    color_timeline = ColorTimeline(self.fill, self._shade_events)
    opacity_timeline = NumericTimeline(self.fill_opacity, self._opacity_events, "to_w")
    xs = {0.0, self.diagram.view_width}
    for transition in color_timeline.transitions:
      xs.update((transition.from_x, transition.to_x))
    for transition in opacity_timeline.transitions:
      xs.update(
        transition.from_x + (transition.to_x - transition.from_x) * fraction
        for fraction in (0.0, 0.25, 0.5, 0.75, 1.0)
      )
    step_xs = {
      transition.from_x
      for transition in (*color_timeline.transitions, *opacity_timeline.transitions)
      if transition.from_x == transition.to_x
    }
    stops = []
    for x in sorted(xs):
      offset = max(0, min(100, x / self.diagram.view_width * 100))
      sides = (BoundarySide.LEFT, BoundarySide.RIGHT) if x in step_xs else (BoundarySide.RIGHT,)
      for side in sides:
        color = color_timeline.value_at(x, side)
        opacity = opacity_timeline.value_at(x, side)
        stops.append(f'<stop offset="{offset}%" stop-color="{color}" stop-opacity="{opacity}"/>')
    gradient_id = f"gradient-{self.id}"
    definition = (
      f'<linearGradient id="{gradient_id}" gradientUnits="userSpaceOnUse" '
      f'x1="0" x2="{self.diagram.view_width}" y1="0" y2="0">'
      f'{"".join(stops)}</linearGradient>'
    )
    return definition, f"url(#{gradient_id})", 1.0

  def draw(self) -> str:
    if not self._components:
      return ""

    definitions = []
    gradient_definition, fill, fill_opacity = self._gradient_definition()
    if gradient_definition:
      definitions.append(gradient_definition)

    hatch_fill = None
    if self.hatch is not None:
      pattern_id = f"pattern-{self.id}"
      definitions.append(
        f'<pattern id="{pattern_id}" width="{self.hatch.spacing}" height="{self.hatch.spacing}" '
        f'patternUnits="userSpaceOnUse" patternTransform="rotate({self.hatch.angle})">'
        f'<line x1="0" y1="0" x2="0" y2="{self.hatch.spacing}" '
        f'stroke="{html.escape(self.hatch.color, quote=True)}" stroke-opacity="{self.hatch.opacity}" '
        f'stroke-width="{self.hatch.width}"/></pattern>'
      )
      hatch_fill = f"url(#{pattern_id})"

    lines = [f'<g id="{self.id}">']
    if definitions:
      lines.append(f'<defs>{"".join(definitions)}</defs>')
    for index, component in enumerate(self._components):
      if not component.path_d:
        continue
      lines.append(
        f'<path id="{self.id}-component-{index}-fill" fill="{html.escape(fill, quote=True)}" '
        f'fill-opacity="{fill_opacity}" stroke="none" d="{component.path_d}"/>'
      )
      if hatch_fill is not None:
        lines.append(
          f'<path id="{self.id}-component-{index}-hatch" fill="{hatch_fill}" '
          f'stroke="none" d="{component.path_d}"/>'
        )
      if self.stroke is not None and self.stroke.width > 0:
        dash = (
          f' stroke-dasharray="{" ".join(str(value) for value in self.stroke.dasharray)}"'
          if self.stroke.dasharray else ""
        )
        lines.append(
          f'<path id="{self.id}-component-{index}-outline" fill="none" '
          f'stroke="{html.escape(self.stroke.color, quote=True)}" stroke-width="{self.stroke.width}" '
          f'stroke-opacity="{self.stroke.opacity}" stroke-linejoin="round"{dash} '
          f'd="{component.path_d}"/>'
        )
    lines.append("</g>")
    return "".join(lines)
