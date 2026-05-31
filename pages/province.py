from __future__ import annotations

import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html

from components.figures import empty_figure, opportunity_sankey, province_compass, spending_rank_chart
from components.kpi_card import kpi_card, pct, rupiah
from components.layout import footer
from data_processing.loader import get_filtered_data, get_province_row, get_regression_models
from tokens import COLORS, GRAPH_CONFIG, TYPOGRAPHY


def layout(
    province: str | None = None,
    metric: str = "rokok_pct_of_gizi",
    region: str = "all",
) -> html.Div:
    df = get_filtered_data(metric, region)
    all_df = get_filtered_data("rokok_pct_of_gizi", "all")

    # Default to highest-risk province if none selected
    if province is None:
        active = all_df[~all_df["_greyed_out"]]
        province = (
            active.sort_values("stunting_pct", ascending=False).iloc[0]["province"]
            if not active.empty else all_df.iloc[0]["province"]
        )

    row = get_province_row(province)
    has_exp = bool(row.get("has_expenditure_data", False))

    # Rank among active provinces (by rokok_pct_of_gizi)
    active_all = all_df[all_df["has_expenditure_data"] == True].copy()
    if has_exp and "rokok_pct_of_gizi" in active_all.columns:
        ranked = active_all.sort_values("rokok_pct_of_gizi", ascending=False).reset_index(drop=True)
        rank_matches = ranked[ranked["province"] == row["province"]]
        rank_str = f"#{rank_matches.index[0] + 1}" if not rank_matches.empty else "—"
    else:
        rank_str = "—"

    # Badge
    _badge_style_base = {"fontFamily": TYPOGRAPHY["font_body"], "fontSize": "0.72rem", "fontWeight": "700", "padding": "4px 10px", "borderRadius": "4px"}
    if not has_exp:
        badge = dbc.Badge("Data pengeluaran tidak tersedia", style={**_badge_style_base, "backgroundColor": COLORS["border_hover"], "color": COLORS["text_secondary"]})
    elif pd.notna(row.get("rokok_pct_of_gizi")) and row["rokok_pct_of_gizi"] > 45:
        badge = dbc.Badge("Risiko Tinggi", style={**_badge_style_base, "backgroundColor": COLORS["tobacco_primary"], "color": COLORS["text_primary"]})
    elif pd.notna(row.get("rokok_pct_of_gizi")) and row["rokok_pct_of_gizi"] > 30:
        badge = dbc.Badge("Risiko Sedang", style={**_badge_style_base, "backgroundColor": COLORS["gold"], "color": COLORS["bg_header"]})
    else:
        badge = dbc.Badge("Risiko Rendah", style={**_badge_style_base, "backgroundColor": COLORS["gizi_primary"], "color": COLORS["bg_header"]})

    # ── Section C: KPIs ──────────────────────────────────────────────────────
    kpi_row1 = dbc.Row([
        dbc.Col(kpi_card(
            "Rokok/kapita",
            rupiah(row["rokok"]) if has_exp and pd.notna(row.get("rokok")) else "N/A",
            "per bulan", "tobacco_primary",
        ), md=3),
        dbc.Col(kpi_card(
            "Gizi total",
            rupiah(row["gizi_total"]) if has_exp and pd.notna(row.get("gizi_total")) else "N/A",
            "sayur, ikan, telur/susu, daging, buah", "gizi_primary",
        ), md=3),
        dbc.Col(kpi_card(
            "Rokok % Gizi",
            pct(row["rokok_pct_of_gizi"]) if has_exp and pd.notna(row.get("rokok_pct_of_gizi")) else "N/A",
            "relatif pengeluaran gizi", "gold",
        ), md=3),
        dbc.Col(kpi_card(
            "Protein/kapita",
            f"{row['protein_per_capita']:.1f} g" if has_exp and pd.notna(row.get("protein_per_capita")) else "N/A",
            "per hari",
        ), md=3),
    ], className="g-3")

    kpi_row2 = dbc.Row([
        dbc.Col(kpi_card(
            "Perokok Harian",
            pct(row["smoking_daily_pct"]) if pd.notna(row.get("smoking_daily_pct")) else "N/A",
            "umur 10+ (SKI 2023)", "tobacco_primary",
        ), md=3),
        dbc.Col(kpi_card(
            "Stunting Balita",
            pct(row["stunting_pct"]) if pd.notna(row.get("stunting_pct")) else "N/A",
            "0-59 bulan (SKI 2023)",
        ), md=3),
        dbc.Col(kpi_card(
            "Mantan Perokok",
            pct(row["ex_smoker_pct"]) if pd.notna(row.get("ex_smoker_pct")) else "N/A",
            "umur 10+ (SKI 2023)",
        ), md=3),
        dbc.Col(kpi_card(
            "Rank Nasional",
            rank_str,
            "berdasarkan rokok % gizi",
        ), md=3),
    ], className="g-3 mt-1")

    # ── Section D: Charts ────────────────────────────────────────────────────
    if has_exp:
        chart_section = dbc.Row([
            dbc.Col(
                [
                    html.Div("Struktur pengeluaran", className="section-kicker"),
                    html.P(
                        "Leaderboard komponen belanja menunjukkan posisi rokok tanpa dekorasi berlebihan.",
                        style={"color": COLORS["text_secondary"], "fontSize": "0.82rem", "marginBottom": "4px"},
                    ),
                    dcc.Graph(figure=spending_rank_chart(row), config=GRAPH_CONFIG),
                ],
                lg=5,
            ),
            dbc.Col(
                [
                    html.Div("Posisi provinsi", className="section-kicker"),
                    html.P(
                        "Kompas kuadran menandai posisi provinsi terhadap rata-rata rokok/gizi dan protein.",
                        style={"color": COLORS["text_secondary"], "fontSize": "0.82rem", "marginBottom": "4px"},
                    ),
                    dcc.Graph(figure=province_compass(all_df, row["province"]), config=GRAPH_CONFIG),
                ],
                lg=7,
            ),
        ], className="g-3 mt-2")
    else:
        chart_section = dbc.Alert(
            "Data pengeluaran pangan tidak tersedia untuk provinsi ini. "
            "Provinsi ini adalah hasil pemekaran Papua (2022) yang belum tercakup dalam data pengeluaran SUSENAS.",
            color="secondary",
            className="mt-3",
        )

    # ── Section E: Policy Simulator ──────────────────────────────────────────
    if has_exp and pd.notna(row.get("rokok")):
        models = get_regression_models()
        rokok_val = float(row["rokok"])
        r2_stunt = models.get("stunting", {}).get("r2", 0)
        n_obs = models.get("n_obs", 0)

        policy_section = html.Div([
            html.Hr(style={"borderColor": "#2E2E2E", "margin": "28px 0 16px"}),
            html.Div("Simulasi Kebijakan", className="section-kicker"),
            html.P(
                "Geser slider untuk mengeksplorasi skenario realokasi pengeluaran rokok ke gizi total.",
                style={"color": COLORS["text_secondary"], "fontSize": "0.85rem"},
            ),
            dcc.Slider(
                id="rokok-slider",
                min=0,
                max=int(rokok_val * 2.5),
                step=500,
                value=rokok_val,
                marks={
                    0: {"label": "Rp 0", "style": {"color": COLORS["text_secondary"]}},
                    int(rokok_val): {"label": "Saat ini", "style": {"color": COLORS["gold"]}},
                },
                tooltip={"placement": "bottom", "always_visible": True},
            ),
            html.Div(id="pred-protein", style={"display": "none"}),
            dbc.Row([
                dbc.Col(html.Div([
                    html.P("Estimasi Stunting", className="kpi-label"),
                    html.H2(id="pred-stunting", children="—",
                            style={"color": COLORS["tobacco_primary"], "fontFamily": TYPOGRAPHY["font_display"]}),
                    html.P("balita % (asosiasi)", className="kpi-subtitle"),
                ], className="kpi-card"), md=4),
                dbc.Col(html.Div([
                    html.P("Dana Dihemat", className="kpi-label"),
                    html.H2(id="savings-card", children="—",
                            style={"color": COLORS["gold"], "fontFamily": TYPOGRAPHY["font_display"]}),
                    html.P("per kapita per bulan", className="kpi-subtitle"),
                ], className="kpi-card"), md=4),
                dbc.Col(html.Div([
                    html.P("Setara dengan", className="kpi-label"),
                    html.H3(id="equiv-card", children="—",
                            style={"color": COLORS["gizi_primary"], "fontSize": "1rem"}),
                    html.P("estimasi konversi", className="kpi-subtitle"),
                ], className="kpi-card"), md=4),
            ], className="g-3 mt-3"),
            dbc.Row([
                dbc.Col([
                    html.Div("Aliran dana dihemat", className="section-kicker"),
                    html.P(
                        "Sankey ini baru bergerak ketika slider diturunkan dari posisi 'Saat ini'.",
                        style={"color": COLORS["text_secondary"], "fontSize": "0.82rem", "marginBottom": "4px"},
                    ),
                    dbc.Row([
                        dbc.Col(
                            dcc.Graph(
                                id="opportunity-sankey",
                                figure=opportunity_sankey(row, amount=0),
                                config=GRAPH_CONFIG,
                            ),
                            lg=10,
                        ),
                        dbc.Col(
                            html.Div([
                                html.P("Strategi alokasi", className="kpi-label"),
                                html.Div([
                                    dcc.Slider(
                                        id="allocation-mode",
                                        min=0,
                                        max=3,
                                        step=None,
                                        value=0,
                                        vertical=True,
                                        verticalHeight=230,
                                        marks={
                                            0: {"label": "Komposisi", "style": {"color": COLORS["text_secondary"], "fontSize": "0.75rem"}},
                                            1: {"label": "Rata", "style": {"color": COLORS["text_secondary"], "fontSize": "0.75rem"}},
                                            2: {"label": "Protein", "style": {"color": COLORS["text_secondary"], "fontSize": "0.75rem"}},
                                            3: {"label": "Serat", "style": {"color": COLORS["text_secondary"], "fontSize": "0.75rem"}},
                                        },
                                        tooltip={"placement": "right"},
                                        className="allocation-vertical-slider",
                                    ),
                                ], className="allocation-control"),
                                html.Div([
                                    html.P("Serat — sayur & buah", className="allocation-legend-item"),
                                    html.P("Protein — ikan, telur, daging", className="allocation-legend-item"),
                                    html.P("Rata — bagi sama besar", className="allocation-legend-item"),
                                    html.P("Komposisi — pola belanja provinsi", className="allocation-legend-item"),
                                ], style={"marginTop": "14px"}),
                            ], className="kpi-card allocation-card"),
                            lg=2,
                        ),
                    ], className="g-3"),
                ], lg=12),
            ], className="g-3 mt-3"),
            html.P(
                f"Estimasi berdasarkan regresi linear gizi total lintas {n_obs} provinsi. "
                f"Stunting R²={r2_stunt:.2f}. "
                "Ini adalah asosiasi statistik, bukan prediksi kausal.",
                style={"color": COLORS["text_muted"], "fontSize": "0.78rem", "marginTop": "12px"},
            ),
        ], className="mt-2")
    else:
        # Placeholder slider IDs so callbacks don't fail (hidden)
        policy_section = html.Div([
            html.Div(dcc.Slider(id="rokok-slider", min=0, max=1, value=0, marks={}, disabled=True),
                     style={"display": "none"}),
            html.Div(id="pred-stunting", style={"display": "none"}),
            html.Div(id="pred-protein", style={"display": "none"}),
            html.Div(id="savings-card", style={"display": "none"}),
            html.Div(id="equiv-card", style={"display": "none"}),
            html.Div(dcc.Slider(id="allocation-mode", min=0, max=3, step=None, value=0),
                     style={"display": "none"}),
            html.Div(dcc.Graph(id="opportunity-sankey", figure=empty_figure("Data pengeluaran tidak tersedia")),
                     style={"display": "none"}),
            dbc.Alert(
                "Simulasi kebijakan tidak tersedia karena data pengeluaran rokok provinsi ini tidak tersedia.",
                color="secondary", className="mt-3",
            ),
        ])

    return html.Div([
        # ── Back button + Header ─────────────────────────────────────────────
        dbc.Row([
            dbc.Col(
                html.A("← Kembali ke Indonesia", href="/",
                       style={"color": COLORS["text_secondary"], "fontSize": "0.85rem", "textDecoration": "none"}),
                width="auto",
            ),
        ], className="mb-2"),
        html.Div(
            [
                html.H2(row["province"], className="page-heading", style={"marginRight": "12px"}),
                badge,
                html.Span(
                    f"• {row.get('region', '—')}",
                    style={"color": COLORS["text_secondary"], "fontSize": "0.85rem", "marginLeft": "10px"},
                ),
            ],
            style={"display": "flex", "alignItems": "center", "flexWrap": "wrap", "gap": "4px", "marginBottom": "16px"},
        ),

        # Section C
        kpi_row1,
        kpi_row2,

        # Section D
        chart_section,

        # Section E
        policy_section,

        footer(),
    ])
