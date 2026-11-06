#!/usr/bin/env python3
"""Compara qué defectos conocidos encontró cada corrida de lectores, para elegir su modelo.

    python tests/auditoria/medir_lectores.py <vara.json> <trabajo-variante-1> <trabajo-variante-2>… [--contexto]

La vara es una lista de {"id", "patron"} y no se versiona acá, porque describe un proyecto auditado.
Cada carpeta de trabajo se llama <variante>-<corrida>, con las fichas en fichas/.

Busca sólo en lo que la ficha presenta como hallazgo: filas que no dan Sí, defectos, observaciones y
tareas. Un patrón da una mención, no un hallazgo probado: revisá el resultado con --contexto.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path


def hallazgos(trabajo: Path) -> list[str] | None:
    """Los textos de hallazgo de una corrida, o None si todavía no tiene fichas."""
    rutas = sorted((trabajo / "fichas").glob("*.json"))
    if not rutas:
        return None
    textos = []
    for ruta in rutas:
        for p in json.loads(ruta.read_text(encoding="utf-8")).get("puntos", []):
            textos += [" ".join(str(f.get(c, "")) for c in ("criterio", "evidencia", "falta")) for f in p.get("filas", []) if f.get("cumple") != "Sí"]
            textos += [f"{d.get('texto', '')} ({d.get('cita', '')})" for d in p.get("defectos", [])]
            textos += [str(o) for o in p.get("observaciones", [])]
            textos += [f"{t.get('texto', '')} ({t.get('cita', '')})" for t in p.get("para_completar", [])]
    return [re.sub(r"\s+", " ", unicodedata.normalize("NFC", t)) for t in textos]


def medir(vara: list[dict], trabajos: list[Path]) -> dict:
    """Por corrida: los id encontrados y sus textos; por variante: promedio y unión."""
    corridas = {}
    for trabajo in trabajos:
        textos = hallazgos(trabajo)
        if textos is None:
            corridas[trabajo.name] = None
            continue
        encontrados = {d["id"]: [t for t in textos if re.search(d["patron"], t)] for d in vara}
        corridas[trabajo.name] = {"encontrados": {k: v for k, v in encontrados.items() if v}, "hallazgos": len(textos)}
    variantes: dict[str, list[dict]] = {}
    for nombre, corrida in corridas.items():
        if corrida:
            variantes.setdefault(nombre.rsplit("-", 1)[0], []).append(corrida)
    resumen = {nombre: {"corridas": len(lista), "promedio": sum(len(c["encontrados"]) for c in lista) / len(lista),
                        "union": len(set().union(*(c["encontrados"] for c in lista)))} for nombre, lista in variantes.items()}
    return {"corridas": corridas, "variantes": resumen}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("vara", type=Path)
    ap.add_argument("trabajos", nargs="+", type=Path)
    ap.add_argument("--contexto", action="store_true", help="muestra el texto que coincidió, para revisarlo a mano")
    a = ap.parse_args()
    vara = json.loads(a.vara.read_text(encoding="utf-8"))
    r = medir(vara, a.trabajos)
    listas = {k: v for k, v in r["corridas"].items() if v}
    ancho = max(len(d["id"]) for d in vara)
    print(" " * ancho, *listas)
    for d in vara:
        print(d["id"].ljust(ancho), *("sí".ljust(len(k)) if d["id"] in v["encontrados"] else "—".ljust(len(k)) for k, v in listas.items()))
    print()
    for nombre, s in r["variantes"].items():
        print(f"{nombre}: {s['promedio']:.1f} de {len(vara)} por corrida · {s['union']} entre las {s['corridas']}")
    for nombre, corrida in r["corridas"].items():
        print(f"{nombre}: {'sin fichas' if corrida is None else str(corrida['hallazgos']) + ' hallazgos en total'}")
    if a.contexto:
        for nombre, corrida in listas.items():
            print(f"\n## {nombre}")
            for clave, textos in corrida["encontrados"].items():
                print(f"- {clave}: {textos[0][:300]}")


if __name__ == "__main__":
    main()
