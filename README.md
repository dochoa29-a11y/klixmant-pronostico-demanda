# Pronóstico de demanda — Klixmant S.A.S.

Trabajo final de **Analítica de Marketing** (UNAB · TEMA, curso 2228). Pronóstico semanal de unidades **por catálogo**, con separación de la demanda **base** y la demanda **de evento** (Mundial 2026) y desagregación a **talla × color** y a **tela** para planear compras y cortes.

> 🔒 **Confidencial.** Los datos son de Klixmant S.A.S. Este repositorio es privado. El Excel original y la documentación de la base de datos **no se suben** (ver `.gitignore`).
>
> ✍️ **Turnitin.** El texto markdown del notebook y de `docs/` es un borrador técnico: el grupo debe redactarlo con sus propias palabras antes de entregar.

## Estado

| Parte | Estado |
|---|---|
| §0–§3 Negocio, cuadre y EDA | ✅ |
| §4 Preparación y variables | ✅ |
| §5 Modelado | ✅ |
| §6 Validación (backtesting + holdout) | ✅ |
| §7 Gráficas | ✅ |
| §8 Modelo guardado, guía y *model card* | ⏳ (agente 06) |
| Tablero Streamlit | ⏳ (agentes 07–08) — ver [docs/PLAN_DESPLIEGUE_STREAMLIT.md](docs/PLAN_DESPLIEGUE_STREAMLIT.md) |
| Póster | ⏳ (después) |

Modelo final: `HGB_redondeo` (HistGradientBoosting Poisson global, scikit-learn), con la cola de catálogos por regla ingenua.

## Estructura

```
Klixmant_Pronostico_Demanda.ipynb   Notebook principal (CRISP-DM, secciones 0–8)
Plan_de_Investigacion_Klixmant.md    Guía de investigación y decisiones
requirements.txt                     Librerías del notebook
datos/        Excel original (no se versiona)
procesado/    Tablas intermedias (prefijo = sección: 3_, 4_, 5_, 6_, 7_)
figuras/      Gráficas (prefijo = sección) y figuras/poster/
modelos/      Modelo entrenado (§8)
docs/         Reportes de traspaso, diccionario de variables, índice de figuras y plan de despliegue
```

## Cómo correr el notebook

1. Poner `Klixmant_Base_de_Datos_UNAB_2026-10-07.xlsx` en `datos/` o en la raíz.
2. Crear un entorno e instalar dependencias:
   ```bash
   python -m venv .venv
   ```
   ```bash
   .venv\Scripts\pip install -r requirements.txt
   ```
3. Abrir el notebook y ejecutar *Run all* (~17 min; con `RECALCULAR_BACKTESTING = False` baja varios minutos).
   En Colab: agregar la carpeta compartida de Drive como acceso directo en "Mi unidad" (ver reporte 01).

## Documentación en `docs/`

| Archivo | Contenido |
|---|---|
| `REPORTE_AGENTE_01_secciones_0-3.md` | Entorno, convenciones, cuadre y EDA |
| `REPORTE_AGENTE_02_seccion_4.md` | Limpieza, panel, variables, K-means, base vs evento |
| `REPORTE_AGENTE_03_seccion_5.md` | Escalera de modelos y candidato |
| `REPORTE_AGENTE_04_seccion_6.md` | Backtesting, holdout e intervalos (cifras del holdout superadas por el reporte 05) |
| `REPORTE_AGENTE_05_seccion_7.md` | Gráficas, pronóstico vigente y corrección de `early_stopping` |
| `PLAN_DESPLIEGUE_STREAMLIT.md` | Plan para §8, la app Streamlit y su publicación |
| `4_diccionario_variables.csv` | Diccionario de variables del panel |
| `7_indice_figuras.csv` | Índice de figuras por fase |
