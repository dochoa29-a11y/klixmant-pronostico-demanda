# Plan de despliegue — Tablero Streamlit del pronóstico de demanda Klixmant

**Fecha:** 4-nov-2026 · **Para:** agentes 06, 07 y 08 · **Repo:** `klixmant-pronostico-demanda` (GitHub, privado, rama `main`)
**Lean antes:** `Plan_de_Investigacion_Klixmant.md` y `docs/REPORTE_AGENTE_01…05_*.md`. Sus convenciones siguen vigentes.

> **Estado al empezar:** el notebook `Klixmant_Pronostico_Demanda.ipynb` tiene §0–§7 completas y ejecutadas. **§8 (modelo guardado, guía, *model card*) sigue pendiente**, no existe la app y el póster queda para después (fuera de este plan).
> En este equipo no hay `python` en el PATH: el venv de los agentes 02–05 no está en el proyecto. Hay que crear uno.

---

## 0. Objetivo

Un **despliegue integral en Streamlit** que muestre todo el trabajo (negocio → datos → Mundial → modelos → plan de producción → guía), con **mucho énfasis visual y facilidad de entendimiento**, publicado en **Streamlit Community Cloud** desde el repo privado.

## 1. Principios de la app

- **Historia, no catálogo de gráficas.** Recorrido CRISP-DM: problema → datos → Mundial → modelo → plan de producción → cómo usarlo. Cada página abre con **una frase-conclusión grande** y 3–4 KPI (`st.metric`).
- **Cero recálculo pesado en la nube.** La app lee un *bundle* precalculado (parquet + JSON) que genera el notebook. Nada de leer el Excel ni reentrenar en Streamlit Cloud (el notebook tarda ~17 min).
- **Interactivo con plotly**, con la misma paleta del notebook: Okabe-Ito, `COLOR_CANAL`, `COLOR_FAMILIA`, `ESTILO_MODELO`. Banda sombreada del Mundial (11-jun → 19-jul) y de la ventana del evento (25-may → 13-jul). Títulos que dicen la conclusión, ejes con unidades, meses en español, punto de miles.
- **Fácil de entender:** cada gráfica con un `st.expander("¿Cómo leer esta gráfica?")` y un glosario (WAPE, sesgo, MASE, ingenuo, backtesting, holdout, ADI/CV², base vs evento) en lenguaje de negocio.
- **Honestidad de resultados** (reportes 04–05): el boosting **no le gana con claridad al ingenuo** en el top; su valor es que **no arrastra el Mundial**. Titular: *"Tras el Mundial el modelo pronosticó 75 uds de Colombia (real 49); una media móvil habría pedido 3.990"*.
- **Cifras vigentes = las posteriores a la corrección de `early_stopping`** (reporte 05 §2). Las tablas 3.1–3.2 del reporte 04 están viejas. Ningún número se escribe a mano en la app: todo sale de `cifras_clave.json` o de las tablas.
- Los textos de la app son **borradores**; el grupo los reescribe con sus palabras (riesgo Turnitin).

## 2. Arquitectura

```
app/
  Inicio.py                 # entrypoint (st.navigation / st.Page)
  requirements.txt          # streamlit, pandas, plotly, pyarrow (sin torch ni statsmodels)
  .streamlit/config.toml    # tema claro, color primario, fuente
  paginas/
    1_problema_y_datos.py
    2_exploracion.py
    3_mundial_base_evento.py
    4_segmentacion.py
    5_modelos_y_validacion.py
    6_plan_de_produccion.py
    7_guia_y_model_card.py
  utils/
    datos.py      # cargar_*() con @st.cache_data, lee app/data/
    estilo.py     # paleta, layout plotly común, banda_mundial(fig), fmt_miles()
    textos.py     # glosario y textos de ayuda
  data/           # bundle generado por el notebook (§8.4)
    *.parquet, cifras_clave.json, ESQUEMA.md, figuras/ (PNG de respaldo)
```

