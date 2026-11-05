/**
 * js/charts.js
 * Intelligent chart recommendation and Chart.js rendering for Crystallytics.
 */

// Active Chart instances storage so we can destroy and recreate on update
const activeCharts = {};

export function recommendVisualizations(data, headers, profiles) {
    const recs = [];
    const numericCols = profiles.filter(p => p.type === "Numeric").map(p => p.column);
    const categoricalCols = profiles.filter(p => p.type === "Categorical").map(p => p.column);
    const datetimeCols = profiles.filter(p => p.type === "Datetime").map(p => p.column);

    // 1. Time Series Line Chart
    if (datetimeCols.length > 0 && numericCols.length > 0) {
        recs.push({
            id: "chart_line",
            type: "line",
            title: `Trend of ${numericCols[0]} over ${datetimeCols[0]}`,
            reason: `Tracks chronological progress of '${numericCols[0]}' over '${datetimeCols[0]}'.`,
            params: { dateCol: datetimeCols[0], numCol: numericCols[0] }
        });
    }

    // 2. Categorical Bar Chart
    if (categoricalCols.length > 0 && numericCols.length > 0) {
        recs.push({
            id: "chart_bar",
            type: "bar",
            title: `${numericCols[0]} by ${categoricalCols[0]} (Top 15)`,
            reason: `Compares '${numericCols[0]}' aggregations across '${categoricalCols[0]}' segments.`,
            params: { catCol: categoricalCols[0], numCol: numericCols[0] }
        });
    } else if (categoricalCols.length > 0) {
        recs.push({
            id: "chart_bar_count",
            type: "bar_count",
            title: `Record Counts by ${categoricalCols[0]}`,
            reason: `Shows distribution frequency of records across '${categoricalCols[0]}'.`,
            params: { catCol: categoricalCols[0] }
        });
    }

    // 3. Scatter Plot (if >= 2 numeric)
    if (numericCols.length >= 2) {
        recs.push({
            id: "chart_scatter",
            type: "scatter",
            title: `Relationship: ${numericCols[0]} vs ${numericCols[1]}`,
            reason: `Explores correlation and clusters between '${numericCols[0]}' and '${numericCols[1]}'.`,
            params: { xCol: numericCols[0], yCol: numericCols[1] }
        });
    }

    // 4. Distribution Bar / Histogram for primary metric
    if (numericCols.length > 0) {
        recs.push({
            id: "chart_dist",
            type: "dist",
            title: `Distribution of ${numericCols[0]}`,
            reason: `Displays the value distribution and frequency bins of '${numericCols[0]}'.`,
            params: { col: numericCols[0] }
        });
    }

    return recs;
}

export function renderChart(containerId, rec, data) {
    const canvas = document.getElementById(containerId);
    if (!canvas) return;

    if (activeCharts[containerId]) {
        activeCharts[containerId].destroy();
    }

    const ctx = canvas.getContext("2d");
    const { type, params } = rec;

    let chartConfig = null;

    if (type === "line") {
        const sorted = [...data].filter(r => r[params.dateCol] && r[params.numCol] !== null)
            .sort((a, b) => new Date(a[params.dateCol]) - new Date(b[params.dateCol]));

        const labels = sorted.map(r => String(r[params.dateCol]).split("T")[0]);
        const values = sorted.map(r => Number(r[params.numCol]) || 0);

        chartConfig = {
            type: "line",
            data: {
                labels,
                datasets: [{
                    label: params.numCol,
                    data: values,
                    borderColor: "#0072FF",
                    backgroundColor: "rgba(0, 114, 255, 0.08)",
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.25,
                    pointRadius: 4,
                    pointBackgroundColor: "#0072FF"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false } },
                    y: { grid: { color: "#F1F5F9" } }
                }
            }
        };
    } else if (type === "bar" || type === "bar_count") {
        const group = {};
        data.forEach(r => {
            const k = String(r[params.catCol] || "Unknown");
            const val = type === "bar" ? (Number(r[params.numCol]) || 0) : 1;
            group[k] = (group[k] || 0) + val;
        });

        const sorted = Object.entries(group).sort((a, b) => b[1] - a[1]).slice(0, 15);
        const labels = sorted.map(s => s[0]);
        const values = sorted.map(s => s[1]);

        chartConfig = {
            type: "bar",
            data: {
                labels,
                datasets: [{
                    label: type === "bar" ? params.numCol : "Count",
                    data: values,
                    backgroundColor: "#3B82F6",
                    borderRadius: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false } },
                    y: { grid: { color: "#F1F5F9" } }
                }
            }
        };
    } else if (type === "scatter") {
        const points = data.map(r => ({
            x: Number(r[params.xCol]),
            y: Number(r[params.yCol])
        })).filter(p => !isNaN(p.x) && !isNaN(p.y));

        chartConfig = {
            type: "scatter",
            data: {
                datasets: [{
                    label: `${params.xCol} vs ${params.yCol}`,
                    data: points,
                    backgroundColor: "rgba(127, 0, 255, 0.65)",
                    borderColor: "#7F00FF",
                    pointRadius: 5,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { title: { display: true, text: params.xCol }, grid: { color: "#F1F5F9" } },
                    y: { title: { display: true, text: params.yCol }, grid: { color: "#F1F5F9" } }
                }
            }
        };
    } else if (type === "dist") {
        const rawVals = data.map(r => Number(r[params.col])).filter(v => !isNaN(v));
        const min = Math.min(...rawVals);
        const max = Math.max(...rawVals);
        const bins = 10;
        const binWidth = (max - min) / bins || 1;
        const binCounts = new Array(bins).fill(0);
        const binLabels = [];

        for (let i = 0; i < bins; i++) {
            const start = (min + i * binWidth).toFixed(1);
            const end = (min + (i + 1) * binWidth).toFixed(1);
            binLabels.push(`${start} - ${end}`);
        }

        rawVals.forEach(v => {
            const idx = Math.min(Math.floor((v - min) / binWidth), bins - 1);
            if (idx >= 0) binCounts[idx]++;
        });

        chartConfig = {
            type: "bar",
            data: {
                labels: binLabels,
                datasets: [{
                    label: "Frequency",
                    data: binCounts,
                    backgroundColor: "#10B981",
                    borderRadius: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { maxRotation: 45, minRotation: 30 } },
                    y: { grid: { color: "#F1F5F9" } }
                }
            }
        };
    }

    if (chartConfig) {
        activeCharts[containerId] = new Chart(ctx, chartConfig);
    }
}
