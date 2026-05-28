from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import (
    METRICS,
    behavior_sankey,
    bubble_map,
    composition_bar,
    distribution_hist,
    dot_components,
    dumbbell_compare,
    education_stack,
    global_benchmark,
    impact_sankey,
    kpi_stats,
    map_or_scatter,
    national_row,
    plate_donut,
    policy_matrix,
    price_lines,
    quadrant,
    radar_profile,
    ranking_bar,
    reallocation_chart,
    smoking_heatmap,
    sunburst_allocation,
    treemap_priority,
    waterfall_allocation,
)
from src.data import DashboardData, load_all_data
from src.theme import GRAPH_CONFIG
from src.util import percent, rupiah


st.set_page_config(
    page_title="Rokok Nomor Satu, Gizi Lain Waktu",
    page_icon="R",
    layout="wide",
    initial_sidebar_state="expanded",
)


PAGE_OPTIONS = {
    "Indonesia": "indonesia",
    "Provinsi": "provinsi",
    "Penyebab": "penyebab",
    "Dampak & Kebijakan": "dampak",
}


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
          --bg: #0b1114;
          --panel: #142126;
          --panel-2: #18282e;
          --line: rgba(236, 230, 215, .13);
          --text: #f2eadb;
          --muted: #b2b6ae;
          --cream: #f1ddad;
          --red: #bd3437;
          --red-hot: #e55348;
          --gold: #c69a3a;
          --gold-light: #ead27a;
        }

        html, body, [class*="css"] {
          font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .stApp {
          color: var(--text);
          background:
            linear-gradient(180deg, rgba(189, 52, 55, .08), transparent 340px),
            linear-gradient(135deg, #0b1114 0%, #111a1d 48%, #0c1215 100%);
        }

        .main .block-container {
          max-width: 1760px;
          padding: 1.25rem 1.35rem 2.2rem;
        }

        section[data-testid="stSidebar"] {
          background: #0e171b;
          border-right: 1px solid var(--line);
        }

        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p {
          color: rgba(242, 234, 219, .78);
        }

        h1, h2, h3 {
          letter-spacing: 0;
        }

        .app-hero {
          display: grid;
          grid-template-columns: minmax(0, 1fr) auto;
          gap: 1rem;
          align-items: end;
          padding: .15rem 0 1.1rem;
          border-bottom: 1px solid rgba(236, 230, 215, .10);
          margin-bottom: 1rem;
        }

        .app-hero h1 {
          margin: 0;
          color: var(--cream);
          font-size: clamp(2rem, 3.5vw, 4rem);
          line-height: 1.02;
          font-weight: 900;
        }

        .app-hero p {
          margin: .55rem 0 0;
          color: rgba(242, 234, 219, .70);
          max-width: 920px;
          line-height: 1.55;
        }

        .hero-meta {
          display: flex;
          flex-wrap: wrap;
          justify-content: flex-end;
          gap: .45rem;
        }

        .meta-pill {
          display: inline-flex;
          min-height: 34px;
          align-items: center;
          padding: 0 .72rem;
          border: 1px solid rgba(236, 230, 215, .20);
          border-radius: 8px;
          background: rgba(20, 33, 38, .74);
          color: rgba(242, 234, 219, .76);
          font-size: .76rem;
          font-weight: 800;
        }

        .meta-pill.accent {
          border-color: rgba(198, 154, 58, .45);
          color: var(--gold-light);
        }

        .section-title {
          margin: .55rem 0 1rem;
        }

        .section-title span {
          color: var(--gold-light);
          font-size: .78rem;
          font-weight: 900;
          text-transform: uppercase;
          letter-spacing: .09em;
        }

        .section-title h2 {
          margin: .25rem 0 .2rem;
          color: var(--text);
          font-size: clamp(1.55rem, 2.1vw, 2.35rem);
          line-height: 1.08;
          font-weight: 900;
        }

        .section-title p {
          margin: 0;
          color: rgba(242, 234, 219, .68);
        }

        div[data-testid="stMetric"] {
          min-height: 106px;
          padding: .9rem .95rem;
          border: 1px solid var(--line);
          border-radius: 8px;
          background: linear-gradient(155deg, rgba(24, 40, 46, .98), rgba(16, 25, 29, .98));
          box-shadow: 0 12px 32px rgba(0, 0, 0, .18);
        }

        div[data-testid="stMetricLabel"] {
          color: rgba(242, 234, 219, .72);
          font-weight: 800;
        }

        div[data-testid="stMetricValue"] {
          color: var(--gold-light);
          font-weight: 900;
        }

        div[data-testid="stPlotlyChart"] {
          border: 1px solid var(--line);
          border-radius: 8px;
          background: linear-gradient(155deg, rgba(20, 33, 38, .98), rgba(12, 20, 24, .98));
          box-shadow: 0 14px 34px rgba(0, 0, 0, .18);
          padding: .35rem;
        }

        .insight-card {
          min-height: 122px;
          padding: .95rem 1rem;
          border: 1px solid var(--line);
          border-radius: 8px;
          background: rgba(20, 33, 38, .72);
        }

        .insight-card strong {
          display: block;
          color: var(--gold-light);
          margin-bottom: .28rem;
        }

        .insight-card p {
          margin: 0;
          color: rgba(242, 234, 219, .72);
          line-height: 1.48;
        }

        .stTabs [data-baseweb="tab-list"] {
          gap: .35rem;
          border: 1px solid rgba(236, 230, 215, .12);
          border-radius: 8px;
          background: rgba(14, 23, 27, .78);
          padding: .35rem;
        }

        .stTabs [data-baseweb="tab"] {
          border-radius: 7px;
          color: rgba(242, 234, 219, .72);
          font-weight: 800;
        }

        .stTabs [aria-selected="true"] {
          color: white;
          background: linear-gradient(180deg, #c54748 0%, #8e2a2d 100%);
        }

        .dataframe {
          border-radius: 8px;
          overflow: hidden;
        }

        @media (max-width: 900px) {
          .app-hero {
            grid-template-columns: 1fr;
          }
          .hero-meta {
            justify-content: flex-start;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner="Memuat data dashboard...")
def get_data() -> DashboardData:
    return load_all_data()


def row_for(data: DashboardData, province: str | None) -> pd.Series:
    df = data.metrics
    value = province or data.default_province
    part = df[df["province"].eq(value)]
    if part.empty:
        return df.sort_values("rokok_pct_of_gizi", ascending=False).iloc[0]
    return part.iloc[0]


def plot(fig) -> None:
    st.plotly_chart(fig, width="stretch", config=GRAPH_CONFIG)


def section(kicker: str, title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="section-title">
          <span>{kicker}</span>
          <h2>{title}</h2>
          <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="insight-card">
          <strong>{title}</strong>
          <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero() -> None:
    st.markdown(
        """
        <div class="app-hero">
          <div>
            <h1>Rokok Nomor Satu, Gizi Lain Waktu</h1>
            <p>Dashboard visualisasi data tentang paradoks pengeluaran pangan rumah tangga Indonesia 2024: rokok berdiri di piring yang sama dengan protein, sayur, buah, dan pangan bergizi lain.</p>
          </div>
          <div class="hero-meta">
            <span class="meta-pill">2024</span>
            <span class="meta-pill">38 provinsi</span>
            <span class="meta-pill accent">BPS/SKI</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar(data: DashboardData) -> tuple[str, str, str, str, int]:
    st.sidebar.title("Panel Kontrol")
    page = st.sidebar.radio("Halaman", list(PAGE_OPTIONS), index=0)
    province = st.sidebar.selectbox(
        "Provinsi fokus",
        data.provinces,
        index=data.provinces.index(data.default_province) if data.default_province in data.provinces else 0,
    )
    metric_label = st.sidebar.selectbox("Metrik peta", list(METRICS), index=0)
    compare = st.sidebar.selectbox("Pembanding", ["Nasional", "Kemiskinan mirip", "Protein mirip", "PDRB mirip"], index=0)
    reallocation = st.sidebar.slider("Realokasi belanja rokok", min_value=0, max_value=50, value=25, step=5, format="%d%%")
    st.sidebar.caption("Sumber: BPS/SUSENAS 2024, SKI 2023 curated, WHO GATS 2021, World Bank affordability.")
    return PAGE_OPTIONS[page], province, METRICS[metric_label], compare, reallocation


def render_kpis(stats: dict) -> None:
    cols = st.columns(6)
    cols[0].metric(f"{stats['count_rokok_gt_sayur']}/{stats['n']} provinsi", "Rokok > Sayur")
    cols[1].metric(f"{stats['count_rokok_gt_daging']}/{stats['n']} provinsi", "Rokok > Daging")
    cols[2].metric("Rokok/Gizi total", percent(stats["avg_ratio"]))
    cols[3].metric("Rata-rata rokok", rupiah(stats["avg_rokok"]))
    cols[4].metric("Rata-rata sayur", rupiah(stats["avg_sayur"]))
    cols[5].metric("Gap rokok vs sayur", rupiah(stats["gap_rokok_sayur"]))


def page_indonesia(data: DashboardData, metric: str, province: str) -> None:
    df = data.metrics
    nat = national_row(df)
    stats = kpi_stats(df)
    top = df.sort_values("rokok_pct_of_gizi", ascending=False).iloc[0]

    section("Page 1", "Indonesia: The National Shock", "Fakta nasional, peta risiko, distribusi provinsi, dan komponen gizi yang kalah dari rokok.")
    render_kpis(stats)

    c1, c2, c3 = st.columns([1, 1.12, 1])
    with c1:
        plot(plate_donut(nat, "Nasional"))
    with c2:
        plot(map_or_scatter(df, data.geojson, metric, province, "Peta Indonesia", 430))
    with c3:
        plot(ranking_bar(df, "rokok_pct_of_gizi", province, 5, "Top 5 rasio rokok/gizi"))

    c1, c2, c3 = st.columns(3)
    with c1:
        plot(distribution_hist(df, "rokok_pct_of_gizi"))
    with c2:
        plot(dot_components(nat))
    with c3:
        insight("Rokok menjadi prioritas belanja pangan terbesar", f"Rata-rata belanja rokok {rupiah(stats['avg_rokok'])}, sedangkan sayur {rupiah(stats['avg_sayur'])}.")
        insight("Provinsi tertinggi", f"{top['province']} memiliki rasio rokok/gizi {percent(top['rokok_pct_of_gizi'])}.")

    c1, c2, c3 = st.columns(3)
    with c1:
        plot(sunburst_allocation(nat))
    with c2:
        plot(treemap_priority(df))
    with c3:
        plot(bubble_map(df))


def peers_for(df: pd.DataFrame, row: pd.Series, compare: str) -> pd.DataFrame:
    peers = df.copy()
    if compare == "Kemiskinan mirip":
        return peers.assign(distance=(peers["poverty_rate"] - row["poverty_rate"]).abs()).sort_values("distance").head(8)
    if compare == "Protein mirip":
        return peers.assign(distance=(peers["protein_per_capita"] - row["protein_per_capita"]).abs()).sort_values("distance").head(8)
    if compare == "PDRB mirip":
        return peers.assign(distance=(peers["pdrb_capita_thousand"] - row["pdrb_capita_thousand"]).abs()).sort_values("distance").head(8)
    return peers.sort_values("rokok_pct_of_gizi", ascending=False).head(8)


def page_provinsi(data: DashboardData, province: str, compare: str, reallocation: int) -> None:
    df = data.metrics
    row = row_for(data, province)
    province = row["province"]
    peers = peers_for(df, row, compare)

    section("Page 2", f"Provinsi: {province}", "Diagnosis lokal: struktur pengeluaran, posisi nasional, peer comparison, dan simulasi realokasi.")
    cols = st.columns(6)
    cols[0].metric("Rokok per kapita", rupiah(row["rokok"]))
    cols[1].metric("Rokok/Gizi total", percent(row["rokok_pct_of_gizi"]), f"Peringkat #{int(row['rank_rokok_gizi'])}")
    cols[2].metric("Protein", f"{row['protein_per_capita']:.1f} g")
    cols[3].metric("Kalori", f"{row['calorie_per_capita']:.0f} kkal")
    cols[4].metric("Kemiskinan", percent(row["poverty_rate"]))
    cols[5].metric("Stunting", percent(row["stunting_0_59_total_pct"]))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        plot(map_or_scatter(df, data.geojson, "rokok_pct_of_gizi", province, f"Fokus: {province}", 340))
    with c2:
        plot(waterfall_allocation(row))
    with c3:
        plot(composition_bar(row))
    with c4:
        plot(dumbbell_compare(df, row))

    c1, c2, c3 = st.columns(3)
    with c1:
        plot(quadrant(df, province, "rokok_pct_of_gizi", "protein_per_capita", "poverty_rate", "Rokok/Gizi vs Protein"))
    with c2:
        plot(reallocation_chart(row, reallocation))
    with c3:
        plot(radar_profile(row, df))

    c1, c2 = st.columns([1.15, .85])
    with c1:
        plot(ranking_bar(peers, "rokok_pct_of_gizi", province, min(8, len(peers)), f"Peer comparison: {compare}"))
    with c2:
        insight("Opportunity cost konkret", f"{reallocation}% belanja rokok setara {rupiah(row['rokok'] * reallocation / 100)} per kapita per bulan untuk pangan bergizi.")
        insight("Status data", str(row.get("source_status", "observed")))


def page_penyebab(data: DashboardData, province: str) -> None:
    df = data.metrics
    row = row_for(data, province)
    province = row["province"]

    section("Page 3", "Penyebab: Ekonomi, Perilaku, Harga, Akses", "Lensa eksploratif untuk membaca kemungkinan penyebab. Korelasi bukan klaim kausal.")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        plot(quadrant(df, province, "poverty_rate", "rokok_pct_of_gizi", "protein_per_capita", "Kemiskinan vs Rokok/Gizi"))
    with c2:
        plot(behavior_sankey())
    with c3:
        plot(smoking_heatmap())
    with c4:
        insight("Tekanan ekonomi", "Kemiskinan dan ketimpangan dapat memperberat trade-off pangan.")
        insight("Perilaku merokok", "Paparan rokok mengubah ruang belanja rumah tangga.")

    c1, c2, c3 = st.columns(3)
    with c1:
        plot(education_stack())
    with c2:
        plot(price_lines(data.price_trends))
    with c3:
        st.metric("Affordability meter", rupiah(row["rokok"]), f"25% realokasi = {rupiah(row['rokok'] * .25)}")

    c1, c2 = st.columns(2)
    with c1:
        plot(quadrant(df, province, "digital_index_pct", "rokok_pct_of_gizi", "poverty_rate", "Akses digital vs Rokok/Gizi"))
    with c2:
        plot(quadrant(df, province, "engel_ratio", "protein_per_capita", "rokok_pct_of_gizi", "Tekanan pangan vs Protein"))


def page_dampak(data: DashboardData, province: str) -> None:
    df = data.metrics
    row = row_for(data, province)
    nat = national_row(df)
    priority = (
        df.sort_values("policy_priority_index", ascending=False)
        .head(10)[["province", "policy_priority_index", "rokok_pct_of_gizi", "stunting_0_59_total_pct", "poverty_rate", "protein_per_capita", "risk_label"]]
        .round(2)
        .rename(
            columns={
                "province": "Provinsi",
                "policy_priority_index": "Prioritas",
                "rokok_pct_of_gizi": "Rokok/Gizi",
                "stunting_0_59_total_pct": "Stunting",
                "poverty_rate": "Kemiskinan",
                "protein_per_capita": "Protein",
                "risk_label": "Label Risiko",
            }
        )
    )

    section("Page 4", "Dampak, Global Benchmark, dan Prioritas Kebijakan", "Penutup narasi: dampak kesehatan-ekonomi, benchmarking, peta prioritas, dan rekomendasi aksi.")
    cols = st.columns(4)
    cols[0].metric("Indonesia vs ASEAN", percent(df["rokok_pct_of_gizi"].mean()))
    cols[1].metric("Opportunity cost", rupiah(df["rokok"].mean()))
    cols[2].metric("Provinsi prioritas", int((df["policy_priority_index"] >= 60).sum()))
    cols[3].metric("Fokus saat ini", row["province"], row["risk_label"])

    c1, c2, c3 = st.columns(3)
    with c1:
        plot(global_benchmark())
    with c2:
        plot(quadrant(df, row["province"], "rokok_pct_of_gizi", "stunting_0_59_total_pct", "poverty_rate", "Rokok/Gizi vs Stunting"))
    with c3:
        plot(reallocation_chart(nat, 25))

    c1, c2, c3 = st.columns([1.08, .9, 1.1])
    with c1:
        plot(map_or_scatter(df, data.geojson, "policy_priority_index", row["province"], "Policy priority index", 390))
    with c2:
        plot(policy_matrix())
    with c3:
        st.dataframe(priority, width="stretch", hide_index=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        plot(impact_sankey(nat))
    with c2:
        plot(treemap_priority(df))
    with c3:
        insight("1. Cukai + edukasi", "Naikkan biaya ekonomi rokok dan dukung layanan berhenti merokok.")
        insight("2. Bantuan pangan bergizi", "Prioritaskan provinsi dengan rokok tinggi dan gizi rendah.")
        insight("3. Monitoring data", "Evaluasi indikator rokok, gizi, dan kesehatan anak secara berkala.")


def main() -> None:
    inject_css()
    data = get_data()
    page, province, metric, compare, reallocation = sidebar(data)
    hero()

    if page == "provinsi":
        page_provinsi(data, province, compare, reallocation)
    elif page == "penyebab":
        page_penyebab(data, province)
    elif page == "dampak":
        page_dampak(data, province)
    else:
        page_indonesia(data, metric, province)


if __name__ == "__main__":
    main()
