# Prompt Log

Curated, not exhaustive — these are the prompts that drove a decision, caused a pivot, or caught a mistake, pulled from each tool used across this project. Spans both the planning phase (below) and the build phase (appended from Claude Code onward). Running log only — see `LEARNINGS.md` for analysis and reflection drawn from these prompts, and `BUILD_LOG.md` for the narrative process record.

---

## Tool: Claude.ai (this chat) — Dataset & concept selection

> "Okay I'm taking a course on Maven. It's called Mastering Agentic AI. My first HW assignment is to: Build interactive data applications with minimal boilerplate / Work with CSV datasets and visualize insights... I need help brainstorming ideas as I'm not that creative, hahaa"

> "Okay what about climate change: highest polluters / most affected by weather or rising sea levels / countries investing in climate change policies... Is there public datasets on these^?"

> "arXiv agentic AI trend explorer - I like this idea too"

> "would this replicate something that already exists?"

> "Okay I'm actually interested in the myth vs reality framing. Maybe not re: rain, but something along those lines....let me vibe with you on that"

> "Okay wait I got more information. For my project documentation I also need to include: 'Submit a Google Doc explaining what you built...'"

## Tool: ChatPRD — Formalizing the concept into a PRD

> Opening prompt (abridged — full version captured in `BUILD_LOG.md` Entry 0):
> "I'm building a Streamlit + CSV data app for a Maven course assignment... Project concept: An exploration of US food recalls (Salmonella, E. coli, Listeria, and related contamination) — inspired by recent recalls in the news (lettuce, jalapeños)... Questions I want the data to answer: [seasonality, top foods, trend shape]... Need to note: recalls can be counted at 'event' level... or 'product' level... I want to pick one and be consistent, not mix them... Stack: Streamlit + CSV... Plan to pull from the openFDA API once, cache to CSV, then build the dashboard off the static file (not live API calls on every reload)."

> [ChatPRD generated the initial PRD; a follow-up options prompt asked about nice-to-have features] → "Skip nice-to-haves for v1"

> "Okay two feedback: remove the days from the phases (1-2 days for example) / can I have beefier section on the nice to haves?"

> "'Geographic/state-level or consumption-specific mapping is excluded from v1, due to data limitations.' -- wait this is a conclusion that is not clear yet. I haven't explored the data. I just noted that potentially it's messy and that I might not be able to explore this. Do you suggest just cutting it from MVP to keep the scope tight? If so, I'm fine with that."

> "For 'Persona: Food Industry Analyst' I think I also want to be able to understand 'What does the trend in recall volume/severity actually look like over time — a steady increase, a rise-then-fall-then-rise pattern, cyclical swings, or roughly flat?' ... I removed biz metrics cause it's unnecessary. I don't think I need to have any analytics. I've removed this: 'Persona: Maven Course Grader...'"

## Tool: Claude.ai (this chat) — PRD correction & data pipeline decisions

> "I created an account on ChatPRD so I could capture this into a proper product requirements docs with clearer specs -- see uploaded md file. Can you review, catch any drift from our discussion above, and also update the prompt as needed?"

> "Need to note: recalls can be counted at 'event' level... or 'product' level... what are the pros/cons for event level or product level?"

> "Okay but I think I'll just download the csv file once right? Do i need the app to do this?"

## Tool: Claude Design — Wireframe exploration (full curated log, produced by Claude Design itself)

**1 · Initial brief**

> "I'm designing a low-fidelity wireframe for a data dashboard called 'US Food Recall Explorer'... This is an early structural sketch, not final visual design — think grayscale/low-color wireframe... A prominent event-level vs. product-level toggle — this needs to feel like a real, noticeable control, not a buried checkbox... Please sketch 2-3 layout variations."

Result: three grayscale layouts (1a sidebar/stacked, 1b top bar/grid, 1c sticky mode band) plus a detail sheet of label and zero-state treatments.

**2 · First review**

> "Please make the scope & limitations section smaller... remove streamlit app from the top app bar. Seems unnecessary? / What is the left axis for seasonality?... / Are these different designs concepts? Also I notice no change in the design when switching modes from event to product"

