# Model card — Pronóstico semanal de demanda por catálogo (Klixmant S.A.S.)

---

## 1. Detalles del modelo

| Campo | Valor |
|---|---|
| Nombre | `HGB_redondeo` |
| Tipo | `HistGradientBoostingRegressor` de scikit-learn, pérdida **Poisson**, **global** (un solo modelo para todos los catálogos) |
| Parámetros | `learning_rate=0.05`, `max_iter=300`, `max_leaf_nodes=15`, `min_samples_leaf=20`, `l2_regularization=1.0`, `early_stopping=False`, `random_state=42`, categóricas nativas |
| Estrategia multi-paso | **Recursiva**: predice la semana 1, la usa como rezago para la 2, y así hasta 8. La trayectoria se **redondea a unidades enteras** |
| Salvaguarda | Cada predicción se limita a **2 × la mejor semana histórica** del catálogo (`TOPE_RELATIVO`) |
| Cola | Los catálogos fuera del top 20 se pronostican con el **ingenuo** (repetir la última semana). Los que no vendieron en 12 semanas quedan en 0 |
| Intervalo | 10–90 % *conformal* por horizonte, calibrado con los residuos del backtesting en semanas fuera del evento |
| Archivos | `modelos/hgb_final.joblib` (con su sha256) y `modelos/metadata.json` (corte, parámetros, 37 variables, categorías, calibración, versiones) |
| Entrenamiento | Toda la historia hasta el **28-sep-2026** (17.722 filas catálogo × semana, 792 catálogos). 300 iteraciones verificadas |
| Versiones | Python 3.14, pandas 3.1, scikit-learn 1.9 (exactas en `metadata.json`) |
| Autores | Grupo del Trabajo Final de Analítica de Marketing (UNAB, TEMA 2228), con apoyo de agentes de IA (reportes 01–06 en `docs/`) |

## 2. Uso previsto

- **Para qué:** planear **cuánto cortar y cuánta tela comprar** en las próximas **4 semanas** (hasta 8, orientativas) para los 20 catálogos
  que concentran el 77 % de las unidades, con desagregación a talla × color y agregación a tela.
- **Quién lo usa:** el área de producción / compras de Klixmant, con revisión humana de los catálogos marcados `revisar`.
- **Fuera de alcance:**
  - Pronosticar **eventos que el modelo no vio** (un torneo nuevo, Black Friday, diciembre). Ahí se necesita ajuste experto.
  - **Catálogos nuevos** o personalizados de un solo pedido (no tienen historia).
  - Decisiones de **precio o pauta**: el modelo no ve esas variables.
  - Pronóstico diario o por cliente.

## 3. Datos

| Aspecto | Detalle |
|---|---|
| Fuente | Hoja `PEDIDOS` del Excel de Klixmant (corte 6-oct-2026): 29.899 líneas, 29.919 unidades, 806 catálogos. Cuadra con las 12 cifras de control |
| Periodo | 12-ene → 28-sep-2026: **38 semanas completas** (~9 meses). La semana del 5-oct es parcial y no se usa para entrenar |
| Demanda | Unidades por `fecha_remision`, sin canceladas. Canales Effi y Dropi (Dropi desde febrero) |
| Unidad | Catálogo normalizado (798) × semana, con ceros explícitos desde la primera venta |
| Variables | 37: rezagos y medias móviles, desviación, semanas desde la última venta, % Dropi, calendario (Mundial, pre-Mundial, festivos, fechas comerciales), atributos del catálogo (línea, tipo de prenda, tela, proceso) y clúster K-means. Diccionario en `docs/4_diccionario_variables.csv` |
| Evento | Mundial 2026 (11-jun → 19-jul). Ventana de evento 25-may → 13-jul: la familia Colombia sumó ~6.582 uds de evento (87 % de su venta en la ventana) |

## 4. Evaluación

### 4.1 Protocolo

