/**
 * js/app.js
 * Main application controller for Crystallytics.
 */

import {
    computeDatasetOverview,
    computeColumnProfiles,
    computeNumericSummary,
    computeDataQualityWarnings,
    inferDomainContext
} from './profiler.js';

import { recommendVisualizations, renderChart } from './charts.js';
import { interpretWithGemini, downloadMarkdownReport } from './ai_interpreter.js';

// Application State
let currentData = [];
let currentHeaders = [];
let currentFilename = "";
let currentOverview = null;
let currentDomain = null;
let currentInterpretation = null;

// Built-in Demo Sales Data (Embedded for instantaneous 1-click test without server requirements)
const DEMO_SALES_CSV = `Date,Product,Region,Units Sold,Unit Price,Customer Rating,Revenue
2024-01-01,Laptop,North,12,1200.0,4.5,14400.0
2024-01-02,Mouse,South,45,25.0,4.2,1125.0
2024-01-03,Keyboard,East,23,75.0,4.8,1725.0
2024-01-04,Monitor,West,15,300.0,3.9,4500.0
2024-01-05,Headphones,North,30,80.0,4.6,2400.0
2024-01-06,Laptop,South,10,1200.0,4.1,12000.0
2024-01-07,Mouse,East,50,25.0,4.3,1250.0
2024-01-08,Keyboard,West,20,75.0,4.7,1500.0
2024-01-09,Monitor,North,18,300.0,4.0,5400.0
2024-01-10,Headphones,South,25,80.0,4.5,2000.0
2024-01-11,Laptop,East,14,1200.0,4.4,16800.0
2024-01-12,Mouse,West,40,25.0,4.2,1000.0
2024-01-13,Keyboard,North,22,75.0,4.9,1650.0
2024-01-14,Monitor,South,16,300.0,3.8,4800.0
2024-01-15,Headphones,East,28,80.0,4.6,2240.0
2024-01-16,Laptop,West,11,1200.0,4.3,13200.0
2024-01-17,Mouse,North,48,25.0,4.1,1200.0
2024-01-18,Keyboard,South,21,75.0,4.8,1575.0
2024-01-19,Monitor,East,17,300.0,4.2,5100.0
2024-01-20,Headphones,West,32,80.0,4.7,2560.0`;

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initFileUpload();
    initDemoButton();
    initDownloadButton();
    initCustomExplorer();
});

function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            const targetId = btn.getAttribute("data-tab");
            document.getElementById(targetId)?.classList.add("active");
        });
    });
}

function initFileUpload() {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("file-input");

    dropzone.addEventListener("click", () => fileInput.click());

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dragover");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });
}

function initDemoButton() {
    const btn = document.getElementById("btn-demo");
    btn.addEventListener("click", () => {
        Papa.parse(DEMO_SALES_CSV, {
            header: true,
            dynamicTyping: true,
            skipEmptyLines: true,
            complete: (results) => {
                processDataset(results.data, results.meta.fields, "sample_sales.csv (Demo)");
            }
        });
    });
}

function handleFile(file) {
    const filename = file.name;
    const isExcel = filename.endsWith(".xlsx") || filename.endsWith(".xls");

    if (isExcel) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, { type: "array" });
            const firstSheet = workbook.SheetNames[0];
            const sheet = workbook.Sheets[firstSheet];
            const json = XLSX.utils.sheet_to_json(sheet, { header: 1 });

            if (json.length < 2) {
                alert("The Excel file does not contain enough data rows.");
                return;
            }

            const headers = json[0];
            const rows = json.slice(1).map(row => {
                const obj = {};
                headers.forEach((h, idx) => { obj[h] = row[idx] !== undefined ? row[idx] : null; });
                return obj;
            });

            processDataset(rows, headers, filename);
        };
        reader.readAsArrayBuffer(file);
    } else {
        // Assume CSV
        Papa.parse(file, {
            header: true,
            dynamicTyping: true,
            skipEmptyLines: true,
            complete: (results) => {
                if (results.data.length === 0) {
                    alert("The uploaded CSV is empty.");
                    return;
                }
                processDataset(results.data, results.meta.fields, filename);
            },
            error: (err) => {
                alert(`Error reading CSV: ${err.message}`);
            }
        });
    }
}

