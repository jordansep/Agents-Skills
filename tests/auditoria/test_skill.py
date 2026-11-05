"""Reglas de auditoria-sistemas-experimental que no deben perderse.

Ejecutar desde la raíz del repositorio:
    python -m unittest discover -s tests -v
"""
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CARPETA = RAIZ / "skills" / "auditoria-sistemas-experimental"
SKILL = (CARPETA / "SKILL.md").read_text(encoding="utf-8")
VARIANTE = (CARPETA / "references" / "formato-devolucion-docente.md").read_text(encoding="utf-8")


class Skill(unittest.TestCase):
    def test_descripcion_dentro_del_limite(self):
        m = re.search(r"^description: >-\r?\n(.*?)^metadata:", SKILL, re.S | re.M)
        self.assertLessEqual(len(" ".join(m[1].split())), 1024)

    def test_sin_herramienta_ni_ruta_fijas(self):
        self.assertNotRegex(SKILL, r"\bREA\b|BonoCorreciones|mcp__rea|reverse-engineer")

    def test_completo_exige_que_no_haya_defectos(self):
        self.assertIn("**Defecto abierto**", SKILL)
        self.assertRegex(SKILL, r"\*\*Completo\*\* \| 100 %, sin defectos abiertos")

    def test_simple_no_certifica(self):
        self.assertIn("Sin defectos a la vista", SKILL)
        self.assertIn("**Nunca se certifica**", SKILL)

    def test_escala_para_requisitos_universales(self):
        self.assertIn("**una sola falla es No**", SKILL)
        self.assertIn("**Una fila por línea del criterio.**", SKILL)

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

    def test_plantilla_general_con_variante_docente(self):
        for seccion in ("## Resumen", "## Detalle por punto", "## Coherencia entre fuentes", "## Lista de tareas"):
            self.assertIn(seccion, SKILL)
        self.assertIn("## Variante docente", VARIANTE)
        self.assertIn("Completo con defectos abiertos", VARIANTE)


if __name__ == "__main__":
    unittest.main()