- **Backtesting de origen móvil:** 15 orígenes semanales (13-abr → 20-jul), horizonte 4 semanas, top 20. Con él se **eligió** el modelo.
- **Holdout:** 6 semanas (24-ago → 28-sep), entrenado al 17-ago. **Se abrió una sola vez**, con el modelo ya elegido.
- **Métricas:** WAPE (Σ|error| / Σ real), sesgo, MASE y RMSSE (escalados por el ingenuo de 1 semana).

### 4.2 Resultados principales (top 20)

| Métrica | `HGB_redondeo` | Ingenuo | Lectura |
|---|---|---|---|
| WAPE backtesting (15 orígenes) | **0,897** | 0,907 | Empate: IC 90 % de la diferencia [−0,062; +0,045], gana en 9/15 orígenes |
| WAPE backtesting después del Mundial | 0,585 | 0,600 | Empate |
| Sesgo backtesting | −1,7 % | +3,5 % | Sin sesgo relevante |
| MASE / RMSSE backtesting | 1,73 / 1,52 | 1,64 / 1,43 | El ingenuo es algo mejor |
| Colombia tras el Mundial (real 49 uds) | **75** | 84 | SARIMAX 1.871, media móvil **3.990**: **el modelo no arrastra el Mundial** |
| Holdout WAPE h = 1…4 | **0,696** | 0,476 | **El ingenuo gana en el top** |
| Holdout WAPE h = 1…6 / sesgo | 0,652 / +19 % | 0,433 / −5 % | Sobrepronóstico, casi todo de un catálogo |
| Holdout sin Honda Reflectivo (WAPE / sesgo) | 0,52 / −3 % | 0,42 / −15 % | Incluso sin Honda el ingenuo gana |
| Holdout **total semanal** (todos los catálogos) | **0,110** | 0,170 | En el total, que mira compras, el modelo es mejor |

### 4.3 Por segmento (backtesting, salvo indicación)

| Segmento | WAPE modelo | WAPE ingenuo |
|---|---|---|
| Horizonte h = 1 / 2 / 3 / 4 | 0,55 / 0,81 / 1,00 / 1,24 | 0,52 / 0,82 / 1,05 / 1,25 |
| Familia Colombia / resto | 0,97 / 0,74 | 0,99 / 0,72 |
| Semanas de evento / normales | 0,88 / 0,96 | 0,90 / 0,94 |
| Cola, por catálogo (regla ingenua) | — | 1,36 (holdout 1,25) |
| Cola, total semanal | — | 0,24 (holdout 0,27) |

Fases del backtesting: 2 orígenes antes del evento (WAPE 0,47), **11 que tocan la ventana del evento** (0,95) y 2 después (0,59).
El origen del 29-jun tiene WAPE ≈ 3 para todos los modelos: nadie podía saber que Colombia quedaría eliminada el 7-jul.

### 4.4 Intervalos 10–90 %

| Método | Cobertura (nominal 80 %) | Ancho medio |
|---|---|---|
| Cuantiles HGB sin calibrar (§5.6), holdout | 64 % | 16 uds |
| **Conformal, semanas fuera del evento (elegido a priori)**, holdout | **92 %** | 35 uds |
| El mismo, en las semanas del evento del backtesting | 63 % | 44 uds |

Conservadores fuera de eventos (sirven como cota de stock de seguridad); **demasiado angostos en un evento**.

### 4.5 Corrección de `early_stopping` (4-nov-2026)

Con el valor por defecto de scikit-learn (`early_stopping="auto"`), si había más de 10.000 filas se apartaba un 10 % **aleatorio** de los
datos para validar y el modelo se detenía antes: en el corte de producción quedaba con **10 iteraciones** en vez de 300 y pronosticaba
la mitad de la venta. Se fijó `early_stopping=False` y se reejecutó todo. **La selección no cambió**; sí cambiaron cifras del holdout
(WAPE top h = 1…6 de 0,718 a 0,652; total semanal de 0,215 a 0,110). Es la corrección de un error, no un ajuste mirando el holdout.
La celda 8.1 verifica `n_iter_ == 300` cada vez que se entrena.

