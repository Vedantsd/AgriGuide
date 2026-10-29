import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ALPHA = 0.05
TARGETS = ["nitrogen", "phosphorus", "potassium"]
PREDICTORS = ["ph_avg", "moisture_avg", "temp_avg", "rainfall_avg"]
NUMERIC_VARS = TARGETS + PREDICTORS
GROUP_COLS = ["location", "soil_type"]

RAW_NUMERIC = [
    "ph_min", "ph_max", "moisture_min", "moisture_max",
    "temperature_min", "temperature_max", "rainfall_min", "rainfall_max",
] + TARGETS


def build_dataframe(crops):
    df = pd.DataFrame(crops)
    for col in RAW_NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["ph_avg"] = (df["ph_min"] + df["ph_max"]) / 2
    df["moisture_avg"] = (df["moisture_min"] + df["moisture_max"]) / 2
    df["temp_avg"] = (df["temperature_min"] + df["temperature_max"]) / 2
    df["rainfall_avg"] = (df["rainfall_min"] + df["rainfall_max"]) / 2
    return df


def num(x):
    x = float(x)
    return x if np.isfinite(x) else None


def check_choice(value, allowed, label):
    if value not in allowed:
        raise ValueError(f"Invalid {label}. Choose one of: {', '.join(allowed)}.")


def verdict(p):
    return "significant" if p is not None and p < ALPHA else "not significant"


def run_regression(df, target):
    check_choice(target, TARGETS, "target")
    data = df[PREDICTORS + [target]].dropna()
    if len(data) <= len(PREDICTORS) + 1:
        raise ValueError("Not enough rows to fit the regression.")

    model = sm.OLS(data[target], sm.add_constant(data[PREDICTORS])).fit()
    ci = model.conf_int()
    coefficients = [
        {
            "term": term,
            "coef": num(model.params[term]),
            "std_err": num(model.bse[term]),
            "t_stat": num(model.tvalues[term]),
            "p_value": num(model.pvalues[term]),
            "ci_low": num(ci.loc[term, 0]),
            "ci_high": num(ci.loc[term, 1]),
        }
        for term in model.params.index
    ]

    f_p = num(model.f_pvalue)
    significant = [
        c["term"] for c in coefficients
        if c["term"] != "const" and c["p_value"] is not None and c["p_value"] < ALPHA
    ]
    text = (
        f"Overall F-test: F({int(model.df_model)}, {int(model.df_resid)}) = {model.fvalue:.2f}, "
        f"p = {f_p:.4f} ({verdict(f_p)} at \u03b1 = {ALPHA}). The predictors explain "
        f"{model.rsquared * 100:.1f}% of the variation in {target} "
        f"(adjusted R\u00b2 = {model.rsquared_adj:.3f}). "
    )
    text += (
        "Predictors with significant t-tests: " + ", ".join(significant) + "."
        if significant
        else "No individual predictor has a significant t-test."
    )
    return {
        "target": target,
        "n": int(model.nobs),
        "r2": num(model.rsquared),
        "adj_r2": num(model.rsquared_adj),
        "f_stat": num(model.fvalue),
        "f_p_value": f_p,
        "df_model": int(model.df_model),
        "df_resid": int(model.df_resid),
        "coefficients": coefficients,
        "interpretation": text,
    }


def group_values(df, variable, group_col, group):
    return df.loc[df[group_col] == group, variable].dropna().astype(float)


