import svgpathtools as svg
import numpy        as np



def smootherstep(linear:float) -> float:
  """Smooth step function implementing quintic smoothing."""
  if linear <= 0: return 0
  if linear >= 1: return 1
  squared = linear * linear
  cubed   = linear * squared
  return cubed * (6.0 * squared - 15.0 * linear + 10.0)



class LineageDiagram:
  """Diagram of lineages."""

  def __init__(
      self,
      view_width:  int,
      view_height: int,
      resolution:  int = 1000,
    ):
    self.view_width  = view_width
    self.view_height = view_height
    self.resolution  = resolution
    self.entities    = []

  def add(self, entity):
    """Add compileable entity to the diagram."""
    self.entities.append(entity)

  def generate(self, filepath:str="diagram.svg"):
    """Generate the diagram to an SVG file."""
    svg_lines = []
    # Open SVG tag
    svg_lines.append(f'<svg width="{self.view_width}" height="{self.view_height}" viewBox="0 0 {self.view_width} {self.view_height}" xmlns="http://www.w3.org/2000/svg">')
    # Draw each diagram entity
    for entity in self.entities:
      svg_lines.append(entity.draw())
    # Close SVG tag
    svg_lines.append('</svg>')
    # Write the SVG file
    try:
      with open(filepath, 'w') as file:
        file.write("\n".join(svg_lines))
      print(f"Diagram successfully saved to {filepath}")
    except IOError as error:
      print(f"Error writing to file {filepath}: {error}")



class LineageSegment:
  """Base class for continuous segment of lineage."""
  def __init__(
      self,
      diagram: LineageDiagram,
      start_x: float,
      start_w: float,
      end_x:   float = None
    ):
    self.diagram = diagram
    self.start_x = start_x
    self.start_w = start_w
    self.end_x   = end_x or diagram.view_width
    self.scales  = []

  def end_at(self, x:float):
    """Set the X position of the end of the lineage."""
    self.end_x = x

  def scale_to(
      self,
      from_x: float,
      to_x:   float,
      to_w:   float,
    ):
    """Scale segment to new W width over X range."""
    self.scales.append({
      "from_x": from_x,
      "to_x":   to_x,
      "to_w":   to_w,
    })

  def get_width_at(self, x:float) -> float:
    """Get the width of the segment at X position."""
    # Initial width of the segment
    last_width = self.start_w
    # Iterate over scale transformations
    for scale in self.scales:
      # Before transformation, return width of previous transformation
      if x <= scale['from_x']:
        return last_width
      # Within transformation, interpolate with smoothing
      elif scale['from_x'] < x < scale['to_x']:
        x1 = scale['from_x']
        x2 = scale['to_x']
        w1 = last_width
        w2 = scale['to_w']
        ratio_linear = (x - x1) / (x2 - x1)
        ratio_smooth = smootherstep(ratio_linear)
        return w1 + (w2 - w1) * ratio_smooth
      # After transformation, continue to next one
      else:
        last_width = scale['to_w']
    # Reached the end, return width of last transformation
    return last_width



