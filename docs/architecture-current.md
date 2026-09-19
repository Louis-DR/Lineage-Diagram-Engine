# Current Architecture

## Engine Flow

`Diagram` owns lineages, bundles, and orbits. Calling `Diagram.compile()` performs the existing layout pipeline without serializing SVG:

1. Solve every bundle baseline and member stack.
2. Build lineage dependencies from orbit satellites to their main lineages.
3. Compile lineages in topological order.
4. Solve each orbit after its main lineage has compiled.
5. Return lineages ordered by z-index.

`Diagram.to_svg()` compiles, draws every lineage, and returns a document string. `Diagram.generate()` writes that string to disk.

## State Storage

`Lineage` stores four independent event lists:

- Position shifts
- Width changes
- Color changes
- Assembly joins and leaves

`compile_segments()` converts membership events into independent and dependent segments. Independent segments create normal offsets around a Bezier baseline. Dependent segments retrieve points from a `Bundle` or `Orbit`.

Several other methods independently reconstruct lineage state for splits, merges, branches, and orbit attachment. This duplication is the primary architectural defect because these reconstructions disagree at event boundaries.

## Assemblies

`Bundle` owns a shifting baseline and packs active member widths plus margins around it. Membership order is the insertion order in one global list.

`Orbit` depends on a main lineage. It derives the main lineage center and normal, then places satellites outward on positive or negative indexed sides.

Membership geometry caches are keyed by lineage object rather than membership identity. This cannot correctly represent reorder transitions that create two memberships for the same lineage.

## Political Flow

Importing `politics_lib` exports the domain API without loading French data. `load_france()` records the provisional source modules with peer imports removed, creates every entity with a stable opaque ID, then resolves facts and relationships in a deterministic second pass. The legacy runtime objects remain mutable compatibility adapters while the source is migrated to native records.

`render_political_diagram.py` performs a second imperative translation:

1. Call `load_france()` and create federation bundles.
2. Create initial party lineages.
3. Apply merge, split, and position events.
4. Apply federation memberships.
5. Apply party satellite memberships.
6. Generate SVG and rewrite the file to insert overlays.

The ordering means topology events do not reliably see federation or satellite state that was historically active at the same date.

## Target Boundaries

The intended replacement pipeline is:

```text
validated domain data
  -> renderer-neutral DiagramSpec
  -> normalized topology timeline
  -> authoritative state evaluator
  -> assembly layout
  -> ribbon geometry
  -> regions and annotations
  -> deterministic SVG scene
```

The existing `Lineage`, `Bundle`, and `Orbit` calls can remain as a builder facade while their event storage and compiler are replaced.
