# Plantilla: Documento de arquitectura en láminas

Diseño tomado de *arquitectura-sistema-gestion-aula-virtual.pdf* (12 láminas), que el usuario entregó como modelo (DEC-007). Es un documento de arquitectura **en formato de presentación**: cada página es una lámina horizontal con una sola idea.

## 1. Página

| Aspecto | Valor |
|---|---|
| Papel | A4 **horizontal** (29,7 × 21 cm) |
| Márgenes | Unos 1,5 cm |
| Estructura | Una idea por lámina: antetítulo, título, bajada de 1 a 3 líneas y el contenido (tarjetas o diagrama) |
| Medio | PDF digital |

## 2. Tipografía

| Elemento | Fuente | Estilo | Color |
|---|---|---|---|
| Antetítulo | Segoe UI | Negrita, unos 7 pt, mayúsculas con espaciado amplio («C4 · NIVEL 1») | Azul `#1F5FBF` |
| Título de lámina | Segoe UI | Negrita, 20 a 26 pt; en la portada, en dos líneas | Azul muy oscuro `#173A6D` |
| Bajada | Segoe UI | Regular, unos 9 pt | Gris azulado `#5B6C85` |
| Texto de tarjetas y cajas | Segoe UI | Regular, 7 a 8 pt; título de la tarjeta en negrita | `#213455` |
| Código | Consolas | Regular | — |

## 3. Color

| Uso | Fondo | Borde |
|---|---|---|
| Tarjeta neutra (Objetivo, Estado) | Blanco | Gris claro `#DFE5EA`, esquinas redondeadas |
| Límite del sistema (C4) | `#F7FAFF` | Azul `#6C84A5` |
| Sistema o contenedor propio | `#E8F1FF` | Azul `#1F5FBF` |
| Persona o actor | `#FFF4D6` (amarillo) | Ocre `#C9A040` |
| Sistema externo o almacenamiento | `#E7F5ED` (verde) | Verde `#3D8B5A` |
| Elemento futuro o fuera de alcance | Blanco | Gris, **línea discontinua** |
| Aviso positivo («Primera demo: …») | `#E7F5ED` | Barra verde a la izquierda |
| Aviso de alcance («Fuera del alcance…») | `#FFF4D6` | Barra ocre a la izquierda |

El significado de cada color es el mismo en todos los diagramas del documento.

## 4. Diagramas

- Notación **C4**: nivel 1 (contexto) y nivel 2 (contenedores y despliegue).
- Caja: nombre en negrita y debajo una línea pequeña con su responsabilidad o tecnología («API NestJS · un backend modular»).
- Flechas finas grises con la etiqueta pequeña sobre la línea («SQL», «URLs firmadas», «REST / OpenAPI»).
- El límite del sistema es un rectángulo redondeado con su nombre en negrita arriba a la izquierda.
- Flujo de izquierda a derecha: actores a la izquierda, sistema al centro y externos a la derecha.

## 5. En el configurador

La plantilla **Arquitectura en láminas** es el primer paso del configurador (`assets/configurador.html`). Carga un punto de partida completo, y después se puede cambiar cualquier valor:

- **Ejes**: tipo documento de arquitectura, metodología ninguna, propósito expositivo, ámbito técnico, lector mixto, medio digital.
- **Estructura**: pretextual Portada; textual Objetivo y estado, Contexto del sistema, Contenedores, Despliegue, Decisiones de arquitectura, Fuera del alcance; postextual ninguna; capítulos sin número, sin paginación.
- **Presentación**: la de las secciones de arriba (fuentes, tamaños, márgenes y colores).

Componentes propios. Cada uno tiene su ejemplo en la vista previa y su regla en el prompt; la regla de esta tabla es la que copia el prompt, palabra por palabra.

| Componente | Regla del prompt | Qué revisa `verificar_doc.py` |
|---|---|---|
| Antetítulo y bajada | cada lámina es un `# Título` seguido, en su propia línea, del antetítulo en negrita (`**C4 · Nivel 1**`, con mayúscula inicial) y de la bajada, un párrafo de una a tres oraciones; al exportar, el antetítulo va arriba del título, en mayúsculas con espaciado amplio. | Que cada lámina tenga antetítulo y que la bajada no pase de tres oraciones. |
| Una idea por lámina | cada lámina desarrolla una sola idea, sin `##` adentro: si hacen falta secciones, se divide en varias láminas. | Que ninguna lámina tenga secciones. |
| Tarjetas | el contenido de una lámina va en tarjetas: una viñeta por tarjeta, con el título en negrita y dos puntos (`- **Objetivo:** texto breve`); se exportan como cajas blancas con borde gris claro y esquinas redondeadas. | — (no se puede revisar en Markdown) |
| Colores de C4 | en los diagramas C4 cada color significa lo mismo en todo el documento: persona en amarillo (`#FFF4D6`, borde `#C9A040`), sistema o contenedor propio en azul (`#E8F1FF`, borde `#1F5FBF`), sistema externo o almacenamiento en verde (`#E7F5ED`, borde `#3D8B5A`) y lo futuro o fuera del alcance en blanco con borde gris discontinuo; el límite del sistema es un rectángulo redondeado con su nombre arriba a la izquierda y el flujo va de izquierda a derecha. | — (no se puede revisar en Markdown) |

## 6. Puntos abiertos

1. ¿Las láminas llevan número de página y pie con el nombre del documento? El modelo no los tiene.
2. ¿Se usa este formato solo para arquitectura o también para presentar otros entregables?
