# Test Report

- **Generated:** 2026-07-06T05:04:48.736609+00:00
- **Status:** PASSED
- **JUnit XML:** `docs\test-results.xml`

## Command

```bash
python scripts/run_tests.py
```

## Output (last run)

```
============================= test session starts =============================
platform win32 -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0 -- C:\Users\patil\Downloads\zomato\zomato\.python-embed\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\patil\Downloads\zomato\zomato
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.13.0
collecting ... collected 30 items / 1 deselected / 29 selected

tests/test_config.py::test_settings_from_env_reads_groq_key PASSED       [  3%]
tests/test_config.py::test_settings_strips_placeholder_prefix PASSED     [  6%]
tests/test_filter.py::test_apply_filters_happy_path PASSED               [ 10%]
tests/test_filter.py::test_apply_filters_relaxes_budget_when_no_exact_budget_match PASSED [ 13%]
tests/test_filter.py::test_apply_filters_returns_empty_without_relaxation PASSED [ 17%]
tests/test_filter.py::test_apply_filters_truncates_to_max_candidates_sorted_by_rating PASSED [ 20%]
tests/test_integration.py::test_integration_happy_path PASSED            [ 24%]
tests/test_integration.py::test_integration_llm_failure_degrades_gracefully PASSED [ 27%]
tests/test_integration.py::test_integration_empty_location_returns_empty PASSED [ 31%]
tests/test_integration.py::test_integration_logs_filter_complete PASSED  [ 34%]
tests/test_integration.py::test_integration_timeout_and_error_fallback[_FailingLLMClient] PASSED [ 37%]
tests/test_integration.py::test_integration_timeout_and_error_fallback[_TimeoutLLMClient] PASSED [ 41%]
tests/test_preferences.py::test_parse_user_preferences_success PASSED    [ 44%]
tests/test_preferences.py::test_parse_user_preferences_invalid_budget PASSED [ 48%]
tests/test_preferences.py::test_parse_user_preferences_invalid_rating_range PASSED [ 51%]
tests/test_preprocessor.py::test_split_cuisines_handles_commas_and_slashes_and_pipes PASSED [ 55%]
tests/test_preprocessor.py::test_parse_float_handles_invalid_and_nan PASSED [ 58%]
tests/test_preprocessor.py::test_preprocess_row_requires_name_and_location PASSED [ 62%]
tests/test_preprocessor.py::test_preprocess_rows_counts_failures PASSED  [ 65%]
tests/test_prompt_builder.py::test_build_recommendation_prompt_includes_preferences_and_candidates PASSED [ 68%]
tests/test_recommendation_engine.py::test_generate_recommendations_success PASSED [ 72%]
tests/test_recommendation_engine.py::test_generate_recommendations_drops_hallucinated_id PASSED [ 75%]
tests/test_recommendation_engine.py::test_generate_recommendations_invalid_json_then_repair PASSED [ 79%]
tests/test_recommendation_engine.py::test_generate_recommendations_timeout_fallback PASSED [ 82%]
tests/test_recommendation_service.py::test_recommend_without_llm_uses_fallback PASSED [ 86%]
tests/test_recommendation_service.py::test_recommend_with_stub_llm PASSED [ 89%]
tests/test_repository.py::test_get_all_returns_all_items PASSED          [ 93%]
tests/test_repository.py::test_filter_applies_predicate PASSED           [ 96%]
tests/test_repository.py::test_get_by_ids_preserves_order_and_skips_unknown PASSED [100%]

- generated xml file: C:\Users\patil\Downloads\zomato\zomato\docs\test-results.xml -
====================== 29 passed, 1 deselected in 17.76s ======================

```
