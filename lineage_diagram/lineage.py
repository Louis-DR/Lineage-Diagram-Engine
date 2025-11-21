from typing import TYPE_CHECKING

from .paths    import ScalablePath, ShiftEvent, ScaleEvent, MembershipEvent, MembershipEventType
from .segments import IndependantSegment, DependantSegment

if TYPE_CHECKING:
  from .diagram import Diagram
  from .bundle  import Bundle

class Lineage(ScalablePath):
  """Lineage."""
  def __init__(
      self,
      diagram: "Diagram",
      color:   str,
      start_x: float,
      start_y: float,
      start_w: float,
    ):
    diagram.add_lineage(self)
    self.diagram = diagram
    self.color   = color
    self.start_x = start_x
    self.start_y = start_y
    self.start_w = start_w
    # Events lists
    self.membership_events: list[MembershipEvent] = []
    self.shift_events:      list[ShiftEvent]      = []
    self.scale_events:      list[ScaleEvent]      = []
    # Computed segments
    self.computed_segments = []

  def shift_to(self, from_x:float, to_x:float, to_y:float):
    """Shift lineage to new Y position over X range."""
    self.shift_events.append(ShiftEvent(from_x, to_x, to_y))

  def scale_to(self, from_x:float, to_x:float, to_w:float):
    """Scale lineage to new W width over X range."""
    self.scale_events.append(ScaleEvent(from_x, to_x, to_w))

  def join(self, from_x:float, to_x:float, to_assembly:"Bundle"):
    """Join assembly over a transition X range."""
    self.membership_events.append(MembershipEvent(from_x, to_x, MembershipEventType.JOIN, assembly=to_assembly))
    # Inform the assembly of the new member.
    # The lineage starts entering at from_x, and is fully inside at to_x.
    to_assembly.add_member(
      lineage          = self,
      start_x          = from_x,
      end_x            = 99999, # Placeholder end
      fade_in_duration = to_x - from_x
    )

  def leave(self, from_x:float, to_x:float, from_assembly:"Bundle", to_y:float):
    """Leave assembly over a transition X range."""
    self.membership_events.append(MembershipEvent(from_x, to_x, MembershipEventType.LEAVE, assembly=from_assembly, target_y=to_y))
    # Update assembly membership.
    # The lineage starts leaving at from_x and is fully gone at to_x.
    for membership in from_assembly.memberships:
      if membership.lineage == self and membership.start_x <= from_x <= membership.end_x:
        membership.end_x             = to_x
        membership.fade_out_duration = to_x - from_x
        break

  def compile_segments(self):
    """Converts events into geometry segments."""
    self.computed_segments = []

    # Sort events by time
    self.membership_events.sort(key=lambda membership_event: membership_event.from_x)

    current_x = self.start_x
    current_y = self.start_y

    # Assume the lineage starts independent.
    # ToDo fix this, because later, lineages will be creatable inside bundles
    is_dependent   = False
    current_bundle = None

    # Process time from start to end, handling events
    event_index = 0
    # We assume a max width for the diagram logic or infinite
    max_x = self.diagram.view_width

    while current_x < max_x:
      # Find next topology event
      next_event    = self.membership_events[event_index] if event_index < len(self.membership_events) else None
      end_segment_x = next_event.from_x if next_event else max_x
      # If lineage is independant
      if not is_dependent:
        # Create independent segment from current_x to end_segment_x
        # Collect shifts that happen in this range
        segment_shifts = [shift_event for shift_event in self.shift_events
                                       if  shift_event.from_x >= current_x
                                       and shift_event.to_x   <= end_segment_x]
        # If the next event is a join, we need a transition shift
        if next_event and next_event.type == MembershipEventType.JOIN:
          bundle = next_event.assembly
          # Get the center point of the lineage when it arrives inside the bundle
          center_in_bundle = bundle.get_center_point_of_member_at(next_event.to_x, self)
          # Shift to connect to segment in bundle
          segment_shifts.append(ShiftEvent(
            from_x = next_event.from_x,
            to_x   = next_event.to_x,
            to_y   = center_in_bundle.imag,
          ))
          # Create the independent segment, it ends at the end of the transition
          segment = IndependantSegment(
            diagram      = self.diagram,
            start_x      = current_x,
            start_y      = current_y,
            start_w      = self.start_w,
            end_x        = next_event.to_x,
            shift_events = segment_shifts,
            scale_events = self.scale_events,
          )
          self.computed_segments.append(segment)
          # Update state
          current_x      = next_event.to_x
          current_bundle = bundle
          is_dependent   = True
          event_index   += 1
          # We don't update current_y because it's now managed by bundle
        else:
          # No next event
          # Independent segment until the end of the lineage
          segment = IndependantSegment(
            diagram      = self.diagram,
            start_x      = current_x,
            start_y      = current_y,
            start_w      = self.start_w,
            end_x        = end_segment_x,
            shift_events = segment_shifts,
            scale_events = self.scale_events,
          )
          self.computed_segments.append(segment)
          current_x = end_segment_x
          # Update current_y based on last shift
          if segment_shifts:
            current_y = segment_shifts[-1].to_y
          if not next_event: break
      else:
        # Dependent lineage (inside a bundle)
        if next_event and next_event.type == MembershipEventType.LEAVE:
          # Segment from current_x to leave event start
          segment = DependantSegment(
            diagram = self.diagram,
            bundle  = current_bundle,
            lineage = self,
            start_x = current_x,
            end_x   = next_event.from_x,
          )
          self.computed_segments.append(segment)
          # Get the center point of the lineage inside the bundle when it leaves
          center_in_bundle = current_bundle.get_center_point_of_member_at(next_event.from_x, self)
          # Create a new independent segment that starts at the bundle position and shifts to the target Y
          transition_shift = ShiftEvent(
            from_x = next_event.from_x,
            to_x   = next_event.to_x,
            to_y   = next_event.target_y,
          )
          # This segment starts at the start of the transition
          leave_seg = IndependantSegment(
            diagram      = self.diagram,
            start_x      = next_event.from_x,
            start_y      = center_in_bundle.imag,
            start_w      = self.start_w,
            end_x        = next_event.to_x,
            shift_events = [transition_shift],
            scale_events = self.scale_events,
          )
          self.computed_segments.append(leave_seg)
          # Update state
          current_x      = next_event.to_x
          current_y      = next_event.target_y
          is_dependent   = False
          current_bundle = None
          event_index   += 1
        else:
          # Dependent until the end of the lineage
          segment = DependantSegment(
            diagram = self.diagram,
            bundle  = current_bundle,
            lineage = self,
            start_x = current_x,
            end_x   = max_x,
          )
          self.computed_segments.append(segment)
          break

  def draw(self):
    """Draw the SVG path of the lineage."""
    shape_path_d = ""
    upper_points = []
    lower_points = []
    # Gather points from all compiled segments
    for segment in self.computed_segments:
      segment_upper_points, segment_lower_points = segment.compile()
      upper_points.extend(segment_upper_points)
      lower_points.extend(segment_lower_points)
    if not upper_points: return ""
    # Construct SVG Path
    shape_path_d = f"M {upper_points[0].real} {upper_points[0].imag}"
    for upper_point in upper_points[1:]:
      shape_path_d += f" L {upper_point.real} {upper_point.imag}"
    for lower_point in reversed(lower_points):
      shape_path_d += f" L {lower_point.real} {lower_point.imag}"
    shape_path_d += " Z"
    shape_path_svg = f'<path fill="{self.color}" stroke="none" d="{shape_path_d}"/>'
    return shape_path_svg
