from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from src.charts import (
    METRICS, altair_heatmap, behavior_sankey, bubble_map,
    composition_bar, distribution_hist, dot_components, dumbbell_compare,
    education_stack, global_benchmark, impact_sankey, kpi_stats,
    map_or_scatter, national_row, plate_donut, policy_matrix, price_lines,
    quadrant, radar_profile, ranking_bar, reallocation_chart, smoking_heatmap,
    sunburst_allocation, treemap_priority, waterfall_allocation,
)
from src.data import DashboardData, load_all_data
from src.theme import GRAPH_CONFIG
from src.util import percent, rupiah

st.set_page_config(
    page_title="Rokok Nomor Satu, Gizi Lain Waktu",
    page_icon="🚬",
    layout="wide",
    initial_sidebar_state="expanded",
)
alt.themes.enable("dark")

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""<style>
html,body,[class*="css"]{font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif;}
.main .block-container{max-width:1760px;padding:1.2rem 1.4rem 2rem;}

/* Full flex stretch — no dead space in any container */
[data-testid="stHorizontalBlock"]{align-items:stretch;}
[data-testid="stColumn"]{display:flex;flex-direction:column;}
[data-testid="stColumn"]>[data-testid="stVerticalBlock"]{flex:1;display:flex;flex-direction:column;}
[data-testid="stVerticalBlock"]{display:flex;flex-direction:column;}
[data-testid="element-container"]{display:flex;flex-direction:column;}
[data-testid="element-container"]:has([data-testid="stPlotlyChart"]){flex:1;min-height:0;}
[data-testid="element-container"]:has([data-testid="stVegaLiteChart"]){flex:1;min-height:0;}
[data-testid="stPlotlyChart"]{flex:1;display:flex;flex-direction:column;min-height:180px;background:#0d181c;border-radius:6px;}
[data-testid="stPlotlyChart"]>div{flex:1;display:flex;flex-direction:column;}
[data-testid="stPlotlyChart"] .js-plotly-plot,
[data-testid="stPlotlyChart"] .plot-container,
[data-testid="stPlotlyChart"] .plotly,
[data-testid="stPlotlyChart"] .svg-container{flex:1;height:100%!important;}
[data-testid="stVegaLiteChart"]{flex:1;min-height:180px;}

[data-testid="stMetric"]{background-color:#18282e;text-align:center;padding:14px 8px;border-radius:8px;}
[data-testid="stMetricLabel"]{display:flex;justify-content:center;align-items:center;}
[data-testid="stMetricDeltaIcon-Up"],[data-testid="stMetricDeltaIcon-Down"]{position:relative;left:38%;transform:translateX(-50%);}

.app-hero{padding:.1rem 0 1rem;border-bottom:1px solid rgba(236,230,215,.10);margin-bottom:.6rem;}
.app-hero h1{margin:0;font-size:clamp(1.9rem,3.2vw,3.5rem);font-weight:900;line-height:1.02;display:flex;align-items:center;gap:.55rem;}
.app-hero p{margin:.4rem 0 0;color:rgba(242,234,219,.62);max-width:860px;line-height:1.55;}
.hero-row{display:flex;gap:1.6rem;margin-top:.85rem;padding-top:.7rem;border-top:1px solid rgba(236,230,215,.10);flex-wrap:wrap;}
.hero-stat{display:flex;flex-direction:column;}
.hs-val{font-size:clamp(1.5rem,2.2vw,2.4rem);font-weight:900;line-height:1;color:#ead27a;}
.hero-stat:first-child .hs-val{color:#e55348;}
.hs-lbl{margin-top:.2rem;font-size:.73rem;color:rgba(242,234,219,.52);max-width:13rem;line-height:1.3;}

.sec-label{font-size:.72rem;font-weight:900;letter-spacing:.09em;text-transform:uppercase;color:#ead27a;margin:0;display:flex;align-items:center;gap:.3rem;}
.sec-title{font-size:clamp(1.35rem,1.8vw,2rem);font-weight:900;margin:.18rem 0 .12rem;}
.sec-sub{font-size:.86rem;color:rgba(242,234,219,.58);margin:0;}

.insight-box{padding:.6rem .8rem;border-radius:6px;background:rgba(236,230,215,.05);margin-bottom:.45rem;}
.insight-box strong{display:flex;align-items:center;gap:.3rem;color:#ead27a;font-size:.88rem;margin-bottom:.2rem;}
.insight-box p{margin:0;font-size:.81rem;color:rgba(242,234,219,.60);line-height:1.4;}

.sidebar-brand{display:flex;align-items:center;gap:.5rem;margin-bottom:.15rem;}
.sidebar-brand span{font-size:1.05rem;font-weight:900;color:#f1ddad;}

.stTabs [data-baseweb="tab-list"]{gap:.3rem;border:1px solid rgba(236,230,215,.12);border-radius:8px;background:rgba(14,23,27,.78);padding:.3rem;}
.stTabs [data-baseweb="tab"]{border-radius:6px;font-weight:700;}
.stTabs [aria-selected="true"]{color:#fff;background:linear-gradient(180deg,#c54748,#8e2a2d);}

.footer-bar{margin-top:1.8rem;padding:.75rem 1rem;text-align:center;border:1px solid rgba(236,230,215,.08);border-radius:8px;font-size:.72rem;color:rgba(242,234,219,.38);}
</style>""", unsafe_allow_html=True)


# ── Lucide icon helpers ───────────────────────────────────────────────────────
def _icon(paths: str, size: int = 14, color: str = "#ead27a") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0">'
            f'{paths}</svg>')

_IC = {
    "cigarette":    '<path d="M18 12H2v4h16"/><path d="M22 12v4"/><path d="M7 12v4"/>'
                    '<path d="M18 8c0-2.5-2-2.5-2-5"/><path d="M22 8c0-2.5-2-2.5-2-5"/>',
    "map":          '<polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/>'
                    '<line x1="9" x2="9" y1="3" y2="18"/><line x1="15" x2="15" y1="6" y2="21"/>',
    "map-pin":      '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>'
                    '<circle cx="12" cy="10" r="3"/>',
    "search":       '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "clipboard":    '<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/>'
                    '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>'
                    '<path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/>',
    "trending-down": '<polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/>'
                    '<polyline points="16 17 22 17 22 11"/>',
    "alert":        '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/>'
                    '<path d="M12 9v4"/><path d="M12 17h.01"/>',
    "activity":     '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "lightbulb":    '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/>'
                    '<path d="M9 18h6"/><path d="M10 22h4"/>',
}


# ── data ─────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Memuat data…")
def get_data() -> DashboardData:
    return load_all_data()


def row_for(data: DashboardData, province: str | None) -> pd.Series:
    df = data.metrics
    part = df[df["province"].eq(province or data.default_province)]
    return part.iloc[0] if not part.empty else df.sort_values("rokok_pct_of_gizi", ascending=False).iloc[0]


# ── rendering helpers ────────────────────────────────────────────────────────
def plot(fig, height: int | None = None) -> None:
    if height is not None:
        fig.update_layout(height=height, autosize=False)
    st.plotly_chart(fig, use_container_width=True, config=GRAPH_CONFIG)


def insight(title: str, body: str, icon: str = "activity") -> None:
    ic = _icon(_IC.get(icon, _IC["activity"]), 13)
    st.markdown(
        f'<div class="insight-box"><strong>{ic}{title}</strong><p>{body}</p></div>',
        unsafe_allow_html=True,
    )


def section(kicker: str, title: str, sub: str, icon: str = "activity") -> None:
    ic = _icon(_IC.get(icon, _IC["activity"]), 13)
    st.markdown(
        f'<p class="sec-label">{ic}{kicker}</p>'
        f'<p class="sec-title">{title}</p>'
        f'<p class="sec-sub">{sub}</p>',
        unsafe_allow_html=True,
    )


def hero(stats: dict) -> None:
    r, n_gt, n = percent(stats["avg_ratio"]), stats["count_rokok_gt_sayur"], stats["n"]
    cig = _icon(_IC["cigarette"], 36, "#e55348")
    st.markdown(
        f"""<div class="app-hero">
<h1>{cig}Rokok Nomor Satu, Gizi Lain Waktu</h1>
<p>Dashboard visualisasi data tentang paradoks pengeluaran pangan rumah tangga Indonesia 2024 —
rokok berdiri di piring yang sama dengan protein, sayur, buah, dan pangan bergizi lain.</p>
<div class="hero-row">
  <div class="hero-stat"><span class="hs-val">{r}</span><span class="hs-lbl">porsi rokok dari total belanja gizi nasional</span></div>
  <div class="hero-stat"><span class="hs-val">{n_gt}/{n}</span><span class="hs-lbl">provinsi: belanja rokok melebihi sayur</span></div>
  <div class="hero-stat"><span class="hs-val">{rupiah(stats['avg_rokok'])}</span><span class="hs-lbl">rata-rata belanja rokok per kapita/bulan</span></div>
</div></div>""",
        unsafe_allow_html=True,
    )


def sidebar(data: DashboardData) -> tuple[str, str, str, int]:
    with st.sidebar:
        cig = _icon(_IC["cigarette"], 20, "#e55348")
        st.markdown(
            f'<div class="sidebar-brand">{cig}<span>Rokok vs Gizi ID</span></div>',
            unsafe_allow_html=True,
        )
        st.caption("Dashboard interaktif IF4061 — 2024")
        st.divider()
        province = st.selectbox(
            "Provinsi fokus", data.provinces,
            index=data.provinces.index(data.default_province)
            if data.default_province in data.provinces else 0,
        )
        metric_label = st.selectbox("Metrik peta", list(METRICS), index=0)
        compare = st.selectbox("Pembanding",
            ["Nasional", "Kemiskinan mirip", "Protein mirip", "PDRB mirip"])
        reallocation = st.slider("Realokasi belanja rokok", 0, 50, 25, 5, format="%d%%")
        st.divider()
        st.caption("BPS/SUSENAS 2024 · SKI 2023 · WHO GATS 2021 · World Bank")
    return province, METRICS[metric_label], compare, reallocation


# ── pages ────────────────────────────────────────────────────────────────────

def page_indonesia(data: DashboardData, metric: str, province: str) -> None:
    df = data.metrics
    nat = national_row(df)
    stats = kpi_stats(df)
    top = df.sort_values("rokok_pct_of_gizi", ascending=False).iloc[0]

    section("Halaman 1", "Indonesia: The National Shock",
            "Fakta nasional, peta risiko, distribusi provinsi, dan komponen gizi yang kalah dari rokok.",
            icon="map")

    # ── KPI strip (above main charts) ────────────────────────────────────────
    k1, k2, k3 = st.columns(3, gap="small")
    k1.metric("Rokok > Sayur",  f"{stats['count_rokok_gt_sayur']}/{stats['n']} prov.")
    k2.metric("Rokok > Daging", f"{stats['count_rokok_gt_daging']}/{stats['n']} prov.")
    k3.metric("Avg Rokok/Gizi", percent(stats["avg_ratio"]))

    # ── main row: each col = label + one chart at H ───────────────────────────
    H = 500
    col = st.columns((1.5, 4.5, 2), gap="medium")
    with col[0]:
        st.markdown("**Komposisi Nasional**")
        plot(plate_donut(nat, "Komposisi Nasional"), height=H)
    with col[1]:
        st.markdown("**Peta Risiko Indonesia**")
        plot(map_or_scatter(df, data.geojson, metric, province, "Peta Indonesia", H))
    with col[2]:
        st.markdown("**Ranking Provinsi**")
        plot(ranking_bar(df, "rokok_pct_of_gizi", province, 8, "Top 8 Rasio Rokok/Gizi"), height=H)

    # ── insights (below main charts) ─────────────────────────────────────────
    i1, i2 = st.columns(2, gap="medium")
    with i1: insight("Provinsi tertinggi",
                     f"{top['province']} — rasio {percent(top['rokok_pct_of_gizi'])}")
    with i2: insight("Gap belanja",
                     f"Rokok {rupiah(stats['avg_rokok'])} vs Sayur {rupiah(stats['avg_sayur'])}")

    # ── secondary row: distribution | dot | treemap ──────────────────────────
    st.divider()
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1: plot(distribution_hist(df, "rokok_pct_of_gizi"), height=290)
    with c2: plot(dot_components(nat), height=290)
    with c3: plot(treemap_priority(df), height=290)


def peers_for(df: pd.DataFrame, row: pd.Series, compare: str) -> pd.DataFrame:
    if compare == "Kemiskinan mirip":
        return df.assign(d=(df["poverty_rate"] - row["poverty_rate"]).abs()).sort_values("d").head(8)
    if compare == "Protein mirip":
        return df.assign(d=(df["protein_per_capita"] - row["protein_per_capita"]).abs()).sort_values("d").head(8)
    if compare == "PDRB mirip":
        return df.assign(d=(df["pdrb_capita_thousand"] - row["pdrb_capita_thousand"]).abs()).sort_values("d").head(8)
    return df.sort_values("rokok_pct_of_gizi", ascending=False).head(8)


def page_provinsi(data: DashboardData, province: str, compare: str, reallocation: int) -> None:
    df = data.metrics
    row = row_for(data, province)
    province = row["province"]
    peers = peers_for(df, row, compare)

    section("Halaman 2", f"Provinsi: {province}",
            "Diagnosis lokal: struktur pengeluaran, posisi nasional, peer comparison, dan simulasi realokasi.",
            icon="map-pin")

    # ── KPI strip ────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
    k1.metric("Rokok/kapita",  rupiah(row["rokok"]))
    k2.metric("Rokok/Gizi",   percent(row["rokok_pct_of_gizi"]), f"#{int(row['rank_rokok_gizi'])}")
    k3.metric("Protein",      f"{row['protein_per_capita']:.1f} g")
    k4.metric("Kalori",       f"{row['calorie_per_capita']:.0f} kkal")
    k5.metric("Kemiskinan",   percent(row["poverty_rate"]))
    k6.metric("Stunting",     percent(row["stunting_0_59_total_pct"]))

    # ── main row: each col = label + chart(s) summing to H ───────────────────
    H = 500
    st.write("")
    col = st.columns((1.5, 4, 2.5), gap="medium")
    with col[0]:
        st.markdown("**Komposisi Pengeluaran**")
        plot(plate_donut(row, province), height=H)
    with col[1]:
        st.markdown(f"**Peta Fokus: {province}**")
        plot(map_or_scatter(df, data.geojson, "rokok_pct_of_gizi", province, f"Fokus: {province}", H))
    with col[2]:
        st.markdown("**Profil Risiko**")
        plot(radar_profile(row, df), height=300)
        plot(dumbbell_compare(df, row), height=200)

    # ── insights (below main charts) ─────────────────────────────────────────
    i1, i2 = st.columns(2, gap="medium")
    with i1: insight("Opportunity cost",
                     f"{reallocation}% rokok = {rupiah(row['rokok'] * reallocation / 100)}/kapita/bln")
    with i2: insight("Status data", str(row.get("source_status", "observed")))

    # ── detail row: waterfall | composition | reallocation | ranking ─────────
    st.divider()
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1: plot(waterfall_allocation(row), height=280)
    with c2: plot(composition_bar(row), height=280)
    with c3: plot(reallocation_chart(row, reallocation), height=280)
    with c4: plot(quadrant(df, province, "rokok_pct_of_gizi", "protein_per_capita",
                           "poverty_rate", "Rokok/Gizi vs Protein"), height=280)

    # ── peer comparison ──────────────────────────────────────────────────────
    st.divider()
    plot(ranking_bar(peers, "rokok_pct_of_gizi", province, min(8, len(peers)),
                     f"Peer comparison: {compare}"), height=300)


def page_penyebab(data: DashboardData, province: str) -> None:
    df = data.metrics
    row = row_for(data, province)
    province = row["province"]

    section("Halaman 3", "Penyebab: Ekonomi, Perilaku, Harga, Akses",
            "Lensa eksploratif. Korelasi bukan klaim kausal.", icon="search")

    # ── main row: sankey | big scatter | insights ─────────────────────────
    col = st.columns((1.5, 4.5, 2), gap="medium")
    with col[0]:
        st.markdown("**Alur Perilaku**")
        plot(behavior_sankey(), height=480)
    with col[1]:
        st.markdown("**Kemiskinan vs Konsumsi Rokok**")
        plot(quadrant(df, province, "poverty_rate", "rokok_pct_of_gizi",
                      "protein_per_capita", "Kemiskinan vs Rokok/Gizi"), height=480)
    with col[2]:
        st.markdown("**Temuan Kunci**")
        insight("Tekanan ekonomi",
                "Kemiskinan dan ketimpangan memperberat trade-off pangan vs rokok.")
        insight("Perilaku merokok",
                "Paparan rokok mengubah ruang belanja rumah tangga secara signifikan.")
        insight("Harga relatif",
                "Indeks harga rokok naik jauh lebih cepat dari pangan bergizi.")

        st.metric("Belanja rokok fokus", rupiah(row["rokok"]),
                  help="Belanja rokok per kapita per bulan provinsi terpilih")

    # ── secondary: heatmap | education | price ───────────────────────────────
    st.divider()
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1: plot(smoking_heatmap(), height=300)
    with c2: plot(education_stack(), height=300)
    with c3: plot(price_lines(data.price_trends), height=300)

    # ── tertiary: digital | engel ─────────────────────────────────────────────
    st.divider()
    c1, c2 = st.columns(2, gap="medium")
    with c1: plot(quadrant(df, province, "digital_index_pct", "rokok_pct_of_gizi",
                           "poverty_rate", "Akses Digital vs Rokok/Gizi"), height=320)
    with c2: plot(quadrant(df, province, "engel_ratio", "protein_per_capita",
                           "rokok_pct_of_gizi", "Tekanan Pangan vs Protein"), height=320)


def page_dampak(data: DashboardData, province: str) -> None:
    df = data.metrics
    row = row_for(data, province)
    nat = national_row(df)

    section("Halaman 4", "Dampak, Global Benchmark & Prioritas Kebijakan",
            "Penutup narasi: dampak kesehatan-ekonomi, benchmarking, peta prioritas, dan rekomendasi aksi.",
            icon="clipboard")

    # ── main row: KPIs+recs | big priority map | table ───────────────────────
    col = st.columns((1.5, 4.5, 2), gap="medium")
    with col[0]:
        st.markdown("**Indikator Dampak**")
        st.metric("Indonesia vs ASEAN", percent(df["rokok_pct_of_gizi"].mean()))
        st.metric("Opportunity cost",   rupiah(df["rokok"].mean()))
        st.metric("Prov. prioritas",    int((df["policy_priority_index"] >= 60).sum()))
        st.metric("Fokus saat ini",     row["province"], row["risk_label"])

        with st.expander("Rekomendasi kebijakan", expanded=True):
            st.caption("1. **Cukai + edukasi** — naikkan biaya rokok, dukung layanan berhenti merokok.")
            st.caption("2. **Bantuan pangan bergizi** — prioritaskan provinsi rokok tinggi + gizi rendah.")
            st.caption("3. **Monitoring berkala** — pantau indikator rokok, gizi, dan kesehatan anak.")
    with col[1]:
        st.markdown("**Peta Prioritas Kebijakan**")
        plot(map_or_scatter(df, data.geojson, "policy_priority_index",
                            row["province"], "Policy Priority Index", 500))
    with col[2]:
        st.markdown("**Top 10 Provinsi Prioritas**")
        priority = (
            df.sort_values("policy_priority_index", ascending=False)
            .head(10)[["province", "policy_priority_index",
                       "rokok_pct_of_gizi", "stunting_0_59_total_pct",
                       "poverty_rate", "risk_label"]]
            .round(2)
            .rename(columns={
                "province": "Provinsi", "policy_priority_index": "Prioritas",
                "rokok_pct_of_gizi": "Rokok/Gizi%",
                "stunting_0_59_total_pct": "Stunting%",
                "poverty_rate": "Kemiskinan%", "risk_label": "Label",
            })
        )
        st.dataframe(
            priority, use_container_width=True, hide_index=True,
            column_config={
                "Prioritas": st.column_config.ProgressColumn(
                    "Prioritas", min_value=0, max_value=100, format="%.1f"),
            },
        )

    # ── secondary: benchmark | scatter | reallocation ────────────────────────
    st.divider()
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1: plot(global_benchmark(), height=300)
    with c2: plot(quadrant(df, row["province"], "rokok_pct_of_gizi",
                           "stunting_0_59_total_pct", "poverty_rate",
                           "Rokok/Gizi vs Stunting"), height=300)
    with c3: plot(reallocation_chart(nat, 25), height=300)

    # ── tertiary: impact sankey | policy matrix | heatmap ────────────────────
    st.divider()
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1: plot(impact_sankey(nat), height=320)
    with c2: plot(policy_matrix(), height=320)
    with c3:
        st.altair_chart(altair_heatmap(df), use_container_width=True)


def footer() -> None:
    st.markdown(
        '<div class="footer-bar">Sumber: BPS/SUSENAS 2024 · SKI 2023 · WHO GATS 2021 · World Bank'
        " &nbsp;|&nbsp; Streamlit · Plotly · Altair</div>",
        unsafe_allow_html=True,
    )


# ── entry point ───────────────────────────────────────────────────────────────
def main() -> None:
    data = get_data()
    stats = kpi_stats(data.metrics)
    province, metric, compare, reallocation = sidebar(data)
    hero(stats)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Indonesia", "Provinsi", "Penyebab", "Dampak & Kebijakan"]
    )
    with tab1: page_indonesia(data, metric, province)
    with tab2: page_provinsi(data, province, compare, reallocation)
    with tab3: page_penyebab(data, province)
    with tab4: page_dampak(data, province)
    footer()


if __name__ == "__main__":
    main()
