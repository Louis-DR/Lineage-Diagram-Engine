import numpy as np

from typing import TYPE_CHECKING

from .paths import ShiftablePath, ScalablePath, ShiftEvent, ScaleEvent

if TYPE_CHECKING:
  from .diagram import Diagram
  from .bundle  import Bundle
  from .lineage import Lineage

class Segment:
  """Base class for compiled segments ready to draw."""
  def __init__(self, diagram: "Diagram"):
    self.diagram       = diagram
    self._upper_points = []
    self._lower_points = []

class IndependentSegment(Segment, ShiftablePath, ScalablePath):
  """Segment that calculates its own geometry based on compiled shifts."""
  def __init__(
      self,
      diagram:      "Diagram",
      start_x:      float,
      start_y:      float,
      start_w:      float,
      end_x:        float,
      shift_events: list[ShiftEvent],
      scale_events: list[ScaleEvent],
    ):
    super().__init__(diagram)
    self.start_x      = start_x
    self.start_y      = start_y
    self.start_w      = start_w
    self.end_x        = end_x
    self._shift_events = shift_events
    self._scale_events = scale_events

  def compile(self) -> tuple[list[complex], list[complex]]:
    """Compile the segment and return the lists of upper and lower points of the shape."""
    baseline_path = self.get_baseline_path()

    # Handle degenerate case: Point-like segment
    if len(baseline_path) == 0:
      return ([], [])

    # Iterate over each segment in the path
    for segment in baseline_path:
        # Check if segment is vertical (jump)
        start = segment.point(0)
        end   = segment.point(1)

        if abs(start.real - end.real) < 1e-5:
            # Vertical segment (jump) - Skip
            continue

        # Sample points along the segment
        # We determine number of samples based on segment length relative to total resolution
        # But for now, let's use a fixed density or minimum samples
        # Simple approach: fixed samples per segment? Or proportional?
        # Let's use proportional to length, but at least 2 (start and end)
        seg_len = segment.length()
        # Heuristic: 1 sample per unit? or based on diagram resolution?
        # diagram.resolution is total samples.
        # Let's just use a reasonable step.
        num_samples = max(2, int(self.diagram.resolution * (seg_len / baseline_path.length())))

        for t in np.linspace(0, 1, num_samples):
            point  = segment.point(t)
            normal = segment.normal(t)

            # Query width with epsilon nudge towards segment interior
            # to handle discontinuities at endpoints correctly.
            query_x = point.real
            if t < 0.5:
                query_x += 1e-5
            else:
                query_x -= 1e-5

            width = self.get_width_at(query_x)

            # Offset lines above and bellow the baseline
            upper_offset =  width / 2
            lower_offset = -width / 2

            # Compute the position of the points of the upper and lower edges
            upper_point = point + normal * upper_offset
            lower_point = point + normal * lower_offset

            self._upper_points.append(upper_point)
            self._lower_points.append(lower_point)

    return (self._upper_points, self._lower_points)

class DependentSegment(Segment):
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