- Streamlit Cloud con **Python 3.12** (verificar compatibilidad de pandas ≥ 3; si no, fijar la versión más alta disponible y probar en un venv limpio).
- Entrypoint: `app/Inicio.py`. Streamlit Cloud busca `requirements.txt` primero junto al entrypoint.
- Las rutas se resuelven con `Path(__file__).parent`, nunca relativas al directorio de trabajo.

## 3. Páginas

| Página | Mensaje | Visuales | Fuente (`procesado/` → bundle) |
|---|---|---|---|
| **Inicio** | Resumen ejecutivo en 30 s | KPI: 29.919 uds, 806 catálogos, 9 meses, top 20 = 77 %, +6.582 uds de evento; diagrama CRISP-DM con enlaces a cada página (`st.page_link`); titular P3 | `cifras_clave.json` |
| **1 Problema y datos** | Se compra sin modelo y el inventario queda tras el evento | Tabla de decisiones (plan §2); cuadre de cifras de control con ✅; reglas de limpieza (§4.1); jerarquía Total → Canal → Tela → Catálogo → Talla × Color | `3_cuadre_cifras_control`, reglas de §4.1 |
| **2 Exploración** | Demanda concentrada, errática y dominada por el Mundial | Serie semanal por canal con banda; Pareto interactivo; dispersión ADI/CV² con cuadrantes (hover = catálogo); heatmap día × semana; % Dropi; ciclo de vida; mezcla de tallas | `3_serie_semanal_canal`, `3_clasificacion_catalogos`, `3_demanda_diaria_catalogo_canal` (agregada), `3_estabilidad_mezcla_top` |
| **3 Mundial: base vs evento** (pregunta central de Klixmant) | El 87 % de lo que vendió Colombia en la ventana fue evento; motos y autos cayeron | Selector de catálogo/línea → área apilada base + evento; barras de incremental por catálogo; tabla de sensibilidad; nota de demanda desplazada (hipótesis por validar) | `4_base_evento_catalogo_semana` (filtrar top + líneas), `4_incremental_mundial_top/_linea`, `4_sensibilidad_base_evento`, `5_comparacion_rutas` |
| **4 Segmentación** | 4 perfiles: evento, base, en declive, base errática | Curvas promedio por clúster; tabla de catálogos por clúster; codo/silueta | `4_perfil_clusters`, `4_maestro_catalogos` |
| **5 Modelos y validación** | El modelo no arrastra el Mundial; empata con el ingenuo | Escalera de modelos (tarjetas); tabla de backtesting resaltada; heatmap WAPE por origen con fases; WAPE por horizonte; holdout (top vs total semanal); caso Honda; cobertura de intervalos; importancia por permutación; recuadro "corrección de early_stopping" | `6_metricas_backtesting`, `6_wape_por_origen_backtesting`, `6_metricas_holdout`, `6_diagnostico_holdout`, `6_evaluacion_intervalos`, `6_metricas_por_segmento`, `5_importancia_permutacion`, `6_holdout_predicciones` (solo top, final + ingenuo) |
| **6 Plan de producción** (herramienta) | Qué cortar las próximas 4–8 semanas | Filtros catálogo / semana / horizonte 4–8; historia + pronóstico + intervalo + ingenuo; heatmap catálogo × semana; heatmap talla × color; barras de tela (insumo); banderas `revisar`; **ajuste experto** (slider de % por semana, p. ej. Black Friday) aplicado solo en pantalla; `st.download_button` para CSV | `7_pronostico_vigente_catalogo`, `_talla_color`, `_tela`, `7_revision_vs_ingenuo`, historia de `4_panel_semanal_catalogo` (solo `catalogo, semana, y` del top) |
| **7 Guía y model card** | Cómo usarlo y cuándo no confiar | Guía "cómo generar un pronóstico", *model card*, limitaciones, diccionario de variables con buscador, glosario, bibliografía | `docs/*.md` de §8, `docs/4_diccionario_variables.csv` |

Sin páginas de póster.

## 4. Reparto en agentes (secuencial)

