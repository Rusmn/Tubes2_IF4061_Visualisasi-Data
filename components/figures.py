from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from tokens import COLORS, TYPOGRAPHY

ROOT = Path(__file__).resolve().parents[1]

GREYOUT_COLOR = COLORS["bg_greyed"]

# Warna konsisten untuk komponen pangan (pie + bar)
_FOOD_COLORS = {
    "Rokok":        COLORS["tobacco_primary"],
    "Sayur":        "#EDE0C8",   # paling terang
    "Ikan":         "#CEC0A8",
    "Telur & Susu": "#B0A08A",
    "Daging":       "#928070",
    "Buah":         "#766254",   # paling gelap
}


def apply_layout(fig: go.Figure, height: int | None = None) -> go.Figure:
    fig.update_layout(
        paper_bgcolor=COLORS["bg_card"],
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text_primary"], family=TYPOGRAPHY["font_body"], size=12),
        margin=dict(l=42, r=24, t=42, b=38),
        uirevision="constant",
        height=height,
        transition={
            "duration": 500,
            "easing": "cubic-in-out",
        },
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=COLORS["border"],
            borderwidth=1,
            font=dict(size=11, color=COLORS["text_secondary"]),
        ),
        hoverlabel=dict(
            bgcolor="#2D2820",
            bordercolor=COLORS["border"],
            font=dict(color=COLORS["text_primary"], size=12, family=TYPOGRAPHY["font_body"]),
        ),
    )
    return fig


def empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message, xref="paper", yref="paper", x=0.5, y=0.5,
        showarrow=False, font=dict(color=COLORS["text_muted"], size=14),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
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
        "Stunting balita: %{customdata[6]:.1f}%"
        "<extra></extra>"
    )


def _choro_scale_for_metric(metric_col: str) -> list:
    return COLORS["choro_scale"]


_MAP_METRIC_LABELS: dict[str, str] = {
    "rokok_pct_of_gizi":  "Rokok % Gizi Total",
    "rokok_pct_of_sayur": "Rokok % Sayuran",
    "rokok_pct_of_daging":"Rokok % Daging",
    "stunting_pct":       "Stunting Balita (%)",
}


def make_indonesia_map(
    df: pd.DataFrame,
    metric_col: str = "rokok_pct_of_gizi",
    region: str = "all",
) -> go.Figure:
    metric_label = _MAP_METRIC_LABELS.get(metric_col, metric_col.replace("_", " "))

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

    # Grey provinces — only render when showing all regions (so fitbounds fits active only when filtered)
    if not df_grey.empty and region == "all":
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
                bgcolor="rgba(0,0,0,0)",
                tickfont=dict(color=COLORS["text_secondary"], size=10),
                title=dict(
                    text=metric_label,
                    font=dict(color=COLORS["text_secondary"], size=11),
                ),
                thickness=14,
                len=0.6,
            ),
            name="",
        ))

    # ── Top-3 rank markers ────────────────────────────────────────────────────
    top3 = (
        df_active.dropna(subset=[metric_col, "latitude", "longitude"])
        .sort_values(metric_col, ascending=False)
        .head(3)
    )
    if not top3.empty:
        medals = ["#FFD700", "#C0C0C0", "#CD7F32"]
        for i, (_, row) in enumerate(top3.iterrows()):
            rank = i + 1
            prov_short = row["province"].replace("Kepulauan ", "Kep. ")
            val = row.get(metric_col, 0)
            fig.add_trace(go.Scattergeo(
                lat=[row["latitude"]],
                lon=[row["longitude"]],
                mode="markers+text",
                marker=dict(
                    symbol="circle",
                    size=22,
                    color=medals[i],
                    line=dict(color="#1E1A18", width=2),
                ),
                text=[f"#{rank}"],
                textfont=dict(color="#1E1A18", size=10, family=TYPOGRAPHY["font_heading"]),
                textposition="middle center",
                customdata=[[row["province"], val]],
                hovertemplate=(
                    f"<b>#{rank} %{{customdata[0]}}</b><br>"
                    f"{metric_label}: %{{customdata[1]:.1f}}%"
                    "<extra></extra>"
                ),
                showlegend=False,
                name="",
            ))
            # Province name label below the marker
            fig.add_trace(go.Scattergeo(
                lat=[row["latitude"]],
                lon=[row["longitude"]],
                mode="text",
                text=[f"{prov_short}<br>{val:.1f}%"],
                textfont=dict(color=medals[i], size=9, family=TYPOGRAPHY["font_body"]),
                textposition="bottom center",
                hoverinfo="skip",
                showlegend=False,
                name="",
            ))

    geo_kwargs: dict = dict(
        fitbounds="locations",
        visible=True,
        bgcolor="#1C1917",
        landcolor="#252220",
        oceancolor="#1C1917",
        lakecolor="#1C1917",
        countrycolor="#3D3530",
        coastlinecolor="#3D3530",
        showland=True,
        showocean=True,
        showlakes=False,
        showcountries=True,
        showcoastlines=True,
        showframe=False,
    )
    fig.update_geos(**geo_kwargs)
    fig.update_layout(
        clickmode="event+select",
        title=dict(
            text=f"<b>{metric_label}</b> per Provinsi | SKI / SUSENAS 2023",
            font=dict(color=COLORS["text_secondary"], size=12, family=TYPOGRAPHY["font_body"]),
            x=0.01,
            xanchor="left",
            y=0.98,
            yanchor="top",
        ),
    )
    fig = apply_layout(fig, height=520)
    fig.update_layout(margin=dict(l=24, r=24, t=36, b=8))
    return fig


