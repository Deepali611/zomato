from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant
from src.services.filter import apply_filters


def _r(
    id_: str,
    *,
    location: str,
    cuisines: list[str],
    budget_tier: str,
    rating: float,
) -> Restaurant:
    return Restaurant(
        id=id_,
        name=f"R{id_}",
        location=location,
        cuisines=cuisines,
        budget_tier=budget_tier,
        rating=rating,
    )


def test_apply_filters_happy_path():
    rows = [
        _r("1", location="Bangalore", cuisines=["Italian"], budget_tier="medium", rating=4.6),
        _r("2", location="Bangalore", cuisines=["Chinese"], budget_tier="medium", rating=4.4),
        _r("3", location="Delhi", cuisines=["Italian"], budget_tier="medium", rating=4.9),
    ]
    prefs = UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisines=["Italian"],
        min_rating=4.0,
    )

    result, meta = apply_filters(rows, prefs, max_candidates=20, relax_on_empty=True)
    assert [r.id for r in result] == ["1"]
    assert meta.total_rows == 3
    assert meta.final_count == 1


def test_apply_filters_relaxes_budget_when_no_exact_budget_match():
    rows = [
        _r("1", location="Bangalore", cuisines=["Italian"], budget_tier="high", rating=4.5),
    ]
    prefs = UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisines=["Italian"],
        min_rating=4.0,
    )

    result, meta = apply_filters(rows, prefs, relax_on_empty=True)
    assert [r.id for r in result] == ["1"]
    assert "budget" in meta.relaxed_constraints


def test_apply_filters_returns_empty_without_relaxation():
    rows = [
        _r("1", location="Bangalore", cuisines=["Italian"], budget_tier="high", rating=4.5),
    ]
    prefs = UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisines=["Italian"],
        min_rating=4.0,
    )

    result, meta = apply_filters(rows, prefs, relax_on_empty=False)
    assert result == []
    assert meta.final_count == 0


def test_apply_filters_truncates_to_max_candidates_sorted_by_rating():
    rows = [
        _r("1", location="Bangalore", cuisines=["Italian"], budget_tier="medium", rating=4.1),
        _r("2", location="Bangalore", cuisines=["Italian"], budget_tier="medium", rating=4.9),
        _r("3", location="Bangalore", cuisines=["Italian"], budget_tier="medium", rating=4.5),
    ]
    prefs = UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisines=["Italian"],
        min_rating=4.0,
    )

    result, meta = apply_filters(rows, prefs, max_candidates=2, relax_on_empty=True)
    assert [r.id for r in result] == ["2", "3"]
    assert meta.final_count == 2

