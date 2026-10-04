import pytest
from python.effective_python.s06_items_16_18 import (
    split_scores,
    number_tasks,
    build_study_plan,
    organize_study_plan,
)


def test_split_scores_nominal():
    assert split_scores([100, 90, 80, 70, 60, 50]) == (
        100,
        [90, 80, 70, 60],
        50,
    )


def test_split_scores_minimal():
    assert split_scores([100, 50]) == (
        100,
        [],
        50,
    )


def test_split_scores_insufficient():
    with pytest.raises(ValueError):
        split_scores([100])


def test_number_tasks():
    tasks = ["SQL", "Python", "PySpark", "Databricks"]

    assert number_tasks(tasks) == [
        (1, "SQL"),
        (2, "Python"),
        (3, "PySpark"),
        (4, "Databricks"),
    ]


def test_build_study_plan_equal_lengths():
    assert build_study_plan(
        ["SQL", "Python", "Databricks"],
        [45, 30, 60],
    ) == [
        ("SQL", 45),
        ("Python", 30),
        ("Databricks", 60),
    ]


def test_build_study_plan_truncates_to_shortest():
    assert build_study_plan(
        ["SQL", "Python", "Databricks"],
        [45, 30],
    ) == [
        ("SQL", 45),
        ("Python", 30),
    ]


def test_organize_study_plan():
    result = organize_study_plan(
        ["SQL", "Python", "Databricks", "Power BI"],
        [45, 30, 60, 20],
    )

    assert result == (
        (1, "SQL", 45),
        [
            (2, "Python", 30),
            (3, "Databricks", 60),
        ],
        (4, "Power BI", 20),
    )