class IndependantLineageSegment(LineageSegment):
  """Lineage segment independant of lineage strutures and with its own compile algorithm."""
  def __init__(
      self,
      diagram: LineageDiagram,
      start_x: float,
      start_y: float,
      start_w: float,
      end_x:   float = None
    ):
    LineageSegment.__init__(self, diagram, start_x, start_w, end_x)
    self.start_y = start_y
    self.shifts  = []

  def shift_to(
      self,
      from_x: float,
      to_x:   float,
      to_y:   float,
    ):
    """Shift segment to new Y position over X range."""
    self.shifts.append({
      "from_x": from_x,
      "to_x":   to_x,
      "to_y":   to_y,
    })

  def get_baseline_path(self) -> svg.Path:
    """Generate the baseline SVG path of the segment."""
    baseline_path = svg.Path()
    start_point   = complex(self.start_x, self.start_y)
    last_point    = start_point
    # Iterate over shift transformation
    for shift in self.shifts:
      shift_start_point = complex(shift["from_x"], last_point.imag)
      # Add line from end end of the previous transformation to the start of this one
      baseline_path.append(svg.Line(last_point, shift_start_point))
      # Compute control points
      shift_end_point  = complex(shift["to_x"], shift["to_y"])
      shift_midpoint_x = (shift_start_point.real + shift_end_point.real)/2
      # Add cubic Bezier curve corresponding to the shift transformation
      baseline_path.append(svg.CubicBezier(
        shift_start_point,
        complex(shift_midpoint_x, shift_start_point.imag),
        complex(shift_midpoint_x, shift_end_point.imag),
        shift_end_point,
      ))
      # Update the last point
      last_point = shift_end_point
    # Line to the end of the segment
    if last_point.real != self.end_x:
      end_point = complex(self.end_x, last_point.imag)
      baseline_path.append(svg.Line(last_point, end_point))
    return baseline_path

  def compile(self) -> tuple[list[complex],list[complex]]:
    """Compile the segment and return the lists of upper and lower points of the shape."""
    baseline_path = self.get_baseline_path()
    upper_points  = []
    lower_points  = []
    # Variables for back-filtering
    last_upper_point     = None
    last_lower_point     = None
    last_upper_backward  = False
    last_lower_backward  = False
    upper_back_filtering = False
    lower_back_filtering = False
    # Work step by step at the configured resolution
    for t in np.linspace(0, 1, self.diagram.resolution):
      # Get parameters at this position alongside the path
      point  = baseline_path.point(t)
      normal = baseline_path.normal(t)
      width  = self.get_width_at(point.real)
      # Offset lines above and bellow the baseline
      upper_offset =  width/2
      lower_offset = -width/2
      # Compute the position of the points of the upper and lower edges
      upper_point = (
        point.real + upper_offset * normal.real,
        point.imag + upper_offset * normal.imag
      )
      lower_point = (
        point.real + lower_offset * normal.real,
        point.imag + lower_offset * normal.imag
      )

      # Back-filtering against artifacts for tight bends
      # When the bend is too tight and the stroke too wide, the offset line will glitch: first the
      # offset of the flat line before the bend will continue too far, then the offset of the bend
      # will go backward in an arc, and finally the offset line of the straigher sloped line will
      # move forward and up, cross the first line and continue as expected. This filtering removes
      # the backward arc and the portions of lines that are inside the stroke. It is applied on the
      # upper and lower edges.

      # Upper edge back filtering
      # Detect if going backward
      if len(upper_points) > 0:
        upper_backward = upper_point[0] < last_upper_point[0]
      else:
        upper_backward = False
      # If going backwards, don't add the points
      if not upper_backward:
        # If going forward after going backward, start back-filtering
        if last_upper_backward:
          upper_back_filtering = True
        # Back filtering
        if not upper_back_filtering:
          upper_points.append(upper_point)
        else:
          # Find the Y position from the original forward line at the X of the current point
          intersect_y = None
          # Traverse the list of previous upper points backwards
          for index in range(len(upper_points) - 1, -1, -1):
            iteration_x = upper_points[index][0]
            # Case 1: exact same X
            if iteration_x == upper_point[0]:
              # We have the Y directly
              intersect_y = upper_points[index][1]
              break
            # Case 2: between two points
            elif iteration_x < upper_point[0]:
              # Interpolate for the Y
              point_a = upper_points[index]
              point_b = upper_points[index+1]
              ratio   = (upper_point[0] - point_a[0]) / (point_b[0] - point_a[0])
              intersect_y  = ratio * point_b[1] + (1 - ratio) * point_a[1]
              break
          # If the current point is above the previous offset line
          if upper_point[1] < intersect_y:
            # Then, remove the previous points with higher X, they are inside the line
            while len(upper_points) > 0 and upper_points[-1][0] > upper_point[0]:
              del upper_points[-1]
            # And add the new point and return to normal operation
            upper_points.append(upper_point)
            upper_back_filtering = False
      # Save state
      last_upper_point    = upper_point
      last_upper_backward = upper_backward

      # Lower edge back filtering
      # Detect if going backward
      if len(lower_points) > 0:
        lower_backward = lower_point[0] < last_lower_point[0]
      else:
        lower_backward = False
      # If going backwards, don't add the points
      if not lower_backward:
        # If going forward after going backward, start back-filtering
        if last_lower_backward:
          lower_back_filtering = True
        # Back filtering
        if not lower_back_filtering:
          lower_points.append(lower_point)
        else:
          # Find the Y position from the original forward line at the X of the current point
          intersect_y = None
          # Traverse the list of previous lower points backwards
          for index in range(len(lower_points) - 1, -1, -1):
            iteration_x = lower_points[index][0]
            # Case 1: exact same X
            if iteration_x == lower_point[0]:
              # We have the Y directly
              intersect_y = lower_points[index][1]
              break
            # Case 2: between two points
            elif iteration_x < lower_point[0]:
              # Interpolate for the Y
              point_a = lower_points[index]
              point_b = lower_points[index+1]
              ratio   = (lower_point[0] - point_a[0]) / (point_b[0] - point_a[0])
              intersect_y  = ratio * point_b[1] + (1 - ratio) * point_a[1]
              break
          # If the current point is under the previous offset line
          if lower_point[1] > intersect_y:
            # Then, remove the previous points with lower Y, they are inside the line
            while len(lower_points) > 0 and lower_points[-1][1] < lower_point[1]:
              del lower_points[-1]
            # And add the new point and return to normal operation
            lower_points.append(lower_point)
            lower_back_filtering = False
      # Save state
      last_lower_point    = lower_point
      last_lower_backward = lower_backward

    return (upper_points, lower_points)



