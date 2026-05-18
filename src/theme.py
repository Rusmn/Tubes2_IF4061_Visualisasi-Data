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
    .block-container {{
        max-width: 1320px;
        padding: 1.25rem 2rem 3rem;
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
        padding: .8rem 0 1.2rem;
        margin-bottom: 1.1rem;
        position: relative;
    }}
    .hero::before {{
        content: "";
        display: block;
        width: 104px;
        height: 4px;
        border-radius: 999px;
        background: {COLORS["red"]};
        margin-bottom: 1.05rem;
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
        background: linear-gradient(145deg, rgba(39,35,33,.94), rgba(31,30,29,.88));
        border: 1px solid rgba(237,229,214,.12);
        border-left: 4px solid {COLORS["gold"]};
        border-radius: 8px;
        padding: 1.05rem 1.1rem;
        min-height: 142px;
        height: 100%;
        box-shadow: 0 12px 30px rgba(0,0,0,.20);
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }}
    .kpi small {{
        color: rgba(237,229,214,.7);
        text-transform: uppercase;
        letter-spacing: .06em;
        font-weight: 700;
        font-size: .76rem;
        line-height: 1.25;
    }}
    .kpi strong {{
        display: block;
        font-family: Oswald, Inter, sans-serif;
        color: {COLORS["gold"]};
        font-size: clamp(2rem, 2.4vw, 2.75rem);
        line-height: 1.05;
        margin-top: .42rem;
        overflow-wrap: anywhere;
    }}
    .kpi span {{
        color: rgba(237,229,214,.78);
        font-size: .9rem;
        line-height: 1.45;
        margin-top: .2rem;
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
        gap: .45rem;
        border: 1px solid rgba(237,229,214,.11);
        border-radius: 8px;
        background: rgba(27,23,21,.48);
        padding: .35rem;
        margin-top: 1rem;
        margin-bottom: 1.2rem;
        overflow-x: auto;
    }}
    .stTabs button[data-baseweb="tab"] {{
        min-height: 42px;
        border-radius: 7px;
        padding: .68rem 1.05rem !important;
        color: rgba(237,229,214,.72);
        background: transparent;
        border: 1px solid transparent;
        transition: background .16s ease, border-color .16s ease, color .16s ease;
    }}
    .stTabs button[data-baseweb="tab"] p {{
        font-size: .93rem;
        line-height: 1;
        font-weight: 700;
        margin: 0;
        white-space: nowrap;
    }}
    .stTabs [aria-selected="true"] {{
        color: {COLORS["paper"]};
        background: rgba(192,39,45,.24);
        border-color: rgba(192,39,45,.62);
        box-shadow: inset 0 -2px 0 {COLORS["red_hot"]};
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
    div[data-baseweb="select"] > div {{
        min-height: 42px;
        border-color: rgba(237,229,214,.18);
        background: rgba(27,23,21,.70);
        padding-left: .35rem;
        padding-right: .35rem;
    }}
    div[data-testid="stSlider"] {{
        padding: .2rem .05rem .7rem;
    }}
    @media (max-width: 900px) {{
        .block-container {{
            padding: 1rem 1rem 2.4rem;
        }}
        .kpi {{
            min-height: 122px;
        }}
        .stTabs button[data-baseweb="tab"] {{
            padding: .64rem .85rem !important;
        }}
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
