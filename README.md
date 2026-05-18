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
