# Reporte de traspaso — Agente 05 (sección 7)

**Fecha:** 4-nov-2026 · **Alcance:** §7 Graficación (plan §7.1–§7.2): gráficas de producción, versión póster e índice de figuras.
Además se corrigió un **error de §5** que afectaba a §6 y al pronóstico de producción (ver §2 de este reporte; se hizo con autorización del grupo).
**No se hizo nada de §8 en adelante.** La sección 8 sigue como encabezado ⏳.
Lean también los reportes 01–04: sus convenciones siguen vigentes, **pero las cifras del holdout del reporte 04 quedaron viejas** (§2).

---

## 1. Qué se entregó

| Archivo | Qué es |
|---|---|
| `Klixmant_Pronostico_Demanda.ipynb` | §7 completa y ejecutada (celdas 130–147). La celda 0 marca §7 ✅ |
| `figuras/7_*.png` | 4 gráficas de producción |
| `figuras/poster/P1…P4` (`.png` 300 dpi + `.pdf`) | 4 gráficas para el póster |
| `procesado/7_*.csv` | 4 tablas (ver §5) |
| `docs/7_indice_figuras.csv` | Índice: fila del plan §7.2 → archivo |

**Ejecución verificada:** notebook completo de arriba abajo con `nbconvert --execute`, **0 celdas con error**, mismo venv de los agentes 02–04.
Copia del notebook **antes** de §7 (y antes de la corrección): scratchpad del agente 05 (`notebook_antes_s7.ipynb`).

## 2. ⚠️ Corrección en §5: `early_stopping`

**Síntoma.** Al pronosticar desde el 28-sep, el modelo final daba 424 uds para el top en 4 semanas, contra 1.372 del ingenuo y 1.275 reales de las últimas 4.
Incluso dentro de la muestra subestimaba la venta a la mitad.

**Causa.** `PARAMS_HGB` no fijaba `early_stopping`. Con el valor por defecto (`"auto"`), scikit-learn lo activa si hay más de 10.000 filas
y aparta un 10 % **aleatorio** de los datos para validar (eso, además, mezcla semanas futuras y pasadas). Las filas crecen con el corte:

| Corte | Filas | Iteraciones con `"auto"` |
|---|---|---|
| 13-abr … 6-jul | ≤ 9.332 | 300 (sin early stopping) |
| 20-jul (último origen del backtesting) | 10.567 | 118 |
| 17-ago (holdout) | 13.265 | 141 |
| 28-sep (producción) | 17.722 | **10** |

**Arreglo.** Celda 5.3.1: `PARAMS_HGB` ahora incluye `early_stopping=False`. `PARAMS_CUANTIL` y todos los HGB lo heredan. Se reejecutó todo.

**Qué cambió** (lo demás quedó igual o casi igual):

| Cifra | Antes (reporte 04) | Ahora |
|---|---|---|
| Modelo final (§6.3) | `HGB_redondeo` | `HGB_redondeo` (**no cambia**) |
| WAPE top backtesting | 0,896 | 0,897 |
| WAPE top después del Mundial | 0,558 | 0,585 |
| Colombia tras el Mundial (real 49) | 90 | **75** |
| Holdout WAPE top h=1…4 / h=1…6 | 0,790 / 0,718 | **0,696 / 0,652** |
| Holdout sesgo top h=1…6 | +31 % | **+19 %** |
| Holdout WAPE total semanal: `HGB_redondeo` / `HGB+ingenuo` / ingenuo | 0,215 / 0,147 / 0,170 | **0,110 / 0,092** / 0,170 |
| Sin Honda: WAPE / sesgo del final | 0,52 / +4 % | 0,52 / −3 % |

Lectura: **en el top el ingenuo sigue ganando en el holdout** (0,43 contra 0,65), pero en el **total semanal**, que es lo que mira compras,
ahora el modelo final es mejor que el ingenuo (0,11 frente a 0,17). Es corregir un error, no afinar con el holdout; documéntenlo así en la *model card*.
Se agregó una nota al inicio de la lectura 6.10 del notebook con estos valores. **El reporte 04 no se modificó**: sus tablas 3.1–3.2 son de antes de la corrección.

## 3. Estructura de §7 en el notebook

| Celda | Contenido |
|---|---|
| 7 (md) | Objetivo y principios aplicados |
| 7.1 | `estilo_poster()`, `guardar_poster()`, `RUTA_POSTER`, `COLOR_PRONOSTICO`, `CMAP_UNIDADES`, `etiqueta_cat()`, `miles()`, `fecha_corta()` |
| 7.2.1 | Pronóstico vigente → **`pron_vigente`**, `tc_vigente`, `tela_vigente`, **`REVISAR`**, `ORDEN_TOP_VIGENTE` |
| 7.2.2–7.2.5 | Gráficas de producción |
| 7.3.1–7.3.4 | Póster P1–P4 |
| 7.4 | `indice_figuras` → `docs/7_indice_figuras.csv` (con `assert` de que todos los archivos existen) |
| 7.5 | Exportación |
| 7.6 | Cifras clave (`h7`) |

**Pronóstico vigente (solo para graficar).** Corte = `ULTIMA_SEMANA_COMPLETA` (28-sep), `H_EXT` = 8 semanas (5-oct → 23-nov).
Top con `METODO_FINAL`, cola con el ingenuo (`MODELO_COLA_FINAL`), intervalos con `aplicar_intervalo(…, CALIBRACION_INTERVALO)` solo en el top.
Columnas de `pron_vigente`: `pred` (publicado), `pred_modelo`, `pred_ingenuo`, `lo`, `hi`, `revisar`.
**Regla de revisión manual** (recomendación del reporte 04): |modelo − ingenuo| / ingenuo > 50 % **y** ≥ 10 uds en las 4 semanas
(`UMBRAL_REVISION`, `UMBRAL_REVISION_UDS`). El segundo umbral evita marcar catálogos de 1–5 uds.

