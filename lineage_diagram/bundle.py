import numpy        as np

from dataclasses import dataclass
from typing      import TYPE_CHECKING, Any

from .paths      import ShiftablePath, ShiftEvent
from .utils      import find_t_at_x, smootherstep

if TYPE_CHECKING:
  from .diagram import Diagram
  from .lineage import Lineage

@dataclass
class BundleMembership:
  lineage:           "Lineage"
  start_x:           float
  end_x:             float
  fade_in_duration:  float = 0.0
  fade_out_duration: float = 0.0

class Bundle(ShiftablePath):
  def __init__(
      self,
      diagram: "Diagram",
      start_x: float,
      start_y: float,
      margin:  float,
    ):
    diagram.add_bundle(self)
    self.diagram = diagram
    self.start_x = start_x
    self.start_y = start_y
    self.margin  = margin
    # Events lists
    self.shift_events: list[ShiftEvent]       = []
    self.memberships:  list[BundleMembership] = []
    # Computed points for members
    self.compiled_member_points: dict["Lineage",tuple[list[complex],list[complex]]] = {}

  @property
  def end_x(self) -> float:
    return self.diagram.view_width

  def add_member(
      self,
      lineage:          "Lineage",
      start_x:          float,
      end_x:            float,
      fade_in_duration: float = 0.0,
      index:            int   = -1,
    ):
    """Add a member lineage to bundle."""
    new_membership = BundleMembership(
      lineage           = lineage,
      start_x           = start_x,
      end_x             = end_x,
      fade_in_duration  = fade_in_duration,
      fade_out_duration = 0.0 # Will be set when/if the lineage leaves
    )
    if index == -1:
      self.memberships.append(new_membership)
    else:
      self.memberships.insert(index, new_membership)

  def shift_to(self, from_x:float, to_x:float, to_y:float):
    """Shift bundle to new Y position over X range."""
    self.shift_events.append(ShiftEvent(
      from_x = from_x,
      to_x   = to_x,
      to_y   = to_y,
    ))

  def get_memberships_at(self, x:float) -> list[BundleMembership]:
    """Return memberships active at X, sorted by insertion order."""
    return [membership for membership in self.memberships if membership.start_x <= x <= membership.end_x]

  def _get_factor(self, membership:BundleMembership, x:float) -> float:
    """Calculate the presence factor (0 to 1) of a member at position X."""
    # Fade In
    if x < membership.start_x + membership.fade_in_duration:
      if membership.fade_in_duration <= 1e-5: return 1.0
      ratio = (x - membership.start_x) / membership.fade_in_duration
      return smootherstep(ratio)
    # Fade Out
    elif x > membership.end_x - membership.fade_out_duration:
      if membership.fade_out_duration <= 1e-5: return 1.0
      start_fade_out = membership.end_x - membership.fade_out_duration
      ratio = (x - start_fade_out) / membership.fade_out_duration
      return 1.0 - smootherstep(ratio)
    # Stable
    return 1.0

  def _calculate_layout(self, memberships:list[BundleMembership], x:float) -> tuple[list[float],list]:
    """Calculate widths and margins for all members at X to ensure smooth transitions."""
    factors = [self._get_factor(membership, x) for membership in memberships]
    # Calculate effective widths (lineage width scaled by factor)
    effective_widths = [membership.lineage.get_width_at(x) * factor for membership, factor in zip(memberships, factors)]
    # Create the array of gaps
    count = len(memberships)
    gaps  = []
    if count > 1:
      # Initial gaps: each member contributes half a margin multiplied by their presense factors
      for index in range(count - 1):
        gaps.append(0.5 * self.margin * (factors[index] + factors[index+1]))
      # Edge correction: The "average" formula assumes neighbors exist on both sides
      # and are fully present (factor 1.0). We must remove the margin allocated to
      # the empty space at the start and end.
      start_excess = 0.5 * self.margin * (1.0 - factors[0])
      end_excess   = 0.5 * self.margin * (1.0 - factors[-1])
      # Apply start correction (bottom to top)
      for index in range(len(gaps)):
        if start_excess <= 1e-5: break
        correction    = min(gaps[index], start_excess)
        gaps[index]  -= correction
        start_excess -= correction
      # Apply end correction (top to bottom)
      for index in range(len(gaps)-1, -1, -1):
        if end_excess <= 1e-5: break
        correction  = min(gaps[index], end_excess)
        gaps[index] -= correction
        end_excess  -= correction
    # Add a zero to make the list lengths match
    if count > 0:
      gaps.append(0)
    return effective_widths, gaps

  def solve_geometry(self):
    """Pre-calculate baseline and stacking for the whole duration."""
    baseline_path = self.get_baseline_path()
    # Initialize empty point lists for all members
    self.compiled_member_points = {membership.lineage: ([], []) for membership in self.memberships}
    # Work step by step at the configured resolution
    for t in np.linspace(0, 1, self.diagram.resolution):
      # Get parameters at this position alongside the path
      point  = baseline_path.point(t)
      normal = baseline_path.normal(t)
      x      = point.real
      memberships = self.get_memberships_at(x)
      if not memberships: continue
      # Get the widths and gaps
      widths, gaps = self._calculate_layout(memberships, x)
      # Total bundle width
      bundle_width = sum(widths) + sum(gaps)
      # Initial offset, start at the top
      current_offset = -bundle_width / 2
      # Iterate over members in order
      for membership, member_width, member_gap in zip(memberships, widths, gaps):
        # Offset lines of this member
        upper_offset = current_offset + member_width
        lower_offset = current_offset
        # Compute the points of the upper and lower edges of the path
        upper_point = point + normal * upper_offset
        lower_point = point + normal * lower_offset
        # ToDo reimplement back-filtering here
        self.compiled_member_points[membership.lineage][0].append(upper_point)
        self.compiled_member_points[membership.lineage][1].append(lower_point)
        # Update bundle offset
        current_offset += member_width + member_gap

  def _get_member_geometry_at(self, x:float, lineage:"Lineage") -> tuple[complex, complex]:
    """Calculate the upper and lower points of a member at a specific X."""
    baseline_path  = self.get_baseline_path()
    t              = find_t_at_x(baseline_path, x)
    # Get parameters at this position alongside the path
    point          = baseline_path.point(t)
    normal         = baseline_path.normal(t)
    x_on_path      = point.real
    memberships    = self.get_memberships_at(x_on_path)
    # Get the widths and gaps
    widths, gaps   = self._calculate_layout(memberships, x_on_path)
    # Total bundle width
    bundle_width   = sum(widths) + sum(gaps)
    # Initial offset, start at the top
    current_offset = -bundle_width / 2
    # Iterate over members in order
    for membership, member_width, member_gap in zip(memberships, widths, gaps):
      # If found the requested lineage
      if membership.lineage == lineage:
        # Then return the position of its center
        upper_point = point + normal * (current_offset + member_width)
        lower_point = point + normal * current_offset
        return upper_point, lower_point
      # Else update the bundle offset
      current_offset += member_width + member_gap
    # Lineage not found, fallback to bundle center
    print(f"ERROR: Lineage not found in bundle at {x=}.")
    return point, point

  def get_center_point_of_member_at(self, x:float, lineage:"Lineage") -> complex:
    """Finds the geometric center of the lineage within the bundle at position X."""
    upper, lower = self._get_member_geometry_at(x, lineage)
    return (upper + lower) / 2

  def get_compiled_points_for(
      self,
      lineage: "Lineage",
      start_x: float,
      end_x:   float,
    ):
    """Retrieve the pre-calculated points, filtered by X range."""
    # ToDo investigate better system, perhaps storing points in membership structure
    # Retrieve points for this lineage
    if lineage not in self.compiled_member_points:
      print("ERROR: No precompiled points this lineage in the bundle.")
      return ([], [])
    all_upper_points, all_lower_points = self.compiled_member_points[lineage]

    # Filter points within x range
    # ToDo replace with bisect or numpy masking for performance
    filtered_upper_points = [upper_point for upper_point in all_upper_points if start_x <= upper_point.real <= end_x]
    filtered_lower_points = [lower_point for lower_point in all_lower_points if start_x <= lower_point.real <= end_x]

    # Interpolate start if missing
    if not filtered_upper_points or filtered_upper_points[0].real > start_x + 1e-5:
      upper_point, lower_point = self._get_member_geometry_at(start_x, lineage)
      filtered_upper_points.insert(0, upper_point)
      filtered_lower_points.insert(0, lower_point)

    # Interpolate end if missing
    if not filtered_upper_points or filtered_upper_points[-1].real < end_x - 1e-5:
      upper_point, lower_point = self._get_member_geometry_at(end_x, lineage)
      filtered_upper_points.append(upper_point)
      filtered_lower_points.append(lower_point)

    return filtered_upper_points, filtered_lower_points