"""
Preprocess raw Zomato dataset rows into the canonical `Restaurant` schema.

Responsibilities:
- Standardize fields: id, name, location, cuisines, cost_for_two, budget_tier, rating
- Normalize strings (trim/case)
- Split multi-cuisine values into a list
- Coerce numeric fields and handle nulls
- Derive budget_tier from threshold config when needed
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Optional, Tuple
import math
import uuid

from src.models.restaurant import Restaurant


class PreprocessingError(RuntimeError):
    """Raised when a row cannot be converted into a Restaurant."""


def _normalize_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_location(value: Any) -> str:
    # Simple normalization: trim; further canonicalization can be layered later.
    return _normalize_string(value)


def _parse_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    text = str(value).strip().replace(",", "")
    try:
        f = float(text)
    except (TypeError, ValueError):
        return None
    if math.isnan(f):
        return None
    return f


def _parse_rating(value: Any) -> Optional[float]:
    """Parse Zomato-style ratings such as '4.1/5', 'NEW', or '-'."""
    if value is None or value == "":
        return None
    text = str(value).strip()
    if text.upper() in {"NEW", "-", "NAN"}:
        return None
    if "/" in text:
        text = text.split("/", 1)[0].strip()
    return _parse_float(text)


def _split_cuisines(value: Any) -> List[str]:
    """
    Split a raw cuisine field into a list.

    The dataset commonly uses comma-separated cuisine strings; we also handle
    "/", "|" as secondary delimiters.
    """
    if value is None:
        return []

    text = str(value)
    for delimiter in ["/", "|"]:
        text = text.replace(delimiter, ",")

    parts = [part.strip() for part in text.split(",")]
    # Drop empties and deduplicate (case-insensitive)
    seen = set()
    cuisines: List[str] = []
    for p in parts:
        if not p:
            continue
        key = p.lower()
        if key in seen:
            continue
        seen.add(key)
        cuisines.append(p)
    return cuisines


def _derive_budget_tier(
    cost_for_two: Optional[float],
    low_threshold: float = 400.0,
    high_threshold: float = 800.0,
) -> Optional[str]:
    """
    Derive a budget tier from numeric cost, using simple thresholds.

    Thresholds are parameters so they can be wired to config later.
    """
    if cost_for_two is None:
        return None
    if cost_for_two <= low_threshold:
        return "low"
    if cost_for_two <= high_threshold:
        return "medium"
    return "high"


def _extract_id(raw: Dict[str, Any]) -> str:
    """
    Extract or generate a stable-ish ID for a restaurant.

    Priority:
    - existing 'id' if present
    - otherwise UUID5 over (name, location)
    """
    if "id" in raw and raw["id"]:
        return str(raw["id"])

    name = _normalize_string(raw.get("name"))
    location = _normalize_location(raw.get("location"))
    # Namespace-based UUID to keep it deterministic for same (name, location)
    base = f"{name}|{location}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, base))


def preprocess_row(
    raw: Dict[str, Any],
    *,
    low_threshold: float = 400.0,
    high_threshold: float = 800.0,
) -> Restaurant:
    """
    Convert a single raw dataset row into a `Restaurant`.

    Raises `PreprocessingError` if mandatory fields are missing.
    """
    name = _normalize_string(raw.get("name"))
    location = _normalize_location(raw.get("location"))

    if not name or not location:
        raise PreprocessingError("Missing mandatory restaurant `name` or `location`.")

    cuisines = _split_cuisines(raw.get("cuisines") or raw.get("cuisine"))
    cost_for_two = _parse_float(
        raw.get("approx_cost(for two people)")
        or raw.get("approx_cost_for_two")
        or raw.get("cost_for_two")
    )
    rating = _parse_rating(
        raw.get("rating") or raw.get("aggregate_rating") or raw.get("rate")
    )

    # Allow pre-existing budget tier, otherwise derive from cost.
    budget_tier_raw = _normalize_string(
        raw.get("budget_tier") or raw.get("price_range")
    )
    if budget_tier_raw.lower() in {"low", "medium", "high"}:
        budget_tier: Optional[str] = budget_tier_raw.lower()
    else:
        budget_tier = _derive_budget_tier(
            cost_for_two, low_threshold=low_threshold, high_threshold=high_threshold
        )

    # Keep a copy of the original raw row for potential prompt context.
    restaurant = Restaurant(
        id=_extract_id(raw),
        name=name,
        location=location,
        cuisines=cuisines,
        cost_for_two=cost_for_two,
        budget_tier=budget_tier,
        rating=rating,
        raw_metadata=dict(raw),
    )
    return restaurant


def preprocess_rows(
    rows: Iterable[Dict[str, Any]],
    *,
    low_threshold: float = 400.0,
    high_threshold: float = 800.0,
) -> Tuple[List[Restaurant], int]:
    """
    Convert an iterable of raw rows into a list of `Restaurant` objects.

    Returns `(restaurants, failed_count)` so callers can track error rates.
    """
    restaurants: List[Restaurant] = []
    failed = 0
    for raw in rows:
        try:
            restaurants.append(
                preprocess_row(
                    raw,
                    low_threshold=low_threshold,
                    high_threshold=high_threshold,
                )
            )
        except PreprocessingError:
            failed += 1
    return restaurants, failed


def restaurant_to_dict(restaurant: Restaurant) -> Dict[str, Any]:
    """
    Helper to convert a Restaurant dataclass to a plain dict, useful for tests
    and potential serialization.
    """
    return asdict(restaurant)

