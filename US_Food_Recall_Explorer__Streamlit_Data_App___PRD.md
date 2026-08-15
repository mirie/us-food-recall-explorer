
# US Food Recall Explorer (Streamlit Data App)

### TL;DR

This Streamlit-based interactive dashboard explores US food recalls (**2012–present**) using openFDA data. It empowers users to analyze seasonality, leading recall categories, and volume/severity trends—while providing full transparency about data limitations and aggregation methods. Geographic and consumption-normalized analyses are excluded from MVP to maintain focus, pending further data evaluation.

> **Corrected in Phase 0.** This document previously said "2004–present." It is wrong. openFDA's Food Enforcement dataset effectively begins in **2012** — there are zero records before 2012 by `report_date`, and only ~97 scattered stragglers by `recall_initiation_date`. The 2004 figure was an untested assumption that propagated through this PRD, the wireframe's x-axis, and the build kickoff prompt before a direct API call refuted it. See `BUILD_LOG.md` Entry 1.

---

## Goals

### Business Goals

* Deliver a functioning MVP dashboard for the "Mastering Agentic AI" course assignment, demonstrating robust interactive data exploration with Streamlit and CSV.
* Clearly visualize key patterns from the openFDA food recall dataset with minimal overhead, supporting actionable data literacy.
* Provide factual, bias-aware insights for users interested in food safety, without overstating causality or suggesting unwarranted conclusions.

### User Goals

* Explore recall seasonality, leading recalled foods/categories, and time trends through responsive, interactive charts.
* Tune views by time range, contamination reason, severity, and food category to uncover both high-level and granular insights.
* Quickly discern which foods/categories are most commonly affected by recalls—and when.
* Visualize the overall trend in recall volume and severity, in ways that clarify distinctions such as gradual increase, cyclical patterns, or steady rates.
* View event-level and product-level aggregation side by side on relevant charts to understand how each lens changes the picture.

### Non-Goals

* No causal analysis or attribution regarding recall trends or reporting/test improvements.
* Exclude geographic/state-level analyses and consumption-based normalization from MVP, as underlying data may not reliably support them or require further vetting. Revisit in future iterations if data quality allows.
* **No meat, poultry, or processed egg recalls — outside FDA's jurisdiction entirely (confirmed Phase 1).** Those are regulated by **USDA FSIS**, which publishes a separate recall system this dataset does not touch. Meat keywords in this corpus are almost always flavourings or ingredients inside FDA-regulated processed foods (`Natural Beef Flavor`, `Bacon Brittle`, `Chicken Flavor Seasoning`); combined, the three meat categories account for 1.6% of rows. This is a scope boundary of the data source, not a gap in the analysis, and it must be stated in "About the data" so nobody reads the near-empty meat bars as "meat is rarely recalled."
* **No country-of-origin analysis — impossible, not deferred (confirmed Phase 0).** The dataset has no country-of-origin field at all. `country`/`state`/`city` record the *recalling firm's* address (98.9% United States), which says nothing about where food was grown or produced. The growing-season-vs-imports angle raised in `BUILD_LOG.md` Entry 0 is unanswerable with this dataset and should stop being carried forward as an open question.
* **No claim that recall counts measure food safety.** Rising or falling counts may reflect changes in detection, testing, and reporting practice rather than in the safety of the food supply. This is a standing caveat for the "About the data & limitations" section, not an incidental note.
* No live API refresh; the app loads from a static CSV snapshot that is pulled **once**, via a separate one-time script run outside the app (see Technical Considerations). The running app never calls the openFDA API itself, on any session — it only reads the pre-built local CSV file.
* No user analytics or behavioral tracking.

---

## User Stories

**Persona: Curious Consumer**

* As a consumer, I want to see if there's a seasonal spike in produce recalls, so that I can be alert at the right time of year.
* As a consumer, I want to see which foods are most often recalled, so I’m better informed as a shopper.

**Persona: Food Industry Analyst**

