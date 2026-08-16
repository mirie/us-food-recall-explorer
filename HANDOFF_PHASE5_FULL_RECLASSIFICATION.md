# Handoff — Phase 5, full-dataset LLM reclassification (context clear point)

Written at a deliberate context-clear point after a planning-only session. No
code changed this session; the deliverable is a plan file plus updated logs.
Read this file first, then the plan it points to.

## What happened, in one paragraph

The manual Claude.ai classification pass from the previous session (BUILD_LOG
Entries 10–10.5) covered only **3,554 rows (12.2%)** of the 29,161-row dataset,
not the full thing — `export_for_classification()` filters to
`category == "Uncategorized"`, and the classifying session had no way to know
rows were missing. Mai's actual intent was a full reclassification. This was
caught before any merge ran, so nothing needs undoing. Mai then recovered a
full taxonomy decision log from that same classifying session — label set,
governing principle, per-category rules, 10 boundary rules, and a self-flagged
gap list — which became the spec for a new plan.

**Read `BUILD_LOG.md` Entry 11 and `PROMPT_LOG.md`'s matching session** for the
full discovery narrative and every correction along the way. `LEARNINGS.md` has
the transferable lesson (an LLM given a filtered slice cannot tell it was
filtered).

## The plan — start here

**`.claude/plans/read-handoff-phase5-llm-merge-md-first-t-purrfect-lynx.md`**

This is the actual next-session starting point. It is a complete, reviewed
(ten rounds of user correction, all resolved), and deliberately trimmed plan —
read it in full before doing anything. Do not re-derive it from this handoff;
this handoff is a pointer, not a substitute.

Summary of what it specifies:

1. **Finalize the taxonomy** — check the recovered decision log into the repo
   as `CLASSIFICATION_RULES.md`, resolve its four self-flagged open questions
   (the biggest: add a separate `Eggs` label), close ~640 rows of coverage
   holes the log never addressed (alcohol, coffee creamer, broth, baby food),
   via one Opus 5 API call against a ~5,000-row sample that includes **all**
   466 rows from the five categories the log had zero evidence for.
2. **Build `classify_all.py`** — `submit`/`fetch` split for cross-session
   resumability, Message Batches API, structured outputs (category as an enum,
   plus a `confidence` field), `effort: "high"` (Opus 5's default).
3. **Run**: pilot 200 rows first (effort sweep + known-answer probes + real
   cost extrapolation, Mai approves before the full run), then all 29,161.
4. **Validate** via six checks designed to make uncertainty locatable rather
   than spot-checked: self-consistency, agreement with the 3,554 already-
   reviewed labels, confidence triage, category-coherence sampling,
   keyword-vs-LLM disagreement per category, residual inspection.
5. **Build `build_classified_dataset.py`** and refactor `pipeline.py` to read
   `llm_category` directly — `assign_category` leaves the runtime path
   entirely (not kept as a fallback). `categories.py` and its 31 tests stay in
   the repo, frozen, as provenance for the submission doc.
6. **Fix four expected test changes**, update the About section, run the QA
   pass from `HANDOFF_PHASE5.md`.
7. **Commit at 8 checkpoints** (table in the plan's Step 7), each pairing code
   with its `BUILD_LOG.md`/doc update.

## Prerequisites — verified ready

- **API credentials**: `ant` CLI installed, logged in as `mai.irie@gmail.com`
  (Mai's Individual Org), `user:inference` scope confirmed via
  `ant auth status`. `ANTHROPIC_API_KEY` is unset — **keep it that way**, a set
  key silently outranks the OAuth profile. Re-verify with `ant auth status`
  at the start of the next session; if it's expired, `ant auth login` again.
- **Not yet installed**: the `anthropic` SDK is not in `.venv`. First real step
  of Step 2 is `.venv/bin/pip install anthropic` + add to `requirements.txt`.
- **Billing**: API usage is pay-as-you-go against this org, separate from any
  subscription. Actual cost is unknown until the pilot measures it — the
  ~$9 figure floating around earlier excluded thinking tokens and is a floor,
  not a number to plan against.

## Quick reference

- `.venv/bin/pytest` — **134 passing**, confirmed clean at this session's
  start. Confirm again before touching anything.
- The decision log Mai recovered is reproduced in full inside the plan file
  (Step 1) — no need to go back to the other Claude.ai session for it.
- Data files: `data/food_recalls.csv` (raw snapshot, must end this phase
  byte-identical to its current state), `data/recall_categories_llm_classified.csv`
  (the 3,554-row manual pass — becomes a validation set, not the merge source).

## Important: unrelated uncommitted work exists in this repo

`git status` currently shows substantial modified/untracked files that
**predate this session** and were not touched here: `app.py`,
`recall_explorer/{charts,pipeline,reasons,transforms,filters,insights,llm_categories}.py`,
several `tests/test_*.py` files, `data/recall_categories_llm_classified.csv`,
and `HANDOFF_PHASE3_SLICE1.md` / `HANDOFF_PHASE3_SLICE2.md` / `HANDOFF_PHASE4.md`
/ `HANDOFF_PHASE5.md` / `HANDOFF_PHASE5_LLM_MERGE.md`. This is completed work
from Phase 3/4/5 sessions that was never committed. It was deliberately left
alone this session — only `BUILD_LOG.md`, `PROMPT_LOG.md`, and `LEARNINGS.md`
were committed here, since those were this session's actual output. Worth a
conscious decision (not just an accumulation) about whether to commit that
backlog before or alongside the reclassification work.

## Starting prompt for the next session

```
Read HANDOFF_PHASE5_FULL_RECLASSIFICATION.md, then the plan it points to at
.claude/plans/read-handoff-phase5-llm-merge-md-first-t-purrfect-lynx.md.

Run .venv/bin/pytest first -- confirm 134 passing. Then check
`ant auth status` to confirm the OAuth profile is still live (re-run
`ant auth login` if not).

Start at Step 1 of the plan: check the recovered decision log into the repo
as CLASSIFICATION_RULES.md, then run the taxonomy-finalization API call
against the ~5,000-row design sample. Show me the proposed label set and the
four open-question resolutions before writing anything else -- I need to
approve the enum before Step 2's classification script can be built against
it.
```
