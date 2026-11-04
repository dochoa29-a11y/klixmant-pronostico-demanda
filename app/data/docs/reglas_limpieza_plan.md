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
