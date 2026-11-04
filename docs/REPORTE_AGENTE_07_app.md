# Reporte de traspaso — Agente 07 (app Streamlit)

**Fecha:** 4-nov-2026 · **Alcance:** app Streamlit en `app/` (`PLAN_DESPLIEGUE_STREAMLIT.md` §2–§3 y bloque "Agente 07" de §4).
**No se tocó el notebook** ni el póster, y **no se desplegó** en Streamlit Community Cloud (eso le toca al agente 08).
Lean también los reportes 01–06. Las cifras vigentes son las **posteriores a la corrección de `early_stopping`** (reporte 05 §2), y la app las lee de `app/data/cifras_clave.json`.

---

## 1. Qué se entregó

| Archivo | Qué es |
|---|---|
| `app/Inicio.py` | Entrypoint. `st.set_page_config(layout="wide")`, `st.navigation` con 8 vistas en 3 grupos (Resumen / La historia / Herramienta), CSS común y sidebar con la nota del corte de datos |
| `app/paginas/0_inicio.py` | Inicio: titular P3, 5 KPI, barras "quién arrastra el Mundial", serie semanal y mapa CRISP-DM con `st.page_link` a cada página |
| `app/paginas/1_problema_y_datos.py` … `7_guia_y_model_card.py` | Las 7 páginas del plan §3 (detalle en §3 de este reporte) |
| `app/utils/datos.py` | `tabla(nombre)`, `cifras()`, `kpi()`, `constantes()`, `documento()`, `curvas_cluster()`, todo con `@st.cache_data`. Rutas con `Path(__file__)` |
| `app/utils/estilo.py` | Paleta (sale de `cifras_clave.json → paleta`), formato es-CO (`num`, `pct`, `dec`, `fecha`), `layout()` plotly común, `eje_meses()`, `banda_mundial()`, `encabezado()`, `kpis()`, `como_leer()` |
| `app/utils/textos.py` | Glosario (19 términos), nombres de modelos, pasos CRISP-DM y los textos de "¿Cómo leer esta gráfica?". **Sin cifras** |
| `app/requirements.txt` | Versiones fijadas, probadas con Python 3.12.10 en un venv limpio |
| `app/.streamlit/config.toml` | Tema claro, color primario `#0072B2` (Okabe-Ito azul), sin estadísticas de uso |
| `app/copiar_docs.py` | Copia a `app/data/docs/` la guía, la *model card*, el registro de decisiones y 3 extractos del Plan de Investigación (§2, §4.1 y §11) |
| `app/data/docs/*.md` | Los 6 documentos que muestran las páginas 1 y 7 (copias; ver §5.4) |
| `docs/capturas_app/*.jpg` | 16 capturas (escritorio 1440 × 900 y celular 375 × 812) |
| `.claude/launch.json` | Configuración para abrir la app en el navegador integrado de Claude (no la usa Streamlit Cloud) |
| `README.md`, `.gitignore` | Fila del tablero, sección "Cómo correr la app" y `.venv-app/` ignorado |

**Tamaño:** código de la app ≈ 1.900 líneas; `app/data/` = 3,2 MB (bundle del agente 06 + 6 `.md`).

## 2. Cómo correrla en local

```bash
py -V:3.12 -m venv C:\Users\diani\.venvs\klixmant-app
```
```bash
C:\Users\diani\.venvs\klixmant-app\Scripts\pip install -r app/requirements.txt
```
```bash
C:\Users\diani\.venvs\klixmant-app\Scripts\streamlit run app/Inicio.py
```

Se abre en `http://localhost:8501`. El venv va **fuera de OneDrive** (como el del agente 06) para no sincronizar cientos de MB.
En este equipo no había Python 3.12: se instaló con `py install 3.12` (Python Install Manager, firma verificada de python.org).

| Librería | Versión fijada | Nota |
|---|---|---|
| streamlit | 1.66.1 | `st.navigation`, `st.Page`, `st.popover`, `st.segmented_control`, `width="stretch"` |
| pandas | 3.1.1 | La misma del notebook; lee los parquet escritos con pandas 3 sin conversión |
| numpy | 2.5.4 | |
| plotly | 7.1.0 | Solo `plotly.graph_objects` |
| pyarrow | 26.0.1 | Lector de parquet |

No hay scikit-learn, statsmodels ni torch: **la app no carga el modelo** (reporte 06 §5.13).

## 3. Páginas

Cada página abre con el título, una **frase-conclusión grande** (`.titular`), **4–5 KPI** con `st.metric` (con `help` que explica el número) y un botón
**📖 Glosario** (`st.popover`). Debajo de **cada** gráfica hay un `st.expander("¿Cómo leer esta gráfica?")`. Al final, la marca "✍️ Texto en borrador".

