# Reporte de traspaso — Agente 03 (sección 5)

**Fecha:** 3-nov-2026 · **Alcance:** §5 Modelado (plan §5.1–§5.7): escalera de modelos, estrategia multi-paso, cuantiles, base/evento con el modelo, desagregación y selección del candidato.
**No se hizo nada de §6 en adelante.** El **holdout (24-ago → 28-sep) no se tocó**. Las secciones 6–8 siguen como encabezados ⏳.
Lean también los reportes 01 y 02: sus convenciones siguen vigentes.

---

## 1. Qué se entregó

| Archivo | Qué es |
|---|---|
| `Klixmant_Pronostico_Demanda.ipynb` | §5 completa y ejecutada (celdas 80–107). La celda 0 marca §5 ✅ (candidato; se confirma en §6) |
| `procesado/5_*.csv` | 8 tablas (ver §4 de este reporte) |
| `figuras/5_*.png` | 6 gráficas |
| `requirements.txt` | Se agregó `torch` (opcional) |

**Ejecución verificada:** notebook completo de arriba abajo con `nbconvert --execute`, sin errores. Tarda unos **13 minutos**: ~3,5 del Excel, ~6 de la validación de §5.5 y ~3 del resto de §5.
Python 3.14.7, pandas 3.1.0, scikit-learn 1.9.1, statsmodels 0.15.0, **torch 2.15.0 CPU** (`VERSIONES["torch"]`). No se probó en Colab; Colab trae torch.
Si torch no está instalado, `TORCH_OK = False` y el LSTM devuelve el ingenuo (se imprime un aviso).

## 2. Estructura de §5 en el notebook

| Celda | Contenido |
|---|---|
| 5.1 (md) | Características del dataset → consecuencias |
| 5.2 | `maestro_al_corte()`, `matriz_X()`, `panel_al_corte()`, `filas_futuras()`, `pronostico_recursivo()`, `escala_mase()`, `metricas()` |
| 5.3.1 | Escalera: `m_ingenuo`, `m_media_movil`, `m_sba`, `m_tsb`, `m_ets`, `m_sarimax`, `m_hgb`, `m_rf`, `contexto()`, `evaluar()`, `combinar_resultados()`, `tabla_metricas()` |
| 5.3.2 | LSTM en PyTorch: `RedLSTM`, `m_lstm` |
| 5.4 | Estrategia directa `m_hgb_directo` y `combinar()` (para pronosticar) |
| 5.5.1–5.5.3 | Validación preliminar (`res`), tabla `resumen`, `por_origen` y gráficas |
| 5.6 | Cuantiles: `m_hgb_cuantiles`, `res_cuantiles`, cobertura y pinball |
| 5.7 | Ruta 2 base/evento: `modelo_ruta2`, `ruta2`, `comparacion_rutas` |
| 5.8 | `desagregar_talla_color()`, `agregar_tela()` y su validación |
| 5.9 | Importancia por permutación (`importancia`) |
| 5.10 | Regla de selección → `MODELO_CANDIDATO`, `MODELO_COLA`; exportación |
| 5.11 | Cifras clave (`h5`) |

### Constantes y funciones nuevas que §6–§8 deben reutilizar

