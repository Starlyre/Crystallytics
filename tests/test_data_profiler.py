"""
tests/test_data_profiler.py

Tests data profiling metrics, type detection, and quality warnings.
"""

import pandas as pd
import numpy as np
from src.data_profiler import (
    detect_column_type,
    get_dataset_overview,
    get_column_profiles,
    get_numeric_summary,
    get_data_quality_warnings,
)


def test_detect_column_type():
    df = pd.DataFrame({
        "numbers": [1.0, 2.5, 3.2],
        "integers": [10, 20, 30],
        "categories": ["Red", "Green", "Red"],
        "booleans": [True, False, True],
        "dates": ["2024-01-01", "2024-01-02", "2024-01-03"],
    })

    assert detect_column_type(df["numbers"]) == "Numeric"
    assert detect_column_type(df["integers"]) == "Numeric"
    assert detect_column_type(df["categories"]) == "Categorical"
    assert detect_column_type(df["booleans"]) == "Boolean"
    assert detect_column_type(df["dates"]) == "Datetime"


def test_get_dataset_overview():
    df = pd.DataFrame({
        "A": [1, 2, np.nan, 1],
        "B": ["x", "y", "z", "x"],
    })
    overview = get_dataset_overview(df)
    assert overview["total_rows"] == 4
    assert overview["total_columns"] == 2
    assert overview["missing_cells"] == 1
    assert overview["duplicate_rows"] == 1


def test_get_numeric_summary_and_outliers():
    # 100 is an outlier compared to 10, 11, 12, 10, 11
    df = pd.DataFrame({
        "values": [10, 11, 12, 10, 11, 12, 10, 100]
    })
    summary = get_numeric_summary(df)
    assert not summary.empty
    assert summary.iloc[0]["Outlier Count"] >= 1


def test_get_data_quality_warnings():
    df = pd.DataFrame({
        "sparse": [1, np.nan, np.nan, np.nan, np.nan],  # 80% missing
        "constant": [5, 5, 5, 5, 5],                    # 1 unique
        "normal": [1, 2, 3, 4, 5],
    })
    warnings = get_data_quality_warnings(df)
    assert len(warnings) >= 2
    assert any("sparse" in w for w in warnings)
    assert any("constant" in w for w in warnings)