def run_t_test(df, variable, group_col, group_a, group_b):
    check_choice(variable, NUMERIC_VARS, "variable")
    check_choice(group_col, GROUP_COLS, "group column")
    if group_a == group_b:
        raise ValueError("Pick two different groups to compare.")

    a = group_values(df, variable, group_col, group_a)
    b = group_values(df, variable, group_col, group_b)
    if len(a) < 2 or len(b) < 2:
        raise ValueError("Each group needs at least 2 observations.")

    var_a, var_b = a.var(ddof=1), b.var(ddof=1)
    se_a, se_b = var_a / len(a), var_b / len(b)
    se = np.sqrt(se_a + se_b)
    diff = a.mean() - b.mean()

    t_stat, t_p = stats.ttest_ind(a, b, equal_var=False)
    with np.errstate(divide="ignore", invalid="ignore"):
        welch_df = (se_a + se_b) ** 2 / (se_a ** 2 / (len(a) - 1) + se_b ** 2 / (len(b) - 1))
    t_crit = stats.t.ppf(1 - ALPHA / 2, welch_df) if np.isfinite(welch_df) else np.nan

    with np.errstate(divide="ignore", invalid="ignore"):
        f_stat = var_a / var_b if var_b > 0 else np.nan
    dfn, dfd = len(a) - 1, len(b) - 1
    f_p = (
        2 * min(stats.f.cdf(f_stat, dfn, dfd), stats.f.sf(f_stat, dfn, dfd))
        if np.isfinite(f_stat) else np.nan
    )

    t_p, f_p = num(t_p), num(f_p)
    text = (
        f"Welch t-test: t = {t_stat:.3f}, p = {t_p:.4f} ({verdict(t_p)} at \u03b1 = {ALPHA}). "
        f"The mean {variable} of {group_a} ({a.mean():.2f}) vs {group_b} ({b.mean():.2f}) "
        f"differs by {diff:.2f}. "
        if t_p is not None else "The t-test could not be computed (both groups are constant). "
    )
    if f_p is not None:
        text += (
            f"Variance F-test: F({dfn}, {dfd}) = {f_stat:.3f}, p = {f_p:.4f} "
            f"({verdict(f_p)}), so the spread in the two groups is "
            f"{'different' if f_p < ALPHA else 'similar'}."
        )

    return {
        "variable": variable,
        "group_col": group_col,
        "groups": [
            {"name": group_a, "n": len(a), "mean": num(a.mean()), "std": num(np.sqrt(var_a))},
            {"name": group_b, "n": len(b), "mean": num(b.mean()), "std": num(np.sqrt(var_b))},
        ],
        "t_test": {
            "method": "Welch's two-sample t-test",
            "t_stat": num(t_stat),
            "df": num(welch_df),
            "p_value": t_p,
            "mean_diff": num(diff),
            "ci_low": num(diff - t_crit * se),
            "ci_high": num(diff + t_crit * se),
        },
        "variance_f_test": {
            "f_stat": num(f_stat), "df_num": dfn, "df_den": dfd, "p_value": f_p,
        },
        "interpretation": text,
    }


def run_anova(df, variable, group_col):
    check_choice(variable, NUMERIC_VARS, "variable")
    check_choice(group_col, GROUP_COLS, "group column")

    all_groups = {
        name: g[variable].dropna().astype(float).values
        for name, g in df.groupby(group_col)
    }
    groups = {k: v for k, v in all_groups.items() if len(v) >= 2}
    excluded = [k for k, v in all_groups.items() if len(v) < 2]
    if len(groups) < 2:
        raise ValueError("Need at least two groups with 2 or more observations.")

    f_stat, p_value = stats.f_oneway(*groups.values())
    everything = np.concatenate(list(groups.values()))
    grand_mean = everything.mean()
    ss_between = sum(len(v) * (v.mean() - grand_mean) ** 2 for v in groups.values())
    ss_within = sum(((v - v.mean()) ** 2).sum() for v in groups.values())
    df_between, df_within = len(groups) - 1, len(everything) - len(groups)
    eta_sq = ss_between / (ss_between + ss_within) if (ss_between + ss_within) else np.nan

    p_value = num(p_value)
    text = (
        f"One-way ANOVA: F({df_between}, {df_within}) = {f_stat:.3f}, p = {p_value:.4f} "
        f"({verdict(p_value)} at \u03b1 = {ALPHA}). "
        f"Group means of {variable} across {group_col} "
        f"{'differ' if p_value < ALPHA else 'do not differ'} significantly; "
        f"{eta_sq * 100:.1f}% of the variance is between groups."
        if p_value is not None else "ANOVA could not be computed (no variation in the data)."
    )
    if excluded:
        text += f" Excluded for having fewer than 2 observations: {', '.join(excluded)}."

    return {
        "variable": variable,
        "group_col": group_col,
        "f_stat": num(f_stat),
        "df_between": df_between,
        "df_within": df_within,
        "p_value": p_value,
        "eta_squared": num(eta_sq),
        "groups": [
            {"name": k, "n": len(v), "mean": num(v.mean()), "std": num(v.std(ddof=1))}
            for k, v in groups.items()
        ],
        "excluded": excluded,
        "interpretation": text,
    }