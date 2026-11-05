#!/usr/bin/env python3
"""Extrae las imágenes de un .docx, un PDF o una carpeta, con un inventario JSON (DEC-013).

Uso:
    python3 extraer_imagenes.py documento.docx --salida DIR [--lado-minimo 32]

Deja en DIR las imágenes y `inventario.json`, con estas listas:
- `imagenes`: lo que el agente lee con Read, con su contexto y su cantidad de referencias.
- `descartadas`: imágenes mínimas (DEC-014) y copias de otra ya extraída, con el motivo.
- `no_extraidas`: formas de Word, formatos sin lectura visual (EMF, WMF...) y referencias
  externas o rotas, con el motivo.
- `avisos`: lo que el agente debe contarle al usuario (por ejemplo, un PDF sin PyMuPDF).

Una carpeta también puede traer imágenes sueltas: se tratan igual, con `origen: "archivo"`.

El procedimiento completo está en references/imagenes.md. Si la entrada no sirve, el script
no escribe nada y sale con 2. Solo usa la biblioteca estándar; PyMuPDF es opcional y hace
falta solo para leer PDF (pip install pymupdf).
"""
import argparse
import hashlib
import json
import posixpath
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile
import zlib
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

LADO_MINIMO = 32  # DEC-014: una imagen es mínima si su lado menor mide menos de 32 px.
MIN_TRAZOS = 10  # Página vectorial de PDF: por debajo, son adornos; un falso positivo solo cuesta una lectura.
PPP_PAGINA = 150
EXTENSIONES_IMAGEN = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tif", ".tiff", ".emf", ".wmf", ".svg"}
OTROS_DOCUMENTOS = {".doc", ".docm", ".dotx", ".odt", ".rtf", ".pptx"}

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
V = "{urn:schemas-microsoft-com:vml}"
PIC = "{http://schemas.openxmlformats.org/drawingml/2006/picture}"
SVG_BLIP = "{http://schemas.microsoft.com/office/drawing/2016/SVG/main}svgBlip"
FALLBACK = "{http://schemas.openxmlformats.org/markup-compatibility/2006}Fallback"
RELS = "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"

# Lo que Word dibuja sin un archivo de imagen detrás.
FORMAS = {
    "{http://schemas.microsoft.com/office/word/2010/wordprocessingShape}wsp": ("forma de Word (wps:wsp)", "se dibuja en el documento: no es un archivo de imagen"),
    "{http://schemas.openxmlformats.org/drawingml/2006/chart}chart": ("gráfico nativo de Word", "se dibuja en el documento: no es un archivo de imagen"),
    "{http://schemas.microsoft.com/office/drawing/2014/chartex}chart": ("gráfico moderno de Word (cx:chart)", "se dibuja en el documento: no es un archivo de imagen"),
    "{http://schemas.openxmlformats.org/drawingml/2006/diagram}relIds": ("SmartArt", "se dibuja en el documento: no es un archivo de imagen"),
}
PARTES = re.compile(r"^word/(document\d*|header\d*|footer\d*|footnotes|endnotes|comments)\.xml$")
ESTILOS_LEYENDA = {"caption", "descripcion", "descripción", "descripcin", "epigrafe", "epígrafe", "leyenda"}
TEXTO_LEYENDA = re.compile(r"^(figura|imagen|ilustraci[oó]n|gr[aá]fico|diagrama|esquema|cuadro|tabla|figure)\s+\d", re.I)


class EntradaInvalida(Exception):
    """La entrada no se puede procesar: el script avisa y sale con 2, sin traza."""


