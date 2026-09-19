import svgpathtools as svg

from dataclasses import dataclass
from enum        import Enum
from typing      import Optional, TYPE_CHECKING, Any

from .utils      import smootherstep
from .timeline   import NumericTimeline, PositionTimeline

if TYPE_CHECKING:
  from .bundle import Bundle
  from .orbit  import Orbit

class MembershipEventType(Enum):
  JOIN  = 0
  LEAVE = 1

@dataclass
class MembershipEvent:
  from_x:         float
  to_x:           float
  type:           MembershipEventType
  assembly:       Optional['Bundle | Orbit'] = None
  target_y:       Optional[float]    = None # For leave events
  # Optional dynamic target: leave to this lineage's position + offset
  target_lineage: Optional['Any'] = None
  offset_y:       float           = 0.0

@dataclass
class ShiftEvent:
  from_x:         float
  to_x:           float
  to_y:           Optional[float] = None
  # Optional dynamic target: shift to this lineage's position + offset
  target_lineage: Optional['Any'] = None
  offset_y:       float           = 0.0

@dataclass
class ScaleEvent:
  from_x: float
  to_x:   float
  to_w:   float

@dataclass
class ShadeEvent:
  from_x: float
  to_x:   float
  color:  str

class PathBase:
  """Base class for paths with a defined lifecycle (start/end)."""
  start_x: float
  end_x:   Optional[float]

class ShiftablePath(PathBase):
  """Path with Y position that can shift."""
  start_y:       float
  _shift_events: list[ShiftEvent]

  def get_baseline_path(self) -> svg.Path:
    """Generate the baseline SVG path of the object."""
    effective_end_x = self.end_x if self.end_x is not None else 999999.0
    return PositionTimeline(self.start_x, self.start_y, self._shift_events).path_until(effective_end_x)

class ScalablePath(PathBase):
  """Path with X width that can scale."""
  start_w:       float
  _scale_events: list[ScaleEvent]

  def get_width_at(self, x:float) -> float:
    """Get the width of the object at X position."""
    # If the object has ended, its width is 0
    if self.end_x is not None and x > self.end_x:
      return 0.0

    return NumericTimeline(self.start_w, self._scale_events, "to_w").value_at(x)
