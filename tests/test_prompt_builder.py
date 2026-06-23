from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant
from src.services.prompt_builder import build_recommendation_prompt


def test_build_recommendation_prompt_includes_preferences_and_candidates():
    prefs = UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisines=["Italian"],
        min_rating=4.0,
        additional_preferences="family-friendly",
    )
    candidates = [
        Restaurant(
            id="abc",
            name="Test Place",
            location="Bangalore",
            cuisines=["Italian"],
            budget_tier="medium",
            rating=4.5,
            cost_for_two=600,
        )
    ]

    payload = build_recommendation_prompt(prefs, candidates, top_k=3)

    assert "Bangalore" in payload.prompt
    assert "Italian" in payload.prompt
    assert "family-friendly" in payload.prompt
    assert '"id": "abc"' in payload.prompt or '"id":"abc"' in payload.prompt.replace(" ", "")
    assert "Rank top 3" in payload.prompt
    assert "recommendations" in payload.expected_schema_hint
