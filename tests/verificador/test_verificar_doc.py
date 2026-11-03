"""Tests de skills/documentacion-generar/scripts/verificar_doc.py.

Ejecutar desde la raíz del repositorio:
    python -m unittest discover -s tests -v
"""
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "skills" / "documentacion-generar" / "scripts" / "verificar_doc.py"
CONFIGURADOR = RAIZ / "skills" / "documentacion-estilo" / "assets" / "configurador.html"

spec = importlib.util.spec_from_file_location("verificar_doc", SCRIPT)
vd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vd)

PROMPT = """\
---
documento: "Manual de prueba"
tipo: manual
metodologia: diataxis
medio: digital
tratamiento: usted
salida: docs/
estructura:
  - Introducción
  - Uso
---
Cuerpo del prompt.
"""

DOC_VALIDO = """\
# Manual de prueba

# 1 Introducción

Este manual explica el uso del sistema. La Tabla 1 resume las opciones.

**Tabla 1.** Opciones del sistema

| Opción | Valor |
|---|---|
| Modo | Activo |

# 2 Uso

La Figura 1 muestra la pantalla principal.

![Pantalla principal del sistema](img.png)

**Figura 1.** Pantalla principal
"""

MEMORIA_AGENTE = """\
# Registro de decisiones de estilo

## DEC-001 · Tratamiento

- **Estado**: confirmada
- **Alcance**: agente

## DEC-002 · Números

- **Estado**: descartada
- **Alcance**: agente
"""

MEMORIA_PROYECTO = """\
# Decisiones de estilo del proyecto

## DP-001 · Títulos

- **Estado**: confirmada
- **Alcance**: proyecto
"""


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def escribir(self, nombre, texto):
        ruta = self.dir / nombre
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(textwrap.dedent(texto), encoding="utf-8")
        return ruta

    def verificar(self, doc, prompt=PROMPT, memorias=None, **extra):
        texto = prompt
        for clave, valor in extra.items():
            texto = texto.replace("---\nCuerpo", f"{clave}: {valor}\n---\nCuerpo", 1)
        datos, _, _ = vd.leer_frontmatter(texto)
        inf = vd.Informe()
        vd.verificar(datos, [self.escribir("doc.md", doc)], inf, memorias)
        return inf

    def assertSinProblemas(self, inf):
        self.assertEqual(inf.errores, [], "errores inesperados")
        self.assertEqual(inf.advertencias, [], "advertencias inesperadas")

    def assertMensaje(self, lista, patron):
        self.assertTrue(any(re.search(patron, m) for m in lista), f"no aparece /{patron}/ en {lista}")


class DocumentoValido(Base):
    def test_documento_valido_no_tiene_errores_ni_advertencias(self):
        self.assertSinProblemas(self.verificar(DOC_VALIDO))


class Titulos(Base):
    def test_nivel_5_es_error(self):
        inf = self.verificar(DOC_VALIDO + "\n##### Detalle\n")
        self.assertMensaje(inf.errores, r"título de nivel 5")

    def test_titulo_con_punto_final_es_error(self):
        inf = self.verificar(DOC_VALIDO.replace("# 2 Uso", "# 2 Uso."))
        self.assertMensaje(inf.errores, r"termina en punto")

    def test_numeracion_salteada_es_error(self):
        inf = self.verificar(DOC_VALIDO.replace("# 2 Uso", "# 3 Uso"))
        self.assertMensaje(inf.errores, r"numeración 3; se esperaba 2")

    def test_titulo_sin_numero_en_capitulo_numerado_es_error(self):
        inf = self.verificar(DOC_VALIDO + "\n## Detalles\n")
        self.assertMensaje(inf.errores, r"sin numeración decimal")

    def test_subtitulo_bien_numerado_pasa(self):
        self.assertSinProblemas(self.verificar(DOC_VALIDO + "\n## 2.1 Detalles\n\nTexto breve.\n"))


class Estructura(Base):
    def test_falta_capitulo_del_prompt_es_error(self):
        inf = self.verificar(DOC_VALIDO.split("# 2 Uso")[0].replace("La Tabla 1", "La Tabla 1"))
        self.assertMensaje(inf.errores, r"falta el capítulo «uso»")


class TablasYFiguras(Base):
    def test_tabla_sin_leyenda_es_error(self):
        inf = self.verificar(DOC_VALIDO.replace("**Tabla 1.** Opciones del sistema\n", ""))
        self.assertMensaje(inf.errores, r"tabla sin la línea «\*\*Tabla N\.\*\* Título» antes")

    def test_figura_sin_leyenda_es_error(self):
        inf = self.verificar(DOC_VALIDO.replace("**Figura 1.** Pantalla principal\n", ""))
        self.assertMensaje(inf.errores, r"figura sin la línea «\*\*Figura N\.\*\* Título» después")

    def test_imagen_sin_texto_alternativo_es_error_en_digital(self):
        inf = self.verificar(DOC_VALIDO.replace("![Pantalla principal del sistema]", "![]"))
        self.assertMensaje(inf.errores, r"imagen sin texto alternativo")

    def test_numeracion_no_continua_es_error(self):
        doc = DOC_VALIDO.replace("**Tabla 1.**", "**Tabla 2.**").replace("La Tabla 1", "La Tabla 2")
        inf = self.verificar(doc)
        self.assertMensaje(inf.errores, r"Tabla 2: la numeración no es continua")

    def test_tabla_no_mencionada_es_advertencia(self):
        inf = self.verificar(DOC_VALIDO.replace(" La Tabla 1 resume las opciones.", ""))
        self.assertMensaje(inf.advertencias, r"Tabla 1 no se menciona")

    def test_leyendas_apa7_pasan(self):
        doc = DOC_VALIDO.replace("**Tabla 1.** Opciones del sistema", "**Tabla 1**\n\n*Opciones del sistema*")
        doc = doc.replace("La Figura 1 muestra la pantalla principal.\n\n![", "La Figura 1 muestra la pantalla principal.\n\n**Figura 1**\n\n*Pantalla principal*\n\n![")
        doc = doc.replace("\n**Figura 1.** Pantalla principal\n", "")
        self.assertSinProblemas(self.verificar(doc, leyendas="apa7"))

    def test_leyenda_clasica_con_prompt_apa7_es_error(self):
        inf = self.verificar(DOC_VALIDO, leyendas="apa7")
        self.assertMensaje(inf.errores, r"tabla sin la leyenda APA 7")


class ReferenciasCruzadas(Base):
    def test_referencia_a_tabla_inexistente_es_error(self):
        inf = self.verificar(DOC_VALIDO + "\nEl detalle está en la Tabla 3.\n")
        self.assertMensaje(inf.errores, r"se cita la Tabla 3, que no existe")

    def test_referencia_a_figura_inexistente_es_error(self):
        inf = self.verificar(DOC_VALIDO + "\nVer la figura 7 para más detalle.\n")
        self.assertMensaje(inf.errores, r"se cita la Figura 7, que no existe")

    def test_referencia_existente_pasa(self):
        self.assertSinProblemas(self.verificar(DOC_VALIDO + "\nComo muestra la Figura 1, el menú está arriba.\n"))

    def test_referencia_dentro_de_codigo_se_ignora(self):
        self.assertSinProblemas(self.verificar(DOC_VALIDO + "\nEl campo `Tabla 9` es un identificador.\n"))


class Escritura(Base):
    def test_sigla_sin_desarrollar_es_advertencia(self):
        inf = self.verificar(DOC_VALIDO + "\nEl sistema usa una API externa.\n")
        self.assertMensaje(inf.advertencias, r"la sigla API no se desarrolla")

    def test_sigla_desarrollada_pasa(self):
        doc = DOC_VALIDO + "\nEl sistema usa una interfaz de programación (API). La API responde rápido.\n"
        self.assertSinProblemas(self.verificar(doc))

    def test_punto_decimal_es_advertencia_con_coma(self):
        inf = self.verificar(DOC_VALIDO + "\nEl tiempo medio es 2.5 segundos.\n")
        self.assertMensaje(inf.advertencias, r"«2\.5»: usa coma decimal")

    def test_porcentaje_sin_espacio_es_advertencia(self):
        inf = self.verificar(DOC_VALIDO + "\nEl uso llega al 15%.\n")
        self.assertMensaje(inf.advertencias, r"falta un espacio antes de «%»")

    def test_oracion_larga_es_advertencia(self):
        larga = "La oración " + " ".join(["muy"] * 30) + " larga termina aquí."
        inf = self.verificar(DOC_VALIDO + f"\n{larga}\n")
        self.assertMensaje(inf.advertencias, r"oración de \d+ palabras \(máximo 25\)")

    def test_aviso_de_tipo_desconocido_es_advertencia(self):
        inf = self.verificar(DOC_VALIDO + "\n> **Importante.** Guarde antes de salir.\n")
        self.assertMensaje(inf.advertencias, r"aviso «Importante» fuera de los tipos")

    def test_aviso_valido_pasa(self):
        self.assertSinProblemas(self.verificar(DOC_VALIDO + "\n> **Nota.** Guarde antes de salir.\n"))


DOC_ESTADISTICO = """\
# Manual de prueba

# 1 Introducción

La Tabla 1 resume el análisis de varianza.

**Tabla 1.** Análisis de varianza del puntaje

| Fuente | gl | *F* | *p* |
|---|---|---|---|
| Entre grupos | 2 | 6,84 | {p} |
| Dentro de grupos | 117 | | |

*Nota.* {nota}

# 2 Uso

La Tabla 2 presenta las correlaciones.

**Tabla 2.** Correlaciones entre variables

| Variable | 1 | 2 |
|---|---|---|
| 1. Edad | — | |
| 2. Uso | {r} | — |

{nota_r}
"""