* As an analyst, I want to compare recall trends by food category and severity, so I can report on risk areas.
* As an analyst, I want to filter by contamination reason, to identify patterns for specific pathogens (e.g., Salmonella or Listeria).
* As an analyst, I want to understand whether the trend in recall volume/severity is steadily increasing, cyclical, flat, or exhibits rise-then-fall dynamics, so that I can frame trends effectively in reporting and risk assessments.
* As an analyst, I want to see event-level and product-level aggregation side by side, so I can see how much a single recall incident's product count inflates or deflates the picture.

---

## Functional Requirements

* **Filtering & Selection (Priority: High)**
  * Year range slider/selector: All charts reflect user-defined time window
  * Contamination reason filter: Salmonella, Listeria, E. coli, undeclared allergen, foreign material, etc. — **✅ RESOLVED (Phase 0): REFUTED.** `reason_for_recall` is free prose, not a code list (e.g. *"Recall initiated as a precautionary measure due to potential risk of product contamination with Burkholderia cepacia."*). Implemented as **keyword-derived tags** over the free text, not a filter on a categorical field. A naive rule set tags 75.6% of rows; a refined set should reach ~90%, with the remainder in an honest "Other" bucket.
  * Severity/classification filter: Class I/II/III — **✅ VERIFIED (Phase 0): clean categorical field, exactly three values.** Class II 14,616 / Class I 12,804 / Class III 1,741.
  * **Trend charts must render the current partial year as a dashed, explicitly labelled segment** ("partial year — through Aug 2026"). The snapshot ends 2026-08-05, so 2026 holds ~7 months against every other year's 12 and plots 692 against 2025's 1,571 — a phantom 56% drop. Annualising or projecting the year is explicitly forbidden: it invents data and edges into the predictive framing the Non-Goals rule out. This is the one permitted exception to the no-per-chart-annotation rule, because the misreading happens at the chart and cannot be prevented from inside a collapsed About section.
  * Food category filter: (Produce, meat/poultry, dairy, eggs, packaged/processed) — **✅ RESOLVED (Phase 0): REFUTED, and more severely than anticipated.** `product_description` is free prose *and ambiguous*: keyword matching leaves **13.5% matching no category** and **41.5% matching two or more** ("Blue Bell coconut fudge" is legitimately Dairy, Snacks, and Nuts simultaneously). The clean five-category dropdown above is **not derivable as written**. Implemented instead as **priority-ordered keyword rules with a visible `Uncategorized` bucket** — fixed precedence resolves multi-matches deterministically, and unmatched rows stay visible in the chart rather than being silently dropped. Dietary supplements get their own category rather than being folded into a food category (openFDA classifies them as `Food`; the corpus contains CoQ10, pre-workout powder, kratom, and infant formula).
  * **Date basis: `recall_initiation_date` is canonical** for seasonality and trend — when the recall actually began, versus `report_date`'s weekly-publication lag, which would smear seasonal peaks. Not user-selectable; a second date basis would add exactly the hidden state the side-by-side lens design exists to avoid.
  * **Event vs. product lens: shown as two permanent side-by-side panels (not a switch/toggle) on relevant charts (seasonality, trend-over-time, top recalled foods) — see Design Direction section below. This is v1 scope.**
* **Key Insights (Priority: High)**
  * A row of 4 computed stat cards above the filters and charts, recalculated live from the current filter state, framed at event-level by default (see Design Direction)
  * Rule-based only — never LLM-generated, never causal language
* **Visualization & Presentation (Priority: High)**
  * Seasonality chart: **heatmap or dot-matrix by month** (color/size intensity encodes recall volume — not a bar chart), shown as side-by-side event/product lens panels (see Design Direction)
  * Trend-over-time chart: **line chart** of volume/severity by year or quarter, shown as side-by-side event/product lens panels
  * Top recalled foods/categories: **horizontal bar chart**, shown as side-by-side event/product lens panels
  * Chart type is deliberately varied by what the data shape needs (seasonality = heatmap, trend = line, ranking = bar) — not defaulted to bar charts across the board
  * All visuals must clearly and permanently label whether each panel is event-level or product-level
  * Chart-level footnotes are not used — data limitations live in the single "About the data & limitations" section (see Design Direction)
