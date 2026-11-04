# Reporte de traspaso — Agente 08 (QA y despliegue de la app)

**Fecha:** 4-nov-2026 · **Alcance:** QA de la app Streamlit (`app/`) y su publicación en Streamlit Community Cloud
(`PLAN_DESPLIEGUE_STREAMLIT.md` §4, bloque "Agente 08").
**No se tocó el notebook** ni el póster. Lean también los reportes 06 y 07.
Las cifras vigentes son las **posteriores a la corrección de `early_stopping`** (reporte 05 §2). La app las lee de `app/data/cifras_clave.json`.

**🌐 App publicada:** <https://klixmant-pronostico.streamlit.app/>

---

## 1. Qué se entregó

| Archivo / cambio | Qué es |
|---|---|
| `app/paginas/2_exploracion.py`, `app/paginas/5_modelos_y_validacion.py` | Pestañas **perezosas** (`st.tabs(..., key=..., on_change="rerun")` + `if tabs[i].open:`): solo se calcula y dibuja la pestaña abierta |
| `app/utils/estilo.py` | `mostrar()` saca el título de cada gráfica plotly a HTML (`.fig-titulo`) para que se ajuste al ancho; `dec(signo=True)` para los deltas |
| `app/paginas/2_exploracion.py` | `.dt.dayofweek` → `.dt.day_of_week` (aviso `Pandas4Warning`) |
| `README.md` | Enlace a la app, fila del tablero en ✅, nota de acceso y este reporte en la tabla de `docs/` |
| `docs/REPORTE_AGENTE_08_despliegue.md` | Este reporte |
| Streamlit Community Cloud | App `klixmant-pronostico` desplegada desde `dochoa29-a11y/klixmant-pronostico-demanda`, rama `main` |

Commits: `40e4810` (arreglos de QA) y el de este reporte + README.

## 2. QA en local

**Entorno:** `C:\Users\diani\.venvs\klixmant-app312` (Python 3.12, el del `.claude/launch.json`) y el venv limpio del agente 07
`C:\Users\diani\.venvs\klixmant-app-limpio` (solo `app/requirements.txt`: streamlit 1.66.1, pandas 3.1.1, numpy 2.5.4, plotly 7.1.0, pyarrow 26.0.1).

**Cómo se revisó:**
- Navegador integrado, recorriendo las 8 vistas por el menú lateral y abriendo **todas las pestañas** (4 en la página 1, 7 en la 2, 9 en la 5, 7 en la 7),
  en escritorio (1440 × 900) y en celular (375 × 812).
- `streamlit.testing.v1.AppTest` (scripts en el scratchpad del agente 08, no están en el repo): las 8 vistas en frío y en caliente, y la página 6 con interacción.
  Las descargas CSV se capturaron interceptando el almacenamiento de archivos de Streamlit y se volvieron a leer con pandas.

### 2.1 Hallazgos y arreglos

| # | Hallazgo | Gravedad | Arreglo |
|---|---|---|---|
| 1 | Páginas 2 y 5 tardaban **3–4 s** en el navegador: dibujaban 8 y 11 gráficas plotly a la vez, aunque estuvieran en pestañas ocultas (el script de Python tardaba < 1 s; el costo era el dibujo en el navegador) | Media (meta < 3 s) | Pestañas perezosas: al abrir la página se dibuja una sola gráfica. Cambiar de pestaña ahora vuelve a ejecutar la página (~0,5–1 s) |
| 2 | Consola: `Error: <text> attribute y: Expected length, "-Infinity"` (×3), de plotly al dibujar gráficas dentro de pestañas ocultas (ancho 0) | Baja | Desaparece con el arreglo 1: consola limpia en las 8 vistas |
| 3 | En celular, los **títulos de las gráficas se cortaban** por la derecha (plotly no ajusta el texto del título; p. ej. uno llegaba a 487 px en una pantalla de 375 px) | Media (legibilidad) | El título se muestra en HTML encima de la gráfica (se ajusta en 2 líneas) y se libera el margen superior. **Efecto secundario:** el PNG que se baja con la cámara de plotly ya no trae el título |
| 4 | Página 5: los deltas positivos salían sin signo («0,220 vs ingenuo» en el holdout, donde el ingenuo gana) | Baja (honestidad del mensaje) | `E.dec(..., signo=True)` → «+0,220 vs ingenuo». Se usa guion ASCII porque `st.metric` decide la flecha mirando si el texto empieza por `-` |
| 5 | `Pandas4Warning: Series.dt.dayofweek is deprecated` en el log del servidor (página 2) | Baja | `.dt.day_of_week` |

