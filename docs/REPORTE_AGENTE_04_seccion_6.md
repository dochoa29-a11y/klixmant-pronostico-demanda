# Reporte de traspaso — Agente 04 (sección 6)

**Fecha:** 3-nov-2026 · **Alcance:** §6 Validación y métricas (plan §6.1–§6.3): backtesting de origen móvil, selección del modelo final, holdout (abierto **una sola vez**), intervalos calibrados, desglose por segmento y análisis de la cola.
**No se hizo nada de §7 en adelante.** Las secciones 7 y 8 siguen como encabezados ⏳.
Lean también los reportes 01, 02 y 03: sus convenciones siguen vigentes.

> ⚠️ **El holdout ya se usó.** No vuelvan a elegir ni a afinar modelos mirando el holdout (24-ago → 28-sep). Cualquier ajuste nuevo (p. ej. el tope) se valida **solo con el backtesting** (`CORTES_BT`).

---

## 1. Qué se entregó

| Archivo | Qué es |
|---|---|
| `Klixmant_Pronostico_Demanda.ipynb` | §6 completa y ejecutada (celdas 108–129). La celda 0 marca §6 ✅ |
| `procesado/6_*.csv` | 12 tablas (ver §4 de este reporte) |
| `figuras/6_*.png` | 5 gráficas |

**Ejecución verificada:** notebook completo de arriba abajo con `nbconvert --execute`, sin errores (~17 min: ~13 de §0–§5 y ~4,5 de §6, casi todo el backtesting).
Mismo entorno del reporte 03 (Python 3.14.7, pandas 3.1.0, scikit-learn 1.9.1, statsmodels 0.15.0, torch 2.15.0 CPU). Aparecen avisos de convergencia de `ExponentialSmoothing` y uno de joblib al cerrar el kernel; no afectan los resultados.
Copia del notebook **antes** de §6: scratchpad del agente 04 (`notebook_antes_s6.ipynb`). Para volver atrás, borren las celdas entre "## 6." y "## 7." y restauren el encabezado "## 6. Validación y métricas — ⏳ PENDIENTE".

## 2. Estructura de §6 en el notebook

| Celda | Contenido |
|---|---|
| 6 (md) | Esquema de validación y métricas |
| 6.1 | `CORTES_BT` (15 lunes, 13-abr → 20-jul), `fase_origen()`, `m_hgb_redondeo`, `METODOS_BT`, `completar_resultados()` → **`bt`** |
| 6.2.1 | `escala_rmsse()`, `rmsse()`, `tabla_completa()` (= `tabla_metricas` + RMSSE), `bootstrap_vs()` → **`resumen_bt`**, `wape_origen_bt` |
| 6.2.2 | Gráficas: WAPE por origen y por horizonte |
| 6.3 | Regla de selección → **`MODELO_FINAL`**, **`METODO_FINAL`**, `MODELO_COLA_FINAL`, `INGENUO_EMPATA` |
| 6.4 | Holdout → **`ho`**, `resumen_ho` (top h=1…4, top h=1…6, cola, total semanal) |
| 6.4.2 | Diagnóstico del sobrepronóstico → `diag_ho`, `CATALOGO_PEOR_HO` |
| 6.5 | Intervalos conformales: `calibrar_intervalo()`, `aplicar_intervalo()`, `evaluar_intervalo()` → **`CALIBRACION_INTERVALO`**, `intervalos_ho`, `cobertura_h` |
| 6.5.2 | Gráficas: cobertura por horizonte y real vs pronóstico en el holdout |
| 6.6 | Segmentos → `segmentos`, `tabla_seg`; error por catálogo → `err_cat_ho` (+ gráfica 6.6.2) |
| 6.7 | Venta de la cola por estado del catálogo (activo / dormido / nuevo) → `cola_estados` |
| 6.8 | Exportación |
| 6.9 / 6.10 | Cifras clave (`h6`) y lectura en borrador |

### Constantes y funciones nuevas que §7–§8 deben reutilizar

