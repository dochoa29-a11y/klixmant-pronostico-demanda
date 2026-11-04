# Reporte de traspaso — Agente 02 (sección 4)

**Fecha:** 3-nov-2026 · **Alcance:** §4 Preparación de datos e ingeniería de variables (plan §4.1–§4.5).
**No se hizo nada de §5 en adelante.** Las secciones 5–8 del notebook siguen como encabezados ⏳.
Lean también `docs/REPORTE_AGENTE_01_secciones_0-3.md`: las convenciones de §0 siguen vigentes.

---

## 1. Qué se entregó

| Archivo | Qué es |
|---|---|
| `Klixmant_Pronostico_Demanda.ipynb` | §4 completa y ejecutada (celdas 53–79). La tabla de estado de la celda 0 marca §4 ✅ |
| `procesado/4_*.csv` | 11 tablas (ver §4 de este reporte) |
| `figuras/4_*.png` | 5 gráficas |
| `docs/4_diccionario_variables.csv` | Diccionario de **todas** las columnas del panel: grupo, descripción, ventana temporal y uso recomendado |

**Ejecución verificada:** notebook completo de arriba abajo, sin errores ni warnings, en unos 3 minutos (casi todo es la lectura del Excel).
Python 3.14.7, pandas 3.1.0, scikit-learn 1.9.1, statsmodels 0.15.0. `VERSIONES` ahora incluye scikit-learn.
No se probó en Colab.

## 2. Estructura de §4 en el notebook

| Celda | Contenido |
|---|---|
| 4.1.1 | Normalización de nombres de catálogo → `prep["catalogo"]` (el original queda en `catalogo_crudo`) |
| 4.1.2 | `referencia` → `genero`, `tela`, `color_ref` |
| 4.1.3 | Validación de `talla_estandar()` contra el texto libre de Dropi |
| 4.1.4 | Tabla de reglas aplicadas (`reglas`) |
| 4.2.1 | Ficha maestra `maestro` (una fila por catálogo, índice = catálogo normalizado) |
| 4.2.2 | `mapa_tela` (catálogo → género × tela × color) y `mezcla_tc` (catálogo top → talla × color) |
| 4.3.1–4.3.2 | Decisión de la ventana del evento y calendario `cal_modelo` (hasta el 30-nov) |
| 4.3.3 | `construir_panel()`, `agregar_variables()`, `escenario_sin_evento()` → `panel_y` |
| 4.3.4 | Prueba automática de no fuga (`assert`) |
| 4.4.1–4.4.2 | K-means de perfiles → `maestro["cluster"]` |
| 4.5.1–4.5.3 | Base frente a evento → `base_evento`, tablas de incremental y sensibilidad |
| 4.6.1–4.6.3 | `panel` final, listas de variables, diccionario, correlaciones y exportación |
| 4.7 | Cifras clave para el texto (`h4`) |

### Constantes nuevas (definidas en 4.2.1 y 4.3.2)

| Constante | Valor | Uso |
|---|---|---|
| `ULTIMA_SEMANA_COMPLETA` | 2026-09-28 | Fin del panel |
| `SEMANAS_HOLDOUT` / `SEMANA_INICIO_HOLDOUT` | 6 / 2026-08-24 | Holdout del plan §6.1 (24-ago a 4-oct). **Tocarlo una sola vez** |
| `SEMANAS_PRE_MUNDIAL` | 2 | Semanas `pre_mundial` (25-may y 1-jun) |
| `VENTANA_EVENTO` | 2026-05-25 → 2026-07-13 (8 semanas) | Ventana de la separación base/evento |
| `TELAS` | 16 códigos | Telas base |
| `VARIABLES_MODELO` | 37 variables (5 categóricas) | Lista recomendada para §5 |
| `VARIABLES_CATEGORICAS` | `linea, tipo_prenda, tela_principal, tipo_proceso, cluster` | Pasar como `category` |
| `VARIABLES_OPCIONALES` | `semana_anio, mes, semanas_desde_fin_mundial, catalogo` | Probar con cuidado (ver §6) |
| `VARIABLES_EVENTO` | 6 variables del Mundial | Las que apaga `escenario_sin_evento()` |
| `VARIABLES_DINAMICAS` | rezagos, medias, desviaciones, `semanas_desde_ultima_venta`, `pct_dropi_8` | Se recalculan en cada paso recursivo |

