import svgpathtools as svg
import numpy        as np



class LineageDiagram:
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
    self.entities.append(entity)

  def render(self, filepath:str="diagram.svg"):
    svg_lines = []
    svg_lines.append(f'<svg width="{self.view_width}" height="{self.view_height}" viewBox="0 0 {self.view_width} {self.view_height}" xmlns="http://www.w3.org/2000/svg">')
    for entity in self.entities:
      svg_lines.append(entity.render())
    svg_lines.append('</svg>')
    svg_text = "\n".join(svg_lines)

    try:
      with open(filepath, 'w') as file:
        file.write(svg_text)
      print(f"Diagram successfully saved to {filepath}")
    except IOError as error:
      print(f"Error writing to file {filepath}: {error}")




class Lineage:
  def __init__(
    self,
    diagram: LineageDiagram,
    color:   str,
    start_x: float,
    start_y: float,
    start_w: float,
  ):
    diagram.add(self)
    self.diagram = diagram
    self.color   = color
    self.start_x = start_x
    self.start_y = start_y
    self.start_w = start_w
    self.shifts  = []

  def width_at(self, x:float) -> float:
    return self.start_w

  def shift_to(
    self,
    from_x: float,
    to_x:   float,
    to_y:   float,
  ):
    shift = {
      "from_x": from_x,
      "to_x":   to_x,
      "to_y":   to_y,
    }
    self.shifts.append(shift)

  def get_baseline_path(self) -> svg.Path:
    baseline_path = svg.Path()
    start_point   = complex(self.start_x, self.start_y)
    last_point    = start_point
    for shift in self.shifts:
      shift_start_point = complex(shift["from_x"], last_point.imag)
      shift_end_point   = None
      baseline_path.append(svg.Line(last_point, shift_start_point))
      shift_end_point  = complex(shift["to_x"], shift["to_y"])
      shift_midpoint_x = (shift_start_point.real + shift_end_point.real)/2
      baseline_path.append(svg.CubicBezier(
        shift_start_point,
        complex(shift_midpoint_x, shift_start_point.imag),
        complex(shift_midpoint_x, shift_end_point.imag),
        shift_end_point,
      ))
      last_point = shift_end_point
    end_point = complex(self.diagram.view_width, last_point.imag)
    baseline_path.append(svg.Line(last_point, end_point))
    return baseline_path

  def render(self) -> str:

    baseline_path = self.get_baseline_path()
    start_point   = baseline_path.point(0)

    upper_points = []
    lower_points = []

    for t in np.linspace(0, 1, self.diagram.resolution):
      point  = baseline_path.point(t)
      normal = baseline_path.normal(t)

      upper_offset = -self.start_w/2
      lower_offset =  self.start_w/2

      upper_point = (
        point.real + upper_offset * normal.real,
        point.imag + upper_offset * normal.imag
      )
      lower_point = (
        point.real + lower_offset * normal.real,
        point.imag + lower_offset * normal.imag
      )

      upper_points.append(upper_point)
      lower_points.append(lower_point)

    shape_path = f"M {start_point.real} {start_point.imag}"
    for upper_point in upper_points:
      shape_path += f" L {upper_point[0]} {upper_point[1]}"
    for lower_point in lower_points[::-1]:
      shape_path += f" L {lower_point[0]} {lower_point[1]}"

    shape_svg = f'<path fill="{self.color}" d="{shape_path}"/>'
    return shape_svg


diagram = LineageDiagram(300, 200, 100)
lineage = Lineage(diagram, "red", 0, 50, 10)
lineage.shift_to(100, 200, 150)
diagram.render()
