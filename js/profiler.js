/**
 * js/profiler.js
 * Comprehensive client-side data profiling, statistical computation,
 * and domain context detection for Crystallytics.
 */

export function detectColumnType(values) {
    const validValues = values.filter(v => v !== null && v !== undefined && v !== "");
    if (validValues.length === 0) return "Categorical";

    // 1. Check Boolean
    const boolCount = validValues.filter(v => 
        v === true || v === false || 
        String(v).toLowerCase() === "true" || String(v).toLowerCase() === "false" ||
        v === 0 || v === 1 || String(v) === "0" || String(v) === "1"
    ).length;
    if (boolCount === validValues.length && new Set(validValues).size <= 2) {
        return "Boolean";
    }

    // 2. Check Numeric
    const numCount = validValues.filter(v => {
        if (typeof v === "number") return true;
        const cleaned = String(v).replace(/[\$,]/g, "").trim();
        return !isNaN(Number(cleaned)) && cleaned !== "";
    }).length;
    if (numCount / validValues.length > 0.85) {
        return "Numeric";
    }

    // 3. Check Datetime
    const dateCount = validValues.filter(v => {
        if (v instanceof Date) return true;
        const s = String(v).trim();
        if (s.length < 8) return false;
        const timestamp = Date.parse(s);
        return !isNaN(timestamp) && (s.includes("-") || s.includes("/") || s.includes("T"));
    }).length;
    if (dateCount / validValues.length > 0.8) {
        return "Datetime";
    }

    // 4. Categorical vs Text/ID
    const uniqueCount = new Set(validValues).size;
    const uniquenessRatio = uniqueCount / validValues.length;
    if (uniquenessRatio > 0.7 && validValues.length > 20) {
        return "Text/ID";
    }

    return "Categorical";
}

export function computeDatasetOverview(data, headers) {
    const totalRows = data.length;
    const totalColumns = headers.length;
    const totalCells = totalRows * totalColumns;

    let missingCells = 0;
    const rowHashes = new Set();
    let duplicateRows = 0;

    data.forEach(row => {
        const rowStr = JSON.stringify(row);
        if (rowHashes.has(rowStr)) {
            duplicateRows++;
        } else {
            rowHashes.add(rowStr);
        }

        headers.forEach(h => {
            const v = row[h];
            if (v === null || v === undefined || v === "" || (typeof v === "number" && isNaN(v))) {
                missingCells++;
            }
        });
    });

    const missingPct = totalCells > 0 ? ((missingCells / totalCells) * 100).toFixed(1) : "0.0";
    const duplicatePct = totalRows > 0 ? ((duplicateRows / totalRows) * 100).toFixed(1) : "0.0";
    const memoryUsageKb = ((JSON.stringify(data).length * 2) / 1024).toFixed(1);

    return {
        totalRows,
        totalColumns,
        totalCells,
        missingCells,
        missingPct,
        duplicateRows,
        duplicatePct,
        memoryUsageKb,
    };
}

export function computeColumnProfiles(data, headers) {
    return headers.map(header => {
        const values = data.map(r => r[header]);
        const detectedType = detectColumnType(values);
        const missingCount = values.filter(v => v === null || v === undefined || v === "" || (typeof v === "number" && isNaN(v))).length;
        const validValues = values.filter(v => v !== null && v !== undefined && v !== "");
        const uniqueCount = new Set(validValues).size;
        const missingPct = data.length > 0 ? ((missingCount / data.length) * 100).toFixed(1) : "0.0";

        return {
            column: header,
            type: detectedType,
            missingCount,
            missingPct,
            uniqueCount,
        };
    });
}

