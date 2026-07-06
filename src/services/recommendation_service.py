"""Orchestrates filtering and Groq-powered recommendation generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import Settings
from src.observability import get_logger, log_event, setup_logging
from src.data.loader import load_raw_restaurant_records
from src.data.parquet_exporter import load_restaurants_from_parquet
from src.data.preprocessor import preprocess_rows
from src.data.repository import RestaurantRepository
from src.models.preferences import UserPreferences, parse_user_preferences
from src.models.recommendation import RecommendationResult
from src.models.restaurant import Restaurant
from src.services.filter import FilterMetadata, apply_filters
from src.services.llm_client import LLMClient, build_groq_client
from src.services.recommendation_engine import _deterministic_fallback, generate_recommendations

logger = get_logger(__name__)


@dataclass
class RecommendationServiceResult:
    preferences: UserPreferences
    candidates: List[Restaurant]
    filter_metadata: FilterMetadata
    recommendation: RecommendationResult
    llm_available: bool
    messages: List[str] = field(default_factory=list)


def load_repository(settings: Settings) -> RestaurantRepository:
    """Load restaurants from local parquet when available, else Hugging Face."""
    if settings.parquet_path.exists():
        restaurants = load_restaurants_from_parquet(settings.parquet_path)
        return RestaurantRepository(restaurants)

    raw_rows = load_raw_restaurant_records()
    restaurants, _ = preprocess_rows(
        raw_rows,
        low_threshold=settings.low_budget_max,
        high_threshold=settings.high_budget_max,
    )
    return RestaurantRepository(restaurants)


def build_llm_client(settings: Settings) -> tuple[Optional[LLMClient], Optional[str]]:
    """
    Build the configured LLM client.

    Returns (client, warning_message). Warning is set when Groq is unavailable.
    """
    if settings.llm_provider != "groq":
        return None, f"Unsupported LLM_PROVIDER '{settings.llm_provider}'. Only 'groq' is wired."

    client = build_groq_client(
        settings.groq_api_key,
        settings.llm_model,
        timeout_seconds=settings.llm_timeout_seconds,
    )
    if client is None:
        return None, (
            "GROQ_API_KEY is not set. Recommendations will use rating-based fallback. "
            "Add your key to `.env` (see `.env.example`)."
        )
    return client, None


class RecommendationService:
    """End-to-end recommendation flow for CLI and Streamlit."""

    def __init__(
        self,
        repository: RestaurantRepository,
        settings: Settings | None = None,
        llm_client: LLMClient | None = None,
    ) -> None:
        self.settings = settings or Settings.from_env()
        setup_logging(self.settings.log_level)
        self.repository = repository
        self._llm_client = llm_client
        self._llm_warning: str | None = None
        if self._llm_client is None:
            self._llm_client, self._llm_warning = build_llm_client(self.settings)

    @property
    def llm_warning(self) -> str | None:
        return self._llm_warning

    def recommend(self, raw_preferences: Dict[str, Any]) -> RecommendationServiceResult:
        preferences = parse_user_preferences(raw_preferences)
        messages: List[str] = list(preferences.warnings)

        if self._llm_warning:
            messages.append(self._llm_warning)

        candidates, filter_metadata = apply_filters(
            self.repository.get_all(),
            preferences,
            max_candidates=self.settings.max_candidates,
            relax_on_empty=self.settings.filter_relax_on_empty,
        )
        messages.extend(filter_metadata.warnings)
        log_event(
            logger,
            "filter_complete",
            total_rows=filter_metadata.total_rows,
            after_location=filter_metadata.after_location,
            after_rating=filter_metadata.after_rating,
            after_cuisine=filter_metadata.after_cuisine,
            after_budget=filter_metadata.after_budget,
            final_count=filter_metadata.final_count,
            relaxed=filter_metadata.relaxed_constraints,
        )

        if not candidates:
            log_event(logger, "recommend_empty", reason="no_candidates_after_filter")
            recommendation = RecommendationResult(
                summary=None,
                recommendations=[],
                degraded=False,
                warnings=["No restaurants matched your filters. Try relaxing cuisine, budget, or location."],
            )
            return RecommendationServiceResult(
                preferences=preferences,
                candidates=[],
                filter_metadata=filter_metadata,
                recommendation=recommendation,
                llm_available=self._llm_client is not None,
                messages=messages,
            )

        if self._llm_client is None:
            recommendation = _deterministic_fallback(
                candidates,
                top_k=self.settings.top_k,
                warning="AI unavailable (missing GROQ_API_KEY). Ranked by rating.",
            )
        else:
            recommendation = generate_recommendations(
                preferences,
                candidates,
                self._llm_client,
                top_k=self.settings.top_k,
                max_retries=self.settings.llm_max_retries,
            )

        messages.extend(recommendation.warnings)
        log_event(
            logger,
            "recommend_complete",
            result_count=len(recommendation.recommendations),
            degraded=recommendation.degraded,
            llm_available=self._llm_client is not None,
        )
        return RecommendationServiceResult(
            preferences=preferences,
            candidates=candidates,
            filter_metadata=filter_metadata,
            recommendation=recommendation,
            llm_available=self._llm_client is not None,
            messages=messages,
        )


def create_default_service(parquet_path: Path | None = None) -> RecommendationService:
    settings = Settings.from_env()
    if parquet_path is not None:
        settings = Settings(
            hf_dataset_id=settings.hf_dataset_id,
            llm_provider=settings.llm_provider,
            llm_model=settings.llm_model,
            groq_api_key=settings.groq_api_key,
            max_candidates=settings.max_candidates,
            top_k=settings.top_k,
            filter_relax_on_empty=settings.filter_relax_on_empty,
            low_budget_max=settings.low_budget_max,
            high_budget_max=settings.high_budget_max,
            parquet_path=parquet_path,
            llm_timeout_seconds=settings.llm_timeout_seconds,
            llm_max_retries=settings.llm_max_retries,
            log_level=settings.log_level,
        )
    repository = load_repository(settings)
    return RecommendationService(repository=repository, settings=settings)
