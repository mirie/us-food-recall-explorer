# Handoff — Phase 5, LLM category-labelling merge (context clear point)

Written at a deliberate context-clear point: Mai is about to paste (or has
already dropped in) the classification results from the separate Claude.ai
chat, and wants a clean context for the merge step. Read this file first,
then `HANDOFF_PHASE5.md` for the rest of Phase 5's original scope (QA,
edge cases — the submission doc draft is explicitly **out of scope**, it should be part of the final phase after QA is complete, see below).

## What's already done this session

- `.venv/bin/pytest` was green at 134 passing (118 original + 16 new) as of
  the last check.
- **`recall_explorer/llm_categories.py`** (new, pure, no network calls):
  - `CATEGORY_ENUM` — the 16 categories from `categories.py`'s own rules
    plus `Uncategorized`, built from the module's own names so it can't
    drift out of sync. This will likely need to be updated given the separate, llm classification process udpated the categories abd made some changes.
  - `export_for_classification(df)` — filters to rows `assign_category`
    left `Uncategorized`.
  - `build_classification_prompt()` — the paste-in prompt sent to Mai,
    stating the fixed enum and exact expected output shape
    (`recall_number,category`, one line per row, no commentary).
  - `parse_classification_result(raw_text, expected_recall_numbers)` —
    parses pasted-back CSV text, validates every category against
    `CATEGORY_ENUM`, and returns `(mapping, problems)`. Invalid categories
    are **dropped**, not coerced; missing/unexpected recall_numbers are
    flagged as problems too.
- **`recall_explorer/pipeline.py`** — new `apply_llm_category_override(df)`,
  a pure function that prefers an optional `llm_category` column over the
  keyword-derived `category` wherever it's set and non-blank; wired into
  `load_recalls()` right after the keyword pass. No-op today since that
  column doesn't exist yet in `data/food_recalls.csv`.
- Both are TDD'd: `tests/test_llm_categories.py` (13 tests) and three new
  tests in `tests/test_pipeline.py`.
- Exported `data/food_recalls.csv`'s 3,554 `Uncategorized` rows to
  `scratch/uncategorized_for_classification.csv`, and the prompt to
  `scratch/classification_prompt.txt`. Delivery took three attempts before
  one worked on Mai's mobile client — see `BUILD_LOG.md` Entry 10.5 for the
  full saga (`SendUserFile` twice, an Artifact download button, then an
  Artifact with copy-to-clipboard buttons, which is what finally worked).
- `BUILD_LOG.md` (Entries 10, 10.5) and `PROMPT_LOG.md` are up to date
  through the export/delivery step.

## What's NOT done yet — start here

**The merge itself has not run.** A file named
`recall_categories_llm_classified.csv` (3,554 data rows + header) already
exists at the repo root, untracked — a quick scan of it shows
category values that are **not** in `CATEGORY_ENUM` as currently defined,
e.g. `Beef/Pork/Poultry/Game Meats` and `Food Additives/Ingredients` appear
in it, but the enum has separate `Beef`, `Pork`, `Poultry/Eggs` and no
"Food Additives/Ingredients" category at all. This is a different/earlier classification attempt with a different taxonomy than what `build_classification_prompt()` specified and the , `build_classification_prompt()` is out of date/previous fixed enum is outdated. The other Claude.ai chat appropriately evolved the classification categories. That said, please review for differences and confirm changes with Mai, one by one.

**First step of the next session: confirm with Mai which file/text is the
actual result to merge**, and if it uses a different category taxonomy than
`CATEGORY_ENUM`, decide the approach to reconcile `CATEGORY_ENUM`
to match what the LLM pass actually produced. Don't silently coerce mismatched categories — that's exactly what `parse_classification_result` is built to catch and surface, not paper over.

## Once the correct result is confirmed, the merge steps are

1. Run `parse_classification_result(raw_text, expected_recall_numbers)`
   where `expected_recall_numbers` is the set of `recall_number` from
   `export_for_classification(load_recalls())` (re-derive fresh, don't
   reuse a stale set).
2. Review `problems` with Mai before merging if there are more than a
   handful — decide together whether to proceed with the valid subset or
   address the gaps first.
3. Merge the validated mapping into `data/food_recalls.csv` as a new
   optional column, `llm_category`, populated only for the rows that got a
   valid classification; leave it blank elsewhere. (`recall_explorer/schema.py`'s
   `EXPECTED_COLUMNS` check is additive/allow-list only, so this doesn't
   need a schema change.)
4. Update `data/fetch_metadata.json` with a record of the pass: timestamp,
   rows reclassified, `Uncategorized` share before/after, and a note that
   the source was a manual Claude.ai chat round trip, not an API call.
5. `.venv/bin/pytest` — should stay green; `apply_llm_category_override`
   will now actually do something instead of being a no-op.
6. Sanity-check the category shift: before/after `Uncategorized` share, and
   a quick look at where the previously-`Uncategorized` rows landed
   (`df["category"].value_counts()`).
7. **This is also the point to check whether `test_uncategorized_share_stays_within_documented_bounds`
   and `test_uncategorized_is_no_longer_the_largest_category` in
   `tests/test_pipeline.py` still pass** — if the `Uncategorized` share
   drops meaningfully (the whole point of this exercise), the documented
   ~12% bound and the About-section text in `app.py` that cites it will
   need updating too. Treat that as an expected, planned change, not a
   test failure to work around.

## After the merge: resume the approved Phase 5 plan

The plan at
`/Users/mirie/.claude/plans/read-handoff-phase5-md-then-us-food-reca-cosmic-blanket.md`
is still the source of truth for what comes after the merge — re-read it.
Short version:

- **Live QA pass** against the now-refined category distribution: filter
  matrix (Year × Category × Reason × Severity), lens sync, full
  2012–2026 range with the partial-2026 dashed segment, the error-UI path,
  cold-start load time.
- **Edge cases**: year range narrowed to 2012 alone; a second zero-result
  filter combination distinct from Dairy+Botulism+Class III; clearing all
  filters back to full; `Uncategorized`/`Other` selected explicitly.
- Any real gap found gets a failing test first, then a small patch (TDD,
  per this project's established pattern).
- Log a `BUILD_LOG.md` entry for the merge (before/after coverage numbers)
  and one for the QA pass, per the plan's "process logging" section.
- **The submission doc draft (`SUBMISSION_DRAFT.md`) is explicitly out of
  scope for this plan** — Mai asked for it to be tracked as a separate
  follow-up, not bundled in here.

## Quick reference

- `.venv/bin/pytest` — run first in the next session, confirm 134 passing
  before touching anything.
- Export/prompt artifacts: `scratch/uncategorized_for_classification.csv`,
  `scratch/classification_prompt.txt`, `scratch/uncategorized_export_artifact.html`.
- Unconfirmed classification-result file: `recall_categories_llm_classified.csv`
  (in `data` root, untracked) — confirm before using.
- The approved plan file (see path above) has the full original design
  rationale and verification checklist.