* **Data Handling (Priority: High)**
  * Parse and cache a static openFDA CSV snapshot, pre-built once via a separate one-time fetch script (not fetched by the app itself)
  * Standardize aggregation logic per chart: event vs. product, rendered side by side (see Design Direction)
* **Transparency & Limitations (Priority: High)**
  * Single collapsible "About the data & limitations" section (collapsed by default) consolidates: the detection/reporting confound caveat, notes on missing/unreliable fields (e.g., country of origin), and the event-vs-product explanation — see Design Direction
  * Not scattered as separate footnotes per chart
* **Usability (Priority: High)**
  * Display "data last updated: \[date\]" indicator in view, reflecting when the CSV snapshot was pulled

---

## User Experience

**Entry Point & First-Time User Experience**

* Users access the app via Streamlit link or local session
* See the Key Insights row first — 4 computed stat cards giving an immediate high-level read, event-level framed
* Below that: intro line on scope, filters, and a link to the collapsible "About the data & limitations" section
* Default filters: "All Years, All Categories, All Contaminants, All Severities"
* Initial visualizations show high-level overview for full dataset, both lenses visible

**Core Experience**

* **Step 1:** User scans the Key Insights row for an immediate headline read of the current view
* **Step 2:** User adjusts filters (year, food category, contamination reason, severity)
  * UI presents labeled sliders/dropdowns, minimal friction
  * Both the Key Insights cards and all charts update instantly on user action
* **Step 3:** User examines seasonality heatmap/calendar
  * Aggregates and displays patterns by month/quarter, shown as side-by-side event and product lens panels
* **Step 4:** User reviews top recalled foods chart
  * Shows most-frequently recalled products/categories for selected filters, side-by-side by lens
  * Grouping granularity adapts based on data available
* **Step 5:** User analyzes trend-over-time chart
  * Illustrates count and severity split across years/quarters, side-by-side by lens
* **Step 6:** User compares the two lens panels directly on any chart
  * Both panels are visible at once, so no state to remember or switch
* **Step 7:** User expands "About the data & limitations" for the fuller explanation (confounders, missing fields, event/product meaning) if curious
* **Step 8:** App visibly displays data age/timestamp
* **Step 9 (Edge Case):** If filters yield no data, user sees a friendly zero-state message (Key Insights row also reflects zero state)

**Advanced Features & Edge Cases**

* Disable or warn on chart if expected columns are missing (e.g., if "reason"/"severity" are absent)
* Nice-to-have features (product search, company/brand filter, geo-mapping) are explicitly deferred unless prioritized for future iteration. (Note: the event/product toggle is *not* in this deferred list — it is v1 scope, see Functional Requirements.)

**UI/UX Highlights**

* Accessible color palette for all charts
* Responsive layout (leveraging Streamlit defaults plus custom tweaks)
* Transparent, persistent labeling for filters and aggregation methods
* All notes on data limitations easily visible yet unobtrusive (tooltips, beneath charts)

---

## Narrative

Maria is a health-conscious shopper who recently read about a lettuce recall. Out of curiosity, she opens the US Food Recall Explorer. She sees clear visual summaries of peak recall months and the most frequently recalled produce items. Narrowing her view to “produce” and recent years, Maria notices a recurring spring spike and identifies which vegetables often appear in recall lists. The dashboard empowers her to fine-tune every parameter—investigating not just which foods are recalled, but also whether recall trends are climbing, falling, or fluctuating over time. By offering transparency about data—and admitting where conclusions are limited—Maria leaves both empowered and informed, able to make smarter decisions, and confident in the tool’s integrity.

---

## Success Metrics

### Technical Metrics

* Dashboard load time <5 seconds with typical-size CSV snapshot
* Zero chart errors (all required columns present and valid)
* Chart interactivity (filters/selections) is 100% reliable throughout typical usage; both lens panels render correctly on every chart

