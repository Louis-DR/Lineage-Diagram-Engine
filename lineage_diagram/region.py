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


@dataclass(frozen=True)
class RegionComponent:
  points: tuple[RegionEnvelopePoint, ...]
  path_d: str


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


def _rounded_polygon_path(
    points: tuple[RegionEnvelopePoint, ...],
    corner_radius: float,
    event_corner_radius: float,
  ) -> str:
  upper = [complex(point.x, point.upper_y) for point in points]
  lower = [complex(point.x, point.lower_y) for point in reversed(points)]
  entries = [[point, 0.0] for point in (*upper, *lower)]
  upper_count = len(upper)

  # Start and end caps are the ordinary rounded corners.
  for index in (0, upper_count - 1, upper_count, len(entries) - 1):
    entries[index][1] = max(entries[index][1], corner_radius)

  # Duplicate timeline coordinates encode an intentional membership step.
  for start, end in ((0, upper_count), (upper_count, len(entries))):
    for index in range(start + 1, end):
      if abs(entries[index - 1][0].real - entries[index][0].real) <= 1e-9:
        entries[index - 1][1] = max(entries[index - 1][1], event_corner_radius)
        entries[index][1] = max(entries[index][1], event_corner_radius)

  compact = []
  for point, radius in entries:
    if compact and _distance(compact[-1][0], point) <= 1e-12:
      compact[-1][1] = max(compact[-1][1], radius)
    else:
      compact.append([point, radius])
  if len(compact) > 1 and _distance(compact[0][0], compact[-1][0]) <= 1e-12:
    compact[0][1] = max(compact[0][1], compact[-1][1])
    compact.pop()
  if len(compact) < 3:
    return ""

  incoming = []
  outgoing = []
  for index, (point, radius) in enumerate(compact):
    previous = compact[index - 1][0]
    following = compact[(index + 1) % len(compact)][0]
    trim = min(radius, _distance(point, previous) / 2, _distance(point, following) / 2)
    incoming.append(_towards(point, previous, trim))
    outgoing.append(_towards(point, following, trim))

  start = outgoing[0]
  commands = [f"M {start.real} {start.imag}"]
  for index in (*range(1, len(compact)), 0):
    point, radius = compact[index]
    in_point = incoming[index]
    out_point = outgoing[index]
    commands.append(f"L {in_point.real} {in_point.imag}")
    if radius > 0 and _distance(in_point, out_point) > 1e-12:
      commands.append(f"Q {point.real} {point.imag} {out_point.real} {out_point.imag}")
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
    diagram.add_region(self)

  @property
  def memberships(self) -> tuple[RegionMembership, ...]:
    return tuple(self._memberships)

  @property
  def components(self) -> tuple[RegionComponent, ...]:
    return tuple(self._components)

  def _validate_target(self, target):
    from .bundle import Bundle
    from .lineage import Lineage
    from .orbit import Orbit

    if not isinstance(target, (Lineage, Bundle, Orbit)):
      raise TypeError("Region members must be Lineage, Bundle, or Orbit instances")
    if target.diagram is not self.diagram:
      raise ValueError("Region members must belong to the same diagram")

  def add_member(self, target, start_x: float, end_x: float | None = None):
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

  def join(self, target, at_x: float):
    return self.add_member(target, at_x)

  def leave(self, target, at_x: float):
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

  def _lineage_vertical_bounds(self, lineage: "Lineage", x: float, side: BoundarySide) -> tuple[float, float]:
    if lineage not in self._compiled_edges:
      upper = []
      lower = []
      for segment in lineage._computed_segments:
        segment_upper, segment_lower = segment.compile()
        upper.extend(segment_upper)
        lower.extend(segment_lower)
      self._compiled_edges[lineage] = (upper, lower)
    upper, lower = self._compiled_edges[lineage]
    values = [
      *self._polyline_intersections(upper, x, side),
      *self._polyline_intersections(lower, x, side),
    ]
    if upper and lower:
      values.extend(self._cap_intersections(upper[0], lower[0], x))
      values.extend(self._cap_intersections(upper[-1], lower[-1], x))
    if values:
      return min(values), max(values)

    # Sparse endpoint sampling can leave a sub-pixel gap at a lifecycle cap.
    frame = lineage.frame_at(x, side)
    return min(frame.upper.imag, frame.lower.imag), max(frame.upper.imag, frame.lower.imag)

  def _bounds_at(self, x: float, side: BoundarySide) -> tuple[float, float] | None:
    lineages = {}
    for membership in self._memberships:
      if not self._membership_active(membership, x, side):
        continue
      for lineage in self._target_lineages(membership.target, x, side):
        lineages[lineage.id] = lineage
    if not lineages:
      return None

    upper_y = math.inf
    lower_y = -math.inf
    for lineage in (lineages[key] for key in sorted(lineages)):
      lineage_upper, lineage_lower = self._lineage_vertical_bounds(lineage, x, side)
      upper_y = min(upper_y, lineage_upper)
      lower_y = max(lower_y, lineage_lower)
    return upper_y - self.padding, lower_y + self.padding

  def compile(self):
    self._components = []
    self._compiled_edges = {}
    if not self._memberships:
      return

    membership_xs = {
      value
      for membership in self._memberships
      for value in (
        membership.start_x,
        membership.end_x if membership.end_x is not None else self.diagram.view_width,
      )
    }
    event_xs = set(diagram_event_xs(self.diagram)) | membership_xs
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
    xs = sorted(
      x for x in event_xs | sample_xs
      if active_start_x <= x <= active_end_x
    )

    raw_components: list[list[RegionEnvelopePoint]] = []
    current: list[RegionEnvelopePoint] | None = None

    def append_bounds(x: float, bounds: tuple[float, float], side: BoundarySide):
      nonlocal current
      point = RegionEnvelopePoint(x, bounds[0], bounds[1], side)
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
        left = self._bounds_at(x, BoundarySide.LEFT)
        right = self._bounds_at(x, BoundarySide.RIGHT)
        if left is not None:
          append_bounds(x, left, BoundarySide.LEFT)
        elif current is not None:
          finish_component()

        if right is None:
          finish_component()
        elif left is None:
          append_bounds(x, right, BoundarySide.RIGHT)
        elif not _same_envelope(left, right):
          append_bounds(x, right, BoundarySide.RIGHT)
      else:
        bounds = self._bounds_at(x, BoundarySide.RIGHT)
        if bounds is None:
          finish_component()
        else:
          append_bounds(x, bounds, BoundarySide.RIGHT)
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
