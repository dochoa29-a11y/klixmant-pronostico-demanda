"""Inicio — resumen ejecutivo en 30 segundos."""
import plotly.graph_objects as go
import streamlit as st

from utils import estilo as E
from utils import textos as T
from utils.datos import constantes, kpi, tabla

k = kpi()
col = k["colombia_post_mundial"]

E.encabezado(
    "Pronóstico de demanda · Klixmant S.A.S.",
    f"Tras el Mundial, el modelo pronosticó <b>{E.num(col['HGB_redondeo'])} uds</b> de Colombia "
    f"(se vendieron {E.num(col['real'])}); una media móvil habría pedido <b>{E.num(col['media_movil_4'])}</b>.",
    "🧵",
)

E.kpis([
    ("Unidades vendidas", E.num(k["unidades_totales"]), None,
     f"Total del Excel {E.fecha(k['fecha_primera_venta'])} → {E.fecha(k['fecha_ultima_venta'], True)} (incluye canceladas; cifra de control)."),
    ("Catálogos con venta", E.num(k["catalogos_con_venta"]), None,
     f"Nombres crudos. Normalizados: {E.num(k['catalogos_normalizados'])}; en el panel del modelo: {E.num(k['catalogos_pareto'])}."),
    ("Meses de historia", E.num(k["meses_historia"]), None, f"{k['semanas_completas']} semanas completas."),
    (f"Venta en el top {k['top_n']}", E.pct(k["pct_unidades_top"]), None,
     f"{k['top_n']} catálogos de {E.num(k['catalogos_pareto'])} explican esta parte de las unidades."),
    ("Unidades de evento (Colombia)", "+" + E.num(k["uds_evento_colombia"]), None,
     f"Venta extra por el Mundial en la familia Colombia = {E.pct(k['pct_evento_colombia'])} de su venta en la ventana del evento."),
])

st.write("")
izq, der = st.columns([3, 2], gap="large")

with izq:
    st.subheader("El titular: quién «arrastra» el Mundial")
    orden = ["real", "HGB_redondeo", "ingenuo", "ETS", "SARIMAX", "media_movil_4"]
    etiquetas = ["Venta real"] + [E.nombre_modelo(m) for m in orden[1:]]
    colores = [E.COLOR_REAL] + [E.estilo_modelo(m)["color"] for m in orden[1:]]
    valores = [col[m] for m in orden]
    fig = go.Figure(go.Bar(
        x=valores, y=etiquetas, orientation="h", marker_color=colores,
        text=[E.num(v) for v in valores], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{x:,.0f} uds<extra></extra>",
    ))
    fig.update_yaxes(autorange="reversed")
    E.layout(fig, "Uds de Colombia pronosticadas después del Mundial (backtesting)", x="unidades", alto=360, leyenda=False)
    fig.update_xaxes(range=[0, max(valores) * 1.15])
    E.mostrar(fig, "inicio_p3")
    E.como_leer(T.COMO_LEER["titular_p3"])

with der:
    st.subheader("La venta semanal")
    s = tabla("serie_semanal_canal")
    completas = s[~s["parcial"]]
    fig = go.Figure(go.Scatter(
        x=completas["semana"], y=completas["TOTAL"], mode="lines", line=dict(color=E.COLOR_REAL, width=2.5),
        fill="tozeroy", fillcolor="rgba(0,114,178,0.10)", text=E.fechas(completas["semana"]),
        hovertemplate="Semana del %{text}: %{y:,.0f} uds<extra></extra>", name="Total",
    ))
    E.banda_mundial(fig)
    E.layout(fig, "Unidades por semana (total)", y="uds / semana", alto=360, leyenda=False)
    E.eje_meses(fig, completas["semana"].min(), completas["semana"].max())
    E.mostrar(fig, "inicio_serie")
    E.como_leer(T.COMO_LEER["serie_inicio"])

st.divider()
st.subheader("El recorrido (CRISP-DM)")
st.caption("Cada paso es una página. Haga clic para entrar.")
filas = [T.PASOS_CRISP[:4], T.PASOS_CRISP[4:]]
for fila in filas:
    cols = st.columns(4)
    for c, (paso, titulo, desc, ruta, icono) in zip(cols, fila):
        with c.container(border=True):
            st.markdown(f'<div class="paso">{paso}</div>', unsafe_allow_html=True)
            st.page_link(ruta, label=f"**{titulo}**", icon=icono)
            st.caption(desc)

st.divider()
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("#### 🎯 Qué pidió Klixmant")
    st.markdown("1. Pronóstico **por catálogo**.\n2. Separar demanda **base** y de **evento**.\n3. Llegar a **talla × color** (y a tela).")
with c2:
    st.markdown("#### ✅ Qué se entrega")
    st.markdown(
        f"- Pronóstico de **{k['top_n']}** catálogos con modelo y el resto con regla.\n"
        f"- Próximas {constantes()['horizonte_principal']} semanas: **{E.num(k['pronostico_4s_top'])}** uds en el top y **{E.num(k['pronostico_4s_cola'])}** en la cola.\n"
        "- Desagregación a talla × color y a tela, con descarga en CSV."
    )
with c3:
    st.markdown("#### ⚠️ Lo honesto")
    bt = k["wape_top_backtesting"]
    st.markdown(
        f"- Por catálogo, el modelo **no le gana con claridad al ingenuo** (WAPE {E.dec(bt['HGB_redondeo'])} vs {E.dec(bt['ingenuo'])}).\n"
        "- Su valor: **no arrastra el Mundial** y acierta mejor el **total semanal** "
        f"({E.dec(k['holdout_wape_total_semanal']['HGB_redondeo'])} vs {E.dec(k['holdout_wape_total_semanal']['ingenuo'])})."
    )
E.nota_borrador()
