"""Integration tests: full recommendation flow with fixture data."""

import json

import pytest

from src.data.repository import RestaurantRepository
from src.services.llm_client import LLMClientError, LLMTimeoutError, StubLLMClient
from src.services.recommendation_service import RecommendationService


class _FailingLLMClient:
    def complete(self, prompt: str) -> str:  # noqa: ARG002
        raise LLMClientError("simulated outage")


class _TimeoutLLMClient:
    def complete(self, prompt: str) -> str:  # noqa: ARG002
        raise LLMTimeoutError("simulated timeout")


def test_integration_happy_path(sample_restaurants, test_settings):
    stub = StubLLMClient(
        json.dumps(
            {
                "summary": "Top Italian spots in Bangalore",
                "recommendations": [
                    {
                        "restaurant_id": "r1",
                        "rank": 1,
                        "explanation": "Strong Italian menu and high rating.",
                    }
                ],
            }
        )
    )
    service = RecommendationService(
        repository=RestaurantRepository(sample_restaurants),
        settings=test_settings,
        llm_client=stub,
    )
    result = service.recommend(
        {
            "location": "Bangalore",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
        }
    )

    assert result.filter_metadata.final_count >= 1
    assert len(result.recommendation.recommendations) >= 1
    item = result.recommendation.recommendations[0]
    assert item.name == "Trattoria Roma"
    assert item.cuisines
    assert item.rating is not None
    assert item.cost_for_two is not None
    assert item.explanation
    assert result.recommendation.degraded is False


def test_integration_llm_failure_degrades_gracefully(sample_restaurants, test_settings):
    service = RecommendationService(
        repository=RestaurantRepository(sample_restaurants),
        settings=test_settings,
        llm_client=_FailingLLMClient(),
    )
    result = service.recommend(
        {
            "location": "Bangalore",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
        }
    )

    assert result.recommendation.degraded is True
    assert len(result.recommendation.recommendations) >= 1


def test_integration_empty_location_returns_empty(sample_restaurants, test_settings):
    service = RecommendationService(
        repository=RestaurantRepository(sample_restaurants),
        settings=test_settings,
        llm_client=StubLLMClient("{}"),
    )
    result = service.recommend(
        {
            "location": "Mumbai",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
        }
    )

    assert result.recommendation.recommendations == []
    assert any("No restaurants" in w for w in result.recommendation.warnings)


def test_integration_logs_filter_complete(sample_restaurants, test_settings, caplog):
    import logging

    caplog.set_level(logging.INFO)
    service = RecommendationService(
        repository=RestaurantRepository(sample_restaurants),
        settings=test_settings,
        llm_client=StubLLMClient(
            '{"summary":null,"recommendations":[{"restaurant_id":"r1","rank":1,"explanation":"ok"}]}'
        ),
    )
    service.recommend(
        {
            "location": "Bangalore",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
        }
    )
    assert any("filter_complete" in r.message for r in caplog.records)


@pytest.mark.parametrize(
    "client_cls",
    [_FailingLLMClient, _TimeoutLLMClient],
)
def test_integration_timeout_and_error_fallback(sample_restaurants, test_settings, client_cls):
    service = RecommendationService(
        repository=RestaurantRepository(sample_restaurants),
        settings=test_settings,
        llm_client=client_cls(),
    )
    result = service.recommend(
        {
            "location": "Bangalore",
            "budget": "medium",
            "cuisine": "Chinese",
            "min_rating": 4.0,
        }
    )
    assert result.recommendation.degraded is True
    assert result.recommendation.recommendations
