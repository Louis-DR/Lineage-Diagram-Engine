# Political Data Inventory

The inventory is produced statically by `python -m tools.political_inventory`. It parses source syntax without importing political data modules.

## Baseline

| Measure | Modular source | Monolithic source |
|---|---:|---:|
| Parties | 76 | 73 |
| Federations | 2 | 2 |
| Alliances | 0 | 0 |
| Total entities | 78 | 75 |

There are 51 shared symbol strings, 27 symbols only in the modular source, and 24 only in the monolith. Most differences are composite aliases such as `UMP LR` versus `LR`, but they must be reconciled rather than assumed equivalent.

The JSON inventory also compares normalized static relationship signatures. Variable renames can make semantically identical relationships appear different, so this is a reconciliation queue rather than an automatic equivalence decision.

The modular source contains:

- 86 presidential result calls
- 137 legislative result calls
- 50 senatorial result calls
- 60 European result calls
- 32 position shifts
- 9 explicit joins
- 2 explicit leaves
- 7 explicit merges
- 7 explicit dissolutions

Constructor relationships such as `merge_from`, `secede_from`, and `inside_entity` are recorded separately in the full JSON artifact and will be normalized during migration.

## Historical Import Failure

The static module graph contains:

```text
centralisme -> gaullisme -> radicalisme -> centralisme
```

`centralisme.py` also contains an unqualified `from radicalisme import ...` import. The production `load_france()` path does not import these source modules: it records declarations first and resolves relationships after all entities exist. The files remain migration input until they are rewritten as native records.

## Source Policy

`politics_lib/france/` is the provisional migration source of truth because it is the newer split representation and contains three more entities. The monolith remains a reconciliation input until every difference has been classified.

The migration will introduce stable opaque IDs. Historical abbreviations and names become time-scoped aliases rather than registry keys.

## Generated Artifacts

`generated_political_diagram.py` fails Python parsing at line 132 because a political symbol containing punctuation was embedded in an identifier. It is not a source of truth.

`political_diagram.svg` is useful only as a visual baseline. The modular adapter can now render it through `load_france()`, but visual output cannot validate historical reconciliation or topology correctness.

## Reproduce

```powershell
python -m tools.political_inventory
```

The complete report is written to `artifacts/political-inventory.json`.
