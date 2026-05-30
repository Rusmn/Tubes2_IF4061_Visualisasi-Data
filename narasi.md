# Narasi dan Panduan Dashboard

## Judul Dashboard

**Rokok Nomor Satu, Gizi Lain Waktu**

Dashboard ini membaca paradoks pengeluaran rumah tangga Indonesia: di banyak provinsi, belanja rokok menjadi komponen besar yang perlu dibandingkan dengan belanja gizi, indikator kesehatan, dan konteks sosial-ekonomi. Narasi dashboard harus selalu dibaca sebagai **asosiasi dan konteks**, bukan sebab-akibat langsung.

## Alur Cerita Utama

Alur dashboard bergerak seperti ini:

1. **Indonesia**
   Melihat gambaran nasional: seberapa besar belanja rokok dibanding gizi dan bagaimana sebarannya di 38 provinsi.

2. **Provinsi**
   Masuk ke diagnosis satu provinsi: posisi provinsi tersebut, struktur pengeluaran, indikator SKI, dan simulasi realokasi sederhana.

3. **Penyebab**
   Membuka beberapa lensa eksplorasi: ekonomi, rokok dari SKI, gizi dari SKI, harga, dan digital.

4. **Kebijakan**
   Merangkum prioritas wilayah dengan gabungan indikator rokok, gizi, kesehatan, kemiskinan, protein, dan populasi.

## Catatan Penting Tentang SKI PDF

Data dari `_source_archive/documents/LAPORAN SKI 2023 DALAM ANGKA_REVISI I_OK.pdf` sudah diekstrak lewat `scripts/extract_ski_pdf.py`.

Indikator SKI yang dipakai:

- Prevalensi merokok umur 10-18 tahun
- Prevalensi merokok umur 10+ tahun
- Rata-rata batang rokok per hari
- Harga rokok per bungkus
- Umur mulai merokok 10-14 dan 15-19 tahun
- Pengetahuan stunting
- Stunting balita
- Konsumsi ikan harian/mingguan/jarang
- Konsumsi telur harian/mingguan/jarang
- Konsumsi susu harian/mingguan/jarang

Kalau indikator SKI belum kelihatan di browser, biasanya server masih memakai proses lama. Matikan server lalu jalankan lagi:

```bash
Ctrl+C
.venv/bin/python scripts/extract_ski_pdf.py
.venv/bin/python scripts/prepare_data.py
.venv/bin/python app.py
```

Lalu hard refresh browser:

```text
Cmd + Shift + R
```

## Kontrol Global

Di bagian atas dashboard ada dua dropdown:

### 1. Area

Pilihan:

- `Total`
- `Perkotaan`
- `Perdesaan`

Efek:

- Mengubah data yang dipakai di KPI, map, ranking, scatter, dan diagnosis provinsi.
- Jika memilih `Perkotaan`, angka pengeluaran rokok/gizi mengikuti data urban.
- Jika memilih `Perdesaan`, angka mengikuti data rural.

### 2. Map Mode

Pilihan:

- `Auto map`
- `Boundary`
- `Point fallback`

Efek:

- `Auto map`: memakai choropleth jika 38 provinsi match ke GeoJSON.
- `Boundary`: memaksa peta batas provinsi.
- `Point fallback`: memakai titik/bubble berbasis latitude-longitude agar tidak ada provinsi hilang.

Gunakan `Point fallback` jika peta boundary terasa ada provinsi yang tidak muncul.

## Page 1: Indonesia

Tujuan halaman ini adalah memberi kejutan awal: rokok bukan isu kecil, dan polanya tersebar lintas provinsi.

### KPI Strip

Kartu yang muncul:

- **Provinsi terbaca**
  Menunjukkan apakah data mencakup 38 provinsi.

- **Rokok rata-rata**
  Rata-rata belanja rokok per kapita per bulan.

- **Gizi rata-rata**
  Rata-rata total belanja lima komponen gizi: sayur, ikan, telur/susu, daging, buah.

- **Rokok/Gizi**
  Rata-rata rasio belanja rokok terhadap total belanja gizi.

- **Perokok 10+**
  Rata-rata prevalensi perokok umur 10+ dari SKI 2023.

- **Stunting balita**
  Rata-rata stunting balita dari SKI 2023.

### Peta Nasional

Yang ditampilkan:

- Warna provinsi berdasarkan rasio `rokok_pct_of_gizi`.
- Semakin merah, rasio rokok terhadap gizi semakin tinggi.

Interaksi:

