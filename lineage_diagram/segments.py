import svgpathtools as svg
import numpy        as np

from typing import TYPE_CHECKING

from .paths import ShiftablePath, ScalablePath, ShiftEvent, ScaleEvent

if TYPE_CHECKING:
  from .diagram import Diagram
  from .bundle  import Bundle
  from .lineage import Lineage

class Segment:
  """Base class for compiled segments ready to draw."""
  def __init__(self, diagram: "Diagram"):
    self.diagram      = diagram
    self.upper_points = []
    self.lower_points = []

class IndependantSegment(Segment, ShiftablePath, ScalablePath):
  """Segment that calculates its own geometry based on compiled shifts."""
  def __init__(
      self,
      diagram: "Diagram",
      start_x: float,
      start_y: float,
      start_w: float,
      end_x:   float,
      shift_events: list[ShiftEvent],
      scale_events: list[ScaleEvent],
    ):
    super().__init__(diagram)
    self.start_x = start_x
    self.start_y = start_y
    self.start_w = start_w
    self.end_x   = end_x
    self.shift_events = shift_events
    self.scale_events = scale_events

  def compile(self) -> tuple[list[complex],list[complex]]:
    """Compile the segment and return the lists of upper and lower points of the shape."""
    baseline_path = self.get_baseline_path()
    # Handle degenerate case: Point-like segment
    if len(baseline_path) == 0:
      return ([], [])
    # Work step by step at the configured resolution
    for t in np.linspace(0, 1, self.diagram.resolution):
      try:
        # Get parameters at this position alongside the path
        point  = baseline_path.point(t)
        normal = baseline_path.normal(t)
        width  = self.get_width_at(point.real)
        # Offset lines above and bellow the baseline
        upper_offset =  width/2
        lower_offset = -width/2
        # Compute the position of the points of the upper and lower edges
        upper_point = point + normal * upper_offset
        lower_point = point + normal * lower_offset
        # ToDo reimplement back-filtering here
        self.upper_points.append(upper_point)
        self.lower_points.append(lower_point)
      except AssertionError:
        # Fallback for rare edge cases in svgpathtools
        continue
    return (self.upper_points, self.lower_points)

class DependantSegment(Segment):
  """Segment whose points are computed by a bundle."""
  def __init__(
      self,
      diagram: "Diagram",
      bundle:  "Bundle",
      lineage: "Lineage",
      start_x: float,
      end_x:   float,
    ):
    super().__init__(diagram)
    self.bundle  = bundle
    self.lineage = lineage
    self.start_x = start_x
    self.end_x   = end_x

  def compile(self):
    # Fetch the pre-computed points from the bundle
    return self.bundle.get_compiled_points_for(self.lineage, self.start_x, self.end_x)