class TablasEstadisticas(Base):
    TABLAS = "\n  - anova\n  - correlacion"

    def doc(self, p=",002", nota="Datos de ejemplo; *p* = ,002.", r=",32\\*\\*", nota_r="*Nota.* \\*\\**p* < ,01."):
        return DOC_ESTADISTICO.format(p=p, nota=nota, r=r, nota_r=nota_r)

    def test_tablas_bien_formateadas_pasan(self):
        self.assertSinProblemas(self.verificar(self.doc(), tablas=self.TABLAS))

    def test_cero_inicial_en_columna_p_es_advertencia(self):
        inf = self.verificar(self.doc(p="0,002"), tablas=self.TABLAS)
        self.assertMensaje(inf.advertencias, r"0,002.*sin cero inicial")

    def test_cero_inicial_en_el_texto_es_advertencia(self):
        inf = self.verificar(self.doc(nota="Datos de ejemplo; *p* = 0,002."), tablas=self.TABLAS)
        self.assertMensaje(inf.advertencias, r"«p = 0,002».*sin cero inicial")

    def test_p_menor_que_con_cero_inicial_es_advertencia(self):
        inf = self.verificar(self.doc(p="< 0,001"), tablas=self.TABLAS)
        self.assertMensaje(inf.advertencias, r"< 0,001.*sin cero inicial")

    def test_separador_decimal_distinto_es_advertencia(self):
        inf = self.verificar(self.doc(p=".002"), tablas=self.TABLAS)
        self.assertMensaje(inf.advertencias, r"\.002.*separador decimal del prompt es la coma")

    def test_asteriscos_sin_nota_son_advertencia(self):
        inf = self.verificar(self.doc(nota_r="Fin del capítulo."), tablas=self.TABLAS)
        self.assertMensaje(inf.advertencias, r"asteriscos pero no tiene la nota")

    def test_sin_tablas_estadisticas_en_el_prompt_no_se_revisa(self):
        self.assertSinProblemas(self.verificar(self.doc(p="0,002", nota_r="Fin del capítulo.")))

    def test_tipos_no_estadisticos_no_activan_la_revision(self):
        self.assertSinProblemas(self.verificar(self.doc(p="0,002"), tablas="\n  - datos\n  - estado-arte"))


CITA_LARGA = ("La documentación técnica cumple su función cuando quien la lee puede actuar sin pedir ayuda: "
              "encuentra el dato que necesita, entiende el contexto en el que se aplica y comprueba por su cuenta "
              "que el resultado es el esperado. Por eso cada decisión de estilo debe poder justificarse frente a esa tarea concreta.")


class ElementosAcademicos(Base):
    def con(self, *componentes):
        return {"componentes": "".join(f"\n  - {c}" for c in componentes)}

    def test_nota_al_pie_sin_definicion_es_error(self):
        inf = self.verificar(DOC_VALIDO + "\nEl estudio fue breve[^1].\n")
        self.assertMensaje(inf.errores, r"\[\^1\] no tiene definición")

    def test_nota_al_pie_definida_sin_uso_es_advertencia(self):
        inf = self.verificar(DOC_VALIDO + "\n[^2]: Aclaración suelta.\n")
        self.assertMensaje(inf.advertencias, r"\[\^2\] está definida pero no se usa")

    def test_nota_al_pie_completa_pasa(self):
        self.assertSinProblemas(self.verificar(DOC_VALIDO + "\nEl estudio fue breve[^1].\n\n[^1]: Duró un mes.\n"))

    def test_cita_en_bloque_larga_pasa_y_no_cuenta_como_oracion_larga(self):
        self.assertSinProblemas(self.verificar(DOC_VALIDO + f"\nLa guía lo resume así:\n\n> {CITA_LARGA} (García y Pérez, 2021)\n", **self.con("cita_bloque")))

    def test_cita_en_bloque_corta_es_advertencia(self):
        inf = self.verificar(DOC_VALIDO + "\n> Una cita breve de pocas palabras.\n", **self.con("cita_bloque"))
        self.assertMensaje(inf.advertencias, r"cita en bloque de 6 palabras")

    def test_cita_larga_entre_comillas_es_advertencia(self):
        inf = self.verificar(DOC_VALIDO + f"\nLa guía dice «{CITA_LARGA}».\n", **self.con("cita_bloque"))
        self.assertMensaje(inf.advertencias, r"entre comillas: las de 40 o más van en bloque")

    def test_aviso_no_es_cita_en_bloque(self):
        self.assertSinProblemas(self.verificar(DOC_VALIDO + "\n> **Nota.** Guarde antes de salir.\n", **self.con("cita_bloque")))

    def test_hipotesis_salteada_es_error(self):
        inf = self.verificar(DOC_VALIDO + "\n**H1.** Primera.\n\n**H3.** Tercera.\n", **self.con("hipotesis"))
        self.assertMensaje(inf.errores, r"H3: la numeración no es continua; se esperaba H2")

    def test_hipotesis_con_nula_pasa(self):
        self.assertSinProblemas(self.verificar(DOC_VALIDO + "\n**H1.** Primera.\n\n**H0.** Nula.\n\n**H2.** Segunda.\n", **self.con("hipotesis")))

    def test_faltan_palabras_clave_es_advertencia(self):
        inf = self.verificar(DOC_VALIDO, **self.con("palabras_clave"))
        self.assertMensaje(inf.advertencias, r"falta la línea «\*\*Palabras clave:\*\*»")

    def test_palabras_clave_fuera_de_rango_es_advertencia(self):
        inf = self.verificar(DOC_VALIDO + "\n**Palabras clave:** uno; dos\n", **self.con("palabras_clave"))
        self.assertMensaje(inf.advertencias, r"2 palabras clave; deben ser de 3 a 5")

    def test_palabras_clave_con_comas_es_advertencia(self):
        inf = self.verificar(DOC_VALIDO + "\n**Palabras clave:** uno, dos, tres\n", **self.con("palabras_clave"))
        self.assertMensaje(inf.advertencias, r"se separan con punto y coma")

    def test_palabras_clave_correctas_pasan(self):
        self.assertSinProblemas(self.verificar(DOC_VALIDO + "\n**Palabras clave:** uno; dos; tres; cuatro\n", **self.con("palabras_clave")))

    def test_anexos_fuera_de_orden_es_error(self):
        doc = DOC_VALIDO + "\nVer Anexo A y Anexo C.\n\n# Anexos\n\n## Anexo A. Cuestionario\n\n## Anexo C. Consentimiento\n"
        self.assertMensaje(self.verificar(doc, **self.con("anexos")).errores, r"Anexo C: las letras no siguen el orden; se esperaba Anexo B")

    def test_anexo_no_mencionado_es_advertencia(self):
        doc = DOC_VALIDO + "\n# Anexos\n\n## Anexo A. Cuestionario\n"
        self.assertMensaje(self.verificar(doc, **self.con("anexos")).advertencias, r"Anexo A no se menciona")

    def test_anexos_correctos_pasan(self):
        doc = DOC_VALIDO + "\nEl cuestionario está en el Anexo A.\n\n# Anexos\n\n## Anexo A. Cuestionario\n"
        self.assertSinProblemas(self.verificar(doc, **self.con("anexos")))

    def test_sin_indices_con_tablas_y_figuras_es_advertencia(self):
        inf = self.verificar(DOC_VALIDO, **self.con("indices"))
        self.assertMensaje(inf.advertencias, r"tiene tablas pero no «Índice de tablas»")
        self.assertMensaje(inf.advertencias, r"tiene figuras pero no «Índice de figuras»")

    def test_componentes_sin_marcar_no_se_revisan(self):
        self.assertSinProblemas(self.verificar(DOC_VALIDO + "\n> Una cita breve.\n\n**H2.** Suelta.\n"))


