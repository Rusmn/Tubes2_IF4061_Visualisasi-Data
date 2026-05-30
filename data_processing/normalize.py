from __future__ import annotations

import re


PROVINCE_ALIASES = {
    "DKI JAKARTA": "Jakarta Raya",
    "JAKARTA": "Jakarta Raya",
    "JAKARTA RAYA": "Jakarta Raya",
    "DI YOGYAKARTA": "Yogyakarta",
    "DAERAH ISTIMEWA YOGYAKARTA": "Yogyakarta",
    "YOGYAKARTA": "Yogyakarta",
    "KEP. RIAU": "Kepulauan Riau",
    "KEPULAUAN RIAU": "Kepulauan Riau",
    "KEP. BANGKA BELITUNG": "Kepulauan Bangka Belitung",
    "KEPULAUAN BANGKA BELITUNG": "Kepulauan Bangka Belitung",
    "BANGKA BELITUNG": "Kepulauan Bangka Belitung",
    "SUMATRA UTARA": "Sumatera Utara",
    "SUMATRA BARAT": "Sumatera Barat",
    "NANGGROE ACEH DARUSSALAM": "Aceh",
    "PAPUA BARAT DAYA": "Papua Barat Daya",
    "PAPUA BARAT DAYA ": "Papua Barat Daya",
    "PAPUA PEGUNUNGAN": "Papua Pegunungan",
}


def normalize_text(value: object) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\ufeff", "").strip()
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_province_name(value: object) -> str:
    text = normalize_text(value)
    if not text:
        return text
    key = text.upper()
    if key in PROVINCE_ALIASES:
        return PROVINCE_ALIASES[key]
    return text.title()


def province_key(value: object) -> str:
    normalized = normalize_province_name(value)
    return re.sub(r"[^A-Z0-9]+", "", normalized.upper())


def province_region(province: str) -> str:
    name = normalize_province_name(province)
    if name in {"Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Jambi", "Sumatera Selatan", "Bengkulu", "Lampung", "Kepulauan Bangka Belitung", "Kepulauan Riau"}:
        return "Sumatera"
    if name in {"Jakarta Raya", "Jawa Barat", "Jawa Tengah", "Yogyakarta", "Jawa Timur", "Banten"}:
        return "Jawa"
    if name in {"Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur"}:
        return "Bali-Nusa Tenggara"
    if name.startswith("Kalimantan"):
        return "Kalimantan"
    if name.startswith("Sulawesi") or name == "Gorontalo":
        return "Sulawesi"
    if name.startswith("Maluku"):
        return "Maluku"
    if name.startswith("Papua"):
        return "Papua"
    return "Lainnya"
