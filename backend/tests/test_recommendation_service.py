from pathlib import Path

from src.config import Settings
from src.data.repository import RestaurantRepository
from src.models.restaurant import Restaurant
from src.services.llm_client import StubLLMClient
from src.services.recommendation_service import RecommendationService


def _restaurant(id_: str, location: str, cuisines: list[str], budget: str, rating: float) -> Restaurant:
    return Restaurant(
        id=id_,
        name=f"R{id_}",
        location=location,
        cuisines=cuisines,
        budget_tier=budget,
        rating=rating,
        cost_for_two=600,
    )


def test_recommend_without_llm_uses_fallback():
    repo = RestaurantRepository(
        [
            _restaurant("1", "Bangalore", ["Italian"], "medium", 4.5),
            _restaurant("2", "Bangalore", ["Chinese"], "medium", 4.0),
        ]
    )
    settings = Settings(
        hf_dataset_id="x",
        llm_provider="groq",
        llm_model="llama-3.3-70b-versatile",
        groq_api_key=None,
        max_candidates=20,
        top_k=1,
        filter_relax_on_empty=True,
        low_budget_max=400,
        high_budget_max=800,
        parquet_path=Path("data/restaurant.parquet"),
        llm_timeout_seconds=30,
        llm_max_retries=1,
        log_level="WARNING",
    )
    service = RecommendationService(repository=repo, settings=settings, llm_client=None)
    result = service.recommend(
        {
            "location": "Bangalore",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
        }
    )

    assert result.llm_available is False
    assert len(result.recommendation.recommendations) == 1
    assert result.recommendation.recommendations[0].restaurant_id == "1"
    assert result.recommendation.degraded is True
    assert any("GROQ_API_KEY" in m for m in result.messages)


def test_recommend_with_stub_llm():
    repo = RestaurantRepository(
        [_restaurant("1", "Bangalore", ["Italian"], "medium", 4.5)]
    )
    settings = Settings(
        hf_dataset_id="x",
        llm_provider="groq",
        llm_model="llama-3.3-70b-versatile",
        groq_api_key="test-key",
        max_candidates=20,
        top_k=1,
        filter_relax_on_empty=True,
        low_budget_max=400,
        high_budget_max=800,
        parquet_path=Path("data/restaurant.parquet"),
        llm_timeout_seconds=30,
        llm_max_retries=1,
        log_level="WARNING",
    )
    stub = StubLLMClient(
        '{"summary":"Great pick","recommendations":[{"restaurant_id":"1","rank":1,"explanation":"Matches Italian preference."}]}'
    )
    service = RecommendationService(repository=repo, settings=settings, llm_client=stub)
    result = service.recommend(
        {
            "location": "Bangalore",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
        }
    )

    assert result.llm_available is True
    assert result.recommendation.degraded is False
    assert result.recommendation.recommendations[0].explanation == "Matches Italian preference."