def medir(datos):
    """(formato, ancho, alto) según los bytes, nunca según el nombre. Sin lectura visual, formato None."""
    if datos.startswith(b"\x89PNG\r\n\x1a\n"):
        return ("png", *struct.unpack(">II", datos[16:24])) if len(datos) >= 24 else ("png", None, None)
    if datos.startswith((b"GIF87a", b"GIF89a")):
        return ("gif", *struct.unpack("<HH", datos[6:10])) if len(datos) >= 10 else ("gif", None, None)
    if datos.startswith(b"\xff\xd8"):
        return ("jpg", *medir_jpeg(datos))
    if datos[:4] == b"RIFF" and datos[8:12] == b"WEBP":
        return ("webp", *medir_webp(datos))
    return (None, None, None)


def medir_jpeg(datos):
    i = 2
    while i + 9 <= len(datos):
        if datos[i] != 0xFF:
            i += 1
            continue
        marca = datos[i + 1]
        if 0xC0 <= marca <= 0xCF and marca not in (0xC4, 0xC8, 0xCC):
            alto, ancho = struct.unpack(">HH", datos[i + 5:i + 9])
            return ancho, alto
        if marca in (0xFF, 0x00, 0x01) or 0xD0 <= marca <= 0xD9:
            i += 1 if marca == 0xFF else 2
            continue
        i += 2 + struct.unpack(">H", datos[i + 2:i + 4])[0]
    return None, None


def medir_webp(datos):
    bloque = datos[12:16]
    if bloque == b"VP8 " and len(datos) >= 30:
        return (struct.unpack("<H", datos[26:28])[0] & 0x3FFF, struct.unpack("<H", datos[28:30])[0] & 0x3FFF)
    if bloque == b"VP8L" and len(datos) >= 25:
        bits = struct.unpack("<I", datos[21:25])[0]
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if bloque == b"VP8X" and len(datos) >= 30:
        return int.from_bytes(datos[24:27], "little") + 1, int.from_bytes(datos[27:30], "little") + 1
    return None, None


def nombre_seguro(nombre):
    """Parte final de un nombre ajeno, sin barras ni puntos iniciales: nunca sale de la carpeta de destino."""
    base = PurePosixPath(nombre.replace("\\", "/")).name
    limpio = re.sub(r"[^\w.-]", "_", base).lstrip(".")[:80]
    return limpio or "imagen"


def contexto_vacio():
    return {"leyenda": None, "texto_alternativo": None, "parrafo_anterior": None, "parrafo_siguiente": None}


