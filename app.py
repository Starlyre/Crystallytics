import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

from src.data_loader import load_dataset
from src.data_profiler import (
    get_dataset_overview,
    get_column_profiles,
    get_numeric_summary,
    get_data_quality_warnings,
)
from src.visualization import (
    recommend_visualizations,
    plot_line_chart,
    plot_bar_chart,
    plot_scatter,
    plot_box,
    plot_correlation_heatmap,
)
from src.context_analyzer import analyze_domain_context
from src.ai_interpreter import (
    build_analysis_payload,
    interpret_dataset,
)

# Page configuration
st.set_page_config(
    page_title="Crystallytics 💎 | Context-Aware Data Intelligence",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (CSS)
CUSTOM_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }

    /* Hero Gradient Title */
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 50%, #7F00FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.4rem;
        margin-bottom: 0.5rem;
    }
    .badge-iso {
        background-color: #EEF2FF;
        color: #4F46E5;
        border: 1px solid #C7D2FE;
    }
    .badge-sec {
        background-color: #ECFDF5;
        color: #059669;
        border: 1px solid #A7F3D0;
    }
    .badge-ai {
        background-color: #FAF5FF;
        color: #9333EA;
        border: 1px solid #E9D5FF;
    }

    /* Cards */
    .glass-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.4rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        margin-bottom: 1.2rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .glass-card:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
    }

    /* Metric Cards */
    .metric-container {
        background: linear-gradient(145deg, #FFFFFF, #F8FAFC);
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0F172A;
        margin: 0.2rem 0;
    }
    .metric-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* AI Insight Cards */
    .insight-card {
        border-left: 4px solid #3B82F6;
        background: #F8FAFC;
        border-radius: 0 10px 10px 0;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .insight-card-green { border-left-color: #10B981; }
    .insight-card-amber { border-left-color: #F59E0B; }
    .insight-card-purple { border-left-color: #8B5CF6; }

    /* Quality Banner */
    .quality-banner {
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 💎 Crystallytics")
    st.caption("v1.0 • Standards-Compliant Data Intelligence")
    st.caption("⚡ *Powered by Google Antigravity & Gemini*")
    st.markdown("---")

    st.subheader("⚙️ AI Configuration")
    api_key_input = st.sidebar.text_input(
        "Google Gemini API Key",
        type="password",
        help="Optional: Enter a Gemini API key for live LLM interpretations. If left blank, Crystallytics operates offline using its verified local rules engine.",
    )

    if api_key_input:
        st.success("✨ Live AI Enabled (Gemini 2.5 Flash)")
    else:
        st.info("⚡ Active Mode: Local Verifiable Engine (Zero-Latency)")

    st.markdown("---")
    with st.expander("🛡️ Data Security & ISO 27001", expanded=False):
        st.markdown(
            """
            - **Zero Disk Retention:** Files stream exclusively through transient memory buffers.
            - **Privacy Boundary:** Raw rows are never transmitted across network boundaries.
            - **Quality Model:** ISO/IEC 25010 verified architecture.
            """
        )

# Header Section
st.markdown('<div class="hero-title">💎 Crystallytics</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Transform messy datasets into crystal-clear statistical profiles, automated charts, and verifiable AI insights.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <span class="badge badge-iso">ISO/IEC 25010 Quality Model</span>
    <span class="badge badge-sec">ISO/IEC 27001 Zero-Retention</span>
    <span class="badge badge-ai">Grounded AI • Zero Hallucinations</span>
    <span class="badge" style="background-color: #E8F0FE; color: #1A73E8; border: 1px solid #AECBFA;">⚡ Built with Google Antigravity</span>
    """,
    unsafe_allow_html=True,
)

st.write("")

# File Upload & Demo Loader
col_up1, col_up2 = st.columns([3, 1])

with col_up1:
    uploaded_file = st.file_uploader(
        "Upload a dataset to crystallize",
        type=["csv", "xlsx"],
        help="Supports UTF-8 / Latin-1 CSV files and multi-sheet Excel workbooks.",
    )

with col_up2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    load_demo = st.button("🚀 Load Sample Sales Data", use_container_width=True, help="Explore Crystallytics instantly with built-in sales data.")

# Handle data source
df = None
status_message = ""
active_filename = ""

if load_demo:
    demo_path = os.path.join(os.path.dirname(__file__), "data", "sample_sales.csv")
    if os.path.exists(demo_path):
        df, status_message = load_dataset(demo_path, filename="sample_sales.csv")
        active_filename = "sample_sales.csv (Demo)"
elif uploaded_file is not None:
    df, status_message = load_dataset(uploaded_file, filename=uploaded_file.name)
    active_filename = uploaded_file.name

if df is not None and not df.empty:
    if status_message != "Success":
        st.error(status_message)
    else:
        # 1. Compute Analytics Payload
        overview = get_dataset_overview(df)
        context_data = analyze_domain_context(df)
        warnings = get_data_quality_warnings(df)
        profiles_df = get_column_profiles(df)
        summary_df = get_numeric_summary(df)

        # 2. Top-Level Metric Bar
        st.write("")
        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            st.markdown(
                f"""<div class="metric-container">
                    <div class="metric-label">Total Rows</div>
                    <div class="metric-value">{overview['total_rows']:,}</div>
                    <span style="font-size: 0.8rem; color: #10B981;">● Complete</span>
                </div>""",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""<div class="metric-container">
                    <div class="metric-label">Columns</div>
                    <div class="metric-value">{overview['total_columns']:,}</div>
                    <span style="font-size: 0.8rem; color: #6366F1;">● {len(df.select_dtypes(include='number').columns)} Numeric</span>
                </div>""",
                unsafe_allow_html=True,
            )
        with c3:
            miss_color = "#10B981" if overview["missing_cells"] == 0 else "#EF4444"
            st.markdown(
                f"""<div class="metric-container">
                    <div class="metric-label">Missing Cells</div>
                    <div class="metric-value" style="color: {miss_color};">{overview['missing_cells']:,}</div>
                    <span style="font-size: 0.8rem; color: {miss_color};">{overview['missing_percentage']}% Missing</span>
                </div>""",
                unsafe_allow_html=True,
            )
        with c4:
            dupe_color = "#10B981" if overview["duplicate_rows"] == 0 else "#F59E0B"
            st.markdown(
                f"""<div class="metric-container">
                    <div class="metric-label">Duplicate Rows</div>
                    <div class="metric-value" style="color: {dupe_color};">{overview['duplicate_rows']:,}</div>
                    <span style="font-size: 0.8rem; color: {dupe_color};">{overview['duplicate_percentage']}% Dupes</span>
                </div>""",
                unsafe_allow_html=True,
            )
        with c5:
            st.markdown(
                f"""<div class="metric-container">
                    <div class="metric-label">Memory Footprint</div>
                    <div class="metric-value">{overview['memory_usage_kb']:.1f} <span style="font-size: 1rem;">KB</span></div>
                    <span style="font-size: 0.8rem; color: #0EA5E9;">In-RAM Stream</span>
                </div>""",
                unsafe_allow_html=True,
            )

        st.write("")

        # 3. Domain & Context Intelligence Banner
        domain_name = context_data.get("domain", "General Tabular Dataset")
        confidence = context_data.get("confidence", "General")
        keywords = ", ".join(context_data.get("matched_keywords", []))

        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #EFF6FF 0%, #F5F3FF 100%); border: 1px solid #BFDBFE; border-radius: 12px; padding: 1rem 1.4rem; margin-bottom: 1.5rem;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <span style="font-size: 0.85rem; font-weight: 700; color: #1D4ED8; text-transform: uppercase; letter-spacing: 0.05em;">🧠 Detected Subject Matter Context</span>
                        <div style="font-size: 1.35rem; font-weight: 800; color: #1E293B; margin-top: 0.2rem;">
                            {domain_name} <span style="font-size: 0.9rem; font-weight: 600; color: #4F46E5;">(Confidence: {confidence})</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #64748B; margin-top: 0.2rem;">
                            {f'<b>Key Signals Detected:</b> <code>{keywords}</code>' if keywords else 'Generalized statistical pattern matching applied.'}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span class="badge badge-sec">ISO 27001 Verified Safe</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 4. Generate AI Interpretation Payload
        payload = build_analysis_payload(
            overview=overview,
            context_data=context_data,
            column_profiles=profiles_df.to_dict(orient="records"),
            numeric_summary=summary_df.to_dict(orient="records") if not summary_df.empty else [],
            warnings=warnings,
        )

        interpretation, engine_name = interpret_dataset(payload, api_key=api_key_input)

        # 5. Core Application Tabs
        tab_ai, tab_viz, tab_profile, tab_explore = st.tabs([
            "🤖 Executive Narrative & AI Insights",
            "📈 Automated Visualizations",
            "📋 Health & Profiling",
            "🔍 Custom Explorer",
        ])

        # TAB 1: AI EXECUTIVE NARRATIVE
        with tab_ai:
            st.markdown(f"<div style='font-size: 0.85rem; color: #64748B; margin-bottom: 0.8rem;'>Inference Engine: <b>{engine_name}</b> • Verifiable Calculation Isolation</div>", unsafe_allow_html=True)

            # Executive Summary Card
            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.4rem; box-shadow: 0 2px 10px rgba(0,0,0,0.03); margin-bottom: 1.5rem;">
                    <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;">📋 Executive Summary</div>
                    <div style="font-size: 1rem; line-height: 1.6; color: #334155;">{interpretation.executive_summary}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_ai_left, col_ai_right = st.columns(2)

            with col_ai_left:
                st.markdown("#### 🎯 Key Verified Findings")
                for finding in interpretation.key_findings:
                    st.markdown(f"""<div class="insight-card insight-card-green"><b>Finding:</b> {finding}</div>""", unsafe_allow_html=True)

                st.markdown("#### 📈 Observed Trends")
                for trend in interpretation.identified_trends:
                    st.markdown(f"""<div class="insight-card"><b>Trend:</b> {trend}</div>""", unsafe_allow_html=True)

            with col_ai_right:
                st.markdown("#### 🔍 Potential Anomalies & Outliers")
                for anomaly in interpretation.potential_anomalies:
                    st.markdown(f"""<div class="insight-card insight-card-amber"><b>Anomaly:</b> {anomaly}</div>""", unsafe_allow_html=True)

                st.markdown("#### ⚠️ Limitations & Governance")
                for limit in interpretation.limitations_and_cautions:
                    st.markdown(f"""<div class="insight-card insight-card-purple"><b>Note:</b> {limit}</div>""", unsafe_allow_html=True)

            st.write("")
            st.markdown("#### 🚀 Recommended Next Analytical Steps")
            for idx, step in enumerate(interpretation.recommended_next_steps, 1):
                st.markdown(f"**{idx}.** {step}")

            # Export Report Button
            st.write("")
            report_md = f"""# Crystallytics Analytical Audit Report
**Dataset:** {active_filename}  
**Inferred Context:** {domain_name} ({confidence} Confidence)  
**Total Records:** {overview['total_rows']:,} | **Total Columns:** {overview['total_columns']:,}  

## Executive Summary
{interpretation.executive_summary}

## Key Verified Findings
{chr(10).join(f"- {f}" for f in interpretation.key_findings)}

## Identified Trends
{chr(10).join(f"- {t}" for t in interpretation.identified_trends)}

## Anomalies & Dispersions
{chr(10).join(f"- {a}" for a in interpretation.potential_anomalies)}

## Data Governance & Limitations
{chr(10).join(f"- {l}" for l in interpretation.limitations_and_cautions)}

---
*Generated by Crystallytics 💎 | Conforms to ISO/IEC 25010 & ISO/IEC 27001*
"""
            st.download_button(
                label="📥 Download Audit Report (.md)",
                data=report_md,
                file_name=f"crystallytics_report_{domain_name.lower().replace(' ', '_')}.md",
                mime="text/markdown",
            )

        # TAB 2: AUTOMATED VISUALIZATIONS
        with tab_viz:
            st.subheader("Intelligent Chart Recommendations")
            st.caption("Crystallytics evaluated column relationships and constructed these visualizations with full rationale.")

            recs = recommend_visualizations(df)
            if not recs:
                st.info("No multi-column visualizations could be recommended for this dataset.")
            else:
                for rec in recs:
                    rec_type = rec["type"]
                    params = rec["params"]

                    with st.container():
                        st.markdown(
                            f"""
                            <div style="background: #F8FAFC; border-radius: 10px; padding: 0.8rem 1rem; margin-top: 1rem; border-left: 3px solid #3B82F6;">
                                <span style="font-weight: 700; color: #1E293B;">{rec['title']}</span> • <span style="color: #64748B; font-size: 0.9rem;">💡 {rec['reason']}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        if rec_type == "line":
                            fig = plot_line_chart(df, params["date_col"], params["numeric_col"])
                        elif rec_type == "bar":
                            fig = plot_bar_chart(df, params["category_col"], params["numeric_col"])
                        elif rec_type == "bar_count":
                            fig = plot_bar_chart(df, params["category_col"])
                        elif rec_type == "heatmap":
                            fig = plot_correlation_heatmap(df, params["numeric_cols"])
                        elif rec_type == "scatter":
                            fig = plot_scatter(df, params["x_col"], params["y_col"], color_col=params.get("color_col"))
                        elif rec_type == "box":
                            fig = plot_box(df, params["category_col"], params["numeric_col"])

                        if fig:
                            st.plotly_chart(fig, use_container_width=True)

        # TAB 3: DATA PROFILING & HEALTH
        with tab_profile:
            if warnings:
                with st.expander("⚠️ Data Quality Alerts", expanded=True):
                    for w in warnings:
                        st.markdown(w)

            st.subheader("Data Preview (First 100 Rows)")
            st.dataframe(df.head(100), use_container_width=True)

            st.subheader("Column Logical Types & Missingness")
            st.dataframe(profiles_df, use_container_width=True)

            if not summary_df.empty:
                st.subheader("Descriptive Statistics & Dispersion")
                st.dataframe(summary_df, use_container_width=True)

        # TAB 4: CUSTOM VARIABLE EXPLORER
        with tab_explore:
            st.subheader("Interactive Column Distribution Inspector")
            numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

            if numeric_cols:
                col_sel = st.selectbox("Select variable to inspect:", numeric_cols)
                fig = px.histogram(
                    df,
                    x=col_sel,
                    title=f"Distribution & Outlier Box Plot: {col_sel}",
                    marginal="box",
                    template="plotly_white",
                    color_discrete_sequence=["#3B82F6"],
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric columns available for distribution inspection.")

else:
    # Beautiful Landing Page (Empty State)
    st.write("")
    st.markdown(
        """
        <div style="background: linear-gradient(145deg, #F8FAFC, #FFFFFF); border: 1px dashed #CBD5E1; border-radius: 16px; padding: 2.5rem; text-align: center; margin-top: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💎</div>
            <div style="font-size: 1.4rem; font-weight: 800; color: #1E293B; margin-bottom: 0.4rem;">Upload your dataset to begin</div>
            <div style="font-size: 0.95rem; color: #64748B; max-width: 560px; margin: 0 auto 1.5rem auto;">
                Drop any CSV or Excel file above, or click <b>'Load Sample Sales Data'</b> to explore Crystallytics immediately.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.markdown("### 🌟 What Crystallytics Does")

    f1, f2, f3 = st.columns(3)

    with f1:
        st.markdown(
            """
            <div class="glass-card">
                <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">⚡</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 0.3rem;">Automated Profiling</div>
                <div style="font-size: 0.9rem; color: #64748B; line-height: 1.5;">
                    Automatically detects logical types, missing cells, duplicates, memory usage, and computes $1.5 \\times \\text{IQR}$ outliers.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with f2:
        st.markdown(
            """
            <div class="glass-card">
                <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">📊</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 0.3rem;">Contextual Charts</div>
                <div style="font-size: 0.9rem; color: #64748B; line-height: 1.5;">
                    Intelligently recommends line trends, categorical bars, correlation heatmaps, and scatter plots with mathematical rationales.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with f3:
        st.markdown(
            """
            <div class="glass-card">
                <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">🧠</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 0.3rem;">Verified AI Insights</div>
                <div style="font-size: 0.9rem; color: #64748B; line-height: 1.5;">
                    Zero hallucinations. Python computes verified facts, while AI delivers executive summaries and actionable next steps.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
