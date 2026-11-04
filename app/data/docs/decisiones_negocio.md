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
