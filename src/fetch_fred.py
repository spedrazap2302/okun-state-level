"""
Download fresh data from FRED (no API key needed) and save it in the same
format as data/original_2024_data.csv.

Run from the project folder:
    python src/fetch_fred.py

Series used (all from FRED, St. Louis Fed):
  {ST}UR     unemployment rate, seasonally adjusted, monthly (BLS)
  {ST}RQGSP  real GDP, all industries, quarterly (BEA)
Monthly unemployment is averaged to quarters to match GDP.
"""

import io
import urllib.request

import pandas as pd

STATES = ["AL", "FL", "NY", "SD", "WA"]
START, END = "2005-01-01", "2024-12-31"
URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd={start}&coed={end}"


def get_series(series):
    """Download one FRED series as a DataFrame with columns date, value."""
    url = URL.format(series=series, start=START, end=END)
    with urllib.request.urlopen(url, timeout=30) as response:
        text = response.read().decode("utf-8")
    df = pd.read_csv(io.StringIO(text))
    df.columns = ["date", "value"]  # FRED names them observation_date, <series>
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")  # "." means missing
    return df.dropna()


def main():
    frames = []
    for st in STATES:
        unemp = get_series(f"{st}UR")
        unemp = (
            unemp.set_index("date")["value"]
            .resample("QS")  # quarter start, matching GDP dates
            .mean()
            .rename("unemp")
        )
        gdp = get_series(f"{st}RQGSP").set_index("date")["value"].rename("real_gdp")
        both = pd.concat([unemp, gdp], axis=1, join="inner").reset_index()
        both.insert(0, "state", st)
        frames.append(both)
        print(f"{st}: {len(both)} quarters")

    out = pd.concat(frames)
    out.to_csv("data/fred_data.csv", index=False)
    print("Saved data/fred_data.csv")


if __name__ == "__main__":
    main()