def plate_donut(df: pd.DataFrame) -> go.Figure:
    active = df[~df.get("_greyed_out", pd.Series(False, index=df.index))].copy() if "_greyed_out" in df.columns else df
    columns = ["rokok", "sayur", "ikan", "telur_susu", "daging", "buah"]
    values = active[columns].sum()
    labels = ["Rokok", "Sayur", "Ikan", "Telur & Susu", "Daging", "Buah"]
    colors = [_FOOD_COLORS[l] for l in labels]
    total = values.sum()
    rokok_pct = values["rokok"] / total * 100 if total > 0 else 0
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.58,
        ids=labels,
        marker=dict(colors=colors, line=dict(color=COLORS["bg_app"], width=2)),
        hovertemplate="<b>%{label}</b><br>Rp %{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        showlegend=True,
        annotations=[
            dict(
                text=f"<b>{rokok_pct:.1f}%</b><br><span style='font-size:10px'>porsi rokok</span>",
                x=0.5, y=0.5,
                font=dict(size=18, color=COLORS["tobacco_primary"], family=TYPOGRAPHY["font_heading"]),
                showarrow=False,
            )
        ],
        title=dict(
            text="Komposisi belanja pangan per kapita/bulan (Rp)",
            font=dict(color=COLORS["text_secondary"], size=11, family=TYPOGRAPHY["font_body"]),
            x=0.5,
            xanchor="center",
        ),
    )
    fig = apply_layout(fig, height=520)
    fig.update_layout(margin=dict(l=24, r=24, t=36, b=8))
    return fig


_BAR_METRIC_LABELS: dict[str, str] = {
    "rokok_pct_of_gizi":  "Rokok % Gizi Total",
    "rokok_pct_of_sayur": "Rokok % Sayuran",
    "rokok_pct_of_daging":"Rokok % Daging",
    "stunting_pct":       "Stunting Balita (%)",
}


