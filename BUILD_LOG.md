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
