# Plan Eksekusi Dashboard TB2 IF4061

## Arah Proyek

Dashboard ini mengembangkan infografis statis "Rokok Nomor Satu, Gizi Lain Waktu" menjadi visualisasi data interaktif. Fokusnya bukan hanya membuktikan bahwa rokok mengambil porsi besar dalam belanja pangan, tetapi juga membuka konteks yang lebih luas: perilaku merokok, paparan asap, kualitas diet anak, stunting, kemiskinan, pendidikan, PDRB, dan tren konsumsi.

Jenis dashboard: dasbor analitis dengan storytelling ringan. Target pembaca: pengambil kebijakan, mahasiswa/peneliti, jurnalis data, aktivis kesehatan publik, dan masyarakat umum yang ingin melihat masalah ini secara cepat tetapi tetap bisa menelusuri datanya.

Pertanyaan kunci:

- Di provinsi mana belanja rokok paling kuat menggeser ruang belanja gizi?
- Apakah daerah dengan beban rokok tinggi juga punya sinyal risiko gizi atau kesehatan yang perlu diperhatikan?
- Apa yang berubah ketika isu ini dilihat dari perilaku merokok, paparan asap, dan indikator SKI 2023?
- Seberapa besar ruang belanja gizi yang muncul jika sebagian kecil belanja rokok dialihkan?

## Stack dan Struktur

Stack utama:

- Streamlit untuk dashboard.
- Plotly untuk grafik interaktif.
- Pandas dan NumPy untuk pembersihan dan penggabungan data.

Struktur repo:

```text
Tubes2_IF4061_Visualisasi-Data/
├── app.py
├── plan.md
├── README.md
├── requirements.txt
├── .streamlit/config.toml
├── data/raw
├── data/clean
├── data/geo
├── src/data.py
├── src/chart.py
├── src/theme.py
├── src/copy.py
└── src/util.py
```

Aturan kode:

- Nama fungsi memakai `snake_case`.
- Nama fungsi maksimal dua kata.
- Copy dashboard ditulis ringkas, manusiawi, dan tidak memakai bahasa template.
- Modul dipisah berdasarkan tanggung jawab: data, chart, tema, teks, utilitas.

## Data

Data lokal:

- Pengeluaran rokok dan komponen gizi 2024.
- Master snapshot sosial-ekonomi per provinsi.
- Tren kalori, protein, kemiskinan, dan internet.
- Prevalensi merokok 15+ tahun 2024.
- Konsumsi rokok dan tembakau kabupaten/kota 2024.
- PDRB per kapita, jumlah penduduk, dan rata-rata lama sekolah.
- GeoJSON provinsi Indonesia.

Data SKI 2023 curated:

- Merokok 10-18 tahun.
- Merokok 10+ tahun.
- Merokok dalam rumah/ruangan.
- Paparan asap rokok harian.
- MDD, MMF, MAD anak 6-23 bulan.
- Konsumsi protein hewani anak.
- Stunting, underweight, wasting balita.

Catatan data:

- Beberapa data memakai 34 provinsi, sementara SKI dan BPS terbaru bisa memakai 38 provinsi. Dashboard menjaga peta 34 provinsi agar geometri stabil.
- Provinsi pemekaran Papua dicatat sebagai caveat metodologis.
- SKI dipakai sebagai CSV ringkas agar dashboard stabil dan tidak parsing PDF besar saat runtime.

## Desain Visual

Identitas visual mengikuti poster statis:

- Background: `#2D2E2D`, `#1B1715`
- Rokok: `#C0272D`, `#8B0000`, `#F73227`
- Gizi: `#DAA520`, `#B8860B`, `#EDE5D6`
- Gizi positif: `#6FAF4E`
- Netral peta: `#CBD5E3`, `#8A8A8A`, `#6B6B6B`

Prinsip tampilan:

- Chart naratif boleh dramatis.
- Chart eksploratif harus bersih dan mudah dibaca.
- Tidak semua informasi ditaruh di satu layar; dashboard memakai tab agar tidak penuh.
- Tooltip wajib membawa angka, satuan, dan konteks.

## Visualisasi

Tab dashboard:

- Cerita Utama: KPI, donut, Sankey, treemap, simulator alokasi.
- Peta Risiko: choropleth, ranking, bivariate map.
- Trade-off: scatter quadrant, dumbbell/slope chart, heatmap indikator.
- Lensa SKI: merokok remaja, paparan asap, merokok dalam ruangan, MAD, stunting, parallel coordinates.
- Drill-down: ranking konsumsi rokok kabupaten/kota dan pencarian.
- Sosial Ekonomi: PDRB, pendidikan, prevalensi merokok, tren kalori/protein/kemiskinan/internet.
- Metodologi: sumber, caveat, dan tabel data.

Visualisasi out of the box yang tetap relevan:

- Sankey untuk aliran belanja pangan.
- Bivariate choropleth untuk membaca dua risiko sekaligus.
- Parallel coordinates untuk melihat pola multi-indikator.
- Heatmap risiko relatif.
- What-if simulator untuk membaca skala uang secara intuitif.

## Pengujian

Checklist lokal:

- `streamlit run app.py` berjalan tanpa error.
- Semua tab terbuka.
- Semua chart menampilkan tooltip.
- Filter provinsi tidak membuat app crash.
- Peta cocok dengan nama provinsi.
- Drill-down kab/kota bisa dicari.
- Path data relatif dan siap untuk Streamlit Cloud.

Checklist presentasi:

- Tunjukkan cerita utama dalam 2-3 menit.
- Gunakan peta risiko untuk membuktikan variasi wilayah.
- Gunakan Lensa SKI untuk menunjukkan kenapa dashboard dinamis lebih kuat dari poster statis.
- Tutup dengan simulator alokasi dan caveat.
