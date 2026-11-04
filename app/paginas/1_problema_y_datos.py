"""1 · Problema y datos — qué decide Klixmant y con qué datos."""
import plotly.graph_objects as go
import streamlit as st

from utils import estilo as E
from utils import textos as T
from utils.datos import cifras, documento, kpi, tabla

k = kpi()
h4 = cifras()["h4"]
cuadre = tabla("cuadre_cifras_control")
reglas = tabla("reglas_limpieza")
val = dict(zip(cuadre["cifra"], cuadre["obtenido"]))
n_ok = int((cuadre["diferencia"] == 0).sum())

E.encabezado(
    "Problema y datos",
    "Hoy se compra tela y se programa el corte <b>mirando el agregado y sin modelo</b>: "
    "cuando el evento termina, <b>el inventario ya quedó comprado</b>.",
    "📋",
)

E.kpis([
    ("Líneas de pedido", E.num(val["lineas"])),
    ("Unidades", E.num(val["unidades"])),
    ("Remisiones", E.num(val["remisiones"])),
    ("Días con venta", E.num(val["dias_con_venta"])),
    ("Cifras de control que cuadran", f"{n_ok} / {len(cuadre)}", "✅ todas" if n_ok == len(cuadre) else None),
])

st.write("")
t1, t2, t3, t4 = st.tabs(["🎯 El problema y las decisiones", "✅ Cuadre de cifras", "🧹 Limpieza", "🪜 Jerarquía de la demanda"])

with t1:
    izq, der = st.columns([2, 3], gap="large")
    with izq:
        st.markdown("#### Lo que pide Klixmant")
        st.markdown(
            "1. Un pronóstico **por catálogo** (el diseño que compra el cliente).\n"
            "2. Que **separe la demanda base de la demanda por evento** (Mundial 2026).\n"
            "3. Que llegue a **talla × color**, que es como se corta la tela, y que sume a **tela** para comprar insumo."
        )
        st.markdown("#### Con qué datos")
        st.markdown(
            f"- Hoja de pedidos del Excel de Klixmant, del **{E.fecha(k['fecha_primera_venta'], True)}** al "
            f"**{E.fecha(k['fecha_ultima_venta'], True)}**.\n"
            f"- **{E.num(val['unidades_effi'])}** uds por Effi (venta directa) y **{E.num(val['unidades_dropi'])}** por Dropi (dropshipping).\n"
            f"- **{k['semanas_completas']}** semanas completas: la del corte es parcial y no entra al modelo."
        )
    with der:
        st.markdown(documento("decisiones_negocio.md").split("### 2.2 Decisiones a tomar", 1)[-1])

with t2:
    vista = cuadre.assign(
        cifra=cuadre["cifra"].str.replace("_", " ").str.capitalize(),
        esperado=cuadre["esperado"].map(E.num), obtenido=cuadre["obtenido"].map(E.num),
        diferencia=cuadre["diferencia"].map(E.num),
    ).rename(columns={"cifra": "Cifra de control", "esperado": "Esperado (Klixmant)", "obtenido": "Obtenido (notebook)",
                      "diferencia": "Diferencia", "cuadra": "¿Cuadra?"})
    E.tabla_st(vista)
    E.como_leer(T.COMO_LEER["cuadre"])

with t3:
    izq, der = st.columns([3, 2], gap="large")
    with izq:
        r = reglas.sort_values("unidades")
        fig = go.Figure(go.Bar(
            x=r["unidades"], y=r["regla"], orientation="h", marker_color=E.OKABE_ITO[0],
            text=[E.num(v) for v in r["unidades"]], textposition="outside", cliponaxis=False,
            customdata=r["decision"], hovertemplate="%{y}<br>%{x:,.0f} uds · %{customdata}<extra></extra>",
        ))
        E.layout(fig, "Unidades afectadas por cada regla de limpieza", x="unidades", alto=380, leyenda=False)
        fig.update_xaxes(range=[0, r["unidades"].max() * 1.18])
        E.mostrar(fig, "p1_reglas")
        E.como_leer(T.COMO_LEER["reglas"])
    with der:
        E.tabla_st(reglas.assign(lineas=reglas["lineas"].map(E.num), unidades=reglas["unidades"].map(E.num))
                   .rename(columns={"regla": "Regla", "lineas": "Líneas", "unidades": "Unidades", "decision": "Decisión"}))
    with st.expander("Reglas de limpieza del plan de investigación (§4.1)"):
        st.markdown(documento("reglas_limpieza_plan.md").split("\n", 1)[-1])

with t4:
    tc = tabla("pronostico_talla_color")
    maestro = tabla("maestro_catalogos")
    demanda = k["unidades_demanda_sin_canceladas"]
    dot = f"""
    digraph G {{
      rankdir=LR; bgcolor="transparent";
      node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=12, color="#BFD3E6", fillcolor="#F4F8FC"];
      edge [color="#7F8FA6"];
      total [label="Total\\n{E.num(demanda)} uds de demanda", fillcolor="#DCEAF7"];
      canal [label="Canal\\nEffi · Dropi"];
      tela  [label="Tela (referencia)\\n{h4['telas base (2.º token de referencia)']} telas base\\n→ compra de insumo"];
      cat   [label="Catálogo\\n{E.num(len(maestro))} normalizados\\n★ nivel que se modela", fillcolor="#FFE9B3", color="#E69F00", penwidth=2];
      tc    [label="Talla × color\\n{tc['talla_std'].nunique()} tallas · {tc['color'].nunique()} colores (top)\\n→ orden de corte"];
      total -> canal -> tela -> cat -> tc;
    }}"""
    st.graphviz_chart(dot, width="stretch")
    E.como_leer(T.COMO_LEER["jerarquia"])

E.nota_borrador()
