from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from tokens import COLORS, TYPOGRAPHY

ROOT = Path(__file__).resolve().parents[1]

GREYOUT_COLOR = "#2E2E2E"


def apply_layout(fig: go.Figure, height: int | None = None) -> go.Figure:
    fig.update_layout(
        paper_bgcolor=COLORS["bg_app"],
        plot_bgcolor=COLORS["bg_card"],
        font=dict(color=COLORS["text_primary"], family=TYPOGRAPHY["font_body"]),
        margin=dict(l=42, r=24, t=46, b=42),
        uirevision="constant",
        height=height,
    )
    return fig


def empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message, xref="paper", yref="paper", x=0.5, y=0.5,
        showarrow=False, font=dict(color=COLORS["text_muted"], size=14),
    )
    return apply_layout(fig, height=420)


def _province_customdata(df: pd.DataFrame) -> list:
    cols = ["province", "rokok", "gizi_total", "rokok_pct_of_gizi",
            "protein_per_capita", "smoking_daily_pct", "stunting_pct"]
    for c in cols:
        if c not in df.columns:
            df = df.copy()
            df[c] = None
    return df[cols].values


def _province_hover() -> str:
    return (
        "<b>%{customdata[0]}</b><br>"
        "Rokok/kapita: Rp %{customdata[1]:,.0f}<br>"
        "Gizi total: Rp %{customdata[2]:,.0f}<br>"
        "Rokok % dari gizi: %{customdata[3]:.1f}%<br>"
        "Perokok harian: %{customdata[5]:.1f}%<br>"
        "Stunting baduta: %{customdata[6]:.1f}%"
        "<extra></extra>"
    )


def _choro_scale_for_metric(metric_col: str) -> list:
    if metric_col == "stunting_pct":
        return COLORS["choro_protein_scale"]
    return COLORS["choro_scale"]


def make_indonesia_map(
    df: pd.DataFrame,
    metric_col: str = "rokok_pct_of_gizi",
    mode: str = "auto",
) -> go.Figure:
    if df.empty or metric_col not in df.columns:
        return empty_figure("Data peta tidak tersedia")

    geo_path = ROOT / "data" / "geo" / "indonesia_provinces.geojson"
    if not geo_path.exists():
        return empty_figure("GeoJSON tidak ditemukan")
    with geo_path.open(encoding="utf-8") as fh:
        geojson = json.load(fh)

    greyed = df.get("_greyed_out", pd.Series(False, index=df.index))
    df_active = df[~greyed].copy()
    df_grey = df[greyed].copy()

    customdata_active = _province_customdata(df_active)

    fig = go.Figure()

    # Grey provinces (region out-of-filter or no expenditure data)
    if not df_grey.empty:
        fig.add_trace(go.Choropleth(
            geojson=geojson,
            locations=df_grey["geo_feature_id"],
            featureidkey="properties.REGION_CODE",
            z=[0] * len(df_grey),
            colorscale=[[0, GREYOUT_COLOR], [1, GREYOUT_COLOR]],
            showscale=False,
            marker_line_color=COLORS["border"],
            marker_line_width=0.5,
            hoverinfo="skip",
            name="",
        ))

    # Active provinces (colored by metric)
    if not df_active.empty:
        fig.add_trace(go.Choropleth(
            geojson=geojson,
            locations=df_active["geo_feature_id"],
            featureidkey="properties.REGION_CODE",
            z=df_active[metric_col],
            colorscale=_choro_scale_for_metric(metric_col),
            marker_line_color=COLORS["border"],
            marker_line_width=0.5,
            customdata=customdata_active,
            hovertemplate=_province_hover(),
            colorbar=dict(
                bgcolor=COLORS["bg_card"],
                tickfont=dict(color=COLORS["text_secondary"]),
                title=dict(text=metric_col.replace("_", " "), font=dict(color=COLORS["text_secondary"])),
            ),
            name="",
        ))

    fig.update_geos(fitbounds="locations", visible=False, bgcolor=COLORS["bg_app"])
    fig.update_layout(clickmode="event+select")
    return apply_layout(fig, height=520)


def plate_donut(df: pd.DataFrame) -> go.Figure:
    active = df[~df.get("_greyed_out", pd.Series(False, index=df.index))].copy() if "_greyed_out" in df.columns else df
    columns = ["rokok", "sayur", "ikan", "telur_susu", "daging", "buah"]
    values = active[columns].sum()
    labels = ["Rokok", "Sayur", "Ikan", "Telur & Susu", "Daging", "Buah"]
    colors = [COLORS["tobacco_primary"], COLORS["sayur"], COLORS["ikan"],
               COLORS["telur"], COLORS["daging"], COLORS["buah"]]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.58,
        marker=dict(colors=colors, line=dict(color=COLORS["bg_app"], width=2)),
        hovertemplate="<b>%{label}</b><br>Rp %{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(showlegend=True)
    return apply_layout(fig, height=420)