async function processDataset(data, headers, filename) {
    currentData = data;
    currentHeaders = headers;
    currentFilename = filename;

    // 1. Profiling
    const overview = computeDatasetOverview(data, headers);
    currentOverview = overview;
    const profiles = computeColumnProfiles(data, headers);
    const summary = computeNumericSummary(data, headers, profiles);
    const warnings = computeDataQualityWarnings(data, headers, profiles);
    const domainContext = inferDomainContext(headers, data, profiles);
    currentDomain = domainContext.domain;

    // 2. Hide Landing, Show Dashboard
    document.getElementById("landing-state").style.display = "none";
    document.getElementById("dashboard-state").style.display = "block";

    // 3. Render Top Metrics
    renderMetrics(overview, data, headers);

    // 4. Render Domain Banner
    renderDomainBanner(domainContext);

    // 5. Render Quality Alerts
    renderQualityAlerts(warnings);

    // 6. Build AI Payload & Render AI Narrative
    const payload = {
        datasetHealth: overview,
        inferredDomain: domainContext,
        pythonVerifiedObservations: domainContext.observations,
        numericStatistics: summary,
        dataQualityFlags: warnings
    };

    const apiKey = document.getElementById("api-key-input")?.value?.trim();
    document.getElementById("ai-engine-badge").textContent = apiKey ? "Google Gemini 2.5 Flash" : "Local Verifiable Engine";

    const interpretation = await interpretWithGemini(payload, apiKey);
    currentInterpretation = interpretation;
    renderAiNarrative(interpretation);

    // 7. Render Charts
    renderVisualizationsTab(data, headers, profiles);

    // 8. Render Data Tables
    renderDataTables(data, headers, profiles, summary);

    // 9. Setup Custom Explorer
    setupCustomExplorer(data, profiles);
}

function renderMetrics(overview, data, headers) {
    document.getElementById("metric-rows").textContent = overview.totalRows.toLocaleString();
    document.getElementById("metric-cols").textContent = overview.totalColumns.toLocaleString();
    
    const missingEl = document.getElementById("metric-missing");
    missingEl.textContent = overview.missingCells.toLocaleString();
    missingEl.style.color = overview.missingCells === 0 ? "var(--color-success)" : "var(--color-danger)";
    document.getElementById("metric-missing-sub").textContent = `${overview.missingPct}% Missing`;

    const dupeEl = document.getElementById("metric-dupes");
    dupeEl.textContent = overview.duplicateRows.toLocaleString();
    dupeEl.style.color = overview.duplicateRows === 0 ? "var(--color-success)" : "var(--color-warning)";
    document.getElementById("metric-dupes-sub").textContent = `${overview.duplicatePct}% Dupes`;

    document.getElementById("metric-memory").textContent = `${overview.memoryUsageKb} KB`;
}

function renderDomainBanner(domainContext) {
    document.getElementById("domain-name").textContent = domainContext.domain;
    document.getElementById("domain-conf").textContent = `(Confidence: ${domainContext.confidence})`;
    const signalsEl = document.getElementById("domain-signals");
    if (domainContext.matchedKeywords.length > 0) {
        signalsEl.innerHTML = `<b>Signals Detected:</b> <code>${domainContext.matchedKeywords.join(", ")}</code>`;
    } else {
        signalsEl.textContent = "General quantitative data pattern evaluated.";
    }
}

function renderQualityAlerts(warnings) {
    const container = document.getElementById("quality-alerts-container");
    container.innerHTML = "";
    if (warnings.length > 0) {
        document.getElementById("quality-alerts-card").style.display = "block";
        warnings.forEach(w => {
            const div = document.createElement("div");
            div.className = "quality-alert";
            div.innerHTML = w;
            container.appendChild(div);
        });
    } else {
        document.getElementById("quality-alerts-card").style.display = "none";
    }
}