class Inventario:
    def __init__(self, entrada, lado_minimo):
        self.entrada, self.lado_minimo = str(entrada), lado_minimo
        self.imagenes, self.descartadas, self.no_extraidas, self.avisos = [], [], [], []
        self._por_hash, self._contenidos = {}, {}

    def avisar(self, texto):
        self.avisos.append(texto)
        print(f"AVISO: {texto}", file=sys.stderr)

    def no_extraer(self, documento, ubicacion, tipo, motivo, contextos=(), **extra):
        contextos = list(contextos)
        primero = contextos[0] if contextos else contexto_vacio()
        self.no_extraidas.append({
            "documento": documento, "ubicacion": ubicacion, "tipo": tipo, "motivo": motivo,
            "referencias": len(contextos), **extra,
            "leyenda": primero["leyenda"], "texto_alternativo": primero["texto_alternativo"],
            "parrafo_anterior": primero["parrafo_anterior"], "parrafo_siguiente": primero["parrafo_siguiente"],
            "otras_referencias": [{"documento": documento, "ubicacion": ubicacion, **c} for c in contextos[1:]],
        })

    def agregar(self, datos, documento, ubicacion, nombre, contextos, origen="incrustada"):
        formato, ancho, alto = medir(datos)
        if formato is None:
            extension = PurePosixPath(nombre).suffix.lstrip(".").upper() or "desconocido"
            self.no_extraer(documento, ubicacion, "imagen", f"formato {extension} sin lectura visual", contextos)
            return
        if ancho is None or alto is None:
            self.avisar(f"{documento}: no se pudo medir {ubicacion}; se conserva sin aplicar el umbral")
        sha = hashlib.sha256(datos).hexdigest()
        base = {"documento": documento, "ubicacion": ubicacion, "formato": formato, "ancho_px": ancho, "alto_px": alto,
                "sha256": sha, "referencias": len(contextos)}
        if origen != "pagina_vectorial" and ancho is not None and alto is not None and min(ancho, alto) < self.lado_minimo:
            motivo = f"imagen mínima: {ancho}x{alto} px, lado menor bajo el umbral de {self.lado_minimo} px"
            self.descartadas.append({**base, "motivo": motivo})
            return
        if sha in self._por_hash:
            original = self._por_hash[sha]
            original["referencias"] += len(contextos)
            original["otras_referencias"] += [{"documento": documento, "ubicacion": ubicacion, **c} for c in contextos]
            self.descartadas.append({**base, "motivo": f"repetida: mismo SHA-256 que {original['id']}", "igual_a": original["id"]})
            return
        identificador = f"img-{len(self.imagenes) + 1:03d}"
        archivo = f"{identificador}-{Path(nombre_seguro(nombre)).stem}.{formato}"
        primero, *resto = contextos or [contexto_vacio()]
        entrada = {"id": identificador, "archivo": archivo, "origen": origen, **base, **primero,
                   "otras_referencias": [{"documento": documento, "ubicacion": ubicacion, **c} for c in resto]}
        self.imagenes.append(entrada)
        self._por_hash[sha] = entrada
        self._contenidos[archivo] = datos

    def escribir(self, salida):
        """Se escribe al final: una entrada inválida no deja una salida a medias."""
        salida.mkdir(parents=True, exist_ok=True)
        for archivo, datos in self._contenidos.items():
            (salida / archivo).write_bytes(datos)
        resultado = {"entrada": self.entrada, "lado_minimo_px": self.lado_minimo, "imagenes": self.imagenes,
                     "descartadas": self.descartadas, "no_extraidas": self.no_extraidas, "avisos": self.avisos}
        ruta = salida / "inventario.json"
        ruta.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return ruta


# ---------- Word ----------
def recorrer(raiz):
    """Elementos en orden del documento, con su párrafo, su dibujo y si están en un cuadro de texto.
    mc:Fallback repite a mc:Choice y se saltea: sus imágenes no cuentan como referencias, para no contar dos
    veces lo que Word muestra una vez. Dentro de un cuadro de texto, el párrafo sigue siendo el exterior."""
    pila = [(raiz, None, None, False)]
    while pila:
        el, parrafo, dibujo, en_cuadro = pila.pop()
        if el.tag == FALLBACK:
            continue
        en_cuadro = en_cuadro or el.tag == W + "txbxContent"
        if el.tag == W + "p" and not en_cuadro:
            parrafo = el
        if el.tag in (WP + "inline", WP + "anchor", V + "shape"):
            dibujo = el
        yield el, parrafo, dibujo, en_cuadro
        pila.extend((h, parrafo, dibujo, en_cuadro) for h in reversed(list(el)))


def texto_de(el):
    return "".join(t.text or "" for t in el.iter(W + "t")).strip()


def texto_alternativo(dibujo):
    if dibujo is None:
        return None
    candidatos = [dibujo.get("alt")]
    for marco in [dibujo.find(WP + "docPr"), *dibujo.iter(PIC + "cNvPr")]:
        if marco is not None:
            candidatos += [marco.get("descr"), marco.get("title")]
    return next((c.strip() for c in candidatos if c and c.strip()), None)


