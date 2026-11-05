"""
tests/test_data_cleaner.py

Tests data cleaning, deduplication, imputation, and outlier clipping.
"""

import pandas as pd
import numpy as np
from src.data_cleaner import clean_dataframe


def test_clean_duplicates():
    df = pd.DataFrame({
        "A": [1, 1, 2],
        "B": ["x", "x", "y"]
    })
    cleaned, audit = clean_dataframe(df, remove_duplicates=True)
    assert len(cleaned) == 2
    assert audit["duplicates_removed"] == 1


def test_clean_missing_imputation():
    df = pd.DataFrame({
        "Num": [10.0, 20.0, np.nan, 30.0],
        "Cat": ["A", "B", "A", np.nan]
    })
    cleaned, audit = clean_dataframe(df, impute_strategy="median")
    assert cleaned["Num"].isna().sum() == 0
    assert cleaned["Cat"].isna().sum() == 0
    assert audit["missing_imputed"] == 2


def test_clean_outlier_clipping():
    df = pd.DataFrame({
        "Val": [10, 11, 12, 10, 11, 12, 10, 100]  # 100 is outlier
    })
    cleaned, audit = clean_dataframe(df, outlier_strategy="clip")
    assert audit["outliers_modified"] >= 1
    assert cleaned["Val"].max() < 100
