# Known Defects

The test suite records confirmed defects as strict expected failures. Remove the marker when implementing a fix.

## Engine

| ID | Defect | Reproduction |
|---|---|---|
| ENG-009 | Tight normal offsets can backtrack or self-intersect; bundle back-filtering is absent. | Existing political SVG and diagnostic backtrack checks |
| ENG-010 | Split/merge widths can overlap because individual widths are clamped without constraining their sum. | Contract decision and fixture still required |

## Resolved Engine Defects

ENG-001 through ENG-008 and ENG-011 through ENG-013 are covered by ordinary passing regression tests. The fixes introduce normalized scalar timelines, effective color sampling at relationship boundaries, segment-local independent geometry, stable topology memberships with transition reservations, whole-assembly reorder interpolation, lifecycle clipping, deterministic SVG IDs, and exact event-aware sampling.

## Political Data

| ID | Defect | Reproduction |
|---|---|---|
| DATA-001 | Modular imports cycle through centralisme, gaullisme, and radicalisme. | `test_modular_political_dataset_imports` |
| DATA-002 | Monolithic data references CNIP before its definition. | `test_legacy_political_database_imports` |
| DATA-003 | Generated political Python is syntactically invalid at line 132. | Static political inventory |
| DATA-004 | Composite alias strings are used as stable identifiers. | `docs/political-inventory.md` |
| DATA-005 | Same-year result fallback can attach a result to the wrong election. | Adapter test pending loader migration |
| DATA-006 | Missing results are treated as zero rather than unknown. | Adapter test pending loader migration |
| DATA-007 | Shared coalition results are duplicated onto multiple parties. | Data migration report pending |
| DATA-008 | Federation and satellite memberships are projected after split/merge events. | Renderer integration test pending |
| DATA-009 | Dissolution does not consistently close memberships. | Dataset validation pending |
| DATA-010 | Federation shift dictionaries and renderer keys disagree. | Dataset validation pending |

## Baseline Measurements

The 18 focused fixtures currently report zero structural violations under the default diagnostics. Optional self-intersection diagnostics and the unresolved curvature and split/merge width policies remain separate work.
