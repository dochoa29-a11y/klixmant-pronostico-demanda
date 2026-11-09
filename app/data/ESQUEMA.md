# Esquema del bundle de datos de la app (`app/data/`)

Generado por `exportar_bundle_app()` (notebook §8.4) el 2026-11-09 17:01. **No editar a mano:** se regenera con *Run all*.
Corte de datos: 2026-10-06 · última semana completa: 2026-09-28 · modelo: HGB_sin_atipico (300 iteraciones). Tamaño total: 3.0 MB.

- Todas las tablas son parquet (zstd), sin índice. Fechas como `datetime64`; texto como `string`.
- Los nombres de columna se limpiaron: `%` → `pct`, `|`, espacios, `=` y `…` → `_` (p. ej. `top h=1…4 | WAPE` → `top_h_1_4_WAPE`).
- Página = número de la página de la app en `docs/PLAN_DESPLIEGUE_STREAMLIT.md` §3 (1–7).
- Las cifras sueltas (KPI, titulares, paleta, constantes) están en `cifras_clave.json` (claves `kpi`, `h3`…`h8`, `correccion_early_stopping`, `constantes`, `paleta`, `metadata_modelo`).
- `figuras/` trae 16 PNG del notebook como respaldo estático.

## Inventario

| Archivo | Página | Filas | KB |
|---|---|---|---|
| `cuadre_cifras_control.parquet` | 1 | 12 | 4 |
| `reglas_limpieza.parquet` | 1 | 7 | 3 |
| `serie_semanal_canal.parquet` | 2 | 39 | 4 |
| `demanda_diaria_canal.parquet` | 2 | 513 | 5 |
| `clasificacion_catalogos.parquet` | 2 | 798 | 25 |
| `pareto_catalogos.parquet` | 2 | 792 | 19 |
| `estabilidad_mezcla_top.parquet` | 2 | 20 | 6 |
| `mezcla_talla_top_mes.parquet` | 2 | 932 | 5 |
| `base_evento_top.parquet` | 3 | 669 | 10 |
| `base_evento_agregado.parquet` | 3 | 341 | 6 |
| `incremental_mundial_top.parquet` | 3 | 20 | 7 |
| `incremental_mundial_linea.parquet` | 3 | 6 | 5 |
| `sensibilidad_base_evento.parquet` | 3 | 9 | 4 |
| `comparacion_rutas.parquet` | 3 | 4 | 5 |
| `calendario_semanal.parquet` | 3 | 47 | 10 |
| `perfil_clusters.parquet` | 4 | 84 | 15 |
| `maestro_catalogos.parquet` | 4 | 798 | 25 |
| `metricas_validacion_s5.parquet` | 5 | 14 | 9 |
| `metricas_backtesting.parquet` | 5 | 8 | 13 |
| `wape_por_origen_backtesting.parquet` | 5 | 15 | 7 |
| `wape_por_horizonte_backtesting.parquet` | 5 | 32 | 5 |
| `backtesting_total_top.parquet` | 5 | 480 | 8 |
| `backtesting_colombia.parquet` | 5 | 480 | 7 |
| `metricas_holdout.parquet` | 5 | 8 | 12 |
| `diagnostico_holdout.parquet` | 5 | 8 | 5 |
| `holdout_predicciones_top.parquet` | 5 | 960 | 10 |
| `holdout_total_semanal.parquet` | 5 | 144 | 4 |
| `intervalos_holdout.parquet` | 5 | 120 | 7 |
| `evaluacion_intervalos.parquet` | 5 | 4 | 4 |
| `cobertura_por_horizonte.parquet` | 5 | 6 | 3 |
| `calibracion_intervalos.parquet` | 5 | 8 | 3 |
| `metricas_por_segmento.parquet` | 5 | 84 | 10 |
| `error_por_catalogo_holdout.parquet` | 5 | 20 | 9 |
| `importancia_permutacion.parquet` | 5 | 37 | 3 |
| `comparacion_modelo_inicial.parquet` | 5 | 18 | 6 |
| `cola_estado_catalogos.parquet` | 5 | 16 | 5 |
| `pronostico_catalogo.parquet` | 6 | 6,336 | 33 |
| `pronostico_talla_color.parquet` | 6 | 4,824 | 37 |
| `pronostico_tela.parquet` | 6 | 960 | 6 |
| `revision_vs_ingenuo.parquet` | 6 | 20 | 5 |
| `historia_semanal_catalogo.parquet` | 6 | 17,722 | 14 |
| `diccionario_variables.parquet` | 7 | 53 | 6 |
| `indice_figuras.parquet` | 7 | 38 | 4 |

