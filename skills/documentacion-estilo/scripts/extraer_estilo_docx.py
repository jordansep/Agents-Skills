#!/usr/bin/env python3
"""Extrae el diseño de un .docx de referencia para definir una plantilla.

Uso:
    python3 extraer_estilo_docx.py documento.docx [--json]

Informa página y márgenes, fuentes del tema, estilos de título, tamaños más usados,
alineación, interlineado, rellenos y bordes de tablas, formato de leyendas
(«Tabla N», «Figura N», «Nota.»), encabezado y pie. No decide nada: el informe es
la evidencia para escribir la plantilla en references/plantillas/ y para hacer al
usuario las preguntas sobre lo que el documento no resuelve o resuelve de forma
inconsistente.

Requiere python-docx (pip install python-docx).
"""
import argparse
import collections
import json
import re
import sys
import zipfile

try:
    import docx
except ImportError:
    sys.exit("Falta python-docx: pip install python-docx")

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def color(run_or_font):
    f = getattr(run_or_font, "font", run_or_font)
    try:
        return str(f.color.rgb) if f.color is not None and f.color.type is not None else None
    except Exception:
        return None


def pt(x):
    return round(x.pt, 1) if x is not None else None


def tema(path):
    with zipfile.ZipFile(path) as z:
        nombres = [n for n in z.namelist() if n.startswith("word/theme/")]
        if not nombres:
            return {}
        t = z.read(nombres[0]).decode("utf8", "ignore")
    fuentes = dict(re.findall(r'<a:(major|minor)Font><a:latin typeface="([^"]*)"', t))
    colores = dict(re.findall(r'<a:(dk1|lt1|dk2|lt2|accent\d)>.*?(?:val|lastClr)="([0-9A-Fa-f]{6})"', t))
    return {"fuente_titulos": fuentes.get("major"), "fuente_cuerpo": fuentes.get("minor"), "colores": colores}


def estilo_titulos(d):
    out = {}
    for st in d.styles:
        if st.type != 1 or not re.match(r"(?i)^(heading \d|title|subtitle|caption|normal)$", st.name):
            continue
        f, pf = st.font, st.paragraph_format
        out[st.name] = {
            "fuente": f.name, "tamano_pt": pt(f.size), "negrita": f.bold, "cursiva": f.italic, "color": color(f),
            "alineacion": str(pf.alignment) if pf.alignment is not None else None,
            "espacio_antes_pt": pt(pf.space_before), "espacio_despues_pt": pt(pf.space_after),
            "interlineado": pf.line_spacing if isinstance(pf.line_spacing, float) else pt(pf.line_spacing),
        }
    return out


def leyendas(d):
    P = d.paragraphs
    res = collections.defaultdict(collections.Counter)
    for i, p in enumerate(P):
        t = p.text.strip()
        m = re.match(r"^(Tabla|Figura)\s+\d+\.?\s*(.*)$", t)
        if m:
            r0 = p.runs[0] if p.runs else None
            mismo = bool(m.group(2))
            sig = P[i + 1] if i + 1 < len(P) else None
            tit = sig.runs[0] if sig is not None and sig.runs else None
            res[m.group(1)][(
                "titulo en la misma línea" if mismo else "titulo en la línea siguiente",
                "número en negrita" if r0 is not None and r0.bold else "número sin negrita",
                "título en cursiva" if (not mismo and tit is not None and tit.italic) else "título sin cursiva",
            )] += 1
        if t.startswith("Nota.") or t.startswith("Fuente:"):
            r0 = p.runs[0] if p.runs else None
            res[t.split()[0]][(
                "cursiva" if r0 is not None and r0.italic else "sin cursiva",
                f"{pt(r0.font.size) if r0 is not None else None} pt",
                f"color {color(r0) if r0 is not None else None}",
            )] += 1
    # ¿La leyenda de tabla va antes de la tabla? Se mira el orden en el cuerpo.
    orden = collections.Counter()
    ultimo = None
    for el in d.element.body.iterchildren():
        if el.tag == W + "p":
            txt = "".join(x.text or "" for x in el.iter(W + "t")).strip()
            if re.match(r"^Tabla\s+\d+", txt):
                ultimo = "leyenda"
            elif txt:
                ultimo = "texto" if ultimo != "leyenda" else ultimo
        elif el.tag == W + "tbl":
            orden["leyenda antes de la tabla" if ultimo == "leyenda" else "tabla sin leyenda inmediata antes"] += 1
            ultimo = None
    return {k: [[list(a), n] for a, n in v.most_common(4)] for k, v in res.items()}, dict(orden)


