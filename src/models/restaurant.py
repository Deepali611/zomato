from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Restaurant:
    """
    Canonical restaurant schema used by the app.

    This mirrors the architecture/context docs:
    - id
    - name
    - location
    - cuisines
    - cost_for_two
    - budget_tier
    - rating
    - raw_metadata
    """

    id: str
    name: str
    location: str
    cuisines: List[str] = field(default_factory=list)
    cost_for_two: Optional[float] = None
    budget_tier: Optional[str] = None  # "low" | "medium" | "high"
    rating: Optional[float] = None
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

