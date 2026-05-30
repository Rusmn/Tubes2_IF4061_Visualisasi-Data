from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from data_processing.loader import coverage_status
from tokens import COLORS, TYPOGRAPHY

ROOT = Path(__file__).resolve().parents[1]


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


def province_hover() -> str:
    return (
        "<b>%{customdata[0]}</b><br>"
        "Rokok/kapita: Rp %{customdata[1]:,.0f}<br>"
        "Gizi total: Rp %{customdata[2]:,.0f}<br>"
        "Rokok % dari gizi: %{customdata[3]:.1f}%<br>"
        "Protein/kapita: %{customdata[4]:.1f} g/hari<br>"
        "Kemiskinan: %{customdata[5]:.1f}%<br>"
        "Status geometri: %{customdata[6]}"
        "<extra></extra>"
    )


def empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(color=COLORS["text_muted"], size=14),
    )
    return apply_layout(fig, height=420)


def make_indonesia_map(df: pd.DataFrame, metric_col: str = "rokok_pct_of_gizi", mode: str = "auto") -> go.Figure:
    if df.empty or metric_col not in df.columns:
        return empty_figure("Data peta tidak tersedia")

    coverage = coverage_status()
    should_choropleth = mode == "choropleth" or (mode == "auto" and coverage["geo_match_count"] == 38)
    customdata = df[
        [
            "province",
            "rokok",
            "gizi_total",
            "rokok_pct_of_gizi",
            "protein_per_capita",
            "poverty_rate",
            "geometry_status",
        ]
    ].values

    if should_choropleth:
        geo_path = ROOT / "data" / "geo" / "indonesia_provinces.geojson"
        with geo_path.open(encoding="utf-8") as handle:
            geojson = json.load(handle)
        fig = go.Figure(
            go.Choropleth(
                geojson=geojson,
                locations=df["geo_feature_id"],
                featureidkey="properties.REGION_CODE",
                z=df[metric_col],
                colorscale=COLORS["choro_scale"],
                marker_line_color=COLORS["border"],
                marker_line_width=0.5,
                customdata=customdata,
                hovertemplate=province_hover(),
                colorbar=dict(
                    bgcolor=COLORS["bg_card"],
                    tickfont=dict(color=COLORS["text_secondary"]),
                    title=dict(text=metric_col, font=dict(color=COLORS["text_secondary"])),
                ),
            )
        )
        fig.update_geos(fitbounds="locations", visible=False, bgcolor=COLORS["bg_app"])
    else:
        marker_size = (df["population_thousands"].fillna(df["population_thousands"].median()).clip(lower=300) ** 0.5) / 5
        fig = go.Figure(
            go.Scattergeo(
                lon=df["longitude"],
                lat=df["latitude"],
                text=df["province"],
                mode="markers",
                customdata=customdata,
                hovertemplate=province_hover(),
                marker=dict(
                    size=marker_size,
                    color=df[metric_col],
                    colorscale=COLORS["choro_scale"],
                    line=dict(color=COLORS["border"], width=1),
                    colorbar=dict(
                        bgcolor=COLORS["bg_card"],
                        tickfont=dict(color=COLORS["text_secondary"]),
                        title=dict(text=metric_col, font=dict(color=COLORS["text_secondary"])),
                    ),
                ),
            )
        )
        fig.update_geos(
            projection_type="natural earth",
            lataxis_range=[-12, 7],
            lonaxis_range=[94, 142],
            showland=True,
            landcolor=COLORS["bg_card"],
            showcountries=False,
            showcoastlines=True,
            coastlinecolor=COLORS["border"],
            bgcolor=COLORS["bg_app"],
        )

    fig.update_layout(clickmode="event+select")
    return apply_layout(fig, height=520)


