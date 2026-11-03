# Plantilla: Ficha de una página (1-pager)

Diseño tomado de *State_1pager.pdf* (ficha del patrón State), que el usuario entregó como modelo (DEC-007). Sirve para fichas de estudio o de referencia: **todo en una sola página A4**, en dos columnas.

## 1. Página

| Aspecto | Valor |
|---|---|
| Papel | A4 vertical, una sola página |
| Márgenes | Unos 1,5 cm |
| Columnas | Dos. Izquierda: definición, diagrama, cuándo usar, trampas. Derecha: problema, solución con código, caso propio, referencias |
| Pie | Línea gris pequeña: materia · año · actividad a la izquierda, nombre de la ficha a la derecha |

## 2. Tipografía

| Elemento | Fuente | Estilo |
|---|---|---|
| Título | Helvetica / Arial (TeX Gyre Heros) | Negrita, unos 16 pt, azul `#1C4F7C` |
| Etiqueta de familia | Igual | Negrita, unos 8 pt, dentro de una pastilla gris a la derecha del título («Familia: Comportamiento (Behavioral)») |
| Título de bloque | Igual | Negrita, unos 10 pt, azul, con una barra vertical azul a la izquierda |
| Cuerpo | Igual | Regular, unos 8,5 pt |
| Código | Liberation Mono / Consolas | Unos 7,5 pt |

## 3. Color

| Uso | Valor |
|---|---|
| Títulos y barras de bloque | `#1C4F7C` |
| Definición (intención) | Fondo beige `#F1EFE8`, en cursiva, con barra gris a la izquierda |
| «Sí usarlo» | Fondo verde `#EAF3DE` |
| «No usarlo» | Fondo rosado `#FCEBEB` |
| Bloque de código | Fondo oscuro `#2C2C2A`, texto claro |
| Cajas del diagrama | Azul `#E6F1FA` (contexto), verde agua `#E1F5EE` (estados) |

## 4. Bloques, en orden

1. **Título + familia** (pastilla).
2. **Intención**: una o dos líneas en cursiva sobre fondo beige, con la cita (Gamma et al., 1994).
3. **Diagrama canónico**: diagrama de clases pequeño, con un pie de una línea centrado debajo.
4. **Cuándo Sí / Cuándo NO**: tabla de dos columnas, verde y rosada.
5. **Trampas y anti-patterns**: viñetas, con el término clave en negrita.
6. **Problema sin el patrón**: un párrafo, con los nombres de código en monoespaciada.
7. **Solución — código**: bloque oscuro con el lenguaje en el título («Solución — código (TypeScript)»).
8. **Caso propio**: el ejemplo aplicado al proyecto, con los estados en negrita y flechas (→).
9. **Referencias bibliográficas**: APA 7, en viñetas, a 7,5 pt.

## 5. En el configurador

La plantilla **Ficha 1-pager** es el primer paso del configurador (`assets/configurador.html`). Carga un punto de partida completo, y después se puede cambiar cualquier valor:

- **Ejes**: tipo otro, metodología ninguna, propósito expositivo, ámbito académico, lector experto, medio impreso.
- **Estructura**: pretextual ninguna; textual Intención, Diagrama canónico, Cuándo usarlo, Trampas y anti-patterns, Problema sin el patrón, Solución en código, Caso propio; postextual Referencias; capítulos sin número, capítulos seguidos, sin página nueva, sin paginación.
- **Presentación**: la de las secciones de arriba (fuentes, tamaños, márgenes y colores).

Componentes propios. Cada uno tiene su ejemplo en la vista previa y su regla en el prompt; la regla de esta tabla es la que copia el prompt, palabra por palabra.

| Componente | Regla del prompt | Qué revisa `verificar_doc.py` |
|---|---|---|
| Familia del patrón | debajo del título, antes del primer bloque, la línea `**Familia:** Nombre (Name)`; se exporta como una pastilla gris a la derecha del título. | Que esté la línea antes del primer bloque. |
| Intención | el bloque Intención tiene una o dos oraciones en cursiva con la cita de la obra que define el patrón; se exporta sobre fondo beige con una barra gris a la izquierda. | Que no pase de dos oraciones. |
| Cuándo sí y cuándo no | el bloque Cuándo usarlo es una tabla de dos columnas, `Sí usarlo` y `No usarlo` (verde y rosada al exportar), con una situación por fila. | Que la tabla tenga solo esas dos columnas. |
| Una página a dos columnas | la ficha entra en una sola página A4, a dos columnas: a la izquierda Intención, Diagrama canónico, Cuándo usarlo y Trampas; a la derecha Problema, Solución, Caso propio y Referencias; si no entra, se acorta el texto y nunca se pasa a una segunda página. | — (no se puede revisar en Markdown) |

## 6. Puntos abiertos

1. ¿La ficha usa siempre Helvetica/Arial, o la familia del documento principal (Calibri)?
