from __future__ import annotations

import importlib.util
import pkgutil
from urllib.parse import parse_qs, quote_plus, urlencode, urlparse

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, no_update

from components.layout import app_shell
from data_processing.loader import (
    BUTTERFLY_DIMENSION_OPTIONS,
    METRIC_OPTIONS,
    REGION_OPTIONS,
    get_butterfly_data,
    get_filtered_data,
    get_regression_models,
    get_province_row,
    load_master_profile,
)
from data_processing.normalize import normalize_province_name
from components.figures import (
    butterfly_chart,
    characteristic_dual_axis,
    make_indonesia_map,
    opportunity_sankey,
    plate_donut,
    ranking_bar,
)
from components.kpi_card import kpi_card, pct, rupiah
from pages import home, province

if not hasattr(pkgutil, "find_loader"):
    pkgutil.find_loader = importlib.util.find_spec

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Rokok Nomor Satu, Gizi Lain Waktu",
)
server = app.server


def global_controls() -> dbc.Row:
    return dbc.Row(
        [
            dbc.Col(
                dcc.Dropdown(
                    id="metric-selector",
                    options=METRIC_OPTIONS,
                    value="rokok_pct_of_gizi",
                    clearable=False,
                ),
                md=5,
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="region-filter",
                    options=REGION_OPTIONS,
                    value="all",
                    clearable=False,
                ),
                md=4,
            ),
        ],
        className="global-controls g-2",
    )


app.layout = app_shell(html.Div([global_controls(), html.Div(id="page-content")]))


def selected_from_search(search: str | None) -> str | None:
    if not search:
        return None
    parsed = parse_qs(search.lstrip("?"))
    value = parsed.get("province", [None])[0]
    return normalize_province_name(value.replace("+", " ")) if value else None


# ── Route callback ────────────────────────────────────────────────────────────

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    Input("url", "search"),
    Input("metric-selector", "value"),
    Input("region-filter", "value"),
)
def route(pathname: str | None, search: str | None, metric: str, region: str):
    selected = selected_from_search(search)
    if pathname == "/province":
        return province.layout(selected, metric, region)
    return home.layout(metric, region)


# ── Map click → navigate to /province ────────────────────────────────────────

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
    return "/province", "?" + urlencode(
        {k: v[0] for k, v in query.items()}, quote_via=quote_plus
    )


# ── Butterfly chart callback ──────────────────────────────────────────────────

@app.callback(
    Output("dual-axis-chart", "figure"),
    Output("butterfly-chart", "figure"),
    Input("butterfly-dimension", "value"),
)
def update_butterfly(dimension: str):
    df = get_butterfly_data(dimension or "gender")
    return characteristic_dual_axis(df, dimension or "gender"), butterfly_chart(df)


# ── Policy slider init (set range + default from province row) ────────────────

@app.callback(
    Output("rokok-slider", "min"),
    Output("rokok-slider", "max"),
    Output("rokok-slider", "value"),
    Output("rokok-slider", "marks"),
    Input("url", "search"),
)
def init_slider(search: str | None):
    selected = selected_from_search(search)
    row = get_province_row(selected or "")
    import pandas as pd
    rokok_val = float(row["rokok"]) if pd.notna(row.get("rokok")) else 80_000
    max_val = rokok_val * 2.5
    marks = {
        0: {"label": "Rp 0", "style": {"color": "#A0A0A0"}},
        int(rokok_val): {"label": "Saat ini", "style": {"color": "#D4A017"}},
    }
    return 0, int(max_val), rokok_val, marks


# ── Policy slider update → prediction cards ───────────────────────────────────

@app.callback(
    Output("pred-stunting", "children"),
    Output("pred-protein", "children"),
    Output("savings-card", "children"),
    Output("equiv-card", "children"),
    Output("opportunity-sankey", "figure"),
    Input("rokok-slider", "value"),
    Input("allocation-mode", "value"),
    State("url", "search"),
)
def update_policy(slider_val: float, allocation_mode: int, search: str | None):
    import pandas as pd
    if slider_val is None:
        return "—", "—", "—", "—", opportunity_sankey(pd.Series(dtype="object"), amount=0)
    selected = selected_from_search(search)
    row = get_province_row(selected or "")
    models = get_regression_models()

    stunting_m = models.get("stunting", {})
    protein_m = models.get("protein", {})

    savings = (float(row["rokok"]) if pd.notna(row.get("rokok")) else slider_val) - slider_val
    current_gizi = float(row["gizi_total"]) if pd.notna(row.get("gizi_total")) else 0
    adjusted_gizi = max(0, current_gizi + savings)
    pred_stunting = stunting_m.get("coef", 0) * adjusted_gizi + stunting_m.get("intercept", 0)
    pred_protein = protein_m.get("coef", 0) * adjusted_gizi + protein_m.get("intercept", 0)
    equiv_telur = max(0, savings) / 2_000
    equiv_ikan = max(0, savings) / 8_000
    return (
        f"{pred_stunting:.1f}%",
        f"{pred_protein:.1f} g/hari",
        rupiah(savings),
        f"{equiv_telur:,.0f} butir telur / {equiv_ikan:,.0f} porsi ikan",
        opportunity_sankey(row, amount=max(0, savings), allocation_mode=allocation_mode or 0),
    )


if __name__ == "__main__":
    app.run(debug=False)
