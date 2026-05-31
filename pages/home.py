from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html

_INSIGHTS_PATH = Path(__file__).resolve().parents[1] / "data" / "insights.json"
_INSIGHTS: dict = json.loads(_INSIGHTS_PATH.read_text(encoding="utf-8-sig"))

from components.figures import (
    butterfly_chart,
    make_indonesia_map,
    plate_donut,
    ranking_bar,
)
from components.kpi_card import kpi_card, pct
from components.layout import footer
from tokens import COLORS
from data_processing.loader import (
    BUTTERFLY_DIMENSION_OPTIONS,
    get_butterfly_data,
    get_filtered_data,
    METRIC_OPTIONS,
)
from tokens import GRAPH_CONFIG


def _metric_label(metric_col: str) -> str:
    for opt in METRIC_OPTIONS:
        if opt["value"] == metric_col:
            return opt["label"]
    return metric_col.replace("_", " ")


def _build_narrative(metric: str, region: str) -> html.Div:
    key = f"{metric}|{region}"
    insight = _INSIGHTS.get(key, {})
    headline = insight.get("headline", "")
    detail = insight.get("detail", "")
    return html.Div([
        html.Div("Temuan", className="section-kicker"),
        html.P(headline, style={
            "color": COLORS["text_primary"],
            "fontSize": "1.15rem",
            "fontWeight": "600",
            "marginBottom": "12px",
            "lineHeight": "1.5",
        }),
        html.P(detail, style={
            "color": COLORS["text_secondary"],
            "fontSize": "0.95rem",
            "lineHeight": "1.7",
            "marginBottom": "14px",
        }),
        html.P("Klik provinsi di peta untuk simulasi pengeluaran rokok.",
               style={"color": COLORS["text_muted"], "fontSize": "0.82rem"}),
    ], className="narrative-card")


def _build_kpi_row(metric: str, region: str) -> dbc.Row:
    df = get_filtered_data(metric, region)
    active = df[~df["_greyed_out"]].copy()
    n_active = int(active["province"].nunique())
    n_total = int(df["province"].nunique())
    metric_avg = active[metric].mean() if not active.empty and metric in active.columns else float("nan")
    smoking_avg = active["smoking_daily_pct"].mean() if not active.empty else float("nan")
    stunting_avg = active["stunting_pct"].mean() if not active.empty else float("nan")
    top_province = "N/A"
    if not active.empty and metric in active.columns and active[metric].notna().any():
        top_province = active.sort_values(metric, ascending=False).iloc[0]["province"]
    metric_label = _metric_label(metric)
    region_label = "Indonesia" if region == "all" else region
    return dbc.Row([
        dbc.Col(kpi_card("Provinsi aktif", f"{n_active}/{n_total}", region_label), md=2),
        dbc.Col(kpi_card(metric_label[:28], f"{metric_avg:.1f}%" if pd.notna(metric_avg) else "N/A", "rata-rata", "gold"), md=3),
        dbc.Col(kpi_card("Perokok Harian", pct(smoking_avg) if pd.notna(smoking_avg) else "N/A", "SKI 2023 umur 10+", "tobacco_primary"), md=2),
        dbc.Col(kpi_card("Stunting Balita", pct(stunting_avg) if pd.notna(stunting_avg) else "N/A", "SKI 2023 umur 0-59 bulan", "warning"), md=2),
        dbc.Col(kpi_card("Tertinggi", top_province[:22], metric_label[:20]), md=3),
    ], className="g-3")


def layout(metric: str = "rokok_pct_of_gizi", region: str = "all") -> html.Div:
    df = get_filtered_data(metric, region)
    active = df[~df["_greyed_out"]].copy()

    top_province = "N/A"
    if not active.empty and metric in active.columns and active[metric].notna().any():
        top_province = active.sort_values(metric, ascending=False).iloc[0]["province"]

    df_nat = get_filtered_data(metric, "all")
    nat_active = df_nat[~df_nat["_greyed_out"]].copy()
    national_avg = float(nat_active[metric].mean()) if metric in nat_active.columns and nat_active[metric].notna().any() else None

    fig_map = make_indonesia_map(df, metric, region)
    fig_donut = plate_donut(df)
    fig_bar = ranking_bar(df, metric, national_avg=national_avg, region=region)
    fig_butterfly = butterfly_chart(get_butterfly_data("pendidikan"))

    narrative = html.Div(id="home-narrative", children=_build_narrative(metric, region))

    return html.Div(
        [
            html.Div(id="home-kpi-row", children=_build_kpi_row(metric, region)),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.Div("Peta nasional", className="section-kicker"),
                                dcc.Graph(id="national-map", figure=fig_map, config=GRAPH_CONFIG),
                            ],
                            className="chart-panel",
                        ),
                        lg=8,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.Div("Piring pengeluaran", className="section-kicker"),
                                dcc.Graph(id="plate-donut", figure=fig_donut, config=GRAPH_CONFIG),
                            ],
                            className="chart-panel",
                            style={"height": "100%"},
                        ),
                        style={"alignSelf": "stretch"},
                    ),
                ],
                className="g-3 mt-2",
                align="center",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            dcc.Graph(id="ranking-bar", figure=fig_bar, config=GRAPH_CONFIG),
                            className="chart-panel",
                        ),
                        lg=7,
                    ),
                    dbc.Col(narrative, lg=5, className="d-flex", style={"alignSelf": "stretch"}),
                ],
                className="g-3 mt-2",
                align="stretch",
            ),
            html.Hr(style={"borderColor": "#2E2E2E", "margin": "32px 0 20px"}),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div("Pola: Siapa yang paling rentan?", className="section-kicker"),
                            html.P(
                                "Karakteristik sosial-ekonomi yang berasosiasi dengan prevalensi merokok (kiri) "
                                "dan stunting balita (kanan). Data nasional SKI 2023.",
                                style={"color": COLORS["text_secondary"], "fontSize": "0.85rem", "marginBottom": "8px"},
                            ),
                        ],
                        md=8,
                    ),
                    dbc.Col(
                        [
                            dcc.Dropdown(
                                id="butterfly-dimension",
                                options=BUTTERFLY_DIMENSION_OPTIONS,
                                value="pendidikan",
                                clearable=False,
                                style={"marginTop": "6px"},
                            ),
                        ],
                        md=4,
                    ),
                ],
                className="g-2 align-items-center",
            ),
            html.Div(
                [
                    dcc.Graph(id="butterfly-chart", figure=fig_butterfly, config=GRAPH_CONFIG),
                    html.P(
                        "Sisi kiri: % perokok harian (umur 10+). "
                        "Sisi kanan: % gizi normal balita (TB/U, 0-59 bulan). "
                        "Makin jauh ke kanan = makin banyak yang bergizi normal.",
                        style={"color": COLORS["text_secondary"], "fontSize": "0.8rem", "marginTop": "6px"},
                    ),
                    html.P(
                        "*Dimensi 'Status Ekonomi': data gizi normal menggunakan sumber berbeda "
                        "(status gizi anak 5-12 tahun per kuintil ekonomi, SKI 2023), "
                        "bukan data balita 0-59 bulan.",
                        style={"color": COLORS["text_muted"], "fontSize": "0.75rem", "marginTop": "2px"},
                    ),
                ],
                className="chart-panel",
            ),
            footer(),
        ]
    )
