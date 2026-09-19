# Geometry Contract

This document describes target semantics. Known differences in the current implementation are listed in `known-defects.md` and protected by expected-failure tests.

## Coordinates

- X is the ordered timeline axis and increases from left to right.
- Y is the layout axis and increases downward in SVG coordinates.
- A lineage centerline must be single-valued and ordered over timeline x.
- Event coordinates must be represented exactly in the sampling mesh.

## Width

- Width is perpendicular geometric thickness, not vertical screen thickness.
- At a valid sample, the distance between upper and lower boundaries equals effective width within tolerance.
- Assembly presence may animate effective width independently from nominal lineage width.
- Width may not be negative or nonfinite.

Normal offsets should satisfy `abs(offset) / curvature_radius <= 0.80`. Compilation warns by default about a nonfinite, unsafe, or x-backtracking offset with its lineage, producer, edge, active shift interval, sampled coordinate, measured curvature, and ratio. Callers may opt into enforcement with `CurvatureSafetyPolicy(mode="reject")`. Explicit discontinuities are separate geometry boundaries; the renderer may not construct a normal offset through one. Removing backward points, changing widths, extending timing, or replacing a curve is not an automatic repair.

## Lifetimes

- Logical lifetimes and stable membership spans use half-open intervals `[start_x, end_x)`.
- The visual end cap may evaluate the left-hand state at `end_x`.
- Membership spans are clipped to both member and assembly lifetimes.
- A terminated lineage consumes no later width, margin, order slot, or dependency.

## Transitions

- `from_x` has the pre-transition state.
- `to_x` has the post-transition state.
- Interpolation occurs strictly between these boundaries.
- Zero-duration events are explicit state changes and may not divide by zero.
- Overlapping transitions of the same property must be normalized or rejected before geometry compilation.
- A public state query and rendered geometry must use the same interpolation function.

## Segment Continuity

- Adjacent segments for one lineage share center, upper, and lower endpoints within tolerance.
- Synthetic join, leave, reorder, and transfer paths are first-class transitions in the authoritative state evaluator.
- Missing assembly geometry is an error, not a fallback to `(x, 0)` or an assembly center.

The current diagnostic seam tolerance is `1e-3` diagram units.

## Assemblies

- A lineage has at most one layout parent at any stable x.
- Every membership has its own stable identity.
- Reorder changes order within one parent; it is not modeled as two ordinary memberships.
- Transfer interpolates between source and destination layout snapshots while emitting one authoritative lineage geometry.
- Assembly dependency cycles are invalid.
- Nested assemblies will form a containment forest with orbit anchor dependencies added to its solve graph.

## Split And Merge

- Child and parent order is resolved before memberships are created.
- All participants query the same event frame and assembly context.
- Color is sampled at the event, not taken from an original constructor value.
- At a shared split or merge frame, participant widths exactly tile the parent or result width. Requested widths are proportional allocation weights; if every requested width is zero, participants receive equal widths. Requested target widths apply after branches have separated or converged.

## Regions

Alliances and similar annotations are post-layout regions. Adding or removing a region must not change lineage geometry. Region components may split when active members are disconnected; the final connected-component policy remains a product decision.
