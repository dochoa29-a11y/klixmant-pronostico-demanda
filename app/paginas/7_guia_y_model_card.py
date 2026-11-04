"""7 · Guía y model card — cómo usarlo y cuándo no confiar en él."""
import pandas as pd
import streamlit as st

from utils import estilo as E
from utils import textos as T
from utils.datos import FIGURAS, cifras, documento, kpi, tabla

k = kpi()
cf = cifras()
md = cf["metadata_modelo"]

E.encabezado(
    "Guía y model card",
    f"Úselo para las próximas <b>{cf['constantes']['horizonte_principal']} semanas</b> del top y revise a mano; "
    "<b>no confíe</b> en él ante eventos que no vio (otro torneo, Black Friday, diciembre) ni en catálogos nuevos.",
    "📘",
)
E.kpis([
    ("Corte del modelo", E.fecha(md["corte"], True)),
    ("Filas de entrenamiento", E.num(md["filas_entrenamiento"]), None, "Catálogo × semana."),
    ("Variables", E.num(cf["h4"]["variables del modelo"])),
    ("Iteraciones del boosting", E.num(md["n_iter"]), None, "Tras la corrección de early_stopping."),
    ("Versión de scikit-learn", md["versiones"]["scikit-learn"], None, "El modelo se entrena en el notebook; la app no lo carga."),
])

tabs = st.tabs(["🧭 Guía", "🪪 Model card", "📝 Decisiones", "🔤 Diccionario de variables", "📖 Glosario", "📚 Bibliografía", "🖼️ Figuras"])


def mostrar_md(nombre: str) -> None:
    texto = documento(nombre)
    # el primer título del documento ya lo da la pestaña
    lineas = texto.splitlines()
    if lineas and lineas[0].startswith("# "):
        texto = "\n".join(lineas[1:])
    st.markdown(texto)


with tabs[0]:
    mostrar_md("guia_generar_pronostico.md")
with tabs[1]:
    mostrar_md("model_card.md")
with tabs[2]:
    mostrar_md("registro_decisiones.md")
with tabs[3]:
    dic = tabla("diccionario_variables")
    f1, f2 = st.columns([3, 2])
    q = f1.text_input("🔎 Buscar variable o palabra", key="p7_q", placeholder="p. ej. mundial, lag, dropi")
    grupos = f2.multiselect("Grupo", sorted(dic["grupo"].unique()), key="p7_g")
    d = dic
    if q:
        mask = d.apply(lambda r: r.astype(str).str.contains(q, case=False, regex=False).any(), axis=1)
        d = d[mask]
    if grupos:
        d = d[d["grupo"].isin(grupos)]
    st.caption(f"{len(d)} de {len(dic)} variables")
    E.tabla_st(d.rename(columns={"variable": "Variable", "grupo": "Grupo", "descripcion": "Descripción",
                                 "ventana_temporal": "Ventana temporal", "uso": "Uso"}), height=520)
with tabs[4]:
    q = st.text_input("🔎 Buscar término", key="p7_gq")
    cols = st.columns(2)
    items = [(t, d) for t, d in T.GLOSARIO.items() if not q or q.lower() in (t + d).lower()]
    for i, (t, d) in enumerate(items):
        with cols[i % 2].container(border=True):
            st.markdown(f"**{t}**")
            st.markdown(d)
with tabs[5]:
    mostrar_md("bibliografia.md")
with tabs[6]:
    idx = tabla("indice_figuras")
    pngs = sorted(FIGURAS.glob("*.png"))
    st.caption(f"{len(pngs)} figuras estáticas del notebook (respaldo). Las gráficas interactivas de la app las reemplazan.")
    elegida = st.selectbox("Figura", [p.name for p in pngs], key="p7_fig")
    st.image(str(FIGURAS / elegida), width="stretch")
    with st.expander("Índice de figuras del plan"):
        E.tabla_st(idx.rename(columns={"fase_plan": "Fase", "grafica_plan": "Gráfica", "archivo": "Archivo",
                                       "poster": "Póster", "existe": "Existe"}))

E.nota_borrador()
