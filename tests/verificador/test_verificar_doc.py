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
            self.assertEqual(s["reimportado"], {k: s[k] for k in ("proposito", "ambito", "lector")}, nombre)


if __name__ == "__main__":
    unittest.main()