## Columnas por archivo

### `cuadre_cifras_control.parquet`

Cuadre de las 12 cifras globales contra la documentación de Klixmant (§3.1). **Grano:** cifra. **Página:** 1. **Filas:** 12.

| Columna | Tipo | Descripción |
|---|---|---|
| `cifra` | str |  |
| `esperado` | int64 |  |
| `obtenido` | int64 |  |
| `diferencia` | int64 |  |
| `cuadra` | str |  |

### `reglas_limpieza.parquet`

Reglas de limpieza aplicadas en §4.1 con líneas y unidades afectadas. **Grano:** regla. **Página:** 1. **Filas:** 7.

| Columna | Tipo | Descripción |
|---|---|---|
| `regla` | str |  |
| `lineas` | int64 |  |
| `unidades` | int64 | Unidades vendidas |
| `decision` | str |  |

### `serie_semanal_canal.parquet`

Unidades por semana y canal (incluye la semana parcial, marcada). **Grano:** semana. **Página:** 2. **Filas:** 39.

| Columna | Tipo | Descripción |
|---|---|---|
| `semana` | datetime64 | Lunes de la semana (W-MON) |
| `DROPI` | float64 |  |
| `EFFI` | float64 |  |
| `TOTAL` | float64 |  |
| `parcial` | bool |  |

### `demanda_diaria_canal.parquet`

Unidades por día y canal (heatmap día × semana, % Dropi). **Grano:** fecha × canal. **Página:** 2. **Filas:** 513.

| Columna | Tipo | Descripción |
|---|---|---|
| `fecha` | datetime64 | Día de remisión |
| `canal` | str | EFFI o DROPI |
| `cantidad_total` | int64 | Unidades |

### `clasificacion_catalogos.parquet`

ADI/CV², ABC, ciclo de vida por catálogo (nombres sin normalizar, §3). **Grano:** catálogo. **Página:** 2. **Filas:** 798.

| Columna | Tipo | Descripción |
|---|---|---|
| `catalogo` | str | Nombre del catálogo (normalizado en §4.1 salvo donde se indica) |
| `semanas_activo` | int64 |  |
| `semanas_con_venta` | int64 |  |
| `ADI` | float64 |  |
| `CV2` | float64 |  |
| `tipo` | str |  |
| `unidades` | int64 | Unidades vendidas |
| `rank` | int64 | Puesto por unidades |
| `clase_abc` | str |  |
| `metodo_sugerido` | str |  |
| `primera` | datetime64 |  |
| `ultima` | datetime64 |  |
| `semanas_vida` | int64 |  |
| `estado` | str |  |
| `familia` | str | COLOMBIA (catálogos de la Selección) o RESTO |

### `pareto_catalogos.parquet`

Curva de Pareto con los catálogos normalizados de §4 (semanas completas). **Grano:** catálogo. **Página:** 2. **Filas:** 792.

| Columna | Tipo | Descripción |
|---|---|---|
| `catalogo` | str | Nombre del catálogo (normalizado en §4.1 salvo donde se indica) |
| `rank` | int64 | Puesto por unidades |
| `unidades` | int64 | Unidades vendidas |
| `pct_acum` | float64 | % acumulado de unidades |
| `top` | bool | True si está en el top 20 |
| `familia` | str | COLOMBIA (catálogos de la Selección) o RESTO |
| `linea` | str | Línea de producto (regex §4.2.1) |

### `estabilidad_mezcla_top.parquet`

Estabilidad de la mezcla de talla y color en el top (distancia TV). **Grano:** catálogo top. **Página:** 2. **Filas:** 20.

| Columna | Tipo | Descripción |
|---|---|---|
| `catalogo` | str | Nombre del catálogo (normalizado en §4.1 salvo donde se indica) |
| `unidades` | int64 | Unidades vendidas |
| `tallas` | int64 |  |
| `colores` | int64 |  |
| `combos_talla_color` | int64 |  |
| `meses_evaluados` | int64 |  |
| `TV_talla` | float64 |  |
| `TV_color` | float64 |  |

