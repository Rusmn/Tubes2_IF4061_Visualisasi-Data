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


def tab_note(text: str) -> None:
    st.markdown(f"<p class='tabnote'>{text}</p>", unsafe_allow_html=True)


def mini_card(title: str, body: str) -> None:
    st.markdown(f"<div class='mini'><strong>{title}</strong><br>{body}</div>", unsafe_allow_html=True)


def rank_pos(data, col: str, name: str, high: bool = True) -> int:
    temp = data.dropna(subset=[col]).sort_values(col, ascending=not high).reset_index(drop=True)
    hit = temp.index[temp["province"].eq(name)]
    return int(hit[0] + 1) if len(hit) else 0


def show_head() -> None:
    st.markdown(
        f"""
        <section class="hero">
            <h1><span class="gold">Rokok</span> <span class="paper">Nomor Satu,</span><br>
            <span class="gold">Gizi</span> <span class="paper">Lain Waktu</span></h1>
            <p class="note">{SUBTITLE}</p>
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

st.sidebar.markdown("### Panel Kontrol")
st.sidebar.caption("Kontrol global untuk membaca satu provinsi dari awal sampai akhir.")
province = st.sidebar.selectbox(
    "Provinsi fokus",
    df["province"].tolist(),
    index=df["risk_index"].idxmax(),
    help="Mengubah cerita provinsi, komposisi belanja, lensa SKI, dan tren.",
)
row = df[df["province"].eq(province)].iloc[0]

national = df.mean(numeric_only=True)
smoke_rank = rank_pos(df, "smoking_15_pct", province)
risk_rank = rank_pos(df, "risk_index", province)
gizi_rank = rank_pos(df, "mad_6_23_pct", province)

st.sidebar.markdown(
    f"""
    <div class="mini">
        <strong>Konteks tampilan</strong><br>
        <span class="chip">{province}</span>
        <p class="note">Provinsi fokus disorot pada scatter, ranking, peta, dan panel cerita. Kontrol khusus grafik ditempatkan dekat grafiknya.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

cols = st.columns(4)
with cols[0]:
    kpi_card("Belanja rokok rata-rata", rupiah(national["rokok"]), "per kapita per bulan, rata-rata provinsi")
with cols[1]:
    kpi_card("Rokok terhadap gizi", percent(national["rokok_pct_of_gizi"]), "dibanding sayur, ikan, buah, daging, telur-susu")
with cols[2]:
    kpi_card("Merokok 15+", percent(national["smoking_15_pct"]), "BPS 2024, penduduk umur 15 tahun ke atas")
with cols[3]:
    kpi_card("Fokus sekarang", province, f"peringkat risiko #{risk_rank} dari {len(df)} provinsi")

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
    tab_note(
        "Mulai dari provinsi fokus. Donut dan treemap membaca komposisi belanja, Sankey memperlihatkan alirannya, "
        "lalu simulator menunjukkan skala uang jika sebagian belanja rokok digeser merata ke lima pangan gizi."
    )
    left, right = st.columns([1.05, .95])
    with left:
        st.plotly_chart(make_donut(row), width="stretch")
    with right:
        st.plotly_chart(sankey_flow(row), width="stretch")
    left, right = st.columns([.9, 1.1])
    with left:
        st.plotly_chart(tree_map(row), width="stretch")
    with right:
        shift = st.slider(
            "Porsi belanja rokok yang dialihkan",
            0,
            50,
            15,
            5,
            help="Kontrol ini hanya mengubah grafik simulasi di bawahnya.",
            key="shift_sim",
        )
        st.markdown(
            f"""
            <div class="block">
            <h3>{province}</h3>
            <p>Belanja rokoknya <b>{rupiah(row['rokok'])}</b> per kapita per bulan. Nilainya setara
            <b>{percent(row['rokok_pct_of_gizi'])}</b> dari lima pangan gizi yang dipakai di sini.</p>
            <p>Slider di atas tidak mengubah data asli. Ia membantu memperjelas skala uang:
            berapa tambahan yang muncul kalau <b>{shift}%</b> belanja rokok digeser ke sayur, ikan, telur-susu, daging, dan buah.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.plotly_chart(whatif_bar(row, shift), width="stretch")
    source_note("Belanja rokok dan pangan bergizi memakai satuan rupiah per kapita per bulan.")

with tabs[1]:
    st.subheader("Sebaran Risiko Provinsi")
    tab_note(
        "Pilih indikator tepat di atas peta untuk mengubah warna peta utama dan urutan ranking di kanan. Peta kedua dibuat tetap "
        "sebagai pembanding antara rasio rokok/gizi dan stunting balita."
    )
    map_label = st.selectbox(
        "Indikator peta",
        list(metric_map.keys()),
        help="Kontrol ini mengubah peta utama dan ranking di sampingnya.",
        key="map_layer",
    )
    map_col = metric_map[map_label]
    left, right = st.columns([1.2, .8])
    with left:
        st.plotly_chart(make_map(df, geo, map_col, map_label, focus=province), width="stretch")
    with right:
        st.plotly_chart(rank_bar(df, map_col, f"Provinsi tertinggi: {map_label}", focus=province), width="stretch")
        mini_card(
            "Panduan baca",
            f"Warna peta mengikuti {map_label.lower()}. Bar merah terang menandai {province}, sekalipun posisinya tidak masuk 10 besar.",
        )
    bi = bi_class(df, "rokok_pct_of_gizi", "stunting_0_59_total_pct")
    st.plotly_chart(bi_map(bi, geo), width="stretch")
    source_note("Peta dua sinyal memakai median nasional sebagai batas sederhana: tinggi/rendah pada rasio rokok-gizi dan stunting.")

with tabs[2]:
    st.subheader("Trade-off rokok dan gizi")
    tab_note(
        "Bagian ini mencari daerah yang jatuh di kuadran berat: rasio rokok/gizi tinggi sekaligus stunting tinggi. "
        "Garis putus-putus adalah median, jadi sisi kanan-atas perlu dibaca paling hati-hati."
    )
    left, right = st.columns([1.15, .85])
    with left:
        st.plotly_chart(
            scatter_quad(
                df,
                "rokok_pct_of_gizi",
                "stunting_0_59_total_pct",
                "Kuadran: rokok terhadap gizi vs stunting",
                province,
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
    tab_note(
        "SKI membuat cerita belanja lebih dekat ke rumah: siapa yang merokok, di mana asapnya muncul, "
        "dan seperti apa indikator makan anak. Bagian ini membantu membaca risiko sebagai keseharian, bukan hanya angka belanja."
    )
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
        st.plotly_chart(rank_bar(df, "smoking_indoor_pct", "Merokok dalam rumah/ruangan tertinggi", focus=province), width="stretch")
    with right:
        st.plotly_chart(rank_bar(df, "mad_6_23_pct", "Diet minimal anak terbaik", high=True, focus=province), width="stretch")
    mini_card(
        "Posisi provinsi fokus",
        f"{province} berada di peringkat #{smoke_rank} untuk merokok 15+ dan #{gizi_rank} untuk diet minimal anak. "
        "Peringkat diet dibaca dari yang tertinggi karena semakin besar semakin baik.",
    )
    st.plotly_chart(parallel_plot(df), width="stretch")

with tabs[4]:
    st.subheader("Drill-down kabupaten/kota")
    tab_note(
        "Gunakan pencarian untuk melihat daerah tertentu, lalu atur jumlah bar untuk membandingkan konsumsi rokok mingguan "
        "antarkabupaten/kota. Bagian ini memberi konteks lokal setelah pola provinsi terbaca."
    )
    query = st.text_input("Cari kabupaten/kota", "")
    top = st.slider("Jumlah bar", 10, 60, 25, 5)
    st.plotly_chart(city_bar(city, query, top), width="stretch")
    if query and city[city["city"].str.contains(query, case=False, na=False)].empty:
        st.warning("Tidak ada nama kabupaten/kota yang cocok. Coba pakai kata yang lebih pendek.")
    st.dataframe(
        city[["city", "weekly_smoke", "kretek_filter", "kretek_plain", "white", "tobacco", "other"]].head(80),
        width="stretch",
        hide_index=True,
    )

with tabs[5]:
    st.subheader("Konteks sosial-ekonomi")
    tab_note(
        "Dua scatter ini bukan untuk menyalahkan satu faktor. Tujuannya melihat apakah beban rokok bergerak bersama ekonomi, "
        "pendidikan, dan prevalensi merokok. Provinsi fokus diberi lingkaran terang."
    )
    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            scatter_quad(
                df,
                "pdrb_capita",
                "rokok_pct_of_gizi",
                "PDRB per kapita vs rasio rokok/gizi",
                province,
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
                province,
            ),
            width="stretch",
        )
    st.plotly_chart(trend_line(trend, province), width="stretch")
    source_note(f"Populasi {province}: {compact(row['population'] * 1000)} jiwa dalam data BPS 2024.")

with tabs[6]:
    st.subheader("Metodologi singkat")
    st.markdown(
        """
        Tema utamanya sederhana: rokok dibaca sebagai pos belanja yang hidup berdampingan dengan pangan bergizi.
        Data pengeluaran BPS menjadi fondasi. SKI 2023 menambahkan sisi perilaku dan kesehatan:
        merokok, paparan asap, diet anak, protein hewani, dan status gizi.

        Ada dua catatan penting. Pertama, sebagian data BPS masih memakai 34 provinsi, sementara beberapa
        tabel terbaru dan SKI sudah mengenal pemekaran Papua. Peta di sini dijaga pada 34 provinsi agar
        geometri tetap stabil. Kedua, simulator pengalihan belanja hanya latihan membaca skala uang, bukan model
        dampak kesehatan. Ketiga, data kabupaten/kota dipakai sebagai ranking nasional karena file BPS yang tersedia
        di repo belum membawa pasangan provinsi-kabupaten/kota.
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