class DependantLineageSegment(LineageSegment):
  """Lineage segment dependent of a lineage struture for its compileing."""
  def __init__(
      self,
      diagram: LineageDiagram,
      start_x: float,
      start_w: float,
      end_x:   float = None
    ):
    LineageSegment.__init__(self, diagram, start_x, start_w, end_x)
    self.upper_points = []
    self.lower_points = []

  def compile(self) -> tuple[list[complex],list[complex]]:
    return (self.upper_points, self.lower_points)



class Lineage:
  """Lineage made of segments."""
  def __init__(
      self,
      diagram: LineageDiagram,
      color:   str,
      start_x: float,
      start_y: float,
      start_w: float,
    ):
    diagram.add(self)
    self.diagram  = diagram
    self.color    = color
    self.start_x  = start_x
    self.start_y  = start_y
    self.start_w  = start_w
    self.segments = [IndependantLineageSegment(
      diagram = diagram,
      start_x = start_x,
      start_y = start_y,
      start_w = start_w,
    )]

  def get_segment_at(self, x:float) -> LineageSegment:
    """Get segment at X position."""
    for segment in self.segments:
      if segment.start_x <= x <= segment.end_x:
        return segment
    print(f"ERROR: No segment at {x=} for this lineage.")
    return None

  def shift_to(
      self,
      from_x: float,
      to_x:   float,
      to_y:   float,
    ):
    """Shift segment to new Y position over X range."""
    self.get_segment_at(from_x).shift_to(from_x, to_x, to_y)

  def scale_to(
      self,
      from_x: float,
      to_x:   float,
      to_w:   float,
    ):
    """Scale segment to new W width over X range."""
    self.get_segment_at(from_x).scale_to(from_x, to_x, to_w)

  def end_at(self, x:float):
    """Set the X position of the end of the lineage."""
    self.get_segment_at(x).end_at(x)

  def join(
      self,
      from_x:      float,
      to_x:        float,
      to_assembly: "LineageAssembly",
    ):
    current_segment = self.get_segment_at(to_x)
    width_at_to_x   = current_segment.get_width_at(to_x)
    segment_end_x   = current_segment.end_x
    current_segment.end_at(to_x)
    created_segment = DependantLineageSegment(
      diagram = self.diagram,
      start_x = to_x,
      start_w = width_at_to_x,
      end_x   = segment_end_x,
    )
    self.segments.append(created_segment)
    to_assembly.add_member(
      from_x  = from_x,
      to_x    = to_x,
      lineage = self,
    )

  def get_width_at(self, x:float) -> float:
    """Get the width of the segment at X position."""
    return self.get_segment_at(x).get_width_at(x)

  @property
  def end_x(self):
    return self.segments[-1].end_x

  def draw(self) -> tuple[list[complex],list[complex]]:
    """Draw the lineage and return the SVG element of the shape."""
    # Start the shape at the start point
    shape_path = f"M {self.start_x} {self.start_y}"
    # Combine the lists of upper and lower points from the segments
    upper_points = []
    lower_points = []
    for segment in self.segments:
      segment_upper_points, segment_lower_points = segment.compile()
      upper_points += segment_upper_points
      lower_points += segment_lower_points
    # Shape is clock-wise starting with the upper points from left to right
    for upper_point in upper_points:
      shape_path += f" L {upper_point[0]} {upper_point[1]}"
    # Shape is clock-wise finishing with the lower points from right to left
    for lower_point in lower_points[::-1]:
      shape_path += f" L {lower_point[0]} {lower_point[1]}"
    # Return the SVG element with the fill color
    shape_svg = f'<path fill="{self.color}" d="{shape_path}"/>'
    return shape_svg



class LineageAssembly:
  """Base class for assembly of lineages"""

