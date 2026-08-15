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



