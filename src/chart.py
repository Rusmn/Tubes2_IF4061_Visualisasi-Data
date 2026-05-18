import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.theme import COLORS, plot_theme
from collections import defaultdict

def fig_style(fig, height=460):
    fig.update_layout(**plot_theme(), height=height)
    fig.update_xaxes(gridcolor="rgba(237,229,214,.10)", zerolinecolor="rgba(237,229,214,.16)")
    fig.update_yaxes(gridcolor="rgba(237,229,214,.10)", zerolinecolor="rgba(237,229,214,.16)")
    return fig

# --- HERO ---
def render_hero(data):
    st.markdown(
        f"""
        <section class="hero">
            <h1><span class="gold">Rokok</span> <span class="paper">Nomor Satu,</span><br>
            <span class="gold">Gizi</span> <span class="paper">Lain Waktu</span></h1>
            <p class="lead">Indonesia menghabiskan lebih banyak uang untuk rokok daripada untuk sayuran, ikan, daging, telur, dan buah — di setiap provinsi. Tanpa terkecuali.</p>
        </section>
        """,
        unsafe_allow_html=True
    )
    
    # Real-time counter mockup
    st.markdown(
        """
        <div class="kpi" style="text-align: center;">
            <small>Sejak kamu membuka halaman ini...</small>
            <strong>Rp 2,149,032</strong>
            <span>dihabiskan untuk rokok di Indonesia</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- MODUL 0: THE BIG PICTURE ---
def modul_0_big_picture(data, province):
    st.header("Modul 0: Ringkasan Argumen")
    st.markdown("### Berapa Piring untuk Satu Batang?")
    st.info("💡 Isotype Chart: Membandingkan 1 batang rokok dengan ekuivalen komoditas pangan.")
    
    # Using baseline_national for waffle/isotype data mock
    baseline = data["baseline_national"] if "baseline_national" in data else pd.DataFrame()
    if not baseline.empty:
        st.dataframe(baseline.head())

    st.markdown("### 5 Fakta Mengejutkan")
    st.markdown(
        """
        1. Di 38 dari 38 provinsi, pengeluaran rokok lebih besar dari sayuran.
        2. Di 33 dari 38 provinsi, rokok mengalahkan daging.
        3. Rata-rata 27.5% dari seluruh uang pangan habis untuk rokok.
        4. Di Sulawesi Barat, 1 dari 2 rupiah untuk pangan masuk ke rokok.
        5. Papua punya belanja rokok hampir sama dengan DKI Jakarta.
        """
    )

# --- MODUL 1: ANATOMI PENGELUARAN ---
def modul_1_anatomi(data, province):
    st.header("Modul 1: Anatomi Pengeluaran")
    st.markdown("Ke mana sebenarnya uang rumah tangga pergi?")
    
    if "komoditas_2024" in data:
        df_komoditas = data["komoditas_2024"]
        if province != "Nasional":
            df_komoditas = df_komoditas[df_komoditas["province"].str.upper() == province.upper()]
        
        # 1.2 Stacked Horizontal Bar Chart Mockup
        st.subheader("Komposisi Pangan")
        temp = df_komoditas.groupby(["province", "commodity"])["value"].sum().reset_index()
        fig = px.bar(
            temp, y="province", x="value", color="commodity", orientation="h",
            title="Komposisi Pangan per Provinsi",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_style(fig, 500), width='stretch')
        
        st.subheader("Aliran Pengeluaran (Sankey)")
        # Render Sankey
        try:
            fig_sankey = build_sankey(df_komoditas)
            st.plotly_chart(fig_style(fig_sankey, 600), width='stretch')
        except Exception as e:
            st.error(f"Sankey gagal dibuat: {e}")

    st.info("💡 Opportunity Cost Calculator: widget interaktif untuk input konsumsi batang rokok per hari.")


def build_sankey(df: pd.DataFrame) -> go.Figure:
    # Aggregate spending by high-level categories: Total -> Food/Non-food -> Commodity
    # Expecting columns: province, commodity, area, value
    df = df.copy()
    df["commodity_clean"] = df["commodity"].str.split("/").str[0].str.strip()
    # Define mapping to coarse groups
    food_keywords = ["Padi", "Ikan", "Daging", "Telur", "Sayur", "Buah", "Pangan", "Kacang", "Makanan", "Minyak"]
    def classify(x):
        x = str(x).lower()
        if "rokok" in x or "cigar" in x:
            return "Rokok"
        for k in food_keywords:
            if k.lower() in x:
                return "Makanan"
        return "Non-makanan"

    df["group"] = df["commodity_clean"].apply(classify)
    # Sum
    total = df.groupby(["group"]) ["value"].sum().to_dict()
    # Build nodes
    nodes = ["Total", "Makanan", "Non-makanan", "Rokok"]
    node_indices = {n: i for i, n in enumerate(nodes)}
    sources = []
    targets = []
    values = []

    # Total -> groups
    total_sum = df["value"].sum()
    for g in ["Makanan", "Non-makanan", "Rokok"]:
        val = df[df["group"] == g]["value"].sum()
        sources.append(node_indices["Total"])
        targets.append(node_indices[g])
        values.append(val)

    # Groups -> top commodities (top 6)
    top = df.groupby(["group", "commodity_clean"]) ["value"].sum().reset_index()
    top = top.sort_values("value", ascending=False)
    top_comms = top.groupby("group").head(6)
    # add commodity nodes
    for _, row in top_comms.iterrows():
        comm = row["commodity_clean"]
        if comm not in node_indices:
            node_indices[comm] = len(node_indices)
            nodes.append(comm)
        sources.append(node_indices[row["group"]])
        targets.append(node_indices[comm])
        values.append(row["value"])

    # Prepare sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(label=nodes, color=[COLORS.get("gold") if n=="Total" else COLORS.get("red") if n=="Rokok" else COLORS.get("blue") for n in nodes]),
        link=dict(source=sources, target=targets, value=values)
    )])
    fig.update_layout(title_text="Aliran Pengeluaran Rumah Tangga", font_size=12)
    return fig

# --- MODUL 2: GEOGRAFI PARADOKS ---
def modul_2_geografi(data, geo, province):
    st.header("Modul 2: Geografi Paradoks")
    
    if "metrics" in data and geo:
        df_metrics = data["metrics"]
        df_metrics["prov_key"] = df_metrics["province"].astype(str).str.title()
        
        st.subheader("Peta Multi-Metric")
        viz_type = st.radio("Tipe Peta", ["Single Metric", "Bivariate"], index=0, horizontal=True)
        if viz_type == "Single Metric":
            metric_col = st.selectbox("Pilih Metrik Peta", [c for c in df_metrics.columns if c not in ["province", "prov_key", "year"]])
            if metric_col in df_metrics.columns:
                fig = px.choropleth(
                    df_metrics, geojson=geo, locations="prov_key", featureidkey="properties.name",
                    color=metric_col, hover_name="province",
                    color_continuous_scale="Reds", title=f"Sebaran {metric_col}"
                )
                fig.update_geos(fitbounds="locations", visible=False)
                st.plotly_chart(fig_style(fig, 600), width='stretch')
        else:
            col_x = st.selectbox("Metrik X (warna horizontal)", [c for c in df_metrics.columns if c not in ["province", "prov_key", "year"]], index=0)
            col_y = st.selectbox("Metrik Y (warna vertikal)", [c for c in df_metrics.columns if c not in ["province", "prov_key", "year"]], index=1)
            if col_x and col_y and col_x in df_metrics.columns and col_y in df_metrics.columns:
                try:
                    fig = build_bivariate_choropleth(df_metrics, geo, col_x, col_y)
                    st.plotly_chart(fig_style(fig, 650), width='stretch')
                except Exception as e:
                    st.error(f"Gagal membuat bivariate map: {e}")


def build_bivariate_choropleth(df, geo, xcol, ycol):
    # compute tertiles (0,1,2) for each metric
    tmp = df[["prov_key", xcol, ycol]].copy()
    tmp[xcol] = pd.to_numeric(tmp[xcol], errors='coerce')
    tmp[ycol] = pd.to_numeric(tmp[ycol], errors='coerce')
    tmp["qx"] = pd.qcut(tmp[xcol].rank(method='first', na_option='bottom'), 3, labels=[0,1,2])
    tmp["qy"] = pd.qcut(tmp[ycol].rank(method='first', na_option='bottom'), 3, labels=[0,1,2])
    tmp["code"] = tmp["qx"].astype(int) * 3 + tmp["qy"].astype(int)

    # 3x3 color matrix (light to dark hues)
    palette = [
        "#e8e8e8", "#b8d6e8", "#6c9bd1",
        "#f2d7d5", "#f08a79", "#c83b2f",
        "#c6e9c6", "#6fbf6f", "#2a9d2a",
    ]

    color_map = {i: palette[i] for i in range(9)}
    tmp["color"] = tmp["code"].map(color_map)

    # Build choropleth by mapping province -> color value (use discrete mapping via color_discrete_map hack)
    # We'll create an index numeric value for each province and use custom colors in marker style
    tmp_map = tmp.set_index("prov_key")["code"].to_dict()

    # Prepare feature properties for hover
    values = []
    locations = []
    for feat in geo.get("features", []):
        name = feat.get("properties", {}).get("name", "").title()
        locations.append(name)
        values.append(tmp_map.get(name, None))

    # Use choropleth with discrete colors via custom colorscale based on code (0-8)
    fig = px.choropleth(
        tmp.reset_index(), geojson=geo, locations="prov_key", featureidkey="properties.name",
        color="code", color_continuous_scale=palette, range_color=(0,8),
        hover_name="prov_key", title=f"Bivariate: {xcol} vs {ycol}"
    )
    fig.update_geos(fitbounds="locations", visible=False)

    # Add legend as annotation (simple)
    annotations = []
    fig.update_layout(coloraxis_showscale=False)
    return fig

# --- MODUL 3: WAJAH KORBAN ---
def modul_3_demografi(data, province):
    st.header("Modul 3: Siapa yang Paling Terdampak?")
    
    if "metrics" in data:
        df_metrics = data["metrics"]
        
        st.subheader("Poverty vs Rokok (Bubble Scatter)")
        if {"poverty_rate", "rokok_pct_of_gizi", "gini"}.issubset(df_metrics.columns):
            temp = df_metrics.dropna(subset=["poverty_rate", "rokok_pct_of_gizi", "gini"])
            fig = px.scatter(
                temp, x="poverty_rate", y="rokok_pct_of_gizi", size="rokok_pct_of_gizi",
                color="gini", hover_name="province", title="Poverty x Rokok x Gini"
            )
            st.plotly_chart(fig_style(fig, 500), width='stretch')

    st.info("💡 Risk Heatmap Matrix & Beeswarm Chart untuk memetakan kelompok rentan.")

# --- MODUL 4: AKAR MASALAH ---
def modul_4_penyebab(data, province):
    st.header("Modul 4: Akar Masalah (Mengapa Ini Terjadi?)")
    
    if "inflasi" in data:
        df_inflasi = data["inflasi"]
        st.subheader("Inflasi Rokok vs Pangan")
        
        # Plotting the inflation line chart
        if "year" in df_inflasi.columns and "sub_group" in df_inflasi.columns:
            temp = df_inflasi.groupby(["year", "sub_group"])["value"].mean().reset_index()
            fig = px.line(temp, x="year", y="value", color="sub_group", title="Tren Inflasi")
            st.plotly_chart(fig_style(fig, 500), width='stretch')
            
    if "metrics" in data:
        df_metrics = data["metrics"]
        st.subheader("Korelasi Antar Variabel")
        cols = ["rokok_pct_of_gizi", "poverty_rate", "gini", "digital_index_pct", "engel_ratio", "calorie_per_capita"]
        avail_cols = [c for c in cols if c in df_metrics.columns]
        corr = df_metrics[avail_cols].corr()
        fig = px.imshow(corr, text_auto=True, aspect="auto", title="Matriks Korelasi", color_continuous_scale="RdBu_r")
        st.plotly_chart(fig_style(fig, 500), width='stretch')

# --- MODUL 5: HARGA YANG DIBAYAR ---
def modul_5_akibat(data, province):
    st.header("Modul 5: Harga yang Dibayar (Akibatnya)")
    
    if "calorie_protein" in data:
        df_cp = data["calorie_protein"]
        st.subheader("Defisit Protein")
        
        temp = df_cp[df_cp["year"] == 2024] if "year" in df_cp.columns else df_cp
        if "protein_per_capita" in temp.columns:
            fig = px.bar(temp.sort_values("protein_per_capita"), x="protein_per_capita", y="province", orientation="h", title="Protein per Kapita (Target WHO: 62g)")
            fig.add_vline(x=62, line_dash="dash", line_color="green", annotation_text="Batas WHO (62g)")
            st.plotly_chart(fig_style(fig, 600), width='stretch')

    st.info("💡 Bivariate Choropleth Stunting & Rokok bersanding di sini.")

# --- MODUL 6: DIMENSI WAKTU ---
def modul_6_waktu(data, province):
    st.header("Modul 6: Tren & Dimensi Waktu")
    
    if "calorie_protein" in data:
        df_cp = data["calorie_protein"]
        if "year" in df_cp.columns and "protein_per_capita" in df_cp.columns:
            st.subheader("Tren 18 Tahun Protein Indonesia")
            fig = px.area(df_cp.groupby("year")["protein_per_capita"].mean().reset_index(), x="year", y="protein_per_capita", title="Area Chart Protein")
            st.plotly_chart(fig_style(fig, 400), width='stretch')
            
    st.info("💡 Animated Choropleth & Streamgraph berada di modul ini.")

# --- MODUL 7: SIMULASI & HARAPAN ---
def modul_7_simulasi(data, province):
    st.header("Modul 7: Jika Kita Berubah")
    st.subheader("Policy Simulator")
    
    shift = st.slider("Simulasi Kenaikan Cukai / Realokasi (%)", 0, 50, 15)
    st.markdown(f"Jika **{shift}%** belanja rokok dialihkan ke pangan bergizi, berapa banyak defisit protein yang bisa ditutup?")
    
    if "komoditas_2024" in data:
        # Mock calculation
        st.success(f"Simulasi mengalihkan {shift}% anggaran berpotensi membebaskan jutaan rupiah per keluarga untuk telur dan susu.")
        
    st.info("💡 Dream Distribution: Mini-game drag & drop alokasi unit berada di sini.")
