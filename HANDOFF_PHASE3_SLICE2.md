# Phase 3 Handoff — Slice 2: Key Insights

State as of the end of Phase 3 Slice 1 (filters & reactivity). Read
`US_Food_Recall_Explorer__Streamlit_Data_App___PRD.md` first if you haven't,
then this file. `HANDOFF_PHASE3_SLICE1.md` is the prior handoff — still
accurate on data findings and locked decisions, superseded only on "what
exists."

This is the last slice of Phase 3. After this, Phase 4 (transparency & UI
polish) is the only PRD phase left before Phase 5 (QA/docs/submission).

## What exists and works

```
recall_explorer/
  schema.py, categories.py, reasons.py     -- unchanged, frozen
  transforms.py   parse_recall_dates(), count_by(), seasonality_matrix(),
                  severity_trend()
  filters.py      apply_filters(), restrict_trend_to_severities()
  pipeline.py     load_recalls()
  charts.py       seasonality_heatmap(), severity_trend_lines(), top_foods_bar()
app.py            Filters row (year slider + 3 multiselects) live and wired
                  into all three charts via filtered_df. Zero-state message
                  in place of all three chart sections when nothing matches.
                  Key Insights section is still an st.info() placeholder,
                  positioned above the Filters row.
tests/            104 passing: .venv/bin/pytest
```

Start every session with `.venv/bin/pytest`. If it isn't green, fix that
before anything else.

## The one non-obvious architectural issue this slice must solve first

**Key Insights needs `filtered_df` to compute its numbers, but the PRD
places it visually *above* the Filters row** ("Below that: intro line on
scope, filters, and a link to the collapsible About section" — Key Insights
comes first). In plain Streamlit, calling a widget (`st.slider`,
`st.multiselect`) both renders it *and* returns its current value at that
call site, so filter values aren't known until the filter widgets have been
called — which happens later in the script than where Key Insights needs to
render.

Fix: create an `st.container()` for Key Insights **before** the Filters
section is defined, keep the reference, compute `filtered_df` as usual after
the filter widgets, then render the four `st.metric(...)` calls **into that
earlier container** (`with key_insights_container: st.metric(...)`).
Streamlit renders containers in the position they were created, not the
position their content was last written, so this gets the PRD's visual order
without restructuring the filter-then-compute flow Slice 1 already built.

## Four cards, locked with Mai before this doc was handed off

The PRD names four allowed stat *types* (magnitude, percentage change,
peak/low, share of total) but leaves the specific numbers open. Settled,
via a concrete preview built from real numbers on the full dataset:

1. **Total events** — `filtered_df["event_id"].nunique()`. Plain magnitude,
   no comparison.
2. **% change** — from the first full year in the current view to the last
   full year in the current view. Not a hardcoded baseline year (e.g. "since
   2014") — that breaks the moment someone filters the year range. "Full
   year" excludes 2026, the one partial year in this dataset (reuse the
   `partial` flag shape from `severity_trend()`/`coverage_end` — a year is
   partial if `year*12+12 > coverage_end_key`, using the **full dataset's**
   `coverage_end`, not a filtered one, same anchoring rule as the trend
   chart's dashed segment). Degrade gracefully if the filtered range
   contains zero or one full year (e.g. filtered to 2026 alone, or a
   single-year range) — show "N/A" rather than dividing by zero or a
   meaningless 0%.
3. **Peak year** — the full year (again excluding partial 2026) with the
   highest event count in the current view, plus its count.
4. **Top reason** — the reason tag with the highest share of events in the
   current view (`reason_tags`, event-level, not product-level — a recall
   with 400 products should count once per event, same as everywhere else in
   this app), shown as "`<label>`: `<pct>`% of events." Include "Other"
   (untagged) as a candidate in this ranking — it's a real, first-class
   value everywhere else in this app (Slice 1's locked decision), so it
   should be eligible to win the "top reason" slot too, not silently
   excluded from the comparison.

Rejected: Class I severity share and top-category share, both considered —
dropped because the trend chart and top-foods chart already show that same
information in full underneath Key Insights; the reason-tag share doesn't
duplicate anything else on the page.

**Reference numbers, full dataset, no filters** (verify your implementation
against these before wiring the container-positioning fix):

```
Total events: 7,791
% change, first full year (2012) -> last full year (2025): +10.5%  (515 -> 569)
Peak year: 2016, 799 events
Top reason: Undeclared allergen, 3,066 events, 39.4% of events
  (runner-up: Salmonella 912/11.7%, Listeria 903/11.6%, Other/untagged
  1,636/21.0% -- Other would win the "top reason" slot only if allergen
  labeling failures were excluded, which they aren't)

Full event-count-by-year series, for the peak/low and %-change logic:
2012  515    2017  599    2022  452
2013  546    2018  578    2023  478
2014  573    2019  516    2024  482
2015  607    2020  381    2025  569
2016  799    2021  463    2026  233 (partial -- excluded from peak/%-change)
```

## Rule-based, never causal, never colorized as good/bad

Direct PRD requirement, not new: no evaluative language ("food safety is
improving"), no causal framing. Extends to *styling* here specifically —
`st.metric()`'s default green-up/red-down `delta` arrow implies a value
judgment (green = good) that doesn't apply to a recall-count going up or
down. Pass `delta_color="off"` on the % change card so the number speaks for
itself without an implicit good/bad color cue.

## Zero-state interaction (PRD line 114, Advanced Features & Edge Cases)

"Key Insights row also reflects zero state." Slice 1 already wraps the three
chart sections in `if len(filtered_df) == 0: st.info(...) / else: <charts>`.
Key Insights needs the same branch — inside the `if` branch, render the four
cards as empty/dash placeholders (e.g. "—") rather than crashing on
`nunique()` of an empty frame or a peak-year `idxmax()` with no rows.

## What's explicitly NOT in this slice

- Any change to `apply_filters()`, `restrict_trend_to_severities()`, or the
  three existing chart builders — this slice is additive (a new
  `key_insights()`-style computation plus four `st.metric()` calls), not a
  refactor of Slice 1.
- LLM category labelling — still deferred, unchanged.
- Phase 4 (transparency & UI polish beyond what's already in the About
  section) — separate phase, don't start it here.

## Testing contract (unchanged)

TDD the computation as a pure function first — e.g. `key_insights(df,
coverage_end)` returning a small dict/namedtuple of the four values, in a new
`recall_explorer/insights.py`, tested against hand-built fixtures the same
way `filters.py` and `transforms.py` were. `app.py` then only formats and
places the returned values into `st.metric()` calls — keep the percentage
math, the full-year exclusion, and the top-reason ranking in the tested pure
function, not inline in `app.py`.

## Verification

1. `.venv/bin/pytest` — 104 existing plus new `insights.py` tests, all green.
2. `streamlit run app.py`, manual check: Key Insights renders above Filters
   (not below, despite being computed after); all four cards update when any
   filter changes; the zero-state case shows dash placeholders instead of
   crashing; a year-range filter that excludes every full year (e.g. 2026
   alone) shows "N/A" for % change and peak year rather than an error.
3. Update `BUILD_LOG.md` and `PROMPT_LOG.md` per the PRD's process
   requirements, same as every prior slice.
