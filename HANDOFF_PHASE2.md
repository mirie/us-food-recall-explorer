# Phase 2 Handoff — App Skeleton & Core Charts

State as of the end of Phase 1. Read `US_Food_Recall_Explorer__Streamlit_Data_App___PRD.md` first, then `BUILD_LOG.md` Entries 1–2.5. This file is the short version.

## What exists and works

```
fetch_data.py              one-time openFDA fetch (already run -- do NOT re-run)
data/food_recalls.csv      29,161 rows x 19 cols, 2012-01-03 to 2026-07-08
data/fetch_metadata.json   fetch timestamp + openFDA last_updated (for the "data last updated" label)
recall_explorer/
  schema.py                EXPECTED_COLUMNS, validate_schema()
  categories.py            assign_category()  -- precedence ladder, first match wins
  reasons.py               tag_reasons()      -- multi-label
  transforms.py            parse_recall_dates(), count_by(df, dimension, lens)
  pipeline.py              load_recalls()     -- the only module touching the filesystem
tests/                     63 passing:  .venv/bin/pytest
```

Start every session with `.venv/bin/pytest`. If it isn't green, fix that before anything else.

`load_recalls()` returns the analysis-ready frame with `recall_date`, `year`, `month`, `category`, `reason_tags` already derived. **Phase 2 should not need to touch any file in `recall_explorer/` except to add chart-shaping functions.**

## The numbers Phase 2 will render

```
29,161 product rows  /  7,791 events  =  3.74 products per event

Produce 15.9%  Bakery 13.1%  Dairy 12.6%  Uncategorized 12.2%
Prepared/Frozen 7.2%  Seafood 6.7%  Spices 6.1%  Snacks 6.0%
Supplements 5.5%  Nuts/Seeds 5.1%  Beverages 4.5%  Grains/Cereal 3.5%
Poultry 0.7%  Pork 0.3%  Beef 0.2%  Plant Protein 0.2%  Oils/Fats 0.2%

Reasons (multi-label, 84.3% tagged):
Undeclared allergen 28.4%  Listeria 25.6%  Salmonella 12.4%
Processing/temperature 6.5%  Foreign material 5.7%

Severity: Class II 14,616  Class I 12,804  Class III 1,741
```

## Decisions already made — do not relitigate

1. **Side-by-side event/product lenses on every chart.** Never a toggle. `st.columns`. Use `count_by(df, dim, lens="events"|"products")`.
2. **Chart type per data shape**: seasonality = heatmap/dot-matrix, trend = line, top foods = horizontal bar. Not bars everywhere.
3. **Key Insights row**: 4 computed cards, rule-based, event-level framed. Never LLM-generated, never causal or evaluative.
4. **One collapsible "About the data & limitations"**, not per-chart footnotes.
5. **Partial 2026 is the single permitted exception to #4** — plot it as a dashed final segment labelled "partial year — through Aug 2026". Do not annualise or project; that invents data. Snapshot ends 2026-08-05, so 2026 plots 692 vs 2025's 1,571, a phantom 56% drop.
6. **`Uncategorized` stays visible** in the top-foods chart. It is the only element that admits the category rules are rules.
7. **Range is 2012–2026**, never 2004. The wireframe's `2004 —— 2026` axis is superseded.

## Testing contract (from Mai, applies to every slice)

- **TDD the pure logic.** Chart shaping goes through a `transform_for_chart()`-style pure function, unit-tested with hand-built DataFrames. Never read the real CSV in a unit test.
- **Do not assert on rendered output** — no SVG bar heights, no pixel/screenshot diffs. Trust the chart library; test your data going into it.
- **One "renders without crashing" smoke test per chart**, using real pipeline output.
- **Update the pipeline E2E test** after each slice is demo-able; update the schema guardrail if columns change.
- Visual correctness (colour, layout, label readability) is a **manual design review** per slice, not automated.
- Commit iteratively — one commit per green slice, not one big one.

## Known limitations to surface in the About section

- **openFDA covers FDA-regulated food only.** Meat, poultry, and processed egg products are USDA FSIS jurisdiction and absent here — which is why the meat categories are near-empty. Say this, or a reader concludes meat is rarely recalled.
- **Category is keyword-derived, lossy, and of unmeasured accuracy.** ~12.2% `Uncategorized` — but that is *coverage*, not correctness. Accuracy on the ~88% that do get a label has never been measured. Five distinct failure classes were found and fixed during Phase 1, every one by someone happening to inspect the right rows rather than by any systematic process; the worst (packaging words like "clamshell") had inflated Seafood by 25% while sitting inside "successfully categorised". Assume a sixth class exists. **Category rules are frozen as of Phase 1 — do not patch them reactively during Phase 2.** The replacement plan is the Phase 3 LLM pass.
- **Reason tags are multi-label**, so any share is "of recalls mentioning X", never "share of total". Only 1.7% of recalls carry 2+ tags, so the distortion is small — but the wording must still be right.
- **Recall counts are not a food-safety measure.** Changes may reflect detection and reporting practice. Standing caveat.
- **No country of origin exists** in this data. `country`/`state` are the recalling firm's address.
- **2012 start is a data-availability boundary**, not evidence that recalls began then.

## Open questions for Phase 2

- **Seasonality is completely unexamined.** The month distribution has never been looked at. This is the only core question whose answer is genuinely unknown — worth starting here.
- **17 categories may be too many** for a readable horizontal bar. Consider collapsing the tail into a display-only "Other" while keeping the underlying data intact.
- Whether the Key Insights cards should recompute from filtered data on every interaction (PRD says yes) or debounce.

## Deferred to Phase 3

LLM-assisted category labelling — see the PRD's Phase 3 section. Not dropped.
