"""
In-memory repository for canonical `Restaurant` objects.

Provides a simple interface for downstream services:
- get_all()
- filter(predicate)
- get_by_ids(ids)
"""

from __future__ import annotations

from typing import Callable, Dict, Iterable, List, Sequence

from src.models.restaurant import Restaurant


class RestaurantRepository:
    """Simple in-memory repository backed by a list and id index."""

    def __init__(self, restaurants: Iterable[Restaurant]) -> None:
        self._restaurants: List[Restaurant] = list(restaurants)
        self._by_id: Dict[str, Restaurant] = {r.id: r for r in self._restaurants}

    def get_all(self) -> List[Restaurant]:
        """Return all restaurants as a new list."""
        return list(self._restaurants)

    def filter(self, predicate: Callable[[Restaurant], bool]) -> List[Restaurant]:
        """
        Return all restaurants that satisfy the given predicate.

        This is intentionally simple; more complex querying can be added later.
        """
        return [r for r in self._restaurants if predicate(r)]

    def get_by_ids(self, ids: Sequence[str]) -> List[Restaurant]:
        """
        Return restaurants matching the given IDs, preserving input order
        and silently skipping unknown IDs.
        """
        return [self._by_id[i] for i in ids if i in self._by_id]

