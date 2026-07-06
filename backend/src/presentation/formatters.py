"""Format recommendation output for CLI and Streamlit."""

from __future__ import annotations

from typing import List

from src.models.recommendation import RecommendationItem, RecommendationResult
from src.services.recommendation_service import RecommendationServiceResult


def _format_cost(cost: float | None) -> str:
    if cost is None:
        return "Not available"
    return f"₹{cost:,.0f} (for two)"


def _format_rating(rating: float | None) -> str:
    if rating is None:
        return "Not available"
    return f"{rating:.1f}"


def format_recommendation_card(item: RecommendationItem) -> str:
    cuisines = ", ".join(item.cuisines) if item.cuisines else "Not available"
    lines = [
        f"#{item.rank} {item.name}",
        f"  Cuisine: {cuisines}",
        f"  Rating: {_format_rating(item.rating)}",
        f"  Estimated cost: {_format_cost(item.cost_for_two)}",
        f"  Why: {item.explanation}",
    ]
    return "\n".join(lines)


def format_service_result(result: RecommendationServiceResult) -> str:
    parts: List[str] = []

    if result.messages:
        parts.append("Notes:")
        for msg in result.messages:
            parts.append(f"  - {msg}")
        parts.append("")

    rec = result.recommendation
    if rec.summary:
        parts.append(f"Summary: {rec.summary}")
        parts.append("")

    if not rec.recommendations:
        parts.append("No recommendations found.")
        return "\n".join(parts)

    if rec.degraded:
        parts.append("(AI unavailable — showing rating-based fallback)")
        parts.append("")

    parts.append("Recommendations:")
    for item in rec.recommendations:
        parts.append(format_recommendation_card(item))
        parts.append("")

    return "\n".join(parts).rstrip()
