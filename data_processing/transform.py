from __future__ import annotations

import numpy as np
import pandas as pd

from data_processing.normalize import normalize_province_name

COMMODITY_MAP = {
    "Rokok/Cigarettes": "rokok",
    "Rokok dan tembakau/Cigarettes and tobacco": "rokok",
    "Sayur-sayuran/Vegetables": "sayur",
    "Ikan/udang/cumi/kerang": "ikan",
    "Telur dan susu/Eggs and milk": "telur_susu",
    "Daging/Meat": "daging",
    "Buah-buahan/Fruits": "buah",
}

NUTRITION_COLUMNS = ["sayur", "ikan", "telur_susu", "daging", "buah"]


def minmax(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    spread = values.max() - values.min()
    if pd.isna(spread) or spread == 0:
        return pd.Series(0.0, index=series.index)
    return (values - values.min()) / spread


def minmax_context(series: pd.Series) -> pd.Series:
    return minmax(series).fillna(0.5)


def standardize_province_column(df: pd.DataFrame) -> pd.DataFrame:
    if "province" not in df.columns:
        return df
    result = df.copy()
    result["province"] = result["province"].map(normalize_province_name)
    return result


def compute_expenditure(raw: pd.DataFrame) -> pd.DataFrame:
    df = standardize_province_column(raw)
    df = df[df["commodity"].isin(COMMODITY_MAP)].copy()
    df["metric"] = df["commodity"].map(COMMODITY_MAP)
    pivot = (
        df.pivot_table(index=["province", "area"], columns="metric", values="value", aggfunc="sum")
        .reset_index()
        .rename_axis(None, axis=1)
    )
    for column in ["rokok", *NUTRITION_COLUMNS]:
        if column not in pivot.columns:
            pivot[column] = 0.0
    pivot["gizi_total"] = pivot[NUTRITION_COLUMNS].sum(axis=1)
    pivot["rokok_pct_of_gizi"] = np.where(
        pivot["gizi_total"] > 0,
        pivot["rokok"] / pivot["gizi_total"] * 100,
        np.nan,
    )
    pivot["rokok_minus_sayur"] = pivot["rokok"] - pivot["sayur"]
    pivot["rokok_vs_sayur_ratio"] = np.where(pivot["sayur"] > 0, pivot["rokok"] / pivot["sayur"], np.nan)
    pivot["gizi_deficit_index"] = np.where(
        pivot["rokok"] > 0,
        (pivot["rokok"] - pivot["gizi_total"]) / pivot["rokok"],
        np.nan,
    )
    pivot["rokok_rank"] = pivot.groupby("area")["rokok"].rank(method="dense", ascending=False).astype(int)
    return pivot


def latest_by_year(df: pd.DataFrame, year: int = 2024) -> pd.DataFrame:
    if "year" not in df.columns:
        return df
    data = standardize_province_column(df)
    preferred = data[data["year"] == year]
    if not preferred.empty:
        return preferred
    latest_year = data["year"].max()
    return data[data["year"] == latest_year]


def merge_profile(
    expenditure: pd.DataFrame,
    calorie_protein: pd.DataFrame,
    poverty: pd.DataFrame,
    gini: pd.DataFrame,
    digital: pd.DataFrame,
    population: pd.DataFrame,
    ski: pd.DataFrame,
    year: int = 2024,
) -> pd.DataFrame:
    base = expenditure.copy()

    cp = latest_by_year(calorie_protein, year)[["province", "calorie_per_capita", "protein_per_capita"]]
    pov = latest_by_year(poverty, year)
    pov = pov[pov.get("area", "total") == "total"][["province", "poverty_rate"]]
    gini_df = latest_by_year(gini, year)
    gini_df = gini_df[gini_df.get("area", "total") == "total"][["province", "gini"]]
    digital_df = latest_by_year(digital, year)
    digital_df = digital_df[digital_df.get("area", "total") == "total"][
        ["province", "internet_pct", "mobile_pct", "computer_pct", "digital_index_pct"]
    ]
    pop = latest_by_year(population, year)[["province", "population_thousands"]]
    ski_df = standardize_province_column(ski)

    for frame in (cp, pov, gini_df, digital_df, pop, ski_df):
        base = base.merge(frame, on="province", how="left")

    base["vulnerability_score"] = (
        minmax(base["rokok_pct_of_gizi"]) * 0.35
        + minmax(base["poverty_rate"]) * 0.30
        + minmax(1 / base["protein_per_capita"].replace(0, np.nan)) * 0.35
    ) * 100
    base["policy_priority_score"] = (
        minmax(base["rokok_pct_of_gizi"]) * 0.30
        + minmax(base["poverty_rate"]) * 0.25
        + minmax(1 / base["protein_per_capita"].replace(0, np.nan)) * 0.25
        + minmax(base["population_thousands"]) * 0.20
    ) * 100
    base["ski_health_context_score"] = (
        minmax_context(base["smoking_10plus_current_pct"]) * 0.25
        + minmax_context(base["stunting_0_59_total_pct"]) * 0.25
        + minmax_context(base["milk_rare_pct"]) * 0.20
        + minmax_context(1 / base["fish_daily_pct"].replace(0, np.nan)) * 0.15
        + minmax_context(1 / base["egg_daily_pct"].replace(0, np.nan)) * 0.15
    ) * 100
    base["policy_priority_score"] = (
        base["policy_priority_score"] * 0.70 + base["ski_health_context_score"].fillna(0) * 0.30
    )
    return base
