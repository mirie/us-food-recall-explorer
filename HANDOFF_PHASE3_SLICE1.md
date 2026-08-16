# Phase 3 Handoff — Slice 1: Filters & Reactivity

State as of the end of Phase 2. Read
`US_Food_Recall_Explorer__Streamlit_Data_App___PRD.md` first if you haven't,
then this file. `HANDOFF_PHASE2_SLICE2.md` is the prior handoff — still
accurate on data findings and locked decisions, superseded only on "what
exists."

**Phase 3 has two slices.** This one is filters + making the three existing
charts reactive to them. Key Insights (4 computed stat cards) is Slice 2,
deliberately deferred — it's simpler once filtered data already exists, and
bundling it here would make this slice too large to review well. Don't start
Key Insights in this slice.

## What exists and works

```
recall_explorer/
  schema.py, categories.py, reasons.py     -- unchanged, frozen
  transforms.py   parse_recall_dates(), count_by(), seasonality_matrix(),
                  severity_trend()
  pipeline.py     load_recalls()
  charts.py       seasonality_heatmap(), severity_trend_lines(), top_foods_bar()
app.py            all three charts LIVE, side by side, both lenses.
                  Key Insights section is still an st.info() placeholder.
tests/            88 passing: .venv/bin/pytest
```

Start every session with `.venv/bin/pytest`. If it isn't green, fix that
before anything else.

## The four filters, per the PRD (Functional Requirements)

1. **Year range** — slider or two-ended selector over `year`. Clean int
   column, nothing derived needed.
2. **Category** — dropdown/multiselect over `category`. Single value per
   row (already resolved by the priority-ordered regex ladder in
   `categories.py`), `Uncategorized` is a normal selectable value, not a
   special case.
3. **Reason** — multiselect over `reason_tags`, which is a **list column**,
   not a plain categorical. A recall can carry more than one tag (e.g.
   `["Undeclared allergen", "Foreign material"]`). Tag distribution on the
   full dataset, for reference:

   ```
   Undeclared allergen   8268      Chemical/contaminant    663
   Listeria               7470      Other pathogen           630
   Salmonella              3606      E. coli                  542
   Processing/temperature  1881      Botulism risk            379
   Foreign material         1668

   Untagged ("Other"): 15.7% of rows
   ```

   Tags are not mutually exclusive and don't sum to the row count — any
   derived share is "of recalls mentioning X," never "share of all
   recalls" (this is already stated in the About section; don't restate it
   per-chart, per the no-footnotes rule).
4. **Severity** — multiselect/checkboxes over `classification`. Clean
   3-value categorical, nothing derived needed.

## Two decisions settled with Mai before this doc was handed off

**Reason filter uses OR semantics.** Selecting Salmonella + Listeria shows
recalls tagged with *either*, not only recalls tagged with both. Matches the
PRD's own user-story phrasing ("identify patterns for specific pathogens,
e.g. Salmonella or Listeria") and is the standard reading of a multiselect
filter. AND semantics were considered and rejected — most recalls carry only
one or two tags, so an AND filter across three or more selections would
return near-empty results almost immediately, which isn't the analyst
question being asked.

**"Other" (untagged) is its own selectable option in the reason filter, not
an always-shown row.** Symmetric with how `Uncategorized` already behaves in
the category dimension: it's a real, first-class value the user can include
or exclude, not a permanent exception. Default state (nothing selected in
the reason filter = show all) includes untagged rows same as today; the
moment a user selects one or more specific reasons, untagged rows drop out
*unless* "Other" is also selected. Implementation note: this makes the
reason filter's option list `REASON_LABELS + ["Other"]`, where `REASON_LABELS`
should be sourced from `reasons.REASON_RULES` (import the labels, don't
hand-copy the list — it must stay in sync if a rule is ever added).

## Implementation shape

