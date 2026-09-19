from dataclasses import dataclass
from enum import Enum
import math

import svgpathtools as svg

from .utils import find_t_at_x, smootherstep


class BoundarySide(Enum):
  LEFT = "left"
  RIGHT = "right"


@dataclass(frozen=True)
class NumericTransition:
  from_x: float
  to_x: float
  base_start_value: float
  base_target_value: float
  from_u: float = 0.0
  to_u: float = 1.0

  @property
  def start_value(self) -> float:
    return self._value_at_u(self.from_u)

  @property
  def target_value(self) -> float:
    return self._value_at_u(self.to_u)

  def _value_at_u(self, ratio: float) -> float:
    return self.base_start_value + (self.base_target_value - self.base_start_value) * smootherstep(ratio)

  def value_at(self, x: float, side: BoundarySide = BoundarySide.RIGHT) -> float:
    if self.from_x == self.to_x:
      if x < self.from_x or (x == self.from_x and side == BoundarySide.LEFT):
        return self.start_value
      return self.target_value
    if x <= self.from_x:
      return self.start_value
    if x >= self.to_x:
      return self.target_value
    ratio = (x - self.from_x) / (self.to_x - self.from_x)
    source_ratio = self.from_u + (self.to_u - self.from_u) * ratio
    return self._value_at_u(source_ratio)

  def crop_to_x(self, from_x: float, to_x: float) -> "NumericTransition":
    span = self.to_x - self.from_x
    from_ratio = (from_x - self.from_x) / span
    to_ratio = (to_x - self.from_x) / span
    return NumericTransition(
      from_x,
      to_x,
      self.base_start_value,
      self.base_target_value,
      self.from_u + (self.to_u - self.from_u) * from_ratio,
      self.from_u + (self.to_u - self.from_u) * to_ratio,
    )


class NumericTimeline:
  """Normalized scalar transitions with later-command interruption semantics."""

  def __init__(self, initial_value: float, events, target_attribute: str):
    self.initial_value = float(initial_value)
    self.transitions: list[NumericTransition] = []
    for event in events:
      target = float(getattr(event, target_attribute))
      self._overlay(float(event.from_x), float(event.to_x), target)

  def _overlay(self, from_x: float, to_x: float, target: float):
    if not all(math.isfinite(value) for value in (from_x, to_x, target)):
      raise ValueError("Timeline coordinates and values must be finite")
    if to_x < from_x:
      raise ValueError("Timeline transition end must not precede its start")

    start_value = self.value_at(from_x, BoundarySide.LEFT)
    interrupted = next(
      (transition for transition in self.transitions if transition.from_x < to_x < transition.to_x),
      None,
    )
    updated = []
    for transition in self.transitions:
      if transition.to_x <= from_x or transition.from_x >= to_x:
        updated.append(transition)
      elif transition.from_x < from_x:
        updated.append(transition.crop_to_x(transition.from_x, from_x))

    updated.append(NumericTransition(from_x, to_x, start_value, target))
    if interrupted is not None and interrupted.to_x > to_x:
      updated.append(NumericTransition(to_x, interrupted.to_x, target, interrupted.target_value))
    self.transitions = sorted(updated, key=lambda transition: (transition.from_x, transition.to_x))

  def value_at(self, x: float, side: BoundarySide = BoundarySide.RIGHT) -> float:
    value = self.initial_value
    for transition in self.transitions:
      if x < transition.from_x or (x == transition.from_x and side == BoundarySide.LEFT):
        return value
      if transition.from_x == transition.to_x:
        if x > transition.from_x or side == BoundarySide.RIGHT:
          value = transition.target_value
        continue
      if x < transition.to_x:
        return transition.value_at(x, side)
      if x == transition.to_x and side == BoundarySide.LEFT:
        return transition.value_at(x, side)
      value = transition.target_value
    return value

  @property
  def boundaries(self) -> tuple[float, ...]:
    return tuple(sorted({value for transition in self.transitions for value in (transition.from_x, transition.to_x)}))


