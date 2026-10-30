"""
src/ai_interpreter.py

AI interpretation engine for Crystallytics.
Provides structured, Pydantic-validated interpretations grounded strictly
in Python-verified statistical computations.
"""

from typing import List, Dict, Any, Optional, Tuple
import os
import json
from pydantic import BaseModel, Field

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class DatasetInterpretation(BaseModel):
    """Structured Pydantic schema for verified interpretations."""
    executive_summary: str = Field(
        description="A concise 2-3 sentence overview explaining what the dataset represents and its primary characteristics."
    )
    key_findings: List[str] = Field(
        description="Bullet points describing the most significant factual findings grounded in the computed data."
    )
    identified_trends: List[str] = Field(
        description="Observed patterns or relationships across variables (e.g., changes over time or categorical distributions)."
    )
    potential_anomalies: List[str] = Field(
        description="Notable outliers, skewness, or data imbalances identified in the calculations."
    )
    limitations_and_cautions: List[str] = Field(
        description="Cautions regarding missing data, small sample sizes, or missing variables."
    )
    recommended_next_steps: List[str] = Field(
        description="Actionable questions or exploratory analyses the user can pursue next."
    )


def build_analysis_payload(
    overview: Dict[str, Any],
    context_data: Dict[str, Any],
    column_profiles: List[Dict[str, Any]],
    numeric_summary: List[Dict[str, Any]],
    warnings: List[str],
) -> Dict[str, Any]:
    """Compiles verified Python calculations into a structured JSON payload."""
    return {
        "dataset_health": overview,
        "inferred_domain": {
            "domain": context_data.get("domain", "General Tabular Dataset"),
            "confidence": context_data.get("confidence", "General"),
            "signals": context_data.get("matched_keywords", []),
        },
        "python_verified_observations": context_data.get("observations", []),
        "columns": column_profiles,
        "numeric_statistics": numeric_summary,
        "data_quality_flags": warnings,
    }


def generate_deterministic_interpretation(payload: Dict[str, Any]) -> DatasetInterpretation:
    """
    Fallback deterministic interpreter when no API key is provided or offline.
    Builds a valid Pydantic model directly from Python calculations without hallucination.
    """
    health = payload.get("dataset_health", {})
    domain_info = payload.get("inferred_domain", {})
    domain = domain_info.get("domain", "General Tabular Dataset")
    rows = health.get("total_rows", 0)
    cols = health.get("total_columns", 0)
    python_obs = payload.get("python_verified_observations", [])
    warnings = payload.get("data_quality_flags", [])
    num_stats = payload.get("numeric_statistics", [])

    summary = (
        f"This dataset consists of {rows:,} records across {cols} columns, classified as a "
        f"'{domain}' dataset. The dataset provides quantitative metrics that have been "
        f"profiled and verified for exploratory analysis."
    )

    findings = list(python_obs) if python_obs else [f"Analyzed {cols} variables across {rows:,} rows."]

    trends = []
    if num_stats:
        top_metric = num_stats[0]
        trends.append(
            f"Primary metric '{top_metric.get('Column')}' averages {top_metric.get('Mean', 0):,.2f} "
            f"with a range from {top_metric.get('Min', 0):,.2f} to {top_metric.get('Max', 0):,.2f}."
        )
    else:
        trends.append("Variables evaluated for categorical frequency distribution.")

    anomalies = []
    for stat in num_stats:
        outliers = stat.get("Outlier Count", 0)
        if outliers > 0:
            anomalies.append(f"Column '{stat.get('Column')}' contains {outliers} potential outlier value(s) beyond 1.5x IQR.")

    if not anomalies:
        anomalies.append("No severe numerical outliers detected across primary variables.")

    limitations = []
    if warnings:
        for w in warnings:
            limitations.append(w.replace("⚠️", "").replace("ℹ️", "").replace("**", "").strip())
    else:
        limitations.append("No major missing data or duplication flags identified.")

    next_steps = [
        "Review recommended visualizations in the 'Automated Visualizations' tab.",
        "Segment key metrics by categorical groups to isolate performance drivers.",
        "Address any potential data quality warnings before finalizing decisions.",
    ]

    return DatasetInterpretation(
        executive_summary=summary,
        key_findings=findings,
        identified_trends=trends,
        potential_anomalies=anomalies,
        limitations_and_cautions=limitations,
        recommended_next_steps=next_steps,
    )


def interpret_dataset(
    payload: Dict[str, Any],
    api_key: Optional[str] = None,
) -> Tuple[DatasetInterpretation, str]:
    """
    Generates a structured interpretation using Gemini API if key is available,
    otherwise gracefully falls back to deterministic Python-grounded interpretation.
    """
    effective_key = api_key or os.environ.get("GEMINI_API_KEY")

    if not effective_key or not GENAI_AVAILABLE:
        mode = "Local Rule-Based Engine (Add Gemini API key in sidebar to enable live AI)"
        return generate_deterministic_interpretation(payload), mode

    try:
        client = genai.Client(api_key=effective_key)

        prompt = f"""
You are Crystallytics' verified analytics interpreter.
Interpret the following verified statistical data profile:

{json.dumps(payload, indent=2)}

STRICT RULES:
1. ONLY reference numbers and facts present in the payload above.
2. DO NOT invent calculations, metrics, or causal explanations.
3. If data is limited or sample size is small, clearly note that in limitations_and_cautions.
4. Output must strictly conform to the required JSON schema.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DatasetInterpretation,
                system_instruction="You are an expert data analyst who interprets verified statistical calculations with complete accuracy and zero hallucination.",
            ),
        )

        parsed_data = DatasetInterpretation.model_validate_json(response.text)
        return parsed_data, "Google Gemini 2.5 Flash"

    except Exception as exc:
        fallback = generate_deterministic_interpretation(payload)
        return fallback, f"Local Fallback (API error: {str(exc)[:60]}...)"
