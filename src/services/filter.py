from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant


@dataclass
class FilterMetadata:
    total_rows: int
    after_location: int
    after_rating: int
    after_cuisine: int
    after_budget: int
    final_count: int
    relaxed_constraints: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def _contains_ci(haystack: str, needle: str) -> bool:
    return needle.lower() in haystack.lower()


def _location_filter(rows: Sequence[Restaurant], location: str) -> List[Restaurant]:
    exact = [r for r in rows if r.location.strip().lower() == location.strip().lower()]
    if exact:
        return exact
    return [r for r in rows if _contains_ci(r.location, location)]


def _rating_filter(rows: Sequence[Restaurant], min_rating: float) -> List[Restaurant]:
    return [r for r in rows if r.rating is not None and r.rating >= min_rating]


def _cuisine_filter(rows: Sequence[Restaurant], cuisines: Sequence[str]) -> List[Restaurant]:
    target = {c.lower() for c in cuisines}
    return [
        r
        for r in rows
        if any(c.lower() in target for c in r.cuisines)
    ]


def _budget_filter(rows: Sequence[Restaurant], budget: str) -> List[Restaurant]:
    return [r for r in rows if (r.budget_tier or "").lower() == budget.lower()]


def _sort_for_truncation(rows: Sequence[Restaurant]) -> List[Restaurant]:
    # Null rating is treated as lowest.
    return sorted(rows, key=lambda r: (r.rating is not None, r.rating or -1.0), reverse=True)


def apply_filters(
    restaurants: Sequence[Restaurant],
    preferences: UserPreferences,
    *,
    max_candidates: int = 20,
    relax_on_empty: bool = True,
) -> Tuple[List[Restaurant], FilterMetadata]:
    """
    Deterministic filtering pipeline for phase 2.

    Order:
    1) location
    2) min rating
    3) cuisine
    4) budget
    5) truncate to max candidates by rating

    Relaxation behavior when no matches (if enabled):
    - Drop budget filter first
    - Then drop cuisine filter
    """
    total_rows = len(restaurants)
    after_location_rows = _location_filter(restaurants, preferences.location)
    after_rating_rows = _rating_filter(after_location_rows, preferences.min_rating)
    after_cuisine_rows = _cuisine_filter(after_rating_rows, preferences.cuisines)
    after_budget_rows = _budget_filter(after_cuisine_rows, preferences.budget)

    relaxed: List[str] = []
    warnings: List[str] = []

    final_rows = after_budget_rows

    if not final_rows and relax_on_empty:
        no_budget_rows = after_cuisine_rows
        if no_budget_rows:
            final_rows = no_budget_rows
            relaxed.append("budget")
            warnings.append("No exact budget matches; budget filter was relaxed.")

    if not final_rows and relax_on_empty:
        no_cuisine_rows = after_rating_rows
        if no_cuisine_rows:
            final_rows = _budget_filter(no_cuisine_rows, preferences.budget)
            if final_rows:
                relaxed.append("cuisine")
                warnings.append("No cuisine matches; cuisine filter was relaxed.")
            else:
                # If budget still kills results, relax both.
                final_rows = no_cuisine_rows
                relaxed.extend(["cuisine", "budget"])
                warnings.append(
                    "No cuisine and budget matches together; cuisine and budget were relaxed."
                )

    sorted_rows = _sort_for_truncation(final_rows)
    if len(sorted_rows) > max_candidates:
        sorted_rows = sorted_rows[:max_candidates]
        warnings.append(
            f"Candidate set truncated to top {max_candidates} restaurants by rating."
        )

    metadata = FilterMetadata(
        total_rows=total_rows,
        after_location=len(after_location_rows),
        after_rating=len(after_rating_rows),
        after_cuisine=len(after_cuisine_rows),
        after_budget=len(after_budget_rows),
        final_count=len(sorted_rows),
        relaxed_constraints=relaxed,
        warnings=warnings,
    )
    return sorted_rows, metadata

