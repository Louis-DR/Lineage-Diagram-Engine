import svgpathtools as svg
import numpy        as np

from dataclasses import dataclass
from enum        import Enum
from typing      import Optional



def smootherstep(linear: float) -> float:
  """Smooth step function implementing quintic smoothing."""
  if linear <= 0: return 0
  if linear >= 1: return 1
  squared = linear * linear
  cubed   = linear * squared
  return cubed * (6.0 * squared - 15.0 * linear + 10.0)



def find_t_at_x(
    path:       svg.Path,
    target_x:   float,
    resolution: int = 100
  ) -> float:
  """Get the T position along the path corresponding to the X position."""
  # ToDo replace with binary search + align to expected resolution for perfect match
  # Quick coarse search
  best_t   = 0.0
  min_dist = float('inf')
  for t in np.linspace(0, 1, resolution):
    point = path.point(t)
    dist = abs(point.real - target_x)
    if dist < min_dist:
      min_dist = dist
      best_t = t
  # Refine with binary search around the best coarse t
  low  = max(0, best_t - 0.01)
  high = min(1, best_t + 0.01)
  for _ in range(10):
    mid   = (low + high) / 2
    point = path.point(mid)
    if point.real < target_x:
      low = mid
    else:
      high = mid
  return (low + high) / 2



class MembershipEventType(Enum):
  JOIN  = 0
  LEAVE = 1

@dataclass
class MembershipEvent:
  from_x:   float
  to_x:     float
  type:     MembershipEventType
  assembly: Optional['Bundle'] = None
  target_y: Optional[float]           = None # For leave events

@dataclass
class ShiftEvent:
  from_x: float
  to_x:   float
  to_y:   float

@dataclass
class ScaleEvent:
  from_x: float
  to_x:   float
  to_w:   float



class ShiftablePath:
  """Path with Y position that can shift."""
  start_x:      float
  start_y:      float
  end_x:        float
  shift_events: list[ShiftEvent]

  def get_baseline_path(self) -> svg.Path:
    """Generate the baseline SVG path of the object."""
    baseline_path = svg.Path()
    last_point    = complex(self.start_x, self.start_y)
    # Sort events by time
    self.shift_events.sort(key=lambda shift_event: shift_event.from_x)
    # Iterate over shift events in order
    for shift in self.shift_events:
      start_shift_point = complex(shift.from_x, last_point.imag)
      # Add line from previous shift if not touching
      if start_shift_point != last_point:
        baseline_path.append(svg.Line(last_point, start_shift_point))
      # Compute control points
      end_shift_point = complex(shift.to_x, shift.to_y)
      shift_midpoint_x = (start_shift_point.real + end_shift_point.real) / 2
      # Add cubic Bezier curve corresponding to the shift transformation
      if start_shift_point != end_shift_point:
        baseline_path.append(svg.CubicBezier(
          start_shift_point,
          complex(shift_midpoint_x, start_shift_point.imag),
          complex(shift_midpoint_x, end_shift_point.imag),
          end_shift_point
        ))
      # Update the last point
      last_point = end_shift_point
    # Line to the end of the object
    end_point = complex(self.end_x, last_point.imag)
    if end_point != last_point:
      baseline_path.append(svg.Line(last_point, end_point))
    return baseline_path

class ScalablePath:
  """Path with X width that can scale."""
  start_w:      float
  scale_events: list[ScaleEvent]

  def get_width_at(self, x: float) -> float:
    """Get the width of the object at X position."""
    # Initial width of the object
    last_width = self.start_w
    # Sort events by time
    self.scale_events.sort(key=lambda scale_event: scale_event.from_x)
    # Iterate over scale transformations in order
    for scale_event in self.scale_events:
      # Before transformation, return width of previous transformation
      if x <= scale_event.from_x:
        return last_width
      # Within transformation, interpolate with smoothing
      elif scale_event.from_x < x < scale_event.to_x:
        x1 = scale_event.from_x
        x2 = scale_event.to_x
        w1 = last_width
        w2 = scale_event.to_w
        ratio_linear = (x - x1) / (x2 - x1)
        ratio_smooth = smootherstep(ratio_linear)
        return w1 + (w2 - w1) * ratio_smooth
      # After transformation, continue to next one
      else:
        last_width = scale_event.to_w
    # Reached the end, return width of last transformation
    return last_width



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