def plate_donut(df: pd.DataFrame) -> go.Figure:
    columns = ["rokok", "sayur", "ikan", "telur_susu", "daging", "buah"]
    values = df[columns].sum()
    labels = ["Rokok", "Sayur", "Ikan", "Telur & Susu", "Daging", "Buah"]
    colors = [
        COLORS["tobacco_primary"],
        COLORS["sayur"],
        COLORS["ikan"],
        COLORS["telur"],
        COLORS["daging"],
        COLORS["buah"],
    ]
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.58,
            marker=dict(colors=colors, line=dict(color=COLORS["bg_app"], width=2)),
            hovertemplate="<b>%{label}</b><br>Rp %{value:,.0f}<br>%{percent}<extra></extra>",
        )
    )
    fig.update_layout(showlegend=True)
    return apply_layout(fig, height=420)


def ranking_bar(df: pd.DataFrame, metric_col: str = "rokok_pct_of_gizi", limit: int = 10) -> go.Figure:
    data = df.sort_values(metric_col, ascending=False).head(limit).sort_values(metric_col)
    fig = go.Figure(
        go.Bar(
            x=data[metric_col],
            y=data["province"],
            orientation="h",
            marker_color=COLORS["tobacco_primary"],
            customdata=data[["province", "rokok", "gizi_total", "rokok_pct_of_gizi", "protein_per_capita", "poverty_rate", "geometry_status"]].values,
            hovertemplate=province_hover(),
        )
    )
    fig.add_vline(x=df[metric_col].mean(), line_color=COLORS["gold"], line_dash="dot")
    fig.update_xaxes(gridcolor=COLORS["border"], title=metric_col)
    fig.update_yaxes(gridcolor=COLORS["bg_card"])
    return apply_layout(fig, height=420)


def scatter_quadrant(df: pd.DataFrame, selected: str | None = None) -> go.Figure:
    sizes = (df["population_thousands"].fillna(df["population_thousands"].median()).clip(lower=300) ** 0.5) / 5
    colors = [COLORS["gold"] if selected and p == selected else COLORS["tobacco_primary"] for p in df["province"]]
    fig = go.Figure(
        go.Scatter(
            x=df["rokok_pct_of_gizi"],
            y=df["protein_per_capita"],
            mode="markers",
            text=df["province"],
            marker=dict(size=sizes, color=colors, line=dict(color=COLORS["border"], width=1), opacity=0.86),
            customdata=df[["province", "rokok", "gizi_total", "rokok_pct_of_gizi", "protein_per_capita", "poverty_rate", "geometry_status"]].values,
            hovertemplate=province_hover(),
        )
    )
    fig.add_vline(x=df["rokok_pct_of_gizi"].mean(), line_color=COLORS["neutral"], line_dash="dot")
    fig.add_hline(y=df["protein_per_capita"].mean(), line_color=COLORS["neutral"], line_dash="dot")
    fig.update_xaxes(title="Rokok % dari gizi", gridcolor=COLORS["border"])
    fig.update_yaxes(title="Protein per kapita", gridcolor=COLORS["border"])
    return apply_layout(fig, height=430)


def metric_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    x_title: str,
    y_title: str,
    selected: str | None = None,
    color_col: str = "rokok_pct_of_gizi",
) -> go.Figure:
    data = df.dropna(subset=[x_col, y_col]).copy()
    if data.empty:
        return empty_figure("Data SKI tidak tersedia")
    sizes = (data["population_thousands"].fillna(data["population_thousands"].median()).clip(lower=300) ** 0.5) / 5
    marker_line = [COLORS["gold"] if selected and p == selected else COLORS["border"] for p in data["province"]]
    fig = go.Figure(
        go.Scatter(
            x=data[x_col],
            y=data[y_col],
            mode="markers",
            text=data["province"],
            marker=dict(
                size=sizes,
                color=data[color_col],
                colorscale=COLORS["choro_scale"],
                line=dict(color=marker_line, width=1.4),
                opacity=0.88,
                colorbar=dict(tickfont=dict(color=COLORS["text_secondary"])),
            ),
            customdata=data[
                [
                    "province",
                    "rokok",
                    "gizi_total",
                    "rokok_pct_of_gizi",
                    "protein_per_capita",
                    "poverty_rate",
                    "geometry_status",
                ]
            ].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                f"{x_title}: %{{x:.1f}}<br>"
                f"{y_title}: %{{y:.1f}}<br>"
                "Rokok % dari gizi: %{customdata[3]:.1f}%"
                "<extra></extra>"
            ),
        )
    )
    fig.add_vline(x=data[x_col].mean(), line_color=COLORS["neutral"], line_dash="dot")
    fig.add_hline(y=data[y_col].mean(), line_color=COLORS["neutral"], line_dash="dot")
    fig.update_xaxes(title=x_title, gridcolor=COLORS["border"])
    fig.update_yaxes(title=y_title, gridcolor=COLORS["border"])
    return apply_layout(fig, height=430)


