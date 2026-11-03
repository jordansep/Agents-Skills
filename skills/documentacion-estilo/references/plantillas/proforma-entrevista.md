# Plantilla: Proforma de entrevista

Diseño tomado de *Proforma_Entrevista_Academica_A4.pdf* (4 páginas), que el usuario entregó como modelo (DEC-007). Es un **formulario para imprimir y completar a mano** durante una entrevista de relevamiento, no un informe.

## 1. Página

| Aspecto | Valor |
|---|---|
| Papel | A4 vertical |
| Márgenes | Unos 2 cm |
| Pie | «Pág. N», centrado. Sin encabezado |
| Medio | Impreso |

## 2. Tipografía

| Elemento | Fuente | Estilo |
|---|---|---|
| Título del formulario | Noto Serif | Negrita, mayúsculas sostenidas, centrado («PROFORMA DE ENTREVISTA») |
| Barra de sección | Noto Serif | Negrita, mayúsculas sostenidas, unos 9 pt, numerada («1. DATOS DE LA ENTREVISTA») |
| Pregunta | Noto Serif | Regular, con su número en negrita («**1.2** Cuéntenos sobre…») |
| Cuerpo y celdas | Noto Serif | Regular, unos 10 pt |

Una sola familia serif en todo el formulario.

## 3. Color

Solo grises; se imprime en blanco y negro sin perder nada.

| Uso | Valor |
|---|---|
| Barra de sección (fondo) | `#E9ECEF`, con borde inferior `#C4C8CC` |
| Encabezado de tabla | `#F5F5F5` |
| Texto | `#000000` |
| Líneas para escribir | Gris medio `#979898` |

## 4. Componentes

- **Barra de sección**: franja de ancho completo con fondo gris claro y el título numerado en mayúsculas. Cada bloque del formulario empieza con una.
- **Tabla de datos**: dos columnas de pares «campo + espacio para completar» (Fecha `___ / ___ / ______`, Hora de inicio `___ : ___`, Modalidad «Presencial / Virtual»). Bordes finos grises.
- **Tabla de agenda**: Bloque · Tema · Tiempo estimado · Tiempo real · Tiempo total, con fila final «TIEMPO TOTAL» en negrita.
- **Pregunta abierta**: número de la pregunta en negrita, texto de la pregunta y debajo de 3 a 4 líneas horizontales para responder.
- **Listas de objetivos y notas guía**: viñetas simples, una línea cada una.
- Secciones: 1. Datos · 2. Objetivos · 3. Agenda y control de tiempos · 4. Notas guía del entrevistador · 5. Cuerpo de la proforma (bloques temáticos: Misión, Estructura, Diagnóstico de dolores…).

## 5. En el configurador

La plantilla **Proforma de entrevista** es el primer paso del configurador (`assets/configurador.html`). Carga un punto de partida completo, y después se puede cambiar cualquier valor:

- **Ejes**: tipo otro, metodología ninguna, propósito instructivo, ámbito académico, lector experto, medio impreso.
- **Estructura**: pretextual ninguna; textual Datos de la entrevista, Objetivos, Agenda y control de tiempos, Notas guía del entrevistador, Cuerpo de la proforma; postextual ninguna; capítulos seguidos, sin página nueva.
- **Presentación**: la de las secciones de arriba (fuentes, tamaños, márgenes y colores).

Componentes propios. Cada uno tiene su ejemplo en la vista previa y su regla en el prompt; la regla de esta tabla es la que copia el prompt, palabra por palabra.

| Componente | Regla del prompt | Qué revisa `verificar_doc.py` |
|---|---|---|
| Barras de sección | cada capítulo empieza con una barra de sección: en Markdown, `# 1. Título` con mayúscula inicial; al exportar, una franja de ancho completo con fondo gris claro, borde inferior gris y el título en mayúsculas sostenidas. | — (no se puede revisar en Markdown) |
| Campos para completar | los datos se piden en una tabla de pares campo y espacio para completar: fechas `___ / ___ / ______`, horas `___ : ___` y opciones separadas por barra («Presencial / Virtual»); nunca se completan con datos inventados. | — (no se puede revisar en Markdown) |
| Agenda con tiempos | tabla Bloque · Tema · Tiempo estimado · Tiempo real · Tiempo total, con los tiempos en minutos (`10 min`) y las columnas de tiempo real en blanco; la última fila es `**Tiempo total**` (en mayúsculas al exportar) con la suma de los tiempos estimados. | Que la última fila sea Tiempo total y que sume los tiempos estimados. |
| Preguntas con líneas | cada pregunta es un párrafo que empieza con su número en negrita, `**1.2** Texto de la pregunta`, numerado por bloque temático (1.1, 1.2… y 2.1 al cambiar de bloque); debajo, de 3 a 4 líneas para responder, cada una como `___` en su propio párrafo. | Que cada pregunta tenga de 3 a 4 líneas y que la numeración sea continua. |

## 6. Puntos abiertos

1. ¿El código del formulario (por ejemplo, P-06) va en el encabezado de cada página, o solo en la tabla de datos?
2. ¿Cuántas líneas de respuesta por pregunta? El modelo usa 3 o 4 según la pregunta.