def tablas(d):
    rellenos, bordes, tam, encabezado_negrita = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    for t in d.tables:
        x = t._tbl.xml
        rellenos.update(c.lower() for c in re.findall(r'w:fill="([0-9A-Fa-f]{6})"', x))
        for m in re.finditer(r"<w:(top|bottom|left|right|insideH|insideV) ([^>]*)/?>", x):
            at = dict(re.findall(r'w:(\w+)="([^"]*)"', m.group(2)))
            if "val" in at:
                sz = f"{int(at['sz']) / 8:g} pt" if at.get("sz", "").isdigit() else None
                bordes[(m.group(1), at["val"], sz, at.get("color"))] += 1
        if t.rows:
            for c in t.rows[0].cells:
                for p in c.paragraphs:
                    for r in p.runs:
                        encabezado_negrita[bool(r.bold)] += 1
        for row in t.rows[1:4]:
            for c in row.cells:
                for p in c.paragraphs:
                    for r in p.runs:
                        if r.font.size:
                            tam[pt(r.font.size)] += 1
    return {
        "cantidad": len(d.tables),
        "rellenos": rellenos.most_common(8),
        "bordes": [[list(k), n] for k, n in bordes.most_common(6)],
        "tamano_celdas_pt": tam.most_common(4),
        "encabezado_en_negrita": dict(encabezado_negrita),
    }


def encabezado_pie(d):
    out = []
    for i, s in enumerate(d.sections):
        for nombre, parte in (("encabezado", s.header), ("pie", s.footer)):
            try:
                x = parte._element.xml
            except Exception:
                continue
            campos = sorted(set(re.findall(r"\b(PAGE|NUMPAGES|SECTIONPAGES)\b", x)))
            texto = " ".join(p.text for p in parte.paragraphs).strip()
            al = [str(p.alignment) for p in parte.paragraphs if p.alignment is not None]
            if campos or texto:
                out.append({"seccion": i + 1, "parte": nombre, "texto": texto[:80], "campos": campos, "alineacion": al[:1]})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("docx")
    ap.add_argument("--json", action="store_true", help="salida en JSON")
    a = ap.parse_args()
    d = docx.Document(a.docx)
    s = d.sections[0]
    tam, alin, inter, fuentes_run = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    for p in d.paragraphs:
        if not p.text.strip():
            continue
        alin[str(p.alignment) if p.alignment is not None else "heredada"] += 1
        ls = p.paragraph_format.line_spacing
        inter[ls if isinstance(ls, float) or ls is None else f"{pt(ls)} pt"] += 1
        if p.style is not None and p.style.name.lower().startswith("heading"):
            continue
        for r in p.runs:
            if r.font.size:
                tam[pt(r.font.size)] += len(r.text)
            if r.font.name:
                fuentes_run[r.font.name] += len(r.text)
    with zipfile.ZipFile(a.docx) as z:
        estilos = z.read("word/styles.xml").decode("utf8", "ignore")
    defecto = re.search(r"<w:rPrDefault>.*?</w:rPrDefault>", estilos, re.S)
    fuente_defecto = re.search(r'w:ascii="([^"]+)"', defecto.group(0)) if defecto else None
    ley, orden = leyendas(d)
    info = {
        "pagina": {"ancho_cm": round(s.page_width.cm, 2), "alto_cm": round(s.page_height.cm, 2),
                   "margenes_cm": {k: round(getattr(s, k + "_margin").cm, 2) for k in ("top", "bottom", "left", "right")}},
        "tema": tema(a.docx),
        "fuente_por_defecto": fuente_defecto.group(1) if fuente_defecto else None,
        "fuentes_en_texto": fuentes_run.most_common(5),
        "estilos": estilo_titulos(d),
        "cuerpo_tamanos_pt_por_caracteres": tam.most_common(6),
        "alineacion_parrafos": alin.most_common(),
        "interlineado": [[str(k), n] for k, n in inter.most_common(5)],
        "leyendas": ley,
        "posicion_leyenda_tabla": orden,
        "tablas": tablas(d),
        "imagenes": len(d.inline_shapes),
        "encabezado_pie": encabezado_pie(d),
    }
    if a.json:
        print(json.dumps(info, ensure_ascii=False, indent=2, default=str))
        return
    for k, v in info.items():
        print(f"## {k}")
        print(json.dumps(v, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
