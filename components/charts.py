"""Graphiques Plotly interactifs (thème sombre SolarScope AI)."""
import numpy as np
import plotly.graph_objects as go

from components.theme import COLORS

TEMPLATE = "plotly_dark"
LAYOUT = dict(
    template=TEMPLATE,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, Segoe UI, Arial, sans-serif", color=COLORS["text"]),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(orientation="h", y=1.08, x=0),
    hovermode="x unified",
)


def _layout(fig, height, **extra):
    fig.update_layout(**{**LAYOUT, "height": height, **extra})
    fig.update_xaxes(gridcolor="#ffffff12", zerolinecolor="#ffffff12")
    fig.update_yaxes(gridcolor="#ffffff12", zerolinecolor="#ffffff12")
    return fig


def forecast(dates, observed, q10, q50, q90, height=460, title=None):
    """Observations, Q10, Q50 et Q90 : bande d'incertitude [Q10, Q90] et observations contrastées."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=q90, line=dict(color=COLORS["gold"], width=1.2),
                             name="Q90 (haut)", hovertemplate="%{y:.2f}"))
    fig.add_trace(go.Scatter(x=dates, y=q10, line=dict(color=COLORS["violet"], width=1.2),
                             fill="tonexty", fillcolor="rgba(139,124,255,0.16)",
                             name="Q10 (bas)", hovertemplate="%{y:.2f}"))
    fig.add_trace(go.Scatter(x=dates, y=q50, line=dict(color=COLORS["cyan"], width=2.2),
                             name="Q50 (médiane)", hovertemplate="%{y:.2f}"))
    fig.add_trace(go.Scatter(x=dates, y=observed, line=dict(color=COLORS["text"], width=1.6),
                             name="Observé", mode="lines", hovertemplate="%{y:.2f}"))
    fig.update_yaxes(title_text="kWh/m²/j")
    if title:
        fig.update_layout(title=dict(text=title, x=0))
    fig.update_xaxes(rangeslider=dict(visible=False),
                     rangeselector=dict(buttons=[
                         dict(count=1, label="1 mois", step="month", stepmode="backward"),
                         dict(count=3, label="3 mois", step="month", stepmode="backward"),
                         dict(step="all", label="Tout")]))
    return _layout(fig, height)


def map_sites(meta, selected=None):
    """Carte interactive des sites (coordonnées réelles de resultats_groupe.csv)."""
    colors = [COLORS["cyan"] if (selected is None or s == selected) else COLORS["grey"]
              for s in meta["site"]]
    fig = go.Figure(go.Scattergeo(
        lat=meta["lat"], lon=meta["lon"], text=meta["site"], mode="markers+text",
        textposition="top center", marker=dict(size=16, color=colors, line=dict(width=2, color="#D6FFFB")),
        hovertemplate="<b>%{text}</b><br>lat %{lat:.2f}, lon %{lon:.2f}<extra></extra>",
    ))
    fig.update_geos(projection_type="natural earth", showland=True, landcolor="#10243a",
                    showocean=True, oceancolor="#07111F", showcountries=True, countrycolor="#ffffff22",
                    lataxis_range=[-5, 45], lonaxis_range=[-25, 30], coastlinecolor="#ffffff22",
                    bgcolor="rgba(0,0,0,0)")
    return _layout(fig, 380, geo=dict(bgcolor="rgba(0,0,0,0)"))


def histogram(values, height=300, name="Rayonnement"):
    fig = go.Figure(go.Histogram(x=values, nbinsx=40, marker_color=COLORS["cyan"], opacity=0.85, name=name))
    fig.update_xaxes(title_text="kWh/m²/j")
    fig.update_yaxes(title_text="Jours")
    return _layout(fig, height, showlegend=False, hovermode="x")


def bars(categories, series, height=320, colors=None, yaxis_title=None, yaxis_format=None):
    """series : dict nom -> liste de valeurs."""
    palette = colors or [COLORS["cyan"], COLORS["violet"], COLORS["gold"], COLORS["green"]]
    fig = go.Figure()
    for i, (name, values) in enumerate(series.items()):
        fig.add_trace(go.Bar(x=categories, y=values, name=name, marker_color=palette[i % len(palette)],
                             hovertemplate="%{y:.3f}"))
    fig.update_layout(barmode="group")
    if yaxis_title:
        fig.update_yaxes(title_text=yaxis_title)
    if yaxis_format:
        fig.update_yaxes(tickformat=yaxis_format)
    return _layout(fig, height)


def convergence(curves, height=420, bound=None, log=True, xlabel="itération", ylabel="écart à l'optimum"):
    """curves : dict nom -> (x, y). bound : (x, y) optionnel, courbe théorique en pointillés."""
    fig = go.Figure()
    palette = [COLORS["cyan"], COLORS["violet"], COLORS["gold"], COLORS["green"], COLORS["red"], COLORS["text"]]
    for i, (name, (x, y)) in enumerate(curves.items()):
        y = np.asarray(y, dtype=float)
        y = np.where(y <= 0, np.nan, y) if log else y
        fig.add_trace(go.Scatter(x=x, y=y, name=name, mode="lines", line=dict(color=palette[i % len(palette)], width=2)))
    if bound is not None:
        x, y = bound
        fig.add_trace(go.Scatter(x=x, y=y, name="borne théorique", mode="lines",
                                 line=dict(color="#ffffff", dash="dash", width=1.5)))
    fig.update_xaxes(title_text=xlabel)
    fig.update_yaxes(title_text=ylabel, type="log" if log else "linear")
    return _layout(fig, height)
