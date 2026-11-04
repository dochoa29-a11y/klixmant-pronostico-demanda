# Reporte de traspaso — Agente 06 (sección 8)

**Fecha:** 4-nov-2026 · **Alcance:** §8 Documentación y despliegue (plan §8 y `PLAN_DESPLIEGUE_STREAMLIT.md` §4 "Agente 06"): modelo guardado y
verificado, pronóstico oficial con el modelo cargado, guía, *model card*, registro de decisiones y *bundle* de datos para la app Streamlit.
**No se construyó la app** (agente 07) ni se tocó el póster.
Lean también los reportes 01–05. Las cifras vigentes son las **posteriores a la corrección de `early_stopping`** (reporte 05 §2).

---

## 1. Qué se entregó

| Archivo | Qué es |
|---|---|
| `Klixmant_Pronostico_Demanda.ipynb` | §8 completa y ejecutada (celdas 148–158). La celda 0 marca §8 ✅ |
| `modelos/hgb_final.joblib` | Modelo de producción (196 KB, `compress=3`), entrenado al 28-sep, **300 iteraciones** |
| `modelos/metadata.json` | Corte, sha256, parámetros, 37 variables, categorías, calibración del intervalo, umbrales de revisión, versiones |
| `procesado/8_pronostico_*.csv` | **Tablas oficiales**: catálogo × semana, talla × color, tela, revisión vs ingenuo |
| `docs/guia_generar_pronostico.md` | Guía para Klixmant (entrada, limpieza, pasos, salida, revisión, cuándo reentrenar, problemas frecuentes) |
| `docs/model_card.md` | *Model card* (Mitchell et al., 2019) con cifras post-corrección y 11 limitaciones |
| `docs/registro_decisiones.md` | 30 decisiones: decisión · alternativas · por qué · dónde · revisar |
| `app/data/` | *Bundle* de la app: 42 parquet + `cifras_clave.json` + 16 PNG + `ESQUEMA.md` = **2,9 MB** (meta < 15 MB) |
| `requirements.txt` | Se agregaron `joblib` y `pyarrow` |
| `README.md` | Estado §8 ✅, carpeta `app/data/`, enlaces a guía y *model card* |

**Ejecución verificada:** notebook completo de arriba abajo con `nbconvert --execute --inplace`, **0 celdas con error**, en 20 min.
Entorno nuevo (no había venv en el proyecto): `C:\Users\diani\.venvs\klixmant` (fuera de OneDrive, para no sincronizar 1 GB),
Python 3.14.7, pandas 3.1.1, numpy 2.5.4, scikit-learn 1.9.1, statsmodels 0.15.0, pyarrow 26.0.1, joblib 1.6.0, torch 2.15.0 CPU.
Solo aparece el aviso conocido de joblib al cerrar el kernel (reporte 04).
Copia del notebook **antes** de §8: scratchpad del agente 06 (`notebook_antes_s8.ipynb`).

**Cambios fuera de §8 (pequeños):**
- **§6.8:** `drop(columns=["segundos"], errors="ignore")` en `bt` y `ho` (fallo conocido del reporte 05 §7 con `RECALCULAR_BACKTESTING = False`).
- **§3.5:** se agregó `h3 = h` al final de la celda. Las cifras clave de §3 se guardaban en `h`, un nombre que se reutiliza más adelante.
- Al reejecutar cambiaron `procesado/5_*.csv` solo en la columna `segundos` (tiempos) y en el orden de filas empatadas. Los PDF del póster solo cambian en metadatos.

## 2. Estructura de §8 en el notebook