## 4. Resultados

### 4.1 Pronóstico vigente (corte 28-sep)
- Próximas 4 semanas: **top 1.444 uds** (ingenuo 1.372; últimas 4 reales 1.275, +13 %) y **cola 984 uds**.
- Ningún catálogo del top quedó para revisión manual. Los más alejados del ingenuo: Red Bull (+44 %, +42 uds) y BMW Estampado (+35 %).
- Mayor volumen: CA Mercedes (221 uds en 4 semanas), Honda Reflectivo (216) y Yamaha Reflectivo (164).
- Tallas: **M y L = 58 %** (S 12 %, XL 19 %).
- Telas: **H·N, D·N y H·R = 98 %** del insumo (H·N sola ≈ 1.790 uds).
- Todas las unidades llegan a tela (cobertura de `mapa_tela` = 100 %).

### 4.2 Póster (`figuras/poster/`)

| Archivo | Bloque | Título que genera la corrida |
|---|---|---|
| `P1_concentracion` | Datos | 20 de 792 catálogos venden el 77 % |
| `P2_mundial_base_evento` | Problema | El Mundial sumó ~6.582 unidades de evento: el 87 % de lo que vendió Colombia en esas semanas |
| `P3_colombia_despues_mundial` | **Titular** | Tras el Mundial el modelo pronosticó 75 uds de Colombia (real 49); una media móvil habría pedido 3.990 |
| `P4_plan_produccion` | Recomendación | Plan de las próximas 4 semanas para los 10 catálogos principales |

El titular es P3, no "X % mejor que el ingenuo" (la mejora frente al ingenuo sigue sin ser concluyente).
Los títulos del póster usan punto de miles (`miles()`); los del notebook siguen con coma, como en §3–§6.

### 4.3 Índice
Las 14 gráficas del plan §7.2 quedan cubiertas con 26 archivos (4 de póster) + 11 complementarias. Ver `docs/7_indice_figuras.csv`.

## 5. Tablas en `procesado/`

| CSV | Grano | Nota |
|---|---|---|
| `7_pronostico_vigente_catalogo.csv` | catálogo × semana (8) | `pred`, `pred_modelo`, `pred_ingenuo`, `lo`, `hi`, `revisar`, `segmento` |
| `7_pronostico_vigente_talla_color.csv` | catálogo top × semana × talla × color | `prop`, `pred_tc` |
| `7_pronostico_vigente_tela.csv` | semana × género × tela × color | `pred_tela` (top + cola) |
| `7_revision_vs_ingenuo.csv` | catálogo top | Suma de 4 semanas, `dif_rel`, `dif_uds`, `revisar` |

Figuras: `7_2_01_pronostico_catalogo_semana`, `7_2_02_pronostico_catalogo_talla`, `7_2_03_pronostico_tela`, `7_2_04_historia_y_pronostico`.

## 6. ⚠️ Lo que el agente de §8 tiene que saber

1. **Las tablas `7_pronostico_vigente_*` no son la salida oficial.** §8 debe separar entrenar / guardar (`joblib`) / pronosticar con
   `ajustar_hgb(ctx, corte)` + `pronostico_recursivo(..., redondear=True)`. Con la misma semilla y el mismo corte debe reproducir `pron_vigente["pred_modelo"]`: úsenlo como prueba.
2. **Guarden el modelo con `early_stopping=False`.** Verifiquen `modelo.n_iter_ == 300` después de entrenar.
3. **Publicar el ingenuo al lado** y la columna `revisar` ya están resueltos en `pron_vigente`; reutilicen la lógica de 7.2.1.
4. **Semana parcial:** el horizonte empieza el 5-oct, semana de la que ya hay 2 días de datos (5–6 oct). Se pronostica completa; díganlo en la guía.
5. **Black Friday (27-nov)** queda fuera de las 8 semanas; si extienden el horizonte, el modelo nunca vio esa fecha (limitación).
6. **Póster:** faltan el diagrama del método y el número grande. P1–P4 ya tienen letra para A0/A1; el PDF es vectorial.

## 7. Fallos conocidos que no se corrigieron

- **§6.8 con `RECALCULAR_BACKTESTING = False`:** `bt.drop(columns=["segundos"])` falla porque el CSV no trae esa columna. Arreglo de una palabra:
  `drop(columns=["segundos"], errors="ignore")` (también en `ho`). Con `True` (valor por defecto) no pasa.
- **Nombres duplicados en el top:** aparecen "CUELLO ALTO RED BULL" y "RED BULL", y "CA COLOMBIA ÉLITE" y "COLOMBIA ELITE/CLASICO". Revisen si la normalización de §4.1 debería unirlos.
- **plotly:** el plan sugiere gráficas interactivas, pero plotly no está en `requirements.txt`; no se agregó.

## 8. Decisiones que el grupo debería revisar

- **Corrección de `early_stopping`** (§2): cambia cifras del holdout ya reportadas. Es un error corregido, no una selección con el holdout; díganlo así.
- **Umbrales de revisión manual** (50 % y 10 uds): son de criterio.
- **Titular del póster** (P3): elegido por honestidad; el grupo puede preferir otro.
- **Textos:** todo el markdown de §7 es un borrador técnico. **Redáctenlo con palabras propias** (riesgo Turnitin).

## 9. Reproducir la ejecución

*Run all* desde la celda 0, con el mismo venv de los agentes 02–04.
