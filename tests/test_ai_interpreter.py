"""
tests/test_ai_interpreter.py

Tests the AI interpretation layer, schema validation, and fallback mechanisms.
"""

from src.ai_interpreter import (
    DatasetInterpretation,
    build_analysis_payload,
    generate_deterministic_interpretation,
    interpret_dataset,
)


def test_pydantic_schema_validation():
    data = {
        "executive_summary": "Test summary",
        "key_findings": ["Finding 1"],
        "identified_trends": ["Trend 1"],
        "potential_anomalies": ["Anomaly 1"],
        "limitations_and_cautions": ["Caution 1"],
        "recommended_next_steps": ["Step 1"],
    }
    model = DatasetInterpretation(**data)
    assert model.executive_summary == "Test summary"
    assert len(model.key_findings) == 1


def test_generate_deterministic_interpretation():
    payload = {
        "dataset_health": {"total_rows": 100, "total_columns": 5},
        "inferred_domain": {"domain": "Sales & Commercial"},
        "python_verified_observations": ["Revenue totals 50,000"],
        "numeric_statistics": [{"Column": "Revenue", "Mean": 500, "Outlier Count": 2}],
        "data_quality_flags": ["⚠️ Duplicate records found: 2 rows"],
    }

    interpretation = generate_deterministic_interpretation(payload)
    assert isinstance(interpretation, DatasetInterpretation)
    assert "100" in interpretation.executive_summary
    assert "Sales & Commercial" in interpretation.executive_summary
    assert len(interpretation.key_findings) > 0
    assert len(interpretation.potential_anomalies) > 0


def test_interpret_dataset_graceful_fallback():
    payload = {
        "dataset_health": {"total_rows": 50, "total_columns": 3},
        "inferred_domain": {"domain": "General Tabular Dataset"},
    }
    # No API key provided -> should use local engine without crashing
    interp, engine = interpret_dataset(payload, api_key=None)
    assert isinstance(interp, DatasetInterpretation)
    assert "Local" in engine or "Rule-Based" in engine
