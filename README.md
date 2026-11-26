# Okun's Law Across U.S. States

Does faster GDP growth lower unemployment by the same amount in every state? This project tests Okun's Law for Florida, Alabama, Washington, New York and South Dakota using quarterly data from 2005 to 2024.

It's a rebuild of my 2024 undergraduate econometrics paper. The original regressed the unemployment *level* on GDP growth and found almost nothing. This version uses the specification Okun's Law actually describes and shows why the first one failed.

![Okun coefficients by state](figures/fig2_okun_coefficients.png)

## Key findings

- **The 2024 null result came from the model, not the economy.** Regressing the unemployment level on GDP growth gives R² ≤ 0.07 and Durbin-Watson statistics below 0.6, a sign of misspecification. Modeling the *change* in unemployment raises R² as high as 0.66.
- **Outside the pandemic, Okun's Law is clearest in Florida.** Excluding 2020–21, one extra point of year-over-year GDP growth goes with unemployment about 0.37 points lower (R² ≈ 0.61), and it holds quarter on quarter too.
- **Alabama and Washington show it less robustly.** Year over year: about −0.47 in Alabama and −0.29 in Washington. Quarter on quarter, Alabama is borderline and Washington isn't significant.
- **New York and South Dakota show no stable relationship outside 2020–21.** Their full-sample coefficients are driven by the pandemic shock.
- **States don't share one coefficient.** A Wald test rejects equal slopes across the five states (χ²(4) = 41.1, p < 0.001).

## Methods

- **Replication** of the 2024 level model, to show the problem.
- **Augmented Dickey-Fuller tests** for unit roots.
- **Okun's difference form**, ΔU = α + β·g, estimated separately for each state:
  - quarter-on-quarter and year-over-year versions
  - with and without the 2020–21 COVID quarters
- **Newey-West (HAC) standard errors** (4 lags), so inference is valid with autocorrelated errors.
- **A pooled regression with state-specific slopes**, plus a Wald test that all five slopes are equal.

## Read the results

- **[Report (HTML)](report/okun_report.html):** the full analysis with charts, no code.
- **[Notebook](okun_analysis.ipynb):** the same analysis with code and outputs.

## Project structure

```
data/fred_data.csv            quarterly unemployment rate and real GDP, 5 states, 2005–2024 (main data)
data/original_2024_data.csv   the data behind the 2024 paper, used only to replicate it
src/okun.py                   helper functions: variables, regressions, tests
src/fetch_fred.py             downloads data/fred_data.csv from FRED
okun_analysis.ipynb           the analysis, start to finish
figures/                      charts used in the report
report/okun_report.html       the report without code
```

## Run it

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook okun_analysis.ipynb
```

To refresh the data, run `python src/fetch_fred.py`, then rerun the notebook. (On a Mac with Python from python.org, run its "Install Certificates" command once if the download fails with a certificate error.)

## Data

From FRED (Federal Reserve Bank of St. Louis): seasonally adjusted state unemployment rates (BLS, series `{ST}UR`, monthly averaged to quarters) and state real GDP (BEA, series `{ST}RQGSP`, millions of chained 2017 dollars). The 2024 paper's file is kept only for the replication; it mixed in a non-seasonally-adjusted Alabama series, and both agencies revise past data, so its numbers differ slightly.

## Limitations

- A bivariate model for five states. Explaining *why* states differ (industry mix, unionization, labor-market flexibility) would need more variables and more states.
- Year-over-year changes overlap and are persistent. The quarterly model is used as a check.
- Excluding 2020–21 is a judgment call, so results are reported both ways.
- These are associations, not causal effects.

## Author

Sebastián Pedraza, MS Applied Data Science, New College of Florida. Original paper: *State-Level Estimation of Okun's Law* (Econometrics, December 2024). 
