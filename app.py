import streamlit as st

from src.data import load_all_data, geo_data
from src.theme import page_css
from src.chart import (
    render_hero,
    modul_0_big_picture,
    modul_1_anatomi,
    modul_2_geografi,
    modul_3_demografi,
    modul_4_penyebab,
    modul_5_akibat,
    modul_6_waktu,
    modul_7_simulasi
)

st.set_page_config(
    page_title="Rokok Nomor Satu, Gizi Lain Waktu",
    page_icon="🚬",
    layout="wide",
)

@st.cache_data
def get_data():
    return load_all_data()

@st.cache_data
def get_geo():
    return geo_data()

def main():
    st.markdown(page_css(), unsafe_allow_html=True)
    
    data = get_data()
    geo = get_geo()
    
    # Global Filter Sidebar
    st.sidebar.markdown("### 📍 Panel Kontrol Global")
    
    # Check if 'metrics' exists
    provinces = sorted(data["metrics"]["province"].unique()) if "metrics" in data else []
    
    selected_province = st.sidebar.selectbox(
        "Pilih Provinsi Fokus:", 
        options=["Nasional"] + list(provinces),
        index=0
    )
    
    selected_year = st.sidebar.radio("Tahun:", [2024, 2023], index=0)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        **Insight Mode**
        <br>
        Gunakan mode navigasi di bawah untuk mengeksplorasi modul.
        """, 
        unsafe_allow_html=True
    )
    
    # Hero Section
    render_hero(data)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Modul Tabs
    tabs = st.tabs([
        "0: The Big Picture",
        "1: Anatomi Pengeluaran",
        "2: Geografi Paradoks",
        "3: Wajah Korban",
        "4: Akar Masalah",
        "5: Harga yang Dibayar",
        "6: Dimensi Waktu",
        "7: Simulasi & Harapan"
    ])
    
    with tabs[0]:
        modul_0_big_picture(data, selected_province)
        
    with tabs[1]:
        modul_1_anatomi(data, selected_province)
        
    with tabs[2]:
        modul_2_geografi(data, geo, selected_province)
        
    with tabs[3]:
        modul_3_demografi(data, selected_province)
        
    with tabs[4]:
        modul_4_penyebab(data, selected_province)
        
    with tabs[5]:
        modul_5_akibat(data, selected_province)
        
    with tabs[6]:
        modul_6_waktu(data, selected_province)
        
    with tabs[7]:
        modul_7_simulasi(data, selected_province)


if __name__ == "__main__":
    main()