| Vista | Frase-conclusión (se arma con cifras del JSON) | Visuales |
|---|---|---|
| **Inicio** | "Tras el Mundial, el modelo pronosticó **75 uds** de Colombia (se vendieron 49); una media móvil habría pedido **3.990**." | KPI 29.919 · 806 · 9 · 77 % · +6.582; barras horizontales real vs 5 métodos (titular P3); serie semanal con banda; 7 tarjetas CRISP-DM con enlace; "qué pidió / qué se entrega / lo honesto" |
| **1 Problema y datos** | Se compra mirando el agregado y sin modelo; el inventario queda comprado | Pestañas: problema + tabla de decisiones del plan §2.2; cuadre de 12 cifras con ✅; reglas de limpieza (barras + tabla + reglas del plan §4.1); jerarquía Total → Canal → Tela → **Catálogo** → Talla × color (graphviz) |
| **2 Exploración** | Concentrada (20 = 77 %), errática y dominada por el Mundial | 7 pestañas: serie por canal (áreas apiladas + semana parcial); Pareto con slider; ADI/CV² log-log con cuadrantes y hover por catálogo; heatmap día × semana; % Dropi semanal; ciclo de vida (histograma + dona); mezcla de tallas por mes con selector + tabla de estabilidad |
| **3 Mundial: base vs evento** | El 87 % de lo que vendió Colombia en la ventana fue evento; motos y autos cayeron | Selector nivel (total / familia / línea / catálogo del top) → base punteada vs real con el evento sombreado y los 5 partidos de Colombia; barras de evento por catálogo y por línea; recuadro de demanda desplazada (hipótesis); heatmap de sensibilidad; ruta 1 vs ruta 2 |
| **4 Segmentación** | 4 perfiles: evento, base, en declive, base errática | Curva semanal promedio por clúster (participación normalizada, calculada en la app con `curvas_cluster()`); intensidad antes/durante/después; dispersión por catálogo; tabla por grupo (`st.segmented_control`) |
| **5 Modelos y validación** | No arrastra el Mundial (75 vs 49), pero por catálogo empata con el ingenuo (0,897 vs 0,907) | Recuadro de la corrección de `early_stopping` (antes/ahora); 9 pestañas: escalera de 14 modelos + tarjetas de niveles; tabla de backtesting con el final resaltado + WAPE por fase; heatmap WAPE por origen con fases; WAPE por horizonte; holdout por catálogo vs total semanal + serie semanal (total/top/cola); caso Honda (KPI con y sin el catálogo + serie); intervalos (cobertura vs meta 80 % + banda por catálogo); importancia por permutación con barras de error; métricas por segmento |
| **6 Plan de producción** (herramienta) | Próximas 4 semanas: el top necesita 1.444 uds (ingenuo 1.372) y la cola 984 | Filtros: catálogo (o Σ total del top), horizonte 4/8, semanas de historia; **ajuste experto** (semanas + % + alcance); historia + pronóstico + intervalo + ingenuo (semanas 5–8 sombreadas como orientativas); heatmap catálogo × semana con ⚠️; heatmap talla × color; barras de tela apiladas por color; banderas de revisión; buscador de la cola; 3 descargas CSV |
| **7 Guía y model card** | Úselo para las próximas 4 semanas del top; no confíe ante eventos que no vio ni en catálogos nuevos | KPI del modelo (corte, filas, 37 variables, 300 iteraciones, sklearn); pestañas: guía, *model card*, registro de decisiones, diccionario con buscador y filtro por grupo, glosario con buscador, bibliografía, figuras PNG de respaldo + índice |

### 3.1 Detalles de la página 6

- **`pred`** es lo publicado (modelo en el top, ingenuo en la cola). El intervalo `lo`/`hi` solo se dibuja para un catálogo del top; para el total del top se muestra solo la línea (**el intervalo no se suma**, reporte 06 §5.5).
- **Ajuste experto** (solo en pantalla, `st.session_state`): se eligen semanas (S1…S8), un % de −50 a +150 y el alcance.
  - *Todos los catálogos*: multiplica `pred`, `lo`, `hi`, `pred_tc` y `pred_tela` de esas semanas.
  - *Solo el catálogo elegido*: multiplica `pred`/`lo`/`hi`/`pred_tc` de ese catálogo; **la tela no cambia** (ya viene sumada sobre catálogos) y la página lo avisa.
  - La línea verde punteada muestra el pronóstico ajustado y el KPI dice cuántas unidades agregó.
