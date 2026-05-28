from __future__ import annotations

import math
import re
import unicodedata
from pathlib import Path
from typing import Iterable

import pandas as pd


def clean_name(value: object) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    text = str(value).strip().upper()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace(".", "").replace("-", " ")
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    text = " ".join(text.split())
    swaps = {
        "D K I JAKARTA": "DKI JAKARTA",
        "DKI JAKARTA": "DKI JAKARTA",
        "DI ACEH": "ACEH",
        "DAERAH ISTIMEWA ACEH": "ACEH",
        "D I YOGYAKARTA": "DI YOGYAKARTA",
        "DAERAH ISTIMEWA YOGYAKARTA": "DI YOGYAKARTA",
        "YOGYAKARTA": "DI YOGYAKARTA",
        "KEP BABEL": "KEP BANGKA BELITUNG",
        "BANGKA BELITUNG": "KEP BANGKA BELITUNG",
        "KEPULAUAN BANGKA BELITUNG": "KEP BANGKA BELITUNG",
        "KEP RIAU": "KEP RIAU",
        "KEPULAUAN RIAU": "KEP RIAU",
        "NUSATENGGARA BARAT": "NUSA TENGGARA BARAT",
        "NUSATENGGARA TIMUR": "NUSA TENGGARA TIMUR",
    }
    return swaps.get(text, text)


def pretty_name(value: object) -> str:
    text = clean_name(value)
    if not text:
        return ""
    keep_upper = {"DKI", "DI"}
    fixes = {
        "KEP BANGKA BELITUNG": "Kep. Bangka Belitung",
        "KEP RIAU": "Kep. Riau",
        "DKI JAKARTA": "DKI Jakarta",
        "DI YOGYAKARTA": "DI Yogyakarta",
    }
    if text in fixes:
        return fixes[text]
    return " ".join(w if w in keep_upper else w.capitalize() for w in text.split())


def norm_col(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")


def find_col(df: pd.DataFrame, candidates: Iterable[str], required: bool = False) -> str | None:
    lut = {norm_col(c): c for c in df.columns}
    for cand in candidates:
        key = norm_col(cand)
        if key in lut:
            return lut[key]
    for cand in candidates:
        key = norm_col(cand)
        for k, original in lut.items():
            if key and (key in k or k in key):
                return original
    if required:
        raise KeyError(f"Tidak menemukan kolom. Kandidat: {list(candidates)}; kolom tersedia: {list(df.columns)}")
    return None


def num_col(series: pd.Series) -> pd.Series:
    text = series.astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    text = text.str.replace(" ", "", regex=False).replace({"-": None, "nan": None, "None": None})
    return pd.to_numeric(text, errors="coerce")


def rupiah(value: float | int | None, prefix: str = "Rp ") -> str:
    if value is None or pd.isna(value):
        return "—"
    return prefix + f"{float(value):,.0f}".replace(",", ".")


def percent(value: float | int | None, digits: int = 1) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):.{digits}f}%".replace(".", ",")


def compact(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "—"
    value = float(value)
    if abs(value) >= 1_000_000_000:
        return f"{value/1_000_000_000:.1f} M".replace(".", ",")
    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:.1f} jt".replace(".", ",")
    if abs(value) >= 1_000:
        return f"{value/1_000:.1f} rb".replace(".", ",")
    return f"{value:.0f}"


def safe_div(left: float, right: float) -> float:
    if right is None or pd.isna(right) or right == 0:
        return math.nan
    return float(left) / float(right)


def existing_path(*candidates: str | Path) -> Path | None:
    for candidate in candidates:
        p = Path(candidate)
        if p.exists():
            return p
    return None
