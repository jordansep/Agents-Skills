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
        self.assertIn("uno por cada título con nombre del primer nivel del índice", SKILL)
        self.assertIn("`Forma del documento` y `Datos personales y seguridad`", SKILL)
        for fila in ("Contenido anunciado presente", "Cuentas correctas", "Formalidades declaradas"):
            self.assertIn(fila, SKILL)

    def test_documento_sin_consigna_con_severidad_y_veredicto_fijos(self):
        self.assertIn("cambia el resultado de una decisión del documento", SKILL)
        self.assertIn("o un error que no cambia lo decidido", SKILL)
        self.assertIn("**No listo** si alguna pregunta abierta cambia el alcance", SKILL)

    def test_documento_sin_consigna_no_pisa_la_variante(self):
        self.assertIn("aplican si hay consigna, norma o variante de entrega académica", SKILL)

    def test_lista_de_tareas_sin_agrupar(self):
        self.assertIn("No juntes correcciones distintas", SKILL)

    def test_carpeta_sin_datos_de_un_proyecto_ni_rutas_locales(self):
        for archivo in CARPETA.rglob("*.md"):
            with self.subTest(archivo=archivo.name):
                texto = archivo.read_text(encoding="utf-8")
                self.assertNotRegex(texto, r"(?i)grupo \d|\bmyd\b|trabajo integrador|\b[a-z]:\\(?!program files)")

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
