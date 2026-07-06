from __future__ import annotations

from typing import Protocol


class LLMClientError(RuntimeError):
    """Base exception for LLM client failures."""


class LLMTimeoutError(LLMClientError):
    """Raised when LLM invocation times out."""


class LLMClient(Protocol):
    """
    Thin abstraction for model providers.

    Implementations should return raw response text (ideally JSON string).
    """

    def complete(self, prompt: str) -> str:
        raise NotImplementedError


class StubLLMClient:
    """
    Utility LLM client for local development/tests.
    """

    def __init__(self, response: str) -> None:
        self.response = response

    def complete(self, prompt: str) -> str:  # noqa: ARG002
        return self.response


class GroqLLMClient:
    """Groq-backed LLM client for live recommendations."""

    def __init__(
        self,
        api_key: str,
        model: str,
        *,
        timeout_seconds: float = 30.0,
    ) -> None:
        try:
            from groq import Groq  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise LLMClientError(
                "Groq SDK is not installed. Run `pip install groq`."
            ) from exc

        self._client = Groq(api_key=api_key, timeout=timeout_seconds)
        self._model = model
        self._timeout = timeout_seconds

    def complete(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a restaurant recommendation assistant. "
                            "Respond with valid JSON only."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
        except Exception as exc:  # pragma: no cover - provider-specific errors
            message = str(exc).lower()
            if "timeout" in message or "timed out" in message:
                raise LLMTimeoutError(str(exc)) from exc
            raise LLMClientError(str(exc)) from exc

        content = response.choices[0].message.content
        if not content:
            raise LLMClientError("Groq returned an empty response.")
        return content


def build_groq_client(
    api_key: str | None,
    model: str,
    *,
    timeout_seconds: float = 30.0,
) -> GroqLLMClient | None:
    """
    Create a Groq client when an API key is configured.

    Returns None when the key is missing so callers can degrade gracefully.
    """
    if not api_key:
        return None
    return GroqLLMClient(
        api_key=api_key,
        model=model,
        timeout_seconds=timeout_seconds,
    )

