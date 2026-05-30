from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html

from components.figures import scatter_quadrant, waterfall
from components.kpi_card import kpi_card, pct, rupiah
from components.layout import footer
from data_processing.loader import get_area_profile, get_province_profile


def layout(province: str | None = None, area: str = "total") -> html.Div:
    df = get_area_profile(area)
    selected = province or df.sort_values("rokok_pct_of_gizi", ascending=False).iloc[0]["province"]
    row = get_province_profile(selected, area)
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(html.H2(row["province"], className="page-heading"), md=5),
                    dbc.Col(kpi_card("Rank rokok", f"#{int(row['rokok_rank'])}", "peringkat nasional"), md=2),
                    dbc.Col(kpi_card("Rokok/kapita", rupiah(row["rokok"]), "per bulan", "tobacco_primary"), md=2),
                    dbc.Col(kpi_card("Rokok/Gizi", pct(row["rokok_pct_of_gizi"]), "relatif gizi", "gold"), md=3),
                ],
                className="g-3",
            ),
            dbc.Row(
                [
                    dbc.Col(kpi_card("Gizi total", rupiah(row["gizi_total"]), "sayur, ikan, telur/susu, daging, buah", "gizi_primary"), md=3),
                    dbc.Col(kpi_card("Protein", f"{row['protein_per_capita']:.1f} g", "per kapita per hari", "gizi_teal"), md=3),
                    dbc.Col(kpi_card("Perokok 10+", pct(row["smoking_10plus_current_pct"]), "SKI 2023", "tobacco_primary"), md=3),
                    dbc.Col(kpi_card("Stunting balita", pct(row["stunting_0_59_total_pct"]), "SKI 2023"), md=3),
                ],
                className="g-3 mt-1",
            ),
            dbc.Row(
                [
                    dbc.Col(kpi_card("Batang/hari", f"{row['cigarettes_per_day']:.1f}", "rata-rata perokok harian"), md=3),
                    dbc.Col(kpi_card("Harga/bungkus", rupiah(row["cigarette_pack_price_rupiah"]), "SKI 2023"), md=3),
                    dbc.Col(kpi_card("Ikan harian", pct(row["fish_daily_pct"]), "umur 5+"), md=3),
                    dbc.Col(kpi_card("Susu jarang", pct(row["milk_rare_pct"]), "umur 5+"), md=3),
                ],
                className="g-3 mt-1",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=waterfall(row), config={"displaylogo": False}), lg=5),
                    dbc.Col(dcc.Graph(figure=scatter_quadrant(df, row["province"]), config={"displaylogo": False}), lg=7),
                ],
                className="g-3 mt-2",
            ),
            dbc.Row(
                dbc.Col(
                    html.Div(
                        [
                            html.H3("What-if sederhana"),
                            html.P(
                                f"Jika 25% belanja rokok di {row['province']} dialihkan, nilainya sekitar "
                                f"{rupiah(row['rokok'] * 0.25)} per kapita per bulan. Nilai ini setara dengan "
                                f"{row['rokok'] * 0.25 / 2000:,.0f} butir telur atau "
                                f"{row['rokok'] * 0.25 / 8000:,.0f} porsi ikan 100g."
                            ),
                            html.P(
                                f"SKI 2023 memberi konteks tambahan: perokok umur 10+ tercatat "
                                f"{row['smoking_10plus_current_pct']:.1f}%, rata-rata {row['cigarettes_per_day']:.1f} "
                                f"batang per hari pada perokok harian, sementara konsumsi ikan harian "
                                f"{row['fish_daily_pct']:.1f}% dan konsumsi susu jarang {row['milk_rare_pct']:.1f}%."
                            ),
                            html.P(
                                "Simulasi ini hanya membaca peluang realokasi pengeluaran. Data tidak menyatakan hubungan sebab-akibat langsung."
                            ),
                        ],
                        className="narrative-card",
                    )
                ),
                className="mt-2",
            ),
            footer(),
        ]
    )