No se encontraron excepciones en ninguna vista ni pestaña, antes ni después de los arreglos.
El único aviso que queda en consola es interno de Streamlit (`No script tag of type "javascript/worker"…`, del visor de graphviz de la página 1),
más los 404 de `_stcore/health` cuando se abre una subpágina escribiendo la URL (reporte 07 §5.2). Ninguno es de la app.

### 2.2 Tiempos

Script de Python por página (AppTest, venv limpio, tras los arreglos):

| Vista | En frío | En caliente |
|---|---|---|
| Inicio | 5,3 s (incluye importar streamlit/plotly/pandas y leer el bundle: solo pasa una vez por proceso) | 0,3 s |
| 1 Problema y datos | 0,2 s | 0,1 s |
| 2 Exploración | 0,2 s | 0,1 s |
| 3 Mundial | 0,6 s | 0,4 s |
| 4 Segmentación | 0,4 s | 0,3 s |
| 5 Modelos | 0,2 s | 0,2 s |
| 6 Plan de producción | 0,8 s | 0,7–1,1 s |
| 7 Guía | 0,2 s | 0,2 s |

En el navegador (local), el título de cada página aparece en ~0,2–0,4 s y la página queda completa en ~1–2 s (la 6, con 4 gráficas, ~2 s).

### 2.3 Cifras (revisión cruzada)

Todo lo visible coincide con `cifras_clave.json → kpi` y con la *model card* (`docs/model_card.md` §4). No queda ninguna cifra del reporte 04:
la búsqueda de 0,79 / 0,215 / 0,718 / «90 uds» / 31 % en `app/` solo aparece en la *model card* (línea 97), donde se explica la corrección «de … a …».

| Dónde | En pantalla | Fuente |
|---|---|---|
| Inicio | 75 uds vs 49 reales; media móvil 3.990 | `kpi.colombia_post_mundial` (75,25 / 49 / 3.990) |
| Inicio | 29.919 · 806 · 9 · 77 % · +6.582 | `unidades_totales`, `catalogos_con_venta`, `meses_historia`, `pct_unidades_top` (0,7696), `uds_evento_colombia` |
| Inicio / 5 | WAPE 0,897 vs 0,907; total semanal 0,110 vs 0,170 | `wape_top_backtesting`, `holdout_wape_total_semanal` |
| 5 | Después del Mundial 0,585 (−0,015); holdout h=1…4 0,696 (**+0,220**: gana el ingenuo); cobertura 92 % | `wape_top_post_backtesting`, `holdout_wape_top_h4`, `cobertura_intervalo_holdout` |
| 3 | +6.582 (87 %), resto −280, total neto 6.302, motos −64 %, autos −64 % | `uds_evento_*`, `incremental_mundial_linea` |
| 4 | El clúster es la 2.ª variable de 37 | `importancia_permutacion` (desv_4, **cluster**, lag_1…) |
| 6 | Top 1.444 (ingenuo 1.372), cola 984, real últimas 4 sem. 1.275, 0 para revisar | `pronostico_4s_*`, `real_ultimas_4s_top`, `catalogos_revisar` |

**Honestidad:** Inicio («Lo honesto»: «el modelo no le gana con claridad al ingenuo»), titular de la página 5 («por catálogo empata con el ingenuo»),
KPI del holdout en rojo (+0,220) con la ayuda «Aquí el ingenuo gana» y la nota del IC 90 % que incluye el 0. ✅

### 2.4 Página 6 (herramienta)

