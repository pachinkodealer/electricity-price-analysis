# ElectricityPrices — Power BI project (.pbip)

A ready-to-open Power BI project that loads the exported CSVs and lays out a starter
dashboard (KPI table, the "ratchet" line chart, inflation comparison, the unexplained-gap
column chart, and an era slicer).

> **This is a best-effort, un-tested scaffold.** It was authored as text files, not saved
> from Power BI Desktop, so the report visuals may need a small repair on first open. The
> **data model is the reliable part** — if a visual errors, the tables still load and you
> can rebuild any chart in seconds by dragging fields (see `DATA_DICTIONARY.md`).

## Requirements

- **Power BI Desktop**, a 2024 or newer version.
- Enable both preview features first (**File → Options and settings → Options → Preview features**), then restart:
  - ✅ *Power BI Project (.pbip) save option*
  - ✅ *Store reports using enhanced metadata format (PBIR)*

## Open it

1. Double-click **`ElectricityPrices.pbip`** (or File → Open in Power BI Desktop).
2. If prompted about the local CSV files, allow access / **Edit Permissions → Run**.
3. If a data-source privacy prompt appears, set the folder to **Public** or **Organizational** and continue.

## The data path is baked in

The three tables load from this absolute folder (single backslashes, as Power Query requires):

```
C:\Users\idcom\USA_Job_Market\Energy\powerbi\
```

If you move the CSVs, either:
- edit the path in **Transform data → each query → File.Contents(...)**, or
- edit `build_pbip.py` (it uses its own folder automatically) and re-run `py build_pbip.py`.

## What's inside

```
ElectricityPrices.pbip                     ← open this
ElectricityPrices.SemanticModel/           ← data model (TMDL): 3 tables, typed, importing the CSVs
ElectricityPrices.Report/                  ← report: one "Overview" page with 5 starter visuals
```

Tables: `electricity_monthly` (main), `electricity_long` (tidy), `key_metrics` (KPIs).
Full column definitions are in `DATA_DICTIONARY.md`.

## If it won't open or a visual is blank

This is expected for a hand-authored PBIP. Fastest recovery:
1. Let the **data model** load (that part is robust).
2. Delete any visual that shows an error.
3. Rebuild it from the field list using the "Suggested visuals" section of `DATA_DICTIONARY.md` — each chart is 2–3 field drags.

Or, as a guaranteed-working alternative, just do **Get Data → Text/CSV** on the three CSVs in a blank report and follow the dictionary. The pre-computed columns mean no DAX is needed.
