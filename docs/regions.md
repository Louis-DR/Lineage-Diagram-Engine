# Regions

`Region` is a post-layout annotation around a time-varying set of `Lineage`, `Bundle`, and `Orbit` targets. It is suitable for alliances and other visual groupings that must not alter ribbon geometry.

```python
from lineage_diagram import Region, RegionHatch, RegionStroke

region = Region(
  diagram,
  padding=6,
  fill="#4f46e5",
  fill_opacity=0.18,
  corner_radius=6,
  event_corner_radius=3,
  stroke=RegionStroke("#312e81", width=1.5, dasharray=(6, 3)),
  hatch=RegionHatch("#312e81", opacity=0.15, spacing=8, angle=45),
)
lineage.join_region(region, 100)
bundle.join_region(region, 180)
lineage.leave_region(region, 260)
region.shade(300, 360, "#db2777")
region.fade(300, 360, 0.08)
```

Membership intervals are half-open. `add_member(target, start_x, end_x)` can be used when both boundaries are known. The reciprocal `region.join(target, x)` and `region.leave(target, x)` forms remain supported. `Lineage.join()` and `Lineage.leave()` are reserved for geometry-changing assembly transitions and are not overloaded for Regions.

## Geometry

- Region geometry is compiled after every ribbon and rendered behind ribbons.
- Padding is Euclidean clearance from the rendered ribbon fill plus half of the visible lineage stroke. On a sloped or rapidly scaling edge, the Region follows the parallel offset instead of applying a vertical shift.
- Padding does not extend membership intervals along timeline X. Component starts and ends remain at their exact authored coordinates.
- All active targets contribute to one vertically spanning envelope.
- A lineage inside a Bundle or Orbit resolves to that whole immediate structure. It returns to individual geometry when it leaves.
- Join and leave coordinates have explicit left and right envelopes. They produce a local vertical boundary instead of a hull extending back to an earlier event.
- `corner_radius` rounds component caps and genuine sharp envelope-source changes. Dense samples along a smooth curve are not treated as corners.
- `event_corner_radius` rounds only changed sides of a local membership boundary and therefore permits a small visual taper around its exact coordinate. Set it to zero for a hard step. Effective radii are independent of sampling resolution and are reduced only when a short contour run or containment requires it.
- A rounded hard-X cap can consume up to its effective radius from the local padding. The radius is clamped to the configured padding so the taper does not extend through the active ribbon; use a zero radius when the full clearance must remain visible at the exact membership cut.
- An interval with no active targets closes the current component. Later membership starts another SVG component.
- Immediate assembly promotion is supported. Recursive nested-assembly region composition is not yet modeled.

Regions consume the same cached, source-X-aware rendered samples as lineage drawing. Adding or removing a Region does not add ribbon samples or change lineage path data.

## Styling

`shade()` changes fill color over timeline X and `fade()` changes fill opacity. Stroke color, opacity, width, and dash patterns are configurable through `RegionStroke`. `RegionHatch` adds a diagonal SVG pattern over the base fill. Regions have deterministic IDs and a `z` value that controls ordering among Regions; every Region remains behind the ribbon layer.
