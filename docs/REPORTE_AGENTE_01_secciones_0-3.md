# Reporte de traspaso — Agente 01 (secciones 0 a 3)

**Fecha:** 3-nov-2026 · **Alcance:** §1 Marco CRISP-DM, §2 Negocio, §3 Entendimiento de los datos (cuadre + EDA + calendario).
**No se hizo nada de §4 en adelante.** Ese trabajo es del siguiente agente.

---

## 1. Qué se entregó

| Archivo | Qué es |
|---|---|
| `Klixmant_Pronostico_Demanda.ipynb` | **Notebook global.** Secciones 0–3 completas y ejecutadas; 4–8 son encabezados vacíos marcados ⏳ |
| `requirements.txt` | Librerías mínimas |
| `figuras/3_*.png` | 14 gráficas del EDA (prefijo = sección) |
| `procesado/3_*.csv` | 11 tablas intermedias (ver §4 de este reporte) |
| `datos/`, `modelos/`, `docs/` | Carpetas creadas (vacías salvo este reporte) |

El Excel original **sigue en la raíz** del proyecto (no se movió). El notebook lo busca en `datos/` y después en la raíz, así que se puede mover a `datos/` sin cambiar código.

**Ejecución verificada:** se corrió en local de principio a fin (`nbconvert --execute`), sin errores ni warnings, en Python 3.14.7 / pandas 3.1.0 / statsmodels 0.15.0. Tarda unos 2 minutos, casi todo en leer el Excel.

## 2. Cómo está armado el notebook (convenciones que hay que respetar)

**Sección 0, que se usa en todo el notebook:**
- **0.1 Entorno.** `EN_COLAB` detecta Colab. En Colab monta Drive en `/content/drive` y busca el Excel en `RUTA_DRIVE = "/content/drive/MyDrive/Trabajo final Klixmant S.A.S"` y después hasta 2 niveles dentro de `MyDrive/` y `Shareddrives/`. Si no lo encuentra, descarga la carpeta compartida (`DRIVE_FOLDER_ID = 19HmUVRpHptxeVwAI32HIwC5_zZ1NGYgO`) con `gdown` en `/content/klixmant`; ahí los resultados no persisten. **Cada integrante debe agregar la carpeta compartida como acceso directo en "Mi unidad".** Si el acceso directo tiene otro nombre, se cambia `RUTA_DRIVE`.
- **0.2 `RUTAS`** es un dict con las rutas `datos/procesado/modelos/figuras/docs`. Guarden siempre ahí, nunca con rutas escritas a mano.
- **0.4** Paleta Okabe-Ito, `COLOR_CANAL`, `COLOR_FAMILIA`, `FMT_MES` (meses en español en ejes de fecha), `guardar_fig(fig, "4_x_nn_nombre")` y `sombrear_mundial(ax)`.
- **0.5 `DECISIONES`** guarda las decisiones de §2 (catálogo, top 20, semana `W-MON`, horizonte 4/8, `fecha_remision`, `cantidad_total`, se excluye `CANCELADO`, corte 6-oct). También están `EVENTOS` (11-jun a 19-jul), `EVENTOS_PARTIDOS` y `FAMILIA_COLOMBIA_REGEX`.
- **0.6 Funciones:** `cargar_pedidos()` (lee PEDIDOS con caché), `cargar_hoja(nombre)` (encabezado en la fila 4 de Excel), `inicio_semana()`, `demanda(df)` (quita canceladas), `talla_estandar()` y `referencia_base()`.

**Variables del EDA que quedan en memoria:** `pedidos`, `dem` (demanda con `fecha`, `semana`, `familia`, `talla_std`, `referencia_base`, `mes`), `sem_canal`, `sem_cat` (catálogo × semana completa), `abc`, `clasif`, `vida`, `estab`, `cal`, `cal_sem`, `SEMANA_PARCIAL`.

**Convención de nombres:** las figuras y CSV llevan el número de sección como prefijo (`4_...`, `5_...`).

## 3. Resultados clave del EDA (cifras del notebook)

**Cuadre §3.1: ✅ completo.** Cuadran exactamente las 12 cifras globales: 29.899 líneas, 29.919 unidades, 21.826 remisiones, 806 catálogos, 435 cortes, 4.061 devoluciones, 370 canceladas, 266 días, Effi 21.877, Dropi 8.042, 216 fechas de carga y 29.514 despachadas. También cuadran la tabla mensual completa (0 celdas distintas) y el top 15 (71,4 %). La celda 3.1.4 tiene `assert`: si la lectura falla, el notebook se detiene.