## 3. Cómo se resolvieron los 8 problemas del reporte 01

| # | Problema | Resolución |
|---|---|---|
| 1 | Talla en texto libre (Dropi) | `talla_estandar()` **validada y adoptada**. En las 7.963 líneas de texto libre, el género coincide con el prefijo H/D de la referencia en el 100 % y el color, con la columna `color` en el 99,85 % (BEIGE = Cocoa, AZUL OSCURO = AzulNavy). El texto no aporta nada nuevo. Las 2 líneas sin talla se recuperaron del código pegado |
| 2 | `referencia` no son 16 telas | El formato es `género · tela · L · color`. **El 2.º token tiene exactamente 16 valores**, que coinciden con las "16 bases" de la documentación: N (65 %), CO90 (22 %), R (8 %), MAR, BANDERA, 100, JB, RF, JBMAR, PER, BO, 3, BL, CM, BTS, CCC. Esta es la tela que se usa para agregar la compra de insumo. 9 catálogos se cortan en más de una tela (9,1 % del volumen) |
| 3 | Nombres duplicados | 804 → **798 catálogos**. Se unificaron espacios y mayúsculas (`CUELLO ALTO BARCELONA`), `BAYER MUNICH` → `BAYERN MUNICH`, `ALLTO`/`ALRTO` → `ALTO` y PERSONALIZADO mal escrito (por similitud ≥ 0,8 de cada palabra). Un `assert` impide fusionar KTM/AKT y KAWASAKI/SIN REFLECTIVO. El mapa está en `4_mapa_nombres_catalogo.csv` |
| 4 | Ficha `CATALOGOS` incompleta | 233 de 798 con ficha (89,6 % del volumen). Sin ficha, `tipo_proceso` sale del sufijo del SKU (BOR/ES; 392 catálogos). Si no hay sufijo, queda `SIN_DATO` (173). `reflectivo` se toma del nombre y `personalizado`, de la línea. `planchadas`, `puntadas` y `no_rotativo` quedan en NaN, con `tiene_ficha` como indicador |
| 5 | Sin catálogo / descarte | Solo **2** de las 10 líneas sin catálogo no están canceladas: quedan como `SIN_CATALOGO`, en el total pero no en el panel. Las 24 líneas con `descarte = 1` (todas despachadas, ago–oct) **cuentan como demanda** |
| 6 | Estados pendientes | Las 15 líneas cuentan como demanda |
| 7 | Ceros explícitos | `construir_panel()` crea una fila por semana desde la primera venta de cada catálogo. Panel: 17.722 filas, 792 catálogos, 83,7 % de las filas con cero (top 20: 669 filas, 13,2 % con cero). Cuadra exactamente: 29.428 uds = demanda − semana parcial (119) − sin catálogo (2) |
| 8 | Devoluciones | No se usan como variable |

## 4. Tablas en `procesado/` (insumos para §5)

| CSV | Grano | Nota |
|---|---|---|
| `4_panel_semanal_catalogo.csv` | catálogo × semana | **Tabla principal.** 53 columnas: objetivo `y`, `y_base`, `y_evento`, variables y `conjunto` (entrenamiento 13.265 / holdout 4.457) |
| `4_maestro_catalogos.csv` | catálogo | Atributos estáticos, rank, ABC, `top_n`, línea, tela, ficha, `fuente_proceso`, clúster |
| `4_calendario_modelo_semanal.csv` | semana (12-ene → 30-nov) | Calendario y evento; cubre el horizonte de 8 semanas |
| `4_base_evento_catalogo_semana.csv` | catálogo × semana | `y`, `y_base`, `y_evento` |
| `4_incremental_mundial_top.csv` / `_linea.csv` | catálogo top / línea | Unidades de evento netas, positivas y desplazadas |
| `4_sensibilidad_base_evento.csv` | escenario | Variando semanas previas (1–3) y k del nivel (3, 4, 6) |
| `4_perfil_clusters.csv` | catálogo elegible (84) | Indicadores del perfil y clúster |
| `4_mapa_catalogo_tela.csv` | catálogo × género × tela × color | Proporciones históricas y de las últimas 12 semanas (para agregar a insumo) |
| `4_proporciones_talla_color_top.csv` | catálogo top × talla × color | Para la desagregación de §5.5 (12 semanas, suavizado 0,5; si en la ventana hubo menos de 30 uds, usa toda la historia: aplica a 7 catálogos del top) |
| `4_mapa_nombres_catalogo.csv` | nombre crudo → normalizado | Trazabilidad de la normalización |

