from __future__ import annotations

import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html

from components.figures import butterfly_chart, make_indonesia_map, plate_donut, ranking_bar
from components.kpi_card import kpi_card, pct
from components.layout import footer
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


def layout(metric: str = "rokok_pct_of_gizi", region: str = "all") -> html.Div:
    df = get_filtered_data(metric, region)
    active = df[~df["_greyed_out"]].copy()

    n_active = int(active["province"].nunique())
    n_total = int(df["province"].nunique())
    metric_avg = active[metric].mean() if not active.empty and metric in active.columns else float("nan")
    smoking_avg = active["smoking_daily_pct"].mean() if not active.empty else float("nan")
    stunting_avg = active["stunting_pct"].mean() if not active.empty else float("nan")

    top_province = "—"
    if not active.empty and metric in active.columns and active[metric].notna().any():
        top_province = active.sort_values(metric, ascending=False).iloc[0]["province"]

    metric_label = _metric_label(metric)
    region_label = "Indonesia" if region == "all" else region

    fig_map = make_indonesia_map(df, metric)
    fig_donut = plate_donut(df)
    fig_bar = ranking_bar(df, metric)
    fig_butterfly = butterfly_chart(get_butterfly_data("gender"))

    narrative = html.Div(
        [
            html.H3("Insight"),
            html.P(
                f"Menampilkan {n_active} dari {n_total} provinsi di wilayah {region_label}. "
                f"Rata-rata {metric_label}: "
                + (f"{metric_avg:.1f}%" if pd.notna(metric_avg) else "N/A")
                + "."
            ),
            html.P(
                f"Rata-rata perokok harian: {smoking_avg:.1f}% | "
                f"Rata-rata stunting balita: {stunting_avg:.1f}%."
            ),
            html.P(
                "Klik provinsi di peta untuk melihat detail dan simulasi kebijakan.",
                style={"color": "#8A8A8A", "fontSize": "0.85rem"},
            ),
        ],
        className="narrative-card",
    )

    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(kpi_card("Provinsi aktif", f"{n_active}/{n_total}", region_label), md=2),
                    dbc.Col(
                        kpi_card(
                            metric_label[:28],
                            f"{metric_avg:.1f}%" if pd.notna(metric_avg) else "N/A",
                            "rata-rata",
                            "gold",
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        kpi_card(
                            "Perokok Harian",
                            pct(smoking_avg) if pd.notna(smoking_avg) else "N/A",
                            "SKI 2023 umur 10+",
                            "tobacco_primary",
                        ),
                        md=2,
                    ),
                    dbc.Col(
                        kpi_card(
                            "Stunting Balita",
                            pct(stunting_avg) if pd.notna(stunting_avg) else "N/A",
                            "SKI 2023 umur 0-59 bulan",
                            "warning",
                        ),
                        md=2,
                    ),
                    dbc.Col(kpi_card("Tertinggi", top_province[:22], metric_label[:20]), md=3),
                ],
                className="g-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div("Peta nasional", className="section-kicker"),
                            dcc.Graph(id="national-map", figure=fig_map, config=GRAPH_CONFIG),
                        ],
                        lg=8,
                    ),
                    dbc.Col(
                        [
                            html.Div("Piring pengeluaran", className="section-kicker"),
                            dcc.Graph(figure=fig_donut, config=GRAPH_CONFIG),
                        ],
                        lg=4,
                    ),
                ],
                className="g-3 mt-2",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="ranking-bar", figure=fig_bar, config=GRAPH_CONFIG), lg=7),
                    dbc.Col(narrative, lg=5),
                ],
                className="g-3 mt-2",
            ),
            html.Hr(style={"borderColor": "#2E2E2E", "margin": "32px 0 20px"}),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div("Penyebab: Siapa yang paling terdampak?", className="section-kicker"),
                            html.P(
                                "Karakteristik sosial-ekonomi yang berasosiasi dengan prevalensi merokok (kiri) "
                                "dan stunting balita (kanan). Data nasional SKI 2023.",
                                style={"color": "#A0A0A0", "fontSize": "0.85rem", "marginBottom": "8px"},
                            ),
                        ],
                        md=8,
                    ),
                    dbc.Col(
                        [
                            dcc.Dropdown(
                                id="butterfly-dimension",
                                options=BUTTERFLY_DIMENSION_OPTIONS,
                                value="gender",
                                clearable=False,
                                style={"marginTop": "6px"},
                            ),
                        ],
                        md=4,
                    ),
                ],
                className="g-2 align-items-center",
            ),
            dcc.Graph(id="butterfly-chart", figure=fig_butterfly, config=GRAPH_CONFIG),
            html.Div(
                [
                    html.P(
                        "Sisi kiri menunjukkan % perokok harian, sisi kanan % stunting balita (0-59 bulan). "
                        "Untuk dimensi 'Status Ekonomi', data stunting per kelas ekonomi tidak tersedia di SKI 2023.",
                        style={"color": "#8A8A8A", "fontSize": "0.8rem"},
                    ),
                ],
                style={"marginTop": "8px"},
            ),
            footer(),
        ]
    )
