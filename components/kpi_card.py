from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html

from tokens import COLORS, TYPOGRAPHY


def kpi_card(label: str, value: str, subtitle: str = "", accent: str = "gold") -> dbc.Card:
    accent_color = COLORS.get(accent, COLORS["gold"])
    return dbc.Card(
        dbc.CardBody(
            [
                html.P(label, className="kpi-label"),
                html.H2(value, style={"color": accent_color, "fontFamily": TYPOGRAPHY["font_display"]}),
                html.P(subtitle, className="kpi-subtitle"),
            ]
        ),
        className="kpi-card",
    )


def rupiah(value: float) -> str:
    return f"Rp {value:,.0f}".replace(",", ".")


def pct(value: float) -> str:
    return f"{value:.1f}%"
