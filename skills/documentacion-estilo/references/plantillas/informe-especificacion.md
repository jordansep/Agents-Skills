# Plantilla: Informe técnico / especificación

Diseño tomado de *informe_av_v2.docx* («Informe de Relevamiento y Diseño de Arquitectura», 18 páginas), que el usuario entregó como modelo (DEC-007). Es un informe técnico de requisitos y arquitectura, más sobrio que el Trabajo de campo y sin portada de color.

## 1. Página

| Aspecto | Valor |
|---|---|
| Papel | Carta (21,59 × 27,94 cm) |
| Márgenes | 2,54 cm arriba y abajo, 3,17 cm a los lados (márgenes «normales» de Word) |
| Encabezado y pie | Ninguno |

## 2. Tipografía y color

| Elemento | Tamaño | Estilo | Color |
|---|---|---|---|
| Título del documento | Unos 22 pt | Regular, centrado, en dos líneas | `#365F91` |
| Datos del documento | Cuerpo | Centrados, uno por línea: sistema, documento, estado | Negro |
| H1 | 14 pt | Negrita, numerado («1. Visión General del Proyecto»), 24 pt antes | `#365F91` |
| H2 | 13 pt | Negrita, numerado («5.1. Decisión Arquitectónica») | `#4F81BD` |
| H3 | Cuerpo | Negrita, sin número («Estudiante (Alumno)») | `#4F81BD` |
| Cuerpo | 10 a 11 pt | Serif (Cambria), regular | Negro |
| Tablas | 9 pt | Regular | Negro |

## 3. Tablas

- Sin leyenda «Tabla N»: la tabla se presenta con una frase en el texto que termina en dos puntos («…se estructura bajo una jerarquía de cuatro niveles:»).
- Encabezado con relleno azul claro `#DCE6F1`, texto en regular.
- Bordes finos en todas las celdas, columnas a la izquierda.
- Columnas típicas: Capa · Tecnología · Justificación; Módulo · Responsabilidad.

## 4. Listas

- Viñetas con el término en negrita seguido de dos puntos («**Cohesión transaccional:** las operaciones…»).
- Listas de funcionalidades agrupadas por rol de usuario, cada grupo bajo un H3.

## 5. Figuras

- «Figura N. Título» en una sola línea, debajo de la imagen, centrada y sin negrita.

## 6. En el configurador

La plantilla **Informe técnico** es el primer paso del configurador (`assets/configurador.html`). Carga un punto de partida completo, y después se puede cambiar cualquier valor:

- **Ejes**: tipo especificación de requisitos, metodología ISO/IEEE 29148, propósito expositivo, ámbito técnico, lector especialista, medio impreso.
- **Estructura**: pretextual Control de versiones; textual Introducción, Descripción general, Requisitos específicos, Trazabilidad; postextual Apéndices; numeración hasta el nivel 2.
- **Presentación**: la de las secciones de arriba (fuentes, tamaños, márgenes y colores).

Componentes propios. Cada uno tiene su ejemplo en la vista previa y su regla en el prompt; la regla de esta tabla es la que copia el prompt, palabra por palabra.

| Componente | Regla del prompt | Qué revisa `verificar_doc.py` |
|---|---|---|
| Datos del documento | debajo del título, antes del primer capítulo, tres líneas centradas, una por dato: `**Sistema:** …`, `**Documento:** …` y `**Estado:** …`. | Que estén las tres líneas antes del primer capítulo. |
| Viñetas con término | las viñetas que definen o caracterizan algo empiezan con el término en negrita y los dos puntos dentro de la negrita: `- **Término:** texto`. | Que los dos puntos queden dentro de la negrita. |

Normas de escritura que suma al prompt (sección 5):

- Las funcionalidades se agrupan por rol de usuario, cada grupo bajo un `###` sin número.

## 7. Puntos abiertos

1. Este informe usa Carta y el Trabajo de campo usa A4. ¿Qué papel se usa para informes técnicos?
2. Las tablas no tienen número ni título, a diferencia del Trabajo de campo (APA 7). ¿Se unifican con APA 7?
3. Los títulos usan los colores de Word 2007 (`#365F91`, `#4F81BD`) y no los del Trabajo de campo (`#2E74B5`). ¿Se unifican?