| Tema | Hallazgo |
|---|---|
| Demanda modelable | 29.549 unidades sin canceladas; **38 semanas completas** + 1 parcial (5–6 oct) |
| Concentración | Top 15 = 71,5 %; **top 20 = 76,9 %**; 25 catálogos clase A (80 %); 707 catálogos clase C = 5 % |
| ADI/CV² (semanal) | Base: 601 *insuficiente* (< 2 semanas con venta), 124 intermitente, 44 irregular, 19 errática, 10 suave. **Top 20: 8 errática, 5 suave, 5 irregular, 2 intermitente.** Las motos (Honda, Yamaha, Suzuki, Pulsar, KTM) son *suaves*; los catálogos de Colombia son *erráticos o irregulares* |
| Mundial | Familia Colombia (28 catálogos, 42,3 % de las unidades): semana promedio **×3,0 durante** el Mundial frente a antes, y **×0,01 después** (≈4 uds/semana: la demanda desaparece). El resto **cae a ×0,71 durante** (canibalización o capacidad) y vuelve a ×1,03 después |
| Pico | Empieza **antes** del 11-jun (fin de mayo y primera semana de junio). Las ventas en el día del partido **no** suben frente a los ±3 días: el efecto es de temporada, no del día del partido |
| Tendencia y patrón semanal | STL diaria: fuerza de tendencia 0,81, patrón semanal 0,45. Serie semanal: ADF/KPSS no concluyentes en nivel; **estacionaria en 1.ª diferencia** |
| Quincena | Sin Mundial, los días de quincena ±1 venden **menos** (87,5 frente a 103,3 uds/día). No hay efecto quincena positivo |
| Canales | Dropi desde el 1-feb. Participación: 23 % antes, **41 % durante** y 19 % después. COLOMBIA ÉLITE es 81 % Dropi; COLOMBIA ELITE/CLASICO es 100 % Effi |
| Talla/color | Mezcla de tallas estable en el top 20 (distancia TV media 0,09); el color es algo menos estable (hasta 0,20 en CUELLO ALTO COLOMBIA). Sirve para la desagregación *top-down* con ventana reciente |
| Ciclo de vida | 618 de 804 catálogos viven 1 sola semana (personalizados/pedidos únicos). 615 inactivos (sin venta en 4 semanas), 189 activos (82 % del volumen). Salen 54–118 catálogos nuevos por mes |
| fecha_carga | Confirmado: 216 días frente a 266, con picos artificiales (figura `3_1_01`) |

## 4. Tablas en `procesado/` (insumos para §4)

| CSV | Grano | Nota |
|---|---|---|
| `3_demanda_diaria_catalogo_canal.csv` | fecha × catálogo × canal | sin canceladas |
| `3_demanda_semanal_catalogo.csv` | semana × catálogo | **sin ceros explícitos**; columna `semana_parcial` |
| `3_demanda_semanal_catalogo_talla_color.csv` | semana × catálogo × `talla_std` × color | talla ya estandarizada |
| `3_serie_semanal_canal.csv` | semana | EFFI, DROPI, TOTAL, parcial |
| `3_clasificacion_catalogos.csv` | catálogo | ADI, CV2, tipo, método sugerido, ABC, rank, primera/última venta, estado, familia (798 filas: los 6 que solo venden en la semana parcial no se clasifican) |
| `3_estabilidad_mezcla_top.csv` | catálogo top 20 | TV talla y color |
| `3_referencias_base.csv` | referencia sin color | unidades, catálogos, % familia Colombia |
| `3_calendario_eventos_diario.csv` / `_semanal.csv` | día / semana, del 12-ene al 6-dic-2026 | festivos, Mundial, partidos de Colombia, fechas comerciales, quincena, prima, `con_historia` (cubre el horizonte de 8 semanas) |
| `3_candidatos_nombres_duplicados.csv` | pares de catálogos | 14 candidatos por similitud |
| `3_cuadre_cifras_control.csv` | cifra | evidencia del cuadre |

## 5. ⚠️ Problemas de datos que §4 debe resolver