| Nombre | Valor / uso |
|---|---|
| `TOP` | Lista de los 20 catálogos del top |
| `H`, `H_EXT`, `SEMANA` | 4, 8, `Timedelta(weeks=1)` |
| `PARAMS_HGB` | `loss="poisson", learning_rate=0.05, max_iter=300, max_leaf_nodes=15, min_samples_leaf=20, l2_regularization=1.0, categorical_features="from_dtype"` |
| `PARAMS_CUANTIL` | Igual pero `loss="quantile"`, **`l2_regularization=0`**, `learning_rate=0.1` |
| `TOPE_RELATIVO` | 2,0: tope de cada predicción = 2 × la mejor semana histórica del catálogo |
| `SEMANAS_ACTIVO` | 12: los modelos globales solo pronostican catálogos con venta en las últimas 12 semanas; el resto va en 0 |
| `CORTES_VALIDACION` | 27-abr, 18-may, 8-jun, 29-jun, 13-jul, 20-jul (el último pronóstico termina el 17-ago; hay un `assert` contra el holdout) |
| `CORTE_ENTRENAMIENTO` | 2026-08-17 = semana anterior al holdout |
| `MODELO_CANDIDATO` / `MODELO_COLA` | `"HGB+ingenuo"` / `"ingenuo"` |
| `contexto(corte)` | Caché por corte: `panel` con variables a ese corte, `maestro` con clúster recalculado, `p_y`, `activos` |
| `evaluar(METODOS, cortes, h)` | **Esto es el backtesting.** Para §6 basta pasarle más cortes (p. ej. todos los lunes) y los métodos elegidos |

**Interfaz de los métodos:** `fn(corte, h, ctx) -> DataFrame[catalogo, semana, h, pred]`, donde `corte` es la **última semana observada**.
`evaluar()` une con la venta real de `panel_y`. Los catálogos que nacen después del corte cuentan con `pred = 0`.

## 3. Resultados de la validación preliminar (top 20, 6 orígenes × 4 semanas)

| Modelo | WAPE top | Sesgo | MASE | WAPE después del Mundial | Uds Colombia pronosticadas después (real = 49) |
|---|---|---|---|---|---|
| HGB_suave | 0,935 | +0,03 | 1,62 | 0,80 | 201 |
| HGB_sin_cluster | 0,950 | +0,12 | 1,57 | 0,62 | 125 |
| **HGB_poisson** (principal) | 0,952 | +0,11 | 1,54 | 0,57 | 118 |
| **HGB+ingenuo** (candidato) | 0,960 | +0,11 | 1,52 | **0,56** | 101 |
| ingenuo | 1,006 | +0,12 | 1,57 | 0,60 | 84 |
| ETS | 1,039 | +0,09 | 1,68 | 0,71 | 313 |
| SARIMAX | 1,104 | +0,22 | 1,69 | 1,27 | 1.871 |
| HGB_directo | 1,145 | +0,22 | 1,77 | 1,16 | 1.303 |
| RF | 1,172 | +0,33 | 1,68 | 1,92 | 3.402 |
| media_movil_4 | 1,224 | +0,22 | 1,73 | 2,18 | 3.990 |
| LSTM | 1,654 | +0,72 | 4,38 | 3,53 | 371 |

(SBA, TSB y HGB_rec+dir también están en `resumen`.)

**Lectura:**
- **El boosting global le gana al ingenuo, pero por poco:** WAPE de 0,95 frente a 1,01 y, después del Mundial, 0,57 frente a 0,60. No exageren la mejora en el póster.
- **Criterio 3 del plan (no arrastrar el Mundial):** HGB y el ingenuo pronostican ~100 uds de Colombia para agosto (real: 49). La media móvil pronostica 3.990, RF 3.402 y SARIMAX 1.871. Ahí está la diferencia que le importa a Klixmant.
- **WAPE ≈ 1 en el promedio** se debe al origen del 29-jun. Con datos a esa fecha nadie sabe que Colombia queda eliminada el 7-jul, y todos los modelos tienen WAPE de 2–3,5. Sin ese origen, el WAPE del HGB ronda 0,6. Repórtenlo **por periodo**, no solo el promedio.
- **La estrategia directa** salió peor que la recursiva (con tan poca historia, cada modelo directo tiene menos filas). La combinación recursiva + directa tampoco ayudó.
- **El LSTM** se sobreajusta (WAPE 5,9 en el origen del 20-jul). Se reporta como experimento, como dice el plan.
- **Sensibilidad:** HGB_suave tiene el mejor WAPE global, pero el peor de los HGB después del Mundial. Quitar el clúster casi no cambia el resultado.
- **Cola:** a nivel catálogo ningún método le gana al ingenuo (WAPE 1,40). SBA y TSB sobrepronostican mucho, porque la cola está llena de pedidos únicos que no se repiten. En el **total de la cola**, el ingenuo tiene un WAPE de 0,20.
- **Cuantiles:** la cobertura del 10–90 % es del **50 %** (nominal 80 %): los intervalos son demasiado angostos.
- **Ruta 2 frente a ruta 1 (catálogos que existían antes de la ventana):** la base coincide (Colombia 980 / 867 uds; resto 3.008 / 3.454). El evento de Colombia sale 5.102 con la ruta 1 y 2.959 con el modelo: el modelo subestima el pico. **Para cuantificar el evento usen la ruta 1**; la ruta 2 confirma la base.
- **Desagregación:** el WAPE pasa de 0,57 (catálogo × semana) a 1,02 (talla × color × semana). Sumando las 4 semanas, que es lo que se compra, queda en 0,67.
- **Importancia** (permutación, a 1 paso, después del Mundial): lag_1, semanas_desde_ultima_venta, clúster, desv_4 y media_4. Las variables de evento valen 0 en esas filas, así que su importancia es 0 por construcción.

