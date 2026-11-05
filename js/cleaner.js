/**
 * js/cleaner.js
 * 1-Click Data Cleaning Engine for Crystallytics.
 * Handles deduplication, smart imputation (mean, median, mode),
 * outlier handling (clipping or removal via 1.5x IQR), and whitespace sanitization.
 */

export function cleanDataset(data, headers, profiles, options = {}) {
    const {
        removeDuplicates = true,
        imputeStrategy = "median", // "none", "drop", "median", "mean"
        outlierStrategy = "keep",  // "keep", "clip", "drop"
        trimWhitespace = true
    } = options;

    let workingData = JSON.parse(JSON.stringify(data));
    const initialRows = workingData.length;
    let initialMissing = 0;
    let initialDupes = 0;

    // Track initial metrics
    const initialRowHashes = new Set();
    workingData.forEach(r => {
        const s = JSON.stringify(r);
        if (initialRowHashes.has(s)) initialDupes++;
        else initialRowHashes.add(s);

        headers.forEach(h => {
            const v = r[h];
            if (v === null || v === undefined || v === "" || (typeof v === "number" && isNaN(v))) {
                initialMissing++;
            }
        });
    });

    // 1. Trim Whitespace from string columns
    if (trimWhitespace) {
        workingData.forEach(r => {
            headers.forEach(h => {
                if (typeof r[h] === "string") {
                    r[h] = r[h].trim();
                }
            });
        });
    }

    // 2. Remove Exact Duplicates
    let duplicatesRemoved = 0;
    if (removeDuplicates) {
        const seen = new Set();
        const deduplicated = [];
        workingData.forEach(r => {
            const s = JSON.stringify(r);
            if (!seen.has(s)) {
                seen.add(s);
                deduplicated.push(r);
            } else {
                duplicatesRemoved++;
            }
        });
        workingData = deduplicated;
    }

    // 3. Handle Missing Values
    let missingRowsDropped = 0;
    let missingValuesImputed = 0;

    if (imputeStrategy === "drop") {
        const nonNullRows = workingData.filter(r => {
            const hasNull = headers.some(h => {
                const v = r[h];
                return v === null || v === undefined || v === "" || (typeof v === "number" && isNaN(v));
            });
            return !hasNull;
        });
        missingRowsDropped = workingData.length - nonNullRows.length;
        workingData = nonNullRows;
    } else if (imputeStrategy === "median" || imputeStrategy === "mean") {
        // Pre-calculate column stats for imputation
        const colImputeValues = {};

        profiles.forEach(p => {
            const h = p.column;
            if (p.type === "Numeric") {
                const nums = workingData
                    .map(r => Number(r[h]))
                    .filter(v => !isNaN(v) && v !== null);

                if (nums.length > 0) {
                    nums.sort((a, b) => a - b);
                    if (imputeStrategy === "median") {
                        const mid = Math.floor(nums.length / 2);
                        colImputeValues[h] = nums.length % 2 !== 0 ? nums[mid] : (nums[mid - 1] + nums[mid]) / 2;
                    } else {
                        const sum = nums.reduce((a, b) => a + b, 0);
                        colImputeValues[h] = sum / nums.length;
                    }
                }
            } else {
                // Categorical Mode
                const freq = {};
                workingData.forEach(r => {
                    const v = r[h];
                    if (v !== null && v !== undefined && v !== "") {
                        freq[v] = (freq[v] || 0) + 1;
                    }
                });
                const sorted = Object.entries(freq).sort((a, b) => b[1] - a[1]);
                if (sorted.length > 0) {
                    colImputeValues[h] = sorted[0][0];
                }
            }
        });

        // Impute missing values
        workingData.forEach(r => {
            headers.forEach(h => {
                const v = r[h];
                if (v === null || v === undefined || v === "" || (typeof v === "number" && isNaN(v))) {
                    if (colImputeValues[h] !== undefined) {
                        r[h] = colImputeValues[h];
                        missingValuesImputed++;
                    }
                }
            });
        });
    }

    // 4. Outlier Handling (1.5x IQR)
    let outliersModified = 0;
    if (outlierStrategy !== "keep") {
        const numericCols = profiles.filter(p => p.type === "Numeric").map(p => p.column);

        numericCols.forEach(col => {
            const nums = workingData
                .map(r => Number(r[col]))
                .filter(v => !isNaN(v))
                .sort((a, b) => a - b);

            if (nums.length >= 4) {
                const q1 = quantile(nums, 0.25);
                const q3 = quantile(nums, 0.75);
                const iqr = q3 - q1;
                const lower = q1 - 1.5 * iqr;
                const upper = q3 + 1.5 * iqr;

                if (outlierStrategy === "clip") {
                    workingData.forEach(r => {
                        const v = Number(r[col]);
                        if (!isNaN(v)) {
                            if (v < lower) {
                                r[col] = lower;
                                outliersModified++;
                            } else if (v > upper) {
                                r[col] = upper;
                                outliersModified++;
                            }
                        }
                    });
                } else if (outlierStrategy === "drop") {
                    const before = workingData.length;
                    workingData = workingData.filter(r => {
                        const v = Number(r[col]);
                        return isNaN(v) || (v >= lower && v <= upper);
                    });
                    outliersModified += (before - workingData.length);
                }
            }
        });
    }

    // Compute final audit stats
    let finalMissing = 0;
    workingData.forEach(r => {
        headers.forEach(h => {
            const v = r[h];
            if (v === null || v === undefined || v === "" || (typeof v === "number" && isNaN(v))) {
                finalMissing++;
            }
        });
    });

    return {
        cleanedData: workingData,
        audit: {
            initialRows,
            finalRows: workingData.length,
            rowsChanged: initialRows - workingData.length,
            duplicatesRemoved,
            missingValuesImputed,
            missingRowsDropped,
            outliersModified,
            initialMissing,
            finalMissing
        }
    };
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

export function exportCleanedCsv(data, headers, filename = "cleaned_dataset.csv") {
    if (!window.Papa) return;
    const csv = Papa.unparse({
        fields: headers,
        data: data
    });

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
