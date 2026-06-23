# Phase-wise Implementation Plan

This plan translates `docs/context.md` and `docs/architecture.md` into an execution roadmap for building the AI-powered restaurant recommendation system.

## Planning Assumptions

- Team size: 1-3 engineers (can be adapted)
- Target: MVP first, production hardening later
- Primary stack: Python, Hugging Face `datasets`, **Groq** LLM SDK, Streamlit/CLI
- Delivery style: iterative, test-driven for core modules

## Milestones at a Glance


| Phase | Focus                                                 | Duration (est.) | Outcome                                     |
| ----- | ----------------------------------------------------- | --------------- | ------------------------------------------- |
| 0     | Setup and alignment                                   | 0.5-1 day       | Repo, config, project skeleton ready        |
| 1     | Data ingestion + schema normalization                 | 1-2 days        | Reliable canonical restaurant store         |
| 2     | Preference parsing + deterministic filtering          | 1-2 days        | Candidate generation works without LLM      |
| 3     | Prompting + LLM recommendation engine                 | 2-3 days        | Ranked, explained recommendations           |
| 4     | Presentation layer (CLI/Streamlit) + Groq integration | 1-2 days        | User-facing interface powered by Groq       |
| 5     | Quality, testing, and resiliency                      | 1-2 days        | Stable MVP with fallback behavior           |
| 6     | Optional productionization                            | 2-5 days        | Monitoring, packaging, deployment readiness |


---

## Phase 0: Setup and Project Baseline

### Objectives

- Initialize a clean, reproducible development environment
- Create module structure from architecture document
- Define configs and secrets handling

### Tasks

- Create base folders under `src/`, `tests/`, `docs/`
- Add dependency management (`requirements.txt` or `pyproject.toml`)
- Add `.env.example` with required keys:
  - `HF_DATASET_ID`
  - `LLM_PROVIDER` (default: `groq`)
  - `LLM_MODEL` (default: `llama-3.3-70b-versatile`)
  - `GROQ_API_KEY`
  - `MAX_CANDIDATES`
  - `TOP_K`
  - `FILTER_RELAX_ON_EMPTY`
- Add `config.py` to load and validate settings
- Add basic lint/test tooling (`pytest`, optional formatter/linter)

### Deliverables

- Project skeleton aligned to architecture
- Config loading verified from environment
- Basic run command documented in README

### Exit Criteria

- App boots with placeholder entrypoint (`main.py`)
- Config errors are clear and actionable

---

## Phase 1: Data Ingestion and Canonical Data Model

### Objectives

- Load Zomato dataset from Hugging Face
- Normalize raw data to canonical schema
- Expose repository interface for downstream use

### Tasks

- Implement `src/data/loader.py`:
  - Load dataset from `HF_DATASET_ID`
  - Convert to DataFrame/list of dicts
- Implement `src/data/preprocessor.py`:
  - Standardize fields: `id`, `name`, `location`, `cuisines`, `cost_for_two`, `budget_tier`, `rating`
  - Normalize strings (trim/case)
  - Split multi-cuisine values into list
  - Coerce numeric fields and handle nulls
  - Derive `budget_tier` from threshold config if required
- Implement `src/data/repository.py`:
  - `get_all()`, `filter(predicate)`, `get_by_ids(ids)`
- Add unit tests for schema mapping and preprocessing edge cases

### Deliverables

- Canonicalized in-memory restaurant store
- Test fixtures and preprocessing tests

### Exit Criteria

- Dataset loads without manual edits
- At least 95%+ rows (or defined threshold) parse without fatal errors
- Repository methods return deterministic results

---

## Phase 2: Preference Parser and Deterministic Filter Pipeline

### Objectives

- Convert raw user input into validated preferences
- Produce high-quality candidate set before LLM call

### Tasks

- Implement `src/models/preferences.py` (`UserPreferences`)
- Implement validation/parsing in parser module:
  - Validate `location`, `budget`, `cuisine`, `min_rating`
  - Normalize cuisine inputs and optional synonyms
  - Support optional `additional_preferences`
- Implement `src/services/filter.py` pipeline:
  1. Location match
  2. Minimum rating
  3. Cuisine match
  4. Budget match
  5. Top-K truncation by rating
- Add fallback behavior:
  - Optional relaxation of cuisine/budget
  - Empty-state return if still zero matches
- Return filter metadata (`counts`, relaxed constraints, warnings)
- Add unit tests for each filter step + fallback scenarios

### Deliverables

- Stable pre-LLM candidate generation
- Filter metadata for UI messaging

### Exit Criteria

- Given representative test inputs, filter returns expected candidates
- Empty and no-match paths are handled without exceptions

---

## Phase 3: Prompt Builder and LLM Recommendation Engine

### Objectives

- Generate grounded prompts from structured candidates
- Obtain ranked recommendations and explanations via the **Groq** API
- Validate and merge responses with source records

### Tasks

- Implement `src/services/prompt_builder.py`:
  - Build system/task prompt from preferences + candidates
  - Enforce "rank only from provided candidates"
  - Request structured JSON output
- Implement `src/services/llm_client.py`:
  - Provider abstraction with timeout/retry handling
  - **Groq client** using the `groq` SDK (`Groq(api_key=...)`)
  - Model config via env (`LLM_MODEL`, default `llama-3.3-70b-versatile`)
  - Keep `StubLLMClient` for unit tests (no live API key required)
- Implement `src/services/recommendation_engine.py`:
  - Call Groq via `LLMClient`
  - Parse schema-compliant response
  - Validate `restaurant_id` against candidate IDs
  - Drop hallucinated IDs
  - Merge with repository fields for display