- **Hover provinsi**
  Menampilkan tooltip berisi nama provinsi, rokok per kapita, gizi total, rasio rokok/gizi, protein, kemiskinan, dan status geometri.

- **Klik provinsi**
  Membuka halaman `Provinsi` dan otomatis memilih provinsi yang diklik.

### Donut Piring Pengeluaran

Yang ditampilkan:

- Komposisi nasional antara rokok dan komponen gizi.

Cara baca:

- Irisan merah adalah rokok.
- Irisan hijau/biru/oranye/ungu adalah komponen gizi.

### Ranking Bar

Yang ditampilkan:

- 10 provinsi dengan rasio rokok/gizi tertinggi.
- Garis putus-putus emas menunjukkan rata-rata nasional/provinsi.

### Insight Nasional

Kartu ini menjelaskan:

- Peta akan otomatis fallback ke bubble map jika boundary tidak lengkap.
- SKI menambah konteks kesehatan, seperti perokok umur 10+, konsumsi ikan harian, dan konsumsi susu jarang.
- Semua pembacaan adalah asosiasi, bukan sebab-akibat.

## Page 2: Provinsi

Tujuan halaman ini adalah menjawab: “Kalau saya pilih satu provinsi, seperti apa profil rokok, gizi, dan kesehatan provinsi itu?”

### Cara Masuk

Ada dua cara:

- Klik provinsi di peta Page 1.
- Klik menu `Provinsi` di navbar.

Jika masuk tanpa memilih provinsi, dashboard memilih provinsi dengan rasio rokok/gizi tertinggi sebagai default.

### KPI Provinsi

Kartu yang muncul:

- **Rank rokok**
  Peringkat belanja rokok provinsi secara nasional.

- **Rokok/kapita**
  Belanja rokok per kapita per bulan.

- **Rokok/Gizi**
  Rasio rokok terhadap total belanja gizi.

- **Gizi total**
  Total belanja sayur, ikan, telur/susu, daging, dan buah.

- **Protein**
  Protein per kapita per hari.

- **Perokok 10+**
  Prevalensi perokok umur 10+ dari SKI.

- **Stunting balita**
  Prevalensi stunting balita dari SKI.

- **Batang/hari**
  Rata-rata batang rokok per hari pada perokok harian.

- **Harga/bungkus**
  Rata-rata harga rokok per bungkus dari SKI.

- **Ikan harian**
  Proporsi penduduk umur 5+ yang konsumsi ikan minimal 1 kali per hari.

- **Susu jarang**
  Proporsi penduduk umur 5+ yang konsumsi susu maksimal 3 kali per bulan.

### Waterfall

Yang ditampilkan:

- Struktur rokok dan komponen gizi untuk provinsi terpilih.

Cara baca:

- Rokok menjadi titik pembanding utama.
- Komponen gizi ditampilkan sebagai pengurang/komparasi visual.

### Scatter Kuadran

Yang ditampilkan:

- Semua provinsi sebagai titik.
- Sumbu X: rasio rokok terhadap gizi.
- Sumbu Y: protein per kapita.
- Ukuran titik: populasi.

Interaksi:

- Hover titik untuk melihat detail provinsi.
- Provinsi terpilih diberi highlight.

### What-if Sederhana

Yang ditampilkan:

- Simulasi jika 25% belanja rokok dialihkan ke pangan bergizi.

Output:

- Estimasi nilai rupiah per kapita per bulan.
- Perkiraan setara butir telur.
- Perkiraan setara porsi ikan.

Catatan:

- Ini bukan rekomendasi individual dan bukan bukti kausalitas.
- Ini hanya cara membaca opportunity cost.

## Page 3: Penyebab

Tujuan halaman ini adalah eksplorasi multi-lensa. Halaman ini paling cocok untuk diskusi dan menjawab pertanyaan dosen/penguji.

### Tab Ekonomi

Yang ditampilkan:

- Scatter provinsi dengan sumbu rokok/gizi dan protein.

Gunakan untuk:

- Melihat apakah provinsi dengan rasio rokok/gizi tinggi cenderung berada pada kondisi protein yang lebih rendah atau tidak.

### Tab SKI Rokok

Yang ditampilkan:

- Scatter `Rokok % dari gizi` vs `Perokok umur 10+`.
- Bar chart provinsi dengan rata-rata batang rokok per hari tertinggi.

Gunakan untuk:

- Membandingkan pola pengeluaran rokok dengan perilaku merokok dari SKI.
- Melihat apakah provinsi dengan belanja rokok relatif tinggi juga punya prevalensi perokok atau intensitas batang/hari yang tinggi.

