"""Optional live E2E test (requires GROQ_API_KEY and data/restaurant.parquet)."""

from __future__ import annotations

import os
import time

import pytest

from src.config import Settings
from src.services.recommendation_service import create_default_service

pytestmark = pytest.mark.e2e


@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY") and not Settings.from_env().groq_api_key,
    reason="GROQ_API_KEY not configured",
)
@pytest.mark.skipif(
    not Settings.from_env().parquet_path.exists(),
    reason="data/restaurant.parquet missing",
)
def test_live_groq_recommendation_under_latency_budget():
    service = create_default_service()
    started = time.perf_counter()
    result = service.recommend(
        {
            "location": "Bangalore",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
        }
    )
    elapsed = time.perf_counter() - started

    assert result.recommendation.recommendations
    assert result.recommendation.recommendations[0].explanation
    assert elapsed < 15.0, f"E2E took {elapsed:.1f}s (budget 15s for CI variance)"