| Prueba | Resultado |
|---|---|
| Σ Total del top, 4 semanas | 1.444 uds; ingenuo 1.372 (+5 % el modelo) |
| Catálogo CUELLO ALTO HONDA REFLECTIVO | 216 uds (= reporte 06 §3.2); ingenuo 236; real últimas 4 sem. 232 |
| Horizonte 8 semanas | 435 uds; semanas 5–8 sombreadas como orientativas |
| Ajuste +50 % en S8, todos los catálogos | 457 uds (+22 por ajuste); en el CSV, S8: `pred` 43,31 → `pred_ajustado` 64,96; la tela sube de 4.891,6 a 5.186,7 |
| Mismo ajuste, solo el catálogo elegido | Aviso «no se propaga a tela»; tela ajustada = tela original (diferencia 0) |
| Buscar «AUDI» en la cola | Sin errores |
| Volver al total con el ajuste activo | 3.096 uds (+172 por ajuste) |
| 3 descargas CSV | `pronostico_catalogo_…csv` (3.168 filas = 792 × 4; 6.336 con 8 semanas), `talla_color` (2.412 / 4.824), `tela` (480 / 960); separador `;`, coma decimal, UTF-8 con BOM; sufijo `_8s_ajustado` cuando corresponde |

### 2.5 Celular y legibilidad

