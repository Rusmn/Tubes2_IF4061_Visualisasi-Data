# Laporan Tugas Besar II — Kelompok 9

**"Rokok Nomor Satu, Gizi Lain Waktu"**  
IF4061 Visualisasi Data dan Informasi, Semester 2 2025/2026

Kompilasi menggunakan **LuaLaTeX** (bukan pdflatex) — diperlukan untuk font rendering yang benar.

---

## Cara Compile di VS Code (Semua OS)

### 1. Install Dependensi

| OS | Distribusi LaTeX | Link |
|---|---|---|
| Windows | **MiKTeX** (auto-install packages) | https://miktex.org/download |
| macOS | **MacTeX** (full) | https://www.tug.org/mactex/ |
| Linux | **TeX Live** via package manager | `sudo pacman -S texlive-full` / `sudo apt install texlive-full` |

### 2. Install Extension VS Code

Install **LaTeX Workshop** oleh James Yu:
- Buka VS Code → Extensions (`Ctrl+Shift+X` / `Cmd+Shift+X`)
- Cari: `LaTeX Workshop`
- Install

### 3. Konfigurasi LaTeX Workshop untuk LuaLaTeX

Buka Settings JSON (`Ctrl+Shift+P` → "Open User Settings (JSON)") dan tambahkan:

```json
"latex-workshop.latex.recipes": [
  {
    "name": "lualatex",
    "tools": ["lualatex", "lualatex"]
  }
],
"latex-workshop.latex.tools": [
  {
    "name": "lualatex",
    "command": "lualatex",
    "args": [
      "-synctex=1",
      "-interaction=nonstopmode",
      "-file-line-error",
      "%DOC%"
    ]
  }
],
"latex-workshop.latex.recipe.default": "lualatex"
```

### 4. Compile

1. Buka file `main.tex` di VS Code
2. Tekan **`Ctrl+Alt+B`** (Windows/Linux) atau **`Cmd+Alt+B`** (macOS)
3. Atau klik tombol **▶ Build LaTeX project** di pojok kanan atas
4. PDF hasil compile tersimpan di folder yang sama: `main.pdf`

> **Catatan:** Compile pertama mungkin lambat karena MiKTeX/TeX Live perlu mengunduh packages.  
> Run compile **dua kali** agar cross-reference dan TOC terbentuk dengan benar.

---

## Cara Compile Manual (Terminal)

```bash
# Masuk ke folder laporan
cd docs/laporan_latex_kelompok9

# Compile (jalankan 2x untuk cross-reference yang benar)
lualatex -interaction=nonstopmode main.tex
lualatex -interaction=nonstopmode main.tex
```

### Windows (Command Prompt / PowerShell)
```bat
cd docs\laporan_latex_kelompok9
lualatex -interaction=nonstopmode main.tex
lualatex -interaction=nonstopmode main.tex
```

### macOS / Linux (Terminal)
```bash
cd docs/laporan_latex_kelompok9
lualatex -interaction=nonstopmode main.tex && lualatex -interaction=nonstopmode main.tex
```

---

## Struktur File

```
docs/laporan_latex_kelompok9/
├── main.tex              # Entry point — compile file ini
├── setup.tex             # Packages, warna, dan konfigurasi global
├── cover.tex             # Halaman cover
├── toc.tex               # (tidak dipakai langsung, TOC via \tableofcontents)
├── chapters/
│   ├── pengembangan.tex  # Bab 1: Proses Pengembangan Dashboard
│   ├── screenshot.tex    # Bab 2: Tangkapan Layar
│   ├── pembagian_tugas.tex # Bab 3: Pembagian Tugas
│   └── tautan.tex        # Bab 4: Tautan Dashboard
├── images/               # Screenshot dashboard (auto-generated, tidak ditrack git)
│   ├── home_full.png
│   ├── home_butterfly.png
│   ├── province_top.png
│   └── province_simulator.png
└── README.md             # File ini
```

> `images/` tidak ditrack di git. Untuk meregenerasi screenshot, jalankan app Dash  
> (`python app.py` dari root project) lalu jalankan script screenshot di bawah ini:

```bash
# Dari root project, jalankan app dulu
python app.py &
sleep 5

# Generate ulang screenshot
cd docs/laporan_latex_kelompok9/images
python3 - << 'EOF'
import asyncio
from playwright.async_api import async_playwright

async def screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"], headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 900})
        await page.goto("http://127.0.0.1:8050/", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path="home_full.png")
        await page.evaluate("window.scrollTo(0, 900)")
        await page.wait_for_timeout(800)
        await page.screenshot(path="home_butterfly.png")
        await page.goto("http://127.0.0.1:8050/province", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path="province_top.png")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="province_simulator.png")
        await browser.close()

asyncio.run(screenshot())
EOF
```

---

## Troubleshooting

| Masalah | Solusi |
|---|---|
| `lualatex: command not found` | Pastikan TeX Live/MiKTeX sudah di PATH. Restart terminal setelah install. |
| Font tidak ditemukan | Jalankan `luaotfload-tool --update` (Linux/macOS) atau reinstall MiKTeX packages |
| `! LaTeX Error: File 'tcolorbox.sty' not found` | Windows: buka MiKTeX Console → Update; Linux: `sudo apt install texlive-latex-extra` |
| Gambar tidak muncul di PDF | Pastikan folder `images/` ada dan berisi `.png`. Jalankan screenshot script di atas. |
| TOC/cross-ref salah | Compile **dua kali** berturut-turut |
| VS Code tidak build otomatis saat save | Settings: `"latex-workshop.latex.autoBuild.run": "onSave"` |
