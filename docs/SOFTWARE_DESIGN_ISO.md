# Crystallytics 💎 | Software Design & Standards Compliance Specification
**ISO/IEC/IEEE 12207 | ISO/IEC/IEEE 90003 | ISO/IEC 25010 | ISO/IEC 27001 | ISO/IEC/IEEE 26514**

---

## Executive Summary

This specification establishes the formal software engineering architecture, quality management policies, information security controls, and software development life cycle (SDLC) processes for **Crystallytics 💎**.

Crystallytics is designed to adhere to international standards governing software engineering excellence, verifiable calculation integrity, and user data privacy.

---

## 1. ISO/IEC/IEEE 12207: Software Life Cycle Processes

ISO/IEC/IEEE 12207 establishes a common framework for software life cycle processes from conception through retirement. Crystallytics implements an **Iterative, Incremental, and Test-Driven Agile SDLC**.

### 1.1 Life Cycle Stages & Governance

| Stage | Process Activity | Crystallytics Implementation | Verification Deliverable |
|---|---|---|---|
| **1. Inception / Conception** | Problem statement, stakeholder definition, feasibility | Defined in Project Charter: Automated analytics for non-technical users | Functional Requirements Spec |
| **2. System Requirements** | Elicitation of functional and non-functional requirements | 5 Core Objectives (Data profiling, Auto-charts, Context detection, Zero-hallucination AI, Usable UI) | Traceability Matrix |
| **3. Architectural Design** | Component decomposition, data flow, interface definitions | Strict decoupled layer architecture separating calculation from interpretation | Architectural Schemas & Data Flow Models |
| **4. Implementation** | Software unit development, coding standards enforcement | Modular Python 3.11 packages (`src/data_loader`, `src/data_profiler`, `src/visualization`, etc.) | Unit modules, PEP 8 compliance |
| **5. Verification & Testing** | Unit, integration, and regression testing | Automated Pytest test suites across all modules | 100% passing test report (`tests/`) |
| **6. Operations & Maintenance** | Virtual environment sandboxing, dependency pinning | `.venv` isolation, `requirements.txt`, reproducible deployment | Release notes, runbook |

### 1.2 Architectural Decoupling Principle (Requirement Traceability)

Under ISO 12207 §6.4.4 (Software Architectural Design), system interfaces must enforce clear separation of concerns:
- **Rule:** The AI layer is strictly prohibited from executing arbitrary code, performing statistical estimations, or altering calculation results.
- **Enforcement:** Calculations are performed exclusively within Python (`pandas`, `numpy`). The AI model receives only the immutable, verified JSON analytical payload.

---

## 2. ISO/IEC/IEEE 90003: Software Quality Management

ISO/IEC/IEEE 90003 provides quality management guidelines (applying ISO 9001 to software development). Crystallytics establishes quality control through:

### 2.1 Configuration & Dependency Management
- **Version Control:** Repository baseline managed with Git, strict branch hygiene, and comprehensive `.gitignore` preventing environmental leakage.
- **Deterministic Dependencies:** Pinned dependencies in `requirements.txt` ensuring bit-for-bit reproducible installations across developer machines.

### 2.2 Coding Standards & Code Hygiene
- **PEP 8 Conformance:** Python code adheres strictly to standard PEP 8 naming conventions, formatting, and indentation.
- **Static Typing:** Type annotations (`typing.Union`, `Optional`, `Dict`, `List`, `Tuple`) applied to all public function signatures.
- **Documentation Hygiene:** Descriptive module-level docstrings, parameter definitions, and return-type specifications across all `src/` modules.

### 2.3 Automated Defect Prevention & Regression Testing
- Every module in `src/` is paired with an independent test suite in `tests/`:
  - `tests/test_data_loader.py` (Ingestion boundary checks)
  - `tests/test_data_profiler.py` (Mathematical & outlier checks)
  - `tests/test_visualization.py` (Figure generation checks)
  - `tests/test_context_analyzer.py` (Domain heuristics checks)
  - `tests/test_ai_interpreter.py` (Schema validation & fallback checks)
- Prior to every release or refactor, `python -m pytest` must achieve **100% pass rate**.

---

## 3. ISO/IEC 25010: Product Quality Model (SQuaRE)

ISO/IEC 25010 evaluates software products across eight fundamental quality characteristics:

### 3.1 Mapping Crystallytics to the 8 Quality Pillars

