"""Auditoría exhaustiva por lotes: el objetivo no llega al hilo principal y no baja ninguna exigencia."""
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "skills" / "auditoria-sistemas" / "scripts" / "auditoria_lotes.py"
SECRETO = "s3cr3t-valor-que-no-se-copia"
RELLENO = "Texto largo del capítulo que nadie debería leer en el hilo principal. "


def correr(*args, ok=True):
    r = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, encoding="utf-8")
    if ok:
        assert r.returncode == 0, r.stderr
    return r


def modulo_lotes():
    spec = importlib.util.spec_from_file_location("auditoria_lotes", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


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
                self.escribir("fichas", lote["id"], ficha(lote["id"], n, [fila("C1"), fila("C2", "No", severidad="Media", certeza="CONFIRMADO", evidencia=f"Falla (doc.md:{lote['rangos']['doc.md'][0]})")],
                                                          para_completar=[{"texto": "Arreglar C2", "severidad": "Media"}]))

    def preparar_doc(self, texto):
        """Otra corrida, de un solo lote, sobre un documento propio."""
        doc = self.dir / "otro.md"
        doc.write_text(texto, encoding="utf-8")
        trabajo = self.dir / "t2"
        correr("preparar", doc, "--trabajo", trabajo)
        return trabajo

    def escribir_en(self, trabajo, lote, dato):
        (trabajo / "fichas").mkdir(exist_ok=True)
        (trabajo / "fichas" / f"{lote}.json").write_text(json.dumps(dato, ensure_ascii=False), encoding="utf-8")

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

    def test_cita_corta_cuenta_en_lote_de_un_solo_pdf(self):
        m = modulo_lotes()
        unico = {"a.pdf": [40, 50]}
        corto = m.archivo_de_cita_corta(unico)
        self.assertEqual(m.leer_citas("Falla (p. 45)", unico, corto), [("a.pdf", 45, 45)])
        self.assertEqual(m.leer_citas("Falla (pp. 45-52)", unico, corto), [("a.pdf", 45, 52)])
        self.assertEqual(m.leer_citas("Falla (pp. 41, 45-46 y 48)", unico, corto), [("a.pdf", 41, 41), ("a.pdf", 45, 46), ("a.pdf", 48, 48)])
        self.assertEqual(m.leer_citas("Falla (p. 45, 12 ítems)", unico, corto), [("a.pdf", 45, 45)])
        self.assertEqual(m.leer_citas("Falla (a.pdf:41-42)", unico, corto), [("a.pdf", 41, 42)])
        self.assertEqual(m.leer_citas("Exp. 45 y app. 3", unico, corto), [])
        self.assertEqual(m.leer_citas("Falla (pp. 45–52)", unico, corto), [("a.pdf", 45, 52)])
        for forma in ("pág. 45", "págs. 45", "página 45", "páginas 45", "P. 45", "PÁGINA 45", "pagina 45"):
            self.assertEqual(m.leer_citas(f"Falla ({forma})", unico, corto), [("a.pdf", 45, 45)], forma)
        self.assertEqual(m.leer_citas("(p. 70, 74-75 y 79)", unico, corto), [("a.pdf", 70, 70), ("a.pdf", 74, 75), ("a.pdf", 79, 79)])
        self.assertEqual(m.leer_citas("(pp. 41 y 3 ítems)", unico, corto), [("a.pdf", 41, 41)])
        self.assertEqual(m.leer_citas("(pp. 45, 46, y 47)", unico, corto), [("a.pdf", 45, 45), ("a.pdf", 46, 46), ("a.pdf", 47, 47)])
        self.assertEqual(m.leer_citas("(p. 45, 12-13 ítems)", unico, corto), [("a.pdf", 45, 45)])
        puntos = lambda t: {"puntos": [{"filas": [{"evidencia": t}]}]}
        self.assertEqual(m.citas_fuera(puntos("Falla (p. 45)"), unico, cortas=True), [])
        self.assertEqual(m.citas_fuera(puntos("Falla (pp. 45-52)"), unico, cortas=True), ["a.pdf:45-52"])
        self.assertEqual(m.citas_fuera(puntos("Falla (p. 3)"), unico, cortas=True), ["a.pdf:3"])
        self.assertEqual(m.citas_fuera(puntos("Falla (p. 3)"), unico), [], "Una cita corta no invalida la ficha")
        self.assertEqual(m.citas_fuera(puntos("Falla (a.pdf:3)"), unico), ["a.pdf:3"])

    def test_rango_invertido_queda_fuera_de_tramo(self):
        m = modulo_lotes()
        unico = {"a.pdf": [40, 60]}
        puntos = lambda t: {"puntos": [{"filas": [{"evidencia": t}]}]}
        self.assertEqual(m.citas_fuera(puntos("(p. 55-45)"), unico, cortas=True), ["a.pdf:55-45"])
        self.assertEqual(m.citas_fuera(puntos("(a.pdf:55-45)"), unico), ["a.pdf:55-45"])

    def test_cita_corta_no_se_resuelve_con_varios_archivos_ni_en_lineas(self):
        m = modulo_lotes()
        varios = {"a.pdf": [1, 5], "b.pdf": [1, 5]}
        self.assertIsNone(m.archivo_de_cita_corta(varios))
        self.assertEqual(m.citas_fuera({"puntos": [{"filas": [{"evidencia": "(p. 45)"}]}]}, varios), [])
        self.assertIsNone(m.archivo_de_cita_corta({"doc.md": [1, 100]}))

    def test_el_lector_de_citas_no_confunde_nombres_parecidos(self):
        m = modulo_lotes()
        self.assertEqual(m.leer_citas("(a b.pdf:3)", ["b.pdf", "a b.pdf"]), [("a b.pdf", 3, 3)])
        self.assertEqual(m.leer_citas("(xb.pdf:3)", ["b.pdf"]), [])

    def test_numeracion_salteada_senala_el_que_falta(self):
        m = modulo_lotes()
        pieza = lambda texto: {"archivo": "a.pdf", "unidad": "p.", "desde": 7, "hasta": 7, "texto": texto, "vacia": False}
        barrido = m.barrer([pieza("PRF-01 y PRF-02, luego PRF-04. HU-1 y HU-3. CU-04.01, CU-04.02, CU-04.04. ISO-9001, ISO-14001, ISO-27001")])
        salteada = barrido["senales"]["numeracion_salteada"]
        self.assertEqual(salteada, {"cantidad": 2, "citas": ["a.pdf:7"], "faltan": ["CU-04.03", "PRF-03"]})

    def test_numeracion_salteada_no_copia_secretos(self):
        m = modulo_lotes()
        pieza = {"archivo": "a.md", "unidad": "líneas", "desde": 1, "hasta": 2, "texto": "1| password: CLAVE-1\n2| token=CLAVE-2 y secret: CLAVE-4\n3| DB_PASSWORD=CLAVE-5 CLAVE-6 y CLAVE-8", "vacia": False}
        self.assertNotIn("CLAVE", json.dumps(m.barrer([pieza]), ensure_ascii=False))

    def test_numeracion_salteada_cita_la_pagina_correcta(self):
        m = modulo_lotes()
        pieza = lambda n, texto: {"archivo": "a.pdf", "unidad": "p.", "desde": n, "hasta": n, "texto": texto, "vacia": False}
        salteada = m.barrer([pieza(7, "PRF-01"), pieza(9, "PRF-02"), pieza(10, "PRF-04")])["senales"]["numeracion_salteada"]
        self.assertEqual(salteada["citas"], ["a.pdf:9"])

    def test_numeracion_salteada_en_consolidado_y_salida_con_la_linea_correcta(self):
        lineas = ["relleno"] * 170
        lineas[0], lineas[149], lineas[159] = "PRF-01", "PRF-02", "PRF-04"
        trabajo = self.preparar_doc("\n".join(lineas))
        self.escribir_en(trabajo, "L01", ficha("L01", 1, [fila("C")]))
        salida = correr("consolidar", "--trabajo", trabajo).stdout
        consolidado = (trabajo / "consolidado.md").read_text(encoding="utf-8")
        self.assertIn("PRF-03", salida)
        self.assertRegex(consolidado, r"numeracion_salteada: 1 \(otro\.md:150\)\. Faltan: PRF-03")

    def test_faltantes_acotados_en_consolidado_y_salida(self):
        self.completar_fichas()
        ruta = self.trabajo / "barrido.json"
        barrido = json.loads(ruta.read_text(encoding="utf-8"))
        barrido["senales"]["numeracion_salteada"] = {"cantidad": 20, "citas": ["doc.md:1"], "faltan": [f"F-{i:03d}" for i in range(1, 21)]}
        ruta.write_text(json.dumps(barrido), encoding="utf-8")
        salida = correr("consolidar", "--trabajo", self.trabajo).stdout
        consolidado = (self.trabajo / "consolidado.md").read_text(encoding="utf-8")
        for texto in (salida, consolidado):
            self.assertIn("F-015", texto)
            self.assertNotIn("F-016", texto)
            self.assertIn("20 en total", texto)

    def test_enmascarar(self):
        m = modulo_lotes()
        base64 = "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7" + "A1b2" * 3
        for texto in ("DB_PASSWORD=x1y2", '"password": "x1y2"', "password: x1y2 otra palabra", "api_key: x1y2", "12| secret_key = x1y2"):
            self.assertNotIn("x1y2", m.enmascarar(texto), texto)
        self.assertIn("[valor omitido]", m.enmascarar("DB_PASSWORD=x1y2"))
        self.assertEqual(m.enmascarar(base64), "[línea base64 omitida]")
        self.assertEqual(m.enmascarar(f"12| {base64}"), "12| [línea base64 omitida]")
        for inicio in ("-----BEGIN RSA PRIVATE KEY-----", "BEGIN PRIVATE KEY"):
            sin_fin = m.enmascarar(f"{inicio}\n{base64}\nz9Y8x7==\nTexto que sigue\nMás texto")
            self.assertNotIn(base64, sin_fin)
            self.assertNotIn("z9Y8x7", sin_fin)
            self.assertIn("Texto que sigue\nMás texto", sin_fin, "Un BEGIN sin END no borra lo que sigue")
        con_fin = m.enmascarar(f"Antes\n-----BEGIN PRIVATE KEY-----\n{base64}\n-----END PRIVATE KEY-----\nDespués")
        self.assertEqual(con_fin, "Antes\n[clave privada omitida]\nDespués")
        con_prefijo = m.enmascarar(f"1| -----BEGIN PRIVATE KEY-----\n2| {base64}\n3| Sigue")
        self.assertNotIn(base64, con_prefijo)
        self.assertIn("3| Sigue", con_prefijo)

    def test_cita_sobre_bloque_pem_y_en_medio(self):
        base64 = "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7" + "A1b2" * 3
        trabajo = self.preparar_doc(f"Inicio\n-----BEGIN RSA PRIVATE KEY-----\n{base64}\n{base64}\n-----END RSA PRIVATE KEY-----\nFin")
        self.escribir_en(trabajo, "L01", ficha("L01", 1, [fila("Bloque", "No", severidad="Crítica", certeza="CONFIRMADO", evidencia="Clave (otro.md:2-5)"),
                                                           fila("Medio", "No", severidad="Crítica", certeza="CONFIRMADO", evidencia="Clave (otro.md:4)")]))
        correr("consolidar", "--trabajo", trabajo)
        prompt = (trabajo / "verifica" / "V01.prompt.md").read_text(encoding="utf-8")
        self.assertNotIn(base64, prompt)
        self.escribir_en(trabajo, "L01", ficha("L01", 1, [fila("Medio", "No", severidad="Crítica", certeza="CONFIRMADO", evidencia="Clave (otro.md:4)")]))
        correr("consolidar", "--trabajo", trabajo)
        prompt = (trabajo / "verifica" / "V01.prompt.md").read_text(encoding="utf-8")
        self.assertNotIn(base64, prompt)
        self.assertIn("[línea base64 omitida]", prompt)

    def test_prompt_tapa_el_campo_hallazgo(self):
        trabajo = self.preparar_doc("uno\ndos")
        self.escribir_en(trabajo, "L01", ficha("L01", 1, [fila("C", "No", severidad="Alta", certeza="CONFIRMADO", evidencia="(otro.md:1) DB_PASSWORD=x1y2z3")]))
        correr("consolidar", "--trabajo", trabajo)
        prompt = (trabajo / "verifica" / "V01.prompt.md").read_text(encoding="utf-8")
        self.assertNotIn("x1y2z3", prompt)

    def test_ubicacion_ajena_va_al_verificador_con_aviso(self):
        trabajo = self.preparar_doc("uno\ndos")
        self.escribir_en(trabajo, "L01", ficha("L01", 1, [fila("Ajeno", "No", severidad="Baja", certeza="CONFIRMADO", evidencia="Falla (externo.py:12)"),
                                                           fila("Linea", "No", severidad="Baja", certeza="CONFIRMADO", evidencia="Falla en la linea 4")]))
        self.assertIn("0 sin ubicar", correr("consolidar", "--trabajo", trabajo).stdout)
        prompt = (trabajo / "verifica" / "V01.prompt.md").read_text(encoding="utf-8")
        self.assertIn("P1:ajeno trae una ubicación", prompt)
        self.assertIn("P1:linea trae una ubicación", prompt)

    def test_lote_multiarchivo_con_cita_corta_va_al_verificador_con_aviso(self):
        carpeta = self.dir / "varios"
        carpeta.mkdir()
        (carpeta / "a.md").write_text("uno", encoding="utf-8")
        (carpeta / "b.md").write_text("dos", encoding="utf-8")
        trabajo = self.dir / "t2"
        correr("preparar", carpeta, "--trabajo", trabajo)
        self.escribir_en(trabajo, "L01", ficha("L01", 1, [fila("C", "No", severidad="Baja", certeza="CONFIRMADO", evidencia="Falla (p. 3)")]))
        salida = correr("consolidar", "--trabajo", trabajo).stdout
        self.assertIn("0 sin ubicar", salida)
        self.assertIn("P1:c trae una ubicación", (trabajo / "verifica" / "V01.prompt.md").read_text(encoding="utf-8"))

    def test_pendientes_se_calculan_por_id(self):
        trabajo = self.preparar_doc("uno\ndos")
        filas = lambda *nombres: [fila(n, "No", severidad="Baja", certeza="CONFIRMADO", evidencia="Falla (otro.md:1)") for n in nombres]
        self.escribir_en(trabajo, "L01", ficha("L01", 1, filas("A", "B")))
        veredictos = lambda *ids: json.dumps([{"id": i, "veredicto": "confirmado", "nota": ""} for i in ids])
        ruta = trabajo / "verifica" / "V01.json"
        correr("consolidar", "--trabajo", trabajo)
        ruta.write_text(veredictos("P1:a"), encoding="utf-8")
        self.assertIn("V01 (haiku)", correr("consolidar", "--trabajo", trabajo).stdout, "Archivo parcial")
        ruta.write_text(veredictos("P9:x", "P9:y"), encoding="utf-8")
        self.assertIn("V01 (haiku)", correr("consolidar", "--trabajo", trabajo).stdout, "Otros id")
        ruta.write_text(veredictos("P1:a", "P1:b"), encoding="utf-8")
        self.assertIn("verificación — ", correr("consolidar", "--trabajo", trabajo).stdout)

    def test_pendientes_cuentan_id_repetidos(self):
        self.completar_fichas()
        for lote in self.plan["lotes"]:
            evidencia = f"Falla (doc.md:{lote['rangos']['doc.md'][0]})"
            self.escribir("fichas", lote["id"], ficha(lote["id"], 1, [fila("A", "No", severidad="Baja", certeza="CONFIRMADO", evidencia=evidencia)]))
        veces = len(self.plan["lotes"])
        self.assertGreater(veces, 1)
        ruta = self.trabajo / "verifica" / "V01.json"
        correr("consolidar", "--trabajo", self.trabajo)
        ruta.write_text(json.dumps([{"id": "P1:a", "veredicto": "confirmado", "nota": ""}]), encoding="utf-8")
        self.assertIn("V01 (haiku)", correr("consolidar", "--trabajo", self.trabajo).stdout)
        ruta.write_text(json.dumps([{"id": "P1:a", "veredicto": "confirmado", "nota": ""}] * veces), encoding="utf-8")
        self.assertIn("verificación — ", correr("consolidar", "--trabajo", self.trabajo).stdout)

    def test_armar_avisa_de_los_sin_ubicar_sin_conciliar(self):
        self.completar_fichas()
        lote = self.plan["lotes"][1]["id"]
        dato = json.loads((self.trabajo / "fichas" / f"{lote}.json").read_text(encoding="utf-8"))
        dato["puntos"][0]["filas"].append(fila("Sin lugar", "No", severidad="Media", certeza="CONFIRMADO", evidencia="Falta algo en alguna parte"))
        self.escribir("fichas", lote, dato)
        correr("consolidar", "--trabajo", self.trabajo)
        id_hallazgo = json.loads((self.trabajo / "revision.json").read_text(encoding="utf-8"))["sin_ubicar"][0]["id"]
        self.assertIn(f"sin conciliar: {id_hallazgo}", self.armar()[1])
        self.assertNotIn(id_hallazgo, self.armar(conciliacion=[{"id": id_hallazgo, "resolucion": "Descartado: sin cita"}])[1])

    def test_preparar_vacia_paginas(self):
        viejo = self.trabajo / "paginas" / "viejo.png"
        viejo.parent.mkdir()
        viejo.write_bytes(b"x")
        correr("preparar", self.doc, "--trabajo", self.trabajo, "--limite", 8000)
        self.assertFalse(viejo.exists())

    def test_ver_acepta_guiones_largos(self):
        salida = correr("ver", "doc.md:1–2", "--trabajo", self.trabajo).stdout
        self.assertIn("# Alfa", salida)
        self.assertEqual(salida.count(RELLENO), 1)

    def test_png_pagina_distinto_para_nombres_parecidos(self):
        m = modulo_lotes()
        self.assertNotEqual(m.png_pagina(self.trabajo, "a b.pdf", 1), m.png_pagina(self.trabajo, "a-b.pdf", 1))

    def test_textos_del_repo_al_dia(self):
        self.assertIn("pip install pymupdf", (RAIZ / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8"))
        self.assertIn("texto citado", (SCRIPT.parents[1] / "agents" / "revisor-auditoria.md").read_text(encoding="utf-8"))
        protocolo = (SCRIPT.parents[1] / "references" / "exhaustiva-por-lotes.md").read_text(encoding="utf-8")
        self.assertIn("sin cita no hay hallazgo", protocolo)

    def test_hallazgo_sin_ubicar_queda_para_decidir(self):
        self.completar_fichas()
        lote = self.plan["lotes"][1]["id"]
        dato = json.loads((self.trabajo / "fichas" / f"{lote}.json").read_text(encoding="utf-8"))
        dato["puntos"][0]["filas"].append(fila("Sin lugar", "No", severidad="Media", certeza="CONFIRMADO", evidencia="Falta algo en alguna parte"))
        self.escribir("fichas", lote, dato)
        self.assertIn("pendientes: —", correr("estado", "--trabajo", self.trabajo).stdout, "La ficha no se invalida")
        salida = correr("consolidar", "--trabajo", self.trabajo).stdout
        self.assertIn("1 sin ubicar", salida)
        decidir = (self.trabajo / "consolidado.md").read_text(encoding="utf-8").split("## Para decidir")[1].split("## Transversal")[0]
        self.assertRegex(decidir, r"Sin ubicar P\d+:sin-lugar")
        prompts = "".join(p.read_text(encoding="utf-8") for p in (self.trabajo / "verifica").glob("*.prompt.md"))
        self.assertNotIn("sin-lugar", prompts)
        self.assertIn(":c2", prompts)

    def test_prompt_de_verificacion_trae_el_texto_citado(self):
        secreto = next(i for i, l in enumerate(self.doc.read_text(encoding="utf-8").splitlines(), 1) if l.startswith("password"))
        for l in self.plan["lotes"]:
            filas = [fila("C1")]
            if l["id"] == "L01":
                filas = [fila("C1", "No", severidad="Alta", certeza="CONFIRMADO", evidencia=f"Falla (doc.md:1, doc.md:{secreto})"),
                         fila("C2", "No", severidad="Baja", certeza="CONFIRMADO", evidencia="Otra (doc.md:99999)")]
            self.escribir("fichas", l["id"], ficha(l["id"], 1, filas))
        # doc.md:99999 está fuera del tramo: sin `rangos` no se valida, y acá se prueba el aviso.
        plan = json.loads((self.trabajo / "plan.json").read_text(encoding="utf-8"))
        for l in plan["lotes"]:
            del l["rangos"]
        (self.trabajo / "plan.json").write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
        correr("consolidar", "--trabajo", self.trabajo)
        prompt = (self.trabajo / "verifica" / "V01.prompt.md").read_text(encoding="utf-8")
        self.assertIn("# Alfa", prompt)
        self.assertIn("password: [valor omitido]", prompt)
        self.assertNotIn(SECRETO, prompt)
        self.assertIn("No encontré doc.md:99999", prompt)
        self.assertNotIn("# Beta", prompt, "Sólo lo citado, no el lote entero")

    def test_plan_viejo_sin_imagenes_ni_rangos_no_falla(self):
        self.completar_fichas()
        plan = json.loads((self.trabajo / "plan.json").read_text(encoding="utf-8"))
        for l in plan["lotes"]:
            del l["imagenes"], l["rangos"]
        (self.trabajo / "plan.json").write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
        barrido = json.loads((self.trabajo / "barrido.json").read_text(encoding="utf-8"))
        del barrido["enlaces"]
        (self.trabajo / "barrido.json").write_text(json.dumps(barrido, ensure_ascii=False), encoding="utf-8")
        self.assertIn("(haiku)", correr("consolidar", "--trabajo", self.trabajo).stdout)

    def test_corrida_vieja_con_otras_tandas_no_pide_verificar_de_nuevo(self):
        self.completar_fichas()
        correr("consolidar", "--trabajo", self.trabajo)
        ids = [h["id"] for l in self.plan["lotes"] for h in modulo_lotes().hallazgos_de_lote(json.loads((self.trabajo / "fichas" / f"{l['id']}.json").read_text(encoding="utf-8")))]
        (self.trabajo / "verifica" / "V07.json").write_text(json.dumps([{"id": i, "veredicto": "confirmado", "nota": ""} for i in ids]), encoding="utf-8")
        self.assertIn("verificación — ", correr("consolidar", "--trabajo", self.trabajo).stdout)

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


@unittest.skipUnless(importlib.util.find_spec("pymupdf"), "Requiere pymupdf")
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

    def crear_pdf(self, tmp, nombre="a.pdf"):
        """Página 1 con texto; página 2 con enlaces; página 3 sin texto, que se lee como imagen."""
        import pymupdf
        doc = pymupdf.open()
        for i in range(3):
            pagina = doc.new_page()
            if i != 2:
                pagina.insert_text((50, 50), f"Pagina {i + 1}. " + "contenido suficiente para no marcarla " * 3, fontsize=8)
        doc[1].insert_link({"kind": pymupdf.LINK_GOTO, "from": pymupdf.Rect(10, 10, 50, 30), "page": 0, "to": pymupdf.Point(0, 0)})
        doc[1].insert_link({"kind": pymupdf.LINK_GOTO, "from": pymupdf.Rect(10, 40, 50, 60), "page": 0, "to": pymupdf.Point(0, 0)})
        doc[1].insert_link({"kind": pymupdf.LINK_URI, "from": pymupdf.Rect(10, 70, 50, 90), "uri": "https://ejemplo.invalid/"})
        doc.set_toc([[1, "Uno", 1], [1, "Dos", 2]])
        doc.save(tmp / nombre)
        doc.close()

    def preparar_pdf(self, tmp, nombre="a.pdf"):
        self.crear_pdf(tmp, nombre)
        correr("preparar", tmp / nombre, "--trabajo", tmp / "t")
        return tmp / "t"

    def escribir_ficha(self, trabajo, filas, n=1):
        (trabajo / "fichas").mkdir(exist_ok=True)
        (trabajo / "fichas" / "L01.json").write_text(json.dumps(ficha("L01", n, filas), ensure_ascii=False), encoding="utf-8")

    def test_enlaces_por_archivo(self):
        with tempfile.TemporaryDirectory() as carpeta:
            trabajo = self.preparar_pdf(Path(carpeta))
            barrido = json.loads((trabajo / "barrido.json").read_text(encoding="utf-8"))
            self.assertEqual(barrido["enlaces"], {"a.pdf": {"internos": 2, "externos": 1}})
            self.escribir_ficha(trabajo, [fila("C")])
            self.assertIn("2 internos y 1 externos", correr("consolidar", "--trabajo", trabajo).stdout)
            self.assertIn("2 internos y 1 externos", (trabajo / "consolidado.md").read_text(encoding="utf-8"))

    def test_rasteriza_y_el_prompt_del_lector_nombra_el_png(self):
        with tempfile.TemporaryDirectory() as carpeta:
            trabajo = self.preparar_pdf(Path(carpeta))
            pngs = list((trabajo / "paginas").glob("*.png"))
            self.assertEqual(len(pngs), 1)
            self.assertTrue(pngs[0].name.endswith("-p003.png"))
            prompt = (trabajo / "lotes" / "L01.prompt.md").read_text(encoding="utf-8")
            self.assertIn(pngs[0].as_posix(), prompt)
            self.assertNotIn("herramienta de leer PDF", prompt)

    def test_citas_sobre_imagenes_van_en_su_tanda_con_los_png(self):
        with tempfile.TemporaryDirectory() as carpeta:
            trabajo = self.preparar_pdf(Path(carpeta))
            self.escribir_ficha(trabajo, [fila("Texto", "No", severidad="Baja", certeza="CONFIRMADO", evidencia="Falla (p. 1)"),
                                          fila("Imagen", "No", severidad="Baja", certeza="CONFIRMADO", evidencia="Falla (pp. 2-3)")])
            salida = correr("consolidar", "--trabajo", trabajo).stdout
            self.assertIn("V01 (haiku)", salida)
            self.assertIn("V02 (sonnet)", salida)
            comun = (trabajo / "verifica" / "V01.prompt.md").read_text(encoding="utf-8")
            imagen = (trabajo / "verifica" / "V02.prompt.md").read_text(encoding="utf-8")
            self.assertIn("Pagina 1", comun, "La cita corta trae su texto")
            self.assertNotIn(".png", comun)
            self.assertIn("-p003.png", imagen)
            self.assertIn("Pagina 2", imagen)
            self.assertNotIn("sin PNG", imagen)

    def test_muchos_hallazgos_y_sobre_imagenes_sin_choques(self):
        with tempfile.TemporaryDirectory() as carpeta:
            trabajo = self.preparar_pdf(Path(carpeta))
            filas = [fila(f"Texto {i}", "No", severidad="Baja", certeza="CONFIRMADO", evidencia="Falla (p. 1)") for i in range(45)]
            filas += [fila(f"Imagen {i}", "No", severidad="Baja", certeza="CONFIRMADO", evidencia="Falla (p. 3)") for i in range(45)]
            self.escribir_ficha(trabajo, filas)
            salida = correr("consolidar", "--trabajo", trabajo).stdout
            self.assertIn("'V01 (haiku)', 'V02 (haiku)', 'V03 (sonnet)', 'V04 (sonnet)'", salida)
            vistos = []
            for ruta in sorted((trabajo / "verifica").glob("*.prompt.md")):
                texto = ruta.read_text(encoding="utf-8")
                hallazgos = json.JSONDecoder().raw_decode(texto[texto.index("\n[\n") + 1:])[0]
                self.assertLessEqual(len(hallazgos), 40)
                vistos += [h["id"] for h in hallazgos]
            self.assertEqual(len(vistos), 90)
            self.assertEqual(len(set(vistos)), 90)

    def test_pagina_citada_dos_veces_aparece_una_vez(self):
        with tempfile.TemporaryDirectory() as carpeta:
            trabajo = self.preparar_pdf(Path(carpeta))
            self.escribir_ficha(trabajo, [fila("A", "No", severidad="Baja", certeza="CONFIRMADO", evidencia="Falla (p. 1)"),
                                          fila("B", "No", severidad="Baja", certeza="CONFIRMADO", evidencia="Otra (a.pdf:1)")])
            correr("consolidar", "--trabajo", trabajo)
            self.assertEqual((trabajo / "verifica" / "V01.prompt.md").read_text(encoding="utf-8").count("=== a.pdf p. 1 ==="), 1)

    def test_cita_corta_fuera_de_tramo_avisa_y_no_invalida(self):
        with tempfile.TemporaryDirectory() as carpeta:
            trabajo = self.preparar_pdf(Path(carpeta))
            self.escribir_ficha(trabajo, [fila("C", "No", severidad="Baja", certeza="CONFIRMADO", evidencia="El índice remite a la p. 120 (a.pdf:1)")])
            self.assertIn("pendientes: —", correr("estado", "--trabajo", trabajo).stdout)
            self.assertNotIn("Inválida", correr("estado", "--trabajo", trabajo).stdout)
            correr("consolidar", "--trabajo", trabajo)
            decidir = (trabajo / "consolidado.md").read_text(encoding="utf-8").split("## Para decidir")[1].split("## Transversal")[0]
            self.assertIn("Cita corta fuera de tramo en L01: a.pdf:120", decidir)
            self.escribir_ficha(trabajo, [fila("C", "No", severidad="Baja", certeza="CONFIRMADO", evidencia="Falla (a.pdf:120)")])
            self.assertIn("Inválida L01", correr("estado", "--trabajo", trabajo).stdout)

    def test_get_pixmap_que_falla_no_aborta_preparar(self):
        import pymupdf
        with tempfile.TemporaryDirectory() as carpeta:
            tmp = Path(carpeta)
            self.crear_pdf(tmp)
            salida = io.StringIO()
            with mock.patch.object(pymupdf.Page, "get_pixmap", side_effect=RuntimeError("roto")), \
                    mock.patch.object(sys, "argv", ["x", "preparar", str(tmp / "a.pdf"), "--trabajo", str(tmp / "t")]), redirect_stdout(salida):
                modulo_lotes().main()
            self.assertIn("no pude rasterizar a.pdf:3", salida.getvalue())
            prompt = (tmp / "t" / "lotes" / "L01.prompt.md").read_text(encoding="utf-8")
            self.assertIn("herramienta de leer PDF", prompt)
            self.assertIn("página 3", prompt)

    def test_cita_sobre_imagen_sin_png_avisa_y_va_en_sonnet(self):
        with tempfile.TemporaryDirectory() as carpeta:
            trabajo = self.preparar_pdf(Path(carpeta))
            for png in (trabajo / "paginas").glob("*.png"):
                png.unlink()
            self.escribir_ficha(trabajo, [fila("Imagen", "No", severidad="Baja", certeza="CONFIRMADO", evidencia="Falla (a.pdf:3)")])
            self.assertIn("V01 (sonnet)", correr("consolidar", "--trabajo", trabajo).stdout)
            self.assertIn("sin PNG", (trabajo / "verifica" / "V01.prompt.md").read_text(encoding="utf-8"))


class SinPymupdf(unittest.TestCase):
    """Se simula la falta de pymupdf: un pypdf mínimo lee el PDF, sin depender de que esté instalado."""

    def correr(self, *args):
        pagina = types.SimpleNamespace(extract_text=lambda: "Pagina con texto. " * 8, images=[])
        vacia = types.SimpleNamespace(extract_text=lambda: "", images=[])
        pypdf = types.SimpleNamespace(PdfReader=lambda _: types.SimpleNamespace(pages=[pagina, vacia], outline=[]))
        salida = io.StringIO()
        with mock.patch.dict(sys.modules, {"pymupdf": None, "pypdf": pypdf}), mock.patch.object(sys, "argv", ["x", *map(str, args)]), redirect_stdout(salida):
            modulo_lotes().main()
        return salida.getvalue()

    def test_sigue_andando_y_dice_que_no_pudo_hacer(self):
        with tempfile.TemporaryDirectory() as carpeta:
            tmp = Path(carpeta)
            (tmp / "a.pdf").write_bytes(b"%PDF-1.4")
            salida = self.correr("preparar", tmp / "a.pdf", "--trabajo", tmp / "t")
            self.assertIn("sin pymupdf no se pudieron contar", salida)
            barrido = json.loads((tmp / "t" / "barrido.json").read_text(encoding="utf-8"))
            self.assertEqual(barrido["enlaces"], {"a.pdf": None})
            self.assertFalse((tmp / "t" / "paginas").exists())
            prompt = (tmp / "t" / "lotes" / "L01.prompt.md").read_text(encoding="utf-8")
            self.assertIn("herramienta de leer PDF", prompt)
            self.assertIn("página 2", prompt)
            (tmp / "t" / "fichas").mkdir()
            (tmp / "t" / "fichas" / "L01.json").write_text(json.dumps(ficha("L01", 1, [fila("C", "No", severidad="Baja", evidencia="Falla (a.pdf:2)")]), ensure_ascii=False), encoding="utf-8")
            salida = self.correr("consolidar", "--trabajo", tmp / "t")
            self.assertIn("no se pudieron contar", salida)
            self.assertIn("no se pudieron contar", (tmp / "t" / "consolidado.md").read_text(encoding="utf-8"))
            self.assertIn("V01 (sonnet)", salida)
            self.assertIn("sin PNG", (tmp / "t" / "verifica" / "V01.prompt.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