---

## Technical Considerations

### Technical Needs

* **One-time data acquisition step, separate from the app**: a standalone script (e.g. `fetch_data.py`) pulls from the openFDA Food Enforcement API once and writes a static CSV snapshot to the project folder. This script is run manually, verified, and is not invoked by the running app.
* The Streamlit app itself only reads the pre-built local CSV (e.g. via `pd.read_csv`) at init — it contains no API-calling code, no rate-limit handling, and makes no network requests at runtime.
* Aggregate by event-level and product-level simultaneously — both rendered side by side on every relevant chart, not switched via toggle (see Design Direction)
* Streamlit app architecture: modular chart/filter sections, verbose aggregation labeling

### Integration Points

* None for v1: static CSV only, no live third-party integrations at runtime. The only external call is the one-time fetch script, run outside the app.

### Data Storage & Privacy

* All data is open government data (no PII whatsoever)
* Store CSV snapshot with visible timestamp (captured at fetch time, displayed in-app)

### Scalability & Performance

* Projected audience <100 active users, minimal backend
* Handle the actual snapshot of **29,161 rows / 7,791 recall events** (measured Phase 0, not estimated) with fast chart performance. The earlier "~10,000 rows" figure was a guess and was low by roughly 3x; still trivial for pandas.

### Potential Challenges

* Data inconsistencies (missing or messy fields such as origin/severity/reason)
* schema drift in openFDA source (remedied by snapshotting for v1)
* Ensuring fast and robust chart updates despite aggregation complexity and rendering both lens panels on every chart

## Design Direction

**Visual spec**: `Design_US_Food_Recall_Explorer.pdf` (2 pages) is the directional reference for layout, spacing, and visual treatment. The points below capture only the *rationale* behind decisions that aren't self-evident from looking at the PDF — not a redundant description of what it shows.

