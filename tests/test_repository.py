from src.data.repository import RestaurantRepository
from src.models.restaurant import Restaurant


def _make_restaurant(id_: str, name: str = "R", location: str = "City") -> Restaurant:
    return Restaurant(id=id_, name=name, location=location)


def test_get_all_returns_all_items():
    repo = RestaurantRepository(
        [_make_restaurant("1"), _make_restaurant("2"), _make_restaurant("3")]
    )
    all_items = repo.get_all()
    assert len(all_items) == 3
    assert {r.id for r in all_items} == {"1", "2", "3"}


def test_filter_applies_predicate():
    repo = RestaurantRepository(
        [
            _make_restaurant("1", name="A"),
            _make_restaurant("2", name="B"),
        ]
    )
    only_a = repo.filter(lambda r: r.name == "A")
    assert [r.id for r in only_a] == ["1"]


def test_get_by_ids_preserves_order_and_skips_unknown():
    repo = RestaurantRepository(
        [
            _make_restaurant("1"),
            _make_restaurant("2"),
            _make_restaurant("3"),
        ]
    )
    result = repo.get_by_ids(["3", "x", "1"])
    assert [r.id for r in result] == ["3", "1"]

