from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data_processing.normalize import normalize_province_name, province_region

NEW_DATA_DIR = ROOT / "new_data"
CLEAN_DIR = ROOT / "data" / "clean"
GEO_DIR = ROOT / "data" / "geo"

GREYOUT_PROVINCES = {"Papua Barat Daya", "Papua Pegunungan", "Papua Selatan", "Papua Tengah"}

BUTTERFLY_CONFIG: dict[str, dict] = {
    "gender": {
        "smoking_labels": ["Laki-laki", "Perempuan"],
        "stunting_labels": ["Laki-laki", "Perempuan"],
        "display_labels": ["Laki-laki", "Perempuan"],
    },
    "pendidikan": {
        "smoking_labels": ["Tidak sekolah", "Tidak tamat SD", "Tamat SD", "Tamat SLTP", "Tamat SLTA", "Tamat D1/D2/D3/PT"],
        "stunting_labels": ["Tidak/belum pernah sekolah", "Tidak tamat SD/MI", "Tamat SD/MI", "Tamat SLTP/MTS", "Tamat SLTA/MA", "Tamat D1/D2/D3/PT"],
        "display_labels": ["Tidak Sekolah", "Tidak Tamat SD", "Tamat SD", "Tamat SLTP", "Tamat SLTA", "Tamat D1/D2/D3/PT"],
    },
    "pekerjaan": {
        "smoking_labels": ["Tidak Bekerja", "Sekolah", "PNS/TNI/Polri/BUMN/BUMD", "Pegawai swasta", "Wiraswasta", "Petani/Buruh tani", "Nelayan", "Buruh/sopir/pembantu ruta"],
        "stunting_labels": ["Tidak bekerja", "Sekolah", "PNS/TNI/Polri/BUMN/BUMD", "Pegawai Swasta", "Wiraswasta", "Petani/buruh tani", "Nelayan", "Buruh/sopir/pembantu ruta"],
        "display_labels": ["Tidak Bekerja", "Sekolah", "PNS/TNI/Polri", "Pegawai Swasta", "Wiraswasta", "Petani/Buruh Tani", "Nelayan", "Buruh/Sopir"],
    },
    "tempat_tinggal": {
        "smoking_labels": ["Perkotaan", "Perdesaan"],
        "stunting_labels": ["Perkotaan", "Pedesaan"],
        "display_labels": ["Perkotaan", "Perdesaan"],
    },
    "status_ekonomi": {
        "smoking_labels": ["Terbawah", "Menengah Bawah", "Menengah", "Menengah Atas", "Teratas"],
        "stunting_labels": None,
        "display_labels": ["Terbawah", "Menengah Bawah", "Menengah", "Menengah Atas", "Teratas"],
    },
}


def _norm(val: object) -> str:
    return normalize_province_name(val)


def parse_rokok_vs_gizi() -> pd.DataFrame:
    df = pd.read_csv(NEW_DATA_DIR / "rokok_vs_gizi.csv")
    df["province"] = df["province"].map(_norm)
    df["rokok_pct_of_sayur"] = df["rokok"] / df["sayur"] * 100
    df["rokok_pct_of_daging"] = np.where(df["daging"] > 0, df["rokok"] / df["daging"] * 100, np.nan)
    return df


