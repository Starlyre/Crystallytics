"""
src/data_cleaner.py

Automated data cleaning and sanitization engine for Crystallytics.
Handles deduplication, missing value imputation, outlier handling, and text trimming.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np


def clean_dataframe(
    df: pd.DataFrame,
    remove_duplicates: bool = True,
    impute_strategy: str = "median",  # "median", "mean", "drop", "none"
    outlier_strategy: str = "clip",   # "clip", "drop", "keep"
    trim_whitespace: bool = True,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans and sanitizes a pandas DataFrame according to specified rules.
    Returns (cleaned_df, audit_metrics).
    """
    working_df = df.copy()
    initial_rows = len(working_df)
    initial_missing = int(working_df.isna().sum().sum())
    initial_dupes = int(working_df.duplicated().sum())

    # 1. Trim whitespace
    if trim_whitespace:
        for col in working_df.select_dtypes(include=["object", "string"]).columns:
            working_df[col] = working_df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

    # 2. Remove duplicates
    duplicates_removed = 0
    if remove_duplicates:
        dupes_count = int(working_df.duplicated().sum())
        if dupes_count > 0:
            working_df = working_df.drop_duplicates()
            duplicates_removed = dupes_count

    # 3. Missing values
    missing_imputed = 0
    missing_dropped = 0

    if impute_strategy == "drop":
        before = len(working_df)
        working_df = working_df.dropna()
        missing_dropped = before - len(working_df)
    elif impute_strategy in ["median", "mean"]:
        for col in working_df.columns:
            if working_df[col].isna().sum() > 0:
                col_missing = int(working_df[col].isna().sum())
                if pd.api.types.is_numeric_dtype(working_df[col]):
                    val = working_df[col].median() if impute_strategy == "median" else working_df[col].mean()
                    working_df[col] = working_df[col].fillna(val)
                    missing_imputed += col_missing
                else:
                    mode = working_df[col].mode()
                    if not mode.empty:
                        working_df[col] = working_df[col].fillna(mode.iloc[0])
                        missing_imputed += col_missing

    # 4. Outliers via 1.5x IQR
    outliers_modified = 0
    if outlier_strategy != "keep":
        numeric_cols = working_df.select_dtypes(include="number").columns
        for col in numeric_cols:
            s = working_df[col].dropna()
            if len(s) >= 4:
                q25 = s.quantile(0.25)
                q75 = s.quantile(0.75)
                iqr = q75 - q25
                lower = q25 - 1.5 * iqr
                upper = q75 + 1.5 * iqr

                if outlier_strategy == "clip":
                    outlier_mask = (working_df[col] < lower) | (working_df[col] > upper)
                    outliers_modified += int(outlier_mask.sum())
                    working_df[col] = working_df[col].clip(lower=lower, upper=upper)
                elif outlier_strategy == "drop":
                    outlier_mask = (working_df[col] < lower) | (working_df[col] > upper)
                    outliers_modified += int(outlier_mask.sum())
                    working_df = working_df[~outlier_mask]

    final_rows = len(working_df)
    final_missing = int(working_df.isna().sum().sum())

    audit = {
        "initial_rows": initial_rows,
        "final_rows": final_rows,
        "duplicates_removed": duplicates_removed,
        "missing_imputed": missing_imputed,
        "missing_dropped": missing_dropped,
        "outliers_modified": outliers_modified,
        "initial_missing": initial_missing,
        "final_missing": final_missing,
    }

    return working_df, audit
