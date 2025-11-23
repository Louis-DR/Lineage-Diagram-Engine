from typing import TYPE_CHECKING, Optional

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
    # Internal state for compilation
    self._initial_bundle = None
    self.end_x           = None

  @classmethod
  def create_in_bundle(
      cls,
      diagram:          "Diagram",
      color:            str,
      start_x:          float,
      start_w:          float,
      in_bundle:        "Bundle",
      index:            int   = -1,
      fade_in_duration: float = 0.0,
    ) -> "Lineage":
    """Create a lineage that starts inside a bundle."""
    # Create the instance
    instance = cls(diagram, color, start_x, 0, start_w)
    # Register membership taking into accound fade-in duration
    start_membership_x = start_x - fade_in_duration
    in_bundle.add_member(
      lineage          = instance,
      start_x          = start_membership_x,
      end_x            = diagram.view_width,
      fade_in_duration = fade_in_duration,
      index            = index,
    )
    # Set internal state so compile_segments knows it starts dependent
    instance._initial_bundle = in_bundle
    return instance

  @classmethod
  def create_in_bundle_from_merge(
      cls,
      diagram:      "Diagram",
      color:        str,
      merge_from_x: float,
      start_x:      float,
      start_w:      float,
      parents:      list["Lineage"],
      in_bundle:    "Bundle",
      index:        int = -1,
    ) -> "Lineage":
    """Create a lineage inside a bundle resulting from the merge of parents."""
    return cls.create_from_merge(
      diagram      = diagram,
      color        = color,
      merge_from_x = merge_from_x,
      start_x      = start_x,
      start_y      = 0, # Ignored when in_bundle is set
      start_w      = start_w,
      parents      = parents,
      in_bundle    = in_bundle,
      index        = index,
    )

  @staticmethod
  def _calculate_merge_layout(
      parents:      list["Lineage"],
      merge_from_x: float,
      start_x:      float,
      start_y:      float,
      start_w:      float,
    ) -> tuple[list[float], list[float]]:
    """Calculate the target width and center Y for each parent at the merge point."""
    # Sampling parent widths at the start of merge
    parents_widths_at_from_x = [parent.get_width_at(merge_from_x) for parent in parents]
    total_parents_width      = sum(parents_widths_at_from_x)
    # Calculate proportional shares
    if total_parents_width > 0:
      proportions = [parent_width / total_parents_width for parent_width in parents_widths_at_from_x]
    else:
      proportions = [1.0 / len(parents) for _ in parents]
    # Calculate widths of parents at merge point
    proportional_widths = []
    for width_at_from, proportion in zip(parents_widths_at_from_x, proportions):
      proportional_share = start_w * proportion
      # Clamp width logic:
      # Lower bound: at least its own width or its share (prevent shrinking too much)
      # Upper bound: at most the child width (prevent overflow)
      lower_bound  = max(width_at_from, proportional_share)
      target_width = min(lower_bound, start_w)
      proportional_widths.append(target_width)
    # Place the parents vertically at the merge point
    proportional_shares = [start_w * proportion for proportion in proportions]
    current_slot_y      = start_y - start_w / 2
    parent_centers      = []
    for share in proportional_shares:
      center = current_slot_y + share / 2
      parent_centers.append(center)
      current_slot_y += share
    # Child edge bounds
    child_upper_edge = start_y + start_w / 2
    child_lower_edge = start_y - start_w / 2
    # Iterate over parents to adjust their centers
    adjusted_centers = []
    for parent_target_w, parent_center in zip(proportional_widths, parent_centers):
      parent_upper_edge = parent_center + parent_target_w / 2
      parent_lower_edge = parent_center - parent_target_w / 2
      # Clamp to container
      if parent_upper_edge > child_upper_edge:
        correction     = parent_upper_edge - child_upper_edge
        parent_center -= correction
      elif parent_lower_edge < child_lower_edge:
        correction     = child_lower_edge - parent_lower_edge
        parent_center += correction
      adjusted_centers.append(parent_center)

    return proportional_widths, adjusted_centers

  @classmethod
  def create_from_merge(
      cls,
      diagram:      "Diagram",
      color:        str,
      merge_from_x: float,
      start_x:      float,
      start_y:      float,
      start_w:      float,
      parents:      list["Lineage"],
      in_bundle:    "Bundle" = None,
      index:        int = -1,
    ) -> "Lineage":
    """Create a lineage resulting from the merge of parents."""
    if in_bundle:
      fade_in_duration = start_x - merge_from_x
      child = cls.create_in_bundle(diagram, color, start_x, start_w, in_bundle, index, fade_in_duration)
      # If in bundle, start_y is ignored/dynamic. We use 0 as base for relative calculations if needed,
      # but really we should rely on the child's dynamic position.
      # For the layout calculation below, we assume centered around 0 (relative) and will use target_lineage offset.
      layout_base_y = 0
    else:
      child = cls(diagram, color, start_x, start_y, start_w)
      layout_base_y = start_y

    # Calculate layout
    parent_target_widths, parent_centers = cls._calculate_merge_layout(
      parents, merge_from_x, start_x, layout_base_y, start_w
    )

    # Iterate over parents and their attributes at merge point
    for parent, parent_target_w, parent_center in zip(parents, parent_target_widths, parent_centers):
      # We need to handle 2 cases:
      # 1. Parent is independent -> shift to target Y
      # 2. Parent is in a bundle -> leave bundle to target Y

      # Check if parent is in a bundle at the start of the merge
      parent_bundle = None
      # Iterate backwards to find the active state
      # ToDo: make this more robust
      for membership_event in sorted(parent.membership_events, key=lambda event: event.from_x):
        if membership_event.from_x <= merge_from_x:
          if membership_event.type == MembershipEventType.JOIN:
            parent_bundle = membership_event.assembly
          elif membership_event.type == MembershipEventType.LEAVE:
            parent_bundle = None

      # Also check initial bundle state
      if parent_bundle is None and parent._initial_bundle:
         # Check if we haven't left it yet
         has_left = False
         for membership_event in parent.membership_events:
           if membership_event.type == MembershipEventType.LEAVE and membership_event.from_x <= merge_from_x:
             has_left = True
             break
         if not has_left:
           parent_bundle = parent._initial_bundle

      # Determine target parameters
      # If child is in bundle, we target the child lineage dynamically
      target_lineage = child if in_bundle else None
      # If targeting a lineage, the Y is an offset from that lineage's center.
      # If targeting absolute Y, it is the calculated center.
      target_y = parent_center if not in_bundle else 0.0
      offset_y = parent_center if     in_bundle else 0.0

      if parent_bundle:
        parent.leave(
          from_x         = merge_from_x,
          to_x           = start_x,
          from_assembly  = parent_bundle,
          to_y           = target_y,
          target_lineage = target_lineage,
          offset_y       = offset_y,
        )
      else:
        parent.shift_to(
          from_x         = merge_from_x,
          to_x           = start_x,
          to_y           = target_y,
          target_lineage = target_lineage,
          offset_y       = offset_y,
        )
      parent.scale_to(merge_from_x, start_x, parent_target_w)
      parent.terminate_at(start_x)
    return child

  def terminate_at(self, x:float):
    """Stop the lineage at X position."""
    self.end_x = x

  def shift_to(
      self,
      from_x:         float,
      to_x:           float,
      to_y:           float,
      target_lineage: "Lineage" = None,
      offset_y:       float     = 0.0
    ):
    """Shift lineage to new Y position over X range."""
    self.shift_events.append(ShiftEvent(from_x, to_x, to_y, target_lineage, offset_y))

  def scale_to(self, from_x:float, to_x:float, to_w:float):
    """Scale lineage to new W width over X range."""
    self.scale_events.append(ScaleEvent(from_x, to_x, to_w))

  def join(self, from_x:float, to_x:float, to_assembly:"Bundle", index:int=-1):
    """Join assembly over a transition X range."""
    self.membership_events.append(MembershipEvent(from_x, to_x, MembershipEventType.JOIN, assembly=to_assembly))
    # Inform the assembly of the new member.
    # The lineage starts entering at from_x, and is fully inside at to_x.
    to_assembly.add_member(
      lineage          = self,
      start_x          = from_x,
      end_x            = self.diagram.view_width,
      fade_in_duration = to_x - from_x,
      index            = index,
    )

  def leave(
      self,
      from_x:         float,
      to_x:           float,
      from_assembly:  "Bundle",
      to_y:           float,
      target_lineage: "Lineage" = None,
      offset_y:       float     = 0.0
    ):
    """Leave assembly over a transition X range."""
    self.membership_events.append(MembershipEvent(
      from_x         = from_x,
      to_x           = to_x,
      type           = MembershipEventType.LEAVE,
      assembly       = from_assembly,
      target_y       = to_y,
      target_lineage = target_lineage,
      offset_y       = offset_y,
    ))
    # Update assembly membership.
    # The lineage starts leaving at from_x and is fully gone at to_x.
    for membership in from_assembly.memberships:
      if membership.lineage == self and membership.start_x <= from_x <= membership.end_x:
        membership.end_x             = to_x
        membership.fade_out_duration = to_x - from_x
        break

  def _resolve_target_y(self, target_lineage: "Lineage", at_x: float, offset_y: float) -> Optional[float]:
    """Resolve the Y position of a target lineage at a specific X, handling bundle context."""
    # Check if target starts in a bundle (common merge case)
    target_bundle = None
    if target_lineage._initial_bundle:
      target_bundle = target_lineage._initial_bundle
    else:
      # Check dynamic membership
      for membership_event in target_lineage.membership_events:
        if membership_event.type == MembershipEventType.JOIN and membership_event.from_x <= at_x <= membership_event.to_x:
          target_bundle = membership_event.assembly
          break

    if target_bundle:
      # Add a small epsilon to avoid boundary conditions where t calculation slightly undershoots
      center = target_bundle.get_center_point_of_member_at(at_x + 1e-3, target_lineage)
      return center.imag + offset_y

    # If target is independent, we can't easily know its Y without compiling it.
    # But typically independent lineages have static Y or shifts we can calculate?
    # For now, return None if not in bundle, implying we fall back to static definition
    return None

  def compile_segments(self):
    """Converts events into geometry segments."""
    self.computed_segments = []
    # Sort events by time
    self.membership_events.sort(key=lambda membership_event: membership_event.from_x)
    current_x = self.start_x
    current_y = self.start_y

    # Initialize state based on constructor
    if self._initial_bundle:
      is_dependent   = True
      current_bundle = self._initial_bundle
    else:
      is_dependent   = False
      current_bundle = None

    # Process time from start to end, handling events
    event_index = 0
    # We assume a max width for the diagram logic or infinite
    max_x = self.end_x if self.end_x is not None else self.diagram.view_width
    while current_x < max_x:
      # Find next topology event
      next_event    = self.membership_events[event_index] if event_index < len(self.membership_events) else None
      end_segment_x = next_event.from_x if next_event else max_x
      # If lineage is independant
      if not is_dependent:
        # Create independent segment from current_x to end_segment_x
        # Collect shifts that happen in this range
        segment_shifts = []
        for shift_event in self.shift_events:
          if shift_event.from_x >= current_x and shift_event.to_x <= end_segment_x:
            # Resolve dynamic target if needed
            resolved_y = None
            if shift_event.target_lineage:
              resolved_y = self._resolve_target_y(shift_event.target_lineage, shift_event.to_x, shift_event.offset_y)
            if resolved_y is not None:
               new_event = ShiftEvent(shift_event.from_x, shift_event.to_x, resolved_y)
               segment_shifts.append(new_event)
            else:
               segment_shifts.append(shift_event)

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
          center_in_bundle = current_bundle.get_center_point_of_member_at(next_event.from_x + 1e-3, self)
          # Create a new independent segment that starts at the bundle position and shifts to the target Y
          # Resolve dynamic target if needed
          resolved_target_y = next_event.target_y
          if next_event.target_lineage:
             resolved_y = self._resolve_target_y(next_event.target_lineage, next_event.to_x, next_event.offset_y)
             if resolved_y is not None:
               resolved_target_y = resolved_y

          transition_shift = ShiftEvent(
            from_x = next_event.from_x,
            to_x   = next_event.to_x,
            to_y   = resolved_target_y if resolved_target_y is not None else 0.0,
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