class ParteWord:
    """Una parte del documento (cuerpo, encabezado...), con sus párrafos en orden."""

    def __init__(self, nombre, raiz, estilos):
        self.nombre, self.estilos = nombre, estilos
        self.textos, self.estilo_de, self.indice = [], [], {}
        self.imagenes, self.formas = [], []  # (id de relación, párrafo, dibujo) y (tipo, motivo, elemento, párrafo)
        self.svg = []  # (id de relación del SVG, id de relación de la imagen que lo acompaña)
        textos = {}
        for el, parrafo, dibujo, en_cuadro in recorrer(raiz):
            if el.tag == W + "p" and not en_cuadro:
                self.indice[id(el)] = len(self.textos)
                self.textos.append("")
                estilo = el.find(f"{W}pPr/{W}pStyle")
                self.estilo_de.append(estilo.get(W + "val") if estilo is not None else None)
                textos[id(el)] = []
            elif el.tag == W + "t" and parrafo is not None and not en_cuadro:
                textos[id(parrafo)].append(el.text or "")
            elif el.tag == A + "blip":
                rid = el.get(R + "embed") or el.get(R + "link")
                self.imagenes.append((rid, parrafo, dibujo))
                self.svg += [(svg.get(R + "embed"), rid) for svg in el.iter(SVG_BLIP)]
            elif el.tag == V + "imagedata":
                self.imagenes.append((el.get(R + "id"), parrafo, dibujo))
            elif el.tag in FORMAS:
                self.formas.append((*FORMAS[el.tag], el, parrafo))
            elif el.tag == W + "pict" and el.find(f".//{V}imagedata") is None:
                self.formas.append(("forma VML de Word (w:pict)", "se dibuja en el documento: no es un archivo de imagen", el, parrafo))
        for clave, i in self.indice.items():
            self.textos[i] = "".join(textos[clave]).strip()

    def es_leyenda(self, i):
        estilo = (self.estilo_de[i] or "").lower()
        return bool(self.textos[i]) and (estilo in self.estilos or estilo in ESTILOS_LEYENDA or bool(TEXTO_LEYENDA.match(self.textos[i])))

    def vecino(self, i, paso):
        """Índice del párrafo con texto más cercano: una imagen suele estar rodeada de párrafos vacíos."""
        i += paso
        while 0 <= i < len(self.textos):
            if self.textos[i]:
                return i
            i += paso
        return None

    def contexto(self, parrafo, dibujo):
        if parrafo is None:
            return {**contexto_vacio(), "texto_alternativo": texto_alternativo(dibujo)}
        i = self.indice[id(parrafo)]
        anterior, siguiente = self.vecino(i, -1), self.vecino(i, 1)
        # Word pone la leyenda de una figura debajo; se prueba también arriba. Los vecinos quedan para confirmarla.
        leyenda = next((self.textos[j] for j in (i, siguiente, anterior) if j is not None and self.es_leyenda(j)), None)
        return {
            "leyenda": leyenda,
            "texto_alternativo": texto_alternativo(dibujo),
            "parrafo_anterior": self.textos[anterior] if anterior is not None else None,
            "parrafo_siguiente": self.textos[siguiente] if siguiente is not None else None,
        }


def relaciones(z, parte, nombres):
    """{id: (ruta dentro del zip o None, destino externo o None)}. Una ruta que sale del zip queda en None."""
    carpeta, archivo = posixpath.split(parte)
    ruta = f"{carpeta}/_rels/{archivo}.rels"
    if ruta not in nombres:
        return {}
    res = {}
    for rel in ET.fromstring(z.read(ruta)).iter(RELS):
        destino = rel.get("Target", "")
        if rel.get("TargetMode") == "External":
            res[rel.get("Id")] = (None, destino)
            continue
        normal = destino.lstrip("/") if destino.startswith("/") else posixpath.normpath(posixpath.join(carpeta, destino))
        if normal not in nombres:
            normal = unquote(normal)
        res[rel.get("Id")] = (normal if normal in nombres else None, None)
    return res


def estilos_leyenda(z, nombres):
    if "word/styles.xml" not in nombres:
        return set()
    res = set()
    for estilo in ET.fromstring(z.read("word/styles.xml")).iter(W + "style"):
        nombre = estilo.find(W + "name")
        if nombre is not None and estilo.get(W + "styleId") and (nombre.get(W + "val") or "").lower() in ESTILOS_LEYENDA:
            res.add(estilo.get(W + "styleId").lower())
    return res


