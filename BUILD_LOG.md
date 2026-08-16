# Build Log — US Food Recall Explorer

Course: Maven, "Mastering Agentic AI" — Homework 1
Format per entry: Goal → What I built → What worked → What broke → What I changed → Open questions → Time spent

---

## Entry 0 — Planning & Design Phase (pre-build)

**Goal**
Land on a dataset, a project concept, a technical spec, and a design direction before writing any code — so Phase 0 starts from a validated plan rather than an assumption-laden one.

**What I explored**

*Dataset brainstorm.* Started broad: sales/startup/financial dashboards (ruled out — too close to my day job), personal fitness data export (ruled out — too personal to make public), team velocity/burnout data (ruled out — confidentiality + no reliable source), climate change datasets (emissions, vulnerability, policy — ruled out, wanted something less heavy and less "serious data science"), and an arXiv agentic-AI paper trend explorer (ruled out — too hard to know the right search keywords for a field I'm still learning, and closer prior art exists — e.g. Emergent Mind).

Pivoted toward "myth vs. reality" as a framing — tested a few candidates:
- NYC-to-suburbs migration (good data via IRS SOI, but real story is more "high earners to Florida" than "everyone to the suburbs")
- Home cooks using less salt/sugar than restaurants (weakest data trail — no clean single source)
- Colds more frequent in winter (strong data via CDC ILINet + NREVSS — flu peaks winter, but rhinovirus/common cold peaks spring–fall, a genuine myth-busting finding)
- Rent vs. buy in NYC (buildable, but edges into financial-advice territory — set aside)

Landed on **colds vs. winter**, then pivoted again after a real-world news hook: recent lettuce/jalapeño recalls. Final concept: **US Food Recall Explorer**, exploring seasonality, top recalled foods, and volume/severity trends using openFDA data (2004–present).

*Dataset survey (secondary research).* Also researched NYC Open Data, FiveThirtyEight's GitHub data repo, The Pudding, BuzzFeed News, and The Guardian as general sources of clean, whimsical, journalist-published datasets — useful context, not used for the final pick, but confirmed FiveThirtyEight and The Pudding are strong go-to sources for future projects.

**Decisions made**

1. **Data source**: openFDA Food Enforcement API. Covers 2004–present, weekly updates, includes recall date, product description, reason for recall, and severity classification (Class I/II/III).
2. **Three core questions**, deliberately hedged against unverified assumptions:
   - Seasonality — pattern by month/quarter, without assuming a cause (growing season vs. imports vs. something else) unless country-of-origin data actually supports it
   - Top recalled foods/categories, year over year
   - Trend shape over time (increasing / cyclical / flat / rise-fall-rise) — explicitly not assumed to be one direction going in, and flagged with a standing caveat: better detection/reporting over 20 years could itself explain a rise in recall counts, independent of actual food safety
3. **Event-level vs. product-level counting**: recalls can be counted per incident (event) or per individual recalled item (product) — these give different pictures. Decided to keep both available rather than picking one.
4. **Data pipeline**: one-time fetch script (`fetch_data.py`) pulls from openFDA once and saves a static CSV. The running Streamlit app only ever reads that local CSV — no live API calls at runtime.
5. **Stack**: Streamlit + CSV (per course requirement). Explicitly evaluated alternatives (Dash, Panel, Shiny for Python, Gradio) — stuck with Streamlit since its whole value proposition (minimal boilerplate, fast iteration) matches the assignment's actual ask; switching would trade away exactly what the homework wants demonstrated.
6. **Documentation requirements** (separate from the product spec): this `BUILD_LOG.md`, updated after each meaningful step including actual prompts used (not just descriptions of them) — plus a final Google Doc deliverable, synthesized from this log at the end, covering project overview, datasets, prompts, iterations, and learnings.

**What worked**
- Using ChatPRD to formalize the concept into a proper PRD surfaced structure the chat conversation alone hadn't — but also introduced drift (see below), which was only caught by re-reading the PRD against the original discussion line by line.
- Wireframing in Claude Design (10 low-fidelity concepts, labeled 1a–1d / 2a–2d / 3a–3b) surfaced two ideas independently worth combining. A parallel exploration in ChatGPT (four higher-level directions: Classic Dashboard, Insight-Led, Question-Based Explorer, Flexible Analyst Workspace) converged on the same two insights from a different angle, which was a good cross-check.

**What broke / drift caught**
- The ChatPRD-generated PRD quietly demoted the event/product distinction from an interactive v1 feature to a deferred "nice-to-have," and softened the one-time CSV fetch into ambiguous "per session" language that could be misread as a live API call on every load. Both caught on review and corrected directly in the PRD file.
- ChatPRD's category/reason filter lists (produce, meat/poultry, dairy, etc.; Salmonella, Listeria, etc.) were written as if confirmed fields, when openFDA's underlying data is likely free text. Flagged explicitly in the PRD as unverified assumptions that Phase 0 must confirm or refute before Phase 1 treats them as real.

**What I changed**
- PRD: corrected the two drift points above, added explicit `⚠️ UNVERIFIED` flags on the category/reason filters, and added Phase 0 deliverables requiring those assumptions to be checked against real pulled data before anything downstream depends on them.
- Design direction, decided after reviewing all 10 wireframe concepts side by side:
  1. **Event vs. product is a permanent side-by-side lens** (concept 2c), not a toggle — both aggregation views shown at once, always labeled, rather than a switch the user has to remember the state of.
  2. **Dynamic, rule-based takeaway sentences** per chart panel (concept 2a, echoed independently by ChatGPT as "dynamic observations") — short, computed-from-data one-liners (e.g., "July has the most recall events — about 3× the lowest month"), explicitly never LLM-generated and never causal ("food safety is getting worse" type language is disallowed by design, consistent with the PRD's existing non-goals).
- Updated the PRD throughout (Functional Requirements, User Experience steps, Success Metrics, Technical Needs, Milestones) to reflect the side-by-side lens model consistently, rather than leaving old toggle language in some sections and new lens language in others.

**Open questions carried into Phase 0**
- Does openFDA's product description field support any reliable food-category derivation, or will this need keyword-based matching (or be reworked entirely, as concept 2d suggested — search-first instead of clean dropdowns)?
- Is "reason for recall" a clean field or free text requiring parsing?
- Does the data include country of origin at all — needed for the seasonality question's growing-season vs. import-pattern angle?
- Event-level vs. product-level: confirm openFDA's raw data actually exposes both an event identifier and product-level rows cleanly enough to aggregate both ways.

**Time spent**
Not tracked in hours — this phase was conversational/iterative across multiple sessions (dataset brainstorming, PRD drafting and correction, wireframe review, design direction decision). Future entries will track time per build session going forward.

---

## Entry 0.5 — Design Revision (pre-build)

**Goal**
Course-correct the design direction after reviewing an actual rendered sketch against what I actually wanted, before any code gets written against the wrong spec.

**What I built**
A low-fi wireframe sketch (via Claude in this chat) combining permanent side-by-side event/product lens panels with a rule-based takeaway sentence under each panel.

**What worked**
The side-by-side lens layout itself held up under scrutiny and was reconfirmed later in this entry.

**What broke**
Two problems surfaced on review:
1. The per-panel takeaway sentence pattern wasn't actually what I wanted — a separately-explored ChatGPT mockup ("Story First / Insight-Led," saved as a screenshot in this project) captured the experience better: a top-of-page row of four computed "Key Insights" cards, rather than a sentence tucked under each chart.
2. The sketch defaulted every chart type to vertical bars (including seasonality, which should be a heatmap/dot-matrix, not bars). This wasn't a deliberate design decision, just an artifact of the sketch — caught on review.

**What I changed**
- Re-confirmed the side-by-side lens decision (still in, explicitly re-checked against the ChatGPT mockup's single-toggle approach — decided to keep side-by-side, not adopt the toggle).
- Replaced per-panel takeaway sentences with a top-of-page **Key Insights row**: 4 computed stat cards, event-level framed by default, rule-based only (never LLM-generated, never causal language) — same guardrail as before, different placement.
- Replaced scattered per-chart footnotes with a single collapsible **"About the data & limitations"** section.
- Made chart type explicit and varied per view instead of defaulting to bars: seasonality = heatmap/dot-matrix, trend-over-time = line chart, top recalled foods = horizontal bar chart. This mapping applies to both lens panels on every chart.
- Adopted the ChatGPT mockup as the **visual style reference** (insight card treatment, filter row layout, chart-type choices) without adopting its single-toggle structure — the two mockups (Claude Design's 2c and ChatGPT's Story First) ended up contributing different pieces to the final direction rather than one replacing the other outright.
- Updated the PRD's Design Direction section (now 4 points instead of 2) and fixed every downstream reference to the old toggle/per-panel-sentence language across Functional Requirements, User Experience steps, Success Metrics, Technical Needs, and Milestones.
- Regenerated the wireframe sketch with corrected chart types (heatmap cells with opacity-based intensity for seasonality, proper horizontal bars for top foods) to confirm the fix visually before locking it in.

**Open questions**
- Line chart treatment for trend-over-time wasn't sketched yet (only described in the PRD) — worth a quick visual check before Phase 2 build, to make sure it doesn't run into the same "defaulted to the wrong chart type" issue.

**Time spent**
Not tracked — folded into the same planning session as Entry 0.

---

## Entry 0.6 — Final Design Confirmation & Documentation Cleanup (pre-build)

**Goal**
Close out the planning phase: get the reconciled design direction actually rendered as a finished artifact, trim the PRD to stop duplicating what that artifact now shows, and organize all planning-phase documentation before the Claude Code build starts.

**What I built**
- Received the finalized 2-page wireframe PDF (`Design_US_Food_Recall_Explorer.pdf`) from Claude Design, rendering the fully reconciled direction: Key Insights row, filter row, side-by-side event/product lens panels across all three chart types with correct chart types per view (heatmap for seasonality, line chart for trend, horizontal bar for top foods), and one collapsible "About the data" section.
- Trimmed the PRD's "Design Direction" section from ~4 dense paragraphs of visual description down to rationale-only bullets, with the PDF established as the visual source of truth. Removed redundancy where prose was trying to recreate an image in words.
- Compiled `PROMPT_LOG_Planning_Phase.md` — curated, pivotal prompts (not full transcripts) from all four tools used during planning: this chat, ChatPRD, Claude Design, and ChatGPT.
- Split reflective analysis out of the prompt log into a dedicated `LEARNINGS.md`, so the prompt log stays a clean running record and all "what this reveals" analysis lives in one place.

**What worked**
- The finalized PDF resolved the open question carried over from Entry 0.5 (line chart treatment for trend-over-time wasn't sketched yet) — confirmed as a proper line chart on page 2, both lenses, no "defaulted to bars" issue.
- Separating "what happened" (this log), "what was said" (prompt log), and "what it means" (learnings) into three distinct files made the eventual Google Doc synthesis straightforward rather than requiring re-deriving structure from a wall of transcript.

**What broke**
- A brief false alarm: thought a rendering artifact (unexpected pink coloring) had appeared in the PDF on a second look. Re-examined the same file — no pink present. Likely a viewer-side rendering quirk (e.g., a font/asset load issue in a different PDF viewer) rather than anything wrong with the file itself. Logged as a reminder to isolate whether a visual discrepancy is in the artifact or in how it's being viewed before assuming the artifact is broken.

**What I changed**
- PRD: Design Direction section rewritten to reference the PDF directly rather than describing it — see PRD for current wording.
- Documentation structure finalized: `BUILD_LOG.md` (process/chronology), `PROMPT_LOG_Planning_Phase.md` (verbatim pivotal prompts), `LEARNINGS.md` (analysis and reflection, including two tool-authored reflections kept verbatim from Claude Design and ChatGPT).

**Open questions carried into Phase 0**
(Unchanged from Entry 0 — still the two unverified data assumptions: food category and contamination reason field structure in the raw openFDA data.)

**Time spent**
Not tracked — folded into the same planning session as Entries 0 and 0.5.

---

## Entry 0.7 — Kickoff Prompt Finalization (pre-build)

**Goal**
Get the actual Claude Code kickoff prompt right before sending it — this is the artifact that governs the whole build phase, so it deserved the same scrutiny as everything else built during planning.

**What broke**
Two framing errors in my own drafted kickoff prompt, caught on review:
1. Called the wireframe PDF the "source of truth for layout, spacing, and chart types" — overstating its authority. It's a low-fidelity directional reference, not a pixel-perfect spec, and was never built against real data. Building strictly to it risks locking in visual choices before the actual data shape is known.
2. Described `PROMPT_LOG.md` (then still named `PROMPT_LOG_Planning_Phase.md`) and `LEARNINGS.md` as "background only, not needed to build the app" — implying they were closed, planning-only artifacts. They should continue as living documents through the build phase, same as `BUILD_LOG.md`.

**What I changed**
- Reframed the PDF in the kickoff prompt: structural decisions (side-by-side lenses, chart-type-per-view, Key Insights row, collapsible About section) stay firm; exact visual treatment is explicitly open to iteration once real data is in the app.
- Reframed the documentation requirement: `PROMPT_LOG.md` and `LEARNINGS.md` both continue to be appended to throughout the build, not just synthesized at the end.
- Renamed `PROMPT_LOG_Planning_Phase.md` → `PROMPT_LOG.md`, since "Planning_Phase" was no longer accurate once it spans the build too.

**Learnings**
The same drift-catching pattern that showed up repeatedly during planning (ChatPRD understating scope, a sketch defaulting to the wrong chart type) showed up one more time in the very prompt meant to prevent exactly that kind of drift during the build. Worth remembering going into Phase 0: the kickoff prompt is a draft like anything else, not a guarantee, and the same scrutiny applies to it as to any other AI-assisted output.

**Time spent**
Not tracked — folded into the same planning session as Entries 0, 0.5, and 0.6.

---

## Entry 1 — Phase 0: One-Time Data Fetch & Assumption Verification

**Goal**
Pull the openFDA Food Enforcement dataset once into a static CSV, and settle the two `⚠️ UNVERIFIED` assumptions the PRD flagged (food category derivable from product description; contamination reason as a clean field) before Phase 1 builds anything on top of them.

**What I built**
- Project scaffold: `git init`, `.gitignore`, `.venv` on Homebrew Python 3.14.7, `requirements.txt` pinned via `pip freeze`.
- `fetch_data.py` — standalone one-time fetch script with `--dry-run`, `--limit N`, and `--out` flags. Never imported by the app.
- `data/food_recalls.csv` — 29,161 rows, 19 columns.
- `data/fetch_metadata.json` — fetch timestamp, openFDA `last_updated`, per-year counts, column list. Backs the PRD's "data last updated: [date]" requirement without the app ever touching the API.

**What worked**
- Answering both unverified assumptions took a handful of read-only `curl` calls during planning, before a single line of the fetch script existed. Cheap, and it changed the plan materially.
- The dry-run → `--limit 1` → full-run sequence caught a real bug at the cheapest possible point (see below).
- The per-year count assertion (`expected` vs. actual rows, abort on mismatch) passed on all 15 years. The script is built to fail loudly rather than write a partial snapshot, and that guard is what makes the row count trustworthy rather than merely plausible.
- Both `⚠️ UNVERIFIED` flags resolved cleanly — refuted, but *specifically* refuted, with a measured failure rate rather than a vague "it's messy."

**What broke**

1. **The dataset does not start in 2004.** It effectively starts in **2012**. Zero records before 2012 on `report_date`; ~97 scattered stragglers on `recall_initiation_date` (37 in 2008, 3 in 2010, 57 in 2011). The PRD said "2004–present" in its TL;DR, the wireframe drew a `2004 —— 2026` x-axis, and the kickoff prompt repeated it. Nothing in the planning chain questioned it, because nothing in the planning chain had called the API.

2. **Both PRD assumptions refuted.**
   - `reason_for_recall` is free prose, not a code list. A naive regex tags 75.6% of rows; the misses are mostly allergen/labeling phrasings a refined rule set should catch (~90% expected).
   - `product_description` is free prose *and ambiguous*. Keyword matching leaves 13.5% matching no category and 41.5% matching two or more — "Blue Bell coconut fudge" is legitimately Dairy, Snacks, and Nuts at once. The PRD's clean five-category dropdown is not derivable as written.

3. **openFDA caps `skip` at 25,000, but the dataset holds 29,278 records.** A naive `while skip < total` offset loop silently drops several thousand rows and only errors on the request *past* the cap — after the damage. Caught by probing the cap directly rather than by hitting it mid-fetch.

4. **`--limit 1` fetched 1,000 rows.** The page-size cap was checked at the top of the loop but not applied to the request itself, so the first page always came back full-sized. Functionally harmless, but it defeats the entire purpose of a smoke test. Caught during the `--limit 1` step — exactly where it should have been.

5. **A correction to my own Phase 0 finding.** I initially reported ~1.4 products per event and flagged the wireframe's 3.8x ratio as unrealistic. That was wrong. The real full-dataset figure is **3.74** (29,161 rows / 7,791 events). My estimate came from a 1,000-row contiguous API slice, which splits multi-product events across page boundaries and systematically undercounts. **The wireframe was right and my correction to it was the error.** Worth recording precisely because it inverts the pattern the rest of this log documents: the sample-based check was less trustworthy than the design assumption it was "correcting."

**What I changed**
- Fetch strategy: **window by year** over `recall_initiation_date` and paginate within each year, rather than paginating by global offset. Every year is far below the 25,000 cap. 37 requests total.
- Applied `min(PAGE_SIZE, cap - len(rows))` to the request itself so `--limit N` fetches exactly N.
- Four decisions taken on the Phase 0 findings:
  1. **Range is 2012–2026, stated plainly.** The About section will explain this is an openFDA availability boundary, not evidence that no recalls happened before 2012. The ~117 out-of-window rows (pre-2012 stragglers plus malformed dates) are dropped.
  2. **`recall_initiation_date` is canonical** for seasonality and trend — semantically "when the recall began," versus `report_date`'s administrative publication lag, which would smear seasonal peaks by weeks.
  3. **Food category = priority-ordered keyword rules + a visible `Uncategorized` bucket.** Fixed precedence resolves the 41.5% multi-match cases deterministically; the 13.5% unmatched stay visible in the chart rather than being quietly dropped.
  4. **Dietary supplements included as their own category.** openFDA classifies them as `Food`, and the corpus contains CoQ10, pre-workout powder, kratom, and infant formula. Breaking them out keeps their share visible instead of folding them into a food category where they'd be misleading.
- `fetch_data.py` writes **raw API fields only**. Category and reason derivation are Phase 1 transformations, so those rules can be revised without re-hitting the API.
- PRD corrected: 2004 → 2012 throughout, both `⚠️ UNVERIFIED` blocks replaced with resolved findings, country-of-origin moved from "deferred" to "impossible," row estimate 10,000 → 29,161.

**Verification**

```
rows: 29161          unique event_id: 7791       products per event: 3.74
date range: 2012-01-03 -> 2026-07-08
unparseable dates: 0                             rows before 2012: 0
classification: Class II 14,616 | Class I 12,804 | Class III 1,741
product_type: Food 29,161 (only value)
empty reason_for_recall: 0    empty product_description: 0
```

Two rows carry a blank `recall_number` (both mid-2026, presumably not yet assigned). They retain `event_id`, dates, classification, and description, so both lenses still count them correctly — product-level counting uses row count, not `recall_number` uniqueness. Noted, not treated as a defect.

**Open questions carried into Phase 1**
- What precedence order for the category rules? "Ice cream sandwich" should probably resolve Dairy over Bakery, but that's a judgment call worth reviewing against real output, not deciding in the abstract.
- Should contamination reason be multi-label (a recall can be both undeclared-allergen and foreign-material) or single-label by precedence? Multi-label matches how an analyst thinks, but complicates any "share of total" arithmetic in the Key Insights cards.
- 2026 is partial (data through 2026-08-05). The final point on every trend line will dip artificially. Needs explicit visual treatment — probably a dashed segment or an annotation — not just a footnote.
- Country of origin is confirmed **absent**, not merely messy. `country`/`state`/`city` are the recalling firm's address (98.9% US). The growing-season vs. imports angle from Entry 0 is dead and should stop being carried forward as an open question.

**Time spent**
~1 session. API probing and the four decisions took the bulk of it; the script itself was quick once the pagination constraint was known.

---


## Entry 2 — Phase 1: Data Preparation (test-driven)

**Goal**
Turn the raw snapshot into an analysis-ready DataFrame — food category, contamination reason, clean dates, and the two aggregation lenses — with a test suite underneath it, after adopting a formal testing strategy mid-build.

**What I built**
- A three-tier test suite, per the strategy set out this session: strict TDD unit tests on pure logic with hand-built fixtures; one end-to-end pipeline test against the real CSV; one schema guardrail.
- `recall_explorer/categories.py` — priority-ordered keyword rules, first match wins.
- `recall_explorer/reasons.py` — multi-label contamination tagging.
- `recall_explorer/transforms.py` — date parsing plus `count_by(df, dimension, lens)`, the event/product lenses.
- `recall_explorer/schema.py` — expected columns, row floor, non-null requirements.
- `recall_explorer/pipeline.py` — the only module that touches the filesystem.
- 44 tests passing.

**What worked**
- Deciding the design questions *before* writing tests. Under TDD the test is the spec, so a guessed precedence order would have been silently frozen into assertions. Both category precedence and multi-label-vs-single were settled first, then encoded.
- Keeping every unit test on hand-built fixtures made the suite run in ~0.02s, so it could be run after every single change without friction.
- Asserting ranges rather than exact values for keyword-derived shares. Tightening a rule moves `Uncategorized` by a fraction of a percent; that should not break the build, while a jump from 18% to 40% should.
- Writing a test that asserts the two lenses **disagree**. That is the app's entire premise, and it is the kind of thing that could regress into "both call `.size()`" without anyone noticing.

**What broke**

1. **A date that parses successfully but is absurd.** openFDA's `"02121207"` parses cleanly as **7 December, year 212** — so `errors="coerce"` never fires. Under pandas 2.x this was caught for free, because `datetime64[ns]` cannot represent years before 1677 and coerced it to `NaT`. Under pandas 3.0's `datetime64[us]` it survives as a real Timestamp and would have dragged the trend chart's x-axis back eighteen centuries. The plausibility window is now explicit rather than inherited from a dtype limit. Directly caught by the test written before the code.

2. **Meat categories were ranked on a false premise — mine.** I placed Beef/Pork/Poultry in the top tier reasoning that those words name products rather than ingredients. They do not, *in this dataset*, because **FDA does not regulate meat, poultry, or processed egg products — USDA FSIS does**, in an entirely separate system. Nearly every meat keyword here is a flavouring or ingredient inside an FDA-regulated processed food: `Natural Beef Flavor`, `Bacon Brittle`, `Cheddar Bacon Skins`, `Chicken Flavor Seasoning`, and a `Pineapple Pie` matching on egg in its ingredient list. One row reads `MME Chicken Parmesan No Meat` and was classified Poultry/Eggs. This is the *same* ingredient-vs-product-type error I had already diagnosed for Dairy and explicitly designed the ladder to prevent — reproduced one tier up, in the same commit.

3. **Two regex bugs, both surfaced by a single failing test.** `Bakery` matched `\bpie\b`, which does not match the plural "pies", so a pie row fell through a tier — landing in `Produce`, because the bare pattern `apple` also matches inside **"pineapple"**. Neither would have thrown; both would have quietly misfiled rows forever.

4. **A TDD discipline lapse, self-reported.** In the second GREEN step I wrote all thirteen category rules when the failing test required one. `CATEGORY_RULES` is closer to a data table than to logic, but the honest description is that I over-implemented. The subsequent category tests therefore lock behavior rather than drive it. They are still real tests — reordering the ladder fails them, which I verified by actually promoting Dairy and watching the assertion break — but they are not what red-green-refactor is supposed to produce.

**What I changed**
- Meat categories demoted from tier 1 to tier 3, below product form. Combined meat share drops from 2,079 rows (7.1%) to 459 (1.6%) — the truthful picture rather than three misleading bars.
- `\bpie\b` → `\bpies?\b`; bare `apple` → `\bapples?\b`. Both have named regression tests.
- Explicit date plausibility window (2000–2100) in `parse_recall_dates`.
- Decisions taken this phase:
  1. **Category = priority-ordered, specific beats generic.** *(Superseded in Entry 2.6 — the "ice cream sandwich → Bakery" example recorded here was never tested and was factually wrong; it resolved to Prepared/Frozen. It now resolves to Dairy.)*
  2. **Reasons are multi-label.** Empirically this matters less than expected — only 499 rows (1.7%) carry two or more tags, averaging 1.02. Still the right semantic choice, but the "percentages won't sum to 100%" caveat is far smaller in practice than in principle.
  3. **The wireframe's top-foods chart is not achievable.** It ranks Poultry #1, Beef #3, Pork #4. Building to real data and documenting the divergence, consistent with how the 2004-axis divergence was handled.

**Measured output (29,161 rows)**

```
Uncategorized 18.4%   Produce 15.4%   Bakery 14.3%   Dairy 9.2%
Snacks 8.8%   Seafood 8.1%   Prepared/Frozen 7.3%   Supplements 5.7%
Spices 4.9%   Beverages 4.0%   Nuts 2.5%   Poultry 0.9%   Pork 0.4%   Beef 0.3%

Reason tagging: 84.3% tagged, 15.7% untagged, 1.02 tags per tagged recall
Top reasons: Undeclared allergen 28.4% | Listeria 25.6% | Salmonella 12.4%
```

**Open questions carried into Phase 2**
- `Uncategorized` at 18.4% is the second-largest bar. Shown honestly as decided, but worth a look on screen — it may dominate the chart visually in a way that reads as a defect rather than as candour.
- The partial-2026 dip still needs a visual treatment decision (dashed segment vs. annotation vs. excluding the year from the trend line).
- Seasonality has not been built yet; the month distribution has not been examined at all.

**Time spent**
~1 session, interleaved with the testing-strategy adoption.

---

## Entry 2.5 — Category Coverage, Partial-Year Treatment & Phase 2 Handoff

**Goal**
Settle three open questions before starting Phase 2, rather than carrying them into UI work where they would be harder to change.

**What I built**
- Three new categories (Grains/Cereal, Plant Protein, Oils/Fats) and ~60 additional keywords, all TDD'd against real strings pulled from the Uncategorized bucket.
- 54 tests passing.

**What worked**
- **Inspecting the bucket instead of reasoning about it.** I had characterised the residual 18.4% as irreducible ambiguity and estimated that expanding rules would hit diminishing returns. Sampling 25 rows refuted that immediately: `Kippered Herring`, `Enoki Mushroom`, `Sunflower Kernels`, `Cardamom Pods`, `Soybean Oil`, `grits`, `Tofu`, `Frosted Mini Wheats`. It was a coverage gap, not ambiguity — three categories were missing outright. Measured before committing to an approach: 41% of the bucket was recoverable, which turned a guess into a decision.
- **A bound test failing on purpose.** Expanding the rules dropped Uncategorized from 18.4% to 11.9% and broke `test_uncategorized_share_stays_within_documented_bounds`. That is precisely the failure it exists to produce — it forced the documented figure to be updated alongside the code rather than silently going stale. Worth noting because it is the first test in this project to fail for a *good* reason.
- Produce (17.0%) now leads the top-foods chart instead of Uncategorized, so the headline chart opens on a real category rather than on an absence.

**What broke**
- **I overstated a wireframe divergence.** I recorded that the PDF's top-foods chart was "not achievable" because it ranks Poultry #1. On challenge, that was wrong: the chart's *structure* — horizontal bars, top categories, both lenses — works exactly as drawn. Only its placeholder labels differ from real data, which is what a low-fidelity mock is for. I had conflated "the mock's illustrative content differs" (expected, unremarkable) with "the design doesn't work" (false). Corrected in the PRD. The real finding was always the USDA jurisdiction boundary, which is a property of the data source and belongs under Non-Goals, not a design note.
- **I flagged the partial-2026 problem three times without ever asking a question about it.** It sat in "Open questions" across two entries and was raised repeatedly in conversation, but no decision was ever put forward. Raising an issue is not the same as surfacing a decision, and a list of open questions can create a false impression that they are being actively worked.

**What I changed**
- Uncategorized: **18.4% → 11.9%**. Residual is genuinely hard (SKU strings like `a89471 batter mix x1`, generic names like `california medley`).
- **Partial 2026 decided**: plot it as a **dashed final segment with an explicit "partial year — through Aug 2026" label**. Data through 2026-08-05 means 2026 holds ~7 months against every other year's 12, so it plots 692 against 2025's 1,571 — a phantom 56% drop. Annualising or projecting was ruled out as inventing data and edging into the predictive territory the Non-Goals forbid.
- **LLM classification logged as Phase 3**, not dropped. See `LEARNINGS.md`; the key distinction is that the PRD's "never LLM-generated" rule governs *claims about the data*, not *labelling of input rows* in a one-time offline pass whose output is frozen into the CSV and auditable.
- Decided **not** to derive further classifications. `classification` (Class I/II/III) is already clean and needs none. Distribution scope, repeat-offender status, and recall duration were all considered and rejected: none serve the three core questions, and each adds filter combinations that produce more empty states and more surface for silent misfiling.

**Final category distribution (29,161 rows, 17 categories)**

```
Produce 17.0%  Bakery 14.1%  Uncategorized 11.9%  Seafood 8.6%  Dairy 8.3%
Prepared/Frozen 8.0%  Snacks 7.7%  Spices 6.0%  Supplements 5.7%
Beverages 4.4%  Grains/Cereal 3.9%  Nuts/Seeds 2.7%
Poultry 0.7%  Pork 0.3%  Beef 0.2%  Plant Protein 0.2%  Oils/Fats 0.2%
```

**Open questions carried into Phase 2**
- Seasonality is entirely unexamined — the month distribution has not been looked at once. This is the only one of the three core questions where the answer is genuinely unknown going in.
- Whether 17 categories is too many for a readable horizontal bar chart, or whether the tail should collapse into "Other" for display only (keeping the underlying data intact).

**Time spent**
~1 session, mostly discussion rather than code.

---

## Entry 2.6 — Category Accuracy: Two More Failure Classes, and Freezing the Rules

**Goal**
Respond to a challenge on a documented classification example — and, on finding it was wrong, work out how much else was wrong.

**What broke**

1. **I documented a behaviour I never ran.** The claim "ice cream sandwich resolves to Bakery" was written into a module docstring, the PRD, `HANDOFF_PHASE2.md`, and two build-log entries. It was false — it resolved to `Prepared/Frozen`. I invented a plausible-sounding example to illustrate a real limitation and never executed it. Worse, it was recorded as an *accepted tradeoff*, which framed a fabrication as a considered decision.

2. **The underlying classification was also wrong, and systematically.** Challenged on whether an ice cream sandwich is really a bakery item, measuring showed **1,393 rows mentioning "ice cream" scattered across nine categories, only 35% in Dairy**. The cause is structural: the ladder ranks *single words*, which works when a product's identity is a single word (`cheesecake` was 95% Bakery) and fails when it is a phrase, because whichever incidental flavour word appears first wins. `strawberry yogurt` hit `berr` in Produce long before Dairy was reached; 605 `peanut butter` rows were dragged toward Dairy by the word "butter".

3. **Packaging vocabulary was being read as food vocabulary.** Found while verifying the fix above: **509 rows — a fifth of the entire Seafood category — were cheesecakes and salads sold in plastic CLAMSHELLS.** Plus 68 more from "plastic wrap" landing in Prepared/Frozen. This bug lived entirely inside "successfully categorised" rows, so no coverage metric would ever have surfaced it.

4. **I had been reporting coverage as though it answered accuracy.** "11.9% Uncategorized" was quoted repeatedly as the quality figure. It measures only how many rows got *a* label, not how many got the *right* one. The clamshell bug inflated Seafood by 25% without touching the coverage number at all.

**What I changed**
- Added `PRODUCT_IDENTITY` as tier 0 — multi-word product identities checked before the single-word ladder. Result: ice cream 9 categories → 1, yogurt 10 → 1, cream cheese 9 → 1, sour cream 8 → 1, peanut butter 9 → 2 (the remainder being "peanut butter ice cream", correctly Dairy).
- Added `_strip_packaging()` — removes packaging language before matching, rather than defending every food keyword with a lookaround. Keeps the fix in one place as more turn up. Seafood 2,448 → 1,959.
- Tests assert that real clams and real food wraps still classify correctly, so the narrowing does not disarm the keywords it narrows.
- Corrected the fabricated example everywhere it had propagated.
- **Froze the category rules.** Decision taken with Mai: stop patching reactively, document honestly, and revisit via the Phase 3 LLM pass.

**Why freeze rather than keep fixing**
Five distinct failure classes have now been found — ingredient-vs-product-type, meat-as-ingredient, regex substring bugs, phrase-identity shattering, and packaging vocabulary. Each fix was cheap. The problem is that **no process is producing these findings**: four of the five came from someone happening to look at the right rows, and two of those from Mai rather than from me. There is no reason to believe a sixth class does not exist, and no way to find it except more luck. Continuing to patch would consume unbounded time while producing a number that still could not be quoted with confidence.

The architecture makes freezing cheap: `pipeline.py` sets `df["category"]` in a single line, and no chart code will ever care whether that column came from regex or from a frozen LLM pass. The swap is a one-line change, so deferring costs essentially no rework.

**Final Phase 1 distribution (29,161 rows)**

```
Produce 15.9%  Bakery 13.1%  Dairy 12.6%  Uncategorized 12.2%
Prepared/Frozen 7.2%  Seafood 6.7%  Spices 6.1%  Snacks 6.0%
Supplements 5.5%  Nuts/Seeds 5.1%  Beverages 4.5%  Grains/Cereal 3.5%
Poultry 0.7%  Pork 0.3%  Beef 0.2%  Plant Protein 0.2%  Oils/Fats 0.2%
```

**Open questions carried into Phase 2**
- Unchanged from Entry 2.5, plus: **category accuracy remains unmeasured.** The About section must say so rather than implying the 12.2% Uncategorized figure is a quality metric.

**Time spent**
~1 session, entirely reactive to a single challenge on a single word.

---

## Entry 3 — Phase 2, Slice 1: App Shell + Seasonality Heatmap

**Goal**
Start Phase 2. Seasonality was flagged in the handoff as the only one of the three core questions with a genuinely unknown answer — start there, and let what the data actually shows decide the chart shape rather than assuming a shape and fitting the data to it.

**What I built**
- Looked at the month distribution before writing any chart code. Aggregated across the 14 complete years (2012–2025), the spread is modest (events 1.42x, Jan low to Oct high; products 1.96x, Jan low to May high) — but the peak month rotates almost every year: Oct, Oct, Dec, Jan, May, Jun, Mar, Sep, Feb, May, May, Mar, Nov, Oct. Only May and Oct repeat, four times each in fourteen years. A 12-cell month-of-year strip would have asserted a stable season the data doesn't support.
- `seasonality_matrix(df, lens, coverage_end=None)` in `transforms.py` — a long-form (year, month, count, covered) grid, TDD'd against hand-built fixtures (11 tests, all written and watched fail before implementation). `count_by()` couldn't be reused: it sorts by count and drops empty groups, both wrong for a calendar grid that needs every cell.
- `seasonality_heatmap()` in a new `charts.py` — month x year heatmap, months in calendar order, years descending, independent single-hue colour scale per lens panel (events and products differ by ~3.7x; a shared scale would wash the smaller one out). Smoke-tested against real `load_recalls()` output per the testing contract.
- `app.py` — the first page shell. Header, scope line, data-last-updated caption, Key Insights / Trend / Top-foods placeholders, a real About section with the six documented limitations, and the seasonality section live via `st.columns`.

**What worked**
- The `covered` flag on `seasonality_matrix()` earned its keep immediately. `coverage_end` is read from `fetch_metadata.json`'s `openfda_last_updated` (2026-08-05) rather than derived from `max(recall_date)` in the loaded frame — the last actual recall row is 2026-07-08, about four weeks earlier, which is openFDA's reporting lag, not missing coverage. Passing the metadata date means August 2026 renders as the real (currently low) count it is, not as an unobserved hole.
- No `chromium-cli` in this environment, so I drove a headless Chrome instance directly over the DevTools Protocol (installed `websocket-client` into the scratchpad, not the project) to get a real post-hydration screenshot rather than trusting a `--screenshot`-flag capture, which only fires on the pre-hydration skeleton. Confirmed: both panels render with correct axis order and independent legends, 2026's Sep–Dec cells are blank against the page background, the About expander opens, and the browser console throws nothing.

**What broke**
Nothing in code. The one wrong assumption was caught before it shipped: I initially treated 2026 running through July as a data gap needing a dashed-segment annotation, following the PRD/handoff's "partial year" framing too literally. Mai corrected this — with today's date being 2026-08-14, a year that only reaches July is just the calendar, not missing data, and doesn't warrant emphasis on this chart (the PRD's dashed-segment rule is specifically about the trend line chart, not touched in this slice).

**What I changed**
Dropped the partial-year caption I'd planned for the seasonality section, and reframed `coverage_end`'s purpose in the plan from "handle the partial year" to "tell real zeros apart from not-yet-observed months" — which is what it actually does, and matters again as soon as Phase 3 filtering can end a subset's data earlier than the full dataset.

**Open questions carried forward**
- Trend-over-time and top-recalled-foods charts are still placeholders — next slices.
- Key Insights row is still Phase 3, per the original phase plan.
- Whether the year-to-year rotation in the heatmap reads as rotation (rather than noise) at production cell size is a manual design-review question, not yet asked of a human viewer at full resolution.

**Time spent**
~1.5 hours reading `HANDOFF_PHASE2.md` and the PRD, examining the month distribution, and reaching the plan (brainstorming + plan mode) — then ~10 minutes once the plan was approved: TDD for the transform, the chart + smoke test, and the app shell. The gap is the point, not a curiosity — see `LEARNINGS.md`'s new entry on where session cost actually goes.

---

## Entry 3.5 — Handoff to Phase 2 Slice 2 (no code this entry)

**Goal**
Prepare for the next Phase 2 slice (trend-over-time, top recalled foods) with a proper handoff rather than jumping straight to Phase 3, and settle the two real design questions the handoff surfaced before they get frozen into code as guesses.

**What I built**
No code. `HANDOFF_PHASE2_SLICE2.md` — precomputed reference numbers (yearly event/product counts, severity by year, category rankings both lenses) so the next session doesn't re-derive them from the CSV.

**What worked**
- Caught prematurely jumping to Phase 3 before checking the PRD's own phase dependencies — trend-over-time and top-recalled-foods were still `st.info()` placeholders, and Phase 3 (filters) explicitly depends on all three charts existing.
- An abstract framing of "should the trend line split by severity or stay one total line" got "this is too abstract for me" from Mai. Rebuilding it as two ASCII previews from the real 2016-spike numbers resolved it in one turn — see `LEARNINGS.md` for the general lesson.
- Top-foods question (whether 17 categories needs a display-only "Other" bucket) resolved the same session, on different reasoning: Mai chose the simplest option deliberately, since the category set itself is expected to change once Phase 3's LLM labelling pass replaces the frozen regex ladder — not worth building a collapsing scheme for numbers that won't be the final numbers.

**What broke**
Found while writing the handoff, not by anyone flagging it: "partial year — through Aug 2026" had been written into the PRD (twice) and `HANDOFF_PHASE2.md` during planning, before real data existed to check it against. The actual last `recall_initiation_date` is 2026-07-08; 2026-08-05 is openFDA's metadata/publication timestamp, not the last recall date. Same shape as the Phase 0 2004-vs-2012 error — a plausible date, unchecked, propagating through multiple documents.

**What I changed**
Corrected the date in both PRD locations and `HANDOFF_PHASE2.md`; locked both design decisions (3-line severity split, no-"Other"-bucket) into `HANDOFF_PHASE2_SLICE2.md` so the next fresh session starts from decisions rather than open questions.

**Open questions carried into Slice 2**
None deliberately left open this time — both design questions specific to these two charts are settled. General open questions (Key Insights recompute-vs-debounce, filter interactions) remain Phase 3's, per `HANDOFF_PHASE2.md`.

**Time spent**
~20 minutes, entirely discussion and documentation.

---

## Entry 4 — Phase 2 Slice 2: trend-over-time & top recalled foods

**Goal**
Close out Phase 2 by building the two remaining core charts — trend-over-time (line, severity split, dashed partial-2026 segment) and top recalled foods (horizontal bar, all 17 categories) — per `HANDOFF_PHASE2_SLICE2.md` and the two design decisions locked there.

**What I built**
- `top_foods_bar()` in `charts.py` — no new transform needed, `count_by()` already returns the right shape. Each lens panel sorts by its own counts (`sort="-x"`), per Mai's call in this session's design question.
- `severity_trend()` in `transforms.py` — new pure transform, TDD'd first (11 tests against hand-built fixtures, following `seasonality_matrix()`'s rectangular-grid and `covered`-flag precedent): year x classification grid, zero-filled for missing combinations, a `partial` flag per year, and an unexpected-classification-value case so data drift surfaces instead of vanishing.
- `severity_trend_lines()` in `charts.py` — three severity lines per panel via a fixed-order categorical color scale, with the dashed partial-2026 segment done as two layers rather than one `strokeDash` encoding (Vega-Lite groups a line per encoding value, so a single partial-year point in its own group draws nothing). Partial-year caption goes in the chart subtitle, worded from `df["recall_date"].max()` (2026-07-08), not the metadata publication date — per this session's other design question.
- Wired both into `app.py`, replacing the two remaining `st.info()` placeholders; hoisted the `coverage_year, coverage_month` pair above the seasonality section since both charts now need it.
- Loaded the `dataviz` skill before touching color: three severity lines use the validated categorical palette's slots 1-3 (blue/orange/aqua, pass CVD checks in both light and dark per `references/palette.md`), bars use slot 1 alone since category isn't a color dimension.

**What worked**
The transform numbers matched every figure in `HANDOFF_PHASE2_SLICE2.md`'s precomputed reference table exactly on the first real-data run (2016 event-lens severity split 415/358/40, 2026 85/134/17, overall Class II 14,616 / Class I 12,804 / Class III 1,741, top three categories Produce/Uncategorized/Bakery) — the handoff's upfront numbers paid for themselves as a verification step, not just documentation.

**What broke**
Two real bugs, both caught by self-checking the actual rendering before handing it off, not by the test suite (matching the testing contract's own claim that visual correctness isn't test-asserted):
1. All 17 category bars rendered, but only every other y-axis label did — Vega-Lite's default label-overlap avoidance was silently dropping half of them at the chart's original fixed height, leaving unlabeled bars. Fixed with a height that scales with category count (`26px` per bar) plus `labelOverlap=False` on the axis.
2. The dashed 2025→2026 segment left a visible gap instead of connecting to the solid line — an earlier version of the two-layer split excluded the connecting year (2025) from the solid layer entirely rather than letting it belong to both layers (endpoint of the solid segment *and* start of the dashed one). Also bumped the partial-year subtitle's color/size — the default was nearly illegible against the dark chart surface.

**What I changed**
See the two fixes above. Also learned mid-session that Streamlit's `runOnSave` defaults to `False` — a code edit doesn't trigger a rerun of an already-running instance without it, so the first re-screenshot after the bar-chart fix silently showed stale output until the server was restarted with `--server.runOnSave true`.

**Open questions for Mai's manual review**
Left `streamlit run app.py` running (`--server.runOnSave true`, port 8501) rather than closing the loop solo, per this session's plan: whether three lines per half-width trend panel reads clearly at a glance, and whether 17 category bars is workable in the top-foods chart or feels like too many (the no-"Other"-bucket call is reversible if so).

**Time spent**
~40 minutes: reading the handoff/PRD and confirming the pytest baseline, two AskUserQuestion rounds for the bar-order and partial-label placement decisions, TDD for `severity_trend()`, both charts, wiring, and the self-check/fix cycle that caught the two rendering bugs above.

---

## Entry 5 — Phase 3 Slice 1: Filters & Reactivity

**Goal**
Build the four PRD filters (year range, category, reason, severity) and wire them into the three existing charts, per `HANDOFF_PHASE3_SLICE1.md`. Key Insights stays out of scope — deliberately deferred to Slice 2 in the handoff.

**What I built**
- `apply_filters()` in a new `recall_explorer/filters.py` — one pure function, TDD'd first against hand-built fixtures (13 new tests in `tests/test_filters.py`): year range (inclusive `between`), category and severity (`isin`), and reason as OR-across-selected-tags with `"Other"` as its own selectable option matching untagged rows (`reason_tags == []`). `None` and `[]` both mean "no filter" on a dimension, so Streamlit's multiselect default (`[]` when nothing's picked) reads directly as "show all" with no special-casing in `app.py`.
- `REASON_LABELS` added to `reasons.py`, derived from `REASON_RULES` rather than hand-copied, per the handoff's explicit instruction — it has to stay in sync if a rule is ever added.
- `app.py` wiring: a `st.columns(4)` filter row (year slider, three multiselects) below the Key Insights placeholder and above the chart sections, matching the PRD's own layout order. `filtered_df = apply_filters(...)` computed once and threaded into all three chart sections in place of `df` — no changes to `seasonality_matrix`, `severity_trend`, or `count_by` themselves, confirming the handoff's prediction that they wouldn't need any. `coverage_year`/`coverage_month` and `last_recall_date` (the partial-year caption) stayed anchored to the full `df`, not the filtered subset, per the handoff.
- Zero-state: one `if len(filtered_df) == 0` check wraps all three chart sections in an `else`, showing a single `st.info(...)` instead — the About expander stays outside the branch so it always renders.
- Reworded the top-foods caption and `top_foods_bar()`'s docstring, both of which hardcoded facts about the *unfiltered* dataset ("All 17 categories", the Uncategorized #2→#4 rank-shift example) that go false under most filter states — confirmed with Mai via AskUserQuestion before touching it, since it wasn't explicitly in the handoff's scope.
- `restrict_trend_to_severities(trend, severities)`, added to `filters.py` after Mai's manual QA caught a real bug (see below), TDD'd first (3 new tests). Applied to both `events_trend` and `products_trend` in `app.py`.

**What worked**
- Every test I wrote for the "harder" `apply_filters()` cases (reason OR-semantics, multi-tag rows, the Other toggle, combined-filter AND, zero-result) passed against the first-draft implementation without a second red-green cycle — the fixture design (five rows, each isolated by a different dimension) caught what it was meant to catch, so first-draft logic held up rather than the tests being too weak to notice a bug.
- No `chromium-cli` and no Node/npx in this environment (checked directly), so first verified by driving the exact sequence of calls `app.py` makes — `apply_filters` → `seasonality_matrix`/`severity_trend`/`count_by` → the three chart builders — across six scenarios (full data, year range excluding 2026, single-category, multi-reason OR, Other-only, and a deliberately impossible combination) directly in Python. Confirmed the partial-year dashed segment disappears exactly when 2026 is filtered out (`partial_year_present=False`) with no special-casing needed, matching the handoff's prediction.
- Mai asked whether the missing browser driver was fixable; `pip install playwright` resolved cleanly, so installed it plus `playwright install chromium` (~270MB into `.venv`, confirmed with Mai first) and drove the actual running app rather than only the underlying Python calls. Three real screenshots: default state (both seasonality panels populated, filter row present), Category=Dairy applied live (both heatmaps visibly re-rendered to a different, lower-magnitude pattern — proof of real reactivity, not a stale chart), and a deliberately impossible combination (Dairy + Botulism risk + Class III) showing the zero-state message with all three chart sections gone and the About expander still present below it. Zero console/page errors across all three. `playwright` is a verification-only dependency, not added to `requirements.txt` — the app itself never imports it.

**What broke**
`apply_filters()` and its wiring held up exactly as predicted — no code changes needed to `charts.py`, `partial` flag fell out correctly, no zero-layer edge case. But Mai's own manual QA against the live app (not from a screenshot I'd taken) caught a real bug my scripted checks missed: filtering the trend chart to Severity = Class I still showed Class II and Class III as flat lines pinned to zero instead of disappearing. Root cause was in `severity_trend()`, not in `apply_filters()` — `apply_filters` was already correctly narrowing `filtered_df` to Class I rows only. But `severity_trend()` always back-fills all three `SEVERITY_ORDER` classes as real zeros for every year, by design — `test_grid_is_rectangular_across_years_and_classifications` in `test_transforms.py` explicitly locks this in (it requires "Class III" to appear even in a fixture that never contains a single Class III row). That behavior is correct for the *unfiltered* view: a class with genuinely zero recalls in a year is a real zero worth showing, not a hole. But once the severity filter itself excludes a class, the class should vanish from the chart entirely — showing it as a flat zero line contradicts what the user just asked for.

**What I changed**
- The caption/docstring wording described above, confirmed with Mai first since the handoff didn't explicitly call it out as in-scope.
- Fixed the severity-trend bug downstream of the transform rather than changing `severity_trend()` itself, since the transform's always-rectangular contract is correct and tested for the unfiltered case — this is filter-driven display logic, not a grid-completeness concern. Also used the bug report as the moment to double check Mai's other two questions from the same message: does Severity affect Top recalled foods, and does Reason? Both already did — screenshotted the top-foods chart with Severity = Class I applied and the bars visibly shrank to Class-I-only counts, because that chart reads from the same shared `filtered_df` as everything else. Only the trend chart's severity-line rendering was broken; the filtering itself was correct everywhere. Re-verified by actually driving the interaction in the browser (not the earlier scripted Python-level check) — selected Severity = Class I via the real dropdown, screenshotted the trend chart (confirmed Class II/III lines gone, only Class I plots) and the top-foods chart (confirmed bars shrank). Zero console/page errors both times.

**Left running for Mai's live review**
`streamlit run app.py` on port 8501, per this session's instruction — didn't close the loop solo.

**Time spent**
~20 minutes: reading the handoff/PRD/app.py/transforms/charts, one AskUserQuestion round on the stale caption, TDD for `filters.py` (16 tests total across both rounds), wiring `app.py`, the scripted six-scenario runtime check, browser-driven verification via a newly installed Playwright, and diagnosing + fixing the severity-trend bug Mai found through manual QA.

---

## Entry 5.5 — Handoff to Phase 3 Slice 2 (no code this entry)

**Goal**
Phase 3 Slice 1 was done and confirmed working (104 tests, live browser QA including the severity-trend fix), so prepare the handoff for Key Insights — the last piece of Phase 3.

**What I built**
No code. `HANDOFF_PHASE3_SLICE2.md` — precomputed reference numbers (event counts by year, peak year, top reason share) so the next session doesn't re-derive them from the CSV, plus one real architectural note and one real design decision surfaced before either got frozen in as a guess.

**What worked**
- The architectural note (Key Insights needs `filtered_df`, but the PRD places it visually *above* the Filters section that produces `filtered_df`) came from actually tracing Streamlit's execution model rather than assuming it would "just work" — a widget call both renders and returns its value at that call site, so the fix is an `st.container()` created early and written into later, not a restructure of the filter-then-compute flow Slice 1 already built. Worth writing down now rather than letting the next session discover it mid-build.
- The four-card design question went to `AskUserQuestion` with two concrete previews built from real numbers (total events, % change, peak year, top reason vs. an alternative leaning on Class I severity share and top-category share) rather than left abstract — same lesson as every prior design question in this project. Settled: total events, % change from first to last full year *in the current view* (not a hardcoded baseline year, since that breaks under a year-range filter), peak year, and top reason tag's share of events. Rejected the severity/category-share alternative specifically because the trend and top-foods charts already show that same information in full underneath Key Insights — the reason-tag share doesn't duplicate anything else on the page.
- One additional design note added without a separate question, since it followed directly from an existing PRD rule rather than needing a decision: `st.metric()`'s default colorized delta arrow (green-up/red-down) implies a good/bad value judgment that doesn't belong on a recall-count trend, so the handoff locks `delta_color="off"` on the % change card as a direct extension of the "never evaluative" rule, not a new one.

**What broke**
Nothing — planning-only entry.

**Open questions carried into Slice 2**
None deliberately left open. The zero-state behavior for Key Insights reuses Slice 1's existing `if len(filtered_df) == 0` branch rather than needing its own design pass.

**Time spent**
~10 minutes: confirming Slice 1's final state, computing real reference numbers (event-level reason-tag shares, corrected from an earlier product-level figure), one AskUserQuestion round, and writing the handoff.

---

## Entry 6 — Phase 3 Slice 2: Key Insights

**Goal**
Replace the Key Insights placeholder with four live `st.metric()` cards, per `HANDOFF_PHASE3_SLICE2.md`. Last piece of Phase 3.

**What I built**
- `key_insights(df, coverage_end)` in a new `recall_explorer/insights.py` — one pure function returning a `KeyInsights` namedtuple (total events, % change from first to last full year in view, peak year, top reason tag's share of events), TDD'd first against hand-built fixtures in `tests/test_insights.py` (14 tests). Full-year exclusion reuses the same `year*12+12 <= coverage_end_key` arithmetic as `severity_trend()`'s `partial` flag, computed inline rather than refactoring `transforms.py`.
- Container-positioning fix in `app.py`: `key_insights_container = st.container()` created immediately before the Filters section, populated with the four `st.metric()` calls inside the existing `if len(filtered_df) == 0: / else:` branch further down — Streamlit renders a container where it's created, not where it's last written to, so Key Insights appears above Filters despite depending on `filtered_df`.
- All four cards pass `delta_color="off"` — mandated by the handoff for the % change card specifically, extended to the peak-year and top-reason cards too since none of these numbers has a good/bad direction.
- Zero-state reuses the existing branch: dash (`"—"`) placeholders instead of a second zero-state design.

**What worked**
- Every test passed on the first implementation attempt for total events, % change, and peak year — the plan's full-year-exclusion logic (borrowed directly from `severity_trend()`'s already-tested `partial` arithmetic) transferred cleanly.
- Verified the unfiltered `key_insights()` output against the handoff's hand-computed reference numbers before wiring anything into `app.py`: total events, first/last full year and their counts, % change, and peak year all matched exactly on the first attempt.

**What broke**
Top reason's share did not match the handoff's reference number on the first attempt — got 3,088 events / 39.6% instead of the locked 3,066 / 39.4%. Root cause: my first implementation counted an event as tagged if *any* of its product rows carried the tag (`explode` across every row, matching how `apply_filters()` treats reason filtering at the row level). But 43 events in the real data have product rows whose `reason_tags` genuinely differ from each other — the same recall's per-product text drifts slightly, and the tagger picks up different keywords row to row. The handoff's locked reference numbers turned out to assume a different rule: one canonical row per event (the first), not a union across all of an event's rows. Confirmed by testing both approaches against the real snapshot — "first row per event" reproduced 3,066/39.4% (and the runner-up Salmonella 912, Listeria 903, Other 1,636/21.0%) exactly; the any-row-tagged approach didn't.

**What I changed**
- Switched `key_insights()`'s top-reason logic to `df.drop_duplicates("event_id", keep="first")` before exploding tags, treating `reason_for_recall` as a genuinely event-level attribute (duplicated onto product rows, not independently meaningful per product) rather than row-level. This only affects Key Insights' top-reason ranking — `apply_filters()`'s row-level reason filtering is untouched and intentionally different, since a user filtering by reason should still see any product row that happens to mention it.
- Rewrote the affected tests in `test_insights.py` to encode this contract directly: one new test asserts that a second product row's drifted tag does NOT change an event's counted reason, with a fixture built to break a tie that would otherwise have made the bug invisible (the first fixture attempt for this test had both candidate reasons land on the same count by coincidence).

**Open questions**
None — all four handoff-locked reference numbers now match exactly, verified against the real snapshot before wiring into `app.py`.

**Left running for Mai's live review**
`streamlit run app.py`, per this session's instruction.

**Note on process**
Partway through this session Mai switched to remote control mode.

**Time spent**
~25 minutes: reading the handoff/PRD, TDD for `insights.py` (14 tests, one full red-green cycle plus a second cycle after the real-data discrepancy), diagnosing and fixing the top-reason methodology mismatch against the handoff's locked reference numbers, and wiring `app.py`.

---

## Entry 6.5 — Key Insights follow-up: sentence-format cards

**Goal**
Mai reviewed the Playwright screenshots from Entry 6 (hadn't opened the live app yet) and noted the cards read as bare data points, not sentences — the PRD's own Key Insights example (`"Recall events up 37% since 2014"`) is a full sentence, but neither the handoff nor Entry 6 had settled the card's internal format, so this was a real open question, not a mistake.

**What I built**
- Presented three concrete format options via `AskUserQuestion` (sentence as the `st.metric` value; the original label/number/delta split; sentence as a caption under a numeric card) with mocked previews built from the real numbers. Mai picked the sentence-as-metric-value option.
- Rewrote all four card values as full sentences in `app.py` (e.g. `"Up 10.5% from 2012 to 2025"`, `"2016 was the peak year"`, `"Undeclared allergen, most common reason"`), keeping the short delta line under each. Pure presentation formatting on the already-tested `KeyInsights` fields — no changes to `insights.py` or its tests, consistent with the handoff's contract that the pure function owns the math and `app.py` only formats.

**What broke**
The sentences are longer than the numbers/short labels `st.metric` is designed for, and Streamlit truncates with an ellipsis by default. First CSS fix (targeting `[data-testid="stMetricValue"]` with `white-space: normal`) had no visible effect — inspected the DOM directly and found Streamlit's actual truncation rule (`white-space: nowrap; overflow: hidden; text-overflow: ellipsis`) lives on the nested `<p>` inside `stMarkdownContainer`, not the outer div. The outer div's computed style already showed `overflow: visible`, which is what made the first attempt look like it should have worked but didn't.

**What I changed**
Extended the CSS override to target the `<p>` and `stMarkdownContainer` explicitly, with `!important` to beat Streamlit's own stylesheet specificity. Re-verified with Playwright by reading `getComputedStyle` on the actual `<p>` element (not just the outer div) before trusting a screenshot again, then confirmed visually — all four cards now wrap onto 1-2 lines with no truncation.

**Left running for Mai's live review**
`streamlit run app.py`, still running (`--server.runOnSave true` picked up every change automatically, so no restart was needed for anything in this entry either).

**Time spent**
~15 minutes: one AskUserQuestion round with three built previews, the sentence rewrite, and two rounds of CSS debugging (the second only needed because the first fix targeted the wrong DOM element).

---

## Entry 6.6 — Key Insights follow-up: zero-state wording

**Goal**
Mai did her own manual QA (a genuine zero-result filter combo, not something scripted before) and found the zero-state cards showed a bare dash "—", which read as unclear/broken rather than intentional.

**What I built**
Went to `AskUserQuestion` to confirm scope, since there are two distinct "can't compute a value" states in the cards that Mai's message could have meant either or both of: zero rows (dashes) versus rows present but fewer than two full years, e.g. year range narrowed to 2026 alone ("N/A"). Confirmed: zero-rows case only — replaced the four dash placeholders in `app.py`'s `if len(filtered_df) == 0` branch with `"No conclusions"`. The separate "N/A" wording for the insufficient-full-years case is untouched; that's a real value gap on real data, not an empty view.

**What worked**
Verified live rather than trusting the change blind: drove the actual Category/Reason/Severity multiselects via Playwright (Dairy + Botulism risk + Class III — confirmed zero matches) and read the four `st.metric` values directly from the rendered page. All four now show "No conclusions"; the existing "No recalls match the current filters" info message and the three hidden chart sections were unaffected.

**What broke**
Nothing.

**Left running for Mai's live review**
`streamlit run app.py`, still running via `--server.runOnSave true`.

**Time spent**
~5 minutes: one AskUserQuestion round to disambiguate the two edge cases, the one-line wording change, and live Playwright verification against a real zero-result filter combo (the multiselect-driving script itself took a couple of selector attempts to get right).

---

## Entry 7 — Phase 3 complete; handoff to Phase 4 (no code this entry)

**Goal**
Phase 3 Slice 2 (Key Insights) plus both of Mai's live-review follow-ups were done and confirmed working, which closes out Phase 3 entirely — all three slices (core charts, filters & reactivity, Key Insights) now live behind 118 passing tests. Summarize the slice and hand off Phase 4 (transparency & UI polish), the only PRD phase left before Phase 5 (QA/docs/submission).

**What I built**
No code. `HANDOFF_PHASE4.md` — an audit of the PRD's four Phase 4 deliverables (last-updated timestamp, accessible labeling, explanatory notes, robust error UI) against what Phases 2-3 already built, rather than assuming Phase 4 starts from zero.

**What worked**
Reading `app.py`, `charts.py`, `schema.py`, and `pipeline.py` directly before writing anything found that three of the four deliverables are already substantially done: the last-updated caption exists, the chart palette is already validated and every widget/panel is labeled, and `load_recalls()` already raises a clear, tested `ValueError` on a bad snapshot. That left two concrete, low-ambiguity gaps instead of a vague "polish everything" scope: (1) the About section is missing the event-vs-product lens explanation the PRD's Design Direction section explicitly names as one of three things it must consolidate — currently that explanation only lives in scattered chart captions, not in the About section itself; and (2) `app.py` never catches `load_recalls()`'s `ValueError`, so a missing/corrupted CSV currently surfaces as Streamlit's raw traceback page instead of a friendly message, which is the concrete case the PRD's "disable or warn... if expected columns are missing" bullet maps to for this app.

**What broke**
Nothing — planning-only entry.

**What I changed**
Nothing in code. Also flagged one thing as a documented platform limitation rather than a build task: Vega-Lite charts via `st.altair_chart` have no built-in screen-reader data-table fallback, which isn't fixable in this stack in this timeframe — recommended one About-section line naming it, matching how the PRD already treats other data-source-boundary facts (meat-category absence, missing country of origin) as documented limitations rather than defects.

**Open questions carried into Phase 4**
None deliberately left open — both concrete gaps are small enough (a markdown bullet, a try/except) that no design decision needs Mai's input before starting.

**Time spent**
~10 minutes: confirming Phase 3's final state (118 tests, both live-review fixes), reading four source files to audit Phase 4's four deliverables against real code rather than the PRD's abstract list, and writing the handoff.

---

## Entry 8 — Phase 4: About-section gaps + robust error UI

**Goal**
Execute the short, targeted slice `HANDOFF_PHASE4.md` scoped: close the two
remaining About-section gaps and catch `load_recalls()`'s `ValueError` in
`app.py` instead of letting it surface as a raw traceback.

**What I built**
Two new bullets in `app.py`'s "About the data & limitations" expander — one
explaining the event-vs-product lens split (reusing the 3.74x
product-to-event ratio already established in the PRD), one documenting the
Vega-Lite/Altair screen-reader-fallback gap as a platform constraint, in the
same tone as the six existing bullets. Also wrapped the `get_data()` call
site in `try/except ValueError`, showing `st.error(str(e))` then
`st.stop()`.

**What worked**
No new pure functions were needed, as the handoff predicted — both were
markdown-string and control-flow changes in `app.py` only. Verified the
error path by renaming `data/food_recalls.csv` out of the way, restarting
the Streamlit process, and confirming the server log showed no unhandled
traceback (previously `load_recalls()`'s `ValueError` would have propagated
unhandled); confirmed directly in Python that `load_recalls()` still raises
`ValueError` with its existing actionable message. Restored the CSV,
restarted, confirmed HTTP 200 with a clean log.

**What broke**
Nothing.

**What I changed**
Nothing beyond the plan — no design decisions needed re-opening.

**Left running for Mai's live review**
`streamlit run app.py --server.runOnSave true`, running on port 8501.

**Time spent**
~10 minutes: reading the handoff and PRD sections it referenced, three small
edits, and the rename/restart verification cycle for the error path.

---

## Entry 9 — Phase 4 remote review: screenshots in place of live access

**Goal**
Mai asked to review Phase 4 live but was away from her laptop, so live
review wasn't possible. Needed a substitute that showed the actual running
app (not a description of it), including two specific edge cases she asked
about after seeing the first round: the zero-result state and the
insufficient-data state.

**What I built**
A Playwright driver script against the already-running `streamlit run app.py`
session, capturing: the default view, the About expander scrolled to the two
new Phase 4 bullets, the Category filter's type-ahead dropdown, a
Produce-filtered result, a genuine zero-result combination (Dairy + Botulism
risk + Class III), and a single-year selection (2026 only) to trigger the
insufficient-full-years "N/A" cards. First delivered via `SendUserFile`;
when Mai reported she couldn't access those, rebuilt the same six
screenshots as a self-contained HTML gallery (base64-embedded images, no
external requests) and published it as a Claude Artifact instead, which
worked.

**What worked**
Driving Streamlit's newer react-aria-based combobox widgets (not the
BaseWeb selects assumed from memory) — `get_by_role("combobox", name=...)`
plus typing the option text to filter, rather than clicking through an
unfiltered option list. Confirmed via direct DOM inspection when the first
locator guesses (`data-baseweb='select'`) came back empty.

**What broke**
Two things, both interaction-model mistakes rather than app bugs. First,
pressing `Escape` after clicking a dropdown option cleared the just-made
selection instead of confirming it — clicking elsewhere on the page instead
of `Escape` was what actually committed the tag. Caught by checking the
rendered event count after the "filtered" screenshot still showed the
full unfiltered total. Second, `SendUserFile` reported success but Mai
couldn't open the files on her end — no error surfaced on this side, so the
gap was invisible until she said so directly.

**What I changed**
Switched the delivery mechanism from `SendUserFile` to a published Artifact
(a single HTML file with all six PNGs inlined as data URIs) once the first
approach was confirmed not to reach her. Left the actual running Streamlit
session untouched throughout — all screenshot capture used separate headless
browser instances against the same port, so the live app Mai will eventually
review directly was never restarted or reconfigured for this.

**Time spent**
~20 minutes: the driver script and two rounds of selector debugging, the
`Escape`-vs-click-away bug hunt, and rebuilding the delivery as an Artifact
after the first channel failed.

---

## Entry 10 — Phase 5 kickoff: LLM category-labelling build (manual round trip)

**Goal**
`HANDOFF_PHASE5.md` scoped this session as QA + edge cases + a submission
draft, explicitly deferring the LLM-assisted category-labelling pass (PRD
"Phase 3 (added)") out of scope. Mai wanted that pass pulled in first, since
refining the ~12% `Uncategorized` residual could shift chart shapes the QA
pass and the doc should reflect.

**What I built**
The PRD's Phase-3-added spec assumed a standalone script hitting the
Anthropic API directly, batching product descriptions against a fixed
category enum. Mai was on mobile via Remote Control with no terminal access,
so there was no safe way to hand a script an API key this session. Landed on
a manual round trip instead: `recall_explorer/llm_categories.py` (new, pure,
no network) exports the 3,554 still-`Uncategorized` rows as
`(recall_number, product_description)`, builds a ready-to-paste prompt
stating the fixed category enum and the exact expected output shape, and
parses/validates whatever comes back from a *separate* Claude.ai chat Mai
runs herself. `recall_explorer/pipeline.py` gained
`apply_llm_category_override()`, a pure function that prefers an optional
`llm_category` raw column over the keyword-derived `category` wherever it's
set, wired into `load_recalls()` right after the keyword pass. The frozen
`categories.py` rules are untouched either way — this only layers on top.

Sent Mai the export CSV and the prompt text via `SendUserFile`; she'll take
those to a separate Claude.ai chat (possibly iterating a few times to tune
the category calls) and paste the result back for the merge step.

**What worked**
`CATEGORY_ENUM` is built directly from `categories.py`'s own
`PRODUCT_IDENTITY` and `CATEGORY_RULES` names rather than a hand-copied
list, so it can't silently drift out of sync if a category is ever
added/renamed there. `EXPECTED_COLUMNS` in `schema.py` turned out to already
be an allow-list check (`missing = [c for c in EXPECTED_COLUMNS if c not in
df.columns]`), so adding the optional `llm_category` column later won't need
a schema change.

**What broke**
Testing `apply_llm_category_override()` through `load_recalls()` directly
wasn't viable — `validate_schema()` enforces a 29,000-row floor a small
fixture CSV can't meet. Extracted the override into its own pure function
and tested it directly on hand-built DataFrames instead, matching this
project's established three-tier strategy (strict TDD on pure logic, one
real-file pipeline test, a schema guardrail).

**What I changed**
Nothing outside the new module and the one pipeline addition — no chart or
insights code needed changes, since `count_by`/`seasonality_matrix`/etc. all
key off whatever the `category` column holds.

**Open questions**
Whether the fixed-enum prompt holds up across Mai's iteration runs on the
other chat, and whether the merge step (once she pastes results back) turns
up any `parse_classification_result` problems worth reviewing before
trusting the merge.

**Time spent**
~25 minutes: reading the handoff/PRD, three rounds of `AskUserQuestion` to
land on the manual-round-trip design given the mobile/no-terminal
constraint, TDD on `llm_categories.py` and the pipeline override (16 new
tests, all green), and generating/sending the export.

---

## Entry 10.5 — Export delivery, round two: the file-link problem again (no code this entry)

**Goal**
Get the 3,554-row CSV and the classification prompt actually into Mai's
hands on mobile, after `SendUserFile` reported success but the file link
wasn't clickable/downloadable from her side — the same class of delivery
gap as Phase 4's Entry 9, this time on the input side rather than the
output side.

**What I built**
A single self-contained HTML page (published as a Claude Artifact, not sent
as a file) embedding both the CSV text and the prompt text directly in
read-only `<textarea>` elements, each with a "Copy" button
(`navigator.clipboard.writeText`, falling back to select-all if clipboard
access is blocked) plus a best-effort blob-URL download link as a third
option. Same light/dark token structure as the Phase 4 screenshot gallery.

**What worked**
The copy-to-clipboard buttons — Mai confirmed she was able to get both the
CSV and the prompt into the other Claude.ai chat this way and has kicked
off classification there.

**What broke**
Two delivery attempts before landing on one that worked: `SendUserFile`
first (file card visible but not clickable/downloadable on her mobile
client), then the Artifact's own download-button/blob-URL path (didn't
trigger a download on her device either — likely an iOS Safari restriction
on programmatic downloads from a blob URL outside a direct user gesture
chain). The copy-to-clipboard buttons, which don't rely on the browser's
download UI at all, were what actually worked.

