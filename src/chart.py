from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.theme import COLORS, plot_theme

LABELS = {
    "rokok": "Belanja rokok",
    "gizi_total": "Belanja gizi esensial",
    "rokok_pct_of_gizi": "Rokok / gizi (%)",
    "smoking_15_pct": "Merokok 15+ (%)",
    "smoking_indoor_pct": "Merokok dalam ruangan (%)",
    "passive_smoke_daily_pct": "Paparan asap harian (%)",
    "stunting_0_59_total_pct": "Stunting balita (%)",
    "mad_6_23_pct": "Diet minimal anak (%)",
    "animal_protein_6_23_pct": "Protein hewani anak (%)",
    "poverty_rate": "Kemiskinan (%)",
    "pdrb_capita": "PDRB per kapita",
    "school_year": "Rata-rata lama sekolah",
    "risk_index": "Indeks risiko",
    "population": "Populasi",
}


def fig_style(fig: go.Figure, height: int = 460) -> go.Figure:
    fig.update_layout(**plot_theme(), height=height)
    fig.update_xaxes(gridcolor="rgba(237,229,214,.10)", zerolinecolor="rgba(237,229,214,.16)")
    fig.update_yaxes(gridcolor="rgba(237,229,214,.10)", zerolinecolor="rgba(237,229,214,.16)")
    return fig


def mark_focus(fig: go.Figure, df: pd.DataFrame, focus: str, xcol: str, ycol: str) -> go.Figure:
    if not focus:
        return fig
    row = df[df["province"].eq(focus)]
    if row.empty:
        return fig
    item = row.iloc[0]
    fig.add_trace(
        go.Scatter(
            x=[item[xcol]],
            y=[item[ycol]],
            mode="markers+text",
            text=[focus],
            textposition="top center",
            marker={"size": 18, "color": COLORS["paper"], "line": {"color": COLORS["red_hot"], "width": 3}},
            name="Provinsi dipilih",
            hovertemplate=f"{focus}<extra></extra>",
        )
    )
    return fig


def make_donut(row: pd.Series) -> go.Figure:
    labels = ["Rokok", "Sayur", "Ikan", "Telur & susu", "Daging", "Buah"]
    values = [row["rokok"], row["sayur"], row["ikan"], row["telur_susu"], row["daging"], row["buah"]]
    colors = [COLORS["red"], COLORS["green"], COLORS["blue"], "#C9B26D", "#A66A3F", "#D99C52"]
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=.48,
            marker={"colors": colors, "line": {"color": "rgba(27,23,21,.9)", "width": 2}},
            textinfo="label+percent",
            hovertemplate="%{label}<br>Rp%{value:,.0f}<br>%{percent}<extra></extra>",
        )
    )
    fig.update_layout(title="Komposisi belanja yang sedang dibandingkan")
    return fig_style(fig, 430)


def map_points(fig: go.Figure, df: pd.DataFrame, focus: str = "") -> go.Figure:
    if not {"Latitude", "Longitude"}.issubset(df.columns):
        return fig
    temp = df.dropna(subset=["Latitude", "Longitude"]).copy()
    fig.add_trace(
        go.Scattergeo(
            lon=temp["Longitude"],
            lat=temp["Latitude"],
            text=temp["province"],
            mode="markers",
            marker={
                "size": np.where(temp["province"].eq(focus), 13, 5),
                "color": np.where(temp["province"].eq(focus), COLORS["red_hot"], COLORS["paper"]),
                "line": {"color": "rgba(27,23,21,.92)", "width": 1.4},
                "opacity": .92,
            },
            hovertemplate="<b>%{text}</b><br>lat %{lat:.3f}<br>lon %{lon:.3f}<extra></extra>",
            showlegend=False,
        )
    )
    return fig


def make_map(df: pd.DataFrame, geo: dict, col: str, title: str, scale: list[str] | None = None, focus: str = "") -> go.Figure:
    scale = scale or ["#F4E7D0", "#D9AE45", COLORS["red"], "#6E0B10"]
    fig = px.choropleth(
        df,
        geojson=geo,
        locations="prov_key",
        featureidkey="properties.name",
        color=col,
        hover_name="province",
        hover_data={col: ":.2f", "risk_index": ":.1f", "prov_key": False},
        color_continuous_scale=scale,
        title=title,
        labels=LABELS,
    )
    fig.update_traces(marker_line={"color": "rgba(27,23,21,.80)", "width": .7})
    map_points(fig, df, focus)
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor="rgba(18,16,15,.98)",
        projection_type="mercator",
    )
    fig.update_coloraxes(colorbar={"title": "", "thickness": 12, "len": .72})
    return fig_style(fig, 560)


