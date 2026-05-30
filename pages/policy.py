from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from components.figures import make_indonesia_map, priority_table, scatter_quadrant
from components.kpi_card import kpi_card, pct, rupiah
from components.layout import footer
from data_processing.loader import get_area_profile
from tokens import COLORS


def layout(area: str = "total", map_mode: str = "auto") -> html.Div:
    df = get_area_profile(area)
    opportunity = (df["rokok"] * df["population_thousands"] * 1000 * 12).sum()
    top = df.sort_values("policy_priority_score", ascending=False).iloc[0]
    return html.Div(
        [
            html.H2("Impact & Policy", className="page-heading"),
            dbc.Row(
                [
                    dbc.Col(kpi_card("Opportunity cost", rupiah(opportunity), "estimasi nasional per tahun", "gold"), md=4),
                    dbc.Col(kpi_card("Prioritas pertama", top["province"], pct(top["policy_priority_score"])), md=4),
                    dbc.Col(kpi_card("Protein rata-rata", f"{df['protein_per_capita'].mean():.1f} g", "per kapita per hari", "gizi_teal"), md=4),
                ],
                className="g-3",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=make_indonesia_map(df, "policy_priority_score", map_mode), config={"displaylogo": False}), lg=7),
                    dbc.Col(dcc.Graph(figure=scatter_quadrant(df), config={"displaylogo": False}), lg=5),
                ],
                className="g-3 mt-2",
            ),
            html.Div(
                [
                    html.H3("Ranking prioritas"),
                    dash_table.DataTable(
                        data=priority_table(df),
                        page_size=12,
                        style_as_list_view=True,
                        style_header={
                            "backgroundColor": COLORS["bg_card"],
                            "color": COLORS["text_primary"],
                            "border": f"1px solid {COLORS['border']}",
                        },
                        style_cell={
                            "backgroundColor": COLORS["bg_app"],
                            "color": COLORS["text_primary"],
                            "border": f"1px solid {COLORS['border']}",
                        },
                    ),
                ],
                className="table-panel mt-3",
            ),
            footer(),
        ]
    )
