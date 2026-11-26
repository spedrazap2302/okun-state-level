"""
Helper functions for the state-level Okun's Law analysis.

The notebook (okun_analysis.ipynb) calls these functions so the
analysis reads as a story, while the mechanics live here.
"""

import warnings

import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tsa.stattools import adfuller

STATE_NAMES = {
    "AL": "Alabama",
    "FL": "Florida",
    "NY": "New York",
    "SD": "South Dakota",
    "WA": "Washington",
}

# Quarters dominated by the COVID-19 shock, excluded in robustness checks.
COVID_START = "2020-01-01"
COVID_END = "2021-12-31"

# Newey-West (HAC) standard errors: lags allowed for autocorrelation.
# 4 lags = one year of quarterly data.
HAC_LAGS = 4


def load_data(path):
    """Read the tidy quarterly data: one row per state per quarter."""
    df = pd.read_csv(path, parse_dates=["date"])
    return df.sort_values(["state", "date"]).reset_index(drop=True)


def add_changes(df):
    """
    Add the variables Okun's Law needs, computed within each state:
      g      quarter-on-quarter real GDP growth, in %
      du     quarter-on-quarter change in the unemployment rate, in points
      g4     year-over-year real GDP growth (vs. same quarter last year), in %
      du4    year-over-year change in the unemployment rate, in points
      covid  True for quarters in the COVID window
    """
    df = df.copy()
    by_state = df.groupby("state")
    df["g"] = by_state["real_gdp"].transform(lambda s: 100 * s.pct_change())
    df["du"] = by_state["unemp"].diff()
    df["g4"] = by_state["real_gdp"].transform(lambda s: 100 * s.pct_change(4))
    df["du4"] = by_state["unemp"].diff(4)
    df["covid"] = (df["date"] >= COVID_START) & (df["date"] <= COVID_END)
    return df


def fit_ols(formula, data, hac=True):
    """Fit OLS. With hac=True, use Newey-West standard errors."""
    model = smf.ols(formula, data)
    if hac:
        return model.fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
    return model.fit()


def summarize(fit, x, state, model_name):
    """Pull the numbers we report from one fitted regression."""
    low, high = fit.conf_int().loc[x]
    return {
        "model": model_name,
        "state": state,
        "okun_coef": fit.params[x],
        "ci_low": low,
        "ci_high": high,
        "p_value": fit.pvalues[x],
        "r2": fit.rsquared,
        "durbin_watson": durbin_watson(fit.resid),
        "n": int(fit.nobs),
    }


def run_state_models(df, y, x, model_name, hac=True, exclude_covid=False):
    """Run the same regression y ~ x separately for every state."""
    rows = []
    for state, d in df.groupby("state"):
        d = d.dropna(subset=[y, x])
        if exclude_covid:
            d = d[~d["covid"]]
        fit = fit_ols(f"{y} ~ {x}", d, hac=hac)
        rows.append(summarize(fit, x, state, model_name))
    return pd.DataFrame(rows)


def adf_table(df, columns):
    """Augmented Dickey-Fuller p-values. Small p-value = stationary."""
    rows = []
    for state, d in df.groupby("state"):
        row = {"state": state}
        for col in columns:
            with warnings.catch_warnings():  # hides a statsmodels notice about a future API change
                warnings.simplefilter("ignore", FutureWarning)
                row[col] = adfuller(d[col].dropna(), autolag="AIC")[1]
        rows.append(row)
    return pd.DataFrame(rows)


def test_equal_slopes(df, y, x, exclude_covid=True):
    """
    Pooled regression with a separate slope for each state, then a Wald
    test of the hypothesis that all five Okun coefficients are equal.
    """
    d = df.dropna(subset=[y, x])
    if exclude_covid:
        d = d[~d["covid"]]
    fit = fit_ols(f"{y} ~ C(state) * {x}", d)
    terms = [t for t in fit.params.index if t.startswith("C(state)[T.") and t.endswith(f":{x}")]
    test = fit.wald_test(", ".join(f"{t} = 0" for t in terms), scalar=True)
    return float(test.statistic), float(test.pvalue), len(terms)
