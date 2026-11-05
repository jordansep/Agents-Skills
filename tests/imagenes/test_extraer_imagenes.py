"""Tests de skills/documentacion-estilo/scripts/extraer_imagenes.py.

Todos los archivos se generan acá: las imágenes de referencia nunca se versionan.
Ejecutar desde la raíz del repositorio:
    python -m unittest discover -s tests -v
"""
import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
import textwrap
import unittest
import zipfile
import zlib
from pathlib import Path
from types import SimpleNamespace as Punto

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "skills" / "documentacion-estilo" / "scripts" / "extraer_imagenes.py"
VERIFICADOR = RAIZ / "skills" / "documentacion-generar" / "scripts" / "verificar_doc.py"

spec = importlib.util.spec_from_file_location("extraer_imagenes", SCRIPT)
ei = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ei)

PYMUPDF = ei.cargar_pymupdf()

NS = (
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
    'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
    'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
    'xmlns:v="urn:schemas-microsoft-com:vml"'
)
TIPO_IMAGEN = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
RELS_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def png(ancho=64, alto=64, color=(10, 20, 30)):
    def bloque(tipo, datos):
        return struct.pack(">I", len(datos)) + tipo + datos + struct.pack(">I", zlib.crc32(tipo + datos))
    filas = (b"\x00" + bytes(color) * ancho) * alto
    return (b"\x89PNG\r\n\x1a\n" + bloque(b"IHDR", struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0))
            + bloque(b"IDAT", zlib.compress(filas)) + bloque(b"IEND", b""))


