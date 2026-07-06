from src.data.preprocessor import (
    preprocess_row,
    preprocess_rows,
    _split_cuisines,
    _parse_float,
    PreprocessingError,
)


def test_split_cuisines_handles_commas_and_slashes_and_pipes():
    raw = "Italian/Chinese, Continental | Mexican"
    cuisines = _split_cuisines(raw)
    assert set(c.lower() for c in cuisines) == {
        "italian",
        "chinese",
        "continental",
        "mexican",
    }


def test_parse_float_handles_invalid_and_nan():
    assert _parse_float(None) is None
    assert _parse_float("") is None
    assert _parse_float("abc") is None
    assert _parse_float("4.5") == 4.5


def test_preprocess_row_requires_name_and_location():
    try:
        preprocess_row({})
    except PreprocessingError:
        pass
    else:
        raise AssertionError("Expected PreprocessingError for missing name/location")


def test_preprocess_rows_counts_failures():
    rows = [
        {"name": "A", "location": "City", "cuisines": "Italian", "rating": "4.0"},
        {},  # invalid
    ]
    restaurants, failed = preprocess_rows(rows)
    assert len(restaurants) == 1
    assert failed == 1

