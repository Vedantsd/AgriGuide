import numpy as np
import pandas as pd

from stats_analysis import GROUP_COLS, NUMERIC_VARS, check_choice

INF = np.inf

AGRONOMIC_BINS = {
    "ph_avg": ([0, 5.5, 6.5, 7.5, INF], ["Acidic", "Slightly acidic", "Neutral", "Alkaline"]),
    "moisture_avg": ([0, 40, 60, 80, INF], ["Low", "Medium", "High", "Very high"]),
    "temp_avg": ([-INF, 15, 22, 28, INF], ["Cool", "Moderate", "Warm", "Hot"]),
    "rainfall_avg": ([0, 50, 100, 200, INF], ["Low", "Moderate", "High", "Very high"]),
    "nitrogen": ([0, 50, 100, 150, INF], ["Low need", "Medium need", "High need", "Very high need"]),
    "phosphorus": ([0, 30, 60, INF], ["Low need", "Medium need", "High need"]),
    "potassium": ([0, 50, 100, INF], ["Low need", "Medium need", "High need"]),
}

CONDITION_FIELDS = {
    "ph": ("ph_avg", "Soil pH"),
    "moisture": ("moisture_avg", "Moisture"),
    "temperature": ("temp_avg", "Temperature"),
    "rainfall": ("rainfall_avg", "Rainfall"),
}

METHODS = ["custom", "equal_width", "quantile"]
METHOD_TEXT = {
    "custom": "agronomic categories",
    "equal_width": "equal-width bins",
    "quantile": "quantile bins (roughly equal counts)",
}


def range_text(low, high):
    if np.isneginf(low):
        return f"below {high:g}"
    if np.isposinf(high):
        return f"{low:g} and above"
    return f"{low:g} to below {high:g}"


def bin_series(series, variable, method="custom", n_bins=4):
    if method == "custom":
        edges, labels = AGRONOMIC_BINS[variable]
        binned = pd.cut(series, bins=edges, labels=labels, right=False)
        ranges = [range_text(edges[i], edges[i + 1]) for i in range(len(labels))]
        return binned, list(labels), ranges

    if method == "equal_width":
        raw = pd.cut(series, bins=n_bins)
    else:
        raw = pd.qcut(series, q=n_bins, duplicates="drop")

    intervals = list(raw.cat.categories)
    lows = [series.min()] + [iv.left for iv in intervals[1:]]
    ranges = [f"{low:.1f} to {iv.right:.1f}" for low, iv in zip(lows, intervals)]
    labels = [f"Bin {i}" for i in range(1, len(intervals) + 1)]
    return raw.cat.rename_categories(labels), labels, ranges


def classify_value(variable, value):
    edges, labels = AGRONOMIC_BINS[variable]
    category = pd.cut([value], bins=edges, labels=labels, right=False)[0]
    return None if pd.isna(category) else str(category)


def describe_conditions(user):
    profile = []
    for key, (variable, label) in CONDITION_FIELDS.items():
        value = user.get(key)
        if value is None:
            continue
        category = classify_value(variable, value)
        if category:
            profile.append({"label": label, "value": value, "category": category})
    return profile


def run_binning(df, variable, method, n_bins, group_col):
    check_choice(variable, NUMERIC_VARS, "variable")
    check_choice(method, METHODS, "method")
    group_col = group_col or None
    if group_col is not None:
        check_choice(group_col, GROUP_COLS, "group column")
    try:
        n_bins = int(n_bins)
    except (TypeError, ValueError):
        raise ValueError("Number of bins must be a whole number.")
    if not 2 <= n_bins <= 10:
        raise ValueError("Number of bins must be between 2 and 10.")

    columns = [variable] + ([group_col] if group_col else [])
    data = df[columns].dropna()
    if len(data) < n_bins:
        raise ValueError("Not enough rows to create that many bins.")

    binned, labels, ranges = bin_series(data[variable].astype(float), variable, method, n_bins)
    counts = binned.value_counts(sort=False)
    total = int(counts.sum())
    rows = [
        {
            "bin": label,
            "range": rng,
            "count": int(counts[label]),
            "percent": round(100 * counts[label] / total, 1),
        }
        for label, rng in zip(labels, ranges)
    ]

    crosstab = None
    if group_col:
        table = pd.crosstab(binned, data[group_col]).reindex(labels, fill_value=0)
        crosstab = {
            "group_col": group_col,
            "columns": [str(c) for c in table.columns],
            "rows": [
                {"bin": str(label), "counts": [int(v) for v in table.loc[label]]}
                for label in labels
            ],
        }

    top = max(rows, key=lambda r: r["count"])
    text = (
        f"{total} crops were grouped into {len(rows)} bins using {METHOD_TEXT[method]}. "
        f"The most common bin is {top['bin']} ({top['range']}) with {top['count']} crops "
        f"({top['percent']}%)."
    )
    if method == "quantile" and len(rows) < n_bins:
        text += f" Repeated values merged some edges, so only {len(rows)} bins were created."

    return {
        "variable": variable,
        "method": method,
        "total": total,
        "rows": rows,
        "crosstab": crosstab,
        "interpretation": text,
    }