export function computeNumericSummary(data, headers, profiles) {
    const numericCols = profiles.filter(p => p.type === "Numeric").map(p => p.column);
    const summaries = [];

    numericCols.forEach(col => {
        const rawVals = data.map(r => {
            const v = r[col];
            if (v === null || v === undefined || v === "") return NaN;
            return typeof v === "number" ? v : Number(String(v).replace(/[\$,]/g, "").trim());
        }).filter(v => !isNaN(v));

        if (rawVals.length === 0) return;

        rawVals.sort((a, b) => a - b);
        const count = rawVals.length;
        const sum = rawVals.reduce((acc, v) => acc + v, 0);
        const mean = sum / count;

        const min = rawVals[0];
        const max = rawVals[count - 1];

        const q1 = quantile(rawVals, 0.25);
        const median = quantile(rawVals, 0.50);
        const q3 = quantile(rawVals, 0.75);
        const iqr = q3 - q1;

        const variance = rawVals.reduce((acc, v) => acc + Math.pow(v - mean, 2), 0) / (count > 1 ? count - 1 : 1);
        const stdDev = Math.sqrt(variance);

        const lowerBound = q1 - 1.5 * iqr;
        const upperBound = q3 + 1.5 * iqr;
        const outliersCount = rawVals.filter(v => v < lowerBound || v > upperBound).length;

        summaries.push({
            column: col,
            mean: mean.toFixed(2),
            stdDev: stdDev.toFixed(2),
            min: min.toFixed(2),
            q1: q1.toFixed(2),
            median: median.toFixed(2),
            q3: q3.toFixed(2),
            max: max.toFixed(2),
            outliersCount,
        });
    });

    return summaries;
}

function quantile(arr, q) {
    const pos = (arr.length - 1) * q;
    const base = Math.floor(pos);
    const rest = pos - base;
    if (arr[base + 1] !== undefined) {
        return arr[base] + rest * (arr[base + 1] - arr[base]);
    }
    return arr[base];
}

export function computeDataQualityWarnings(data, headers, profiles) {
    const warnings = [];
    const totalRows = data.length;

    // 1. Duplicates
    const rowHashes = new Set();
    let dupes = 0;
    data.forEach(r => {
        const s = JSON.stringify(r);
        if (rowHashes.has(s)) dupes++;
        else rowHashes.add(s);
    });
    if (dupes > 0) {
        const pct = ((dupes / totalRows) * 100).toFixed(1);
        warnings.push(`⚠️ <b>Duplicate records found:</b> ${dupes} rows (${pct}%) appear to be exact duplicates.`);
    }

    // 2. High missingness
    profiles.forEach(p => {
        if (parseFloat(p.missingPct) >= 40) {
            warnings.push(`⚠️ <b>High missing data:</b> Column <b>\`${p.column}\`</b> is missing ${p.missingPct}% of its values (${p.missingCount} rows).`);
        }
        if (p.uniqueCount === 1 && totalRows > 1) {
            warnings.push(`ℹ️ <b>Constant column:</b> Column <b>\`${p.column}\`</b> contains only a single unique value.`);
        }
    });

    return warnings;
}

