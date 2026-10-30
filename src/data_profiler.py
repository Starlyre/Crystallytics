"""
src/data_profiler.py

Calculates comprehensive data profiling metrics, statistical summaries,
and data quality warnings from a Pandas DataFrame.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


def detect_column_type(series: pd.Series) -> str:
    """
    Intelligently infer the logical data type of a column.
    Returns: 'Numeric', 'Datetime', 'Boolean', 'Categorical', or 'Text/ID'
    """
    # 1. Check boolean
    if pd.api.types.is_bool_dtype(series):
        return "Boolean"

    # 2. Check datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return "Datetime"

    # If it's an object/string series, check if it can be parsed as datetime
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
        # Drop missing values to check sample
        non_null = series.dropna()
        if len(non_null) > 0:
            sample = non_null.head(50)
            try:
                # Attempt conversion of sample to datetime without errors
                converted = pd.to_datetime(sample, errors="coerce", format="mixed")
                if converted.notna().mean() > 0.8:
                    return "Datetime"
            except Exception:
                pass

    # 3. Check numeric
    if pd.api.types.is_numeric_dtype(series):
        # Check if it acts like a boolean (only 0 and 1)
        unique_vals = series.dropna().unique()
        if len(unique_vals) <= 2 and set(unique_vals).issubset({0, 1, 0.0, 1.0}):
            return "Boolean"
        return "Numeric"

    # 4. Check categorical vs text/identifier
    n_unique = series.nunique()
    total_valid = series.count()

    if total_valid > 0:
        uniqueness_ratio = n_unique / total_valid
        # If uniqueness is very high and there are many rows, it's likely an ID or free text
        if uniqueness_ratio > 0.7 and total_valid > 20:
            return "Text/ID"
        return "Categorical"

    return "Categorical"


def get_dataset_overview(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate high-level dataset metrics."""
    total_rows, total_cols = df.shape
    total_cells = total_rows * total_cols
    missing_cells = int(df.isna().sum().sum())
    missing_pct = round((missing_cells / total_cells * 100), 2) if total_cells > 0 else 0.0
    duplicate_rows = int(df.duplicated().sum())
    duplicate_pct = round((duplicate_rows / total_rows * 100), 2) if total_rows > 0 else 0.0

    return {
        "total_rows": total_rows,
        "total_columns": total_cols,
        "total_cells": total_cells,
        "missing_cells": missing_cells,
        "missing_percentage": missing_pct,
        "duplicate_rows": duplicate_rows,
        "duplicate_percentage": duplicate_pct,
        "memory_usage_kb": round(df.memory_usage(deep=True).sum() / 1024, 2),
    }


def get_column_profiles(df: pd.DataFrame) -> pd.DataFrame:
    """Generate a summary table for all columns in the dataset."""
    profiles = []
    total_rows = len(df)

    for col in df.columns:
        series = df[col]
        col_type = detect_column_type(series)
        missing_count = int(series.isna().sum())
        missing_pct = round((missing_count / total_rows * 100), 1) if total_rows > 0 else 0.0
        unique_count = int(series.nunique())

        profiles.append({
            "Column": str(col),
            "Detected Type": col_type,
            "Missing Values": missing_count,
            "Missing %": f"{missing_pct}%",
            "Unique Values": unique_count,
        })

    return pd.DataFrame(profiles)


def get_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate detailed statistics for all numeric columns including
    mean, median, standard deviation, IQR, and detected outlier counts.
    """
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        return pd.DataFrame()

    summaries = []
    for col in numeric_cols:
        s = df[col].dropna()
        if len(s) == 0:
            continue

        q25 = float(s.quantile(0.25))
        q50 = float(s.median())
        q75 = float(s.quantile(0.75))
        iqr = q75 - q25

        # Outliers via 1.5 * IQR rule
        lower_bound = q25 - (1.5 * iqr)
        upper_bound = q75 + (1.5 * iqr)
        outlier_count = int(((s < lower_bound) | (s > upper_bound)).sum())

        summaries.append({
            "Column": str(col),
            "Mean": round(float(s.mean()), 2),
            "Std Dev": round(float(s.std()), 2) if len(s) > 1 else 0.0,
            "Min": round(float(s.min()), 2),
            "25% (Q1)": round(q25, 2),
            "Median": round(q50, 2),
            "75% (Q3)": round(q75, 2),
            "Max": round(float(s.max()), 2),
            "Outlier Count": outlier_count,
        })

    return pd.DataFrame(summaries)


def get_data_quality_warnings(df: pd.DataFrame) -> List[str]:
    """Scan dataset for common data-quality red flags and return actionable warnings."""
    warnings = []
    total_rows = len(df)

    # 1. Duplicate rows
    dupes = int(df.duplicated().sum())
    if dupes > 0:
        pct = round(dupes / total_rows * 100, 1)
        warnings.append(f"⚠️ **Duplicate records found:** {dupes} rows ({pct}%) appear to be exact duplicates.")

    # 2. Columns with high missingness
    for col in df.columns:
        missing_count = int(df[col].isna().sum())
        missing_pct = round(missing_count / total_rows * 100, 1) if total_rows > 0 else 0
        if missing_pct >= 40:
            warnings.append(f"⚠️ **High missing data:** Column **`{col}`** is missing {missing_pct}% of its values ({missing_count} rows).")

    # 3. Constant columns (zero variance)
    for col in df.columns:
        if df[col].nunique() == 1 and total_rows > 1:
            warnings.append(f"ℹ️ **Constant column:** Column **`{col}`** contains only a single unique value throughout.")

    return warnings