### `mezcla_talla_top_mes.parquet`

Unidades por catálogo del top × mes × talla (mezcla de tallas). **Grano:** catálogo top × mes × talla. **Página:** 2. **Filas:** 932.

| Columna | Tipo | Descripción |
|---|---|---|
| `catalogo` | str | Nombre del catálogo (normalizado en §4.1 salvo donde se indica) |
| `mes` | datetime64 |  |
| `talla_std` | str | Talla estandarizada |
| `cantidad_total` | int64 | Unidades |

### `base_evento_top.parquet`

Base vs evento (ruta 1) por catálogo del top y semana. **Grano:** catálogo top × semana. **Página:** 3. **Filas:** 669.

| Columna | Tipo | Descripción |
|---|---|---|
| `catalogo` | str | Nombre del catálogo (normalizado en §4.1 salvo donde se indica) |
| `semana` | datetime64 | Lunes de la semana (W-MON) |
| `y` | float64 | Unidades reales de la semana |
| `y_base` | float64 | Demanda base (ruta 1: interpolación entre medianas) |
| `y_evento` | float64 | Demanda de evento = y − y_base |
| `familia` | str | COLOMBIA (catálogos de la Selección) o RESTO |
| `linea` | str | Línea de producto (regex §4.2.1) |
| `rank` | int64 | Puesto por unidades |
| `top_n` | bool |  |
| `cluster` | str | Grupo K-means (evento, base, en declive, base errática, cola) |

### `base_evento_agregado.parquet`

Base vs evento sumado por línea, por familia y total. **Grano:** nivel × grupo × semana. **Página:** 3. **Filas:** 341.

| Columna | Tipo | Descripción |
|---|---|---|
| `nivel` | str |  |
| `grupo` | str |  |
| `semana` | datetime64 | Lunes de la semana (W-MON) |
| `y` | float64 | Unidades reales de la semana |
| `y_base` | float64 | Demanda base (ruta 1: interpolación entre medianas) |
| `y_evento` | float64 | Demanda de evento = y − y_base |

### `incremental_mundial_top.parquet`

Unidades de evento netas / positivas / desplazadas por catálogo del top. **Grano:** catálogo top. **Página:** 3. **Filas:** 20.

| Columna | Tipo | Descripción |
|---|---|---|
| `catalogo` | str | Nombre del catálogo (normalizado en §4.1 salvo donde se indica) |
| `uds_reales` | float64 | Unidades reales |
| `uds_base` | float64 |  |
| `uds_evento_neto` | float64 |  |
| `uds_evento_positivo` | float64 |  |
| `uds_desplazadas` | float64 |  |
| `pct_evento_sobre_real` | float64 |  |
| `rank` | int64 | Puesto por unidades |
| `familia` | str | COLOMBIA (catálogos de la Selección) o RESTO |
| `cluster` | str | Grupo K-means (evento, base, en declive, base errática, cola) |

### `incremental_mundial_linea.parquet`

Unidades de evento por línea de producto. **Grano:** línea. **Página:** 3. **Filas:** 6.

| Columna | Tipo | Descripción |
|---|---|---|
| `linea` | str | Línea de producto (regex §4.2.1) |
| `uds_reales` | float64 | Unidades reales |
| `uds_base` | float64 |  |
| `uds_evento_neto` | float64 |  |
| `uds_evento_positivo` | float64 |  |
| `uds_desplazadas` | float64 |  |
| `pct_evento_sobre_real` | float64 |  |

### `sensibilidad_base_evento.parquet`

Evento estimado al variar semanas previas y k del nivel. **Grano:** escenario. **Página:** 3. **Filas:** 9.

| Columna | Tipo | Descripción |
|---|---|---|
| `semanas_pre` | int64 |  |
| `k_nivel` | int64 |  |
| `evento_COLOMBIA` | float64 |  |
| `evento_RESTO` | float64 |  |
| `pct_evento_COLOMBIA` | float64 |  |

### `comparacion_rutas.parquet`

Base/evento: ruta 1 (interpolación) vs ruta 2 (modelo). **Grano:** grupo × familia. **Página:** 3. **Filas:** 4.

