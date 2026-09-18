# Known Defects

The test suite records confirmed defects as strict expected failures. Remove the marker when implementing a fix.

## Engine

| ID | Defect | Reproduction |
|---|---|---|
| ENG-001 | Bundle reorder creates overlapping memberships and an edge seam. | `test_bundle_reorder_is_continuous_and_has_one_membership` |
| ENG-002 | Orbit reorder overwrites or selects duplicate membership geometry. | `test_orbit_reorder_is_continuous_and_has_one_membership` |
| ENG-003 | `terminate_at()` does not close assembly memberships. | `test_termination_closes_assembly_membership` |
| ENG-004 | Transfer has two simultaneous ordinary memberships instead of one transition state. | `test_transfer_emits_one_member_geometry_per_x` |
| ENG-005 | Invalid join/leave topology is not rejected and can stall compilation. | `test_leave_while_independent_is_rejected_immediately` |
| ENG-006 | Automatic bundle split indices are calculated after children have joined. | `test_bundle_split_replaces_parent_slot_before_layout` |
| ENG-007 | `_get_y_at()` and rendered Bezier geometry use different interpolation models. | `test_state_query_matches_rendered_baseline_during_overlapping_shift` |
| ENG-008 | Orbit attachment to an independent compiled transition may use the lineage-wide baseline instead of segment geometry. | Not yet minimized |
| ENG-009 | Tight normal offsets can backtrack or self-intersect; bundle back-filtering is absent. | Existing political SVG and diagnostic backtrack checks |
| ENG-010 | Split/merge widths can overlap because individual widths are clamped without constraining their sum. | Contract decision and fixture still required |
| ENG-011 | Shade state is not time-queryable and overlapping shade events can produce invalid gradient ordering. | Fixture still required |
| ENG-012 | SVG gradient IDs use process memory identity and paths have no semantic IDs. | Structural renderer work pending |
| ENG-013 | Width-only and some assembly events are not sampled exactly in the geometry mesh. | `test_geometry_samples_event_boundaries_exactly` |

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

The small fixture diagnostics currently detect:

- A 6-unit boundary seam in the focused bundle reorder fixture.
- A 5-unit boundary seam in the focused orbit reorder fixture.
- Duplicate active memberships throughout both reorder transitions.
- Simultaneous source and destination memberships during transfer.
- A membership extending from x=0 to x=360 after its lineage terminates at x=160.

The older comprehensive SVG has larger reorder jumps because its widths, margins, and layout differ from the focused fixtures.
