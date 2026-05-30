from __future__ import annotations

import importlib.util
import pkgutil
from urllib.parse import parse_qs, quote_plus, urlencode, urlparse

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, no_update

from components.layout import app_shell
from data_processing.normalize import normalize_province_name
from pages import causes, home, policy, province
from tokens import COLORS

if not hasattr(pkgutil, "find_loader"):
    pkgutil.find_loader = importlib.util.find_spec

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Rokok Nomor Satu, Gizi Lain Waktu",
)
server = app.server


def controls() -> dbc.Row:
    return dbc.Row(
        [
            dbc.Col(
                dcc.Dropdown(
                    id="area-filter",
                    options=[
                        {"label": "Total", "value": "total"},
                        {"label": "Perkotaan", "value": "urban"},
                        {"label": "Perdesaan", "value": "rural"},
                    ],
                    value="total",
                    clearable=False,
                ),
                md=3,
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="map-mode",
                    options=[
                        {"label": "Auto map", "value": "auto"},
                        {"label": "Boundary", "value": "choropleth"},
                        {"label": "Point fallback", "value": "point"},
                    ],
                    value="auto",
                    clearable=False,
                ),
                md=3,
            ),
        ],
        className="global-controls g-2",
    )


app.layout = app_shell(html.Div([controls(), html.Div(id="page-content")]))


def selected_from_search(search: str | None) -> str | None:
    if not search:
        return None
    parsed = parse_qs(search.lstrip("?"))
    value = parsed.get("province", [None])[0]
    return normalize_province_name(value.replace("+", " ")) if value else None


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    Input("url", "search"),
    Input("area-filter", "value"),
    Input("map-mode", "value"),
)
def route(pathname: str | None, search: str | None, area: str, map_mode: str):
    selected = selected_from_search(search)
    if pathname == "/province":
        return province.layout(selected, area)
    if pathname == "/causes":
        return causes.layout(area)
    if pathname == "/policy":
        return policy.layout(area, map_mode)
    return home.layout(area, map_mode)


@app.callback(
    Output("url", "pathname"),
    Output("url", "search"),
    Input("national-map", "clickData"),
    State("url", "search"),
    prevent_initial_call=True,
)
def national_map_click(click_data, current_search):
    if not click_data:
        return no_update, no_update
    province_name = click_data["points"][0]["customdata"][0]
    query = parse_qs((current_search or "").lstrip("?"))
    query["province"] = [province_name]
    return "/province", "?" + urlencode({key: value[0] for key, value in query.items()}, quote_via=quote_plus)


if __name__ == "__main__":
    app.run(debug=False)
