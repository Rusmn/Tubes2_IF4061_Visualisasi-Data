# Rokok Nomor Satu, Gizi Lain Waktu

Dashboard interaktif Dash untuk eksplorasi asosiasi pengeluaran rokok, gizi, kemiskinan, protein, digital adoption, dan prioritas kebijakan provinsi Indonesia.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/download_external_geo.py
.venv/bin/python scripts/extract_ski_pdf.py
.venv/bin/python scripts/prepare_data.py
.venv/bin/python app.py
```

Dashboard berjalan di `http://127.0.0.1:8050`.

## Data Notes

Folder `data/` dan `_source_archive/` sengaja tidak dilacak Git agar repository tetap ringan dan hanya berisi source code. Untuk menjalankan ulang pipeline, simpan CSV/PDF sumber secara lokal ke `data/raw/` atau `_source_archive/`, lalu jalankan script di bawah.

Aplikasi memakai `data/raw/` sebagai seed dan menghasilkan data siap pakai di `data/clean/`.

Map bersifat adaptif:

- `choropleth` dipakai jika 38 provinsi match ke GeoJSON.
- `point fallback` dipakai jika ada boundary yang tidak match, agar tidak ada provinsi hilang.

Seluruh narasi dashboard membaca pola sebagai asosiasi, bukan hubungan sebab-akibat langsung.
