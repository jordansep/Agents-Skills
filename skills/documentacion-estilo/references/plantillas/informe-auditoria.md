# Plantilla: Informe de completitud (auditoría)

Diseño tomado de *2026-10-31-Informe-completitud-hemocentro-79bbf4b.pdf* (10 páginas, «Informe de completitud — Grupo 3 — Hemocentro Municipal de Córdoba»), que el usuario entregó como modelo (DEC-007). Es un informe que revisa un entregable contra una lista de criterios y dice qué falta, con evidencia para cada punto.

## 1. Página

| Aspecto | Valor |
|---|---|
| Papel | A4 vertical |
| Márgenes | Unos 1,8 cm |
| Fuente | Segoe UI en todo el documento; Consolas para rutas, identificadores y código |
| Encabezado y pie | Ninguno |

## 2. Títulos y color

| Elemento | Estilo | Color |
|---|---|---|
| Título | Negrita, unos 16 pt, en dos líneas: «Informe de completitud — Grupo N — Organización» | Azul `#1F5FBF` |
| H2 («Resumen», «Detalle por punto») | Negrita, con una línea azul debajo en todo el ancho | Azul `#1F5FBF` |
| H3 de cada punto | Negrita: «N · Nombre — Estado (NN %)» | Texto `#1F2328` |
| Línea de archivo | Pequeña, gris, debajo del H3: «Archivo: docs/01-vision-y-backlog.md» | Gris `#57606A` |
| Cuerpo | Regular, unos 9 pt | `#1F2328` |

## 3. Bloques

1. **Ficha de corrida**, debajo del título, en gris pequeño: commit corregido (en negrita y monoespaciada), fecha, corte, modo; rama y estado del repositorio; criterio usado; y la explicación de las etiquetas.
2. **Resumen**: un párrafo con el veredicto general, lo que falta y lo mejor logrado. Debajo, la tabla resumen.
3. **Tabla resumen**: Punto · Estado · Completitud · Lo principal que falta.
4. **Detalle por punto**: para cada punto, una tabla Criterio · ¿Cumple? · Evidencia, y luego dos párrafos:
   - «**Observaciones de *tema*:** …»
   - «**Para completar:** …» (una raya «—» si no falta nada, o una lista de acciones).
5. La **evidencia** cita el lugar exacto entre paréntesis, con archivo o línea («(01:124-152)», «06:681, 691, 702»).

## 4. Estados y etiquetas

El estado siempre va escrito; el color lo acompaña, no lo reemplaza.

| Valor | Celda |
|---|---|
| Completo / Sí | Fondo verde claro `#DAFBE1`, texto verde `#1A7F37` |
| Parcial | Fondo amarillo claro `#FFF8C5`, texto ocre `#9A6700` |
| No | Fondo rosado `#FFEBE9`, texto rojo `#CF222E` |

Etiquetas de certeza, como pastillas pequeñas en mayúsculas al final de la oración:

| Etiqueta | Significado | Color |
|---|---|---|
| `CONFIRMADO` | Verificado en la fuente | Azul sobre azul claro |
| `PROBABLE` | Inferencia sin verificar del todo | Violeta sobre violeta claro |

## 5. Tablas

- Encabezado con relleno gris claro `#F6F8FA` y texto en negrita.
- Líneas finas grises entre filas y en el contorno.
- Columna de criterios estrecha; la de evidencia ocupa el resto.
- Porcentajes alineados a la derecha.

## 6. En el configurador

La plantilla **Informe de auditoría** es el primer paso del configurador (`assets/configurador.html`). Carga un punto de partida completo, y después se puede cambiar cualquier valor:

- **Ejes**: tipo informe técnico, metodología ninguna, propósito analítico, ámbito técnico, lector experto, medio impreso.
- **Estructura**: pretextual ninguna; textual Resumen de la revisión, Detalle por punto; postextual ninguna; capítulos sin número, capítulos seguidos, sin página nueva.
- **Presentación**: la de las secciones de arriba (fuentes, tamaños, márgenes y colores).

Componentes propios. Cada uno tiene su ejemplo en la vista previa y su regla en el prompt; la regla de esta tabla es la que copia el prompt, palabra por palabra.

| Componente | Regla del prompt | Qué revisa `verificar_doc.py` |
|---|---|---|
| Ficha de corrida | debajo del título, antes del primer capítulo y en gris pequeño: `` **Commit:** `abc1234` · **Fecha:** … · **Corte:** … · **Modo:** … ``; en la línea siguiente, `**Rama:** … · **Estado del repositorio:** …`; después, `**Criterio:** …` y qué significa cada estado. | Que estén el commit (en código), la fecha y el criterio antes del primer capítulo. |
| Estado y completitud | el resumen es un párrafo con el veredicto general, lo que falta y lo mejor logrado, seguido de la tabla Punto · Estado · Completitud · Lo principal que falta; Estado es Completo, Parcial o No y siempre va escrito (el color verde, amarillo o rosado lo acompaña, no lo reemplaza); Completitud es un porcentaje alineado a la derecha y Completo es siempre 100 %. | Que Estado sea Completo, Parcial o No y que Completo sea 100 %. |
| Criterio y evidencia | cada punto del detalle es un `### N · Nombre — Estado (NN %)` con la línea `` Archivo: `ruta` `` debajo; luego, la tabla Criterio · ¿Cumple? · Evidencia, donde ¿Cumple? es Sí, Parcial o No y la evidencia cita el lugar exacto entre paréntesis (`(01:124-152)`); cierran el punto dos párrafos: `**Observaciones de *tema*:** …` y `**Para completar:** …`, con una raya «—» si no falta nada o la lista de acciones. | El título de cada punto, la línea Archivo, los valores de ¿Cumple?, el lugar de la evidencia en Sí y Parcial, y el párrafo Para completar. |
| Etiquetas de certeza | lo verificado en la fuente termina con `` `CONFIRMADO` `` y una inferencia sin verificar del todo, con `` `PROBABLE` ``; se exportan como pastillas pequeñas en mayúsculas, azul y violeta. | — (no se puede revisar en Markdown) |

## 7. Puntos abiertos

1. ¿Este informe se genera siempre en PDF, o también en Markdown para el repositorio?
