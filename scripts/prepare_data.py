from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data_processing.geo import build_dim_province, geo_coverage, load_geojson
from data_processing.transform import compute_expenditure, merge_profile, standardize_province_column

RAW_DIR = ROOT / "data" / "raw"
CLEAN_DIR = ROOT / "data" / "clean"
GEO_DIR = ROOT / "data" / "geo"


def read(name: str) -> pd.DataFrame:
    return standardize_province_column(pd.read_csv(RAW_DIR / name))


def main() -> None:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    GEO_DIR.mkdir(parents=True, exist_ok=True)

    expenditure_raw = read("combined_komoditas_2024.csv")
    expenditure = compute_expenditure(expenditure_raw)
    expenditure.to_csv(CLEAN_DIR / "expenditure_features.csv", index=False)

    dim, coverage = build_dim_province(expenditure["province"])
    dim.to_csv(CLEAN_DIR / "dim_province.csv", index=False)

    geojson = load_geojson()
    if geojson:
        with (GEO_DIR / "indonesia_provinces.geojson").open("w", encoding="utf-8") as handle:
            json.dump(geojson, handle)

    ski_path = CLEAN_DIR / "ski_2023_curated.csv"
    ski = pd.read_csv(ski_path if ski_path.exists() else RAW_DIR / "ski_2023_curated.csv")

    profile = merge_profile(
        expenditure,
        read("calorie_protein_long.csv"),
        read("poverty_rate_all.csv"),
        read("gini_ratio_all.csv"),
        read("digital_adoption.csv"),
        read("population_province.csv"),
        ski,
    )
    profile.to_csv(CLEAN_DIR / "province_profile.csv", index=False)

    coverage = geo_coverage(dim)
    (CLEAN_DIR / "geo_coverage.json").write_text(json.dumps(coverage, indent=2), encoding="utf-8")
    print(f"provinces: {coverage['province_count']}")
    print(f"geo matches: {coverage['geo_match_count']}")
    print(f"fallback points: {coverage['fallback_point_count']}")


if __name__ == "__main__":
    main()
