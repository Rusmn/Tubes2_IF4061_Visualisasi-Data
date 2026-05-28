from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src.util import clean_name, find_col, num_col, pretty_name

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CLEAN = DATA / "clean"
RAW = DATA / "raw"
GEO = DATA / "geo"


@dataclass
class DashboardData:
    metrics: pd.DataFrame
    expenditure_long: pd.DataFrame
    price_trends: pd.DataFrame
    trends: pd.DataFrame
    geojson: dict | None
    default_province: str
    provinces: list[str]


def _read_csv(filename: str, folder: Path | None = None, required: bool = False) -> pd.DataFrame:
    folders = [folder] if folder else [CLEAN, RAW, DATA, ROOT]
    for base in folders:
        if not base:
            continue
        p = base / filename
        if p.exists():
            return pd.read_csv(p)
    if required:
        raise FileNotFoundError(f"File {filename} tidak ditemukan di {CLEAN}, {RAW}, {DATA}, atau root project")
    return pd.DataFrame()


def _normalize(df: pd.DataFrame, province_col: str | None = None) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    province_col = province_col or find_col(df, ["province", "provinsi", "name", "Provinsi", "Provinsi di Indonesia"])
    if province_col and province_col in df.columns:
        df = df.rename(columns={province_col: "province"})
        df = df[df["province"].notna()].copy()
        df["province_key"] = df["province"].map(clean_name)
        df["province"] = df["province_key"].map(pretty_name)
    return df


def _latest_total(df: pd.DataFrame, year: int = 2024) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    ycol = find_col(df, ["year", "tahun"])
    if ycol:
        df[ycol] = pd.to_numeric(df[ycol], errors="coerce")
        if (df[ycol] == year).any():
            df = df[df[ycol] == year].copy()
        elif df[ycol].notna().any():
            latest = df[ycol].dropna().max()
            df = df[df[ycol] == latest].copy()
    acol = find_col(df, ["area", "wilayah", "daerah"])
    if acol:
        total = df[df[acol].astype(str).str.lower().str.strip().eq("total")]
        if not total.empty:
            df = total.copy()
    return df


