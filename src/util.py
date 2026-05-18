from __future__ import annotations

import math

import pandas as pd


def clean_name(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    text = text.strip().upper().replace(".", "").replace("-", " ")
    text = " ".join(text.split())
    swaps = {
        "D K I JAKARTA": "DKI JAKARTA",
        "DKI JAKARTA": "DKI JAKARTA",
        "D I YOGYAKARTA": "DI YOGYAKARTA",
        "DI YOGYAKARTA": "DI YOGYAKARTA",
        "KEP BABEL": "KEP BANGKA BELITUNG",
        "BANGKA BELITUNG": "KEP BANGKA BELITUNG",
        "KEPULAUAN BANGKA BELITUNG": "KEP BANGKA BELITUNG",
        "NUSATENGGARA BARAT": "NUSA TENGGARA BARAT",
        "NUSATENGGARA TIMUR": "NUSA TENGGARA TIMUR",
        "PAPUA BARAT DAYA": "PAPUA BARAT",
    }
    return swaps.get(text, text)


def num_col(series: pd.Series) -> pd.Series:
    text = series.astype(str).str.replace(",", ".", regex=False)
    text = text.str.replace(" ", "", regex=False).replace({"-": None, "nan": None})
    return pd.to_numeric(text, errors="coerce")


def rupiah(value: float) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"Rp{value:,.0f}".replace(",", ".")


def percent(value: float) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{value:.1f}%".replace(".", ",")


def compact(value: float) -> str:
    if value is None or pd.isna(value):
        return "-"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f} jt".replace(".", ",")
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f} rb".replace(".", ",")
    return f"{value:.0f}"


def safe_div(left: float, right: float) -> float:
    if right is None or pd.isna(right) or right == 0:
        return math.nan
    return left / right