| Celda | Contenido |
|---|---|
| 8 (md) | Objetivo: separar entrenar / guardar / pronosticar; tabla de productos |
| 8.1 | `CORTE_PRODUCCION`, `ctx_prod`, **`modelo_final`** = `ajustar_hgb(contexto(ULTIMA_SEMANA_COMPLETA), ULTIMA_SEMANA_COMPLETA)`; `assert n_iter_ == 300`, `early_stopping is False` y orden de variables; `joblib.dump`; `_a_json()`; **`metadata`** |
| 8.2 | **`cargar_modelo()`** (verifica sha256, `n_iter_`, variables y versión de sklearn), **`generar_pronostico(modelo, corte, h)`** → dict `catalogo / talla_color / tela / revision`; prueba contra §7.2.1; exporta `8_*.csv` |
| 8.3 | Verifica que existan los 3 docs y que la *model card* cite las cifras de la corrida (WAPE backtesting, holdout h=1…4, total semanal) |
| 8.4 | `tablas_bundle()`, **`exportar_bundle_app()`**, `FIGURAS_APP`, `DESC_COLUMNAS`; `assert` de tamaño < 15 MB e ida y vuelta del parquet |
| 8.5 / 8.6 | Cifras clave `h8` y lectura en borrador |

## 3. Resultados

### 3.1 Modelo guardado (§8.1)
- 17.722 filas (792 catálogos, 29.428 uds), corte **28-sep-2026**, **`n_iter_ = 300`** ✅. Entrena en ~2 s.
- La metadata trae todo lo necesario para auditarlo o recargarlo: `params_hgb`, `variables`, `categorias` por variable categórica,
  `pronostico` (recursivo, redondeo, tope 2, 12 semanas activo, cola ingenuo, lista `top`), `intervalo` (z₁₀ / z₉₀ por *h*), `revision_manual`, `versiones`.

### 3.2 Pronóstico oficial con el modelo cargado (§8.2)
- **Reproduce exactamente `pron_vigente["pred_modelo"]` de §7.2.1** (diferencia máxima = 0; también `pred` y `revisar`). Prueba del reporte 05 §6.1 superada.
- Próximas 4 semanas (5-oct → 26-oct): **top 1.444 uds** (ingenuo 1.372) y **cola 984 uds**. Ningún catálogo del top queda para revisión manual.
- Mayores volúmenes: CA Mercedes 221, CA Honda Reflectivo 216, CA Yamaha Reflectivo 164, CA BMW Estampado 162 (4 semanas).
- `procesado/8_pronostico_catalogo.csv` (6.336 filas = 792 × 8), `_talla_color` (4.824), `_tela` (960), `8_revision_vs_ingenuo.csv` (20).

### 3.3 Cifras de la *model card* (post-corrección)
WAPE top backtesting **0,897** (ingenuo 0,907) · después del Mundial 0,585 · Colombia tras el Mundial **75** uds (real 49; media móvil 3.990) ·
holdout top h=1…4 **0,696** (ingenuo 0,476) · h=1…6 0,652 con sesgo +19 % · total semanal **0,110** (ingenuo 0,170) · cobertura del intervalo 92 %.

## 4. El *bundle* de `app/data/`

42 parquet (zstd, sin índice), agrupados por página del plan §3. El detalle de cada columna y tipo está en **`app/data/ESQUEMA.md`** (generado).

| Página | Archivos |
|---|---|
| Inicio | `cifras_clave.json` (`kpi`) |
| 1 Problema y datos | `cuadre_cifras_control`, `reglas_limpieza` |
| 2 Exploración | `serie_semanal_canal`, `demanda_diaria_canal` (fecha × canal), `clasificacion_catalogos`, `pareto_catalogos`, `estabilidad_mezcla_top`, `mezcla_talla_top_mes` |
| 3 Mundial | `base_evento_top`, `base_evento_agregado` (línea / familia / total), `incremental_mundial_top`, `incremental_mundial_linea`, `sensibilidad_base_evento`, `comparacion_rutas`, `calendario_semanal` |
| 4 Segmentación | `perfil_clusters`, `maestro_catalogos` |
| 5 Modelos | `metricas_validacion_s5` (escalera), `metricas_backtesting`, `wape_por_origen_backtesting`, `wape_por_horizonte_backtesting`, `backtesting_total_top`, `backtesting_colombia`, `metricas_holdout`, `diagnostico_holdout`, `holdout_predicciones_top`, `holdout_total_semanal`, `intervalos_holdout`, `evaluacion_intervalos`, `cobertura_por_horizonte`, `calibracion_intervalos`, `metricas_por_segmento`, `error_por_catalogo_holdout`, `importancia_permutacion`, `cola_estado_catalogos` |
| 6 Plan de producción | `pronostico_catalogo`, `pronostico_talla_color`, `pronostico_tela`, `revision_vs_ingenuo`, `historia_semanal_catalogo` |
| 7 Guía | `diccionario_variables`, `indice_figuras` (+ los `.md` de `docs/`) |