| Columna | Tipo | Descripción |
|---|---|---|
| `grupo` | str |  |
| `familia` | str | COLOMBIA (catálogos de la Selección) o RESTO |
| `uds_reales` | float64 | Unidades reales |
| `base_ruta1` | float64 |  |
| `evento_ruta1` | float64 |  |
| `pron_con_evento` | float64 |  |
| `base_ruta2` | float64 |  |
| `evento_ruta2` | float64 |  |

### `calendario_semanal.parquet`

Calendario del modelo (Mundial, festivos, fechas comerciales) hasta el fin del horizonte. **Grano:** semana. **Página:** 3. **Filas:** 47.

| Columna | Tipo | Descripción |
|---|---|---|
| `semana` | datetime64 | Lunes de la semana (W-MON) |
| `n_festivos` | int64 |  |
| `dias_mundial` | int64 |  |
| `n_partidos_colombia` | int64 |  |
| `fecha_comercial` | int64 |  |
| `quincena` | int64 |  |
| `prima` | int64 |  |
| `con_historia` | int64 |  |
| `semana_mundial` | int64 |  |
| `pre_mundial` | int64 |  |
| `colombia_en_torneo` | int64 |  |
| `ventana_evento` | int64 |  |
| `semanas_desde_fin_mundial` | int64 |  |
| `semana_anio` | int64 |  |
| `mes` | int32 |  |

### `perfil_clusters.parquet`

Indicadores del perfil y clúster K-means (catálogos elegibles). **Grano:** catálogo elegible. **Página:** 4. **Filas:** 84.

| Columna | Tipo | Descripción |
|---|---|---|
| `catalogo` | str | Nombre del catálogo (normalizado en §4.1 salvo donde se indica) |
| `int_antes` | float64 |  |
| `int_evento` | float64 |  |
| `int_despues` | float64 |  |
| `semanas_activo` | int64 |  |
| `semanas_con_venta` | int64 |  |
| `unidades` | float64 | Unidades vendidas |
| `ADI` | float64 |  |
| `CV2` | float64 |  |
| `tendencia_8s` | float64 |  |
| `pct_dropi` | float64 |  |
| `elegible` | bool |  |
| `log_ADI` | float64 |  |
| `cluster_id` | int32 |  |
| `cluster` | str | Grupo K-means (evento, base, en declive, base errática, cola) |

### `maestro_catalogos.parquet`

Ficha maestra de catálogos normalizados (atributos estáticos y clúster). **Grano:** catálogo. **Página:** 4. **Filas:** 798.

| Columna | Tipo | Descripción |
|---|---|---|
| `catalogo` | str | Nombre del catálogo (normalizado en §4.1 salvo donde se indica) |
| `unidades` | int64 | Unidades vendidas |
| `rank` | int64 | Puesto por unidades |
| `clase_abc` | str |  |
| `top_n` | bool |  |
| `familia` | str | COLOMBIA (catálogos de la Selección) o RESTO |
| `linea` | str | Línea de producto (regex §4.2.1) |
| `tipo_prenda` | str |  |
| `tela_principal` | str |  |
| `n_telas` | int64 |  |
| `pct_dama` | float64 |  |
| `tipo_proceso` | str |  |
| `reflectivo` | int64 |  |
| `personalizado` | int64 |  |
| `tiene_ficha` | int64 |  |
| `cluster` | str | Grupo K-means (evento, base, en declive, base errática, cola) |
| `primera_venta` | datetime64 |  |
| `ultima_venta` | datetime64 |  |

### `metricas_validacion_s5.parquet`

Escalera de modelos de §5 (6 orígenes, validación preliminar). **Grano:** modelo. **Página:** 5. **Filas:** 14.

| Columna | Tipo | Descripción |
|---|---|---|
| `modelo` | str | Nombre del modelo |
| `nivel` | str |  |
| `WAPE_top` | float64 |  |
| `sesgo_top` | float64 |  |
| `MASE_top` | float64 |  |
| `WAPE_top_post` | float64 |  |
| `uds_Colombia_post_real` | int64 |  |
| `uds_Colombia_post_pron` | float64 |  |
| `WAPE_cola` | float64 |  |
| `WAPE_cola_agregada` | float64 |  |
| `skill_MASE_vs_ingenuo` | float64 |  |
| `segundos_por_origen` | float64 |  |

### `metricas_backtesting.parquet`

Backtesting de 15 orígenes (top 20): WAPE, sesgo, MASE, RMSSE, por fase, vs ingenuo. **Grano:** modelo. **Página:** 5. **Filas:** 8.

