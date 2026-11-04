"""6 · Plan de producción — herramienta: qué cortar y qué tela comprar en las próximas 4–8 semanas.

El ajuste experto se aplica SOLO en pantalla (memoria de la sesión); no cambia el bundle.
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import estilo as E
from utils import textos as T
from utils.datos import constantes, historia_y_pronostico, kpi, tabla

k = kpi()
c = constantes()
hist, pron = historia_y_pronostico()
tc = tabla("pronostico_talla_color")
tela = tabla("pronostico_tela")
rev = tabla("revision_vs_ingenuo")
TOP = c["top"]
H_PRINCIPAL, H_EXT = c["horizonte_principal"], c["horizonte_extendido"]
TOTAL_TOP = f"Σ Total del top {len(TOP)}"
semanas = sorted(pron["semana"].unique())
sem_txt = {s: f"S{h} · {E.fecha(s)}" for h, s in enumerate(semanas, start=1)}

E.encabezado(
    "Plan de producción",
    f"Próximas {H_PRINCIPAL} semanas: el top necesita <b>{E.num(k['pronostico_4s_top'])} uds</b> "
    f"(el ingenuo diría {E.num(k['pronostico_4s_top_ingenuo'])}) y la cola <b>{E.num(k['pronostico_4s_cola'])}</b>."
)

# ---------------- controles ----------------
with st.container(border=True):
    f1, f2, f3 = st.columns([3, 2, 2])
    opciones = [TOTAL_TOP] + TOP
    cat = f1.selectbox("Catálogo", opciones, key="p6_cat",
                       help="Los 20 del top tienen modelo e intervalo. El total del top no tiene intervalo (no se suma entre catálogos).")
    horizonte = f2.segmented_control("Horizonte", [H_PRINCIPAL, H_EXT], default=H_PRINCIPAL, key="p6_h",
                                     format_func=lambda h: f"{h} semanas" + (" (orientativo)" if h == H_EXT else "")) or H_PRINCIPAL
    n_hist = f3.slider("Semanas de historia en la gráfica", 8, 38, 12, key="p6_hist")

    with st.expander("Ajuste experto (solo en pantalla) — p. ej. Black Friday o una promoción", expanded=False):
        st.caption("Sube o baja el pronóstico en las semanas que elija. No modifica los datos oficiales: solo lo que ve y descarga aquí.")
        a1, a2, a3 = st.columns([3, 2, 2])
        sem_aj = a1.multiselect("Semanas a ajustar", semanas, format_func=lambda s: sem_txt[s], key="p6_sem_aj")
        pct_aj = a2.slider("Ajuste (%)", -50, 150, 0, 5, key="p6_pct", format="%d %%")
        alcance = a3.radio("Aplicar a", ["Todos los catálogos", "Solo el catálogo elegido"], key="p6_alc",
                           disabled=cat == TOTAL_TOP)
        if cat == TOTAL_TOP:
            alcance = "Todos los catálogos"

factor_sem = {s: 1.0 for s in semanas}
for s in sem_aj:
    factor_sem[s] = 1 + pct_aj / 100
ajuste_activo = bool(sem_aj) and pct_aj != 0
ajuste_global = alcance == "Todos los catálogos"


def factor(df: pd.DataFrame) -> np.ndarray:
    f = df["semana"].map(factor_sem).to_numpy(dtype=float)
    if not ajuste_global:
        f = np.where(df["catalogo"].to_numpy() == cat, f, 1.0)
    return f


p = pron[pron["h"] <= horizonte].copy()
p["pred_aj"] = p["pred"] * factor(p)
p["lo_aj"] = p["lo"] * factor(p)
p["hi_aj"] = p["hi"] * factor(p)
ptop = p[p["segmento"] == "top"]
pcola = p[p["segmento"] == "cola"]

tc_h = tc[tc["h"] <= horizonte].copy()
tc_h["pred_aj"] = tc_h["pred_tc"] * factor(tc_h)
tela_h = tela[tela["semana"].isin(semanas[:horizonte])].copy()
tela_h["pred_aj"] = tela_h["pred_tela"] * (tela_h["semana"].map(factor_sem) if ajuste_global else 1.0)

revisar = rev[rev["revisar"]]["catalogo"].tolist()

# ---------------- KPI ----------------
sel = ptop if cat == TOTAL_TOP else ptop[ptop["catalogo"] == cat]
real_ult = hist[hist["catalogo"].isin(TOP if cat == TOTAL_TOP else [cat])].groupby("semana")["y"].sum().sort_index()
real_ult_h = real_ult.tail(horizonte).sum()
E.kpis([
    (f"{'Top' if cat == TOTAL_TOP else 'Catálogo'} · próximas {horizonte} sem.", f"{E.num(sel['pred_aj'].sum())} uds",
     ((("+" if sel['pred_aj'].sum() >= sel['pred'].sum() else "") + f"{E.num(sel['pred_aj'].sum() - sel['pred'].sum())} uds por ajuste") if ajuste_activo else None),
     "Pronóstico publicado (con ajuste experto si lo activó)."),
    ("Ingenuo (repite la última semana)", f"{E.num(sel['pred_ingenuo'].sum())} uds",
     E.pct(sel["pred"].sum() / sel["pred_ingenuo"].sum() - 1, signo=True) + " el modelo" if sel["pred_ingenuo"].sum() else None,
     None, "off"),
    (f"Real de las últimas {horizonte} sem.", f"{E.num(real_ult_h)} uds", None, "Para comparar el ritmo reciente."),
    (f"Cola · próximas {horizonte} sem.", f"{E.num(pcola['pred_aj'].sum())} uds", None,
     f"{E.num(pcola['catalogo'].nunique())} catálogos con regla ingenua."),
    ("Catálogos para revisar a mano", f"{len(revisar)}", "ninguno" if not revisar else None,
     f"Modelo e ingenuo difieren más de {E.pct(c['umbral_revision'])} y al menos {c['umbral_revision_uds']} uds en {H_PRINCIPAL} semanas."),
])

# ---------------- 1. historia + pronóstico ----------------
st.subheader("1 · Historia y pronóstico")
h = real_ult.tail(n_hist)
if cat == TOTAL_TOP:
    fut = ptop.groupby("semana")[["pred", "pred_aj", "pred_ingenuo"]].sum().reset_index()
else:
    fut = sel.sort_values("semana")
fig = go.Figure()
fig.add_trace(go.Scatter(x=h.index, y=h.values, name="Venta real", mode="lines+markers", line=dict(color=E.COLOR_REAL, width=2.5),
                         marker=dict(size=5), text=E.fechas(h.index), hovertemplate="Real · %{text}: %{y:,.0f} uds<extra></extra>"))
puente_x = [h.index[-1]] + list(fut["semana"])
if cat != TOTAL_TOP and fut["lo"].notna().any():
    fig.add_trace(go.Scatter(x=fut["semana"], y=fut["hi_aj"], mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=fut["semana"], y=fut["lo_aj"], mode="lines", line=dict(width=0), fill="tonexty",
                             fillcolor=E.rgba(E.VINO, 0.16), name="Intervalo 10–90 %",
                             customdata=fut["hi_aj"], text=E.fechas(fut["semana"]),
                             hovertemplate="Intervalo · %{text}: %{y:,.0f}–%{customdata:,.0f} uds<extra></extra>"))
fig.add_trace(go.Scatter(x=puente_x, y=[h.values[-1]] + list(fut["pred_ingenuo"]), name="Ingenuo", mode="lines",
                         line=dict(color=E.COLOR_INGENUO, dash="dot", width=2), text=[""] + E.fechas(fut["semana"]),
                         hovertemplate="Ingenuo · %{text}: %{y:,.0f} uds<extra></extra>"))
fig.add_trace(go.Scatter(x=puente_x, y=[h.values[-1]] + list(fut["pred"]), name="Pronóstico publicado", mode="lines+markers",
                         line=dict(color=E.COLOR_PRONOSTICO, width=3), marker=dict(size=7), text=[""] + E.fechas(fut["semana"]),
                         hovertemplate="Pronóstico · %{text}: %{y:,.1f} uds<extra></extra>"))
if ajuste_activo:
    fig.add_trace(go.Scatter(x=puente_x, y=[h.values[-1]] + list(fut["pred_aj"]), name="Con ajuste experto", mode="lines+markers",
                             line=dict(color=E.OKABE_ITO[2], width=3, dash="dash"), marker=dict(size=7, symbol="diamond"),
                             text=[""] + E.fechas(fut["semana"]), hovertemplate="Ajustado · %{text}: %{y:,.1f} uds<extra></extra>"))
if horizonte > H_PRINCIPAL:
    fig.add_vrect(x0=semanas[H_PRINCIPAL] - pd.Timedelta(days=3.5), x1=semanas[horizonte - 1] + pd.Timedelta(days=3.5),
                  fillcolor=E.GRIS, opacity=0.12, line_width=0, layer="below")
    fig.add_annotation(x=semanas[H_PRINCIPAL], y=1, yref="paper", text="semanas 5–8: orientativas", showarrow=False,
                       xanchor="left", yanchor="top", font=dict(size=11, color="#666"))
fig.add_vline(x=h.index[-1] + pd.Timedelta(days=3.5), line_dash="dash", line_color="#999")
fig.add_annotation(x=h.index[-1] + pd.Timedelta(days=3.5), y=0.98, yref="paper", text="hoy (corte) ", showarrow=False,
                   xanchor="right", yanchor="top", font=dict(size=11, color="#666"))
if h.index.min() <= pd.Timestamp(c["mundial"][1]):
    E.banda_mundial(fig)
nombre = "Total del top" if cat == TOTAL_TOP else cat.title()
E.layout(fig, f"{nombre}: {E.num(fut['pred_aj'].sum())} uds en las próximas {horizonte} semanas", y="uds / semana", alto=460)
E.eje_meses(fig, h.index.min(), semanas[horizonte - 1])
fig.update_xaxes(range=[h.index.min() - pd.Timedelta(days=4), semanas[horizonte - 1] + pd.Timedelta(days=4)])
E.mostrar(fig, "p6_serie")
if cat in revisar:
    st.warning(f"**{cat}** está marcado para revisión manual: el modelo y el ingenuo difieren mucho. Revise antes de cortar.")
E.como_leer(T.COMO_LEER["plan_serie"])

# ---------------- 2. heatmap catálogo × semana ----------------
st.subheader("2 · Mapa del top: catálogo × semana")
piv = ptop.pivot_table(index="catalogo", columns="semana", values="pred_aj", aggfunc="sum")
piv = piv.loc[piv.sum(axis=1).sort_values(ascending=False).index]
filas = [("[revisar] " if c_ in revisar else "") + c_.title() for c_ in piv.index]
fig = go.Figure(go.Heatmap(z=piv.values, x=[sem_txt[s] for s in piv.columns], y=filas, colorscale=E.ESCALA_VINO,
                           text=[[E.num(v) for v in fila] for fila in piv.values], texttemplate="%{text}", textfont=dict(size=10),
                           colorbar=dict(title="uds"), hovertemplate="%{y} · %{x}: %{z:,.1f} uds<extra></extra>"))
fig.update_yaxes(autorange="reversed")
E.layout(fig, None, alto=max(420, 24 * len(filas) + 80), leyenda=False)
fig.update_layout(margin=dict(t=10))
E.mostrar(fig, "p6_heat")
E.como_leer(T.COMO_LEER["plan_heatmap"])

# ---------------- 3. talla × color ----------------
izq, der = st.columns(2, gap="large")
with izq:
    st.subheader("3 · Talla × color (orden de corte)")
    d = tc_h if cat == TOTAL_TOP else tc_h[tc_h["catalogo"] == cat]
    if cat == TOTAL_TOP:
        st.caption(f"Suma de los {len(TOP)} catálogos del top. Elija un catálogo arriba para ver su corte.")
    orden = ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4", "6", "8", "10", "12", "14", "16"]
    pv = d.pivot_table(index="talla_std", columns="color", values="pred_aj", aggfunc="sum", fill_value=0)
    if pv.empty:
        st.info("Este catálogo no tiene desagregación talla × color.")
    else:
        pv = pv.reindex([t for t in orden if t in pv.index] + sorted(set(pv.index) - set(orden)))
        pv = pv[pv.sum().sort_values(ascending=False).index]
        fig = go.Figure(go.Heatmap(z=pv.values, x=list(pv.columns), y=list(pv.index), colorscale=E.ESCALA_VINO,
                                   text=[[E.num(v, 1) if v < 10 else E.num(v) for v in fila] for fila in pv.values],
                                   texttemplate="%{text}", textfont=dict(size=11), colorbar=dict(title="uds"),
                                   hovertemplate="Talla %{y} · %{x}: %{z:,.1f} uds<extra></extra>"))
        fig.update_yaxes(autorange="reversed", title_text="talla", type="category")
        E.layout(fig, f"{E.num(pv.values.sum())} uds en {horizonte} semanas", alto=440, leyenda=False)
        E.mostrar(fig, "p6_tc")
        E.como_leer(T.COMO_LEER["plan_talla_color"])

# ---------------- 4. tela ----------------
with der:
    st.subheader("4 · Tela (compra de insumo)")
    if ajuste_activo and not ajuste_global:
        st.caption("El ajuste de un solo catálogo no se propaga a tela (la tabla de tela ya viene sumada sobre catálogos).")
    g = tela_h.groupby(["genero", "tela", "color_ref"], as_index=False)["pred_aj"].sum()
    g = g[g["pred_aj"] > 0.05]
    g["insumo"] = g["genero"].map({"H": "Hombre", "D": "Dama"}).fillna(g["genero"]) + " · " + g["tela"]
    orden_ins = g.groupby("insumo")["pred_aj"].sum().sort_values().index.tolist()
    colores = g.groupby("color_ref")["pred_aj"].sum().sort_values(ascending=False).index.tolist()
    paleta_color = {"NEGRO": "#222222", "BLANCO": "#E0E0E0", "MARFIL": "#EADFC8", "ROJO": "#C62828", "AZULNAVY": "#1A237E",
                    "AZULREY": "#1565C0", "AMARILLO": "#F9D71C", "AMARILLOCB": "#F5C400", "GRISJASPE": "#9E9E9E",
                    "VERDEOSCURO": "#1B5E20", "NARANJA": "#EF6C00", "COCOA": "#6D4C41", "ROSADOCLARO": "#F8BBD0",
                    "LILA": "#B39DDB", "CELESTE": "#81D4FA", "FUCSIA": "#D81B60", "VINOTINTO": "#7B1F2B",
                    "AZULPETROLEO": "#00596B", "VERDECALI": "#2E7D32", "MULTICOLOR": "#CC79A7", "COLOR": "#56B4E9"}
    fig = go.Figure()
    for col in colores:
        x = g[g["color_ref"] == col]
        fig.add_trace(go.Bar(y=x["insumo"], x=x["pred_aj"], name=col.capitalize(), orientation="h",
                             marker_color=paleta_color.get(col, E.GRIS), marker_line=dict(color="#888", width=0.4),
                             hovertemplate="%{y} · " + col.lower() + ": %{x:,.1f} uds<extra></extra>"))
    fig.update_layout(barmode="stack")
    fig.update_yaxes(categoryorder="array", categoryarray=orden_ins)
    E.layout(fig, f"{E.num(g['pred_aj'].sum())} uds por tela en {horizonte} semanas (top + cola)", x="unidades",
             alto=max(440, 28 * len(orden_ins) + 120))
    fig.update_layout(legend=dict(orientation="v", x=1.01, y=1, yanchor="top", xanchor="left", font=dict(size=11)),
                      margin=dict(t=55))
    E.mostrar(fig, "p6_tela")
    E.como_leer(T.COMO_LEER["plan_tela"])

# ---------------- 5. revisión ----------------
st.subheader("5 · Banderas de revisión: modelo vs ingenuo")
if not revisar:
    st.success(f"Ningún catálogo del top requiere revisión manual en este corte (umbral: diferencia > {E.pct(c['umbral_revision'])} "
               f"y ≥ {c['umbral_revision_uds']} uds en {H_PRINCIPAL} semanas).")
rv = rev.sort_values("pred_modelo", ascending=False)
E.tabla_st(pd.DataFrame({
    "Revisar": ["Sí" if r else "No" for r in rv["revisar"]],
    "Catálogo": rv["catalogo"],
    f"Modelo ({H_PRINCIPAL} sem.)": rv["pred_modelo"].round(0),
    f"Ingenuo ({H_PRINCIPAL} sem.)": rv["pred_ingenuo"].round(0),
    "Diferencia (uds)": rv["dif_uds"].round(0),
    "Diferencia (%)": rv["dif_rel"].map(lambda v: E.pct(v, signo=True)),
}), column_config={f"Modelo ({H_PRINCIPAL} sem.)": st.column_config.NumberColumn(format="%d"),
                   f"Ingenuo ({H_PRINCIPAL} sem.)": st.column_config.NumberColumn(format="%d"),
                   "Diferencia (uds)": st.column_config.NumberColumn(format="%+d")}, height=300)

# ---------------- 6. cola y descargas ----------------
with st.expander(f"Buscar en la cola ({E.num(pcola['catalogo'].nunique())} catálogos con regla ingenua)"):
    q = st.text_input("Buscar catálogo", key="p6_q", placeholder="p. ej. AUDI")
    cola = pcola.groupby("catalogo", as_index=False)["pred_aj"].sum().sort_values("pred_aj", ascending=False)
    if q:
        cola = cola[cola["catalogo"].str.contains(q, case=False, na=False)]
    E.tabla_st(cola.rename(columns={"catalogo": "Catálogo", "pred_aj": f"Uds en {horizonte} semanas"}).head(300),
               column_config={f"Uds en {horizonte} semanas": st.column_config.NumberColumn(format="%d")}, height=300)

st.subheader("6 · Descargas (CSV)")
st.caption("Separador «;» y coma decimal, para abrir directo en Excel en español. Incluyen el ajuste experto si está activo.")


def csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, sep=";", decimal=",", float_format="%.2f", date_format="%Y-%m-%d").encode("utf-8-sig")


sufijo = f"corte_{pd.Timestamp(pron['corte'].iloc[0]):%Y-%m-%d}_{horizonte}s" + ("_ajustado" if ajuste_activo else "")
d1, d2, d3 = st.columns(3)
d1.download_button("Descargar: Catálogo × semana (todos)", csv(p[["corte", "catalogo", "segmento", "semana", "h", "pred", "pred_aj", "pred_ingenuo",
                                                          "lo_aj", "hi_aj", "revisar"]].rename(columns={"pred_aj": "pred_ajustado",
                                                          "lo_aj": "lo", "hi_aj": "hi"})),
                   f"pronostico_catalogo_{sufijo}.csv", "text/csv", width="stretch", key="dl1")
d2.download_button("Descargar: Talla × color (top)", csv(tc_h.rename(columns={"pred_aj": "pred_tc_ajustado"})),
                   f"pronostico_talla_color_{sufijo}.csv", "text/csv", width="stretch", key="dl2")
d3.download_button("Descargar: Tela (insumo)", csv(tela_h.rename(columns={"pred_aj": "pred_tela_ajustado"})),
                   f"pronostico_tela_{sufijo}.csv", "text/csv", width="stretch", key="dl3")