def png_rgba(ancho=64, alto=64):
    """Mitad izquierda transparente y mitad derecha opaca."""
    def bloque(tipo, datos):
        return struct.pack(">I", len(datos)) + tipo + datos + struct.pack(">I", zlib.crc32(tipo + datos))
    fila = b"\x00" + bytes((200, 0, 0, 0)) * (ancho // 2) + bytes((200, 0, 0, 255)) * (ancho - ancho // 2)
    return (b"\x89PNG\r\n\x1a\n" + bloque(b"IHDR", struct.pack(">IIBBBBB", ancho, alto, 8, 6, 0, 0, 0))
            + bloque(b"IDAT", zlib.compress(fila * alto)) + bloque(b"IEND", b""))


def parrafo(texto="", estilo=None, interior=""):
    ppr = f'<w:pPr><w:pStyle w:val="{estilo}"/></w:pPr>' if estilo else ""
    run = f"<w:r><w:t>{texto}</w:t></w:r>" if texto else ""
    return f"<w:p>{ppr}{run}{interior}</w:p>"


def dibujo(rid, descr=""):
    return (f'<w:r><w:drawing><wp:inline><wp:docPr id="1" name="x" descr="{descr}"/>'
            f'<a:graphic><a:graphicData><pic:pic><pic:blipFill><a:blip r:embed="{rid}"/></pic:blipFill></pic:pic>'
            f"</a:graphicData></a:graphic></wp:inline></w:drawing></w:r>")


def forma(texto="", fallback=""):
    cuerpo = f"<wps:txbx><w:txbxContent><w:p><w:r><w:t>{texto}</w:t></w:r></w:p></w:txbxContent></wps:txbx>" if texto else ""
    return (f'<w:r><mc:AlternateContent><mc:Choice Requires="wps"><w:drawing><wp:anchor><wp:docPr id="9" name="f"/>'
            f"<a:graphic><a:graphicData><wps:wsp>{cuerpo}</wps:wsp></a:graphicData></a:graphic></wp:anchor></w:drawing></mc:Choice>"
            f"<mc:Fallback>{fallback}</mc:Fallback></mc:AlternateContent></w:r>")


def crear_docx(ruta, cuerpo, media=None, rels=None, estilos=None, extra=None):
    """rels: {id: destino} o {id: (destino, "External")}."""
    filas = []
    for rid, destino in (rels or {}).items():
        modo = ""
        if isinstance(destino, tuple):
            destino, m = destino
            modo = f' TargetMode="{m}"'
        filas.append(f'<Relationship Id="{rid}" Type="{TIPO_IMAGEN}" Target="{destino}"{modo}/>')
    with zipfile.ZipFile(ruta, "w") as z:
        z.writestr("word/document.xml", f"<w:document {NS}><w:body>{cuerpo}</w:body></w:document>")
        z.writestr("word/_rels/document.xml.rels", f'<Relationships xmlns="{RELS_NS}">' + "".join(filas) + "</Relationships>")
        for nombre, datos in (media or {}).items():
            z.writestr(nombre, datos)
        if estilos:
            z.writestr("word/styles.xml", f"<w:styles {NS}>{estilos}</w:styles>")
        for nombre, datos in (extra or {}).items():
            z.writestr(nombre, datos)
    return ruta


class Base(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.dir = Path(t.name)
        self.salida = self.dir / "salida"

    def correr(self, *args, sin_pymupdf=False):
        if sin_pymupdf:
            codigo = ("import sys, runpy; sys.modules['pymupdf'] = None; sys.modules['fitz'] = None; "
                      f"sys.argv = sys.argv[1:]; sys.exit(runpy.run_path({str(SCRIPT)!r})['main']())")
            cmd = [sys.executable, "-c", codigo, "extraer_imagenes.py", *map(str, args)]
        else:
            cmd = [sys.executable, str(SCRIPT), *map(str, args)]
        return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

    def extraer(self, entrada, *args, **kw):
        r = self.correr(entrada, "--salida", self.salida, *args, **kw)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads((self.salida / "inventario.json").read_text(encoding="utf-8"))

    def assertInvalida(self, entrada):
        r = self.correr(entrada, "--salida", self.salida)
        self.assertEqual(r.returncode, 2)
        self.assertIn("ERROR:", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertFalse(self.salida.exists(), "una entrada inválida no debe dejar salida")


class WordNormal(Base):
    def test_extrae_con_contexto(self):
        cuerpo = (parrafo("Intro") + parrafo("") + parrafo("Título de la figura") + parrafo("", interior=dibujo("rId1", "Texto alt"))
                  + parrafo("") + parrafo("Figura 1. Leyenda") + parrafo("Después"))
        doc = crear_docx(self.dir / "d.docx", cuerpo, {"word/media/image1.png": png()}, {"rId1": "media/image1.png"})
        inv = self.extraer(doc)
        self.assertEqual(len(inv["imagenes"]), 1)
        img = inv["imagenes"][0]
        self.assertEqual((img["formato"], img["ancho_px"], img["alto_px"], img["referencias"]), ("png", 64, 64, 1))
        self.assertEqual(img["texto_alternativo"], "Texto alt")
        self.assertEqual(img["leyenda"], "Figura 1. Leyenda")
        self.assertEqual(img["parrafo_anterior"], "Título de la figura")
        self.assertEqual(img["parrafo_siguiente"], "Figura 1. Leyenda")
        self.assertEqual(img["origen"], "incrustada")
        self.assertEqual((self.salida / img["archivo"]).read_bytes(), png())
        self.assertEqual((inv["descartadas"], inv["no_extraidas"], inv["avisos"]), ([], [], []))

    def test_sin_estilo_de_leyenda_quedan_los_vecinos(self):
        cuerpo = parrafo("Título de la imagen") + parrafo("", interior=dibujo("rId1")) + parrafo("Nota. Texto de la nota")
        doc = crear_docx(self.dir / "d.docx", cuerpo, {"word/media/a.png": png()}, {"rId1": "media/a.png"})
        img = self.extraer(doc)["imagenes"][0]
        self.assertIsNone(img["leyenda"])
        self.assertIsNone(img["texto_alternativo"])
        self.assertEqual((img["parrafo_anterior"], img["parrafo_siguiente"]), ("Título de la imagen", "Nota. Texto de la nota"))

    def test_leyenda_por_estilo_traducido(self):
        estilos = '<w:style w:type="paragraph" w:styleId="Dsc1"><w:name w:val="caption"/></w:style>'
        cuerpo = parrafo("", interior=dibujo("rId1")) + parrafo("Vista general", estilo="Dsc1")
        doc = crear_docx(self.dir / "d.docx", cuerpo, {"word/media/a.png": png()}, {"rId1": "media/a.png"}, estilos=estilos)
        self.assertEqual(self.extraer(doc)["imagenes"][0]["leyenda"], "Vista general")

    def test_imagen_de_encabezado_se_cuenta(self):
        encabezado = f"<w:hdr {NS}>{parrafo('', interior=dibujo('rId1'))}</w:hdr>"
        rels = f'<Relationships xmlns="{RELS_NS}"><Relationship Id="rId1" Type="{TIPO_IMAGEN}" Target="media/a.png"/></Relationships>'
        doc = crear_docx(self.dir / "d.docx", parrafo("x"), {"word/media/a.png": png()},
                         extra={"word/header1.xml": encabezado, "word/_rels/header1.xml.rels": rels})
        self.assertEqual(self.extraer(doc)["imagenes"][0]["referencias"], 1)

    def test_archivo_sin_referencias_se_conserva_con_cero(self):
        doc = crear_docx(self.dir / "d.docx", parrafo("x"), {"word/media/a.png": png()})
        self.assertEqual(self.extraer(doc)["imagenes"][0]["referencias"], 0)

    def test_leyenda_arriba_de_la_imagen(self):
        cuerpo = parrafo("Figura 1. Arriba") + parrafo("", interior=dibujo("rId1")) + parrafo("Texto corrido")
        doc = crear_docx(self.dir / "d.docx", cuerpo, {"word/media/a.png": png()}, {"rId1": "media/a.png"})
        self.assertEqual(self.extraer(doc)["imagenes"][0]["leyenda"], "Figura 1. Arriba")

    def test_estilo_de_leyenda_sin_id_no_vuelve_leyenda_a_cualquier_parrafo(self):
        estilos = '<w:style w:type="paragraph"><w:name w:val="caption"/></w:style>'
        cuerpo = parrafo("Texto corrido") + parrafo("", interior=dibujo("rId1"))
        doc = crear_docx(self.dir / "d.docx", cuerpo, {"word/media/a.png": png()}, {"rId1": "media/a.png"}, estilos=estilos)
        self.assertIsNone(self.extraer(doc)["imagenes"][0]["leyenda"])

    def test_cuadro_de_texto_no_contamina_los_vecinos(self):
        cuerpo = (parrafo("Antes") + parrafo("", interior=forma("Dentro de la forma")) + parrafo("", interior=dibujo("rId1"))
                  + parrafo("", interior=forma("Otra forma")) + parrafo("Después"))
        doc = crear_docx(self.dir / "d.docx", cuerpo, {"word/media/a.png": png()}, {"rId1": "media/a.png"})
        inv = self.extraer(doc)
        img = inv["imagenes"][0]
        self.assertEqual((img["parrafo_anterior"], img["parrafo_siguiente"]), ("Antes", "Después"))
        self.assertEqual([f["texto"] for f in inv["no_extraidas"]], ["Dentro de la forma", "Otra forma"])

    def test_texto_de_cuadro_no_se_suma_al_parrafo_exterior(self):
        cuerpo = parrafo("Exterior", interior=forma("Interior")) + parrafo("", interior=dibujo("rId1"))
        doc = crear_docx(self.dir / "d.docx", cuerpo, {"word/media/a.png": png()}, {"rId1": "media/a.png"})
        self.assertEqual(self.extraer(doc)["imagenes"][0]["parrafo_anterior"], "Exterior")

    def test_imagen_en_cuadro_de_texto_usa_el_parrafo_exterior(self):
        cuadro = f"<w:r><w:pict><v:shape><v:textbox><w:txbxContent>{parrafo('Interior', interior=dibujo('rId1'))}</w:txbxContent></v:textbox></v:shape></w:pict></w:r>"
        cuerpo = parrafo("Antes") + parrafo("", interior=cuadro) + parrafo("Después")
        doc = crear_docx(self.dir / "d.docx", cuerpo, {"word/media/a.png": png()}, {"rId1": "media/a.png"})
        img = self.extraer(doc)["imagenes"][0]
        self.assertEqual((img["referencias"], img["parrafo_anterior"], img["parrafo_siguiente"]), (1, "Antes", "Después"))

    def test_vml_directo(self):
        vml = '<w:r><w:pict><v:shape alt="Alt VML"><v:imagedata r:id="rId1"/></v:shape></w:pict></w:r>'
        doc = crear_docx(self.dir / "d.docx", parrafo("", interior=vml), {"word/media/a.png": png()}, {"rId1": "media/a.png"})
        inv = self.extraer(doc)
        self.assertEqual(inv["imagenes"][0]["referencias"], 1)
        self.assertEqual(inv["imagenes"][0]["texto_alternativo"], "Alt VML")
        self.assertEqual(inv["no_extraidas"], [])

    def test_destinos_absolutos_y_codificados(self):
        cuerpo = parrafo("", interior=dibujo("rId1")) + parrafo("", interior=dibujo("rId2"))
        doc = crear_docx(self.dir / "d.docx", cuerpo, {"word/media/a.png": png(40, 40), "word/media/b c.png": png(50, 50)},
                         {"rId1": "/word/media/a.png", "rId2": "media/b%20c.png"})
        inv = self.extraer(doc)
        self.assertEqual([i["referencias"] for i in inv["imagenes"]], [1, 1])
        self.assertEqual(inv["no_extraidas"], [])

    def test_pies_notas_y_comentarios(self):
        rels = f'<Relationships xmlns="{RELS_NS}"><Relationship Id="rId1" Type="{TIPO_IMAGEN}" Target="media/%s"/></Relationships>'
        extra = {}
        media = {}
        for i, (parte, raiz) in enumerate((("footer1", "ftr"), ("footnotes", "footnotes"), ("endnotes", "endnotes"), ("comments", "comments"))):
            cuerpo = parrafo(f"Texto {parte}", interior=dibujo("rId1")) + parrafo("", interior=forma(f"Forma {parte}"))
            extra[f"word/{parte}.xml"] = f"<w:{raiz} {NS}>{cuerpo}</w:{raiz}>"
            extra[f"word/_rels/{parte}.xml.rels"] = rels % f"{parte}.png"
            media[f"word/media/{parte}.png"] = png(40 + i, 40)
        inv = self.extraer(crear_docx(self.dir / "d.docx", parrafo("x"), media, extra=extra))
        self.assertEqual(sorted(i["parte"] for i in inv["imagenes"]), [f"word/{n}.xml" for n in ("comments", "endnotes", "footer1", "footnotes")])
        self.assertTrue(all(i["referencias"] == 1 for i in inv["imagenes"]))
        self.assertEqual(sorted(f["texto"] for f in inv["no_extraidas"]), [f"Forma {n}" for n in ("comments", "endnotes", "footer1", "footnotes")])

    def test_ooxml_estricto_avisa(self):
        doc = self.dir / "d.docx"
        with zipfile.ZipFile(doc, "w") as z:
            z.writestr("word/document.xml", '<w:document xmlns:w="http://purl.oclc.org/ooxml/wordprocessingml/main"><w:body/></w:document>')
        self.assertEqual(sum("OOXML estricto" in a for a in self.extraer(doc)["avisos"]), 1)

    def test_jpeg_truncado_se_conserva_con_aviso(self):
        doc = crear_docx(self.dir / "d.docx", parrafo("x"), {"word/media/a.jpg": b"\xff\xd8\xff\xe0"})
        inv = self.extraer(doc)
        self.assertEqual(len(inv["imagenes"]), 1)
        self.assertIsNone(inv["imagenes"][0]["ancho_px"])
        self.assertIn("no se pudo medir", inv["avisos"][0])


class ImagenMinima(Base):
    def _docx(self, ancho, alto):
        return crear_docx(self.dir / "d.docx", parrafo("x"), {"word/media/a.png": png(ancho, alto)})

    def test_bajo_el_umbral_va_a_descartadas(self):
        inv = self.extraer(self._docx(31, 500))
        self.assertEqual(inv["imagenes"], [])
        self.assertEqual(len(inv["descartadas"]), 1)
        self.assertIn("imagen mínima", inv["descartadas"][0]["motivo"])
        self.assertIn("31x500", inv["descartadas"][0]["motivo"])

    def test_justo_en_el_umbral_se_conserva(self):
        inv = self.extraer(self._docx(32, 32))
        self.assertEqual(len(inv["imagenes"]), 1)
        self.assertEqual(inv["lado_minimo_px"], 32)

    def test_umbral_configurable(self):
        inv = self.extraer(self._docx(32, 32), "--lado-minimo", "33")
        self.assertEqual(inv["imagenes"], [])
        self.assertEqual(inv["lado_minimo_px"], 33)
        self.assertEqual(self.correr(self._docx(32, 32), "--salida", self.salida, "--lado-minimo", "0").returncode, 2)


class Repetidas(Base):
    def test_mismo_hash_en_otro_archivo(self):
        cuerpo = parrafo("", interior=dibujo("rId1")) + parrafo("", interior=dibujo("rId2"))
        doc = crear_docx(self.dir / "d.docx", cuerpo, {"word/media/a.png": png(), "word/media/b.png": png()},
                         {"rId1": "media/a.png", "rId2": "media/b.png"})
        inv = self.extraer(doc)
        self.assertEqual(len(inv["imagenes"]), 1)
        self.assertEqual(inv["imagenes"][0]["referencias"], 2)
        self.assertEqual(len(inv["descartadas"]), 1)
        self.assertEqual(inv["descartadas"][0]["ubicacion"], "word/media/b.png")
        self.assertEqual(inv["descartadas"][0]["igual_a"], inv["imagenes"][0]["id"])
        self.assertIn("repetida", inv["descartadas"][0]["motivo"])
        self.assertEqual(len(list(self.salida.glob("*.png"))), 1)

    def test_un_archivo_referenciado_varias_veces(self):
        cuerpo = parrafo("Uno") + parrafo("", interior=dibujo("rId1")) + parrafo("Dos") + parrafo("", interior=dibujo("rId1")) + parrafo("Tres")
        doc = crear_docx(self.dir / "d.docx", cuerpo, {"word/media/a.png": png()}, {"rId1": "media/a.png"})
        inv = self.extraer(doc)
        self.assertEqual(inv["imagenes"][0]["referencias"], 2)
        self.assertEqual(inv["descartadas"], [])
        self.assertEqual(inv["imagenes"][0]["parrafo_anterior"], "Uno")
        self.assertEqual(inv["imagenes"][0]["otras_referencias"][0]["parrafo_anterior"], "Dos")

    def test_repetida_entre_documentos_de_una_carpeta(self):
        carpeta = self.dir / "docs"
        carpeta.mkdir()
        for nombre in ("a.docx", "b.docx"):
            crear_docx(carpeta / nombre, parrafo("", interior=dibujo("rId1")), {"word/media/x.png": png()}, {"rId1": "media/x.png"})
        inv = self.extraer(carpeta)
        self.assertEqual(len(inv["imagenes"]), 1)
        self.assertEqual(inv["imagenes"][0]["referencias"], 2)
        self.assertEqual(inv["descartadas"][0]["documento"], "b.docx")


class NoExtraidas(Base):
    def test_forma_de_word(self):
        cuerpo = parrafo("Antes") + parrafo("", interior=forma("Texto en la forma")) + parrafo("Después")
        inv = self.extraer(crear_docx(self.dir / "d.docx", cuerpo))
        self.assertEqual(len(inv["no_extraidas"]), 1)
        fila = inv["no_extraidas"][0]
        self.assertIn("wps:wsp", fila["tipo"])
        self.assertTrue(fila["motivo"])
        self.assertEqual(fila["texto"], "Texto en la forma")
        self.assertEqual(fila["parrafo_anterior"], "Antes")

    def test_fallback_no_cuenta_como_referencia(self):
        """El mc:Fallback de una forma repite lo que Word muestra: no suma referencias ni otra forma."""
        vml = "<w:pict><v:shape><v:imagedata r:id='rId1'/></v:shape></w:pict>"
        cuerpo = parrafo("", interior=forma(fallback=vml + dibujo("rId1")))
        doc = crear_docx(self.dir / "d.docx", cuerpo, {"word/media/a.png": png()}, {"rId1": "media/a.png"})
        inv = self.extraer(doc)
        self.assertEqual(inv["imagenes"][0]["referencias"], 0)
        self.assertEqual(len(inv["no_extraidas"]), 1)

    def test_forma_vml_y_grafico_nativo(self):
        chart = ('<w:r><w:drawing><wp:inline><a:graphic><a:graphicData>'
                 '<c:chart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" r:id="rId9"/>'
                 '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r>')
        cuerpo = parrafo("", interior="<w:r><w:pict><v:rect/></w:pict></w:r>") + parrafo("", interior=chart)
        tipos = [f["tipo"] for f in self.extraer(crear_docx(self.dir / "d.docx", cuerpo))["no_extraidas"]]
        self.assertEqual(len(tipos), 2)
        self.assertIn("VML", tipos[0])
        self.assertIn("gráfico nativo", tipos[1])

    def test_grafico_moderno_y_smartart(self):
        def grafico(interior):
            return f"<w:r><w:drawing><wp:inline><a:graphic><a:graphicData>{interior}</a:graphicData></a:graphic></wp:inline></w:drawing></w:r>"
        cx = '<cx:chart xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex" r:id="rId9"/>'
        dgm = '<dgm:relIds xmlns:dgm="http://schemas.openxmlformats.org/drawingml/2006/diagram" r:dm="rId8"/>'
        alterno = f'<w:r><mc:AlternateContent><mc:Choice Requires="cx1">{grafico(cx)}</mc:Choice><mc:Fallback><w:r><w:t>Sin soporte</w:t></w:r></mc:Fallback></mc:AlternateContent></w:r>'
        cuerpo = parrafo("", interior=alterno) + parrafo("", interior=grafico(dgm))
        tipos = [f["tipo"] for f in self.extraer(crear_docx(self.dir / "d.docx", cuerpo))["no_extraidas"]]
        self.assertEqual(len(tipos), 2)
        self.assertIn("cx:chart", tipos[0])
        self.assertIn("SmartArt", tipos[1])

    def test_imagen_sin_relacion(self):
        sin_id = '<w:r><w:drawing><wp:inline><a:graphic><a:graphicData><pic:pic><pic:blipFill><a:blip/></pic:blipFill></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'
        vml = "<w:r><w:pict><v:shape><v:imagedata/></v:shape></w:pict></w:r>"
        cuerpo = parrafo("", interior=sin_id) + parrafo("", interior=vml)
        filas = self.extraer(crear_docx(self.dir / "d.docx", cuerpo))["no_extraidas"]
        self.assertEqual(len(filas), 2)
        self.assertTrue(all("sin relación" in f["motivo"] for f in filas))

    def test_conserva_leyenda_alternativo_y_demas_referencias(self):
        cuerpo = (parrafo("", interior=dibujo("rId1", "Alt del EMF")) + parrafo("Figura 1. Leyenda") + parrafo("Medio")
                  + parrafo("", interior=dibujo("rId1", "Otro alt")) + parrafo("Fin"))
        doc = crear_docx(self.dir / "d.docx", cuerpo, {"word/media/a.emf": b"EMF"}, {"rId1": "media/a.emf"})
        fila = self.extraer(doc)["no_extraidas"][0]
        self.assertEqual((fila["referencias"], fila["leyenda"], fila["texto_alternativo"]), (2, "Figura 1. Leyenda", "Alt del EMF"))
        self.assertEqual(len(fila["otras_referencias"]), 1)
        self.assertEqual(fila["otras_referencias"][0]["texto_alternativo"], "Otro alt")
        self.assertEqual(fila["otras_referencias"][0]["parrafo_siguiente"], "Fin")

    def _svg(self, rels, media):
        blip = ('<w:r><w:drawing><wp:inline><a:graphic><a:graphicData><pic:pic><pic:blipFill><a:blip r:embed="rId1"><a:extLst><a:ext>'
                '<asvg:svgBlip xmlns:asvg="http://schemas.microsoft.com/office/drawing/2016/SVG/main" r:embed="rId2"/>'
                "</a:ext></a:extLst></a:blip></pic:blipFill></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>")
        return self.extraer(crear_docx(self.dir / "d.docx", parrafo("", interior=blip), media, rels))

    def test_svg_que_acompana_a_su_png_no_se_lista(self):
        inv = self._svg({"rId1": "media/a.png", "rId2": "media/a.svg"}, {"word/media/a.png": png(), "word/media/a.svg": b"<svg/>"})
        self.assertEqual(len(inv["imagenes"]), 1)
        self.assertEqual(inv["no_extraidas"], [])

    def test_svg_se_lista_si_su_imagen_no_se_extrajo(self):
        inv = self._svg({"rId1": "media/a.png", "rId2": "media/a.svg"}, {"word/media/a.png": png(8, 8), "word/media/a.svg": b"<svg/>"})
        self.assertEqual(inv["imagenes"], [])
        self.assertEqual([f["ubicacion"] for f in inv["no_extraidas"]], ["word/media/a.svg"])

    def test_formatos_sin_lectura_visual(self):
        for nombre, datos, extension in (("a.emf", b"\x01\x00\x00\x00EMFDATA", "EMF"), ("b.wmf", b"\xd7\xcd\xc6\x9a", "WMF"),
                                         ("c.bmp", b"BM0000", "BMP"), ("d.tif", b"II*\x00", "TIF")):
            with self.subTest(nombre):
                doc = crear_docx(self.dir / "d.docx", parrafo("", interior=dibujo("rId1")), {f"word/media/{nombre}": datos}, {"rId1": f"media/{nombre}"})
                inv = self.extraer(doc)
                self.assertEqual(inv["imagenes"], [])
                self.assertIn(extension, inv["no_extraidas"][0]["motivo"])
                self.assertEqual(inv["no_extraidas"][0]["referencias"], 1)
                self.assertEqual(list(self.salida.glob(f"*{Path(nombre).suffix}")), [])

    def test_el_formato_sale_de_los_bytes_y_no_del_nombre(self):
        doc = crear_docx(self.dir / "d.docx", parrafo("x"), {"word/media/falso.png": b"no es imagen", "word/media/real.emf": png()})
        inv = self.extraer(doc)
        self.assertEqual([i["ubicacion"] for i in inv["imagenes"]], ["word/media/real.emf"])
        self.assertTrue(inv["imagenes"][0]["archivo"].endswith(".png"))
        self.assertEqual(inv["no_extraidas"][0]["ubicacion"], "word/media/falso.png")

    def test_referencias_externas_y_rotas(self):
        cuerpo = parrafo("", interior=dibujo("rId1")) + parrafo("", interior=dibujo("rId2")) + parrafo("", interior=dibujo("rId3"))
        doc = crear_docx(self.dir / "d.docx", cuerpo, rels={"rId1": ("https://example.com/a.png", "External"), "rId2": "media/falta.png"})
        filas = self.extraer(doc)["no_extraidas"]
        self.assertEqual(len(filas), 3)
        self.assertEqual(filas[0]["destino"], "https://example.com/a.png")
        self.assertIn("referencia rota", filas[1]["motivo"])
        self.assertIn("referencia rota", filas[2]["motivo"])

    def test_blip_enlazado_con_r_link(self):
        enlace = '<w:r><w:drawing><wp:inline><a:graphic><a:graphicData><pic:pic><pic:blipFill><a:blip r:link="rId1"/></pic:blipFill></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'
        doc = crear_docx(self.dir / "d.docx", parrafo("", interior=enlace), rels={"rId1": ("https://example.com/a.png", "External")})
        fila = self.extraer(doc)["no_extraidas"][0]
        self.assertEqual(fila["destino"], "https://example.com/a.png")


class NombresDelZip(Base):
    def test_nombres_hostiles_no_salen_de_la_carpeta(self):
        hostiles = ["word/media/../../../../evil1.png", "word/media/..\\..\\evil2.png", "word/media/C:\\evil3.png", "word/media/.png"]
        media = {n: png(40 + i, 40) for i, n in enumerate(hostiles)}
        doc = crear_docx(self.dir / "d.docx", parrafo("x"), media)
        inv = self.extraer(doc)
        self.assertEqual(len(inv["imagenes"]), 4)
        escritos = {p.name for p in self.salida.iterdir()}
        self.assertEqual(escritos, {i["archivo"] for i in inv["imagenes"]} | {"inventario.json"})
        self.assertEqual([p for p in self.dir.rglob("evil*") if p.parent != self.salida], [])
        for i in inv["imagenes"]:
            self.assertRegex(i["archivo"], r"^img-\d{3}-[\w.-]+\.png$")

    def test_relacion_que_sale_del_zip_queda_rota(self):
        (self.dir / "secreto.png").write_bytes(png())
        doc = crear_docx(self.dir / "d.docx", parrafo("", interior=dibujo("rId1")), rels={"rId1": "../../secreto.png"})
        inv = self.extraer(doc)
        self.assertEqual(inv["imagenes"], [])
        self.assertIn("referencia rota", inv["no_extraidas"][0]["motivo"])


class Invalidas(Base):
    def test_no_existe(self):
        self.assertInvalida(self.dir / "nada.docx")

    def test_formato_no_admitido(self):
        f = self.dir / "a.txt"
        f.write_text("x")
        self.assertInvalida(f)

    def test_docx_corrupto(self):
        f = self.dir / "a.docx"
        f.write_bytes(b"esto no es un zip")
        self.assertInvalida(f)

    def test_zip_sin_documento(self):
        f = self.dir / "a.docx"
        with zipfile.ZipFile(f, "w") as z:
            z.writestr("otra.txt", "x")
        self.assertInvalida(f)

    def test_xml_roto(self):
        f = self.dir / "a.docx"
        with zipfile.ZipFile(f, "w") as z:
            z.writestr("word/document.xml", "<w:document")
        self.assertInvalida(f)

    def test_carpeta_sin_documentos(self):
        carpeta = self.dir / "vacia"
        carpeta.mkdir()
        (carpeta / "notas.txt").write_text("x")
        self.assertInvalida(carpeta)

    def test_imagen_suelta_como_entrada_directa(self):
        f = self.dir / "a.png"
        f.write_bytes(png())
        self.assertInvalida(f)

    def test_codificacion_desconocida(self):
        f = self.dir / "a.docx"
        with zipfile.ZipFile(f, "w") as z:
            z.writestr("word/document.xml", '<?xml version="1.0" encoding="no-existe"?><w:document/>')
        self.assertInvalida(f)

    def test_salida_igual_a_la_entrada_o_que_la_contiene(self):
        carpeta = self.dir / "a" / "docs"
        carpeta.mkdir(parents=True)
        crear_docx(carpeta / "d.docx", parrafo("x"))
        for salida in (carpeta, self.dir / "a"):
            with self.subTest(salida):
                r = self.correr(carpeta, "--salida", salida)
                self.assertEqual(r.returncode, 2)
                self.assertIn("--salida", r.stderr)
                self.assertNotIn("Traceback", r.stderr)
        r = self.correr(carpeta / "d.docx", "--salida", carpeta / "d.docx")
        self.assertEqual(r.returncode, 2)
        self.assertIn("--salida", r.stderr)

    def test_docx_corrupto_en_carpeta_no_deja_salida_a_medias(self):
        carpeta = self.dir / "docs"
        carpeta.mkdir()
        crear_docx(carpeta / "a.docx", parrafo("x"), {"word/media/a.png": png()})
        (carpeta / "b.docx").write_bytes(b"roto")
        self.assertInvalida(carpeta)

    def test_salida_que_es_un_archivo(self):
        doc = crear_docx(self.dir / "d.docx", parrafo("x"), {"word/media/a.png": png()})
        self.salida.write_text("x")
        r = self.correr(doc, "--salida", self.salida)
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stderr)


class Carpeta(Base):
    def test_saltea_bloqueos_de_word_y_la_propia_salida(self):
        carpeta = self.dir / "docs"
        carpeta.mkdir()
        crear_docx(carpeta / "a.docx", parrafo("x"), {"word/media/a.png": png()})
        (carpeta / "~$a.docx").write_bytes(b"bloqueo")
        self.salida = carpeta / "figuras"
        self.assertEqual(len(self.extraer(carpeta)["imagenes"]), 1)
        crear_docx(self.salida / "copia.docx", parrafo("x"), {"word/media/b.png": png(70, 70)})
        self.assertEqual(len(self.extraer(carpeta)["imagenes"]), 1)

    def test_imagenes_sueltas_se_procesan_como_las_demas(self):
        carpeta = self.dir / "docs"
        carpeta.mkdir()
        (carpeta / "a.png").write_bytes(png())
        (carpeta / "b.png").write_bytes(png())
        (carpeta / "c.png").write_bytes(png(8, 8))
        (carpeta / "d.bmp").write_bytes(b"BM00")
        inv = self.extraer(carpeta)
        self.assertEqual([(i["origen"], i["ubicacion"]) for i in inv["imagenes"]], [("archivo", "a.png")])
        self.assertEqual(inv["imagenes"][0]["referencias"], 2)
        self.assertEqual([d["ubicacion"] for d in inv["descartadas"]], ["b.png", "c.png"])
        self.assertEqual(inv["descartadas"][0]["igual_a"], inv["imagenes"][0]["id"])
        self.assertIn("mínima", inv["descartadas"][1]["motivo"])
        self.assertEqual(inv["no_extraidas"][0]["ubicacion"], "d.bmp")
        self.assertEqual(inv["avisos"], [])

    def test_avisa_los_documentos_de_otro_formato(self):
        carpeta = self.dir / "docs"
        carpeta.mkdir()
        crear_docx(carpeta / "a.docx", parrafo("x"))
        for nombre in ("b.doc", "c.docm", "d.dotx", "e.odt", "f.rtf", "g.pptx"):
            (carpeta / nombre).write_bytes(b"x")
        self.assertEqual(sum("6 documentos de otro formato" in a for a in self.extraer(carpeta)["avisos"]), 1)


class PdfSinPyMuPDF(Base):
    def test_pdf_solo_avisa_y_sale_con_0(self):
        f = self.dir / "a.pdf"
        f.write_bytes(b"%PDF-1.4")
        r = self.correr(f, "--salida", self.salida, sin_pymupdf=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("PyMuPDF", r.stderr)
        inv = json.loads((self.salida / "inventario.json").read_text(encoding="utf-8"))
        self.assertIn("PyMuPDF", inv["avisos"][0])
        self.assertEqual(inv["imagenes"], [])

    def test_en_carpeta_sigue_con_el_resto(self):
        carpeta = self.dir / "docs"
        carpeta.mkdir()
        (carpeta / "a.pdf").write_bytes(b"%PDF-1.4")
        crear_docx(carpeta / "b.docx", parrafo("x"), {"word/media/a.png": png()})
        inv = self.extraer(carpeta, sin_pymupdf=True)
        self.assertEqual(len(inv["imagenes"]), 1)
        self.assertIn("a.pdf", inv["avisos"][0])


@unittest.skipUnless(PYMUPDF, "requiere PyMuPDF")
class PdfConPyMuPDF(Base):
    def _pdf(self):
        doc = PYMUPDF.open()
        p1 = doc.new_page()
        p1.insert_text((72, 60), "Título de la imagen")
        p1.insert_image(PYMUPDF.Rect(72, 100, 272, 300), stream=png(64, 64))
        p1.insert_text((72, 340), "Figura 1. Leyenda")
        p2 = doc.new_page()  # Página vectorial: curvas.
        for i in range(12):
            p2.draw_bezier((50, 50 + i * 20), (100, 80 + i * 20), (200, 20 + i * 20), (300, 50 + i * 20))
        p3 = doc.new_page()  # Tabla simple: muchas líneas, pero todas rectas.
        for i in range(15):
            p3.draw_line((50, 50 + i * 20), (500, 50 + i * 20))
        p4 = doc.new_page()  # Pocos trazos con diagonal: un adorno.
        p4.draw_line((50, 50), (300, 300))
        p5 = doc.new_page()  # Imagen mínima, y otra igual a la de la página 1.
        p5.insert_image(PYMUPDF.Rect(72, 100, 82, 110), stream=png(8, 8))
        p5.insert_image(PYMUPDF.Rect(72, 200, 272, 400), stream=png(64, 64))
        ruta = self.dir / "a.pdf"
        doc.save(ruta)
        doc.close()
        return ruta

    def test_imagenes_y_pagina_vectorial(self):
        inv = self.extraer(self._pdf())
        incrustadas = [i for i in inv["imagenes"] if i["origen"] == "incrustada"]
        vectoriales = [i for i in inv["imagenes"] if i["origen"] == "pagina_vectorial"]
        self.assertEqual(len(incrustadas), 1)
        self.assertEqual(incrustadas[0]["referencias"], 2)
        self.assertEqual(incrustadas[0]["pagina"], 1)
        self.assertEqual(incrustadas[0]["leyenda"], "Figura 1. Leyenda")
        self.assertEqual(incrustadas[0]["parrafo_anterior"], "Título de la imagen")
        self.assertEqual([v["pagina"] for v in vectoriales], [2])
        self.assertEqual(vectoriales[0]["formato"], "png")
        self.assertTrue((self.salida / vectoriales[0]["archivo"]).is_file())
        self.assertTrue(any("imagen mínima" in d["motivo"] for d in inv["descartadas"]))

    def test_avisa_las_paginas_con_muchos_trazos_rectos(self):
        avisos = [a for a in self.extraer(self._pdf())["avisos"] if "trazos rectos" in a]
        self.assertEqual(len(avisos), 1)
        self.assertIn("páginas 3:", avisos[0])

    def test_imagen_con_mascara_conserva_la_transparencia(self):
        doc = PYMUPDF.open()
        doc.new_page().insert_image(PYMUPDF.Rect(72, 100, 272, 300), stream=png_rgba(64, 64))
        ruta = self.dir / "a.pdf"
        doc.save(ruta)
        doc.close()
        img = self.extraer(ruta)["imagenes"][0]
        self.assertEqual(img["formato"], "png")
        pix = PYMUPDF.Pixmap((self.salida / img["archivo"]).read_bytes())
        self.assertEqual(pix.alpha, 1)
        self.assertEqual(pix.pixel(0, 0)[-1], 0)

    def test_misma_imagen_dos_veces_en_una_pagina(self):
        doc = PYMUPDF.open()
        pagina = doc.new_page()
        xref = pagina.insert_image(PYMUPDF.Rect(72, 100, 172, 200), stream=png())
        pagina.insert_image(PYMUPDF.Rect(72, 300, 172, 400), xref=xref)
        ruta = self.dir / "a.pdf"
        doc.save(ruta)
        doc.close()
        self.assertEqual(self.extraer(ruta)["imagenes"][0]["referencias"], 2)

    def test_pdf_corrupto(self):
        f = self.dir / "a.pdf"
        f.write_bytes(b"esto no es un pdf")
        self.assertInvalida(f)


class ConversionPdf(unittest.TestCase):
    """`imagen_pdf` con dobles de `doc` y `pymupdf`, para que corra en CI sin PyMuPDF."""

    class Pix:
        def __init__(self, *origen, n=3, alpha=0, width=10, height=10):
            self.origen, self.n, self.alpha, self.width, self.height = origen, n, alpha, width, height

        def tobytes(self, formato):
            return f"{formato}:{self.origen}".encode()

    def _dobles(self, base, pix=None, alfa=None):
        creados = []

        def pixmap(*args):
            if len(args) == 2 and args[0] == "doc":
                creado = alfa if args[1] == 99 else pix
            else:
                creado = self.Pix(*args)
            creados.append(args)
            return creado
        pymupdf = Punto(Pixmap=pixmap, csRGB="rgb")
        doc = "doc"

        class Doc(str):
            def extract_image(self, xref):
                return base
        return pymupdf, Doc(doc), creados

    def test_legible_sin_mascara_no_se_convierte(self):
        pymupdf, doc, creados = self._dobles({"image": png(), "ext": "png"})
        self.assertEqual(ei.imagen_pdf(pymupdf, doc, 1), (png(), "png"))
        self.assertEqual(creados, [])

    def test_formato_no_legible_se_convierte_a_png(self):
        pix = self.Pix("original")
        pymupdf, doc, _ = self._dobles({"image": b"jp2", "ext": "jpx"}, pix)
        self.assertEqual(ei.imagen_pdf(pymupdf, doc, 1), (pix.tobytes("png"), "png"))

    def test_sin_datos_tambien_se_convierte(self):
        pix = self.Pix("original")
        pymupdf, doc, _ = self._dobles(None, pix)
        self.assertEqual(ei.imagen_pdf(pymupdf, doc, 1), (pix.tobytes("png"), "png"))

    def test_cmyk_pasa_a_rgb(self):
        pix = self.Pix("cmyk", n=4)
        pymupdf, doc, creados = self._dobles({"image": b"jp2", "ext": "jpx"}, pix)
        datos, extension = ei.imagen_pdf(pymupdf, doc, 1)
        self.assertEqual(extension, "png")
        self.assertIn(("rgb", pix), creados)
        self.assertEqual(datos, self.Pix("rgb", pix).tobytes("png"))

    def test_mascara_se_compone_aunque_la_imagen_sea_legible(self):
        pix, alfa = self.Pix("base"), self.Pix("alfa")
        pymupdf, doc, creados = self._dobles({"image": png(), "ext": "png", "smask": 99}, pix, alfa)
        datos, extension = ei.imagen_pdf(pymupdf, doc, 1)
        self.assertEqual(extension, "png")
        self.assertIn((pix, alfa), creados)
        self.assertEqual(datos, self.Pix(pix, alfa).tobytes("png"))

    def test_mascara_de_otro_tamano_se_escala(self):
        pix, alfa = self.Pix("base"), self.Pix("alfa", width=5, height=5)
        pymupdf, doc, creados = self._dobles({"image": png(), "ext": "png", "smask": 99}, pix, alfa)
        ei.imagen_pdf(pymupdf, doc, 1)
        self.assertIn((alfa, 10, 10, None), creados)


class PaginaVectorial(unittest.TestCase):
    """El criterio se prueba sin PyMuPDF: en CI no está instalado."""

    @staticmethod
    def linea(x1, y1, x2, y2):
        return ("l", Punto(x=x1, y=y1), Punto(x=x2, y=y2))

    def test_rectas_nunca_convierten(self):
        items = [self.linea(0, i, 100, i) for i in range(50)]
        self.assertFalse(ei.es_pagina_vectorial([{"items": items}]))

    def test_diagonal_con_pocos_trazos_no_convierte(self):
        self.assertFalse(ei.es_pagina_vectorial([{"items": [self.linea(0, 0, 50, 50)]}]))

    def test_curva_o_diagonal_con_suficientes_trazos_convierte(self):
        rectas = [self.linea(0, i, 100, i) for i in range(ei.MIN_TRAZOS - 1)]
        self.assertTrue(ei.es_pagina_vectorial([{"items": rectas + [self.linea(0, 0, 50, 50)]}]))
        self.assertTrue(ei.es_pagina_vectorial([{"items": rectas}, {"items": [("c", None, None, None, None)]}]))


class Medir(unittest.TestCase):
    def test_formatos(self):
        jpeg = b"\xff\xd8\xff\xe0\x00\x04\x00\x00\xff\xc0\x00\x11\x08" + struct.pack(">HH", 480, 640) + b"\x00" * 12
        gif = b"GIF89a" + struct.pack("<HH", 320, 200) + b"\x00" * 4
        vp8x = b"RIFF\x00\x00\x00\x00WEBPVP8X\x00\x00\x00\x00\x00\x00\x00\x00" + (99).to_bytes(3, "little") + (49).to_bytes(3, "little")
        vp8 = b"RIFF\x00\x00\x00\x00WEBPVP8 \x00\x00\x00\x00\x00\x00\x00\x9d\x01\x2a" + struct.pack("<HH", 300, 150)
        vp8l = b"RIFF\x00\x00\x00\x00WEBPVP8L\x00\x00\x00\x00\x2f" + struct.pack("<I", 199 | (99 << 14))
        for datos, esperado in ((png(10, 20), ("png", 10, 20)), (jpeg, ("jpg", 640, 480)), (gif, ("gif", 320, 200)), (vp8x, ("webp", 100, 50)),
                                (vp8, ("webp", 300, 150)), (vp8l, ("webp", 200, 100))):
            self.assertEqual(ei.medir(datos), esperado)
        self.assertEqual(ei.medir(b"BM"), (None, None, None))


class Verificador(Base):
    PROMPT = textwrap.dedent("""\
        ---
        documento: "Manual"
        tipo: manual
        metodologia: diataxis
        medio: digital
        tratamiento: usted
        salida: docs/
        estructura:
          - Introducción
        {extra}---
        Cuerpo.
        """)
    INVENTARIO = "# Inventario de figuras\n\n## img-001\n\n**Tabla 9.** Mal numerada\n\n[PENDIENTE: ilegible]\n"

    def verificar(self, carpeta, extra=""):
        prompt = self.dir / "prompt-estilo.md"
        prompt.write_text(self.PROMPT.format(extra=extra), encoding="utf-8")
        return subprocess.run([sys.executable, str(VERIFICADOR), "--prompt", str(prompt), str(carpeta)],
                              capture_output=True, text=True, encoding="utf-8")

    def _inventario(self, carpeta):
        (carpeta / "figuras").mkdir(parents=True)
        (carpeta / "figuras" / "inventario.md").write_text(self.INVENTARIO, encoding="utf-8")

    def test_inventario_no_se_lee_en_una_carpeta(self):
        carpeta = self.dir / "doc"
        self._inventario(carpeta)
        (carpeta / "documento.md").write_text("# Manual\n\n# 1 Introducción\n\nTexto del manual.\n", encoding="utf-8")
        r = self.verificar(carpeta)
        self.assertIn("archivos: 1", r.stdout)
        self.assertNotIn("inventario", r.stdout)
        self.assertNotIn("PENDIENTE: ilegible", r.stdout)

    def test_inventario_no_se_lee_en_multiarchivo(self):
        carpeta = self.dir / "doc"
        self._inventario(carpeta)
        (carpeta / "README.md").write_text("# Manual\n\n[Introducción](<01 - Introducción.md>)\n", encoding="utf-8")
        (carpeta / "01 - Introducción.md").write_text("# 1 Introducción\n\nTexto del manual.\n", encoding="utf-8")
        r = self.verificar(carpeta, "entrega: multiarchivo\n")
        self.assertIn("archivos: 2", r.stdout)
        self.assertNotIn("inventario", r.stdout)
        self.assertNotIn("PENDIENTE: ilegible", r.stdout)

    def test_inventario_no_se_lee_desde_dentro_de_figuras(self):
        carpeta = self.dir / "doc"
        self._inventario(carpeta)
        (carpeta / "figuras" / "documento.md").write_text("# Manual\n\n# 1 Introducción\n\nTexto del manual.\n", encoding="utf-8")
        prompt = self.dir / "prompt-estilo.md"
        prompt.write_text(self.PROMPT.format(extra=""), encoding="utf-8")
        r = subprocess.run([sys.executable, str(VERIFICADOR), "--prompt", str(prompt), "."], cwd=carpeta / "figuras",
                           capture_output=True, text=True, encoding="utf-8")
        self.assertIn("archivos: 1", r.stdout)
        self.assertNotIn("PENDIENTE: ilegible", r.stdout)

    def test_otro_inventario_si_se_lee(self):
        carpeta = self.dir / "doc"
        carpeta.mkdir()
        (carpeta / "inventario.md").write_text("# Manual\n\n# 1 Introducción\n\n[PENDIENTE: ilegible]\n", encoding="utf-8")
        r = self.verificar(carpeta)
        self.assertIn("archivos: 1", r.stdout)
        self.assertIn("PENDIENTE: ilegible", r.stdout)


if __name__ == "__main__":
    unittest.main()