class TablasTecnicas(Base):
    def tabla(self, cabecera, *filas):
        sep = "|" + "---|" * len(cabecera)
        cuerpo = "\n".join("| " + " | ".join(map(str, f)) + " |" for f in filas)
        return DOC_VALIDO + f"\nLa Tabla 2 resume los datos.\n\n**Tabla 2.** Datos técnicos\n\n| {' | '.join(cabecera)} |\n{sep}\n{cuerpo}\n"

    def con(self, *tipos):
        return {"tablas": "".join(f"\n  - {t}" for t in tipos)}

    ENDPOINTS = ("Método", "Ruta", "Descripción", "Respuestas")
    RIESGOS = ("Riesgo", "Probabilidad", "Impacto", "Nivel")
    TRAZA = ("Requisito", "Descripción", "Caso de prueba")

    def test_endpoints_correctos_pasan(self):
        doc = self.tabla(self.ENDPOINTS, ("`GET`", "`/api/cursos`", "Lista", "200"), ("`DELETE`", "`/api/cursos/{id}`", "Elimina", "204"))
        self.assertSinProblemas(self.verificar(doc, **self.con("endpoints")))

    def test_metodo_en_minusculas_o_inexistente_es_advertencia(self):
        inf = self.verificar(self.tabla(self.ENDPOINTS, ("`get`", "`/api`", "Lista", "200"), ("`FETCH`", "`/api`", "Trae", "200")), **self.con("endpoints"))
        self.assertMensaje(inf.advertencias, r"método «get»")
        self.assertMensaje(inf.advertencias, r"método «FETCH»")

    def test_riesgos_correctos_pasan(self):
        doc = self.tabla(self.RIESGOS, ("Caída", 3, 5, "15 (alto)"), ("Rotación", 2, 4, "8 (medio)"), ("Cambio", 1, 3, "3 (bajo)"))
        self.assertSinProblemas(self.verificar(doc, **self.con("riesgos")))

    def test_nivel_que_no_es_el_producto_es_advertencia(self):
        inf = self.verificar(self.tabla(self.RIESGOS, ("Caída", 3, 5, "12 (alto)")), **self.con("riesgos"))
        self.assertMensaje(inf.advertencias, r"nivel de riesgo 12: con probabilidad 3 e impacto 5 debería ser 15")

    def test_categoria_equivocada_es_advertencia(self):
        inf = self.verificar(self.tabla(self.RIESGOS, ("Rotación", 2, 4, "8 (alto)")), **self.con("riesgos"))
        self.assertMensaje(inf.advertencias, r"nivel 8 es «medio», no «alto»")

    def test_riesgos_desordenados_es_advertencia(self):
        inf = self.verificar(self.tabla(self.RIESGOS, ("Cambio", 1, 3, "3 (bajo)"), ("Caída", 3, 5, "15 (alto)")), **self.con("riesgos"))
        self.assertMensaje(inf.advertencias, r"no están ordenados de mayor a menor")

    def test_requisito_sin_caso_de_prueba_es_advertencia(self):
        inf = self.verificar(self.tabla(self.TRAZA, ("RF-001", "Exportar", "CP-012"), ("RF-002", "Anular", "—")), **self.con("trazabilidad"))
        self.assertMensaje(inf.advertencias, r"«RF-002» no tiene caso de prueba")

    def test_trazabilidad_completa_pasa(self):
        doc = self.tabla(self.TRAZA, ("RF-001", "Exportar", "CP-012"), ("RF-002", "Anular", "[PENDIENTE: caso de prueba]"))
        self.assertEqual(self.verificar(doc, **self.con("trazabilidad")).advertencias, [])

    def test_sin_tipos_tecnicos_no_se_revisa(self):
        self.assertSinProblemas(self.verificar(self.tabla(self.RIESGOS, ("Caída", 3, 5, "12 (bajo)"))))


class Pendientes(Base):
    def test_pendientes_se_cuentan(self):
        doc = DOC_VALIDO + "\n[PENDIENTE: dato del cliente]\n\nOtro [PENDIENTE: fecha].\n"
        inf = self.verificar(doc)
        self.assertEqual(len(inf.info), 2)

    def test_sin_pendientes_la_lista_esta_vacia(self):
        self.assertEqual(self.verificar(DOC_VALIDO).info, [])


class Memoria(Base):
    def memorias(self, agente=True, proyecto=True):
        a = vd.leer_memoria(self.escribir("agente.md", MEMORIA_AGENTE)) if agente else None
        p = vd.leer_memoria(self.escribir("decisiones-estilo.md", MEMORIA_PROYECTO)) if proyecto else None
        return {"DEC": a, "DP": p}

    def test_leer_memoria_devuelve_ids_y_estados(self):
        self.assertEqual(vd.leer_memoria(self.escribir("m.md", MEMORIA_AGENTE)), {"DEC-001": "confirmada", "DEC-002": "descartada"})
        self.assertIsNone(vd.leer_memoria(self.dir / "no-existe.md"))

    def test_ids_existentes_pasan(self):
        doc = DOC_VALIDO + "\nEl tratamiento sigue DEC-001 y los títulos, DP-001.\n"
        self.assertSinProblemas(self.verificar(doc, memorias=self.memorias()))

    def test_dec_inexistente_es_error(self):
        inf = self.verificar(DOC_VALIDO + "\nSegún DEC-099.\n", memorias=self.memorias())
        self.assertMensaje(inf.errores, r"se cita DEC-099, que no existe en la memoria del agente")

    def test_dp_inexistente_es_error(self):
        inf = self.verificar(DOC_VALIDO + "\n[PENDIENTE: estilo no definido, ver DP-004]\n", memorias=self.memorias())
        self.assertMensaje(inf.errores, r"se cita DP-004, que no existe en la memoria del proyecto")

    def test_dp_sin_memoria_de_proyecto_es_error(self):
        inf = self.verificar(DOC_VALIDO + "\nSegún DP-001.\n", memorias=self.memorias(proyecto=False))
        self.assertMensaje(inf.errores, r"se cita DP-001 pero no se encontró la memoria del proyecto")

    def test_dec_sin_memoria_del_agente_es_advertencia(self):
        inf = self.verificar(DOC_VALIDO + "\nSegún DEC-001.\n", memorias=self.memorias(agente=False))
        self.assertEqual(inf.errores, [])
        self.assertMensaje(inf.advertencias, r"no se encontró la memoria del agente")

    def test_id_descartado_es_advertencia(self):
        inf = self.verificar(DOC_VALIDO + "\nSegún DEC-002.\n", memorias=self.memorias())
        self.assertMensaje(inf.advertencias, r"DEC-002, que está descartada")

    def test_marcador_generico_no_se_comprueba(self):
        doc = DOC_VALIDO + "\n[PENDIENTE: estilo no definido, ver DEC-NNN]\n"
        inf = self.verificar(doc, memorias=self.memorias())
        self.assertEqual(inf.errores, [])


class Frontmatter(Base):
    def test_valores_entre_comillas_y_listas(self):
        datos, resto, saltadas = vd.leer_frontmatter('---\na: "x \\"y\\""\nb: \'it\'\'s\'\nc:\n  - uno\n  - dos\n---\nresto')
        self.assertEqual(datos, {"a": 'x "y"', "b": "it's", "c": ["uno", "dos"]})
        self.assertEqual(resto, "resto")
        self.assertEqual(saltadas, 7)