| Columna | Tipo | Descripción |
|---|---|---|
| `modelo` | str | Nombre del modelo |
| `nivel` | str |  |
| `WAPE_top` | float64 |  |
| `sesgo_top` | float64 |  |
| `MASE_top` | float64 |  |
| `RMSSE_top` | float64 |  |
| `WAPE_top_antes` | float64 |  |
| `WAPE_top_evento` | float64 |  |
| `WAPE_top_post` | float64 |  |
| `uds_Colombia_post_real` | int64 |  |
| `uds_Colombia_post_pron` | float64 |  |
| `origenes_gana_al_ingenuo` | int64 |  |
| `skill_WAPE_vs_ingenuo` | float64 |  |
| `skill_MASE_vs_ingenuo` | float64 |  |
| `dif_WAPE_vs_ingenuo_IC90` | str |  |
| `prob_gana_bootstrap` | float64 |  |
| `WAPE_cola` | float64 |  |
| `WAPE_cola_agregada` | float64 |  |

### `wape_por_origen_backtesting.parquet`

WAPE del top por origen del backtesting y fase. **Grano:** origen. **Página:** 5. **Filas:** 15.

| Columna | Tipo | Descripción |
|---|---|---|
| `corte` | datetime64 | Última semana observada antes de pronosticar |
| `fase` | str |  |
| `HGB_ingenuo` | float64 |  |
| `HGB_redondeo` | float64 |  |
| `HGB_poisson` | float64 |  |
| `HGB_sin_atipico` | float64 |  |
| `ingenuo` | float64 |  |
| `ETS` | float64 |  |
| `SARIMAX` | float64 |  |
| `media_movil_4` | float64 |  |

### `wape_por_horizonte_backtesting.parquet`

WAPE y sesgo del top por horizonte (backtesting). **Grano:** modelo × h. **Página:** 5. **Filas:** 32.

| Columna | Tipo | Descripción |
|---|---|---|
| `modelo` | str | Nombre del modelo |
| `h` | int64 | Semanas hacia adelante (1 = primera semana pronosticada) |
| `WAPE` | float64 | Σ|error| / Σ real |
| `sesgo` | float64 | Σ error / Σ real (+ = sobrepronóstico) |
| `uds_reales` | int64 | Unidades reales |
| `uds_pronosticadas` | float64 | Unidades pronosticadas |

### `backtesting_total_top.parquet`

Real vs pronóstico del total del top por modelo, origen y semana (backtesting). **Grano:** modelo × origen × semana. **Página:** 5. **Filas:** 480.

| Columna | Tipo | Descripción |
|---|---|---|
| `modelo` | str | Nombre del modelo |
| `corte` | datetime64 | Última semana observada antes de pronosticar |
| `semana` | datetime64 | Lunes de la semana (W-MON) |
| `h` | int64 | Semanas hacia adelante (1 = primera semana pronosticada) |
| `y` | int64 | Unidades reales de la semana |
| `pred` | float64 | Unidades pronosticadas (publicadas) |
| `fase_origen` | str | antes del evento / toca el evento / después del evento |

### `backtesting_colombia.parquet`

Real vs pronóstico de la familia Colombia del top (base del titular P3). **Grano:** modelo × origen × semana. **Página:** 5. **Filas:** 480.

| Columna | Tipo | Descripción |
|---|---|---|
| `modelo` | str | Nombre del modelo |
| `corte` | datetime64 | Última semana observada antes de pronosticar |
| `semana` | datetime64 | Lunes de la semana (W-MON) |
| `y` | int64 | Unidades reales de la semana |
| `pred` | float64 | Unidades pronosticadas (publicadas) |
| `fase_origen` | str | antes del evento / toca el evento / después del evento |

### `metricas_holdout.parquet`

Holdout (24-ago → 28-sep): top h=1…4, h=1…6, cola y total semanal. **Grano:** modelo. **Página:** 5. **Filas:** 8.

