# Zomato AI Restaurant Recommendations

AI-powered restaurant recommendations using the Zomato dataset and **Groq** for ranking and explanations.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set GROQ_API_KEY
```

Ensure `data/restaurant.parquet` exists (or the app will download from Hugging Face on first run):

```bash
python scripts/generate_restaurant_parquet.py
```

## Run

**Streamlit UI**

```bash
streamlit run src/presentation/streamlit_app.py
```

**CLI**

```bash
python -m src.presentation.cli --location Bangalore --budget medium --cuisine Italian --min-rating 4.0
```

## Environment

See `.env.example` for `GROQ_API_KEY`, `LLM_MODEL`, `MAX_CANDIDATES`, `TOP_K`, `LLM_TIMEOUT_SECONDS`, and `LOG_LEVEL`.

## Testing (Phase 5)

```bash
# Full automated suite (mocked LLM)
python scripts/run_tests.py

# Or directly
python -m pytest -v -m "not e2e"

# E2E smoke (parquet + Groq if key set)
python scripts/smoke_e2e.py

# Live Groq API check
python scripts/smoke_test_groq.py

# Optional live E2E pytest (requires GROQ_API_KEY)
python -m pytest -v -m e2e
```

See `docs/KNOWN_LIMITATIONS.md` and `docs/TEST_REPORT.md` (generated after `run_tests.py`).