class Diagram:
  """Diagram made of lineages."""
  def __init__(
      self,
      view_width:  float,
      view_height: float,
      resolution:  int = 1000,
    ):
    self.view_width  = view_width
    self.view_height = view_height
    self.resolution  = resolution
    self.lineages    = []
    self.bundles     = []

  def add_lineage(self, lineage:"Lineage"):
    """Register a lineage to the diagram."""
    self.lineages.append(lineage)

  def add_bundle(self, bundle:"Bundle"):
    """Register a bundle to the diagram."""
    self.bundles.append(bundle)

  def generate(self, filepath:str="diagram.svg"):
    """Generate the diagram to an SVG file."""
    svg_lines = []

    # Compile all bundles: compute their baselines and internal stacking
    print("Step 1: Solving bundle constraints...")
    for bundle in self.bundles:
      bundle.solve_geometry()

    # Compile all lineages: compute segments, fetch from bundles when needed
    print("Step 2: Compiling lineage segments...")
    for lineage in self.lineages:
      lineage.compile_segments()
      svg_lines.append(lineage.draw())

    # Write SVG
    print("Step 3: Rendering...")
    # Open SVG tag
    svg_lines.insert(0, f'<svg width="{self.view_width}" height="{self.view_height}" viewBox="0 0 {self.view_width} {self.view_height}" xmlns="http://www.w3.org/2000/svg">')
    # Close SVG tag
    svg_lines.append('</svg>')
    # Write the SVG file
    try:
      with open(filepath, 'w') as file:
        file.write("\n".join(svg_lines))
      print(f"Diagram successfully saved to {filepath}")
    except IOError as error:
      print(f"Error writing to file {filepath}: {error}")


@dataclass
class BundleMembership:
  from_x:  float
  to_x:    float
  lineage: "Lineage"

class Bundle(ShiftablePath):
  def __init__(
      self,
      diagram: Diagram,
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
    self.compiled_member_points: dict[Lineage,tuple[list[complex],list[complex]]] = {}

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



class Lineage(ScalablePath):
  """Lineage."""
  def __init__(
      self,
      diagram: Diagram,
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

  def join(self, from_x:float, to_x:float, to_assembly:Bundle):
    """Join assembly over a transition X range."""
    self.membership_events.append(MembershipEvent(from_x, to_x, MembershipEventType.JOIN, assembly=to_assembly))
    # Inform the assembly of the new member
    # ToDo how to implement the lineage ending
    to_assembly.add_member(to_x, 99999, self) # 99999 is placeholder end

  def leave(self, from_x:float, to_x:float, from_assembly:Bundle, to_y:float):
    """Leave assembly over a transition X range."""
    self.membership_events.append(MembershipEvent(from_x, to_x, MembershipEventType.LEAVE, assembly=from_assembly, target_y=to_y))
    # Update assembly membership
    for membership in from_assembly.memberships:
      # Find the membership for that lineage that matches the X position
      if membership.lineage == self and membership.from_x <= from_x <= membership.to_x:
        membership.to_x = from_x
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



# Usage example
diagram = Diagram(1600, 500, resolution=500)

# Define Lineages (Phase 1: Registration)
lineage_r = Lineage(diagram, "indianred", 0, 50, 10)
lineage_b = Lineage(diagram, "steelblue", 0, 200, 10)
lineage_g = Lineage(diagram, "darkseagreen", 0, 250, 10)

# Define Bundle
bundle = Bundle(diagram, 0, 300, margin=5)

# Events
lineage_r.shift_to(100, 200, 150)
lineage_r.scale_to(100, 200, 20)

# Joins
lineage_r.join(300, 350, bundle)
lineage_b.join(350, 400, bundle)
lineage_g.join(400, 450, bundle)

# Scaling inside bundle (Logic handled by get_width_at)
lineage_r.scale_to(500, 550, 10)
lineage_b.scale_to(550, 600, 20)
lineage_g.scale_to(600, 650, 20)

# Bundle moves
bundle.shift_to(850, 950, 200)

# Leave
lineage_b.leave(1000, 1050, bundle, to_y=50)

# Generate (Phase 2 & 3: Solving & Rendering)
diagram.generate()