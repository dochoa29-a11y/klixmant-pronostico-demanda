"""Paleta, formato es-CO y piezas visuales comunes (plotly + Streamlit).

La paleta sale de cifras_clave.json → paleta (la misma del notebook: Okabe-Ito,
COLOR_CANAL, COLOR_FAMILIA, ESTILO_MODELO).
"""
from __future__ import annotations

import math
from datetime import date, datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import textos
from utils.datos import cifras, constantes

# ---------- paleta ----------
_P = cifras()["paleta"]
OKABE_ITO: list[str] = _P["okabe_ito"]
COLOR_CANAL: dict = _P["color_canal"]
COLOR_FAMILIA: dict = _P["color_familia"]
COLOR_EVENTO: str = _P["color_evento"]
COLOR_PRONOSTICO: str = _P["color_pronostico"]
COLOR_INGENUO: str = _P["color_ingenuo"]
_DASH = {"-": "solid", "--": "dash", ":": "dot", "-.": "dashdot"}
ESTILO_MODELO: dict = {m: {"color": e["color"], "dash": _DASH.get(e["linea"], "solid")}
                       for m, e in _P["estilo_modelo"].items()}
COLOR_REAL = "#000000"
GRIS = "#9E9E9E"
COLOR_CLUSTER = {"evento": OKABE_ITO[3], "base": OKABE_ITO[0], "en declive": OKABE_ITO[4],
                 "base errática": OKABE_ITO[1], "cola": GRIS}
COLOR_LINEA = {"COLOMBIA": COLOR_FAMILIA["COLOMBIA"], "FUTBOL": OKABE_ITO[2], "MOTOS": OKABE_ITO[0],
               "AUTOS_Y_MOTOR": OKABE_ITO[5], "PERSONALIZADO": OKABE_ITO[4], "OTROS": GRIS}

MESES = constantes()["meses_es"]
DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]


def estilo_modelo(m: str) -> dict:
    return ESTILO_MODELO.get(m, {"color": GRIS, "dash": "solid"})


def nombre_modelo(m: str) -> str:
    return textos.NOMBRE_MODELO.get(m, m)


# ---------- formato es-CO ----------

def num(x, dec: int = 0) -> str:
    """1234.5 → '1.234,5' (punto de miles, coma decimal)."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    s = f"{x:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def pct(x, dec: int = 0, signo: bool = False) -> str:
    """0.7696 → '77 %'."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    s = num(x * 100, dec) + " %"
    return ("+" + s) if (signo and x > 0) else s


def dec(x, d: int = 3) -> str:
    """0.8973 → '0,897' (para WAPE, MASE…)."""
    return num(x, d)


def a_fecha(x) -> date:
    if isinstance(x, str):
        return datetime.fromisoformat(x).date()
    if isinstance(x, (pd.Timestamp, datetime)):
        return x.date()
    return x


def fecha(x, anio: bool = False) -> str:
    """2026-10-05 → '5-oct' (o '5-oct-2026')."""
    d = a_fecha(x)
    s = f"{d.day}-{MESES[d.month - 1]}"
    return f"{s}-{d.year}" if anio else s


def fechas(serie) -> list[str]:
    return [fecha(v) for v in pd.to_datetime(pd.Series(serie))]


# ---------- plotly ----------
FUENTE = "Source Sans Pro, Segoe UI, sans-serif"


def layout(fig: go.Figure, titulo: str | None = None, y: str | None = None, x: str | None = None,
           alto: int = 420, leyenda: bool = True) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        title=dict(text=titulo, x=0, xanchor="left", y=0.985, yref="container", yanchor="top", font=dict(size=17)) if titulo else None,
        font=dict(family=FUENTE, size=13, color="#262730"),
        separators=",.",  # coma decimal, punto de miles
        height=alto,
        margin=dict(l=10, r=10, t=(95 if leyenda else 55) if titulo else (50 if leyenda else 20), b=10),
        hoverlabel=dict(font_family=FUENTE),
        showlegend=leyenda,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, title=None),
    )
    if y:
        fig.update_yaxes(title_text=y)
    if x:
        fig.update_xaxes(title_text=x)
    fig.update_xaxes(showgrid=False, separatethousands=True)
    fig.update_yaxes(gridcolor="#ECECEC", zerolinecolor="#BDBDBD", separatethousands=True)
    return fig


def eje_meses(fig: go.Figure, inicio, fin, eje: str = "x", cada: int = 1) -> go.Figure:
    """Pone marcas mensuales con los meses en español en un eje de fechas."""
    i, f = pd.Timestamp(a_fecha(inicio)), pd.Timestamp(a_fecha(fin))
    marcas = pd.date_range(i.replace(day=1), f, freq="MS")[::cada]
    marcas = [m for m in marcas if m >= i - pd.Timedelta(days=3)] or [i]
    texto = [MESES[m.month - 1] + (f"<br>{m.year}" if (k == 0 or m.month == 1) else "") for k, m in enumerate(marcas)]
    fig.update_layout(**{f"{eje}axis": dict(tickmode="array", tickvals=marcas, ticktext=texto)})
    return fig


