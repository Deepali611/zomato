import pytest

from src.models.preferences import (
    PreferenceValidationError,
    parse_user_preferences,
)


def test_parse_user_preferences_success():
    prefs = parse_user_preferences(
        {
            "location": " Bangalore ",
            "budget": "MEDIUM",
            "cuisine": "Italian/Chinese",
            "min_rating": "4.0",
            "additional_preferences": "quick service",
        }
    )
    assert prefs.location == "Bangalore"
    assert prefs.budget == "medium"
    assert set(c.lower() for c in prefs.cuisines) == {"italian", "chinese"}
    assert prefs.min_rating == 4.0


def test_parse_user_preferences_invalid_budget():
    with pytest.raises(PreferenceValidationError):
        parse_user_preferences(
            {
                "location": "Delhi",
                "budget": "cheap",
                "cuisine": "Indian",
                "min_rating": 4.0,
            }
        )


def test_parse_user_preferences_invalid_rating_range():
    with pytest.raises(PreferenceValidationError):
        parse_user_preferences(
            {
                "location": "Delhi",
                "budget": "low",
                "cuisine": "Indian",
                "min_rating": 10,
            }
        )