**What I changed**
Nothing in the app or its tests — this was entirely about getting existing
export artifacts (the CSV, the prompt) into Mai's hands, not about their
content.

**Open questions**
Same as Entry 10: whether the fixed-enum prompt holds up across her
iteration runs, and what `parse_classification_result` turns up once she
pastes results back — that merge step hasn't happened yet.

**Time spent**
~10 minutes: two failed delivery attempts, the Artifact rebuild with copy
buttons, and confirmation it worked.

---

## Entry 11 — The subset pass covered 12%, not 100%: a scope error and its correction (planning only, no code)

**Goal**
Confirm the file to merge (per `HANDOFF_PHASE5_LLM_MERGE.md`), run the merge,
and continue into QA — the plan Phase 5 was supposed to execute this session.

**What happened instead**
`export_for_classification()` filters to `category == "Uncategorized"`
([llm_categories.py:44](recall_explorer/llm_categories.py#L44)). The manual
Claude.ai round trip from Entries 10–10.5 therefore classified 3,554 rows —
12.2% of the dataset — not the full 29,161 rows Mai intended. It filled the
keyword rules' blanks; it never reviewed a single one of the 25,607 rows the
keyword rules had already labeled.

Confirmed from both directions independently:

- Here: a fresh `export_for_classification(load_recalls())` reproduces
  exactly the 3,554-row expected set; the classification CSV's recall
  numbers match it 1:1, zero outside it.
- From the classifying session, asked directly: it confirmed the same
  boundary and named the tell it had itself produced but misread — its own
  QA found *zero* egg products, *zero* oils/fats, and one poultry row in its
  slice, which it reported as a property of the dataset rather than the
  fingerprint of a pre-filtered file. (Keyword rules catch "chicken",
  "egg", and "olive oil" trivially, so those rows never reached it.)

Caught before any merge ran, so nothing needed to be undone — but the
original merge plan (`HANDOFF_PHASE5_LLM_MERGE.md`) was built on the
assumption that this file was the intended full-dataset result, and that
assumption was wrong.

**What I verified before replanning**

- **The app is not brittle to this kind of data change.** Grepped
  `app.py`, `charts.py`, `insights.py`, `filters.py`, `transforms.py` for
  hardcoded category names: one hit, a comment in the About-section prose.
  A dry-run merge of the 3,554-row file (never committed) broke exactly two
  tests, both documentation-shaped — the `Uncategorized`-share bound and an
  exact-column-order schema assertion.
- **Real errors exist in the unaudited 87.8%.** `Beef` (65 rows) and `Pork`
  (88 rows) are mostly flavoring words ("Nat Flv Beef FF", "Bacon Twice
  Bake"), matching `categories.py`'s own documented tier-3 tradeoff.
  `Poultry/Eggs` (208 rows) is two categories under one label: roughly 50
  genuine shell-egg recalls — including the Rose Acre Farms salmonella and
  Almark Foods listeria events, two of the largest in the 2012–2026 window
  — mixed with ~141 poultry-flavoring rows.

**Decision: reclassify the full dataset via the API, not another manual
round trip.** The original manual-round-trip design (Entry 10) existed
solely because Mai was on mobile Remote Control with no terminal access.
That constraint no longer holds — she now has terminal access and ran
`ant auth login` herself mid-session, giving the project a working OAuth
profile (`user:inference` scope, no static key needed). The PRD's original
"one-time API script" design is viable again, and correct at this volume:
29,161 descriptions cannot go through a chat round trip without repeating
the three-attempt delivery saga from Entry 10.5 roughly eight times over.

**Decisive input: a recovered decision log.** Mid-session, Mai retrieved a
full decision log from the classifying session — an 18-label taxonomy, a
governing principle ("classify what the product most fundamentally *is*,
not every ingredient it contains"), per-category inclusion rules, 10
boundary rules for the collisions that actually caused trouble (Bakery vs.
Baking Supplies, cooked beans, frozen novelties, chile products, bulk
batter mixes, ...), and a **self-flagged "Known gaps" section**. That
section named the same three blind spots independently found here — zero
eggs, zero oils, one poultry row — and asked, unprompted, for a ruling on
each. This is now the taxonomy spec; the new plan finalizes it rather than
designing one from scratch.

Pressure-testing the log against the full dataset (not just its own
awareness of its gaps) found it is not fully comprehensive either: ~640
rows of alcohol (262), coffee creamer (237), broth/stock (82), and baby
food (62) have no rule at all, plus honey and agave/stevia/molasses that
are only implied. The new plan's Step 1 closes these alongside the log's
own four open questions before the classification prompt is written.

**What I changed**
Wrote a full replacement plan (`.claude/plans/read-handoff-phase5-llm-merge-md-first-t-purrfect-lynx.md`),
superseding both `HANDOFF_PHASE5_LLM_MERGE.md`'s merge-the-subset design and
this session's own first two drafts of the replacement. Key decisions locked
into the plan:

- Taxonomy: the recovered log's 18 labels plus a new `Eggs` label (the log's
  own top-priority open question), finalized against a ~5,000-row stratified
  design sample that includes *all* 466 rows from the five categories the
  log never saw evidence for (`Poultry/Eggs`, `Pork`, `Beef`, `Plant
  Protein`, `Oils/Fats`) rather than sampling into them.
- Classification: `claude-opus-5` via the Message Batches API (50% off),
  structured outputs with a `category` enum (invalid labels impossible by
  construction) plus a `confidence` field, `effort: "high"` — Opus 5's
  default — with the pilot sweeping *downward* only if cheaper settings
  produce materially the same labels.
- Pipeline: replace `apply_llm_category_override()` with a direct read of
  `llm_category` and drop `assign_category` from the runtime path entirely,
  rather than keeping it as a fallback — a keyword fallback for
  never-seen rows would silently reintroduce the labeling this pass exists
  to replace. `categories.py` and its 31 tests stay in the repo, frozen, as
  provenance for the submission doc.
- Trust: six validation checks (self-consistency, agreement with the 3,554
  reviewed labels, confidence triage, category-coherence sampling,
  keyword-vs-LLM disagreement per category, residual inspection) rather than
  spot-checking, because 29,161 rows cannot be eyeballed and the point is to
  make the remaining uncertainty locatable.

**Open questions**
Actual cost, once the pilot measures real token usage including thinking
(the earlier ~$9 `chars/4` estimate excludes thinking tokens and is a
floor, not a number to plan against). Whether the coverage-hole categories
(alcohol, coffee creamer, broth, baby food) need genuinely new labels or
fit inside the existing 18 with the right rule. Whether `effort: "high"`
turns out to be necessary once the pilot's downward sweep runs, or whether
`medium` gives the same labels for less.

**Time spent**
~2 hours: confirming the scope error from both sides, verifying app
robustness and the meat/eggs data problems empirically, three full
plan-writing passes (the first assumed no API access and proposed a
500-row hand-design; the second incorporated Mai's terminal access and the
Batch API; the third incorporated the recovered decision log and cut the
plan's accumulated self-justifying prose after a request to reduce drift
risk), and ten rounds of user review comments, each requiring a factual
check before the fix (confirming `ant auth status`, sizing the untested
categories at 466 rows, verifying all 249 "Blue Bell" rows are ice cream,
pressure-testing the log's coverage against the real data, reconciling an
internally contradictory `effort` recommendation).

---

## Entry 12 — Step 1 taxonomy finalization: prep and design sample (in progress)

**Goal**
Execute Step 1 of the reviewed plan
(`.claude/plans/read-handoff-phase5-llm-merge-md-first-t-purrfect-lynx.md`):
finalize the taxonomy against a ~5,000-row design sample via one Opus 5 API
call, and show the proposal before writing `CLASSIFICATION_RULES.md` or
touching `CATEGORY_ENUM`.

**What I found**
The handoff (`HANDOFF_PHASE5_FULL_RECLASSIFICATION.md`) claimed the recovered
decision log was "reproduced in full inside the plan file." It wasn't — the
plan file only carried a summary (label list, four open questions, gap
table), not the actual per-category rules or the 10 boundary rules. Mai
re-supplied the full log directly; it's now saved at
`scratch/decision_log.md` (not checked in, per the plan — it's the seed
content for the eventual `CLASSIFICATION_RULES.md`, written only after
approval).

**What I built**
- Confirmed prerequisites: `.venv/bin/pytest` 134 passed; `ant auth status`
  live (`mai.irie@gmail.com`, `user:inference` scope); `ANTHROPIC_API_KEY`
  unset.
- Installed the `anthropic` SDK (0.122.0) and its transitive deps into
  `requirements.txt`, keeping the existing pinned-freeze convention rather
  than a full `pip freeze` overwrite (which would have pulled in unrelated
  dev-only packages like `pytest`/`playwright` that aren't part of this
  pinned file's scope).
- Built the design sample (`scratch/build_design_sample.py`, `scratch/design_sample.csv`,
  neither checked in): all 466 rows from the five categories the log never
  saw evidence for (`Poultry/Eggs` 208, `Pork` 88, `Beef` 65, `Plant Protein`
  55, `Oils/Fats` 50 — confirmed via `load_recalls()["category"].value_counts()`,
  matching the plan's numbers exactly), plus 801 rows pulled by keyword for
  the six coverage-hole product types, plus 3,733 stratified from the
  remaining eleven categories. Total: exactly 5,000 rows.

**What broke**
A first pass at the coffee-creamer keyword (`creamer` with no word boundary)
matched 237 rows — but 180 of those were "Creamery" (a dairy-brand name
substring), not creamer products. The same class of bug `categories.py`
already documents (`clamshell` → `Seafood`, 509 rows). Added a trailing
`\b` and the true count is 57. The plan's original coverage-hole estimates
(alcohol 262, coffee creamer 237, broth 82, baby food 62) were themselves
rough; my keyword counts came out different in most cases (alcohol 277,
creamer 57, broth 67, baby food 25) — real evidence either way, so the
sample proceeds with the measured counts rather than reconciling to the
estimates.

**What I changed**
Nothing in `recall_explorer/` yet. Only `requirements.txt` (the `anthropic`
dependency) is a real repo change so far; `scratch/decision_log.md` and the
design-sample script/CSV are intentionally not checked in.

**Open questions**
None new — the four from the decision log's "Known gaps" section are still
open, to be resolved by the upcoming API call against this sample.

**Time spent**
~45 minutes: recovering the decision log, verifying prerequisites, installing
the SDK, and building/debugging the design sample.

---

## Entry 13 — Step 1 taxonomy finalization: the design-sample API call

**Goal**
Run the taxonomy-finalization call (Opus 5, `effort: high`) against the
5,000-row design sample and get a proposal to show Mai, per Step 1's
"nothing written until approved" rule.

**What I built**
`scratch/run_taxonomy_finalization.py` (not checked in): system prompt =
`scratch/decision_log.md` verbatim + a task wrapper (apply the log's rules,
resolve the four open questions with sample evidence, write rules for the
six coverage-hole types, flag new collisions, propose the final label set).
User message = the 5,000-row sample CSV. `client.messages.stream(...)`,
`model="claude-opus-5"`, `effort: "high"`, no explicit `thinking` param
(adaptive by default on this model per the SDK skill's guidance).

**What broke**
First run: `max_tokens=16000` truncated mid-response. Adaptive thinking used
14,959 of those tokens, leaving ~1,000 for the actual proposal text — Opus 5
counts thinking against `max_tokens` unless thinking is disabled. Reran at
`max_tokens=48000`; the full response completed at 37,998 output tokens
(21,638 thinking + ~16,360 text).

**What I got**
Cost: 622,299 input tokens (~$3.11), 37,998 output tokens (~$0.95) — about
$4 for this one design call. The proposal (`scratch/taxonomy_proposal.md`,
not checked in) is substantially more thorough than Step 1 anticipated:

- **20 labels**, not the expected "18 + Eggs = 19." A second new label,
  `Baby/Toddler Food`, emerged from evidence the plan already flagged as a
  coverage hole but hadn't sized as label-worthy — the sample showed a
  single product line (infant purees, infant formula across protein bases)
  fragmenting three to four ways under the log's ingredient-based rules.
- All four open questions resolved with cited row evidence rather than
  general reasoning: add `Eggs` (~60+ rows with no home in the 18); the
  milk/produce/meat rules mostly hold with two dairy additions and one
  produce clarification (fresh vs. dried herbs); `Oils/Fats` confirmed with
  an expanded boundary; full relabel confirmed, with a table of specific
  keyword-labeling error classes (buns matched on "hamburger," seasonings
  matched on the meat they season, plant analogs matched on the animal they
  imitate) as the evidence a forward mapping can't fix.
- All six coverage-hole types resolved: alcohol and coffee creamer →
  `Beverages`; broth split by concentration (liquid → `Prepared/Frozen`,
  bases/bouillon → `Spices/Condiments`); baby food → the new
  `Baby/Toddler Food` label, which also absorbs all infant formula
  (superseding the log's protein-based formula split); honey →
  `Spices/Condiments` with a carve-out for claim-bearing sachets →
  `Supplements`; agave/stevia/molasses → `Spices/Condiments`, with dry
  crystalline sugar staying `Baking Supplies` and bulk purified compounds
  going to `Food Additives/Ingredients`.
- **8 new label collisions** beyond the log's 10 boundary rules, each
  evidenced with specific recall numbers: meat-named seasonings/rubs/
  marinades → `Spices/Condiments`; deli sandwiches → `Prepared/Frozen`;
  plant-based analogs classified by composition not by what they imitate;
  dressed deli salads split by dominant ingredient; hummus/dips three-way
  split; medical/enteral nutrition → `Supplements`; **protein powders and
  RTD shakes → `Supplements` regardless of protein source** (a real change
  from the log, which had them in `Plant Protein`); non-food items
  (pet food, cosmetic kits) confirmed as `Non-Food Item`.
- The model flagged its own evidence gaps rather than papering over them:
  raw single-ingredient meat cuts are essentially absent from FDA data
  (USDA jurisdiction), so the merged meat label is validated only against
  deli/cured/cooked meat; `Baking Supplies` had no direct sample coverage
  at all and its boundaries were inferred from adjacent rows.

**What I changed**
Nothing in `recall_explorer/`, `CLASSIFICATION_RULES.md`, or `data/` — per
Step 1's plan, the proposal is presented to Mai for approval before any of
that gets written. Only `scratch/run_taxonomy_finalization.py` (script) and
`scratch/taxonomy_proposal.md` (output), neither checked in.

**Open questions**
Whether Mai approves 20 labels (vs. the plan's expected ~19) — specifically
the two new labels (`Eggs`, `Baby/Toddler Food`) and the protein-powder
reclassification into `Supplements`, which is a real behavior change from
the recovered log, not just a gap-fill. If approved, Step 2's classification
script needs the finalized enum plus a note that `Beef/Pork/Poultry/Game
Meats` boundaries now explicitly exclude several product types (seasonings,
buns, sandwiches, plant analogs) that a keyword match on a meat word would
have caught.

**Time spent**
~15 minutes: writing and debugging the prompt/script, two API calls (~5 min
combined including the truncated first attempt), reviewing the output.

---

## Entry 14 — Step 1 taxonomy, revision round: four corrections from Mai

**Goal**
Fold Mai's review feedback on `scratch/taxonomy_proposal.md` into a revised
proposal, without a second API call, and get final sign-off before writing
`CLASSIFICATION_RULES.md`.

**What Mai flagged**
Four corrections, all the same underlying fix: v1 grouped several items by
*where they're consumed* or *what they're not*, rather than by *what
they're made of* — inconsistent with v1's own stated principle for plant
analogs. Specifically: (1) protein powders/RTD shakes shouldn't all go to
`Supplements` — plant-protein-based ones belong in `Plant Protein`; (2)
should plant milks move from `Beverages` to `Plant Protein` too?; (3) pet
food/treats shouldn't be lumped into `Non-Food Item` with genuinely
inedible objects — it deserves its own label; (4) coffee creamer
shouldn't be a blanket `Beverages` call — dairy creamer should be `Dairy`,
plant-based creamer should follow whatever plant milk does.

**What I did**
Point 2 was a genuine open call (not something Mai's message resolved on
its own), so asked via AskUserQuestion rather than deciding unilaterally.
Mai chose "Plant Protein" — same composition-over-destination logic as the
other three points, and consistent with how dairy milk itself sits in
`Dairy` (composition) rather than `Beverages` (how it's drunk). That
resolved point 4 automatically: creamer now splits three ways by base
(dairy → Dairy, plant → Plant Protein, neither → Beverages fallback).

Wrote `scratch/taxonomy_proposal_v2.md` (not checked in) — a diff-style
document against v1, not a rewrite: a before/after table for the four
points, the revised label set (now **21**, not v1's 20 — `Pet Food/Treats`
is a new label on top of `Eggs` and `Baby/Toddler Food`), revised rule text
for the six affected labels (`Plant Protein`, `Supplements`, `Dairy`,
`Beverages`, `Non-Food Item`, new `Pet Food/Treats`), and an explicit note
that everything else from v1 (open questions, coverage-hole rules, 7 of 8
collisions) carries over unchanged. No new API call — these are precise
re-groupings of rows the first call already examined and cited; the
evidence didn't change, only which label it lands in.

**What I changed**
Nothing in `recall_explorer/`, `CLASSIFICATION_RULES.md`, or `data/` — v2
is presented for final approval before any of that gets written, same rule
as v1.

**Open questions**
None outstanding on the label set itself — all four correction points are
now resolved (three from Mai's direct instruction, one via AskUserQuestion).
Pending: Mai's final approval of the 21-label v2 set before
`CLASSIFICATION_RULES.md` gets written.

**Time spent**
~10 minutes: reading feedback, asking the one genuinely open question,
writing the revision document.

---

## Entry 15 — Correcting the plant-based coffee creamer call in v2

**Goal**
Sanity-check one piece of v2's own revision before it goes to Mai for final
approval: does plant-based coffee creamer actually contain meaningful plant
protein, the way plant milk does? Mai asked this directly rather than
accepting the v2 draft's assumption at face value.

**What I built**
Re-read v1's actual cited evidence for the coffee-creamer rule (all brand
examples — Coffee-Mate, Silk, International Delight, MO-CHA, Kraft,
Libby's) and found it never examined ingredient or protein content; it only
used inconsistent keyword-labeling of near-identical products as the reason
to standardize on `Beverages`. Real plant-based coffee creamer is
typically water, oil (often coconut/sunflower, not the named plant milk),
sugar, and thickeners/emulsifiers — an additive product with ~0g protein
per serving, unlike oat/soy/almond milk itself, which is sold and consumed
as the primary protein-bearing beverage/food.

**What worked**
Separating "plant milk" from "plant-based coffee creamer" — they'd been
folded together under the same composition-over-destination principle in
v2, but only one of them is actually a protein-bearing plant food.

**What broke**
Nothing broke; this is a correction to the v2 draft before it was ever
presented as final, not a rework of already-approved output.

**What I changed**
`scratch/taxonomy_proposal_v2.md`: reverted plant-based coffee creamer from
`Plant Protein` back to `Beverages` (its v1 fallback). Plant milk keeps its
`Plant Protein` placement — unaffected. Coffee creamer is now a two-way
split (dairy → `Dairy`; everything else, including plant-based → 
`Beverages`), not three-way. Updated the "What changed vs. v1" table, the
label-set summary table (`Plant Protein` and `Beverages` rows), and the
detailed rule text for both labels, plus added an explicit correction note
explaining why plant milk and plant creamer are treated differently despite
both being "plant-based."

**Open questions**
None. Ready to present the corrected v2 set for final approval.

**Time spent**
~10 minutes.

---

## Entry 16 — Phase 5 Step 1 checkpoint: CLASSIFICATION_RULES.md + CATEGORY_ENUM

**Goal**
Close out Step 1 of the master plan: write the approved 21-label taxonomy
into the repo as `CLASSIFICATION_RULES.md`, rewrite `CATEGORY_ENUM` in
`recall_explorer/llm_categories.py` to match it exactly, and add a
doc/code sync test — the checkpoint that unblocks Step 2's classification
script.

**What I built**
- `CLASSIFICATION_RULES.md` (repo root): the full taxonomy spec — label
  set (21), governing principle, per-category rules (21 sections),
  boundary rules (24 entries, up from the original log's 10), coverage-hole
  rules (6 product types), known gaps (3), and a revision-history section
  documenting v1 (API proposal) -> v2 (Mai's four corrections) -> v2
  correction (the coffee-creamer walk-back from this session). Built by
  merging `scratch/decision_log.md` (the original 18-label log),
  `scratch/taxonomy_proposal.md` (v1's API output, with full row-level
  citations), and `scratch/taxonomy_proposal_v2.md` (Mai's corrections)
  into one authoritative document — no new analysis, no fabricated
  evidence, every rule traceable to prior citations.
- `recall_explorer/llm_categories.py`: `CATEGORY_ENUM` replaced with a
  literal 21-item list matching the doc verbatim. Deleted
  `EXTRA_LLM_CATEGORIES` and the derivation from `categories.py`'s
  `CATEGORY_RULES`/`PRODUCT_IDENTITY` (the old enum was keyword-rule-shaped;
  the new one is taxonomy-shaped and intentionally decoupled from the
  frozen keyword module). Module docstring rewritten to explain the Phase 3
  -> Phase 5 scope change.
- `tests/test_llm_categories.py`: replaced
  `test_category_enum_matches_categories_module_rules` (which asserted
  keyword-rule categories were a subset of the enum -- meaningless now that
  the enum no longer derives from keyword rules) with
  `test_category_enum_matches_classification_rules_doc`, which regex-parses
  the "## 1. Label set (21)" code block out of `CLASSIFICATION_RULES.md`
  and asserts exact list equality against `CATEGORY_ENUM`. This is the
  doc/code sync guardrail the master plan's Step 1 Output requires --
  editing one without the other now fails a test.

**What worked**
`.venv/bin/pytest` -> 134 passed, no regressions. The only test that needed
rewriting was the one directly coupled to the old enum-derivation logic;
`export_for_classification`, `build_classification_prompt`, and
`parse_classification_result` all still pass unmodified since they only
reference `CATEGORY_ENUM` by name, not by how it's built.

**What broke**
Nothing. `categories.py` and its 31 tests are untouched, per the master
plan's "out of scope" list -- it stays frozen, just no longer feeds
`llm_categories.py`.

**What I changed**
See "What I built." No other files touched.

**Open questions**
None on the taxonomy itself. Step 2 (build `classify_all.py` against the
Batch API) is next, per the master plan -- not started this session.

**Time spent**
~35 minutes: assembling `CLASSIFICATION_RULES.md` from three source docs,
rewriting the enum, writing and verifying the sync test, full test run.

---

## Entry 17 — Phase 5 Step 2: classify_all.py (Batch API classifier)

**Goal**
Build the one-time script that submits the full 29,161-row dataset to the
Claude Message Batches API for classification under `CLASSIFICATION_RULES.md`,
per the master plan's Step 2.

**What I built**
`classify_all.py` (repo root, beside `fetch_data.py`), two subcommands:
- `submit` -- loads the full dataset, chunks it into 292 requests of up to
  100 rows each, splits those into 3 roughly-equal submissions (98/97/97),
  builds each request with a cached system block (`CLASSIFICATION_RULES.md`
  + a task wrapper covering the confidence rubric and two worked examples,
  one of them fixing v1's unresolved "Blue Bell coconut fudge" example to
  its correct answer, `Dairy`), a `json_schema` output_config constraining
  `category` to `CATEGORY_ENUM` and `confidence` to `high|medium|low` by
  construction, and `effort: "high"` with default adaptive thinking. Writes
  batch IDs to `data/batch_ids.json`.
- `fetch` -- polls every batch ID, reports per-batch status, and once all
  have ended, streams every chunk's results (`succeeded`/`errored`/
  `canceled`/`expired`, checking `stop_reason == "refusal"` before reading
  content), validates zero missing / zero unexpected recall_numbers against
  the full dataset, and writes `data/recall_categories_llm_full.csv`.
  Aborts loudly (`SystemExit`) rather than writing a partial file.

Pure logic factored out for TDD: `chunk_rows`, `split_into_submissions`,
`custom_id_for`, `build_chunk_user_content`, `build_response_schema`,
`build_system_blocks`, `build_chunk_request`, `parse_chunk_response_text`,
`check_completeness`, `write_results_csv`, `rows_to_classify`.
`tests/test_classify_all.py`: 25 tests, strict TDD (written first, watched
fail on `ModuleNotFoundError` before any implementation existed), plus one
real-file pipeline test (`rows_to_classify` against the actual
`data/food_recalls.csv` via `load_recalls()`). The `submit`/`fetch` CLI
functions themselves are not unit-tested -- per the project's standing
skip list, no retry/mocking theater around network calls.

**What worked**
Chunk math confirmed against the master plan's estimate exactly: 29,161
rows -> 292 chunks -> submissions of [98, 97, 97]. `.venv/bin/pytest` ->
159 passed (134 prior + 25 new), zero regressions.

**What broke**
Two things caught by the tests, not assumed:
1. `anthropic.types.messages.batch_create_params.Request` is a `TypedDict`,
   not a class instance -- `request.custom_id` fails,
   `request["custom_id"]` is correct. Caught immediately by the first test
   run against real types, fixed in the test (the implementation was
   already using dict-style construction correctly).
2. **Two rows in the real dataset share a blank `recall_number`**
   (`event_id` 99068 and 99205, both from a 2026-05/06 batch -- an
   ANGEL-branded soft-serve powder recall and a Le Chef Bakery pastry
   recall). Both fields are empty/`"N/A"` in the raw CSV, which pandas
   reads as `NaN` for both, so they collapse to one key. This is a
   pre-existing openFDA data gap, not introduced by this pass -- caught by
   the real-file pipeline test expecting `len(df)` unique keys and getting
   `len(df) - 1`.

**What I changed**
Fixed the `Request` test to dict-subscript access. Adjusted the real-file
test's assertion to document the known 2-row blank-key collision rather
than assume uniqueness. **Did not** invent a synthetic key for the two
blank rows -- that's a data-quality call outside Step 2's scope.

**Open questions**
1. **The blank-recall_number collision needs a decision before `fetch`
   runs for real.** As written, `cmd_fetch`'s completeness check treats the
   dataset's `set(df["recall_number"])` as the expected set, which also
   collapses the two blank IDs into one -- so the check will not flag a
   missing classification if only one of the two rows' results survives
   the final merge (`collected[row["recall_number"]] = row`, keyed by the
   same blank string, second write wins). Net effect: the pilot and full
   run would silently produce 29,160 output rows for 29,161 input rows,
   with the loss undetectable by the current guard. Options: (a) use a
   different join key entirely (`event_id` + row position) for these two
   rows only, (b) exclude blank-recall_number rows from classification and
   flag them for manual handling, (c) patch the two source rows in
   `data/food_recalls.csv` with synthetic IDs before this pipeline runs.
   Flagging for Mai before the pilot, not deciding unilaterally.
2. Cost is still unknown until the pilot (Step 3) runs and measures actual
   token usage -- nothing here should be read as a spend commitment.

**Time spent**
~50 minutes: reading the Batches API and structured-output reference
material, writing the 25 failing tests, implementing against them, fixing
the two real-vs-assumed-shape breaks, full suite run.

---

## Entry 18 — Resolve the blank-recall_number open question: exclude, don't patch

**Goal**
Close Entry 17's open question. Mai's call: treat the two blank-recall_number
rows as incomplete data and exclude them from analysis/visualization
entirely, not just work around them in the classifier.

**What I built**
`recall_explorer/pipeline.py`'s `load_recalls()`: added a filter dropping
rows with a null or blank `recall_number` immediately after schema
validation, before date parsing or category assignment. Comment documents
the two known rows (event_ids 99068, 99205) and why -- `recall_number` is
the product-level key the whole app keys off of, so a row without one is
an incomplete record, not a normal edge case to route around.

Since `classify_all.py` calls `load_recalls()` too, this automatically
removes them from the classification input as well -- no special-casing
needed in `classify_all.py` itself, which is exactly the "keep the code
uniform" side of the (1)/(2) tradeoff Mai picked.

**What worked**
Both known rows turned out to be singleton events (each is its own
`event_id`, shared with no other row), so excluding them also cleanly drops
the event count by exactly 2 -- no partial-event weirdness to reason about.
Re-ran the chunk math after the exclusion: still exactly 292 chunks, same
[98, 97, 97] submission split, since 29,159 rows crosses the same 100-row
chunk boundaries as 29,161 did.

**What broke**
Nothing broke; two existing tests needed their hardcoded expectations
updated since they encode a structural fact of the snapshot that changed:
`SNAPSHOT_ROWS` (29,161 -> 29,159) and `SNAPSHOT_EVENTS` (7,791 -> 7,789) in
`test_pipeline.py`.

**What I changed**
- `pipeline.py`: the new filter (above).
- `test_pipeline.py`: updated the two constants with a comment explaining
  the 2-row gap; added `test_pipeline_excludes_rows_with_no_recall_number`
  asserting both the general invariant (no blank/null recall_number
  survives) and the specific two event_ids are gone.
- `test_classify_all.py`: simplified
  `test_rows_to_classify_covers_the_full_real_dataset` back to asserting
  full uniqueness, since `load_recalls()` now guarantees it -- removed the
  documented-collision special case from Entry 17.

**Open questions**
None. `.venv/bin/pytest` -> 160 passed (159 prior + 1 new), zero
regressions.

**Time spent**
~15 minutes.

---

## Entry 19 — Phase 5 Step 3: pilot run (high/medium/low effort)

**Goal**
Run the master plan's Step 3 pilot: ~250 rows (stratified + known-answer
probes) at three effort levels, measure cost and accuracy, and bring Mai a
recommendation before spending real money on the full 29,159-row run.

**What I built**
`scratch/build_pilot_sample.py` (not checked in): 197 proportionally-
stratified rows + 58 known-answer probes (regex-matched against 17 product
patterns -- shell eggs, romaine, bottled water, etc.), 255 rows total.
`scratch/run_pilot.py` (not checked in): classifies the sample synchronously
(not via Batch API -- iterating 3 effort levels serially mattered more here
than the 50% batch discount) at `high`/`medium`/`low`, reusing
`classify_all.py`'s exact request-shaping helpers so the pilot exercises the
same system prompt, schema, and 100-row chunking shape production will use.

**What broke**
1. **`high`-effort chunk 1 truncated** (`stop_reason=max_tokens`) --
   `MAX_TOKENS=8000` wasn't enough headroom for high-effort adaptive
   thinking on a 100-row chunk. Same failure class as Step 1's design-sample
   call hitting this at `max_tokens=16000`. Fixed by raising
   `classify_all.py`'s `MAX_TOKENS` to 24000. Confirmed clean on a full
   re-run of all 3 chunks at `high` (13,224 output tokens including
   thinking, well under budget, all `end_turn`).
2. **My own probe labels were wrong for ~20 of the 58 rows.** The regex
   patterns matched a keyword without confirming the keyword was actually
   the product -- e.g. `\bolive oil\b` tagged "Olive Oil Cake" (a finished
   Bakery item) and "Oysters in Olive Oil" (packing medium, still
   `Seafood`) as expected `Oils/Fats`; `\bhoney\b` tagged a "Honeydew" melon
   mix as expected `Spices/Condiments`. Manually re-read all 58 full
   descriptions against `CLASSIFICATION_RULES.md`, corrected 20 labels, and
   dropped 3 as genuinely ambiguous (a 40-item multi-product recall notice;
   a bean soup where the cooked-bean-dish rule and the soup-is-Prepared/
   Frozen rule conflict with no doc resolution; one truncated/unreadable
   description) -- 55 usable probes. Recorded in
   `scratch/pilot_probes_corrected.py` with the reasoning for every
   correction, not checked in.

**Results (55 corrected probes, 255-row sample)**

| Effort | Probe accuracy | Agreement w/ high | Pilot cost | Extrapolated full run (Batch API, 50% off) |
|---|---|---|---|---|
| high | 54/55 (98.2%) | -- | $0.51 | ~$29 |
| medium | 55/55 (100%) | 97.6% | $0.54 | ~$31 |
| low | 53/55 (96.4%) | 98.8% | $0.40 | ~$23 |

The two genuine misses: `F-2292-2012` (a vegan meal-replacement shake,
explicitly labeled "Dietary supplement" -- the model called it `Plant
Protein`, likely pulled by its "plant nutrition" branding language despite
squarely matching the `Supplements` rule) missed at both `high` and `low`;
`F-0684-2013` ("Whole Foods Meal Shrimp Stir Fry," a defensible boundary
case between protein-dominant and composite-meal) missed only at `low`.
Neither looks like a broken prompt -- both are plausible, explainable edge
cases, and medium's 100% on the same set suggests the differences across
effort levels are within noise at n=55, not a real quality gradient.

**What I changed**
`classify_all.py`: `MAX_TOKENS` 8000 -> 24000, with a comment explaining why.

**Open questions**
Effort level and full-run spend approval -- Mai's call per the master
plan's explicit Step 3 gate, not decided here. Cost via the Batch API (what
production will actually use) is close across all three levels (~$23-31)
relative to the total project; the bigger differentiator so far is output
token volume (high 13,224 vs. low 9,062 for the same 255 rows), not
accuracy.

**Time spent**
~70 minutes: sample construction, first pilot pass, catching and fixing the
truncation bug, catching and correcting my own probe-labeling errors,
clean re-run, cost/accuracy analysis.

---

## Entry 20 — Phase 5 Step 3: full run submitted

**Goal**
Submit the full 29,159-row dataset for classification, per Mai's approval
(effort: high, ~$29 estimated via the Batch API).

**What I built**
Ran `classify_all.py submit` for real. 292 chunks split across 3
submissions (98/97/97), each a separate Batch API job:
- `msgbatch_015K8biH1CtondHooZkywYHg` (98 chunks)
- `msgbatch_01LaQaAqoLNNCtwUwRtJwvsK` (97 chunks)
- `msgbatch_011XJNtZnCTBKVFk3XR2RAVH` (97 chunks)

IDs written to `data/batch_ids.json`, committed immediately so they survive
a lost session -- results stay retrievable from Anthropic for 29 days
independent of this process. All three showed `in_progress` on the
first status check immediately after submission.

**What worked**
Submission itself was clean -- no request-shape errors, matches the pilot's
validated shape exactly (same system prompt, schema, chunking).

**Open questions**
None yet. Next: run `classify_all.py fetch` once all three batches show
`processing_status == "ended"` (typically under an hour, up to 24h per
Anthropic's SLA). `fetch` is safe to re-run -- it reports per-batch status
and only writes the output CSV once all three have ended and the
completeness check passes.

**Time spent**
~5 minutes (submission + status check).

---

## Entry 21 — Phase 5 Step 3: full run complete

**Goal**
Fetch and finalize results from the full 29,159-row classification run
submitted in Entry 20.

**What broke**
All 3 batches ended cleanly (292/292 chunks succeeded, zero errored/
canceled/expired at the batch-API level) -- but `classify_all.py fetch`'s
completeness check refused to write the output file: 419 recall_numbers
missing, 0 unexpected. Root cause, found by comparing each chunk's
`classifications` array length against its input row count: 16 of 292
chunks (~5.5%) had `stop_reason == "end_turn"` but the model had silently
omitted rows from its own JSON output -- not a token-budget truncation (that
would show `stop_reason == "max_tokens"`, the bug fixed in Entry 19), a
different failure mode where structured-output schema validation guarantees
per-item shape but not array completeness. Drop sizes ranged from 1 row (10
chunks) to 99 rows (2 chunks, i.e. the model returned essentially one row
and called it done).

**What I changed**
Did not silently patch or drop the missing rows. Extracted the exact 419
missing `recall_number`s (`data/missing_rows_retry.json`, temporary, not
checked in), and re-submitted them synchronously in smaller 25-row chunks
(`scratch/retry_missing_rows.py`, not checked in) rather than the
production 100-row size, on the theory that a smaller array is less likely
to be dropped from. All 17 retry chunks returned complete
(`25 in / 25 out` x16, `19 in / 19 out` x1) on the first attempt --
confirms the drop rate scales with array size rather than being random
per-row noise. Merged into the batch results and re-ran the completeness
check: **0 missing, 0 unexpected against all 29,159 recall_numbers.**
Documented the failure mode directly in `classify_all.py`'s module
docstring for whoever re-runs this script next -- `cmd_fetch`'s abort-loudly
behavior worked exactly as designed, but there's no automatic retry built
in, so a manual smaller-chunk pass is the documented fallback.

**Result**
`data/recall_categories_llm_full.csv` written: 29,159 rows,
recall_number/category/confidence. Category distribution:

```
Produce                         3890    Nuts/Seeds                  1300
Dairy                           3633    Beverages                    971
Prepared/Frozen                 3388    Plant Protein                782
Bakery                          3317    Food Additives/Ingredients   231
Supplements                     2733    Uncategorized                231
Snacks/Candy                    2383    Baby/Toddler Food            201
Spices/Condiments               2262    Baking Supplies              177
Seafood                         1857    Beef/Pork/Poultry/Game Meats 152
Grains/Cereal                   1374    Eggs                         142
                                         Oils/Fats                    83
                                         Non-Food Item                46
                                         Pet Food/Treats               6
```

`Uncategorized` share: **0.8%** (231/29,159), down from the original
keyword pass's 12.2% (3,554/29,161) -- confirms Q4's relabel-everything
decision from the taxonomy-finalization pass. Confidence distribution:
high 18,788 (64.4%), medium 8,718 (29.9%), low 1,653 (5.7%).

**Open questions**
Step 3b (six validation checks: self-consistency, agreement with the
3,554 reviewed rows, confidence triage, category coherence, keyword-vs-LLM
disagreement, residual inspection) not yet run -- next step per the master
plan, pending Mai's go-ahead.

**Time spent**
~25 minutes: diagnosing the drop pattern, building and running the retry,
verifying completeness, documenting the failure mode.

---

## Entry 22 — Phase 5 Step 3b: six validation checks

**Goal**
Run the master plan's Step 3b validation gate against the full 29,159-row
classification from Entry 21 before Step 4's pipeline refactor: self-
consistency, agreement with the manually-reviewed residual, confidence
triage, category coherence, keyword-vs-LLM disagreement, and residual
inspection.

**What I built**
`scratch/self_consistency_check.py` (not checked in): re-classifies a
1,000-row random sample (seed `20260816`) in a second, independent Batch
API run, reusing `classify_all.py`'s exact request-shaping helpers.
Submitted, polled, and fetched cleanly (0 missing, 0 unexpected against
the sample).

**Results**

1. **Self-consistency** (1,000 rows, second independent pass): **96.1%
   agreement** (961/1,000). All 39 disagreements landed on first-pass
   `medium` (20) or `low` (19) confidence rows -- zero disagreements
   among `high`-confidence rows. Confidence is a real, calibrated signal
   of the accuracy ceiling, not decoration.
2. **Agreement with the 3,554 manually-reviewed rows**
   (`data/recall_categories_llm_classified.csv`, the Phase 3 residual
   pass): **87.7% raw agreement** (3,118/3,554). Of the 436 raw
   disagreements: 41 are taxonomy expansions into labels the old 18-label
   set didn't have (`Eggs`, `Baby/Toddler Food`, `Pet Food/Treats`); 116
   are old-real-category rows the new pass moved to `Uncategorized` (111
   of those at `low` confidence -- hand-reviewed, and they're bare/
   ambiguous descriptions like "Nano Papa," "Placenta," "SOD" that the
   old manual pass over-guessed on, not new-pass errors); 20 are old-
   `Uncategorized` rows the new pass resolved to a real category
   (improvement); 259 are true swaps among shared labels, explained by
   coverage rules added since the old pass (coffee creamer, formula,
   batter mix, cooked-bean dishes).
3. **Confidence triage**: reviewed a 10-per-category stratified sample of
   the 1,643 `low`-confidence rows outside `Uncategorized`, plus the full
   confidence-by-category breakdown. No misclassifications found --
   `low` correctly flags genuinely thin or boundary descriptions. Highest
   `low`-confidence shares match the doc's own Known Gaps section:
   `Baking Supplies` 37.3%, `Food Additives/Ingredients` 26.8%,
   `Beef/Pork/Poultry/Game Meats` 23.7%.
4. **Category coherence**: 15 random descriptions per category, all 21
   categories (315 total), eyeballed. All coherent -- no category
   absorbing junk, no repeat of the keyword-era "clamshell -> Seafood"
   bug class.
5. **Keyword-vs-LLM disagreement**: ran `categories.py`'s
   `assign_category()` against every description and compared to the LLM
   label per category. Lowest agreement -- `Beef` 18.5%, `Pork` 26.1%,
   `Poultry/Eggs` 37.5%, `Grains/Cereal` 39.2% -- lands exactly on the
   failure classes `categories.py`'s own docstring predicted (meat words
   read as flavoring/ingredient, an FDA-vs-USDA jurisdiction artifact,
   not a product signal). Highest agreement: `Supplements` 88.3%,
   `Plant Protein` 83.6%, `Seafood` 80.7%, `Oils/Fats` 78.0%.
6. **Residual inspection**: read all 231 `Uncategorized` rows in full.
   Overwhelmingly bare SKUs/item codes, gift baskets and assortments, and
   unlabeled bulk shipments -- matches the taxonomy's own definition of
   the label. Found one systematic miss: **13 rows** matching the exact
   `"BATTER MIX X1, 50 LBS"`-style bare-code pattern that
   `CLASSIFICATION_RULES.md`'s Grains/Cereal rule explicitly covers by
   worked example (489 rows total match that pattern dataset-wide; only
   these 13, all from the same manufacturer's 2023 filings, were missed).

**What I changed**
Patched the 13 batter-mix/breader rows directly in
`data/recall_categories_llm_full.csv`: `Uncategorized` -> `Grains/Cereal`,
confidence `high` (the rule match is unambiguous). `Uncategorized` share
after the fix: **218/29,159 (0.75%)**, down from 231 (0.79%). Recorded
all six results in `data/fetch_metadata.json`'s new
`llm_classification_pass.step_3b_validation` block.

**Verdict**
All six checks pass. No systemic issues beyond the one fixed. Step 4
(pipeline refactor) is cleared to proceed.

**Time spent**
~55 minutes: submitting and polling the self-consistency batch, six
checks' worth of comparison scripts and manual review, the batter-mix
patch, documentation.

---

## Entry 23 — Phase 5 Step 3b: Mai's manual review of the boundary cases

**Goal**
Surface the genuinely judgment-call rows the six checks turned up (not
pipeline bugs -- real ambiguity a human should decide) and apply Mai's
calls.

**What I found and Mai decided**
- **Donor/mothers'-own human breast milk** (22 rows matching "human milk/
  breast milk/donor milk"): inconsistently split across `Dairy` (13),
  `Baby/Toddler Food` (6, correct), `Uncategorized` (1), and one unrelated
  supplement (turmeric marketed to boost milk supply, correctly excluded).
  Mai: all human milk -> `Baby/Toddler Food` -- it's an infant feeding
  product, not commercial dairy, regardless of the word "milk."
- **Sorbet** (139 rows): split ~90/10 between `Prepared/Frozen` and
  `Dairy`. Mai: sorbet belongs with the water-based frozen novelties
  (Italian ice, popsicles) -> `Prepared/Frozen`, same call the doc already
  made for those. `CLASSIFICATION_RULES.md` had listed "sherbet" under
  Dairy without distinguishing it from sorbet (sherbet has dairy; sorbet
  doesn't) -- a real doc gap, not a model error.
- **"Gravy Beef" (F-0812-2020)** and **"3FT American Substitute Turkey...
  deli service item" (F-0995-2016)**: both already landed correctly
  (`Spices/Condiments` and `Beef/Pork/Poultry/Game Meats` respectively) --
  flagged for review, no change needed.
- **Bare Albertson's deli tray/platter codes** (6 rows, e.g. "PLATTER LOAF
  SLC 20CT," "TRAY CHARCUTERIE ELEGANT," all `Uncategorized`): Mai read
  the named-cut ones as deli meat -> applied to 4 rows (carving,
  charcuterie, Italian sampler, loaf) -> `Beef/Pork/Poultry/Game Meats`.
  For the remaining 2 with no named filling ("SWEET START CATERING TRAY,"
  "TRAY COCKTAIL"), Mai's follow-up call: "Categorized as a prepared
  food" -> `Prepared/Frozen`, not `Uncategorized` -- a composite
  assortment with unnamed contents still deserves a real label.

**What I changed**
29 rows patched directly in `data/recall_categories_llm_full.csv`
(confidence set to `high` -- human-confirmed, no longer a model guess): 14
human milk, 9 sorbet, 6 deli trays (4 to the meat label, 2 to
`Prepared/Frozen`). `Uncategorized` share: 218 -> **211 (0.72%)**.

`CLASSIFICATION_RULES.md` updated (v3 in Revision history) to close the
two real gaps for any future re-run: `Baby/Toddler Food` rule now names
human/donor breast milk explicitly; `Dairy`'s sherbet/gelato line now
distinguishes sorbet as water-based and points to `Prepared/Frozen`; a
new boundary-rule row covers bare deli tray/platter descriptions (named
cut/style -> the meat label, unnamed contents -> `Prepared/Frozen`).
`fetch_metadata.json`'s `llm_classification_pass` block updated with the
corrected confidence distribution and `manual_review_corrections`
sub-block.

**Time spent**
~20 minutes: pulling every row matching each pattern, applying Mai's
calls (including a follow-up correction on the deli-tray split), updating
the rules doc and metadata.

---

## Entry 24 — Phase 5 Step 4: derived dataset and pipeline refactor

**Goal**
With Step 3b's validation gate cleared (211/29,159 Uncategorized, 0.72%),
join the raw snapshot with the final classification into a derived file
and point the app at it, retiring `assign_category` from the runtime
path.

**What I built**
`build_classified_dataset.py` (repo root): reads `data/food_recalls.csv`
and `data/recall_categories_llm_full.csv`, left-joins on `recall_number`,
writes `data/food_recalls_classified.csv` -- the 19 raw columns in their
original order plus `llm_category`. `confidence` is deliberately left
behind in the classification CSV; it's a review artifact, not something
the app reads. 29,161 rows written; 2 without an `llm_category` -- the
same two blank-`recall_number` rows `load_recalls()` already excludes
(event_ids 99068, 99205), so they're inert.

`recall_explorer/pipeline.py` refactored: `DATA_PATH` now points at
`data/food_recalls_classified.csv`; the `categories.py` import and
`apply_llm_category_override` are gone. Category assignment is now a
direct read:

```python
df["category"] = df["llm_category"].fillna("").str.strip()
df.loc[df["category"] == "", "category"] = UNCATEGORIZED
```

`categories.py` itself is untouched -- stays in the repo, frozen, its 31
tests still passing, as historical documentation of the keyword rules'
five failure classes.

Added a comment to `fetch_data.py`: it rebuilds the raw snapshot only,
and `build_classified_dataset.py` must be re-run afterward.

**What worked**
`grep assign_category recall_explorer/pipeline.py` returns nothing.
`data/food_recalls.csv` stayed byte-identical throughout (`git status`
clean on it before and after). `.venv/bin/pytest --continue-on-collection-
errors` shows exactly the failures the master plan's Step 5 anticipated
and no others: `test_pipeline.py` fails to import (it still references
the now-deleted `apply_llm_category_override`, which also covers its
uncategorized-share-bound test), and
`test_columns_match_exactly_and_in_order` fails on the appended
`llm_category` column. Both are Step 5's job, not this one's.

**What I changed**
Nothing beyond the plan's three Step 4 deliverables -- no test files
touched, per the plan's explicit instruction to leave the four
anticipated failures for Step 5.

**Time spent**
~15 minutes: writing and running the join script, the pipeline refactor,
the fetch_data.py comment, and verification.

---

## Entry 25 -- Phase 5 Step 5: tests and documentation

**Goal**
Close out the two anticipated post-Step-4 test failures, rewrite the
tests that exercised the retired `apply_llm_category_override`, add a
coverage test for the derived file, and bring the About section's
user-facing claims in line with the Phase 5 reclassification.

**What I built**
`tests/test_pipeline.py`:
- `test_uncategorized_share_stays_within_documented_bounds` retargeted
  from the old keyword-era 8-16% band to 0.3-2%, bracketing the measured
  211/29,159 (0.72%) figure from BUILD_LOG Entry 22-23 / Step 3b.
- The three `apply_llm_category_override` tests (which called a function
  that no longer exists) replaced with three tests against `load_recalls`
  itself, since the category-derivation logic is now inlined rather than
  a standalone pure function: label present -> used; blank -> falls back
  to `Uncategorized`; and a dedicated no-keyword-inference test proving a
  blank `llm_category` on a row with an obviously keyword-matchable
  description ("Whole milk, 1 gallon") still lands on `Uncategorized`
  rather than `Dairy`. All three build a synthetic 29,000-row CSV via a
  `_make_classified_csv` helper so `validate_schema()`'s row-count floor
  doesn't block testing the two-line derivation in isolation.
- New `test_classified_csv_has_llm_category_for_essentially_every_row`
  asserts <0.1% of rows in the real derived file are missing
  `llm_category` (measured: 2/29,161, the same two blank-`recall_number`
  rows `load_recalls()` already excludes).

`tests/test_schema_guardrail.py`: `test_columns_match_exactly_and_in_order`
now asserts an ordered prefix (`list(raw.columns)[:len(EXPECTED_COLUMNS)]
== EXPECTED_COLUMNS`) instead of exact equality, so the derived file's
appended `llm_category` column no longer trips it, while a fresh
`fetch_data.py` run (no `llm_category` at all) still passes.

`tests/test_llm_categories.py`'s doc<->code sync test
(`test_category_enum_matches_classification_rules_doc`) and the deleted
`categories.py`-derived-enum import were already done as part of Step 1 --
verified them still passing rather than re-doing the work.

`data/fetch_metadata.json`'s `llm_classification_pass` block was already
complete from Step 3b (timestamp, model, row count, taxonomy, before/after
Uncategorized share, confidence distribution, all six Step 3b figures, and
the Batch-API-supersedes-manual-round-trip note) -- nothing to add.

`app.py`'s About section (~line 245): rewrote the two stale bullets. The
meat bullet now scopes the FDA/USDA jurisdiction gap to meat and poultry
specifically and notes shell eggs are FDA-regulated and have their own
`Eggs` category (142 rows). The keyword/coverage bullet now states the
LLM classification pass (Claude Opus 5, full 29,159-row dataset), the
0.72% Uncategorized share, and the 96.1% self-consistency accuracy signal,
pointing to `CLASSIFICATION_RULES.md` and `BUILD_LOG.md` for the full
validation record.

**What worked**
TDD on the two test-only retargets (uncategorized share, schema prefix)
and the `load_recalls`-based rewrites: watched each fail for the expected
reason under the pre-Step-4 code shape, then confirmed green.
`.venv/bin/pytest` fully green, no `--continue-on-collection-errors`
needed. `categories.py`'s 31 tests untouched and passing.
`load_recalls()["category"].value_counts()` shows exactly the 21
approved-taxonomy categories, `Uncategorized` at 211 rows, no leftover
keyword-era labels. `grep assign_category recall_explorer/pipeline.py`
still empty.

**What broke**
Nothing outside the two anticipated failures, both closed as planned.

**What I changed**
Nothing beyond the plan's Step 5 scope. `app.py` had substantial unrelated
pre-existing uncommitted work (Phase 3/4 filters, insights, styling); only
the About-section hunk was staged for this commit.

**Open questions**
None -- Step 5's verification checklist (pytest green, `categories.py`
untouched, category value_counts sane) is fully satisfied. Step 6 (live QA)
is next.

**Time spent**
~30 minutes: test rewrites, About section, verification, logging.

---

## Entry 26 — Phase 5 Step 6: live QA against the reclassified distribution

**Goal**
Run the plan's Step 6 QA checklist live against `streamlit run app.py` --
filter matrix, lens sync, full date range, error UI, cold start, and the
named edge cases -- and fix any real gap found, TDD-first.

**What I built**
No browser-automation tool (Playwright MCP/`chromium-cli`) was available
in this session, so I drove the running app with `playwright`'s
Python sync API directly (already installed in `.venv`) via one-off
scripts in the scratchpad, screenshotting each state and cross-checking
every "Total recall events" figure against `apply_filters(df,
...)["event_id"].nunique()` computed independently in a plain Python
shell -- the same ground truth the UI is supposed to reflect.

Checked live: Category/Reason/Severity alone and combined (including a
4-dimension small-but-nonzero case, Seafood + 2018-2020 + Listeria + Class
I = 22 events); both lenses (event/product) in sync at every filter state
via the Seasonality and Top-recalled-foods panels; the full 2012-2026
range with the trend chart's dashed partial-2026 segment; 2012 alone (515
events); 2026 alone (231 events, partial); `Dairy` + `Botulism risk` +
`Class III` -- still zero-results post-reclassification, confirmed by
direct query rather than assumed; a fresh zero-result combination other
than that one (`Pet Food/Treats` + `Salmonella` = 0); clearing all filters
back to the full 7,789-event baseline; `Uncategorized` + `Other` reason
selected explicitly (16 events, renders normally, no residual-bucket
special-casing needed); all 21 approved-taxonomy categories present with
sane counts in both lenses' bar charts, including `Eggs` (64 events / 142
rows), `Beef/Pork/Poultry/Game Meats` (56 events / 156 rows), and
`Pet Food/Treats` (4 events / 6 rows). Cold start measured at 4.0s
(process start to Key Insights data visible in the browser) against the
PRD's 5-second target.

Every one of the 13 checked filter states matched its independently
computed expected event count exactly -- no discrepancies found in the
filter/lens/derivation logic itself.

**What worked**
Cross-checking the UI against an independently computed ground truth
(rather than eyeballing numbers) caught the one real gap below with
certainty rather than suspicion. Screenshots at generous viewport heights
(`full_page=True` with a tall viewport) avoided the scroll-position
flakiness of driving a real scroll.

**What broke**
The error-UI path (`mv data/food_recalls_classified.csv{,.bak}`, restart
the server since `@st.cache_data` memoizes `get_data()` per-process and
would otherwise mask a missing file on a live process) rendered
`st.error()` + `st.stop()` correctly, but the message itself was stale:
"Run `python fetch_data.py` to build it." `DATA_PATH` has pointed at the
Phase 5 derived file since Step 4 -- built by `fetch_data.py` *and then*
`build_classified_dataset.py` (see `pipeline.py`'s own module docstring).
A user hitting this error and following its instructions would run
`fetch_data.py`, watch it succeed, and land on the exact same error again,
because the derived file `load_recalls()` actually reads still wouldn't
exist. `tests/test_schema_guardrail.py::test_snapshot_file_exists` carried
the identical stale message in its own assertion.

**What I changed**
TDD: added `test_missing_snapshot_error_names_build_classified_dataset` to
`tests/test_pipeline.py`, watched it fail with the old message, then
updated both `pipeline.py`'s raised `ValueError` and
`test_schema_guardrail.py`'s `test_snapshot_file_exists` assertion message
to name both scripts in order. Restored `food_recalls_classified.csv` and
restarted the server to confirm the app returns to normal before leaving
it running.

**Open questions**
None. All Step 6 checklist items completed live; the one real gap found
has a regression test and a fix; `.venv/bin/pytest` fully green; the app
is left running on `localhost:8501`.

**Time spent**
~1.5 hours: driver scripts, ground-truth cross-checks, screenshots, the
error-UI gap's TDD cycle, logging.

---

## Entry 27 — Post-Phase-5: "Reset filters" button

**Goal**
Mai noticed the QA pass never surfaced a missing "reset all filters"
button -- checked the PRD and every project doc and confirmed it was
never a stated requirement, then added it on request, TDD-first, with
placement as a judgment call.

**What I built**
Added explicit `key=` params to the four filter widgets
(`year_range`, `category_filter`, `reason_filter`, `severity_filter`) so
their state is addressable, plus a `_reset_filters()` callback that
writes each key's default back into `st.session_state` and a
`st.button("Reset filters", on_click=_reset_filters, key=
"reset_filters_button")` placed on its own row directly below the four
filter columns -- visible immediately where the user just made changes,
without crowding the already-narrow multiselect columns.

Introduced `tests/test_app.py`, this project's first UI-level test, using
Streamlit's headless `AppTest` harness (`streamlit.testing.v1`, bundled
since 1.x, no browser needed) against the real derived CSV: one test
asserts the button exists, the other selects a category/reason/severity
and narrows the year slider, confirms the metric changed, clicks the
button, and asserts every widget and the Key Insights total return
exactly to their defaults. Watched both fail red (no button, then
`FileNotFoundError` on the relative script path) before making them pass.

**What worked**
TDD caught a real mechanical detail immediately: Streamlit only lets a
callback overwrite a widget's value via `st.session_state[key]` if that
widget has an explicit `key=` -- the pre-existing widgets didn't, so the
first test failure after adding the button was `StreamlitAPIException`
until the four `key=` params were added. `AppTest` proved the reset
behavior headlessly in under a second per run; a live Playwright pass
against the running app afterward confirmed the same behavior pixel-for-
pixel (select Eggs -> 64 events, click Reset filters -> back to 7,789).

**What broke**
Staging hit a real snag: the new code lives inside `app.py`'s Filters
section, which -- it turned out on inspection -- was never actually
committed. `git show HEAD:app.py` is still the 114-line Phase 2 stub with
"Coming in Phase 3" placeholders; the 289-line version with Filters/Key
Insights/Trend/Top-foods has been sitting uncommitted in the working tree
since before this session (per the standing instruction about app.py's
pre-existing uncommitted work). Unlike Step 5's About-section edit, which
could be isolated with `git apply --cached` because that block's context
already existed in HEAD, there was no committed anchor here to patch
against. Asked Mai directly rather than guess; she chose to commit all of
app.py now rather than continue leaving it uncommitted.

**What I changed**
`app.py`, `tests/test_app.py` (new). Committed the entire current
`app.py` -- the reset button along with the rest of the not-previously-
committed Phase 3/4 work it lives inside.

**Open questions**
None.

**Time spent**
~25 minutes: TDD cycle, live verification, the staging question, logging.

---
