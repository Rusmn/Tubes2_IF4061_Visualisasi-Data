COLORS = {
    # ── Background — dari infografis statis ─────────────────────────────────────
    "bg_app":         "#26211F",   # very dark warm brown (base infografis)
    "bg_card":        "#2D2E2D",   # card (sedikit lebih terang + netral)
    "bg_card_hover":  "#363330",
    "bg_header":      "#1E1A18",   # header lebih gelap
    "border":         "#3D3530",   # warm brown border
    "border_hover":   "#5C4A3A",

    # ── Tobacco (rokok) — merah khas infografis ──────────────────────────────────
    "tobacco_primary": "#C0272D",  # crimson utama
    "tobacco_dark":    "#5C0000",  # very dark red
    "tobacco_light":   "#F73227",  # bright red
    "tobacco_glow":    "#C0272D28",

    # ── Nutrition (gizi) ─────────────────────────────────────────────────────────
    "gizi_primary":  "#3DD68C",
    "gizi_teal":     "#2DD4BF",
    "gizi_orange":   "#DB9541",    # dari infografis
    "gizi_light":    "#86EFAC",

    # ── Commodity colors ──────────────────────────────────────────────────────────
    "sayur":    "#4ADE80",
    "ikan":     "#5BA3C9",         # biru lebih warm (bukan sky blue terlalu terang)
    "telur":    "#DB9541",         # amber dari infografis
    "daging":   "#C0272D",
    "buah":     "#BE9434",         # gold-bronze dari infografis
    "susu":     "#EDE5D6",

    # ── Semantic ──────────────────────────────────────────────────────────────────
    "gold":     "#DAA520",         # goldenrod utama dari infografis
    "gold_light": "#EED757",       # light gold
    "warning":  "#F73227",
    "neutral":  "#99948F",         # warm grey dari infografis
    "positive": "#4ADE80",

    # ── Text — dari palet infografis ─────────────────────────────────────────────
    "text_primary":   "#EDE5D6",   # warm cream/parchment
    "text_secondary": "#99948F",   # warm grey
    "text_muted":     "#6B6B6B",   # medium grey
    "text_gold":      "#DAA520",

    # ── Choropleth — grey → dark red → bright red (persis infografis) ────────────
    "choro_scale": [
        [0.0,  "#4D4D4D"],   # netral grey (nilai rendah)
        [0.25, "#5C0000"],   # very dark crimson
        [0.55, "#8B0000"],   # dark red
        [0.78, "#C0272D"],   # medium crimson
        [1.0,  "#F73227"],   # bright red (nilai tertinggi)
    ],
    # Protein: merah (rendah) → abu warm → hijau (tinggi)
    "choro_protein_scale": [
        [0.0, "#8B0000"],
        [0.5, "#99948F"],
        [1.0, "#1A9850"],
    ],
}

TYPOGRAPHY = {
    "font_display": "'Oswald', 'Impact', sans-serif",
    "font_heading":  "'Oswald', 'Impact', sans-serif",
    "font_body":     "'Inter', 'Helvetica Neue', sans-serif",
    "font_mono":     "'JetBrains Mono', 'Courier New', monospace",
}

GRAPH_CONFIG = {
    "displayModeBar": True,
    "responsive": True,
    "displaylogo": False,
}
