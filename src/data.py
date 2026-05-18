from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.util import clean_name, num_col

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
GEO = ROOT / "data" / "geo"


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(RAW / name)


def norm_col(series: pd.Series) -> pd.Series:
    low = series.min(skipna=True)
    high = series.max(skipna=True)
    if pd.isna(low) or pd.isna(high) or low == high:
        return pd.Series(np.nan, index=series.index)
    return (series - low) / (high - low)


def load_food() -> pd.DataFrame:
    df = read_csv("rokok_vs_gizi.csv")
    df["prov_key"] = df["province"].map(clean_name)
    return df


def load_master() -> pd.DataFrame:
    df = read_csv("master_snapshot.csv")
    df["prov_key"] = df["province"].map(clean_name)
    cols = [
        "prov_key",
        "internet_pct_total",
        "mobile_pct_total",
        "computer_pct_total",
        "exp_food_total",
        "exp_rokok_total",
        "exp_protein_total",
        "engel_ratio_total",
        "poverty_rate_total",
        "poverty_line_total",
        "gini_total",
        "population_2024",
        "Latitude",
        "Longitude",
    ]
    return df[[col for col in cols if col in df.columns]]


def load_smoke() -> pd.DataFrame:
    df = read_csv("smoking_15_province.csv")
    df = df.rename(columns={df.columns[0]: "province", df.columns[1]: "smoking_15_pct"})
    df = df.dropna(subset=["province"])
    df = df[~df["province"].str.upper().eq("INDONESIA")]
    df["prov_key"] = df["province"].map(clean_name)
    df["smoking_15_pct"] = num_col(df["smoking_15_pct"])
    return df.groupby("prov_key", as_index=False)["smoking_15_pct"].mean()


def load_pdrb() -> pd.DataFrame:
    df = read_csv("pdrb_capita.csv")
    df = df.rename(columns={df.columns[0]: "province", df.columns[1]: "pdrb_capita"})
    df["prov_key"] = df["province"].map(clean_name)
    df["pdrb_capita"] = num_col(df["pdrb_capita"])
    return df.groupby("prov_key", as_index=False)["pdrb_capita"].mean()


def load_school() -> pd.DataFrame:
    df = read_csv("school_year.csv")
    df = df.rename(columns={"Cakupan": "province", "Total": "school_year"})
    df = df.dropna(subset=["province"])
    df = df[~df["province"].str.upper().eq("INDONESIA")]
    df["prov_key"] = df["province"].map(clean_name)
    df["school_year"] = num_col(df["school_year"])
    return df.groupby("prov_key", as_index=False)["school_year"].mean()


def load_people() -> pd.DataFrame:
    df = read_csv("population_2024.csv")
    df = df.rename(columns={df.columns[0]: "province", df.columns[1]: "population_bps"})
    df = df.dropna(subset=["province"])
    df = df[~df["province"].str.upper().eq("INDONESIA")]
    df["prov_key"] = df["province"].map(clean_name)
    df["population_bps"] = num_col(df["population_bps"])
    return df.groupby("prov_key", as_index=False)["population_bps"].sum()


def load_ski() -> pd.DataFrame:
    df = pd.read_csv(CLEAN / "ski_2023_curated.csv")
    df["prov_key"] = df["province"].map(clean_name)
    return df.drop(columns=["province"])


def risk_score(df: pd.DataFrame) -> pd.Series:
    parts = []
    for col in ["rokok_pct_of_gizi", "smoking_15_pct", "smoking_indoor_pct", "stunting_0_59_total_pct"]:
        if col in df:
            parts.append(norm_col(df[col]))
    if "mad_6_23_pct" in df:
        parts.append(1 - norm_col(df["mad_6_23_pct"]))
    if not parts:
        return pd.Series(np.nan, index=df.index)
    return pd.concat(parts, axis=1).mean(axis=1, skipna=True) * 100


def load_data() -> pd.DataFrame:
    df = load_food()
    for other in [load_master(), load_smoke(), load_pdrb(), load_school(), load_people(), load_ski()]:
        df = df.merge(other, on="prov_key", how="left")
    df["province"] = df["prov_key"].str.title()
    df["province"] = df["province"].str.replace("Dki", "DKI", regex=False)
    df["province"] = df["province"].str.replace("Di Yogyakarta", "DI Yogyakarta", regex=False)
    df["population"] = df["population_bps"].fillna(df.get("population_2024"))
    df["protein_gap"] = 57 - df["protein_per_capita"]
    df["calorie_gap"] = 2100 - df["calorie_per_capita"]
    df["risk_index"] = risk_score(df)
    df["gizi_per_rokok"] = df["gizi_total"] / df["rokok"]
    return df.sort_values("province").reset_index(drop=True)


def load_trend() -> pd.DataFrame:
    df = read_csv("master_trends.csv")
    df["prov_key"] = df["province"].map(clean_name)
    df["province"] = df["prov_key"].str.title()
    df["province"] = df["province"].str.replace("Dki", "DKI", regex=False)
    return df


def load_city() -> pd.DataFrame:
    df = read_csv("smoking_city_week.csv").iloc[3:].copy()
    df.columns = ["city", "all_type", "kretek_filter", "kretek_plain", "white", "tobacco", "other"]
    df = df.dropna(subset=["city"])
    for col in df.columns[1:]:
        df[col] = num_col(df[col])
    df["weekly_smoke"] = df[["kretek_filter", "kretek_plain", "white", "tobacco", "other"]].sum(axis=1)
    df = df[df["weekly_smoke"].notna()]
    return df.sort_values("weekly_smoke", ascending=False).reset_index(drop=True)


def geo_data() -> dict:
    with open(GEO / "indonesia-prov.geojson", encoding="utf-8") as file:
        data = json.load(file)
    for item in data["features"]:
        item["properties"]["name"] = clean_name(item["properties"].get("Propinsi"))
    return data


def bi_class(df: pd.DataFrame, xcol: str, ycol: str) -> pd.DataFrame:
    temp = df.copy()
    xmed = temp[xcol].median(skipna=True)
    ymed = temp[ycol].median(skipna=True)
    temp["bi_key"] = np.select(
        [
            (temp[xcol] >= xmed) & (temp[ycol] >= ymed),
            (temp[xcol] >= xmed) & (temp[ycol] < ymed),
            (temp[xcol] < xmed) & (temp[ycol] >= ymed),
            (temp[xcol] < xmed) & (temp[ycol] < ymed),
        ],
        ["Rokok tinggi, gizi rapuh", "Rokok tinggi", "Gizi rapuh", "Lebih ringan"],
        default="Data kurang",
    )
    return temp