## 4. Tablas en `procesado/`

| CSV | Grano | Nota |
|---|---|---|
| `5_predicciones_validacion.csv` | modelo × corte × catálogo × semana | `y`, `pred`, `h`, `segmento` (top/cola), `familia`, `periodo`, `segundos` |
| `5_metricas_validacion.csv` | modelo | La tabla `resumen` completa |
| `5_wape_por_origen.csv` | modelo × origen | WAPE del top |
| `5_cuantiles_validacion.csv` | corte × catálogo × semana | `pred`, `q10`, `q50`, `q90` |
| `5_base_evento_dos_rutas.csv` | catálogo × semana de la ventana | `y`, `y_base` (ruta 1), `con_evento`, `sin_evento` (ruta 2), `grupo` |
| `5_comparacion_rutas.csv` | grupo × familia | Totales de las dos rutas |
| `5_desagregacion_talla_color_validacion.csv` | catálogo × semana × talla × color | Ejemplo en el origen del 20-jul |
| `5_importancia_permutacion.csv` | variable | Aumento del MAE ± desviación |

Figuras: `5_5_01_wape_por_modelo`, `5_5_02_wape_modelo_origen` (heatmap), `5_6_01_real_vs_pronostico_fin_mundial`, `5_7_01_base_evento_dos_rutas` y `5_9_01_importancia_permutacion`.

## 5. ⚠️ Lo que el agente de §6 tiene que saber