_NAMED_COLORS = {
  "black": (0, 0, 0),
  "blue": (0, 0, 255),
  "darkgoldenrod": (184, 134, 11),
  "darkseagreen": (143, 188, 143),
  "gold": (255, 215, 0),
  "goldenrod": (218, 165, 32),
  "gray": (128, 128, 128),
  "green": (0, 128, 0),
  "grey": (128, 128, 128),
  "orange": (255, 165, 0),
  "purple": (128, 0, 128),
  "red": (255, 0, 0),
  "indianred": (205, 92, 92),
  "seagreen": (46, 139, 87),
  "steelblue": (70, 130, 180),
  "white": (255, 255, 255),
  "yellow": (255, 255, 0),
}


def _parse_color(color: str) -> tuple[int, int, int]:
  value = color.lower()
  if value in _NAMED_COLORS:
    return _NAMED_COLORS[value]
  if value.startswith("#") and len(value) == 4:
    return tuple(int(character * 2, 16) for character in value[1:])
  if value.startswith("#") and len(value) == 7:
    return tuple(int(value[index:index + 2], 16) for index in (1, 3, 5))
  raise ValueError(f"Overlapping color transitions require a hex or supported named color, got {color!r}")


def _format_color(color: tuple[float, float, float]) -> str:
  return "#" + "".join(f"{round(channel):02x}" for channel in color)


@dataclass(frozen=True)
class ColorTransition:
  from_x: float
  to_x: float
  base_start: tuple[int, int, int]
  base_target: tuple[int, int, int]
  from_u: float = 0.0
  to_u: float = 1.0

  def _value_at_u(self, ratio: float) -> tuple[float, float, float]:
    return tuple(start + (target - start) * ratio for start, target in zip(self.base_start, self.base_target))

  @property
  def start_color(self) -> tuple[float, float, float]:
    return self._value_at_u(self.from_u)

  @property
  def target_color(self) -> tuple[float, float, float]:
    return self._value_at_u(self.to_u)

  def value_at(self, x: float) -> tuple[float, float, float]:
    if x <= self.from_x:
      return self.start_color
    if x >= self.to_x:
      return self.target_color
    ratio = (x - self.from_x) / (self.to_x - self.from_x)
    return self._value_at_u(self.from_u + (self.to_u - self.from_u) * ratio)

  def crop_to_x(self, to_x: float) -> "ColorTransition":
    ratio = (to_x - self.from_x) / (self.to_x - self.from_x)
    return ColorTransition(
      self.from_x,
      to_x,
      self.base_start,
      self.base_target,
      self.from_u,
      self.from_u + (self.to_u - self.from_u) * ratio,
    )


class ColorTimeline:
  def __init__(self, initial_color: str, events):
    self.initial_color = _parse_color(initial_color)
    self.transitions: list[ColorTransition] = []
    for event in events:
      self._overlay(float(event.from_x), float(event.to_x), _parse_color(event.color))

  def _overlay(self, from_x: float, to_x: float, target: tuple[int, int, int]):
    if to_x < from_x:
      raise ValueError("Color transition end must not precede its start")
    start = self._rgb_at(from_x, BoundarySide.LEFT)
    interrupted = next(
      (transition for transition in self.transitions if transition.from_x < to_x < transition.to_x),
      None,
    )
    updated = []
    for transition in self.transitions:
      if transition.to_x <= from_x or transition.from_x >= to_x:
        updated.append(transition)
      elif transition.from_x < from_x:
        updated.append(transition.crop_to_x(from_x))
    updated.append(ColorTransition(from_x, to_x, tuple(round(value) for value in start), target))
    if interrupted is not None and interrupted.to_x > to_x:
      updated.append(ColorTransition(
        to_x,
        interrupted.to_x,
        target,
        tuple(round(value) for value in interrupted.target_color),
      ))
    self.transitions = sorted(updated, key=lambda transition: (transition.from_x, transition.to_x))

  def _rgb_at(self, x: float, side: BoundarySide) -> tuple[float, float, float]:
    color = self.initial_color
    for transition in self.transitions:
      if x < transition.from_x or (x == transition.from_x and side == BoundarySide.LEFT):
        return color
      if x < transition.to_x:
        return transition.value_at(x)
      if x == transition.to_x and side == BoundarySide.LEFT:
        return transition.value_at(x)
      color = transition.target_color
    return color

  def value_at(self, x: float, side: BoundarySide = BoundarySide.RIGHT) -> str:
    return _format_color(self._rgb_at(x, side))

  def stops(self, end_x: float) -> tuple[tuple[float, str], ...]:
    stops = [(0.0, _format_color(self.initial_color))]
    for transition in self.transitions:
      stops.append((transition.from_x, _format_color(transition.start_color)))
      stops.append((transition.to_x, _format_color(transition.target_color)))
    stops.append((end_x, self.value_at(end_x)))
    return tuple(sorted(stops, key=lambda item: item[0]))