| Nombre | Valor / uso |
|---|---|
| `MODELO_FINAL` | `"HGB_redondeo"`: HGB Poisson global (`PARAMS_HGB`) con la trayectoria recursiva **redondeada a unidades enteras** |
| `METODO_FINAL` | `fn(corte, h, ctx) -> DataFrame[catalogo, semana, h, pred]`. Es `m_hgb_redondeo`. **Para el pronóstico real de §8:** `METODO_FINAL(ULTIMA_SEMANA_COMPLETA, H_EXT, contexto(ULTIMA_SEMANA_COMPLETA))` |
| `MODELO_COLA_FINAL` | `"ingenuo"` (igual que en §5) |
| `CALIBRACION_INTERVALO` | DataFrame índice h = 1…4, columnas 0,1 / 0,9 (z₁₀, z₉₀). Se aplica con `aplicar_intervalo(pron, CALIBRACION_INTERVALO)` → columnas `lo`, `hi`. Para h > 4 usa h = 4 |
| `CORTES_BT` | 15 orígenes de backtesting. Úsenlos para validar cualquier ajuste nuevo |
| `fase_origen(corte, h)` | "antes del evento" / "toca el evento" / "después del evento" |
| `tabla_completa(d, por)` | Métricas con RMSSE |
| `ESTILO_MODELO` | Color y línea por modelo (reúsenlo en §7 para mantener la paleta) |
| `RECALCULAR_BACKTESTING` | `True` por defecto. Con `False` lee `6_backtesting_predicciones.csv` y ahorra ~4 min |

## 3. Resultados

### 3.1 Backtesting (top 20, 15 orígenes × 4 semanas)

| Modelo | WAPE top | Sesgo | MASE | RMSSE | WAPE antes | WAPE toca evento | WAPE después | Gana al ingenuo (orígenes) | IC 90 % dif. WAPE vs ingenuo |
|---|---|---|---|---|---|---|---|---|---|
| HGB+ingenuo | 0,879 | +0,01 | 1,65 | 1,45 | 0,42 | 0,94 | 0,557 | 12/15 | [−0,068, +0,011] |
| **HGB_redondeo** (final) | 0,896 | −0,02 | 1,72 | 1,51 | 0,47 | 0,95 | 0,558 | 9/15 | [−0,063, +0,043] |
| HGB_poisson | 0,898 | −0,02 | 1,72 | 1,51 | 0,47 | 0,95 | 0,572 | 9/15 | [−0,059, +0,044] |
| ingenuo | 0,907 | +0,04 | 1,64 | 1,43 | 0,44 | 0,97 | 0,600 | — | — |
| ETS | 0,934 | 0,00 | 1,73 | 1,48 | 0,45 | 0,99 | 0,710 | 5/15 | [−0,014, +0,067] |
| SARIMAX | 1,018 | +0,05 | 1,79 | 1,55 | 0,50 | 1,05 | 1,266 | 4/15 | [+0,043, +0,193] |
| media_movil_4 | 1,078 | +0,06 | 1,79 | 1,54 | 0,47 | 1,06 | 2,184 | 4/15 | [+0,027, +0,375] |

Fases: 2 orígenes antes, **11 que tocan la ventana del evento** (25-may → 13-jul) y 2 después. Colombia después del Mundial (real 49 uds): HGB_redondeo 90, ingenuo 84, HGB_poisson 118, SARIMAX 1.871, media móvil 3.990.

**Selección (§6.3):** los tres HGB empatan en WAPE (≤ 0,923) y en WAPE después del Mundial (≤ 0,585). Por simplicidad quedan `HGB_poisson` y `HGB_redondeo`, y desempata el WAPE después del Mundial → **`HGB_redondeo`**. Esto **cambia** el candidato de §5 (`HGB+ingenuo`). **`INGENUO_EMPATA = True`**: la mejora frente al ingenuo no es concluyente (el intervalo incluye el 0, P(gana) = 0,61) y en MASE/RMSSE el ingenuo es algo mejor.

### 3.2 Holdout (24-ago → 28-sep, entrenado al 17-ago)

| Modelo | WAPE top h=1…4 | WAPE top h=1…6 | Sesgo top h=1…6 | WAPE cola (catálogo / agregada) | WAPE total semanal |
|---|---|---|---|---|---|
| ETS | 0,470 | 0,427 | −0,07 | 1,37 / 0,27 | 0,166 |
| **ingenuo** | 0,476 | 0,433 | −0,05 | 1,25 / 0,27 | 0,170 |
| media_movil_4 | 0,492 | 0,453 | −0,03 | 1,37 / 0,27 | 0,157 |
| HGB+ingenuo | 0,637 | 0,574 | +0,14 | 1,38 / 0,19 | **0,147** |
| **HGB_redondeo** (final) | 0,790 | 0,718 | **+0,31** | 1,24 / 0,13 | 0,215 |
| HGB_poisson | 0,810 | 0,743 | +0,34 | 1,54 / 0,41 | 0,365 |
| SARIMAX | 1,180 | 1,189 | +0,64 | 1,37 / 0,27 | 0,391 |