def banda_mundial(fig: go.Figure, ventana: bool = True, partidos: bool = False, texto: bool = True,
                  fila: int | None = None, col: int | None = None) -> go.Figure:
    """Banda sombreada del Mundial (11-jun → 19-jul) y, opcional, de la ventana del evento (25-may → 13-jul)."""
    c = constantes()
    kw = dict(row=fila, col=col) if fila else {}
    if ventana:
        v0, v1 = c["ventana_evento"]
        fig.add_vrect(x0=v0, x1=v1, fillcolor=COLOR_EVENTO, opacity=0.13, line_width=0, layer="below", **kw)
    m0, m1 = c["mundial"]
    fig.add_vrect(x0=m0, x1=m1, fillcolor=COLOR_EVENTO, opacity=0.30, line_width=0, layer="below", **kw)
    if texto and not fila:
        fig.add_annotation(x=m0, y=1, yref="paper", text="⚽ Mundial",
                           showarrow=False, xanchor="left", yanchor="top", font=dict(size=11, color="#6B5B00"))
    if partidos:
        for p in c["partidos_colombia"]:
            fig.add_vline(x=p["fecha"], line_width=1, line_dash="dot", line_color=COLOR_FAMILIA["COLOMBIA"], **kw)
    return fig


def mostrar(fig: go.Figure, key: str | None = None) -> None:
    """st.plotly_chart con la barra de herramientas mínima."""
    config = {"displaylogo": False, "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
              "toImageButtonOptions": {"format": "png", "scale": 2}}
    st.plotly_chart(fig, width="stretch", config=config, key=key)


def tabla_st(df: pd.DataFrame, **kw) -> None:
    st.dataframe(df, width="stretch", hide_index=True, **kw)


# ---------- piezas de página ----------

CSS = """
<style>
.block-container {padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1400px;}
.titular {font-size: 1.55rem; line-height: 1.35; font-weight: 650; color: #1F2A44;
          border-left: 6px solid %(acento)s; background: #F4F8FC; padding: .9rem 1.1rem;
          border-radius: 0 .5rem .5rem 0; margin: .3rem 0 1.1rem 0;}
.titular b {color: %(acento)s;}
.borrador {font-size: .78rem; color: #8A6D00; background: #FFF8DC; padding: .15rem .5rem; border-radius: .3rem;}
div[data-testid="stMetric"] {background: #FFFFFF; border: 1px solid #E6EAF0; border-radius: .6rem;
          padding: .7rem .9rem; box-shadow: 0 1px 2px rgba(0,0,0,.04);}
div[data-testid="stMetricValue"] {font-size: clamp(1.15rem, 2.1vw, 1.75rem);}
div[data-testid="stMetricValue"] *, div[data-testid="stMetricLabel"] * {
          white-space: normal !important; overflow: visible !important; text-overflow: clip !important;}
.tarjeta {border: 1px solid #E6EAF0; border-radius: .6rem; padding: .8rem 1rem; background: #FFFFFF; height: 100%%;}
.tarjeta h4 {margin: 0 0 .3rem 0; font-size: 1.02rem;}
.tarjeta p {margin: 0; font-size: .9rem; color: #444;}
.paso {font-size: .75rem; font-weight: 700; color: %(acento)s; letter-spacing: .04em; text-transform: uppercase;}
@media (max-width: 640px) {
  .titular {font-size: 1.18rem; padding: .7rem .8rem;}
  h1 {font-size: 1.9rem !important;}
  div[data-testid="stMetricValue"] {font-size: 1.35rem;}
  .block-container {padding-left: 1rem; padding-right: 1rem;}
}
</style>
""" % {"acento": COLOR_PRONOSTICO}


def css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado(titulo: str, conclusion_html: str, icono: str = "") -> None:
    """Título de la página + frase-conclusión grande + acceso rápido al glosario."""
    c1, c2 = st.columns([5, 1], vertical_alignment="bottom")
    with c1:
        st.title(f"{icono} {titulo}".strip())
    with c2:
        with st.popover("📖 Glosario", width="stretch"):
            for termino, definicion in textos.GLOSARIO.items():
                st.markdown(f"**{termino}.** {definicion}")
    st.markdown(f'<div class="titular">{conclusion_html}</div>', unsafe_allow_html=True)


def kpis(items: list[tuple]) -> None:
    """items = [(etiqueta, valor, delta|None, ayuda|None, delta_color?)]."""
    cols = st.columns(len(items))
    for col, it in zip(cols, items):
        etiqueta, valor = it[0], it[1]
        delta = it[2] if len(it) > 2 else None
        ayuda = it[3] if len(it) > 3 else None
        color = it[4] if len(it) > 4 else "normal"
        col.metric(etiqueta, valor, delta=delta, help=ayuda, delta_color=color)


def como_leer(texto: str) -> None:
    with st.expander("¿Cómo leer esta gráfica?"):
        st.markdown(texto)


def nota_borrador() -> None:
    st.markdown('<span class="borrador">✍️ Texto en borrador: el grupo lo redactará con sus palabras.</span>',
                unsafe_allow_html=True)
