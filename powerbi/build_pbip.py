"""
Generate a Power BI Project (.pbip / PBIR + TMDL) that loads the exported CSVs
and lays out a starter dashboard. Text-based, source-controllable format.

Requires (to OPEN the result): Power BI Desktop (2024+), with
  File > Options > Preview features > "Power BI Project (.pbip) save option" and
  "Store reports using enhanced metadata format (PBIR)"  both ENABLED.

Run:  py build_pbip.py     (re-runnable; overwrites the project tree)
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
CSV_FOLDER = str(ROOT)  # absolute path baked into the M queries (single backslashes; M treats "\" literally)
PROJ = "ElectricityPrices"
REPORT = ROOT / f"{PROJ}.Report"
MODEL = ROOT / f"{PROJ}.SemanticModel"


def w(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def wj(path: Path, obj: dict):
    w(path, json.dumps(obj, indent=2))


# ---------------------------------------------------------------- .pbip pointer
wj(ROOT / f"{PROJ}.pbip", {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
    "version": "1.0",
    "artifacts": [{"report": {"path": f"{PROJ}.Report"}}],
    "settings": {"enableAutoRecovery": True},
})

# ---------------------------------------------------------- semantic model side
wj(MODEL / "definition.pbism", {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
    "version": "4.2",
    "settings": {},
})

w(MODEL / "definition" / "database.tmdl", "database\n\tcompatibilityLevel: 1567\n")

w(MODEL / "definition" / "model.tmdl",
"""model Model
\tculture: en-US
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: en-US

\tannotation PBI_QueryOrder = ["electricity_monthly","electricity_long","key_metrics"]