def ranking_bar(df: pd.DataFrame, metric_col: str = "rokok_pct_of_gizi", limit: int = 10) -> go.Figure:
    active = df[~df.get("_greyed_out", pd.Series(False, index=df.index))].copy() if "_greyed_out" in df.columns else df
    data = active.dropna(subset=[metric_col]).sort_values(metric_col, ascending=False).head(limit).sort_values(metric_col)
    if data.empty:
        return empty_figure("Data tidak tersedia")
    customdata = _province_customdata(data)
    fig = go.Figure(go.Bar(
        x=data[metric_col], y=data["province"],
        orientation="h",
        marker_color=COLORS["tobacco_primary"],
        customdata=customdata,
        hovertemplate=_province_hover(),
    ))
    mean_val = active[metric_col].mean()
    if pd.notna(mean_val):
        fig.add_vline(x=mean_val, line_color=COLORS["gold"], line_dash="dot")
    fig.update_xaxes(gridcolor=COLORS["border"], title=metric_col.replace("_", " "))
    fig.update_yaxes(gridcolor=COLORS["bg_card"])
    return apply_layout(fig, height=420)


def scatter_quadrant(df: pd.DataFrame, selected: str | None = None) -> go.Figure:
    active = df[~df.get("_greyed_out", pd.Series(False, index=df.index))].copy() if "_greyed_out" in df.columns else df.copy()
    data = active.dropna(subset=["rokok_pct_of_gizi", "protein_per_capita"])
    if data.empty:
        return empty_figure("Data tidak tersedia")
    sizes = (data["population_thousands"].fillna(data["population_thousands"].median()).clip(lower=100) ** 0.5) / 4
    colors = [COLORS["gold"] if selected and p == selected else COLORS["tobacco_primary"] for p in data["province"]]
    customdata = _province_customdata(data)
    fig = go.Figure(go.Scatter(
        x=data["rokok_pct_of_gizi"], y=data["protein_per_capita"],
        mode="markers", text=data["province"],
        marker=dict(size=sizes, color=colors, line=dict(color=COLORS["border"], width=1), opacity=0.86),
        customdata=customdata,
        hovertemplate=_province_hover(),
    ))
    fig.add_vline(x=data["rokok_pct_of_gizi"].mean(), line_color=COLORS["neutral"], line_dash="dot")
    fig.add_hline(y=data["protein_per_capita"].mean(), line_color=COLORS["neutral"], line_dash="dot")
    fig.update_xaxes(title="Rokok % dari gizi", gridcolor=COLORS["border"])
    fig.update_yaxes(title="Protein per kapita (g/hari)", gridcolor=COLORS["border"])
    return apply_layout(fig, height=430)


def waterfall(row: pd.Series) -> go.Figure:
    labels = ["Rokok", "Sayur", "Ikan", "Telur & Susu", "Daging", "Buah"]
    vals = [
        float(row.get("rokok", 0) or 0),
        -float(row.get("sayur", 0) or 0),
        -float(row.get("ikan", 0) or 0),
        -float(row.get("telur_susu", 0) or 0),
        -float(row.get("daging", 0) or 0),
        -float(row.get("buah", 0) or 0),
    ]
    fig = go.Figure(go.Waterfall(
        x=labels, y=vals,
        measure=["absolute", "relative", "relative", "relative", "relative", "relative"],
        connector=dict(line=dict(color=COLORS["border"])),
        increasing=dict(marker_color=COLORS["positive"]),
        decreasing=dict(marker_color=COLORS["tobacco_primary"]),
        hovertemplate="<b>%{x}</b><br>Rp %{y:,.0f}<extra></extra>",
    ))
    fig.update_yaxes(tickprefix="Rp ", tickformat=",.0f", gridcolor=COLORS["border"])
    return apply_layout(fig, height=410)


def butterfly_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_figure("Data tidak tersedia")

    right_colors = [
        COLORS["warning"] if pd.notna(v) else COLORS["neutral"]
        for v in df["stunting_pct"]
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["label"],
        x=-df["smoking_daily_pct"].fillna(0),
        orientation="h",
        name="Perokok Harian (%)",
        marker_color=COLORS["tobacco_primary"],
        customdata=df["smoking_daily_pct"],
        hovertemplate="<b>%{y}</b><br>Perokok harian: %{customdata:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=df["label"],
        x=df["stunting_pct"].fillna(0),
        orientation="h",
        name="Stunting Baduta (%)",
        marker_color=right_colors,
        hovertemplate="<b>%{y}</b><br>Stunting: %{x:.1f}%<extra></extra>",
    ))

    # Compute symmetric axis range
    max_left = df["smoking_daily_pct"].max() if df["smoking_daily_pct"].notna().any() else 60
    max_right = df["stunting_pct"].max() if df["stunting_pct"].notna().any() else 30
    axis_max = max(max_left, max_right) * 1.15

    tick_step = 15 if axis_max > 40 else 10
    ticks = list(range(0, int(axis_max) + tick_step, tick_step))
    tick_vals = [-t for t in ticks] + ticks
    tick_text = [f"{t}%" for t in ticks] + [f"{t}%" for t in ticks]

    fig.update_layout(
        barmode="overlay",
        bargap=0.25,
        xaxis=dict(
            range=[-axis_max, axis_max],
            tickvals=tick_vals,
            ticktext=tick_text,
            title=dict(
                text="← Perokok Harian (%)                    Stunting Baduta (%) →",
                font=dict(color=COLORS["text_secondary"]),
            ),
            zeroline=True,
            zerolinecolor=COLORS["text_secondary"],
            zerolinewidth=2,
            gridcolor=COLORS["border"],
        ),
        yaxis=dict(gridcolor=COLORS["bg_card"]),
        legend=dict(orientation="h", y=1.06, x=0.5, xanchor="center"),
    )
    return apply_layout(fig, height=480)