### Agente 06 — §8 del notebook + bundle de datos (prerrequisito)
Trabaja en `Klixmant_Pronostico_Demanda.ipynb`.
1. Leer reportes 01–05 y este plan. Crear un venv con `requirements.txt` + `pyarrow` (y torch CPU si se corre el LSTM).
2. Arreglar el fallo conocido de §6.8: `drop(columns=["segundos"], errors="ignore")` en `bt` y `ho`.
3. **§8.1** Entrenar con `ctx = contexto(ULTIMA_SEMANA_COMPLETA)` + `ajustar_hgb(ctx, ULTIMA_SEMANA_COMPLETA)`; `assert modelo.n_iter_ == 300` (con `early_stopping=False`). Guardar `modelos/hgb_final.joblib` + `modelos/metadata.json` (versiones, corte, `PARAMS_HGB`, variables, `CALIBRACION_INTERVALO`).
4. **§8.2** Pronosticar con el modelo **cargado** vía `pronostico_recursivo(..., redondear=True)` y comprobar que reproduce `pron_vigente["pred_modelo"]` (prueba del reporte 05 §6.1).
5. **§8.3** Docs en `docs/`: `guia_generar_pronostico.md`, `model_card.md` (limitaciones del reporte 04 §5.5 y del reporte 05 §6–§8), `registro_decisiones.md`.
6. **§8.4** Función `exportar_bundle_app()` que escribe en `app/data/`: parquet filtrados/agregados (meta: < 15 MB en total; **no** copiar completos los CSV de 21–23 MB), `cifras_clave.json` con `h3…h7`, y copia de figuras clave como respaldo. Documentar columnas y tipos de cada archivo en `app/data/ESQUEMA.md`.
7. Entregar `docs/REPORTE_AGENTE_06_seccion_8.md`. Commit + push.

### Agente 07 — App Streamlit
Solo toca `app/`; no modifica el notebook.
1. Implementar §2–§3 sobre `app/data/ESQUEMA.md`. Primero `utils/estilo.py` (paleta y layout común), luego las páginas en orden.
2. Formato es-CO (punto de miles, meses en español), `st.set_page_config(layout="wide")`, sidebar con navegación y nota de corte de datos (28-sep-2026).
3. Probar con `streamlit run app/Inicio.py` y revisar cada página en el navegador (escritorio y ancho móvil).
4. Entregar `docs/REPORTE_AGENTE_07_app.md` con capturas. Commit + push.
- *Opcional para paralelizar:* 07a hace `utils/` + Inicio + páginas 1–3; 07b hace las páginas 4–7 una vez 07a publique `utils/`.

### Agente 08 — QA y despliegue
1. Revisión cruzada: cada cifra mostrada coincide con `cifras_clave.json` y con los reportes (cifras post-corrección); sin errores en consola; carga < 3 s por página; contraste y tamaños legibles.
2. Despliegue en **Streamlit Community Cloud**: el usuario inicia sesión en share.streamlit.io con GitHub y autoriza el repo privado (el agente no maneja credenciales). Configuración: repo `klixmant-pronostico-demanda`, rama `main`, entrypoint `app/Inicio.py`, Python 3.12. Definir quién puede ver la app: los datos agregados quedan visibles para los invitados.
3. Agregar el enlace al `README.md`. Entregar `docs/REPORTE_AGENTE_08_despliegue.md`.

## 5. Riesgos

| Riesgo | Mitigación |
|---|---|
| Cifras viejas del reporte 04 | Leer siempre `cifras_clave.json`; nunca escribir números a mano |
| Memoria limitada en Streamlit Cloud (~1 GB) | Bundle parquet pequeño y `@st.cache_data` |
| pandas 3 vs. Python de Cloud | Fijar versiones en `app/requirements.txt` y probar en un venv limpio |
| Exposición de datos de Klixmant | Repo privado; app con visores restringidos; sin Excel ni tablas por línea de pedido |
| Turnitin | Textos marcados como borrador para que el grupo los reescriba |
