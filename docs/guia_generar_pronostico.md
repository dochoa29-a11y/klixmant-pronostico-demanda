# Guía: cómo generar un pronóstico de demanda

> ✍️ **Borrador técnico (agente 06, 4-nov-2026).** El grupo debe redactarlo con sus propias palabras antes de entregarlo (Turnitin).
> Las cifras de ejemplo son de la corrida con corte al 28-sep-2026.

**Para quién:** la persona de Klixmant que planea compras de tela y cortes. **Cada cuánto:** cada semana (lunes) para el pronóstico,
cada mes para reentrenar el modelo. **Tiempo:** unos 20 minutos de computador; la revisión manual depende de cuántos catálogos se marquen.

---

## 1. Qué se necesita

| Cosa | Detalle |
|---|---|
| Exportación de pedidos | El Excel de Klixmant con la hoja **`PEDIDOS`** y las mismas columnas del archivo `Klixmant_Base_de_Datos_UNAB_2026-10-07.xlsx` (en especial `fecha_remision`, `cantidad_total`, `catalogo`, `referencia`, `talla`, `color`, `canal`, `estado_actual`). También se leen las hojas `CATALOGOS` y `TALLAS`. |
| Nombre del archivo | El notebook busca `NOMBRE_EXCEL` (celda 0.1) en `datos/` o en la raíz del proyecto. Si el archivo nuevo tiene otro nombre, se cambia esa línea. |
| Entorno | Python 3.12 o superior con las librerías de `requirements.txt` (pandas ≥ 3, scikit-learn, statsmodels, joblib, pyarrow). En Google Colab ya vienen casi todas. |
| Modelo guardado | `modelos/hgb_final.joblib` y `modelos/metadata.json` (los genera la celda 8.1). |

> ⚠️ La sección 3.1 del notebook **cuadra las cifras de control** de la documentación de Klixmant de 2026-10-07. Con un archivo nuevo esas
> cifras cambian: hay que actualizar `CONTROL` (celda 3.1.1), `CONTROL_MENSUAL` (3.1.2) y `CONTROL_TOP15` (3.1.3) con las cifras de la
> documentación nueva, o el notebook se detiene en el `assert` de la celda 3.1.4. Si Klixmant no entrega cifras de control, se puede
> comentar ese `assert`, pero se pierde la verificación de que la lectura es correcta.

## 2. Qué limpieza se aplica (automática)

El notebook aplica las mismas reglas de §4.1 a cualquier exportación nueva:

1. Se excluyen las líneas **canceladas**; las devoluciones no se usan como señal.
2. El tiempo es **`fecha_remision`** (nunca `fecha_carga`), en semanas de lunes a domingo. La semana en curso queda como **parcial** y no se usa para entrenar.
3. Se **normalizan los nombres de catálogo** (espacios, mayúsculas, errores como `ALLTO` → `ALTO`, `BAYER` → `BAYERN`). KTM y AKT no se fusionan.
4. La **talla** se estandariza a la sigla oficial aunque venga como texto libre de Dropi.
5. La **referencia** se separa en género (H/D), tela (16 códigos) y color.
6. Se agregan **ceros explícitos** en las semanas sin venta desde la primera venta de cada catálogo.

Si aparece un error de digitación nuevo en los nombres, se agrega a la regla de la celda 4.1.1 y se revisa `procesado/4_mapa_nombres_catalogo.csv`.

## 3. Pasos

### 3.1 Pronóstico semanal (sin reentrenar)

1. Copiar la exportación nueva en `datos/` (o en la raíz).
2. Si hay eventos nuevos (festivos, fechas comerciales, un torneo), **actualizar el calendario** (paso 3.3).
3. Abrir `Klixmant_Pronostico_Demanda.ipynb` y ejecutar **Run all**. Para ahorrar tiempo, en la celda 6.1 se puede poner
   `RECALCULAR_BACKTESTING = False` (lee el backtesting ya guardado).
4. La celda **8.2** carga el modelo con `cargar_modelo()` y llama a `generar_pronostico(modelo, corte, h)`:

   ```python
   modelo, meta = cargar_modelo()                        # verifica sha256, 300 iteraciones y variables
   pronostico = generar_pronostico(modelo, ULTIMA_SEMANA_COMPLETA, h=8)
   pronostico["catalogo"]      # catálogo × semana
   pronostico["talla_color"]   # top 20 × semana × talla × color
   pronostico["tela"]          # semana × género × tela × color (insumo)
   pronostico["revision"]      # top 20: modelo vs ingenuo en 4 semanas
   ```

   `corte` es siempre la **última semana completa** (el lunes de la última semana que ya terminó). El pronóstico arranca la semana siguiente.
5. Las tablas quedan en `procesado/8_pronostico_*.csv` (ver §4).

> **Modelo guardado vs. datos nuevos.** Si el modelo guardado se entrenó con un corte anterior, igual sirve: usa los rezagos y medias
> de los datos nuevos. Pero no conoce catálogos que hayan nacido después de su corte (los trata con sus variables, sin identidad propia)
> ni cambios de tendencia recientes. Por eso se reentrena cada mes.

### 3.2 Reentrenar (una vez al mes, o después de un evento)

La celda **8.1** entrena con toda la historia hasta `ULTIMA_SEMANA_COMPLETA`, comprueba `n_iter_ == 300` (sin *early stopping*) y
sobrescribe `modelos/hgb_final.joblib` y `modelos/metadata.json`. Como *Run all* ejecuta 8.1 antes de 8.2, cada corrida completa reentrena.
Antes de usar un modelo reentrenado, revisar en §6 que el WAPE del backtesting no empeoró de forma notable.

