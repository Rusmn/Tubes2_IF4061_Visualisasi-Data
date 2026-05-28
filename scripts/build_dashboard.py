from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"
GEO38 = ROOT / "data" / "geo" / "indonesia-38-provinces.geojson"
OUT = ROOT / "dashboard" / "data.js"


def clean_name(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    text = text.strip().upper().replace(".", "").replace("-", " ")
    text = " ".join(text.split())
    swaps = {
        "D K I JAKARTA": "DKI JAKARTA",
        "D I YOGYAKARTA": "DI YOGYAKARTA",
        "DAERAH ISTIMEWA YOGYAKARTA": "DI YOGYAKARTA",
        "BANGKA BELITUNG": "KEP BANGKA BELITUNG",
        "KEPULAUAN BANGKA BELITUNG": "KEP BANGKA BELITUNG",
        "KEP RIAU": "KEP RIAU",
        "KEPULAUAN RIAU": "KEP RIAU",
        "NUSATENGGARA BARAT": "NUSA TENGGARA BARAT",
        "NUSATENGGARA TIMUR": "NUSA TENGGARA TIMUR",
    }
    return swaps.get(text, text)


def display_name(value: object) -> str:
    text = clean_name(value).title()
    fixes = {
        "Dki Jakarta": "DKI Jakarta",
        "Di Yogyakarta": "DI Yogyakarta",
        "Kep Bangka Belitung": "Kep. Bangka Belitung",
        "Kep Riau": "Kep. Riau",
    }
    return fixes.get(text, text)


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(CLEAN / name)


def latest_total(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "year" in df.columns:
        if 2024 in set(df["year"].dropna().astype(int)):
            df = df[df["year"] == 2024]
        else:
            latest = int(df["year"].dropna().max())
            df = df[df["year"] == latest].copy()
            df["year"] = 2024
    if "area" in df.columns:
        total = df[df["area"].astype(str).str.lower().eq("total")]
        if not total.empty:
            df = total
    return df


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["province_key"] = df["province"].map(clean_name)
    df["province"] = df["province"].map(display_name)
    return df


def first_by_province(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    keep = ["province", "province_key"] + numeric
    keep = [col for col in keep if col in df.columns]
    return df[keep].groupby(["province", "province_key"], as_index=False).mean(numeric_only=True)


def minmax(series: pd.Series, invert: bool = False) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    low = values.min()
    high = values.max()
    if pd.isna(low) or pd.isna(high) or high == low:
        out = pd.Series(0.0, index=series.index)
    else:
        out = (values - low) / (high - low)
    return (1 - out if invert else out).fillna(0)


def risk_label(score: float) -> str:
    if score >= 72:
        return "Prioritas tinggi"
    if score >= 48:
        return "Perlu pemantauan"
    return "Relatif terkendali"


def build_metrics() -> pd.DataFrame:
    base = normalize_df(read_csv("rokok_vs_gizi.csv"))
    coords = normalize_df(read_csv("provinces.csv").rename(columns={"Name": "province"}))
    pdrb = pd.read_csv(ROOT / "data" / "raw" / "pdrb_capita.csv")
    pdrb = pdrb.rename(columns={pdrb.columns[0]: "province", pdrb.columns[1]: "pdrb_capita_thousand"})
    pdrb = normalize_df(pdrb)
    school = pd.read_csv(ROOT / "data" / "raw" / "school_year.csv")
    school = school.rename(columns={"Cakupan": "province", "Total": "school_years"})
    school["school_years"] = (
        school["school_years"].astype(str).str.replace(",", ".", regex=False).astype(float)
    )
    school = normalize_df(school)
    frames = [
        first_by_province(coords.rename(columns={"Latitude": "latitude", "Longitude": "longitude"})),
        first_by_province(pdrb),
        first_by_province(school),
        first_by_province(normalize_df(latest_total(read_csv("digital_plate_metrics.csv")))),
        first_by_province(normalize_df(latest_total(read_csv("population_province.csv")))),
        first_by_province(normalize_df(latest_total(read_csv("poverty_rate_all.csv")))),
        first_by_province(normalize_df(latest_total(read_csv("gini_ratio_all.csv")))),
        first_by_province(normalize_df(read_csv("ski_2023_curated.csv"))),
    ]
    merged = base.copy()
    for frame in frames:
        duplicates = [col for col in frame.columns if col in merged.columns and col not in {"province", "province_key"}]
        merged = merged.merge(frame.drop(columns=duplicates), on=["province", "province_key"], how="left")

    merged["population"] = merged.get("population_thousands", np.nan) * 1000
    merged["rokok_minus_sayur"] = merged["rokok"] - merged["sayur"]
    merged["source_status"] = "observed"

    inheritance = {
        "PAPUA SELATAN": "PAPUA",
        "PAPUA TENGAH": "PAPUA",
        "PAPUA PEGUNUNGAN": "PAPUA",
        "PAPUA BARAT DAYA": "PAPUA BARAT",
    }
    additions = []
    for child, parent in inheritance.items():
        parent_rows = merged[merged["province_key"].eq(parent)]
        if parent_rows.empty:
            continue
        row = parent_rows.iloc[0].copy()
        row["province_key"] = child
        row["province"] = display_name(child)
        row["source_status"] = "estimasi_pemekaran"
        additions.append(row)
    if additions:
        merged = pd.concat([merged, pd.DataFrame(additions)], ignore_index=True)

    merged["norm_rokok"] = minmax(merged["rokok_pct_of_gizi"])
    merged["norm_poverty"] = minmax(merged["poverty_rate"])
    merged["norm_stunting"] = minmax(merged.get("stunting_0_59_total_pct", pd.Series(0, index=merged.index)))
    merged["norm_low_protein"] = minmax(merged["protein_per_capita"], invert=True)
    merged["norm_population"] = minmax(merged["population"])
    merged["policy_priority_index"] = (
        merged["norm_rokok"] * 0.25
        + merged["norm_poverty"] * 0.25
        + merged["norm_stunting"] * 0.20
        + merged["norm_low_protein"] * 0.20
        + merged["norm_population"] * 0.10
    ) * 100
    merged["risk_label"] = merged["policy_priority_index"].map(risk_label)
    merged["rank_rokok_gizi"] = merged["rokok_pct_of_gizi"].rank(ascending=False, method="min").astype(int)
    return merged.sort_values("province_key").reset_index(drop=True)


def build_price_trends() -> pd.DataFrame:
    harga = read_csv("indeks_harga_tahunan.csv")
    patterns = {
        "Rokok dan tembakau": "rokok|tembakau",
        "Pangan umum": "makanan|minuman|pangan",
        "Protein hewani": "ikan|daging|telur|susu",
        "Sayur dan buah": "sayur|buah",
    }
    rows = []
    for label, pattern in patterns.items():
        part = harga[harga["sub_group"].astype(str).str.contains(pattern, case=False, na=False)]
        if part.empty:
            continue
        agg = part.groupby("year", as_index=False)["value"].mean()
        agg["indicator"] = label
        rows.append(agg)
    if not rows:
        return pd.DataFrame(columns=["year", "indicator", "value"])
    return pd.concat(rows, ignore_index=True).sort_values(["indicator", "year"])


def build_geojson() -> dict:
    geo = json.load(open(GEO38, encoding="utf-8"))
    for feature in geo.get("features", []):
        props = feature.setdefault("properties", {})
        raw_name = props.get("PROVINSI") or props.get("province") or props.get("name")
        props["province_key"] = clean_name(raw_name)
        props["province_name"] = display_name(raw_name)
    return geo


def main() -> None:
    metrics = build_metrics()
    geojson = build_geojson()
    payload = {
        "generated_at": "2026-05-18",
        "metrics": metrics.replace({np.nan: None}).to_dict(orient="records"),
        "geojson": geojson,
        "priceTrends": build_price_trends().replace({np.nan: None}).to_dict(orient="records"),
        "meta": {
            "province_count": int(metrics["province_key"].nunique()),
            "observed_count": int(metrics["source_status"].eq("observed").sum()),
            "estimated_count": int(metrics["source_status"].eq("estimasi_pemekaran").sum()),
            "geojson_source": "https://gist.github.com/denyherianto/aae0dd09837a4cfd7c834e28a5ed4b8c",
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "window.DASHBOARD_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT} with {payload['meta']['province_count']} provinces")


if __name__ == "__main__":
    main()
