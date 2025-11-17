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
    path:    str,
    width:   int,
  ):
    diagram.add(self)
    self.diagram = diagram
    self.color   = color
    self.path    = path
    self.width   = width

  def render(self) -> str:

    baseline_path = svg.parse_path(self.path)
    start_point   = baseline_path.point(0)

    upper_points = []
    lower_points = []

    for t in np.linspace(0, 1, self.diagram.resolution):
      point  = baseline_path.point(t)
      normal = baseline_path.normal(t)

      upper_offset = -self.width/2
      lower_offset =  self.width/2

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
lineage = Lineage(diagram, "red",  "M 0 50 h 100 c 50 0 50 50 100 50 h 100", 10)
lineage = Lineage(diagram, "blue", "M 0 75 h 100 c 50 0 50 50 100 50 h 100", 15)
diagram.render()