### Tab SKI Gizi

Yang ditampilkan:

- Scatter `Rokok % dari gizi` vs `Stunting balita`.
- Scatter `Perokok umur 10+` vs `Konsumsi susu jarang`.

Gunakan untuk:

- Menghubungkan konteks rokok dengan indikator kesehatan dan pola konsumsi gizi dari SKI.
- Membaca provinsi yang punya kombinasi risiko: rokok tinggi, stunting tinggi, atau konsumsi susu jarang tinggi.

### Tab Harga

Yang ditampilkan:

- Line chart indeks harga untuk rokok dan beberapa komoditas pangan.

Gunakan untuk:

- Membaca konteks keterjangkauan: bagaimana harga rokok dan pangan bergerak dari waktu ke waktu.

### Tab Digital

Yang ditampilkan:

- Scatter berbasis indikator digital.

Gunakan untuk:

- Membuka pertanyaan eksploratif: apakah akses digital berkaitan dengan variasi rokok/gizi atau tidak.

## Page 4: Kebijakan

Tujuan halaman ini adalah sintesis: provinsi mana yang bisa diprioritaskan jika membaca banyak indikator sekaligus.

### KPI Policy

Kartu yang muncul:

- **Opportunity cost**
  Estimasi belanja rokok nasional tahunan.

- **Prioritas pertama**
  Provinsi dengan skor prioritas tertinggi.

- **Protein rata-rata**
  Rata-rata protein per kapita per hari.

### Policy Map

Yang ditampilkan:

- Peta berdasarkan `policy_priority_score`.

Skor ini menggabungkan:

- Rasio rokok/gizi
- Kemiskinan
- Protein
- Populasi
- Indikator SKI melalui `ski_health_context_score`

### Scatter Policy

Yang ditampilkan:

- Scatter provinsi untuk membaca posisi relatif rokok/gizi dan protein.

### Ranking Prioritas

Yang ditampilkan:

- Tabel 12 provinsi prioritas tertinggi.

Kolom penting:

- Provinsi
- Region
- Rokok/gizi
- Perokok umur 10+
- Stunting balita
- Konsumsi susu jarang
- Policy priority score

Gunakan untuk:

- Menjelaskan provinsi mana yang layak jadi perhatian awal.
- Membandingkan apakah prioritas muncul dari belanja rokok, indikator kesehatan, atau kombinasi keduanya.

## Cara Presentasi 5 Menit

1. Buka Page 1.
   Tekankan bahwa data mencakup 38 provinsi dan peta aman dari masalah provinsi hilang karena ada fallback point map.

2. Tunjukkan KPI nasional.
   Jelaskan rokok/gizi, perokok 10+, dan stunting balita.

3. Klik salah satu provinsi merah di peta.
   Masuk ke Page 2 dan jelaskan diagnosis lokal.

4. Di Page 2, baca KPI SKI.
   Hubungkan belanja rokok dengan prevalensi merokok, batang/hari, harga rokok, ikan harian, dan susu jarang.

5. Masuk Page 3.
   Buka tab `SKI Rokok`, lalu `SKI Gizi`.

6. Masuk Page 4.
   Tutup dengan ranking prioritas dan jelaskan bahwa ini bukan klaim kausal, melainkan alat bantu eksplorasi kebijakan.

## Kalimat Aman untuk Dipakai Saat Presentasi

Gunakan:

- “Data ini menunjukkan asosiasi antar indikator provinsi.”
- “Rasio ini memberi konteks tekanan pengeluaran rumah tangga.”
- “SKI menambahkan lapisan perilaku dan kesehatan untuk membaca pola rokok dan gizi.”
- “Dashboard ini membantu memilih provinsi yang perlu ditelaah lebih lanjut.”

Hindari:

- “Rokok menyebabkan stunting.”
- “Karena rokok, protein turun.”
- “Provinsi ini miskin karena rokok.”

## Troubleshooting

### Data SKI belum muncul

Jalankan ulang:

```bash
.venv/bin/python scripts/extract_ski_pdf.py
.venv/bin/python scripts/prepare_data.py
```

Lalu restart server:

```bash
Ctrl+C
.venv/bin/python app.py
```

### Port 8050 penuh

Jalankan di port lain:

```bash
.venv/bin/python -c "import app; app.app.run(port=8051, debug=False)"
```

### Peta ada provinsi hilang

Ubah dropdown `Map Mode` ke:

```text
Point fallback
```

### Halaman masih tampak versi lama

Hard refresh browser:

```text
Cmd + Shift + R
```
