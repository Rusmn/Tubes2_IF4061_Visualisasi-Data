# Rokok vs Gizi Rumah Tangga Indonesia

Dashboard interaktif untuk Tugas Besar 2 IF4061. Implementasi utama memakai **Streamlit + Plotly** melalui `app.py`, dengan sidebar filter, halaman narasi, peta, KPI, dan visualisasi interaktif.

## Jalankan Lokal

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Buka URL lokal yang muncul di terminal, biasanya `http://localhost:8501`.

## Isi Visualisasi

- Navigasi 4 halaman: Indonesia, Provinsi, Penyebab, Dampak & Kebijakan.
- Kontrol global di sidebar Streamlit.
- Navigasi halaman memakai radio control Streamlit.
- Peta choropleth 38 provinsi dengan hover dan zoom.
- Plotly Sankey, Sunburst/donut, Treemap/matrix, Radar-style/diagnosis scatter, Waterfall, Bubble/choropleth map.
- Ranking, histogram, heatmap, stacked bar, benchmark global, dan tabel prioritas.

## Data dan Catatan

Data utama berada di `data/clean/` dan `data/raw/`: rokok vs gizi, SKI 2023 curated, kemiskinan, gini, PDRB per kapita, pendidikan, akses digital, protein/kalori, harga/inflasi, dan populasi.

Peta memakai GeoJSON 38 provinsi di `data/geo/indonesia-38-provinces.geojson`. Provinsi pemekaran Papua yang belum memiliki observasi lokal lengkap diberi estimasi dari provinsi induk agar peta tetap lengkap dan status data tetap transparan.

Audit referensi ada di `REFERENCE_AUDIT.md`.
