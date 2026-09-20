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
region.join(lineage, 100)
region.join(bundle, 180)
region.leave(lineage, 260)
region.shade(300, 360, "#db2777")
region.fade(300, 360, 0.08)
```

Membership intervals are half-open. `add_member(target, start_x, end_x)` can be used when both boundaries are known.

## Geometry

- Region geometry is compiled after every ribbon and rendered behind ribbons.
- Padding is measured vertically from the rendered upper and lower lineage edges. It does not extend membership intervals along timeline X.
- All active targets contribute to one vertically spanning envelope.
- A lineage inside a Bundle or Orbit resolves to that whole immediate structure. It returns to individual geometry when it leaves.
- Join and leave coordinates have explicit left and right envelopes. They produce a local vertical boundary instead of a hull extending back to an earlier event.
- `event_corner_radius` rounds that local boundary and therefore permits a small visual bleed around its exact coordinate. Set it to zero for a hard step. Corner radii are clamped to the available padding so rounding cannot cut into a member ribbon.
- An interval with no active targets closes the current component. Later membership starts another SVG component.
- Immediate assembly promotion is supported. Recursive nested-assembly region composition is not yet modeled.

Region sampling is private. Adding or removing a Region does not add ribbon samples or change lineage path data.

## Styling

`shade()` changes fill color over timeline X and `fade()` changes fill opacity. Stroke color, opacity, width, and dash patterns are configurable through `RegionStroke`. `RegionHatch` adds a diagonal SVG pattern over the base fill. Regions have deterministic IDs and a `z` value that controls ordering among Regions; every Region remains behind the ribbon layer.
