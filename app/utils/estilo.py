"""Paleta, formato es-CO y piezas visuales comunes (plotly + Streamlit)."""
from __future__ import annotations

import math
from datetime import date, datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import textos
from utils.datos import constantes

# ---------- paleta ----------
# Identidad visual: vinotinto, dorado, rojo, negro y blanco cálido. Los 4 tonos de serie
# (vino, dorado, azul acero, rosa) pasan el validador de color (CVD ΔE >= 8, contraste >= 3:1).
VINO = "#962A3B"          # acento principal: modelo final, pronóstico, marca
VINO_OSCURO = "#5C1424"   # sidebar y títulos
ROJO = "#B3261E"          # alertas puntuales
DORADO = "#B0841A"        # segundo tono: Colombia, Dropi, evento
DORADO_CLARO = "#E3CB86"  # bandas y rellenos
AZUL = "#1F6CAB"          # contraste frío (uso escaso)
ROSA = "#C9688A"
NEGRO = "#1A1A1A"
GRIS = "#8A817C"          # gris cálido: ingenuo, inactivo
GRIS_CLARO = "#C9C1BA"
CREMA = "#FBF7F2"
BORDE = "#E8DDD3"

# Orden fijo de tonos para series sin color asignado (no se cicla más allá de 8).
OKABE_ITO: list[str] = [VINO, DORADO, AZUL, ROSA, GRIS, "#C8B8A6", DORADO_CLARO, NEGRO]
COLOR_CANAL: dict = {"EFFI": VINO, "DROPI": DORADO, "TOTAL": NEGRO}
COLOR_FAMILIA: dict = {"COLOMBIA": DORADO, "RESTO": VINO}
COLOR_EVENTO: str = DORADO_CLARO
COLOR_PRONOSTICO: str = VINO
COLOR_INGENUO: str = GRIS
ESTILO_MODELO: dict = {
    "HGB_sin_atipico": {"color": VINO, "dash": "solid"},
    "HGB_redondeo": {"color": "#B9778A", "dash": "dashdot"},
    "HGB_poisson": {"color": ROSA, "dash": "solid"},
    "HGB+ingenuo": {"color": AZUL, "dash": "solid"},
    "HGB_ingenuo": {"color": AZUL, "dash": "solid"},
    "ingenuo": {"color": GRIS, "dash": "dot"},
    "media_movil_4": {"color": DORADO, "dash": "dash"},
    "ETS": {"color": "#D4A94A", "dash": "dash"},
    "SARIMAX": {"color": "#6E9CC8", "dash": "dash"},
}
COLOR_REAL = NEGRO
COLOR_CLUSTER = {"evento": DORADO, "base": VINO, "en declive": GRIS, "base errática": ROSA, "cola": GRIS_CLARO}
COLOR_LINEA = {"COLOMBIA": DORADO, "FUTBOL": AZUL, "MOTOS": VINO, "AUTOS_Y_MOTOR": ROSA,
               "PERSONALIZADO": "#D4A94A", "OTROS": GRIS_CLARO}
# Escalas secuenciales de un solo tono (claro -> oscuro)
ESCALA_VINO = [[0, "#FBF3F3"], [0.35, "#E2A9B1"], [0.7, "#A8394B"], [1, "#4A0F1C"]]
ESCALA_DORADO = [[0, "#FCF8EC"], [0.4, "#EBD49A"], [0.75, "#B88A22"], [1, "#6B4D0B"]]


def rgba(hex_: str, a: float) -> str:
    h = hex_.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


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


def dec(x, d: int = 3, signo: bool = False) -> str:
    """0.8973 → '0,897' (para WAPE, MASE…). Con signo=True: '+0,220' / '-0,010'
    (guion ASCII: st.metric lo usa para decidir la flecha del delta)."""
    s = num(x, d)
    return ("+" + s) if (signo and s != "—" and x > 0) else s


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
FUENTE = "Inter, Segoe UI, sans-serif"


def layout(fig: go.Figure, titulo: str | None = None, y: str | None = None, x: str | None = None,
           alto: int = 420, leyenda: bool = True) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        title=dict(text=titulo, x=0, xanchor="left", y=0.985, yref="container", yanchor="top", font=dict(size=17, color=VINO_OSCURO)) if titulo else None,
        font=dict(family=FUENTE, size=13, color="#2B2422"),
        separators=",.",  # coma decimal, punto de miles
        height=alto,
        margin=dict(l=10, r=10, t=(95 if leyenda else 55) if titulo else (50 if leyenda else 20), b=10),
        hoverlabel=dict(font_family=FUENTE, bgcolor="#FFFFFF", bordercolor=BORDE, font_color=NEGRO),
        colorway=OKABE_ITO, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=leyenda,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, title=None),
    )
    if y:
        fig.update_yaxes(title_text=y)
    if x:
        fig.update_xaxes(title_text=x)
    fig.update_xaxes(showgrid=False, separatethousands=True)
    fig.update_xaxes(linecolor=GRIS_CLARO, tickfont=dict(color="#5E5551"))
    fig.update_yaxes(gridcolor="#EFE7E0", zerolinecolor=GRIS_CLARO, separatethousands=True, tickfont=dict(color="#5E5551"))
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
        fig.add_vrect(x0=v0, x1=v1, fillcolor=COLOR_EVENTO, opacity=0.22, line_width=0, layer="below", **kw)
    m0, m1 = c["mundial"]
    fig.add_vrect(x0=m0, x1=m1, fillcolor=COLOR_EVENTO, opacity=0.45, line_width=0, layer="below", **kw)
    if texto and not fila:
        fig.add_annotation(x=m0, y=1, yref="paper", text="Mundial",
                           showarrow=False, xanchor="left", yanchor="top", font=dict(size=11, color="#6B4D0B"))
    if partidos:
        for p in c["partidos_colombia"]:
            fig.add_vline(x=p["fecha"], line_width=1, line_dash="dot", line_color=COLOR_FAMILIA["COLOMBIA"], **kw)
    return fig