**Diagnóstico (celda 6.4.2):** el **90 %** del sobrepronóstico del final sale de **CUELLO ALTO HONDA REFLECTIVO**. Su última semana antes del holdout fue su récord (71 uds; promedio de las 8 semanas previas: 35) y el boosting extrapoló la tendencia a ~132 uds/semana, cerca del tope (`TOPE_RELATIVO` × 71 = 142). La venta real fue ~47/semana. Sin Honda: HGB_redondeo WAPE 0,52 / sesgo +4 %; ingenuo 0,42 / −15 %. **Incluso sin Honda, el ingenuo gana en el holdout.**

### 3.3 Intervalos (top, holdout)

| Método | Cobertura 10–90 % | Ancho medio (uds) | Pinball q10 / q90 |
|---|---|---|---|
| §5.6 cuantiles HGB sin calibrar | 63 % | 16 | 2,72 / 2,62 |
| Conformal, todos los orígenes | 93 % | 72 | 2,73 / 6,61 |
| **Conformal, semanas fuera del evento (elegida a priori)** | 92 % | 37 | 2,85 / 3,35 |
| La elegida, evaluada en las semanas del evento del backtesting | 63 % | 44 | 15,4 / 22,4 |

Factores z (h = 1…4): z₁₀ = −2,8 / −3,1 / −3,8 / −4,6 y z₉₀ = 3,9 / 5,1 / 6,0 / 7,2. Los intervalos quedan **conservadores** (92 % contra 80 % nominal) porque se calibraron con las semanas normales del backtesting, que incluyen las del pre-Mundial con su tendencia. Sirven como cota para stock de seguridad. No los hagan más angostos mirando el holdout.

### 3.4 Segmentos y cola
- **Por horizonte** (backtesting, HGB_redondeo): WAPE 0,55 → 0,81 → 1,00 → 1,24 de h = 1 a 4. El ingenuo es igual en h = 1 y peor en h ≥ 2.
- **Colombia vs resto** (backtesting): 0,97 vs 0,74. En el holdout, Colombia vende casi 0 y cualquier pronóstico positivo da WAPE enorme (5,6). No lo usen como titular.
- **Cola:** regla ingenuo. Del total de unidades de la cola en el backtesting (9.823), **26,6 %** son de catálogos que nacen después del origen (error inevitable) y solo **0,3 %** de catálogos dormidos que reviven. En el holdout: 28 % y 3 %. La regla de 12 semanas (`SEMANAS_ACTIVO`) casi no pierde venta.
- **Redondeo de la trayectoria** (punto 11 del reporte 03): es casi indiferente en el top (0,896 vs 0,898) y mejora la cola (1,19 vs 1,35) y el WAPE después del Mundial.

## 4. Tablas en `procesado/`

| CSV | Grano | Nota |
|---|---|---|
| `6_backtesting_predicciones.csv` | modelo × corte × catálogo × semana | `y`, `pred`, `h`, `segmento`, `familia`, `fase_origen`, `periodo_semana` (234.647 filas) |
| `6_metricas_backtesting.csv` | modelo | `resumen_bt` completo |
| `6_wape_por_origen_backtesting.csv` | origen × modelo | WAPE del top, con la fase |
| `6_holdout_predicciones.csv` | modelo × catálogo × semana | 6 semanas |
| `6_metricas_holdout.csv` | modelo | Columnas aplanadas "bloque \| métrica" |
| `6_metricas_por_segmento.csv` | fuente × dimensión × grupo × modelo | segmento, familia, periodo_semana, h |
| `6_error_por_catalogo_holdout.csv` | catálogo del top | Final vs ingenuo |
| `6_calibracion_intervalos.csv` | calibración × h | z10, z90 |
| `6_intervalos_holdout.csv` | catálogo × semana | `lo`, `hi` del final |
| `6_evaluacion_intervalos.csv` | método | Cobertura, ancho, pinball |
| `6_cola_estado_catalogos.csv` | origen | Unidades activo / dormido / nuevo |
| `6_diagnostico_holdout.csv` | modelo | Con y sin el catálogo de mayor exceso |

