#!/usr/bin/env python3
"""Versionado de los agentes del repositorio.

Cada agente tiene un manifiesto en agentes/<agente>/agente.json (con su versión
SemVer y las carpetas de sus skills) y un agentes/<agente>/CHANGELOG.md.
La política está en VERSIONADO.md.

Uso:
    python3 scripts/versionado.py listar
    python3 scripts/versionado.py subir documentacion minor --agregado "Nuevo componente de línea de tiempo"
    python3 scripts/versionado.py verificar [--base origin/main]
    python3 scripts/versionado.py notas documentacion [0.4.0]
    python3 scripts/versionado.py pendientes      # versiones sin etiqueta (lo usa la GitHub Action)

Solo usa la biblioteca estándar.
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z.-]+))?$")
SECCIONES = ["Agregado", "Cambiado", "Corregido", "Eliminado", "Seguridad"]
TITULO_VERSION = re.compile(r"^## \[([^\]]+)\](?: - (\d{4}-\d{2}-\d{2}))?\s*$", re.M)


def git(*args):
    r = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True)
    return r.returncode, r.stdout


def clave(version):
    m = SEMVER.match(version or "")
    if not m:
        return None
    mayor, menor, parche, pre = m.groups()
    return (int(mayor), int(menor), int(parche), 0 if pre else 1, pre or "")


def leer_agentes():
    agentes = {}
    for manifiesto in sorted((RAIZ / "agentes").glob("*/agente.json")):
        datos = json.loads(manifiesto.read_text(encoding="utf-8"))
        agentes[manifiesto.parent.name] = (manifiesto, datos)
    return agentes


def secciones_changelog(texto):
    """Devuelve [(version, fecha, cuerpo)] en el orden del archivo."""
    marcas = list(TITULO_VERSION.finditer(texto))
    salida = []
    for i, m in enumerate(marcas):
        fin = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        salida.append((m.group(1), m.group(2), texto[m.end():fin].strip()))
    return salida


def ruta_changelog(nombre):
    return RAIZ / "agentes" / nombre / "CHANGELOG.md"


# ---------- listar ----------
def cmd_listar(_):
    agentes = leer_agentes()
    if not agentes:
        print("No hay agentes en agentes/*/agente.json")
        return 0
    ancho = max(len(n) for n in agentes)
    for nombre, (_, datos) in agentes.items():
        print(f"{nombre.ljust(ancho)}  {datos.get('version', '?'):<10} {', '.join(datos.get('skills', []))}")
    return 0


# ---------- subir ----------
def cmd_subir(a):
    agentes = leer_agentes()
    if a.agente not in agentes:
        print(f"ERROR: no existe el agente «{a.agente}». Agentes: {', '.join(agentes) or 'ninguno'}", file=sys.stderr)
        return 2
    manifiesto, datos = agentes[a.agente]
    actual = clave(datos.get("version"))
    if not actual:
        print(f"ERROR: la versión actual «{datos.get('version')}» no es SemVer", file=sys.stderr)
        return 2
    mayor, menor, parche = actual[:3]
    if a.nivel == "major":
        nueva = f"{mayor + 1}.0.0"
    elif a.nivel == "minor":
        nueva = f"{mayor}.{menor + 1}.0"
    elif a.nivel == "patch":
        nueva = f"{mayor}.{menor}.{parche + 1}"
    else:
        nueva = a.nivel
        if not clave(nueva) or clave(nueva) <= actual:
            print(f"ERROR: «{nueva}» debe ser SemVer y mayor que {datos['version']}", file=sys.stderr)
            return 2

    hoy = a.fecha or datetime.date.today().isoformat()
    entradas = {s: getattr(a, s.lower()) or [] for s in SECCIONES}
    ruta = ruta_changelog(a.agente)
    texto = ruta.read_text(encoding="utf-8") if ruta.exists() else f"# Changelog: {a.agente}\n\n"
    secciones = secciones_changelog(texto)
    if any(v == nueva for v, _, _ in secciones):
        print(f"ERROR: la versión {nueva} ya está en el CHANGELOG", file=sys.stderr)
        return 2
    bloques = [f"### {s}\n\n" + "\n".join(f"- {i}" for i in items) for s, items in entradas.items() if items]
    pendiente = not bloques
    if pendiente:
        bloques = ["### Cambiado\n\n- [PENDIENTE: describir los cambios de esta versión]"]
    nueva_seccion = f"## [{nueva}] - {hoy}\n\n" + "\n\n".join(bloques) + "\n\n"
    primera = TITULO_VERSION.search(texto)
    texto = texto[:primera.start()] + nueva_seccion + texto[primera.start():] if primera else texto.rstrip() + "\n\n" + nueva_seccion

    ruta.write_text(texto.rstrip() + "\n", encoding="utf-8")
    datos["version"] = nueva
    manifiesto.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{a.agente}: {'.'.join(map(str, actual[:3]))} → {nueva}")
    print(f"Actualizados: {manifiesto.relative_to(RAIZ)} y {ruta.relative_to(RAIZ)}")
    if pendiente:
        print("Aviso: completa la entrada [PENDIENTE] del CHANGELOG antes de abrir el PR (verificar la rechaza).")
    return 0


# ---------- verificar ----------
def cmd_verificar(a):
    errores, avisos = [], []
    agentes = leer_agentes()
    if not agentes:
        errores.append("no hay agentes en agentes/*/agente.json")
    dueños = {}
    for nombre, (manifiesto, datos) in agentes.items():
        donde = str(manifiesto.relative_to(RAIZ))
        for campo in ("nombre", "version", "descripcion", "skills"):
            if not datos.get(campo):
                errores.append(f"{donde}: falta el campo «{campo}»")
        if datos.get("nombre") and datos["nombre"] != nombre:
            errores.append(f"{donde}: «nombre» ({datos['nombre']}) no coincide con la carpeta ({nombre})")
        version = datos.get("version", "")
        if version and not clave(version):
            errores.append(f"{donde}: la versión «{version}» no es SemVer (X.Y.Z)")
        for skill in datos.get("skills", []):
            if not (RAIZ / skill / "SKILL.md").is_file():
                errores.append(f"{donde}: «{skill}» no tiene SKILL.md")
            if skill in dueños:
                errores.append(f"{donde}: «{skill}» ya pertenece al agente {dueños[skill]}")
            dueños[skill] = nombre
        ruta = ruta_changelog(nombre)
        if not ruta.is_file():
            errores.append(f"{nombre}: falta agentes/{nombre}/CHANGELOG.md")
            continue
        secciones = secciones_changelog(ruta.read_text(encoding="utf-8"))
        if not secciones or secciones[0][0] != version:
            errores.append(f"{nombre}: la primera versión del CHANGELOG ({secciones[0][0] if secciones else 'ninguna'}) no es la del manifiesto ({version})")
        else:
            _, fecha, cuerpo = secciones[0]
            if not fecha:
                errores.append(f"{nombre}: la versión {version} del CHANGELOG no tiene fecha (## [{version}] - AAAA-MM-DD)")
            if not re.search(r"^- \S", cuerpo, re.M):
                errores.append(f"{nombre}: la versión {version} del CHANGELOG no tiene entradas")
            if "[PENDIENTE" in cuerpo:
                errores.append(f"{nombre}: la versión {version} del CHANGELOG tiene entradas [PENDIENTE]")
        vistas = [s[0] for s in secciones]
        if len(vistas) != len(set(vistas)):
            errores.append(f"{nombre}: hay versiones repetidas en el CHANGELOG")
        ordenadas = [clave(v) for v in vistas if clave(v)]
        if ordenadas != sorted(ordenadas, reverse=True):
            errores.append(f"{nombre}: las versiones del CHANGELOG no están de la más nueva a la más vieja")

    if a.base:
        codigo, salida = git("diff", "--name-only", f"{a.base}...HEAD")
        if codigo != 0:
            errores.append(f"no se pudo comparar con {a.base} (¿falta git fetch?)")
        else:
            cambiados = [l for l in salida.splitlines() if l]
            for nombre, (_, datos) in agentes.items():
                rutas = [s.rstrip("/") + "/" for s in datos.get("skills", [])]
                tocados = [c for c in cambiados if any(c.startswith(r) for r in rutas)]
                codigo, anterior = git("show", f"{a.base}:agentes/{nombre}/agente.json")
                if codigo != 0:
                    avisos.append(f"{nombre}: agente nuevo respecto de {a.base} (versión {datos.get('version')})")
                    continue
                version_base = json.loads(anterior).get("version", "")
                if clave(datos.get("version")) and clave(version_base) and clave(datos["version"]) < clave(version_base):
                    errores.append(f"{nombre}: la versión bajó ({version_base} → {datos['version']})")
                if tocados and datos.get("version") == version_base:
                    errores.append(
                        f"{nombre}: cambiaron {len(tocados)} archivo(s) de sus skills pero la versión sigue en {version_base}. "
                        f"Ejecuta: python3 scripts/versionado.py subir {nombre} <patch|minor|major> --cambiado \"...\""
                    )
                elif tocados:
                    avisos.append(f"{nombre}: {version_base} → {datos['version']} ({len(tocados)} archivo(s) de skills cambiados)")

    for av in avisos:
        print(f"AVISO: {av}")
    for e in errores:
        print(f"ERROR: {e}")
    print("Resultado:", "con errores" if errores else "sin errores")
    return 1 if errores else 0


# ---------- notas y pendientes ----------
def cmd_notas(a):
    agentes = leer_agentes()
    if a.agente not in agentes:
        print(f"ERROR: no existe el agente «{a.agente}»", file=sys.stderr)
        return 2
    version = a.version or agentes[a.agente][1]["version"]
    for v, fecha, cuerpo in secciones_changelog(ruta_changelog(a.agente).read_text(encoding="utf-8")):
        if v == version:
            print(cuerpo)
            return 0
    print(f"ERROR: la versión {version} no está en el CHANGELOG", file=sys.stderr)
    return 2


def cmd_pendientes(_):
    _, etiquetas = git("tag", "-l")
    existentes = set(etiquetas.split())
    for nombre, (_, datos) in leer_agentes().items():
        etiqueta = f"{nombre}/v{datos['version']}"
        if etiqueta not in existentes:
            print(f"{nombre} {datos['version']} {etiqueta}")
    return 0


def main():
    p = argparse.ArgumentParser(description="Versionado de los agentes (ver VERSIONADO.md).")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("listar", help="muestra cada agente con su versión")
    s = sub.add_parser("subir", help="sube la versión de un agente y agrega su entrada en el CHANGELOG")
    s.add_argument("agente")
    s.add_argument("nivel", help="major, minor, patch o una versión exacta (X.Y.Z)")
    for seccion in SECCIONES:
        s.add_argument(f"--{seccion.lower()}", action="append", metavar="TEXTO", help=f"entrada para «{seccion}» (repetible)")
    s.add_argument("--fecha", help="fecha AAAA-MM-DD (por defecto, hoy)")
    v = sub.add_parser("verificar", help="valida manifiestos y changelogs; con --base exige subir la versión si cambió un agente")
    v.add_argument("--base", help="rama o commit de comparación, por ejemplo origin/main")
    n = sub.add_parser("notas", help="imprime la entrada del CHANGELOG de una versión")
    n.add_argument("agente")
    n.add_argument("version", nargs="?")
    sub.add_parser("pendientes", help="lista las versiones que todavía no tienen etiqueta")
    a = p.parse_args()
    return {"listar": cmd_listar, "subir": cmd_subir, "verificar": cmd_verificar, "notas": cmd_notas, "pendientes": cmd_pendientes}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
