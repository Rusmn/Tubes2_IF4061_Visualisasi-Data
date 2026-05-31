from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from data_processing.normalize import normalize_province_name, province_key, province_region

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
EXTERNAL_DIR = DATA_DIR / "external"
GEO_DIR = DATA_DIR / "geo"

GEOJSON_CANDIDATES = [
    EXTERNAL_DIR / "indonesia-geodata-low.geojson",
    GEO_DIR / "indonesia-prov-legacy.geojson",
]


def _walk_numbers(value: Any) -> list[tuple[float, float]]:
    if not isinstance(value, list):
        return []
    if len(value) >= 2 and all(isinstance(x, (int, float)) for x in value[:2]):
        return [(float(value[0]), float(value[1]))]
    points: list[tuple[float, float]] = []
    for item in value:
        points.extend(_walk_numbers(item))
    return points


def _feature_centroid(feature: dict[str, Any]) -> tuple[float | None, float | None]:
    points = _walk_numbers(feature.get("geometry", {}).get("coordinates", []))
    if not points:
        return None, None
    lon = sum(point[0] for point in points) / len(points)
    lat = sum(point[1] for point in points) / len(points)
    return lat, lon


def _feature_name(feature: dict[str, Any]) -> str:
    props = feature.get("properties", {})
    for key in ("name", "NAME_1", "Propinsi", "provinsi", "PROVINSI"):
        if props.get(key):
            return normalize_province_name(props[key])
    return normalize_province_name(feature.get("id", ""))


@lru_cache(maxsize=1)
def load_geojson() -> dict[str, Any] | None:
    for candidate in GEOJSON_CANDIDATES:
        if not candidate.exists():
            continue
        try:
            with candidate.open(encoding="utf-8") as handle:
                geojson = json.load(handle)
            if geojson.get("features"):
                return geojson
        except json.JSONDecodeError:
            continue
    return None


def _load_external_codes() -> pd.DataFrame:
    path = EXTERNAL_DIR / "wilayah_provinces.json"
    if not path.exists():
        return pd.DataFrame(columns=["province", "province_code"])
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    rows = payload.get("data", payload if isinstance(payload, list) else [])
    records = [
        {
            "province": normalize_province_name(row.get("name")),
            "province_code": str(row.get("code", "")).strip(),
        }
        for row in rows
        if row.get("name")
    ]
    return pd.DataFrame(records).drop_duplicates("province")


def _load_local_coordinates() -> pd.DataFrame:
    path = RAW_DIR / "provinces.csv"
    if not path.exists():
        return pd.DataFrame(columns=["province", "latitude_local", "longitude_local"])
    df = pd.read_csv(path)
    df["province"] = df["Name"].map(normalize_province_name)
    return df.rename(
        columns={
            "Code": "province_code_local",
            "Latitude": "latitude_local",
            "Longitude": "longitude_local",
        }
    )[["province", "province_code_local", "latitude_local", "longitude_local"]]


def _geo_feature_table() -> pd.DataFrame:
    geojson = load_geojson()
    if not geojson:
        return pd.DataFrame(columns=["province", "geo_feature_id", "latitude_geo", "longitude_geo"])
    records = []
    for feature in geojson.get("features", []):
        props = feature.get("properties", {})
        lat, lon = _feature_centroid(feature)
        province = _feature_name(feature)
        records.append(
            {
                "province": province,
                "geo_feature_id": props.get("REGION_CODE") or props.get("id") or feature.get("id") or province,
                "latitude_geo": lat,
                "longitude_geo": lon,
            }
        )
    return pd.DataFrame(records).drop_duplicates("province")


def build_dim_province(province_source: pd.Series | list[str]) -> tuple[pd.DataFrame, dict[str, Any]]:
    provinces = pd.DataFrame({"province": [normalize_province_name(p) for p in province_source]})
    provinces = provinces.dropna().drop_duplicates("province")
    provinces["province_key"] = provinces["province"].map(province_key)

    codes = _load_external_codes()
    local = _load_local_coordinates()
    features = _geo_feature_table()
    for frame in (codes, local, features):
        if not frame.empty:
            frame["province_key"] = frame["province"].map(province_key)

    dim = provinces.merge(codes.drop(columns=["province"], errors="ignore"), on="province_key", how="left")
    dim = dim.merge(local.drop(columns=["province"], errors="ignore"), on="province_key", how="left")
    dim = dim.merge(features.drop(columns=["province"], errors="ignore"), on="province_key", how="left")

    dim["province_code"] = dim["province_code"].fillna(dim.get("province_code_local"))
    dim["latitude"] = dim["latitude_geo"].fillna(dim.get("latitude_local"))
    dim["longitude"] = dim["longitude_geo"].fillna(dim.get("longitude_local"))
    dim["province_alias"] = dim["province"]
    dim["region"] = dim["province"].map(province_region)
    dim["island"] = dim["region"]
    dim["geometry_status"] = dim["geo_feature_id"].notna().map(lambda ok: "matched" if ok else "point_fallback")

    missing_coords = dim["latitude"].isna() | dim["longitude"].isna()
    if missing_coords.any():
        dim.loc[missing_coords, "latitude"] = -2.5
        dim.loc[missing_coords, "longitude"] = 118.0
        dim.loc[missing_coords, "geometry_status"] = "missing_coordinate_fallback"

    output = dim[
        [
            "province_code",
            "province",
            "province_alias",
            "region",
            "island",
            "latitude",
            "longitude",
            "geo_feature_id",
            "geometry_status",
        ]
    ].sort_values("province")

    coverage = {
        "province_count": int(output["province"].nunique()),
        "geo_match_count": int(output["geo_feature_id"].notna().sum()),
        "fallback_point_count": int((output["geometry_status"] != "matched").sum()),
        "missing_geometry": output.loc[output["geometry_status"] != "matched", "province"].tolist(),
    }
    return output, coverage


@lru_cache(maxsize=1)
def get_dim_province() -> pd.DataFrame:
    path = DATA_DIR / "clean" / "dim_province.csv"
    if path.exists():
        return pd.read_csv(path)
    expenditure = pd.read_csv(RAW_DIR / "combined_komoditas_2024.csv")
    dim, _coverage = build_dim_province(expenditure["province"])
    return dim


def geo_coverage(dim: pd.DataFrame | None = None) -> dict[str, Any]:
    dim = get_dim_province() if dim is None else dim
    return {
        "province_count": int(dim["province"].nunique()),
        "geo_match_count": int(dim["geo_feature_id"].notna().sum()),
        "fallback_point_count": int((dim["geometry_status"] != "matched").sum()),
        "missing_geometry": dim.loc[dim["geometry_status"] != "matched", "province"].tolist(),
    }
