from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from data_processing.geo import get_dim_province, geo_coverage
from data_processing.normalize import normalize_province_name
from data_processing.transform import compute_expenditure, merge_profile, standardize_province_column

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"


@lru_cache(maxsize=None)
def read_csv(name: str) -> pd.DataFrame:
    clean = CLEAN_DIR / name
    raw = RAW_DIR / name
    path = clean if clean.exists() else raw
    df = pd.read_csv(path)
    return standardize_province_column(df)


@lru_cache(maxsize=1)
def get_expenditure() -> pd.DataFrame:
    path = CLEAN_DIR / "expenditure_features.csv"
    if path.exists():
        return pd.read_csv(path)
    return compute_expenditure(read_csv("combined_komoditas_2024.csv"))


@lru_cache(maxsize=1)
def get_profile() -> pd.DataFrame:
    path = CLEAN_DIR / "province_profile.csv"
    if path.exists():
        return pd.read_csv(path)
    profile = merge_profile(
        get_expenditure(),
        read_csv("calorie_protein_long.csv"),
        read_csv("poverty_rate_all.csv"),
        read_csv("gini_ratio_all.csv"),
        read_csv("digital_adoption.csv"),
        read_csv("population_province.csv"),
        read_csv("ski_2023_curated.csv"),
    )
    return profile


@lru_cache(maxsize=1)
def get_map_profile() -> pd.DataFrame:
    profile = get_profile()
    dim = get_dim_province()
    return profile.merge(dim, on="province", how="left")


def get_area_profile(area: str = "total") -> pd.DataFrame:
    profile = get_map_profile()
    area = area or "total"
    if area not in set(profile["area"].dropna().unique()):
        area = "total"
    return profile[profile["area"] == area].copy()


def get_province_profile(province: str, area: str = "total") -> pd.Series:
    name = normalize_province_name(province)
    df = get_area_profile(area)
    matched = df[df["province"] == name]
    if matched.empty:
        matched = df.sort_values("vulnerability_score", ascending=False).head(1)
    return matched.iloc[0]


def coverage_status() -> dict[str, object]:
    return geo_coverage(get_dim_province())