def leer_docx(ruta, documento, inv):
    try:
        with zipfile.ZipFile(ruta) as z:
            nombres = set(z.namelist())
            partes = sorted((n for n in nombres if PARTES.match(n)), key=lambda n: (not n.startswith("word/document"), n))
            if not any(n.startswith("word/document") for n in partes):
                raise EntradaInvalida(f"{documento}: no es un .docx válido (falta word/document.xml)")
            estilos = estilos_leyenda(z, nombres)
            contextos, svg_de = {}, {}  # ruta en el zip -> contextos, en orden de aparición; SVG -> su imagen
            estricto = False
            for nombre in partes:
                rels = relaciones(z, nombre, nombres)
                raiz = ET.fromstring(z.read(nombre))
                estricto = estricto or raiz.tag.startswith("{http://purl.oclc.org/")
                parte = ParteWord(nombre, raiz, estilos)
                for rid_svg, rid in parte.svg:
                    if rels.get(rid_svg, (None,))[0] and rels.get(rid, (None,))[0]:
                        svg_de[rels[rid_svg][0]] = rels[rid][0]
                for rid, parrafo, dibujo in parte.imagenes:
                    contexto = {"parte": nombre, **parte.contexto(parrafo, dibujo)}
                    interna, externa = rels.get(rid, (None, None))
                    if rid is None:
                        inv.no_extraer(documento, nombre, "imagen", "sin relación: el elemento no indica qué archivo muestra", [contexto])
                    elif interna:
                        contextos.setdefault(interna, []).append(contexto)
                    elif externa:
                        inv.no_extraer(documento, nombre, "imagen enlazada", "referencia externa: la imagen no está dentro del documento", [contexto], destino=externa)
                    else:
                        inv.no_extraer(documento, nombre, "imagen", f"referencia rota: la relación {rid} no lleva a un archivo del documento", [contexto])
                for tipo, motivo, el, parrafo in parte.formas:
                    contexto = parte.contexto(parrafo, None)
                    inv.no_extraer(documento, nombre, tipo, motivo, [contexto], texto=texto_de(el) or None)
            if estricto:
                inv.avisar(f"{documento}: está en OOXML estricto y sus referencias no se reconocen; guardarlo como .docx común y volver a extraer")
            sin_referencia = sorted(n for n in nombres if n.startswith("word/media/") and not n.endswith("/") and n not in contextos)
            for interna in [*contextos, *(n for n in sin_referencia if n not in svg_de)]:
                inv.agregar(z.read(interna), documento, interna, interna, contextos.get(interna, []))
            # El SVG que Word guarda junto a su imagen no se lista si esa imagen se extrajo (o es copia de una extraída).
            extraidas = {i["ubicacion"] for i in inv.imagenes if i["documento"] == documento}
            extraidas |= {d["ubicacion"] for d in inv.descartadas if d["documento"] == documento and "igual_a" in d}
            for interna in sin_referencia:
                if interna in svg_de and svg_de[interna] not in extraidas:
                    inv.agregar(z.read(interna), documento, interna, interna, [])
    except EntradaInvalida:
        raise
    except (zipfile.BadZipFile, ET.ParseError, KeyError, EOFError, zlib.error, RuntimeError, NotImplementedError, ValueError, LookupError, struct.error) as e:
        raise EntradaInvalida(f"{documento}: el .docx está corrupto o protegido ({e})") from None


# ---------- PDF ----------
def cargar_pymupdf():
    for modulo in ("pymupdf", "fitz"):
        try:
            return __import__(modulo)
        except ImportError:
            continue
    return None


