from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html

from tokens import COLORS


def app_shell(content: html.Div) -> html.Div:
    return html.Div(
        [
            dcc.Location(id="url", refresh=False),
            dcc.Store(
                id="global-store",
                storage_type="session",
                data={"selected_province": None, "selected_area": "total", "map_mode": "auto"},
            ),
            header(),
            html.Main(content, className="app-main"),
        ],
        style={"backgroundColor": COLORS["bg_app"], "minHeight": "100vh"},
    )


def header() -> dbc.Navbar:
    return dbc.Navbar(
        dbc.Container(
            [
                html.Div(
                    [
                        html.Div("Kelompok 9 - IF4061", className="eyebrow"),
                        html.H1("Rokok Nomor Satu, Gizi Lain Waktu", className="app-title"),
                    ]
                ),
            ],
            fluid=True,
        ),
        className="app-header",
        dark=True,
    )


def footer() -> html.P:
    return html.P(
        "Sumber data: BPS/SUSENAS 2024, SKI 2023 Kemenkes, BPS indikator ekonomi dan digital. "
        "Data menunjukkan asosiasi dan konteks, bukan hubungan sebab-akibat langsung.",
        className="source-footer",
    )


def coverage_panel(status: dict[str, object]) -> dbc.Alert:
    missing = status.get("missing_geometry") or []
    detail = "Semua provinsi match ke boundary." if not missing else "Fallback point: " + ", ".join(missing)
    return dbc.Alert(
        [
            html.Strong("Coverage status: "),
            f"{status.get('province_count', 0)} provinsi data, "
            f"{status.get('geo_match_count', 0)} match GeoJSON, "
            f"{status.get('fallback_point_count', 0)} fallback. ",
            html.Span(detail),
        ],
        color="dark",
        className="coverage-panel",
    )
