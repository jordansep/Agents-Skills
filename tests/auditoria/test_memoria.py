"""Memoria de errores: aprende lo que se repite, con aprobación y sin guardar nada sensible."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SKILL = RAIZ / "skills" / "auditoria-sistemas"
SCRIPT = SKILL / "scripts" / "auditoria_lotes.py"
LECCION = {"categoria": "hallazgo_perdido", "clave": "anunciado-ausente", "leccion": "Los lectores no cruzan lo anunciado con lo que aparece en otras partes."}


class Memoria(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.memoria = self.dir / "personal" / "errores.jsonl"

    def correr(self, *args, ok=True):
        env = {**os.environ, "AUDITORIA_MEMORIA": str(self.memoria)}
        r = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, encoding="utf-8", env=env)
        if ok:
            self.assertEqual(r.returncode, 0, r.stderr)
        else:
            self.assertNotEqual(r.returncode, 0, r.stdout)
        return r

    def registrar(self, *lecciones, ok=True, trabajo=None):
        ruta = self.dir / "lecciones.json"
        ruta.write_text(json.dumps(list(lecciones), ensure_ascii=False), encoding="utf-8")
        extra = ["--trabajo", trabajo] if trabajo else []
        return self.correr("errores-registrar", "--lecciones", ruta, *extra, ok=ok)

    def test_lo_sensible_no_se_guarda(self):
        casos = ["Faltó revisar a.pdf en el índice.", "Mirá C:\\Users\\alguien\\doc para saberlo.", "Se perdió HU-18 en la tabla.",
                 "Escribí a alguien@example.com por esto.", "El commit abc1234f lo tenía.", "El documento dice «no aplica» en esa parte.",
                 "Había 127 casos sin contar.", "Lo revisó la gente de Ficticia en esa parte.", "Ver https://example.com/x por el detalle."]
        for texto in casos:
            with self.subTest(texto):
                self.registrar({**LECCION, "leccion": texto}, ok=False)
                self.assertFalse(self.memoria.exists(), "Rechazar es no escribir nada")

    def test_lista_blanca_rechaza_lo_que_no_parece_sensible(self):
        for texto in ("el centro de donantes no tenía ese dato", "faltó mirar la tabla del laboratorio", "la palabra zzzinventada no vale"):
            with self.subTest(texto):
                r = self.registrar({**LECCION, "leccion": texto}, ok=False)
                self.assertIn("no está en el vocabulario", r.stderr)
                self.assertFalse(self.memoria.exists())

    def test_tampoco_pasan_numeros_ni_signos(self):
        for texto in ("Se perdieron 3 hallazgos.", "Usá el valor x=y en la regla.", "regla_general para el lector"):
            with self.subTest(texto):
                self.registrar({**LECCION, "leccion": texto}, ok=False)

    def test_la_clave_tambien_pasa_el_control(self):
        self.registrar({**LECCION, "clave": "laboratorio-central"}, ok=False)

    def test_control_prueba_sin_guardar(self):
        ruta = self.dir / "l.json"
        ruta.write_text(json.dumps([LECCION], ensure_ascii=False), encoding="utf-8")
        self.assertIn("Control superado", self.correr("errores-control", "--lecciones", ruta, "--regla", "Una regla general.").stdout)
        self.correr("errores-control", "--regla", "Revisá el laboratorio.", ok=False)
        self.assertFalse(self.memoria.exists())

    def test_ninguna_escritura_evita_el_control(self):
        sys.path.insert(0, str(SKILL / "scripts"))
        import auditoria_memoria as m
        base = {"tipo": "auditoria", "id": "0" * 32, "mes": "2026-11", "conteos": {}, "errores": []}
        malos = [{**base, "sistema": "x"}, {**base, "id": "nombre del proyecto"}, {**base, "conteos": {"nota": "dato"}}, {**base, "conteos": {"diferencias": "dato"}},
                 {**base, "errores": [{**LECCION, "leccion": "Faltó el laboratorio."}]}, {**base, "errores": [{**LECCION, "extra": "dato"}]},
                 {"tipo": "regla", "clave": "tabla", "categoria": "conteo", "rol": "lector", "regla": "Revisá el laboratorio."}, {"tipo": "otro", "dato": "x"}]
        with tempfile.TemporaryDirectory() as carpeta, unittest.mock.patch.dict(os.environ, {"AUDITORIA_MEMORIA": str(Path(carpeta) / "e.jsonl")}):
            for malo in malos:
                with self.subTest(malo), self.assertRaises(SystemExit):
                    m.agregar_personal(malo)
            self.assertFalse((Path(carpeta) / "e.jsonl").exists())

    def test_los_textos_automaticos_pasan_el_control(self):
        sys.path.insert(0, str(SKILL / "scripts"))
        import auditoria_memoria as m
        for clave, (categoria, leccion) in m.AUTOMATICOS.items():
            self.assertIsNone(m.control_estricto(clave))
            self.assertIsNone(m.control_estricto(leccion))
            self.assertIn(categoria, m.CATEGORIAS)

    def test_vocabulario_sin_datos(self):
        sys.path.insert(0, str(SKILL / "scripts"))
        import auditoria_memoria as m
        palabras = m.vocabulario()
        self.assertGreater(len(palabras), 300)
        for palabra in palabras:
            self.assertRegex(palabra, r"^[a-zñ]+$")
        self.assertFalse(palabras & {"laboratorio", "donante", "hospital", "universidad"})

    def test_el_mensaje_de_rechazo_no_repite_el_dato(self):
        r = self.registrar({**LECCION, "leccion": "Se perdió HU-18 en la tabla."}, ok=False)
        self.assertNotIn("HU-18", r.stderr)

    def test_rechaza_nombres_de_la_corrida(self):
        trabajo = self.dir / "t"
        (trabajo / "fichas").mkdir(parents=True)
        (trabajo / "fichas" / "L01.json").write_text(json.dumps({"hechos": [{"tipo": "nombre", "clave": "sistema gamma", "valor": "x"}]}), encoding="utf-8")
        r = self.registrar({**LECCION, "leccion": "Faltó mirar el sistema gamma entero."}, ok=False, trabajo=trabajo)
        self.assertIn("nombre del objetivo", r.stderr)
        self.assertNotIn("gamma", r.stderr)

    def test_rechaza_datos_del_usuario(self):
        import getpass
        nombre = getpass.getuser().lower()
        if len(nombre) < 4:
            self.skipTest("Usuario demasiado corto para el filtro")
        self.registrar({**LECCION, "leccion": f"lo pidió {nombre} al final."}, ok=False)

    def test_el_registro_no_identifica_la_auditoria(self):
        trabajo = self.dir / "corrida-identificable"
        (trabajo / "verifica").mkdir(parents=True)
        (trabajo / "revision.json").write_text(json.dumps({
            "sin_sostener": [{"id": "P1:dato-secreto", "nota": "nota-secreta", "lote": "L01"}] * 3,
            "sin_ubicar": [{"id": "P2:otro-secreto", "hallazgo": "hallazgo-secreto"}], "diferencias": []}), encoding="utf-8")
        (trabajo / "verifica" / "V01.json").write_text(json.dumps([{"id": str(i)} for i in range(10)]), encoding="utf-8")
        self.registrar(trabajo=trabajo)
        texto = self.memoria.read_text(encoding="utf-8")
        for dato in ("secreto", "secreta", str(trabajo.name), self.tmp.name):
            self.assertNotIn(dato, texto)
        registro = json.loads(texto)
        self.assertEqual(registro["conteos"]["no_sostenidos"], 3)
        self.assertEqual({e["clave"] for e in registro["errores"]}, {"alta-tasa-no-sostenidos", "hallazgos-sin-ubicar"})

    def test_una_corrida_no_cuenta_dos_veces(self):
        trabajo = self.dir / "t"
        trabajo.mkdir()
        self.correr("errores-registrar", "--trabajo", trabajo)
        self.correr("errores-registrar", "--trabajo", trabajo, ok=False)

    def test_hacen_falta_dos_auditorias_para_proponer_y_aprobar(self):
        self.registrar(LECCION)
        self.assertIn("0 para proponer · 1 en observación", self.correr("errores-propuestas").stdout)
        aprobar = ("errores-aprobar", "--clave", LECCION["clave"], "--rol", "lector", "--regla", "Cruzá lo anunciado con el resto.")
        self.correr(*aprobar, ok=False)
        self.registrar(LECCION)
        salida = self.correr("errores-propuestas").stdout
        self.assertIn(f"{LECCION['clave']} · hallazgo_perdido · 2 auditorías", salida)
        self.correr(*aprobar)
        self.assertIn("0 para proponer · 0 en observación · 1 reglas activas", self.correr("errores-propuestas").stdout)

    def aprobar_regla(self, rol="lector", clave=LECCION["clave"], regla="Cruzá lo anunciado con el resto."):
        for _ in range(2):
            self.registrar({**LECCION, "clave": clave})
        self.correr("errores-aprobar", "--clave", clave, "--rol", rol, "--regla", regla)

    def test_la_regla_aprobada_tampoco_puede_tener_datos(self):
        for _ in range(2):
            self.registrar(LECCION)
        self.correr("errores-aprobar", "--clave", LECCION["clave"], "--rol", "lector", "--regla", "Revisá siempre HU-18.", ok=False)
        self.assertNotIn('"regla"', self.memoria.read_text(encoding="utf-8"))

    def test_la_regla_llega_sólo_al_prompt_de_su_rol(self):
        self.aprobar_regla()
        doc = self.dir / "doc.md"
        doc.write_text("# Alfa\nTexto del capítulo.\n", encoding="utf-8")
        trabajo = self.dir / "t"
        self.correr("preparar", doc, "--trabajo", trabajo)
        self.assertIn("Cruzá lo anunciado con el resto.", (trabajo / "lotes" / "L01.prompt.md").read_text(encoding="utf-8"))
        ficha = {"lote": "L01", "hechos": [], "transversal": [], "puntos": [{
            "n": 1, "nombre": "Alfa", "cobertura": {"completo": [], "parcial": [], "sin_leer": []}, "filas": [
                {"criterio": "C", "cumple": "No", "evidencia": "Falla (doc.md:2)", "severidad": "Media", "certeza": "CONFIRMADO"}],
            "defectos": [], "observaciones": [], "refutar": "x", "para_completar": [{"texto": "Arreglar", "severidad": "Media"}]}]}
        (trabajo / "fichas").mkdir()
        (trabajo / "fichas" / "L01.json").write_text(json.dumps(ficha), encoding="utf-8")
        self.correr("consolidar", "--trabajo", trabajo)
        self.assertNotIn("Cruzá lo anunciado", (trabajo / "verifica" / "V01.prompt.md").read_text(encoding="utf-8"))
        self.assertNotIn("Cruzá lo anunciado", (trabajo / "consolidado.md").read_text(encoding="utf-8"))

    def test_regla_de_verificador_y_de_hilo(self):
        self.aprobar_regla("verificador", "regla-uno", "Regla para quien verifica.")
        self.aprobar_regla("hilo", "regla-dos", "Regla para quien sintetiza.")
        doc = self.dir / "doc.md"
        doc.write_text("# Alfa\nTexto del capítulo.\n", encoding="utf-8")
        trabajo = self.dir / "t"
        self.correr("preparar", doc, "--trabajo", trabajo)
        ficha = {"lote": "L01", "hechos": [], "transversal": [], "puntos": [{
            "n": 1, "nombre": "Alfa", "cobertura": {"completo": [], "parcial": [], "sin_leer": []}, "filas": [
                {"criterio": "C", "cumple": "No", "evidencia": "Falla (doc.md:2)", "severidad": "Media", "certeza": "CONFIRMADO"}],
            "defectos": [], "observaciones": [], "refutar": "x", "para_completar": [{"texto": "Arreglar", "severidad": "Media"}]}]}
        (trabajo / "fichas").mkdir()
        (trabajo / "fichas" / "L01.json").write_text(json.dumps(ficha), encoding="utf-8")
        self.correr("consolidar", "--trabajo", trabajo)
        self.assertIn("Regla para quien verifica.", (trabajo / "verifica" / "V01.prompt.md").read_text(encoding="utf-8"))
        self.assertIn("Regla para quien sintetiza.", (trabajo / "consolidado.md").read_text(encoding="utf-8"))
        self.assertNotIn("Regla para quien", (trabajo / "lotes" / "L01.prompt.md").read_text(encoding="utf-8"))

    def test_tope_de_reglas(self):
        palabras = "tabla fila figura indice fecha cifra enlace imagen lote ficha tanda hoja nota norma paso plan".split()
        for i in palabras:
            self.registrar({**LECCION, "clave": f"clave-{i}"})
            self.registrar({**LECCION, "clave": f"clave-{i}"})
        for i in palabras[:15]:
            self.correr("errores-aprobar", "--clave", f"clave-{i}", "--rol", "lector", "--regla", "Una regla general.")
        r = self.correr("errores-aprobar", "--clave", "clave-plan", "--rol", "lector", "--regla", "Una regla general.", ok=False)
        self.assertIn("retirá una", r.stderr)

    def test_una_linea_cortada_no_rompe_la_memoria(self):
        self.memoria.parent.mkdir(parents=True)
        self.memoria.write_text('{"tipo": "audito\n', encoding="utf-8")
        self.assertIn("0 para proponer", self.correr("errores-propuestas").stdout)


class MemoriaDelSkill(unittest.TestCase):
    def test_aprobar_en_el_repo_escribe_la_regla_y_nada_mas(self):
        import argparse
        mock = unittest.mock
        sys.path.insert(0, str(SKILL / "scripts"))
        import auditoria_memoria as m
        with tempfile.TemporaryDirectory() as carpeta, mock.patch.dict(os.environ, {"AUDITORIA_MEMORIA": str(Path(carpeta) / "e.jsonl")}),                 mock.patch.object(m, "ruta_repo", lambda: Path(carpeta) / "memoria" / "reglas.json"):
            for _ in range(2):
                m.agregar_personal({"tipo": "auditoria", "id": f"{_:032x}", "mes": "2026-11", "conteos": {}, "errores": [LECCION]})
            m.aprobar(argparse.Namespace(clave=LECCION["clave"], rol="lector", regla="Cruzá lo anunciado con el resto.", repo=True))
            reglas = json.loads((Path(carpeta) / "memoria" / "reglas.json").read_text(encoding="utf-8"))
        self.assertEqual(reglas, [{"id": "ERR-001", "clave": LECCION["clave"], "categoria": "hallazgo_perdido", "rol": "lector", "regla": "Cruzá lo anunciado con el resto."}])

    def test_las_reglas_compartidas_no_tienen_datos_sensibles(self):
        sys.path.insert(0, str(SKILL / "scripts"))
        import auditoria_memoria as m
        reglas = json.loads((SKILL / "memoria" / "reglas.json").read_text(encoding="utf-8"))
        self.assertLessEqual(len(reglas), m.MAX_REGLAS)
        for regla in reglas:
            self.assertIsNone(m.control_estricto(regla["regla"], m.vetos_personales()), regla["regla"])
            self.assertIn(regla["rol"], m.ROLES)

    def test_el_skill_explica_cómo_usar_la_memoria(self):
        texto = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/memoria-errores.md", texto)
        referencia = (SKILL / "references" / "memoria-errores.md").read_text(encoding="utf-8")
        self.assertIn("Nunca apruebes una regla sin que el usuario", referencia)


if __name__ == "__main__":
    unittest.main()
