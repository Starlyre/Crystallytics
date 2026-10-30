"""
tests/test_context_analyzer.py

Tests domain context inference and factual observation generation.
"""

import pandas as pd
from src.context_analyzer import infer_domain, analyze_domain_context


def test_infer_sales_domain():
    df = pd.DataFrame({
        "Date": ["2024-01-01", "2024-01-02"],
        "Product": ["Laptop", "Mouse"],
        "Revenue": [1200.0, 50.0],
        "Units Sold": [1, 2],
    })
    res = infer_domain(df)
    assert res["domain"] == "Sales & Commercial"
    assert res["confidence"] in ["High", "Medium"]


def test_infer_hr_domain():
    df = pd.DataFrame({
        "EmployeeID": [1, 2],
        "Department": ["Engineering", "HR"],
        "Salary": [90000, 60000],
    })
    res = infer_domain(df)
    assert "Human Resources" in res["domain"]


def test_analyze_domain_context_observations():
    df = pd.DataFrame({
        "Product": ["Laptop", "Laptop", "Mouse"],
        "Revenue": [1000.0, 2000.0, 100.0],
    })
    analysis = analyze_domain_context(df)
    assert analysis["domain"] == "Sales & Commercial"
    assert len(analysis["observations"]) > 0
    # Check that calculations are grounded (Laptop sum is 3000, total is 3100)
    obs_text = " ".join(analysis["observations"])
    assert "Laptop" in obs_text
    assert "3,100" in obs_text or "3100" in obs_text
