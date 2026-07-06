from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RecommendationItem:
    restaurant_id: str
    rank: int
    explanation: str
    name: str
    cuisines: List[str]
    rating: Optional[float]
    cost_for_two: Optional[float]


@dataclass
class RecommendationResult:
    summary: Optional[str]
    recommendations: List[RecommendationItem] = field(default_factory=list)
    degraded: bool = False
    warnings: List[str] = field(default_factory=list)