`cifras_clave.json`: `kpi` (números sin formato), `h3`…`h8` (las cifras que imprimen las celdas de hallazgos), `correccion_early_stopping`
(antes / ahora), `constantes` (Mundial, ventana, holdout, cortes del backtesting, top, partidos de Colombia, umbrales, meses en español),
`paleta` (Okabe-Ito, `COLOR_CANAL`, `COLOR_FAMILIA`, `COLOR_EVENTO`, `ESTILO_MODELO`, color del pronóstico y del ingenuo) y `metadata_modelo`.

Nada a nivel de línea de pedido: el grano más fino es catálogo × semana (o fecha × canal en la demanda diaria total).

## 5. ⚠️ Lo que el agente 07 (app Streamlit) tiene que saber

1. **Fuente única de cifras:** `app/data/cifras_clave.json` → `kpi`. Son números crudos (p. ej. `pct_unidades_top = 0.7696`, `colombia_post_mundial.HGB_redondeo = 75.25`):
   **formatéenlos en la app** (es-CO: punto de miles, coma decimal, `round`). No muestren tal cual los textos de `h3`…`h7`: algunos traen formato
   inglés (`"71.5% / 76.9%"`) o tuplas; sirven como referencia, no como texto final.
2. **KPI de Inicio** (plan §3): 29.919 uds = `kpi.unidades_totales` (incluye canceladas, cifra de control); 806 catálogos = `kpi.catalogos_con_venta`
   (crudos; normalizados = 798, en el panel 792); 9 meses = `kpi.meses_historia`; top 20 = 77 % = `kpi.pct_unidades_top`; +6.582 uds = `kpi.uds_evento_colombia`.
   Titular P3: `kpi.colombia_post_mundial` (`real` 49, `HGB_redondeo` 75, `media_movil_4` 3.990).
3. **Columnas limpias:** `%` → `pct`, `|`/espacios/`=`/`…` → `_`. Ej.: `metricas_holdout.top_h_1_4_WAPE`, `total_semanal_h_1_6_WAPE`,
   `error_por_catalogo_holdout.WAPE_HGB_redondeo`, `incremental_mundial_top.pct_evento_sobre_real`. Consulten `ESQUEMA.md` antes de escribir cada página.
4. **Tipos:** se escribieron con pandas 3 → texto como `str`, fechas `datetime64[us]`. Con pandas 2 + pyarrow se leen igual (texto como `object`).
   Para Streamlit Cloud con Python 3.12, pandas 3.x funciona; si fijan pandas 2.2, prueben `pd.read_parquet` en un venv limpio.
5. **`pronostico_catalogo`** (página 6): `pred` es lo publicado (modelo en el top, ingenuo en la cola). `lo`/`hi` solo existen en el top (NaN en la cola).
   `h` 1–4 = horizonte principal; 5–8 = extendido (márquenlo distinto). `revisar` está todo en `False` en esta corrida: el filtro / la bandera debe
   funcionar igual con lista vacía. **El intervalo no se suma entre catálogos** (para el total del top muestren solo la línea).
6. **Historia para la página 6:** `historia_semanal_catalogo` (catálogo, semana, `y`, segmento) cubre los 792 catálogos del panel, 12-ene → 28-sep,
   con ceros desde la primera venta. Unan con `pronostico_catalogo` por `catalogo`.
