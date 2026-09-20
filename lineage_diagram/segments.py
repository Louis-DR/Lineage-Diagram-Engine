import numpy as np

from typing import TYPE_CHECKING

from .layout import CompiledRibbonSample
from .paths import ShiftablePath, ScalablePath, ShiftEvent, ScaleEvent
from .sampling import diagram_event_xs
from .timeline import BoundarySide
from .utils import find_t_at_x

if TYPE_CHECKING:
  from .diagram import Diagram
  from .bundle import Bundle
  from .lineage import Lineage


class Segment:
  """Base class for compiled segments ready to draw."""

  def __init__(self, diagram: "Diagram"):
    self.diagram = diagram
    self._upper_points = []
    self._lower_points = []
    self._samples = []

  def compile(self) -> tuple[list[complex], list[complex]]:
    samples = self.compile_samples()
    self._upper_points = [sample.upper for sample in samples]
    self._lower_points = [sample.lower for sample in samples]
    return self._upper_points, self._lower_points

  def compile_samples(self) -> list[CompiledRibbonSample]:
    raise NotImplementedError


class IndependentSegment(Segment, ShiftablePath, ScalablePath):
  """Segment that calculates its own geometry based on compiled shifts."""

  def __init__(
      self,
      diagram: "Diagram",
      start_x: float,
      start_y: float,
      start_w: float,
      end_x: float,
      shift_events: list[ShiftEvent],
      scale_events: list[ScaleEvent],
    ):
    super().__init__(diagram)
    self.start_x = start_x
    self.start_y = start_y
    self.start_w = start_w
    self.end_x = end_x
    self._shift_events = shift_events
    self._scale_events = scale_events

  def get_geometry_at(self, x: float) -> tuple[complex, complex]:
    """Return ribbon edges from this segment's local baseline and width state."""
    baseline_path = self.get_baseline_path()
    t = find_t_at_x(baseline_path, x)
    point = baseline_path.point(t)
    normal = baseline_path.normal(t)
    width = self.get_width_at(x)
    return point + normal * (width / 2), point - normal * (width / 2)

  def compile_samples(self) -> list[CompiledRibbonSample]:
    """Compile paired edge points while preserving their timeline coordinate."""
    self._upper_points = []
    self._lower_points = []
    self._samples = []
    baseline_path = self.get_baseline_path()

    if len(baseline_path) == 0:
      return []

    for segment in baseline_path:
      start = segment.point(0)
      end = segment.point(1)

      if abs(start.real - end.real) < 1e-5:
        continue

      seg_len = segment.length()
      num_samples = max(2, int(self.diagram.resolution * (seg_len / baseline_path.length())))
      sample_ts = set(np.linspace(0, 1, num_samples))
      segment_path = None
      authored_samples = []
      for event_x in diagram_event_xs(self.diagram):
        if start.real < event_x < end.real:
          if segment_path is None:
            from svgpathtools import Path
            segment_path = Path(segment)
          event_t = find_t_at_x(segment_path, event_x)
          sample_ts.add(event_t)
          authored_samples.append((event_t, event_x))

      scale_step_xs = {
        event.from_x for event in self._scale_events
        if event.from_x == event.to_x
      }

      for t in sorted(sample_ts):
        point = segment.point(t)
        normal = segment.normal(t)
        source_x = next((event_x for event_t, event_x in authored_samples if t == event_t), point.real)

        is_internal_scale_step = (
          1e-12 < t < 1 - 1e-12
          and source_x in scale_step_xs
        )
        if is_internal_scale_step:
          for side, query_x in (
              (BoundarySide.LEFT, source_x - 2e-5),
              (BoundarySide.RIGHT, source_x + 2e-5),
            ):
            width = self.get_width_at(query_x)
            upper_point = point + normal * (width / 2)
            lower_point = point - normal * (width / 2)
            sample = CompiledRibbonSample(source_x, upper_point, lower_point, side)
            self._samples.append(sample)
            self._upper_points.append(upper_point)
            self._lower_points.append(lower_point)
          continue

        query_x = source_x
        if t < 0.5:
          query_x += 1e-5
        else:
          query_x -= 1e-5

        width = self.get_width_at(query_x)
        upper_point = point + normal * (width / 2)
        lower_point = point - normal * (width / 2)
        side = BoundarySide.LEFT if abs(t - 1.0) <= 1e-12 else BoundarySide.RIGHT
        sample = CompiledRibbonSample(source_x, upper_point, lower_point, side)
        self._samples.append(sample)
        self._upper_points.append(upper_point)
        self._lower_points.append(lower_point)

    return self._samples


class DependentSegment(Segment):
  """Segment whose points are computed by a bundle."""

  def __init__(
      self,
      diagram: "Diagram",
      bundle: "Bundle",
      lineage: "Lineage",
      start_x: float,
      end_x: float,
    ):
    super().__init__(diagram)
    self.bundle = bundle
    self.lineage = lineage
    self.start_x = start_x
    self.end_x = end_x

  def compile_samples(self) -> list[CompiledRibbonSample]:
    return self.bundle.get_compiled_samples_for(self.lineage, self.start_x, self.end_x)
