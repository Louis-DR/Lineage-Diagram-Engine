# Engineering Guide

## Purpose

The repository has two distinct systems:

- `lineage_diagram/` is a generic variable-width timeline ribbon engine.
- `politics_lib/` and `render_political_diagram.py` describe and project French political history.

Keep political concepts out of the generic geometry engine. The political adapter may depend on the engine; the engine must not depend on political data.

## Authority

- `politics_lib/france/` is the provisional political migration source of truth.
- `politics_database.py` is reconciliation input, not production code.
- `*.backup`, `generated_political_diagram.py`, `.history/`, SVGs, and `artifacts/` are not authoritative source.
- `comprehensive_example.py` is a scenario inventory. Its current visual output is not automatically correct.
- `docs/geometry-contract.md` defines target behavior when current behavior conflicts with the intended architecture.

Do not delete legacy political sources until the inventory reports that every divergent entity and relationship has been classified.

## Commands

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m tools.geometry_diagnostics
python -m tools.render_fixtures
python -m tools.political_inventory
```

The expected baseline includes strict `xfail` tests. When fixing one, remove its `xfail` marker in the same change so an unexpected pass cannot be ignored.

## Geometry Workflow

1. Add or reduce a defect to a fixture in `tools/fixture_cases.py`.
2. Add a structural assertion before changing layout code.
3. Run `python -m tools.geometry_diagnostics`.
4. Inspect `artifacts/fixtures/index.html` after `python -m tools.render_fixtures`.
5. Change the smallest relevant layout layer.
6. Re-run the complete suite and fixture gallery.

Every geometry failure should report a lineage, event coordinate, and measured error. Do not rely only on a full political SVG or verbal visual feedback.

## Required Invariants

- Coordinates and widths are finite.
- Widths are nonnegative.
- A normal lineage has one authoritative layout state at each x.
- Memberships do not outlive their lineage or assembly.
- Segment boundaries are geometrically continuous unless an explicit discontinuity is modeled.
- Event boundaries are sampled exactly.
- Dependency cycles are validation errors.
- SVG IDs and ordering must become deterministic before snapshot tests are authoritative.
- Enabling annotations such as alliances must not alter lineage geometry.

Perpendicular width and timeline x can conflict on very tight curves. Do not hide this with arbitrary point deletion. Detect unsafe curvature and follow `docs/geometry-contract.md`.

## Data Workflow

Political source modules currently execute constructors and relationships at import time. Do not fix circular dependencies by repeatedly changing import order. The migration target is a two-pass loader:

1. Load entity records with stable IDs.
2. Resolve relationships and events after every entity is known.

Run the static inventory after political-data edits. Historical names and abbreviations are not stable IDs. Rendering overrides do not belong in historical facts.

## Editing Rules

- Preserve the existing public builder vocabulary while the geometry kernel is replaced behind it.
- Prefer typed records over dictionaries with undocumented string keys.
- Add validation at event creation, not only during rendering.
- Keep generated files out of source control unless they are deliberately small test snapshots.
- Do not calibrate political positions to compensate for geometry bugs.