def es_pagina_vectorial(dibujos, min_trazos=MIN_TRAZOS):
    """Trazos con curvas o diagonales, y suficientes: las tablas simples solo tienen líneas rectas."""
    trazos, con_forma = 0, False
    for dibujo in dibujos:
        for item in dibujo["items"]:
            trazos += 1
            if item[0] == "c":
                con_forma = True
            elif item[0] == "l" and abs(item[1].x - item[2].x) > 1 and abs(item[1].y - item[2].y) > 1:
                con_forma = True
    return con_forma and trazos >= min_trazos


def contexto_pdf(pagina, rect, numero):
    bloques = sorted((b for b in pagina.get_text("blocks") if b[6] == 0), key=lambda b: b[1])
    anterior = next((b[4].strip() for b in reversed(bloques) if rect is not None and b[3] <= rect.y0 and b[4].strip()), None)
    siguiente = next((b[4].strip() for b in bloques if rect is not None and b[1] >= rect.y1 and b[4].strip()), None)
    leyenda = next((t for t in (siguiente, anterior) if t and TEXTO_LEYENDA.match(t)), None)
    return {"pagina": numero, "leyenda": leyenda, "texto_alternativo": None, "parrafo_anterior": anterior, "parrafo_siguiente": siguiente}


def imagen_pdf(pymupdf, doc, xref):
    """(bytes, extensión). JPEG 2000 y otros que no se leen a la vista se pasan a PNG, igual que una imagen
    con máscara: sin componerla, lo transparente queda con fondo negro."""
    base = doc.extract_image(xref) or {}
    datos, extension, mascara = base.get("image"), base.get("ext", ""), base.get("smask")
    if datos and medir(datos)[0] and not mascara:
        return datos, extension
    pix = pymupdf.Pixmap(doc, xref)
    if pix.n - pix.alpha > 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    if mascara:
        alfa = pymupdf.Pixmap(doc, mascara)
        if (alfa.width, alfa.height) != (pix.width, pix.height):
            alfa = pymupdf.Pixmap(alfa, pix.width, pix.height, None)
        pix = pymupdf.Pixmap(pix, alfa)
    return pix.tobytes("png"), "png"


def leer_pdf(ruta, documento, inv):
    pymupdf = cargar_pymupdf()
    if pymupdf is None:
        inv.avisar(f"{documento}: no se procesó porque falta PyMuPDF (pip install pymupdf)")
        return
    if hasattr(pymupdf, "TOOLS"):
        pymupdf.TOOLS.mupdf_display_errors(False)
    try:  # PyMuPDF no publica una jerarquía de errores estable: cualquier fallo al leer es un PDF inválido.
        with pymupdf.open(ruta) as doc:
            if doc.needs_pass:
                raise EntradaInvalida(f"{documento}: el PDF está protegido con contraseña")
            contextos, vectoriales, rectas = {}, [], []
            for numero, pagina in enumerate(doc, start=1):
                for xref in dict.fromkeys(info[0] for info in pagina.get_images(full=True)):
                    rects = pagina.get_image_rects(xref)
                    for rect in rects or [None]:
                        contextos.setdefault(xref, []).append(contexto_pdf(pagina, rect, numero))
                dibujos = pagina.get_drawings()
                if es_pagina_vectorial(dibujos):
                    vectoriales.append((numero, pagina.get_pixmap(dpi=PPP_PAGINA).tobytes("png")))
                elif sum(len(d["items"]) for d in dibujos) >= MIN_TRAZOS:
                    rectas.append(numero)
            if rectas:
                inv.avisar(f"{documento}: revisar las páginas {', '.join(map(str, rectas))}: tienen muchos trazos rectos y no se convirtieron (una tabla o un diagrama ortogonal)")
            for xref, lista in contextos.items():
                paginas = sorted({c["pagina"] for c in lista})
                ubicacion = f"página {paginas[0]}, objeto {xref}"
                try:
                    datos, extension = imagen_pdf(pymupdf, doc, xref)
                except Exception as e:
                    inv.no_extraer(documento, ubicacion, "imagen", f"no se pudo leer ni convertir a PNG ({e})", lista)
                    continue
                inv.agregar(datos, documento, ubicacion, f"p{paginas[0]}-x{xref}.{extension}", lista)
            for numero, datos in vectoriales:
                contexto = {**contexto_vacio(), "pagina": numero}
                inv.agregar(datos, documento, f"página {numero}", f"p{numero}-vectorial.png", [contexto], origen="pagina_vectorial")
    except EntradaInvalida:
        raise
    except Exception as e:
        raise EntradaInvalida(f"{documento}: el PDF está corrupto o no se puede leer ({e})") from None


