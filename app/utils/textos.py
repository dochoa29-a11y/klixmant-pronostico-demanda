"""Textos de la app.

Aquí no hay cifras: los números se insertan en cada página desde cifras_clave.json
o desde las tablas del bundle.
"""

NOMBRE_MODELO = {
    "HGB_sin_atipico": "Modelo final (boosting, Mundial como atípico)",
    "HGB_redondeo": "Boosting entrenado con el Mundial",
    "HGB_poisson": "Boosting Poisson",
    "HGB+ingenuo": "Boosting + ingenuo",
    "HGB_ingenuo": "Boosting + ingenuo",
    "HGB_suave": "Boosting suavizado",
    "HGB_sin_cluster": "Boosting sin clúster",
    "HGB_rec+dir": "Boosting recursivo + directo",
    "HGB_directo": "Boosting directo",
    "ingenuo": "Ingenuo (repite la última semana)",
    "media_movil_4": "Media móvil 4 semanas",
    "ETS": "Suavizamiento exponencial (ETS)",
    "SARIMAX": "SARIMAX",
    "RF": "Random forest",
    "LSTM": "Red LSTM",
    "TSB": "TSB (intermitente)",
    "SBA": "SBA (intermitente)",
}

GLOSARIO = {
    "Catálogo": "El diseño que ve el cliente (p. ej. «Cuello alto Colombia retro»). Es la unidad que se pronostica.",
    "Top y cola": "Los catálogos que más venden (el top) se pronostican con el modelo; los demás (la «cola») con una regla simple.",
    "Demanda base": "Lo que se habría vendido sin el Mundial: el ritmo normal del catálogo.",
    "Demanda de evento": "Lo que se vendió de más (o de menos) por el Mundial = venta real − base.",
    "Demanda desplazada": "Ventas que no desaparecen sino que se corren de semana (o de catálogo) por el evento. Es una hipótesis por validar.",
    "Ingenuo": "El pronóstico más simple: «la próxima semana se vende lo mismo que la última». Es la vara contra la que se mide todo modelo.",
    "Media móvil": "Promedio de las últimas 4 semanas. Tras un pico (como el Mundial) arrastra el pico hacia adelante.",
    "Dato atípico": "Un valor que no representa el comportamiento normal. Klixmant pidió tratar así el pico del Mundial: es cada cuatro años y no sirve para proyectar un junio cualquiera.",
    "SKU": "Código de la prenda: género · tela · largo · color · talla · proceso (BOR/ES) · reflectivo (RV). Ej.: «H N L NEGRO L ES RV».",
    "MAPE con venta": "Error porcentual promedio calculado solo en las filas donde hubo venta. Es la métrica del modelo inicial del curso.",
    "WAPE": "Error porcentual ponderado: de cada 100 unidades vendidas, cuántas se equivocó el pronóstico (sumando excesos y faltantes). Menor es mejor.",
    "Sesgo": "Si el pronóstico, en total, se pasa (+) o se queda corto (−). Un sesgo positivo significa producir de más.",
    "MASE": "Error comparado con el del ingenuo: menos de 1 = mejor que repetir la última semana; más de 1 = peor.",
    "Backtesting": "Ensayo en el pasado: se «congela» la historia en una fecha, se pronostica y se compara con lo que de verdad pasó. Se repite en varias fechas (orígenes).",
    "Holdout": "Las últimas semanas guardadas bajo llave: el modelo nunca las vio al escogerse. Es el examen final.",
    "Horizonte (h)": "Cuántas semanas hacia adelante se pronostica: h = 1 es la próxima semana.",
    "Intervalo 10–90 %": "Rango donde se espera que caiga la venta 8 de cada 10 veces. Sirve para decidir cuánto colchón dejar.",
    "ADI / CV²": "ADI = cada cuántas semanas hay una venta; CV² = qué tanto varía el tamaño de esas ventas. Juntos dicen si un catálogo es suave, intermitente, errático o irregular.",
    "Boosting": "Modelo de aprendizaje automático que suma muchos árboles de decisión pequeños. Aquí es uno solo para todos los catálogos (global).",
    "Clúster": "Grupo de catálogos con un perfil de venta parecido, encontrado con K-means.",
    "Talla × color": "La combinación que realmente se corta en el taller. El pronóstico del catálogo se reparte con las proporciones recientes.",
    "Tela (insumo)": "El segundo código de la referencia. Sumar el pronóstico por tela dice cuánto insumo comprar.",
}

