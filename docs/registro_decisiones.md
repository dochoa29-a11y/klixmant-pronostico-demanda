# Registro de decisiones

> ✍️ **Borrador técnico (agente 06, 4-nov-2026).** El grupo debe redactarlo con sus propias palabras (Turnitin).
> Parte de las tablas del plan de investigación (§2, §5) y de los reportes de traspaso 01–05. La columna **Revisar** marca las decisiones
> de criterio que el grupo debería discutir o confirmar con Klixmant o con el docente.

| # | Fase | Decisión | Alternativas | Por qué | Dónde | Revisar |
|---|---|---|---|---|---|---|
| 1 | Negocio | Pronosticar por **catálogo**, agregar a tela y desagregar a talla × color | Referencia (16 telas) · SKU | Klixmant corta por catálogo; 16 series de tela no sirven para producción | §2, plan §2.2 | Confirmar con el docente ("referencia" en el enunciado) |
| 2 | Negocio | Modelar el **top 20** (77 % de las unidades) y la cola por regla | Los 806 · top 15 | La cola es intermitente: 601 catálogos tienen menos de 2 semanas con venta | §2, §3.2 | — |
| 3 | Negocio | Semanas **lunes a domingo**; horizonte **4** (principal) y **8** (extendido) | Diario · mensual · 1 semana | 9 meses de datos; 4 semanas alcanzan para comprar insumo y programar cortes | §0.5 | — |
| 4 | Negocio | Demanda = `cantidad_total` **sin canceladas**, por **`fecha_remision`** | Con canceladas · neta de devoluciones · `fecha_carga` | Las canceladas no se producen; `fecha_carga` agrupa días por lote (216 fechas frente a 266 días) | §0.5, §3.1 | — |
| 5 | Datos | Las 24 líneas con `descarte = 1` y las 15 en estados pendientes **cuentan** como demanda | Excluirlas | Se produjeron o están por producirse; no cambian el resultado | §4.1 | Decisión de negocio |
| 6 | Datos | **Normalizar nombres** de catálogo (804 → 798); KTM/AKT y KAWASAKI/SIN REFLECTIVO no se fusionan | Dejar los nombres crudos | Errores de digitación partían la historia de un mismo catálogo | §4.1.1 | Posibles duplicados restantes (RED BULL, COLOMBIA ÉLITE) |
| 7 | Datos | **Tela = 2.º token de `referencia`** (16 códigos) | Referencia completa (124 valores) | Coincide con las "16 bases" de la documentación | §4.1.2 | Confirmar significado de cada código con Klixmant |
| 8 | Datos | **Ceros explícitos** desde la primera venta de cada catálogo | Solo semanas con venta | Sin ceros el modelo no aprende cuándo un catálogo deja de vender | §4.3.3 | — |
| 9 | Variables | Ventana del evento **25-may → 13-jul** (2 semanas antes del Mundial) | Solo semanas del torneo | El pico de la familia Colombia empezó dos semanas antes del 11-jun | §4.3.1 | — |
| 10 | Variables | Sin `semana_anio` ni `mes` en el modelo | Incluirlas | Octubre–diciembre no existen en el entrenamiento (fuera de rango) | §4.6 | — |
| 11 | Base/evento | **Ruta 1** (línea base interpolada entre medianas) para cuantificar el evento; ruta 2 (modelo sin evento) como contraste | Solo el modelo | El modelo subestima el pico (2.959 frente a 5.102 uds en catálogos existentes); la base coincide en las dos rutas | §4.5, §5.7 | — |
| 12 | Base/evento | La caída de motos y autos durante el Mundial se reporta como **demanda desplazada** | Tratarla como ruido | −1.645 uds frente a su base, al mismo tiempo que el pico de Colombia | §4.5 | Hipótesis por validar con Klixmant |
| 13 | Segmentación | **K-means con k = 4** (silueta 0,26) sobre 84 catálogos elegibles | k = 2 (silueta 0,37) | k = 2 solo separa evento de resto; k = 4 distingue base, en declive y errática | §4.4 | — |
| 14 | Modelado | Modelo principal: **HGB global Poisson** (scikit-learn) | ARIMA por serie · LSTM · Random Forest | Pocos datos por serie, muchos ceros; un modelo global comparte información entre catálogos. El enunciado pide sklearn/keras/pytorch | §5.3 | — |
| 15 | Modelado | Estrategia **recursiva** | Directa · combinación | La directa salió peor (WAPE 1,15 frente a 0,95) con tan poca historia | §5.4 | — |
| 16 | Modelado | **Tope** de cada predicción = 2 × la mejor semana del catálogo | Sin tope · tope menor | La recursión con enlace log puede explotar; es una salvaguarda, no un parámetro afinado | §5.2 | Probar 1,25–1,5 solo con el backtesting |
| 17 | Modelado | Catálogos sin venta en **12 semanas** van en 0 | Pronosticarlos todos | Solo 0,3 % de la venta de la cola viene de catálogos dormidos que reviven | §5.3, §6.7 | — |
| 18 | Modelado | **`early_stopping=False`** en todos los HGB | `"auto"` (por defecto) | Con > 10.000 filas, `"auto"` cortaba el modelo con una validación aleatoria (10 iteraciones en producción) | §5.3.1, reporte 05 | Es la corrección de un error, no un ajuste con el holdout |
| 19 | Validación | **Backtesting de 15 orígenes** (13-abr → 20-jul) para elegir; **holdout** de 6 semanas abierto una sola vez | Un solo corte | Evita elegir con el holdout; el primer origen deja ≥ 14 semanas de historia | §6.1, §6.4 | — |
| 20 | Validación | Métricas **WAPE, sesgo, MASE, RMSSE** | MAPE · RMSE | El MAPE explota con ceros; WAPE pesa por volumen, que es lo que importa a producción | §6.2 | — |
| 21 | Selección | **`HGB_redondeo`** (trayectoria en unidades enteras) | `HGB+ingenuo` · `HGB_poisson` · ingenuo | Regla: WAPE a 5 % del mejor → WAPE después del Mundial → más simple. `HGB+ingenuo` (mejor WAPE, 12/15 orígenes) cae por simplicidad | §6.3 | Criterio del grupo; cambiarlo ahora sería elegir con el holdout |
| 22 | Selección | Cola con el **ingenuo** | SBA · TSB · media móvil | Ningún método le gana al ingenuo en la cola; SBA y TSB sobrepronostican pedidos únicos | §5.5, §6.3 | — |
| 23 | Intervalos | **Conformal** por horizonte con los residuos del backtesting en **semanas fuera del evento** (elegido a priori) | Cuantiles HGB · todos los orígenes | Los cuantiles cubrían 50–64 %; el horizonte de producción no tiene evento conocido | §6.5 | Son conservadores (92 %) |
| 24 | Producción | Publicar el **ingenuo al lado** y marcar `revisar` si difieren > 50 % y ≥ 10 uds en 4 semanas | Solo el modelo | Caso Honda Reflectivo en el holdout: el modelo extrapoló un récord | §7.2.1, §8.2 | Umbrales de criterio |
| 25 | Producción | Desagregar a talla × color con la mezcla de las **últimas 12 semanas** (suavizado 0,5; toda la historia si < 30 uds) | Toda la historia · modelo por talla | La mezcla de tallas es estable en el top (TV 0,09) | §4.2.2, §5.8 | — |
| 26 | Despliegue | Entrenar el modelo final con **toda la historia** hasta el 28-sep (incluye el holdout) | Usar el modelo al 17-ago | El holdout ya cumplió su función; los datos más recientes son los más informativos | §8.1 | — |
| 27 | Despliegue | Guardar con **joblib** + `metadata.json` con sha256, versiones y categorías; `cargar_modelo()` verifica | Solo el `.joblib` | Detecta archivos cambiados, versiones distintas y modelos cortados por *early stopping* | §8.1–§8.2 | — |
| 28 | Despliegue | **Reentrenar cada mes**; ajuste experto para eventos nuevos | Reentrenar cada semana · nunca | Pocas semanas nuevas por mes cambian poco; los eventos no se aprenden de la historia | Guía §3.2 | — |
| 29 | Despliegue | Tablero **Streamlit** que lee un **bundle precalculado** (parquet < 15 MB, `cifras_clave.json`) | Reentrenar en la nube · leer el Excel | El notebook tarda ~17 min; la nube tiene ~1 GB de memoria; no se exponen datos por línea de pedido | §8.4, `PLAN_DESPLIEGUE_STREAMLIT.md` | Definir quién puede ver la app |
| 30 | Comunicación | Titular del póster: **"Tras el Mundial el modelo pronosticó 75 uds de Colombia (real 49); una media móvil habría pedido 3.990"** | "X % mejor que el ingenuo" | La mejora frente al ingenuo no es concluyente; el valor real es no arrastrar el evento | §7.3 | El grupo puede preferir otro |
