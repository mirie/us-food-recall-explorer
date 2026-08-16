# US Food Recall Explorer — Project Submission

**Course:** Maven, "Mastering Agentic AI" — Homework 1
**Author:** Mai Irie

*This document is a synthesis of `BUILD_LOG.md` (27 chronological entries), `PROMPT_LOG.md`, `LEARNINGS.md`, the PRD, and `CLASSIFICATION_RULES.md`. It is a working draft for review before anything is pasted into the final Google Doc.*

---

## 1. Project Overview

**US Food Recall Explorer** is a Streamlit dashboard that lets users explore US food recalls (2012–present) using openFDA's Food Enforcement data. It answers three core questions:

1. **Seasonality** — is there a monthly/seasonal pattern to recalls?
2. **Top recalled foods** — which food categories are recalled most often?
3. **Trend over time** — is recall volume/severity rising, falling, cyclical, or flat?

The project's origin was a "myth vs. reality" framing exercise during brainstorming — testing candidate topics like NYC-to-suburbs migration, common colds vs. winter, and rent-vs-buy economics before landing on food recalls, prompted by a real news hook (recent lettuce and jalapeño recalls). The final concept kept the same instinct — take a claim people casually believe and check it against real data — while grounding it in a single well-documented public dataset.

**Design philosophy.** A defining decision, locked early and never reopened: recalls can be counted two different ways — **per incident (event)** or **per individual recalled product** — and these produce meaningfully different pictures (roughly a 3.74x ratio of products to events). Rather than picking one lens or hiding the choice behind a toggle, the app shows **both lenses permanently, side by side**, on every relevant chart. The reasoning: a toggle asks the user to remember which mode they're in; two panels shown at once make the comparison immediate and the "hidden state" problem disappear entirely. This is treated as a locked design decision throughout the build — considered and reconfirmed multiple times, never walked back.

Other locked decisions carried through from planning to submission: chart type is chosen per data shape rather than defaulted to bars (heatmap for seasonality, line chart for trend, horizontal bar for top foods); a single collapsible "About the data & limitations" section instead of scattered footnotes; and a hard rule that a top-of-page "Key Insights" row of four computed stat cards is **always rule-based, never LLM-generated, and never causal or evaluative** ("recalls up 37% since 2014" is fine; "food safety is getting worse" is not).

The app deliberately makes **no causal claims** — rising or falling recall counts may reflect changes in detection and reporting practice as much as changes in actual food safety, and the dashboard says so explicitly rather than letting a chart imply otherwise.

---

## 2. Datasets Used

### Source

**openFDA Food Enforcement API** — a public, no-PII government dataset of FDA-regulated food recalls. The app pulls the data **once**, via a standalone script (`fetch_data.py`), into a static CSV snapshot; the running Streamlit app never calls the API itself and makes no network requests at runtime.

**Snapshot size:** 29,161 rows / 7,791 recall events (later reduced to 29,159 rows / 7,789 events after excluding two rows with a data-quality problem — see below).

### What's actually in it (and what corrected early assumptions)

The PRD originally assumed the dataset covered **2004–present**. A direct API call during Phase 0 refuted this: the dataset effectively starts in **2012** (zero records before 2012 by `report_date`; only ~97 scattered stragglers by `recall_initiation_date`). This wrong assumption had already propagated into the PRD's TL;DR, the wireframe's x-axis, and the build kickoff prompt before anyone had actually queried the API — a pattern discussed further in Section 4.

