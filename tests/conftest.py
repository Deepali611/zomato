import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import Settings
from src.models.restaurant import Restaurant


@pytest.fixture
def sample_restaurants() -> list[Restaurant]:
    return [
        Restaurant(
            id="r1",
            name="Trattoria Roma",
            location="Bangalore",
            cuisines=["Italian", "Continental"],
            budget_tier="medium",
            rating=4.6,
            cost_for_two=700,
        ),
        Restaurant(
            id="r2",
            name="Dragon Wok",
            location="Bangalore",
            cuisines=["Chinese"],
            budget_tier="medium",
            rating=4.4,
            cost_for_two=500,
        ),
        Restaurant(
            id="r3",
            name="Delhi Darbar",
            location="Delhi",
            cuisines=["North Indian"],
            budget_tier="low",
            rating=4.8,
            cost_for_two=350,
        ),
    ]


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    return Settings(
        hf_dataset_id="test/dataset",
        llm_provider="groq",
        llm_model="llama-3.3-70b-versatile",
        groq_api_key="test-key",
        max_candidates=20,
        top_k=2,
        filter_relax_on_empty=True,
        low_budget_max=400,
        high_budget_max=800,
        parquet_path=tmp_path / "missing.parquet",
        llm_timeout_seconds=30,
        llm_max_retries=1,
        log_level="WARNING",
    )
