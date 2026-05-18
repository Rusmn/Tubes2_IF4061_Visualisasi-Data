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
            linear-gradient(145deg, rgba(192,39,45,.14) 0%, rgba(45,46,45,0) 32%),
            linear-gradient(180deg, #2D2E2D 0%, #171514 100%);
    }}
    section[data-testid="stSidebar"] {{
        background: rgba(27,23,21,.92);
        border-right: 1px solid rgba(237,229,214,.10);
    }}
    section[data-testid="stSidebar"] label {{
        color: rgba(237,229,214,.88) !important;
        font-weight: 700;
    }}
    div[data-testid="stSidebarUserContent"] {{
        padding-top: 1rem;
    }}
    h1, h2, h3 {{
        font-family: Oswald, Inter, sans-serif;
        letter-spacing: 0;
    }}
    h2, h3 {{
        color: {COLORS["paper"]};
    }}
    .hero {{
        border-bottom: 3px solid {COLORS["red"]};
        padding: 1.3rem 0 1.2rem;
        margin-bottom: 1.2rem;
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
        background: linear-gradient(135deg, rgba(38,33,31,.96), rgba(45,46,45,.76));
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
    .tabnote {{
        color: rgba(237,229,214,.82);
        max-width: 980px;
        line-height: 1.62;
        margin: -.25rem 0 1rem;
    }}
    .block {{
        background: rgba(27,23,21,.62);
        border: 1px solid rgba(237,229,214,.10);
        border-radius: 8px;
        padding: 1rem 1.15rem;
        box-shadow: 0 12px 34px rgba(0,0,0,.18);
    }}
    .block h3 {{
        margin-top: 0;
        color: {COLORS["gold"]};
    }}
    .mini {{
        background: rgba(237,229,214,.055);
        border: 1px solid rgba(237,229,214,.10);
        border-radius: 8px;
        padding: .82rem .9rem;
        margin: .55rem 0;
    }}
    .mini strong {{
        color: {COLORS["gold"]};
    }}
    .chip {{
        display: inline-block;
        border: 1px solid rgba(218,165,32,.42);
        border-radius: 999px;
        color: rgba(237,229,214,.92);
        padding: .22rem .65rem;
        margin: .1rem .2rem .1rem 0;
        font-size: .82rem;
        background: rgba(218,165,32,.08);
    }}
    div[data-testid="stMetric"] {{
        background: rgba(27,23,21,.62);
        border: 1px solid rgba(237,229,214,.10);
        border-radius: 8px;
        padding: .9rem;
    }}
    div[data-testid="stMetricLabel"] {{
        color: rgba(237,229,214,.72);
    }}
    div[data-testid="stMetricValue"] {{
        color: {COLORS["gold"]};
        font-family: Oswald, Inter, sans-serif;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: .35rem;
        border-bottom: 1px solid rgba(237,229,214,.12);
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px 8px 0 0;
        color: rgba(237,229,214,.72);
        background: rgba(27,23,21,.34);
    }}
    .stTabs [aria-selected="true"] {{
        color: {COLORS["paper"]};
        background: rgba(192,39,45,.22);
    }}
    div[data-testid="stPlotlyChart"] {{
        background: rgba(27,23,21,.36);
        border: 1px solid rgba(237,229,214,.08);
        border-radius: 8px;
        padding: .35rem;
    }}
    button[kind="secondary"], div[data-baseweb="select"] > div {{
        border-radius: 8px;
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