**New module: `recall_explorer/filters.py`.** One pure function,
`apply_filters(df, year_range=None, categories=None, reasons=None,
severities=None)`, each parameter `None` meaning "no filter on this
dimension" (the default/unfiltered state). Returns the filtered DataFrame.
TDD this first, hand-built fixtures, same contract as every other transform
in this codebase (`HANDOFF_PHASE2.md`'s testing contract, restated in every
handoff since — it hasn't changed). Test cases to cover at minimum:

- each of the four filters in isolation
- two filters combined (they should compose as AND across dimensions —
  e.g. year range AND category, even though *within* the reason dimension
  it's OR across selected tags)
- the reason filter's OR-across-tags behavior specifically, including a row
  with multiple tags matching on just one of them
- the reason filter's "Other" behavior: a specific reason selected without
  "Other" drops untagged rows; adding "Other" brings them back
- no filters applied returns the input unchanged (or an equal copy)
- a filter combination that yields zero rows returns an empty DataFrame
  without raising

**`app.py` wiring.** Filter widgets go in the position the PRD's own layout
puts them: below the intro/last-updated line, above the chart sections —
which today means directly below the Key Insights placeholder, since that
section hasn't been built yet. Don't try to guess Key Insights' final layout
here; Slice 2 can reposition if needed. Compute `filtered_df =
apply_filters(df, ...)` once, near the top, and thread it into all three
existing chart sections in place of the current unfiltered `df`. The
per-chart code (`seasonality_matrix`, `severity_trend`, `count_by`) doesn't
need to change at all — they already operate on whatever DataFrame they're
given.

**`coverage_end` stays anchored to the full dataset, not the filtered
one.** `coverage_year, coverage_month` are already computed from
`fetch_metadata.json`, independent of `df` — don't switch that to be
derived from `filtered_df`. If a user filters the year range to exclude
2026 entirely, the trend chart's dashed-segment logic should simply not
apply (no partial year in the filtered range), which falls out naturally
from `severity_trend()`'s existing `partial` flag once the filtered df
doesn't contain 2026 rows — no special-casing needed, but worth a specific
manual check in the visual review below.

**Zero-state handling (PRD line 114, Advanced Features & Edge Cases).** If
`filtered_df` is empty, don't attempt to render any chart — `seasonality_matrix`
and friends will likely raise on an empty frame (e.g. `df["year"].min()` on
zero rows) rather than degrade gracefully, and that's fine; don't add
defensive code inside the transforms for a case the app layer should
short-circuit before calling them. Show a single friendly message (e.g.
`st.info("No recalls match the current filters. Try widening the year range or clearing a filter.")`)
in place of all three chart sections when `len(filtered_df) == 0`, checked
once near the top of the file, not duplicated per section.

**Category filter reaches the top-foods chart too**, same as every other
filter — no special-casing there either. If a user filters to a single
category, that chart legitimately renders one bar per lens panel; that's
correct behavior, not a bug to work around.

## What's explicitly NOT in this slice

- Key Insights row (4 stat cards) — Slice 2.
- Any recomputation of `About the data & limitations` copy — it's already
  general enough to not need per-filter wording.
- LLM category labelling — still Phase 3 (added), still deferred per every
  prior handoff.
- Performance optimization beyond what `st.cache_data` already gives
  `get_data()` — 29,161 rows is trivial for pandas per every prior note on
  this; don't add caching layers for the filtered subset unless a real
  slowdown shows up in manual testing.

## Verification

1. `.venv/bin/pytest` — 88 existing plus new `filters.py` tests, all green.
2. `streamlit run app.py`, manual check: every filter actually changes every
   chart (including both lens panels); the zero-state message appears and
   the three chart sections disappear when filters exclude everything;
   clearing filters restores the full view; the trend chart's dashed segment
   only appears when the filtered range actually includes 2026.
3. Update `BUILD_LOG.md` and `PROMPT_LOG.md` per the PRD's process
   requirements, same as every prior slice.