Figuras: `6_2_01_wape_por_origen_backtesting`, `6_2_02_wape_por_horizonte`, `6_5_01_cobertura_intervalos`, `6_5_02_holdout_real_vs_pronostico`, `6_6_01_error_por_catalogo_holdout` (los títulos se generan con las cifras de la corrida).

## 5. ⚠️ Lo que el agente de §7–§8 tiene que saber

1. **Mensaje honesto para el póster:** el boosting **no le gana de forma clara al ingenuo**. Sí le gana a la media móvil, a SARIMAX y a RF, que arrastran el Mundial, y ese es el riesgo que le importa a Klixmant. En el holdout el ingenuo fue mejor. No digan "X % mejor que el ingenuo" como titular. Un titular defendible: "después del Mundial, el modelo pronosticó 90 uds de Colombia (real 49); una media móvil habría pronosticado 3.990".
2. **Pronóstico real (§8):** `ctx = contexto(ULTIMA_SEMANA_COMPLETA)` → `pron = METODO_FINAL(ULTIMA_SEMANA_COMPLETA, H_EXT, ctx)` → `aplicar_intervalo(pron, CALIBRACION_INTERVALO)` → `desagregar_talla_color(pron, ULTIMA_SEMANA_COMPLETA)` y `agregar_tela(pron)`. La cola va con `m_ingenuo`. El modelo para guardar con `joblib` es `ajustar_hgb(ctx, ULTIMA_SEMANA_COMPLETA)`. Ojo: `METODO_FINAL` lo reentrena por dentro, así que en §8 conviene separar entrenar / guardar / pronosticar con `pronostico_recursivo(..., redondear=True)`.
3. **Riesgo de extrapolación (Honda):** si un catálogo cierra con un récord, el HGB puede pronosticar casi 2 × ese récord (el tope). Recomendaciones para §8: (a) publicar el ingenuo al lado del modelo y marcar para revisión manual los catálogos donde los dos difieran más del 50 %; (b) si quieren probar un `TOPE_RELATIVO` menor (p. ej. 1,25–1,5) o un tope sobre la media de 8 semanas, **valídenlo solo con `CORTES_BT`** y documenten que la idea surgió del holdout.
4. **Alternativa defendible:** si el grupo prefiere `HGB+ingenuo` (mejor WAPE en el backtesting, 12/15 orígenes ganados y mejor total semanal en el holdout), la regla de simplicidad es la que lo descarta. Cambiarlo ahora sería elegir con el holdout: si lo hacen, díganlo explícitamente en la *model card*.
5. **Limitaciones para la *model card*:** 15 orígenes, de los cuales 11 tocan el evento; un solo holdout de 6 semanas; ninguna temporada de fin de año en los datos; estáticas (`tela_principal`, `pct_dama`…) calculadas con toda la historia; intervalos conservadores en semanas normales y demasiado angostos en eventos.
6. **`_CTX` y `_ESCALAS_RMSSE`** son caché. Si cambian `maestro`, `cal_modelo` o `agregar_variables()`, hagan `_CTX.clear(); _ESCALAS_RMSSE.clear()`.
7. **Tiempo de corrida:** ~17 min completo. Con `RECALCULAR_BACKTESTING = False` §6 baja a ~1 min (sigue calculando el holdout y los cuantiles de referencia).
8. **Gráficas de §7:** reúsen `ESTILO_MODELO` y `COLOR_FAMILIA`. Las de §6 ya cubren "barras de WAPE por modelo", "error por catálogo" y "real vs pronóstico con intervalo" del catálogo de gráficas del plan §7.2. Faltan las de producción (heatmap catálogo × talla × semana) y la versión de póster.

## 6. Decisiones que el grupo debería revisar

- **Regla de selección con simplicidad** (celda 6.3): con ella `HGB_redondeo` le gana a `HGB+ingenuo`. Es criterio del grupo.
- **Calibración "fuera del evento" elegida a priori:** da intervalos amplios (92 %). Es una decisión conservadora.
- **Primer origen del backtesting = 13-abr:** antes hay muy poca historia (Dropi arranca en febrero). Se puede justificar en el texto.
- **Textos:** todo el markdown de §6 (incluida la lectura 6.10) es un borrador técnico. **Redáctenlo con palabras propias** (riesgo Turnitin).

## 7. Reproducir la ejecución

*Run all* desde la celda 0, con el mismo venv de los agentes 02–03.
