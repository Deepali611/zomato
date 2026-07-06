from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant
from src.services.llm_client import LLMClientError, LLMTimeoutError
from src.services.recommendation_engine import generate_recommendations


class _SequenceClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = 0

    def complete(self, prompt: str) -> str:  # noqa: ARG002
        self.calls += 1
        if not self._responses:
            raise LLMClientError("No more responses")
        nxt = self._responses.pop(0)
        if isinstance(nxt, Exception):
            raise nxt
        return nxt


def _prefs() -> UserPreferences:
    return UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisines=["Italian"],
        min_rating=4.0,
    )


def _candidates():
    return [
        Restaurant(
            id="r1",
            name="A",
            location="Bangalore",
            cuisines=["Italian"],
            budget_tier="medium",
            rating=4.7,
            cost_for_two=700,
        ),
        Restaurant(
            id="r2",
            name="B",
            location="Bangalore",
            cuisines=["Italian"],
            budget_tier="medium",
            rating=4.3,
            cost_for_two=500,
        ),
    ]


def test_generate_recommendations_success():
    client = _SequenceClient(
        [
            '{"summary":"Top picks","recommendations":[{"restaurant_id":"r1","rank":1,"explanation":"Great fit"}]}'
        ]
    )
    result = generate_recommendations(_prefs(), _candidates(), client, top_k=1)
    assert result.degraded is False
    assert len(result.recommendations) == 1
    assert result.recommendations[0].restaurant_id == "r1"
    assert result.recommendations[0].name == "A"


def test_generate_recommendations_drops_hallucinated_id():
    client = _SequenceClient(
        [
            '{"summary":"x","recommendations":[{"restaurant_id":"fake","rank":1,"explanation":"x"},{"restaurant_id":"r2","rank":2,"explanation":"ok"}]}'
        ]
    )
    result = generate_recommendations(_prefs(), _candidates(), client, top_k=1)
    assert len(result.recommendations) == 1
    assert result.recommendations[0].restaurant_id == "r2"
    assert any("Dropped" in w for w in result.warnings)


def test_generate_recommendations_invalid_json_then_repair():
    client = _SequenceClient(
        [
            "not-json",
            '{"summary":null,"recommendations":[{"restaurant_id":"r1","rank":1,"explanation":"fixed"}]}',
        ]
    )
    result = generate_recommendations(_prefs(), _candidates(), client, top_k=1)
    assert client.calls == 2
    assert result.degraded is False
    assert result.recommendations[0].restaurant_id == "r1"


def test_generate_recommendations_timeout_fallback():
    client = _SequenceClient([LLMTimeoutError("timeout")])
    result = generate_recommendations(_prefs(), _candidates(), client, top_k=2)
    assert result.degraded is True
    assert len(result.recommendations) == 2
    assert result.recommendations[0].restaurant_id == "r1"