Key fields used:
- **`recall_initiation_date`** — the canonical date field for seasonality and trend analysis (chosen over `report_date`, which reflects FDA's weekly publication lag and would smear real seasonal peaks by weeks).
- **`product_description`** — free-text product name, used to derive food category.
- **`reason_for_recall`** — free-text contamination/recall reason, used to derive multi-label contamination tags (Salmonella, Listeria, undeclared allergen, etc.).
- **`classification`** — a clean categorical field with exactly three values: Class I (12,804), Class II (14,616), Class III (1,741). No derivation needed.
- **`recall_number`** / `event_id` — used to distinguish event-level from product-level counting.

**What's absent:** no country-of-origin field. `country`/`state`/`city` record the *recalling firm's* address (98.9% United States), not where the food was grown or produced — this makes a "growing season vs. imports" analysis genuinely impossible with this dataset, not merely deferred.

**A scope boundary, not a data gap:** the dataset contains **no meat, poultry, or processed egg recalls** in any meaningful volume, because those are regulated by USDA FSIS, an entirely separate recall system this dataset doesn't touch. Meat-related keywords in this corpus are almost always flavorings or ingredients inside FDA-regulated processed foods (`Natural Beef Flavor`, `Bacon Brittle`). This had to be stated explicitly in the app's "About the data" section so a near-empty meat category doesn't read as "meat is rarely recalled."

**A known data-quality issue:** two rows share a blank `recall_number` (a pre-existing openFDA gap, not introduced by this project). Per Mai's decision, these are excluded from the dataset entirely at load time rather than patched or worked around, since `recall_number` is the key the whole app relies on.

### Category and reason taxonomy derivation

Two fields the PRD originally assumed were clean categorical filters (`product_description` for food category, `reason_for_recall` for contamination reason) turned out to be **free prose**, and category was worse than expected: naive keyword matching left 13.5% of rows matching no category and 41.5% matching two or more (a "Blue Bell coconut fudge" is legitimately Dairy, Snacks, and Nuts at once).

The taxonomy went through two distinct phases:

**Phase 1 — keyword rules (frozen mid-build).** Priority-ordered regex rules, first match wins, with a visible `Uncategorized` bucket rather than silently dropping unmatched rows. Over several iterations this reached 17 categories and got `Uncategorized` down to 11.9%. But five distinct *failure classes* were found along the way (see Section 4), and the decision was made to **freeze the rules rather than keep patching them reactively** — the architecture (`pipeline.py` sets `df["category"]` in one line) made this cheap, since nothing downstream cared where the category column came from.

**Phase 2 — LLM-assisted full reclassification.** A one-time, offline classification pass using Claude Opus 5 against a finalized 21-label taxonomy (`CLASSIFICATION_RULES.md`), run via the Anthropic Batch API over all 29,159 rows. This is explicitly **not** a violation of the "never LLM-generated" rule for Key Insights — that rule governs claims *about* the data; this is a one-time preprocessing step whose output is frozen, inspectable, and committed to the repo, with no runtime API calls. Final result: `Uncategorized` dropped from 12.2% (keyword era) to 0.72% (211 rows), validated through six separate checks (self-consistency re-run, agreement with a manually-reviewed subset, confidence triage, category coherence sampling, keyword-vs-LLM disagreement analysis, and full manual reading of the residual). Category assignment now derives directly from a `llm_category` column with no keyword fallback.

### Known limitations (from `CLASSIFICATION_RULES.md` and the build record)

- **Coverage is not accuracy.** The keyword-era `Uncategorized` percentage measured how many rows got *a* label, not how many got the *right* one — a documented bug (509 rows of cheesecake and salad, a fifth of the entire Seafood category, misfiled because "clamshell" packaging language was read as a food keyword) lived entirely inside the "successfully categorized" share and was invisible to that metric.
- **Raw single-ingredient meat cuts are largely untested** — FDA recall data underrepresents raw primal cuts (USDA jurisdiction), so the merged meat category is validated mainly against deli meat, cured meat, and cooked cuts.
- **`Baking Supplies` and `Food Additives/Ingredients`** have the thinnest direct evidence in the taxonomy — inferred from adjacent rows rather than a dedicated sample.
- **The reclassification is a clean break, not a mapping** — old keyword labels weren't forward-mapped to the new taxonomy, since the same keyword produced both correct and incorrect legacy labels depending on context (e.g. "Beef" correctly resolving to Bakery for bun-named rows and to Beef for actual beef rows). The legacy label is retained separately for diff-based QA only.
- **Detection/reporting confound** — rising or falling recall counts may reflect changes in testing and reporting practice, not changes in the underlying safety of the food supply. Stated as a standing caveat, not an incidental note.
- **2026 is a partial year** — the snapshot's last actual recall date is 2026-07-08, roughly four weeks before openFDA's own "last updated" metadata timestamp. Trend charts render the partial year as an explicit dashed segment rather than letting it read as a phantom 56% drop.

---

## 3. Prompts Used During Vibe Coding

A curated selection spanning planning through build. Full log in `PROMPT_LOG.md`.

**Planning phase**

> *"I created an account on ChatPRD so I could capture this into a proper product requirements docs with clearer specs — can you review, catch any drift from our discussion above, and also update the prompt as needed?"*
Caught ChatPRD quietly softening the event/product lens from an interactive v1 feature into a deferred "nice-to-have," and the one-time CSV fetch into ambiguous "per session" language.

> *"'Geographic/state-level or consumption-specific mapping is excluded from v1, due to data limitations.' — wait this is a conclusion that is not clear yet. I haven't explored the data. I just noted that potentially it's messy..."*
Caught the AI tool phrasing an untested hunch as a confirmed finding — a recurring pattern across the whole planning phase.

> *"Can you note that they shouldn't always be bar charts? Something is off about this image above. honestly the chatgpt design direction... seems to feel the best in capturing the experience. Maybe let's just use that for the PRD?"*
Caught a generated wireframe defaulting every chart type to bars, including seasonality (which should be a heatmap), and reconciled two parallel design explorations (Claude Design's structural wireframes vs. ChatGPT's insight-led concept) into the final side-by-side-lens, chart-type-per-shape direction.

> *"'This is the source of truth for layout, spacing, and chart types' — This isn't perfectly designed. So I don't want to build exactly to spec. This is a low-fi design. We will iterate with real data."*
Corrected the build kickoff prompt itself before sending it — reframing the wireframe PDF from a pixel-perfect spec to a directional reference, immediately after noticing the same overstated-authority pattern in the artifact meant to prevent exactly that.

**Build phase kickoff**

> *"...First step — Phase 0: pull a sample from the openFDA API, explicitly check the two unverified assumptions flagged in the PRD (food category and contamination reason — clean fields or free text?). Log findings in BUILD_LOG.md before touching Phase 1."*
The single most load-bearing instruction in the project — "dry-run before real runs, `--limit 1` on first real writes" directly caught a real pagination bug, and "check assumptions before building" caught the 2004→2012 date error before it reached a chart.

> *"I think I failed to mention earlier that I'd like to take a test-driven approach as part of implementation... use small, hand-built DataFrames/dicts as input fixtures — do not read the real file in these tests... Explicitly Skip: no integration tests... no malformed/adversarial input handling..."*
The most consequential build-phase prompt — the explicit skip list (what *not* to test) did as much work as the requirements, keeping the unit suite at ~0.02s and making strict TDD practical rather than theoretical.

**Mid-build corrections and challenges**

> *"I disagree with a line I see in the handoff_phase2.md doc: '"ice cream sandwich" → Bakery' — I don't think an ice cream sandwich is a bakery item. I see this restated in categories.py as well... I disagree. It's mostly dairy."*
The single highest-value prompt of the build. It surfaced a fabricated, never-executed documentation example, a systematic classification bug affecting 1,393 rows, and a second bug (packaging language misread as food vocabulary) affecting 509 more.

> *"I'm starting to think we will actually need to walk back 'LLM-assisted category labelling' — would it be helpful to add this to scope to reduce the brittleness of regex?"*
Led directly to the decision to freeze the keyword rules and defer to an LLM pass.

> *"...does this mean this data was never sent to LLM for classification?"*
The moment that reframed the entire Phase 5 session — revealed that the manual LLM classification round trip had covered only 3,554 of 29,161 rows (12.2%), not the full dataset as intended, triggering a full replan around the Batch API.

> *"Okay what does that mean? Does that mean I need to set an API key etc? Is there a way to do this over multiple sessions even if I hit a session limit?"*
Led to splitting `classify_all.py` into independent `submit`/`fetch` commands, making the long-running batch job resumable across sessions.

> *"okay just help me sort thru something real quick. Does plant-based coffee creamer have plant protein in it? I made an assumption but I actually might be totally wrong"*
Caught a factual error in the finalized taxonomy before it shipped — plant-based coffee creamer is compositionally closer to an oil/thickener product than to protein-bearing plant milk, so it was moved back to `Beverages`.

> *"wait a minute... these are not correct categories. How should I read this output?"*
Caught roughly 20 of the author's own 58 "known-answer" validation probes as themselves mislabeled, before they could be used to validate the real classification run.

**Phase 5 taxonomy revision rounds**

> *"Do we truly have egg products in the original dataset?"*
The right instinct to push rather than accept a claim at face value — a `Poultry/Eggs` category assumed to be a near-empty jurisdictional artifact turned out to contain roughly 50 genuine shell-egg recalls, including two of the largest recall events in the entire 2012–2026 dataset (Rose Acre Farms salmonella, Almark Foods listeria).

> *"Okay I think I'm getting confused here. So let's review this plan for the iteration with llm classification. Order of operations: (1) ... (2) ... (3) now we are in the final integration stage of reconciling the updated classifications with the application. Can you review this plan and see where we are aligned and misaligned?"*
The pivotal self-correction prompt of the whole reclassification arc — surfaced that a stage-1 data-quality question (meat-category restructuring) had ballooned into three rounds of debate that didn't belong in what was supposed to be stage-3 integration work, and reset the session to the minimal correct move.

> *"Is there a way to do this without an api key and a separate charge?"*
A direct cost-consciousness check partway through replanning the full reclassification — led to comparing all three real routes (Batch API, in-session chunking, chunked Claude.ai chat) with honest wall-clock estimates for each, rather than defaulting to the option already in motion.

> *"Can you verify the whole plan to make sure it accurately reflects the approach discussed?"*
A single request that surfaced twelve real drift points accumulated across several rounds of plan revision — a stale "no credentials" section, an unmeasured cost figure presented as firm, an unsupported prediction, overloaded terminology, a duplicate checklist item, among others. All twelve were fixed rather than defended.

> *"okay just help me sort thru something real quick. Does plant-based coffee creamer have plant protein in it? I made an assumption but I actually might be totally wrong... I think if a protein powder has plant protein in it, it should be in Plant protein and not in supplements. Should plant milks go into plant protein too?"*
Four separate taxonomy questions that turned out to be one underlying correction — classify by composition, not by where a product is consumed or grouped by exclusion — applied consistently across plant milk, plant-based protein powder, pet food, and (in a same-day follow-up) coffee creamer specifically.

> *"Should I manually review any particular rows?" → (five clusters surfaced) → "F-2113-2014 'Raspberry Sorbet': should be in the same category as italian ice, popsicles" / "Categorized as a prepared food"*
The closing round of the classification effort — genuinely ambiguous judgment-call clusters (donor breast milk, sorbet, unnamed deli trays) that the six automated validation checks correctly flagged as uncertain rather than silently resolving, settled in a few words each once put to a human. Dropped `Uncategorized` from 231 to 211 rows (0.72%) across two follow-up commits.

---

## 4. Iterations Tried

This section is the heart of the record — the actual arc of drift, correction, and revision, not a cleaned-up summary.

### Planning phase: catching drift before it became code

The planning phase established a pattern that recurred throughout the project: **AI-generated artifacts tend to quietly overstate their own authority**, and the fix is always the same — re-read them against the original intent rather than trusting them at face value. ChatPRD demoted a locked feature to "deferred" and softened a hard technical constraint into ambiguous language; a generated wireframe defaulted every chart to bars including a seasonality view that needed a heatmap; the kickoff prompt itself initially called a low-fidelity wireframe a "source of truth." Each was caught by review, not by luck.

Two design questions surfaced independently in two different tools (Claude Design's structural wireframes, ChatGPT's insight-led concept) and resolved the same way both times — convergent evidence for side-by-side lenses over a toggle, treated as stronger confirmation than either tool alone would have provided.

### Phase 0: two data assumptions reversed, one reversal itself reversed

Phase 0 (one-time data fetch) was framed around two explicit `⚠️ UNVERIFIED` flags carried over from planning — was food category cleanly derivable, and was contamination reason a clean field? Both were refuted by direct API calls: category derivation left 13.5% unmatched and 41.5% ambiguous; reason was free prose. Because both had been explicitly flagged as unverified, refuting them cost nothing — no downstream work depended on them yet.

The far more expensive error was the one that had **not** been flagged: the PRD's "2004–present" date range. It had propagated, unchallenged, through the PRD's TL;DR, a two-page wireframe's x-axis, and the kickoff prompt itself — until a direct API call showed the dataset actually starts in 2012. As `LEARNINGS.md` puts it: *"Review catches what a document says. It does not catch what a document assumes."*

A third, rarer kind of correction also happened in Phase 0: an initial sample-based measurement (products per event ≈ 1.4) was used to flag the wireframe's 3.8x ratio as unrealistic — and that correction was itself wrong. The true full-dataset figure is 3.74; the sample was a contiguous 1,000-row API slice that split multi-product events across page boundaries and systematically undercounted. This is the one entry in the whole build where a *measurement*, not an AI-authored artifact, overstated its own confidence.

Phase 0 also caught a smoke-test bug that would otherwise have shipped invisibly: `--limit 1` was fetching 1,000 rows because the page-size cap was checked but never applied to the actual request — caught exactly where the dry-run → `--limit 1` → full-run discipline was designed to catch it.

### The category-classification failure classes, and the decision to freeze

Category classification went through five distinct, unrelated failure classes over the course of Phase 1 and its follow-up entries:

1. **Ingredient-vs-product-type confusion** — a chocolate chip cookie matching Dairy, Bakery, and Snacks simultaneously because `milk`/`butter`/`cream` are ingredient words, not product-type signals.
2. **Meat-as-ingredient, reproduced after being diagnosed** — meat categories were initially ranked in the top tier on the reasoning that "beef names a product," which is false in this dataset specifically because FDA does not regulate meat/poultry/processed eggs (USDA FSIS does). This was the *same* error already fixed for Dairy, reproduced one tier up in the same commit — "a stated rule doesn't automatically apply itself to the next case."
3. **Regex substring bugs** — `\bpie\b` didn't match "pies"; bare `apple` matched inside "pineapple." Both silently misfiled rows with no error ever thrown.
4. **Phrase-identity shattering** — the ladder ranked single words, which worked for single-word product identities but failed for phrases: "strawberry yogurt" hit the Produce rule's `berr` stem before Dairy was ever reached; 605 "peanut butter" rows were dragged toward Dairy by the word "butter." Measuring the actual scope found 1,393 rows mentioning "ice cream" scattered across nine categories, only 35% correctly in Dairy.
5. **Packaging vocabulary read as food vocabulary** — 509 rows (a fifth of the entire Seafood category) were cheesecakes and salads sold in plastic **clamshells**, misfiled because "clamshell" matched a Seafood keyword.

Each fix was cheap. The real problem, stated directly in the build log, was that **no process was generating these findings** — four of the five were found by someone happening to look at the right rows, and two of those four by Mai rather than by the author. That is not a repeatable process, and it's the direct reason the team decided to **freeze the keyword rules** rather than keep patching reactively, deferring further accuracy work to a planned LLM-assisted pass. The architecture made this cheap: category assignment lived behind one line in `pipeline.py`, so nothing downstream needed to change when the source of that column changed later.

A related, uncomfortable finding: a specific illustrative example ("ice cream sandwich resolves to Bakery") had been written into a module docstring, the PRD, a handoff document, and two build-log entries — and it was **fabricated**. It had never actually been run. It resolved to `Prepared/Frozen`, and the classification itself was wrong regardless (an ice cream sandwich is a dairy product). Worse, it had been labeled an "accepted tradeoff," dressing a fabrication up as a considered decision. This surfaced only because Mai directly challenged the claim.

### Design decisions revisited mid-build

Several UI decisions that looked settled were reopened once real numbers or a live screenshot were available:

- **Key Insights card format.** The PRD's own example was a full sentence ("Recall events up 37% since 2014"), but the initial build rendered bare numeric `st.metric()` cards. Once Mai reviewed screenshots, this was corrected to full-sentence card values — a real, previously-unlocked gap in the handoff, not a mistake.
- **Zero-state wording.** Filters producing no results initially showed a bare "—" dash. Reworded to "No conclusions" after Mai's manual QA flagged it as reading as broken rather than intentional.
- **Severity-trend filtering bug.** Filtering the trend chart to a single severity class (e.g. Class I) initially still showed the other two classes as flat lines pinned at zero, rather than disappearing — caught by Mai's manual QA against the live app, not by any automated check, and traced to the transform's correct-for-unfiltered-view "always show all three classes" contract colliding with filtered data.
- **The partial-2026 framing itself.** Initially treated as a data gap needing a dashed-segment caption on *every* chart, including the seasonality heatmap — corrected once Mai pointed out that a year running only through July, when today's date is August 14, is just the calendar, not missing data. Reserved the dashed-segment treatment specifically for the trend-over-time line chart, where a raw year-over-year comparison really would misread the partial total as a 56% drop.
- **An overstated finding, walked back.** The wireframe's top-recalled-foods chart was initially recorded as "not achievable" because its placeholder labels showed Poultry #1 — a real design conclusion drawn from a real fact (the FDA/USDA jurisdiction boundary) but overstated. On direct challenge ("Does this apply to top-foods generally or are you just fixating on a fake data point?"), the claim was withdrawn: the chart's *structure* works exactly as drawn; only its illustrative labels differed from real data, which is expected of a low-fidelity mock.

### The LLM classification scope error, and its correction

The most significant iteration of the project. The original plan (Phase 5) called for an LLM-assisted classification pass to resolve the keyword rules' `Uncategorized` residual. Because Mai was working from a mobile device via Remote Control with no terminal access, this was implemented as a **manual round trip**: exporting the Uncategorized rows to a separate Claude.ai chat, having Mai run the classification there, and pasting the results back for merging.

That round trip itself took three delivery attempts to work (`SendUserFile` reporting success but files not being openable on mobile; an Artifact's download button hitting an iOS Safari restriction; copy-to-clipboard buttons finally working) — a recurring theme discussed further in Section 5.

But the deeper problem surfaced only once merge work began: `export_for_classification()` filtered to `category == "Uncategorized"` — meaning the manual pass had classified **3,554 rows, 12.2% of the dataset**, not the full 29,161 rows Mai had actually intended. It filled in the keyword rules' blanks; it never reviewed a single one of the 25,607 rows the keyword rules had already (possibly wrongly) labeled. This was caught from two directions at once — independently reproduced here, and confirmed by the classifying session itself, which had noticed (but misread) its own tell: zero eggs, zero oils/fats, and one poultry row in its slice, which it reported as a fact about the dataset rather than the fingerprint of a pre-filtered file.

The correction required rebuilding the whole classification approach: since Mai now had terminal access, the project reverted to the PRD's original design — a standalone script hitting the Anthropic Batch API directly, covering all 29,159 rows, built around a finalized 21-label taxonomy (recovered from a decision log from the earlier manual pass, cross-checked against independently-found evidence, and revised through several rounds of Mai's own corrections — most notably reclassifying protein powders, plant milk, pet food, and coffee creamer by composition rather than by where they're consumed or grouped by exclusion).

The full pipeline that followed: a taxonomy-finalization API call against a 5,000-row design sample → four rounds of Mai's taxonomy corrections → `CLASSIFICATION_RULES.md` written as the authoritative spec → `classify_all.py` built (Batch API, structured JSON-schema outputs, resumable submit/fetch commands) → a 255-row pilot run at three effort levels (during which roughly 20 of the author's own 58 hand-built "known-answer" probes turned out to be mislabeled, caught by Mai's pushback) → full 29,159-row run submitted and fetched (hitting and fixing a silent row-drop bug affecting 419 rows across 16 of 292 chunks — the model was completing normally but silently omitting rows from its own structured output array) → six independent validation checks → Mai's manual review of five genuinely judgment-call clusters (donor breast milk, sorbet, ambiguous deli-tray descriptions) → a pipeline refactor retiring the keyword-based fallback entirely in favor of a direct read of the LLM-derived category column.

Final result: `Uncategorized` dropped from 12.2% (keyword era, partial coverage) to 0.72% (211/29,159, full-dataset coverage), with a 96.1% self-consistency rate on an independent re-classification of 1,000 rows.

### The manual-round-trip approach itself: an ineffective detour, not just a delivery problem

The LLM classification scope error above didn't happen in isolation — it was downstream of a design choice (the manual Claude.ai round trip) made under a real constraint (Mai on mobile via Remote Control, no terminal access) that turned out to cost far more than it saved, on two separate fronts:

- **The delivery mechanism itself failed three times before working.** Getting the export file and prompt text *to* Mai, and getting her classification results *back*, took three attempts: `SendUserFile` reported success but the files weren't openable on her mobile client; a published Artifact's built-in download button hit what looks like an iOS Safari restriction on programmatic downloads outside a direct user-gesture chain; a self-contained HTML page with copy-to-clipboard buttons was what finally worked, on both legs of the round trip (Entries 9, 10.5). None of these failures were caught early — each one reported success on this side while failing silently on Mai's end, so the gap was only visible once she said directly that she couldn't open something.
- **The approach was the wrong one, not just poorly delivered.** Even once delivery worked, the round trip itself was the source of the scope error: `export_for_classification()` silently scoped the export to only the `Uncategorized` rows, and that scoping assumption never got surfaced or confirmed before two full sessions (Entries 10–10.5) were spent building and running a manual chat-based classification pass on the wrong 12% of the data. In hindsight, a chat-pasted round trip was never going to scale to 29,161 rows regardless of the scoping bug — the plan that replaced it (Entry 11's Batch API script) is what the PRD had specified from the start, before the mobile constraint pushed the project toward a workaround.
- **The real cost was a miscommunication that compounded rather than one bad delivery attempt.** The manual round-trip plan (`HANDOFF_PHASE5_LLM_MERGE.md`) was read and approved before it ran, but the scoping assumption inside it (Uncategorized-only, not full-dataset) wasn't caught on that read — it surfaced only two sessions later, once merge work actually began. That gap between "the plan was reviewed" and "the plan's central assumption was actually checked" is what elongated this part of the build the most: not the three failed delivery attempts, which cost minutes each, but the two full sessions spent executing a plan whose scope nobody had verified against what was actually intended.

---

## 5. Learnings & Observations

Synthesized from `LEARNINGS.md`; see that file for the full analysis.

### What worked

- **Deciding before testing, under TDD.** Design questions (category precedence, multi-label vs. single-label reasons) were settled with Mai *before* any test was written. Under TDD, the test is the spec — a guessed answer would have been silently frozen into a passing suite and become invisible as an unexamined assumption, since green tests read as validation rather than as a guess that happened to compile.
- **Concrete previews beat abstract questions, consistently.** An abstract framing ("should the trend line split by severity or stay one line?") got "this is too abstract for me." The same question rebuilt as two small ASCII sketches from real 2016-spike numbers resolved it in one turn, and surfaced a reason to prefer one option that the abstract framing hadn't carried at all. This pattern — a sketch, a wireframe, a real screenshot beats a description of one — held across design questions the author was both asking and answering, and recurred at least four separate times in the build log.
- **Precomputed handoff reference numbers paid for themselves as verification, not just documentation.** When a new session's transform output matched a handoff's precomputed numbers exactly on the first real-data run, that wasn't incidental — it was the check working as designed.
- **An explicit skip list did as much work as the requirements list.** Ruling out adversarial-input handling, retry-logic tests, and rendered-output assertions prevented an entire tier of work that would have looked diligent and caught nothing, because the input file is fixed and controlled rather than user-supplied.
- **A bound test that fails for a good reason.** `test_uncategorized_share_stays_within_documented_bounds` breaking when the rules improved wasn't a bug — it was the test forcing documentation to move with the code instead of quietly going stale behind it.

### What was harder than expected / real hazards surfaced

- **The most expensive error in the whole project came from an unaudited human assumption, not from any AI tool.** The entire planning phase was organized around catching AI drift, and every instance of that was caught by review. The 2004-vs-2012 date error passed through three documents unchallenged specifically because it had never been flagged as unverified — nobody had thought to doubt it, so nobody reviewed it. The lesson isn't "verify assumptions" in the abstract; it's that writing down *which* claims are unverified is itself the protection, and it only protects the claims someone thought to mark.
- **Coverage is not accuracy, and this was reported as if it were, more than once.** "11.9% Uncategorized" and later "12.2% classified" were both quoted as quality signals when they measured only how many rows got *a* label — the clamshell bug and the 12%-not-100% scope error both hid inside metrics that couldn't see them.
- **A tool reporting success is not evidence the other end received anything.** `SendUserFile` reported success three separate times across the project while the recipient (on a mobile device) couldn't actually open or download what was sent. The fix wasn't a better version of the same delivery mechanism — it was switching to a fundamentally different one (a self-contained HTML page published as a Claude Artifact, with copy-to-clipboard as the most robust fallback).
- **An LLM given a filtered slice cannot tell it was filtered.** The classifying session in the scope-error incident reported "this dataset has no egg products" as if it were a fact about the population, when it was actually the fingerprint of an upstream filter it had no visibility into. The fix that worked was already present, unprompted, in that session's own output — it had written down its own "Known gaps" rather than just its conclusions, which is what made the scope error recoverable instead of silently compounding.
- **Flagging is not asking.** The partial-2026 problem sat under "Open questions" across two build-log entries and came up three times in conversation before anyone actually put forward a decision. An open-questions list can look like active work while nothing is actually moving.
- **Session cost and context-remaining are two different meters.** Watching context-remaining felt like a safe signal but wasn't predictive of the thing that actually ran out — session budget, which is driven more by *how* the context gets used (turns run at very high token counts, heavy skills loaded repeatedly) than by how full the context window looks at any one moment.
- **Commit iteratively instruction was not followed (and I did not verify).** By the time a late-build session ran `git show HEAD:app.py`, it returned the 114-line Phase 2 stub — five sessions' worth of filters, Key Insights cards, and About-section work had been sitting uncommitted in the working tree the entire time, invisible because the app itself worked and each session's own diff looked reasonable in isolation. Nothing was lost, but nothing was in project history either. The build log's own accurate narration of progress turned out not to be a substitute for checking that the repository actually reflected it. The fix was structural, not clever: `git status` showing a clean tree became an explicit, session-ending checklist item going forward, alongside a green test run — see `LEARNINGS.md`'s "the uncommitted-`app.py` problem" for the full account.
- **A plan being read and approved is not the same as its central assumption being checked.** `HANDOFF_PHASE5_LLM_MERGE.md` was reviewed before the manual classification round trip ran, but the assumption buried inside it — that the export covered the full dataset, when it actually scoped to the `Uncategorized` 12% — wasn't caught on that read. It surfaced two full sessions later, once merge work began. The elongation wasn't the failed delivery attempts (Section 4) — those cost minutes each — it was the gap between "the plan was reviewed" and "the plan's central claim was verified," which let two sessions of real work run against the wrong scope before anyone checked.

### Big-picture reflections

- **Planning took the longest, by a wide margin — including brainstorming.** Dataset brainstorming, PRD drafting/correction, and wireframe review spanned multiple sessions before any application code existed, and that time doesn't show up in a commit history. It paid for itself: most of the project's cheapest catches (the toggle-vs-side-by-side reversal, chart-type-per-shape) happened during planning, before they were expensive to fix.
- **A parallel attempt on ChatGPT hit a free-tier usage limit with a reset not until September**, which effectively ended that comparison branch — a reminder that a tool comparison on a real project is bounded by quota, not just capability.
- **ChatGPT was a quicker design/UX partner that gave me better results than Claude Design**, I spent a number of cycles with Claude Design with suboptimal results. ChatGPT gave me the design I was looking for in one-shot from the PRD and then I was able to improve/iterate upon that with Claude Design in one turn. 
- **Scope was deliberately expanded beyond the assignment**, to get hands-on with tools and techniques worth learning regardless of this specific project: ChatPRD, Claude Design, Remote Control with a Claude session, the Claude API directly (the batch classification pipeline), TDD applied to an AI-coded app, and Playwright-driven QA. This was a knowing choice, not scope creep — though it's also directly responsible for the project's biggest scope error (the 12%-vs-100% LLM classification coverage mistake in Section 4).
- **Longer plan documents got less scrutiny, not more.** Once handoff docs and phase plans grew past a certain length, the line-by-line review discipline that caught real drift during planning stopped happening as consistently — length itself became a reason to skim. The one clear exception was the LLM classification + Anthropic API plan, reviewed closely specifically because it was going to cost real money to run. Document length predicts how much scrutiny a plan will actually get, not how much it needs.
- **Repeated session-limit blocks are a signal about effectiveness, not just an inconvenience.** They line up with the earlier finding that context-remaining and session budget are different meters — running into the ceiling repeatedly suggests some of the token spend (long turns, heavy skills reloaded, full-document re-reads) wasn't buying proportionate value.

### Meta-observations on AI-assisted development

- **The recurring shape of this project's errors was not "the AI got things wrong" — it was "an artifact quietly overstated its own authority," and this happened at every layer**, from ChatPRD phrasing a hunch as a conclusion, to a low-fidelity sketch defaulting silently to the wrong chart type, to the human author's own kickoff prompt calling a low-fi wireframe a "source of truth," to the author's own finding about a wireframe divergence being overstated into a design conclusion it didn't support. The fix was the same every time: the artifact meant to prevent drift needed exactly the same scrutiny as everything that came before it, with no exemption for being the thing currently doing the reviewing.
- **A challenge on a single word was worth more than several rounds of self-review.** Mai's "I don't think an ice cream sandwich is a bakery item" surfaced a fabricated documentation claim, two separate classification bugs affecting nearly 2,000 rows combined, and the coverage-vs-accuracy confusion underneath the whole category effort — none of which had come from the author's own repeated review of the same code, because those reviews checked whether the code matched the comments, never whether the comments were true.
- **This project surfaced a genuinely useful distinction for future agentic-AI work: labelling input rows in a one-time, inspectable, version-controlled preprocessing step is not the same act as generating a live claim about data**, even though both involve an LLM touching the dataset. The PRD's "never LLM-generated" rule was written for the second case; recognizing that the LLM classification pass was actually the first case is what made it possible to use an LLM for the hardest data-quality problem in the project without weakening that rule at all.