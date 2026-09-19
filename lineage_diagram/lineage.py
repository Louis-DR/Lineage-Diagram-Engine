from typing import TYPE_CHECKING, Optional

from .paths    import ScalablePath, ShiftablePath, ShiftEvent, ScaleEvent, MembershipEvent, MembershipEventType, ShadeEvent
from .segments import IndependentSegment, DependentSegment
from .utils      import smootherstep, find_t_at_x
from .timeline   import BoundarySide, PositionTimeline
from .timeline   import ColorTimeline, NumericTimeline
from .layout     import LineageFrame, LineageState

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
    in_assembly.validate_member_index(index, allow_append=True)
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
  def _calculate_packet_layout(
      container_width: float,
      container_center_y: float,
      requested_widths: list[float],
    ) -> tuple[list[float], list[float]]:
    """Allocate participant widths that exactly tile one shared container."""
    if not requested_widths:
      return [], []

    weights = [max(0.0, width) for width in requested_widths]
    total_weight = sum(weights)
    if total_weight == 0:
      widths = [container_width / len(weights) for _ in weights]
    else:
      widths = [container_width * weight / total_weight for weight in weights]

    current_edge = container_center_y - container_width / 2
    centers = []
    for width in widths:
      centers.append(current_edge + width / 2)
      current_edge += width
    return widths, centers

  @staticmethod
  def _calculate_merge_layout(
      parents:      list["Lineage"],
      merge_from_x: float,
      start_x:      float,
      start_y:      float,
      start_w:      float,
    ) -> tuple[list[float], list[float]]:
    """Calculate the target width and center Y for each parent at the merge point."""
    requested_widths = [parent.get_width_at(merge_from_x) for parent in parents]
    return Lineage._calculate_packet_layout(start_w, start_y, requested_widths)

  @staticmethod
  def _calculate_split_layout(
      parent_w:               float,
      parent_center_y:        float,
      children_target_widths: list[float],
    ) -> tuple[list[float],list[float]]:
    """Calculate the start width and center Y for each child at the split point."""
    return Lineage._calculate_packet_layout(parent_w, parent_center_y, children_target_widths)

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
      in_assembly.validate_member_index(index, allow_append=True)
      # The child exists at start_x. Before then, its transition reservation
      # participates in the parent assembly without creating an impossible
      # stable membership that predates the lineage lifecycle.
      child = cls(diagram, color, start_x, 0, start_w, z=z)
      in_assembly.add_member(child, start_x, diagram.view_width, index=index)
      in_assembly.reserve_member(child, merge_from_x, start_x, fade_in=True, index=index)
      child._initial_bundle = in_assembly
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

    ordered_parents = sorted(parents, key=get_parent_y)

    # Calculate layout
    parent_target_widths, parent_centers = cls._calculate_merge_layout(
      ordered_parents, merge_from_x, start_x, layout_base_y, start_w
    )

    # Iterate over parents and their attributes at merge point
    for parent, parent_target_w, parent_center in zip(ordered_parents, parent_target_widths, parent_centers):
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
        parent.shade(shade_start, start_x, child._color_at(start_x))
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
    original_children_specs = [dict(spec) for spec in children_specs]
    children_specs = list(original_children_specs)

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

    # 1. Get parent state at start_x
    parent_w = self.get_width_at(start_x)

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

    # Default assembly targets replace the parent's active slot in child order.
    if parent_bundle:
      active_memberships = parent_bundle.get_memberships_at(start_x)
      parent_membership = next((membership for membership in active_memberships if membership.lineage is self), None)
      if parent_membership is not None:
        if hasattr(parent_bundle, 'effective_index_of'):
          next_index = parent_bundle.effective_index_of(self, start_x)
          index_step = 1 if next_index > 0 else -1
        else:
          next_index = active_memberships.index(parent_membership)
          index_step = 1
        for spec in children_specs:
          if spec.get('in_assembly') is parent_bundle and 'index' not in spec:
            spec['index'] = next_index
            next_index += index_step

    is_orbit_split = (
      parent_bundle is not None
      and hasattr(parent_bundle, "main_lineage")
      and all(spec.get('in_assembly') is parent_bundle for spec in children_specs)
    )
    if is_orbit_split:
      original_order = {id(spec): index for index, spec in enumerate(original_children_specs)}

      def orbit_layout_key(spec):
        index = spec['index']
        if index > 0:
          # SVG top-to-bottom packing: upper members run outer to inner.
          return (0, -index, original_order[id(spec)])
        # Lower members run inner to outer. Equal indices use newest-inner.
        return (1, abs(index), -original_order[id(spec)])

      children_specs = sorted(children_specs, key=orbit_layout_key)
    else:
      children_specs.sort(key=get_child_y)

    children_target_widths = [spec['target_w'] for spec in children_specs]
    children_start_widths, children_start_centers_relative = self._calculate_split_layout(
      parent_w, 0, children_target_widths
    )
    layout_by_spec = {
      id(spec): (start_w, start_center_rel)
      for spec, start_w, start_center_rel in zip(children_specs, children_start_widths, children_start_centers_relative)
    }

    children = []
    children_by_spec = {}
    creation_specs = original_children_specs if is_orbit_split else children_specs
    for spec in creation_specs:
      start_w, start_center_rel = layout_by_spec[id(spec)]
      color       = spec['color']
      target_w    = spec['target_w']
      in_assembly = spec.get('in_assembly')
      index       = spec.get('index', -1)
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
      children_by_spec[id(spec)] = child

    # Handle parent leaving bundle if applicable
    if parent_bundle:
      # We manually update the membership to fade out the parent from the bundle
      # This ensures the space is reclaimed smoothly while the children fade in.
      active_memberships = parent_bundle.get_memberships_at(start_x)
      active_slot = next(
        (index for index, membership in enumerate(active_memberships) if membership.lineage is self),
        -1,
      )
      for membership in parent_bundle.memberships:
        if membership.lineage == self and membership.start_x <= start_x <= membership.end_x:
          membership.end_x             = start_x
          membership.fade_out_duration = 0.0
          reservation_index = (
            parent_bundle.effective_index_of(self, start_x)
            if hasattr(parent_bundle, "effective_index_of") else active_slot
          )
          parent_bundle.reserve_member(self, start_x, split_to_x, fade_in=False, index=reservation_index)
          break

      # Visual termination: stop drawing at start_x (clean cut)
      # But keep end_x at split_to_x for bundle layout calculations
      self.visual_end_x = start_x
      self.end_x = split_to_x
    else:
      # Independent split: terminate instantly to avoid overlap
      self.terminate_at(start_x)

    if is_orbit_split:
      return [children_by_spec[id(spec)] for spec in original_children_specs]
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
            initial_color = parent._color_at(start_x) if parent.diagram.auto_color_transition else spec['color']
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

    ordered_parents = sorted(parents, key=get_parent_y)

    # Resolve target_y if not provided
    child_target_y = target_y
    if child_target_y is None:
        child_target_y = target_lineage._get_y_at(end_x)

    # Target spec defines the "child" (result) properties
    child_start_w = target_w

    # We need to calculate where they should be at `end_x` (the merge point).
    parent_target_widths, parent_centers = self._calculate_merge_layout(
      ordered_parents, merge_from_x, end_x, child_target_y, child_start_w
    )

    # 2. Apply updates
    for parent, target_w_at_merge, center_at_merge in zip(ordered_parents, parent_target_widths, parent_centers):
        if parent == self:
            # Merging Lineage (Ends)
            parent.scale_to(merge_from_x, end_x, target_w_at_merge)
            parent.shift_to(merge_from_x, end_x, center_at_merge)
            if self.diagram.auto_color_transition:
                # Merge: Align to end (end_x)
                duration = end_x - merge_from_x
                fade_duration = duration * self.diagram.color_transition_duration
                shade_start = end_x - fade_duration
                parent.shade(shade_start, end_x, target_lineage._color_at(end_x))
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
    for assembly in (*self.diagram._bundles, *self.diagram._orbits):
      assembly._memberships = [
        membership for membership in assembly.memberships
        if membership.lineage is not self or membership.start_x < x
      ]
      for membership in assembly.memberships:
        if membership.lineage is self and membership.end_x > x:
          membership.end_x = x
          membership.fade_out_duration = 0.0

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
    to_assembly.validate_member_index(index, allow_append=True)
    for assembly in (*self.diagram._bundles, *self.diagram._orbits):
      if assembly is to_assembly:
        continue
      active_membership = next((
        membership for membership in assembly.memberships
        if membership.lineage is self and membership.start_x <= from_x < membership.end_x
      ), None)
      if active_membership is not None:
        # A lineage has one authoritative assembly state. Keep the outgoing
        # slot only as a transition reservation while entering the new one.
        self.leave(from_x, to_x, assembly)
        break
    self.membership_events.append(MembershipEvent(from_x, to_x, MembershipEventType.JOIN, assembly=to_assembly))
    # Inform the assembly of the new member.
    # The lineage starts entering at from_x, and is fully inside at to_x.
    to_assembly.add_member(
      lineage          = self,
      start_x          = to_x,
      end_x            = self.diagram.view_width,
      fade_in_duration = 0.0,
      index            = index,
    )
    to_assembly.reserve_member(self, from_x, to_x, fade_in=True, index=index)

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
    active_membership = next((
      membership for membership in from_assembly.memberships
      if membership.lineage is self and membership.start_x <= from_x <= membership.end_x
    ), None)
    if active_membership is None:
      raise ValueError("Cannot leave an assembly while the lineage is independent")
    if hasattr(from_assembly, "effective_index_of"):
      reservation_index = from_assembly.effective_index_of(self, from_x)
    else:
      reservation_index = from_assembly.get_memberships_at(from_x).index(active_membership)
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
    active_membership.end_x = from_x
    active_membership.fade_out_duration = 0.0
    from_assembly.reserve_member(self, from_x, to_x, fade_in=False, index=reservation_index)

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
    active_membership = next((
      membership for membership in in_assembly.memberships
      if membership.lineage is self and membership.start_x <= from_x <= membership.end_x
    ), None)
    if active_membership is None:
      raise ValueError("Cannot reorder a lineage while it is independent")
    in_assembly.validate_member_index(new_index, allow_append=False)
    self.membership_events.append(MembershipEvent(from_x, to_x, MembershipEventType.LEAVE, assembly=in_assembly))
    self.membership_events.append(MembershipEvent(from_x, to_x, MembershipEventType.JOIN, assembly=in_assembly))
    in_assembly.reorder_member(self, from_x, to_x, new_index)

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
    to_assembly.validate_member_index(index, allow_append=True)
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

  def _assembly_at(self, x: float, side: BoundarySide):
    for assembly in (*self.diagram._bundles, *self.diagram._orbits):
      for membership in assembly.memberships:
        if membership.lineage is not self:
          continue
        if side == BoundarySide.LEFT and membership.start_x < x <= membership.end_x:
          return assembly
        if side == BoundarySide.RIGHT and membership.start_x <= x < membership.end_x:
          return assembly
    return None

  def frame_at(self, x: float, side: BoundarySide = BoundarySide.RIGHT) -> LineageFrame:
    """Return the authoritative geometric frame at a timeline coordinate."""
    if x < self.start_x or (self.end_x is not None and x > self.end_x):
      raise ValueError(f"Coordinate {x} is outside lineage {self.id} lifecycle")
    if not self._computed_segments:
      self.diagram.compile()

    query_x = x - 2e-5 if side == BoundarySide.LEFT else x + 2e-5
    query_x = max(self.start_x, query_x)
    if self.end_x is not None:
      query_x = min(self.end_x, query_x)
    upper, lower = self.get_geometry_at(query_x)
    center = (upper + lower) / 2
    width = abs(upper - lower)
    if width > 1e-12:
      normal = (upper - lower) / width
    else:
      normal = 1j
    tangent = complex(normal.imag, -normal.real)
    if tangent.real < 0:
      tangent = -tangent
    return LineageFrame(x, center, tangent, normal, width, upper, lower)

  def state_at(self, x: float, side: BoundarySide = BoundarySide.RIGHT) -> LineageState:
    """Return normalized scalar and topology state at a timeline coordinate."""
    frame = self.frame_at(x, side)
    width = NumericTimeline(self.start_w, self._scale_events, "to_w").value_at(x, side)
    color = self._color_at(x, side)
    assembly = self._assembly_at(x, side)
    return LineageState(self.id, x, frame.center.imag, width, color, assembly.id if assembly else None)

  def _color_at(self, x: float, side: BoundarySide = BoundarySide.RIGHT) -> str:
    """Resolve the normalized effective color at an event boundary."""
    try:
      return ColorTimeline(self.color, self._shade_events).value_at(x, side)
    except ValueError:
      color = self.color
      for event in sorted(self._shade_events, key=lambda item: (item.to_x, item.from_x)):
        if x > event.to_x or (x == event.to_x and side == BoundarySide.RIGHT):
          color = event.color
      return color

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
                    return segment.get_geometry_at(x)

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
        if next_event and next_event.type == MembershipEventType.JOIN:
          if next_event.assembly is current_bundle:
            # A repeated join into the current assembly does not change the
            # authoritative geometry state.
            self._computed_segments.append(DependentSegment(
              diagram = self.diagram,
              bundle  = current_bundle,
              lineage = self,
              start_x = current_x,
              end_x   = min(next_event.to_x, drawing_max_x),
            ))
            current_x = next_event.to_x
            event_index += 1
            continue

          # Political affiliations can overlap while a member transfers from
          # one assembly to another. The newest join becomes authoritative;
          # a later leave for the old assembly is consumed below.
          self._computed_segments.append(DependentSegment(
            diagram = self.diagram,
            bundle  = current_bundle,
            lineage = self,
            start_x = current_x,
            end_x   = min(next_event.from_x, drawing_max_x),
          ))
          start_center = current_bundle.get_center_point_of_member_at(next_event.from_x - 1e-5, self)
          end_center = next_event.assembly.get_center_point_of_member_at(next_event.to_x, self)
          self._computed_segments.append(IndependentSegment(
            diagram      = self.diagram,
            start_x      = next_event.from_x,
            start_y      = start_center.imag,
            start_w      = self.start_w,
            end_x        = min(next_event.to_x, drawing_max_x),
            shift_events = [ShiftEvent(next_event.from_x, next_event.to_x, end_center.imag)],
            scale_events = self._scale_events,
          ))
          current_x = next_event.to_x
          current_bundle = next_event.assembly
          event_index += 1
          continue

        if next_event and next_event.type == MembershipEventType.LEAVE:
          if next_event.assembly is not current_bundle:
            # The lineage already transferred to another assembly before its
            # historical affiliation interval formally closed.
            event_index += 1
            continue

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
             start_center = current_bundle.get_center_point_of_member_at(next_event.from_x - 1e-5, self)

             # End point: Center in NEW bundle at to_x
             new_bundle = next_next_event.assembly
             if new_bundle is current_bundle:
               self._computed_segments.append(DependentSegment(
                 diagram = self.diagram,
                 bundle  = current_bundle,
                 lineage = self,
                 start_x = next_event.from_x,
                 end_x   = min(next_event.to_x, drawing_max_x),
               ))
               current_x = next_event.to_x
               event_index += 2
               continue

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
             center_in_bundle = current_bundle.get_center_point_of_member_at(next_event.from_x - 1e-5, self)
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

    # 2. Independent: use the same normalized cubic timeline as rendering.
    return PositionTimeline(self.start_x, self.start_y, self._shift_events).value_at(x, BoundarySide.RIGHT)

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
    initial_color = parent._color_at(start_x) if parent.diagram.auto_color_transition else new_color
    new_lineage = cls(parent.diagram, initial_color, start_x, start_y, new_target_w, z=z)
    if parent.diagram.auto_color_transition:
        fade_duration = (transition_to_x - start_x) * parent.diagram.color_transition_duration
        new_lineage.shade(start_x, start_x + fade_duration, new_color)

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
    if self.diagram.auto_color_transition:
      fade_duration = (end_x - transition_from_x) * self.diagram.color_transition_duration
      self.shade(end_x - fade_duration, end_x, target_lineage._color_at(end_x))
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
        gradient_id = f"gradient-{self.id}"

        try:
          color_stops = ColorTimeline(self.color, self._shade_events).stops(self.diagram.view_width)
        except ValueError:
          color_stops = [(0.0, self.color)]
          current_color = self.color
          for event in sorted(self._shade_events, key=lambda item: item.from_x):
            color_stops.append((event.from_x, current_color))
            color_stops.append((event.to_x, event.color))
            current_color = event.color
          color_stops.append((self.diagram.view_width, current_color))
        stops = [
          f'<stop offset="{max(0, min(100, x / self.diagram.view_width * 100))}%" stop-color="{color}"/>'
          for x, color in color_stops
        ]

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

    shape_path_svg += f'<path id="{self.id}" fill="{fill_attr}" {stroke} d="{shape_path_d}"/>'
    return shape_path_svg