def bi_map(df: pd.DataFrame, geo: dict) -> go.Figure:
    colors = {
        "Rokok tinggi, gizi rapuh": COLORS["red_dark"],
        "Rokok tinggi": COLORS["red"],
        "Gizi rapuh": COLORS["gold_dark"],
        "Lebih ringan": COLORS["blue"],
        "Data kurang": COLORS["gray_dark"],
    }
    fig = px.choropleth(
        df,
        geojson=geo,
        locations="prov_key",
        featureidkey="properties.name",
        color="bi_key",
        hover_name="province",
        hover_data={
            "rokok_pct_of_gizi": ":.1f",
            "stunting_0_59_total_pct": ":.1f",
            "prov_key": False,
        },
        color_discrete_map=colors,
        title="Dua sinyal dalam satu peta",
    )
    fig.update_traces(marker_line={"color": "rgba(27,23,21,.80)", "width": .7})
    map_points(fig, df)
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor="rgba(18,16,15,.98)",
        projection_type="mercator",
    )
    return fig_style(fig, 560)


def rank_bar(df: pd.DataFrame, col: str, title: str, top: int = 10, high: bool = True, focus: str = "") -> go.Figure:
    temp = df.dropna(subset=[col]).sort_values(col, ascending=not high).head(top)
    if focus and focus not in temp["province"].tolist():
        picked = df[df["province"].eq(focus)].dropna(subset=[col])
        temp = pd.concat([temp, picked], ignore_index=True).drop_duplicates("province")
    temp["picked"] = np.where(temp["province"].eq(focus), "Provinsi dipilih", "Provinsi lain")
    fig = px.bar(
        temp.sort_values(col),
        x=col,
        y="province",
        orientation="h",
        text=col,
        title=title,
        color="picked",
        color_discrete_map={"Provinsi dipilih": COLORS["red_hot"], "Provinsi lain": COLORS["gold"]},
        hover_data={"province": True, col: ":.2f"},
        labels=LABELS,
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False)
    return fig_style(fig, 430)


def city_bar(df: pd.DataFrame, query: str = "", top: int = 25) -> go.Figure:
    temp = df.copy()
    if query:
        temp = temp[temp["city"].str.contains(query, case=False, na=False)]
    temp = temp.sort_values("weekly_smoke", ascending=False).head(top)
    fig = px.bar(
        temp.sort_values("weekly_smoke"),
        x="weekly_smoke",
        y="city",
        orientation="h",
        title="Kab/kota dengan konsumsi rokok mingguan tertinggi",
        color="weekly_smoke",
        color_continuous_scale=[COLORS["blue"], COLORS["gold"], COLORS["red"]],
        hover_data={
            "kretek_filter": ":.2f",
            "kretek_plain": ":.2f",
            "white": ":.2f",
            "tobacco": ":.2f",
            "other": ":.2f",
        },
    )
    fig.update_coloraxes(showscale=False)
    fig.update_xaxes(title="Batang rokok per kapita per minggu")
    fig.update_yaxes(title="")
    return fig_style(fig, 620)


def scatter_quad(df: pd.DataFrame, xcol: str, ycol: str, title: str, focus: str = "") -> go.Figure:
    temp = df.dropna(subset=[xcol, ycol]).copy()
    xmid = temp[xcol].median()
    ymid = temp[ycol].median()
    fig = px.scatter(
        temp,
        x=xcol,
        y=ycol,
        size="population",
        color="risk_index",
        hover_name="province",
        color_continuous_scale=[COLORS["green"], COLORS["gold"], COLORS["red"]],
        title=title,
        size_max=42,
        labels=LABELS,
    )
    fig.add_vline(x=xmid, line_dash="dash", line_color="rgba(237,229,214,.42)")
    fig.add_hline(y=ymid, line_dash="dash", line_color="rgba(237,229,214,.42)")
    fig.add_annotation(x=xmid, y=ymid, text="median", showarrow=False, font={"size": 11})
    mark_focus(fig, temp, focus, xcol, ycol)
    return fig_style(fig, 520)


def heat_map(df: pd.DataFrame, cols: list[str], names: list[str]) -> go.Figure:
    temp = df[["province"] + cols].copy().dropna(how="all", subset=cols)
    show = temp.sort_values("risk_index", ascending=False).head(18)
    matrix = show[cols].copy()
    matrix = (matrix - matrix.min()) / (matrix.max() - matrix.min())
    fig = go.Figure(
        go.Heatmap(
            z=matrix.T,
            x=show["province"],
            y=names,
            colorscale=[[0, COLORS["blue"]], [.5, COLORS["gold"]], [1, COLORS["red"]]],
            hovertemplate="%{y}<br>%{x}<br>skor relatif %{z:.2f}<extra></extra>",
        )
    )
    fig.update_layout(title="Matriks panas provinsi prioritas")
    return fig_style(fig, 520)


