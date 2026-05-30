from __future__ import annotations

from dash import dcc, html


def layout(*args, **kwargs) -> html.Div:
    return html.Div(dcc.Location(id="_policy-redirect", href="/province", refresh=True))
