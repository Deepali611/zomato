"""
Dataset loader for the Zomato restaurant recommendation app.

Responsible for:
- Downloading/loading the Hugging Face dataset identified by HF_DATASET_ID
- Returning raw records (list of dicts) for preprocessing

This module does not enforce the canonical schema; that is handled by
`preprocessor.py`.
"""

from typing import Any, Dict, List, Optional
import os

try:
    from datasets import load_dataset  # type: ignore
except Exception:  # pragma: no cover - optional dependency at import time
    load_dataset = None  # type: ignore


DEFAULT_DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"


class DatasetLoadError(RuntimeError):
    """Raised when the HF dataset cannot be loaded."""


def get_dataset_id(env_var: str = "HF_DATASET_ID") -> str:
    """
    Resolve the dataset identifier from the environment, with a safe default.

    This keeps Phase 1 usable without requiring full config wiring.
    """
    return os.getenv(env_var, DEFAULT_DATASET_ID)


def load_raw_restaurant_records(split: str = "train") -> List[Dict[str, Any]]:
    """
    Load raw restaurant records from the Hugging Face dataset.

    Returns a list of dictionaries, preserving the dataset's original schema.
    """
    if load_dataset is None:
        raise DatasetLoadError(
            "Hugging Face `datasets` library is not available. "
            "Install it with `pip install datasets`."
        )

    dataset_id = get_dataset_id()
    try:
        ds = load_dataset(dataset_id, split=split)
    except Exception as exc:  # pragma: no cover - thin wrapper
        raise DatasetLoadError(
            f"Failed to load dataset '{dataset_id}' (split='{split}'): {exc}"
        ) from exc

    # Convert to plain Python dicts for downstream processing
    return [dict(row) for row in ds]  # type: ignore[return-value]


def load_raw_dataset(
    split: str = "train",
) -> List[Dict[str, Any]]:
    """
    Convenience alias for `load_raw_restaurant_records`.

    This can be useful for tests or scripts that only need raw rows.
    """
    return load_raw_restaurant_records(split=split)

