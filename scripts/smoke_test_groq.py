"""Live smoke test: one real Groq API call using .env credentials."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import Settings
from src.services.llm_client import build_groq_client, LLMClientError


def main() -> int:
    settings = Settings.from_env()
    if not settings.groq_api_key:
        print("FAIL: GROQ_API_KEY not found in .env")
        return 1

    print(f"Provider: {settings.llm_provider}")
    print(f"Model: {settings.llm_model}")

    client = build_groq_client(
        settings.groq_api_key,
        settings.llm_model,
        timeout_seconds=settings.llm_timeout_seconds,
    )
    if client is None:
        print("FAIL: Could not create Groq client")
        return 1

    prompt = (
        'Return JSON only: {"status": "ok", "message": "Groq is working"}'
    )
    try:
        response = client.complete(prompt)
    except LLMClientError as exc:
        print(f"FAIL: Groq API error: {exc}")
        return 1

    print("SUCCESS: Groq API responded.")
    print(f"Response preview: {response[:200]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
