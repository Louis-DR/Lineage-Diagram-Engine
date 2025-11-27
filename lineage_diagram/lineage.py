from typing import TYPE_CHECKING, Optional

from .paths    import ScalablePath, ShiftablePath, ShiftEvent, ScaleEvent, MembershipEvent, MembershipEventType, ShadeEvent
from .segments import IndependentSegment, DependentSegment
from .utils      import smootherstep, find_t_at_x

if TYPE_CHECKING:
  from .diagram import Diagram
  from .bundle  import Bundle
  from .orbit   import Orbit

class Lineage(ScalablePath, ShiftablePath):
  """
  Represents a single lineage in the diagram.
  A lineage is a path that can change width and position over time.
  It can be independent or part of a bundle.
  """

  def __init__(
      self,
      diagram: "Diagram",
      color:    str,
      start_x:  float,
      start_y:  float,
      start_w:  float,
      z:        float = 0.0,
    ):
    diagram.add_lineage(self)
    self.diagram = diagram
    self.color   = color
    self.start_x = start_x
    self.start_y = start_y
    self.start_w = start_w
    self.z       = z

    # Events lists
    self.membership_events: list[MembershipEvent] = []
    self._shift_events:     list[ShiftEvent]      = []
    self._scale_events:     list[ScaleEvent]      = []
    self._shade_events:     list[ShadeEvent]      = []

    # Computed segments
    self._computed_segments = []

    # Internal state for compilation
    self._initial_bundle = None
    self.end_x           = None
    self.visual_end_x    = None  # Controls when to stop drawing (independent of width calculations)

  @classmethod
  def create_in_assembly(
      cls,
      diagram:         "Diagram",
      color:            str,
      start_x:          float,
      start_w:          float,
      in_assembly:     "Bundle | Orbit",
      index:            int   = -1,
      fade_in_duration: float = 0.0,
      z:                float = 0.0,
    ) -> "Lineage":
    """Create a lineage that starts inside an assembly."""
    # For Orbit, index is mandatory and cannot be 0 (or -1 default if not handled)
    # But let's assume the caller provides a valid index for Orbit.
    # Bundle handles -1 as append.

    # Create the lineage
    # We start at y=0 because the assembly controls the position
    new_lineage = cls(diagram, color, start_x, 0, start_w, z=z)

    # Add to assembly
    # Note: Orbit.add_member requires index. Bundle.add_member defaults index=-1.
    # We pass index explicitly.
    # We must account for fade_in_duration so that at start_x the lineage is fully visible (factor 1.0)
    start_membership_x = start_x - fade_in_duration
    in_assembly.add_member(
      lineage          = new_lineage,
      start_x          = start_membership_x,
      end_x            = diagram.view_width,
      fade_in_duration = fade_in_duration,
      index            = index,
    )

    # Record initial assembly state
    new_lineage._initial_bundle = in_assembly # ToDo: Rename _initial_bundle to _initial_assembly

    return new_lineage

  # Create a lineage inside an assembly resulting from the merge of parents.
  @classmethod
  def create_in_assembly_from_merge(
      cls,
      diagram:     "Diagram",
      color:        str,
      merge_from_x: float,
      start_x:      float,
      start_w:      float,
      parents:      list["Lineage"],
      in_assembly: "Bundle | Orbit",
      index:        int   = -1,
      z:            float = 0.0,
    ) -> "Lineage":
    """Create a lineage inside an assembly resulting from the merge of parents."""
    return cls.create_from_merge(
      diagram, color, merge_from_x, start_x, 0, start_w, parents,
      in_assembly=in_assembly, index=index, z=z
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

  @staticmethod
  def _calculate_split_layout(
      parent_w:               float,
      parent_center_y:        float,
      children_target_widths: list[float],
    ) -> tuple[list[float],list[float]]:
    """Calculate the start width and center Y for each child at the split point."""
    total_children_target_width = sum(children_target_widths)

    # Calculate proportional shares based on target widths
    if total_children_target_width > 0:
      proportions = [width / total_children_target_width for width in children_target_widths]
    else:
      proportions = [1.0 / len(children_target_widths) for _ in children_target_widths]

    # Calculate start widths of children at split point
    children_start_widths = []
    for target_width, proportion in zip(children_target_widths, proportions):
      proportional_share = parent_w * proportion
      # Clamp width logic:
      # Lower bound: at least its own target width or its share (prevent shrinking too much)
      # Upper bound: at most the parent width (prevent overflow)
      lower_bound  = max(target_width, proportional_share)
      start_width  = min(lower_bound, parent_w)
      children_start_widths.append(start_width)

    # Place the children vertically at the split point
    proportional_shares    = [parent_w * proportion for proportion in proportions]
    current_slot_y         = parent_center_y - parent_w / 2
    children_start_centers = []

    for share in proportional_shares:
      center = current_slot_y + share / 2
      children_start_centers.append(center)
      current_slot_y += share

    # Parent edge bounds
    parent_upper_edge = parent_center_y + parent_w / 2
    parent_lower_edge = parent_center_y - parent_w / 2

    # Iterate over children to adjust their centers
    adjusted_centers = []
    for child_start_w, child_center in zip(children_start_widths, children_start_centers):
      child_upper_edge = child_center + child_start_w / 2
      child_lower_edge = child_center - child_start_w / 2

      # Clamp to container
      if child_upper_edge > parent_upper_edge:
        correction    = child_upper_edge - parent_upper_edge
        child_center -= correction
      elif child_lower_edge < parent_lower_edge:
        correction    = parent_lower_edge - child_lower_edge
        child_center += correction
      adjusted_centers.append(child_center)

    return children_start_widths, adjusted_centers

  @classmethod
  def create_from_merge(
      cls,
      diagram:     "Diagram",
      color:        str,
      merge_from_x: float,
      start_x:      float,
      start_y:      float,
      start_w:      float,
      parents:      list["Lineage"],
      in_assembly: "Bundle | Orbit" = None,
      index:        int     = -1,
      z:            float   = 0.0,
    ) -> "Lineage":
    """Create a lineage resulting from the merge of parents."""
    if in_assembly:
      fade_in_duration = start_x - merge_from_x
      child            = cls.create_in_assembly(diagram, color, start_x, start_w, in_assembly, index, fade_in_duration, z=z)
      # If in assembly, start_y is ignored/dynamic. We use 0 as base for relative calculations if needed,
      # but really we should rely on the child's dynamic position.
      # For the layout calculation below, we assume centered around 0 (relative) and will use target_lineage offset.
      layout_base_y = 0
    else:
      child         = cls(diagram, color, start_x, start_y, start_w, z=z)
      layout_base_y = start_y

    # Sort parents by Y position at merge_from_x
    # We need to resolve their Y position at merge_from_x
    def get_parent_y(parent: "Lineage") -> float:
      # Check bundle state
      parent_bundle = None
      for membership_event in sorted(parent.membership_events, key=lambda event: event.from_x):
        if membership_event.from_x <= merge_from_x:
          if membership_event.type == MembershipEventType.JOIN:
            parent_bundle = membership_event.assembly
          elif membership_event.type == MembershipEventType.LEAVE:
            parent_bundle = None

      if parent_bundle is None and parent._initial_bundle:
         has_left = False
         for membership_event in parent.membership_events:
           if membership_event.type == MembershipEventType.LEAVE and membership_event.from_x <= merge_from_x:
             has_left = True
             break
         if not has_left:
           parent_bundle = parent._initial_bundle

      if parent_bundle:
        center = parent_bundle.get_center_point_of_member_at(merge_from_x, parent)
        return center.imag
      else:
        # Independent
        current_y = parent.start_y
        for shift in parent._shift_events:
          if shift.to_x <= merge_from_x:
            current_y = shift.to_y
        return current_y

    parents.sort(key=get_parent_y)

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
      # If child is in assembly, we target the child lineage dynamically
      target_lineage = child if in_assembly else None
      # If targeting a lineage, the Y is an offset from that lineage's center.
      # If targeting absolute Y, it is the calculated center.
      target_y = parent_center if not in_assembly else 0.0
      offset_y = parent_center if     in_assembly else 0.0

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
      if diagram.auto_color_transition:
        # Merge: Align to end (start_x)
        duration = start_x - merge_from_x
        fade_duration = duration * diagram.color_transition_duration
        shade_start = start_x - fade_duration
        parent.shade(shade_start, start_x, color)
      parent.terminate_at(start_x)
    return child

  def split(
      self,
      start_x:        float,
      split_to_x:     float,
      children_specs: list[dict],
    ) -> list["Lineage"]:
    """
    Split this lineage into multiple children.
    children_specs is a list of dicts with keys:
      - color: str
      - target_w: float
      - target_y: float (optional, for independent)
      - in_assembly: Bundle | Orbit (optional)
      - index: int (optional, for assembly)
      - z: float (optional, default 0.0)
    """
    # Sort children specs by target_y (or index if in bundle)
    # If target_y is not present (e.g. in bundle), we might use index or default to 0
    # For independent, target_y is key.
    def get_child_y(spec):
        if 'target_y' in spec:
            return spec['target_y']
        if 'index' in spec:
            # Proxy for Y order in bundle? Lower index usually higher up?
            # Or just use 0
            return spec['index']
        return 0

    children_specs.sort(key=get_child_y)

    # 1. Get parent state at start_x
    parent_w = self.get_width_at(start_x)

    # Let's calculate the layout relative to the parent's center.
    children_target_widths = [spec['target_w'] for spec in children_specs]
    children_start_widths, children_start_centers_relative = self._calculate_split_layout(
      parent_w, 0, children_target_widths
    )

    # We need to know if the parent is in a bundle at start_x
    parent_bundle = None
    if self._initial_bundle:
       parent_bundle = self._initial_bundle

    # Check events
    for membership_event in sorted(self.membership_events, key=lambda event: event.from_x):
      if membership_event.from_x <= start_x:
        if membership_event.type == MembershipEventType.JOIN:
          parent_bundle = membership_event.assembly
        elif membership_event.type == MembershipEventType.LEAVE:
          parent_bundle = None

    children = []
    for spec, start_w, start_center_rel in zip(children_specs, children_start_widths, children_start_centers_relative):
      color       = spec['color']
      target_w    = spec['target_w']
      in_assembly = spec.get('in_assembly')
      index       = spec.get('index', -1)
      index     = spec.get('index', -1)
      target_y  = spec.get('target_y', 0)
      z         = spec.get('z', 0.0)

      # Create child
      # The child starts at start_x.
      # Its Y position at start_x depends on the parent.

      # Let's try to resolve parent Y.
      parent_y_at_start = self.start_y # Default

      # If parent is in bundle, we can get its center.
      if parent_bundle:
        # We need to access bundle geometry.
        # `get_center_point_of_member_at` works if member is in bundle.
        # Parent is in bundle at start_x.
        center_in_bundle  = parent_bundle.get_center_point_of_member_at(start_x, self)
        parent_y_at_start = center_in_bundle.imag
      else:
        # Best effort for independent parent
        # We scan shifts
        current_y = self.start_y
        for shift in self._shift_events:
          if shift.to_x <= start_x:
            current_y = shift.to_y
        parent_y_at_start = current_y

      child_start_y = parent_y_at_start + start_center_rel

      # Create the child instance
      # Let's create it as independent first, then join/shift.
      # Start with parent color, then shade to target color IF auto_color_transition is True
      initial_color = self.color if self.diagram.auto_color_transition else color
      child = Lineage(self.diagram, initial_color, start_x, child_start_y, start_w, z=z)
      if self.diagram.auto_color_transition:
        # Split: Align to start (start_x)
        duration = split_to_x - start_x
        fade_duration = duration * self.diagram.color_transition_duration
        shade_end = start_x + fade_duration
        child.shade(start_x, shade_end, color)

      # Transition width
      child.scale_to(start_x, split_to_x, target_w)

      # Transition position
      if in_assembly:
        # Join assembly
        # We want to join such that at split_to_x we are in the assembly.
        # `join` takes (from_x, to_x).
        child.join(start_x, split_to_x, in_assembly, index)
      else:
        # Shift to target Y
        child.shift_to(start_x, split_to_x, target_y)

      children.append(child)

    # Handle parent leaving bundle if applicable
    if parent_bundle:
      # We manually update the membership to fade out the parent from the bundle
      # This ensures the space is reclaimed smoothly while the children fade in.
      parent_index = -1
      for i, membership in enumerate(parent_bundle.memberships):
        if membership.lineage == self and membership.start_x <= start_x <= membership.end_x:
          membership.end_x             = split_to_x
          membership.fade_out_duration = split_to_x - start_x
          parent_index = i
          break

      # Sandwich Logic:
      # To prevent layout jumps, we insert children around the parent.
      # Half before, half after.
      # This ensures the gap loss at the boundaries (Neighbor <-> Child) is compensated
      # by the internal gaps (Child <-> Parent).
      if parent_index != -1:
          mid_point = len(children_specs) // 2

          # First half: insert at parent_index (shifting parent down)
          # We iterate backwards to keep order: C1, C2, P
          # Wait, if we insert at K, item at K moves to K+1.
          # If we want C1, C2, P.
          # Insert C2 at K. -> C2, P.
          # Insert C1 at K. -> C1, C2, P.
          # So we iterate backwards through the first half.
          for i in range(mid_point - 1, -1, -1):
              children_specs[i]['index'] = parent_index

          # Second half: insert after parent.
          # Parent is now at parent_index + mid_point.
          # We want C3, C4 after P.
          # Insert C3 at P_index + 1.
          # Insert C4 at P_index + 2.
          current_offset = 1
          for i in range(mid_point, len(children_specs)):
              children_specs[i]['index'] = parent_index + mid_point + current_offset
              current_offset += 1

      # Visual termination: stop drawing at start_x (clean cut)
      # But keep end_x at split_to_x for bundle layout calculations
      self.visual_end_x = start_x
      self.end_x = split_to_x
    else:
      # Independent split: terminate instantly to avoid overlap
      self.terminate_at(start_x)

    return children

  @classmethod
  def create_split_from(
      cls,
      parent:           "Lineage",
      start_x:           float,
      split_to_x:        float,
      new_color:         str,
      new_target_w:      float,
      new_target_y:      float   = 0.0,
      new_in_assembly:  "Bundle | Orbit" = None,
      new_index:         int     = -1,
      parent_target_w:   float   = 0.0,
      parent_target_y:   float   = 0.0,
      parent_in_assembly: "Bundle | Orbit" = None,
      parent_index:      int     = -1,
      new_z:             float   = 0.0,
    ) -> "Lineage":
    """
    Split a new lineage from parent, while parent continues.
    """
    # 1. Get parent state at start_x
    parent_w = parent.get_width_at(start_x)

    # 2. Prepare specs for sorting
    parent_spec = {
        'type':        'parent',
        'target_w':    parent_target_w,
        'target_y':    parent_target_y,
        'in_assembly': parent_in_assembly,
        'index':       parent_index
    }
    new_spec = {
        'type':        'new',
        'target_w':    new_target_w,
        'target_y':    new_target_y,
        'in_assembly': new_in_assembly,
        'index':       new_index,
        'color':     new_color,
        'z':         new_z
    }

    children_specs = [parent_spec, new_spec]

    # Sort based on target Y
    def get_spec_y(spec):
        if spec['in_assembly']:
            # If in assembly, use index as proxy? Or 0?
            return spec['index']
        return spec['target_y']

    children_specs.sort(key=get_spec_y)

    children_target_widths = [spec['target_w'] for spec in children_specs]

    children_start_widths, children_start_centers_relative = cls._calculate_split_layout(
      parent_w, 0, children_target_widths
    )

    # 3. Resolve parent Y at start_x
    parent_bundle = None
    if parent._initial_bundle:
       parent_bundle = parent._initial_bundle

    for membership_event in sorted(parent.membership_events, key=lambda event: event.from_x):
      if membership_event.from_x <= start_x:
        if membership_event.type == MembershipEventType.JOIN:
          parent_bundle = membership_event.assembly
        elif membership_event.type == MembershipEventType.LEAVE:
          parent_bundle = None

    parent_y_at_start = parent.start_y
    if parent_bundle:
      center_in_bundle  = parent_bundle.get_center_point_of_member_at(start_x, parent)
      parent_y_at_start = center_in_bundle.imag
    else:
      current_y = parent.start_y
      for shift in parent._shift_events:
        if shift.to_x <= start_x:
          current_y = shift.to_y
      parent_y_at_start = current_y

    # 4. Apply changes
    new_lineage = None

    for spec, start_w, start_center_rel in zip(children_specs, children_start_widths, children_start_centers_relative):
        if spec['type'] == 'parent':
            # Update PARENT (Parent)
            # We need to transition from "Packed State" at start_x to "Target State" at split_to_x.
            # BUT the parent is currently at "Original State" at start_x.
            # So we must JUMP (0-duration) from Original to Packed at start_x.

            packed_w = start_w
            packed_y = parent_y_at_start + start_center_rel

            # Jump to packed state at start_x
            parent.scale_to(start_x, start_x, packed_w)

            if spec['in_assembly']:
                 # If jumping into an assembly instantly?
                 # Usually parent continues in same context or switches.
                 # If switching to assembly, we join.
                 # If already in assembly, we might need to jump index?
                 # For now, let's assume position jump is handled by shift/join logic.
                 pass
            else:
                 parent.shift_to(start_x, start_x, packed_y)

            # Transition to Target State
            parent.scale_to(start_x, split_to_x, spec['target_w'])

            # Position
            if spec['in_assembly']:
                parent.join(start_x, split_to_x, spec['in_assembly'], spec['index'])
            else:
                parent.shift_to(start_x, split_to_x, spec['target_y'])

        else:
            # Create NEW Lineage
            # New lineage starts at Packed State at start_x.
            new_start_w = start_w
            new_start_y = parent_y_at_start + start_center_rel
            z           = spec.get('z', 0.0)

            # Start with parent color, shade to new color IF auto_color_transition is True
            initial_color = parent.color if parent.diagram.auto_color_transition else spec['color']
            new_lineage = cls(parent.diagram, initial_color, start_x, new_start_y, new_start_w, z=z)
            if parent.diagram.auto_color_transition:
                # Split: Align to start (start_x)
                duration = split_to_x - start_x
                fade_duration = duration * parent.diagram.color_transition_duration
                shade_end = start_x + fade_duration
                new_lineage.shade(start_x, shade_end, spec['color'])
            new_lineage.scale_to(start_x, split_to_x, spec['target_w'])

            if spec['in_assembly']:
                new_lineage.join(start_x, split_to_x, spec['in_assembly'], spec['index'])
            else:
                new_lineage.shift_to(start_x, split_to_x, spec['target_y'])

    return new_lineage

  def merge_into(
      self,
      target_lineage: "Lineage",
      merge_from_x:    float,
      end_x:           float,
      target_w:        float,
      target_y:        Optional[float] = None,
    ):
    """
    Merge this lineage into target_lineage. target_lineage continues.
    """
    # 1. Sort parents by Y position at merge_from_x
    parents = [self, target_lineage]

    def get_parent_y(parent: "Lineage") -> float:
      # Check bundle state
      parent_bundle = None
      for membership_event in sorted(parent.membership_events, key=lambda event: event.from_x):
        if membership_event.from_x <= merge_from_x:
          if membership_event.type == MembershipEventType.JOIN:
            parent_bundle = membership_event.assembly
          elif membership_event.type == MembershipEventType.LEAVE:
            parent_bundle = None

      if parent_bundle is None and parent._initial_bundle:
         has_left = False
         for membership_event in parent.membership_events:
           if membership_event.type == MembershipEventType.LEAVE and membership_event.from_x <= merge_from_x:
             has_left = True
             break
         if not has_left:
           parent_bundle = parent._initial_bundle

      if parent_bundle:
        center = parent_bundle.get_center_point_of_member_at(merge_from_x, parent)
        return center.imag
      else:
        # Independent
        current_y = parent.start_y
        for shift in parent._shift_events:
          if shift.to_x <= merge_from_x:
            current_y = shift.to_y
        return current_y

    parents.sort(key=get_parent_y)

    # Resolve target_y if not provided
    child_target_y = target_y
    if child_target_y is None:
        child_target_y = target_lineage._get_y_at(end_x)

    # Target spec defines the "child" (result) properties
    child_start_w = target_w

    # We need to calculate where they should be at `end_x` (the merge point).
    parent_target_widths, parent_centers = self._calculate_merge_layout(
      parents, merge_from_x, end_x, child_target_y, child_start_w
    )

    # 2. Apply updates
    for parent, target_w_at_merge, center_at_merge in zip(parents, parent_target_widths, parent_centers):
        if parent == self:
            # Merging Lineage (Ends)
            parent.scale_to(merge_from_x, end_x, target_w_at_merge)
            parent.shift_to(merge_from_x, end_x, center_at_merge)
            if self.diagram.auto_color_transition:
                # Merge: Align to end (end_x)
                duration = end_x - merge_from_x
                fade_duration = duration * self.diagram.color_transition_duration
                shade_start = end_x - fade_duration
                parent.shade(shade_start, end_x, target_lineage.color)
            parent.terminate_at(end_x)
        else:
            # Parent Lineage (Target)
            # We need to transition from "Original State" at merge_from_x to "Packed State" at end_x.
            # THEN jump (0-duration) to "Target State" at end_x.

            # Transition to Packed State
            parent.scale_to(merge_from_x, end_x, target_w_at_merge)
            parent.shift_to(merge_from_x, end_x, center_at_merge)

            # Jump to Target State at end_x
            parent.scale_to(end_x, end_x, child_start_w)
            parent.shift_to(end_x, end_x, child_target_y)

  def terminate_at(self, x:float):
    """Stop the lineage at X position."""
    self.end_x = x

  def shift_to(
      self,
      from_x:          float,
      to_x:            float,
      to_y:            float,
      target_lineage: "Lineage" = None,
      offset_y:        float    = 0.0
    ):
    """Shift lineage to new Y position over X range."""
    self._shift_events.append(ShiftEvent(from_x, to_x, to_y, target_lineage, offset_y))

  def scale_to(self, from_x:float, to_x:float, to_w:float):
    """Scale lineage to new W width over X range."""
    self._scale_events.append(ScaleEvent(from_x, to_x, to_w))

  def shade(self, from_x:float, to_x:float, color:str):
    """Transition lineage color to new color over X range."""
    self._shade_events.append(ShadeEvent(from_x, to_x, color))

  def join(self, from_x:float, to_x:float, to_assembly:"Bundle | Orbit", index:int=-1):
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
      from_x:          float,
      to_x:            float,
      from_assembly:  "Bundle | Orbit",
      to_y:            Optional[float] = None,
      target_lineage: "Lineage" = None,
      offset_y:        float    = 0.0
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

  def reorder(
      self,
      from_x:       float,
      to_x:         float,
      in_assembly: "Bundle | Orbit",
      new_index:    int,
    ):
    """
    Reorder the lineage within a bundle/orbit over a transition.
    """
    # Leave current assembly (maintain Y relative to it)
    self.leave(from_x, to_x, in_assembly, to_y=None)
    # Join same assembly at new index
    self.join(from_x, to_x, in_assembly, index=new_index)

  def transfer(
      self,
      from_x:         float,
      to_x:           float,
      from_assembly: "Bundle | Orbit",
      to_assembly:   "Bundle | Orbit",
      index:          int,
    ):
    """
    Transfer the lineage from a bundle/orbit to another over a transition.
    """
    # Leave current assembly (maintain Y relative to it)
    self.leave(from_x, to_x, from_assembly, to_y=None)
    # Join new assembly at index
    self.join(from_x, to_x, to_assembly, index=index)

  def _resolve_target_y(self, target_lineage:"Lineage", at_x:float, offset_y:float) -> Optional[float]:
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

  def get_geometry_at(self, x: float) -> tuple[complex, complex]:
    """
    Get the upper and lower points of the lineage at position X.
    This is used by Orbits to attach satellites to this lineage.
    """
    # If we have computed segments, use them
    # If we have computed segments, use them
    if self._computed_segments:
        for segment in self._computed_segments:
            if segment.start_x <= x <= segment.end_x:
                # If it's a DependentSegment, delegate to the assembly (Bundle or Orbit)
                if hasattr(segment, 'bundle'):
                    # Note: segment.bundle can be a Bundle or an Orbit
                    # We access the protected method _get_member_geometry_at which both should implement
                    return segment.bundle._get_member_geometry_at(x, self)
                else:
                    # IndependentSegment: calculate from baseline path
                    baseline_path = self.get_baseline_path()
                    t = find_t_at_x(baseline_path, x)
                    point = baseline_path.point(t)
                    normal = baseline_path.normal(t)
                    width = self.get_width_at(x)

                    upper = point + normal * (width / 2)
                    lower = point - normal * (width / 2)
                    return upper, lower

    # If no segments (not compiled yet) or out of range
    # Fallback to calculating from events (Independent behavior)
    baseline_path = self.get_baseline_path()
    # Check if x is within range?
    # If x is beyond end, width is 0.

    t = find_t_at_x(baseline_path, x)
    point = baseline_path.point(t)
    normal = baseline_path.normal(t)
    width = self.get_width_at(x)

    upper = point + normal * (width / 2)
    lower = point - normal * (width / 2)
    return upper, lower

  def compile_segments(self):
    """Converts events into geometry segments."""
    self._computed_segments = []
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

    # For drawing segments, respect visual_end_x if set (for clean cuts)
    visual_max_x = self.visual_end_x if self.visual_end_x is not None else max_x
    drawing_max_x = min(max_x, visual_max_x)

    while current_x < max_x:
      # Find next topology event
      next_event    = self.membership_events[event_index] if event_index < len(self.membership_events) else None
      end_segment_x = next_event.from_x if next_event else max_x

      # Clamp to drawing_max_x for visual cutoff
      end_segment_x = min(end_segment_x, drawing_max_x)

      # If lineage is independent
      if not is_dependent:
        # Create independent segment from current_x to end_segment_x
        # Collect shifts that happen in this range
        segment_shifts = []
        for shift_event in self._shift_events:
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
          segment = IndependentSegment(
            diagram      = self.diagram,
            start_x      = current_x,
            start_y      = current_y,
            start_w      = self.start_w,
            end_x        = min(next_event.to_x, drawing_max_x),
            shift_events = segment_shifts,
            scale_events = self._scale_events,
          )
          self._computed_segments.append(segment)
          # Update state
          current_x      = next_event.to_x
          current_bundle = bundle
          is_dependent   = True
          event_index   += 1
          # We don't update current_y because it's now managed by bundle
        else:
          # No next event
          # Independent segment until the end of the lineage
          segment = IndependentSegment(
            diagram      = self.diagram,
            start_x      = current_x,
            start_y      = current_y,
            start_w      = self.start_w,
            end_x        = min(end_segment_x, drawing_max_x),
            shift_events = segment_shifts,
            scale_events = self._scale_events,
          )
          self._computed_segments.append(segment)
          current_x = end_segment_x
          # Update current_y based on last shift
          if segment_shifts:
            current_y = segment_shifts[-1].to_y
          if not next_event: break
      else:
        # Dependent lineage (inside a bundle)
        if next_event and next_event.type == MembershipEventType.LEAVE:
          # Check for Reorder (Leave + Join)
          next_next_event = self.membership_events[event_index+1] if event_index + 1 < len(self.membership_events) else None

          if next_next_event and next_next_event.type == MembershipEventType.JOIN and abs(next_next_event.from_x - next_event.from_x) < 1e-5:
             # REORDER / TRANSFER
             # 1. Segment from current_x to transition start
             segment = DependentSegment(
               diagram = self.diagram,
               bundle  = current_bundle,
               lineage = self,
               start_x = current_x,
               end_x   = min(next_event.from_x, drawing_max_x),
             )
             self._computed_segments.append(segment)

             # 2. Transition Segment
             # Start point: Center in OLD bundle at from_x
             start_center = current_bundle.get_center_point_of_member_at(next_event.from_x + 1e-3, self)

             # End point: Center in NEW bundle at to_x
             new_bundle = next_next_event.assembly
             end_center = new_bundle.get_center_point_of_member_at(next_next_event.to_x, self)

             transition_shift = ShiftEvent(
               from_x = next_event.from_x,
               to_x   = next_event.to_x,
               to_y   = end_center.imag,
             )

             reorder_seg = IndependentSegment(
               diagram      = self.diagram,
               start_x      = next_event.from_x,
               start_y      = start_center.imag,
               start_w      = self.start_w,
               end_x        = min(next_event.to_x, drawing_max_x),
               shift_events = [transition_shift],
               scale_events = self._scale_events,
             )
             self._computed_segments.append(reorder_seg)

             # 3. Update State
             current_x      = next_event.to_x
             current_bundle = new_bundle
             is_dependent   = True # We are back in a bundle
             event_index   += 2    # Skip both LEAVE and JOIN

          else:
             # NORMAL LEAVE
             # Segment from current_x to leave event start
             segment = DependentSegment(
               diagram = self.diagram,
               bundle  = current_bundle,
               lineage = self,
               start_x = current_x,
               end_x   = min(next_event.from_x, drawing_max_x),
             )
             self._computed_segments.append(segment)
             # Get the center point of the lineage inside the bundle when it leaves
             center_in_bundle = current_bundle.get_center_point_of_member_at(next_event.from_x + 1e-3, self)
             # Create a new independent segment that starts at the bundle position and shifts to the target Y
             # Resolve dynamic target if needed
             resolved_target_y = next_event.target_y
             if next_event.target_lineage:
                resolved_y = self._resolve_target_y(next_event.target_lineage, next_event.to_x, next_event.offset_y)
                if resolved_y is not None:
                  resolved_target_y = resolved_y
             elif resolved_target_y is None:
                # If no target Y provided, default to the position when leaving (no shift)
                resolved_target_y = center_in_bundle.imag

             transition_shift = ShiftEvent(
               from_x = next_event.from_x,
               to_x   = next_event.to_x,
               to_y   = resolved_target_y if resolved_target_y is not None else 0.0,
             )
             # This segment starts at the start of the transition
             leave_seg = IndependentSegment(
               diagram      = self.diagram,
               start_x      = next_event.from_x,
               start_y      = center_in_bundle.imag,
               start_w      = self.start_w,
               end_x        =min(next_event.to_x, drawing_max_x),
               shift_events = [transition_shift],
               scale_events = self._scale_events,
             )
             self._computed_segments.append(leave_seg)
             # Update state
             current_x      = next_event.to_x
             current_y      = resolved_target_y
             is_dependent   = False
             current_bundle = None
             event_index   += 1
        else:
          # Dependent until the end of the lineage
          segment = DependentSegment(
            diagram = self.diagram,
            bundle  = current_bundle,
            lineage = self,
            start_x = current_x,
            end_x   = min(max_x, drawing_max_x),
          )
          self._computed_segments.append(segment)
          break

  def _get_y_at(self, x:float) -> float:
    """Resolve the Y position of the lineage at a specific X, handling shifts and bundles."""
    # 1. Check bundle membership
    parent_bundle = None
    if self._initial_bundle:
       parent_bundle = self._initial_bundle

    for membership_event in sorted(self.membership_events, key=lambda event: event.from_x):
      if membership_event.from_x <= x:
        if membership_event.type == MembershipEventType.JOIN:
          parent_bundle = membership_event.assembly
        elif membership_event.type == MembershipEventType.LEAVE:
          parent_bundle = None

    if parent_bundle:
      center_in_bundle = parent_bundle.get_center_point_of_member_at(x, self)
      return center_in_bundle.imag

    # 2. Independent: Interpolate shifts
    current_y = self.start_y
    for shift in self._shift_events:
      if x >= shift.to_x:
        current_y = shift.to_y
      elif x > shift.from_x:
        # Interpolate
        duration = shift.to_x - shift.from_x
        if duration > 1e-5:
            ratio = (x - shift.from_x) / duration
            factor = smootherstep(ratio)
            current_y = current_y + (shift.to_y - current_y) * factor
    return current_y

  @classmethod
  def create_from_lineage(
      cls,
      parent:          "Lineage",
      start_x:         float,
      transition_to_x: float,
      new_color:       str,
      new_target_w:    float,
      new_target_y:    float,
      new_in_bundle:   "Bundle" = None,
      new_index:       int      = -1,
      z:               float    = 0.0,
    ) -> "Lineage":
    """
    Create a new lineage that starts at the edge of the parent lineage.
    The parent lineage is NOT modified (no split effect).
    """
    # 1. Get parent state at start_x
    parent_w = parent.get_width_at(start_x)
    parent_y_at_start = parent._get_y_at(start_x)

    # 2. Determine start Y for new lineage (touching edge)
    # If new_target_y < parent_y_at_start (Above) -> Touch Top Edge (Lower Y)
    # If new_target_y > parent_y_at_start (Below) -> Touch Bottom Edge (Higher Y)

    # Note: In SVG, smaller Y is top.
    if new_target_y < parent_y_at_start:
        # New is above parent. Touch top edge of parent.
        # Top edge = Center - Width/2
        # New lineage top edge should touch parent top edge.
        # New Center = Parent Top Edge + New Width/2
        start_y = (parent_y_at_start - parent_w / 2) + new_target_w / 2
    else:
        # New is below parent. Touch bottom edge of parent.
        # Bottom edge = Center + Width/2
        # New lineage bottom edge should touch parent bottom edge.
        # New Center = Parent Bottom Edge - New Width/2
        start_y = (parent_y_at_start + parent_w / 2) - new_target_w / 2

    # 3. Create new lineage
    new_lineage = cls(parent.diagram, new_color, start_x, start_y, new_target_w, z=z)

    if new_in_bundle:
        new_lineage.join(start_x, transition_to_x, new_in_bundle, new_index)
    else:
        new_lineage.shift_to(start_x, transition_to_x, new_target_y)

    return new_lineage

  def end_at_lineage(
      self,
      target_lineage:    "Lineage",
      transition_from_x: float,
      end_x:             float,
    ):
    """
    End this lineage by touching the edge of the target lineage.
    The target lineage is NOT modified (no merge effect).
    """
    # 1. Get target state at end_x
    target_w = target_lineage.get_width_at(end_x)
    target_y_at_end = target_lineage._get_y_at(end_x)

    # 2. Get Self Y at transition_from_x
    self_y_at_start = self._get_y_at(transition_from_x)

    # 3. Determine end Y (touching edge)
    # We need self width at end_x to calculate center offset.
    # Assuming self width is constant or we use width at end?
    # "just a shift and ending at the to_x".
    # Let's use width at end_x (which might be target width if scaling, or current width).
    self_w_at_end = self.get_width_at(end_x)

    if self_y_at_start < target_y_at_end:
        # Self is above target. Touch top edge.
        # Self Top Edge touches Target Top Edge.
        # Target Top Edge = Target Center - Target Width/2
        # Self Center = Target Top Edge + Self Width/2
        end_y = (target_y_at_end - target_w / 2) + self_w_at_end / 2
    else:
        # Self is below target. Touch bottom edge.
        # Self Bottom Edge touches Target Bottom Edge.
        # Target Bottom Edge = Target Center + Target Width/2
        # Self Center = Target Bottom Edge - Self Width/2
        end_y = (target_y_at_end + target_w / 2) - self_w_at_end / 2

    # 4. Apply transition
    # "no scale on the source lineage" -> self maintains width?
    # "just a shift and ending at the to_x"
    self.shift_to(transition_from_x, end_x, end_y)
    self.terminate_at(end_x)

  def draw(self):
    """Draw the SVG path of the lineage."""
    shape_path_d = ""
    upper_points = []
    lower_points = []
    # Gather points from all compiled segments
    for segment in self._computed_segments:
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

    shape_path_svg = ""

    # Handle Gradient
    if self._shade_events:
        gradient_id = f"gradient-{id(self)}"

        # Sort events
        self._shade_events.sort(key=lambda e: e.from_x)

        stops = []
        # Initial color stop
        stops.append(f'<stop offset="0%" stop-color="{self.color}"/>')

        current_color = self.color

        for event in self._shade_events:
            # Calculate offsets as percentage of view_width
            start_offset = (event.from_x / self.diagram.view_width) * 100
            end_offset   = (event.to_x / self.diagram.view_width) * 100

            # Clamp offsets
            start_offset = max(0, min(100, start_offset))
            end_offset   = max(0, min(100, end_offset))

            # Add stops
            # Before transition: maintain current color until start
            stops.append(f'<stop offset="{start_offset}%" stop-color="{current_color}"/>')

            # After transition: new color
            stops.append(f'<stop offset="{end_offset}%" stop-color="{event.color}"/>')

            current_color = event.color

        # Final stop to maintain last color until end
        stops.append(f'<stop offset="100%" stop-color="{current_color}"/>')

        gradient_def = f'''
        <defs>
            <linearGradient id="{gradient_id}" gradientUnits="userSpaceOnUse" x1="0" x2="{self.diagram.view_width}" y1="0" y2="0">
                {"".join(stops)}
            </linearGradient>
        </defs>
        '''
        shape_path_svg += gradient_def
        fill_attr = f"url(#{gradient_id})"
    else:
        fill_attr = self.color

    stroke = 'stroke="none"'
    if self.diagram.lineage_stroke_width != 0:
      stroke = f'stroke="{fill_attr}" stroke-width="{self.diagram.lineage_stroke_width}"'

    shape_path_svg += f'<path fill="{fill_attr}" {stroke} d="{shape_path_d}"/>'
    return shape_path_svg
