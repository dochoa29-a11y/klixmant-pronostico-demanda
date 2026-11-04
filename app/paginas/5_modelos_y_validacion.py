"""5 · Modelos y validación — el modelo no arrastra el Mundial; empata con el ingenuo."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import estilo as E
from utils import textos as T
from utils.datos import cifras, constantes, kpi, tabla

k = kpi()
cf = cifras()
c = constantes()
h6 = cf["h6"]
final = k["modelo_final"]
bt = tabla("metricas_backtesting")
bt_i = bt.set_index("modelo")
ho = tabla("metricas_holdout").set_index("modelo")
ORDEN_BT = ["ingenuo", "media_movil_4", "ETS", "SARIMAX", "HGB_poisson", "HGB_redondeo", "HGB+ingenuo"]

wf, wi = k["wape_top_backtesting"][final], k["wape_top_backtesting"]["ingenuo"]
col = k["colombia_post_mundial"]

E.encabezado(
    "Modelos y validación",
    f"El modelo <b>no arrastra el Mundial</b> (Colombia después del evento: {E.num(col[final])} uds vs {E.num(col['real'])} reales), "
    f"pero por catálogo <b>empata con el ingenuo</b> (WAPE {E.dec(wf)} vs {E.dec(wi)}).",
    "📈",
)
tot = k["holdout_wape_total_semanal"]
E.kpis([
    ("WAPE top · backtesting", E.dec(wf), f"{E.dec(wf - wi, signo=True)} vs ingenuo", f"{len(c['cortes_backtesting'])} orígenes, {c['horizonte_principal']} semanas. Menor es mejor.", "inverse"),
    ("WAPE top · después del Mundial", E.dec(k["wape_top_post_backtesting"][final]),
     f"{E.dec(k['wape_top_post_backtesting'][final] - k['wape_top_post_backtesting']['ingenuo'], signo=True)} vs ingenuo", None, "inverse"),
    ("Total semanal · holdout", E.dec(tot[final]), f"{E.dec(tot[final] - tot['ingenuo'], signo=True)} vs ingenuo",
     "WAPE del total de unidades por semana en el holdout: lo que importa para planear la planta.", "inverse"),
    ("Top h=1…4 · holdout", E.dec(k["holdout_wape_top_h4"][final]),
     f"{E.dec(k['holdout_wape_top_h4'][final] - k['holdout_wape_top_h4']['ingenuo'], signo=True)} vs ingenuo",
     "Aquí el ingenuo gana: un catálogo (Honda) explica casi todo el exceso.", "inverse"),
    ("Cobertura del intervalo", E.pct(k["cobertura_intervalo_holdout"]), None, "Meta: 80 %. Intervalo 10–90 % conformal."),
])

ce = cf["correccion_early_stopping"]
with st.expander("🔧 Corrección de `early_stopping` (por qué estas cifras difieren del reporte 04)"):
    st.markdown("El modelo de producción se entrenaba con una parada temprana que lo cortaba en "
                f"**{ce['antes']['n_iter_produccion']}** iteraciones; ahora usa **{ce['ahora']['n_iter_produccion']}**. "
                "Las cifras vigentes son las de la columna «ahora».")
    filas = [("WAPE top backtesting", "wape_top_backtesting", E.dec), ("Colombia después del Mundial (uds)", "colombia_post", E.num),
             ("Holdout WAPE top h=1…4", "holdout_wape_top_h4", E.dec), ("Holdout WAPE top h=1…6", "holdout_wape_top_h6", E.dec),
             ("Holdout sesgo top h=1…6", "holdout_sesgo_top_h6", lambda v: E.pct(v, signo=True)),
             ("Holdout WAPE total semanal", "holdout_wape_total_semanal", E.dec)]
    E.tabla_st(pd.DataFrame([{"Métrica": n, "Antes (no vigente)": f(ce["antes"][key]), "Ahora": f(ce["ahora"][key])} for n, key, f in filas]))

st.write("")
tabs = st.tabs(["🪜 Escalera", "🧪 Backtesting", "🗺️ Por origen", "📏 Por horizonte", "🔒 Holdout", "🏍️ Caso Honda",
                "↕️ Intervalos", "🧠 Variables", "🧩 Segmentos"],
               key="p5_tabs", on_change="rerun")

with tabs[0]:
    if tabs[0].open:  # pestaña perezosa: solo se dibuja la abierta
        s5 = tabla("metricas_validacion_s5").sort_values("WAPE_top")
        niveles = list(dict.fromkeys(s5.sort_values("nivel")["nivel"]))
        color_nivel = {n: E.OKABE_ITO[i % 8] for i, n in enumerate(niveles)}
        fig = go.Figure()
        for n in niveles:
            d = s5[s5["nivel"] == n]
            fig.add_trace(go.Bar(x=d["WAPE_top"], y=[E.nombre_modelo(m) for m in d["modelo"]], orientation="h", name=n,
                                 marker_color=color_nivel[n], customdata=np.stack([d["sesgo_top"], d["uds_Colombia_post_pron"]], axis=1),
                                 hovertemplate="<b>%{y}</b><br>WAPE %{x:.3f} · sesgo %{customdata[0]:+.0%}"
                                               "<br>Colombia post-Mundial: %{customdata[1]:,.0f} uds<extra></extra>"))
        ing = s5.set_index("modelo").loc["ingenuo", "WAPE_top"]
        fig.add_vline(x=ing, line_dash="dot", line_color=E.COLOR_INGENUO)
        fig.add_annotation(x=ing, y=1.02, yref="paper", text="ingenuo", showarrow=False, font=dict(color=E.COLOR_INGENUO))
        fig.update_yaxes(categoryorder="array", categoryarray=[E.nombre_modelo(m) for m in s5["modelo"]][::-1])
        E.layout(fig, "De simple a complejo: más complejidad no siempre es menos error", x="WAPE del top (validación §5)", alto=520)
        E.mostrar(fig, "p5_escalera")
        E.como_leer(T.COMO_LEER["escalera"])
        cols = st.columns(4)
        for cc, (tit, txt) in zip(cols, [
            ("0 · Línea base", "Ingenuo y media móvil: la vara mínima."),
            ("1 · Estadísticos", "ETS y SARIMAX: una serie a la vez."),
            ("2 · Boosting global", "Un modelo para todos los catálogos, con calendario y atributos."),
            ("3 · Deep learning", f"LSTM: con {k['meses_historia']} meses de datos no alcanza."),
        ]):
            cc.markdown(f'<div class="tarjeta"><h4>{tit}</h4><p>{txt}</p></div>', unsafe_allow_html=True)

with tabs[1]:
    if tabs[1].open:  # pestaña perezosa: solo se dibuja la abierta
        d = bt.set_index("modelo").reindex([m for m in ORDEN_BT if m in bt_i.index]).reset_index()
        vista = pd.DataFrame({
            "Modelo": [("⭐ " if m == final else "") + E.nombre_modelo(m) for m in d["modelo"]],
            "WAPE top": d["WAPE_top"].map(E.dec), "Sesgo": d["sesgo_top"].map(lambda v: E.pct(v, 1, True)),
            "MASE": d["MASE_top"].map(lambda v: E.dec(v, 2)),
            "WAPE antes": d["WAPE_top_antes"].map(E.dec), "WAPE toca evento": d["WAPE_top_evento"].map(E.dec),
            "WAPE después": d["WAPE_top_post"].map(E.dec),
            "Colombia post (uds)": d["uds_Colombia_post_pron"].map(E.num),
            "Orígenes que gana al ingenuo": d["origenes_gana_al_ingenuo"].map(lambda v: f"{v}/{len(c['cortes_backtesting'])}"),
            "P(gana al ingenuo)": d["prob_gana_bootstrap"].map(lambda v: E.pct(v) if pd.notna(v) else "—"),
        })
        st.dataframe(vista.style.apply(lambda r: ["background-color:#E8F1FA; font-weight:600" if "⭐" in r["Modelo"] else "" for _ in r], axis=1),
                     width="stretch", hide_index=True)
        st.caption(f"Colombia real después del Mundial: {E.num(col['real'])} uds. IC 90 % de la diferencia de WAPE final − ingenuo: "
                   f"{h6['final vs ingenuo: IC 90 % dif. WAPE, P(gana), orígenes ganados'][0].replace('.', ',')} (incluye el 0 → empate).")
        fig = go.Figure()
        for fase, colname in [("Antes", "WAPE_top_antes"), ("Toca el evento", "WAPE_top_evento"), ("Después", "WAPE_top_post")]:
            fig.add_trace(go.Bar(x=[E.nombre_modelo(m) for m in d["modelo"]], y=d[colname], name=fase,
                                 marker_color={"Antes": E.OKABE_ITO[5], "Toca el evento": E.COLOR_EVENTO, "Después": E.OKABE_ITO[0]}[fase],
                                 marker_line=dict(color="#555", width=0.5), hovertemplate="%{x} · " + fase.lower() + ": %{y:.3f}<extra></extra>"))
        fig.update_layout(barmode="group")
        E.layout(fig, "Después del Mundial es donde se separan: media móvil y SARIMAX se disparan", y="WAPE del top", alto=420)
        E.mostrar(fig, "p5_fases")
        E.como_leer("WAPE del top por fase del origen del backtesting. Todos sufren cuando el horizonte toca el evento; "
                    "lo que diferencia a los modelos es la fase **después**: quien arrastra el pico se equivoca muchísimo.")

with tabs[2]:
    if tabs[2].open:  # pestaña perezosa: solo se dibuja la abierta
        o = tabla("wape_por_origen_backtesting").sort_values("corte")
        mods = [m for m in ["ingenuo", "media_movil_4", "ETS", "SARIMAX", "HGB_poisson", "HGB_redondeo", "HGB_ingenuo"] if m in o.columns]
        z = o[mods].T.values
        fig = go.Figure(go.Heatmap(z=z, x=E.fechas(o["corte"]), y=[E.nombre_modelo(m) for m in mods], colorscale="RdYlGn_r",
                                   zmin=0, zmax=min(2.5, float(np.nanmax(z))), text=[[E.dec(v, 2) for v in fila] for fila in z],
                                   texttemplate="%{text}", textfont=dict(size=10), colorbar=dict(title="WAPE"),
                                   hovertemplate="%{y} · origen %{x}: WAPE %{z:.3f}<extra></extra>"))
        fases = o["fase"].tolist()
        for i, f in enumerate(fases):
            if i == 0 or f != fases[i - 1]:
                fig.add_annotation(x=i - 0.4, y=1.0, yref="paper", text=f.replace(" del evento", "").replace("toca el evento", "toca el Mundial"), showarrow=False, xanchor="left", yanchor="bottom",
                                   font=dict(size=11, color="#555"))
                if i:
                    fig.add_vline(x=i - 0.5, line_color="white", line_width=3)
        E.layout(fig, None, x="origen (última semana observada)", alto=430, leyenda=False)
        fig.update_layout(margin=dict(t=40))
        E.mostrar(fig, "p5_origen")
        E.como_leer(T.COMO_LEER["por_origen"])

with tabs[3]:
    if tabs[3].open:  # pestaña perezosa: solo se dibuja la abierta
        hz = tabla("wape_por_horizonte_backtesting")
        fig = go.Figure()
        for m in ORDEN_BT:
            d = hz[hz["modelo"] == m].sort_values("h")
            if d.empty:
                continue
            es = E.estilo_modelo(m)
            fig.add_trace(go.Scatter(x=d["h"], y=d["WAPE"], name=E.nombre_modelo(m), mode="lines+markers",
                                     line=dict(color=es["color"], dash=es["dash"], width=3.5 if m == final else 2),
                                     customdata=d["sesgo"], hovertemplate=E.nombre_modelo(m) + " · h=%{x}: WAPE %{y:.3f}, sesgo %{customdata:+.0%}<extra></extra>"))
        E.layout(fig, "El error crece con el horizonte (backtesting)", x="semanas hacia adelante (h)", y="WAPE del top", alto=430)
        fig.update_xaxes(dtick=1)
        E.mostrar(fig, "p5_h")
        E.como_leer(T.COMO_LEER["por_horizonte"])

with tabs[4]:
    if tabs[4].open:  # pestaña perezosa: solo se dibuja la abierta
        izq, der = st.columns([2, 3], gap="large")
        with izq:
            d = ho.reindex([m for m in ORDEN_BT if m in ho.index])
            fig = go.Figure()
            fig.add_trace(go.Bar(y=[E.nombre_modelo(m) for m in d.index], x=d["top_h_1_4_WAPE"], orientation="h", name="Top · por catálogo (h=1…4)",
                                 marker_color=E.OKABE_ITO[5], hovertemplate="%{y}: %{x:.3f}<extra></extra>"))
            fig.add_trace(go.Bar(y=[E.nombre_modelo(m) for m in d.index], x=d["total_semanal_h_1_6_WAPE"], orientation="h", name="Total semanal (h=1…6)",
                                 marker_color=E.OKABE_ITO[0], hovertemplate="%{y}: %{x:.3f}<extra></extra>"))
            fig.update_layout(barmode="group")
            E.layout(fig, "Holdout: catálogo vs total semanal", x="WAPE (menor = mejor)", alto=470)
            E.mostrar(fig, "p5_ho")
            E.como_leer(T.COMO_LEER["holdout"])
        with der:
            hs = tabla("holdout_total_semanal")
            seg = st.radio("Segmento", ["total", "top", "cola"], horizontal=True, key="p5_seg",
                           format_func=lambda s: {"total": "Total", "top": f"Top {k['top_n']}", "cola": "Cola"}[s])
            d = hs[hs["segmento"] == seg]
            real = d.drop_duplicates("semana").sort_values("semana")
            fig = go.Figure(go.Scatter(x=real["semana"], y=real["y"], name="Venta real", mode="lines+markers",
                                       line=dict(color=E.COLOR_REAL, width=3), text=E.fechas(real["semana"]),
                                       hovertemplate="Real · %{text}: %{y:,.0f} uds<extra></extra>"))
            for m in ORDEN_BT:
                x = d[d["modelo"] == m].sort_values("semana")
                if x.empty:
                    continue
                es = E.estilo_modelo(m)
                fig.add_trace(go.Scatter(x=x["semana"], y=x["pred"], name=E.nombre_modelo(m), mode="lines",
                                         line=dict(color=es["color"], dash=es["dash"], width=3 if m == final else 1.8),
                                         visible=True if m in (final, "ingenuo") else "legendonly", text=E.fechas(x["semana"]),
                                         hovertemplate=E.nombre_modelo(m) + " · %{text}: %{y:,.0f} uds<extra></extra>"))
            E.layout(fig, "Holdout semana a semana", y="uds / semana", alto=420)
            fig.update_xaxes(tickvals=real["semana"], ticktext=E.fechas(real["semana"]))
            E.mostrar(fig, "p5_ho_serie")
            E.como_leer(T.COMO_LEER["holdout_total"])

with tabs[5]:
    if tabs[5].open:  # pestaña perezosa: solo se dibuja la abierta
        dg = tabla("diagnostico_holdout").set_index("modelo")
        peor = h6["holdout sin el catálogo de mayor exceso: WAPE top final / ingenuo"][0]
        E.kpis([
            ("WAPE top holdout · final", E.dec(dg.loc[final, "WAPE_top"]), None),
            (f"Sin {peor.title()}", E.dec(dg.loc[final, "WAPE_top_sin_peor"]),
             E.dec(dg.loc[final, "WAPE_top_sin_peor"] - dg.loc[final, "WAPE_top"]), None, "inverse"),
            ("Exceso de ese catálogo", f"+{E.num(dg.loc[final, 'exceso_uds_peor'])} uds", None),
            ("Exceso de todo el top", f"+{E.num(dg.loc[final, 'exceso_uds_top'])} uds", None,
             "El exceso del top es menor que el de un solo catálogo: los demás se compensan."),
        ])
        hp = tabla("holdout_predicciones_top")
        d = hp[hp["catalogo"] == peor]
        real = d.drop_duplicates("semana").sort_values("semana")
        fig = go.Figure(go.Bar(x=real["semana"], y=real["y"], name="Venta real", marker_color="#BDBDBD",
                               text=E.fechas(real["semana"]), hovertemplate="Real · %{text}: %{y:,.0f} uds<extra></extra>"))
        for m in [final, "ingenuo"]:
            x = d[d["modelo"] == m].sort_values("semana")
            es = E.estilo_modelo(m)
            fig.add_trace(go.Scatter(x=x["semana"], y=x["pred"], name=E.nombre_modelo(m), mode="lines+markers",
                                     line=dict(color=es["color"], dash=es["dash"], width=3), text=E.fechas(x["semana"]),
                                     hovertemplate=E.nombre_modelo(m) + " · %{text}: %{y:,.0f} uds<extra></extra>"))
        pf = d[d["modelo"] == final]["pred"].sum()
        pi = d[d["modelo"] == "ingenuo"]["pred"].sum()
        E.layout(fig, f"{peor.title()}: el modelo pidió {E.num(pf)} uds, el ingenuo {E.num(pi)}; se vendieron {E.num(real['y'].sum())}",
                 y="uds / semana", alto=420)
        fig.update_xaxes(tickvals=real["semana"], ticktext=E.fechas(real["semana"]))
        E.mostrar(fig, "p5_honda")
        E.como_leer(T.COMO_LEER["honda"])

with tabs[6]:
    if tabs[6].open:  # pestaña perezosa: solo se dibuja la abierta
        izq, der = st.columns(2, gap="large")
        ev = tabla("evaluacion_intervalos")
        with izq:
            fig = go.Figure(go.Bar(x=ev["cobertura_80"], y=[m.replace(" · ", "<br>") for m in ev["metodo"]], orientation="h",
                                   marker_color=[E.OKABE_ITO[2] if "fuera del evento) · holdout" in m else E.OKABE_ITO[5] for m in ev["metodo"]],
                                   customdata=ev["ancho_medio"], text=[E.pct(v) for v in ev["cobertura_80"]], textposition="outside",
                                   cliponaxis=False, hovertemplate="%{y}<br>Cobertura %{x:.0%} · ancho medio %{customdata:,.1f} uds<extra></extra>"))
            fig.add_vline(x=0.8, line_dash="dot", line_color="#333")
            fig.add_annotation(x=0.8, y=1.02, yref="paper", text="meta 80 %", showarrow=False)
            fig.update_yaxes(autorange="reversed")
            E.layout(fig, "¿Cuántas veces la venta cayó dentro del intervalo?", x="cobertura", alto=420, leyenda=False)
            fig.update_xaxes(tickformat=".0%", range=[0, 1.12])
            E.mostrar(fig, "p5_cob")
            E.como_leer(T.COMO_LEER["intervalos"])
        with der:
            ih = tabla("intervalos_holdout")
            cats = ih.groupby("catalogo")["y"].sum().sort_values(ascending=False).index.tolist()
            cat = st.selectbox("Catálogo", cats, key="p5_int_cat")
            d = ih[ih["catalogo"] == cat].sort_values("semana")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=d["semana"], y=d["hi"], mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=d["semana"], y=d["lo"], mode="lines", line=dict(width=0), fill="tonexty",
                                     fillcolor="rgba(0,114,178,0.18)", name="Intervalo 10–90 %", hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=d["semana"], y=d["pred"], mode="lines", name="Pronóstico", line=dict(color=E.COLOR_PRONOSTICO, width=2.5),
                                     customdata=np.stack([d["lo"], d["hi"]], axis=1), text=E.fechas(d["semana"]),
                                     hovertemplate="%{text}: %{y:,.0f} uds (%{customdata[0]:,.0f}–%{customdata[1]:,.0f})<extra></extra>"))
            fig.add_trace(go.Scatter(x=d["semana"], y=d["y"], mode="markers", name="Venta real", marker=dict(color=E.COLOR_REAL, size=9),
                                     text=E.fechas(d["semana"]), hovertemplate="Real · %{text}: %{y:,.0f} uds<extra></extra>"))
            E.layout(fig, "Intervalo del modelo final en el holdout", y="uds / semana", alto=380)
            fig.update_xaxes(tickvals=d["semana"], ticktext=E.fechas(d["semana"]))
            E.mostrar(fig, "p5_int")
            E.como_leer(T.COMO_LEER["intervalo_cat"])

with tabs[7]:
    if tabs[7].open:  # pestaña perezosa: solo se dibuja la abierta
        imp = tabla("importancia_permutacion").sort_values("aumento_MAE", ascending=False)
        n = st.slider("Variables a mostrar", 5, len(imp), 15, key="p5_nimp")
        d = imp.head(n).iloc[::-1]
        fig = go.Figure(go.Bar(x=d["aumento_MAE"], y=d["variable"], orientation="h", marker_color=E.OKABE_ITO[0],
                               error_x=dict(type="data", array=d["desv"], color="#555", thickness=1.2),
                               hovertemplate="%{y}: +%{x:.3f} de MAE<extra></extra>"))
        E.layout(fig, "Lo que más usa el modelo: volatilidad reciente, tipo de catálogo y la última semana",
                 x="aumento del MAE al revolver la variable", alto=max(380, 26 * n), leyenda=False)
        E.mostrar(fig, "p5_imp")
        E.como_leer(T.COMO_LEER["importancia"])
        dic = tabla("diccionario_variables").set_index("variable")["descripcion"]
        with st.expander("¿Qué significa cada variable?"):
            E.tabla_st(pd.DataFrame({"Variable": imp["variable"], "Descripción": imp["variable"].map(dic).fillna("—")}).head(n))

with tabs[8]:
    if tabs[8].open:  # pestaña perezosa: solo se dibuja la abierta
        ms = tabla("metricas_por_segmento")
        f1, f2 = st.columns(2)
        fuente = f1.radio("Fuente", ["backtesting", "holdout"], horizontal=True, key="p5_fuente")
        dims = ms[ms["fuente"] == fuente]["dimension"].unique().tolist()
        dim = f2.radio("Corte", dims, horizontal=True, key="p5_dim",
                       format_func=lambda x: {"segmento": "Top / cola", "familia": "Familia", "periodo_semana": "Semana normal / evento", "h": "Horizonte"}.get(x, x))
        d = ms[(ms["fuente"] == fuente) & (ms["dimension"] == dim)]
        fig = go.Figure()
        for m in [x for x in ORDEN_BT if x in d["modelo"].unique()]:
            x = d[d["modelo"] == m]
            es = E.estilo_modelo(m)
            fig.add_trace(go.Bar(x=x["grupo"].astype(str), y=x["WAPE"], name=E.nombre_modelo(m), marker_color=es["color"],
                                 customdata=np.stack([x["sesgo"], x["uds_reales"]], axis=1),
                                 hovertemplate=E.nombre_modelo(m) + " · %{x}: WAPE %{y:.3f}, sesgo %{customdata[0]:+.0%} (%{customdata[1]:,.0f} uds reales)<extra></extra>"))
        fig.update_layout(barmode="group")
        E.layout(fig, "WAPE por segmento", y="WAPE", alto=420)
        E.mostrar(fig, "p5_seg_fig")
        E.como_leer("Barras agrupadas: cada color es un modelo. Compare dentro de cada grupo; la cola tiene WAPE alto por catálogo "
                    "porque vende a saltos, pero sumada se pronostica bien.")

E.nota_borrador()
