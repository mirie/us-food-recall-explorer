# Phase 4 Handoff — Transparency & UI Polish

State as of the end of Phase 3 (all three slices: core charts, filters &
reactivity, Key Insights — plus two live-review follow-ups on Key Insights'
wording). Read
`US_Food_Recall_Explorer__Streamlit_Data_App___PRD.md` first if you haven't,
then this file. `HANDOFF_PHASE3_SLICE2.md` is the prior handoff — still
accurate on what exists, superseded only on "what's left."

Per the PRD's phase list, Phase 4 is the only phase left before Phase 5
(QA/docs/submission).

## What exists and works

```
recall_explorer/
  schema.py, categories.py, reasons.py     -- unchanged, frozen
  transforms.py   parse_recall_dates(), count_by(), seasonality_matrix(),
                  severity_trend()
  filters.py      apply_filters(), restrict_trend_to_severities()
  insights.py     key_insights() -- total events, % change (first->last full
                  year), peak year, top reason share
  pipeline.py     load_recalls()
  charts.py       seasonality_heatmap(), severity_trend_lines(), top_foods_bar()
app.py            Key Insights row (4 st.metric cards, sentence-format values,
                  "No conclusions" zero-state, "N/A" insufficient-full-years
                  state) rendered above Filters via an early st.container().
                  Filters row live and wired into all three charts. Zero-state
                  message in place of chart sections + Key Insights cards when
                  nothing matches. About expander with 6 data-limitation bullets.
tests/            118 passing: .venv/bin/pytest
```

Start every session with `.venv/bin/pytest`. If it isn't green, fix that
before anything else.

## Phase 4 deliverables, audited against current state

The PRD names four Phase 4 deliverables. Three-plus of them are already
substantially done from earlier phases — this slice is a short, targeted gap
list, not a from-scratch build.

**1. Last-updated timestamp — done, no action needed.**
`app.py` already shows `st.caption(f"Data last updated: {fetched_at:%Y-%m-%d} ...")`
sourced from `data/fetch_metadata.json`. Matches the PRD's "Data Storage &
Privacy" requirement exactly.

**2. Accessible labeling — done, one platform limitation to document rather
than fix.**
The categorical/sequential palette is already validated (see `charts.py`'s
header comment referencing the dataviz skill), every filter widget has a
visible label, and every chart panel is titled with its event/product lens.
One real gap that isn't fixable in this stack: Vega-Lite charts rendered via
`st.altair_chart` have no built-in screen-reader-accessible data table
fallback — this is a Streamlit/Altair platform constraint, not something to
engineer around in this timeframe. Worth one line in the About section
alongside the other data-source-boundary caveats, following the same pattern
the PRD already uses for the meat-category and country-of-origin gaps
(documented limitation, not treated as a bug).

**3. Explanatory notes — mostly done, one concrete gap.**
The About expander has 6 bullets covering the FDA/USDA jurisdiction boundary,
category coverage, reason-tag multi-label caveat, the detection/reporting
confound, missing country-of-origin, and the 2012 start date. But the PRD's
Design Direction section 3 says the About section should consolidate three
specific things: the detection/reporting confound, missing/unreliable field
notes, **and the event-vs-product explanation**. The third one is currently
*only* explained inline via each chart section's caption ("event-level and
product-level side by side") — never spelled out in the About section itself.
Add one more bullet there explaining what the event/product lens split means
and why both are always shown (reuse the ~3.7x ratio fact already established
in the PRD's Design Direction section as a concrete illustration, e.g. "a
single multi-product recall can span dozens of rows in the product lens but
counts once in the event lens").

**4. Robust error UI — the one real gap.**
`load_recalls()` (`pipeline.py`) already raises a clear `ValueError` with an
actionable message when the CSV snapshot is missing, truncated, or has
drifted in schema (`schema.py`'s `validate_schema()`, tested in
`test_schema_guardrail.py`). But `app.py` never catches it — today, a missing
or corrupted snapshot surfaces as Streamlit's default unhandled-exception
page (a raw traceback), not a friendly message. This is the concrete case the
PRD's Advanced Features & Edge Cases bullet ("Disable or warn on chart if
expected columns are missing") maps to for this app — the CSV never changes
at runtime, so the only realistic failure mode is a bad/missing file, already
caught at the pipeline layer and just needing to be surfaced gracefully.
Fix: wrap the `get_data()` call site in `app.py` in `try/except ValueError`,
show `st.error(str(e))`, then `st.stop()` so nothing downstream tries to run
against a `None` dataframe.

## Suggested scope for this slice

Two small, concrete, low-ambiguity changes:

1. One new bullet in the About expander: the event-vs-product lens
   explanation (Design Direction's third required topic).
2. One new bullet in the About expander (or a short standalone note):
   documenting the Vega-Lite screen-reader limitation as a platform
   constraint, matching the tone of the existing bullets.
3. Wrap `get_data()`'s call in `app.py` with `try/except ValueError` →
   `st.error()` + `st.stop()`.

None of this is pure computation — no new `recall_explorer/` module or
function is anticipated, so no TDD cycle is expected. If that assumption
turns out wrong once you're in the code, TDD it as usual per this project's
established practice.

## What's explicitly NOT in this slice

- No new charts, filters, or Key Insights cards — Phase 3 covered all
  interactivity.
- No re-litigating the sentence-format or "No conclusions" wording decisions
  from Phase 3 Slice 2's live-review follow-ups — those are locked.
- Phase 5 (QA, edge-case testing, the final submission Google Doc) stays out
  of scope; this slice is UI/transparency polish only, per the PRD's own
  phase boundary.

## Verification

1. `.venv/bin/pytest` — 118 passing, unchanged (no new pure functions
   anticipated in this slice).
2. Manual: open the About expander, confirm the new event/product and
   accessibility bullets read clearly alongside the existing six.
3. Manual: temporarily rename `data/food_recalls.csv` (or point
   `load_recalls()` at a bad path) and confirm the app shows a friendly
   `st.error()` message instead of a raw traceback; restore the file
   afterward and confirm the app returns to normal.
4. Update `BUILD_LOG.md` and `PROMPT_LOG.md` per the PRD's process
   requirements, same as every prior slice.
