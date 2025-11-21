import numpy        as np

from dataclasses import dataclass
from typing      import TYPE_CHECKING

from .paths      import ShiftablePath, ShiftEvent
from .utils      import find_t_at_x

if TYPE_CHECKING:
  from .diagram import Diagram
  from .lineage import Lineage

@dataclass
class BundleMembership:
  from_x:  float
  to_x:    float
  lineage: "Lineage"

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

  def add_member(self, from_x:float, to_x:float, lineage:"Lineage"):
    """Add a member lineage to bundle."""
    self.memberships.append(BundleMembership(
      from_x  = from_x,
      to_x    = to_x,
      lineage = lineage,
    ))

  def shift_to(self, from_x:float, to_x:float, to_y:float):
    """Shift bundle to new Y position over X range."""
    self.shift_events.append(ShiftEvent(
      from_x = from_x,
      to_x   = to_x,
      to_y   = to_y,
    ))

  def get_memberships_at(self, x:float):
    """Return memberships active at X, sorted by some criteria (currently insertion order)."""
    return [membership for membership in self.memberships if membership.from_x <= x <= membership.to_x]

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
      # Total bundle width
      member_widths = [membership.lineage.get_width_at(x) for membership in memberships]
      bundle_width  = sum(member_widths) + self.margin * (len(memberships) - 1)
      # Initial offset, start at the top
      current_offset = -bundle_width / 2
      # Iterate over members in order
      for membership, member_width in zip(memberships, member_widths):
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
        current_offset += member_width + self.margin

  def get_center_point_of_member_at(self, x:float, lineage:"Lineage") -> complex:
    """Finds the geometric center of the lineage within the bundle at position X."""
    # Find position alongside path corresponding to X
    baseline_path  = self.get_baseline_path()
    t              = find_t_at_x(baseline_path, x)
    # Get parameters at this position alongside the path
    point          = baseline_path.point(t)
    normal         = baseline_path.normal(t)
    memberships    = self.get_memberships_at(x)
    # Total bundle width
    member_widths  = [membership.lineage.get_width_at(x) for membership in memberships]
    bundle_width   = sum(member_widths) + self.margin * (len(memberships) - 1)
    # Initial offset, start at the top
    current_offset = -bundle_width / 2
    # Iterate over members in order
    for membership, member_width in zip(memberships, member_widths):
      # If found the requested lineage
      if membership.lineage == lineage:
        # Then return the position of its center
        return point + normal * (current_offset + member_width/2)
      # Else update the bundle offset
      current_offset += member_width + self.margin
    # Lineage not found, fallback to bundle center
    print(f"ERROR: Lineage not found in bundle at {x=}.")
    return point

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
    return filtered_upper_points, filtered_lower_points