class LineaDeComandos(Base):
    def correr(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, encoding="utf-8")

    def test_documento_valido_sale_con_0(self):
        prompt = self.escribir("docs/prompt-estilo.md", PROMPT)
        self.escribir("docs/manual/doc.md", DOC_VALIDO)
        r = self.correr("--prompt", str(prompt), str(self.dir / "docs" / "manual"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Resultado: sin errores", r.stdout)

    def test_documento_con_errores_sale_con_1(self):
        prompt = self.escribir("docs/prompt-estilo.md", PROMPT)
        doc = self.escribir("docs/manual/doc.md", DOC_VALIDO + "\nVer la Tabla 5.\n")
        r = self.correr("--prompt", str(prompt), str(doc))
        self.assertEqual(r.returncode, 1)
        self.assertIn("se cita la Tabla 5", r.stdout)

    def test_memoria_del_proyecto_junto_al_prompt(self):
        prompt = self.escribir("docs/prompt-estilo.md", PROMPT)
        self.escribir("docs/decisiones-estilo.md", MEMORIA_PROYECTO)
        doc = self.escribir("docs/manual/doc.md", DOC_VALIDO + "\nSegún DP-001.\n")
        r = self.correr("--prompt", str(prompt), str(doc))
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_prompt_incompleto_sale_con_2(self):
        prompt = self.escribir("prompt.md", "---\ndocumento: X\n---\n")
        doc = self.escribir("doc.md", DOC_VALIDO)
        r = self.correr("--prompt", str(prompt), str(doc))
        self.assertEqual(r.returncode, 2)
        self.assertIn("le faltan los campos", r.stderr)

    def test_prompt_inexistente_sale_con_2(self):
        r = self.correr("--prompt", str(self.dir / "no.md"), str(self.dir))
        self.assertEqual(r.returncode, 2)


class EjesDeClasificacion(Base):
    def test_ejes_validos_no_dan_aviso(self):
        inf = self.verificar(DOC_VALIDO, proposito="instructivo", ambito="tecnico", lector="publico_general")
        self.assertSinProblemas(inf)

    def test_valor_de_eje_desconocido_es_advertencia(self):
        inf = self.verificar(DOC_VALIDO, lector="niños")
        self.assertEqual(inf.errores, [])
        self.assertMensaje(inf.advertencias, r"valor de eje desconocido: lector: niños")

    def test_valor_con_tilde_o_mayuscula_es_desconocido(self):
        # Se compara el identificador exacto, como lo escribe el configurador.
        inf = self.verificar(DOC_VALIDO, ambito="Técnico", lector="público general")
        self.assertMensaje(inf.advertencias, r"valor de eje desconocido: ambito: Técnico")
        self.assertMensaje(inf.advertencias, r"valor de eje desconocido: lector: público general")

    def test_prompt_viejo_sin_ejes_con_audiencia_no_cambia(self):
        self.assertSinProblemas(self.verificar(DOC_VALIDO, audiencia='"no técnica"'))
        self.assertSinProblemas(self.verificar(DOC_VALIDO))


class Configurador(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "node no está instalado")
    def test_script_del_configurador_es_javascript_valido(self):
        html = CONFIGURADOR.read_text(encoding="utf-8")
        codigo = "\n".join(re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S))
        self.assertTrue(codigo.strip(), "no se encontró código en el configurador")
        with tempfile.TemporaryDirectory() as tmp:
            js = Path(tmp) / "configurador.js"
            js.write_text(codigo, encoding="utf-8")
            r = subprocess.run(["node", "--check", str(js)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


@unittest.skipUnless(shutil.which("node"), "node no está instalado")
class EjesDelConfigurador(unittest.TestCase):
    """Ejecuta el configurador en Node (configurador_node.js) y revisa el prompt que genera."""

    @classmethod
    def setUpClass(cls):
        import json
        estados = {
            "nuevo": None,
            "divulgacion": {"proposito": "expositivo", "ambito": "cientifico", "lector": "publico_general"},
            "tecnico_expositivo": {"proposito": "expositivo", "ambito": "tecnico", "lector": "publico_general"},
            "institucional": {"proposito": "expositivo", "ambito": "institucional", "lector": "publico_general"},
            "viejo": {"tipo": "tesis", "metodologia": "academica", "audiencia": "académica"},
            "viejo_no_tecnico": {"tipo": "informe", "metodologia": "ninguna", "audiencia": "no técnica"},
            "desconocido": {"proposito": "expositivo", "ambito": "tecnico", "lector": "niños"},
            "constructor": {"proposito": "constructor", "ambito": "tecnico", "lector": "constructor"},
            "mixto": {"proposito": "mixto", "ambito": "profesional", "lector": "mixto"},
            "informe_academica": {"tipo": "informe", "audiencia": "académica"},
            "manual_tecnica": {"tipo": "manual", "audiencia": "técnica"},
            "manual_mixta": {"tipo": "manual", "audiencia": "mixta"},
            "narrativo": {"proposito": "narrativo", "ambito": "cientifico", "lector": "publico_general"},
            "especialista": {"lector": "especialista"},
        }
        r = subprocess.run(
            ["node", str(Path(__file__).with_name("configurador_node.js")), str(CONFIGURADOR), json.dumps(estados)],
            capture_output=True, text=True, encoding="utf-8")
        if r.returncode:
            raise AssertionError(r.stderr)
        cls.salida = json.loads(r.stdout)
        cls.salida.pop("__catalogo")

    def test_estado_por_defecto_escribe_los_tres_ejes_y_sus_reglas(self):
        p = self.salida["nuevo"]["prompt"]
        for linea in ("proposito: instructivo", "ambito: tecnico", "lector: publico_general"):
            self.assertIn("\n" + linea + "\n", p)
        self.assertNotIn("audiencia:", p)
        for regla in ("- Propósito instructivo:", "- Ámbito técnico:", "- Lector público general:"):
            self.assertIn(regla, p)
        # Un manual instructivo no recibe las reglas de divulgación.
        self.assertNotIn("**Divulgación**", p)
        self.assertNotIn("(texto de divulgación)", p)

    def test_cientifico_con_publico_general_y_expositivo_suma_divulgacion(self):
        p = self.salida["divulgacion"]["prompt"]
        self.assertIn("**Divulgación** (ámbito científico, lector público general y propósito expositivo)", p)
        self.assertIn("No simplifiques hasta volver falso un enunciado.", p)

    def test_tecnico_con_publico_general_y_expositivo_suma_divulgacion(self):
        p = self.salida["tecnico_expositivo"]["prompt"]
        self.assertIn("**Divulgación** (ámbito técnico, lector público general y propósito expositivo)", p)

    def test_institucional_con_publico_general_no_suma_divulgacion(self):
        self.assertNotIn("**Divulgación**", self.salida["institucional"]["prompt"])

    def test_tesis_vieja_se_migra_por_tipo(self):
        s = self.salida["viejo"]
        self.assertEqual((s["proposito"], s["ambito"], s["lector"]), ("argumentativo", "academico", "experto"))
        self.assertIn("\nlector: experto\n", s["prompt"])
        self.assertNotIn("audiencia:", s["prompt"])

    def test_informe_viejo_no_tecnico_se_migra_sin_divulgacion(self):
        s = self.salida["viejo_no_tecnico"]
        self.assertEqual((s["proposito"], s["ambito"], s["lector"]), ("analitico", "tecnico", "publico_general"))
        self.assertNotIn("**Divulgación**", s["prompt"])

    def test_valor_desconocido_vuelve_al_valor_por_defecto(self):
        for nombre in ("desconocido", "constructor"):
            s = self.salida[nombre]
            self.assertEqual(s["lector"], "publico_general", nombre)
            self.assertNotIn("undefined", s["prompt"], nombre)
        self.assertEqual(self.salida["constructor"]["proposito"], "instructivo")

    def test_lector_mixto_usa_la_frase_de_perfil_mixto(self):
        self.assertIn("para lectores de perfil mixto.", self.salida["mixto"]["prompt"])

    def test_audiencia_academica_en_informe_pasa_a_ambito_academico(self):
        s = self.salida["informe_academica"]
        self.assertEqual((s["ambito"], s["lector"]), ("academico", "experto"))

    def test_audiencia_tecnica_y_mixta_se_traducen_a_lector(self):
        self.assertEqual(self.salida["manual_tecnica"]["lector"], "experto")
        self.assertEqual(self.salida["manual_mixta"]["lector"], "mixto")

    def test_cientifico_con_publico_general_y_narrativo_suma_divulgacion(self):
        self.assertIn("**Divulgación** (ámbito científico, lector público general y propósito narrativo)",
                      self.salida["narrativo"]["prompt"])

    def test_lector_especialista(self):
        p = self.salida["especialista"]["prompt"]
        for texto in ("\nlector: especialista\n", "para un lector especialista de otra área", "- Lector especialista de otra área:"):
            self.assertIn(texto, p)
        self.assertNotIn("undefined", p)

    def test_las_reglas_emitidas_coinciden_con_escritura_md(self):
        referencia = (CONFIGURADOR.parents[1] / "references" / "escritura.md").read_text(encoding="utf-8")
        patron = re.compile(r"^- (Propósito|Ámbito|Lector) [^:\n]+: (.+)$", re.M)
        vistos = {"Propósito": set(), "Ámbito": set(), "Lector": set()}
        for nombre, s in self.salida.items():
            p = s["prompt"]
            for eje, texto in patron.findall(p):
                self.assertIn(texto, referencia, f"{nombre}: {eje}")
            vistos["Propósito"].add(s["proposito"]); vistos["Ámbito"].add(s["ambito"]); vistos["Lector"].add(s["lector"])
            if "**Divulgación**" in p:
                bloque = p.split("**Divulgación**", 1)[1].split("## 6.", 1)[0]
                reglas = re.findall(r"^- (.+)$", bloque, re.M)
                self.assertEqual(len(reglas), 3, nombre)
                for regla in reglas:
                    self.assertIn(regla, referencia, f"{nombre}: divulgación")
        self.assertEqual(vistos["Propósito"], set(vd.EJES["proposito"]))
        self.assertEqual(vistos["Ámbito"], set(vd.EJES["ambito"]))
        self.assertEqual(vistos["Lector"], set(vd.EJES["lector"]))

    def test_los_ejes_se_recuperan_al_reimportar(self):
        for nombre, s in self.salida.items():
            self.assertEqual({k: s["reimportado"][k] for k in ("proposito", "ambito", "lector")},
                             {k: s[k] for k in ("proposito", "ambito", "lector")}, nombre)


PROLOGO = "\n  - Prólogo\n  - Control de versiones"


class Prologo(Base):
    def doc(self, texto):
        return DOC_VALIDO.replace("# 1 Introducción", f"# Prólogo\n\n{texto}\n\n# 1 Introducción")

    def test_prologo_con_marcador_pasa(self):
        self.assertSinProblemas(self.verificar(self.doc("[PENDIENTE: texto del prologuista]"), sin_numerar=PROLOGO))

    def test_prologo_redactado_es_advertencia_y_no_error(self):
        inf = self.verificar(self.doc("Conocí al autor hace años y su obra me sorprendió."), sin_numerar=PROLOGO)
        self.assertEqual(inf.errores, [])
        self.assertMensaje(inf.advertencias, r"«Prólogo» tiene texto: el prólogo lo escribe otra persona")

    def test_prologo_al_final_del_documento_tambien_se_revisa(self):
        inf = self.verificar(DOC_VALIDO + "\n# Prólogo\n\nTexto escrito por el agente.\n", sin_numerar=PROLOGO)
        self.assertMensaje(inf.advertencias, r"«Prólogo» tiene texto")

    def test_prologo_con_marcador_en_cursiva_o_negrita_pasa(self):
        for texto in ("*[PENDIENTE: texto del prologuista]*", "**[PENDIENTE: texto del prologuista]**",
                      "_[PENDIENTE: texto del prologuista]_"):
            self.assertSinProblemas(self.verificar(self.doc(texto), sin_numerar=PROLOGO))

    def test_prologo_vacio_da_aviso(self):
        inf = self.verificar(self.doc(""), sin_numerar=PROLOGO)
        self.assertEqual(inf.errores, [])
        self.assertMensaje(inf.advertencias, r"«Prólogo» está vacía")

    def test_prologo_con_otro_pendiente_da_aviso(self):
        inf = self.verificar(self.doc("[PENDIENTE: completar]"), sin_numerar=PROLOGO)
        self.assertMensaje(inf.advertencias, r"«Prólogo» tiene texto")

    def test_prologo_sin_numerar_por_defecto(self):
        # «Prólogo» está en SIN_NUMERAR_BASE: no hace falta declararlo en sin_numerar.
        self.assertSinProblemas(self.verificar(self.doc("[PENDIENTE: texto del prologuista]")))

    def test_partes_nuevas_sin_numerar_por_defecto(self):
        for nombre in ("Prefacio", "Prólogo", "Epígrafe", "Índice alfabético", "Colofón"):
            self.assertIn(vd.normalizar(nombre), vd.SIN_NUMERAR_BASE, nombre)

    def test_prefacio_redactado_no_da_aviso(self):
        doc = DOC_VALIDO.replace("# 1 Introducción", "# Prefacio\n\nEscribí este manual para el equipo.\n\n# 1 Introducción")
        self.assertSinProblemas(self.verificar(doc, sin_numerar="\n  - Prefacio"))


@unittest.skipUnless(shutil.which("node"), "node no está instalado")
class ZonasDelConfigurador(unittest.TestCase):
    """Estructura en tres zonas (references/escritura.md, §4 ter): una prueba por fila de la matriz del spec."""

    VIEJO = {"estructura": "Control de versiones\nResumen\nIntroducción\nGlosario\nDesarrollo\nReferencias\nAnexos",
             "sin_numerar": "Control de versiones\nResumen\nGlosario\nReferencias\nAnexos"}

    @classmethod
    def setUpClass(cls):
        import json
        estados = {
            "nuevo": None,
            "academica": {"metodologia": "academica", "__acciones": [["esqueleto"]]},
            "orden": {"metodologia": "academica", "__acciones": [["esqueleto"], ["mover", "pre", "Abstract", -1]]},
            "propio": {"__acciones": [["propio", "pre", "Lista de símbolos", "Cada símbolo con su significado y unidad."], ["propio", "pre", "  ", "Sin nombre"]]},
            "prologo": {"__acciones": [["alternar", "pre", "Prólogo", True], ["alternar", "pre", "Prefacio", True], ["alternar", "pre", "Portada", True]]},
            "viejo": cls.VIEJO,
            "en_medio": {"estructura": "Introducción\nGlosario\nDesarrollo", "sin_numerar": "Glosario"},
            "en_medio_pre": {"estructura": "Introducción\nResumen\nApéndice de datos\nDesarrollo",
                             "sin_numerar": "Resumen\nApéndice de datos"},
            "sin_titulo": {"__acciones": [["alternar", "pre", "Dedicatoria", True], ["alternar", "pre", "Epígrafe", True],
                                          ["alternar", "pre", "Portada", True], ["alternar", "pre", "Índice general", True]]},
            "control_primero": {"__acciones": [["alternar", "pre", "Portada", True], ["alternar", "pre", "Control de versiones", False],
                                               ["alternar", "pre", "Control de versiones", True]]},
            "quitar": {"__acciones": [["propio", "post", "Fe de erratas", "Correcciones."], ["quitar", "post", "Fe de erratas"]]},
            "invalido": {"pretextuales": ["Control de versiones"], "textual": "Introducción", "postextuales": [],
                         "formato_zonas": {"pre": {"paginacion": "griega", "pagina_nueva": "si"}, "textual": "x", "epigrafe": {"estilo": 3}},
                         "propios": [None, "texto", {"zona": "medio", "nombre": "X"}, {"zona": "pre", "nombre": "  "},
                                     {"zona": "post", "nombre": " Fe de erratas ", "regla": 5}]},
            "epigrafe": {"formato_zonas": {"epigrafe": {"alineacion": "izquierda", "estilo": "normal"}},
                         "__acciones": [["alternar", "pre", "Epígrafe", True]]},
            "dos_zonas": {"__acciones": [["propio", "pre", "Notas", "Aclaraciones."], ["propio", "post", "notas", "Otra."],
                                         ["propio", "pre", "Glosario", "Repetido."], ["alternar", "post", "Glosario", False],
                                         ["propio", "pre", "Glosario", "Glosario al comienzo."], ["alternar", "post", "Glosario", True]]},
            "tuberia": {"__acciones": [["propio", "pre", "Uso A|B", "Columna a|b."]], "textual": "Introducción\nEntrada|salida"},
            "duplicado": {"pretextuales": ["Control de versiones"], "textual": "Introducción\nGlosario\nUso\nUso",
                          "postextuales": ["Glosario"]},
            "capitulos": {"__acciones": [["capitulos", ["Portada", "Control de versiones", "Introducción", "Glosario", "Uso", "Bibliografía", "Colofón"]]]},
            "formato": {"formato_zonas": {"pre": {"paginacion": "arabiga", "pagina_nueva": False}, "dedicatoria": {"alineacion": "centro", "estilo": "normal"}},
                        "__acciones": [["alternar", "pre", "Dedicatoria", True]]},
        }
        r = subprocess.run(
            ["node", str(Path(__file__).with_name("configurador_node.js")), str(CONFIGURADOR), json.dumps(estados)],
            capture_output=True, text=True, encoding="utf-8")
        if r.returncode:
            raise AssertionError(r.stderr)
        cls.salida = json.loads(r.stdout)
        cls.catalogo = cls.salida.pop("__catalogo")
        cls.sin_numerar_base = cls.catalogo.pop("sin_numerar_base")
        cls.catalogo.pop("plantillas")
        cls.catalogo.pop("componentes_plantilla")

    def z(self, nombre):
        return self.salida[nombre]["zonas"]

    def seccion(self, nombre, titulo):
        p = self.salida[nombre]["prompt"]
        return p.split(f"### {titulo}", 1)[1].split("\n### ", 1)[0].split("\n## ", 1)[0]

    def fm(self, nombre, clave):
        datos, _, _ = vd.leer_frontmatter(self.salida[nombre]["prompt"])
        return datos.get(clave)

    def test_nuevo_reparte_el_esqueleto_y_deriva_lo_mismo_que_0_12(self):
        z = self.z("nuevo")
        self.assertEqual(z["pretextuales"], ["Control de versiones"])
        self.assertEqual(z["postextuales"], ["Glosario"])
        self.assertEqual(z["textual"].split("\n")[0], "Introducción")
        self.assertEqual(self.fm("nuevo", "estructura"), [
            "Control de versiones", "Introducción", "Primeros pasos", "Tareas frecuentes", "Referencia de la interfaz",
            "Conceptos", "Solución de problemas", "Preguntas frecuentes", "Glosario"])
        self.assertEqual(self.fm("nuevo", "sin_numerar"), ["Control de versiones", "Glosario"])
        self.assertEqual(self.fm("nuevo", "pretextuales"), ["Control de versiones"])
        self.assertEqual(self.fm("nuevo", "postextuales"), ["Glosario"])

    def test_formato_por_defecto(self):
        esperado = {"paginacion_pretextual": "romana", "paginacion_textual": "arabiga", "paginacion_postextual": "arabiga",
                    "pagina_nueva_pretextual": "si", "pagina_nueva_textual": "si", "pagina_nueva_postextual": "si",
                    "dedicatoria_alineacion": "derecha", "dedicatoria_estilo": "cursiva",
                    "epigrafe_alineacion": "derecha", "epigrafe_estilo": "cursiva"}
        for clave, valor in esperado.items():
            self.assertEqual(self.fm("nuevo", clave), valor, clave)
        self.assertIn("### Pretextuales (sin número, paginación romana, cada elemento en página nueva)", self.salida["nuevo"]["prompt"])

    def test_esqueleto_academico(self):
        z = self.z("academica")
        self.assertEqual(z["pretextuales"], ["Control de versiones", "Resumen", "Abstract", "Índice general"])
        self.assertEqual(z["postextuales"], ["Referencias", "Anexos"])
        self.assertNotIn("Resumen", z["textual"])

    def test_orden_cambia_pretextuales_y_estructura(self):
        self.assertEqual(self.z("orden")["pretextuales"], ["Control de versiones", "Abstract", "Resumen", "Índice general"])
        self.assertEqual(self.fm("orden", "estructura")[:4], ["Control de versiones", "Abstract", "Resumen", "Índice general"])
        pre = self.seccion("orden", "Pretextuales")
        self.assertLess(pre.index("| Abstract |"), pre.index("| Resumen |"))

    def test_elemento_propio_con_su_regla(self):
        s = self.salida["propio"]
        self.assertEqual(s["resultados"], [True, False])  # sin nombre no se agrega
        self.assertEqual(s["zonas"]["pretextuales"], ["Control de versiones", "Lista de símbolos"])
        self.assertIn("| Lista de símbolos | Cada símbolo con su significado y unidad. |", self.seccion("propio", "Pretextuales"))
        self.assertIn("Lista de símbolos", self.fm("propio", "sin_numerar"))
        self.assertNotIn("Sin nombre", s["prompt"])

    def test_prologo_lo_escribe_otra_persona(self):
        pre = self.seccion("prologo", "Pretextuales")
        self.assertIn("| Prólogo | Lo escribe otra persona: deja `[PENDIENTE: texto del prologuista]` y nunca lo redactes. |", pre)
        self.assertIn("| Prefacio | Lo escribe el autor", pre)
        self.assertLess(pre.index("| Prefacio |"), pre.index("| Prólogo |"))
        self.assertIn("La sección «Prólogo» solo tiene `[PENDIENTE: texto del prologuista]`.", self.salida["prologo"]["prompt"])
        self.assertNotIn("Prólogo", self.salida["nuevo"]["prompt"].split("<!--")[0])

    def test_control_de_versiones_sigue_primero_al_marcar_portada(self):
        self.assertEqual(self.z("prologo")["pretextuales"], ["Control de versiones", "Portada", "Prefacio", "Prólogo"])

    def test_configuracion_vieja_se_reparte_en_zonas(self):
        z = self.z("viejo")
        self.assertEqual(z["pretextuales"], ["Control de versiones", "Resumen"])
        self.assertEqual(z["textual"], "Introducción\nDesarrollo")
        self.assertEqual(z["postextuales"], ["Glosario", "Referencias", "Anexos"])
        self.assertEqual(self.fm("viejo", "estructura"), [
            "Control de versiones", "Resumen", "Introducción", "Desarrollo", "Glosario", "Referencias", "Anexos"])
        self.assertIn("Glosario", self.salida["viejo"]["aviso_importar"])

    def test_sin_numero_en_medio_va_a_postextual_con_aviso(self):
        s = self.salida["en_medio"]
        self.assertEqual(s["zonas"]["pretextuales"], [])
        self.assertEqual(s["zonas"]["textual"], "Introducción\nDesarrollo")
        self.assertEqual(s["zonas"]["postextuales"], ["Glosario"])
        self.assertEqual(self.fm("en_medio", "sin_numerar"), ["Glosario"])
        self.assertRegex(s["aviso_importar"], r"Se movieron a su zona .*: Glosario$")
        self.assertIn("| 1 Introducción |", self.seccion("en_medio", "Textuales"))
        self.assertIn("| 2 Desarrollo |", self.seccion("en_medio", "Textuales"))
        self.assertEqual(self.salida["nuevo"]["aviso_importar"], "")

    def test_sin_numero_en_medio_va_a_su_zona_o_a_post_como_propio(self):
        z = self.z("en_medio_pre")
        self.assertEqual(z["pretextuales"], ["Resumen"])
        self.assertEqual(z["postextuales"], ["Apéndice de datos"])
        self.assertEqual(z["textual"], "Introducción\nDesarrollo")
        self.assertIn({"zona": "post", "nombre": "Apéndice de datos", "regla": ""}, z["propios"])
        self.assertTrue(self.salida["en_medio_pre"]["aviso_importar"].endswith("; sin regla: Apéndice de datos"))

    def test_textual_nunca_figura_en_sin_numerar(self):
        for nombre, s in self.salida.items():
            sin_numerar = {vd.normalizar(x) for x in s["zonas"]["sin_numerar"].split("\n") if x}
            zonas = {vd.normalizar(x) for x in s["zonas"]["pretextuales"] + s["zonas"]["postextuales"]}
            self.assertEqual(sin_numerar, zonas, nombre)

    def test_usar_capitulos_reparte_con_la_misma_regla(self):
        s = self.salida["capitulos"]
        z = s["zonas"]
        self.assertEqual(z["pretextuales"], ["Control de versiones", "Portada"])
        self.assertEqual(z["textual"], "Introducción\nUso")
        self.assertEqual(z["postextuales"], ["Glosario", "Bibliografía", "Colofón"])
        self.assertRegex(s["resultados"][0], r"Se movieron a su zona .*: Glosario$")
        self.assertNotIn("Portada", self.fm("capitulos", "estructura"))

    def test_sin_titulo_no_entra_en_estructura(self):
        z = self.z("sin_titulo")
        self.assertEqual(z["pretextuales"], ["Control de versiones", "Portada", "Dedicatoria", "Epígrafe", "Índice general"])
        estructura = self.fm("sin_titulo", "estructura")
        for nombre in ("Portada", "Dedicatoria", "Epígrafe"):
            self.assertNotIn(nombre, estructura)
        self.assertIn("Índice general", estructura)
        self.assertEqual(self.fm("sin_titulo", "pretextuales"), z["pretextuales"])
        pre = self.seccion("sin_titulo", "Pretextuales")
        self.assertIn("| Dedicatoria | Una o dos líneas del autor, sin título. |", pre)
        self.assertIn("| Epígrafe | Cita breve con su autor, sin título. |", pre)

    def test_sin_titulo_el_verificador_no_exige_su_h1(self):
        datos, _, _ = vd.leer_frontmatter(self.salida["sin_titulo"]["prompt"])
        caps = [c for c in datos["estructura"]]
        sin_num = {vd.normalizar(x) for x in datos["sin_numerar"]}
        cuerpo, n = [], 0
        for c in caps:
            if vd.normalizar(c) in sin_num:
                cuerpo.append(f"# {c}\n\nTexto de la parte.\n")
            else:
                n += 1
                cuerpo.append(f"# {n} {c}\n\nTexto del capítulo.\n")
        doc = f"# {datos['documento']}\n\n*Para mi familia.*\n\n" + "\n".join(cuerpo)
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "doc.md"
            ruta.write_text(doc, encoding="utf-8")
            inf = vd.Informe()
            vd.verificar(datos, [ruta], inf)
        self.assertEqual(inf.errores, [])

    def test_control_de_versiones_vuelve_a_primero(self):
        self.assertEqual(self.z("control_primero")["pretextuales"], ["Control de versiones", "Portada"])
        self.assertEqual(self.catalogo["pre"][0]["nombre"], "Control de versiones")

    def test_sin_numerar_base_igual_en_el_configurador_y_el_verificador(self):
        self.assertEqual(set(self.sin_numerar_base), vd.SIN_NUMERAR_BASE)

    def test_encabezado_pretextual_con_formato_elegido(self):
        self.assertIn("### Pretextuales (sin número, paginación arábiga, sin salto de página entre uno y otro)",
                      self.salida["formato"]["prompt"])

    def test_alineacion_y_estilo_del_epigrafe(self):
        self.assertIn("El epígrafe va a la izquierda, en redonda.", self.seccion("epigrafe", "Pretextuales"))

    def test_un_nombre_esta_en_una_sola_zona(self):
        s = self.salida["dos_zonas"]
        self.assertEqual(s["resultados"][:4], [True, False, False, None])  # «notas» y «Glosario» ya están en una zona
        self.assertTrue(s["resultados"][4])  # sin Glosario en post, se puede agregar en pre
        self.assertEqual(s["zonas"]["pretextuales"], ["Control de versiones", "Notas"])  # marcarlo en post lo saca de pre
        self.assertEqual(s["zonas"]["postextuales"], ["Glosario"])

    def test_quitar_propio(self):
        z = self.z("quitar")
        self.assertEqual(z["postextuales"], ["Glosario"])
        self.assertEqual(z["propios"], [])
        self.assertNotIn("Fe de erratas", self.salida["quitar"]["prompt"].split("<!--")[0])

    def test_formato_y_propios_invalidos_vuelven_al_valor_por_defecto(self):
        z = self.z("invalido")
        self.assertEqual(z["formato_zonas"], self.z("nuevo")["formato_zonas"])
        self.assertEqual(z["propios"], [{"zona": "post", "nombre": "Fe de erratas", "regla": "5"}])

    def test_nombre_con_barra_no_rompe_la_tabla(self):
        pre = self.seccion("tuberia", "Pretextuales")
        self.assertIn("| Uso A\\|B | Columna a\\|b. |", pre)
        self.assertIn("| 2 Entrada\\|salida |", self.seccion("tuberia", "Textuales"))

    def test_duplicados_entre_textual_y_zonas_gana_la_zona(self):
        self.assertEqual(self.fm("duplicado", "estructura"), ["Control de versiones", "Introducción", "Uso", "Glosario"])
        txt = self.seccion("duplicado", "Textuales")
        self.assertNotIn("Glosario", txt)
        self.assertIn("| 2 Uso |", txt)
        self.assertNotIn("| 3 ", txt)

    def test_editar_las_zonas_marca_la_estructura_como_editada(self):
        for nombre in ("orden", "propio", "prologo", "quitar", "control_primero"):
            self.assertTrue(self.salida[nombre]["editada"], nombre)
        self.assertFalse(self.salida["nuevo"]["editada"])
        self.assertFalse(self.salida["academica"]["editada"])

    def test_formato_elegido_y_dedicatoria(self):
        self.assertEqual(self.fm("formato", "paginacion_pretextual"), "arabiga")
        self.assertEqual(self.fm("formato", "pagina_nueva_pretextual"), "no")
        self.assertEqual(self.fm("formato", "dedicatoria_alineacion"), "centro")
        self.assertEqual(self.fm("formato", "epigrafe_estilo"), "cursiva")  # lo no indicado queda por defecto
        self.assertIn("La dedicatoria va centrada, en redonda.", self.seccion("formato", "Pretextuales"))

    def test_reimportar_recupera_las_zonas_y_su_formato(self):
        for nombre, s in self.salida.items():
            self.assertEqual(s["reimportado"]["zonas"], s["zonas"], nombre)

    def test_reglas_del_catalogo_estan_en_escritura_md(self):
        referencia = (CONFIGURADOR.parents[1] / "references" / "escritura.md").read_text(encoding="utf-8")
        for zona, elementos in self.catalogo.items():
            for e in elementos:
                self.assertIn(f"| {e['nombre']} | {e['regla']} |", referencia, f"{zona}: {e['nombre']}")
        self.assertEqual(self.catalogo["pre"][0]["nombre"], "Control de versiones")

    def test_tabla_textual_sigue_numerada(self):
        txt = self.seccion("nuevo", "Textuales")
        self.assertIn("| 1 Introducción |", txt)
        self.assertNotIn("Control de versiones", txt)
        self.assertNotIn("Glosario", txt)


if __name__ == "__main__":
    unittest.main()


@unittest.skipUnless(shutil.which("node"), "node no está instalado")
class PlantillasDelConfigurador(Base):
    """Plantillas como punto de partida (0.14.0): cada una fija ejes, zonas, componentes propios y presentación,
    y cada componente propio llega a la vista previa, al prompt y, si se puede revisar, al verificador."""

    PLANTILLAS = ["trabajo-campo-unc", "informe-especificacion", "informe-auditoria", "proforma-entrevista", "ficha-1pager", "arquitectura-presentacion"]

    @classmethod
    def setUpClass(cls):
        import json
        estados = {p: {"__acciones": [["plantilla", p]]} for p in cls.PLANTILLAS}
        estados.update({
            "sin_plantilla": {"__acciones": [["plantilla", "proforma-entrevista"], ["plantilla", ""]]},
            "titulo_propio": {"documento": "Mi informe", "__acciones": [["plantilla", "informe-auditoria"]]},
            "cambio": {"__acciones": [["plantilla", "proforma-entrevista"], ["plantilla", "ficha-1pager"]]},
            "vieja": {"plantilla": "proforma-entrevista", "componentes_plantilla": ["agenda", "inventado", "agenda"]},
            "desconocida": {"plantilla": "otra", "componentes_plantilla": ["agenda"]},
            "ver_todo": {"ver_todo": True},
            "niveles": {"__acciones": [["formato", "textual", "niveles", 2]]},
            "sin_numero": {"__acciones": [["formato", "textual", "numeracion", "ninguna"]]},
            "preajuste": {"__acciones": [["plantilla", "ficha-1pager"]]},
        })
        r = subprocess.run(
            ["node", str(Path(__file__).with_name("configurador_node.js")), str(CONFIGURADOR), json.dumps(estados)],
            capture_output=True, text=True, encoding="utf-8")
        if r.returncode:
            raise AssertionError(r.stderr)
        cls.salida = json.loads(r.stdout)
        cls.catalogo = cls.salida.pop("__catalogo")

    def prompt(self, nombre):
        datos, _, _ = vd.leer_frontmatter(self.salida[nombre]["prompt"])
        return datos

    def revisar(self, plantilla, doc):
        inf = vd.Informe()
        vd.verificar(self.prompt(plantilla), [self.escribir("doc.md", doc)], inf)
        return inf

    # --- Configurador ---

    def test_cada_plantilla_fija_ejes_zonas_componentes_y_presentacion(self):
        for p in self.PLANTILLAS:
            with self.subTest(p):
                d = self.prompt(p)
                def_ = self.catalogo["plantillas"][p]
                self.assertEqual(d["plantilla"], f"references/plantillas/{p}.md")
                self.assertEqual(d["tipo"], def_["ejes"]["tipo"])
                self.assertEqual(d["proposito"], def_["ejes"]["proposito"])
                self.assertEqual(d["componentes_plantilla"], def_["propios"])
                self.assertEqual(self.salida[p]["zonas"]["textual"].split("\n"), def_["textual"])
                self.assertIn("Componentes propios de la plantilla " + def_["nombre"], self.salida[p]["prompt"])
                self.assertNotIn("[PENDIENTE: propósito]", self.salida[p]["prompt"])

    def test_cada_componente_tiene_ejemplo_regla_y_esta_en_su_plantilla(self):
        comps = self.catalogo["componentes_plantilla"]
        usados = {c for p in self.catalogo["plantillas"].values() for c in p["propios"]}
        self.assertEqual(usados, set(comps))
        for p in self.PLANTILLAS:
            prompt = self.salida[p]["prompt"]
            for k in self.catalogo["plantillas"][p]["propios"]:
                self.assertIn(f"- **{comps[k]['nombre']}**: {comps[k]['regla']}", prompt)
        vista = self.salida["ver_todo"]["vista"]
        for c in comps.values():
            self.assertIn(f">{c['nombre']}</h3>", vista)

    def test_las_reglas_estan_en_la_referencia_de_cada_plantilla(self):
        for p, def_ in self.catalogo["plantillas"].items():
            ref = (RAIZ / "skills" / "documentacion-estilo" / "references" / "plantillas" / f"{p}.md").read_text(encoding="utf-8")
            for k in def_["propios"]:
                with self.subTest(p=p, componente=k):
                    self.assertIn(self.catalogo["componentes_plantilla"][k]["regla"], ref)

    def test_la_vista_previa_muestra_los_componentes_de_su_plantilla(self):
        marcas = {"trabajo-campo-unc": ["portada-unc", "Documento fuente:", "<b>Tabla 1</b><br>"],
                  "informe-especificacion": ["datos-doc", "<b>Sistema:</b>"],
                  "informe-auditoria": ["ficha-corrida", "estado parcial", "Para completar:", "certeza confirmado"],
                  "proforma-entrevista": ["cap barra", "linea-respuesta", "Tiempo total"],
                  "ficha-1pager": ["pastilla", "intencion", "uso-si", "columnas"],
                  "arquitectura-presentacion": ["lamina", "antetitulo", "tarjeta", "#FFF4D6"]}
        for p, ms in marcas.items():
            for m in ms:
                with self.subTest(p=p, marca=m):
                    self.assertIn(m, self.salida[p]["vista"])
        self.assertNotIn("linea-respuesta", self.salida["trabajo-campo-unc"]["vista"])

    def test_sin_plantilla_no_deja_componentes_ni_normas(self):
        s = self.salida["sin_plantilla"]
        self.assertEqual((s["plantilla"], s["componentes_plantilla"]), ("", []))
        self.assertNotIn("componentes_plantilla", self.prompt("sin_plantilla"))
        self.assertNotIn("plantilla", self.prompt("sin_plantilla"))
        self.assertNotIn("Componentes propios", s["prompt"])

    def test_el_titulo_del_usuario_no_se_reemplaza(self):
        self.assertEqual(self.prompt("titulo_propio")["documento"], "Mi informe")
        self.assertEqual(self.prompt("cambio")["documento"], "Patrón State")

    def test_cambiar_de_plantilla_reemplaza_sus_componentes(self):
        self.assertEqual(self.prompt("cambio")["componentes_plantilla"], self.catalogo["plantillas"]["ficha-1pager"]["propios"])

    def test_configuracion_vieja_o_desconocida_se_depura(self):
        self.assertEqual(self.salida["vieja"]["componentes_plantilla"], ["agenda"])
        self.assertEqual((self.salida["desconocida"]["plantilla"], self.salida["desconocida"]["componentes_plantilla"]), ("", ["agenda"]))

    def test_se_recupera_al_reimportar(self):
        for p in self.PLANTILLAS:
            self.assertEqual(self.salida[p]["reimportado"]["zonas"], self.salida[p]["zonas"])

    def test_numeracion_ninguna_pasa_la_zona_textual_a_sin_numerar(self):
        d = self.prompt("sin_numero")
        self.assertEqual(d["numeracion_textual"], "ninguna")
        self.assertIn("Introducción", d["sin_numerar"])
        self.assertNotIn("niveles_numerados", d)
        self.assertIn("Ningún capítulo lleva número", self.salida["sin_numero"]["prompt"])
        self.assertIn("| Introducción |", self.salida["sin_numero"]["prompt"])

    def test_niveles_numerados(self):
        d = self.prompt("niveles")
        self.assertEqual(d["niveles_numerados"], "2")
        self.assertIn("`### Subsección` (desde el nivel 3, sin número)", self.salida["niveles"]["prompt"])
        self.assertEqual(self.prompt("nuevo" if "nuevo" in self.salida else "niveles")["numeracion_textual"], "decimal")

    # --- Verificador: un documento correcto por plantilla y errores sembrados ---

    TDC = textwrap.dedent("""\
        # Trabajo de campo: práctica profesional

        # Control de versiones

        Sin cambios.

        # Índice general

        Índice generado.

        # 1 Estructura del documento

        - **Calidad de proceso:** que la forma de trabajo se pueda repetir.

        **Documento fuente: *Plan de trabajo v1.0*.**

        # 2 Planeamiento del proyecto

        Texto.

        **Documento fuente: [PENDIENTE: documento fuente].**

        # 3 Acta de acuerdos

        Texto.

        **Documento fuente: *Acta 1*.**

        # 4 Cronograma de aproximación

        Texto.

        **Documento fuente: *Cronograma*.**

        # Referencias

        Ninguna.

        # Anexos

        Ninguno.
        """)

    def test_trabajo_de_campo_valido_pasa(self):
        self.assertSinProblemas(self.revisar("trabajo-campo-unc", self.TDC))

    def test_trabajo_de_campo_sin_documento_fuente_y_dos_puntos_afuera(self):
        doc = self.TDC.replace("**Documento fuente: *Acta 1*.**", "Documento fuente: Acta 1.").replace("**Calidad de proceso:**", "**Calidad de proceso**:")
        inf = self.revisar("trabajo-campo-unc", doc)
        self.assertMensaje(inf.advertencias, "«acta de acuerdos» no cierra con «\\*\\*Documento fuente")
        self.assertMensaje(inf.advertencias, "dos puntos del término van dentro de la negrita")

    INFORME = textwrap.dedent("""\
        # Informe de relevamiento y diseño de arquitectura

        **Sistema:** Sistema de Gestión Académica

        **Documento:** Especificación de requisitos

        **Estado:** Borrador

        # Control de versiones

        Sin cambios.

        # 1 Introducción

        ## 1.1 Propósito

        ### Estudiante (Alumno)

        - **Cohesión transaccional:** las operaciones se confirman juntas.

        # 2 Descripción general

        Texto.

        # 3 Requisitos específicos

        Texto.

        # 4 Trazabilidad

        Texto.

        # Apéndices

        Ninguno.
        """)

    def test_informe_tecnico_valido_pasa_con_h3_sin_numero(self):
        self.assertSinProblemas(self.revisar("informe-especificacion", self.INFORME))

    def test_informe_tecnico_sin_datos_del_documento(self):
        inf = self.revisar("informe-especificacion", self.INFORME.replace("**Estado:** Borrador", ""))
        self.assertMensaje(inf.advertencias, "falta «\\*\\*Estado:\\*\\*»")

    def test_h3_sin_numero_es_error_con_tres_niveles(self):
        inf = self.verificar("# 1 Introducción\n\n## 1.1 Propósito\n\n### Estudiante\n", estructura="\n  - Introducción", niveles_numerados=3)
        self.assertMensaje(inf.errores, "título sin numeración decimal: «Estudiante»")

    AUDITORIA = textwrap.dedent("""\
        # Informe de completitud

        **Commit:** `79bbf4b` · **Fecha:** 31/10/2026 · **Corte:** primera entrega · **Modo:** completo

        **Rama:** main · **Estado del repositorio:** limpio

        **Criterio:** consigna de la primera entrega.

        # Resumen de la revisión

        El entregable cumple casi toda la consigna. La Tabla 1 resume cada punto.

        **Tabla 1.** Completitud por punto

        | Punto | Estado | Completitud | Lo principal que falta |
        |---|---|---|---|
        | 1 · Visión | Completo | 100 % | — |
        | 2 · Requisitos | Parcial | 60 % | Criterios de aceptación |

        # Detalle por punto

        ### 2 · Requisitos — Parcial (60 %)

        Archivo: `docs/02-requisitos.md`

        La Tabla 2 muestra los criterios.

        **Tabla 2.** Criterios del punto

        | Criterio | ¿Cumple? | Evidencia |
        |---|---|---|
        | Historias con criterios | Parcial | 8 de 12 historias (02:40-118) |
        | Requisitos medibles | No | — |

        **Observaciones de *requisitos*:** el formato es uniforme `CONFIRMADO`.

        **Para completar:** agregar los criterios que faltan.
        """)

    def test_auditoria_valida_pasa(self):
        self.assertSinProblemas(self.revisar("informe-auditoria", self.AUDITORIA))

    def test_auditoria_con_errores_sembrados(self):
        doc = (self.AUDITORIA.replace("| Completo | 100 % |", "| Completo | 90 % |").replace("| Parcial | 60 % | Criterios", "| A medias | 60 % | Criterios")
               .replace("| Parcial | 8 de 12 historias (02:40-118) |", "| Parcial | 8 de 12 historias |").replace("| No | — |", "| Tal vez | — |")
               .replace("**Para completar:** agregar los criterios que faltan.", "").replace("Archivo: `docs/02-requisitos.md`", "")
               .replace("— Parcial (60 %)", "(60 %)").replace("`79bbf4b`", "79bbf4b"))
        inf = self.revisar("informe-auditoria", doc)
        for patron in ("Completo es siempre 100 %", "estado «A medias»", "no cita el lugar exacto", "«¿Cumple\\?» es «Tal vez»",
                       "no tiene el párrafo «\\*\\*Para completar", "falta la línea «Archivo", "título del punto debe ser", "commit de la ficha de corrida va en código"):
            self.assertMensaje(inf.advertencias, patron)

    PROFORMA = textwrap.dedent("""\
        # Proforma de entrevista

        # 1. Datos de la entrevista

        La Tabla 1 tiene los datos.

        **Tabla 1.** Datos de la entrevista

        | Campo | Dato |
        |---|---|
        | Fecha | ___ / ___ / ______ |

        # 2. Objetivos

        - Conocer la misión del área.

        # 3. Agenda y control de tiempos

        La Tabla 2 es la agenda.

        **Tabla 2.** Agenda

        | Bloque | Tema | Tiempo estimado | Tiempo real | Tiempo total |
        |---|---|---|---|---|
        | 1 | Apertura | 5 min | | |
        | 2 | Misión | 15 min | | |
        | **Tiempo total** | | **20 min** | | |

        # 4. Notas guía del entrevistador

        - Pedir ejemplos concretos.

        # 5. Cuerpo de la proforma

        ## 5.1 Misión

        **1.1** Cuéntenos cuál es la misión del área.

        ___

        ___

        ___

        **1.2** ¿Qué tareas ocupan la semana?

        ___

        ___

        ___

        ___

        ## 5.2 Diagnóstico

        **2.1** ¿Qué parte del proceso demora más?

        ___

        ___

        ___
        """)

    def test_proforma_valida_pasa(self):
        self.assertSinProblemas(self.revisar("proforma-entrevista", self.PROFORMA))

    def test_proforma_con_errores_sembrados(self):
        doc = self.PROFORMA.replace("**20 min**", "**25 min**").replace("**1.2**", "**1.3**")
        doc = doc.replace("**2.1** ¿Qué parte del proceso demora más?\n\n___\n\n___\n\n", "**2.1** ¿Qué parte del proceso demora más?\n\n")
        inf = self.revisar("proforma-entrevista", doc)
        self.assertMensaje(inf.advertencias, "tiempo total es 25 min, pero los tiempos estimados suman 20 min")
        self.assertMensaje(inf.advertencias, "pregunta 1.3: la numeración no es continua; se esperaba 1.2")
        self.assertMensaje(inf.advertencias, "la pregunta 2.1 tiene 1 líneas")
        sin_total = self.PROFORMA.replace("| **Tiempo total** | | **20 min** | | |\n", "")
        self.assertMensaje(self.revisar("proforma-entrevista", sin_total).advertencias, "no termina con la fila «\\*\\*Tiempo total")

    FICHA = textwrap.dedent("""\
        # Patrón State

        **Familia:** Comportamiento (Behavioral)

        # Intención

        *Permite que un objeto cambie su comportamiento cuando cambia su estado.* (Gamma et al., 1994)

        # Diagrama canónico

        La Figura 1 muestra la estructura.

        ![Diagrama de clases del patrón State](state.png)

        **Figura 1.** Estructura del patrón

        # Cuándo usarlo

        La Tabla 1 resume cuándo usarlo.

        **Tabla 1.** Cuándo usar el patrón

        | Sí usarlo | No usarlo |
        |---|---|
        | El comportamiento depende del estado | Hay dos estados fijos |

        # Trampas y anti-patterns

        - **Explosión de clases:** un estado por combinación.

        # Problema sin el patrón

        Texto.

        # Solución en código

        Texto.

        # Caso propio

        Texto.

        # Referencias

        Gamma, E. et al. (1994). *Design Patterns*. Addison-Wesley.
        """)

    def test_ficha_valida_pasa(self):
        self.assertSinProblemas(self.revisar("ficha-1pager", self.FICHA))

    def test_ficha_con_errores_sembrados(self):
        doc = (self.FICHA.replace("**Familia:** Comportamiento (Behavioral)", "")
               .replace("cuando cambia su estado.*", "cuando cambia su estado. Parece otra clase. Se usa mucho.*")
               .replace("| Sí usarlo | No usarlo |\n|---|---|", "| Sí | No | Nota |\n|---|---|---|"))
        inf = self.revisar("ficha-1pager", doc)
        self.assertMensaje(inf.advertencias, "falta «\\*\\*Familia:\\*\\*»")
        self.assertMensaje(inf.advertencias, "la intención tiene 3 oraciones")
        self.assertMensaje(inf.advertencias, "solo dos columnas")

    LAMINAS = textwrap.dedent("""\
        # Arquitectura del sistema de gestión

        # Objetivo y estado

        **Visión general**

        Un sistema para centralizar inscripciones.

        - **Objetivo:** reemplazar planillas.

        # Contexto del sistema

        **C4 · Nivel 1**

        Quién usa el sistema.

        # Contenedores

        **C4 · Nivel 2**

        Las aplicaciones del sistema.

        # Despliegue

        **Infraestructura**

        Dónde se ejecuta.

        # Decisiones de arquitectura

        **Decisiones**

        Cada decisión con su motivo.

        # Fuera del alcance

        **Alcance**

        Lo que no entra.
        """)

    def test_laminas_validas_pasan(self):
        self.assertSinProblemas(self.revisar("arquitectura-presentacion", self.LAMINAS))

    def test_laminas_con_errores_sembrados(self):
        doc = (self.LAMINAS.replace("**C4 · Nivel 2**\n\n", "").replace("Dónde se ejecuta.", "Uno. Dos. Tres. Cuatro.")
               .replace("Lo que no entra.", "Lo que no entra.\n\n## Detalle\n\nTexto."))
        inf = self.revisar("arquitectura-presentacion", doc)
        self.assertMensaje(inf.advertencias, "«contenedores» no empieza con el antetítulo")
        self.assertMensaje(inf.advertencias, "la bajada de «despliegue» tiene 4 oraciones")
        self.assertMensaje(inf.advertencias, "«fuera del alcance» tiene secciones")

    def test_sin_componentes_de_plantilla_no_se_revisa(self):
        prompt = self.prompt("arquitectura-presentacion")
        prompt.pop("componentes_plantilla")
        inf = vd.Informe()
        vd.verificar(prompt, [self.escribir("doc.md", self.LAMINAS.replace("**C4 · Nivel 2**\n\n", ""))], inf)
        self.assertSinProblemas(inf)
