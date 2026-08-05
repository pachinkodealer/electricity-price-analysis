"""
Build Power BI-ready datasets from the electricity price analysis.

Pulls the same public FRED series used in electricity_analysis.ipynb and writes
clean, tidy CSVs with all derived measures pre-computed — so Power BI just needs
to import and visualize (no DAX required for the hard stuff like the OLS residual).

Outputs (in this folder):
  - electricity_monthly.csv   one row per month, all series + derived columns (wide)
  - electricity_long.csv       tidy long format for slicer-driven line charts
  - key_metrics.csv            headline numbers for KPI card visuals
Run:  py build_powerbi_data.py
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path

OUT = Path(__file__).parent


def fred(series_id, col_name):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    df = pd.read_csv(url, parse_dates=["observation_date"], index_col="observation_date")
    df.columns = [col_name]
    df[col_name] = pd.to_numeric(df[col_name], errors="coerce")
    return df


# --- 1. Pull data (same series/IDs as the notebook) ---
elec = fred("APU000072610", "elec_price_usd_per_kwh")
cpi  = fred("CPIAUCSL", "cpi_index")
gas  = fred("MHHNGSP", "gas_price_usd_per_mmbtu")

elec["elec_price_usd_per_kwh"] = elec["elec_price_usd_per_kwh"].interpolate(limit=2)

# --- 2. Merge onto a common monthly index ---
m = elec.join(cpi, how="outer").join(gas, how="outer").sort_index()
m = m.loc["1978-11-01":]
m.index.name = "date"

# --- 3. Derived measures (mirror the notebook exactly) ---
base = "2020-01-01"
m["elec_index_jan2020"] = m["elec_price_usd_per_kwh"] / m.loc[base, "elec_price_usd_per_kwh"] * 100
m["gas_index_jan2020"]  = m["gas_price_usd_per_mmbtu"] / m.loc[base, "gas_price_usd_per_mmbtu"] * 100
m["gas_index_jan2020_12mo_avg"] = m["gas_index_jan2020"].rolling(12).mean()

m["elec_change_6yr_pct"] = m["elec_price_usd_per_kwh"].pct_change(72, fill_method=None) * 100
m["cpi_change_6yr_pct"]  = m["cpi_index"].pct_change(72, fill_method=None) * 100

m["elec_yoy_pct"] = m["elec_price_usd_per_kwh"].pct_change(12, fill_method=None) * 100
m["gas_yoy_pct"]  = m["gas_price_usd_per_mmbtu"].pct_change(12, fill_method=None) * 100
m["cpi_yoy_pct"]  = m["cpi_index"].pct_change(12, fill_method=None) * 100

# --- 4. Two-factor model + residual (trained pre-2023, mirrors the notebook) ---
m["gas_yoy_lag6"] = m["gas_yoy_pct"].shift(6)
cols = ["elec_yoy_pct", "gas_yoy_lag6", "cpi_yoy_pct"]
train = m.loc[:"2022-12-01", cols].dropna()
model = sm.OLS(train["elec_yoy_pct"],
               sm.add_constant(train[["gas_yoy_lag6", "cpi_yoy_pct"]])).fit()

pred_mask = m[["gas_yoy_lag6", "cpi_yoy_pct"]].notna().all(axis=1)
X_all = sm.add_constant(m.loc[pred_mask, ["gas_yoy_lag6", "cpi_yoy_pct"]], has_constant="add")
m.loc[pred_mask, "model_predicted_elec_yoy_pct"] = model.predict(X_all)
m["residual_unexplained_pct"] = m["elec_yoy_pct"] - m["model_predicted_elec_yoy_pct"]

# --- 5. Era label (mutually exclusive, good for slicing / color) ---
def era(d):
    if d < pd.Timestamp("2010-01-01"):
        return "Pre-2010"
    if d < pd.Timestamp("2020-01-01"):
        return "Shale decade (2010-2019)"
    return "Demand era (2020+)"
m["era"] = [era(d) for d in m.index]

# --- 6. Write wide monthly table ---
wide = m.reset_index()
wide["date"] = wide["date"].dt.strftime("%Y-%m-%d")
wide = wide.round(4)
wide.to_csv(OUT / "electricity_monthly.csv", index=False)

# --- 7. Tidy long format for flexible line charts ---
long_specs = [
    ("Electricity price ($/kWh)", "elec_price_usd_per_kwh", "$/kWh"),
    ("Natural gas price ($/MMBtu)", "gas_price_usd_per_mmbtu", "$/MMBtu"),
    ("Electricity (indexed, Jan 2020=100)", "elec_index_jan2020", "index"),
    ("Natural gas 12-mo avg (indexed, Jan 2020=100)", "gas_index_jan2020_12mo_avg", "index"),
    ("Electricity 6-yr change (%)", "elec_change_6yr_pct", "%"),
    ("All prices / CPI 6-yr change (%)", "cpi_change_6yr_pct", "%"),
    ("Unexplained electricity inflation (pct pts)", "residual_unexplained_pct", "pct pts"),
]
frames = []
for label, col, unit in long_specs:
    f = m[[col]].reset_index()
    f.columns = ["date", "value"]
    f["metric"] = label
    f["unit"] = unit
    frames.append(f)
long = pd.concat(frames, ignore_index=True).dropna(subset=["value"])
long["date"] = long["date"].dt.strftime("%Y-%m-%d")
long["value"] = long["value"].round(4)
long = long[["date", "metric", "unit", "value"]]
long.to_csv(OUT / "electricity_long.csv", index=False)

# --- 8. Key metrics for KPI cards ---
def pc(a, b):
    return (m.loc[a, "elec_price_usd_per_kwh"] / m.loc[b, "elec_price_usd_per_kwh"] - 1) * 100

gas_peak = m.loc["2022", "gas_price_usd_per_mmbtu"].max()
gas_recent = m.loc["2024":, "gas_price_usd_per_mmbtu"].mean()
last = m["elec_price_usd_per_kwh"].dropna().index[-1]

metrics = [
    ("Electricity price change 2014-2020", round(pc("2020-01-01", "2014-01-01"), 1), "%"),
    ("Electricity price change since 2020", round(pc(last, "2020-01-01"), 1), "%"),
    ("Gas decline from 2022 peak", round((gas_recent / gas_peak - 1) * 100, 0), "%"),
    ("Electricity change since 2022 gas peak", round(pc(last, "2022-08-01"), 0), "%"),
    ("Gas-electricity correlation (6-mo lag)",
     round(m["elec_yoy_pct"].corr(m["gas_yoy_pct"].shift(6)), 2), "r"),
    ("Unexplained inflation, 2024+ (pts/yr)",
     round(m.loc["2024":, "residual_unexplained_pct"].mean(), 1), "pct pts/yr"),
    ("Model R-squared (pre-2023)", round(model.rsquared, 3), "r2"),
]
pd.DataFrame(metrics, columns=["metric", "value", "unit"]).to_csv(
    OUT / "key_metrics.csv", index=False)

print("Wrote:")
for f in ["electricity_monthly.csv", "electricity_long.csv", "key_metrics.csv"]:
    print("  powerbi/" + f, "->", (OUT / f).stat().st_size, "bytes")
print(f"\nRows in monthly table: {len(wide)}  ({wide['date'].iloc[0]} to {wide['date'].iloc[-1]})")
