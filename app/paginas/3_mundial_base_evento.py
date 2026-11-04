"""3 · Mundial: base vs evento — la pregunta central de Klixmant."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import estilo as E
from utils import textos as T
from utils.datos import constantes, kpi, tabla

k = kpi()
c = constantes()
top = tabla("base_evento_top")
agr = tabla("base_evento_agregado")
inc_top = tabla("incremental_mundial_top")
inc_lin = tabla("incremental_mundial_linea")
sens = tabla("sensibilidad_base_evento")
rutas = tabla("comparacion_rutas")

lin = inc_lin.set_index("linea")
caen = lin[lin["uds_evento_neto"] < 0].sort_values("uds_evento_neto")
nombres_caen = " y ".join(n.replace("AUTOS_Y_MOTOR", "autos").lower() for n in caen.index[:2])

E.encabezado(
    "Mundial: base vs evento",
    f"El <b>{E.pct(k['pct_evento_colombia'])}</b> de lo que vendió Colombia en la ventana del Mundial fue <b>evento</b>; "
    f"{nombres_caen} <b>cayeron</b>.",
    "⚽",
)

E.kpis([
    ("Uds de evento · Colombia", "+" + E.num(k["uds_evento_colombia"]), None, "Venta real − base en la ventana del evento."),
    ("Parte de su venta que fue evento", E.pct(k["pct_evento_colombia"])),
    ("Evento neto · resto de catálogos", E.num(k["uds_evento_resto_neto"]), None,
     "Negativo: el resto vendió menos de lo normal durante el Mundial (demanda desplazada)."),
    ("Rango según supuestos", f"{E.num(sens['evento_COLOMBIA'].min())}–{E.num(sens['evento_COLOMBIA'].max())}", None,
     "Mínimo y máximo del evento Colombia al cambiar cómo se estima la base (tabla de sensibilidad)."),
])
st.caption(f"Ventana del evento: {E.fecha(c['ventana_evento'][0])} → {E.fecha(c['ventana_evento'][1])} · "
           f"Mundial: {E.fecha(c['mundial'][0])} → {E.fecha(c['mundial'][1])}")

st.write("")
st.subheader("Explore: ¿cuánto fue ritmo normal y cuánto fue Mundial?")
f1, f2 = st.columns([1, 2])
nivel = f1.radio("Nivel", ["Total", "Familia", "Línea", "Catálogo del top"], horizontal=True, key="p3_nivel")
if nivel == "Catálogo del top":
    opciones = top.groupby("catalogo")["rank"].first().sort_values().index.tolist()
    grupo = f2.selectbox("Catálogo", opciones, key="p3_cat")
    d = top[top["catalogo"] == grupo]
else:
    mapa = {"Total": "total", "Familia": "familia", "Línea": "linea"}
    sub = agr[agr["nivel"] == mapa[nivel]]
    opciones = sorted(sub["grupo"].unique(), key=lambda g: (g != "COLOMBIA", g))
    grupo = f2.selectbox("Grupo", opciones, key="p3_grupo", disabled=nivel == "Total")
    d = sub[sub["grupo"] == grupo]
d = d.sort_values("semana")
txt = E.fechas(d["semana"])

fig = go.Figure()
fig.add_trace(go.Scatter(x=d["semana"], y=d["y_base"], name="Base (sin Mundial)", mode="lines",
                         line=dict(color=E.COLOR_PRONOSTICO, width=2.5, dash="dash"), text=txt,
                         hovertemplate="Base · %{text}: %{y:,.0f} uds<extra></extra>"))
fig.add_trace(go.Scatter(x=d["semana"], y=d["y"], name="Venta real", mode="lines", fill="tonexty",
                         fillcolor="rgba(240,228,66,0.55)", line=dict(color=E.COLOR_REAL, width=2.5),
                         customdata=d["y_evento"], text=txt,
                         hovertemplate="Real · %{text}: %{y:,.0f} uds<br>Evento: %{customdata:+,.0f} uds<extra></extra>"))
E.banda_mundial(fig, partidos=True)
tot_ev = d["y_evento"].sum()
E.layout(fig, f"{grupo.title() if nivel != 'Total' else 'Total'}: {E.num(tot_ev)} uds de evento neto en todo el periodo",
         y="uds / semana", alto=460)
E.eje_meses(fig, d["semana"].min(), d["semana"].max())
E.mostrar(fig, "p3_base_evento")
E.como_leer(T.COMO_LEER["base_evento"])

st.divider()
izq, der = st.columns([3, 2], gap="large")
with izq:
    r = inc_top.sort_values("uds_evento_neto")
    fig = go.Figure(go.Bar(
        x=r["uds_evento_neto"], y=r["catalogo"], orientation="h",
        marker_color=[E.COLOR_FAMILIA.get(f, E.GRIS) for f in r["familia"]],
        customdata=np.stack([r["uds_reales"], r["uds_base"], r["pct_evento_sobre_real"].fillna(0), r["cluster"].fillna("")], axis=1),
        hovertemplate="<b>%{y}</b><br>Evento neto: %{x:+,.0f} uds<br>Real %{customdata[0]:,.0f} · base %{customdata[1]:,.0f}"
                      "<br>Evento / real: %{customdata[2]:.0%}<br>Clúster: %{customdata[3]}<extra></extra>",
    ))
    fig.add_vline(x=0, line_color="#666")
    E.layout(fig, "Unidades de evento por catálogo del top (ventana del Mundial)", x="uds de evento neto", alto=600, leyenda=False)
    E.mostrar(fig, "p3_inc_top")
    st.caption("🟥 familia Colombia · 🟦 resto")
    E.como_leer(T.COMO_LEER["incremental"])
with der:
    r = inc_lin.sort_values("uds_evento_neto")
    fig = go.Figure(go.Bar(
        x=r["uds_evento_neto"], y=[l.replace("_", " ").capitalize() for l in r["linea"]], orientation="h",
        marker_color=[E.COLOR_LINEA.get(l, E.GRIS) for l in r["linea"]],
        text=[E.pct(p, signo=True) for p in r["pct_evento_sobre_real"]], textposition="outside", cliponaxis=False,
        customdata=np.stack([r["uds_reales"], r["uds_base"]], axis=1),
        hovertemplate="<b>%{y}</b><br>Evento: %{x:+,.0f} uds<br>Real %{customdata[0]:,.0f} · base %{customdata[1]:,.0f}<extra></extra>",
    ))
    fig.add_vline(x=0, line_color="#666")
    lim = r["uds_evento_neto"].abs().max() * 1.3
    E.layout(fig, "Por línea de producto", x="uds de evento neto", alto=380, leyenda=False)
    fig.update_xaxes(range=[r["uds_evento_neto"].min() * 1.6, lim])
    E.mostrar(fig, "p3_inc_lin")
    E.como_leer(T.COMO_LEER["linea"])

    pos = lin["uds_evento_positivo"].sum()
    desp = lin["uds_desplazadas"].sum()
    st.info(
        f"**Demanda desplazada (hipótesis por validar).** Sumando las semanas en que cada línea vendió por encima de su base hay "
        f"**{E.num(pos)}** uds; las semanas por debajo restan **{E.num(-desp)}**. Parte de la caída de motos y autos "
        "podría ser clientes que ese mes compraron la camiseta de Colombia en vez de su prenda habitual. "
        "Con estos datos no se puede probar: conviene validarlo con Klixmant.", icon="🔄")

st.divider()
izq, der = st.columns(2, gap="large")
with izq:
    piv = sens.pivot(index="semanas_pre", columns="k_nivel", values="evento_COLOMBIA")
    pct_piv = sens.pivot(index="semanas_pre", columns="k_nivel", values="pct_evento_COLOMBIA")
    texto = [[f"{E.num(v)}<br>{E.pct(p)}" for v, p in zip(fr, fp)] for fr, fp in zip(piv.values, pct_piv.values)]
    fig = go.Figure(go.Heatmap(
        z=piv.values, x=[f"k = {c}" for c in piv.columns], y=[f"{s} sem. previas" for s in piv.index],
        colorscale="YlOrBr", text=texto, texttemplate="%{text}", hovertemplate="%{y} · %{x}: %{z:,.0f} uds<extra></extra>",
        colorbar=dict(title="uds"),
    ))
    E.layout(fig, "Sensibilidad: el evento Colombia cambia poco", alto=380, leyenda=False)
    E.mostrar(fig, "p3_sens")
    E.como_leer(T.COMO_LEER["sensibilidad"])
with der:
    r = rutas[rutas["grupo"] == "existía antes"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=r["familia"].str.capitalize(), y=r["evento_ruta1"], name="Ruta 1 · interpolación", marker_color=E.OKABE_ITO[1],
                         hovertemplate="%{x} · ruta 1: %{y:+,.0f} uds<extra></extra>"))
    fig.add_trace(go.Bar(x=r["familia"].str.capitalize(), y=r["evento_ruta2"], name="Ruta 2 · modelo sin Mundial", marker_color=E.OKABE_ITO[0],
                         hovertemplate="%{x} · ruta 2: %{y:+,.0f} uds<extra></extra>"))
    fig.update_layout(barmode="group")
    E.layout(fig, "Dos rutas, misma historia", y="uds de evento (catálogos que ya existían)", alto=380)
    E.mostrar(fig, "p3_rutas")
    nacio = rutas[rutas["grupo"] == "nació en la ventana"]["uds_reales"].sum()
    st.caption(f"Además, {E.num(nacio)} uds vinieron de catálogos que **nacieron** en la ventana del evento (todo es evento).")
    E.como_leer(T.COMO_LEER["rutas"])

with st.expander("Partidos de Colombia en el Mundial"):
    E.tabla_st(pd.DataFrame([{"Fecha": E.fecha(p["fecha"], True), "Partido": p["evento"]} for p in c["partidos_colombia"]]))

E.nota_borrador()
