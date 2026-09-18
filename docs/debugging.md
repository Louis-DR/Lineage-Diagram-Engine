# Debugging And Visual Validation

## Test Suite

```powershell
python -m pytest
```

Passing tests characterize established behavior. Strict expected failures identify confirmed defects. Pytest will report an unexpected pass as a failure until the corresponding marker is deliberately removed.

## Geometry Report

```powershell
python -m tools.geometry_diagnostics
```

The command builds every small fixture through the production `Diagram.compile()` pipeline and writes `artifacts/diagnostics/geometry.json`.

Current violation kinds include:

- `segment-seam`
- `event-boundary-missing`
- `x-backtrack`
- `non-finite-coordinate`
- `non-finite-width`
- `negative-width`
- `width-error`
- `overlapping-memberships`
- `overlapping-layout-parents`
- `multiple-active-memberships`
- `membership-after-termination`
- `dependency-cycle`
- `polygon-self-intersection`

Use `--self-intersections` for the more expensive polygon check.

## Fixture Gallery

```powershell
python -m tools.render_fixtures
```

Open `artifacts/fixtures/index.html`. Each fixture includes:

- Plain SVG
- Debug SVG
- Headless-browser PNG when Edge or Chromium is available
- Per-fixture geometry JSON
- Event boundary lines
- Centerlines and sample markers
- Measured violation counts

The gallery deliberately uses small diagrams. A defect should be reduced here before using the comprehensive or political diagram for diagnosis.

Use `--fail-on-violations` only after known defects have been fixed or excluded; the baseline intentionally contains expected failures.

## Political Inventory

```powershell
python -m tools.political_inventory
```

This command never imports political modules. It reports entity declarations, result calls, relationships, import cycles, source divergence, and generated-file parse failures.

## Adding A Regression

1. Add a fixture builder to `tools/fixture_cases.py`.
2. Add it to `FIXTURE_BUILDERS` if it should appear in the gallery.
3. Add a focused assertion to the test suite.
4. Mark a confirmed current defect with strict `xfail` and a specific reason.
5. Run tests, diagnostics, and the gallery.
6. When fixed, remove `xfail` and keep the assertion permanently.

## Full Diagrams

Do not use the multi-megabyte political SVG as a primary snapshot. Once deterministic semantic SVG exists, store small fixture snapshots and publish full renders as build artifacts. Event-focused crops are more useful to both humans and vision-capable agents than one extremely wide image.
