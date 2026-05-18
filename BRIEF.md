# BRIEF: Dashboard "Rokok Nomor Satu, Gizi Lain Waktu"

Ringkasan gabungan dari `plan.md` dan `plan_2.md` — diperbarui sesuai masukan: fokus pada 2024, visual dinamis, dan peta lengkap.

Prinsip baru:

- Data: hanya tahun 2024. Jika dataset hanya punya 2023, data 2023 akan diasumsikan menjadi 2024 (ditandai sebagai inferred).
- Narasi: jangan bagi secara literal menjadi 7 tab — susun alur sebagai naratif yang digabungkan dengan panel eksplorasi interaktif (sidebar navigation, deep-linking untuk share).
- Visual: setiap grafik harus interaktif dan dapat dimainkan (filter, highlight, animasi waktu/trend, parameter slider untuk what-if).
- Peta: pastikan geojson provinsi lengkap — jika file lokal tidak lengkap, script akan mencoba mengunduh geojson yang umum dipakai dan menyimpan salinan lokal.

Perubahan prioritas kerja:

1. Konsolidasi data 2024 dan dokumentasikan asumsi inference dari 2023.
2. Perbaiki loader geojson otomatis (unduh bila perlu) dan normalisasi nama provinsi.
3. Rombak struktur UI: navigasi di sidebar (Hero + Narrative flow + Exploratory panels) bukan 7 tabs literal.
4. Pastikan semua chart interaktif (filter, hover, drilldown, sliders). Mulai dari peta choropleth dan sankey.
5. Tambahkan quality check untuk provinsi yang hilang — buat CSV helper yang menambahkan provinsi kosong dengan NaN agar peta tetap lengkap.

Catatan implementasi: lihat perubahan kode di `src/data.py` dan penggantian `use_container_width` ke `width='stretch'` di `src/chart.py`.
