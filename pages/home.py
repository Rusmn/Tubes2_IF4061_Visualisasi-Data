from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html

from components.figures import make_indonesia_map, plate_donut, ranking_bar
from components.kpi_card import kpi_card, pct, rupiah
from components.layout import coverage_panel, footer
from data_processing.loader import coverage_status, get_area_profile


def layout(area: str = "total", map_mode: str = "auto") -> html.Div:
    df = get_area_profile(area)
    all_provinces = df["province"].nunique()
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(kpi_card("Provinsi terbaca", f"{all_provinces}/38", "target validasi nasional"), md=2),
                    dbc.Col(kpi_card("Rokok rata-rata", rupiah(df["rokok"].mean()), "per kapita per bulan", "tobacco_primary"), md=2),
                    dbc.Col(kpi_card("Gizi rata-rata", rupiah(df["gizi_total"].mean()), "lima komponen gizi", "gizi_primary"), md=2),
                    dbc.Col(kpi_card("Rokok/Gizi", pct(df["rokok_pct_of_gizi"].mean()), "rata-rata provinsi", "gold"), md=2),
                    dbc.Col(kpi_card("Perokok 10+", pct(df["smoking_10plus_current_pct"].mean()), "SKI 2023", "tobacco_primary"), md=2),
                    dbc.Col(kpi_card("Stunting balita", pct(df["stunting_0_59_total_pct"].mean()), "SKI 2023"), md=2),
                ],
                className="g-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div("Peta nasional", className="section-kicker"),
                            dcc.Graph(id="national-map", figure=make_indonesia_map(df, mode=map_mode), config={"displaylogo": False}),
                        ],
                        lg=8,
                    ),
                    dbc.Col(
                        [
                            html.Div("Piring pengeluaran", className="section-kicker"),
                            dcc.Graph(figure=plate_donut(df), config={"displaylogo": False}),
                        ],
                        lg=4,
                    ),
                ],
                className="g-3 mt-2",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=ranking_bar(df), config={"displaylogo": False}), lg=7),
                    dbc.Col(
                        html.Div(
                            [
                                html.H3("Insight nasional"),
                                html.P(
                                    "Rasio rokok terhadap gizi tersebar luas lintas provinsi. Peta otomatis memakai boundary "
                                    "ketika semua 38 provinsi match; jika tidak, dashboard berpindah ke bubble map agar "
                                    "tidak ada provinsi yang hilang."
                                ),
                                html.P(
                                    f"SKI 2023 menambah konteks kesehatan: rata-rata perokok umur 10+ sekitar "
                                    f"{df['smoking_10plus_current_pct'].mean():.1f}%, konsumsi ikan harian "
                                    f"{df['fish_daily_pct'].mean():.1f}%, dan konsumsi susu jarang mencapai "
                                    f"{df['milk_rare_pct'].mean():.1f}% lintas provinsi."
                                ),
                                html.P(
                                    "Narasi ini menggunakan bahasa asosiasi. Angka-angka memberi konteks tekanan pengeluaran, "
                                    "bukan bukti sebab-akibat langsung."
                                ),
                                coverage_panel(coverage_status()),
                            ],
                            className="narrative-card",
                        ),
                        lg=5,
                    ),
                ],
                className="g-3 mt-2",
            ),
            footer(),
        ]
    )
