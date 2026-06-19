# Why Your Electric Bill Stopped Following Fuel Prices

A data investigation into US electricity prices (1978–2026): natural gas, inflation, and the datacenter demand era.

**Key findings:**
- Electricity prices ratchet — they follow natural gas up (~6-month lag, r=0.53) but didn't retrace when gas gave back its entire 2022 spike
- After controlling for fuel costs and general inflation, US electricity inflation has run ~2.7 points/year hot since 2023, coinciding with the first sustained power demand growth in two decades

**Stack:** Python, pandas, matplotlib, statsmodels. Data pulled live from FRED public endpoints (BLS, EIA) — fully reproducible, no API keys.

📓 [`electricity_analysis.ipynb`](electricity_analysis.ipynb) — full notebook, reproducible end-to-end

🔗 [github.com/pachinkodealer/electricity-price-analysis](https://github.com/pachinkodealer/electricity-price-analysis)

*Ian Lee, June 2026*