def parse_tabel_11_29() -> pd.DataFrame:
    df = pd.read_csv(NEW_DATA_DIR / "tabel_11_29_prevalensi_merokok_provinsi.csv", skiprows=1)
    df = df.rename(columns={
        df.columns[0]: "province",
        "Perokok Setiap Hari (%)": "smoking_daily_pct",
        "Perokok Kadang-kadang (%)": "smoking_sometimes_pct",
        "Mantan Perokok (%)": "ex_smoker_pct",
        "Bukan perokok (%)": "non_smoker_pct",
        "N tertimbang": "n_sample",
    })
    df = df[~df["province"].isin(["INDONESIA"])].copy()
    df["province"] = df["province"].map(_norm)
    for col in ["smoking_daily_pct", "smoking_sometimes_pct", "ex_smoker_pct", "non_smoker_pct", "n_sample"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[["province", "smoking_daily_pct", "smoking_sometimes_pct", "ex_smoker_pct", "non_smoker_pct", "n_sample"]].copy()


def parse_tabel_14_106() -> pd.DataFrame:
    df = pd.read_csv(NEW_DATA_DIR / "tabel_14_106_status_gizi_baduta_provinsi.csv", skiprows=1)
    df = df.rename(columns={
        df.columns[0]: "province",
        "Severely Stunting (%)": "severely_stunting_pct",
        "Stunting (%)": "stunting_pct",
        "Normal (%)": "normal_pct",
    })
    df = df[~df["province"].isin(["INDONESIA"])].copy()
    df["province"] = df["province"].map(_norm)
    for col in ["severely_stunting_pct", "stunting_pct", "normal_pct"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[["province", "severely_stunting_pct", "stunting_pct", "normal_pct"]].copy()


def parse_tabel_11_30() -> pd.DataFrame:
    df = pd.read_csv(NEW_DATA_DIR / "tabel_11_30_prevalensi_merokok_karakteristik.csv", skiprows=1)
    df = df.rename(columns={df.columns[0]: "karakteristik", "Perokok setiap hari (%)": "smoking_daily_pct"})
    df["smoking_daily_pct"] = pd.to_numeric(df["smoking_daily_pct"], errors="coerce")
    df["karakteristik"] = df["karakteristik"].astype(str).str.strip()
    # Drop section-header rows (no numeric value in smoking_daily_pct)
    return df[df["smoking_daily_pct"].notna()][["karakteristik", "smoking_daily_pct"]].copy()


def parse_tabel_14_107() -> pd.DataFrame:
    # Section-header rows (e.g. "Jenis Kelamin,,,,,,,,") have 1 more comma than the 8-column
    # header, so pandas treats CSV col-0 as the DataFrame index and shifts named columns right
    # by 1.  After that shift the actual "Stunting (%)" values land in "Severely Stunting 95% CI".
    df = pd.read_csv(NEW_DATA_DIR / "tabel_14_107_status_gizi_baduta_karakteristik.csv", skiprows=1)
    df["karakteristik"] = df.index.astype(str).str.strip()
    df["stunting_pct"] = pd.to_numeric(df["Severely Stunting 95% CI"], errors="coerce")
    return df[df["stunting_pct"].notna()][["karakteristik", "stunting_pct"]].copy()


def build_master_profile(
    rokok: pd.DataFrame,
    smoking: pd.DataFrame,
    stunting_prov: pd.DataFrame,
    dim: pd.DataFrame,
) -> pd.DataFrame:
    # 34 provinces with expenditure data
    base = rokok.merge(smoking, on="province", how="left")
    base = base.merge(stunting_prov, on="province", how="left")
    base["has_expenditure_data"] = True

    # 4 Papua baru — only SKI data, no expenditure
    extra_smoking = smoking[smoking["province"].isin(GREYOUT_PROVINCES)].copy()
    extra_stunting = stunting_prov[stunting_prov["province"].isin(GREYOUT_PROVINCES)].copy()
    extra = extra_smoking.merge(extra_stunting, on="province", how="outer")
    extra["has_expenditure_data"] = False

    profile = pd.concat([base, extra], ignore_index=True)

    # Population proxy from n_sample (weighted survey N ∝ population)
    max_n = profile["n_sample"].max()
    profile["population_thousands"] = (profile["n_sample"] / max_n * 50_000).round(0)

    # Merge geo metadata (lat, lon, geo_feature_id, geometry_status, province_code)
    geo_cols = ["province", "province_code", "geo_feature_id", "latitude", "longitude", "geometry_status"]
    profile = profile.merge(dim[geo_cols], on="province", how="left")

    profile["region"] = profile["province"].map(province_region)
    return profile


def build_butterfly_dim(
    smoking_char: pd.DataFrame,
    stunting_char: pd.DataFrame,
    dimension: str,
) -> pd.DataFrame:
    cfg = BUTTERFLY_CONFIG[dimension]
    rows = []
    for i, s_label in enumerate(cfg["smoking_labels"]):
        d_label = cfg["display_labels"][i]
        row: dict = {"label": d_label}

        s_match = smoking_char[smoking_char["karakteristik"].astype(str).str.strip() == s_label.strip()]
        row["smoking_daily_pct"] = float(s_match["smoking_daily_pct"].iloc[0]) if not s_match.empty else None

        if cfg["stunting_labels"] is None:
            row["stunting_pct"] = None
        else:
            st_label = cfg["stunting_labels"][i]
            st_match = stunting_char[stunting_char["karakteristik"].astype(str).str.strip() == st_label.strip()]
            row["stunting_pct"] = float(st_match["stunting_pct"].iloc[0]) if not st_match.empty else None

        rows.append(row)
    return pd.DataFrame(rows)


def compute_regression_models(profile: pd.DataFrame) -> dict:
    df = profile.dropna(subset=["rokok", "stunting_pct", "protein_per_capita"])
    if len(df) < 5:
        return {"n_obs": 0, "stunting": {}, "protein": {}}
    X = df[["rokok"]].values

    stunting_m = LinearRegression().fit(X, df["stunting_pct"].values)
    protein_m = LinearRegression().fit(X, df["protein_per_capita"].values)

    return {
        "n_obs": int(len(df)),
        "stunting": {
            "coef": float(stunting_m.coef_[0]),
            "intercept": float(stunting_m.intercept_),
            "r2": round(float(stunting_m.score(X, df["stunting_pct"].values)), 3),
        },
        "protein": {
            "coef": float(protein_m.coef_[0]),
            "intercept": float(protein_m.intercept_),
            "r2": round(float(protein_m.score(X, df["protein_per_capita"].values)), 3),
        },
    }


def _ensure_dim_province(smoking: pd.DataFrame) -> pd.DataFrame:
    dim_path = CLEAN_DIR / "dim_province.csv"
    if dim_path.exists():
        return pd.read_csv(dim_path)
    from data_processing.geo import build_dim_province
    dim, _ = build_dim_province(smoking["province"])
    dim.to_csv(dim_path, index=False)
    return dim


def main() -> None:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    print("Parsing source data...")
    rokok = parse_rokok_vs_gizi()
    smoking = parse_tabel_11_29()
    stunting_prov = parse_tabel_14_106()

    dim = _ensure_dim_province(smoking)

    print("Building master profile...")
    profile = build_master_profile(rokok, smoking, stunting_prov, dim)
    profile.to_csv(CLEAN_DIR / "master_profile.csv", index=False)
    has_exp = profile["has_expenditure_data"].sum()
    print(f"  {len(profile)} provinces total, {has_exp} with expenditure data")

    print("Building butterfly datasets...")
    smoking_char = parse_tabel_11_30()
    stunting_char = parse_tabel_14_107()
    for dim_name in BUTTERFLY_CONFIG:
        df_b = build_butterfly_dim(smoking_char, stunting_char, dim_name)
        df_b.to_csv(CLEAN_DIR / f"butterfly_{dim_name}.csv", index=False)
    print(f"  {len(BUTTERFLY_CONFIG)} dimension files written")

    print("Computing regression models...")
    models = compute_regression_models(profile)
    (CLEAN_DIR / "regression_models.json").write_text(json.dumps(models, indent=2), encoding="utf-8")
    print(f"  stunting R²={models['stunting'].get('r2', 'N/A')}, protein R²={models['protein'].get('r2', 'N/A')}, n={models['n_obs']}")

    print("Done.")


if __name__ == "__main__":
    main()
