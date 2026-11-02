#!/usr/bin/env python3
"""Verifica documentación Markdown contra un prompt de estilo de documentacion-estilo.

Uso:
    python3 verificar_doc.py --prompt docs/prompt-estilo.md docs/manual/
    python3 verificar_doc.py --prompt docs/prompt-estilo.md docs/manual/01-intro.md docs/manual/02-uso.md

Revisa estructura, numeración de títulos, tablas, figuras, avisos, siglas,
números y largo de oraciones. Termina con código 1 si encuentra errores.
Solo usa la biblioteca estándar.
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

SIN_NUMERAR_BASE = {
    "control de versiones", "portada", "resumen", "abstract", "agradecimientos",
    "dedicatoria", "indice", "indice general", "indice de figuras", "indice de tablas",
    "lista de siglas y abreviaturas", "siglas y abreviaturas", "glosario",
    "referencias", "bibliografia", "anexos", "apendices",
}
SIGLAS_BASE = {"URL", "PDF", "HTML", "CSS", "HTTP", "HTTPS", "JSON", "XML", "USB", "ID", "OK", "SI", "PNG", "SVG", "SQL"}
AVISOS = {"nota", "consejo", "advertencia", "peligro"}
ROMANOS = re.compile(r"^[IVXLC]+$")
CONTEXTO_NUMERO = re.compile(r"(secci[oó]n|apartado|cap[ií]tulo|versi[oó]n|figura|tabla|v)\s*$", re.I)


def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.strip().lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texto)


def leer_frontmatter(texto):
    """Lee un encabezado YAML simple (claves, valores y listas). Devuelve (datos, resto, líneas_saltadas)."""
    if not texto.startswith("---"):
        return {}, texto, 0
    lineas = texto.split("\n")
    fin = next((i for i in range(1, len(lineas)) if lineas[i].strip() == "---"), None)
    if fin is None:
        return {}, texto, 0
    datos, clave = {}, None
    for linea in lineas[1:fin]:
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        item = re.match(r"^\s+-\s+(.*)$", linea)
        if item and clave:
            if not isinstance(datos.get(clave), list):
                datos[clave] = []
            datos[clave].append(item.group(1).strip().strip("\"'"))
            continue
        par = re.match(r"^([\w\-]+):\s*(.*)$", linea)
        if par:
            clave, valor = par.group(1), par.group(2).strip().strip("\"'")
            datos[clave] = valor if valor else []
    return datos, "\n".join(lineas[fin + 1:]), fin + 1


class Informe:
    def __init__(self):
        self.errores, self.advertencias, self.info = [], [], []

    def error(self, donde, msg):
        self.errores.append(f"{donde}: {msg}")

    def aviso(self, donde, msg):
        self.advertencias.append(f"{donde}: {msg}")


def bloques(archivos):
    """Devuelve las líneas de todos los archivos con su ubicación, marcando las que están en código."""
    salida = []
    for ruta in archivos:
        texto = ruta.read_text(encoding="utf-8")
        _, cuerpo, saltadas = leer_frontmatter(texto)
        en_codigo, lenguaje = False, ""
        for n, linea in enumerate(cuerpo.split("\n"), start=saltadas + 1):
            valla = re.match(r"^\s*(```|~~~)\s*([\w\-]*)", linea)
            if valla:
                if not en_codigo:
                    en_codigo, lenguaje = True, valla.group(2).lower()
                    salida.append((f"{ruta}:{n}", linea, "inicio_codigo", lenguaje))
                else:
                    en_codigo = False
                    salida.append((f"{ruta}:{n}", linea, "fin_codigo", lenguaje))
                continue
            salida.append((f"{ruta}:{n}", linea, "codigo" if en_codigo else "texto", lenguaje if en_codigo else ""))
    return salida


def siguiente_no_vacia(lineas, i, paso):
    j = i + paso
    while 0 <= j < len(lineas) and not lineas[j][1].strip():
        j += paso
    return lineas[j] if 0 <= j < len(lineas) else None


def verificar(prompt, archivos, inf):
    lineas = bloques(archivos)
    documento = normalizar(prompt.get("documento", ""))
    sin_numerar = SIN_NUMERAR_BASE | {normalizar(s) for s in prompt.get("sin_numerar", []) or []}
    siglas_ok = SIGLAS_BASE | set(prompt.get("siglas_conocidas", []) or [])
    try:
        max_palabras = int(prompt.get("max_palabras_oracion", 25))
    except ValueError:
        max_palabras = 25
    decimal_coma = normalizar(str(prompt.get("decimal", "coma"))) == "coma"
    digital = normalizar(str(prompt.get("medio", "digital"))) in {"digital", "ambos"}

    # Títulos y numeración
    contadores, capitulos, en_numerado, primer_h1 = [0, 0, 0], [], False, True
    for donde, linea, tipo, _ in lineas:
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", linea) if tipo == "texto" else None
        if not m:
            continue
        nivel, titulo = len(m.group(1)), m.group(2)
        if nivel > 4:
            inf.error(donde, f"título de nivel {nivel}; el máximo es 4: «{titulo}»")
            continue
        if titulo.endswith(".") and not titulo.endswith("..."):
            inf.error(donde, f"el título termina en punto: «{titulo}»")
        num = re.match(r"^(\d+(?:\.\d+)*)\.?\s+(.+)$", titulo)
        nombre = (num.group(2) if num else titulo).rstrip(".")
        if nivel == 1 and primer_h1 and not num and documento and normalizar(nombre) == documento:
            primer_h1 = False
            continue  # título del documento
        primer_h1 = False
        if nivel == 1:
            capitulos.append((donde, normalizar(nombre)))
            if normalizar(nombre) in sin_numerar:
                en_numerado = False
                if num:
                    inf.aviso(donde, f"«{nombre}» suele ir sin número")
                continue
            en_numerado = True
        if nivel == 4:
            continue
        if not num:
            if en_numerado:
                inf.error(donde, f"título sin numeración decimal: «{titulo}»")
            continue
        partes = [int(p) for p in num.group(1).split(".")]
        if len(partes) != nivel:
            inf.error(donde, f"el número {num.group(1)} no corresponde a un título de nivel {nivel}")
            continue
        esperado = contadores[: nivel - 1] + [contadores[nivel - 1] + 1]
        if partes != esperado:
            inf.error(donde, f"numeración {num.group(1)}; se esperaba {'.'.join(map(str, esperado))}")
        contadores = partes + [0] * (3 - nivel)

    # Estructura exigida por el prompt
    estructura = [normalizar(s) for s in prompt.get("estructura", []) or []]
    presentes = [c for _, c in capitulos]
    faltan = [s for s in estructura if s not in presentes]
    for s in faltan:
        inf.error("estructura", f"falta el capítulo «{s}» exigido por el prompt")
    orden = [c for c in presentes if c in estructura]
    if not faltan and orden != [s for s in estructura if s in orden]:
        inf.aviso("estructura", "los capítulos no siguen el orden del prompt")

    # Tablas, figuras y avisos
    texto_plano = "\n".join(l for _, l, t, _ in lineas if t == "texto")
    numeros = {"Tabla": [], "Figura": []}
    for i, (donde, linea, tipo, lenguaje) in enumerate(lineas):
        if tipo == "texto" and linea.lstrip().startswith("|"):
            sig = lineas[i + 1][1] if i + 1 < len(lineas) else ""
            prev_es_tabla = i > 0 and lineas[i - 1][1].lstrip().startswith("|")
            if not prev_es_tabla and re.match(r"^\s*\|?\s*:?-{3,}", sig):
                ant = siguiente_no_vacia(lineas, i, -1)
                m = re.match(r"^\*{0,2}Tabla (\d+)\.", ant[1].strip()) if ant else None
                if m:
                    numeros["Tabla"].append((donde, int(m.group(1))))
                else:
                    inf.error(donde, "tabla sin la línea «**Tabla N.** Título» antes")
        es_imagen = tipo == "texto" and re.search(r"!\[(.*?)\]\(", linea)
        es_mermaid = tipo == "fin_codigo" and lenguaje == "mermaid"
        if es_imagen and not es_imagen.group(1).strip():
            (inf.error if digital else inf.aviso)(donde, "imagen sin texto alternativo")
        if es_imagen or es_mermaid:
            sig = siguiente_no_vacia(lineas, i, 1)
            m = re.match(r"^\*{0,2}Figura (\d+)\.", sig[1].strip()) if sig else None
            if m:
                numeros["Figura"].append((donde, int(m.group(1))))
            else:
                inf.error(donde, "figura sin la línea «**Figura N.** Título» después")
        aviso = re.match(r"^>\s*\*\*([^*]+?)[.:]\*\*", linea) if tipo == "texto" else None
        if aviso and normalizar(aviso.group(1)) not in AVISOS:
            inf.aviso(donde, f"aviso «{aviso.group(1)}» fuera de los tipos Nota, Consejo, Advertencia, Peligro")
        elif tipo == "texto" and re.match(r"^>\s*(Nota|Consejo|Advertencia|Peligro|Importante)\s*:", linea, re.I):
            inf.aviso(donde, "el aviso debe escribirse como «> **Nota.** texto»")

    for clase, lista in numeros.items():
        for k, (donde, n) in enumerate(lista, start=1):
            if n != k:
                inf.error(donde, f"{clase} {n}: la numeración no es continua; se esperaba {clase} {k}")
            menciones = re.findall(rf"(?<!\*\*){clase} {n}(?![\d.]*\*\*)(?!\d)", texto_plano, re.I)
            if not menciones:
                inf.aviso(donde, f"{clase} {n} no se menciona en el texto")

    # Siglas, números, pendientes y oraciones
    vistas = set()
    parrafo, inicio = [], None
    oraciones_largas = []

    def cerrar_parrafo():
        if not parrafo:
            return
        texto = " ".join(parrafo)
        texto = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", texto)
        texto = re.sub(r"`[^`]*`", "X", texto)
        for oracion in re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡])", texto):
            palabras = len(re.findall(r"\w+", oracion))
            if palabras > max_palabras:
                oraciones_largas.append((inicio, palabras))
        parrafo.clear()

    capitulo_actual = ""
    for donde, linea, tipo, _ in lineas:
        es_prosa = tipo == "texto" and linea.strip() and not re.match(r"^\s*(#|\||!\[|<!--)", linea)
        if not es_prosa:
            cerrar_parrafo()
            inicio = None
        if tipo == "texto" and re.match(r"^#\s", linea):
            capitulo_actual = normalizar(re.sub(r"^#\s+(\d+\.?\s+)?", "", linea).rstrip("."))
        if tipo != "texto" or re.match(r"^#", linea):
            continue
        sin_codigo = re.sub(r"`[^`]*`", "", linea)
        sin_codigo = re.sub(r"\]\([^)]*\)", "]", sin_codigo)
        for m in re.finditer(r"(?<![\w-])([A-ZÁÉÍÓÚÑ]{2,6})s?(?![\w-])", sin_codigo):
            sigla = m.group(1)
            if sigla in vistas or sigla in siglas_ok or ROMANOS.match(sigla):
                continue
            vistas.add(sigla)
            antes, despues = sin_codigo[: m.start()], sin_codigo[m.end():]
            if not (antes.endswith("(") or despues.lstrip().startswith("(")):
                inf.aviso(donde, f"la sigla {sigla} no se desarrolla en su primera aparición")
        if decimal_coma and capitulo_actual != "control de versiones":
            for m in re.finditer(r"(?<![\w.,])(\d+)\.(\d+)(?![\w.])", sin_codigo):
                if not CONTEXTO_NUMERO.search(sin_codigo[: m.start()]):
                    inf.aviso(donde, f"«{m.group(0)}»: usa coma decimal o espacio para miles")
        for m in re.finditer(r"\d%", sin_codigo):
            inf.aviso(donde, "falta un espacio antes de «%»")
        if "[PENDIENTE" in linea.upper():
            inf.info.append(f"{donde}: {linea.strip()}")
        if es_prosa:
            if inicio is None:
                inicio = donde
            parrafo.append(re.sub(r"^\s*(?:[-*+]|\d+\.|>)\s*", "", linea.strip()))
            if re.match(r"^\s*(?:[-*+]|\d+\.)\s", linea):
                cerrar_parrafo()
                inicio = None
    cerrar_parrafo()
    for donde, palabras in oraciones_largas:
        inf.aviso(donde, f"oración de {palabras} palabras (máximo {max_palabras})")


def main():
    p = argparse.ArgumentParser(description="Verifica documentación Markdown contra un prompt de estilo.")
    p.add_argument("--prompt", required=True, help="ruta al prompt-estilo.md")
    p.add_argument("rutas", nargs="+", help="archivos .md o carpetas con el documento")
    a = p.parse_args()

    prompt_ruta = Path(a.prompt)
    if not prompt_ruta.is_file():
        print(f"ERROR: no existe el prompt {prompt_ruta}", file=sys.stderr)
        return 2
    prompt, _, _ = leer_frontmatter(prompt_ruta.read_text(encoding="utf-8"))
    faltan = [k for k in ("documento", "tipo", "metodologia", "medio", "tratamiento", "salida", "estructura") if not prompt.get(k)]
    if faltan:
        print(f"ERROR: al prompt le faltan los campos: {', '.join(faltan)}", file=sys.stderr)
        return 2

    archivos = []
    for r in map(Path, a.rutas):
        if r.is_dir():
            archivos += sorted(f for f in r.rglob("*.md") if f.resolve() != prompt_ruta.resolve())
        elif r.is_file():
            archivos.append(r)
        else:
            print(f"ERROR: no existe {r}", file=sys.stderr)
            return 2
    if not archivos:
        print("ERROR: no se encontraron archivos .md", file=sys.stderr)
        return 2

    inf = Informe()
    verificar(prompt, archivos, inf)
    print(f"Documento: {prompt.get('documento')} | archivos: {len(archivos)}")
    for titulo, lista in (("ERRORES", inf.errores), ("ADVERTENCIAS", inf.advertencias), ("PENDIENTES", inf.info)):
        print(f"\n{titulo} ({len(lista)})")
        for item in lista:
            print(f"  - {item}")
    print("\nResultado:", "con errores" if inf.errores else "sin errores")
    return 1 if inf.errores else 0


if __name__ == "__main__":
    sys.exit(main())