def metric_bar(df: pd.DataFrame, metric_col: str, title: str, limit: int = 10, high_is_risk: bool = True) -> go.Figure:
    data = df.dropna(subset=[metric_col]).sort_values(metric_col, ascending=not high_is_risk).head(limit)
    data = data.sort_values(metric_col)
    color = COLORS["tobacco_primary"] if high_is_risk else COLORS["gizi_primary"]
    fig = go.Figure(
        go.Bar(
            x=data[metric_col],
            y=data["province"],
            orientation="h",
            marker_color=color,
            hovertemplate="<b>%{y}</b><br>%{x:.1f}<extra></extra>",
        )
    )
    fig.add_vline(x=df[metric_col].mean(), line_color=COLORS["gold"], line_dash="dot")
    fig.update_xaxes(title=title, gridcolor=COLORS["border"])
    fig.update_yaxes(gridcolor=COLORS["bg_card"])
    return apply_layout(fig, height=410)


def waterfall(row: pd.Series) -> go.Figure:
    labels = ["Rokok", "Sayur", "Ikan", "Telur & Susu", "Daging", "Buah"]
    values = [row["rokok"], -row["sayur"], -row["ikan"], -row["telur_susu"], -row["daging"], -row["buah"]]
    fig = go.Figure(
        go.Waterfall(
            x=labels,
            y=values,
            measure=["absolute", "relative", "relative", "relative", "relative", "relative"],
            connector=dict(line=dict(color=COLORS["border"])),
            increasing=dict(marker_color=COLORS["positive"]),
            decreasing=dict(marker_color=COLORS["tobacco_primary"]),
            totals=dict(marker_color=COLORS["neutral"]),
            hovertemplate="<b>%{x}</b><br>Rp %{y:,.0f}<extra></extra>",
        )
    )
    fig.update_yaxes(tickprefix="Rp ", tickformat=",.0f", gridcolor=COLORS["border"])
    return apply_layout(fig, height=410)


def price_lines(price_df: pd.DataFrame) -> go.Figure:
    if price_df.empty:
        return empty_figure("Data harga tidak tersedia")
    fig = go.Figure()
    for label, group in price_df.groupby("sub_group"):
        fig.add_trace(
            go.Scatter(
                x=group["year"],
                y=group["value"],
                mode="lines+markers",
                name=str(label)[:32],
                hovertemplate="<b>%{fullData.name}</b><br>%{x}: %{y:.1f}<extra></extra>",
            )
        )
    fig.update_xaxes(gridcolor=COLORS["border"])
    fig.update_yaxes(gridcolor=COLORS["border"], title="Indeks")
    return apply_layout(fig, height=400)


def priority_table(df: pd.DataFrame) -> list[dict[str, object]]:
    cols = [
        "province",
        "region",
        "rokok_pct_of_gizi",
        "smoking_10plus_current_pct",
        "stunting_0_59_total_pct",
        "milk_rare_pct",
        "policy_priority_score",
    ]
    data = df.sort_values("policy_priority_score", ascending=False).head(12)[cols].copy()
    for column in [
        "rokok_pct_of_gizi",
        "smoking_10plus_current_pct",
        "stunting_0_59_total_pct",
        "milk_rare_pct",
        "policy_priority_score",
    ]:
        data[column] = data[column].round(1)
    return data.to_dict("records")