| Columna | Tipo | Descripción |
|---|---|---|
| `modelo` | str | Nombre del modelo |
| `top_h_1_4_WAPE` | float64 |  |
| `top_h_1_4_sesgo` | float64 |  |
| `top_h_1_4_MASE` | float64 |  |
| `top_h_1_4_RMSSE` | float64 |  |
| `top_h_1_4_uds_reales` | int64 |  |
| `top_h_1_4_uds_pronosticadas` | float64 |  |
| `top_h_1_6_WAPE` | float64 |  |
| `top_h_1_6_sesgo` | float64 |  |
| `top_h_1_6_MASE` | float64 |  |
| `top_h_1_6_RMSSE` | float64 |  |
| `top_h_1_6_uds_reales` | int64 |  |
| `top_h_1_6_uds_pronosticadas` | float64 |  |
| `cola_h_1_6_WAPE_catalogo` | float64 |  |
| `cola_h_1_6_WAPE_agregada` | float64 |  |
| `total_semanal_h_1_6_WAPE` | float64 |  |
| `total_semanal_h_1_6_sesgo` | float64 |  |

### `diagnostico_holdout.parquet`

Holdout con y sin el catálogo de mayor exceso (CUELLO ALTO MERCEDES). **Grano:** modelo. **Página:** 5. **Filas:** 8.

| Columna | Tipo | Descripción |
|---|---|---|
| `modelo` | str | Nombre del modelo |
| `WAPE_top` | float64 |  |
| `sesgo_top` | float64 |  |
| `WAPE_top_sin_peor` | float64 |  |
| `sesgo_top_sin_peor` | float64 |  |
| `exceso_uds_peor` | float64 |  |
| `exceso_uds_top` | float64 |  |

### `holdout_predicciones_top.parquet`

Predicciones del holdout para el top, todos los modelos. **Grano:** modelo × catálogo top × semana. **Página:** 5. **Filas:** 960.

| Columna | Tipo | Descripción |
|---|---|---|
| `modelo` | str | Nombre del modelo |
| `catalogo` | str | Nombre del catálogo (normalizado en §4.1 salvo donde se indica) |
| `semana` | datetime64 | Lunes de la semana (W-MON) |
| `h` | int64 | Semanas hacia adelante (1 = primera semana pronosticada) |
| `y` | int64 | Unidades reales de la semana |
| `pred` | float64 | Unidades pronosticadas (publicadas) |
| `familia` | str | COLOMBIA (catálogos de la Selección) o RESTO |

### `holdout_total_semanal.parquet`

Holdout sumado por semana: total, top y cola, por modelo. **Grano:** modelo × segmento × semana. **Página:** 5. **Filas:** 144.

| Columna | Tipo | Descripción |
|---|---|---|
| `modelo` | str | Nombre del modelo |
| `semana` | datetime64 | Lunes de la semana (W-MON) |
| `y` | int64 | Unidades reales de la semana |
| `pred` | float64 | Unidades pronosticadas (publicadas) |
| `segmento` | str | top (20 catálogos modelados) o cola (regla ingenua) |

### `intervalos_holdout.parquet`

Intervalo 10–90 % calibrado del modelo final en el holdout. **Grano:** catálogo top × semana. **Página:** 5. **Filas:** 120.

| Columna | Tipo | Descripción |
|---|---|---|
| `catalogo` | str | Nombre del catálogo (normalizado en §4.1 salvo donde se indica) |
| `semana` | datetime64 | Lunes de la semana (W-MON) |
| `h` | int64 | Semanas hacia adelante (1 = primera semana pronosticada) |
| `y` | int64 | Unidades reales de la semana |
| `pred` | float64 | Unidades pronosticadas (publicadas) |
| `lo` | float64 | Límite inferior del intervalo 10–90 % (solo top) |
| `hi` | float64 | Límite superior del intervalo 10–90 % (solo top) |

### `evaluacion_intervalos.parquet`

Cobertura, ancho y pinball de cada método de intervalo. **Grano:** método. **Página:** 5. **Filas:** 4.

| Columna | Tipo | Descripción |
|---|---|---|
| `metodo` | str |  |
| `cobertura_80` | float64 |  |
| `ancho_medio` | float64 |  |
| `pinball_q10` | float64 |  |
| `pinball_q90` | float64 |  |
| `n` | float64 |  |

### `cobertura_por_horizonte.parquet`

Cobertura del intervalo por horizonte en el holdout. **Grano:** h. **Página:** 5. **Filas:** 6.

| Columna | Tipo | Descripción |
|---|---|---|
| `h` | int64 | Semanas hacia adelante (1 = primera semana pronosticada) |
| `5_6_sin_calibrar` | float64 |  |
| `conformal_todos_los_orígenes` | float64 |  |
| `conformal_semanas_fuera_del_evento` | float64 |  |

