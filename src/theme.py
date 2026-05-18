from __future__ import annotations


COLORS = {
    "bg": "#2D2E2D",
    "deep": "#1B1715",
    "panel": "rgba(38,33,31,0.78)",
    "red": "#C0272D",
    "red_dark": "#8B0000",
    "red_hot": "#F73227",
    "gold": "#DAA520",
    "gold_dark": "#B8860B",
    "paper": "#EDE5D6",
    "green": "#6FAF4E",
    "blue": "#CBD5E3",
    "gray": "#8A8A8A",
    "gray_dark": "#6B6B6B",
}


def page_css() -> str:
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Oswald:wght@500;600;700&display=swap');
    html, body, [class*="css"] {{
        font-family: Inter, sans-serif;
        color: {COLORS["paper"]};
    }}
    .stApp {{
        background:
            radial-gradient(circle at top right, rgba(192,39,45,.22), transparent 28rem),
            linear-gradient(180deg, #2D2E2D 0%, #171514 100%);
    }}
    h1, h2, h3 {{
        font-family: Oswald, Inter, sans-serif;
        letter-spacing: 0;
    }}
    .hero {{
        border-bottom: 4px solid {COLORS["red"]};
        padding: 1.4rem 0 1.1rem;
        margin-bottom: 1rem;
    }}
    .hero h1 {{
        font-size: clamp(2.2rem, 5vw, 4.6rem);
        line-height: .95;
        margin: 0;
    }}
    .gold {{ color: {COLORS["gold"]}; }}
    .paper {{ color: {COLORS["paper"]}; }}
    .lead {{
        max-width: 920px;
        color: rgba(237,229,214,.84);
        font-size: 1.05rem;
        line-height: 1.65;
        margin-top: .8rem;
    }}
    .kpi {{
        background: linear-gradient(135deg, rgba(38,33,31,.95), rgba(45,46,45,.78));
        border: 1px solid rgba(237,229,214,.12);
        border-left: 5px solid {COLORS["gold"]};
        border-radius: 8px;
        padding: 1rem;
        min-height: 126px;
        box-shadow: 0 10px 28px rgba(0,0,0,.22);
    }}
    .kpi small {{
        color: rgba(237,229,214,.7);
        text-transform: uppercase;
        letter-spacing: .08em;
        font-weight: 700;
    }}
    .kpi strong {{
        display: block;
        font-family: Oswald, Inter, sans-serif;
        color: {COLORS["gold"]};
        font-size: 2.25rem;
        line-height: 1.05;
        margin-top: .3rem;
    }}
    .kpi span {{
        color: rgba(237,229,214,.78);
        font-size: .92rem;
    }}
    .note {{
        color: rgba(237,229,214,.68);
        font-size: .88rem;
        line-height: 1.55;
    }}
    .block {{
        background: rgba(27,23,21,.62);
        border: 1px solid rgba(237,229,214,.10);
        border-radius: 8px;
        padding: 1rem 1.1rem;
    }}
    div[data-testid="stMetric"] {{
        background: rgba(27,23,21,.62);
        border: 1px solid rgba(237,229,214,.10);
        border-radius: 8px;
        padding: .9rem;
    }}
    </style>
    """


def plot_theme() -> dict:
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, sans-serif", "color": COLORS["paper"]},
        "colorway": [
            COLORS["red"],
            COLORS["gold"],
            COLORS["green"],
            COLORS["blue"],
            COLORS["gray"],
        ],
        "margin": {"l": 20, "r": 20, "t": 56, "b": 28},
    }
