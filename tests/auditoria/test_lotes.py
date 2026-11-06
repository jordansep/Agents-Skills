"""Auditoría exhaustiva por lotes: el objetivo no llega al hilo principal y no baja ninguna exigencia."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "skills" / "auditoria-sistemas" / "scripts" / "auditoria_lotes.py"
SECRETO = "s3cr3t-valor-que-no-se-copia"
RELLENO = "Texto largo del capítulo que nadie debería leer en el hilo principal. "


def correr(*args, ok=True):
    r = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, encoding="utf-8")
    if ok:
        assert r.returncode == 0, r.stderr
    return r


def fila(criterio, cumple="Sí", **extra):
    return {"criterio": criterio, "cumple": cumple, "evidencia": f"{criterio}, en el texto", **extra}


def ficha(lote, n, filas, **extra):
    return {"lote": lote, "hechos": extra.pop("hechos", []), "transversal": [], "puntos": [{
        "n": n, "nombre": f"Punto {n}", "cobertura": {"completo": ["doc.md:1-9"], "parcial": [], "sin_leer": []}, "sin_material": False,
        "falta": "", "filas": filas, "defectos": [], "observaciones": [], "refutar": "Busqué un camino que la saltee",
        "para_completar": [], **extra}]}


class Lotes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.trabajo = self.dir / "t"
        cuerpo = "\n".join(RELLENO for _ in range(300))
        self.doc = self.dir / "doc.md"
        self.doc.write_text(f"# Alfa\n{cuerpo}\npassword: {SECRETO}\nTabla 1\nTabla 3\n# Beta\n{cuerpo}\n# Gamma\n{cuerpo}\n", encoding="utf-8")
        self.salida = correr("preparar", self.doc, "--trabajo", self.trabajo, "--limite", 8000).stdout
        self.plan = json.loads((self.trabajo / "plan.json").read_text(encoding="utf-8"))

    def escribir(self, carpeta, lote, dato):
        ruta = self.trabajo / carpeta / f"{lote}.json"
        ruta.parent.mkdir(exist_ok=True)
        ruta.write_text(json.dumps(dato, ensure_ascii=False), encoding="utf-8")

    def completar_fichas(self):
        """Todo lote lleva el punto 1 entero en Sí; el resto de los puntos, con un No."""
        for lote in self.plan["lotes"]:
            n = lote["puntos"][0]
            if n == 1:
                self.escribir("fichas", lote["id"], ficha(lote["id"], 1, [fila("C1"), fila("C2")]))
            else:
                self.escribir("fichas", lote["id"], ficha(lote["id"], n, [fila("C1"), fila("C2", "No", severidad="Media", certeza="CONFIRMADO")],
                                                          para_completar=[{"texto": "Arreglar C2", "severidad": "Media"}]))

    def armar(self, **sintesis):
        ruta = self.dir / "s.json"
        ruta.write_text(json.dumps({"equipo": "E", "sistema": "S", "resumen": "R", **sintesis}, ensure_ascii=False), encoding="utf-8")
        salida = correr("armar", "--trabajo", self.trabajo, "--sintesis", ruta, "--salida", self.dir / "i.html").stdout
        return (self.dir / "i.html").read_text(encoding="utf-8"), salida

    def test_salida_sin_el_texto_del_objetivo(self):
        self.assertNotIn(RELLENO, self.salida)

    def test_prompt_autocontenido(self):
        prompt = (self.trabajo / "lotes" / "L01.prompt.md").read_text(encoding="utf-8")
        self.assertIn("# Hoja del lector", prompt)
        self.assertIn(RELLENO, prompt)
        self.assertIn("no abras otros", prompt)

    def test_cita_fuera_del_lote_invalida_la_ficha(self):
        lote = self.plan["lotes"][0]
        dato = ficha(lote["id"], 1, [fila("C1")])
        dato["puntos"][0]["filas"][0]["evidencia"] = "Sí (doc.md:99999)"
        self.escribir("fichas", lote["id"], dato)
        self.assertIn("citas fuera del lote", correr("estado", "--trabajo", self.trabajo).stdout)

    def test_presupuesto_cuenta_el_arranque_de_cada_subagente(self):
        self.assertGreaterEqual(self.plan["presupuesto"]["primera_pasada"], len(self.plan["lotes"]) * 10000)
        self.assertIn("Sin los agentes livianos", self.salida)

    def test_lotes_dentro_del_limite_y_cobertura_total(self):
        self.assertGreater(len(self.plan["lotes"]), 1)
        self.assertTrue(all(l["tokens"] <= 8000 for l in self.plan["lotes"]))
        unido = "".join(p.read_text(encoding="utf-8") for p in sorted((self.trabajo / "lotes").glob("L??.txt")))
        self.assertEqual(unido.count(RELLENO), 900)

    def test_puntos_salen_del_indice(self):
        self.assertEqual([p["nombre"] for p in self.plan["puntos"]], ["Alfa", "Beta", "Gamma"])
        self.assertTrue(self.plan["doc_sin_consigna"])

    def test_barrido_ubica_sin_copiar_secretos(self):
        barrido = (self.trabajo / "barrido.json").read_text(encoding="utf-8")
        self.assertIn("credencial", barrido)
        self.assertNotIn(SECRETO, barrido)
        self.assertEqual(json.loads(barrido)["rotulos_salteados"], {"Tabla": [2]})

    def test_estado_marca_pendientes_e_invalidas(self):
        self.escribir("fichas", "L01", ficha("L01", 1, [fila("C1", "Quizás")]))
        salida = correr("estado", "--trabajo", self.trabajo).stdout
        self.assertIn("Inválida L01", salida)
        self.assertIn("L02", salida)
        self.assertNotEqual(correr("consolidar", "--trabajo", self.trabajo, ok=False).returncode, 0)

    def test_ver_devuelve_solo_lo_citado(self):
        salida = correr("ver", "doc.md:1-2", "--trabajo", self.trabajo).stdout
        self.assertIn("# Alfa", salida)
        self.assertEqual(salida.count(RELLENO), 1)

    def test_ver_acepta_varias_citas(self):
        salida = correr("ver", "doc.md:1", "doc.md:2", "doc.md:999999", "--trabajo", self.trabajo).stdout
        self.assertIn("# Alfa", salida)
        self.assertEqual(salida.count(RELLENO), 1)
        self.assertIn("No encontré doc.md:999999", salida)

    def test_el_peor_resultado_gana_entre_lotes(self):
        for i, lote in enumerate(self.plan["lotes"]):
            filas = [fila("C1"), fila("C2", "No", severidad="Alta", certeza="CONFIRMADO") if i == 0 else fila("C2")]
            for f in filas:
                f["evidencia"] = f["criterio"]
            self.escribir("fichas", lote["id"], ficha(lote["id"], 1, filas, para_completar=[{"texto": "x"}]))
        correr("consolidar", "--trabajo", self.trabajo)
        self.assertIn("[Alta] C2", self.armar()[0])

    def test_consolidado_acotado_y_prompts_de_revision(self):
        self.completar_fichas()
        correr("consolidar", "--trabajo", self.trabajo)
        consolidado = (self.trabajo / "consolidado.md").read_text(encoding="utf-8")
        self.assertNotIn(RELLENO, consolidado)
        self.assertNotIn(SECRETO, consolidado)
        self.assertTrue((self.trabajo / "coherencia.prompt.md").exists())
        self.assertTrue(list((self.trabajo / "verifica").glob("*.prompt.md")))

    def test_presupuesto_ajustado_a_la_corrida_real(self):
        p = self.plan["presupuesto"]
        n = len(self.plan["lotes"])
        self.assertEqual(p["primera_pasada"], p["fuente"] * 3 + n * 25000)
        self.assertEqual(p["peor_caso"], p["primera_pasada"] * 2 + p["fuente"] * 5)

    def test_consolidado_indica_el_modelo_de_cada_revision(self):
        self.completar_fichas()
        salida = correr("consolidar", "--trabajo", self.trabajo).stdout
        consolidado = (self.trabajo / "consolidado.md").read_text(encoding="utf-8")
        self.assertIn("(haiku)", consolidado)
        self.assertIn("`coherencia.prompt.md`, modelo opus", consolidado)
        self.assertIn("modelo opus): ", consolidado)
        self.assertIn("(haiku)", salida)

    def test_verificacion_sube_de_modelo_con_citas_sobre_imagenes(self):
        spec = importlib.util.spec_from_file_location("auditoria_lotes", SCRIPT)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        elegir = modulo.modelo_verificacion
        imagenes = ["a.pdf:12"]
        self.assertEqual(elegir([{"hallazgo": "Falla (a.pdf:11)"}, {"hallazgo": "Otra (b.pdf:12)"}], imagenes), "haiku")
        self.assertEqual(elegir([{"hallazgo": "Falla (a.pdf:11)"}, {"hallazgo": "Otra (a.pdf:12)"}], imagenes), "sonnet")
        self.assertEqual(elegir([{"hallazgo": "Tramo (a.pdf:10-13)"}], imagenes), "sonnet")
        self.assertEqual(elegir([{"hallazgo": "Sin imágenes (a.pdf:12)"}], []), "haiku")

    def test_segunda_pasada_a_ciegas(self):
        prompt = (self.trabajo / "lotes" / "L01.segunda.prompt.md").read_text(encoding="utf-8")
        self.assertIn("no abras `fichas/`", prompt)
        self.assertIn("/segunda/L01.json", prompt)

    def test_conflictos_de_hechos_entre_lotes(self):
        ids = [l["id"] for l in self.plan["lotes"]]
        for i, lote in enumerate(ids):
            self.escribir("fichas", lote, ficha(lote, 1, [fila("C1")], hechos=[{"clave": "Total", "tipo": "cifra", "valor": str(10 + (i > 0)), "cita": "capítulo"},
                                                                                {"clave": "HU-9", "tipo": "id", "rol": "usa", "valor": "x", "cita": "capítulo"}]))
        correr("consolidar", "--trabajo", self.trabajo)
        cruces = json.loads((self.trabajo / "cruces.json").read_text(encoding="utf-8"))
        self.assertEqual(cruces["conflictos"][0]["clave"], "total")
        self.assertEqual(cruces["sin_definir"][0]["clave"], "hu-9")

    def test_completo_exige_cruce_segunda_pasada_y_conciliacion(self):
        self.completar_fichas()
        correr("consolidar", "--trabajo", self.trabajo)
        self.assertRegex(self.armar()[0], r"1 · Alfa — Avanzado \(\d+ %\)")  # sin cruce: Coherente queda Parcial
        (self.trabajo / "coherencia.json").write_text("[]", encoding="utf-8")
        self.assertIn("1 · Alfa — Avanzado (100 %)", self.armar()[0])  # falta la segunda pasada
        revision = json.loads((self.trabajo / "revision.json").read_text(encoding="utf-8"))
        self.assertEqual(revision["candidatos"], [1])
        for lote in revision["lotes_segunda"]:
            self.escribir("segunda", lote, ficha(lote, 1, [fila("C1"), fila("C2")]))
        correr("consolidar", "--trabajo", self.trabajo)
        self.assertIn("1 · Alfa — Completo (100 %)", self.armar()[0])
        self.escribir("segunda", revision["lotes_segunda"][0], ficha("L01", 1, [fila("C1"), fila("C2", "No", severidad="Media", certeza="CONFIRMADO")]))
        correr("consolidar", "--trabajo", self.trabajo)
        html, salida = self.armar()
        self.assertIn("1 · Alfa — Avanzado", html)
        self.assertIn("Diferencia sin conciliar", salida)
        html, _ = self.armar(conciliacion=[{"id": "P1:c2", "resolucion": "Releído: cumple", "fila": {"cumple": "Sí"}}])
        self.assertIn("1 · Alfa — Completo (100 %)", html)
        self.assertIn("Releído: cumple", html)

    def test_sin_leer_impide_completo(self):
        self.completar_fichas()
        for lote in self.plan["puntos"][0]["lotes"]:
            dato = ficha(lote, 1, [fila("C1")])
            dato["puntos"][0]["cobertura"]["sin_leer"] = ["doc.md:50"]
            self.escribir("fichas", lote, dato)
            self.escribir("segunda", lote, ficha(lote, 1, [fila("C1")]))
        (self.trabajo / "coherencia.json").write_text("[]", encoding="utf-8")
        correr("consolidar", "--trabajo", self.trabajo)
        self.assertIn("1 · Alfa — Avanzado", self.armar()[0])

    def test_informe_con_las_cinco_secciones_y_anexos(self):
        self.completar_fichas()
        correr("consolidar", "--trabajo", self.trabajo)
        html, _ = self.armar(coherencia=[{"tema": "T", "texto": "Dos reglas", "tarea": "Unificar"}], listo=[{"pieza": "P", "veredicto": "no listo", "preguntas": ["¿Q?"]}])
        for seccion in ("Resumen", "Detalle por punto", "Coherencia entre fuentes", "¿Listo para implementar?", "Lista de tareas", "Matriz de cumplimiento", "Conciliación"):
            self.assertIn(seccion, html)
        self.assertIn("☐", html)

    def test_faltas_sin_tarea_avisan(self):
        for lote in self.plan["lotes"]:
            self.escribir("fichas", lote["id"], ficha(lote["id"], 2, [fila("C", "No", severidad="Media", certeza="CONFIRMADO")]))
        correr("consolidar", "--trabajo", self.trabajo)
        self.assertIn("tiene faltas y ninguna tarea", self.armar()[1])

    def test_variante_academica(self):
        self.completar_fichas()
        correr("consolidar", "--trabajo", self.trabajo)
        html, _ = self.armar(variante="academica", puntos_extra=[{"n": 9, "nombre": "X", "filas": [fila("C", "No", severidad="Alta")], "para_completar": [{"texto": "t"}]}])
        self.assertIn("Coherencia entre documentos", html)
        self.assertIn("Lista de tareas para el grupo", html)
        self.assertNotIn("[Alta]", html)


@unittest.skipUnless(importlib.util.find_spec("pymupdf"), "requiere pymupdf")
class MedirLectores(unittest.TestCase):
    def test_cuenta_solo_hallazgos_y_separa_variantes(self):
        spec = importlib.util.spec_from_file_location("medir_lectores", Path(__file__).with_name("medir_lectores.py"))
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        vara = [{"id": "uno", "patron": "CU-23"}, {"id": "dos", "patron": "CU-21"}]
        with tempfile.TemporaryDirectory() as carpeta:
            base = Path(carpeta)
            for nombre, filas in (("opus-1", [fila("CU-23", "No")]), ("opus-2", [fila("CU-21", "Parcial")]), ("sonnet-1", [fila("CU-23")])):
                (base / nombre / "fichas").mkdir(parents=True)
                (base / nombre / "fichas" / "L01.json").write_text(json.dumps(ficha("L01", 1, filas)), encoding="utf-8")
            (base / "sonnet-2").mkdir()
            r = modulo.medir(vara, [base / n for n in ("opus-1", "opus-2", "sonnet-1", "sonnet-2")])
        self.assertEqual(r["variantes"]["opus"], {"corridas": 2, "promedio": 1, "union": 2})
        self.assertEqual(r["variantes"]["sonnet"]["union"], 0, "Una fila en Sí no es un hallazgo")
        self.assertIsNone(r["corridas"]["sonnet-2"])


class LotesPdf(unittest.TestCase):
    def test_pdf_por_indice_con_paginas_para_ver_como_imagen(self):
        import pymupdf
        with tempfile.TemporaryDirectory() as carpeta:
            tmp = Path(carpeta)
            doc = pymupdf.open()
            for i in range(4):
                pagina = doc.new_page()
                if i != 2:
                    pagina.insert_text((50, 50), f"Pagina {i + 1}. " + "contenido suficiente para no marcarla " * 3, fontsize=8)
            doc.set_toc([[1, "Uno", 1], [1, "  ", 2], [1, "Dos", 3]])
            doc.save(tmp / "a.pdf")
            doc.close()
            correr("preparar", tmp / "a.pdf", "--trabajo", tmp / "t")
            plan = json.loads((tmp / "t" / "plan.json").read_text(encoding="utf-8"))
            self.assertEqual([p["nombre"] for p in plan["puntos"]], ["Uno", "Dos"])
            prompt = (tmp / "t" / "lotes" / "L01.prompt.md").read_text(encoding="utf-8")
            self.assertIn("página 3", prompt)
            salida = correr("ver", "a.pdf:2", "--trabajo", tmp / "t").stdout
            self.assertIn("Pagina 2", salida)
            self.assertNotIn("Pagina 1", salida)
            self.assertIn("4 páginas", correr("revisar-pdf", tmp / "a.pdf").stdout)


if __name__ == "__main__":
    unittest.main()
