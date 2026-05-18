import pandas as pd
from pathlib import Path
import json
import requests
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"
GEO = ROOT / "data" / "geo"

def load_csv(filename):
    return pd.read_csv(CLEAN / filename)

def load_all_data():
    metrics = load_csv("digital_plate_metrics.csv")
    metrics["province"] = metrics["province"].astype(str).str.title()
    # Ensure metrics are 2024 only; if only 2023 exists, assume as 2024 and mark as inferred
    if "year" in metrics.columns:
        if 2024 in metrics["year"].unique():
            metrics = metrics[metrics["year"] == 2024]
        elif 2023 in metrics["year"].unique():
            metrics_2023 = metrics[metrics["year"] == 2023].copy()
            metrics_2023["year"] = 2024
            metrics_2023["_inferred_from_2023"] = True
            metrics = metrics_2023

    
    # Merge additional specific metrics if they exist
    try:
        rokok = load_csv("rokok_vs_gizi.csv")
        rokok["province"] = rokok["province"].astype(str).str.title()
        metrics = metrics.merge(rokok[["province", "rokok_pct_of_gizi", "gizi_total"]], on="province", how="left")
    except FileNotFoundError:
        pass
        
    try:
        ski = load_csv("ski_2023_curated.csv")
        ski["province"] = ski["province"].astype(str).str.title()
        metrics = metrics.merge(ski[["province", "stunting_0_59_total_pct", "mad_6_23_pct"]], on="province", how="left")
    except FileNotFoundError:
        pass

    return {
        "calorie_protein": load_csv("calorie_protein_long.csv"),
        "komoditas_2024": load_csv("combined_komoditas_2024.csv"),
        "baseline_national": load_csv("commodity_baseline_national.csv"),
        "digital_adoption": load_csv("digital_adoption.csv"),
        "metrics": metrics,
        "engel_ratio": load_csv("engel_ratio.csv"),
        "gini_ratio": load_csv("gini_ratio.csv"),
        "indeks_harga": load_csv("indeks_harga_tahunan.csv"),
        "inflasi": load_csv("inflasi_tahunan.csv"),
        "population": load_csv("population_province.csv"),
        "poverty": load_csv("poverty_rate_all.csv"),
        "provinces": load_csv("provinces.csv")
    }

def geo_data():
    geo_file = GEO / "indonesia-prov.geojson"
    # Try local file first
    if geo_file.exists():
        with open(geo_file, encoding="utf-8") as file:
            data = json.load(file)
    else:
        # Try to download a commonly used Indonesia provinces geojson
        url_candidates = [
            "https://raw.githubusercontent.com/chmdznr/indonesia-geojson/master/indonesia-province.geojson",
            "https://raw.githubusercontent.com/angga-ramadhan/indonesia-geojson/main/indonesia-provinces.geojson",
        ]
        data = None
        for url in url_candidates:
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    # save local copy
                    geo_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(geo_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False)
                    break
            except Exception:
                continue
        if data is None:
            raise FileNotFoundError(f"GeoJSON not found locally and download failed: {geo_file}")

    # Normalize property name keys and ensure title-case names
    for item in data.get("features", []):
        props = item.get("properties", {})
        name = props.get("name") or props.get("propinsi") or props.get("Propinsi") or props.get("provinsi")
        item["properties"]["name"] = (name or "").title()

    return data
