# Lineage Diagram Engine

This repository contains a Python engine for drawing variable-width lineage diagrams over a horizontal timeline and an incomplete database of French political history.

The engine supports independent ribbons, bundles, satellites orbiting another ribbon, width and position transitions, color transitions, splitting, merging, branching, reordering, transfers between assemblies, and post-layout Regions around changing groups. Width is intended to represent perpendicular geometric thickness through curves.

The political projection maps parties to lineages, federations to bundles, selected party relationships to orbits, and political alliances to Regions. The political data is loaded through an order-independent two-pass loader.

## Status

The standalone and political examples render. Unsafe perpendicular offsets are reported by the configured curvature policy. See:

- `docs/known-defects.md`
- `docs/geometry-contract.md`
- `docs/political-inventory.md`
- `docs/regions.md`

## Development

Python 3.10 or later is required.

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m tools.geometry_diagnostics
python -m tools.render_fixtures
python -m tools.political_inventory
```

Generated diagnostics are written under `artifacts/` and are not committed.

## Repository Map

- `lineage_diagram/`: diagram model, geometry, assembly layout, and SVG rendering.
- `tools/fixture_cases.py`: small feature fixtures used for geometry and visual checks.
- `tools/geometry_diagnostics.py`: machine-readable geometry validation.
- `tools/render_fixtures.py`: SVG, PNG, and HTML fixture gallery generation.
- `politics_lib/`: provisional modular political data source.
- `render_political_diagram.py`: legacy political-to-engine adapter.
- `comprehensive_example.py`: broad legacy feature demonstration.
- `docs/`: architecture, contracts, inventory, and debugging guidance.
