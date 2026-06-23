# Known Limitations (MVP)

## Data

- Restaurant data is a static snapshot from Hugging Face; no live Zomato API sync.
- Location matching is string-based (exact/contains), not geospatial.
- Some rows lack rating or cost; shown as "Not available".
- Budget tiers are derived from fixed INR thresholds (`LOW_MAX` / `HIGH_MAX`).

## LLM (Groq)

- Recommendations depend on Groq availability and API quotas.
- JSON parsing may fail occasionally; app falls back to rating-based ranking.
- Explanations are model-generated and should not be treated as verified facts.
- `MAX_CANDIDATES` caps prompt size; very broad searches may miss good options.

## Performance

- First run without `data/restaurant.parquet` downloads ~574 MB from Hugging Face.
- End-to-end latency is dominated by Groq; target is under 10 seconds for MVP.
- Streamlit caches the service; restart app after `.env` changes.

## Security

- API keys must stay in `.env` only; never commit secrets.
- User `additional_preferences` is passed to the model as soft constraints (prompt injection risk is mitigated in prompts but not eliminated).

## UI

- No user accounts, history, or feedback loop in MVP.
- CLI and Streamlit only; no REST API or mobile client.

## Testing

- Live Groq E2E tests are manual (`scripts/smoke_e2e.py`, `scripts/smoke_test_groq.py`).
- Automated suite uses stubs/mocks for LLM calls.
