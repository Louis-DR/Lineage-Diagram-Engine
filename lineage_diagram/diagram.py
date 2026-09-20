import math
import warnings
from typing import TYPE_CHECKING

from .timeline import BoundarySide
from .geometry_safety import (
  CurvatureSafetyPolicy,
  GeometryValidationReport,
  UnsafeNormalOffsetError,
  format_geometry_diagnostics,
  validate_compiled_geometry,
)

if TYPE_CHECKING:
  from .lineage import Lineage
  from .bundle  import Bundle
  from .orbit   import Orbit
  from .region  import Region

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
      auto_color_transition:     bool  = True,
      lineage_stroke_width:      float = 0.0,
      color_transition_duration: float = 1.0,
      curvature_policy: CurvatureSafetyPolicy | None = None,
  ):
    if not math.isfinite(color_transition_duration) or not 0.0 <= color_transition_duration <= 1.0:
      raise ValueError("color_transition_duration must be a finite fraction between 0 and 1")
    if not math.isfinite(lineage_stroke_width) or lineage_stroke_width < 0:
      raise ValueError("lineage_stroke_width must be finite and nonnegative")
    self.view_width  = view_width
    self.view_height = view_height
    self.resolution  = resolution
    self.auto_color_transition     = auto_color_transition
    self.lineage_stroke_width      = lineage_stroke_width
    self.color_transition_duration = color_transition_duration
    self.curvature_policy = curvature_policy or CurvatureSafetyPolicy()
    self.last_geometry_report = GeometryValidationReport(())
    self._lineages: list["Lineage"] = []
    self._bundles:  list["Bundle"]  = []
    self._orbits:   list["Orbit"]   = []
    self._regions:  list["Region"]  = []

  def add_lineage(self, lineage:"Lineage"):
    """Register a lineage to the diagram."""
    lineage.id = f"lineage-{len(self._lineages)}"
    self._lineages.append(lineage)

  def add_bundle(self, bundle:"Bundle"):
    """Register a bundle to the diagram."""
    bundle.id = f"bundle-{len(self._bundles)}"
    self._bundles.append(bundle)

  def add_orbit(self, orbit:"Orbit"):
    """Register an orbit to the diagram."""
    orbit.id = f"orbit-{len(self._orbits)}"
    self._orbits.append(orbit)

  def add_region(self, region:"Region"):
    """Register a post-layout Region annotation."""
    region.id = f"region-{len(self._regions)}"
    self._regions.append(region)

  def _lineage_by_id(self, lineage_id: str) -> "Lineage":
    try:
      return next(lineage for lineage in self._lineages if lineage.id == lineage_id)
    except StopIteration as error:
      raise KeyError(f"Unknown lineage ID: {lineage_id}") from error

  def state_at(self, lineage_id: str, x: float, side: BoundarySide = BoundarySide.RIGHT):
    return self._lineage_by_id(lineage_id).state_at(x, side)

  def frame_at(self, lineage_id: str, x: float, side: BoundarySide = BoundarySide.RIGHT):
    return self._lineage_by_id(lineage_id).frame_at(x, side)

  def compile(self) -> list["Lineage"]:
    """Compile layout geometry and return lineages in drawing order."""
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
            raise ValueError(f"Cyclic lineage dependency detected involving {node!r}")
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

    for lineage in solve_order_lineages:
        lineage.compile_geometry()

    self.last_geometry_report = validate_compiled_geometry(self, self.curvature_policy)
    if self.curvature_policy.mode == "reject" and not self.last_geometry_report.is_safe:
      raise UnsafeNormalOffsetError(self.last_geometry_report.diagnostics)
    if self.curvature_policy.mode == "warn" and not self.last_geometry_report.is_safe:
      warnings.warn(
        format_geometry_diagnostics(self.last_geometry_report.diagnostics),
        RuntimeWarning,
        stacklevel=2,
      )

    for region in self._regions:
      region.compile()

    # Sort by Z (ascending) to ensure correct layering.
    # Stable sort preserves topological/creation order for equal Z.
    return sorted(solve_order_lineages, key=lambda lineage: lineage.z)

  def validate_geometry(self, policy: CurvatureSafetyPolicy | None = None) -> GeometryValidationReport:
    """Compile and return curvature-safety diagnostics without requiring rendering."""
    selected_policy = policy or CurvatureSafetyPolicy(mode="report")
    original_policy = self.curvature_policy
    self.curvature_policy = CurvatureSafetyPolicy(
      mode="report",
      max_offset_radius_fraction=selected_policy.max_offset_radius_fraction,
      samples_per_curve=selected_policy.samples_per_curve,
      x_order_tolerance=selected_policy.x_order_tolerance,
    )
    try:
      self.compile()
      return self.last_geometry_report
    finally:
      self.curvature_policy = original_policy

  def to_svg(self) -> str:
    """Compile the diagram and return the complete SVG document."""
    draw_order_lineages = self.compile()
    svg_lines = []

    for region in sorted(self._regions, key=lambda item: item.z):
        svg_lines.append(region.draw())

    for lineage in draw_order_lineages:
        svg_lines.append(lineage.draw())

    print("Step 3: Rendering...")
    svg_lines.insert(0, f'<svg width="{self.view_width}" height="{self.view_height}" viewBox="0 0 {self.view_width} {self.view_height}" xmlns="http://www.w3.org/2000/svg">')
    svg_lines.append('</svg>')
    return "\n".join(svg_lines)

  def generate(self, filepath:str="diagram.svg"):
    """Generate the diagram to an SVG file."""
    svg = self.to_svg()

    try:
      with open(filepath, 'w', encoding='utf-8') as file:
        file.write(svg)
      print(f"Diagram successfully saved to {filepath}")
    except IOError as error:
      print(f"Error writing to file {filepath}: {error}")
