from __future__ import annotations

import pandas as pd

from data_processing.normalize import normalize_province_name


def standardize_province_column(df: pd.DataFrame) -> pd.DataFrame:
    if "province" not in df.columns:
        return df
    result = df.copy()
    result["province"] = result["province"].map(normalize_province_name)
    return result