Guarden una copia del `.joblib` anterior con la fecha (p. ej. `hgb_final_2026-09-28.joblib`) por si hay que volver atrás.

### 3.3 Actualizar el calendario de eventos

- **Festivos y fechas comerciales:** celda 3.3 (`FESTIVOS_2026` y `FECHAS_COMERCIALES`). El calendario semanal del modelo (`cal_modelo`, celda 4.3.2)
  debe cubrir el horizonte: hoy llega hasta el 30-nov-2026. Para pronosticar diciembre hay que extenderlo.
- **Un evento nuevo como el Mundial:** el modelo **no puede aprender un evento que nunca vio**. Lo correcto es el **ajuste experto**
  (paso 5): estimar a mano cuánto suma el evento a los catálogos afectados, apoyándose en lo que pasó con el Mundial (§4.5: el evento fue
  el 87 % de lo que vendió la familia Colombia en esas semanas y el pico empezó dos semanas antes del torneo).
- **Black Friday (27-nov):** cae fuera de las 8 semanas del pronóstico con corte al 28-sep y el modelo nunca vio uno. Si se pronostica esa semana, ajustar a mano.

## 4. Qué salida produce y cómo leerla

| Archivo | Grano | Columnas clave | Para quién |
|---|---|---|---|
| `procesado/8_pronostico_catalogo.csv` | catálogo × semana (8 semanas) | `pred` (publicado), `pred_modelo`, `pred_ingenuo`, `lo`, `hi`, `revisar`, `segmento`, `h` | Planeación |
| `procesado/8_pronostico_talla_color.csv` | catálogo del top × semana × talla × color | `pred_tc`, `prop` | Corte |
| `procesado/8_pronostico_tela.csv` | semana × género × tela × color | `pred_tela` (top + cola) | Compras de insumo |
| `procesado/8_revision_vs_ingenuo.csv` | catálogo del top | suma de 4 semanas de modelo e ingenuo, `dif_rel`, `revisar` | Revisión manual |

**Cómo leerla:**

- **`pred`** es el número a usar: el modelo en el **top 20** y el ingenuo (repetir la última semana) en la **cola**.
- **`h`** = semanas hacia adelante. Las **4 primeras** son el horizonte principal; de la 5 a la 8 son orientativas (el error crece con *h*: WAPE 0,55 en *h* = 1 y 1,24 en *h* = 4 en el backtesting).
- **`lo` – `hi`** es el intervalo 10–90 % (solo top). Es **conservador** fuera de eventos (cubrió el 92 % en el holdout): sirve como cota de stock de seguridad. **En un evento es demasiado angosto** (63 %).
- **`pred_ingenuo`** se publica al lado como referencia. Si `revisar = True`, el modelo y el ingenuo difieren más del 50 % y en al menos 10 unidades en las 4 semanas: **revisar a mano antes de cortar** (caso Honda Reflectivo del holdout: el modelo extrapoló un récord).
- **Talla × color** reparte el pronóstico de cada catálogo con su mezcla de las últimas 12 semanas. Sumado en 4 semanas el error es razonable (WAPE 0,67); semana a semana es alto: úsenlo para planear el corte del mes, no de cada semana.
- **Tela** suma todos los catálogos (top + cola) con la proporción de tela de cada uno. Es lo que se compra.
- La **primera semana** del pronóstico puede estar en curso (con corte al 28-sep, la semana del 5-oct ya tenía 2 días de datos). Se pronostica completa.

## 5. Revisión y ajuste experto

1. Abrir `8_revision_vs_ingenuo.csv` y mirar los catálogos con `revisar = True` (con corte al 28-sep: ninguno).
2. Para cada uno, comparar la historia reciente: ¿la última semana fue un récord? ¿hubo un pedido grande puntual? Si sí, usar algo entre el modelo y el ingenuo.
3. **Eventos conocidos** (Black Friday, un lanzamiento, un torneo): aplicar un porcentaje por semana a los catálogos afectados y anotar la razón.
   La app Streamlit (página "Plan de producción") permite probar ese ajuste en pantalla sin cambiar los archivos.
4. **Catálogos nuevos** (que nacieron después del corte) no tienen pronóstico: se planean a mano. En el backtesting fueron el 27 % de las unidades de la cola.

## 6. Cuándo reentrenar o desconfiar

- **Reentrenar cada mes**, y siempre después de un evento grande.
- **Desconfiar** si: (a) el sesgo de las últimas 4 semanas (pronóstico − real) supera ±30 %; (b) muchos catálogos quedan marcados `revisar`;
  (c) cambia el portafolio (líneas nuevas, precios, pauta) o hay un evento que el modelo no conoce.
- Detalles y cifras en `docs/model_card.md`.

## 7. Problemas frecuentes

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| Se detiene en la celda 3.1.4 | Las cifras de control son de la exportación anterior | Actualizar `CONTROL`, `CONTROL_MENSUAL` y `CONTROL_TOP15` (3.1.1–3.1.3) |
| `No se encontró …xlsx` | Nombre o carpeta del Excel | Cambiar `NOMBRE_EXCEL` (0.1) o mover el archivo |
| `n_iter_ = 10` en 8.1 | `early_stopping` volvió a `"auto"` | Revisar `PARAMS_HGB` en 5.3.1 (`early_stopping=False`) |
| `El archivo del modelo no coincide con la metadata` | Se reemplazó el `.joblib` sin la metadata | Volver a correr 8.1 |
| Aviso de versión de scikit-learn | El modelo se guardó con otra versión | Reentrenar con 8.1 en el entorno actual |
| El pronóstico de un catálogo se ve el doble de su récord | Tope de 2 × la mejor semana (salvaguarda) | Revisión manual (§5) |