> **Where real data supersedes the wireframe (Phase 0).** The PDF was drawn before the data was pulled, and two things in it are now known to be wrong:
> - **The `2004 —— 2026` x-axis on both trend charts.** The real range is **2012–2026**. Drawing 2004–2011 as empty would read as "no recalls happened then," which is false.
> - **2026 is a partial year** (data through 2026-08-05). The final point on every trend line will dip artificially and needs explicit visual treatment — a dashed segment or annotation — not a footnote.
> The top-foods chart itself is **not** superseded — horizontal bars ranking categories under both lenses works exactly as drawn. Its placeholder labels (Poultry #1, Beef #3, Pork #4) differ from the real ranking, which is expected of a low-fidelity mock and is not a design problem. The real ranking is **Produce 15.4%, Bakery 14.3%, Dairy 9.2%**, with `Uncategorized` at 18.4%. The reason meat is absent is a property of the data source, recorded under Non-Goals, not a flaw in the wireframe.
>
> Conversely, one thing in the PDF was **confirmed correct against a mid-build challenge**: its roughly 3.8x product-to-event ratio. A Phase 0 sample estimate suggested ~1.4 and was used to call the wireframe unrealistic; that estimate was itself the error (a contiguous API page splits multi-product events across boundaries). The true figure is **3.74**. Recorded because it cuts against the direction of every other correction in this project's history — see `LEARNINGS.md`.
>
> Everything structural in the PDF stands: side-by-side lenses, chart type per view, Key Insights row, one collapsible About section.

**1. Event vs. product is a permanent side-by-side lens, not a toggle.**
Both lenses are always visible rather than switched between, so the analyst persona never has to trust a hidden state or remember which mode they're in — comparison is immediate. Tradeoff accepted deliberately: charts run at half-width, roughly doubling render work. In Streamlit: `st.columns`.

**2. Key Insights cards are computed, never LLM-generated, and never causal.**
Allowed: magnitude, peak/low values, percentage change, share of total (e.g., "Recall events up 37% since 2014"). Not allowed: evaluative or causal language (e.g., never "food safety is getting worse"). Direct extension of this PRD's Non-Goals around causal analysis. Framed at event-level by default, explicitly labeled as such, since the side-by-side charts below still carry the full product-level picture for anyone who wants it.

**3. One collapsible "About the data & limitations" section, not per-chart footnotes.**
Consolidates the detection/reporting confound caveat, missing/unreliable field notes (e.g., country of origin), and the event-vs-product explanation in one place — available without being repeated as visual noise on every chart.

**4. Chart type is chosen per data shape, not defaulted to bars.**
Seasonality = heatmap/dot-matrix, trend-over-time = line chart, top recalled foods = horizontal bar chart — applied identically to both lens panels. This was a real bug in an earlier sketch (everything rendered as bars by default) — worth stating explicitly so it doesn't silently regress during the build.



### Suggested Phases

**Phase 0: One-Time Data Fetch**

* Deliverables: `fetch_data.py` script that pulls from openFDA API once and saves `food_recalls.csv`; verify fields and record counts. **Explicitly confirm or refute the two unverified assumptions flagged above: (1) whether food category can be reliably derived from the product description field, and (2) whether contamination reason is a clean field or free text requiring parsing. Document findings in `BUILD_LOG.md` before Phase 1 begins.**
* Dependencies: openFDA API availability

**Phase 1: Data Preparation**

* Deliverables: Analyze and clean the cached CSV; document data structure and aggregation columns (event ID, product ID, category, reason, severity, date, origin if present)
* Dependencies: Phase 0 completion

**Phase 2: App Skeleton & Core Charts**

* Deliverables: Streamlit app scaffold; CSV loader (reads local file only); basic charts for seasonality, trend, and top foods
* Dependencies: Phase 1 completion

**Phase 3: Core Filters & Interactivity**

* Deliverables: Year range, category, contaminant, and severity filters; side-by-side event/product lens panels on all three charts; Key Insights row (4 computed cards); ensure dynamic updates for charts
* Dependencies: Core chart modules implemented

**Phase 4: Transparency & UI Polish**

* Deliverables: Explanatory notes, last-updated timestamp, accessible labeling, robust error UI
* Dependencies: Completion of core interactivity

**Phase 3 (added): LLM-assisted category labelling — deferred, not dropped**

* Keyword rules leave ~11.9% of rows `Uncategorized`, and the residual is genuinely hard: SKU strings (`a89471 batter mix x1`), generic names (`california medley`), obscure items (`pure trans-resveratrol`). A one-time offline LLM labelling pass could plausibly reduce this below 3%.
* Shape: a standalone script alongside `fetch_data.py`, batching product descriptions against a **fixed category enum**, validating every returned label against that enum, and writing a static column. The app continues to read a frozen CSV — no runtime API calls, no change to its offline/deterministic character.
* **This does not conflict with the "never LLM-generated" rule.** That rule governs *claims about the data* — the Key Insights cards must never have a model author an assertion. Labelling input rows in a preprocessing step whose output is committed, inspectable, and version-controlled is a different act. Stated explicitly here so the distinction is a recorded decision rather than an apparent loophole.
* Testable without network calls: unit-test the prompt builder, the response parser, and the enum validator against hand-built fixtures.

**Phase 5: QA, Docs & Submission**

* Deliverables: End-to-end QA, edge case testing, documentation for project submission
* Dependencies: All major features present

---

## Process & Documentation Requirements (outside PRD scope, tracked separately)

This PRD describes the product only. Per the course assignment, the build process itself must also be documented:

* **`BUILD_LOG.md`**: a running working log in the project folder, updated after each meaningful build step, using the format: Goal → What I built → What worked → What broke → What I changed → Open questions → Time spent. Should also capture the actual prompts used during vibe coding sessions, not just descriptions of them.
* **Final submission deliverable (Google Doc)**: written after the build is complete, synthesized from `BUILD_LOG.md`. Covers: project overview, datasets used, prompts used during vibe coding, iterations tried, and learnings/observations from the workflow.
