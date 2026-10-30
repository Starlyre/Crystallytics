# Crystallytics 💎
**Crystal-Clear, Context-Aware Automated Data Analytics**

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.66-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Antigravity](https://img.shields.io/badge/Engineered%20With-Google%20Antigravity-4285F4?style=flat&logo=google&logoColor=white)](https://deepmind.google)
[![ISO 25010](https://img.shields.io/badge/Architecture-ISO%2FIEC%2025010-059669?style=flat)](https://www.iso.org/standard/35733.html)
[![Tests Passing](https://img.shields.io/badge/Tests-15%2F15%20Passed-10B981?style=flat&logo=pytest&logoColor=white)](https://docs.pytest.org/)

> **Crystallytics** blends *crystallize* (bringing absolute clarity out of messy raw data), *tally* (rigorous, verifiable mathematical calculation by Python), and *analytics* (automated profiling, interactive visualizations, and AI narratives).

Crystallytics bridges the gap between raw datasets and executive understanding. It allows users to upload Excel or CSV files and instantly receive verified statistical calculations, context-aware visual charts, and reliable AI-generated narrative interpretations.

---

## 🌟 Key Features

1. **Robust Data Ingestion (`src/data_loader.py`)**
   - Supports `.csv` and `.xlsx` formats.
   - Automatic fallback character encoding detection (UTF-8 and Latin-1).
   - Validation against empty or corrupted files.

2. **Automated Profiling & Data Quality Engine (`src/data_profiler.py`)**
   - **Smart Type Detection**: Infers logical types (*Numeric*, *Categorical*, *Datetime*, *Boolean*, *Text/ID*).
   - **Health Metrics**: Total rows, columns, missing cells %, duplicate records %, and memory footprint.
   - **Statistical Deep-Dive**: Computes mean, median, standard deviation, quartiles ($Q_1$, $Q_3$), and detects outliers using the $1.5 \times \text{IQR}$ rule.
   - **Data Quality Alerts**: Warns of excessive missingness ($\ge 40\%$), exact duplicate rows, or zero-variance columns.

3. **Intelligent Visualization Recommender (`src/visualization.py`)**
   - Recommends charts tailored to the detected data types:
     - **Time-series Line Charts**: Automatically tracks metrics over chronological dates.
     - **Categorical Bar Charts**: Shows metric sums or frequency distributions.
     - **Correlation Heatmap**: Visualizes linear relationships across numeric columns.
     - **Scatter Plots**: Identifies clusters and multi-variable correlations.
     - **Box Plots**: Compares distribution spread across categorical groups.
   - Every chart includes a *"Why this chart was chosen"* rationale card.

4. **Domain & Context Awareness (`src/context_analyzer.py`)**
   - Detects the subject domain (e.g. *Sales & Commercial*, *Human Resources*, *Financial*, *Healthcare*, or *General Tabular*).
   - Performs domain-specific calculations (e.g., top contributing product, total revenue volume, compensation benchmarks).

5. **Strictly Grounded AI Interpretations (`src/ai_interpreter.py`)**
   - **Zero Hallucinations**: Python computes all numbers first. The AI interprets only verified results.
   - **Pydantic Validation**: Structured JSON responses strictly conforming to `DatasetInterpretation`.
   - **Dual-Mode Engine**: Operates seamlessly offline with the built-in deterministic analytics engine, or connects live to Google Gemini 2.5 Flash via optional API key.

---

## 🏗️ Architecture

```text
Crystallytics/
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py        # Safe ingestion & encoding handling
│   ├── data_profiler.py      # Statistical profiling & data quality checks
│   ├── visualization.py      # Automated chart recommendation & Plotly rendering
│   ├── context_analyzer.py   # Domain inference & domain-specific analytics
│   └── ai_interpreter.py     # Pydantic schema & Gemini LLM interpretation layer
│
├── tests/
│   ├── test_data_loader.py
│   ├── test_data_profiler.py
│   ├── test_visualization.py
│   ├── test_context_analyzer.py
│   └── test_ai_interpreter.py
│
├── data/
│   ├── sample_sales.csv
│   └── sample_sales.xlsx
│
├── app.py                    # Streamlit dashboard
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### 1. Activate the Virtual Environment
In Windows PowerShell:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2. Run the Application
```powershell
python -m streamlit run app.py
```
Open `http://localhost:8501` in your browser.

### 3. Run Automated Tests
```powershell
python -m pytest
```
All 15 tests should pass.

---

## 🛠️ Engineering & Acknowledgements

- **Development Environment:** Architected and developed with **Google Antigravity** (Google DeepMind's advanced agentic coding environment).
- **Standards Conformance:** Formally aligns with ISO/IEC/IEEE 12207, 90003, 25010, 27001, and 26514 (documented in [`docs/SOFTWARE_DESIGN_ISO.md`](docs/SOFTWARE_DESIGN_ISO.md)).
- **Core Stack:** Python 3.11, Pandas, NumPy, Plotly Express, Streamlit, Pydantic, and Google Gemini API.
