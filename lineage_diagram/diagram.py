from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from .lineage import Lineage
  from .bundle  import Bundle
  from .orbit   import Orbit

class Diagram:
  """
  Diagram made of lineages.
  This is the main container that manages all lineages and bundles.
  """

  def __init__(
      self,
      view_width:  float,
      view_height: float,
      resolution:  int = 1000,
    ):
    self.view_width  = view_width
    self.view_height = view_height
    self.resolution  = resolution
    self._lineages: list["Lineage"] = []
    self._bundles:  list["Bundle"]  = []
    self._orbits:   list["Orbit"]   = []

  def add_lineage(self, lineage:"Lineage"):
    """Register a lineage to the diagram."""
    self._lineages.append(lineage)

  def add_bundle(self, bundle:"Bundle"):
    """Register a bundle to the diagram."""
    self._bundles.append(bundle)

  def add_orbit(self, orbit:"Orbit"):
    """Register an orbit to the diagram."""
    self._orbits.append(orbit)

  def generate(self, filepath:str="diagram.svg"):
    """Generate the diagram to an SVG file."""
    svg_lines = []

    # Compile all bundles: compute their baselines and internal stacking
    print("Step 1: Solving bundle constraints...")
    for bundle in self._bundles:
      bundle.solve_geometry()

    # Compile all lineages: compute segments, fetch from bundles when needed
    print("Step 2: Compiling lineage segments...")

    # Topological Sort for Dependencies
    # Dependencies:
    # - Satellite depends on Orbit
    # - Orbit depends on Main Lineage
    # - Therefore: Satellite depends on Main Lineage

    # Build adjacency list: lineage -> list of dependencies (lineages that must be compiled BEFORE this one)
    dependencies = {lineage: set() for lineage in self._lineages}

    # 1. Check Orbits
    for orbit in self._orbits:
        # Orbit depends on Main Lineage (implicitly, for solving)
        # Satellites depend on Orbit (and thus Main Lineage)
        for membership in orbit.memberships:
            satellite = membership.lineage
            if satellite in dependencies:
                dependencies[satellite].add(orbit.main_lineage)

    # 2. Perform Topological Sort
    solve_order_lineages = []
    visited   = set()
    temp_mark = set()

    def visit(node):
        if node in temp_mark:
            print(f"WARNING: Cyclic dependency detected involving {node}")
            return
        if node not in visited:
            temp_mark.add(node)
            for dependency in dependencies.get(node, []):
                visit(dependency)
            temp_mark.remove(node)
            visited.add(node)
            solve_order_lineages.append(node)

    for lineage in self._lineages:
        if lineage not in visited:
            visit(lineage)

    # Compile in sorted order
    # We also need to solve Orbits.
    # We can solve an Orbit as soon as its Main Lineage is compiled.
    # Or simply solve all Orbits that are ready?
    # Easier: When compiling a lineage, check if it is a main lineage for any orbit, and solve those orbits?
    # Or: Just iterate sorted lineages. After compiling L, solve any Orbit where L is main.

    # Map main_lineage -> list of orbits
    orbits_by_main = {}
    for orbit in self._orbits:
        if orbit.main_lineage not in orbits_by_main:
            orbits_by_main[orbit.main_lineage] = []
        orbits_by_main[orbit.main_lineage].append(orbit)

    for lineage in solve_order_lineages:
        lineage.compile_segments()

        # If this lineage is a main body for orbits, solve them now
        if lineage in orbits_by_main:
            for orbit in orbits_by_main[lineage]:
                orbit.solve_geometry()

    # Draw
    # Sort by Z (ascending) to ensure correct layering.
    # Stable sort preserves topological/creation order for equal Z.
    draw_order_lineages = sorted(solve_order_lineages, key=lambda lineage: lineage.z)

    for lineage in draw_order_lineages:
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