Al leer los CSV se pierden los tipos: conviertan `semana` con `pd.to_datetime` y las categóricas con `.astype("category")`.
Si trabajan dentro del notebook, usen las variables en memoria (`panel`, `maestro`, `cal_modelo`).

## 5. Resultados clave de §4

- **Ventana del evento:** la familia Colombia está en su nivel de abril hasta el 18-may. Sube ×2,0 la semana del 25-may y ×6,0 la del 1-jun. Por eso se toman **2 semanas previas** y la ventana va del 25-may al 19-jul.
- **Base frente a evento (línea base interpolada entre medianas):** en la ventana se vendieron 10.297 uds, con una base de 3.995.
  - **Familia Colombia:** 6.582 uds de evento, el 87 % de lo que vendió en la ventana. El rango de sensibilidad es 6.009–6.750: la conclusión no depende de los parámetros.
  - **Resto:** −280 uds netas. Hay +1.365 uds de evento (Argentina, Portugal y Nacional Rey de Copas, que también son de fútbol) y −1.645 uds **desplazadas**: motos y autos vendieron menos que su base. En Honda la caída empieza a fines de mayo, al mismo tiempo que el pico de Colombia. La hipótesis es que la planta priorizó la producción para el Mundial; hay que validarla con Klixmant antes de afirmarla.
- **K-means (k = 4, silueta 0,26):** se agruparon 84 catálogos elegibles, que son el 94,8 % de las unidades antes del holdout. El resto queda como `cola`.
  - **evento** (15 catálogos, 13.304 uds): Colombia, Argentina y Portugal.
  - **base** (34 catálogos, 8.869 uds): motos, autos y América.
  - **en declive** (32 catálogos, 2.487 uds): por ejemplo, RED BULL sin cuello alto.
  - **base errática** (3 catálogos): incluye Nacional Rey de Copas.
  - k = 2 tiene más silueta (0,37), pero solo separa el evento del resto.
- **Línea de producto** (regex en `LINEAS_PRODUCTO`): COLOMBIA 12.495 uds, MOTOS 7.295, AUTOS_Y_MOTOR 4.888, FUTBOL 3.377, PERSONALIZADO 828, OTROS 545.
- **Correlación de Spearman con `y`** (top, entrenamiento): lag_1 0,81, media_4 0,66 y lag_2 0,62. `semanas_desde_ultima_venta` y `semanas_desde_lanzamiento` son negativas. Las variables de evento tienen correlación global baja porque el efecto es solo para Colombia, y los árboles lo capturan con interacciones.
- **Top 20:** es el mismo que en §3. Si se calcula solo antes del holdout, comparte 19 de 20 (sale FORD y entra BUZO COLOMBIA 100 AÑOS).

## 6. ⚠️ Lo que el agente de §5 tiene que saber

1. **Prueba de no fuga.** `verificar_sin_fuga()` comprueba que las variables dinámicas de una semana no cambian si se borra el futuro (3 cortes, 0 celdas distintas). Si modifican `agregar_variables()`, vuelvan a correrla.
2. **Pronóstico recursivo.** `agregar_variables()` está pensada para eso. El procedimiento es:
   1. Agregar filas futuras con `y = NaN` e `y_dropi = NaN`.
   2. Llamar `agregar_variables(..., ultima_observada=ULTIMA_SEMANA_COMPLETA)`.
   3. Predecir la semana h y escribir la predicción en `y`.
   4. Repetir para h + 1.

   `pct_dropi_8` se congela en su último valor conocido. Con predicciones fraccionarias, `semanas_desde_ultima_venta` queda en 1 en el futuro. Decidan si eso es aceptable o si redondean antes.