function renderAiNarrative(interp) {
    document.getElementById("exec-summary-text").textContent = interp.executiveSummary;

    // Key findings
    const findingsList = document.getElementById("ai-findings-list");
    findingsList.innerHTML = "";
    interp.keyFindings.forEach(f => {
        const div = document.createElement("div");
        div.className = "insight-item insight-item-green";
        div.innerHTML = f;
        findingsList.appendChild(div);
    });

    // Trends
    const trendsList = document.getElementById("ai-trends-list");
    trendsList.innerHTML = "";
    interp.identifiedTrends.forEach(t => {
        const div = document.createElement("div");
        div.className = "insight-item";
        div.textContent = t;
        trendsList.appendChild(div);
    });

    // Anomalies
    const anomaliesList = document.getElementById("ai-anomalies-list");
    anomaliesList.innerHTML = "";
    interp.potentialAnomalies.forEach(a => {
        const div = document.createElement("div");
        div.className = "insight-item insight-item-amber";
        div.textContent = a;
        anomaliesList.appendChild(div);
    });

    // Limitations
    const limitsList = document.getElementById("ai-limits-list");
    limitsList.innerHTML = "";
    interp.limitationsAndCautions.forEach(l => {
        const div = document.createElement("div");
        div.className = "insight-item insight-item-purple";
        div.textContent = l;
        limitsList.appendChild(div);
    });

    // Next steps
    const stepsList = document.getElementById("ai-steps-list");
    stepsList.innerHTML = "";
    interp.recommendedNextSteps.forEach((s, idx) => {
        const li = document.createElement("li");
        li.style.marginBottom = "0.4rem";
        li.innerHTML = `<b>${idx + 1}.</b> ${s}`;
        stepsList.appendChild(li);
    });
}

function renderVisualizationsTab(data, headers, profiles) {
    const recs = recommendVisualizations(data, headers, profiles);
    const container = document.getElementById("charts-container");
    container.innerHTML = "";

    recs.forEach(rec => {
        const card = document.createElement("div");
        card.className = "chart-card";

        const canvasId = `canvas_${rec.id}`;
        card.innerHTML = `
            <div class="chart-card-header">
                <div class="chart-card-title">${rec.title}</div>
                <div class="chart-card-reason">💡 ${rec.reason}</div>
            </div>
            <div class="chart-canvas-wrapper">
                <canvas id="${canvasId}"></canvas>
            </div>
        `;
        container.appendChild(card);

        // Render with Chart.js
        setTimeout(() => renderChart(canvasId, rec, data), 50);
    });
}

function renderDataTables(data, headers, profiles, summary) {
    // 1. Preview Table (first 25 rows)
    const previewHead = document.getElementById("table-preview-head");
    const previewBody = document.getElementById("table-preview-body");
    previewHead.innerHTML = `<tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr>`;
    previewBody.innerHTML = data.slice(0, 25).map(r => {
        return `<tr>${headers.map(h => `<td>${r[h] !== null && r[h] !== undefined ? r[h] : '<i style="color:#94A3B8">null</i>'}</td>`).join("")}</tr>`;
    }).join("");

    // 2. Profiles Table
    const profBody = document.getElementById("table-profiles-body");
    profBody.innerHTML = profiles.map(p => `
        <tr>
            <td><b>${p.column}</b></td>
            <td><span class="badge badge-iso">${p.type}</span></td>
            <td>${p.missingCount} (${p.missingPct}%)</td>
            <td>${p.uniqueCount}</td>
        </tr>
    `).join("");

    // 3. Stats Table
    const statsBody = document.getElementById("table-stats-body");
    statsBody.innerHTML = summary.map(s => `
        <tr>
            <td><b>${s.column}</b></td>
            <td>${s.mean}</td>
            <td>${s.stdDev}</td>
            <td>${s.min}</td>
            <td>${s.q1}</td>
            <td>${s.median}</td>
            <td>${s.q3}</td>
            <td>${s.max}</td>
            <td>${s.outliersCount > 0 ? `<b style="color:var(--color-warning)">${s.outliersCount}</b>` : "0"}</td>
        </tr>
    `).join("");
}

function setupCustomExplorer(data, profiles) {
    const select = document.getElementById("select-custom-col");
    const numericCols = profiles.filter(p => p.type === "Numeric").map(p => p.column);

    select.innerHTML = numericCols.map(c => `<option value="${c}">${c}</option>`).join("");

    const updateCustomPlot = () => {
        const col = select.value;
        if (!col) return;
        const rec = {
            id: "custom_chart",
            type: "dist",
            title: `Distribution of ${col}`,
            reason: `Frequency histogram of values for ${col}`,
            params: { col }
        };
        renderChart("canvas-custom-chart", rec, data);
    };

    select.addEventListener("change", updateCustomPlot);
    if (numericCols.length > 0) {
        updateCustomPlot();
    }
}

function initDownloadButton() {
    const btn = document.getElementById("btn-download-report");
    btn.addEventListener("click", () => {
        if (!currentOverview || !currentInterpretation) return;
        downloadMarkdownReport(currentFilename, currentDomain, currentOverview, currentInterpretation);
    });
}
function initCustomExplorer() {}
