"""Reglas de auditoria-sistemas que no deben perderse.

Ejecutar desde la raíz del repositorio:
    python -m unittest discover -s tests -v
"""
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CARPETA = RAIZ / "skills" / "auditoria-sistemas"
SKILL = (CARPETA / "SKILL.md").read_text(encoding="utf-8")
VARIANTE = (CARPETA / "references" / "variante-entrega-academica.md").read_text(encoding="utf-8")
PLAN = (CARPETA / "references" / "plan-de-auditoria.md").read_text(encoding="utf-8")


class Skill(unittest.TestCase):
    def test_descripcion_dentro_del_limite(self):
        m = re.search(r"^description: >-\r?\n(.*?)^metadata:", SKILL, re.S | re.M)
        self.assertLessEqual(len(" ".join(m[1].split())), 1024)

    def test_sin_herramienta_ni_ruta_fijas(self):
        self.assertNotRegex(SKILL, r"\bREA\b|mcp__rea|reverse-engineer")

    def test_completo_exige_que_no_haya_defectos(self):
        self.assertIn("**Defecto abierto**", SKILL)
        self.assertRegex(SKILL, r"\*\*Completo\*\* \| 100 %, sin defectos abiertos")

    def test_simple_no_certifica(self):
        self.assertIn("Sin defectos a la vista", SKILL)
        self.assertIn("**Nunca se certifica**", SKILL)

    def test_nombre_y_sin_rastros_de_la_version_de_prueba(self):
        self.assertRegex(SKILL, r"(?m)^name: auditoria-sistemas\s*$")
        self.assertNotRegex(SKILL.lower(), "experimental")

    def test_toda_falla_verificada_es_no(self):
        self.assertIn("encontraste al menos una falla verificada", SKILL)
        self.assertIn("**Lectura estricta.**", SKILL)
        self.assertIn("**Una fila por requisito.**", SKILL)

    def test_falta_exige_que_no_haya_material(self):
        self.assertIn("0 % con material entregado", SKILL)
        self.assertIn("0 % y sin material", SKILL)

    def test_punto_adicional_sin_promedio(self):
        self.assertIn("`Adicional · Seguridad y otros defectos`", SKILL)
        self.assertIn("**Sin promedio general.**", SKILL)

    def test_variante_usa_la_escala_de_la_consigna(self):
        self.assertIn("Si la consigna trae otra escala, usá esa", VARIANTE)

    def test_cruces_de_detalle_en_el_nivel_medio(self):
        self.assertIn("**Cruces de detalle**", SKILL)

    def test_variante_no_parte_los_items_de_su_lista(self):
        self.assertIn("«Título y estado» es una sola fila", VARIANTE)

    def test_documento_sin_consigna_con_puntos_y_filas_fijos(self):
        self.assertIn("**Documentos sin consigna.**", SKILL)
        self.assertIn("sección *Documentos sin consigna* de `references/plan-de-auditoria.md`", SKILL)
        self.assertIn("uno por cada título con nombre del primer nivel del índice", PLAN)
        self.assertIn("`Forma del documento` y `Datos personales y seguridad`", PLAN)
        for fila in ("Contenido anunciado presente", "Cuentas correctas", "Formalidades declaradas"):
            self.assertIn(fila, PLAN)

    def test_documento_sin_consigna_con_severidad_y_veredicto_fijos(self):
        self.assertIn("cambia el resultado de una decisión del documento", SKILL)
        self.assertIn("deja sin saber si algo entra al alcance o en qué etapa", SKILL)
        self.assertIn("(fecha, horario, DNI), salvo las firmas", SKILL)
        self.assertIn("**No listo** si alguna pregunta abierta cambia el alcance", SKILL)

    def test_plan_de_auditoria_fija_puntos_filas_y_chequeos(self):
        self.assertIn("`references/plan-de-auditoria.md`", SKILL)
        self.assertIn("El nivel simple no usa plan", SKILL)
        self.assertIn("plan y su versión", SKILL)
        self.assertIn("esperá su aprobación", PLAN)
        self.assertIn("Los números no se reciclan", PLAN)
        self.assertIn("Los PROBABLE no entran", PLAN)
        self.assertIn("Lo que va entre corchetes es la fila donde se informa", PLAN)
        self.assertIn("El plan nunca va dentro de la skill ni del sistema auditado", PLAN)

    def test_reglas_para_juzgar_igual_en_cada_corrida(self):
        self.assertIn("**Juzgar igual en cada corrida.**", SKILL)
        self.assertIn("**Dónde va cada defecto**", SKILL)
        self.assertIn("pide y otro no trae va en el que lo pide", SKILL)
        self.assertIn("Parcial no quiere decir \"cumple a medias\"", SKILL)
        self.assertIn("\"FUERA DEL DOCUMENTO:\"", SKILL)
        self.assertIn("Los rótulos y títulos de tablas y figuras no van acá", PLAN)

    def test_un_defecto_en_cada_chequeo_o_en_la_seccion_a_corregir(self):
        self.assertIn("va en **cada una** de esas filas, con el mismo veredicto y la misma severidad", SKILL)
        self.assertIn("la del punto cuya sección hay que", SKILL)
        self.assertIn("recibe lo que falta en otra", SKILL)
        self.assertNotIn("Una contradicción entre dos puntos es No en los dos", SKILL)
        self.assertIn("La etiqueta tiene que señalar una sola fila del mismo punto", PLAN)

    def test_reglas_de_la_medicion_de_consistencia(self):
        self.assertIn("El PROBABLE lleva la severidad que tendría si se confirmara", SKILL)
        self.assertIn("\"FUERA DEL DOCUMENTO:\" nunca va en una fila No", SKILL)
        self.assertIn("\"definida; sin registro de cumplimiento\" y sin severidad", SKILL)
        self.assertIn("se cuenta con lo vigente", SKILL)
        self.assertIn("**Imágenes leídas**", SKILL)

    def test_documento_sin_consigna_no_pisa_la_variante(self):
        self.assertIn("aplican si hay consigna, norma o variante de entrega académica", SKILL)

    def test_lista_de_tareas_sin_agrupar(self):
        self.assertIn("No juntes correcciones distintas", SKILL)

    def test_carpeta_sin_datos_de_un_proyecto_ni_rutas_locales(self):
        for archivo in CARPETA.rglob("*.md"):
            with self.subTest(archivo=archivo.name):
                texto = archivo.read_text(encoding="utf-8")
                self.assertNotRegex(texto, r"(?i)grupo \d|\bmyd\b|trabajo integrador|\b[a-z]:\\(?!program files)")

    def test_exhaustiva_no_lee_el_objetivo_en_el_hilo_principal(self):
        self.assertIn("**El objetivo no entra en el hilo principal.**", SKILL)
        self.assertIn("references/exhaustiva-por-lotes.md", SKILL)
        self.assertIn("Nunca `fork`", SKILL)
        for archivo in ("references/exhaustiva-por-lotes.md", "references/hoja-lector.md", "scripts/auditoria_lotes.py"):
            self.assertTrue((CARPETA / archivo).exists(), archivo)

    def test_subagentes_livianos_con_pocas_herramientas(self):
        for nombre, herramientas in (("lector-auditoria", "Read, Write"), ("revisor-auditoria", "Read, Write, Bash")):
            texto = (CARPETA / "agents" / f"{nombre}.md").read_text(encoding="utf-8")
            self.assertIn(f"name: {nombre}", texto)
            self.assertIn(f"tools: {herramientas}", texto)
            self.assertIn(nombre, (CARPETA / "references" / "exhaustiva-por-lotes.md").read_text(encoding="utf-8"))
        self.assertIn("-Subagentes", (RAIZ / "scripts" / "instalar_skills.ps1").read_text(encoding="utf-8"))

    def test_cada_nivel_suma_una_exigencia(self):
        self.assertIn("**Intento de refutar cada Completo**", SKILL)
        self.assertIn("**Segunda pasada independiente**", SKILL)
        self.assertIn("Cobertura: leído completo", SKILL)

    def test_severidad_para_todo_hallazgo(self):
        for nivel in ("Crítica", "Alta", "Media", "Baja", "Info"):
            self.assertIn(f"| **{nivel}** |", SKILL)

    def test_binarios_sin_ejecutar_y_con_metodo(self):
        self.assertIn("**No ejecutes ni cargues el objetivo**", SKILL)
        self.assertIn("**Declará el método**", SKILL)

    def test_plantilla_general_con_variante_academica(self):
        for seccion in ("## Resumen", "## Detalle por punto", "## Coherencia entre fuentes", "## Lista de tareas"):
            self.assertIn(seccion, SKILL)
        self.assertIn("# Variante de entrega académica", VARIANTE)
        self.assertIn("Completo con defectos abiertos", VARIANTE)


if __name__ == "__main__":
    unittest.main()
