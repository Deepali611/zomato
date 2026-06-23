import os

from src.config import Settings


def test_settings_from_env_reads_groq_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_key_123")
    monkeypatch.setenv("LLM_MODEL", "llama-3.3-70b-versatile")
    monkeypatch.setenv("MAX_CANDIDATES", "15")
    monkeypatch.setenv("TOP_K", "3")

    settings = Settings.from_env()

    assert settings.groq_api_key == "gsk_test_key_123"
    assert settings.llm_model == "llama-3.3-70b-versatile"
    assert settings.max_candidates == 15
    assert settings.top_k == 3


def test_settings_strips_placeholder_prefix(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "your_groq_api_key_heregsk_realkey")
    settings = Settings.from_env()
    assert settings.groq_api_key == "gsk_realkey"
