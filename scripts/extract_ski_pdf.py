from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data_processing.normalize import normalize_province_name

PDF_PATH = ROOT / "_source_archive" / "documents" / "LAPORAN SKI 2023 DALAM ANGKA_REVISI I_OK.pdf"
FALLBACK = ROOT / "data" / "raw" / "ski_2023_curated.csv"
OUTPUT = ROOT / "data" / "clean" / "ski_2023_curated.csv"
LOG = ROOT / "data" / "clean" / "ski_pdf_extraction_notes.txt"

PROVINCES = [
    "Aceh",
    "Sumatera Utara",
    "Sumatera Barat",
    "Riau",
    "Jambi",
    "Sumatera Selatan",
    "Bengkulu",
    "Lampung",
    "Bangka Belitung",
    "Kepulauan Riau",
    "DKI Jakarta",
    "Jawa Barat",
    "Jawa Tengah",
    "DI Yogyakarta",
    "Jawa Timur",
    "Banten",
    "Bali",
    "Nusa Tenggara Barat",
    "Nusa Tenggara Timur",
    "Kalimantan Barat",
    "Kalimantan Tengah",
    "Kalimantan Selatan",
    "Kalimantan Timur",
    "Kalimantan Utara",
    "Sulawesi Utara",
    "Sulawesi Tengah",
    "Sulawesi Selatan",
    "Sulawesi Tenggara",
    "Gorontalo",
    "Sulawesi Barat",
    "Maluku Utara",
    "Maluku",
    "Papua Barat Daya",
    "Papua Barat",
    "Papua Selatan",
    "Papua Tengah",
    "Papua Pegunungan",
    "Papua",
]

PROVINCES_BY_LENGTH = sorted(PROVINCES, key=len, reverse=True)


def _num(value: str) -> float:
    return float(value.replace(".", "").replace(",", "."))


def numbers(line: str) -> list[float]:
    return [_num(match.group()) for match in re.finditer(r"\d+(?:[.,]\d+)?", line)]


def province_line(line: str) -> tuple[str, str] | None:
    line = " ".join(line.split())
    if not line or line.startswith("INDONESIA"):
        return None
    for province in PROVINCES_BY_LENGTH:
        if line.startswith(province + " ") or line == province:
            return normalize_province_name(province), line[len(province) :].strip()
    return None


def parse_page(reader, page_number: int, fields: dict[str, int | tuple[int, ...]]) -> dict[str, dict[str, float]]:
    page = reader.pages[page_number - 1]
    text = page.extract_text() or ""
    rows: dict[str, dict[str, float]] = {}
    for line in text.splitlines():
        parsed = province_line(line)
        if not parsed:
            continue
        province, rest = parsed
        vals = numbers(rest)
        if not vals:
            continue
        rows.setdefault(province, {})
        for field, index in fields.items():
            if isinstance(index, tuple):
                selected = [vals[i] for i in index if i < len(vals)]
                if len(selected) == len(index):
                    rows[province][field] = sum(selected)
            elif index < len(vals):
                rows[province][field] = vals[index]
    return rows


def merge_rows(base: dict[str, dict[str, float]], addition: dict[str, dict[str, float]]) -> None:
    for province, values in addition.items():
        base.setdefault(province, {}).update(values)


def extract_selected_ski_tables() -> tuple[list[dict[str, object]], list[str]]:
    from pypdf import PdfReader

    reader = PdfReader(str(PDF_PATH))
    rows: dict[str, dict[str, float]] = {}
    notes = [
        "SKI PDF extraction note",
        f"PDF source: {PDF_PATH}",
        f"PDF pages detected: {len(reader.pages)}",
        "Parsed selected province tables from SKI 2023 Dalam Angka.",
    ]

    table_specs = {
        431: {"stunting_knowledge_correct_pct": 0},
        433: {
            "stunting_knowledge_weight_not_gain_pct": 0,
            "stunting_knowledge_failed_growth_pct": 1,
            "stunting_knowledge_stunted_pct": 4,
            "stunting_knowledge_chronic_malnutrition_pct": 5,
        },
        462: {
            "smoking_10_18_daily_pct": 0,
            "smoking_10_18_current_pct": (0, 3),
            "smoking_10_18_never_pct": 9,
        },
        464: {
            "smoking_10plus_daily_pct": 0,
            "smoking_10plus_current_pct": (0, 3),
            "smoking_10plus_never_pct": 9,
        },
        466: {"cigarettes_per_day": 0, "cigarettes_per_week_occasional": 3},
        468: {"cigarette_pack_price_rupiah": 0},
        470: {"smoking_start_10_14_pct": 3, "smoking_start_15_19_pct": 6},
        524: {"fish_daily_pct": 0, "fish_weekly_pct": 3, "fish_rare_pct": 6},
        526: {"egg_daily_pct": 0, "egg_weekly_pct": 3, "egg_rare_pct": 6},
        528: {"milk_daily_pct": 0, "milk_weekly_pct": 3, "milk_rare_pct": 6},
    }

    for page_number, fields in table_specs.items():
        parsed = parse_page(reader, page_number, fields)
        merge_rows(rows, parsed)
        notes.append(f"page {page_number}: parsed {len(parsed)} province rows")

    records = [{"province": province, **values} for province, values in sorted(rows.items())]
    return records, notes


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    try:
        records, notes = extract_selected_ski_tables()
    except Exception as exc:
        notes = [f"PDF table extraction failed: {exc}", "Using curated fallback only."]

    if not FALLBACK.exists():
        raise FileNotFoundError(f"Missing SKI curated fallback: {FALLBACK}")

    curated: dict[str, dict[str, object]] = {}
    with FALLBACK.open(newline="", encoding="utf-8") as src:
        reader = csv.DictReader(src)
        for row in reader:
            province = normalize_province_name(row["province"])
            row["province"] = province
            curated[province] = row

    for record in records:
        province = normalize_province_name(record["province"])
        curated.setdefault(province, {"province": province})
        curated[province].update(record)

    fieldnames = ["province"]
    for row in curated.values():
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)

    with OUTPUT.open("w", newline="", encoding="utf-8") as dst:
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(curated.values())

    LOG.write_text("\n".join(notes), encoding="utf-8")
    print(f"wrote {OUTPUT}")
    print(f"wrote {LOG}")


if __name__ == "__main__":
    main()
