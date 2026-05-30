from __future__ import annotations

from components.figures import make_indonesia_map
from data_processing.loader import coverage_status, get_area_profile


def test_dim_province_has_38_provinces() -> None:
    status = coverage_status()
    assert status["province_count"] == 38


def test_auto_map_uses_boundary_when_complete() -> None:
    df = get_area_profile("total")
    fig = make_indonesia_map(df, mode="auto")
    assert fig.data[0].type == "choropleth"
    assert fig.layout.uirevision == "constant"


def test_point_fallback_keeps_all_provinces() -> None:
    df = get_area_profile("total")
    fig = make_indonesia_map(df, mode="point")
    assert fig.data[0].type == "scattergeo"
    assert len(fig.data[0].lat) == 38
    assert fig.layout.uirevision == "constant"


def test_ski_pdf_indicators_are_joined() -> None:
    df = get_area_profile("total")
    required = [
        "smoking_10plus_current_pct",
        "cigarettes_per_day",
        "cigarette_pack_price_rupiah",
        "smoking_start_10_14_pct",
        "fish_daily_pct",
        "egg_daily_pct",
        "milk_rare_pct",
        "ski_health_context_score",
    ]
    assert all(column in df.columns for column in required)
    assert df[required].notna().all().all()