def ranking_bar(
    df: pd.DataFrame,
    metric_col: str = "rokok_pct_of_gizi",
    limit: int = 10,
    national_avg: float | None = None,
    region: str = "all",
) -> go.Figure:
    greyed = df.get("_greyed_out", pd.Series(False, index=df.index))
    all_active = (~greyed).any()
    active = df[~greyed].copy() if all_active else df.copy()
    data = active.dropna(subset=[metric_col]).sort_values(metric_col, ascending=False).head(limit).sort_values(metric_col)
    if data.empty:
        return empty_figure("Data tidak tersedia")
    customdata = _province_customdata(data)
    y_labels = data["province"].str.replace("Kepulauan ", "Kep. ", regex=False)
    fig = go.Figure(go.Bar(
        x=data[metric_col], y=y_labels,
        orientation="h",
        marker=dict(
            color=COLORS["tobacco_primary"],
            line=dict(width=0),
        ),
        customdata=customdata,
        hovertemplate=_province_hover(),
    ))
    mean_val = active[metric_col].mean()
    axis_label = _BAR_METRIC_LABELS.get(metric_col, metric_col.replace("_", " "))
    x_max = max(
        float(data[metric_col].max()) * 1.22,
        (national_avg * 1.15) if national_avg is not None and pd.notna(national_avg) else 0,
    )

    show_filter_line = pd.notna(mean_val) and region != "all"
    show_national_line = national_avg is not None and pd.notna(national_avg)

    if show_national_line:
        fig.add_vline(x=national_avg, line_color=COLORS["text_muted"], line_dash="dash", line_width=1.2)
        fig.add_annotation(
            x=national_avg, y=1.04, xref="x", yref="paper",
            text=f"rata-rata nasional: {national_avg:.1f}%",
            showarrow=False, xanchor="center",
            font=dict(color=COLORS["text_muted"], size=10, family=TYPOGRAPHY["font_body"]),
        )

    if show_filter_line:
        fig.add_vline(x=mean_val, line_color=COLORS["gold"], line_dash="dot", line_width=1.5)
        fig.add_annotation(
            x=mean_val, y=-0.1, xref="x", yref="paper",
            text=f"rata-rata regional: {mean_val:.1f}%",
            showarrow=False, xanchor="center",
            font=dict(color=COLORS["gold"], size=10, family=TYPOGRAPHY["font_body"]),
        )

    fig.update_xaxes(
        range=[0, x_max],
        gridcolor=COLORS["border"],
        title=axis_label,
    )
    n_bars = len(data)
    fig.update_yaxes(gridcolor=COLORS["bg_card"], ticks="", range=[-0.5, n_bars - 0.5])
    fig = apply_layout(fig, height=420)
    fig.update_layout(margin=dict(l=155, r=28, t=48, b=48))
    return fig


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


def nutrition_duel_chart(row: pd.Series) -> go.Figure:
    labels = ["Sayur", "Ikan", "Telur & Susu", "Daging", "Buah"]
    columns = ["sayur", "ikan", "telur_susu", "daging", "buah"]
    rokok = float(row.get("rokok", 0) or 0)
    values = [float(row.get(col, 0) or 0) for col in columns]
    if rokok <= 0 or not any(values):
        return empty_figure("Data duel gizi tidak tersedia")

    ratios = [rokok / value if value > 0 else 0 for value in values]
    colors = [COLORS["tobacco_primary"] if ratio >= 1 else COLORS["gizi_primary"] for ratio in ratios]
    verdicts = ["Rokok menang" if ratio >= 1 else "Gizi unggul" for ratio in ratios]
    text = [f"{ratio:.1f}x" for ratio in ratios]

    data = pd.DataFrame(
        {
            "label": labels,
            "value": values,
            "ratio": ratios,
            "color": colors,
            "verdict": verdicts,
            "text": text,
        }
    ).sort_values("ratio", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=data["ratio"],
            y=data["label"],
            orientation="h",
            marker=dict(color=data["color"], line=dict(color=COLORS["border"], width=1)),
            text=data["text"],
            textposition="outside",
            customdata=data[["verdict", "value"]],
            hovertemplate=(
                "<b>Rokok vs %{y}</b><br>"
                "%{customdata[0]}: %{x:.2f}x<br>"
                "Belanja gizi: Rp %{customdata[1]:,.0f}<br>"
                f"Belanja rokok: Rp {rokok:,.0f}"
                "<extra></extra>"
            ),
        )
    )
    wins = int(sum(ratio >= 1 for ratio in ratios))
    fig.add_vline(x=1, line_color=COLORS["gold"], line_dash="dot", line_width=2)
    fig.add_annotation(
        x=1,
        y=1.06,
        xref="x",
        yref="paper",
        text="seri",
        showarrow=False,
        font=dict(color=COLORS["gold"], size=12),
    )
    fig.add_annotation(
        x=0,
        y=-0.18,
        xref="paper",
        yref="paper",
        text=f"Rokok mengalahkan {wins} dari 5 komponen gizi.",
        showarrow=False,
        align="left",
        font=dict(color=COLORS["text_secondary"], size=13),
    )
    fig.update_xaxes(
        title="Kelipatan belanja rokok dibanding komponen gizi",
        gridcolor=COLORS["border"],
        rangemode="tozero",
    )
    fig.update_yaxes(gridcolor=COLORS["bg_card"])
    return apply_layout(fig, height=410)