export function inferDomainContext(headers, data, profiles) {
    const DOMAINS = {
        "Sales & Commercial": {
            keywords: ["sale", "sales", "revenue", "price", "unit", "units", "product", "order", "orders", "quantity", "discount", "profit"],
            primaryMetric: ["revenue", "sales", "profit", "total", "amount"],
            entity: ["product", "item", "category", "region", "customer"]
        },
        "Human Resources & Workforce": {
            keywords: ["employee", "salary", "wage", "department", "role", "experience", "hire", "tenure", "performance", "bonus"],
            primaryMetric: ["salary", "wage", "compensation", "bonus"],
            entity: ["department", "role", "title", "employee", "team"]
        },
        "Financial & Accounting": {
            keywords: ["balance", "credit", "debit", "transaction", "asset", "expense", "cost", "income", "budget", "invoice"],
            primaryMetric: ["amount", "balance", "cost", "expense", "budget"],
            entity: ["account", "category", "type", "client", "vendor"]
        },
        "Healthcare & Clinical": {
            keywords: ["patient", "diagnosis", "glucose", "blood", "treatment", "dosage", "symptom", "hospital", "physician"],
            primaryMetric: ["dosage", "age", "level", "score", "measurement"],
            entity: ["diagnosis", "treatment", "department", "condition"]
        }
    };

    const cleanHeaders = headers.map(h => String(h).toLowerCase().replace(/[-_]/g, " "));
    let bestDomain = "General Tabular Dataset";
    let bestScore = 0;
    let matchedKeywords = [];

    for (const [dom, conf] of Object.entries(DOMAINS)) {
        let score = 0;
        const matches = [];
        conf.keywords.forEach(kw => {
            cleanHeaders.forEach(h => {
                if (h.split(" ").includes(kw)) {
                    score += 2;
                    matches.push(kw);
                } else if (h.includes(kw)) {
                    score += 1;
                    matches.push(kw);
                }
            });
        });
        if (score > bestScore) {
            bestScore = score;
            bestDomain = dom;
            matchedKeywords = [...new Set(matches)];
        }
    }

    const confidence = bestScore >= 4 ? "High" : (bestScore >= 2 ? "Medium" : "General");
    if (bestScore < 2) bestDomain = "General Tabular Dataset";

    // Factual Observations
    const observations = [];
    const findCol = (candidates) => {
        for (const cand of candidates) {
            for (const orig of headers) {
                if (orig.toLowerCase().includes(cand)) return orig;
            }
        }
        return null;
    };

    if (bestDomain === "Sales & Commercial") {
        const metricCol = findCol(DOMAINS["Sales & Commercial"].primaryMetric);
        const entityCol = findCol(DOMAINS["Sales & Commercial"].entity);

        if (metricCol) {
            const vals = data.map(r => Number(r[metricCol]) || 0);
            const total = vals.reduce((a, b) => a + b, 0);
            const avg = total / (vals.length || 1);
            observations.push(`<b>Total Volume:</b> Overall <code>${metricCol}</code> totals <b>${total.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</b> with an average of <b>${avg.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</b> per record.`);

            if (entityCol) {
                const group = {};
                data.forEach(r => {
                    const k = r[entityCol] || "Unknown";
                    group[k] = (group[k] || 0) + (Number(r[metricCol]) || 0);
                });
                const sorted = Object.entries(group).sort((a, b) => b[1] - a[1]);
                if (sorted.length > 0) {
                    const top = sorted[0];
                    const share = total > 0 ? ((top[1] / total) * 100).toFixed(1) : 0;
                    observations.push(`<b>Top Contributor:</b> <code>${top[0]}</code> leads <code>${entityCol}</code> with <b>${top[1].toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</b> in <code>${metricCol}</code> (${share}% of total).`);
                }
            }
        }
    }

    // General outlier / dispersion check
    const numericCols = profiles.filter(p => p.type === "Numeric").map(p => p.column);
    if (numericCols.length > 0) {
        const col = numericCols[0];
        const rawVals = data.map(r => Number(r[col])).filter(v => !isNaN(v)).sort((a, b) => a - b);
        if (rawVals.length >= 4) {
            const q1 = quantile(rawVals, 0.25);
            const q3 = quantile(rawVals, 0.75);
            const iqr = q3 - q1;
            const outliers = rawVals.filter(v => v < (q1 - 1.5 * iqr) || v > (q3 + 1.5 * iqr)).length;
            if (outliers > 0) {
                observations.push(`<b>Statistical Dispersion:</b> <code>${col}</code> exhibits <b>${outliers} potential outlier(s)</b> outside 1.5x IQR.`);
            }
        }
    }

    if (observations.length === 0) {
        observations.push("Dataset evaluated. Numerical and categorical distributions profiled across all available variables.");
    }

    return {
        domain: bestDomain,
        confidence,
        matchedKeywords,
        observations
    };
}
