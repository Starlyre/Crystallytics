"""
tests/test_visualization.py

Tests automatic chart recommendation and rendering logic.
"""

import pandas as pd
from src.visualization import (
    recommend_visualizations,
    plot_line_chart,
    plot_bar_chart,
    plot_scatter,
    plot_box,
    plot_correlation_heatmap,
)


def get_mock_df():
    return pd.DataFrame({
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "Category": ["Electronics", "Clothing", "Electronics", "Groceries"],
        "Sales": [100.0, 50.0, 150.0, 20.0],
        "Units": [2, 1, 3, 5],
    })


def test_recommend_visualizations():
    df = get_mock_df()
    recs = recommend_visualizations(df)

    assert len(recs) > 0
    rec_types = [r["type"] for r in recs]

    # Should recommend line, bar, heatmap, scatter, and box
    assert "line" in rec_types
    assert "bar" in rec_types
    assert "heatmap" in rec_types
    assert "scatter" in rec_types


def test_plot_generation():
    df = get_mock_df()

    # Check that each generator returns a valid Plotly Figure without crashing
    fig_line = plot_line_chart(df, "Date", "Sales")
    assert fig_line is not None

    fig_bar = plot_bar_chart(df, "Category", "Sales")
    assert fig_bar is not None

    fig_scatter = plot_scatter(df, "Sales", "Units", color_col="Category")
    assert fig_scatter is not None

    fig_box = plot_box(df, "Category", "Sales")
    assert fig_box is not None

    fig_heat = plot_correlation_heatmap(df, ["Sales", "Units"])
    assert fig_heat is not None
