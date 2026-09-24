from python.effective_python.s05_items_13_15 import (
    build_topics,
    get_even_values_from_middle,
    get_slice_examples,
)


def test_build_topics_returns_three_distinct_topics():
    assert build_topics() == ["python", "sql", "pyspark"]


def test_slice_examples():
    values = [10, 20, 30, 40, 50]

    result = get_slice_examples(values)

    assert result["first_three"] == [10, 20, 30]
    assert result["from_third"] == [30, 40, 50]
    assert result["last_two"] == [40, 50]
    assert result["middle"] == [20, 30, 40]
    assert result["copy"] == [10, 20, 30, 40, 50]


def test_slice_copy_is_a_different_list():
    values = [10, 20, 30]

    result = get_slice_examples(values)

    assert result["copy"] == values
    assert result["copy"] is not values


def test_get_even_values_from_middle():
    values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    assert get_even_values_from_middle(values) == [2, 4, 6, 8]
