"""
src/visualization.py

Automated visualization engine for Crystallytics.
Recommends and generates appropriate Plotly charts based on data types and relationships.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.data_profiler import detect_column_type


def get_column_type_map(df: pd.DataFrame) -> Dict[str, str]:
    """Map each column name to its detected logical type."""
    return {col: detect_column_type(df[col]) for col in df.columns}


def recommend_visualizations(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Intelligently inspects the dataset and recommends high-value visualizations
    with clear justifications.
    """
    recommendations = []
    type_map = get_column_type_map(df)

    numeric_cols = [c for c, t in type_map.items() if t == "Numeric"]
    categorical_cols = [c for c, t in type_map.items() if t == "Categorical"]
    datetime_cols = [c for c, t in type_map.items() if t == "Datetime"]

    # 1. Time Series Line Chart (if date + numeric exist)
    if datetime_cols and numeric_cols:
        date_col = datetime_cols[0]
        num_col = numeric_cols[0]
        recommendations.append({
            "type": "line",
            "title": f"Trend of {num_col} over {date_col}",
            "reason": f"Tracks how '{num_col}' changes chronologically over time.",
            "params": {"date_col": date_col, "numeric_col": num_col},
        })

    # 2. Categorical Aggregation Bar Chart (if categorical + numeric exist)
    if categorical_cols and numeric_cols:
        cat_col = categorical_cols[0]
        num_col = numeric_cols[0]
        recommendations.append({
            "type": "bar",
            "title": f"{num_col} by {cat_col}",
            "reason": f"Compares '{num_col}' totals across different '{cat_col}' segments.",
            "params": {"category_col": cat_col, "numeric_col": num_col},
        })
    elif categorical_cols:
        # Frequency bar chart
        cat_col = categorical_cols[0]
        recommendations.append({
            "type": "bar_count",
            "title": f"Frequency Count of {cat_col}",
            "reason": f"Shows distribution of records across '{cat_col}'.",
            "params": {"category_col": cat_col},
        })

    # 3. Correlation Heatmap (if at least 2 numeric columns)
    if len(numeric_cols) >= 2:
        recommendations.append({
            "type": "heatmap",
            "title": "Correlation Matrix",
            "reason": "Reveals linear relationships and potential dependencies between numeric metrics.",
            "params": {"numeric_cols": numeric_cols},
        })

    # 4. Scatter Plot (if at least 2 numeric columns)
    if len(numeric_cols) >= 2:
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        color_col = categorical_cols[0] if categorical_cols else None
        recommendations.append({
            "type": "scatter",
            "title": f"Relationship: {x_col} vs {y_col}",
            "reason": f"Examines whether changes in '{x_col}' associate with '{y_col}'.",
            "params": {"x_col": x_col, "y_col": y_col, "color_col": color_col},
        })

    # 5. Box Plot by Category (if categorical + numeric exist)
    if categorical_cols and numeric_cols:
        cat_col = categorical_cols[0]
        num_col = numeric_cols[0]
        recommendations.append({
            "type": "box",
            "title": f"Distribution of {num_col} by {cat_col}",
            "reason": f"Displays spread, medians, and outliers of '{num_col}' across each '{cat_col}'.",
            "params": {"category_col": cat_col, "numeric_col": num_col},
        })

    return recommendations


def plot_line_chart(df: pd.DataFrame, date_col: str, numeric_col: str) -> go.Figure:
    """Generate a clean time-series line chart."""
    temp_df = df.copy()
    temp_df[date_col] = pd.to_datetime(temp_df[date_col], errors="coerce")
    temp_df = temp_df.dropna(subset=[date_col, numeric_col]).sort_values(by=date_col)

    fig = px.line(
        temp_df,
        x=date_col,
        y=numeric_col,
        title=f"Trend: {numeric_col} over {date_col}",
        markers=True,
        template="plotly_white",
    )
    fig.update_layout(xaxis_title=date_col, yaxis_title=numeric_col)
    return fig


def plot_bar_chart(df: pd.DataFrame, category_col: str, numeric_col: Optional[str] = None) -> go.Figure:
    """Generate a bar chart showing either sums or record counts, limited to top 15 categories."""
    if numeric_col:
        grouped = (
            df.groupby(category_col)[numeric_col]
            .sum()
            .reset_index()
            .sort_values(by=numeric_col, ascending=False)
            .head(15)
        )
        fig = px.bar(
            grouped,
            x=category_col,
            y=numeric_col,
            title=f"Total {numeric_col} by {category_col} (Top 15)",
            template="plotly_white",
            color=numeric_col,
            color_continuous_scale="Blues",
        )
    else:
        counts = (
            df[category_col]
            .value_counts()
            .reset_index()
            .head(15)
        )
        counts.columns = [category_col, "Count"]
        fig = px.bar(
            counts,
            x=category_col,
            y="Count",
            title=f"Count of Records by {category_col} (Top 15)",
            template="plotly_white",
            color="Count",
            color_continuous_scale="Viridis",
        )

    fig.update_layout(xaxis_tickangle=-30)
    return fig


def plot_scatter(df: pd.DataFrame, x_col: str, y_col: str, color_col: Optional[str] = None) -> go.Figure:
    """Generate a scatter plot to explore correlations and clusters."""
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title=f"{x_col} vs {y_col}" + (f" (Grouped by {color_col})" if color_col else ""),
        template="plotly_white",
        opacity=0.8,
    )
    return fig


def plot_box(df: pd.DataFrame, category_col: str, numeric_col: str) -> go.Figure:
    """Generate a box plot showing numeric distributions across categories."""
    fig = px.box(
        df,
        x=category_col,
        y=numeric_col,
        color=category_col,
        title=f"Distribution of {numeric_col} across {category_col}",
        template="plotly_white",
    )
    fig.update_layout(showlegend=False, xaxis_tickangle=-30)
    return fig


def plot_correlation_heatmap(df: pd.DataFrame, numeric_cols: Optional[List[str]] = None) -> Optional[go.Figure]:
    """Generate an annotated correlation heatmap."""
    cols = numeric_cols if numeric_cols else [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if len(cols) < 2:
        return None

    corr_matrix = df[cols].corr().round(2)

    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        title="Numeric Correlation Matrix",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        template="plotly_white",
    )
    return fig
