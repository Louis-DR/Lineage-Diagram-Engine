from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from .lineage import Lineage
  from .bundle  import Bundle

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
    self.lineages: list["Lineage"] = []
    self.bundles:  list["Bundle"]  = []

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
