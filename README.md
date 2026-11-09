# Pronóstico de demanda — Klixmant S.A.S.

Trabajo final de **Analítica de Marketing** (UNAB · TEMA, curso 2228). Pronóstico semanal de unidades **por catálogo**, con separación de la demanda **base** y la demanda **de evento** (Mundial 2026) y desagregación a **talla × color** y a **tela** para planear compras y cortes.

**🌐 App publicada:** <https://klixmant-pronostico.streamlit.app/> (Streamlit Community Cloud, rama `main`).

> 🔒 **Confidencial.** Los datos son de Klixmant S.A.S. Este repositorio es privado; la **app sí es pública** para quien tenga el enlace (decisión del grupo, ver [reporte 08](docs/REPORTE_AGENTE_08_despliegue.md) §4) y muestra solo datos agregados (catálogo × semana). El Excel original y la documentación de la base de datos **no se suben** (ver `.gitignore`).
>
> ✍️ **Turnitin.** El texto markdown del notebook y de `docs/` es un borrador técnico: el grupo debe redactarlo con sus propias palabras antes de entregar.

## Estado

| Parte | Estado |
|---|---|
| §0–§3 Negocio, cuadre y EDA | ✅ |
| §4 Preparación y variables | ✅ |
| §5 Modelado | ✅ |
| §6 Validación (backtesting + holdout) + §6.11 comparación con el modelo inicial (SKU) | ✅ (actualizado 9-nov) |
| §7 Gráficas | ✅ |
| §8 Modelo guardado, guía, *model card* y datos de la app | ✅ |
| Tablero Streamlit | ✅ Publicado en <https://klixmant-pronostico.streamlit.app/> (app: agente 07 — [reporte](docs/REPORTE_AGENTE_07_app.md); QA y despliegue: agente 08 — [reporte](docs/REPORTE_AGENTE_08_despliegue.md)) |
| Póster | ⏳ (después) |

Modelo final: `HGB_sin_atipico` (HistGradientBoosting Poisson global, scikit-learn; el Mundial se trata como **dato atípico**: sus semanas no entran al entrenamiento y los rezagos se calculan sin el pico), con la cola de catálogos por regla ingenua. §6.11 del notebook compara con el modelo inicial del curso a nivel SKU (MAPE en filas con venta: 79,8 % → 67,2 %).
Para generar un pronóstico nuevo, ver [docs/guia_generar_pronostico.md](docs/guia_generar_pronostico.md); límites del modelo en [docs/model_card.md](docs/model_card.md).

## Estructura

```
Klixmant_Pronostico_Demanda.ipynb   Notebook principal (CRISP-DM, secciones 0–8)
Plan_de_Investigacion_Klixmant.md    Guía de investigación y decisiones
requirements.txt                     Librerías del notebook
datos/        Excel original (no se versiona)
procesado/    Tablas intermedias (prefijo = sección: 3_, 4_, 5_, 6_, 7_)
figuras/      Gráficas (prefijo = sección) y figuras/poster/
modelos/      Modelo entrenado (§8): hgb_final.joblib + metadata.json
app/          App Streamlit (entrypoint app/Inicio.py, páginas en app/paginas/, utils/)
app/data/     Datos precalculados para la app Streamlit (§8.4; ver app/data/ESQUEMA.md)
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
   (opcional, para el LSTM de §5: `pip install torch --index-url https://download.pytorch.org/whl/cpu`)
3. Abrir el notebook y ejecutar *Run all* (~17 min; con `RECALCULAR_BACKTESTING = False` baja varios minutos).
   En Colab: agregar la carpeta compartida de Drive como acceso directo en "Mi unidad" (ver reporte 01).

## Cómo correr la app (Streamlit)

Con Python 3.12 (la versión de Streamlit Community Cloud):

```bash
py -V:3.12 -m venv .venv-app
```
```bash
.venv-app\Scripts\pip install -r app/requirements.txt
```
```bash
.venv-app\Scripts\streamlit run app/Inicio.py
```

La app solo lee `app/data/` (no necesita el Excel ni el modelo). Detalles en [docs/REPORTE_AGENTE_07_app.md](docs/REPORTE_AGENTE_07_app.md).

**En la nube:** <https://klixmant-pronostico.streamlit.app/>. Cada `git push` a `main` la redespliega sola; configuración y cómo redesplegar a mano en [docs/REPORTE_AGENTE_08_despliegue.md](docs/REPORTE_AGENTE_08_despliegue.md).

## Documentación en `docs/`

| Archivo | Contenido |
|---|---|
| `REPORTE_AGENTE_01_secciones_0-3.md` | Entorno, convenciones, cuadre y EDA |
| `REPORTE_AGENTE_02_seccion_4.md` | Limpieza, panel, variables, K-means, base vs evento |
| `REPORTE_AGENTE_03_seccion_5.md` | Escalera de modelos y candidato |
| `REPORTE_AGENTE_04_seccion_6.md` | Backtesting, holdout e intervalos (cifras del holdout superadas por el reporte 05) |
| `REPORTE_AGENTE_05_seccion_7.md` | Gráficas, pronóstico vigente y corrección de `early_stopping` |
| `REPORTE_AGENTE_06_seccion_8.md` | Modelo guardado, pronóstico oficial, documentación y bundle de la app |
| `REPORTE_AGENTE_07_app.md` | App Streamlit: páginas, verificación, capturas (`docs/capturas_app/`) y notas para el despliegue |
| `REPORTE_AGENTE_08_despliegue.md` | QA de la app, despliegue en Streamlit Community Cloud, acceso y cómo redesplegar |
| `PLAN_DESPLIEGUE_STREAMLIT.md` | Plan para §8, la app Streamlit y su publicación |
| `guia_generar_pronostico.md` | Cómo generar un pronóstico nuevo (para Klixmant) |
| `model_card.md` | Uso previsto, métricas, limitaciones y cuándo reentrenar |
| `registro_decisiones.md` | Decisión · alternativas · por qué (§2–§8) |
| `4_diccionario_variables.csv` | Diccionario de variables del panel |
| `7_indice_figuras.csv` | Índice de figuras por fase |
