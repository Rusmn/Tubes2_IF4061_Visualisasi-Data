from __future__ import annotations

import numpy as np
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go

from src.theme import CHOROPLETH_SCALE, COLORS, COMMODITY_COLORS, base_layout
from src.util import percent, rupiah

METRICS = {
    "Rokok/Gizi (%)": "rokok_pct_of_gizi",
    "Rokok/Sayur (rasio)": "rokok_vs_sayur_ratio",
    "Protein per kapita": "protein_per_capita",
    "Kemiskinan (%)": "poverty_rate",
    "Stunting (%)": "stunting_0_59_total_pct",
    "Policy priority": "policy_priority_index",
}


def style(fig: go.Figure, height: int | None = None, showlegend: bool = False) -> go.Figure:
    fig.update_layout(**base_layout(height, showlegend))
    fig.update_xaxes(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"], linecolor=COLORS["border"])
    fig.update_yaxes(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"], linecolor=COLORS["border"])
    return fig


def _label_for_metric(metric: str) -> str:
    return next((name for name, col in METRICS.items() if col == metric), metric)


def component_df(row: pd.Series) -> pd.DataFrame:
    labels = {
        "rokok": "Rokok",
        "sayur": "Sayur",
        "ikan": "Ikan",
        "telur_susu": "Telur & susu",
        "daging": "Daging",
        "buah": "Buah",
    }
    return pd.DataFrame({
        "Komponen": list(labels.values()),
        "Nilai": [float(row.get(k, 0) or 0) for k in labels],
        "Kelompok": ["Rokok", "Gizi", "Gizi", "Gizi", "Gizi", "Gizi"],
    })


def kpi_stats(df: pd.DataFrame) -> dict:
    return {
        "count_rokok_gt_sayur": int((df["rokok"] > df["sayur"]).sum()),
        "count_rokok_gt_daging": int((df["rokok"] > df["daging"]).sum()),
        "n": int(len(df)),
        "avg_rokok": float(df["rokok"].mean()),
        "avg_sayur": float(df["sayur"].mean()),
        "avg_ratio": float(df["rokok_pct_of_gizi"].mean()),
        "gap_rokok_sayur": float(df["rokok"].mean() - df["sayur"].mean()),
    }


def national_row(df: pd.DataFrame) -> pd.Series:
    cols = ["rokok", "sayur", "ikan", "telur_susu", "daging", "buah", "gizi_total", "rokok_pct_of_gizi", "rokok_vs_sayur_ratio", "poverty_rate", "protein_per_capita", "calorie_per_capita", "policy_priority_index"]
    vals = {c: float(df[c].mean()) for c in cols if c in df.columns}
    vals["province"] = "Nasional"
    vals["province_key"] = "NASIONAL"
    return pd.Series(vals)


def plate_donut(row: pd.Series, title: str = "Piring Pengeluaran") -> go.Figure:
    comp = component_df(row)
    rokok_pct = float(row.get("rokok_pct_of_gizi", 0) or 0)
    fig = go.Figure(go.Pie(
        labels=comp["Komponen"],
        values=comp["Nilai"],
        hole=0.50,
        sort=False,
        marker={"colors": [COMMODITY_COLORS.get(x, COLORS["gold"]) for x in comp["Komponen"]], "line": {"color": COLORS["bg"], "width": 2}},
        textinfo="percent",
        textposition="inside",
        insidetextfont={"size": 9},
        hovertemplate="<b>%{label}</b><br>Rp %{value:,.0f}<br>%{percent}<extra></extra>",
        pull=[0.06, 0, 0, 0, 0, 0],
    ))
    center = f"<b>{percent(rokok_pct)}</b><br>rokok/gizi"
    fig.update_layout(
        title=title,
        annotations=[{"text": center, "showarrow": False, "x": 0.5, "y": 0.5,
                       "font": {"size": 14, "color": COLORS["red_hot"]}}],
    )
    return style(fig)


def gauge_donut(pct: int, color_name: str = "red") -> go.Figure:
    fill = COLORS["red"] if color_name == "red" else COLORS["green"]
    fig = go.Figure(go.Pie(
        values=[pct, 100 - pct],
        hole=0.65,
        sort=False,
        marker={"colors": [fill, COLORS["panel2"]], "line": {"color": COLORS["bg"], "width": 1}},
        textinfo="none",
        hoverinfo="skip",
        direction="clockwise",
        rotation=90,
    ))
    fig.update_layout(
        showlegend=False,
        margin={"l": 8, "r": 8, "t": 8, "b": 8},
        annotations=[{"text": f"<b>{pct}%</b>", "showarrow": False,
                       "x": 0.5, "y": 0.5,
                       "font": {"size": 20, "color": fill}}],
    )
    return style(fig)


_MB = {"style": "carto-darkmatter", "center": {"lat": -2.5, "lon": 118.0}, "zoom": 3.5}


def map_or_scatter(df: pd.DataFrame, geojson: dict | None, metric: str, focus_province: str | None, graph_title: str = "Peta Indonesia", height: int | None = None) -> go.Figure:
    label = _label_for_metric(metric)
    data = df.copy()
    if geojson:
        fig = go.Figure(go.Choroplethmapbox(
            geojson=geojson,
            featureidkey="properties.province_key",
            locations=data["province_key"],
            z=data[metric],
            text=data["province"],
            customdata=np.stack([
                data["rokok"].round(0), data["gizi_total"].round(0),
                data["rokok_pct_of_gizi"].round(1), data["poverty_rate"].round(1),
                data["protein_per_capita"].round(1),
            ], axis=-1),
            colorscale=CHOROPLETH_SCALE,
            marker_line_color="rgba(7,17,21,.72)",
            marker_line_width=0.8,
            marker_opacity=0.88,
            colorbar={"title": label},
            hovertemplate="<b>%{text}</b><br>" + label + ": %{z:.1f}<br>Rokok: Rp %{customdata[0]:,.0f}<br>Gizi total: Rp %{customdata[1]:,.0f}<br>Rokok/Gizi: %{customdata[2]:.1f}%<br>Kemiskinan: %{customdata[3]:.1f}%<br>Protein: %{customdata[4]:.1f} g<extra></extra>",
        ))
        if focus_province:
            focus = data[data["province"].eq(focus_province)]
            if not focus.empty:
                fig.add_trace(go.Choroplethmapbox(
                    geojson=geojson, featureidkey="properties.province_key",
                    locations=focus["province_key"], z=[1] * len(focus),
                    colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                    showscale=False, marker_line_color=COLORS["gold_light"],
                    marker_line_width=3, hoverinfo="skip",
                ))
    else:
        part = data.dropna(subset=["latitude", "longitude"])
        fig = go.Figure(go.Scattermapbox(
            lon=part["longitude"], lat=part["latitude"], mode="markers+text",
            text=part["province"], textposition="top right",
            customdata=part[["province", "rokok_pct_of_gizi", "poverty_rate", "protein_per_capita"]],
            marker={"size": np.clip(part[metric].rank(pct=True) * 28 + 8, 8, 36), "color": part[metric], "colorscale": CHOROPLETH_SCALE, "showscale": True},
            hovertemplate="<b>%{customdata[0]}</b><br>Rokok/Gizi: %{customdata[1]:.1f}%<br>Kemiskinan: %{customdata[2]:.1f}%<br>Protein: %{customdata[3]:.1f}<extra></extra>",
        ))
    fig.update_layout(title=graph_title, mapbox=_MB)
    fig = style(fig, height, False)
    return fig.update_layout(margin={"l": 0, "r": 60, "t": 38, "b": 0})


def ranking_bar(df: pd.DataFrame, metric: str, focus_province: str | None = None, top_n: int = 8, title: str | None = None) -> go.Figure:
    label = _label_for_metric(metric)
    rank = df.sort_values(metric, ascending=False).head(top_n).sort_values(metric)
    is_pct = any(k in metric for k in ("pct", "rate", "index"))
    fmt = lambda v: percent(v) if is_pct else f"{v:.1f}"
    colors = [COLORS["gold_light"] if p == focus_province else COLORS["red"] for p in rank["province"]]
    fig = go.Figure(go.Bar(
        x=rank[metric], y=rank["province"], orientation="h",
        marker_color=colors,
        marker_line_width=0,
        text=[fmt(v) for v in rank[metric]],
        textposition="outside",
        textfont={"size": 11, "color": COLORS["muted"]},
        hovertemplate="<b>%{y}</b><br>" + label + ": %{x:.2f}<extra></extra>",
    ))
    mean_val = df[metric].mean()
    fig.add_vline(x=mean_val, line_dash="dash", line_color=COLORS["gold_light"],
                  annotation_text=f"Rata-rata {fmt(mean_val)}", annotation_font_size=10)
    fig.update_layout(title=title or f"Ranking provinsi — {label}", xaxis_title=label, yaxis_title="",
                      xaxis={"showgrid": True})
    return style(fig)


def distribution_hist(df: pd.DataFrame, metric: str, focus_value: float | None = None) -> go.Figure:
    label = _label_for_metric(metric)
    fig = go.Figure(go.Histogram(x=df[metric], nbinsx=9, marker_color=COLORS["amber"], opacity=.92))
    fig.add_vline(x=df[metric].mean(), line_dash="dash", line_color=COLORS["red_hot"], annotation_text="Rata-rata")
    if focus_value is not None and not pd.isna(focus_value):
        fig.add_vline(x=focus_value, line_color=COLORS["gold_light"], annotation_text="Fokus")
    fig.update_layout(title="Distribusi antar provinsi", xaxis_title=label, yaxis_title="Jumlah provinsi")
    return style(fig)


def dot_components(row: pd.Series, title: str = "Rokok vs Komponen Gizi") -> go.Figure:
    comp = component_df(row)
    fig = go.Figure(go.Scatter(
        x=comp["Nilai"], y=comp["Komponen"], mode="markers+text",
        marker={"size": [20 if k == "Rokok" else 15 for k in comp["Komponen"]], "color": [COMMODITY_COLORS.get(k, COLORS["gold"]) for k in comp["Komponen"]], "line": {"color": COLORS["cream"], "width": 1}},
        text=[rupiah(v) for v in comp["Nilai"]], textposition="middle right",
        hovertemplate="<b>%{y}</b><br>Rp %{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(title=title, xaxis_title="Rupiah per kapita per bulan", yaxis_title="")
    fig = style(fig)
    return fig.update_layout(margin={"r": 80})


def waterfall_allocation(row: pd.Series) -> go.Figure:
    fig = go.Figure(go.Waterfall(
        x=["Rokok", "Sayur", "Ikan", "Telur+susu", "Daging", "Buah", "Sisa"],
        y=[row["rokok"], -row["sayur"], -row["ikan"], -row["telur_susu"], -row["daging"], -row["buah"], max(0, row["rokok"] - row["gizi_total"])],
        measure=["absolute", "relative", "relative", "relative", "relative", "relative", "total"],
        increasing={"marker": {"color": COLORS["red"]}},
        decreasing={"marker": {"color": COLORS["green"]}},
        totals={"marker": {"color": COLORS["gold"]}},
        connector={"line": {"color": COLORS["border"]}},
        hovertemplate="%{x}<br>Rp %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(title="Alokasi Pengeluaran Pangan (Waterfall)", yaxis_title="Rupiah")
    return style(fig)


def composition_bar(row: pd.Series) -> go.Figure:
    comp = component_df(row)
    total = comp["Nilai"].sum()
    comp["pct"] = comp["Nilai"] / total * 100
    fig = go.Figure(go.Bar(
        x=comp["pct"], y=comp["Komponen"], orientation="h",
        marker_color=[COMMODITY_COLORS.get(k, COLORS["gold"]) for k in comp["Komponen"]],
        text=[percent(v) for v in comp["pct"]], textposition="outside",
    ))
    fig.update_layout(title="Komposisi Pengeluaran", xaxis_title="% dari total", yaxis_title="")
    return style(fig)


def dumbbell_compare(df: pd.DataFrame, row: pd.Series) -> go.Figure:
    labels = ["Rokok", "Sayur", "Ikan", "Telur & susu", "Daging", "Buah"]
    cols = ["rokok", "sayur", "ikan", "telur_susu", "daging", "buah"]
    avg = [df[c].mean() for c in cols]
    cur = [row[c] for c in cols]
    fig = go.Figure()
    for y, a, c in zip(labels, avg, cur):
        fig.add_trace(go.Scatter(x=[a, c], y=[y, y], mode="lines", line={"color": COLORS["border"], "width": 3}, showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=avg, y=labels, mode="markers", marker={"size": 12, "color": COLORS["gold"]}, name="Nasional"))
    fig.add_trace(go.Scatter(x=cur, y=labels, mode="markers", marker={"size": 14, "color": COLORS["red_hot"]}, name=row["province"]))
    fig.update_layout(title="Perbandingan dengan Nasional", xaxis_title="Rp per kapita per bulan", yaxis_title="")
    return style(fig, showlegend=True)


def quadrant(df: pd.DataFrame, focus_province: str | None = None, x: str = "rokok_pct_of_gizi", y: str = "protein_per_capita", color: str = "poverty_rate", title: str = "Diagnosis lokal") -> go.Figure:
    data = df.dropna(subset=[x, y]).copy()
    fig = px.scatter(
        data, x=x, y=y, size="population", color=color, hover_name="province",
        color_continuous_scale=CHOROPLETH_SCALE,
        size_max=34,
        labels={x: _label_for_metric(x), y: _label_for_metric(y), color: _label_for_metric(color)},
    )
    fig.add_vline(x=data[x].mean(), line_dash="dash", line_color=COLORS["muted"])
    fig.add_hline(y=data[y].mean(), line_dash="dash", line_color=COLORS["muted"])
    if focus_province and focus_province in set(data["province"]):
        r = data[data["province"].eq(focus_province)].iloc[0]
        fig.add_trace(go.Scatter(x=[r[x]], y=[r[y]], mode="markers+text", text=[focus_province], textposition="top center", marker={"size": 22, "color": COLORS["red_hot"], "line": {"color": COLORS["cream"], "width": 3}}, name="Fokus"))
    fig.update_layout(title=title)
    return style(fig)


def reallocation_chart(row: pd.Series, pct: int) -> go.Figure:
    shifted = row["rokok"] * pct / 100
    scenario = pd.DataFrame({
        "Skenario": ["Saat ini", f"Realokasi {pct}%"],
        "Rokok": [row["rokok"], row["rokok"] - shifted],
        "Gizi": [row["gizi_total"], row["gizi_total"] + shifted],
    })
    fig = px.bar(scenario, x="Skenario", y=["Rokok", "Gizi"], barmode="group", color_discrete_sequence=[COLORS["red"], COLORS["gold"]])
    fig.update_layout(title="Simulasi realokasi rokok ke pangan", yaxis_title="Rp per kapita/bulan", xaxis_title="")
    return style(fig, showlegend=True)


def behavior_sankey() -> go.Figure:
    labels = ["Kuartil 1", "Kuartil 2", "Kuartil 3", "Kuartil 4", "Perokok aktif", "Perokok pasif", "Bukan perokok", "Gizi rentan", "Gizi sedang", "Gizi baik"]
    fig = go.Figure(go.Sankey(
        node={"label": labels, "pad": 13, "thickness": 16, "color": [COLORS["red"], COLORS["amber"], COLORS["gold"], COLORS["green"], COLORS["red_deep"], COLORS["amber"], COLORS["green"], COLORS["red"], COLORS["gold"], COLORS["green"]]},
        link={
            "source": [0,0,1,1,2,2,3,3,4,4,5,5,6,6],
            "target": [4,5,4,5,5,6,5,6,7,8,7,8,8,9],
            "value": [18,8,14,12,10,15,7,22,19,14,12,17,9,29],
            "color": ["rgba(192,39,45,.34)", "rgba(219,149,65,.24)", "rgba(192,39,45,.28)", "rgba(219,149,65,.24)", "rgba(219,149,65,.24)", "rgba(122,166,106,.28)", "rgba(219,149,65,.20)", "rgba(122,166,106,.32)", "rgba(192,39,45,.42)", "rgba(219,149,65,.25)", "rgba(192,39,45,.26)", "rgba(219,149,65,.32)", "rgba(219,149,65,.24)", "rgba(122,166,106,.35)"],
        },
    ))
    fig = style(fig)
    return fig.update_layout(margin={"l": 8, "r": 8, "t": 40, "b": 8})


def smoking_heatmap() -> go.Figure:
    ages = ["15-19", "20-29", "30-39", "40-49", "50-59", "60+"]
    rows = ["Q1 terbawah", "Q2", "Q3", "Q4 teratas"]
    z = np.array([[10.5,36.8,45.9,45.1,39.2,26.7],[7.6,30.4,40.2,39.1,32.7,21.3],[6.1,25.2,33.3,32.3,26.7,15.6],[3.6,17.4,24.1,22.7,17.8,9.8]])
    fig = go.Figure(go.Heatmap(z=z, x=ages, y=rows, colorscale=[[0, COLORS["green"]], [.45, COLORS["gold"]], [1, COLORS["red"]]], text=np.char.add(np.round(z, 1).astype(str), "%"), texttemplate="%{text}", hovertemplate="%{y}, %{x}: %{z:.1f}%<extra></extra>"))
    fig.update_layout(title="Prevalensi Merokok: Umur × Status Ekonomi", xaxis_title="Umur", yaxis_title="Status ekonomi")
    return style(fig)


def education_stack() -> go.Figure:
    edu = ["≤ SD", "SMP", "SMA", "Diploma/PT", "Pascasarjana"]
    active = [41.2, 36.1, 30.3, 20.4, 14.2]
    passive = [28.7, 29.3, 28.7, 24.3, 20.2]
    non = [30.1, 34.6, 41.0, 55.3, 65.6]
    fig = go.Figure()
    fig.add_trace(go.Bar(y=edu, x=active, orientation="h", name="Perokok aktif", marker_color=COLORS["red"]))
    fig.add_trace(go.Bar(y=edu, x=passive, orientation="h", name="Perokok pasif", marker_color=COLORS["amber"]))
    fig.add_trace(go.Bar(y=edu, x=non, orientation="h", name="Bukan perokok", marker_color=COLORS["green"]))
    fig.update_layout(title="Pendidikan × Status Merokok", barmode="stack", xaxis_title="Proporsi (%)", yaxis_title="")
    return style(fig, showlegend=True)


def price_lines(trends: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if trends.empty:
        return style(fig, showlegend=True)
    color_map = {"Rokok/tembakau": COLORS["red_hot"], "Daging": COLORS["amber"], "Telur & susu": COLORS["gold"], "Ikan": COLORS["blue"], "Sayur/buah": COLORS["green"]}
    for label, group in trends.groupby("indicator"):
        fig.add_trace(go.Scatter(x=group["year"], y=group["value"], mode="lines+markers", name=label, line={"color": color_map.get(label, COLORS["muted"]), "width": 2.6}))
    fig.update_layout(title="Indeks Harga Relatif vs Pangan Bergizi", yaxis_title="Indeks, awal periode = 100", xaxis_title="")
    return style(fig, showlegend=True)


def global_benchmark() -> go.Figure:
    labels = ["Indonesia", "ASEAN", "G20", "China", "India", "Brazil", "USA", "World"]
    indonesia = [33.2, 26.1, 25.2, 24.0, 13.6, 14.7, 11.6, 23.0]
    peers = [26.1, 24.8, 22.7, 22.1, 12.8, 13.1, 11.1, 18.7]
    bar_colors = [COLORS["red_hot"] if l == "Indonesia" else COLORS["red"] for l in labels]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=indonesia, name="Indonesia / negara", marker_color=bar_colors))
    fig.add_trace(go.Bar(x=labels, y=peers, name="Rata-rata kelompok", marker_color=COLORS["gold"], opacity=0.85))
    fig.add_annotation(x="Indonesia", y=indonesia[0] + 1.8, text="⚠ Tertinggi",
                       showarrow=False, font={"color": COLORS["red_hot"], "size": 11, "family": "Inter"})
    fig.update_layout(title="Indonesia vs Global Benchmark", barmode="group",
                      yaxis_title="Prevalensi merokok dewasa (%)", xaxis_title="")
    return style(fig, showlegend=True)


def policy_matrix() -> go.Figure:
    fig = go.Figure()
    quadrants = [
        (0.25, 0.75, "Cukai + Edukasi", COLORS["red"], "Naikkan cukai & kampanye antirokok"),
        (0.75, 0.75, "Bantuan Gizi", COLORS["green"], "Bantuan pangan bergizi & suplementasi"),
        (0.25, 0.25, "Akses Pangan", COLORS["amber"], "Perkuat akses dan harga pangan"),
        (0.75, 0.25, "Monitoring Perilaku", COLORS["blue"], "Pantau rokok dan gizi rutin"),
    ]
    for x, y, title, color, note in quadrants:
        fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers+text", marker={"size": 86, "color": color, "opacity": .75}, text=[f"<b>{title}</b><br>{note}"], textposition="middle center", hoverinfo="skip", showlegend=False))
    fig.update_xaxes(range=[0, 1], tickvals=[0.15, 0.85], ticktext=["Kelayakan rendah", "Kelayakan tinggi"])
    fig.update_yaxes(range=[0, 1], tickvals=[0.15, 0.85], ticktext=["Dampak rendah", "Dampak tinggi"])
    fig.update_layout(title="Matriks Prioritas Kebijakan")
    return style(fig)


def impact_sankey(row: pd.Series) -> go.Figure:
    labels = ["Pengeluaran rumah tangga", "Rokok", "Gizi", "Dampak kesehatan", "Dampak ekonomi", "Human capital", "PTM", "Produktivitas", "Stunting/kognitif"]
    fig = go.Figure(go.Sankey(
        node={"label": labels, "pad": 16, "thickness": 16, "color": [COLORS["gold"], COLORS["red"], COLORS["green"], COLORS["red_dark"], COLORS["amber"], COLORS["green"], COLORS["red"], COLORS["amber"], COLORS["green"]]},
        link={"source": [0,0,1,1,2,3,4,5], "target": [1,2,3,4,5,6,7,8], "value": [row["rokok"], row["gizi_total"], row["rokok"]*.42, row["rokok"]*.33, row["gizi_total"]*.25, row["rokok"]*.42, row["rokok"]*.33, row["gizi_total"]*.25], "color": ["rgba(192,39,45,.42)", "rgba(122,166,106,.35)", "rgba(192,39,45,.42)", "rgba(219,149,65,.35)", "rgba(122,166,106,.35)", "rgba(192,39,45,.35)", "rgba(219,149,65,.35)", "rgba(122,166,106,.35)"]},
    ))
    fig = style(fig)
    return fig.update_layout(margin={"l": 8, "r": 8, "t": 40, "b": 8})


def sunburst_allocation(row: pd.Series) -> go.Figure:
    comp = component_df(row)
    labels = ["Total belanja piring", "Rokok", "Gizi esensial"] + comp.loc[comp["Kelompok"].eq("Gizi"), "Komponen"].tolist()
    parents = ["", "Total belanja piring", "Total belanja piring"] + ["Gizi esensial"] * int(comp["Kelompok"].eq("Gizi").sum())
    values = [
        float(comp["Nilai"].sum()),
        float(row["rokok"]),
        float(comp.loc[comp["Kelompok"].eq("Gizi"), "Nilai"].sum()),
        *comp.loc[comp["Kelompok"].eq("Gizi"), "Nilai"].astype(float).tolist(),
    ]
    colors = [COLORS["panel"], COLORS["red"], COLORS["green"]] + [COMMODITY_COLORS.get(x, COLORS["gold"]) for x in comp.loc[comp["Kelompok"].eq("Gizi"), "Komponen"]]
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker={"colors": colors, "line": {"color": COLORS["bg"], "width": 2}},
        hovertemplate="<b>%{label}</b><br>Rp %{value:,.0f}<extra></extra>",
    ))
    fig.update_layout(title="Sunburst alokasi piring")
    return style(fig)


def treemap_priority(df: pd.DataFrame) -> go.Figure:
    data = df.sort_values("policy_priority_index", ascending=False).head(18).copy()
    fig = px.treemap(
        data,
        path=["risk_label", "province"],
        values="population",
        color="policy_priority_index",
        color_continuous_scale=CHOROPLETH_SCALE,
        hover_data=["rokok_pct_of_gizi", "stunting_0_59_total_pct", "poverty_rate"],
    )
    fig.update_traces(textinfo="label+value", marker_line_color=COLORS["bg"], marker_line_width=1.5)
    fig.update_layout(title="Treemap prioritas provinsi")
    return style(fig)


def radar_profile(row: pd.Series, df: pd.DataFrame) -> go.Figure:
    metrics = {
        "Rokok/Gizi": "rokok_pct_of_gizi",
        "Kemiskinan": "poverty_rate",
        "Stunting": "stunting_0_59_total_pct",
        "Gini": "gini",
        "Digital": "digital_index_pct",
        "Protein": "protein_per_capita",
    }
    theta = list(metrics.keys())
    focus = []
    national = []
    for col in metrics.values():
        series = df[col].astype(float)
        lo, hi = float(series.min()), float(series.max())
        span = hi - lo if hi != lo else 1
        focus.append((float(row[col]) - lo) / span * 100)
        national.append((float(series.mean()) - lo) / span * 100)
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=focus + [focus[0]], theta=theta + [theta[0]], fill="toself", name=row["province"], line_color=COLORS["red_hot"]))
    fig.add_trace(go.Scatterpolar(r=national + [national[0]], theta=theta + [theta[0]], fill="toself", name="Nasional", line_color=COLORS["gold"], opacity=.65))
    fig.update_layout(title="Radar profil risiko", polar={"bgcolor": "rgba(0,0,0,0)", "radialaxis": {"visible": True, "range": [0, 100], "gridcolor": COLORS["grid"]}})
    return style(fig, showlegend=True)


def bubble_map(df: pd.DataFrame, metric: str = "policy_priority_index") -> go.Figure:
    data = df.dropna(subset=["latitude", "longitude"]).copy()
    fig = go.Figure(go.Scattermapbox(
        lon=data["longitude"], lat=data["latitude"], mode="markers",
        text=data["province"],
        marker={"size": np.clip(np.sqrt(data["population"]) / 10, 8, 38),
                "color": data[metric], "colorscale": CHOROPLETH_SCALE, "showscale": True, "opacity": .88},
        customdata=data[["rokok_pct_of_gizi", "poverty_rate", "protein_per_capita"]],
        hovertemplate="<b>%{text}</b><br>Rokok/Gizi: %{customdata[0]:.1f}%<br>Kemiskinan: %{customdata[1]:.1f}%<br>Protein: %{customdata[2]:.1f} g<extra></extra>",
    ))
    fig.update_layout(title="Bubble map prioritas", mapbox=_MB)
    fig = style(fig)
    return fig.update_layout(margin={"l": 0, "r": 60, "t": 38, "b": 0})


def altair_heatmap(df: pd.DataFrame):
    cols = [("Rokok/Gizi","rokok_pct_of_gizi"),("Kemiskinan","poverty_rate"),
            ("Stunting","stunting_0_59_total_pct"),("Protein","protein_per_capita"),
            ("Digital","digital_index_pct"),("Gini","gini")]
    top = df.sort_values("policy_priority_index", ascending=False).head(14).copy()
    records = []
    for label, col in cols:
        series = df[col].astype(float)
        lo, hi = float(series.min()), float(series.max())
        span = hi - lo if hi != lo else 1
        for _, row in top.iterrows():
            records.append({"Provinsi": row["province"], "Indikator": label, "Skor": (float(row[col]) - lo) / span * 100})
    chart = alt.Chart(pd.DataFrame(records)).mark_rect(cornerRadius=2).encode(
        x=alt.X("Indikator:N", title=None),
        y=alt.Y("Provinsi:N", title=None, sort=top["province"].tolist()),
        color=alt.Color("Skor:Q", scale=alt.Scale(range=[COLORS["green"], COLORS["gold"], COLORS["red"]])),
        tooltip=["Provinsi", "Indikator", alt.Tooltip("Skor:Q", format=".1f")],
    ).properties(height=320)
    return chart.configure(background="transparent").configure_axis(labelColor=COLORS["muted"], titleColor=COLORS["text"], grid=False).configure_view(strokeOpacity=0).configure_legend(labelColor=COLORS["muted"], titleColor=COLORS["text"])


def altair_ridgeline(df: pd.DataFrame):
    data = df[["risk_label", "rokok_pct_of_gizi", "province"]].copy()
    base = alt.Chart(data).transform_density(
        "rokok_pct_of_gizi",
        as_=["Rasio", "Density"],
        groupby=["risk_label"],
        extent=[float(data["rokok_pct_of_gizi"].min()) - 2, float(data["rokok_pct_of_gizi"].max()) + 2],
    )
    chart = base.mark_area(orient="horizontal", opacity=.78, interpolate="monotone").encode(
        y=alt.Y("Rasio:Q", title="Rokok/Gizi (%)"),
        x=alt.X("Density:Q", title=None, stack="center", axis=None),
        row=alt.Row("risk_label:N", title=None),
        color=alt.Color("risk_label:N", legend=None, scale=alt.Scale(range=[COLORS["green"], COLORS["gold"], COLORS["red"]])),
        tooltip=["risk_label:N", alt.Tooltip("Rasio:Q", format=".1f")],
    ).properties(height=78)
    return chart.configure(background="transparent").configure_axis(labelColor=COLORS["muted"], titleColor=COLORS["text"], gridColor=COLORS["grid"]).configure_header(labelColor=COLORS["text"], titleColor=COLORS["text"]).configure_view(strokeOpacity=0)
