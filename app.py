from __future__ import annotations

import importlib.util
import pkgutil
from urllib.parse import parse_qs, quote_plus, urlencode, urlparse

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, no_update

from components.layout import app_shell
from tokens import COLORS
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


app.layout = app_shell(html.Div([
    dcc.Store(id="donut-store"),
    html.Div(id="donut-animate-dummy", style={"display": "none"}),
    html.Div(global_controls(), id="global-controls-wrapper"),
    html.Div(id="page-content"),
]))


def selected_from_search(search: str | None) -> str | None:
    if not search:
        return None
    parsed = parse_qs(search.lstrip("?"))
    value = parsed.get("province", [None])[0]
    return normalize_province_name(value.replace("+", " ")) if value else None


# ── Route callback ────────────────────────────────────────────────────────────

@app.callback(
    Output("page-content", "children"),
    Output("global-controls-wrapper", "style"),
    Output("nav-home", "className"),
    Output("nav-province", "className"),
    Input("url", "pathname"),
    Input("url", "search"),
    State("metric-selector", "value"),
    State("region-filter", "value"),
)
def route(pathname: str | None, search: str | None, metric: str, region: str):
    selected = selected_from_search(search)
    on_province = pathname == "/province"
    base = "header-nav-link"
    active = base + " active"
    hide = {"display": "none"}
    show = {}
    if on_province:
        return province.layout(selected, metric, region), hide, base, active
    return home.layout(metric, region), show, active, base


# ── Home chart updates on filter change (preserve component → enable animation) ─

@app.callback(
    Output("home-kpi-row", "children"),
    Input("metric-selector", "value"),
    Input("region-filter", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def update_home_kpis(metric: str, region: str, pathname: str | None):
    if pathname == "/province":
        return no_update
    return home._build_kpi_row(metric, region)


@app.callback(
    Output("home-narrative", "children"),
    Input("metric-selector", "value"),
    Input("region-filter", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def update_home_narrative(metric: str, region: str, pathname: str | None):
    if pathname == "/province":
        return no_update
    return home._build_narrative(metric, region)


@app.callback(
    Output("national-map", "figure"),
    Input("metric-selector", "value"),
    Input("region-filter", "value"),
    prevent_initial_call=True,
)
def update_map(metric: str, region: str):
    df = get_filtered_data(metric, region)
    return make_indonesia_map(df, metric, region)


@app.callback(
    Output("donut-store", "data"),
    Input("metric-selector", "value"),
    Input("region-filter", "value"),
    prevent_initial_call=True,
)
def update_donut_store(metric: str, region: str):
    df = get_filtered_data(metric, region)
    return plate_donut(df)


app.clientside_callback(
    """
    function(figureData) {
        if (!figureData) return window.dash_clientside.no_update;
        var wrapper = document.getElementById('plate-donut');
        if (!wrapper) return window.dash_clientside.no_update;
        var el = wrapper.querySelector('.js-plotly-plot');
        if (!el) return window.dash_clientside.no_update;
        el.style.transition = 'opacity 0.22s ease';
        el.style.opacity = '0';
        setTimeout(function() {
            Plotly.react(el, figureData.data, figureData.layout);
            el.style.opacity = '1';
        }, 240);
        return window.dash_clientside.no_update;
    }
    """,
    Output("donut-animate-dummy", "children"),
    Input("donut-store", "data"),
)


@app.callback(
    Output("ranking-bar", "figure"),
    Input("metric-selector", "value"),
    Input("region-filter", "value"),
    prevent_initial_call=True,
)
def update_ranking(metric: str, region: str):
    import pandas as pd
    df = get_filtered_data(metric, region)
    df_nat = get_filtered_data(metric, "all")
    nat_active = df_nat[~df_nat["_greyed_out"]] if "_greyed_out" in df_nat.columns else df_nat
    national_avg = float(nat_active[metric].mean()) if metric in nat_active.columns and nat_active[metric].notna().any() else None
    fig = ranking_bar(df, metric, national_avg=national_avg, region=region)
    fig.update_layout(uirevision=f"{metric}-{region}")
    return fig


# ── Chart clicks → navigate to /province ─────────────────────────────────────

def _navigate_to_province(province_name: str, current_search: str | None):
    query = parse_qs((current_search or "").lstrip("?"))
    query["province"] = [province_name]
    return "/province", "?" + urlencode(
        {k: v[0] for k, v in query.items()}, quote_via=quote_plus
    )


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
    return _navigate_to_province(province_name, current_search)


@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("url", "search", allow_duplicate=True),
    Input("ranking-bar", "clickData"),
    State("url", "search"),
    prevent_initial_call=True,
)
def ranking_bar_click(click_data, current_search):
    if not click_data:
        return no_update, no_update
    province_name = click_data["points"][0]["customdata"][0]
    return _navigate_to_province(province_name, current_search)


@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("url", "search", allow_duplicate=True),
    Input("province-compass", "clickData"),
    State("url", "search"),
    prevent_initial_call=True,
)
def compass_click(click_data, current_search):
    if not click_data:
        return no_update, no_update
    province_name = click_data["points"][0]["customdata"][0]
    return _navigate_to_province(province_name, current_search)


# ── Butterfly chart callback ──────────────────────────────────────────────────

@app.callback(
    Output("butterfly-chart", "figure"),
    Input("butterfly-dimension", "value"),
    prevent_initial_call=True,
)
def update_butterfly(dimension: str):
    df = get_butterfly_data(dimension or "pendidikan")
    fig = butterfly_chart(df)
    fig.update_layout(uirevision=dimension or "pendidikan")
    return fig


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
        0: {"label": "Rp 0", "style": {"color": COLORS["text_secondary"]}},
        int(rokok_val): {"label": "Saat ini", "style": {"color": COLORS["gold"]}},
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
        return "N/A", "N/A", "N/A", "N/A", opportunity_sankey(pd.Series(dtype="object"), amount=0)
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
