# Plantilla: Trabajo de campo (UNC · AUSI)

Diseño tomado del documento de referencia que entregó el usuario: *Trabajo de Campo v3.6* de la Práctica Profesional (Grupo 19, Analista Universitario de Sistemas de Información, UNC y ESCMB). El usuario indicó que este documento muestra el diseño que quiere (DEC-007). Los valores salen de `scripts/extraer_estilo_docx.py` y de revisar el documento renderizado.

Esta plantilla funciona como una guía de marca: cuando se usa, manda sobre los valores predeterminados de `estilo-visual.md`. Lo que el documento de referencia no resuelve, o resuelve de forma inconsistente, figura en «Puntos abiertos» y no se aplica hasta que el usuario lo confirme.

En el configurador, la plantilla **Trabajo de campo UNC** (primer paso, «Plantilla») carga estos valores y sus componentes propios (sección 8).

## 1. Página

| Aspecto | Valor |
|---|---|
| Papel | A4 (21 × 29,7 cm) |
| Márgenes | 1,27 cm en los cuatro lados (margen «estrecho» de Word) |
| Columnas | Una |
| Pie | Número de página a la derecha, sin texto. Sin encabezado |
| Medio | Impreso o PDF (`medio: impreso`, `formato: docx`) |

## 2. Tipografía

| Elemento | Fuente | Tamaño | Estilo | Color |
|---|---|---|---|---|
| Cuerpo | Calibri | 12 pt | Regular | Negro `#000000` |
| H1 (capítulo) | Calibri | 16 pt | Regular, centrado | `#2E74B5` |
| H2 (sección) | Calibri | 13 pt | Regular, a la izquierda | `#2E74B5` |
| H3 (subsección) | Calibri | 12 pt | Regular | `#1F4D78` |
| H4 | Calibri | 12 pt | Cursiva | `#2E74B5` |
| Texto de tablas | Calibri | 9 pt | Regular; encabezado en negrita | Negro |
| Notas de tabla y figura | Calibri | 9 pt | Cursiva | Negro |
| Código | Consolas | 9 pt | Regular | Negro |

- Los títulos **no** van en negrita: se distinguen por tamaño y color.
- Una sola familia (Calibri) para títulos y cuerpo. Consolas solo para código.
- Interlineado 1,15 en el cuerpo.
- Párrafos justificados, sin sangría de primera línea.

## 3. Color

| Token del prompt | Valor | Uso |
|---|---|---|
| `primario` | `#2E74B5` | H1, H2, H4 y enlaces (4,9 : 1 sobre blanco) |
| `primario-oscuro` | `#1F4D78` | H3 (8,8 : 1) |
| `texto` | `#000000` | Cuerpo y tablas |
| `secundario` | `#666666` | Notas y fuentes (5,7 : 1) |
| `superficie` | `#D9EAD3` | Encabezado y primera columna de tablas (verde claro) |
| `superficie-alterna` | `#EFEFEF` | Celdas de datos que se quieren destacar (gris claro) |
| `borde` | `#000000` | Bordes de tabla de 0,75 pt |

Colores de estado que usa el documento en cronogramas y planes (siempre con el estado escrito en la celda, nunca solo el color):

| Estado | Relleno |
|---|---|
| Finalizado / aceptada | `#93C47D` |
| Fila de etapa o fase | `#B6D7A8` |
| En curso / Etapa 2 | `#E69138` (naranja) |

Portada: azul UNC `#001F5B` y `#0047A0`, verde ESCMB `#1B7A3E` y `#27AE60`, fondo de datos `#F5F7FA` y etiqueta verde claro `#D6EFDF`.

## 4. Tablas (APA 7)

Formato:

```
**Tabla 3**
*Calificaciones en experiencia práctica*

| Atributo | Alejandro | Jeremías | Jordan | Promedio grupal |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

*Nota.* Escala de calificación del 1 al 10.
```

- La leyenda va **arriba** de la tabla, en dos líneas: «Tabla N» en negrita y, en la línea siguiente, el título en cursiva. Sin punto después del número.
- Debajo de la tabla, una nota que empieza con «*Nota.*» en cursiva, a 9 pt. La nota reemplaza a «Fuente: elaboración propia.»
- Bordes simples de 0,75 pt en negro en todos los lados, también entre columnas (grilla completa).
- Fila de encabezado en negrita con relleno `superficie` (`#D9EAD3`). En tablas de atributos, la primera columna lleva el mismo relleno.
- Las filas de subtotal o promedio van en negrita y cursiva.
- Las filas de agrupación (etapa, fase) ocupan todo el ancho, en negrita, con relleno `#B6D7A8`.
- Texto de celdas a 9 pt; números centrados o a la derecha.

## 5. Figuras (APA 7)

```
**Figura 12**
*Diagrama de secuencia AS-IS del circuito de inscripción y matriculación*

![Diagrama de secuencia ...](figuras/fig-12.png)

*Nota.* Puntos críticos: doble carga planilla/SGE ...
```

- Igual que las tablas: «Figura N» en negrita arriba, el título en cursiva en la línea siguiente, la imagen y, debajo, la nota en cursiva.
- La imagen va centrada y ocupa como máximo el ancho del texto.
- Esto **reemplaza** la regla general de `estilo-visual.md` (leyenda de figura debajo).

## 6. Portada

La portada es una composición de bloques de color, no una página de texto:

