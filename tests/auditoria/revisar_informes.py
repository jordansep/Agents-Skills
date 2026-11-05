#!/usr/bin/env python3
"""Intenta voltear informes reales del skill auditoria-sistemas.

Cada chequeo compara una promesa de SKILL.md con el PDF entregado y, cuando se
indica el repo auditado, con el contenido real de ese repo en el commit citado.

    python tests/auditoria/revisar_informes.py <carpeta-pdf> --repo <repo> [--json salida.json]

Requiere pymupdf y pdftotext. Los informes y el repo auditado no se versionan acá.

Límites conocidos, comprobados a mano contra informes reales:
- C5 y C8 leen la tabla por coordenadas: una diferencia es una señal para revisar,
  no un error probado, porque el parser puede perder filas en tablas partidas.
- C14 descarta propuestas de redacción y textos atribuidos al Board; lo que queda
  se revisa a mano.
- X3 mide si la línea citada ya existía, no si el defecto ya existía.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

SECCIONES = ["Resumen", "Detalle por punto", "Coherencia entre (?:documentos|fuentes)",
             r"¿Listo para [^?\n]+\?", "Lista de tareas(?: para el grupo)?"]
PUNTO = re.compile(r"^(\d{1,2}) · (.+?) (?:--|—|–) (Completo(?: con defectos abiertos)?|Sin defectos a la vista|Avanzado|Inicial|Falta) \((\d{1,3}) ?%\)\s*$", re.M)
FILA = re.compile(r"(?:^|\s{2,})(Sí|Parcial|No)(?=\s{2,}|\s*$)")
CITA = re.compile(r"(?<![\w/.-])((?:docs/)?[A-Za-z0-9][\w./-]*?):(\d+(?:-\d+)?(?:, ?\d+(?:-\d+)?)*)(?![\d:])")
ANCLA_WI = re.compile(r"(?:WI|Issue|work item|PR|commit)\s*#?\s*[\w]+|#\d+", re.I)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s)).strip()


def estado_de(p: int) -> str:
    return "Completo" if p >= 90 else "Avanzado" if p >= 50 else "Inicial" if p >= 1 else "Falta"


def redondear(x: float) -> int:
    return int(x + 0.5)


def texto_pdf(ruta: Path) -> tuple[str, list[int]]:
    import pymupdf
    doc = pymupdf.open(ruta)
    salida = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(ruta), "-"],
                            capture_output=True)
    palabras = [len(p.get_text("words")) for p in doc]
    return salida.stdout.decode("utf-8", "replace").replace("\f", "\n"), palabras


class Repo:
    def __init__(self, ruta: Path | None):
        self.ruta, self.arboles, self.cache = ruta, {}, {}

    def git(self, *a: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(self.ruta), *a], capture_output=True)

    def existe(self, c: str) -> bool:
        return bool(self.ruta and c) and self.git("cat-file", "-e", c + "^{commit}").returncode == 0

    def arbol(self, c: str) -> list[str]:
        if c not in self.arboles:
            s = self.git("ls-tree", "-r", "--name-only", c).stdout.decode("utf-8", "replace")
            self.arboles[c] = s.splitlines()
        return self.arboles[c]

    def resolver(self, c: str, ref: str) -> str | None:
        """docs/03, 06, HU-008, README, plan -> ruta real; None si es ambiguo o no existe."""
        arbol = self.arbol(c)
        if ref in arbol:
            return ref
        cand = re.fullmatch(r"\d{2}", ref) and f"docs/{ref}" or ref
        hits = [p for p in arbol if p.startswith(cand)]
        if not hits:
            base = cand.rsplit("/", 1)[-1].lower()
            hits = [p for p in arbol if p.rsplit("/", 1)[-1].lower().startswith(base)
                    and p.endswith((".md", ".mmd", ".html"))]
        hits = [p for p in hits if not p.startswith((".claude/", ".agents/", "_bmad"))]
        return hits[0] if len(hits) == 1 else None

    def lineas(self, c: str, ruta: str) -> list[str]:
        k = (c, ruta)
        if k not in self.cache:
            b = self.git("show", f"{c}:{ruta}").stdout.decode("utf-8", "replace")
            self.cache[k] = b.splitlines()
        return self.cache[k]


def recorte(t: str, ini: str, fines: list[str]) -> str:
    i = re.search(rf"^\s*{ini}\s*$", t, re.M)
    if not i:
        return ""
    resto = t[i.end():]
    cortes = [m.start() for f in fines for m in [re.search(rf"^\s*{f}\s*$", resto, re.M)] if m]
    return resto[: min(cortes)] if cortes else resto


def filas_por_columna(ruta: Path) -> dict[int, list[dict]]:
    """Lee los criterios por la posición de la columna ¿Cumple?, no por el orden del texto."""
    import pymupdf
    puntos: dict[int, list[dict]] = defaultdict(list)
    actual, x_cumple, x_evid = None, None, None
    for pagina in pymupdf.open(ruta):
        renglones = defaultdict(list)
        for w in pagina.get_text("words"):
            renglones[round(w[1] / 3)].append(w)
        for clave in sorted(renglones):
            r = sorted(renglones[clave], key=lambda w: w[0])
            texto = norm(" ".join(w[4] for w in r))
            m = re.match(r"^(\d{1,2}) · .+ (?:--|—|–) (?:Completo(?: con defectos abiertos)?|Sin defectos a la vista|Avanzado|Inicial|Falta) \(\d{1,3} ?%\)", texto)
            if m:
                actual, x_cumple = int(m[1]), None
                continue
            if texto.startswith(("Coherencia entre documentos", "Para completarlo", "Observaciones")):
                x_cumple = None
                if texto.startswith("Coherencia"):
                    actual = None
                continue
            cab = next((w for w in r if w[4].startswith("¿Cumple")), None)
            if cab and actual is not None:
                x_cumple = cab[0]
                ev = next((w for w in r if w[4].startswith("Evidencia")), None)
                x_evid = ev[0] if ev else x_cumple + 50
                continue
            if actual is None or x_cumple is None:
                continue
            for w in r:
                if w[4] in ("Sí", "Parcial", "No") and abs(w[0] - x_cumple) < 12:
                    puntos[actual].append({"v": w[4], "ev": ""})
            if puntos[actual]:
                puntos[actual][-1]["ev"] += " " + " ".join(w[4] for w in r if w[0] >= x_evid - 2)
    return puntos


def analizar_puntos(t: str, ruta: Path) -> list[dict]:
    detalle = recorte(t, "Detalle por punto", SECCIONES[2:])
    filas = filas_por_columna(ruta)
    puntos = []
    marcas = list(PUNTO.finditer(detalle))
    for i, m in enumerate(marcas):
        cuerpo = detalle[m.end(): marcas[i + 1].start() if i + 1 < len(marcas) else len(detalle)]
        partes = re.split(r"^\s*Para completarlo\s*:?", cuerpo, maxsplit=1, flags=re.M)
        fs = filas.get(int(m[1]), [])
        sin_evid = [f["ev"][:70] for f in fs if not (CITA.search(norm(f["ev"])) or ANCLA_WI.search(f["ev"]))]
        puntos.append({"n": int(m[1]), "nombre": norm(m[2]), "estado": m[3], "pct": int(m[4]),
                       "filas": [f["v"] for f in fs], "sin_evidencia": len(sin_evid), "ej_sin_evidencia": sin_evid,
                       "tiene_para_completarlo": len(partes) > 1,
                       "para_completarlo": norm(partes[1]) if len(partes) > 1 else ""})
    return puntos


def revisar(ruta: Path, repo: Repo) -> dict:
    t, palabras = texto_pdf(ruta)
    ch: dict[str, dict] = {}

    def anotar(k: str, ok, det: str = "", n: int | None = None):
        ch[k] = {"ok": ok, "det": det}
        if n is not None:
            ch[k]["n"] = n

    pos = [re.search(rf"^\s*{s}\s*$", t, re.M) for s in SECCIONES]
    faltan = [s for s, m in zip(SECCIONES, pos) if not m]
    orden = [m.start() for m in pos if m]
    anotar("C1 cinco secciones en orden", not faltan and orden == sorted(orden), "faltan: " + ", ".join(faltan) if faltan else "")
    enc = re.search(r"Corregido:\s*([0-9a-f]{7,40})\s+del\s+(\d{4}-\d{2}-\d{2}).*?Corte:.*?Modo:\s*\S.*", t)
    anotar("C2 encabezado con commit, fecha, corte y modo", bool(enc))
    sha = enc[1] if enc else ""
    anotar("C3 nombre con distintivo", bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}-Informe-completitud-.+-[0-9a-z]{2,}", ruta.stem)
                                            and re.search(r"-(?:[0-9a-f]{7}|\d{4}|v\d+)(?:-\d{4})?$", ruta.stem)), ruta.stem)

    puntos = analizar_puntos(t, ruta)
    anotar("C4 detalle por punto legible", bool(puntos) and all(p["filas"] for p in puntos), f"{len(puntos)} puntos")
    malos, estados, vin, sinfin = [], [], [], []
    for p in puntos:
        if p["filas"]:
            calc = redondear(100 * sum({"Sí": 1, "Parcial": .5, "No": 0}[f] for f in p["filas"]) / len(p["filas"]))
            if calc != p["pct"]:
                malos.append(f"{p['n']}: dice {p['pct']} %, {'/'.join(p['filas'])} da {calc} %")
        estado = "Completo" if p["estado"].startswith(("Completo", "Sin defectos")) else p["estado"]
        if estado_de(p["pct"]) != estado and not (estado == "Avanzado" and p["pct"] >= 90) and not (estado == "Inicial" and p["pct"] == 0):
            estados.append(f"{p['n']}: {p['pct']} % no es {p['estado']}")
        if not p["tiene_para_completarlo"]:
            sinfin.append(str(p["n"]))
    anotar("C5 % coincide con los criterios", not malos if puntos else None, "; ".join(malos), len(malos))
    anotar("C6 estado coincide con el %", not estados if puntos else None, "; ".join(estados))
    anotar("C7 cada punto cierra con Para completarlo", not sinfin if puntos else None, "sin: " + ",".join(sinfin))
    tot = sum(len(p["filas"]) for p in puntos)
    sev = sum(p["sin_evidencia"] for p in puntos)
    anotar("C8 cada criterio tiene evidencia", sev == 0 if puntos else None, f"{sev} de {tot} filas sin cita", sev)
    anotar("C9 separa CONFIRMADO y PROBABLE", "CONFIRMADO" in t and "PROBABLE" in t)
    anotar("C10 declara fuentes y límites", bool(re.search(r"MCP|API REST", t[:2500]))
           and bool(re.search(r"no se pudo|no se revis|no se compar|no evaluad|no verificab|No se us", t, re.I)))
    anotar("C11 sin páginas casi vacías", all(w >= 40 for w in palabras[:-1]), f"palabras por pág.: {palabras}")
    tareas = recorte(t, SECCIONES[4], [])
    casillas = len(re.findall(r"[☐-]|\[ \]", tareas))
    anotar("C12 lista de tareas con casillas", casillas > 0, f"{casillas} tareas", casillas)

    plano = norm(t)
    # C13: las citas archivo:línea existen en el commit auditado.
    res = {"ok": 0, "fuera": [], "sin_resolver": set()}
    if repo.existe(sha):
        for m in CITA.finditer(plano):
            ruta_real = repo.resolver(sha, m[1])
            if not ruta_real:
                res["sin_resolver"].add(m[1])
                continue
            total = len(repo.lineas(sha, ruta_real))
            for tramo in re.split(r", ?", m[2]):
                ult = int(tramo.split("-")[-1])
                if ult <= total:
                    res["ok"] += 1
                else:
                    res["fuera"].append(f"{m[1]}:{tramo} (tiene {total})")
        anotar("C13 citas dentro del archivo real", not res["fuera"],
               f"{res['ok']} válidas; fuera: {res['fuera'][:6]}; sin resolver: {sorted(res['sin_resolver'])[:8]}", len(res["fuera"]))
        # C14: lo que el informe entrecomilla y atribuye a una cita está en ese archivo.
        q_ok, q_otro, q_mal = 0, [], []
        limpio = lambda s: "".join(x for x in s.lower() if x.isalnum())
        todo = {f: limpio(" ".join(repo.lineas(sha, f))) for f in repo.arbol(sha)
                if f.endswith((".md", ".mmd", ".html")) and not f.startswith((".claude/", ".agents/", "_bmad"))}
        for m in re.finditer(r"«([^«»]{12,160})»", plano):
            cerca = plano[max(0, m.start() - 90): m.end() + 60]
            cs = {c for c in (repo.resolver(sha, x[1]) for x in CITA.finditer(cerca)) if c}
            if not cs or "…" in m[1] or "..." in m[1]:
                continue
            antes = plano[max(0, m.start() - 60): m.start()].lower()
            if re.search(r"por ejemplo|agreguen|sumen|cambien|por $|reemplacen|corrijan|escriban|digan|ajusten|wi #\\d+|issue #\\d+|el board", antes):
                continue
            b_ = limpio(m[1])
            if any(b_ in todo.get(c, "") for c in cs):
                q_ok += 1
            elif any(b_ in v for v in todo.values()):
                q_otro.append(m[1][:50])
            else:
                q_mal.append({"cita": m[1], "fuente": sorted(cs), "ctx": cerca})
        anotar("C14 citas textuales están en la fuente", not q_mal if (q_ok or q_mal or q_otro) else None,
               f"{q_ok} ok; {len(q_otro)} en otro archivo; {len(q_mal)} en ninguno", len(q_mal))
        ch["C14 citas textuales están en la fuente"]["no_halladas"] = q_mal
    else:
        anotar("C13 citas dentro del archivo real", None, f"commit {sha or '?'} no disponible")
        anotar("C14 citas textuales están en la fuente", None, "commit no disponible")
    return {"archivo": ruta.name, "commit": sha, "fecha": enc[2] if enc else "", "puntos": puntos,
            "mtime": ruta.stat().st_mtime, "chequeos": ch, "citas": {"ok": res["ok"], "fuera": res["fuera"], "sin_resolver": sorted(res["sin_resolver"])}}


def cruces(informes: list[dict], repo: Repo) -> list[dict]:
    """X1: mismo commit y punto, otro %. X2: el archivo del punto no cambió y el % sí."""
    filas, por_punto = [], defaultdict(list)
    for inf in sorted(informes, key=lambda i: i["mtime"]):
        for p in inf["puntos"]:
            por_punto[p["n"]].append((inf["commit"], p["pct"], inf["archivo"], p["estado"]))
    rutas = {1: "docs/01", 2: "docs/02", 3: "docs/03", 4: "docs/04", 5: "docs/adr", 6: "docs/06", 7: "docs/07",
             8: "docs/historias", 9: "docs/testing", 10: "docs/10"}
    for n, h in sorted(por_punto.items()):
        for (c1, p1, a1, e1), (c2, p2, a2, e2) in zip(h, h[1:]):
            if p1 == p2:
                continue
            if c1 == c2:
                filas.append({"tipo": "X1 mismo commit, otro %", "punto": n, "de": f"{p1} % ({a1})", "a": f"{p2} % ({a2})", "commit": c1})
            elif n in rutas and repo.existe(c1) and repo.existe(c2):
                arbol = repo.arbol(c2)
                archivos = [f for f in arbol if f.startswith(rutas[n])]
                if archivos and repo.git("diff", "--quiet", c1, c2, "--", *archivos).returncode == 0:
                    filas.append({"tipo": "X2 archivo sin cambios, otro %", "punto": n, "de": f"{p1} % en {c1}", "a": f"{p2} % en {c2}", "commit": f"{c1}..{c2}"})
    return filas


def tardios(informes: list[dict], repo: Repo) -> list[dict]:
    """X3: líneas citadas en Para completarlo que ya existían cuando otro informe dio ese punto por Completo."""
    filas = []
    orden = sorted(informes, key=lambda i: i["mtime"])
    for j, inf in enumerate(orden):
        for p in inf["puntos"]:
            previos = [(i["commit"], q["pct"], i["archivo"]) for i in orden[:j] for q in i["puntos"]
                       if q["n"] == p["n"] and q["estado"] == "Completo" and i["commit"] != inf["commit"]]
            if not previos or not p["para_completarlo"] or p["pct"] >= 100:
                continue
            base, pct, arch = previos[-1]
            ya, nuevas = [], []
            for m in CITA.finditer(p["para_completarlo"]):
                ruta = repo.resolver(inf["commit"], m[1])
                if not ruta:
                    continue
                for tramo in re.split(r", ?", m[2]):
                    n = tramo.split("-")[0]
                    bl = repo.git("blame", "-s", "-L", f"{n},{n}", inf["commit"], "--", ruta)
                    if bl.returncode:
                        continue
                    sha = bl.stdout.decode("utf-8", "replace").split()[0].lstrip("^")
                    anc = repo.git("merge-base", "--is-ancestor", sha, base).returncode == 0
                    (ya if anc else nuevas).append(f"{m[1]}:{n}")
            if ya or nuevas:
                filas.append({"punto": p["n"], "informe": inf["archivo"], "pct": p["pct"], "base": base, "pct_base": pct,
                              "ya_estaban": ya, "nuevas": nuevas})
    return filas


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("carpeta", type=Path)
    ap.add_argument("--repo", type=Path)
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()
    repo = Repo(a.repo)
    informes = [revisar(p, repo) for p in sorted(a.carpeta.glob("*Informe-completitud*.pdf"))]
    claves = sorted({k for i in informes for k in i["chequeos"]}, key=lambda s: int(re.match(r"C(\d+)", s)[1]))
    fallas = 0
    print(f"{len(informes)} informes\n")
    for k in claves:
        v = [i["chequeos"].get(k, {}).get("ok") for i in informes]
        ok, ko, na = v.count(True), v.count(False), v.count(None)
        fallas += ko
        print(f"{k:48} pasa {ok:2}  falla {ko:2}  n/a {na:2}")
    print("\nFallas:")
    for i in informes:
        for k in claves:
            c = i["chequeos"].get(k, {})
            if c.get("ok") is False:
                print(f"- {i['archivo'][11:-4]} | {k.split()[0]} | {c['det'][:230]}")
    x = cruces(informes, repo)
    print("\nCruces entre informes:")
    for f in x:
        print(f"- {f['tipo']}: punto {f['punto']}: {f['de']} → {f['a']}")
    tard = tardios(informes, repo)
    print("\nHallazgos tardíos (líneas citadas que ya existían cuando el punto se dio por Completo):")
    for f in tard:
        print(f"- punto {f['punto']} en {f['informe'][11:-4]} ({f['pct']} %), base {f['base']} ({f['pct_base']} %): "
              f"{len(f['ya_estaban'])} ya estaban, {len(f['nuevas'])} nuevas")
    if a.json:
        a.json.write_text(json.dumps({"informes": informes, "cruces": x, "tardios": tard}, ensure_ascii=False, indent=1), encoding="utf-8")
    return 1 if fallas or x else 0


if __name__ == "__main__":
    raise SystemExit(main())
