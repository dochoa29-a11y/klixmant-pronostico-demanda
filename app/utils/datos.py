"""Carga del bundle precalculado (app/data/). La app no lee nada fuera de esta carpeta."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

APP = Path(__file__).resolve().parent.parent
DATA = APP / "data"
DOCS = DATA / "docs"
FIGURAS = DATA / "figuras"


@st.cache_data(show_spinner=False)
def tabla(nombre: str) -> pd.DataFrame:
    """Lee app/data/<nombre>.parquet. Texto como object para que funcione igual con pandas 2 y 3."""
    df = pd.read_parquet(DATA / f"{nombre}.parquet")
    for c in df.columns:
        if pd.api.types.is_string_dtype(df[c]) and not pd.api.types.is_object_dtype(df[c]):
            df[c] = df[c].astype(object)
    return df


@st.cache_data(show_spinner=False)
def cifras() -> dict:
    """cifras_clave.json completo (kpi, h3…h8, constantes, paleta, metadata_modelo)."""
    return json.loads((DATA / "cifras_clave.json").read_text(encoding="utf-8"))


def kpi() -> dict:
    return cifras()["kpi"]


def constantes() -> dict:
    return cifras()["constantes"]


@st.cache_data(show_spinner=False)
def documento(nombre: str) -> str:
    """Markdown copiado en app/data/docs/ por app/copiar_docs.py."""
    ruta = DOCS / nombre
    return ruta.read_text(encoding="utf-8") if ruta.exists() else f"_No se encontró `{nombre}` en app/data/docs/._"


def figura(nombre: str) -> Path:
    return FIGURAS / nombre


# ---------- tablas derivadas (pequeñas, en caché) ----------

@st.cache_data(show_spinner=False)
def historia_y_pronostico() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Historia semanal y pronóstico oficial, con el segmento (top/cola)."""
    return tabla("historia_semanal_catalogo"), tabla("pronostico_catalogo")


@st.cache_data(show_spinner=False)
def curvas_cluster() -> pd.DataFrame:
    """Curva semanal promedio por clúster: cada catálogo normalizado por su total (participación semanal)."""
    hist = tabla("historia_semanal_catalogo")
    maestro = tabla("maestro_catalogos")[["catalogo", "cluster"]]
    df = hist.merge(maestro, on="catalogo", how="left")
    df = df[df["cluster"].notna() & (df["cluster"] != "cola")]
    tot = df.groupby("catalogo")["y"].transform("sum")
    df = df[tot > 0].assign(part=lambda d: d["y"] / d.groupby("catalogo")["y"].transform("sum"))
    # rejilla completa catálogo × semana (antes de la primera venta = 0)
    semanas = sorted(hist["semana"].unique())
    rej = pd.MultiIndex.from_product([df["catalogo"].unique(), semanas], names=["catalogo", "semana"])
    part = df.set_index(["catalogo", "semana"])["part"].reindex(rej, fill_value=0).reset_index()
    part = part.merge(maestro, on="catalogo")
    out = part.groupby(["cluster", "semana"])["part"].mean().reset_index()
    n = part.groupby("cluster")["catalogo"].nunique().rename("n_catalogos").reset_index()
    return out.merge(n, on="cluster")