- Sin *scroll* horizontal a 375 px en ninguna vista (el ancho del documento queda en 375). Las tablas markdown anchas (página 1, guía) se desplazan dentro de su propio recuadro.
- Los KPI se apilan en una columna; titular y `h1` más pequeños (CSS `@media (max-width: 640px)` del agente 07).
- El menú lateral se colapsa en celular (`initial_sidebar_state="auto"`).
- Texto oscuro (#262730 / #1F2A44) sobre blanco o #F4F8FC. La marca «borrador» (#8A6D00 sobre #FFF8DC) queda en ~4,5 : 1, justo en el mínimo AA para texto normal.

## 3. Despliegue en Streamlit Community Cloud

| Campo | Valor |
|---|---|
| URL | <https://klixmant-pronostico.streamlit.app/> |
| Repositorio | `dochoa29-a11y/klixmant-pronostico-demanda` (privado) |
| Rama | `main` |
| Main file path | `app/Inicio.py` |
| Python | 3.12 (*Advanced settings*; coincide con el venv donde se probó) |
| Dependencias | `app/requirements.txt`. Cloud lo toma porque está junto al entrypoint y tiene prioridad sobre el `requirements.txt` de la raíz (que es del notebook e incluye torch y statsmodels) |
| Tema | `app/.streamlit/config.toml` **sí se aplica** en Cloud (sidebar #F4F8FC, primario #0072B2): no hizo falta copiarlo a la raíz |
| Secretos | Ninguno: la app solo lee `app/data/` |
| Cuenta | La de GitHub `dochoa29-a11y`; el despliegue se hizo desde el navegador de quien administra la cuenta (el agente no maneja credenciales) |

### 3.1 Verificación en Cloud
Se abrió la app directamente (`https://klixmant-pronostico.streamlit.app/~/+/`, el iframe que Cloud pone dentro de la página) y se recorrieron las 8 vistas y todas las pestañas de las páginas 2, 5 y 7:
**0 excepciones** y cifras iguales a las de local. Sirve la versión con los arreglos (aparece `.fig-titulo`).

| Vista | Título visible | Página completa |
|---|---|---|
| Inicio (primera carga, ya despierta) | — | ~4,3 s |
| 1 Problema y datos | 0,3–1,8 s | 0,8–2,1 s |
| 2 Exploración | 0,5–0,7 s | 1,0–1,2 s |
| 3 Mundial | 0,4 s | 2,6 s |
| 4 Segmentación | 0,5 s | 1,5 s |
| 5 Modelos | 0,5–0,9 s | 1,2–1,9 s |
| 6 Plan de producción | 0,5–1,0 s | 1,9–2,8 s |
| 7 Guía | 0,5–3,1 s (la primera vez lee los `.md`) | 2,8–4,2 s |

Medido con el panel del navegador **oculto** (el navegador frena los temporizadores de las pestañas en segundo plano), así que son cotas altas.
Las páginas quedan entre 1 y 3 s; solo la primera visita a la Guía y la carga inicial pasan de 3 s.
**Ojo:** si nadie la abre en varios días, Community Cloud **duerme** la app. La primera visita muestra «This app has gone to sleep» y un botón para despertarla, que tarda alrededor de 1 minuto.
Ábranla un rato antes de la sustentación.

## 4. ⚠️ Quién puede ver la app

**Decisión del grupo (4-nov-2026): app pública. Cualquiera con el enlace puede verla.**
El agente recomendó dejarla privada, solo para los invitados del grupo y el docente, porque muestra datos agregados de Klixmant (catálogo × semana, pronósticos, telas).
El repositorio **sigue privado**: el código y los datos no se pueden descargar desde GitHub. Lo que la app muestra, y las 3 descargas CSV de la página 6, sí quedan a la vista de quien tenga el enlace.

Para hacerla privada: en share.streamlit.io, menú **⋮** de la app → **Settings** → **Sharing** → *Who can view this app* → **Only specific people can view this app** y agreguen los correos
del grupo y del docente (cada uno entra con Google o GitHub con ese correo). Community Cloud permite **una** app privada por cuenta.
Comenten con Klixmant si están de acuerdo con que quede pública.

## 5. Cómo redesplegar

- **Automático:** cada `git push` a `main` que toque el repo redespliega la app en ~1–2 min (Cloud vigila la rama).
- **Si cambia el bundle** (*Run all* del notebook → `app/data/*.parquet` y `cifras_clave.json`): commit + push; no hay que tocar código.
  Si cambian `docs/guia_generar_pronostico.md`, `docs/model_card.md` o `docs/registro_decisiones.md`: `python app/copiar_docs.py` antes del commit (reporte 07 §6.3).
- **Si cambia `app/requirements.txt`:** Cloud reinstala solo; si se queda con la versión anterior, ⋮ → **Reboot app**.
- **A mano:** share.streamlit.io → ⋮ de la app → **Reboot app** (vuelve a clonar y a arrancar). Para ver errores: **Manage app** (abajo a la derecha, dentro de la app) → logs.
- **Cambiar Python:** no se puede editar en una app ya creada: hay que borrarla (⋮ → *Delete*) y volver a desplegarla con la misma URL y la configuración de §3.
- **Probar antes de subir:** `streamlit run app/Inicio.py` con el venv de 3.12 (README, "Cómo correr la app").
  Ojo: con `runOnSave = false`, si se edita un archivo de `app/utils/` hay que **reiniciar** el servidor local; Streamlit no recarga ese módulo y puede mostrar errores falsos.

## 6. Pendientes para el grupo

1. **Turnitin:** todos los textos de la app (`app/utils/textos.py`, las frases-conclusión y los "¿Cómo leer…?" de cada página), los documentos de `docs/` y los reportes son **borradores**: redáctenlos con sus palabras.
   Tras editarlos, hagan push y la app se actualiza sola.
2. **Acceso:** decidir con Klixmant si la app queda pública (§4).
3. **Póster:** queda para después (fuera del alcance de los agentes 06–08).
4. **Página 1 → pestaña "El problema y las decisiones":** muestra el extracto del Plan de Investigación con «Acción: confirmar con el docente la decisión catálogo frente a referencia **antes del 5-nov**». Es una nota interna:
   cuando la confirmen, actualicen el plan y corran `python app/copiar_docs.py`. En el mismo extracto aparece «Klixmsoft»: verifiquen que es el nombre correcto del software.
5. **Detalles menores no corregidos:**
   - Los ejes en porcentaje de plotly salen como «5%» (sin espacio), mientras que los textos dicen «5 %».
   - Al cambiar de pestaña en las páginas 2 y 5, los controles de la pestaña que se cierra (p. ej. el slider del Pareto) vuelven a su valor inicial. Es el costo de las pestañas perezosas.
   - Los nombres duplicados del top («CUELLO ALTO RED BULL» / «RED BULL», «CA COLOMBIA ÉLITE» / «COLOMBIA ELITE/CLASICO») siguen igual (reporte 06 §6).
   - Mejoras del reporte 07 §6.10 (modo oscuro, codo/silueta del K-means, zoom sincronizado).