ref table electricity_monthly
ref table electricity_long
ref table key_metrics
""")

# --- table definitions: (name, csv, [(col, tmdl_dataType, m_type)]) ---
DATE, NUM, TXT = "dateTime", "double", "string"
tables = {
    "electricity_monthly": ("electricity_monthly.csv", [
        ("date", DATE, "type date"),
        ("elec_price_usd_per_kwh", NUM, "type number"),
        ("cpi_index", NUM, "type number"),
        ("gas_price_usd_per_mmbtu", NUM, "type number"),
        ("elec_index_jan2020", NUM, "type number"),
        ("gas_index_jan2020", NUM, "type number"),
        ("gas_index_jan2020_12mo_avg", NUM, "type number"),
        ("elec_change_6yr_pct", NUM, "type number"),
        ("cpi_change_6yr_pct", NUM, "type number"),
        ("elec_yoy_pct", NUM, "type number"),
        ("gas_yoy_pct", NUM, "type number"),
        ("cpi_yoy_pct", NUM, "type number"),
        ("gas_yoy_lag6", NUM, "type number"),
        ("model_predicted_elec_yoy_pct", NUM, "type number"),
        ("residual_unexplained_pct", NUM, "type number"),
        ("era", TXT, "type text"),
    ]),
    "electricity_long": ("electricity_long.csv", [
        ("date", DATE, "type date"),
        ("metric", TXT, "type text"),
        ("unit", TXT, "type text"),
        ("value", NUM, "type number"),
    ]),
    "key_metrics": ("key_metrics.csv", [
        ("metric", TXT, "type text"),
        ("value", NUM, "type number"),
        ("unit", TXT, "type text"),
    ]),
}


def tmdl_table(name, csv, cols):
    lines = [f"table {name}", ""]
    for col, dt, _ in cols:
        lines.append(f"\tcolumn {col}")
        lines.append(f"\t\tdataType: {dt}")
        if dt == DATE:
            lines.append("\t\tformatString: Long Date")
        lines.append(f"\t\tsourceColumn: {col}")
        lines.append("")
    # M partition
    transforms = ", ".join(f'{{"{c}", {mt}}}' for c, _, mt in cols)
    m = (
        f'let\n'
        f'    Source = Csv.Document(File.Contents("{CSV_FOLDER}\\{csv}"), '
        f'[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n'
        f'    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n'
        f'    Typed = Table.TransformColumnTypes(Promoted, {{{transforms}}})\n'
        f'in\n'
        f'    Typed'
    )
    m_indented = "\n".join("\t\t\t\t" + ln for ln in m.split("\n"))
    lines.append(f"\tpartition {name} = m")
    lines.append("\t\tmode: import")
    lines.append("\t\tsource =")
    lines.append(m_indented)
    lines.append("")
    return "\n".join(lines)


for name, (csv, cols) in tables.items():
    w(MODEL / "definition" / "tables" / f"{name}.tmdl", tmdl_table(name, csv, cols))

# ----------------------------------------------------------------- report side
wj(REPORT / "definition.pbir", {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/1.0.0/schema.json",
    "version": "1.0",
    "datasetReference": {"byPath": {"path": f"../{PROJ}.SemanticModel"}},
})

# PBIR requires a version.json declaring the report-definition schema version
wj(REPORT / "definition" / "version.json", {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
    "version": "2.0.0",
})

wj(REPORT / "definition" / "report.json", {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/2.0.0/schema.json",
    "settings": {"useStylableVisualContainerHeader": True},
})

wj(REPORT / "definition" / "pages" / "pages.json", {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
    "pageOrder": ["overview"],
    "activePageName": "overview",
})

wj(REPORT / "definition" / "pages" / "overview" / "page.json", {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json",
    "name": "overview",
    "displayName": "Electricity Prices — Overview",
    "displayOption": "FitToPage",
    "height": 720,
    "width": 1280,
})

VC = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.4.0/schema.json"


def col_field(ent, prop):
    return {"field": {"Column": {"Expression": {"SourceRef": {"Entity": ent}}, "Property": prop}},
            "queryRef": f"{ent}.{prop}", "nativeQueryRef": prop}


def sum_field(ent, prop):
    return {"field": {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Entity": ent}}, "Property": prop}}, "Function": 0}},
            "queryRef": f"Sum({ent}.{prop})", "nativeQueryRef": prop}


def visual(name, x, y, wd, ht, vtype, roles, title):
    # title kept as an argument for readability but not emitted (auto-title avoids
    # the formatting-object schema, the most fragile part of hand-authored PBIR)
    return {
        "$schema": VC,
        "name": name,
        "position": {"x": x, "y": y, "z": 0, "width": wd, "height": ht, "tabOrder": 0},
        "visual": {
            "visualType": vtype,
            "query": {"queryState": {role: {"projections": proj} for role, proj in roles.items()}},
            "drillFilterOtherVisuals": True,
        },
    }


E = "electricity_monthly"
visuals = [
    visual("v_metrics", 16, 16, 400, 320, "tableEx",
           {"Values": [col_field("key_metrics", "metric"), sum_field("key_metrics", "value")]},
           "Key metrics"),
    visual("v_ratchet", 432, 16, 832, 320, "lineChart",
           {"Category": [col_field(E, "date")],
            "Y": [sum_field(E, "elec_index_jan2020"), sum_field(E, "gas_index_jan2020_12mo_avg")]},
           "Gas fell back. Electricity didn't. (Jan 2020 = 100)"),
    visual("v_inflation", 16, 352, 624, 352, "lineChart",
           {"Category": [col_field(E, "date")],
            "Y": [sum_field(E, "elec_change_6yr_pct"), sum_field(E, "cpi_change_6yr_pct")]},
           "Electricity vs. overall inflation (6-yr change)"),
    visual("v_residual", 656, 352, 448, 352, "columnChart",
           {"Category": [col_field(E, "date")], "Y": [sum_field(E, "residual_unexplained_pct")]},
           "Inflation not explained by gas or CPI"),
    visual("v_era", 1120, 352, 144, 352, "slicer",
           {"Values": [col_field(E, "era")]},
           "Era"),
]
for v in visuals:
    wj(REPORT / "definition" / "pages" / "overview" / "visuals" / v["name"] / "visual.json", v)

# ------------------------------------------------------------- validate + report
import glob
bad = 0
for jf in glob.glob(str(ROOT / f"{PROJ}.*") + "/**/*.json", recursive=True) + [str(ROOT / f"{PROJ}.pbip")]:
    try:
        json.load(open(jf, encoding="utf-8"))
    except Exception as e:
        bad += 1
        print("INVALID JSON:", jf, e)
print(f"Generated PBIP project '{PROJ}'  (JSON files valid: {'all' if bad == 0 else f'{bad} BAD'})")
print("Open:", ROOT / f"{PROJ}.pbip")
