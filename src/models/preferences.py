from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional


ALLOWED_BUDGETS = {"low", "medium", "high"}


class PreferenceValidationError(ValueError):
    """Raised when user preference input is invalid."""


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_cuisines(value: Any) -> List[str]:
    if value is None:
        return []

    if isinstance(value, list):
        raw_parts = [str(v) for v in value]
    else:
        text = str(value)
        for delimiter in ["/", "|", ";"]:
            text = text.replace(delimiter, ",")
        raw_parts = text.split(",")

    seen = set()
    cuisines: List[str] = []
    for item in raw_parts:
        cleaned = item.strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        cuisines.append(cleaned)
    return cuisines


@dataclass
class UserPreferences:
    location: str
    budget: str
    cuisines: List[str]
    min_rating: float
    additional_preferences: Optional[str] = None
    # Store user input warnings (e.g. trimmed notes) for optional UI display later
    warnings: List[str] = field(default_factory=list)


def parse_user_preferences(raw: dict[str, Any]) -> UserPreferences:
    """
    Validate and normalize raw user input into UserPreferences.

    Required:
    - location
    - budget in {"low", "medium", "high"}
    - cuisine or cuisines
    - min_rating in [0, 5]
    """
    location = _normalize_text(raw.get("location"))
    if not location:
        raise PreferenceValidationError("`location` is required.")

    budget = _normalize_text(raw.get("budget")).lower()
    if budget not in ALLOWED_BUDGETS:
        raise PreferenceValidationError("`budget` must be one of: low, medium, high.")

    cuisines_input = raw.get("cuisines", raw.get("cuisine"))
    cuisines = _normalize_cuisines(cuisines_input)
    if not cuisines:
        raise PreferenceValidationError("At least one cuisine is required.")

    try:
        min_rating = float(raw.get("min_rating"))
    except (TypeError, ValueError):
        raise PreferenceValidationError("`min_rating` must be a number between 0 and 5.")
    if min_rating < 0 or min_rating > 5:
        raise PreferenceValidationError("`min_rating` must be between 0 and 5.")

    notes = _normalize_text(raw.get("additional_preferences"))
    warnings: List[str] = []
    if notes and len(notes) > 1000:
        notes = notes[:1000]
        warnings.append("additional_preferences was truncated to 1000 characters.")

    return UserPreferences(
        location=location,
        budget=budget,
        cuisines=cuisines,
        min_rating=min_rating,
        additional_preferences=notes or None,
        warnings=warnings,
    )

