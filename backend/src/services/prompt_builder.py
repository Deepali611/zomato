from __future__ import annotations

from dataclasses import dataclass
import json
from typing import List

from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant


@dataclass
class PromptPayload:
    prompt: str
    expected_schema_hint: str


def build_recommendation_prompt(
    preferences: UserPreferences,
    candidates: List[Restaurant],
    *,
    top_k: int,
) -> PromptPayload:
    """
    Build a grounded prompt that only allows ranking from candidate rows.
    """
    candidate_rows = [
        {
            "id": r.id,
            "name": r.name,
            "location": r.location,
            "cuisines": r.cuisines,
            "rating": r.rating,
            "cost_for_two": r.cost_for_two,
            "budget_tier": r.budget_tier,
        }
        for r in candidates
    ]

    pref_json = {
        "location": preferences.location,
        "budget": preferences.budget,
        "cuisines": preferences.cuisines,
        "min_rating": preferences.min_rating,
        "additional_preferences": preferences.additional_preferences,
    }

    schema_hint = (
        '{"summary": "string or null", "recommendations": '
        '[{"restaurant_id": "string", "rank": 1, "explanation": "string"}]}'
    )

    prompt = (
        "You are a restaurant recommendation assistant.\n"
        "Rank ONLY from the provided candidates. Do not invent restaurants "
        "or attributes. If information is missing, say 'not available'.\n"
        "Return STRICT JSON matching this shape:\n"
        f"{schema_hint}\n\n"
        "User preferences:\n"
        f"{json.dumps(pref_json, ensure_ascii=True)}\n\n"
        "Candidate restaurants:\n"
        f"{json.dumps(candidate_rows, ensure_ascii=True)}\n\n"
        f"Task:\n1) Rank top {top_k} restaurants\n"
        "2) Include concise explanation (1-2 sentences) for each\n"
        "3) Optionally include one-line summary."
    )
    return PromptPayload(prompt=prompt, expected_schema_hint=schema_hint)