def spending_gap_chart(row: pd.Series) -> go.Figure:
    labels = ["Sayur", "Ikan", "Telur & Susu", "Daging", "Buah"]
    columns = ["sayur", "ikan", "telur_susu", "daging", "buah"]
    colors = [COLORS["sayur"], COLORS["ikan"], COLORS["telur"], COLORS["daging"], COLORS["buah"]]
    rokok = float(row.get("rokok", 0) or 0)
    values = [float(row.get(col, 0) or 0) for col in columns]
    if rokok <= 0 or not any(values):
        return empty_figure("Data jarak belanja tidak tersedia")

    data = pd.DataFrame({"label": labels, "value": values, "color": colors})
    data["gap"] = rokok - data["value"]
    data["abs_gap"] = data["gap"].abs()
    data = data.sort_values("abs_gap", ascending=True).reset_index(drop=True)
    y_positions = list(range(len(data)))
    x_max = max([rokok, *data["value"].tolist()]) * 1.22

    fig = go.Figure()
    for idx, item in data.iterrows():
        gap = float(item["gap"])
        nutrition_value = float(item["value"])
        start, end = sorted([rokok, nutrition_value])
        line_color = COLORS["tobacco_primary"] if gap > 0 else item["color"]
        verdict = "Rokok lebih besar" if gap > 0 else "Gizi lebih besar"
        fig.add_trace(
            go.Scatter(
                x=[start, end],
                y=[idx, idx],
                mode="lines",
                line=dict(color=line_color, width=7),
                opacity=0.68,
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[nutrition_value],
                y=[idx],
                mode="markers",
                marker=dict(size=17, color=item["color"], line=dict(color=COLORS["text_primary"], width=1)),
                customdata=[[item["label"], nutrition_value, gap, verdict]],
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Belanja gizi: Rp %{customdata[1]:,.0f}<br>"
                    f"Belanja rokok: Rp {rokok:,.0f}<br>"
                    "%{customdata[3]}: Rp %{customdata[2]:+,.0f}"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )
        label_x = end + (x_max * 0.018)
        gap_text = f"Rokok +Rp {gap:,.0f}" if gap > 0 else f"Gizi +Rp {abs(gap):,.0f}"
        fig.add_annotation(
            x=label_x,
            y=idx,
            text=gap_text,
            showarrow=False,
            xanchor="left",
            font=dict(color=line_color, size=12),
        )

    fig.add_vline(x=rokok, line_color=COLORS["tobacco_primary"], line_dash="dot", line_width=3)
    fig.add_trace(
        go.Scatter(
            x=[rokok] * len(data),
            y=y_positions,
            mode="markers",
            marker=dict(
                symbol="line-ns",
                size=20,
                color=COLORS["tobacco_primary"],
                line=dict(color=COLORS["tobacco_primary"], width=2),
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    wins = int((data["gap"] > 0).sum())
    fig.add_annotation(
        x=rokok,
        y=1.08,
        xref="x",
        yref="paper",
        text="belanja rokok",
        showarrow=False,
        font=dict(color=COLORS["tobacco_light"], size=12),
        bgcolor="rgba(28,28,28,0.78)",
        bordercolor=COLORS["border"],
        borderpad=4,
    )
    fig.add_annotation(
        x=0,
        y=-0.24,
        xref="paper",
        yref="paper",
        text=f"Rokok lebih besar dari {wins} dari 5 komponen gizi; garis memperlihatkan selisih rupiah per kapita per bulan.",
        showarrow=False,
        align="left",
        font=dict(color=COLORS["text_secondary"], size=13),
    )
    fig.update_xaxes(
        title="Rupiah per kapita per bulan",
        range=[0, x_max],
        tickprefix="Rp ",
        tickformat=",.0f",
        gridcolor=COLORS["border"],
    )
    fig.update_yaxes(
        tickmode="array",
        tickvals=y_positions,
        ticktext=data["label"],
        gridcolor=COLORS["bg_card"],
    )
    fig.update_layout(showlegend=False, margin=dict(l=86, r=136, t=54, b=86))
    return apply_layout(fig, height=430)


def spending_rank_chart(row: pd.Series) -> go.Figure:
    items = [
        ("Rokok",        "rokok",      _FOOD_COLORS["Rokok"]),
        ("Sayur",        "sayur",      _FOOD_COLORS["Sayur"]),
        ("Ikan",         "ikan",       _FOOD_COLORS["Ikan"]),
        ("Telur & Susu", "telur_susu", _FOOD_COLORS["Telur & Susu"]),
        ("Daging",       "daging",     _FOOD_COLORS["Daging"]),
        ("Buah",         "buah",       _FOOD_COLORS["Buah"]),
    ]
    data = pd.DataFrame(
        [
            {
                "label": label,
                "value": float(row.get(column, 0) or 0),
                "color": color,
            }
            for label, column, color in items
        ]
    )
    if data["value"].le(0).all():
        return empty_figure("Data struktur pengeluaran tidak tersedia")

    data = data.sort_values("value", ascending=False).reset_index(drop=True)
    data["rank"] = data.index + 1
    data["rank_label"] = data.apply(lambda x: f"#{int(x['rank'])} {x['label']}", axis=1)
    data["bar_color"] = data.apply(
        lambda x: COLORS["tobacco_primary"] if x["label"] == "Rokok" else x["color"],
        axis=1,
    )
    data["opacity"] = data["label"].map(lambda label: 1.0 if label == "Rokok" else 0.70)

    rokok_row = data[data["label"] == "Rokok"].iloc[0]
    top_row = data.iloc[0]
    rokok_rank = int(rokok_row["rank"])
    defeated = int((float(rokok_row["value"]) > data.loc[data["label"] != "Rokok", "value"]).sum())
    if rokok_rank == 1:
        verdict = f"Rokok menjadi komponen terbesar dan melampaui {defeated} dari 5 komponen gizi."
    else:
        gap = float(top_row["value"] - rokok_row["value"])
        verdict = (
            f"Rokok peringkat #{rokok_rank}; masih di bawah {top_row['label']} "
            f"sebesar Rp {gap:,.0f}, tetapi melampaui {defeated} dari 5 komponen gizi."
        )

    plot_data = data.sort_values("value", ascending=True)
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=plot_data["value"],
            y=plot_data["rank_label"],
            orientation="h",
            marker=dict(
                color=plot_data["bar_color"],
                opacity=plot_data["opacity"],
                line=dict(color=COLORS["border"], width=1),
            ),
            text=[f"Rp {value:,.0f}" for value in plot_data["value"]],
            textposition="inside",
            insidetextanchor="end",
            textfont=dict(color=COLORS["text_primary"], size=12),
            cliponaxis=False,
            customdata=plot_data[["label", "rank", "value"]],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Peringkat: #%{customdata[1]}<br>"
                "Belanja: Rp %{customdata[2]:,.0f}"
                "<extra></extra>"
            ),
        )
    )
    fig.add_annotation(
        x=0,
        y=-0.22,
        xref="paper",
        yref="paper",
        text=verdict,
        showarrow=False,
        align="left",
        font=dict(color=COLORS["text_secondary"], size=13),
    )
    x_max = float(data["value"].max()) * 1.28
    fig.update_xaxes(
        title="Rupiah per kapita per bulan",
        tickprefix="Rp ",
        tickformat=",.0f",
        gridcolor=COLORS["border"],
        range=[0, x_max],
    )
    fig.update_yaxes(gridcolor=COLORS["bg_card"])
    fig.update_layout(showlegend=False, uniformtext_minsize=10)
    fig = apply_layout(fig, height=430)
    fig.update_layout(margin=dict(l=112, r=28, t=30, b=78))
    return fig


def province_compass(df: pd.DataFrame, selected: str | None = None) -> go.Figure:
    active = df[~df.get("_greyed_out", pd.Series(False, index=df.index))].copy() if "_greyed_out" in df.columns else df.copy()
    data = active.dropna(subset=["rokok_pct_of_gizi", "protein_per_capita"])
    if data.empty:
        return empty_figure("Data posisi provinsi tidak tersedia")

    x_mean = float(data["rokok_pct_of_gizi"].mean())
    y_mean = float(data["protein_per_capita"].mean())
    x_min, x_max = float(data["rokok_pct_of_gizi"].min()), float(data["rokok_pct_of_gizi"].max())
    y_min, y_max = float(data["protein_per_capita"].min()), float(data["protein_per_capita"].max())
    x_pad = (x_max - x_min) * 0.12 or 1
    y_pad = (y_max - y_min) * 0.12 or 1
    x_range = [x_min - x_pad, x_max + x_pad]
    y_range = [y_min - y_pad, y_max + y_pad]

    selected_data = data[data["province"] == selected] if selected else data.iloc[0:0]
    other_data = data[data["province"] != selected] if selected else data

    fig = go.Figure()
    zone_fill = "rgba(127, 140, 141, 0.10)"
    risk_fill = "rgba(192, 57, 43, 0.16)"
    ideal_fill = "rgba(39, 174, 96, 0.13)"
    fig.add_shape(type="rect", x0=x_range[0], x1=x_mean, y0=y_mean, y1=y_range[1], fillcolor=ideal_fill, line_width=0, layer="below")
    fig.add_shape(type="rect", x0=x_mean, x1=x_range[1], y0=y_mean, y1=y_range[1], fillcolor=zone_fill, line_width=0, layer="below")
    fig.add_shape(type="rect", x0=x_range[0], x1=x_mean, y0=y_range[0], y1=y_mean, fillcolor=zone_fill, line_width=0, layer="below")
    fig.add_shape(type="rect", x0=x_mean, x1=x_range[1], y0=y_range[0], y1=y_mean, fillcolor=risk_fill, line_width=0, layer="below")

    sizes = (other_data["population_thousands"].fillna(other_data["population_thousands"].median()).clip(lower=100) ** 0.5) / 5
    fig.add_trace(
        go.Scatter(
            x=other_data["rokok_pct_of_gizi"],
            y=other_data["protein_per_capita"],
            mode="markers",
            text=other_data["province"],
            marker=dict(
                size=sizes,
                color=COLORS["tobacco_primary"],
                opacity=0.48,
                line=dict(color=COLORS["border"], width=1),
            ),
            customdata=_province_customdata(other_data),
            hovertemplate=_province_hover(),
            name="Provinsi lain",
        )
    )
    if not selected_data.empty:
        fig.add_trace(
            go.Scatter(
                x=selected_data["rokok_pct_of_gizi"],
                y=selected_data["protein_per_capita"],
                mode="markers+text",
                text=selected_data["province"],
                textposition="top center",
                marker=dict(
                    symbol="diamond",
                    size=24,
                    color=COLORS["gold"],
                    line=dict(color=COLORS["text_primary"], width=2),
                ),
                customdata=_province_customdata(selected_data),
                hovertemplate=_province_hover(),
                name="Provinsi terpilih",
            )
        )

    fig.add_vline(x=x_mean, line_color=COLORS["text_secondary"], line_dash="dot", line_width=2)
    fig.add_hline(y=y_mean, line_color=COLORS["text_secondary"], line_dash="dot", line_width=2)
    annotations = [
        (x_range[0], y_range[1], "Rokok rendah<br>protein tinggi", "left", "top"),
        (x_range[1], y_range[1], "Rokok tinggi<br>protein tinggi", "right", "top"),
        (x_range[0], y_range[0], "Rokok rendah<br>protein rendah", "left", "bottom"),
        (x_range[1], y_range[0], "Tekanan ganda", "right", "bottom"),
    ]
    for x, y, text_label, xanchor, yanchor in annotations:
        fig.add_annotation(
            x=x,
            y=y,
            text=text_label,
            showarrow=False,
            xanchor=xanchor,
            yanchor=yanchor,
            font=dict(color=COLORS["text_muted"], size=12),
            bgcolor="rgba(28,28,28,0.72)",
            bordercolor=COLORS["border"],
            borderpad=4,
        )

    fig.update_xaxes(title="Rokok % dari gizi", gridcolor=COLORS["border"], range=x_range)
    fig.update_yaxes(title="Protein per kapita (g/hari)", gridcolor=COLORS["border"], range=y_range)
    fig.update_layout(showlegend=False, clickmode="event")
    apply_layout(fig, height=430)
    fig.update_layout(margin=dict(l=58, r=24, t=42, b=38))
    return fig


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


def opportunity_sankey(
    row: pd.Series,
    amount: float | None = None,
    allocation_mode: int | str = 0,
) -> go.Figure:
    labels = ["Sayur", "Ikan", "Telur & Susu", "Daging", "Buah"]
    columns = ["sayur", "ikan", "telur_susu", "daging", "buah"]
    colors = [COLORS["sayur"], COLORS["ikan"], COLORS["telur"], COLORS["daging"], COLORS["buah"]]
    rokok = float(row.get("rokok", 0) or 0)
    current_values = [float(row.get(col, 0) or 0) for col in columns]
    total_gizi = sum(current_values)
    flow_amount = rokok if amount is None else max(float(amount), 0)
    if rokok <= 0 or total_gizi <= 0:
        return empty_figure("Data opportunity cost tidak tersedia")
    if flow_amount <= 0:
        return empty_figure("Turunkan slider rokok untuk melihat aliran dana yang bisa dialihkan ke gizi")

    try:
        mode = int(allocation_mode)
    except (TypeError, ValueError):
        mode = 0
    mode_specs = {
        0: {
            "name": "Komposisi belanja sekarang",
            "weights": [value / total_gizi for value in current_values],
            "note": "Alokasi mengikuti komposisi belanja gizi provinsi saat ini.",
        },
        1: {
            "name": "Bagi rata",
            "weights": [0.2] * 5,
            "note": "Alokasi dibagi sama besar ke lima komponen gizi.",
        },
        2: {
            "name": "Fokus protein hewani",
            "weights": [0.08, 0.42, 0.30, 0.15, 0.05],
            "note": "Alokasi diprioritaskan ke ikan, telur/susu, dan daging.",
        },
        3: {
            "name": "Fokus serat pangan",
            "weights": [0.45, 0.10, 0.10, 0.05, 0.30],
            "note": "Alokasi diprioritaskan ke sayur dan buah.",
        },
    }
    spec = mode_specs.get(mode, mode_specs[0])
    weight_total = sum(spec["weights"]) or 1
    weights = [weight / weight_total for weight in spec["weights"]]
    allocated = [flow_amount * weight for weight in weights]
    node_labels = ["Belanja Rokok", *labels]
    node_colors = [COLORS["tobacco_primary"], *colors]
    link_colors = [
        "rgba(46, 204, 113, 0.40)",
        "rgba(30, 139, 195, 0.40)",
        "rgba(243, 156, 18, 0.42)",
        "rgba(231, 76, 60, 0.34)",
        "rgba(155, 89, 182, 0.40)",
    ]
    customdata = [
        [
            label,
            allocation,
            current,
            allocation / current * 100 if current else 0,
            spec["name"],
        ]
        for label, allocation, current in zip(labels, allocated, current_values)
    ]
    fig = go.Figure(
        go.Sankey(
            arrangement="fixed",
            node=dict(
                pad=20,
                thickness=18,
                line=dict(color=COLORS["border"], width=1),
                label=node_labels,
                color=node_colors,
                hovertemplate="<b>%{label}</b><extra></extra>",
            ),
            link=dict(
                source=[0] * len(labels),
                target=list(range(1, len(labels) + 1)),
                value=allocated,
                color=link_colors,
                customdata=customdata,
                hovertemplate=(
                    "<b>Rokok dialihkan ke %{customdata[0]}</b><br>"
                    "Mode: %{customdata[4]}<br>"
                    "Alokasi skenario: Rp %{customdata[1]:,.0f}<br>"
                    "Belanja saat ini: Rp %{customdata[2]:,.0f}<br>"
                    "Setara %{customdata[3]:.1f}% dari belanja saat ini"
                    "<extra></extra>"
                ),
            ),
        )
    )
    fig.add_annotation(
        text=f"{spec['note']} Angka ini skenario eksploratif, bukan rekomendasi kausal.",
        xref="paper",
        yref="paper",
        x=0,
        y=-0.08,
        showarrow=False,
        align="left",
        font=dict(color=COLORS["text_muted"], size=12),
    )
    return apply_layout(fig, height=410)


def butterfly_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_figure("Data tidak tersedia")

    right_colors = [
        COLORS["gizi_primary"] if pd.notna(v) else COLORS["neutral"]
        for v in df["normal_pct"]
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
        x=df["normal_pct"].fillna(0),
        orientation="h",
        name="Gizi Normal (%)",
        marker_color=right_colors,
        hovertemplate="<b>%{y}</b><br>Gizi normal: %{x:.1f}%<extra></extra>",
    ))

    max_left = df["smoking_daily_pct"].max() if df["smoking_daily_pct"].notna().any() else 60
    max_right = df["normal_pct"].max() if df["normal_pct"].notna().any() else 90
    axis_max = max(max_left, max_right) * 1.10

    tick_step = 20 if axis_max > 60 else 15
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
                text="← Perokok Harian (%)                    Gizi Normal Balita (%) →",
                font=dict(color=COLORS["text_secondary"]),
            ),
            zeroline=True,
            zerolinecolor=COLORS["text_secondary"],
            zerolinewidth=2,
            gridcolor=COLORS["border"],
        ),
        yaxis=dict(gridcolor=COLORS["bg_card"]),
        legend=dict(orientation="h", y=1.10, x=0.5, xanchor="center"),
    )
    fig = apply_layout(fig, height=480)
    fig.update_layout(margin=dict(l=160, r=24, t=72, b=48))
    return fig