class LineageBundle(LineageAssembly):
  """Bundle of lineages."""
  def __init__(
      self,
      diagram: LineageDiagram,
      start_x: float,
      start_y: float,
      margin:  float,
    ):
    self.diagram = diagram
    self.start_x = start_x
    self.start_y = start_y
    self.margin  = margin
    self.shifts  = [] # Y-shift transformations
    self.members = []

  def add_member(
      self,
      from_x:  float,
      to_x:    float,
      lineage: Lineage
    ):
    self.members.append({
      "from_x":  to_x,
      "to_x":    lineage.end_x,
      "lineage": lineage,
    })

  def shift_to(
      self,
      from_x: float,
      to_x:   float,
      to_y:   float,
    ):
    """Shift segment to new Y position over X range."""
    self.shifts.append({
      "from_x": from_x,
      "to_x":   to_x,
      "to_y":   to_y,
    })

  def get_baseline_path(self) -> svg.Path:
    """Generate the baseline SVG path of the bundle."""
    baseline_path = svg.Path()
    start_point   = complex(self.start_x, self.start_y)
    last_point    = start_point
    # Iterate over shift transformation
    for shift in self.shifts:
      shift_start_point = complex(shift["from_x"], last_point.imag)
      # Add line from end end of the previous transformation to the start of this one
      baseline_path.append(svg.Line(last_point, shift_start_point))
      # Compute control points
      shift_end_point  = complex(shift["to_x"], shift["to_y"])
      shift_midpoint_x = (shift_start_point.real + shift_end_point.real)/2
      # Add cubic Bezier curve corresponding to the shift transformation
      baseline_path.append(svg.CubicBezier(
        shift_start_point,
        complex(shift_midpoint_x, shift_start_point.imag),
        complex(shift_midpoint_x, shift_end_point.imag),
        shift_end_point,
      ))
      # Update the last point
      last_point = shift_end_point
    # Line to the end of the view port
    end_point = complex(self.diagram.view_width, last_point.imag)
    baseline_path.append(svg.Line(last_point, end_point))
    return baseline_path

  def get_members_at(self, x:float) -> Lineage:
    """Get list of lineage members at X position."""
    members_at_x = []
    for member in self.members:
      if member["from_x"] <= x <= member["to_x"]:
        members_at_x.append(member["lineage"])
    return members_at_x

  def compile(self):
    baseline_path = self.get_baseline_path()
    # Work step by step at the configured resolution
    for t in np.linspace(0, 1, self.diagram.resolution):
      # Get parameters at this position alongside the path
      point   = baseline_path.point(t)
      normal  = baseline_path.normal(t)
      members = self.get_members_at(point.real)
      bundle_width = sum([member.get_width_at(point.real) for member in members]) + self.margin * (len(members) - 1)
      upper_offset = -bundle_width/2
      lower_offset = None
      for member in members:
        member_segment = member.get_segment_at(point.real)
        member_width   = member_segment.get_width_at(point.real)
        lower_offset   = upper_offset + member_width
        member_upper_point = (
          point.real + upper_offset * normal.real,
          point.imag + upper_offset * normal.imag
        )
        member_lower_point = (
          point.real + lower_offset * normal.real,
          point.imag + lower_offset * normal.imag
        )
        member_segment.upper_points.append(member_upper_point)
        member_segment.lower_points.append(member_lower_point)
        upper_offset += member_width + self.margin



diagram = LineageDiagram(
  view_width  = 1600,
  view_height = 500,
  resolution  = 500,
)

lineage_r = Lineage(diagram, color="indianred", start_x=0, start_y=50, start_w=10)
lineage_r.shift_to(from_x=100, to_x=200, to_y=150)
lineage_r.scale_to(from_x=100, to_x=200, to_w=20)

lineage_b = Lineage(diagram, color="steelblue",    start_x=0, start_y=200, start_w=10)
lineage_g = Lineage(diagram, color="darkseagreen", start_x=0, start_y=250, start_w=10)

bundle = LineageBundle(diagram, start_x=0, start_y=300, margin=5)
lineage_r.join(from_x=300, to_x=350, to_assembly=bundle)
lineage_b.join(from_x=350, to_x=400, to_assembly=bundle)
lineage_g.join(from_x=400, to_x=450, to_assembly=bundle)

lineage_r.scale_to(from_x=500, to_x=550, to_w=10)
lineage_b.scale_to(from_x=550, to_x=600, to_w=20)
lineage_g.scale_to(from_x=600, to_x=650, to_w=20)
lineage_b.scale_to(from_x=700, to_x=800, to_w=10)
lineage_g.scale_to(from_x=700, to_x=800, to_w=10)

bundle.shift_to(from_x=850, to_x=950, to_y=200)

bundle.compile()

diagram.generate()
