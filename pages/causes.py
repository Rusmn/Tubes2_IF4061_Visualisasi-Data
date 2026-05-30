from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html

from components.figures import metric_bar, metric_scatter, price_lines, scatter_quadrant
from components.layout import footer
from data_processing.loader import get_area_profile, read_csv


def layout(area: str = "total") -> html.Div:
    df = get_area_profile(area)
    price = read_csv("indeks_harga_tahunan_by_province.csv") if (read_csv.cache_info().currsize >= 0) else None
    if price is None or price.empty:
        price = read_csv("indeks_harga_tahunan.csv")
    filtered_price = price[price["sub_group"].astype(str).str.contains("rokok|telur|ikan|sayur|susu", case=False, na=False)]
    return html.Div(
        [
            html.H2("Cause Explorer", className="page-heading"),
            dbc.Tabs(
                [
                    dbc.Tab(
                        dcc.Graph(figure=scatter_quadrant(df), config={"displaylogo": False}),
                        label="Ekonomi",
                    ),
                    dbc.Tab(
                        html.Div(
                            [
                                dcc.Graph(
                                    figure=metric_scatter(
                                        df,
                                        "rokok_pct_of_gizi",
                                        "smoking_10plus_current_pct",
                                        "Rokok % dari gizi",
                                        "Perokok umur 10+ (%)",
                                    ),
                                    config={"displaylogo": False},
                                ),
                                dcc.Graph(
                                    figure=metric_bar(df, "cigarettes_per_day", "Batang rokok per hari", high_is_risk=True),
                                    config={"displaylogo": False},
                                ),
                            ]
                        ),
                        label="SKI Rokok",
                    ),
                    dbc.Tab(
                        html.Div(
                            [
                                dcc.Graph(
                                    figure=metric_scatter(
                                        df,
                                        "rokok_pct_of_gizi",
                                        "stunting_0_59_total_pct",
                                        "Rokok % dari gizi",
                                        "Stunting balita (%)",
                                    ),
                                    config={"displaylogo": False},
                                ),
                                dcc.Graph(
                                    figure=metric_scatter(
                                        df,
                                        "smoking_10plus_current_pct",
                                        "milk_rare_pct",
                                        "Perokok umur 10+ (%)",
                                        "Konsumsi susu jarang (%)",
                                    ),
                                    config={"displaylogo": False},
                                ),
                            ]
                        ),
                        label="SKI Gizi",
                    ),
                    dbc.Tab(
                        dcc.Graph(figure=price_lines(filtered_price), config={"displaylogo": False}),
                        label="Harga",
                    ),
                    dbc.Tab(
                        dcc.Graph(
                            figure=scatter_quadrant(df.assign(rokok_pct_of_gizi=df["internet_pct"]), None),
                            config={"displaylogo": False},
                        ),
                        label="Digital",
                    ),
                ],
                className="mt-2",
            ),
            html.Div(
                [
                    html.H3("Catatan pembacaan"),
                    html.P(
                        "Tab ini dipakai untuk membandingkan lensa ekonomi, harga, dan digital. Pola yang terlihat "
                        "adalah asosiasi antar indikator provinsi. Tabel SKI yang dipakai mencakup prevalensi merokok, "
                        "batang rokok, harga rokok, stunting, dan pola konsumsi ikan, telur, serta susu."
                    ),
                ],
                className="narrative-card mt-3",
            ),
            footer(),
        ]
    )
