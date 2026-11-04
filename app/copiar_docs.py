"""Copia a app/data/docs/ los textos que muestra la página 7 (y la 1).

La app solo lee app/data/ (así funciona igual en Streamlit Cloud y no depende
de carpetas del notebook). Este script se corre a mano cada vez que cambien
los documentos de docs/ o el Plan de Investigación:

    python app/copiar_docs.py

No escribe .parquet (el notebook §8.4 borra y reescribe esos).
"""
from __future__ import annotations

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "app" / "data" / "docs"

COPIAS = {
    "guia_generar_pronostico.md": RAIZ / "docs" / "guia_generar_pronostico.md",
    "model_card.md": RAIZ / "docs" / "model_card.md",
    "registro_decisiones.md": RAIZ / "docs" / "registro_decisiones.md",
}

# Secciones que se extraen del Plan de Investigación (título exacto del encabezado ##)
EXTRACTOS = {
    "decisiones_negocio.md": "## 2. Entendimiento del negocio",
    "reglas_limpieza_plan.md": "### 4.1 Limpieza y reglas",
    "bibliografia.md": "## 11. Bibliografía y fuentes",
}


def extraer(texto: str, encabezado: str) -> str:
    """Devuelve la sección que empieza en `encabezado` hasta el siguiente encabezado del mismo nivel o superior."""
    nivel = len(encabezado.split(" ")[0])
    lineas = texto.splitlines()
    inicio = next(i for i, l in enumerate(lineas) if l.startswith(encabezado))
    patron = re.compile(r"^#{1,%d} " % nivel)
    fin = next((j for j in range(inicio + 1, len(lineas)) if patron.match(lineas[j])), len(lineas))
    return "\n".join(lineas[inicio:fin]).strip().rstrip("-").strip() + "\n"


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    for nombre, origen in COPIAS.items():
        texto = origen.read_text(encoding="utf-8")
        # La app no muestra el aviso de borrador ni emojis de los documentos de trabajo
        texto = re.sub(r"^> ✍️ \*\*Borrador.*\n(>.*\n)*\n?", "", texto, flags=re.M)
        texto = re.sub("[\U0001F000-\U0001FAFF☀-➿️]+ ?", "", texto)
        (DESTINO / nombre).write_text(texto, encoding="utf-8")
        print("copiado", nombre)
    plan = (RAIZ / "Plan_de_Investigacion_Klixmant.md").read_text(encoding="utf-8")
    for nombre, encabezado in EXTRACTOS.items():
        (DESTINO / nombre).write_text(extraer(plan, encabezado), encoding="utf-8")
        print("extraído", nombre)


if __name__ == "__main__":
    main()