### `calibracion_intervalos.parquet`

Factores z10 / z90 por horizonte. **Grano:** calibración × h. **Página:** 5. **Filas:** 8.

| Columna | Tipo | Descripción |
|---|---|---|
| `calibracion` | str |  |
| `h` | int64 | Semanas hacia adelante (1 = primera semana pronosticada) |
| `z10` | float64 |  |
| `z90` | float64 |  |

### `metricas_por_segmento.parquet`

Métricas por segmento, familia, periodo y horizonte (backtesting y holdout). **Grano:** fuente × dimensión × grupo × modelo. **Página:** 5. **Filas:** 84.

| Columna | Tipo | Descripción |
|---|---|---|
| `modelo` | str | Nombre del modelo |
| `grupo` | str |  |
| `WAPE` | float64 | Σ|error| / Σ real |
| `sesgo` | float64 | Σ error / Σ real (+ = sobrepronóstico) |
| `MAE` | float64 | Error absoluto medio (uds) |
| `uds_reales` | int64 | Unidades reales |
| `uds_pronosticadas` | float64 | Unidades pronosticadas |
| `n` | int64 |  |
| `MASE` | float64 | Error absoluto escalado por el ingenuo de 1 semana |
| `fuente` | str |  |
| `dimension` | str |  |

### `error_por_catalogo_holdout.parquet`

Error del final vs ingenuo por catálogo del top en el holdout. **Grano:** catálogo top. **Página:** 5. **Filas:** 20.

| Columna | Tipo | Descripción |
|---|---|---|
| `catalogo` | str | Nombre del catálogo (normalizado en §4.1 salvo donde se indica) |
| `uds_reales_HGB_sin_atipico` | int64 |  |
| `uds_reales_ingenuo` | int64 |  |
| `uds_pron_HGB_sin_atipico` | float64 |  |
| `uds_pron_ingenuo` | float64 |  |
| `WAPE_HGB_sin_atipico` | float64 |  |
| `WAPE_ingenuo` | float64 |  |
| `sesgo_HGB_sin_atipico` | float64 |  |
| `sesgo_ingenuo` | float64 |  |
| `rank` | int64 | Puesto por unidades |
| `familia` | str | COLOMBIA (catálogos de la Selección) o RESTO |

### `importancia_permutacion.parquet`

Importancia por permutación (aumento del MAE). **Grano:** variable. **Página:** 5. **Filas:** 37.

| Columna | Tipo | Descripción |
|---|---|---|
| `variable` | str |  |
| `aumento_MAE` | float64 |  |
| `desv` | float64 |  |

### `comparacion_modelo_inicial.parquet`

Comparación con el modelo inicial del curso a nivel SKU (§6.11): mismas métricas, paso a paso. **Grano:** panel × paso. **Página:** 5. **Filas:** 18.

| Columna | Tipo | Descripción |
|---|---|---|
| `panel` | str | Unidad y semanas usadas |
| `paso` | str | Paso de la comparación (§6.11) |
| `modelo` | str | Nombre del modelo |
| `MAE` | float64 | Error absoluto medio (uds) |
| `RMSE` | float64 | Raíz del error cuadrático medio (uds) |
| `MAPE_con_venta` | float64 | MAPE solo en las filas con venta (métrica del modelo inicial) |
| `WAPE` | float64 | Σ|error| / Σ real |
| `sesgo` | float64 | Σ error / Σ real (+ = sobrepronóstico) |

### `cola_estado_catalogos.parquet`

Venta de la cola por estado del catálogo en el origen. **Grano:** origen. **Página:** 5. **Filas:** 16.

| Columna | Tipo | Descripción |
|---|---|---|
| `origen` | str |  |
| `activo` | int64 |  |
| `dormido` | int64 |  |
| `nuevo` | int64 |  |
| `total` | int64 |  |
| `pct_dormido` | float64 |  |
| `pct_nuevo` | float64 |  |

### `pronostico_catalogo.parquet`

Pronóstico oficial (§8.2): catálogo × semana, con ingenuo, intervalo y bandera revisar. **Grano:** catálogo × semana. **Página:** 6. **Filas:** 6,336.

