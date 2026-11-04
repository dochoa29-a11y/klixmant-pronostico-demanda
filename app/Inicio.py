"""Entrypoint de la app Streamlit — Pronóstico de demanda Klixmant S.A.S.

    streamlit run app/Inicio.py

Solo lee app/data/ (bundle generado por el notebook §8.4). No reentrena ni lee el Excel.
"""
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Klixmant · Pronóstico de demanda",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="auto",  # abierto en escritorio, colapsado en celular
)

from utils import estilo, textos  # noqa: E402  (después de set_page_config)
from utils.datos import kpi  # noqa: E402

AQUI = Path(__file__).resolve().parent
P = AQUI / "paginas"

paginas = {
    "Resumen": [
        st.Page(P / "0_inicio.py", title="Inicio", icon="🏠", default=True),
    ],
    "La historia": [
        st.Page(P / "1_problema_y_datos.py", title="1 · Problema y datos", icon="📋"),
        st.Page(P / "2_exploracion.py", title="2 · Exploración", icon="🔎"),
        st.Page(P / "3_mundial_base_evento.py", title="3 · Mundial: base vs evento", icon="⚽"),
        st.Page(P / "4_segmentacion.py", title="4 · Segmentación", icon="🧩"),
        st.Page(P / "5_modelos_y_validacion.py", title="5 · Modelos y validación", icon="📈"),
    ],
    "Herramienta": [
        st.Page(P / "6_plan_de_produccion.py", title="6 · Plan de producción", icon="✂️"),
        st.Page(P / "7_guia_y_model_card.py", title="7 · Guía y model card", icon="📘"),
    ],
}

pg = st.navigation(paginas)
estilo.css()

k = kpi()
with st.sidebar:
    st.markdown("### 🧵 Klixmant S.A.S.")
    st.caption("Pronóstico semanal de demanda por catálogo · Analítica de Marketing (UNAB)")
    st.info(textos.AVISO_DATOS.format(corte=estilo.fecha(k["fecha_corte_datos"], anio=True),
                                      semana=estilo.fecha(k["ultima_semana_completa"], anio=True)), icon="🗓️")
    st.caption("✍️ Textos en borrador. Modelo: "
               f"`{k['modelo_final']}` (top {k['top_n']}) · cola: `{k['modelo_cola']}`.")

pg.run()
