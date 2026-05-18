import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_RAW = [
    ROOT / "data_gabungan",
    ROOT.parent / "data_gabungan",
    Path("/Users/rusmn/Kuliah/SEMESTER 6/Visualisasi Data/Tubes/data_gabungan")
]

RAW = None
for p in CANDIDATE_RAW:
    if p.exists():
        RAW = p
        break
if RAW is None:
    RAW = ROOT / "data_gabungan"  # fallback
CLEAN = ROOT / "data" / "clean"
GEO = ROOT / "data" / "geo"


def ensure_dirs():
    CLEAN.mkdir(parents=True, exist_ok=True)
    GEO.mkdir(parents=True, exist_ok=True)


def copy_csv_simple(name: str):
    src = RAW / name
    dst = CLEAN / name
    if not src.exists():
        print(f"WARN: source missing {src}")
        return

    with src.open(encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        rows = []
        for r in reader:
            # Normalise year if present
            if "year" in r and r["year"]:
                try:
                    y = int(r["year"])
                except Exception:
                    y = None
                if y == 2024:
                    rows.append(r)
                elif y == 2023:
                    r["year"] = "2024"
                    r["_inferred_from_2023"] = "1"
                    rows.append(r)
                else:
                    # if no year values or other year, include row (for non-year tables)
                    rows.append(r)
            else:
                rows.append(r)

    if rows:
        # determine all fieldnames across rows (some rows may have extra keys)
        fieldnames = []
        for r in rows:
            for k in r.keys():
                if k not in fieldnames:
                    fieldnames.append(k)
        with dst.open("w", encoding="utf-8", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()
            for r in rows:
                # ensure all keys present
                out = {k: r.get(k, "") for k in fieldnames}
                writer.writerow(out)
        print(f"Wrote {dst}")
    else:
        print(f"No rows written for {name}")


def copy_geojson():
    src = RAW / "indonesia-prov.geojson"
    dst = GEO / "indonesia-prov.geojson"
    if src.exists():
        data = json.loads(src.read_text(encoding="utf-8"))
        for f in data.get("features", []):
            props = f.get("properties", {})
            name = props.get("name") or props.get("propinsi") or props.get("Propinsi") or props.get("provinsi")
            f.setdefault("properties", {})
            f["properties"]["name"] = (name or "").title()
        dst.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        print(f"Copied geojson to {dst}")
    else:
        print("No geojson found in data_gabungan/")


def main():
    ensure_dirs()
    files = [
        "combined_komoditas_2024.csv",
        "digital_plate_metrics.csv",
        "commodity_baseline_national.csv",
        "calorie_protein_long.csv",
        "population_province.csv",
        "poverty_rate_all.csv",
    ]
    for f in files:
        copy_csv_simple(f)
    copy_geojson()


if __name__ == "__main__":
    main()