| Columna | Tipo | Descripción |
|---|---|---|
| `corte` | datetime64 | Última semana observada antes de pronosticar |
| `catalogo` | str | Nombre del catálogo (normalizado en §4.1 salvo donde se indica) |
| `segmento` | str | top (20 catálogos modelados) o cola (regla ingenua) |
| `semana` | datetime64 | Lunes de la semana (W-MON) |
| `h` | int64 | Semanas hacia adelante (1 = primera semana pronosticada) |
| `pred` | float64 | Unidades pronosticadas (publicadas) |
| `pred_modelo` | float64 | Pronóstico del modelo final (HGB) |
| `pred_ingenuo` | float64 | Pronóstico ingenuo (repite la última semana) |
| `lo` | float64 | Límite inferior del intervalo 10–90 % (solo top) |
| `hi` | float64 | Límite superior del intervalo 10–90 % (solo top) |
| `revisar` | bool | True si modelo e ingenuo difieren > 50 % y ≥ 10 uds en 4 semanas |

### `pronostico_talla_color.parquet`

Pronóstico del top desagregado a talla × color. **Grano:** catálogo top × semana × talla × color. **Página:** 6. **Filas:** 4,824.

| Columna | Tipo | Descripción |
|---|---|---|
| `catalogo` | str | Nombre del catálogo (normalizado en §4.1 salvo donde se indica) |
| `semana` | datetime64 | Lunes de la semana (W-MON) |
| `h` | int64 | Semanas hacia adelante (1 = primera semana pronosticada) |
| `talla_std` | str | Talla estandarizada |
| `color` | str | Color |
| `prop` | float64 | Proporción usada para repartir |
| `pred_tc` | float64 | Unidades pronosticadas en esa talla × color |

### `pronostico_tela.parquet`

Pronóstico agregado a insumo (género × tela × color), top + cola. **Grano:** semana × género × tela × color. **Página:** 6. **Filas:** 960.

| Columna | Tipo | Descripción |
|---|---|---|
| `semana` | datetime64 | Lunes de la semana (W-MON) |
| `genero` | str | H = hombre, D = dama |
| `tela` | str | Código de tela (2.º token de la referencia) |
| `color_ref` | str | Color de la referencia |
| `pred_tela` | float64 | Unidades pronosticadas que pasan por esa tela |

### `revision_vs_ingenuo.parquet`

Suma de 4 semanas modelo vs ingenuo y bandera revisar (top). **Grano:** catálogo top. **Página:** 6. **Filas:** 20.

| Columna | Tipo | Descripción |
|---|---|---|
| `catalogo` | str | Nombre del catálogo (normalizado en §4.1 salvo donde se indica) |
| `pred_modelo` | float64 | Pronóstico del modelo final (HGB) |
| `pred_ingenuo` | float64 | Pronóstico ingenuo (repite la última semana) |
| `dif_rel` | float64 |  |
| `dif_uds` | float64 |  |
| `revisar` | bool | True si modelo e ingenuo difieren > 50 % y ≥ 10 uds en 4 semanas |

### `historia_semanal_catalogo.parquet`

Venta semanal real (semanas completas, con ceros desde la primera venta) de todos los catálogos del panel. **Grano:** catálogo × semana. **Página:** 6. **Filas:** 17,722.

| Columna | Tipo | Descripción |
|---|---|---|
| `catalogo` | str | Nombre del catálogo (normalizado en §4.1 salvo donde se indica) |
| `semana` | datetime64 | Lunes de la semana (W-MON) |
| `y` | int64 | Unidades reales de la semana |
| `segmento` | str | top (20 catálogos modelados) o cola (regla ingenua) |

### `diccionario_variables.parquet`

Diccionario de variables del panel (§4.6). **Grano:** variable. **Página:** 7. **Filas:** 53.

| Columna | Tipo | Descripción |
|---|---|---|
| `variable` | str |  |
| `grupo` | str |  |
| `descripcion` | str |  |
| `ventana_temporal` | str |  |
| `uso` | str |  |

### `indice_figuras.parquet`

Índice de figuras del plan §7.2. **Grano:** archivo. **Página:** 7. **Filas:** 38.

| Columna | Tipo | Descripción |
|---|---|---|
| `fase_plan` | str |  |
| `grafica_plan` | str |  |
| `archivo` | str |  |
| `poster` | bool |  |
| `existe` | bool |  |