1. Franja superior en dos bloques: **UNC** (azul, «Universidad Nacional de Córdoba») y **ESCMB** (verde, «Esc. Superior de Comercio Manuel Belgrano»), con una línea fina debajo de cada uno.
2. Banda clara con el nombre de la carrera en azul y negrita: «Analista Universitario de Sistemas de Información».
3. Bloque azul oscuro grande con el título en dos líneas: la primera palabra en blanco y la segunda en verde («Práctica / Profesional»), una línea verde fina y el subtítulo en cursiva.
4. Tabla de datos sin bordes: etiquetas en verde claro (Grupo, Año, Integrantes) y valores sobre fondo gris claro. Los integrantes van uno por línea, precedidos de una raya.
5. Franja inferior bicolor (azul y verde) y pie con «Córdoba, Argentina» sobre azul y el año y el grupo sobre verde.

## 7. Estructura y escritura que muestra el documento

- Índice (tabla de contenido de Word) después de la portada.
- Los capítulos H1 llevan el nombre del entregable y, si tiene, su versión: «Planeamiento del Proyecto V2.0 (RUP + SCRUM)».
- Viñetas con un término en negrita seguido de dos puntos: «**Calidad de proceso:** que la forma de...».
- Cierre de sección con la línea «Documento fuente: *nombre del documento*.» en negrita.
- Las personas de la organización se citan por su rol, nunca por su nombre.

## 8. En el configurador

La plantilla **Trabajo de campo UNC** es el primer paso del configurador (`assets/configurador.html`). Carga un punto de partida completo, y después se puede cambiar cualquier valor:

- **Ejes**: tipo informe técnico, metodología ninguna, propósito mixto, ámbito académico, lector experto, medio impreso.
- **Estructura**: pretextual Control de versiones, Portada, Índice general; textual Estructura del documento, Planeamiento del proyecto, Acta de acuerdos, Cronograma de aproximación; postextual Referencias, Anexos.
- **Presentación**: la de las secciones de arriba (fuentes, tamaños, márgenes y colores).

Componentes propios. Cada uno tiene su ejemplo en la vista previa y su regla en el prompt; la regla de esta tabla es la que copia el prompt, palabra por palabra.

| Componente | Regla del prompt | Qué revisa `verificar_doc.py` |
|---|---|---|
| Portada institucional | la portada es una composición de bloques: franja con UNC y ESCMB, la carrera, el título en dos líneas (la primera palabra en blanco y la segunda en verde) con el subtítulo en cursiva, una tabla sin bordes con Grupo, Año e Integrantes (uno por línea, precedidos de una raya) y la franja inferior con «Córdoba, Argentina», el año y el grupo; los datos que falten van como `[PENDIENTE: dato]`. | — (no se puede revisar en Markdown) |
| Documento fuente | cada capítulo de la zona textual cierra con la línea `**Documento fuente: *nombre del documento*.**`; si no se conoce, `**Documento fuente: [PENDIENTE: documento fuente].**`. | Que cada capítulo de la zona textual cierre con esa línea. |
| Viñetas con término | las viñetas que definen o caracterizan algo empiezan con el término en negrita y los dos puntos dentro de la negrita: `- **Término:** texto`. | Que los dos puntos queden dentro de la negrita. |

Normas de escritura que suma al prompt (sección 5):

- Las personas de la organización se citan por su rol, nunca por su nombre.
- Cada capítulo lleva el nombre del entregable y, si tiene, su versión («Planeamiento del proyecto v2.0»).

## 9. Puntos abiertos (sin decidir)

El documento de referencia no es uniforme en estos puntos. Se preguntan al usuario (DEC-007) y no se aplican hasta que responda:

1. **Numeración de títulos**: unos H2 llevan número escrito a mano («1. Régimen de Reuniones») y otros no («Problema y Objetivo»). ¿Numeración decimal automática, numeración manual por capítulo o sin números?
2. **Mayúsculas en títulos**: la mayoría usa mayúscula inicial en cada palabra («Estructura del Documento»), y las normas del skill piden solo la primera. ¿Cuál se usa?
3. **Tamaño del cuerpo**: casi todo está a 12 pt, pero algunas secciones (Planeamiento, Cronograma de aproximación) están a 11 pt. ¿12 pt en todo el documento?
4. **Color de las notas**: la mayoría son negras en cursiva a 9 pt, y algunas están en gris (`#B7B7B7`, `#999999`) a 12 pt. `#B7B7B7` no cumple el contraste mínimo (2,0 : 1). ¿Negro en cursiva a 9 pt, o gris `#666666`?
5. **Alineación del H2**: el estilo base lo justifica, pero en el documento aparece a la izquierda. ¿A la izquierda?
6. **Interlineado**: el cuerpo usa 1,15, pero el Acta de acuerdos usa doble espacio. ¿1,15 en todo, o doble en actas formales?
7. **Versiones anteriores**: *TdC v2.2* (PDF) y *Ponderación de metodologías v3* usan Times New Roman, doble espacio, sangría de primera línea, papel Carta con márgenes de 2,54 cm, encabezado en mayúsculas centrado («RESUMEN EJECUTIVO — PONDERACIÓN METODOLÓGICA») y número de página centrado. La v3.6 pasó a Calibri, 1,15, A4 y número a la derecha. Se toma la v3.6 como vigente: ¿es correcto?