def sankey_flow(row: pd.Series) -> go.Figure:
    labels = ["Belanja pangan", "Rokok", "Gizi esensial", "Sayur", "Ikan", "Telur & susu", "Daging", "Buah"]
    values = [row["rokok"], row["gizi_total"], row["sayur"], row["ikan"], row["telur_susu"], row["daging"], row["buah"]]
    fig = go.Figure(
        go.Sankey(
            node={"label": labels, "pad": 18, "thickness": 18, "color": [COLORS["paper"], COLORS["red"], COLORS["gold"], COLORS["green"], COLORS["blue"], "#C9B26D", "#A66A3F", "#D99C52"]},
            link={
                "source": [0, 0, 2, 2, 2, 2, 2],
                "target": [1, 2, 3, 4, 5, 6, 7],
                "value": values,
                "color": ["rgba(192,39,45,.55)", "rgba(218,165,32,.35)", "rgba(111,175,78,.35)", "rgba(203,213,227,.35)", "rgba(201,178,109,.35)", "rgba(166,106,63,.35)", "rgba(217,156,82,.35)"],
            },
        )
    )
    fig.update_layout(title=f"Aliran belanja di {row['province']}")
    return fig_style(fig, 430)


def tree_map(row: pd.Series) -> go.Figure:
    data = pd.DataFrame(
        {
            "item": ["Rokok", "Sayur", "Ikan", "Telur & susu", "Daging", "Buah"],
            "group": ["Rokok", "Gizi", "Gizi", "Gizi", "Gizi", "Gizi"],
            "value": [row["rokok"], row["sayur"], row["ikan"], row["telur_susu"], row["daging"], row["buah"]],
        }
    )
    fig = px.treemap(
        data,
        path=["group", "item"],
        values="value",
        color="group",
        color_discrete_map={"Rokok": COLORS["red"], "Gizi": COLORS["gold"]},
        title=f"Ukuran kantong belanja di {row['province']}",
    )
    return fig_style(fig, 430)


def slope_chart(row: pd.Series) -> go.Figure:
    items = ["Sayur", "Ikan", "Telur & susu", "Daging", "Buah", "Gizi total"]
    values = [row["sayur"], row["ikan"], row["telur_susu"], row["daging"], row["buah"], row["gizi_total"]]
    fig = go.Figure()
    for item, value in zip(items, values):
        color = COLORS["red"] if row["rokok"] > value else COLORS["green"]
        fig.add_trace(
            go.Scatter(
                x=["Rokok", item],
                y=[row["rokok"], value],
                mode="lines+markers+text",
                text=[f"{row['rokok']:,.0f}", f"{value:,.0f}"],
                textposition="top center",
                line={"color": color, "width": 3},
                marker={"size": 9},
                name=item,
            )
        )
    fig.update_layout(title=f"Rokok dibanding tiap komponen gizi di {row['province']}", showlegend=True)
    return fig_style(fig, 480)


def parallel_plot(df: pd.DataFrame) -> go.Figure:
    cols = ["rokok_pct_of_gizi", "smoking_15_pct", "poverty_rate", "mad_6_23_pct", "stunting_0_59_total_pct"]
    temp = df.dropna(subset=[col for col in cols if col in df.columns]).copy()
    temp = temp.sort_values("risk_index", ascending=False).head(24)
    fig = px.parallel_coordinates(
        temp,
        dimensions=cols,
        color="risk_index",
        color_continuous_scale=[COLORS["green"], COLORS["gold"], COLORS["red"]],
        labels={
            "rokok_pct_of_gizi": "Rokok/Gizi",
            "smoking_15_pct": "Merokok 15+",
            "poverty_rate": "Miskin",
            "mad_6_23_pct": "MAD",
            "stunting_0_59_total_pct": "Stunting",
        },
        title="Jejak indikator pada 24 provinsi berisiko tinggi",
    )
    return fig_style(fig, 520)


def trend_line(df: pd.DataFrame, province: str) -> go.Figure:
    temp = df[df["province"].eq(province)].sort_values("year")
    fig = go.Figure()
    for col, name, color in [
        ("calorie_per_capita", "Kalori", COLORS["gold"]),
        ("protein_per_capita", "Protein", COLORS["green"]),
        ("poverty_rate", "Kemiskinan", COLORS["red"]),
        ("internet_pct", "Internet", COLORS["blue"]),
    ]:
        if col in temp:
            fig.add_trace(go.Scatter(x=temp["year"], y=temp[col], mode="lines+markers", name=name, line={"color": color, "width": 3}))
    fig.update_layout(title=f"Tren pendukung: {province}")
    return fig_style(fig, 460)


def whatif_bar(row: pd.Series, shift: float) -> go.Figure:
    moved = row["rokok"] * shift / 100
    base = pd.DataFrame(
        {
            "item": ["Sayur", "Ikan", "Telur & susu", "Daging", "Buah"],
            "awal": [row["sayur"], row["ikan"], row["telur_susu"], row["daging"], row["buah"]],
        }
    )
    base["simulasi"] = base["awal"] + moved / len(base)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=base["item"], y=base["awal"], name="Saat ini", marker_color=COLORS["gray"]))
    fig.add_trace(go.Bar(x=base["item"], y=base["simulasi"], name=f"Jika {shift:.0f}% rokok dialihkan", marker_color=COLORS["gold"]))
    fig.update_layout(title="Jika sebagian belanja rokok dipindahkan rata ke pangan gizi", barmode="group")
    return fig_style(fig, 430)
