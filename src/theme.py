from __future__ import annotations

COLORS = {
    "bg": "#0B1114",
    "bg2": "#111A1D",
    "panel": "#142126",
    "panel2": "#18282E",
    "panel3": "#22333A",
    "border": "rgba(236,230,215,0.14)",
    "grid": "rgba(236,230,215,0.10)",
    "text": "#F2EADB",
    "muted": "#B2B6AE",
    "muted2": "#7C8782",
    "red": "#BD3437",
    "red_hot": "#E55348",
    "red_dark": "#8E2A2D",
    "red_deep": "#762222",
    "gold": "#C69A3A",
    "gold_light": "#EAD27A",
    "amber": "#D08B45",
    "green": "#6D9B74",
    "teal": "#569F98",
    "blue": "#68A6C8",
    "purple": "#AD6DBE",
    "cream": "#F4E6C8",
}

CHOROPLETH_SCALE = [
    [0.00, "#B9C7C0"],
    [0.25, "#EAD27A"],
    [0.50, "#D08B45"],
    [0.75, "#BD3437"],
    [1.00, "#762222"],
]

COMMODITY_COLORS = {
    "Rokok": COLORS["red_deep"],
    "Sayur": COLORS["green"],
    "Ikan": COLORS["teal"],
    "Telur & susu": COLORS["gold_light"],
    "Daging": COLORS["amber"],
    "Buah": COLORS["purple"],
    "Gizi total": COLORS["gold"],
}

GRAPH_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
}


def base_layout(height: int | None = None, showlegend: bool = False) -> dict:
    layout: dict = {
        "autosize": height is None,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, system-ui, sans-serif", "color": COLORS["text"], "size": 12},
        "margin": {"l": 56, "r": 44, "t": 48, "b": 48},
        "showlegend": showlegend,
        "legend": {"orientation": "h", "y": 1.08, "x": 0, "bgcolor": "rgba(0,0,0,0)", "font": {"size": 11}},
        "hoverlabel": {"bgcolor": "#18282E", "font_color": COLORS["text"], "bordercolor": COLORS["border"]},
        "title": {"font": {"size": 15, "color": COLORS["text"]}, "x": 0.02, "xanchor": "left"},
        "xaxis": {
            "gridcolor": COLORS["grid"],
            "zerolinecolor": COLORS["grid"],
            "linecolor": COLORS["border"],
            "tickfont": {"color": COLORS["muted"]},
            "title": {"font": {"color": COLORS["muted"]}},
        },
        "yaxis": {
            "gridcolor": COLORS["grid"],
            "zerolinecolor": COLORS["grid"],
            "linecolor": COLORS["border"],
            "tickfont": {"color": COLORS["muted"]},
            "title": {"font": {"color": COLORS["muted"]}},
        },
    }
    if height is not None:
        layout["height"] = height
    return layout
