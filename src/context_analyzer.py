"""
src/context_analyzer.py

Identifies dataset subject matter/domain and calculates factual, domain-specific
statistical observations strictly grounded in Python computations.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


DOMAIN_PATTERNS = {
    "Sales & Commercial": {
        "keywords": {"sale", "sales", "revenue", "price", "unit", "units", "product", "order", "orders", "quantity", "discount", "profit"},
        "primary_metric_candidates": ["revenue", "sales", "profit", "total", "amount"],
        "entity_candidates": ["product", "item", "category", "region", "customer"],
    },
    "Human Resources & Payroll": {
        "keywords": {"employee", "salary", "wage", "department", "role", "experience", "hire", "tenure", "performance", "bonus"},
        "primary_metric_candidates": ["salary", "wage", "compensation", "bonus"],
        "entity_candidates": ["department", "role", "title", "employee", "team"],
    },
    "Financial & Accounting": {
        "keywords": {"balance", "credit", "debit", "transaction", "asset", "expense", "cost", "income", "budget", "invoice"},
        "primary_metric_candidates": ["amount", "balance", "cost", "expense", "budget"],
        "entity_candidates": ["account", "category", "type", "client", "vendor"],
    },
    "Healthcare & Clinical": {
        "keywords": {"patient", "diagnosis", "glucose", "blood", "treatment", "dosage", "symptom", "hospital", "physician"},
        "primary_metric_candidates": ["dosage", "age", "level", "score", "measurement"],
        "entity_candidates": ["diagnosis", "treatment", "department", "condition"],
    },
}


def infer_domain(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Infers the likely domain context of the dataset based on column names.
    """
    col_names_clean = [str(c).lower().strip().replace("_", " ").replace("-", " ") for c in df.columns]
    
    best_domain = "General Tabular Dataset"
    best_score = 0
    matched_keywords = []

    for domain, config in DOMAIN_PATTERNS.items():
        score = 0
        matches = []
        for kw in config["keywords"]:
            for col in col_names_clean:
                if kw in col.split():
                    score += 2
                    matches.append(kw)
                elif kw in col:
                    score += 1
                    matches.append(kw)

        if score > best_score:
            best_score = score
            best_domain = domain
            matched_keywords = list(set(matches))

    confidence = "High" if best_score >= 4 else ("Medium" if best_score >= 2 else "Low")
    if best_score < 2:
        best_domain = "General Tabular Dataset"
        confidence = "General"

    return {
        "domain": best_domain,
        "confidence": confidence,
        "score": best_score,
        "matched_keywords": matched_keywords,
    }


def analyze_domain_context(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs context-aware statistical calculations based on the inferred domain.
    Returns domain metadata and verified factual observations.
    """
    domain_info = infer_domain(df)
    domain = domain_info["domain"]
    observations: List[str] = []

    col_map = {str(c).lower().strip(): c for c in df.columns}

    # Helper to find column matching any candidate keywords
    def find_col(candidates: List[str]) -> Any:
        for cand in candidates:
            for clean_name, orig_col in col_map.items():
                if cand in clean_name:
                    return orig_col
        return None

    if domain == "Sales & Commercial":
        metric_col = find_col(DOMAIN_PATTERNS["Sales & Commercial"]["primary_metric_candidates"])
        entity_col = find_col(DOMAIN_PATTERNS["Sales & Commercial"]["entity_candidates"])

        if metric_col and pd.api.types.is_numeric_dtype(df[metric_col]):
            total_val = df[metric_col].sum()
            avg_val = df[metric_col].mean()
            observations.append(f"**Total Volume:** Overall `{metric_col}` totals **{total_val:,.2f}** with an average of **{avg_val:,.2f}** per record.")

            if entity_col:
                top_entity = df.groupby(entity_col)[metric_col].sum().sort_values(ascending=False)
                if not top_entity.empty:
                    top_name = top_entity.index[0]
                    top_rev = top_entity.iloc[0]
                    share = (top_rev / total_val * 100) if total_val > 0 else 0
                    observations.append(f"**Top Contributor:** `{top_name}` leads `{entity_col}` with **{top_rev:,.2f}** in `{metric_col}` ({share:.1f}% of total).")

    elif domain == "Human Resources & Workforce":
        salary_col = find_col(DOMAIN_PATTERNS["Human Resources & Payroll"]["primary_metric_candidates"])
        dept_col = find_col(DOMAIN_PATTERNS["Human Resources & Payroll"]["entity_candidates"])

        if salary_col and pd.api.types.is_numeric_dtype(df[salary_col]):
            med_sal = df[salary_col].median()
            avg_sal = df[salary_col].mean()
            observations.append(f"**Compensation Benchmark:** Median `{salary_col}` is **{med_sal:,.2f}** (Average: **{avg_sal:,.2f}**).")

            if dept_col:
                dept_group = df.groupby(dept_col)[salary_col].mean().sort_values(ascending=False)
                if not dept_group.empty:
                    top_dept = dept_group.index[0]
                    top_dept_sal = dept_group.iloc[0]
                    observations.append(f"**Highest Compensated Segment:** `{dept_col}` '**{top_dept}**' has the highest average `{salary_col}` at **{top_dept_sal:,.2f}**.")

    # General observations for all datasets (trends, top categories, anomalies)
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    categorical_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c]) and df[c].nunique() < len(df)]

    # Outlier observation
    for col in numeric_cols[:2]:
        s = df[col].dropna()
        if len(s) >= 4:
            q25 = s.quantile(0.25)
            q75 = s.quantile(0.75)
            iqr = q75 - q25
            outliers = ((s < q25 - 1.5 * iqr) | (s > q75 + 1.5 * iqr)).sum()
            if outliers > 0:
                observations.append(f"**Statistical Dispersion:** `{col}` exhibits **{outliers} potential outlier(s)** outside the $1.5 \\times \\text{{IQR}}$ range.")

    # Dominant category observation
    if categorical_cols:
        cat_col = categorical_cols[0]
        top_val = df[cat_col].mode()
        if not top_val.empty:
            val_name = top_val.iloc[0]
            val_count = (df[cat_col] == val_name).sum()
            val_pct = (val_count / len(df) * 100) if len(df) > 0 else 0
            observations.append(f"**Categorical Concentration:** In `{cat_col}`, '**{val_name}**' is the most frequent value, representing **{val_pct:.1f}%** ({val_count} rows) of records.")

    if not observations:
        observations.append("Dataset evaluated. Basic distribution metrics computed across all available variables.")

    return {
        "domain": domain,
        "confidence": domain_info["confidence"],
        "matched_keywords": domain_info["matched_keywords"],
        "observations": observations,
    }
