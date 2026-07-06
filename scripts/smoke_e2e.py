"""End-to-end smoke test: load parquet, filter, and recommend (live Groq if configured)."""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import Settings
from src.observability import setup_logging
from src.presentation.formatters import format_service_result
from src.services.recommendation_service import create_default_service

LATENCY_BUDGET_SECONDS = 10.0


def main() -> int:
    setup_logging()
    settings = Settings.from_env()

    if not settings.parquet_path.exists():
        print(f"FAIL: Missing {settings.parquet_path}. Run scripts/generate_restaurant_parquet.py")
        return 1

    print("Loading restaurant data and running recommendation pipeline...")
    print(f"  Parquet: {settings.parquet_path}")
    print(f"  LLM: {settings.llm_provider} / {settings.llm_model}")
    print(f"  Groq configured: {'yes' if settings.groq_api_key else 'no (fallback mode)'}")

    service = create_default_service()
    prefs = {
        "location": "BTM",
        "budget": "medium",
        "cuisine": "Italian",
        "min_rating": 4.0,
        "additional_preferences": "family-friendly",
    }

    started = time.perf_counter()
    try:
        result = service.recommend(prefs)
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1
    elapsed = time.perf_counter() - started

    print(format_service_result(result))
    print(f"\nElapsed: {elapsed:.2f}s")

    if elapsed > LATENCY_BUDGET_SECONDS:
        print(f"WARN: Exceeded MVP latency budget ({LATENCY_BUDGET_SECONDS}s)")
    else:
        print(f"PASS: Within MVP latency budget ({LATENCY_BUDGET_SECONDS}s)")

    if not result.recommendation.recommendations:
        print("FAIL: No recommendations returned")
        return 1

    print("PASS: E2E smoke test completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
