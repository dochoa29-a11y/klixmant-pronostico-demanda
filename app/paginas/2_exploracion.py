"""2 · Exploración — demanda concentrada, errática y dominada por el Mundial."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from utils import estilo as E
from utils import textos as T
from utils.datos import cifras, kpi, tabla

k = kpi()
h3 = cifras()["h3"]
serie = tabla("serie_semanal_canal")
pareto = tabla("pareto_catalogos")
clasif = tabla("clasificacion_catalogos")

# Umbrales de Syntetos, Boylan y Croston (2005): constantes del método, no resultados.
ADI_CORTE, CV2_CORTE = 1.32, 0.49

n_80 = int((pareto["pct_acum"] < 0.80).sum()) + 1
dropi = h3["% Dropi antes / durante / después"]
n_insuf = int((clasif["tipo"] == "insuficiente").sum())

E.encabezado(
    "Exploración",
    f"La demanda está <b>concentrada</b> ({k['top_n']} catálogos = {E.pct(k['pct_unidades_top'])} de las unidades), "
    f"es <b>errática</b> y el <b>Mundial</b> la domina.",
    "🔎",
)

E.kpis([
    (f"Unidades en el top {k['top_n']}", E.pct(k["pct_unidades_top"]), None, f"De {E.num(len(pareto))} catálogos del panel."),
    ("Catálogos para llegar al 80 %", E.num(n_80), None, "Clase A del análisis ABC."),
    ("Catálogos con muy poca historia", E.pct(n_insuf / len(clasif)), None,
     f"{E.num(n_insuf)} de {E.num(len(clasif))}: tipo «insuficiente» (menos de las semanas mínimas para clasificar)."),
    ("Dropi antes → durante el Mundial", f"{E.pct(dropi['1_antes'])} → {E.pct(dropi['2_durante'])}",
     E.pct(dropi["2_durante"] - dropi["1_antes"], signo=True).replace(" %", " pp"), "Participación de Dropi en las unidades."),
    ("Colombia: semana durante / antes", f"× {E.num(h3['familia Colombia: semana prom. durante / antes'], 1)}", None,
     "Venta semanal promedio de la familia Colombia durante el Mundial frente a antes."),
])

st.write("")
tabs = st.tabs(["📅 Serie semanal", "🏔️ Concentración", "🎲 Patrón ADI/CV²", "🗓️ Día × semana", "🔀 Canales", "⏳ Ciclo de vida", "👕 Tallas"])

# --- Serie semanal por canal ---
with tabs[0]:
    fig = go.Figure()
    for canal in ["EFFI", "DROPI"]:
        fig.add_trace(go.Scatter(
            x=serie["semana"], y=serie[canal], name=canal.capitalize(), stackgroup="canal", mode="lines",
            line=dict(width=0.5, color=E.COLOR_CANAL[canal]), text=E.fechas(serie["semana"]),
            hovertemplate=canal.capitalize() + " · semana del %{text}: %{y:,.0f} uds<extra></extra>",
        ))
    fig.add_trace(go.Scatter(x=serie["semana"], y=serie["TOTAL"], name="Total", mode="lines",
                             line=dict(color=E.COLOR_CANAL["TOTAL"], width=2), text=E.fechas(serie["semana"]),
                             hovertemplate="Total · semana del %{text}: %{y:,.0f} uds<extra></extra>"))
    p = serie[serie["parcial"]]
    if len(p):
        fig.add_trace(go.Scatter(x=p["semana"], y=p["TOTAL"], mode="markers+text", name="Semana parcial",
                                 marker=dict(symbol="x", size=11, color="#D55E00"), text=["parcial"], textposition="top center",
                                 hovertemplate="Semana parcial: %{y:,.0f} uds<extra></extra>"))
    E.banda_mundial(fig)
    pico = serie.loc[serie["TOTAL"].idxmax()]
    E.layout(fig, f"El Mundial multiplicó la venta: pico de {E.num(pico['TOTAL'])} uds la semana del {E.fecha(pico['semana'])}",
             y="uds / semana", alto=450)
    E.eje_meses(fig, serie["semana"].min(), serie["semana"].max())
    E.mostrar(fig, "p2_serie")
    E.como_leer(T.COMO_LEER["serie_canal"])

# --- Pareto ---
with tabs[1]:
    n = st.slider("Catálogos a mostrar", 10, 120, 40, 5, key="p2_n")
    d = pareto.head(n)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=d["rank"], y=d["unidades"], marker_color=[E.COLOR_FAMILIA.get(f, E.GRIS) for f in d["familia"]],
                         customdata=np.stack([d["catalogo"], d["familia"]], axis=1), name="Unidades",
                         hovertemplate="#%{x} %{customdata[0]}<br>%{y:,.0f} uds · %{customdata[1]}<extra></extra>"),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=pareto["rank"], y=pareto["pct_acum"], mode="lines", name="% acumulado",
                             line=dict(color=E.COLOR_REAL, width=2),
                             hovertemplate="Top %{x}: %{y:.0%} de las unidades<extra></extra>"), secondary_y=True)
    fig.add_hline(y=0.8, line_dash="dot", line_color=E.GRIS, secondary_y=True)
    fig.add_vline(x=k["top_n"] + 0.5, line_dash="dash", line_color=E.COLOR_PRONOSTICO)
    fig.add_annotation(x=k["top_n"] + 0.5, y=1, yref="paper", text=f" top {k['top_n']} = {E.pct(k['pct_unidades_top'])}",
                       showarrow=False, xanchor="left", font=dict(color=E.COLOR_PRONOSTICO))
    E.layout(fig, f"Pocos catálogos hacen casi toda la venta: {n_80} llegan al 80 %", alto=450)
    fig.update_xaxes(title_text="puesto del catálogo", range=[0.5, n + 0.5])
    fig.update_yaxes(title_text="unidades", secondary_y=False)
    fig.update_yaxes(title_text="% acumulado", tickformat=".0%", range=[0, 1.02], secondary_y=True, showgrid=False)
    E.mostrar(fig, "p2_pareto")
    st.caption("🟥 familia Colombia · 🟦 resto")
    E.como_leer(T.COMO_LEER["pareto"])

# --- ADI / CV² ---
with tabs[2]:
    c = clasif[clasif["tipo"] != "insuficiente"].dropna(subset=["ADI", "CV2"]).copy()
    colores_tipo = {"suave": E.OKABE_ITO[2], "intermitente": E.OKABE_ITO[0], "errática": E.OKABE_ITO[1], "irregular": E.OKABE_ITO[3]}
    solo_top = st.toggle(f"Resaltar solo el top {k['top_n']}", value=False, key="p2_top")
    fig = go.Figure()
    for tipo, color in colores_tipo.items():
        d = c[c["tipo"] == tipo]
        if solo_top:
            d = d[d["rank"] <= k["top_n"]]
        fig.add_trace(go.Scatter(
            x=d["ADI"], y=d["CV2"], mode="markers", name=f"{tipo} ({len(d)})",
            marker=dict(color=color, size=np.clip(np.sqrt(d["unidades"]) * 0.9, 5, 45), opacity=0.75, line=dict(width=0.5, color="white")),
            customdata=np.stack([d["catalogo"], d["unidades"], d["metodo_sugerido"]], axis=1),
            hovertemplate="<b>%{customdata[0]}</b><br>ADI %{x:.2f} · CV² %{y:.2f}<br>%{customdata[1]:,.0f} uds<br>Método: %{customdata[2]}<extra></extra>",
        ))
    fig.add_vline(x=ADI_CORTE, line_dash="dot", line_color=E.GRIS)
    fig.add_hline(y=CV2_CORTE, line_dash="dot", line_color=E.GRIS)
    for x, y, t in [(1.02, 0.03, "suave"), (4, 0.03, "intermitente"), (1.02, 5, "errática"), (4, 5, "irregular")]:
        fig.add_annotation(x=np.log10(x), y=np.log10(y), text=t.upper(), showarrow=False, font=dict(size=11, color="#888"), xanchor="left")
    E.layout(fig, "Casi ningún catálogo es «suave»: la mayoría vende a saltos", alto=500)
    fig.update_xaxes(type="log", title_text="ADI (semanas entre ventas, escala log)")
    fig.update_yaxes(type="log", title_text="CV² (variación del tamaño, escala log)")
    E.mostrar(fig, "p2_adi")
    st.caption(f"No se muestran los {E.num(n_insuf)} catálogos con historia insuficiente. Tamaño del punto = unidades.")
    E.como_leer(T.COMO_LEER["adi"])

# --- Heatmap día × semana ---
with tabs[3]:
    dd = tabla("demanda_diaria_canal").groupby("fecha", as_index=False)["cantidad_total"].sum()
    dd["fecha"] = pd.to_datetime(dd["fecha"])
    dd["semana"] = dd["fecha"] - pd.to_timedelta(dd["fecha"].dt.dayofweek, unit="D")
    dd["dia"] = dd["fecha"].dt.dayofweek
    piv = dd.pivot_table(index="dia", columns="semana", values="cantidad_total", aggfunc="sum").reindex(range(7))
    texto = [[f"{E.fecha(s + pd.Timedelta(days=int(d)))}: {E.num(v) if pd.notna(v) else 'sin venta'}" for s, v in zip(piv.columns, piv.loc[d])] for d in piv.index]
    fig = go.Figure(go.Heatmap(z=piv.values, x=piv.columns, y=E.DIAS, colorscale="Blues", text=texto,
                               hovertemplate="%{text} uds<extra></extra>", colorbar=dict(title="uds")))
    fig.update_yaxes(autorange="reversed")
    E.banda_mundial(fig, ventana=False, texto=True)
    E.layout(fig, "Durante el Mundial todos los días se encendieron", alto=380, leyenda=False)
    E.eje_meses(fig, piv.columns.min(), piv.columns.max())
    E.mostrar(fig, "p2_heat")
    E.como_leer(T.COMO_LEER["heatmap_dia"])

# --- Canales ---
with tabs[4]:
    s = serie[~serie["parcial"]].assign(pct=lambda d: d["DROPI"] / d["TOTAL"])
    fig = go.Figure(go.Scatter(x=s["semana"], y=s["pct"], mode="lines+markers", line=dict(color=E.COLOR_CANAL["DROPI"], width=2.5),
                               text=E.fechas(s["semana"]), hovertemplate="Semana del %{text}: %{y:.0%} Dropi<extra></extra>", name="% Dropi"))
    E.banda_mundial(fig)
    E.layout(fig, f"Dropi pasó de {E.pct(dropi['1_antes'])} antes a {E.pct(dropi['2_durante'])} durante el Mundial "
                  f"y bajó a {E.pct(dropi['3_despues'])} después", y="% de las unidades por Dropi", alto=400, leyenda=False)
    fig.update_yaxes(tickformat=".0%")
    E.eje_meses(fig, s["semana"].min(), s["semana"].max())
    E.mostrar(fig, "p2_dropi")
    E.como_leer(T.COMO_LEER["dropi"])

# --- Ciclo de vida ---
with tabs[5]:
    izq, der = st.columns([3, 2], gap="large")
    with izq:
        fig = go.Figure()
        for fam in ["RESTO", "COLOMBIA"]:
            d = clasif[clasif["familia"] == fam]
            fig.add_trace(go.Histogram(x=d["semanas_vida"], name=fam.capitalize(), marker_color=E.COLOR_FAMILIA[fam],
                                       xbins=dict(size=2), opacity=0.85,
                                       hovertemplate="%{x} semanas: %{y} catálogos<extra></extra>"))
        fig.update_layout(barmode="stack")
        E.layout(fig, "La mayoría de catálogos vive pocas semanas", x="semanas entre la primera y la última venta", y="catálogos", alto=400)
        E.mostrar(fig, "p2_vida")
        E.como_leer(T.COMO_LEER["ciclo"])
    with der:
        est = clasif["estado"].value_counts()
        fig = go.Figure(go.Pie(labels=[e.capitalize() for e in est.index], values=est.values, hole=0.55,
                               marker_colors=[E.GRIS if e == "inactivo" else E.OKABE_ITO[2] for e in est.index],
                               hovertemplate="%{label}: %{value} catálogos (%{percent})<extra></extra>", textinfo="label+percent"))
        E.layout(fig, "Estado al corte (sin venta en 4 semanas = inactivo)", alto=400, leyenda=False)
        E.mostrar(fig, "p2_estado")

# --- Tallas ---
with tabs[6]:
    mz = tabla("mezcla_talla_top_mes")
    est = tabla("estabilidad_mezcla_top").sort_values("unidades", ascending=False)
    izq, der = st.columns([3, 2], gap="large")
    with izq:
        cat = st.selectbox("Catálogo del top", est["catalogo"], key="p2_cat")
        d = mz[mz["catalogo"] == cat].copy()
        d["mes"] = pd.to_datetime(d["mes"])
        d["pct"] = d["cantidad_total"] / d.groupby("mes")["cantidad_total"].transform("sum")
        orden = ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4", "6", "8", "10", "12", "14", "16"]
        tallas = [t for t in orden if t in set(d["talla_std"])] + sorted(set(d["talla_std"]) - set(orden))
        fig = go.Figure()
        for i, t in enumerate(tallas):
            x = d[d["talla_std"] == t]
            fig.add_trace(go.Bar(x=[E.MESES[m.month - 1] for m in x["mes"]], y=x["pct"], name=t,
                                 marker_color=E.OKABE_ITO[i % len(E.OKABE_ITO)] if i < 7 else None,
                                 customdata=x["cantidad_total"], hovertemplate=f"Talla {t}: " + "%{y:.0%} (%{customdata:,.0f} uds)<extra></extra>"))
        fig.update_layout(barmode="stack")
        E.layout(fig, "Mezcla de tallas por mes", y="% de las unidades del mes", alto=420)
        fig.update_yaxes(tickformat=".0%")
        fig.update_xaxes(categoryorder="array", categoryarray=E.MESES)
        E.mostrar(fig, "p2_tallas")
        E.como_leer(T.COMO_LEER["tallas"])
    with der:
        st.markdown("##### Estabilidad de la mezcla (0 = no cambia; 100 = cambia por completo)")
        est = est.assign(TV_talla=est["TV_talla"] * 100, TV_color=est["TV_color"] * 100)
        E.tabla_st(est[["catalogo", "TV_talla", "TV_color", "tallas", "colores"]].rename(columns={
            "catalogo": "Catálogo", "TV_talla": "Cambio en tallas", "TV_color": "Cambio en colores", "tallas": "Tallas", "colores": "Colores"}),
            column_config={"Cambio en tallas": st.column_config.ProgressColumn(format="%.0f", min_value=0, max_value=50),
                           "Cambio en colores": st.column_config.ProgressColumn(format="%.0f", min_value=0, max_value=50)},
            height=420)
        st.caption(f"Distancia de variación total media en el top: {E.num(h3['TV talla media en el top (0 = estable)'], 2)}. "
                   "Con una mezcla estable, repartir el pronóstico por proporciones es razonable.")

E.nota_borrador()
