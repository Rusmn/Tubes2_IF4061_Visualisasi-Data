from __future__ import annotations

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external"

SOURCES = {
    "indonesia-geodata-low.geojson": "https://cdn.jsdelivr.net/npm/indonesia-geodata@0.1.2/json/indonesiaLow.json",
    "wilayah_provinces.json": "https://wilayah.id/api/provinces.json",
}


def main() -> None:
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    for filename, url in SOURCES.items():
        target = EXTERNAL_DIR / filename
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                target.write_bytes(response.read())
            print(f"downloaded {filename}")
        except Exception as exc:
            if target.exists():
                print(f"kept cached {filename}: {exc}")
            else:
                print(f"missing {filename}: {exc}")


if __name__ == "__main__":
    main()