7. **Ajuste experto** (slider): aplíquenlo sobre `pred` en memoria y propáguenlo a talla × color multiplicando `pred_tc` por el mismo factor por catálogo/semana
   (la desagregación es proporcional) y a tela con `pronostico_tela` solo si el ajuste es global (la tabla de tela ya viene sumada sobre catálogos).
8. **Nombres de catálogo:** `clasificacion_catalogos` usa los nombres **crudos** de §3 (798 filas); el resto usa los **normalizados** de §4. No los unan por nombre sin cuidado.
9. **Bandas del Mundial:** `constantes.mundial` = 11-jun → 19-jul; `constantes.ventana_evento` = 25-may → 13-jul. `calendario_semanal` tiene las dummies por semana.
10. **Caso Honda (página 5):** `diagnostico_holdout` (con y sin el peor catálogo) + `holdout_predicciones_top` filtrado a `CUELLO ALTO HONDA REFLECTIVO`.
    El titular P3 se puede reconstruir con `backtesting_colombia` filtrando `fase_origen == "después del evento"` y sumando (`y` = 49, `pred` del final = 75,3).
11. **Recuadro de la corrección de `early_stopping`:** `cifras_clave.json` → `correccion_early_stopping.antes` (valores del reporte 04, ya no vigentes) y `.ahora`.
12. **Figuras de respaldo:** `app/data/figuras/*.png` (P1–P4 del póster y 12 del notebook). Úsenlas solo si una gráfica plotly no está lista.
13. **No carguen el modelo en la app:** el `.joblib` exige scikit-learn 1.9.1 y no hace falta. Todo está precalculado.
14. **Regenerar el bundle:** *Run all* del notebook (o, con las variables en memoria, `exportar_bundle_app()`). Borra y reescribe los `.parquet` de `app/data/`;
    **no guarden archivos propios dentro de `app/data/`** con extensión `.parquet`.
15. **`docs/guia_generar_pronostico.md`, `docs/model_card.md` y `docs/registro_decisiones.md`** son el contenido de la página 7; `diccionario_variables.parquet`
    tiene el diccionario con buscador.

## 6. Fallos conocidos y pendientes

- **Nombres duplicados en el top** (reporte 05): "CUELLO ALTO RED BULL" / "RED BULL" y "CA COLOMBIA ÉLITE" / "COLOMBIA ELITE/CLASICO". No se tocaron.
- **plotly** sigue fuera de `requirements.txt` del notebook: es dependencia de la app (`app/requirements.txt`, agente 07).
- La **guía** describe un flujo con el notebook completo (~20 min). No hay un script independiente de pronóstico; si Klixmant lo necesita, `cargar_modelo()` y
  `generar_pronostico()` son la base, pero dependen de las funciones de §4–§6.
- El calendario del modelo llega al **30-nov-2026**: para pronosticar diciembre hay que extenderlo (guía §3.3).

## 7. Decisiones que el grupo debería revisar

- **Entrenar el modelo final con el holdout incluido** (corte 28-sep): es lo habitual antes de producción, pero díganlo en el texto.
- **Reentrenar mensualmente** y los umbrales de alarma de la *model card* §6 (sesgo ±30 %, WAPE total > 0,25) son de criterio.
- **Qué datos ve la app:** el bundle es agregado, pero sigue siendo información de Klixmant. Restrinjan los visores en Streamlit Cloud (agente 08).
- **Textos:** todo el markdown de §8 y los tres documentos de `docs/` son borradores técnicos. **Redáctenlos con palabras propias** (riesgo Turnitin).

## 8. Reproducir la ejecución

```bash
C:\Users\diani\.venvs\klixmant\Scripts\python.exe -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=3600 Klixmant_Pronostico_Demanda.ipynb
```

O *Run all* desde la celda 0 con ese venv (o uno nuevo con `requirements.txt`).
