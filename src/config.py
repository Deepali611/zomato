"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv() -> None:
    """Load `.env` from project root when python-dotenv is not required."""
    root = Path(__file__).resolve().parents[1]
    env_path = root / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    hf_dataset_id: str
    llm_provider: str
    llm_model: str
    groq_api_key: str | None
    max_candidates: int
    top_k: int
    filter_relax_on_empty: bool
    low_budget_max: float
    high_budget_max: float
    parquet_path: Path
    llm_timeout_seconds: float
    llm_max_retries: int
    log_level: str

    @classmethod
    def from_env(cls) -> Settings:
        _load_dotenv()
        root = Path(__file__).resolve().parents[1]
        api_key = os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY")
        if api_key:
            api_key = api_key.strip()
            if api_key.startswith("your_groq_api_key_here"):
                api_key = api_key.removeprefix("your_groq_api_key_here").strip()
            if api_key in {"", "your_groq_api_key_here"}:
                api_key = None

        return cls(
            hf_dataset_id=os.getenv(
                "HF_DATASET_ID", "ManikaSaini/zomato-restaurant-recommendation"
            ),
            llm_provider=os.getenv("LLM_PROVIDER", "groq").lower(),
            llm_model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
            groq_api_key=api_key,
            max_candidates=_env_int("MAX_CANDIDATES", 20),
            top_k=_env_int("TOP_K", 5),
            filter_relax_on_empty=_env_bool("FILTER_RELAX_ON_EMPTY", True),
            low_budget_max=float(os.getenv("LOW_MAX", "400")),
            high_budget_max=float(os.getenv("HIGH_MAX", "800")),
            parquet_path=root / "data" / "restaurant.parquet",
            llm_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
            llm_max_retries=_env_int("LLM_MAX_RETRIES", 1),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )
