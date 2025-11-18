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
    """Add renderable entity to the diagram."""
    self.entities.append(entity)

  def render(self, filepath:str="diagram.svg"):
    """Render the diagram to an SVG file."""
    svg_lines = []
    # Open SVG tag
    svg_lines.append(f'<svg width="{self.view_width}" height="{self.view_height}" viewBox="0 0 {self.view_width} {self.view_height}" xmlns="http://www.w3.org/2000/svg">')
    # Render each diagram entity
    for entity in self.entities:
      svg_lines.append(entity.render())
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
  """Continuous segment of lineage."""
  def __init__(
    self,
    diagram: LineageDiagram,
    start_x: float,
    start_y: float,
    start_w: float,
  ):
    self.diagram = diagram
    self.start_x = start_x
    self.start_y = start_y
    self.start_w = start_w
    self.shifts  = [] # Y-shift transformations
    self.scales  = [] # W-scale transformations

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
    end_point = complex(self.diagram.view_width, last_point.imag)
    baseline_path.append(svg.Line(last_point, end_point))
    return baseline_path

  def render(self) -> tuple[list[complex],list[complex]]:
    """Render the segment and return the lists of upper and lower points of the shape."""
    baseline_path = self.get_baseline_path()
    upper_points  = []
    lower_points  = []
    # Work step by step at the configured resolution
    for t in np.linspace(0, 1, self.diagram.resolution):
      # Get parameters at this position alongside the path
      point  = baseline_path.point(t)
      normal = baseline_path.normal(t)
      width  = self.get_width_at(point.real)
      # Offset lines above and bellow the baseline
      upper_offset = -width/2
      lower_offset =  width/2
      # Compute the position of the points of the upper and lower edges
      upper_point = (
        point.real + upper_offset * normal.real,
        point.imag + upper_offset * normal.imag
      )
      lower_point = (
        point.real + lower_offset * normal.real,
        point.imag + lower_offset * normal.imag
      )
      # Append to the lists
      upper_points.append(upper_point)
      lower_points.append(lower_point)
    return (upper_points, lower_points)



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
    self.segments = [LineageSegment(
      diagram = diagram,
      start_x = start_x,
      start_y = start_y,
      start_w = start_w,
    )]

  def get_segment_at(self, x:float) -> LineageSegment:
    """Get segment at X position."""
    return self.segments[0]

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

  def get_width_at(self, x:float) -> float:
    """Get the width of the segment at X position."""
    return self.get_segment_at(x).get_width_at(x)

  def render(self) -> tuple[list[complex],list[complex]]:
    """Render the lineage and return the SVG element of the shape."""
    # Start the shape at the start point
    shape_path = f"M {self.start_x} {self.start_y}"
    # Combine the lists of upper and lower points from the segments
    upper_points = []
    lower_points = []
    for segment in self.segments:
      segment_upper_points, segment_lower_points = segment.render()
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



diagram = LineageDiagram(300, 200, 100)
lineage = Lineage(diagram, "red", 0, 50, 10)
lineage.shift_to(100, 200, 150)
lineage.scale_to(100, 200,  20)
diagram.render()
