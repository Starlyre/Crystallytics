"""
tests/test_data_loader.py

Tests file reading and edge case handling for CSV and Excel formats.
"""

import io
import pandas as pd
from src.data_loader import load_dataset


def test_load_valid_csv():
    csv_data = io.BytesIO(b"Name,Age\nAlice,30\nBob,25")
    df, msg = load_dataset(csv_data, filename="people.csv")
    assert msg == "Success"
    assert len(df) == 2
    assert list(df.columns) == ["Name", "Age"]


def test_load_empty_csv():
    empty_csv = io.BytesIO(b"")
    df, msg = load_dataset(empty_csv, filename="empty.csv")
    assert df.empty
    assert "error" in msg.lower() or "empty" in msg.lower()


def test_unsupported_file_type():
    data = io.BytesIO(b"random content")
    df, msg = load_dataset(data, filename="file.pdf")
    assert df.empty
    assert "Unsupported file type" in msg
