from __future__ import annotations

from components.figures import make_indonesia_map
from data_processing.loader import coverage_status, get_butterfly_data, get_filtered_data, get_regression_models, load_master_profile


def test_master_profile_has_38_provinces() -> None:
    df = load_master_profile()
    assert df["province"].nunique() == 38
    assert int(df["has_expenditure_data"].sum()) == 34


def test_stunting_uses_balita_table() -> None:
    df = load_master_profile()
    aceh = df[df["province"] == "Aceh"].iloc[0]
    assert aceh["stunting_pct"] == 20.3


def test_dim_province_has_38_provinces() -> None:
    status = coverage_status()
    assert status["province_count"] == 38


def test_map_keeps_all_provinces_in_choropleth_traces() -> None:
    df = get_filtered_data("rokok_pct_of_gizi", "all")
    fig = make_indonesia_map(df)
    assert all(trace.type == "choropleth" for trace in fig.data)
    assert sum(len(trace.locations) for trace in fig.data) == 38
    assert fig.layout.uirevision == "constant"


def test_butterfly_uses_balita_characteristics() -> None:
    df = get_butterfly_data("gender")
    laki = df[df["label"] == "Laki-laki"].iloc[0]
    assert laki["stunting_pct"] == 16.5


def test_regression_models_are_available() -> None:
    models = get_regression_models()
    assert models["n_obs"] == 34
    assert models["stunting"]["r2"] == 0.063
