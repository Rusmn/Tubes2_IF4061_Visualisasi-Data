# Rokok Nomor Satu, Gizi Lain Waktu — Dashboard

Runlokal

1. Buat virtualenv dan install dependency:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Jalankan Streamlit:

```bash
streamlit run app.py
```

Jika belum menyiapkan data bersih, jalankan script berikut untuk menyalin dan membersihkan data dari `data_gabungan/` ke `data/clean/`:

```bash
python scripts/prepare_data.py
```

Struktur singkat repositori:

- `app.py` — Entrypoint Streamlit
- `src/` — modul data, chart, theme, util, copy
- `data/clean` — data bersih yang dipakai app
- `data/geo` — geojson peta provinsi
- `BRIEF.md` — ringkasan gabungan plan

Langkah selanjutnya: bersihkan data ke `data/clean/`, implement visual utama, dan tambahkan deployment config.

# Tubes2 IF4061 Visualisasi Data

Dashboard interaktif untuk Tugas Besar 2 IF4061. Tema utamanya adalah paradoks belanja rokok dan gizi rumah tangga Indonesia, diperluas dengan indikator kesehatan, perilaku merokok, dan konteks sosial-ekonomi.

## Jalankan Lokal

```bash
source venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

## Isi Dashboard

- Cerita utama rokok vs gizi.
- Peta risiko per provinsi.
- Trade-off pengeluaran rokok dan pangan bergizi.
- Lensa SKI 2023: paparan asap, merokok remaja, MAD, protein hewani, stunting.
- Drill-down kabupaten/kota untuk konsumsi rokok mingguan.
- Konteks sosial-ekonomi: PDRB, pendidikan, kemiskinan, kalori, protein.

## Catatan

Sebagian data memakai 34 provinsi, sementara sebagian publikasi terbaru memakai 38 provinsi. Dashboard menjaga peta 34 provinsi supaya visual stabil, lalu mencatat keterbatasan provinsi pemekaran Papua di tab metodologi.