## 5. Limitaciones

1. **Poca historia:** ~9 meses (38 semanas). Sin un año completo no hay estacionalidad anual: **no hay temporada de fin de año, Black Friday ni diciembre** en los datos.
2. **Un solo evento:** el Mundial 2026 es único. El modelo lo usa como contexto, pero **no puede anticipar un evento nuevo** ni su tamaño.
3. **Sin precios, promociones ni pauta:** la demanda se explica solo con su propia historia y el calendario.
4. **Mejora frente al ingenuo no concluyente en el top:** en el backtesting empatan y en el holdout gana el ingenuo. El valor del modelo está en
   **no arrastrar el evento** y en un mejor **total semanal**, no en cada catálogo.
5. **Extrapolación de récords:** si un catálogo cierra con su mejor semana, el modelo puede pronosticar cerca del tope (2 × ese récord), como
   Honda Reflectivo en el holdout (~132 uds/semana pronosticadas contra ~47 reales). Por eso se publica el ingenuo al lado y se marca `revisar`.
6. **Validación limitada:** 15 orígenes, de los cuales 11 tocan el evento, y un solo holdout de 6 semanas.
7. **Catálogos nuevos:** no se pronostican (≈ 27 % de las unidades de la cola en el backtesting).
8. **Variables estáticas** (`tela_principal`, `pct_dama`, `n_telas`…) calculadas con toda la historia: fuga menor dentro del entrenamiento.
9. **Desagregación:** talla × color por proporciones recientes; error alto semana a semana (WAPE ≈ 1,0), aceptable sumando 4 semanas (≈ 0,67).
10. **Nombres duplicados posibles** en el top ("CUELLO ALTO RED BULL" / "RED BULL", "CA COLOMBIA ÉLITE" / "COLOMBIA ELITE/CLASICO"): hay que confirmarlo con Klixmant.
11. **Demanda desplazada:** motos y autos vendieron menos durante el Mundial (−1.645 uds). La hipótesis de que la planta priorizó el evento no está validada.

## 6. Cuándo no confiar y cuándo reentrenar

- **No confiar** sin revisión: catálogos marcados `revisar`; semanas con un evento conocido; catálogos con menos de 8 semanas de historia; *h* > 4.
- **Reentrenar** cada mes (celda 8.1) y después de cualquier evento grande; revisar el backtesting antes de usar el modelo nuevo.
- **Señal de alarma:** sesgo de las últimas 4 semanas fuera de ±30 %, o WAPE del total semanal por encima de 0,25 durante varias semanas.

## 7. Consideraciones éticas y de datos

- Los datos son **confidenciales** de Klixmant: el repositorio es privado y no versiona el Excel ni la documentación.
- La app Streamlit solo muestra tablas **agregadas** (catálogo × semana o más); ninguna línea de pedido ni dato de cliente.
- Riesgo de negocio principal: **sobreproducir** (inventario sin rotación) o **quedarse corto** en un evento. El modelo reduce el primer riesgo
  tras un evento (no arrastra el pico), pero no el segundo: los eventos requieren criterio humano.

## 8. Referencias

- Mitchell, M. et al. (2019). Model cards for model reporting. *FAT\* '19*, 220–229.
- Hyndman, R. J. y Athanasopoulos, G. (2021). *Forecasting: Principles and Practice* (3.ª ed.). OTexts.
- Syntetos, A. A., Boylan, J. E. y Croston, J. D. (2005). On the categorization of demand patterns. *JORS*, 56(5), 495–503.
- Makridakis, S., Spiliotis, E. y Assimakopoulos, V. (2022). M5 accuracy competition. *International Journal of Forecasting*, 38(4), 1346–1364.
- Angelopoulos, A. N. y Bates, S. (2023). Conformal prediction: A gentle introduction. *Foundations and Trends in ML*, 16(4), 494–591.
