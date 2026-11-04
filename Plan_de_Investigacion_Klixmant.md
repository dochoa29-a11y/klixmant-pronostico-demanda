# Plan de investigación — Pronóstico de demanda Klixmant S.A.S.

**Curso:** Analítica de Marketing (TEMA UNAB, curso 2228) · **Actividad:** Trabajo Final (U4) · **Entrega:** 12 de noviembre de 2026
**Grupo:** hasta 4 personas · **Producto:** modelo en sklearn, keras o pytorch, documentación para pronosticar con él y póster del proceso

> Este documento es una **guía de investigación y decisiones**, no el informe final. No contiene código. El grupo debe redactar con sus propias palabras el notebook, la documentación y el póster: el curso revisa las entregas con Turnitin, y si la probabilidad de IA supera el 70 % se exige una defensa oral o se califica con 1.0.

---

## Índice

0. [Lo que dice el curso: metodología y temas vistos](#0-lo-que-dice-el-curso)
1. [Marco de trabajo (CRISP-DM)](#1-marco-de-trabajo)
2. [Entendimiento del negocio y definición del problema](#2-entendimiento-del-negocio)
3. [Entendimiento de los datos (EDA)](#3-entendimiento-de-los-datos-eda)
4. [Preparación de datos e ingeniería de variables](#4-preparación-de-datos-e-ingeniería-de-variables)
5. [Selección de modelos según el dataset](#5-selección-de-modelos)
6. [Validación y métricas](#6-validación-y-métricas)
7. [Graficación](#7-graficación)
8. [Documentación y "despliegue" del modelo](#8-documentación-y-despliegue)
9. [Póster](#9-póster)
10. [Cronograma, reparto y riesgos](#10-cronograma-reparto-y-riesgos)
11. [Bibliografía y fuentes](#11-bibliografía-y-fuentes)

---

## 0. Lo que dice el curso

### Temas vistos (según el aula de TEMA)

| Unidad | Contenidos | Cómo se usa en este trabajo |
|---|---|---|
| U1 · Intro a ML en marketing | Artículos: LDA, **LSTM**, *Attention is all you need*, CNN, GFlowNets | LSTM como modelo de comparación (deep learning) |
| U2 · Supervisados | Regresión lineal múltiple, logística, KNN, **árboles de decisión**, SVM, YOLO, **ARIMA, autocorrelación, descomposición de series**; competencias Kaggle de churn, **predicción de demanda**, mailing y **Bimbo** | Es el núcleo: líneas base estadísticas, árboles/boosting y un análisis de series al estilo de clase |
| U3 · No supervisados | LDA y **K-means** sobre texto | K-means para agrupar catálogos por perfil de demanda |
| U4 · Tópicos avanzados | Notebooks: Amazon reviews, Spotify, **Supermercado**, **Supermercado regresión** | Referencia de estilo para el notebook final |

### Cómo se trabaja

- **Notebooks prácticos** (Colab/Kaggle) sobre casos de marketing. El profesor comparte un notebook por técnica.
- **Lectura de papers** con presentación grupal en PDF (Quiz 1.1, Quiz 2.2).
- **Envíos tardíos a Kaggle**: se entrega un pantallazo del score y el enlace al notebook (Quiz 2.1, Proyecto 1). La métrica objetiva importa.
- **Comunicación de resultados**: video en el Proyecto 1 y **póster** en el Trabajo Final.
- **Escala de 0 a 5.** Grupos de hasta 4 personas.

> **Pendiente del grupo:** el *Syllabus*, la *Guía de aprendizaje* y la *Unidad 0* no se pudieron leer por el conector. Revísenlos a mano para confirmar si hay una **rúbrica del Trabajo Final** o un formato de póster, y ajusten este plan si es necesario.

---

## 1. Marco de trabajo

**Decisión:** usar **CRISP-DM** (Cross-Industry Standard Process for Data Mining) como columna vertebral del notebook, de la documentación y del póster.

| Fase CRISP-DM | Sección de este plan | Producto |
|---|---|---|
| Entendimiento del negocio | §2 | Pregunta de negocio, unidad de pronóstico, horizonte |
| Entendimiento de los datos | §3 | EDA, cifras de control, clasificación de catálogos |
| Preparación | §4 | Tabla semanal limpia y variables |
| Modelado | §5 | Líneas base, modelo principal y comparación |
| Evaluación | §6 | Backtesting, métricas por segmento |
| Despliegue | §8 | Modelo guardado, guía de uso, *model card* |

**Por qué:** es el estándar más usado en la industria, encaja con la lógica de los notebooks del curso y da una narrativa lista para el póster.

**Reproducibilidad (lista de verificación):**
- Un solo notebook principal, numerado por fases, con texto que explique cada decisión.
- Versiones de librerías anotadas y semilla aleatoria fija.
- Carpetas separadas: `datos/` (original, sin tocar), `procesado/`, `modelos/`, `figuras/`, `docs/`.
- El Excel original nunca se modifica. Las hojas de resumen se recalculan con fórmulas, así que se debe leer `PEDIDOS` directamente.

**Fuente:** Chapman, P. et al. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. SPSS.

---

## 2. Entendimiento del negocio

### 2.1 El problema real (según Klixmant)
Hoy se compra insumo y se programa la confección **mirando el agregado y con criterio, sin modelo**. Cuando termina un evento (el Mundial), **el inventario queda comprado**. Klixmant pide:
1. Un pronóstico **por catálogo**.
2. Que **separe la demanda base de la demanda por evento**.
3. Que llegue al nivel de **talla y color**, que es como se corta la tela.

### 2.2 Decisiones a tomar

| Pregunta | Opciones | Recomendación | Justificación |
|---|---|---|---|
| ¿Qué se pronostica? | Referencia (16 telas) · Catálogo (806) · SKU | **Catálogo**, con agregación a referencia para insumo y desagregación a talla y color | El enunciado dice "referencia", pero en Klixmsoft referencia = tela base. Pronosticar 16 series no sirve para producción (advertencia 4 de la documentación) |
| ¿Qué catálogos se modelan? | Los 806 · Top N | **Top 15–20** (≈71–75 % del volumen); el resto **por regla** | Lo sugiere la empresa. La cola es intermitente y tiene poca señal |
| Granularidad temporal | Diaria · Semanal · Mensual | **Semanal** (lunes a domingo, como `RESUMEN_SEMANAL`); el análisis diario solo se usa en el EDA | 9 meses de datos: la serie mensual tiene 9 puntos y la diaria por catálogo está llena de ceros |
| Horizonte | 1 · 4 · 8 semanas | **4 semanas** como principal, **8** como extendido | Tiempo suficiente para comprar insumo y planear cortes. El ciclo de fábrica es corto (mediana 0,4 días) |
| ¿Qué es "demanda"? | Todas las líneas · Sin canceladas · Neta de devoluciones | **Unidades (`cantidad_total`) de líneas no canceladas, por `fecha_remision`** | Las canceladas no llegan a producirse. Las devoluciones sí se produjeron, así que cuentan como demanda; aparte se reporta la tasa de devolución |
| ¿Un modelo por canal? | Total · Effi / Dropi por separado | **Total por catálogo** con el canal como variable. Revisar si conviene separar | Dropi arranca en febrero y tiene otro comportamiento |

> **Acción:** confirmar con el docente la decisión catálogo frente a referencia antes del 5-nov. La documentación de Klixmant dice que el punto está "pendiente de conversar entre Klixmant y la universidad".

**Fuentes:** Hyndman, R. J. y Athanasopoulos, G. (2021). *Forecasting: Principles and Practice* (3.ª ed.), cap. 1 ("Getting started") y cap. 5 ("The forecaster's toolbox"). OTexts. https://otexts.com/fpp3/

---

## 3. Entendimiento de los datos (EDA)

### 3.1 Cuadre contra las cifras de control (obligatorio)
Antes de analizar nada, reproducir con `PEDIDOS`:
- 29.899 líneas, 29.919 unidades, 21.826 remisiones, 806 catálogos con venta.
- La tabla mensual por canal (por ejemplo, junio = 7.346 unidades; Effi 21.877 y Dropi 8.042).
- El top 15 de catálogos (CUELLO ALTO COLOMBIA RETRO = 6.445 unidades = 21,5 %).

Si algo no cuadra, el error es de lectura o de filtro y hay que corregirlo antes de seguir. Este cuadre también va en el notebook como evidencia de calidad.

### 3.2 Preguntas que debe responder el EDA

| # | Pregunta | Análisis | Gráfica (ver §7) |
|---|---|---|---|
| 1 | ¿Qué tan concentrada está la demanda? | Pareto / clasificación **ABC** | Curva de Pareto |
| 2 | ¿Qué tipo de demanda tiene cada catálogo? | Clasificación **ADI / CV²** de Syntetos-Boylan | Dispersión ADI vs CV² en cuatro cuadrantes |
| 3 | ¿Hay tendencia o estacionalidad? | Descomposición **STL**, **ACF / PACF**, pruebas **ADF / KPSS** (como en U2) | STL y correlograma |
| 4 | ¿Cuánto pesó el Mundial? | Comparar la familia "Colombia" con el resto, antes, durante y después del 11-jun al 19-jul | Serie con bandas sombreadas del evento |
| 5 | ¿Hay patrón semanal o quincenal? | Venta por día de la semana y por día del mes (quincenas 15/30) | Heatmap semana × día |
| 6 | ¿Cómo se comportan los canales? | Effi vs Dropi en el tiempo; Dropi empieza en febrero | Líneas por canal |
| 7 | ¿Cómo se reparte talla y color dentro de cada catálogo? ¿Es estable? | Proporciones por mes | Barras apiladas al 100 % |
| 8 | ¿Nacen y mueren catálogos? | Primera y última fecha de venta por catálogo | Línea de vida / histograma |

### 3.3 Clasificación ADI / CV² (Syntetos, Boylan y Croston, 2005)
- **ADI** (Average Demand Interval) = número de periodos / número de periodos con demanda.
- **CV²** = (desviación estándar / media)² de la demanda **cuando hay venta**.
- Umbrales: **ADI = 1,32**, **CV² = 0,49**.

| Tipo | ADI | CV² | Método sugerido |
|---|---|---|---|
| Suave | < 1,32 | < 0,49 | Suavizamiento exponencial, ARIMA, ML |
| Errática | < 1,32 | ≥ 0,49 | ML con variables explicativas, métodos robustos |
| Intermitente | ≥ 1,32 | < 0,49 | Croston / SBA |
| Irregular (*lumpy*) | ≥ 1,32 | ≥ 0,49 | SBA / TSB, o reglas simples |

Esta tabla sirve para **justificar con datos** qué método se usa en cada grupo de catálogos. Es un argumento fuerte para el póster.

### 3.4 Calendario de eventos a construir (variables exógenas)
Hay que armarlo a mano y verificarlo con una fuente oficial:
- **Mundial 2026:** 11 de junio a 19 de julio. Partidos de Colombia (Grupo K): 17 de junio vs. Uzbekistán, 2.º partido vs. RD Congo en Guadalajara (verificar la fecha), 27 de junio vs. Portugal (0-0, primera del grupo), dieciseisavos el 3 de julio vs. Ghana. Si hubo más partidos, agregarlos.
- **Festivos de Colombia 2026:** 1 y 12 de enero; 23 de marzo; 2 y 3 de abril; 1 y 18 de mayo; 8, 15 y 29 de junio; 20 de julio; 7 y 17 de agosto; 12 de octubre (verificar en el calendario oficial). Junio concentra festivos, Mundial y prima, así que los efectos se mezclan.
- **Fechas comerciales:** Día de la Madre (10-may), **Día del Padre (21-jun, en pleno Mundial)**, Amor y Amistad (19-sep).
- **Pagos:** quincenas (15 y 30 de cada mes) y **prima de servicios** (a más tardar el 30 de junio y el 20 de diciembre).

> **Advertencia sobre el horizonte:** el pronóstico arranca después del 6 de octubre y entra en **Black Friday (27-nov), la prima de diciembre y Navidad**, temporadas **sin historia en los datos** (Klixmsoft empezó en enero de 2026). Hay que decirlo explícitamente como limitación y sugerir un ajuste por criterio experto.

**Fuentes:**
- Syntetos, A. A., Boylan, J. E. y Croston, J. D. (2005). On the categorization of demand patterns. *Journal of the Operational Research Society*, 56(5), 495–503. https://doi.org/10.1057/palgrave.jors.2601841
- FPP3, cap. 2 (gráficas de series), cap. 3 (descomposición, STL) y cap. 9 (estacionariedad, ACF/PACF, ARIMA).
- Documentación de `statsmodels`: STL, `acf`/`pacf`, `adfuller`, `kpss`.

---

## 4. Preparación de datos e ingeniería de variables

### 4.1 Limpieza y reglas (derivadas de las advertencias de Klixmant)

| Regla | Motivo |
|---|---|
| Eje de tiempo = **`fecha_remision`**, nunca `fecha_carga` | `fecha_carga` agrupa días por lote (216 fechas frente a 266 reales) |
| Volumen = **suma de `cantidad_total`**, no conteo de filas | Una línea puede traer más de una unidad |
| Excluir `estado_actual = CANCELADO` (370 líneas) | No es demanda que se produce |
| Revisar `descarte = 1` | Se descartó por calidad. Decidir si es demanda (sí la pidió un cliente) |
| **Octubre incompleto** (hasta el 6-oct): excluir esa semana o marcarla parcial | Si no, el modelo "aprende" una caída falsa |
| No usar `es_devolucion` de agosto en adelante como señal | Las devoluciones se marcan semanas después (advertencia 3) |
| Rellenar con **0** las semanas sin venta de un catálogo activo | Sin ceros explícitos los rezagos quedan mal calculados |
| Normalizar nombres de catálogo (p. ej. "CUELLO ALLTO PULSAR") | Hay errores de digitación que parten una serie en dos |
| Geografía solo para Effi | Dropi no trae destino (advertencia 2); no usarla como variable del total |

### 4.2 Estructura jerárquica
Total → Canal → Referencia (tela) → **Catálogo** → Talla × Color.
- Se modela el nivel **catálogo**.
- **Hacia arriba:** sumar para obtener la referencia (compra de tela) y el total.
- **Hacia abajo:** desagregar a talla y color con proporciones históricas recientes (*top-down*, §5.5).

### 4.3 Variables (features) para el modelo principal

| Grupo | Variables | Nota |
|---|---|---|
| Rezagos | Demanda t-1, t-2, t-3, t-4 | Calcular **solo con información pasada** (sin *leakage*) |
| Ventanas | Media y desviación móvil de 4 y 8 semanas | Desplazadas una semana |
| Calendario | Semana del año, mes, n.º de festivos en la semana, semana con quincena | Pocas semanas: preferir variables de evento a "mes" puro |
| Evento | Semana del Mundial (0/1), n.º de partidos de Colombia en la semana, semanas antes y después del evento | Clave para separar base y evento |
| Catálogo (estáticas) | Familia (Colombia / motos / marcas / otros), referencia (tela), tipo de proceso (bordado o estampado), puntadas, planchadas (hoja `CATALOGOS`) | Permiten que un **modelo global** comparta aprendizaje entre catálogos |
| Ciclo de vida | Semanas desde la primera venta | Diferencia lanzamientos de catálogos maduros |
| Canal | % Dropi en las últimas semanas | O un modelo por canal si el EDA lo justifica |
| Clúster | Grupo K-means del perfil de demanda (§4.4) | Conecta con U3 |

### 4.4 Clustering de perfiles de demanda (U3)
- Representar cada catálogo por su curva semanal **normalizada** (dividida por su total) y/o por indicadores (ADI, CV², % de la venta en junio y julio, tendencia).
- **K-means**, eligiendo k con el método del codo y la silueta.
- Uso: (a) variable para el modelo; (b) narrativa de negocio: "catálogos de evento", "catálogos base", "lanzamientos".

### 4.5 Separar demanda base de demanda de evento
Es **el problema central** según Klixmant. Hay dos caminos complementarios:
1. **Descomposición:** STL robusta sobre la serie de cada catálogo top; el componente atípico de junio y julio se trata como "evento".
2. **Variable de intervención** en el modelo: con las dummies del Mundial, el pronóstico **sin evento** (dummies en 0) da la demanda base. La diferencia con el pronóstico con evento cuantifica la demanda incremental.

Entregable: una gráfica por catálogo top con base y evento apilados, y una tabla "unidades incrementales por el Mundial".

**Fuentes:**
- FPP3, cap. 7 (regresión y predictores, *dummies* de intervención) y cap. 10 (regresión dinámica).
- Bandara, K., Bergmeir, C. y Smyl, S. (2020). Forecasting across time series databases using recurrent neural networks on groups of similar series: A clustering approach. *Expert Systems with Applications*, 140.
- Ejemplo de scikit-learn: *Time-related feature engineering* y *Lagged features for time series forecasting*.

---

## 5. Selección de modelos

### 5.1 Características del dataset que condicionan la elección

| Característica | Consecuencia |
|---|---|
| Historia corta (~38 semanas útiles) | Sin estacionalidad anual estimable. Los modelos muy flexibles (LSTM) se sobreajustan |
| Un evento atípico (Mundial) que no se repite en el horizonte | Hay que modelarlo de forma explícita o el pronóstico queda inflado |
| Alta concentración (top 15 = 71 %) | Esfuerzo de modelado en el top. Reglas simples para la cola |
| Cola intermitente | Métodos para demanda intermitente o agregación |
| Muchas series relacionadas (comparten tela, proceso, familia) | Un **modelo global** (uno para todas las series) aprovecha mejor la poca historia |
| Restricción del enunciado: sklearn, keras o pytorch | El modelo final debe estar en una de estas librerías |

### 5.2 Escalera de modelos (de simple a complejo)

| Nivel | Modelo | Librería | Rol |
|---|---|---|---|
| 0 | **Ingenuo** (última semana), **media móvil** de 4 semanas | Manual | Línea base obligatoria: si no se le gana, el modelo no aporta |
| 1 | **Suavizamiento exponencial (ETS)** y **ARIMA/SARIMAX** con dummy del Mundial | statsmodels | Referencia estadística (temas de U2) |
| 2 | **Modelo global de gradient boosting**: `HistGradientBoostingRegressor` con `loss="poisson"` | **scikit-learn** | **Modelo principal recomendado** |
| 2b | Random Forest / árbol de decisión global | scikit-learn | Comparación interpretable (U2) |
| 3 | **LSTM** global | **Keras** | Experimento de deep learning (U1); se reporta aunque no gane |
| Cola | **Croston / SBA / TSB** o media móvil por clúster | Manual / statsforecast | Catálogos intermitentes fuera del top |

### 5.3 Por qué el modelo principal es gradient boosting global en sklearn
- En la **competencia M5** (Walmart: 42.840 series jerárquicas de venta en unidades), el método ganador se basó en **modelos LightGBM directos y recursivos**. Las conclusiones del concurso fueron que el **ML superó a los métodos estadísticos**, que **entrenar a través de series (*cross-learning*) aporta** y que **combinar modelos mejora el resultado**.
- La competencia **Grupo Bimbo** (vista en clase) también fue ganada con árboles de gradiente y rezagos.
- `HistGradientBoostingRegressor` es el equivalente de LightGBM dentro de sklearn y cumple la restricción del enunciado. Tiene **pérdida Poisson**, adecuada para conteos no negativos, y **pérdida cuantil** (*pinball*) para intervalos.
- Opción práctica: **skforecast** (`ForecasterRecursiveMultiSeries`) envuelve cualquier regresor de sklearn como modelo global multiserie y trae *backtesting*. Revisar la versión instalada, porque la API cambia entre versiones.

### 5.4 Estrategia de pronóstico multi-paso
- **Recursiva:** un modelo que usa sus propias predicciones como rezagos. Es simple, pero el error se acumula.
- **Directa:** un modelo por horizonte (h = 1…4).
- **Recomendación:** empezar con la recursiva y, si da tiempo, comparar con la directa. M5 mostró que **promediar ambas** funciona bien.

### 5.5 Desagregación a talla y color
- Proporción de cada talla y color dentro del catálogo en las **últimas 8–12 semanas** (más reciente = más representativo), con suavizado para combinaciones con poca venta.
- Validar que las proporciones sean estables (§3.2, pregunta 7). Si cambian mucho, usar una ventana más corta.
- Resultado: una tabla de unidades por catálogo × talla × color × semana, lista para planear cortes.

### 5.6 Intervalos de predicción (recomendado para producción)
- Entrenar el boosting con `loss="quantile"` para los cuantiles 0,1 / 0,5 / 0,9.
- Negocio: el cuantil 0,9 sirve para decidir stock de seguridad en los catálogos de alta rotación y el 0,5 para el plan base.

### 5.7 Criterio de selección final
Gana el modelo con **menor error en el backtesting (§6)**, con prioridad en: (1) WAPE del top; (2) sesgo cercano a 0; (3) buen comportamiento **después del Mundial** (que no siga pronosticando demanda de evento); (4) simplicidad y explicabilidad.

**Fuentes:**
- Makridakis, S., Spiliotis, E. y Assimakopoulos, V. (2022). M5 accuracy competition: Results, findings, and conclusions. *International Journal of Forecasting*, 38(4), 1346–1364.
- Documentación de scikit-learn: `HistGradientBoostingRegressor` (pérdidas `poisson` y `quantile`).
- Documentación de skforecast: https://skforecast.org/
- Kaggle: *Grupo Bimbo Inventory Demand* (discusiones y soluciones ganadoras).
- Hochreiter, S. y Schmidhuber, J. (1997). Long short-term memory. *Neural Computation*, 9(8). (Artículo de la U1.)
- Croston, J. D. (1972). Forecasting and stock control for intermittent demands. *Operational Research Quarterly*, 23(3); Syntetos y Boylan (2005) para SBA.

---

## 6. Validación y métricas

### 6.1 Esquema de validación
- **Nunca** validar con partición aleatoria: en series de tiempo eso filtra el futuro (*leakage*).
- **Backtesting con origen móvil** (*rolling origin*): entrenar hasta la semana *t*, pronosticar t+1…t+4, avanzar el origen una semana y repetir. En sklearn es `TimeSeriesSplit`; skforecast trae su propio *backtesting*.
- **Holdout final:** las últimas **6 semanas completas** (mediados de agosto a fin de septiembre). Se tocan **una sola vez**, al final.
- **Ojo con el Mundial:** el backtesting debe incluir orígenes **antes, durante y después** del evento. Un modelo que pronostica bien en septiembre pero que en julio no ve venir la caída de agosto no sirve para Klixmant.
- Las variables (rezagos, medias móviles, proporciones, clústeres) se calculan **dentro de cada pliegue** solo con datos del pasado.

### 6.2 Métricas

| Métrica | Para qué | Por qué |
|---|---|---|
| **WAPE** (Σ\|error\| / Σ real) | Métrica principal de negocio | Se interpreta como un %, pondera por volumen y aguanta ceros |
| **MASE** o **RMSSE** | Comparar contra la línea base ingenua | Sin escala. RMSSE fue la base de la métrica de M5 |
| **Sesgo** (Σ error / Σ real) | ¿Sobrepronostica o subpronostica? | Sobrepronosticar = inventario quedado, que es el dolor de Klixmant |
| **Pinball loss** | Calidad de los cuantiles | Solo si se hacen intervalos |
| ~~MAPE~~ | — | **No usar**: se indefine con ceros y castiga de forma asimétrica |

### 6.3 Reporte de evaluación
- Tabla modelo × métrica, con una fila por modelo de la escalera (§5.2).
- Desglose por **segmento**: top contra cola, familia Colombia contra resto y periodo evento contra normal.
- **Skill score** frente al ingenuo: % de mejora en MASE.

**Fuentes:**
- Hyndman, R. J. y Koehler, A. B. (2006). Another look at measures of forecast accuracy. *International Journal of Forecasting*, 22(4), 679–688. (Origen del MASE.)
- Hewamalage, H., Ackermann, K. y Bergmeir, C. (2023). Forecast evaluation for data scientists: common pitfalls and best practices. *Data Mining and Knowledge Discovery*, 37, 788–832. https://doi.org/10.1007/s10618-022-00894-5 (líneas base débiles, *leakage*, gráficas engañosas, origen fijo frente a móvil).
- FPP3, cap. 5.8–5.10 (métricas y validación cruzada de series).

---

## 7. Graficación

### 7.1 Principios
1. **Una idea por gráfica**, con un título que diga la conclusión ("Junio duplicó la venta por el Mundial") y no solo el tema ("Ventas por mes").
2. Ejes con unidades ("unidades por semana") y fechas legibles.
3. **Anotar el contexto:** banda sombreada del Mundial y líneas en festivos clave.
4. Paleta accesible para daltonismo y consistente: el mismo color para el mismo canal o catálogo en todo el trabajo.
5. Sin 3D, sin tortas con muchas categorías y sin doble eje salvo que sea indispensable.
6. Estáticas (matplotlib/seaborn) para el póster; interactivas (plotly) para explorar en el notebook.

### 7.2 Catálogo de gráficas por fase

| Fase | Gráfica | Mensaje |
|---|---|---|
| EDA | Serie semanal total y por canal, con banda del Mundial | Tamaño del evento y entrada de Dropi |
| EDA | **Curva de Pareto** de catálogos | 15 catálogos = 71 %: justifica el enfoque top + regla |
| EDA | **Dispersión ADI vs CV²** con cuadrantes | Justifica qué método va a cada catálogo |
| EDA | **STL** de la serie total y de 2–3 catálogos top | Tendencia, componente semanal y atípico de evento |
| EDA | **ACF / PACF** | Dependencia temporal y elección de rezagos |
| EDA | Heatmap día de la semana × semana | Patrones semanales y quincenales |
| EDA | Barras al 100 % de talla dentro de los catálogos top | Estabilidad de la mezcla (base de la desagregación) |
| Preparación | Perfiles promedio por clúster K-means | "Catálogos de evento" frente a "catálogos base" |
| Modelo | **Real vs pronóstico** con intervalo, para 3–4 catálogos top | Calidad visual del pronóstico |
| Modelo | **Base vs evento apilado** | Responde la pregunta central de Klixmant |
| Evaluación | Barras de WAPE / MASE por modelo | Selección del modelo |
| Evaluación | Error por catálogo (ordenado) | Dónde falla el modelo |
| Explicabilidad | **Importancia por permutación** o SHAP | Qué impulsa la demanda |
| Negocio | Tabla/heatmap catálogo × talla × semana pronosticada | Insumo directo para producción |

**Fuentes:**
- Wilke, C. O. (2019). *Fundamentals of Data Visualization*. O'Reilly (libre en https://clauswilke.com/dataviz/).
- Knaflic, C. N. (2015). *Storytelling with Data*. Wiley.
- Tufte, E. R. (2001). *The Visual Display of Quantitative Information* (2.ª ed.).
- FPP3, cap. 2 (gráficas para series de tiempo).
- Documentación de scikit-learn: *Permutation feature importance*.

---

## 8. Documentación y "despliegue"

El enunciado pide **"documentación suficiente para orientar un pronóstico"** con el modelo. Eso significa que alguien de Klixmant debe poder generar un pronóstico nuevo sin el grupo presente.

| Documento | Contenido mínimo |
|---|---|
| **README** | Objetivo, estructura de carpetas, requisitos (librerías y versiones), cómo correr el notebook de principio a fin |
| **Guía "Cómo generar un pronóstico"** | 1) Qué archivo de entrada se necesita (exportación de `PEDIDOS` con las mismas columnas); 2) qué pasos de limpieza se aplican; 3) cómo cargar el modelo guardado; 4) cómo actualizar el calendario de eventos; 5) qué salida produce (tabla catálogo × talla × color × semana) y cómo leerla |
| **Model card** | Uso previsto, datos de entrenamiento, métricas por segmento, **limitaciones** (9 meses de historia, sin Black Friday ni diciembre en los datos, evento único, sin precios ni marketing), cuándo reentrenar |
| **Diccionario de variables derivadas** | Cada variable creada, su fórmula en palabras y su ventana temporal |
| **Registro de decisiones** | Tabla "decisión · alternativas · por qué" (esta guía es el punto de partida) |

- Guardar el modelo entrenado: `joblib` para sklearn o el formato nativo de Keras.
- Recomendación operativa: **reentrenar mensualmente** y revisar a mano los catálogos nuevos o de evento.

**Fuente:** Mitchell, M. et al. (2019). Model cards for model reporting. *Proceedings of FAT\* '19*, 220–229. https://doi.org/10.1145/3287560.3287596

---

## 9. Póster

### 9.1 Formato
- **Vertical, A0 o A1**, salvo que el *Syllabus* o la *Guía* digan otra cosa.
- Herramientas: PowerPoint, Canva o Figma, exportado a PDF.
- Lectura en menos de 1 minuto a 2 metros: títulos de 80 pt o más y texto de 24 pt o más.

### 9.2 Estructura (flujo CRISP-DM de arriba abajo o en columnas)
1. **Título y equipo** (UNAB · Analítica de Marketing · Klixmant).
2. **Problema:** "Se compra insumo sin modelo; después del Mundial queda inventario."
3. **Datos:** 29.9 mil unidades, 806 catálogos, 9 meses; Pareto en miniatura.
4. **Método:** diagrama del flujo (limpieza → variables → modelo global → desagregación a talla y color).
5. **Resultados:** **número grande** (p. ej. "WAPE del top = X %, Y % mejor que el ingenuo"), gráfica real vs pronóstico y gráfica base vs evento.
6. **Recomendaciones de negocio:** 3 viñetas accionables.
7. **Limitaciones y trabajo futuro**, y un QR al notebook.

### 9.3 Buenas prácticas
- Enfoque *Better Poster* (Mike Morrison): **la conclusión principal en grande, al centro**, en lenguaje simple; el detalle va a los lados.
- Máximo 3–4 gráficas, con la misma paleta del notebook.
- Revisar contraste y ortografía.

**Fuentes:** Morrison, M. (2019). *#BetterPoster* (video y plantillas en OSF/YouTube); guías de póster académico de bibliotecas universitarias.

---

## 10. Cronograma, reparto y riesgos

### 10.1 Cronograma (3 al 12 de noviembre)

| Fecha | Fase | Entregable interno |
|---|---|---|
| Mar 3 – Mié 4 | Negocio + consulta al docente (catálogo vs referencia) + carga y cuadre de datos | Cifras de control cuadradas, decisiones de §2 cerradas |
| Mié 4 – Jue 5 | EDA completo + calendario de eventos | Gráficas de §7 (EDA), clasificación ABC y ADI/CV² |
| Vie 6 | Preparación + variables + clustering | Tabla semanal lista y clústeres |
| Sáb 7 – Lun 9 | Líneas base, ETS/ARIMA, boosting global, LSTM; backtesting | Tabla de métricas y modelo elegido |
| Lun 9 | Desagregación a talla y color + cuantiles | Tabla de pronóstico final |
| Mar 10 | Documentación (README, guía, *model card*) | Carpeta `docs/` |
| Mié 11 | Póster + revisión cruzada del notebook | PDF del póster |
| Jue 12 | Entrega en TEMA | ✔ |

### 10.2 Reparto sugerido (4 personas)

| Rol | Responsabilidades |
|---|---|
| Datos y EDA | Carga, cuadre, limpieza, gráficas de EDA, calendario de eventos |
| Modelado estadístico | Líneas base, ETS/ARIMA, Croston para la cola, desagregación a talla y color |
| Modelado ML | Variables, boosting global, LSTM, backtesting y métricas |
| Comunicación | Documentación, *model card*, póster y revisión de redacción propia |

Todos deben **entender y poder explicar** el trabajo completo: puede haber defensa oral si Turnitin la exige.

### 10.3 Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| El docente exige "referencia" en lugar de catálogo | Cambia la unidad de análisis | Preguntar antes del 5-nov; el modelo global permite agregar a referencia sin rehacerlo |
| Historia corta y evento único | Sobreajuste, pronósticos inflados | Modelos simples como base, variables de evento explícitas, validar después del Mundial |
| Horizonte con temporadas sin historia (Black Friday, diciembre) | Pronóstico bajo | Declararlo como limitación y proponer un ajuste experto |
| *Leakage* en variables | Métricas falsamente buenas | Variables calculadas por pliegue y revisión cruzada |
| Errores de lectura del Excel | Resultados equivocados | Cuadre obligatorio contra las cifras de control (§3.1) |
| Texto con alta probabilidad de IA | Nota 1.0 o defensa | Redacción propia del grupo; esta guía no se copia |
| Falta de tiempo | Entrega incompleta | Priorizar: línea base + boosting + documentación + póster. LSTM y cuantiles son opcionales |

---

## 11. Bibliografía y fuentes

**Metodología y pronóstico**
- Chapman, P. et al. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. SPSS.
- Hyndman, R. J. y Athanasopoulos, G. (2021). *Forecasting: Principles and Practice* (3.ª ed.). OTexts. https://otexts.com/fpp3/
- Hyndman, R. J. y Koehler, A. B. (2006). Another look at measures of forecast accuracy. *IJF*, 22(4), 679–688.
- Hewamalage, H., Ackermann, K. y Bergmeir, C. (2023). Forecast evaluation for data scientists: common pitfalls and best practices. *Data Mining and Knowledge Discovery*, 37, 788–832. https://arxiv.org/abs/2203.10716
- Makridakis, S., Spiliotis, E. y Assimakopoulos, V. (2022). M5 accuracy competition: Results, findings, and conclusions. *IJF*, 38(4), 1346–1364. https://econpapers.repec.org/RePEc:eee:intfor:v:38:y:2022:i:4:p:1346-1364
- Syntetos, A. A., Boylan, J. E. y Croston, J. D. (2005). On the categorization of demand patterns. *JORS*, 56(5), 495–503. https://doi.org/10.1057/palgrave.jors.2601841
- Croston, J. D. (1972). Forecasting and stock control for intermittent demands. *Operational Research Quarterly*, 23(3), 289–303.
- Bandara, K., Bergmeir, C. y Smyl, S. (2020). Forecasting across time series databases using RNNs on groups of similar series: A clustering approach. *Expert Systems with Applications*, 140.
- Hochreiter, S. y Schmidhuber, J. (1997). Long short-term memory. *Neural Computation*, 9(8), 1735–1780.

**Herramientas (documentación oficial)**
- scikit-learn: `HistGradientBoostingRegressor` — https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html
- scikit-learn: *Lagged features for time series forecasting* — https://scikit-learn.org/dev/auto_examples/applications/plot_time_series_lagged_features.html
- skforecast — https://skforecast.org/
- statsmodels (STL, ARIMA/SARIMAX, ETS, ACF/PACF, ADF/KPSS) — https://www.statsmodels.org/
- Keras (LSTM) — https://keras.io/

**Visualización y comunicación**
- Wilke, C. O. (2019). *Fundamentals of Data Visualization*. https://clauswilke.com/dataviz/
- Knaflic, C. N. (2015). *Storytelling with Data*. Wiley.
- Tufte, E. R. (2001). *The Visual Display of Quantitative Information*.
- Mitchell, M. et al. (2019). Model cards for model reporting. *FAT\* '19*.
- Morrison, M. (2019). *#BetterPoster*.

**Contexto del caso**
- Klixmant S.A.S. (2026). *Documentación de la base de datos* (PDF entregado en TEMA).
- Calendario Mundial 2026 y partidos de Colombia: prensa deportiva (Blu Radio, Vanguardia, Publimetro). **Verificar contra FIFA.com.**
- Festivos de Colombia 2026: El Tiempo, Noticias Caracol, calendariodecolombia.com. **Verificar contra el calendario oficial.**