@dataclass(frozen=True)
class PositionPiece:
  segment: svg.CubicBezier

  @property
  def from_x(self) -> float:
    return float(self.segment.start.real)

  @property
  def to_x(self) -> float:
    return float(self.segment.end.real)

  @property
  def start_y(self) -> float:
    return float(self.segment.start.imag)

  @property
  def target_y(self) -> float:
    return float(self.segment.end.imag)

  def point_at_x(self, x: float) -> complex:
    if x <= self.from_x:
      return self.segment.start
    if x >= self.to_x:
      return self.segment.end
    path = svg.Path(self.segment)
    return self.segment.point(find_t_at_x(path, x))

  def crop_to_x(self, from_x: float, to_x: float) -> "PositionPiece":
    path = svg.Path(self.segment)
    start_t = find_t_at_x(path, from_x)
    end_t = find_t_at_x(path, to_x)
    return PositionPiece(self.segment.cropped(start_t, end_t))

  def slope_at_x(self, x: float) -> float:
    path = svg.Path(self.segment)
    t = find_t_at_x(path, x, tolerance=1e-10)
    derivative = self.segment.derivative(t)
    if abs(derivative.real) < 1e-12:
      return 0.0
    return float(derivative.imag / derivative.real)


def _position_segment(
  from_x: float,
  to_x: float,
  start_y: float,
  target_y: float,
  start_slope: float = 0.0,
  end_slope: float = 0.0,
) -> svg.CubicBezier:
  midpoint_x = (from_x + to_x) / 2
  control_distance = (to_x - from_x) / 2
  return svg.CubicBezier(
    complex(from_x, start_y),
    complex(midpoint_x, start_y + start_slope * control_distance),
    complex(midpoint_x, target_y - end_slope * control_distance),
    complex(to_x, target_y),
  )


