# Phase 2 Handoff — Slice 2: Trend-Over-Time & Top Recalled Foods

State as of the end of Phase 2 Slice 1 (seasonality). Read
`US_Food_Recall_Explorer__Streamlit_Data_App___PRD.md` first if you haven't,
then this file. `HANDOFF_PHASE2.md` is the prior handoff — still accurate on
data findings and locked decisions, superseded only on "what exists."

**Not ready for Phase 3.** Phase 3 (filters & interactivity) depends on all
three core charts existing — the PRD's own phase dependency, not a guess.
Two remain: trend-over-time (line chart) and top recalled foods (bar chart).

## What exists and works

```
recall_explorer/
  schema.py, categories.py, reasons.py     -- unchanged, frozen (see below)
  transforms.py   parse_recall_dates(), count_by(), seasonality_matrix()
  pipeline.py     load_recalls()
  charts.py       seasonality_heatmap()
app.py            page shell -- header, About section, seasonality section
                  LIVE. Trend and top-foods sections are st.info() placeholders
                  at app.py:82 and app.py:86.
tests/            75 passing: .venv/bin/pytest
```

Start every session with `.venv/bin/pytest`. If it isn't green, fix that
before anything else.

## The numbers these two slices will render

```
Yearly counts (event lens / product lens):
2012  515 / 2151    2017  599 / 2623    2022  452 / 1427
2013  546 / 2420    2018  578 / 1977    2023  478 / 2221
2014  573 / 2451    2019  516 / 1807    2024  482 / 1387
2015  607 / 2750    2020  381 / 1117    2025  569 / 1571
2016  799 / 3066    2021  463 / 1501    2026  233 /  692 (partial year)

Severity by year, event lens (Class I / Class II / Class III):
2012  266/218/50   2017  248/321/38   2022  171/256/34
2013  203/298/65   2018  199/326/63   2023  165/263/63
2014  284/251/53   2019  182/302/45   2024  189/272/42
2015  284/289/48   2020  134/223/33   2025  213/312/51
2016  415/358/40   2021  160/269/43   2026   85/134/17

Overall severity: Class II 14,616  Class I 12,804  Class III 1,741

Top categories, event lens:  Produce 1443, Uncategorized 1305, Bakery 1229,
  Dairy 899, Prepared/Frozen 816, Snacks/Candy 791
Top categories, product lens: Produce 4645, Bakery 3824, Dairy 3669,
  Uncategorized 3554, Prepared/Frozen 2089, Seafood 1959

17 categories total (unchanged from Phase 1):
Bakery, Beef, Beverages, Dairy, Grains/Cereal, Nuts/Seeds, Oils/Fats,
Plant Protein, Pork, Poultry/Eggs, Prepared/Frozen, Produce, Seafood,
Snacks/Candy, Spices/Condiments, Supplements, Uncategorized
```

2016 and 2020 stand out (799 events vs. neighbors' ~550-600; 381 vs.
neighbors' ~450-600). Both are facts about the shape, not causes — do not
attribute either to a specific external event. That's exactly the causal
framing the PRD's Non-Goals and Key Insights rules forbid.

## Decisions already made — do not relitigate

All of `HANDOFF_PHASE2.md`'s seven decisions still hold. Additions from
Slice 1:

8. **`covered`-flag pattern for calendar-aware transforms.** `coverage_end`
   is read from `fetch_metadata.json`'s `openfda_last_updated`, not derived
   from `max(recall_date)` — the two differ by openFDA's ~4-week reporting
   lag, and using the metadata date correctly renders the most recent
   covered period as a real (possibly low) count rather than as unobserved.
   `app.py` already computes `coverage_year, coverage_month` from metadata
   at the top of the seasonality section — reuse that pair rather than
   recomputing it if the trend chart needs the same boundary.
9. **The partial-2026 dashed-segment rule is real and unclaimed.** It was
   deliberately *not* applied to the seasonality heatmap (blank cells are
   self-explanatory on a calendar grid, per the Slice 1 build log). The
   trend line chart is the one place `HANDOFF_PHASE2.md` decision #5 and PRD
   line 62 actually require it: 2026 holds ~7 months against every other
   year's 12, and an unmarked line would show recall volume looking like it
   dropped by half. Render 2026 as a dashed final segment, labeled
   "partial year — through July 2026" (the last real `recall_initiation_date`
   is 2026-07-08; do not use openFDA's 2026-08-05 metadata date for this
   label, that's the fetch/publication timestamp, not the last recall date).
   Do not annualize or project — explicitly forbidden, invents data.

## Testing contract (unchanged, from `HANDOFF_PHASE2.md`)

TDD the pure transform first, hand-built DataFrames, never the real CSV in a
unit test. One smoke test per chart against real `load_recalls()` output,
marked `@pytest.mark.pipeline`. No assertions on rendered SVG/pixels. Visual
correctness is a manual design review — this session used a headless-Chrome
+ CDP screenshot to do that (see Slice 1's build log entry for the recipe;
`chromium-cli` wasn't available in this environment).

## Suggested order and what's new per slice

**Top recalled foods first — it needs no new transform.** `count_by(df,
"category", lens)` already exists and already returns exactly what a
horizontal bar chart needs (dimension + count, sorted descending). This
slice is close to chart-only: `top_foods_bar()` in `charts.py`, wired into
`app.py`'s existing placeholder. The open question carried from
`HANDOFF_PHASE2.md`: **17 categories may be too many for a readable bar
chart** — decide whether to collapse the tail into a display-only "Other"
(keeping `df["category"]` itself untouched) before or after seeing it
rendered. `Uncategorized` stays visible regardless (locked decision #6).

**Trend-over-time second — this one needs both a transform and the dashed-
segment chart logic.** Shape the transform as year x count (or year x
severity x count, if the line chart splits by Class I/II/III — the PRD says
"volume/severity," which is genuinely ambiguous between "one line, total
volume" and "three lines, one per severity class"; look at the severity-by-
year numbers above before deciding, and treat it as a real design question
worth a quick check-in rather than a guess to freeze into passing tests, the
way seasonality's chart shape was decided last session). The dashed-segment
requirement (decision #9 above) is the main implementation risk — Altair
supports this via a `strokeDash` encoding conditioned on a `partial: bool`
column the transform should emit, following the same shape `seasonality_matrix()`
used for `covered`.

## Deferred to Phase 3

Filters (year range, category, reason, severity), Key Insights row, and the
event/product lens becoming filter-reactive. Don't start these until both
remaining chart modules exist — per the PRD's own phase dependency, not a
guess.

## Deferred to Phase 3 (LLM labelling)

Unchanged from `HANDOFF_PHASE2.md` — not in scope for this slice either.
