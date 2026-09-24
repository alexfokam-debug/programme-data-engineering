import pytest

from python.effective_python.s04_items_10_12 import (
    IngestionRun,
    format_ingestion_summary,
    to_bytes,
    to_text,
)


def test_to_text_with_str():
    assert to_text("hello") == "hello"
    assert to_text("café") == "café"


def test_to_text_with_bytes():
    assert to_text(b"hello") == "hello"
    assert to_text("café".encode()) == "café"


def test_to_text_with_invalid_type():
    with pytest.raises(TypeError):
        to_text(123)


def test_to_bytes():
    assert to_bytes("hello") == b"hello"
    assert to_bytes(b"hello") == b"hello"
    assert to_bytes("café") == "café".encode()

    with pytest.raises(TypeError):
        to_bytes(123)


def test_format_ingestion_summary():
    result = format_ingestion_summary("customers.csv", 12500, 0.03456)

    assert result == "Source: customers.csv, Rows: 12,500, Error Rate: 3.46%"


def test_ingestion_run_repr_and_str():
    run = IngestionRun("customers.csv", 12500, "success")

    assert "source='customers.csv'" in repr(run)
    assert "rows=12500" in repr(run)
    assert "status='success'" in repr(run)

    assert str(run) == "customers.csv: 12500 rows - success"
