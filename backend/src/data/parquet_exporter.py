"""
Export canonical restaurant records to a Parquet file.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import json

import pandas as pd

from src.data.loader import load_raw_restaurant_records
from src.data.preprocessor import preprocess_rows
from src.models.restaurant import Restaurant


def restaurants_to_dataframe(restaurants: List[Restaurant]) -> pd.DataFrame:
    """Convert Restaurant objects to a flat DataFrame suitable for Parquet."""
    rows = [
        {
            "id": r.id,
            "name": r.name,
            "location": r.location,
            "cuisines": json.dumps(r.cuisines, ensure_ascii=True),
            "cost_for_two": r.cost_for_two,
            "budget_tier": r.budget_tier,
            "rating": r.rating,
        }
        for r in restaurants
    ]
    return pd.DataFrame(rows)


def export_restaurants_parquet(
    output_path: str | Path,
    *,
    split: str = "train",
    low_threshold: float = 400.0,
    high_threshold: float = 800.0,
) -> tuple[Path, int, int]:
    """
    Load HF dataset, preprocess, and write `restaurant.parquet`.

    Returns: (output_path, success_count, failed_count)
    """
    raw_rows = load_raw_restaurant_records(split=split)
    restaurants, failed = preprocess_rows(
        raw_rows,
        low_threshold=low_threshold,
        high_threshold=high_threshold,
    )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    df = restaurants_to_dataframe(restaurants)
    df.to_parquet(out, index=False, engine="pyarrow")

    return out, len(restaurants), failed


def load_restaurants_from_parquet(path: str | Path) -> List[Restaurant]:
    """Load canonical restaurants from a Parquet file."""
    df = pd.read_parquet(path, engine="pyarrow")
    restaurants: List[Restaurant] = []
    for _, row in df.iterrows():
        cuisines_raw = row.get("cuisines", "[]")
        if isinstance(cuisines_raw, str):
            cuisines = json.loads(cuisines_raw)
        else:
            cuisines = list(cuisines_raw) if cuisines_raw is not None else []

        restaurants.append(
            Restaurant(
                id=str(row["id"]),
                name=str(row["name"]),
                location=str(row["location"]),
                cuisines=cuisines,
                cost_for_two=_optional_float(row.get("cost_for_two")),
                budget_tier=_optional_str(row.get("budget_tier")),
                rating=_optional_float(row.get("rating")),
            )
        )
    return restaurants


def _optional_float(value: object) -> Optional[float]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_str(value: object) -> Optional[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    return text or None
