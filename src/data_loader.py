"""
src/data_loader.py

Responsible for safely loading CSV and Excel files into Pandas DataFrames,
with proper error handling and file validation.
"""

from typing import Union, Tuple
import io
import pandas as pd


def load_dataset(file_source: Union[str, io.BytesIO], filename: str = "") -> Tuple[pd.DataFrame, str]:
    """
    Load a dataset from a file path or uploaded file buffer.

    Parameters:
    -----------
    file_source : str or BytesIO
        The file path or file-like object from Streamlit's file_uploader.
    filename : str, optional
        The filename (used to determine extension if file_source is a buffer).

    Returns:
    --------
    Tuple[pd.DataFrame, str]:
        A tuple of (dataframe, status_message).
        If loading fails, dataframe will be empty and status_message will explain why.
    """
    name = filename if filename else (file_source if isinstance(file_source, str) else "")
    name_lower = name.lower()

    try:
        if name_lower.endswith(".csv"):
            # Try reading with default utf-8, fallback to latin-1 for legacy CSVs
            try:
                df = pd.read_csv(file_source)
            except UnicodeDecodeError:
                if hasattr(file_source, "seek"):
                    file_source.seek(0)
                df = pd.read_csv(file_source, encoding="latin-1")

        elif name_lower.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_source)
        else:
            return pd.DataFrame(), f"Unsupported file type. Please upload a .csv or .xlsx file."

        # Check if the dataframe is empty
        if df.empty:
            return pd.DataFrame(), "The uploaded file is empty (contains no data)."

        return df, "Success"

    except Exception as exc:
        return pd.DataFrame(), f"Error loading file: {str(exc)}"
