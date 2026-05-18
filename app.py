from __future__ import annotations

import streamlit as st

from src.chart import (
    bi_map,
    city_bar,
    heat_map,
    make_donut,
    make_map,
    parallel_plot,
    rank_bar,
    sankey_flow,
    scatter_quad,
    slope_chart,
    tree_map,
    trend_line,
    whatif_bar,
)
from src.copy import LEAD, LINKS, SOURCES, SUBTITLE, TITLE
from src.data import bi_class, geo_data, load_city, load_data, load_trend
from src.theme import COLORS, page_css
from src.util import compact, percent, rupiah


st.set_page_config(
    page_title="Rokok Nomor Satu, Gizi Lain Waktu",
    page_icon="R",
    layout="wide",
)


@st.cache_data
def get_data():
    return load_data()


@st.cache_data
def get_trend():
    return load_trend()


@st.cache_data
def get_city():
    return load_city()


@st.cache_data
def get_geo():
    return geo_data()


def kpi_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="kpi">
            <small>{label}</small>
            <strong>{value}</strong>
            <span>{note}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def source_note(text: str) -> None:
    st.markdown(f"<p class='note'>{text}</p>", unsafe_allow_html=True)


def show_head() -> None:
    st.markdown(
        f"""
        <section class="hero">
            <h1><span class="gold">Rokok</span> <span class="paper">Nomor Satu,</span><br>
            <span class="gold">Gizi</span> <span class="paper">Lain Waktu</span></h1>
            <p class="lead">{LEAD}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


st.markdown(page_css(), unsafe_allow_html=True)
show_head()

df = get_data()
trend = get_trend()
city = get_city()
geo = get_geo()

metric_map = {
    "Rasio rokok terhadap gizi": "rokok_pct_of_gizi",
    "Prevalensi merokok 15+": "smoking_15_pct",
    "Merokok dalam rumah/ruangan": "smoking_indoor_pct",
    "Paparan asap harian": "passive_smoke_daily_pct",
    "Stunting balita": "stunting_0_59_total_pct",
    "Diet minimal anak": "mad_6_23_pct",
    "Protein hewani anak": "animal_protein_6_23_pct",
    "Indeks risiko gabungan": "risk_index",
}

province = st.sidebar.selectbox("Pilih provinsi", df["province"].tolist(), index=df["risk_index"].idxmax())
row = df[df["province"].eq(province)].iloc[0]
shift = st.sidebar.slider("Simulasi pengalihan belanja rokok", 0, 50, 15, 5)
map_label = st.sidebar.selectbox("Layer peta", list(metric_map.keys()))
map_col = metric_map[map_label]

national = df.mean(numeric_only=True)
worst = df.sort_values("risk_index", ascending=False).iloc[0]
best = df.sort_values("risk_index", ascending=True).iloc[0]

cols = st.columns(4)
with cols[0]:
    kpi_card("Belanja rokok rata-rata", rupiah(national["rokok"]), "per kapita per bulan, rata-rata provinsi")
with cols[1]:
    kpi_card("Rokok terhadap gizi", percent(national["rokok_pct_of_gizi"]), "dibanding sayur, ikan, buah, daging, telur-susu")
with cols[2]:
    kpi_card("Merokok 15+", percent(national["smoking_15_pct"]), "BPS 2024, penduduk umur 15 tahun ke atas")
with cols[3]:
    kpi_card("Risiko tertinggi", worst["province"], f"skor gabungan {percent(worst['risk_index'])}")

tabs = st.tabs(
    [
        "Cerita Utama",
        "Peta Risiko",
        "Trade-off",
        "Lensa SKI",
        "Drill-down",
        "Sosial Ekonomi",
        "Metodologi",
    ]
)

with tabs[0]:
    st.subheader("Satu meja makan, dua arah uang")
    source_note("Bagian ini menjaga nada poster statis, tetapi membukanya agar bisa diperiksa per provinsi.")
    left, right = st.columns([1.05, .95])
    with left:
        st.plotly_chart(make_donut(row), width="stretch")
    with right:
        st.plotly_chart(sankey_flow(row), width="stretch")
    left, right = st.columns([.9, 1.1])
    with left:
        st.plotly_chart(tree_map(row), width="stretch")
    with right:
        st.markdown(
            f"""
            <div class="block">
            <h3>{province}</h3>
            <p>Di provinsi ini, belanja rokok berada di <b>{rupiah(row['rokok'])}</b> per kapita per bulan.
            Angkanya setara <b>{percent(row['rokok_pct_of_gizi'])}</b> dari total lima komponen gizi esensial.</p>
            <p>Kalau sebagian kecil saja ruang belanja rokok bergeser, visual di bawah memperlihatkan seberapa besar
            tambahan yang bisa masuk ke kelompok pangan bergizi. Ini simulasi alokasi, bukan klaim sebab-akibat.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.plotly_chart(whatif_bar(row, shift), width="stretch")

with tabs[1]:
    st.subheader("Peta risiko yang bisa diganti-ganti")
    left, right = st.columns([1.2, .8])
    with left:
        st.plotly_chart(make_map(df, geo, map_col, map_label), width="stretch")
    with right:
        st.plotly_chart(rank_bar(df, map_col, f"10 provinsi tertinggi: {map_label}"), width="stretch")
    bi = bi_class(df, "rokok_pct_of_gizi", "stunting_0_59_total_pct")
    st.plotly_chart(bi_map(bi, geo), width="stretch")
    source_note("Peta bivariate membaca dua sinyal sekaligus: beban rokok relatif terhadap gizi, dan stunting balita.")

with tabs[2]:
    st.subheader("Trade-off rokok dan gizi")
    left, right = st.columns([1.15, .85])
    with left:
        st.plotly_chart(
            scatter_quad(
                df,
                "rokok_pct_of_gizi",
                "stunting_0_59_total_pct",
                "Kuadran: rokok terhadap gizi vs stunting",
            ),
            width="stretch",
        )
    with right:
        st.plotly_chart(slope_chart(row), width="stretch")
    cols = [
        "risk_index",
        "rokok_pct_of_gizi",
        "smoking_15_pct",
        "poverty_rate",
        "mad_6_23_pct",
        "stunting_0_59_total_pct",
    ]
    names = ["Risiko", "Rokok/Gizi", "Merokok", "Miskin", "MAD", "Stunting"]
    st.plotly_chart(heat_map(df, cols, names), width="stretch")

with tabs[3]:
    st.subheader("Lensa SKI 2023")
    source_note("SKI menambah sisi perilaku dan kesehatan: bukan hanya uang keluar untuk rokok, tapi juga asap, remaja, dan gizi anak.")
    left, mid, right = st.columns(3)
    with left:
        st.metric("Merokok 10+ tiap hari", percent(row["smoking_10plus_daily_pct"]))
        st.metric("Merokok remaja 10-18", percent(row["smoking_10_18_daily_pct"]))
    with mid:
        st.metric("Merokok dalam ruangan", percent(row["smoking_indoor_pct"]))
        st.metric("Paparan asap harian", percent(row["passive_smoke_daily_pct"]))
    with right:
        st.metric("Stunting balita", percent(row["stunting_0_59_total_pct"]))
        st.metric("Diet minimal anak", percent(row["mad_6_23_pct"]))
    left, right = st.columns(2)
    with left:
        st.plotly_chart(rank_bar(df, "smoking_indoor_pct", "Merokok dalam rumah/ruangan tertinggi"), width="stretch")
    with right:
        st.plotly_chart(rank_bar(df, "mad_6_23_pct", "Diet minimal anak terbaik", high=True), width="stretch")
    st.plotly_chart(parallel_plot(df), width="stretch")

with tabs[4]:
    st.subheader("Drill-down kabupaten/kota")
    source_note("Data kab/kota memberi rasa lokal. File BPS ini tidak membawa kolom provinsi, jadi panel ini fokus pada pencarian dan ranking nasional kab/kota.")
    query = st.text_input("Cari kabupaten/kota", "")
    top = st.slider("Jumlah bar", 10, 60, 25, 5)
    st.plotly_chart(city_bar(city, query, top), width="stretch")
    st.dataframe(
        city[["city", "weekly_smoke", "kretek_filter", "kretek_plain", "white", "tobacco", "other"]].head(80),
        width="stretch",
        hide_index=True,
    )

with tabs[5]:
    st.subheader("Konteks sosial-ekonomi")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            scatter_quad(
                df,
                "pdrb_capita",
                "rokok_pct_of_gizi",
                "PDRB per kapita vs rasio rokok/gizi",
            ),
            width="stretch",
        )
    with right:
        st.plotly_chart(
            scatter_quad(
                df,
                "school_year",
                "smoking_15_pct",
                "Lama sekolah vs prevalensi merokok 15+",
            ),
            width="stretch",
        )
    st.plotly_chart(trend_line(trend, province), width="stretch")
    source_note(f"Populasi {province}: {compact(row['population'])} ribu jiwa dalam data BPS 2024.")

with tabs[6]:
    st.subheader("Metodologi singkat")
    st.markdown(
        """
        Dashboard ini memakai satu tema besar: rokok sebagai pengeluaran yang bersaing dengan pangan bergizi.
        Data pengeluaran dari BPS dipakai sebagai fondasi. SKI 2023 dipakai untuk menambahkan sisi perilaku
        dan status kesehatan, terutama merokok, paparan asap, diet anak, protein hewani, dan stunting.

        Ada dua catatan penting. Pertama, sebagian data BPS masih memakai 34 provinsi, sementara beberapa
        tabel terbaru dan SKI sudah mengenal pemekaran Papua. Dashboard ini menjaga peta 34 provinsi agar
        geometri stabil. Kedua, simulator pengalihan belanja adalah latihan membaca skala uang, bukan model
        dampak kesehatan.
        """
    )
    st.markdown("#### Sumber")
    for item in SOURCES:
        st.markdown(f"- {item}")
    st.markdown("#### Link rujukan")
    for label, url in LINKS.items():
        st.markdown(f"- [{label}]({url})")
    st.markdown("#### Kolom utama")
    st.dataframe(df.head(34), width="stretch", hide_index=True)
