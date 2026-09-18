import numpy        as np

from dataclasses import dataclass
from typing      import TYPE_CHECKING

from .paths      import ShiftablePath, ShiftEvent
from .utils      import find_t_at_x, smootherstep
from .sampling   import diagram_event_xs
from .topology   import AssemblyReservation, ReorderTransition

if TYPE_CHECKING:
  from .diagram import Diagram
  from .lineage import Lineage

@dataclass
class BundleMembership:
  """
  Represents the membership of a lineage in a bundle.
  """
  lineage:          "Lineage"
  start_x:           float
  end_x:             float
  fade_in_duration:  float = 0.0
  fade_out_duration: float = 0.0

class Bundle(ShiftablePath):
  """
  Represents a bundle of lineages.
  A bundle manages the layout of its members, ensuring they move together
  with a fixed margin between them.
  """

  def __init__(
      self,
      diagram: "Diagram",
      start_x:  float,
      start_y:  float,
      margin:   float,
    ):
    diagram.add_bundle(self)
    self.diagram = diagram
    self.start_x = start_x
    self.start_y = start_y
    self.margin  = margin

    # Events lists
    self._shift_events: list[ShiftEvent]       = []
    self._memberships:  list[BundleMembership] = []
    self._reservations: list[AssemblyReservation] = []
    self._reorder_events: list[ReorderTransition] = []

    # Computed points for members
    self._compiled_member_points: dict["Lineage", tuple[list[complex], list[complex]]] = {}
    self._compiled_member_samples: dict["Lineage", list[tuple[float, complex, complex]]] = {}

  @property
  def end_x(self) -> float:
    return self.diagram.view_width

  @property
  def memberships(self) -> list[BundleMembership]:
    """Public accessor for memberships."""
    return self._memberships

  def add_member(
      self,
      lineage:         "Lineage",
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
      self._memberships.append(new_membership)
    else:
      # Resolve relative index to global index based on active members
      active_memberships = self.get_memberships_at(start_x)

      if index >= len(active_memberships):
        # Insert after the last active member
        if active_memberships:
          last_active = active_memberships[-1]
          # Find insertion point (after last_active)
          insert_pos = len(self._memberships)
          for i, m in enumerate(self._memberships):
            if m is last_active:
              insert_pos = i + 1
              break
          self._memberships.insert(insert_pos, new_membership)
        else:
          # No active members, just append
          self._memberships.append(new_membership)
      else:
        # Insert before the member at the specified relative index
        target_member = active_memberships[index]
        insert_pos = 0
        for i, m in enumerate(self._memberships):
          if m is target_member:
            insert_pos = i
            break
        self._memberships.insert(insert_pos, new_membership)

  def shift_to(self, from_x:float, to_x:float, to_y:float):
    """Shift bundle to new Y position over X range."""
    self._shift_events.append(ShiftEvent(
      from_x = from_x,
      to_x   = to_x,
      to_y   = to_y,
    ))

  def reserve_member(
      self,
      lineage: "Lineage",
      start_x: float,
      end_x: float,
      *,
      fade_in: bool,
      index: int = -1,
    ):
    self._reservations.append(AssemblyReservation(
      lineage=lineage,
      start_x=start_x,
      end_x=end_x,
      fade_in_duration=end_x - start_x if fade_in else 0.0,
      fade_out_duration=0.0 if fade_in else end_x - start_x,
      index=index,
    ))

  def reorder_member(self, lineage: "Lineage", from_x: float, to_x: float, new_index: int):
    self._reorder_events.append(ReorderTransition(lineage, from_x, to_x, new_index))

  def get_memberships_at(self, x:float) -> list[BundleMembership]:
    """Return memberships active at X, sorted by insertion order."""
    memberships = [membership for membership in self._memberships if membership.start_x <= x + 1e-5 and x <= membership.end_x + 1e-5]
    for event in sorted(self._reorder_events, key=lambda item: (item.to_x, item.from_x)):
      if x + 1e-5 < event.to_x:
        continue
      target = next((membership for membership in memberships if membership.lineage is event.lineage), None)
      if target is None:
        continue
      memberships.remove(target)
      memberships.insert(max(0, min(event.new_index, len(memberships))), target)
    return memberships

  def _get_layout_memberships_at(self, x: float):
    memberships = list(self.get_memberships_at(x))
    for reservation in self._reservations:
      if (
        reservation.start_x < x < reservation.end_x
        and not any(membership.lineage is reservation.lineage for membership in memberships)
      ):
        index = len(memberships) if reservation.index == -1 else max(0, min(reservation.index, len(memberships)))
        memberships.insert(index, reservation)
    return memberships

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
      start_excess = 0.5 * self.margin * (1.0 - factors[ 0])
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

  def _calculate_offsets(self, memberships, x: float) -> tuple[dict["Lineage", float], dict["Lineage", float]]:
    widths, gaps = self._calculate_layout(memberships, x)
    current_offset = -(sum(widths) + sum(gaps)) / 2
    offsets = {}
    width_by_lineage = {}
    for membership, width, gap in zip(memberships, widths, gaps):
      offsets[membership.lineage] = current_offset + width / 2
      width_by_lineage[membership.lineage] = width
      current_offset += width + gap
    return offsets, width_by_lineage

  def _layout_at(self, x: float):
    memberships = self._get_layout_memberships_at(x)
    offsets, widths = self._calculate_offsets(memberships, x)
    active_event = next((event for event in self._reorder_events if event.from_x < x < event.to_x), None)
    if active_event is None:
      return memberships, offsets, widths

    after = list(memberships)
    target = next((membership for membership in after if membership.lineage is active_event.lineage), None)
    if target is None:
      return memberships, offsets, widths
    after.remove(target)
    after.insert(max(0, min(active_event.new_index, len(after))), target)
    after_offsets, _ = self._calculate_offsets(after, x)
    factor = smootherstep((x - active_event.from_x) / (active_event.to_x - active_event.from_x))
    offsets = {
      lineage: offset + (after_offsets.get(lineage, offset) - offset) * factor
      for lineage, offset in offsets.items()
    }
    return memberships, offsets, widths

  def solve_geometry(self):
    """Pre-calculate baseline and stacking for the whole duration."""
    baseline_path = self.get_baseline_path()

    # Initialize empty point lists for all members
    self._compiled_member_points = {membership.lineage: ([],[]) for membership in self._memberships}
    self._compiled_member_samples = {membership.lineage: [] for membership in self._memberships}

    # Sample uniformly and exactly at every authored event boundary.
    sample_ts = set(np.linspace(0, 1, self.diagram.resolution))
    for event_x in diagram_event_xs(self.diagram):
      if self.start_x <= event_x <= self.end_x:
        sample_ts.add(find_t_at_x(baseline_path, event_x))
    for t in sorted(sample_ts):
      # Get parameters at this position alongside the path
      point  = baseline_path.point(t)
      normal = baseline_path.normal(t)
      x      = point.real

      memberships, offsets, width_by_lineage = self._layout_at(x)
      if not memberships: continue

      # Iterate over members in order
      for membership in memberships:
        member_width = width_by_lineage[membership.lineage]
        center_offset = offsets[membership.lineage]
        # Offset lines of this member
        upper_offset = center_offset + member_width / 2
        lower_offset = center_offset - member_width / 2

        # Compute the points of the upper and lower edges of the path
        upper_point = point + normal * upper_offset
        lower_point = point + normal * lower_offset

        # ToDo reimplement back-filtering here
        self._compiled_member_points[membership.lineage][0].append(upper_point)
        self._compiled_member_points[membership.lineage][1].append(lower_point)
        self._compiled_member_samples[membership.lineage].append((x, upper_point, lower_point))


  def _get_member_geometry_at(self, x:float, lineage:"Lineage") -> tuple[complex,complex]:
    """Calculate the upper and lower points of a member at a specific X."""
    baseline_path  = self.get_baseline_path()
    t              = find_t_at_x(baseline_path, x)

    # Get parameters at this position alongside the path
    point          = baseline_path.point(t)
    normal         = baseline_path.normal(t)
    x_on_path      = point.real

    memberships, offsets, widths = self._layout_at(x_on_path)

    # Iterate over members in order
    for membership in memberships:
      # If found the requested lineage
      if membership.lineage == lineage:
        # Then return the position of its center
        member_width = widths[lineage]
        center_offset = offsets[lineage]
        upper_point = point + normal * (center_offset + member_width / 2)
        lower_point = point + normal * (center_offset - member_width / 2)
        return upper_point, lower_point

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
    if lineage not in self._compiled_member_points:
      print("ERROR: No precompiled points this lineage in the bundle.")
      return ([], [])
    all_upper_points, all_lower_points = self._compiled_member_points[lineage]

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