- **Banderas `revisar`:** hoy la lista está vacía y la página muestra "✅ Ningún catálogo requiere revisión"; si hay alguno, aparece ⚠️ en el heatmap, en la tabla y un `st.warning` al elegirlo. Los umbrales salen de `constantes.umbral_revision` y `umbral_revision_uds`.
- **CSV:** `;` como separador, coma decimal y UTF-8 con BOM (abren bien en Excel en español). Nombre: `pronostico_<tabla>_corte_2026-09-28_<h>s[_ajustado].csv`. Columnas extra: `pred_ajustado`, `pred_tc_ajustado`, `pred_tela_ajustado`.

## 4. Convenciones visuales

- **Paleta del notebook**, leída de `cifras_clave.json → paleta`: `COLOR_CANAL` (Effi azul, Dropi naranja, total negro), `COLOR_FAMILIA` (Colombia bermellón, resto azul),
  `ESTILO_MODELO` (color y trazo de cada modelo: el `linea` de matplotlib se traduce a `dash` de plotly), `COLOR_EVENTO` amarillo. Los clústeres y las líneas usan Okabe-Ito.
- **Banda del Mundial:** amarillo fuerte 11-jun → 19-jul y amarillo claro para la ventana del evento 25-may → 13-jul (`constantes`), en todas las series de tiempo.
- **es-CO:** `separators=",."` en plotly + `separatethousands` en los ejes; `estilo.num()` / `pct()` para textos y tablas (`29.919`, `0,897`, `77 %`); meses en español en los ejes con `eje_meses()` (plotly no trae locales) y fechas `5-oct` en los *hover*.
  Las tablas con decimales o porcentajes se muestran ya formateadas como texto, porque los formatos de `st.column_config` usan punto decimal.
- **Títulos que dicen la conclusión** y se arman con datos (p. ej. "pico de 1.964 uds la semana del 8-jun").
- **Celular:** CSS con `@media (max-width: 640px)` (titular y KPI más pequeños, `h1` a 1,9 rem); `initial_sidebar_state="auto"` (el menú se colapsa en celular). Sin *scroll* horizontal a 375 px.

## 5. Verificación

### 5.1 Pruebas automáticas
Script `streamlit.testing.v1.AppTest` (scratchpad del agente 07, no está en el repo): ejecuta `Inicio.py`, cambia a cada página con `switch_page` y falla si hay alguna excepción.
- **8/8 vistas sin excepciones**, en el venv de trabajo y en un **venv limpio** creado solo con `app/requirements.txt` (Python 3.12.10).
- Página 6 con interacción: catálogo Mercedes → horizonte 8 → ajuste +50 % en S8 global → solo el catálogo → Toyota → búsqueda en la cola: sin errores y KPI coherentes (p. ej. Mercedes 415 uds en 8 semanas; con +50 % en S8, +20 uds).

### 5.2 Navegador (escritorio 1440 × 900 y celular 375 × 812)
- Recorrido de las 8 vistas por el menú lateral en una pestaña nueva: **0 errores en consola** (solo un aviso interno de Streamlit: `No script tag of type "javascript/worker"…`, del visor de graphviz).
- Si se abre una subpágina escribiendo la URL (p. ej. `/exploracion`), Streamlit pide `/exploracion/_stcore/health` y `/host-config`, recibe **404** y reintenta en la raíz. Es del propio Streamlit, no de la app, y no afecta nada.
- Todas las pestañas de las páginas 1, 2, 5 y 7 se abrieron una por una. En celular la página 6 es usable (el heatmap del top queda apretado pero legible).

### 5.3 Cifras
Ningún número de resultados está escrito en el código: KPI, titulares y títulos salen de `cifras_clave.json` o de los parquet. Las únicas constantes fijas son de **método**, no de resultados:
umbrales ADI = 1,32 y CV² = 0,49 (Syntetos, Boylan y Croston, 2005), la meta del 80 % del intervalo 10–90 % y el rango del slider de ajuste.
Comprobado en pantalla: 75 / 49 / 3.990, 29.919, 806, 9, 77 %, +6.582, 0,897 vs 0,907, 0,110 vs 0,170, 92 %, 1.444 / 1.372 / 984.

### 5.4 Capturas (`docs/capturas_app/`)

