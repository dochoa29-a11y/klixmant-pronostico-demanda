"""4 · Segmentación — perfiles de demanda (K-means)."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from utils import estilo as E
from utils import textos as T
from utils.datos import cifras, curvas_cluster, tabla

h4 = cifras()["h4"]
perfil = tabla("perfil_clusters")
maestro = tabla("maestro_catalogos")
k_grupos, nombres = h4["k de K-means / grupos"]
curvas = curvas_cluster()
DESC = {
    "evento": "Se disparan con el Mundial y luego se apagan.",
    "base": "Venden parejo semana a semana.",
    "en declive": "Vendían antes y van perdiendo fuerza.",
    "base errática": "Venta de base, pero a saltos grandes.",
}

E.encabezado(
    "Segmentación",
    f"Los catálogos con historia se agrupan en <b>{k_grupos} perfiles</b>: " + ", ".join(f"<b>{n}</b>" for n in nombres) + "."
)
cnt = perfil["cluster"].value_counts()
E.kpis([(f"{n.capitalize()} · catálogos", E.num(cnt.get(n, 0)), None, DESC.get(n)) for n in nombres]
       + [("Cola sin perfil · catálogos", E.num((maestro['cluster'] == 'cola').sum()), None,
           "Catálogos con muy poca historia: no entran al K-means.")])

st.write("")
izq, der = st.columns([3, 2], gap="large")
with izq:
    fig = go.Figure()
    for n in nombres:
        d = curvas[curvas["cluster"] == n].sort_values("semana")
        if d.empty:
            continue
        fig.add_trace(go.Scatter(x=d["semana"], y=d["part"], mode="lines", name=f"{n} ({d['n_catalogos'].iloc[0]})",
                                 line=dict(color=E.COLOR_CLUSTER.get(n), width=2.8), text=E.fechas(d["semana"]),
                                 hovertemplate=n + " · %{text}: %{y:.1%} de la venta del catálogo<extra></extra>"))
    E.banda_mundial(fig)
    E.layout(fig, "Curva promedio de cada perfil: el grupo «evento» vive del Mundial", y="% de la venta total del catálogo", alto=450)
    fig.update_yaxes(tickformat=".0%")
    E.eje_meses(fig, curvas["semana"].min(), curvas["semana"].max())
    E.mostrar(fig, "p4_curvas")
    E.como_leer(T.COMO_LEER["curvas_cluster"])
with der:
    m = perfil.groupby("cluster")[["int_antes", "int_evento", "int_despues"]].mean().reindex(nombres)
    fig = go.Figure()
    for col, nom, color in [("int_antes", "Antes", E.OKABE_ITO[5]), ("int_evento", "Durante el evento", E.COLOR_EVENTO),
                            ("int_despues", "Después", E.OKABE_ITO[0])]:
        fig.add_trace(go.Bar(x=m.index, y=m[col], name=nom, marker_color=color, marker_line=dict(color="#555", width=0.5),
                             hovertemplate="%{x} · " + nom.lower() + ": %{y:.0%}<extra></extra>"))
    fig.update_layout(barmode="group")
    E.layout(fig, "¿Cuándo venden? (participación por periodo)", y="% de la venta del catálogo", alto=450)
    fig.update_yaxes(tickformat=".0%")
    E.mostrar(fig, "p4_intens")
    E.como_leer(T.COMO_LEER["intensidad_cluster"])

st.divider()
izq, der = st.columns([2, 3], gap="large")
with izq:
    fig = go.Figure()
    for n in nombres:
        d = perfil[perfil["cluster"] == n]
        fig.add_trace(go.Scatter(x=d["tendencia_8s"], y=d["int_evento"], mode="markers", name=n,
                                 marker=dict(color=E.COLOR_CLUSTER.get(n), size=np.clip(np.sqrt(d["unidades"]) * 1.1, 6, 40),
                                             opacity=0.8, line=dict(width=0.5, color="white")),
                                 customdata=np.stack([d["catalogo"], d["unidades"]], axis=1),
                                 hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]:,.0f} uds<br>En el evento: %{y:.0%}"
                                               "<br>Tendencia 8 sem.: %{x:.2f}<extra></extra>"))
    E.layout(fig, "Cada catálogo en su grupo", x="tendencia de las últimas 8 semanas", y="% de su venta en el evento", alto=430)
    fig.update_yaxes(tickformat=".0%")
    E.mostrar(fig, "p4_scatter")
    st.caption("Tamaño del punto = unidades.")
with der:
    g = st.segmented_control("Grupo", nombres, default=nombres[0], key="p4_g") or nombres[0]
    st.caption(DESC.get(g, ""))
    d = (perfil[perfil["cluster"] == g].merge(maestro[["catalogo", "linea", "familia", "rank"]], on="catalogo", how="left")
         .sort_values("unidades", ascending=False))
    d = d.assign(**{c_: d[c_] * 100 for c_ in ["int_antes", "int_evento", "int_despues", "pct_dropi"]},
                 unidades=d["unidades"].map(E.num))
    E.tabla_st(d[["catalogo", "unidades", "linea", "int_antes", "int_evento", "int_despues", "pct_dropi"]].rename(columns={
        "catalogo": "Catálogo", "unidades": "Unidades", "linea": "Línea", "int_antes": "Antes", "int_evento": "Evento",
        "int_despues": "Después", "pct_dropi": "% Dropi"}),
        column_config={
            "Antes": st.column_config.ProgressColumn(format="%.0f %%", min_value=0, max_value=100),
            "Evento": st.column_config.ProgressColumn(format="%.0f %%", min_value=0, max_value=100),
            "Después": st.column_config.ProgressColumn(format="%.0f %%", min_value=0, max_value=100),
            "% Dropi": st.column_config.NumberColumn(format="%.0f %%"),
        }, height=390)

imp = tabla("importancia_permutacion").sort_values("aumento_MAE", ascending=False).reset_index(drop=True)
puesto = int(imp.index[imp["variable"] == "cluster"][0]) + 1 if (imp["variable"] == "cluster").any() else None
st.info(f"El clúster entra como variable al modelo: es la **{puesto}.ª más importante** de {len(imp)} en la importancia por permutación "
        "(página 5). Saber «qué tipo de catálogo es» ayuda a pronosticarlo.")