Result: disclaimers reduced to single mono lines; app-bar label removed; seasonality axis explained; event/product control rewired so counts/ranking/bar lengths actually change.

**3 · Widening the search**

> "Can we take a moment to explore this?" [pulling on a thread about genuinely different concepts]

> "I actually have a PRD for this -- it focuses on the layout that I started this chat but I'm interested in seeing if we should take it a different direction"

Result: four new concepts drawn directly against the PRD — question-led scroll, single-chart focus with reading panel, permanent side-by-side lenses (2c), and search-first (2d, a hedge against the PRD's unverified free-text field assumptions).

**4 · Narrowing back down**

> "Okay honestly I like 1a's approach the best. I think the counting mode should be a lot smaller (more of a toggle versus a huge row). I think the filter left rail could be smaller OR placed horizontally at the top and collapsible."

Result: two riffs on 1a (narrow rail, collapsible horizontal bar), counting mode shrunk to a small segmented control.

**5 · Final direction**

> "Direction is now finalized. Structure: A top-of-page 'Key Insights' row... two permanent side-by-side panels — 'Lens A · Events' and 'Lens B · Products' — always both visible, no toggle... Visual style reference: the ChatGPT 'Story First' mockup..."

Result: concept 4a — insight-led header, compact filter row, three chart sections each with two permanently labeled lens panels, one collapsed "About the data" section.

**6 · Delivery**

> "wait i don't see the pdf at all so how do I download it"

Result: PDF dialog had failed silently; fallback was a self-contained HTML file to print locally.

> "I need 4: Finalized direction... exported into a PDF or html doc"

Result: print copy narrowed from ten options to 4a alone, paginated as two landscape pages — this is the PDF used for the final Claude Code handoff.

## Tool: ChatGPT — Alternative design directions (full curated log)

**Initial concept**

> "if I give you a concept, can you do some lo-fi visual designs? I want to brainstorm what this interface is going to look like."

> "Give me a few different rough interface concepts"

Result: multiple genuinely different rough interface concepts, not iterations on one layout.

**Exploring alternatives to the PRD**

> "Okay, I'm attaching my PRD. Now, this PRD clearly focuses on a certain kind of layout with certain kinds of filters and such as part of the spec, but I'm also open to exploring different layouts. I just wanted to take a moment to see: are there other ways to represent this information in an accessible way for the use cases?"

Result: four alternative interaction models — Classic Dashboard, Insight-Led, Question-Based Explorer, and Flexible Analyst Workspace.

**Moving toward an insight-led model**

> "ooo, this is interesting. But for the Story first (insight led) do you think these key insights can be pulled in / determined on the fly?"

Result: concept shifted from static "insight-led" layout to dynamic, data-derived observations calculated from the current filters.

## Tool: Claude.ai (this chat) — Reconciling the two design explorations

> "wait a minute.....thi" → "Wait a minute. I'm looking at the sketch. That's not what I wanted..." [uploaded ChatGPT's "Story First" mockup] "This is actually the direction from chatgpt that spoke to me the most"

> "Can you note that they shouldn't always be bar charts? Something is off about this image above. honestly the chatgpt design direction (image I pasted seems to feel the best in capturing the experience). Maybe let's just use that for the PRD?"

> [Clarifying question answered]: "No — keep side-by-side panels, just fix the insight-cards part"

> [Clarifying question answered]: "No — keep side-by-side lenses, just match its chart types/insight-card style/filter layout"

Result: final Design Direction locked — permanent side-by-side event/product lenses (not a toggle), top-of-page Key Insights row, one collapsible "About the data" section, chart type varied by data shape (heatmap/line/bar, not defaulted to bars). Finalized wireframe PDF produced in Claude Design from this reconciled spec.

## Tool: Claude.ai (this chat) — Finalizing the kickoff prompt

> "'This is the source of truth for layout, spacing, and chart types' -- This isn't perfectly designed. So I don't want to build exactly to spec. This is a low-fi design. We will iterate with real data."

> "'PROMPT_LOG_Planning_Phase.md and LEARNINGS.md — background only, not needed to build the app...' -- I think we should keep appending to it during the build"

Result: kickoff prompt revised twice before handoff — the wireframe PDF reframed as a directional reference (structure firm, exact visual treatment flexible) rather than a pixel-perfect spec to build against; and this prompt log plus `LEARNINGS.md` established as living documents that continue through the build phase, not artifacts that close out once planning ends. File renamed from `PROMPT_LOG_Planning_Phase.md` to `PROMPT_LOG.md` to reflect that.

---

## Build phase (Claude Code / VS Code) — appended from here onward

## Tool: Claude Code — Phase 0 kickoff

> "I'm building a Streamlit + CSV data app for a Maven course assignment... Reference documents (all attached, and also exist in this directory) — please review all four before starting)... Core design decisions, held firm regardless of implementation convenience — but open to visual iteration once real data is flowing: Event vs. product is a permanent side-by-side layout... Chart type varies by data shape, not defaulted to bars... Key Insights row... rule-based/calculated from filtered data only — never LLM-generated, never causal or evaluative language... One collapsible 'About the data & limitations' section...
>
> How I want to work: I'm directing, you're coding — explain what you're doing in plain language, flag what I should understand vs. what I can trust you to handle, keep scope tight (spec before building, dry-run before real runs, --limit 1 on first real writes).
>
> First step — Phase 0: pull a sample from the openFDA API, explicitly check the two unverified assumptions flagged in the PRD (food category and contamination reason — clean fields or free text?). Log findings in BUILD_LOG.md before touching Phase 1."

Result: the "dry-run before real runs, `--limit 1` on first real writes" instruction is the single most load-bearing line in this prompt. It directly produced the execution sequence that caught the `--limit` page-size bug, and it set the expectation that assumptions get probed before code gets written — which is what surfaced the 2004-vs-2012 error before any chart was built against a wrong axis.

## Tool: Claude Code — Phase 0 decision points

Four decisions surfaced once the API had actually been called, presented as options rather than assumed. All four recommendations were accepted:

> **Date range** — "The dataset really starts in 2012, not 2004. How should the app frame its time range?" → *2012–2026, state it plainly.* The rejected option (keeping the 2004 axis with 2004–2011 as zeroes) would have read as "there were no food recalls before 2012," which is false and precisely the causal misreading the PRD's Non-Goals forbid.

> **Date field** — "Which date field should drive seasonality and trend charts?" → *`recall_initiation_date`*, over `report_date`. The former is when the recall actually began; the latter is FDA's weekly publication date, an administrative lag that would smear real seasonal peaks. A third option (make it user-selectable) was rejected for adding hidden state to an app whose entire design premise is that there is none.

> **Food category** — "Food category can't be cleanly derived. Which way do you want to go?" → *priority-ordered keywords plus a visible `Uncategorized` bucket*, over both a narrow high-precision set and the search-first fallback that planning had pre-emptively designed as a hedge (Claude Design concept 2d).

> **Supplements** — "openFDA's 'Food' type includes dietary supplements, kratom, and infant formula. In or out?" → *include, as their own category*, so their share stays visible rather than being folded into a food category where it would mislead.

## Tool: Claude Code — environment correction

> "I like the plan overall. Can you re-review the python part? I installed python via homebrew in a separate session and I think it will now work with: `python3 -m venv .venv` / `source .venv/bin/activate` / `pip install streamlit`"

Result: the plan had been written against a stale environment reading (system Python 3.9.6, captured before the Homebrew install), and carried a warning about pip resolving to an outdated Streamlit. Re-checking showed `python3` now resolving to Homebrew 3.14.7, and a PyPI query confirmed every binary dependency ships a prebuilt `cp314` arm64 wheel. The obsolete warning was replaced with a genuine one — pip resolves to pandas 3.0, a major release — and `requirements.txt` was pinned rather than left floating.

Worth logging as a prompt: it is the first time in the project that the *human* caught the *tool* working from stale state, reversing the direction every earlier correction in this log runs.




## Tool: Claude Code — adopting a testing strategy mid-build

> "I think I failed to mention earlier that I'd like to take a test-driven approach as part of implementation. Now that we have the data, I want you to make sure you are writing tests: 1. Unit Tests (TDD) — write tests first, then implement, for all pure logic... use small, hand-built DataFrames/dicts as input fixtures — do not read the real file in these tests... 2. Pipeline / E2E Tests — run the actual fixed CSV file through the full real pipeline... 3. One Guardrail Test — validates the CSV's expected schema... **Explicitly Skip**: no integration tests as a separate tier... no malformed/adversarial input handling — the file is fixed and controlled, not user-uploaded... no retry logic, upload validation, or encoding-detection tests."
>
> "Testing Interactive Visualizations... Split Data Shaping from Rendering: `raw data → [transform_for_chart()] → chart-ready data → [render component]`... Do not unit test the rendering output itself (e.g., asserting SVG bar heights) — brittle, breaks on styling changes, low signal... Visual Correctness Stays Manual."

Result: the most consequential prompt of the build phase, and notable for what it *excludes*. The skip list is doing as much work as the requirements — it rules out an entire tier of tests that would have looked responsible and produced nothing, because the input file is fixed and controlled rather than user-supplied. The explicit "don't assert on rendered output" line pre-empts the most common way chart test suites become maintenance burdens.

The instruction to use hand-built fixtures for unit logic, and the real file *only* at the pipeline tier, is what kept the unit suite at ~0.02s — fast enough to run after every single edit, which is what made strict red-green-refactor practical rather than theoretical.

> "Also please commit iteratively, rather than one massive commit"

Result: sent mid-turn, while a slice was in progress. Changed the commit cadence from one Phase-1 commit to one per green slice, so the history records the meat-category bug and its fix as a distinct, inspectable step rather than burying it inside a larger diff.

## Tool: Claude Code — Phase 1 decision points

> **Category resolution** — asked after measuring that 35.4% of descriptions match two or more categories, with the collision table showing Dairy colliding with everything. → *Precedence, specific beats generic.* The framing that made the decision answerable was identifying **why** the collisions happen: `milk`, `butter`, and `cream` are ingredient words, not product-type words, so a chocolate chip cookie matches Dairy, Bakery, and Snacks at once. The accepted tradeoff — "ice cream sandwich" resolving to Bakery — was shown in the option preview rather than discovered later.

> **Reason labelling** — → *Multi-label.* Measured afterwards at only 1.7% of recalls carrying two or more tags, making the choice semantically right but practically minor. Worth recording that the decision was made on principle and the data later showed the stakes were low; the reverse (deciding on principle and discovering the stakes were high) is the case this habit is insurance against.

> **Meat categories** — surfaced after inspecting what actually landed in Beef/Pork/Poultry and finding `Natural Beef Flavor`, `Bacon Brittle`, and `MME Chicken Parmesan No Meat`. → *Demote below product form*, and *build the top-foods chart to real data, documenting the wireframe divergence.* The underlying fact — FDA does not regulate meat, poultry, or processed egg products, USDA FSIS does — was not in the PRD, the wireframe, or any planning document, and it invalidates three of the wireframe's eight top-foods bars.


## Tool: Claude Code — challenging an overstated finding

> "Does this apply to top-foods generally or are you just fixating on a fake data point of Poultry. Please note that the designs were not based on real data but is just a low-fi representation of the general design."

Result: the challenge was correct and the claim was withdrawn. I had recorded the wireframe's top-foods chart as "not achievable" because it ranks Poultry #1; in fact only its placeholder labels differ from real data, which is exactly what a low-fidelity mock is for. The chart's structure works as drawn. Notable as the first time in the project that a *finding* — rather than a plan or an assumption — was overstated and had to be walked back, and it took a direct challenge rather than self-review to catch it. The underlying USDA jurisdiction fact was real; the design conclusion drawn from it was not.

> "Tell me more. I'm not following -- did I miss a question earlier that you asked me?"

Result: no, and that was the point. The partial-2026 problem had been listed under "Open questions" across two build-log entries and mentioned three times in conversation, but no decision had ever actually been put forward. Recorded because it is a specific failure mode worth naming: **an open-questions list can look like active work while nothing is being decided.** Flagging is not asking.

> "I need to know more about this. Can we discuss different approaches? What are the tradeoffs?"

Result: forced the Uncategorized question out of a one-line recommendation and into a measured comparison — which immediately refuted my own characterisation of it. I had called the bucket irreducible ambiguity; sampling 25 rows showed missing keywords and three absent categories. The prompt asked for tradeoffs, and producing real ones required inspecting the data rather than reasoning about it.

> "Also would it help or hurt to do some classifications on the data set for the visualizations -- seems that's what you're already doing, but wanted to double check if there's anything else to consider"

Result: surfaced the risk worth naming explicitly — every derived column launders judgment into something that reads as measurement. A bar labelled "Produce 17.0%" carries the authority of a count, but the assignment behind it is a keyword rule. This is the strongest argument for keeping `Uncategorized` visible: it is the one element of the chart that admits the rules are rules. Also settled what *not* to classify further (distribution scope, repeat-offender status, recall duration) — all rejected for not serving the three core questions.

> "Don't forget to update the relevant files with decisions, logs as well (build_log.md, prompt_log.md, etc). I'll clear this session when we are ready to do Phase 2."

Result: sent mid-turn. Worth logging as a process note — the documentation requirement held up across the whole build, but it needed reinforcing at exactly the point where a decision-heavy discussion was about to end without being written down.


## Tool: Claude Code — a user challenge that exposed a fabricated claim

> "I disagree with a line I see in the handoff_phase2.md doc: '"ice cream sandwich" → Bakery' -- I don't think an ice cream sandwich is a bakery item. I see this restated in categories.py as well... I disagree. It's mostly dairy (aka ice cream)."

Result: the single highest-value prompt of the build so far. The disagreement was correct twice over. First, the classification was wrong — an ice cream sandwich is a dairy product. Second, and worse, **the documented claim was fabricated**: it did not resolve to Bakery at all, it resolved to `Prepared/Frozen`. I had invented a plausible illustration of a real limitation, written it into a docstring, the PRD, the handoff note, and two build-log entries, and never once executed it. It was recorded as an "accepted tradeoff", which dressed a fabrication up as a considered decision.

Measuring what the challenge implied found 1,393 rows mentioning "ice cream" scattered across nine categories, and chasing *that* found 509 rows — a fifth of the Seafood category — that were cheesecakes in plastic **clamshells**.

> "Also I was examining categories.py and I see: Seafood: anchov / Produce: cherr / Did you mean these two?"

Result: they were intentional stems (anchovy/anchovies, cherry/cherries), so the answer was "yes, deliberate" — but the question landed on exactly the right lines anyway. `cherr` and `berr` in the Produce rule were the specific patterns stealing flavoured yogurt and ice cream from Dairy. A question aimed at readability found the mechanism of the bug.

> "I imagine categories.py doesn't cover every use case in the csv file (or does it?)"

Result: forced the admission that **I had been reporting coverage as though it answered accuracy.** "11.9% Uncategorized" had been quoted repeatedly as the quality figure; it measures only how many rows got *a* label, never how many got the *right* one. The clamshell bug inflated Seafood by 25% while sitting entirely inside "successfully categorised" rows, invisible to any coverage metric.

> "I'm starting to think we will actually need to walk back 'LLM-assisted category labelling' -- would it be helpful to add this to scope to reduce the brittleness of regex?"

Result: a scope reassessment prompted by accumulating evidence rather than by preference — five distinct regex failure classes by this point, four of them found by someone happening to inspect the right rows and two of those by Mai rather than by me. Decision was to **freeze the rules now and revisit in Phase 3** rather than either continuing to patch or pivoting mid-build. The deciding factor was architectural: `pipeline.py` sets `df["category"]` in one line, so swapping the source later costs no rework, which makes deferral genuinely cheap rather than merely postponed.