def characteristic_dual_axis(df: pd.DataFrame, dimension: str = "") -> go.Figure:
    if df.empty or "normal_pct" not in df.columns or df["normal_pct"].isna().all():
        return empty_figure("Data gizi normal tidak tersedia untuk dimensi ini")

    data = df.dropna(subset=["smoking_daily_pct", "normal_pct"]).copy()
    if data.empty:
        return empty_figure("Data karakteristik tidak tersedia")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=data["label"],
            y=data["smoking_daily_pct"],
            name="Perokok harian",
            marker=dict(
                color=COLORS["tobacco_primary"],
                opacity=0.82,
                line=dict(color=COLORS["border"], width=1),
            ),
            customdata=data[["label", "smoking_daily_pct", "normal_pct"]],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Perokok harian: %{customdata[1]:.1f}%<br>"
                "Gizi normal balita: %{customdata[2]:.1f}%"
                "<extra></extra>"
            ),
            yaxis="y",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data["label"],
            y=data["normal_pct"],
            name="Gizi normal balita",
            mode="lines+markers",
            line=dict(color=COLORS["gizi_teal"], width=3, shape="spline"),
            marker=dict(size=10, color=COLORS["gizi_teal"], line=dict(color=COLORS["text_primary"], width=1)),
            customdata=data[["label", "smoking_daily_pct", "normal_pct"]],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Gizi normal balita: %{customdata[2]:.1f}%<br>"
                "Perokok harian: %{customdata[1]:.1f}%"
                "<extra></extra>"
            ),
            yaxis="y2",
        )
    )

    smoke_max = max(float(data["smoking_daily_pct"].max()) * 1.25, 10)
    normal_min = max(float(data["normal_pct"].min()) - 4, 0)
    normal_max = min(float(data["normal_pct"].max()) + 4, 100)

    if len(data) >= 2:
        first = data.iloc[0]
        last = data.iloc[-1]
        smoke_delta = float(last["smoking_daily_pct"] - first["smoking_daily_pct"])
        normal_delta = float(last["normal_pct"] - first["normal_pct"])
        if dimension == "pendidikan":
            note = (
                f"Dari pendidikan terendah ke tertinggi: perokok harian {smoke_delta:+.1f} poin, "
                f"gizi normal {normal_delta:+.1f} poin."
            )
        else:
            note = "Baca sebagai pola asosiasi antar-kelompok karakteristik, bukan hubungan sebab-akibat."
        fig.add_annotation(
            x=0,
            y=-0.28,
            xref="paper",
            yref="paper",
            text=note,
            showarrow=False,
            align="left",
            font=dict(color=COLORS["text_secondary"], size=12),
        )

    fig.update_layout(
        barmode="group",
        legend=dict(orientation="h", y=1.14, x=0.5, xanchor="center"),
        xaxis=dict(
            tickangle=-18 if len(data) > 4 else 0,
            gridcolor=COLORS["bg_card"],
        ),
        yaxis=dict(
            title=dict(text="Perokok harian (%)", font=dict(color=COLORS["tobacco_light"])),
            range=[0, smoke_max],
            gridcolor=COLORS["border"],
            tickfont=dict(color=COLORS["tobacco_light"]),
        ),
        yaxis2=dict(
            title=dict(text="Gizi normal balita (%)", font=dict(color=COLORS["gizi_teal"])),
            range=[normal_min, normal_max],
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color=COLORS["gizi_teal"]),
        ),
    )
    fig = apply_layout(fig, height=440)
    fig.update_layout(margin=dict(l=58, r=58, t=72, b=112))
    return fig