| Archivo | Vista |
|---|---|
| `00_inicio.jpg` | Inicio (titular, KPI, barras P3, serie) |
| `01_problema_y_datos.jpg` | Problema y decisiones |
| `02_exploracion_serie.jpg` | Serie semanal por canal |
| `03_mundial_titular.jpg`, `03_mundial_base_evento.jpg` | Mundial: KPI y gráfica base vs evento con partidos |
| `04_segmentacion.jpg` | Curvas por clúster e intensidad |
| `05_modelos_escalera.jpg`, `05_modelos_backtesting.jpg`, `05_modelos_por_origen.jpg` | Escalera, tabla de backtesting, heatmap por origen |
| `06_plan_total_top.jpg` | Plan de producción: total del top |
| `06_plan_ajuste_experto_honda.jpg` | Honda, 8 semanas, ajuste +50 % en S8 (intervalo, ingenuo, zona orientativa) |
| `06_plan_talla_color_tela.jpg` | Heatmap talla × color y barras de tela |
| `06_plan_revision_descargas.jpg` | Talla × color, tela y banderas de revisión |
| `07_guia_model_card.jpg` | Guía |
| `90_movil_inicio.jpg`, `91_movil_plan.jpg` | Celular 375 px |

## 6. ⚠️ Lo que el agente 08 (QA y despliegue) tiene que saber

1. **Configuración en Streamlit Community Cloud:** repo `dochoa29-a11y/klixmant-pronostico-demanda`, rama `main`, *main file* **`app/Inicio.py`**, Python **3.12** (en *Advanced settings*).
   Cloud toma `app/requirements.txt` porque está junto al entrypoint (y tiene prioridad sobre el `requirements.txt` de la raíz, que es del notebook e incluye torch y statsmodels).
   `app/.streamlit/config.toml` está junto al entrypoint; si Cloud no aplicara el tema, copiarlo a `.streamlit/config.toml` en la raíz.
2. **La app solo lee `app/data/`.** El repo completo se clona en Cloud, pero el Excel no está versionado (`.gitignore`) y la app no lo necesita.
3. **`app/data/docs/` son copias.** Si cambian `docs/guia_generar_pronostico.md`, `docs/model_card.md`, `docs/registro_decisiones.md` o el Plan de Investigación, correr `python app/copiar_docs.py` y hacer commit.
   El notebook (§8.4) **no** toca esa carpeta: solo borra y reescribe los `.parquet`.
4. **Si se regenera el bundle** (*Run all* del notebook), la app toma las cifras nuevas sin cambiar código. Si cambian nombres de columnas o claves del JSON, la página falla con `KeyError`:
   revisen `app/data/ESQUEMA.md` contra `utils/datos.py` y las páginas.
5. **Revisión cruzada de cifras sugerida** (plan §4 agente 08): la tabla de §5.3 de este reporte; comparar con `cifras_clave.json` y la *model card*.
   Tengan en cuenta que `catalogos_con_venta` = 806 (crudos), 798 normalizados y 792 en el panel: la app usa cada uno donde corresponde y lo explica en el `help` del KPI.
6. **Tiempos:** la primera carga lee y cachea los parquet (~1–2 s en local); luego las páginas cambian casi al instante. La página 4 calcula `curvas_cluster()` una vez (rejilla 99 catálogos × 38 semanas). Midan en Cloud (meta < 3 s).
7. **Memoria:** todo el bundle cabe en unos pocos MB en memoria; no hay riesgo con el límite de ~1 GB.
8. **Privacidad:** la app muestra datos agregados de Klixmant (catálogo × semana). Restrinjan los visores en Cloud; la nota de confidencialidad está en el sidebar.
9. **Errores 404 de `_stcore/health`** al abrir una subpágina por URL directa: son de Streamlit (ver §5.2). No los confundan con fallos de la app.
10. **Mejoras que no se hicieron** (por si hay tiempo): modo oscuro (el tema está fijo en claro y los colores de las tarjetas son claros); curvas codo/silueta del K-means (no están en el bundle);
    zoom sincronizado entre gráficas; descarga del gráfico como PNG (ya existe en la barra de plotly, pero en inglés).

## 7. Decisiones que el grupo debería revisar

- **Textos:** todo lo de `utils/textos.py`, las frases-conclusión y los "¿Cómo leer…?" son **borradores**. Redáctenlos con palabras propias (Turnitin). Están centralizados en `textos.py` para que sea fácil.
- **Títulos de las gráficas** con afirmaciones fuertes ("Durante el Mundial todos los días se encendieron", "Casi ningún catálogo es «suave»"): verifiquen que los sostienen.
- **Demanda desplazada** (página 3): se presenta como **hipótesis por validar** con Klixmant, no como hallazgo.
- **Ajuste experto:** es multiplicativo y no se guarda. Si Klixmant quiere dejar registro, habría que agregar una exportación con el ajuste (hoy va en los CSV como `pred_ajustado`).
- **Nombres duplicados del top** ("CUELLO ALTO RED BULL" / "RED BULL", "CA COLOMBIA ÉLITE" / "COLOMBIA ELITE/CLASICO"): se muestran tal cual vienen del bundle (reporte 06 §6).