3. **Variables con fuga parcial dentro del periodo de entrenamiento.** El clúster y algunas estáticas (`tela_principal`, `pct_dama`, `n_telas`, `pct_tela_principal`, `rank`) se calcularon con datos anteriores al holdout o con toda la historia. Para el holdout no hay problema. En los pliegues del backtesting rodante (§6) **recalculen `perfil_demanda(panel_y, corte, VENTANA_EVENTO)` y `agrupar_catalogos()` con el corte de cada pliegue**, o al menos documenten la limitación.
4. **Variables fuera de rango.** `semana_anio` y `mes` del horizonte (octubre a diciembre) no existen en el entrenamiento, por eso están en `VARIABLES_OPCIONALES`.
5. **NaN.** `pct_dropi_8` (792), `no_rotativo`, `planchadas` y `puntadas` traen NaN. `HistGradientBoostingRegressor` los maneja; para Random Forest, ETS o LSTM hay que imputar.
6. **Categóricas.** Usen `X[VARIABLES_CATEGORICAS].astype("category")` y `categorical_features="from_dtype"`.
7. **Separar base de evento con el modelo (ruta 2 del plan §4.5).** `escenario_sin_evento(X)` pone en 0 las 6 `VARIABLES_EVENTO`. Ojo: los rezagos de las semanas del Mundial siguen teniendo demanda de evento, así que el contrafactual del modelo no es puro. Compárenlo con `y_base` de la ruta 1.
8. **`y_base` como objetivo alterno.** Pueden entrenar un modelo de demanda base con `y_base` en lugar de `y`, y comparar en el holdout. Dentro de la ventana, `y_base` es una interpolación, no un dato observado.
9. **Demanda desplazada.** Motos y autos vendieron menos durante el Mundial. Si el modelo trata esa caída como "normal", va a subpronosticar la base. Las variables de evento (`semana_mundial`, `pre_mundial`) deberían capturarla también para la familia RESTO; revísenlo con la importancia por permutación.
10. **Familia Colombia después del Mundial ≈ 0** (los 5 catálogos Colombia del top están en el clúster `evento`). El criterio del plan §5.7 es que el modelo **no siga pronosticando demanda de evento** en el holdout. Midan el sesgo en estos catálogos por separado.
11. **Cola.** De los 792 catálogos del panel, 708 no son elegibles para el clustering (`cluster = "cola"`). Para ellos, la regla del plan es media móvil o SBA. Las filas están en el panel, por si quieren usarlas como datos extra del modelo global (cross-learning).

## 7. Decisiones que el grupo debería revisar

- **La tela como 2.º token de `referencia`:** el conteo coincide con las 16 bases de la documentación, pero conviene confirmar con Klixmant qué es cada código (N, CO90, R, MAR…) y qué significa la "L".
- **Clasificación de líneas por regex (`LINEAS_PRODUCTO`):** BMW se contó como MOTOS (sus diseños son reflectivos) y RED BULL como AUTOS_Y_MOTOR. Hay 545 uds en OTROS. Si el grupo conoce mejor el portafolio, ajusten los patrones en la celda 4.2.1.
- **`descarte = 1` como demanda:** son 24 uds y no cambian el resultado, pero es una decisión de negocio.
- **Textos:** todo el markdown de §4 es un borrador técnico. **Redáctenlo con palabras propias** (riesgo Turnitin).
- **Pendientes del reporte 01 que siguen abiertos:** confirmar con el docente catálogo frente a referencia, verificar en FIFA.com la fecha del partido contra RD Congo y revisar la rúbrica en el Syllabus.

## 8. Reproducir la ejecución

El notebook se ejecuta completo con *Run all*. En local se usó un entorno con las librerías de `requirements.txt`; scikit-learn ya estaba listado.
Una copia del notebook **antes** de §4 quedó fuera del proyecto (en el scratchpad del agente). Si se necesita volver atrás, borren las celdas 53–79 y restauren la celda de encabezado "## 4. … ⏳ PENDIENTE".
