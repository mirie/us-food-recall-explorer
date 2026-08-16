# US Food Recall Explorer

A Streamlit dashboard exploring US food recalls (2012–present) using openFDA's Food Enforcement API. Built for Maven's "Mastering Agentic AI" course, Homework 1.

Answers three questions from the data: is there seasonality to recalls, which food categories are recalled most, and is recall volume/severity rising, falling, or cyclical — all with event-level and product-level counts shown side by side, since a single multi-product recall can span many product rows but counts once as an incident.

## Running it

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app reads a static CSV snapshot in `data/` — no API key or network access needed to run it. That snapshot was built once via `fetch_data.py` (openFDA) and `classify_all.py` (Anthropic Batch API, for category labelling); neither runs at app startup.

## Project docs

- [`US_Food_Recall_Explorer__Streamlit_Data_App___PRD.md`](US_Food_Recall_Explorer__Streamlit_Data_App___PRD.md) — product requirements
- [`SUBMISSION_DRAFT.md`](SUBMISSION_DRAFT.md) — project overview, datasets, prompts, iterations, and learnings (source for the course submission doc)
- [`BUILD_LOG.md`](BUILD_LOG.md) — chronological build log
- [`CLASSIFICATION_RULES.md`](CLASSIFICATION_RULES.md) — food category taxonomy and LLM classification methodology
- [`LEARNINGS.md`](LEARNINGS.md) — synthesized learnings from the build process

## Tests

```bash
pytest
```