def mostrar(fig: go.Figure, key: str | None = None) -> None:
    """st.plotly_chart con la barra de herramientas mínima."""
    config = {"displaylogo": False, "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
              "toImageButtonOptions": {"format": "png", "scale": 2}}
    # El título de plotly es SVG y no se ajusta al ancho: en celular se corta. Se saca a HTML (sí se ajusta)
    # y se libera el espacio que ocupaba arriba.
    titulo = fig.layout.title.text if fig.layout.title else None
    if titulo:
        st.markdown(f'<div class="fig-titulo">{titulo}</div>', unsafe_allow_html=True)
        t = fig.layout.margin.t if fig.layout.margin and fig.layout.margin.t is not None else 95
        fig.update_layout(title=None, margin=dict(t=max(10, t - 45)), height=(fig.layout.height or 420) - 30)
    st.plotly_chart(fig, width="stretch", config=config, key=key)


def tabla_st(df: pd.DataFrame, **kw) -> None:
    st.dataframe(df, width="stretch", hide_index=True, **kw)


# ---------- piezas de página ----------

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
.block-container {padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1400px;}
h1, h2, h3 {font-family: 'Playfair Display', Georgia, serif !important; color: %(vino_oscuro)s !important; letter-spacing: -.01em;}
h4, h5 {color: %(vino_oscuro)s !important;}
h1 {font-weight: 700 !important; border-bottom: 3px solid %(dorado)s; padding-bottom: .35rem;}
hr {border-color: %(borde)s !important;}

/* Frase-conclusión */
.titular {font-size: 1.42rem; line-height: 1.4; font-weight: 500; color: #FFFFFF;
          background: linear-gradient(120deg, %(vino_oscuro)s 0%%, %(vino)s 100%%);
          border-left: 6px solid %(dorado)s; padding: 1rem 1.3rem; border-radius: .6rem; margin: .4rem 0 1.2rem 0;
          box-shadow: 0 6px 18px rgba(92,20,36,.18);}
.titular b {color: #F2D88E; font-weight: 700;}

/* KPI */
div[data-testid="stMetric"] {background: #FFFFFF; border: 1px solid %(borde)s; border-top: 4px solid %(vino)s;
          border-radius: .6rem; padding: .75rem .95rem; box-shadow: 0 2px 6px rgba(92,20,36,.06);}
[data-testid="stMetricLabel"] p {color: #6B605B !important; font-weight: 600; font-size: .82rem !important;}
[data-testid="stMetricLabel"] {width: 100%% !important;}
[data-testid="stMetricLabel"] > div {overflow: visible !important;}
div[data-testid="stMetricValue"] {font-size: clamp(1.15rem, 2.1vw, 1.8rem); color: %(vino_oscuro)s; font-weight: 700;}
div[data-testid="stMetricValue"] *, [data-testid="stMetricLabel"] * {
          white-space: normal !important; overflow: visible !important; text-overflow: clip !important;}

/* Tarjetas, contenedores, pestañas y desplegables */
.tarjeta {border: 1px solid %(borde)s; border-radius: .6rem; padding: .8rem 1rem; background: #FFFFFF; height: 100%%;}
.tarjeta h4 {margin: 0 0 .3rem 0; font-size: 1.02rem;}
.tarjeta p {margin: 0; font-size: .9rem; color: #4A403C;}
.stTabs [data-baseweb="tab-list"] {gap: .25rem; border-bottom: 1px solid %(borde)s;}
.stTabs [data-baseweb="tab"] {font-weight: 600; color: #6B605B;}
.stTabs [aria-selected="true"] {color: %(vino)s !important;}
.stTabs [data-baseweb="tab-highlight"] {background-color: %(dorado)s !important; height: 3px;}
div[data-testid="stExpander"] details {border-color: %(borde)s !important; background: #FFFFFF;}
div[data-testid="stExpander"] summary p {color: %(vino)s; font-weight: 600;}
.fig-titulo {font-size: 1.04rem; font-weight: 600; color: %(vino_oscuro)s; line-height: 1.3; margin: .6rem 0 -.2rem 0;}
.paso {font-size: .72rem; font-weight: 700; color: %(dorado)s; letter-spacing: .08em; text-transform: uppercase;}

/* Sidebar */
section[data-testid="stSidebar"] {border-right: 3px solid %(dorado)s;}
.marca {font-family: 'Playfair Display', Georgia, serif; font-size: 1.45rem; font-weight: 700; color: #FFFFFF;
        letter-spacing: .06em; border-bottom: 2px solid %(dorado)s; padding-bottom: .3rem; margin-bottom: .4rem;}
.marca span {color: #E3CB86; font-size: .95rem; letter-spacing: .02em;}

@media (max-width: 640px) {
  .titular {font-size: 1.12rem; padding: .75rem .9rem;}
  h1 {font-size: 1.8rem !important;}
  div[data-testid="stMetricValue"] {font-size: 1.35rem;}
  .block-container {padding-left: 1rem; padding-right: 1rem;}
}
</style>
""" % {"vino": VINO, "vino_oscuro": VINO_OSCURO, "dorado": DORADO, "borde": BORDE}


def css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado(titulo: str, conclusion_html: str, icono: str = "") -> None:
    """Título de la página + frase-conclusión grande + acceso rápido al glosario."""
    c1, c2 = st.columns([5, 1], vertical_alignment="bottom")
    with c1:
        st.title(f"{icono} {titulo}".strip())
    with c2:
        with st.popover("Glosario", width="stretch"):
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