- Implement fallback behavior:
  - Timeout/invalid JSON -> deterministic ranking by rating
  - Explanations optional when degraded
- Add tests with mocked LLM responses (success, malformed, hallucinated IDs, timeout)

### Deliverables

- End-to-end recommendation logic (service-level, no UI required yet)
- Working `GroqLLMClient` implementation
- Robust parsing and failure handling

### Exit Criteria

- Service returns ranked cards for valid user requests using Groq (or stub in tests)
- All critical failure modes degrade gracefully

---

## Phase 4: Presentation Layer and User Interaction

### Objectives

- Provide user-facing interface for preference collection and result display
- Wire the UI to the recommendation pipeline using **Groq** as the live LLM provider
- Keep UI adapter thin and decoupled from core logic

### Tasks

- Choose MVP interface:
  - `CLI` for fastest path, or
  - `Streamlit` for richer demo
- Implement `GroqLLMClient` wiring in orchestration layer (`recommendation_service.py`):
  - Read `GROQ_API_KEY` and `LLM_MODEL` from config
  - Instantiate Groq client and pass to `generate_recommendations`
  - Surface clear error when API key is missing
- Implement presentation adapter in `src/presentation/`
- Input form/arguments:
  - location (dropdown of unique locations from dataset in Streamlit, argument for CLI), budget, cuisine(s), minimum rating, additional preferences
- Output cards/list:
  - name, cuisine, rating, estimated cost, explanation, optional summary
- Show warning/fallback metadata (e.g., "budget relaxed due to no exact matches", "AI unavailable—ranked by rating")
- Add basic UX validations and empty-state messaging
- Manual smoke test with live Groq API key

### Deliverables

- Runnable end-user interface powered by Groq
- Human-readable recommendation output aligned with problem statement

### Exit Criteria

- User can submit preferences and get Groq-generated results without touching code
- Output includes all mandatory fields from context
- App degrades gracefully when Groq is unavailable

---

## Phase 5: QA, Testing, and MVP Stabilization

### Objectives

- Validate correctness, resilience, and maintainability before release

### Tasks

- Complete test suite:
  - Unit: parser, filter, preprocessor, prompt builder
  - Integration: `recommendation_service` with fixture dataset + mocked LLM
- Add smoke test script for E2E local run
- Add structured logging around:
  - candidate counts
  - LLM latency
  - parse/validation failures
- Tune runtime params:
  - `MAX_CANDIDATES`
  - `TOP_K`
  - timeout/retry values
- Validate non-functional targets:
  - acceptable latency (MVP target <10s)
  - graceful degradation when LLM fails

### Deliverables

- MVP release candidate
- Test report + known limitations list

### Exit Criteria

- Core user journeys pass
- No critical defects in filtering/ranking paths
- Failures are handled with user-visible, safe fallback

---

## Phase 6 (Optional): Productionization and Scale

### Objectives

- Improve operational robustness and readiness for wider usage

### Tasks

- Add persistent cache (SQLite/Parquet) for faster startup
- Add API layer (`FastAPI`) if multiple UIs/clients are needed
- Add monitoring dashboards and token/cost tracking
- Add CI pipeline:
  - lint
  - tests
  - packaging checks
- Add deployment assets (Dockerfile, environment profiles)
- Add user feedback loop for recommendation quality improvements

### Deliverables

- Deployment-ready package with observability baseline

### Exit Criteria

- Repeatable deploy path exists
- Runtime behavior is measurable and alertable

---

## Suggested Sprint Breakdown (Example: 2 Weeks)


| Sprint Day | Focus                             |
| ---------- | --------------------------------- |
| Day 1      | Phase 0 setup                     |
| Day 2-3    | Phase 1 ingestion + preprocessing |
| Day 4-5    | Phase 2 parser + filter           |
| Day 6-8    | Phase 3 prompt + LLM engine       |
| Day 9-10   | Phase 4 UI integration            |
| Day 11-12  | Phase 5 testing + hardening       |
| Day 13-14  | Buffer + demo + documentation     |


---

## RACI-lite Ownership Suggestion


| Workstream                    | Primary Owner                   | Secondary        |
| ----------------------------- | ------------------------------- | ---------------- |
| Data ingestion/preprocessing  | Data/Backend Engineer           | QA               |
| Parser/filter service         | Backend Engineer                | QA               |
| Prompt + Groq LLM integration | AI Engineer                     | Backend Engineer |
| UI/presentation               | Frontend or Full-stack Engineer | AI Engineer      |
| Testing and release           | QA/All                          | Tech Lead        |


---

## Risks and Mitigation


| Risk                            | Impact                | Mitigation                                                       |
| ------------------------------- | --------------------- | ---------------------------------------------------------------- |
| Dataset schema drift            | Ingestion breaks      | Schema mapping layer + defensive defaults                        |
| LLM non-deterministic output    | Parse failures        | JSON schema validation + retry/repair + fallback                 |
| Groq API latency or rate limits | Poor UX / throttling  | Candidate truncation, retry with backoff, deterministic fallback |
| No exact filter matches         | Empty recommendations | Controlled filter relaxation + user messaging                    |
| Hallucinated restaurants        | Trust erosion         | Candidate-ID validation and strict merge logic                   |


---

## Definition of Done (MVP)

MVP is complete when:

- User can submit preferences and receive top-K recommendations
- Every recommendation shows name, cuisine, rating, cost, explanation
- LLM output is grounded to filtered candidate IDs
- Failure modes (timeout/invalid JSON/no match) are gracefully handled
- Core tests pass and docs (`context.md`, `architecture.md`, this plan) are consistent