# ---------- Entrada ----------
LECTORES = {".docx": leer_docx, ".pdf": leer_pdf}


def leer_imagen(ruta, documento, inv):
    inv.agregar(ruta.read_bytes(), documento, documento, ruta.name, [contexto_vacio()], origen="archivo")


def documentos(entrada, salida, inv):
    """[(ruta, nombre para el inventario)]. En una carpeta se saltean los bloqueos de Word (~$) y la propia salida."""
    if not entrada.exists():
        raise EntradaInvalida(f"no existe {entrada}")
    origen, destino = entrada.resolve(), salida.resolve()
    if destino == origen or (entrada.is_dir() and destino in origen.parents):
        raise EntradaInvalida(f"--salida no puede ser la entrada ni una carpeta que la contiene: {salida}")
    if entrada.is_file():
        if entrada.suffix.lower() not in LECTORES:
            raise EntradaInvalida(f"formato no admitido: {entrada.name} (se admiten .docx, .pdf o una carpeta)")
        return [(entrada, entrada.name)]
    lista, otros = [], 0
    for f in sorted(p for p in entrada.rglob("*") if p.is_file()):
        if destino in f.resolve().parents or f.name.startswith("~$"):
            continue
        if f.suffix.lower() in LECTORES or f.suffix.lower() in EXTENSIONES_IMAGEN:
            lista.append((f, f.relative_to(entrada).as_posix()))
        elif f.suffix.lower() in OTROS_DOCUMENTOS:
            otros += 1
    if not lista:
        raise EntradaInvalida(f"la carpeta {entrada} no tiene archivos .docx, .pdf ni imágenes ({otros} documentos de otro formato)")
    if otros:
        inv.avisar(f"se ignoraron {otros} documentos de otro formato ({', '.join(sorted(OTROS_DOCUMENTOS))}): guardarlos como .docx o PDF")
    return lista


def entero_positivo(texto):
    valor = int(texto)
    if valor < 1:
        raise ValueError
    return valor


def main():
    p = argparse.ArgumentParser(description="Extrae las imágenes de un .docx, un PDF o una carpeta, con un inventario JSON.")
    p.add_argument("entrada", help="archivo .docx o .pdf, o carpeta con esos archivos o con imágenes sueltas")
    p.add_argument("--salida", required=True, help="carpeta donde dejar las imágenes e inventario.json")
    p.add_argument("--lado-minimo", type=entero_positivo, default=LADO_MINIMO,
                   help=f"una imagen es mínima si su lado menor mide menos de estos px (por defecto {LADO_MINIMO}, DEC-014)")
    a = p.parse_args()
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8", errors="replace")

    entrada, salida = Path(a.entrada), Path(a.salida)
    inv = Inventario(entrada, a.lado_minimo)
    try:
        for ruta, documento in documentos(entrada, salida, inv):
            LECTORES.get(ruta.suffix.lower(), leer_imagen)(ruta, documento, inv)
        inventario = inv.escribir(salida)
    except EntradaInvalida as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"ERROR: no se pudo leer la entrada o escribir la salida: {e}", file=sys.stderr)
        return 2
    print(f"Imágenes: {len(inv.imagenes)} | descartadas: {len(inv.descartadas)} | no extraídas: {len(inv.no_extraidas)} | avisos: {len(inv.avisos)}")
    print(f"Inventario: {inventario}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