def _by_province_mean(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "province_key" not in df.columns:
        return df
    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    keep = ["province", "province_key"] + numeric
    keep = [c for c in keep if c in df.columns]
    return df[keep].groupby(["province", "province_key"], as_index=False).mean(numeric_only=True)


def _minmax(series: pd.Series, invert: bool = False) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    lo, hi = s.min(), s.max()
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        out = pd.Series(0.0, index=s.index)
    else:
        out = (s - lo) / (hi - lo)
    if invert:
        out = 1 - out
    return out.fillna(0)


def _risk_label(score: float) -> str:
    if pd.isna(score):
        return "Data terbatas"
    if score >= 72:
        return "Prioritas tinggi"
    if score >= 48:
        return "Perlu dipantau"
    return "Relatif terkendali"


def _load_rokok() -> pd.DataFrame:
    df = _normalize(_read_csv("rokok_vs_gizi.csv", CLEAN, required=False))
    if df.empty:
        df = _normalize(_read_csv("rokok_vs_gizi.csv", RAW, required=True))
    # Pastikan numeric
    for col in ["rokok", "sayur", "ikan", "telur_susu", "daging", "buah", "gizi_total", "rokok_pct_of_gizi", "rokok_vs_sayur_ratio", "poverty_rate", "protein_per_capita", "calorie_per_capita"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "gizi_total" not in df.columns:
        df["gizi_total"] = df[[c for c in ["sayur", "ikan", "telur_susu", "daging", "buah"] if c in df]].sum(axis=1)
    if "rokok_pct_of_gizi" not in df.columns:
        df["rokok_pct_of_gizi"] = df["rokok"] / df["gizi_total"] * 100
    if "rokok_vs_sayur_ratio" not in df.columns:
        df["rokok_vs_sayur_ratio"] = df["rokok"] / df["sayur"]
    return df


def _load_optional_context() -> list[pd.DataFrame]:
    frames: list[pd.DataFrame] = []
    # master_snapshot punya banyak indikator bagus jika tersedia
    snap = _normalize(_read_csv("master_snapshot.csv", RAW))
    if not snap.empty:
        ren = {
            "internet_pct_total": "internet_pct",
            "mobile_pct_total": "mobile_pct",
            "computer_pct_total": "computer_pct",
            "engel_ratio_total": "engel_ratio",
            "poverty_rate_total": "poverty_rate",
            "gini_total": "gini",
            "population_2024": "population_thousands",
            "Latitude": "latitude",
            "Longitude": "longitude",
            "pdrb_capita_thousand": "pdrb_capita_thousand",
        }
        snap = snap.rename(columns={k: v for k, v in ren.items() if k in snap.columns})
        frames.append(_by_province_mean(snap))

    for filename in ["digital_plate_metrics.csv", "population_province.csv", "poverty_rate_all.csv", "gini_ratio_all.csv", "ski_2023_curated.csv", "engel_ratio.csv", "digital_adoption.csv"]:
        frame = _normalize(_latest_total(_read_csv(filename, CLEAN)))
        if not frame.empty:
            frames.append(_by_province_mean(frame))

    # PDRB raw
    pdrb = _read_csv("pdrb_capita.csv", RAW)
    if not pdrb.empty:
        prov = find_col(pdrb, ["Provinsi", "province"], required=True)
        val = [c for c in pdrb.columns if c != prov][-1]
        pdrb = pdrb[[prov, val]].rename(columns={prov: "province", val: "pdrb_capita_thousand"})
        pdrb["pdrb_capita_thousand"] = num_col(pdrb["pdrb_capita_thousand"])
        frames.append(_by_province_mean(_normalize(pdrb)))

    # koordinat provinsi
    prov = _read_csv("provinces.csv", CLEAN)
    if not prov.empty:
        prov_col = find_col(prov, ["Name", "province", "Provinsi"], required=True)
        lat = find_col(prov, ["Latitude", "lat"])
        lon = find_col(prov, ["Longitude", "lon", "lng"])
        cols = [prov_col] + [c for c in [lat, lon] if c]
        prov = prov[cols].rename(columns={prov_col: "province", lat: "latitude", lon: "longitude"})
        frames.append(_by_province_mean(_normalize(prov)))
    return frames


def build_metrics() -> pd.DataFrame:
    base = _load_rokok()
    merged = base.copy()
    for frame in _load_optional_context():
        if frame.empty or "province_key" not in frame.columns:
            continue
        dupes = [c for c in frame.columns if c in merged.columns and c not in ["province", "province_key"]]
        # Jangan override metrik utama dari rokok_vs_gizi, kecuali target masih null semua
        frame = frame.drop(columns=dupes, errors="ignore")
        merged = merged.merge(frame, on=["province", "province_key"], how="left")

    # Jika masih belum ada population, coba population_thousands
    if "population" not in merged.columns:
        if "population_thousands" in merged.columns:
            merged["population"] = merged["population_thousands"] * 1000
        else:
            merged["population"] = 1_000_000
    if "population_thousands" not in merged.columns:
        merged["population_thousands"] = merged["population"] / 1000

    # Kolom default agar chart aman
    defaults = {
        "poverty_rate": merged.get("poverty_rate", pd.Series(np.nan, index=merged.index)),
        "protein_per_capita": merged.get("protein_per_capita", pd.Series(np.nan, index=merged.index)),
        "calorie_per_capita": merged.get("calorie_per_capita", pd.Series(np.nan, index=merged.index)),
        "stunting_0_59_total_pct": pd.Series(np.nan, index=merged.index),
        "smoking_10plus_daily_pct": pd.Series(np.nan, index=merged.index),
        "passive_smoke_daily_pct": pd.Series(np.nan, index=merged.index),
        "mad_6_23_pct": pd.Series(np.nan, index=merged.index),
        "animal_protein_6_23_pct": pd.Series(np.nan, index=merged.index),
        "digital_index_pct": pd.Series(np.nan, index=merged.index),
        "engel_ratio": pd.Series(np.nan, index=merged.index),
        "gini": pd.Series(np.nan, index=merged.index),
        "pdrb_capita_thousand": pd.Series(np.nan, index=merged.index),
        "latitude": pd.Series(np.nan, index=merged.index),
        "longitude": pd.Series(np.nan, index=merged.index),
    }
    for col, fallback in defaults.items():
        if col not in merged.columns:
            merged[col] = fallback

    # Imputasi ringan untuk visual agar tidak crash; tetap eksplisit di tooltip sebagai data terbatas bila kosong
    for col in ["poverty_rate", "protein_per_capita", "calorie_per_capita", "stunting_0_59_total_pct", "digital_index_pct", "engel_ratio", "gini", "pdrb_capita_thousand"]:
        if merged[col].isna().all():
            merged[col] = 0
        else:
            merged[col] = merged[col].fillna(merged[col].median())

    merged["norm_rokok"] = _minmax(merged["rokok_pct_of_gizi"])
    merged["norm_poverty"] = _minmax(merged["poverty_rate"])
    merged["norm_stunting"] = _minmax(merged["stunting_0_59_total_pct"])
    merged["norm_low_protein"] = _minmax(merged["protein_per_capita"], invert=True)
    merged["norm_population"] = _minmax(merged["population"])
    merged["policy_priority_index"] = (
        merged["norm_rokok"] * 0.30
        + merged["norm_poverty"] * 0.22
        + merged["norm_stunting"] * 0.20
        + merged["norm_low_protein"] * 0.18
        + merged["norm_population"] * 0.10
    ) * 100
    merged["risk_label"] = merged["policy_priority_index"].map(_risk_label)
    merged["rank_rokok_gizi"] = merged["rokok_pct_of_gizi"].rank(ascending=False, method="min").astype(int)
    merged["rank_policy"] = merged["policy_priority_index"].rank(ascending=False, method="min").astype(int)
    merged["rokok_minus_sayur"] = merged["rokok"] - merged["sayur"]
    merged["map_key"] = merged["province_key"]
    inheritance = {
        "PAPUA SELATAN": "PAPUA",
        "PAPUA TENGAH": "PAPUA",
        "PAPUA PEGUNUNGAN": "PAPUA",
        "PAPUA BARAT DAYA": "PAPUA BARAT",
    }
    if not any(merged["province_key"].isin(inheritance)):
        additions = []
        for child, parent in inheritance.items():
            parent_rows = merged[merged["province_key"].eq(parent)]
            if parent_rows.empty:
                continue
            row = parent_rows.iloc[0].copy()
            row["province_key"] = child
            row["province"] = pretty_name(child)
            row["map_key"] = child
            row["source_status"] = "estimasi pemekaran"
            additions.append(row)
        if additions:
            merged["source_status"] = merged.get("source_status", "observed")
            merged = pd.concat([merged, pd.DataFrame(additions)], ignore_index=True)
    if "source_status" not in merged.columns:
        merged["source_status"] = "observed"
    return merged.sort_values("province").reset_index(drop=True)


def build_expenditure_long(metrics: pd.DataFrame) -> pd.DataFrame:
    labels = {
        "rokok": "Rokok",
        "sayur": "Sayur",
        "ikan": "Ikan",
        "telur_susu": "Telur & susu",
        "daging": "Daging",
        "buah": "Buah",
    }
    cols = [c for c in labels if c in metrics.columns]
    out = metrics[["province", "province_key"] + cols].melt(["province", "province_key"], cols, "commodity", "value")
    out["commodity_label"] = out["commodity"].map(labels)
    out["group"] = np.where(out["commodity"].eq("rokok"), "Rokok", "Gizi")
    return out


def build_price_trends() -> pd.DataFrame:
    df = _read_csv("indeks_harga_tahunan.csv", CLEAN)
    if df.empty or not {"year", "sub_group", "value"}.issubset(df.columns):
        # fallback ilustratif agar halaman tetap hidup
        years = list(range(2018, 2025))
        rows = []
        for name, values in {
            "Rokok/tembakau": [100, 116, 135, 158, 178, 193, 208],
            "Daging": [100, 108, 116, 126, 138, 146, 153],
            "Telur & susu": [100, 105, 111, 119, 127, 132, 136],
            "Ikan": [100, 104, 109, 116, 122, 127, 131],
            "Sayur/buah": [100, 101, 103, 105, 107, 110, 114],
        }.items():
            rows += [{"year": y, "indicator": name, "value": v} for y, v in zip(years, values)]
        return pd.DataFrame(rows)

    tmp = df.copy()
    tmp["year"] = pd.to_numeric(tmp["year"], errors="coerce")
    tmp["value"] = pd.to_numeric(tmp["value"], errors="coerce")
    patterns = {
        "Rokok/tembakau": "rokok|tembakau",
        "Daging": "daging",
        "Telur & susu": "telur|susu",
        "Ikan": "ikan",
        "Sayur/buah": "sayur|buah",
    }
    rows = []
    for label, pat in patterns.items():
        part = tmp[tmp["sub_group"].astype(str).str.contains(pat, case=False, na=False)]
        if not part.empty:
            agg = part.groupby("year", as_index=False)["value"].mean()
            if not agg.empty and agg["value"].iloc[0] != 0:
                agg["value"] = agg["value"] / agg["value"].iloc[0] * 100
            agg["indicator"] = label
            rows.append(agg)
    if rows:
        return pd.concat(rows, ignore_index=True).sort_values(["indicator", "year"])
    return pd.DataFrame(columns=["year", "indicator", "value"])


def build_trends() -> pd.DataFrame:
    df = _normalize(_read_csv("master_trends.csv", RAW))
    if df.empty:
        return pd.DataFrame()
    for col in ["year", "internet_pct", "poverty_rate", "calorie_per_capita", "protein_per_capita"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_geojson() -> dict | None:
    for filename in ["indonesia-38-provinces.geojson", "indonesia-prov.geojson"]:
        p = GEO / filename
        if not p.exists():
            continue
        with open(p, encoding="utf-8") as f:
            geo = json.load(f)
        for feat in geo.get("features", []):
            props = feat.setdefault("properties", {})
            name = None
            for key in ["province_key", "name", "Name", "NAME_1", "Propinsi", "propinsi", "provinsi", "PROVINSI"]:
                if props.get(key):
                    name = props[key]
                    break
            key = clean_name(name)
            props["province_key"] = key
            props["name"] = pretty_name(key)
        return geo
    return None


def load_all_data() -> DashboardData:
    metrics = build_metrics()
    default = "Sulawesi Barat" if "Sulawesi Barat" in set(metrics["province"]) else metrics.sort_values("rokok_pct_of_gizi", ascending=False).iloc[0]["province"]
    return DashboardData(
        metrics=metrics,
        expenditure_long=build_expenditure_long(metrics),
        price_trends=build_price_trends(),
        trends=build_trends(),
        geojson=load_geojson(),
        default_province=default,
        provinces=metrics["province"].sort_values().tolist(),
    )
