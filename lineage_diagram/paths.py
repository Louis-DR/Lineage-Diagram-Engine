import svgpathtools as svg

from dataclasses import dataclass
from enum        import Enum
from typing      import Optional, TYPE_CHECKING, Any

from .utils      import smootherstep

if TYPE_CHECKING:
  from .bundle import Bundle

class MembershipEventType(Enum):
  JOIN  = 0
  LEAVE = 1

@dataclass
class MembershipEvent:
  from_x:   float
  to_x:     float
  type:     MembershipEventType
  assembly: Optional['Bundle'] = None
  target_y: Optional[float]    = None # For leave events
  # Optional dynamic target: leave to this lineage's position + offset
  target_lineage: Optional['Any'] = None
  offset_y:       float           = 0.0

@dataclass
class ShiftEvent:
  from_x: float
  to_x:   float
  to_y:   Optional[float] = None
  # Optional dynamic target: shift to this lineage's position + offset
  target_lineage: Optional['Any'] = None
  offset_y:       float           = 0.0

@dataclass
class ScaleEvent:
  from_x: float
  to_x:   float
  to_w:   float

class PathBase:
  """Base class for paths with a defined lifecycle (start/end)."""
  start_x: float
  end_x:   Optional[float]

class ShiftablePath(PathBase):
  """Path with Y position that can shift."""
  start_y:      float
  shift_events: list[ShiftEvent]

  def get_baseline_path(self) -> svg.Path:
    """Generate the baseline SVG path of the object."""
    baseline_path = svg.Path()
    last_point    = complex(self.start_x, self.start_y)
    # Sort events by time
    self.shift_events.sort(key=lambda shift_event: shift_event.from_x)
    # Iterate over shift events in order
    for shift in self.shift_events:
      start_shift_point = complex(shift.from_x, last_point.imag)
      # Add line from previous shift if not touching
      if start_shift_point != last_point:
        baseline_path.append(svg.Line(last_point, start_shift_point))
      # Compute control points
      # The shift.to_y may be resolved dynamically upstream (in Lineage.compile_segments())
      resolved_to_y = shift.to_y
      # Apply the shift logic using the resolved coordinate
      end_shift_y = (resolved_to_y if resolved_to_y is not None else 0.0) + shift.offset_y
      # Assuming creating code put the base Y in to_y
      end_shift_y = (resolved_to_y if resolved_to_y is not None else 0.0) + shift.offset_y
      end_shift_point = complex(shift.to_x, end_shift_y)
      shift_midpoint_x = (start_shift_point.real + end_shift_point.real) / 2
      # Add cubic Bezier curve corresponding to the shift transformation
      if start_shift_point != end_shift_point:
        baseline_path.append(svg.CubicBezier(
          start_shift_point,
          complex(shift_midpoint_x, start_shift_point.imag),
          complex(shift_midpoint_x, end_shift_point.imag),
          end_shift_point
        ))
      # Update the last point
      last_point = end_shift_point
    # Line to the end of the object
    # Use a large number if end_x is not defined (infinite existence)
    effective_end_x = self.end_x if self.end_x is not None else 999999.0
    end_point = complex(effective_end_x, last_point.imag)
    if end_point != last_point:
      baseline_path.append(svg.Line(last_point, end_point))
    return baseline_path

class ScalablePath(PathBase):
  """Path with X width that can scale."""
  start_w:      float
  scale_events: list[ScaleEvent]

  def get_width_at(self, x: float) -> float:
    """Get the width of the object at X position."""
    # If the object has ended, its width is 0
    if self.end_x is not None and x > self.end_x:
      return 0.0
    # Initial width of the object
    last_width = self.start_w
    # Sort events by time
    self.scale_events.sort(key=lambda scale_event: scale_event.from_x)
    # Iterate over scale transformations in order
    for scale_event in self.scale_events:
      # Before transformation, return width of previous transformation
      if x <= scale_event.from_x:
        return last_width
      # Within transformation, interpolate with smoothing
      elif scale_event.from_x < x < scale_event.to_x:
        x1 = scale_event.from_x
        x2 = scale_event.to_x
        w1 = last_width
        w2 = scale_event.to_w
        ratio_linear = (x - x1) / (x2 - x1)
        ratio_smooth = smootherstep(ratio_linear)
        return w1 + (w2 - w1) * ratio_smooth
      # After transformation, continue to next one
      else:
        last_width = scale_event.to_w
    # Reached the end, return width of last transformation
    return last_width