| Quality Pillar | ISO 25010 Definition | Crystallytics Architectural Implementation |
|---|---|---|
| **1. Functional Suitability** | Degree to which functions meet stated requirements under specified conditions. | Full automated profiling (missing cells, types, duplicates, outliers), automated Plotly charts, and domain detection. |
| **2. Performance Efficiency** | Performance relative to the amount of resources used under stated conditions. | Transient memory processing; execution times for profiling datasets under 100,000 rows complete in sub-seconds. |
| **3. Compatibility** | Degree to which components exchange information and perform required functions. | Seamless ingestion of standard UTF-8 and Latin-1 CSVs, multi-sheet XLSX workbooks, and Plotly/Streamlit integration. |
| **4. Usability** | Degree to which software can be understood, learned, and operated by designated users. | Clean tabbed layout (`🤖 AI Narrative`, `📈 Visualizations`, `📋 Profiling`, `🔍 Explorer`), metric cards with delta indicators, and non-technical language. |
| **5. Reliability** | Maturity, fault tolerance, and recoverability under unexpected inputs. | **Dual-Engine Architecture:** If network or API keys fail, the system falls back gracefully to its deterministic rule engine without throwing application errors. |
| **6. Security** | Degree to which data is protected from unauthorized access or exfiltration. | Zero data persistence on disk, no unaggregated row exfiltration to LLMs, and memory-only session storage. |
| **7. Maintainability** | Modularity, reusability, analyzability, and testability. | Decoupled architecture (`src/` package structure), 100% unit-tested code, Pydantic type validation. |
| **8. Portability** | Adaptability, installability, and replaceability across environments. | Pure Python 3.11 implementation running identically on Windows, Linux, and macOS. |

---

## 4. ISO/IEC 27001: Information Security Management Systems (ISMS)

ISO/IEC 27001 requires organizations to establish security controls to protect information assets. Crystallytics embeds security directly into its design:

### 4.1 Principle of Data Minimization & Zero Persistence
- **No Disk Retention:** Uploaded files are read directly from memory streams (`io.BytesIO`). Crystallytics does not write uploaded customer datasets to the local hard drive or temporary scratch disks.
- **Session Ephemerality:** When the user closes or refreshes their browser tab, memory pointers are released and garbage-collected by the Python runtime.

### 4.2 LLM Privacy & Aggregated Exfiltration Prevention
- **PII Protection:** Crystallytics **never sends raw, row-level dataset records** to external AI endpoints.
- **Aggregation Boundary:** Only the mathematical profile (summary statistics, column names, outlier counts, and high-level distribution metrics) is serialized into the payload passed to the LLM.

### 4.3 Secure Credential Management
- API keys (e.g. Gemini API) are supplied through masked password inputs (`type="password"`), stored solely in ephemeral Streamlit session memory, and are never written to source control, log files, or environment dumps.

---

## 5. ISO/IEC/IEEE 26514: User Documentation & Help Systems

ISO/IEC/IEEE 26514 sets rigorous standards for user documentation design, structure, and readability:

### 5.1 Contextual In-App Guidance
- Every interactive control in the Crystallytics dashboard features contextual tooltips (`help="..."`) explaining its purpose and operation.
- Every automated chart includes a dedicated **Rationale Card** (*"💡 Why this chart was chosen"*) that educates the user on how the selected chart corresponds to their data types.

### 5.2 Plain-English Statistical Translation
- Rather than presenting raw, obscure statistical symbols ($IQR$, $\sigma$, $\mu$, $p$), the interface accompanies statistics with human-friendly descriptions (e.g., *"Statistical Dispersion: Column exhibits 2 potential outliers outside $1.5 \times \text{IQR}$"*).

### 5.3 Comprehensive Developer Documentation
- Standardized documentation across `README.md`, docstrings, and architectural diagrams allows any engineer to understand, audit, and extend the system.

---

## 6. Standards Compliance Checklist

- [x] **ISO/IEC/IEEE 12207:** Modular SDLC lifecycle, decoupled calculation/interpretation architecture.
- [x] **ISO/IEC/IEEE 90003:** Pinned configuration dependencies, PEP 8 style, Pytest test automation.
- [x] **ISO/IEC 25010:** All 8 quality characteristics formally addressed and implemented.
- [x] **ISO/IEC 27001:** Zero-persistence memory streaming, aggregated-only LLM payloads, credential protection.
- [x] **ISO/IEC/IEEE 26514:** Contextual help tooltips, chart rationale annotations, plain-English statistics.
