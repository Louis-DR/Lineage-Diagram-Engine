# Known Defects

The test suite records confirmed defects as strict expected failures. Remove the marker when implementing a fix.

## Engine

| ID | Defect | Reproduction |
|---|---|---|

## Resolved Engine Defects

ENG-001 through ENG-013 are covered by ordinary passing regression tests. The fixes introduce normalized scalar timelines, packet-conserving split/merge widths, curvature-safe normal-offset rejection, effective color sampling at relationship boundaries, segment-local independent geometry, stable topology memberships with transition reservations, whole-assembly reorder interpolation, lifecycle clipping, deterministic SVG IDs, and exact event-aware sampling.

## Political Data

| ID | Defect | Reproduction |
|---|---|---|
| DATA-002 | Monolithic data references CNIP before its definition. | `test_legacy_political_database_imports` |
| DATA-003 | Generated political Python is syntactically invalid at line 132. | Static political inventory |
| DATA-005 | Same-year result fallback can attach a result to the wrong election. | Adapter test pending loader migration |
| DATA-006 | Missing results are treated as zero rather than unknown. | Adapter test pending loader migration |
| DATA-007 | Shared coalition results are duplicated onto multiple parties. | Data migration report pending |

## Baseline Measurements

Twenty safe focused fixtures report zero structural violations. Three expected-warning curvature fixtures exercise independent, Bundle, and Orbit offset diagnostics. Optional polygon self-intersection remains a separate postcondition.

DATA-001, DATA-004, DATA-008, DATA-009, and DATA-010 are resolved by the deterministic French two-pass loader and normalized assembly transfers. The monolith remains reconciliation input and retains its import xfail.