class PositionTimeline:
  """Normalized horizontal-tangent cubic position transitions."""

  def __init__(self, start_x: float, start_y: float, events):
    self.start_x = float(start_x)
    self.start_y = float(start_y)
    self.pieces: list[PositionPiece] = []
    self.steps: list[tuple[float, float]] = []
    for event in events:
      target_y = (event.to_y if event.to_y is not None else 0.0) + event.offset_y
      self._overlay(float(event.from_x), float(event.to_x), float(target_y))

  def _overlay(self, from_x: float, to_x: float, target_y: float):
    if not all(math.isfinite(value) for value in (from_x, to_x, target_y)):
      raise ValueError("Timeline coordinates and positions must be finite")
    if to_x < from_x:
      raise ValueError("Timeline transition end must not precede its start")

    start_y = self.value_at(from_x, BoundarySide.LEFT)
    if from_x == to_x:
      # A step ends any in-flight position transition. Later commands build a
      # new run from this explicit right-side state.
      updated = []
      for piece in self.pieces:
        if piece.to_x <= from_x:
          updated.append(piece)
        elif piece.from_x < from_x:
          updated.append(piece.crop_to_x(piece.from_x, from_x))
      self.pieces = updated
      self.steps = [(x, value) for x, value in self.steps if x != from_x]
      self.steps.append((from_x, target_y))
      self.steps.sort()
      return

    start_piece = next((piece for piece in self.pieces if piece.from_x < from_x < piece.to_x), None)
    interrupted = next((piece for piece in self.pieces if piece.from_x < to_x < piece.to_x), None)
    start_slope = start_piece.slope_at_x(from_x) if start_piece is not None else 0.0
    updated = []
    for piece in self.pieces:
      if piece.to_x <= from_x or piece.from_x >= to_x:
        updated.append(piece)
      elif piece.from_x < from_x:
        updated.append(piece.crop_to_x(piece.from_x, from_x))

    updated.append(PositionPiece(_position_segment(
      from_x,
      to_x,
      start_y,
      target_y,
      start_slope=start_slope,
    )))
    if interrupted is not None and interrupted.to_x > to_x:
      updated.append(PositionPiece(_position_segment(to_x, interrupted.to_x, target_y, interrupted.target_y)))
    self.pieces = sorted(updated, key=lambda piece: (piece.from_x, piece.to_x))

  def value_at(self, x: float, side: BoundarySide = BoundarySide.RIGHT) -> float:
    value = self.start_y
    pieces = iter(self.pieces)
    steps = iter(sorted(self.steps))
    pending_piece = next(pieces, None)
    pending_step = next(steps, None)

    while pending_piece is not None or pending_step is not None:
      piece_x = pending_piece.from_x if pending_piece is not None else math.inf
      step_x = pending_step[0] if pending_step is not None else math.inf
      if step_x <= piece_x:
        if x < step_x or (x == step_x and side == BoundarySide.LEFT):
          return value
        value = pending_step[1]
        pending_step = next(steps, None)
        continue

      if x < pending_piece.from_x or (x == pending_piece.from_x and side == BoundarySide.LEFT):
        return value
      if x < pending_piece.to_x:
        return pending_piece.point_at_x(x).imag
      if x == pending_piece.to_x and side == BoundarySide.LEFT:
        return pending_piece.point_at_x(x).imag
      value = pending_piece.target_y
      pending_piece = next(pieces, None)
    return value

  def path_until(self, end_x: float) -> svg.Path:
    path = svg.Path()
    current = complex(self.start_x, self.start_y)
    steps = iter(sorted(self.steps))
    pending_step = next(steps, None)

    for piece in self.pieces:
      if piece.from_x > end_x:
        break
      while pending_step is not None and pending_step[0] <= piece.from_x:
        step_x, step_y = pending_step
        if current.real < step_x:
          path.append(svg.Line(current, complex(step_x, current.imag)))
        next_point = complex(step_x, step_y)
        if current != next_point:
          path.append(svg.Line(complex(step_x, current.imag), next_point))
        current = next_point
        pending_step = next(steps, None)
      if current.real < piece.from_x:
        path.append(svg.Line(current, complex(piece.from_x, current.imag)))
      segment = piece.segment
      if piece.to_x > end_x:
        segment = piece.crop_to_x(piece.from_x, end_x).segment
      path.append(segment)
      current = segment.end
      if current.real >= end_x:
        return path

    while pending_step is not None and pending_step[0] <= end_x:
      step_x, step_y = pending_step
      if current.real < step_x:
        path.append(svg.Line(current, complex(step_x, current.imag)))
      next_point = complex(step_x, step_y)
      if current != next_point:
        path.append(svg.Line(complex(step_x, current.imag), next_point))
      current = next_point
      pending_step = next(steps, None)
    if current.real < end_x:
      path.append(svg.Line(current, complex(end_x, self.value_at(end_x))))
    return path

  @property
  def boundaries(self) -> tuple[float, ...]:
    return tuple(sorted({
      *[value for piece in self.pieces for value in (piece.from_x, piece.to_x)],
      *[x for x, _ in self.steps],
    }))
