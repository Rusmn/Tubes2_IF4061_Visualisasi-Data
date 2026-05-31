from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd

from data_processing.normalize import normalize_province_name

ROOT = Path(__file__).resolve().parents[1]
CLEAN_DIR = ROOT / "data" / "clean"

GREYOUT_PROVINCES = {"Papua Barat Daya", "Papua Pegunungan", "Papua Selatan", "Papua Tengah"}
EXPENDITURE_METRICS = {"rokok_pct_of_gizi", "rokok_pct_of_sayur", "rokok_pct_of_daging"}

METRIC_OPTIONS = [
    {"label": "Rokok % dari Gizi Total", "value": "rokok_pct_of_gizi"},
    {"label": "Rokok % dari Sayuran", "value": "rokok_pct_of_sayur"},
    {"label": "Rokok % dari Daging", "value": "rokok_pct_of_daging"},
    {"label": "Rokok vs Stunting Balita", "value": "stunting_pct"},
]

REGION_OPTIONS = [
    {"label": "Seluruh Indonesia", "value": "all"},
    {"label": "Jawa", "value": "Jawa"},
    {"label": "Sumatera", "value": "Sumatera"},
    {"label": "Kalimantan", "value": "Kalimantan"},
    {"label": "Sulawesi", "value": "Sulawesi"},
    {"label": "Bali-Nusa Tenggara", "value": "Bali-Nusa Tenggara"},
    {"label": "Maluku-Papua", "value": "Maluku-Papua"},
]

BUTTERFLY_DIMENSION_OPTIONS = [
    {"label": "Jenis Kelamin", "value": "gender"},
    {"label": "Pendidikan", "value": "pendidikan"},
    {"label": "Pekerjaan", "value": "pekerjaan"},
    {"label": "Tempat Tinggal", "value": "tempat_tinggal"},
    {"label": "Status Ekonomi", "value": "status_ekonomi"},
]


@lru_cache(maxsize=1)
def load_master_profile() -> pd.DataFrame:
    return pd.read_csv(CLEAN_DIR / "master_profile.csv")


def get_filtered_data(metric_col: str = "rokok_pct_of_gizi", region: str = "all") -> pd.DataFrame:
    df = load_master_profile().copy()

    # Region mask
    if region == "Maluku-Papua":
        in_region = df["region"].isin(["Maluku", "Papua"])
    elif region != "all":
        in_region = df["region"] == region
    else:
        in_region = pd.Series(True, index=df.index)

    # Grey-out = outside region OR no expenditure data (for pengeluaran metrics)
    no_exp_data = df["province"].isin(GREYOUT_PROVINCES) if metric_col in EXPENDITURE_METRICS else pd.Series(False, index=df.index)
    df["_greyed_out"] = (~in_region) | no_exp_data
    return df


@lru_cache(maxsize=8)
def get_butterfly_data(dimension: str) -> pd.DataFrame:
    return pd.read_csv(CLEAN_DIR / f"butterfly_{dimension}.csv")


@lru_cache(maxsize=1)
def get_regression_models() -> dict:
    path = CLEAN_DIR / "regression_models.json"
    return json.loads(path.read_text(encoding="utf-8"))


def get_province_row(province: str) -> pd.Series:
    name = normalize_province_name(province)
    df = load_master_profile()
    matched = df[df["province"] == name]
    if matched.empty:
        matched = df.sort_values("stunting_pct", ascending=False).head(1)
    return matched.iloc[0]


def get_dim_province() -> pd.DataFrame:
    return pd.read_csv(CLEAN_DIR / "dim_province.csv")


def coverage_status() -> dict:
    dim = get_dim_province()
    return {
        "province_count": int(dim["province"].nunique()),
        "geo_match_count": int((dim["geometry_status"] == "matched").sum()),
        "fallback_point_count": int((dim["geometry_status"] != "matched").sum()),
    }