1. **`talla` es texto libre en Dropi.** Hay 358 valores crudos (p. ej. `MARFIL/M – HOMBRE/`, `HOMBRE L/NEGRO/`), casi todos de Dropi (7.963 líneas). `talla_estandar()` extrae la sigla oficial de la hoja TALLAS y recupera el 100 % (0 ambiguas, 2 sin talla). **§4 debe validar esta regla y adoptarla.** Ese texto también trae género (HOMBRE/DAMA) y color: comprobar si coincide con `color` y con el prefijo H/D de `referencia`.
2. **`referencia` no son 16 telas.** El campo trae tela + color (`H N L NEGRO`): son 124 valores. Sin el color quedan 33 `referencia_base` (más algunos códigos pegados, como `HNLMARFILLBOR`). La primera letra parece ser género (H/D) y el segundo token la tela (N, CO90, R, MAR…). Definir con criterio cuál es "la tela" para agregar la compra de insumo y confirmarlo con Klixmant si se puede.
3. **Nombres de catálogo duplicados:**
   - `CUELLO ALTO BARCELONA` aparece dos veces (difieren en espacios).
   - `BAYERN MUNICH` / `BAYER MUNICH`.
   - Varios `PERSONALIZADO` mal escritos.
   - **`KTM` frente a `AKT` NO son duplicados** (son marcas distintas), igual que `KAWASAKI` frente a `KAWASAKI SIN REFLECTIVO`.
   - `CUELLO ALLTO PULSAR` no tiene un gemelo "ALTO" con venta, pero conviene normalizarlo.
   - Revisar el CSV a mano antes de fusionar.
4. **Ficha `CATALOGOS`:** solo 233 de 803 catálogos con venta tienen ficha (89,4 % del volumen). En el top 20 faltan `COLOMBIA ELITE/CLASICO` y `RED BULL`. Las variables estáticas (proceso, puntadas, planchadas) necesitan imputación o una categoría "sin ficha".
5. **10 líneas sin catálogo** y 2 sin talla/color. Hay 24 líneas con `descarte = 1` (ninguna cancelada): falta decidir si cuentan como demanda (hoy **sí** cuentan).
6. Hay 15 líneas en estados pendientes (CONFECCION/ALISTAMIENTO): hoy cuentan como demanda.
7. Faltan los **ceros explícitos** en semanas sin venta de catálogos activos. Hay que rellenarlos en §4 (`sem_cat` ya los trae, pero el CSV semanal no).
8. **Devoluciones** de agosto en adelante: no usarlas como señal (advertencia 3).

## 6. Recomendaciones para §4–§5 que salen del EDA

- **Variables de evento:** el pico arranca ~2 semanas **antes** del 11-jun. Usen semanas antes y después del evento, no solo `semana_mundial`. `n_partidos_colombia` por día no mostró efecto; por semana, pruébenla igual.
- **Variable de familia Colombia** (o un clúster K-means de "catálogos de evento"): es lo que separa base de evento. Después del Mundial su demanda base es ≈0. El modelo **no** debe arrastrar el nivel de junio.
- **Quincena:** no la asuman positiva; el EDA muestra lo contrario.
- **Canal:** el peso de Dropi cambia mucho con el evento. Incluir `%_dropi` rezagado o probar un modelo por canal.
- **Cola** (601 *insuficientes* + 124 intermitentes): aplicar una regla (media móvil / SBA). No se modelan.
- **Desagregación:** como la mezcla de tallas es estable, sirven proporciones de las últimas 8–12 semanas.
- **Horizonte sin historia:** `cal_sem.con_historia = 0` a partir del 5-oct. Black Friday (27-nov) cae dentro del horizonte de 8 semanas.

## 7. Pendientes del grupo (no técnicos)

- Confirmar con el docente la decisión **catálogo vs. referencia** (§2), con los números de la celda 2.1–2.2.
- Verificar en FIFA.com la fecha del partido Colombia vs. RD Congo (23-jun, Guadalajara). Las otras 4 fechas se verificaron en prensa: 17-jun vs Uzbekistán 3-1, 27-jun vs Portugal 0-0, 3-jul vs Ghana 1-0 (dieciseisavos), 7-jul vs Suiza 0-0 y 3-4 en penales (octavos, eliminación).
- Revisar si el Syllabus o la Guía traen una rúbrica del Trabajo Final.
- **Redactar con palabras propias** todo el texto markdown del notebook (riesgo Turnitin). El texto actual es un borrador técnico.