PASOS_CRISP = [
    ("1 · Negocio", "Problema y datos", "Qué decide Klixmant y con qué datos contamos.", "paginas/1_problema_y_datos.py"),
    ("2 · Datos", "Exploración", "Concentración, intermitencia y el golpe del Mundial.", "paginas/2_exploracion.py"),
    ("3 · Preparación", "Mundial: base vs evento", "Cuánto fue ritmo normal y cuánto fue fiebre mundialista.", "paginas/3_mundial_base_evento.py"),
    ("3 · Preparación", "Segmentación", "Cuatro perfiles de catálogos según cómo venden.", "paginas/4_segmentacion.py"),
    ("4–5 · Modelo y evaluación", "Modelos y validación", "Qué modelo se escogió y qué tan bien le va.", "paginas/5_modelos_y_validacion.py"),
    ("6 · Despliegue", "Plan de producción", "Cuánto cortar y qué tela comprar en las próximas semanas.", "paginas/6_plan_de_produccion.py"),
    ("6 · Despliegue", "Guía y model card", "Cómo usarlo y cuándo no confiar en él.", "paginas/7_guia_y_model_card.py"),
]

COMO_LEER = {
    "titular_p3": (
        "Cada barra es lo que **cada método pronosticó** para los catálogos de Colombia en las semanas **después** del Mundial, "
        "sumando los orígenes del backtesting. La barra negra es lo que **de verdad se vendió**. "
        "Un método que «arrastra» el Mundial sigue pidiendo mucho cuando la fiebre ya pasó: eso es inventario que se queda en bodega."
    ),
    "serie_inicio": (
        "Unidades vendidas por semana (lunes a domingo). La franja amarilla fuerte es el Mundial; la clara, la ventana del evento "
        "(desde que arranca la compra anticipada). Pase el cursor para ver el valor de cada semana."
    ),
    "cuadre": (
        "Antes de analizar, se reconstruyeron las cifras de control que entregó Klixmant. Si **esperado = obtenido**, los datos se "
        "leyeron completos y bien. Una sola diferencia invalidaría todo lo que sigue."
    ),
    "reglas": (
        "Cada barra es una regla de limpieza y cuántas unidades toca. La columna «decisión» dice si esas unidades cuentan como demanda o no."
    ),
    "jerarquia": (
        "La demanda se puede mirar en varios niveles. El modelo trabaja en **catálogo × semana**; hacia arriba se suma (tela y total) "
        "y hacia abajo se reparte (talla × color) con las proporciones recientes de cada catálogo."
    ),
    "serie_canal": (
        "Áreas apiladas: azul = Effi (venta directa), naranja = Dropi (dropshipping). La línea negra es el total. "
        "La última semana es parcial (el corte de datos cae a mitad de semana) y se marca aparte."
    ),
    "pareto": (
        "Barras = unidades de cada catálogo, ordenados de mayor a menor (rojo = familia Colombia). La línea es el % acumulado: "
        "donde cruza el 80 % se ve cuántos catálogos explican casi toda la venta."
    ),
    "adi": (
        "Cada punto es un catálogo (tamaño = unidades). Eje horizontal: cada cuántas semanas vende (ADI). Eje vertical: qué tan "
        "distintas son sus ventas (CV²). Las líneas punteadas dividen los cuatro tipos de Syntetos, Boylan y Croston (2005): "
        "**suave** (abajo-izquierda) es fácil de pronosticar; **irregular** (arriba-derecha) es lo más difícil."
    ),
    "heatmap_dia": (
        "Cada celda es un día; las columnas son semanas y las filas, días de la semana. Más oscuro = más unidades. "
        "Sirve para ver si hay un día fuerte y cómo el Mundial encendió todos los días a la vez."
    ),
    "dropi": (
        "Participación de Dropi en las unidades de cada semana. Dropi crece durante el Mundial: el canal de dropshipping "
        "reaccionó más al evento que la venta directa."
    ),
    "ciclo": (
        "Cuántas semanas vivió cada catálogo entre su primera y su última venta. La mayoría son catálogos cortos "
        "(personalizados o de temporada): por eso solo se modela el top."
    ),
    "tallas": (
        "Participación de cada talla en las unidades del mes. Si las barras se parecen mes a mes, la mezcla es estable y "
        "se puede repartir el pronóstico del catálogo con las proporciones recientes."
    ),
    "base_evento": (
        "La línea punteada azul es la **base** estimada (el ritmo sin Mundial, interpolado entre las medianas de antes y después). "
        "La línea negra es la venta real. La zona amarilla entre las dos es la **demanda de evento**. Las líneas rojas punteadas son los partidos de Colombia."
    ),
    "incremental": (
        "Unidades de evento netas por catálogo (real − base en la ventana). Positivo = vendió más por el Mundial; "
        "negativo = vendió menos de lo normal (demanda que se fue a otros catálogos o se aplazó)."
    ),
    "linea": (
        "Lo mismo, sumado por línea de producto. El % es la parte de la venta en la ventana que fue evento."
    ),
    "sensibilidad": (
        "El tamaño del evento depende de cómo se defina la base. Cada celda cambia dos supuestos (semanas previas usadas y "
        "número de semanas para el nivel). Si los valores se parecen, la conclusión es robusta."
    ),
    "rutas": (
        "Dos formas de estimar la base: **ruta 1** interpola entre antes y después; **ruta 2** usa el modelo apagando las variables del Mundial. "
        "Si ambas cuentan la misma historia, la separación base/evento es creíble."
    ),
    "curvas_cluster": (
        "Para cada catálogo se calcula qué parte de su venta total cayó en cada semana; luego se promedia por grupo. "
        "Así se comparan catálogos grandes y pequeños en la misma escala. El grupo «evento» se dispara en el Mundial y luego se apaga."
    ),
    "intensidad_cluster": (
        "Intensidad promedio de venta antes, durante y después del evento para cada grupo. Ayuda a ponerle nombre a cada perfil."
    ),
    "escalera": (
        "Se probaron modelos de simple a complejo. Cada barra es el WAPE del top (menor = mejor) en la validación preliminar de §5. "
        "La línea punteada es el ingenuo: lo que no baje de ahí no vale la complejidad."
    ),
    "por_origen": (
        "Filas = modelos; columnas = fecha en que se «congeló» la historia para pronosticar (origen). Color = WAPE (rojo = peor). "
        "Las semanas que tocan el Mundial son difíciles para **todos**; la diferencia está en cómo salen del evento."
    ),
    "por_horizonte": (
        "WAPE del top según cuántas semanas hacia adelante se pronostica. Lo normal es que el error crezca con el horizonte."
    ),
    "holdout": (
        "El holdout son las últimas semanas (24-ago → 28-sep). Con el Mundial tratado como atípico, el modelo final queda a la par o mejor "
        "que el ingenuo por catálogo y se equivoca menos en el **total semanal** (lo que importa para planear la planta). "
        "Ojo: esa decisión se tomó con el holdout ya abierto, así que estas cifras son indicativas."
    ),
    "holdout_total": (
        "Unidades totales por semana en el holdout: real (negro) contra cada modelo. Elija los modelos en la leyenda."
    ),
    "honda": (
        "El catálogo que más pesa en el sobrepronóstico del holdout, semana a semana: real, modelo final e ingenuo. "
        "Con el modelo anterior (entrenado con el Mundial) ese catálogo era Honda Reflectivo, que explicaba casi todo el exceso."
    ),
    "intervalos": (
        "Cobertura = % de semanas en que la venta real cayó dentro del intervalo. El objetivo es 80 % (línea punteada). "
        "Por debajo, el intervalo es demasiado optimista; muy por encima, demasiado ancho."
    ),
    "intervalo_cat": (
        "Banda azul = intervalo 10–90 % del modelo final; línea azul = pronóstico; puntos negros = venta real del holdout."
    ),
    "importancia": (
        "Cuánto empeora el error si se «revuelve» cada variable. Más larga = el modelo depende más de ella. La raya es la variación entre repeticiones."
    ),
    "plan_serie": (
        "Línea negra = venta real de las últimas semanas. Línea azul = pronóstico publicado (con su banda 10–90 % si el catálogo es del top). "
        "Línea gris punteada = ingenuo. Las semanas 5 a 8 (zona gris) son **orientativas**. Si hay ajuste experto, la línea verde lo muestra."
    ),
    "plan_heatmap": (
        "Filas = catálogos del top; columnas = semanas. Color = unidades pronosticadas (con el ajuste experto aplicado). "
        "«[revisar]» marca los catálogos que el sistema sugiere revisar a mano."
    ),
    "plan_talla_color": (
        "Unidades a cortar por talla (filas) y color (columnas) en el horizonte elegido. Es el pronóstico del catálogo repartido "
        "con su mezcla reciente de talla y color: un número decimal pequeño quiere decir «casi nada»."
    ),
    "plan_tela": (
        "Unidades que pasan por cada tela (género · código de tela), apiladas por color de la referencia. Incluye top y cola. "
        "Es la base para el pedido de insumo."
    ),
}

AVISO_DATOS = (
    "Datos agregados de Klixmant S.A.S. (confidenciales). Corte de datos: **{corte}** · última semana completa: **{semana}**."
)