1. **Backtesting de origen móvil (plan §6.1).** Usen `evaluar()` con todos los lunes posibles como corte, por ejemplo desde el 13-abr hasta `CORTE_ENTRENAMIENTO − 4 semanas`. Corran solo los métodos finalistas: `ingenuo`, `HGB_poisson`, `HGB+ingenuo` (vía `combinar_resultados`), `SARIMAX` y `media_movil_4` como referencia. Cada corte cuesta ~4 s de `contexto()` más ~6 s por HGB. Con 15 cortes son unos 3–4 min.
2. **El holdout se toca una sola vez:** `contexto(CORTE_ENTRENAMIENTO)` y `evaluar({...}, [CORTE_ENTRENAMIENTO], h=6)`. Ojo: con h = 6 la recursión llega al 28-sep. Decidan si reportan h = 1…4 (horizonte principal) o las 6 semanas.
3. **`contexto()` está cacheado** en `_CTX`. Si cambian `maestro`, `cal_modelo` o `agregar_variables()`, hagan `_CTX.clear()`. Las escalas del MASE se guardan en `_ESCALAS` al llamar a `evaluar()`.
4. **El clúster ya se recalcula por corte** (`maestro_al_corte`), con k fijo = `K_ELEGIDO`. Las demás estáticas (`tela_principal`, `pct_dama`, `n_telas`, `pct_tela_principal`) siguen calculadas con toda la historia; documéntenlo como limitación menor.
5. **Cortes dentro del Mundial:** con un corte antes del fin de la ventana, `int_despues` (e `int_evento`) no existen y se llenan con 0 antes del K-means. Los nombres de clúster cambian por pliegue (p. ej. "en declive (2)"). No importa porque cada pliegue entrena su propio modelo.
6. **Reporten por segmento** (plan §6.3): top frente a cola, Colombia frente a resto y por periodo. `res` ya trae `segmento`, `familia` y `periodo`, y `tabla_metricas(d, por=(...))` acepta cualquier agrupación.
7. **Cuantiles:** con 50 % de cobertura no sirven todavía para stock de seguridad. Opciones: (a) calibrar con los residuos del backtesting (conformal: ensanchar q10/q90 por un factor por horizonte); (b) intervalos Poisson / binomial negativa alrededor de `pred`. Si no da el tiempo, repórtenlo como limitación.
8. **El candidato es una combinación (HGB + ingenuo, 50/50).** Para pronosticar se usa `combinar(m_hgb, m_ingenuo)(corte, h, ctx)`. Si en el backtesting de §6 la diferencia con `HGB_poisson` solo es mínima, el criterio 4 del plan (simplicidad) favorece a `HGB_poisson`. Decídanlo con los números.
9. **Pronóstico real para Klixmant (§8):** se entrena con `contexto(ULTIMA_SEMANA_COMPLETA)` y se pronostica `H_EXT = 8` semanas (5-oct → 23-nov). Con `semana_anio`/`mes` fuera del modelo no hay problema de rango. Black Friday (27-nov) cae fuera del horizonte de 8 semanas. `fecha_comercial` sí lo marca si se extiende el horizonte, pero el modelo nunca vio un Black Friday.
10. **Salida para producción:** `desagregar_talla_color(pron, corte)` para cortes y `agregar_tela(pron)` para insumo. Para la cola, `mapa_tela` también cubre los catálogos de la cola.
11. **Redondeo:** `pronostico_recursivo(..., redondear=False)` por defecto (punto 2 del reporte 02). Con `redondear=True`, `semanas_desde_ultima_venta` vuelve a crecer cuando el pronóstico es < 0,5. No se probó cuál da mejor WAPE; es un experimento barato para §6.
12. **Tiempo de corrida:** el notebook ya tarda ~13 min. Si §6 suma mucho más, consideren guardar `res` en CSV y leerlo con una bandera `RECALCULAR = False`.

## 6. Decisiones que el grupo debería revisar

- **Regla de empate del 5 %** en la selección (celda 5.10.1): es una decisión de criterio. Con 6 orígenes, diferencias de 1–2 puntos de WAPE no son significativas.
- **`TOPE_RELATIVO = 2`:** es una salvaguarda de producción, no un parámetro afinado. Si un catálogo de verdad duplica su récord, el tope recorta el pronóstico. Para un evento nuevo que Klixmant conozca de antemano, lo correcto es el ajuste experto, no el modelo.
- **Cola en 0 si no vendió en 12 semanas:** es una regla, no un modelo. Cuantifiquen en §6 cuántas unidades de la cola son de catálogos "dormidos" que reviven.
- **Hipótesis de la demanda desplazada** (reporte 02): la ruta 2 también ve el resto por debajo de su base durante el Mundial (−240 uds frente a −517 de la ruta 1). Sigue siendo una hipótesis para validar con Klixmant.
- **Textos:** todo el markdown de §5 es un borrador técnico. **Redáctenlo con palabras propias** (riesgo Turnitin).

## 7. Reproducir la ejecución

*Run all* desde la celda 0. En local se usó el venv del agente 02 más `pip install torch --index-url https://download.pytorch.org/whl/cpu`.
Hay una copia del notebook **antes** de §5 fuera del proyecto (scratchpad del agente 03, `notebook_antes_s5.ipynb`). Para volver atrás, borren las celdas 80–107 y restauren el encabezado "## 5. Selección de modelos — ⏳ PENDIENTE".
