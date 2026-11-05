# Registro de decisiones de estilo

Memoria persistente del agente de documentación (skills `documentacion-estilo` y `documentacion-generar`). Vale para todos los documentos que produzca el agente, en cualquier proyecto. El procedimiento está en `../references/memoria.md`.

Aquí solo van decisiones con alcance de **agente**. Las de un solo proyecto se guardan en `decisiones-estilo.md` del repositorio de ese proyecto, junto a su prompt de estilo, con IDs `DP-NNN`.

- Las decisiones **confirmadas** mandan sobre las referencias del skill.
- Las decisiones **pendientes** son preguntas que el usuario todavía no respondió. Si el documento en curso las necesita, se hacen antes de escribir la parte afectada.

## Índice

| ID | Tema | Estado | Alcance |
|---|---|---|---|
| DEC-001 | Tratamiento y variante del español | confirmada | agente |
| DEC-002 | Convención de números | confirmada | agente |
| DEC-003 | Tipografía y paleta de color | confirmada | agente |
| DEC-004 | Estilo de citas | confirmada | agente |
| DEC-005 | Ubicación del prompt y de la documentación | confirmada | agente |
| DEC-006 | Comillas | confirmada | agente |
| DEC-007 | Plantillas tomadas de documentos de referencia | parcial | agente |
| DEC-008 | Entregas en varios archivos | confirmada | agente |
| DEC-009 | Numeración de tablas y figuras en entregas multiarchivo | confirmada | agente |
| DEC-010 | Control de versiones desde git | confirmada | agente |
| DEC-011 | Mermaid como fuente editable de los diagramas | confirmada | agente |
| DEC-012 | Diagramas sin tipo propio en Mermaid | confirmada | agente |
| DEC-013 | Alcance de la extracción de imágenes | confirmada | agente |
| DEC-014 | Umbral de imagen mínima | confirmada | agente |

---

## DEC-001 · Tratamiento y variante del español

- **Estado**: confirmada
- **Alcance**: agente
- **Preguntado**: 02/11/2026 · **Respondido**: 05/11/2026
- **Origen**: creación inicial de los skills
- **Contexto**: el agente propuso por su cuenta español neutro, "usted" en manuales e impersonal en tesis y especificaciones. El usuario no lo confirmó. Los valores están en `escritura.md` §3 y §4 y en la tabla del Paso 1 de `SKILL.md`.

**Preguntas**

1. ¿Qué variante del español se usa? Opciones: a) neutro (recomendada: el documento llega a más lectores); b) rioplatense con voseo.
2. ¿Qué tratamiento se usa en manuales? Opciones: a) usted ("Seleccione el archivo"); b) tú ("Selecciona el archivo"); c) vos ("Seleccioná el archivo").
3. ¿Qué tratamiento se usa en tesis y especificaciones? Opciones: a) impersonal ("Se propone un modelo"; recomendada: es lo habitual en textos académicos); b) primera persona del plural ("Proponemos un modelo").

**Respuestas**

1. Rioplatense con voseo.
2. Impersonal.
3. Impersonal. En informes técnicos, también impersonal.

**Regla resultante**: español rioplatense con voseo y tratamiento impersonal en manuales, tesis, especificaciones e informes técnicos.
**Aplicada en**: `references/escritura.md` §3, §4 y §6; `references/estilo-visual.md` (Pasos de manual); `SKILL.md`; `assets/configurador.html`.
**PR**: https://github.com/jordansep/Agents-Skills/pull/39

---

## DEC-002 · Convención de números

- **Estado**: confirmada
- **Alcance**: agente
- **Preguntado**: 02/11/2026 · **Respondido**: 05/11/2026
- **Origen**: creación inicial de los skills
- **Contexto**: el agente propuso coma decimal, espacio para miles, espacio antes de % y fechas dd/mm/aaaa (`escritura.md` §3). El verificador lo controla con el campo `decimal: coma`.

**Preguntas**

1. ¿Qué separador decimal se usa? Opciones: a) coma, `3,5` (recomendada: norma RAE y uso en Argentina); b) punto, `3.5`.
2. ¿Cómo se separan los miles? Opciones: a) espacio, `12 500`; b) punto, `12.500`; c) sin separación.
3. ¿El símbolo % va con espacio? Opciones: a) sí, `15 %` (norma RAE); b) no, `15%`.

**Respuestas**

1. Coma (`3,5`).
2. Punto (`12.500`).
3. Con espacio (`15 %`). Fechas en tablas: dd/mm/aaaa.

**Regla resultante**: coma decimal, punto para miles, espacio antes de % y fechas dd/mm/aaaa en tablas.
**Aplicada en**: `references/escritura.md` §3; `assets/plantilla-prompt-estilo.md`; `assets/configurador.html`; `verificar_doc.py`.
**PR**: https://github.com/jordansep/Agents-Skills/pull/39

---

## DEC-003 · Tipografía y paleta de color

- **Estado**: confirmada
- **Alcance**: agente
- **Preguntado**: 02/11/2026 · **Respondido**: 05/11/2026
- **Origen**: creación inicial de los skills
- **Contexto**: el agente propuso Inter o Source Sans 3 para documentos digitales, Times New Roman 12 o Arial 11 para impresos y una paleta de tokens con contraste AA verificado (`estilo-visual.md` §4 y §5). No hay guía de marca confirmada.

**Preguntas**

1. ¿Hay una guía de marca o un reglamento institucional que fije la tipografía y los colores? Opciones: a) sí (adjuntarla); b) no, usar la propuesta actual; c) no, pero se quiere otra propuesta.
2. ¿Qué familia se usa en documentos digitales? Opciones: a) Inter; b) Source Sans 3; c) otra.
3. ¿Qué color primario se usa? Opciones: a) azul `#1F4E79` (actual); b) color institucional (indicar el código).

**Respuestas**

1. No hay guía de marca ni reglamento.
2. Calibri en títulos y cuerpo, Consolas en código. Pedido textual sobre el catálogo: «Suma Calibri, Sans, Arial y algunas mas, que respeten la integridad formal / academica / cientifica»; «Sans» es la categoría Sans Serif.
3. `#2E74B5`. Los tamaños impresos 12/16/13/12 pt y los márgenes de 1,27 cm quedan solo en la plantilla Trabajo de campo.

**Regla resultante**: Calibri en títulos y cuerpo, Consolas en código y `#2E74B5` como primario. Catálogo formal: Calibri, Arial, Helvetica, Source Sans 3, Times New Roman, Cambria, Georgia, Palatino Linotype, Garamond y STIX Two Text. El usuario nombró Calibri, Arial y la categoría Sans Serif; el resto lo propuso el agente porque el usuario pidió sumar «algunas más». Los tamaños y márgenes generales no cambian.
**Aplicada en**: `references/estilo-visual.md` §4 y §5; `assets/plantilla-prompt-estilo.md`; `assets/configurador.html`.
**PR**: https://github.com/jordansep/Agents-Skills/pull/39

---

## DEC-004 · Estilo de citas

- **Estado**: confirmada
- **Alcance**: agente
- **Preguntado**: 02/11/2026 · **Respondido**: 05/11/2026
- **Origen**: creación inicial de los skills
- **Contexto**: el agente propuso APA 7 como estilo por defecto cuando un documento tiene citas.

**Preguntas**

1. ¿Qué estilo de citas se usa? Opciones: a) APA 7; b) IEEE (habitual en ingeniería y computación); c) el que fije el reglamento de la institución (indicar cuál).
2. ¿Se usa un gestor de referencias con archivo exportado? Opciones: a) sí, BibTeX (`.bib`); b) sí, otro formato; c) no, las referencias se escriben a mano.

**Respuestas**

1. APA 7.
2. BibTeX (`.bib`).

**Regla resultante**: citas en APA 7, con las referencias en un archivo BibTeX (`.bib`).
**Aplicada en**: `references/escritura.md` §3; `SKILL.md`; `assets/configurador.html`.
**PR**: https://github.com/jordansep/Agents-Skills/pull/39

---

## DEC-005 · Ubicación del prompt y de la documentación

- **Estado**: confirmada
- **Alcance**: agente
- **Preguntado**: 02/11/2026 · **Respondido**: 05/11/2026
- **Origen**: creación inicial de los skills
- **Contexto**: el agente propuso guardar el prompt en `docs/prompt-estilo.md` y cada documento en una carpeta bajo `docs/`.

**Preguntas**

1. ¿Dónde se guarda el prompt de estilo? Opciones: a) `docs/prompt-estilo.md`, uno por proyecto; b) uno por documento, dentro de su carpeta (`docs/<documento>/prompt-estilo.md`).
2. ¿Dónde se guardan los documentos? Opciones: a) `docs/<documento>/`; b) otra ruta (indicarla).

**Respuestas**

1. `docs/prompt-estilo.md`, uno por proyecto.
2. `docs/<documento>/`.

**Regla resultante**: un prompt por proyecto en `docs/prompt-estilo.md` y cada documento en `docs/<documento>/`.
**Aplicada en**: `SKILL.md`; `assets/configurador.html`.
**PR**: https://github.com/jordansep/Agents-Skills/pull/39

---

## DEC-006 · Comillas

- **Estado**: confirmada
- **Alcance**: agente
- **Preguntado**: 02/11/2026 · **Respondido**: 05/11/2026
- **Origen**: creación inicial de los skills
- **Contexto**: `escritura.md` §3 recomienda comillas dobles (“ ”) y admite las angulares (« ») si la institución las pide. No hay una elección confirmada.

**Preguntas**

1. ¿Qué comillas se usan? Opciones: a) dobles inglesas “así”; b) angulares «así» (recomendación de la RAE); c) rectas "así" (más simples de escribir en Markdown).

**Respuestas**

1. Dobles “así”.

**Regla resultante**: se usan comillas dobles (“así”).
**Aplicada en**: `references/escritura.md` §3; `assets/plantilla-prompt-estilo.md`; `assets/configurador.html`.
**PR**: https://github.com/jordansep/Agents-Skills/pull/39

---

## DEC-007 · Plantillas tomadas de documentos de referencia

- **Estado**: parcial (lo uniforme está confirmado; las preguntas siguen abiertas)
- **Alcance**: agente
- **Preguntado**: 02/11/2026 · **Respondido**: 02/11/2026 (en parte)
- **Origen**: el usuario entregó documentos propios y dijo: «Estos documentos son en cuanto a diseño lo que yo quiero o necesito».
- **Documentos**: *Trabajo de Campo v3.6* (.docx), *TdC v2.2* (.pdf), *Ponderación de metodologías v3* (.docx), *Proforma de entrevista académica* (.pdf), *State 1-pager* (.pdf), *Arquitectura del sistema de gestión y aula virtual* (.pdf), *Informe de relevamiento y diseño de arquitectura* (informe_av_v2.docx), *Informe de completitud — Hemocentro* (.pdf), *mermaid.html* y cinco imágenes de diagramas (contexto, organigrama, dos secuencias AS-IS y casos de uso).

**Respuesta**: el diseño de esos documentos es el que se quiere. Lo que cada uno hace de forma uniforme quedó como regla en `references/plantillas/`.

**Preguntas abiertas** (detalladas en «Puntos abiertos» de cada plantilla):

1. Trabajo de campo: numeración y mayúsculas de los títulos, cuerpo de 11 o 12 pt, color de las notas, alineación del H2, interlineado de las actas, y si la v3.6 (Calibri, A4) reemplaza a la v2.2 (Times, Carta).
2. Informe técnico: papel Carta o A4, tablas sin leyenda o con APA 7, y si se unifican sus colores con los del Trabajo de campo.
3. Diagramas: si el de casos de uso estilo Mermaid se redibuja con el estilo de lámina y si se nombra a las personas o solo su rol. La parte de Mermaid (si queda solo para la documentación web) la responde DEC-011.
4. Proforma: dónde va el código del formulario y cuántas líneas de respuesta por pregunta.
5. Ficha 1-pager: Arial o la familia del documento principal.
6. Arquitectura en láminas: número de página y pie, y si el formato sirve para otros entregables.
7. Informe de auditoría: PDF solo, o también Markdown.

**Regla resultante**: cuando el prompt declara `plantilla`, su diseño manda sobre `estilo-visual.md`. El verificador acepta las leyendas APA 7 cuando la plantilla las usa o el prompt dice `leyendas: apa7`. El configurador tiene un preajuste para cada plantilla y escribe el campo `plantilla` en el prompt.
**Aplicada en**: `references/plantillas/`, `SKILL.md`, `references/estilo-visual.md`, `assets/configurador.html`, `assets/plantilla-prompt-estilo.md`, `../documentacion-generar/SKILL.md`.
**PR**: —

---

## DEC-008 · Entregas en varios archivos

- **Estado**: confirmada
- **Alcance**: agente
- **Preguntado**: 05/11/2026 · **Respondido**: 05/11/2026
- **Origen**: issue #15, historia 3 del Sprint 1
- **Contexto**: `documentacion-generar` ya admite un archivo por capítulo con numeración continua, y el issue pide un campo `entrega: unico | multiarchivo` sin aclarar cómo conviven.

**Preguntas**

1. ¿Cómo conviven `multiarchivo` y «un archivo por capítulo»? Opciones: a) `unico` es un documento lógico, aunque esté partido por capítulos y con numeración continua; `multiarchivo` es una entrega con puntos independientes y numeración con prefijo; si el campo falta, vale `unico` (recomendada: los prompts existentes siguen funcionando); b) otra distinción.

**Respuestas**

1. Opción a.

**Regla resultante**: `entrega: unico` es un documento lógico, en uno o varios archivos, con numeración continua. `entrega: multiarchivo` es una entrega con un archivo índice y un archivo por punto. Si el campo falta, vale `unico`.
**Aplicada en**: `SKILL.md`, `../documentacion-generar/SKILL.md`, `../documentacion-generar/scripts/verificar_doc.py`, `assets/configurador.html`, `assets/plantilla-prompt-estilo.md`, `references/estilo-visual.md`.
**PR**: https://github.com/jordansep/Agents-Skills/pull/40

---

## DEC-009 · Numeración de tablas y figuras en entregas multiarchivo

- **Estado**: confirmada
- **Alcance**: agente
- **Preguntado**: 05/11/2026 · **Respondido**: 05/11/2026
- **Origen**: issue #15, historia 3 del Sprint 1
- **Contexto**: el issue pide `Tabla 4.1`, pero el estilo y el verificador exigen numeración continua, y las leyendas APA 7 usan un entero.

**Preguntas**

1. ¿De dónde sale el prefijo? Opciones: a) del número del archivo, y las tablas del índice van sin prefijo (recomendada: el nombre del archivo ya fija el orden); b) otra fuente.
2. ¿Qué pasa con APA 7? Opciones: a) admitir `Tabla 4.1` con APA cuando la entrega es `multiarchivo`, como excepción explícita (recomendada: una sola regla para toda entrega multiarchivo); b) mantener la numeración continua con APA 7.

**Respuestas**

1. Opción a.
2. Opción a.

**Regla resultante**: en una entrega `multiarchivo`, tablas y figuras se numeran por archivo con el número del archivo como prefijo (`04 - …` da `Tabla 4.1`), y las del índice van sin prefijo (`Tabla 1`). Con leyendas APA 7 se mantiene su formato y se admite ese número, como excepción explícita a APA 7. Con `entrega: unico`, la numeración sigue siendo continua.
**Aplicada en**: `../documentacion-generar/SKILL.md`, `../documentacion-generar/scripts/verificar_doc.py`, `assets/configurador.html`, `assets/plantilla-prompt-estilo.md`, `references/estilo-visual.md`.
**PR**: https://github.com/jordansep/Agents-Skills/pull/40

---

## DEC-010 · Control de versiones desde git

- **Estado**: confirmada
- **Alcance**: agente
- **Preguntado**: 05/11/2026 · **Respondido**: 05/11/2026
- **Origen**: issue #15, historia 3 del Sprint 1
- **Contexto**: el issue pide un control de versiones «alimentado por git», pero git da fechas, autores y mensajes, no versiones del documento.

**Preguntas**

1. ¿Qué significa «alimentado por git»? Opciones: a) el agente propone las filas desde el `git log` de la carpeta, el usuario confirma versión y descripción, y el verificador solo controla que haya una única tabla en el índice; sin repositorio queda `[PENDIENTE]` (recomendada: la versión y la descripción no salen de git); b) generar las filas sin confirmación.

**Respuestas**

1. Opción a.

**Regla resultante**: una entrega `multiarchivo` tiene un solo control de versiones, en el índice. El agente propone las filas desde el `git log` de la carpeta de la entrega y el usuario confirma la versión y la descripción. Sin repositorio, las filas quedan como `[PENDIENTE]`.
**Aplicada en**: `../documentacion-generar/SKILL.md`, `../documentacion-generar/scripts/verificar_doc.py`, `assets/configurador.html`, `assets/plantilla-prompt-estilo.md`, `references/estilo-visual.md`.
**PR**: https://github.com/jordansep/Agents-Skills/pull/40


## DEC-011 · Mermaid como fuente editable de los diagramas

- **Estado**: confirmada
- **Alcance**: agente
- **Preguntado**: 05/11/2026 · **Respondido**: 05/11/2026
- **Origen**: análisis previo de la historia 4 (#16)
- **Contexto**: el issue #16 traduce los diagramas a Mermaid, pero `references/plantillas/diagramas.md` dice que se dibujan como SVG o HTML, y la pregunta 3 de DEC-007 seguía abierta.

**Preguntas**

1. ¿Qué papel cumple Mermaid? Opciones: a) fuente editable en todos los casos, con el estilo de lámina resuelto en #18 (recomendada: #16 no depende de cerrar el diseño visual); b) solo para la documentación web.

**Respuestas**

1. Opción a, la recomendada.

**Regla resultante**: la traducción de un diagrama siempre produce Mermaid como fuente editable. La traducción no busca reproducir el estilo de lámina: eso se resuelve en #18. Responde la parte de Mermaid de la pregunta 3 de DEC-007.
**Aplicada en**: `references/imagenes.md` §4; `references/plantillas/diagramas.md` §6; `../documentacion-generar/SKILL.md`.
**PR**: https://github.com/jordansep/Agents-Skills/pull/41


## DEC-012 · Diagramas sin tipo propio en Mermaid

- **Estado**: confirmada
- **Alcance**: agente
- **Preguntado**: 05/11/2026 · **Respondido**: 05/11/2026
- **Origen**: análisis previo de la historia 4 (#16)
- **Contexto**: el issue pide Mermaid «en la notación del prompt», pero Mermaid no tiene un tipo propio para casos de uso ni para BPMN.

**Preguntas**

1. ¿Qué se hace con esos diagramas? Opciones: a) aproximarlos con `flowchart` y marcarlos como aproximación (recomendada: cumple el criterio de casos de uso sin inventar notación); b) dejarlos como imagen.

**Respuestas**

1. Opción a, la recomendada.

**Regla resultante**: lo que no tenga tipo propio en Mermaid se traduce con `flowchart` y se marca como «aproximación» en `figuras/inventario.md`.
**Aplicada en**: `references/imagenes.md` §4 y §6; `../documentacion-generar/SKILL.md`.
**PR**: https://github.com/jordansep/Agents-Skills/pull/41


## DEC-013 · Alcance de la extracción de imágenes

- **Estado**: confirmada
- **Alcance**: agente
- **Preguntado**: 05/11/2026 · **Respondido**: 05/11/2026
- **Origen**: análisis previo de la historia 4 (#16)
- **Contexto**: un documento de Word puede traer muchas imágenes, algunas mínimas o repetidas, y formas de dibujo que no son archivos de imagen. Además, un diagrama vectorial de un PDF no es una imagen incrustada.

**Preguntas**

1. ¿Qué entra en el alcance? Opciones: a) filtrar imágenes mínimas y repetidas, convertir a PNG las páginas de PDF con dibujo vectorial y listar las formas de Word como «no extraídas» (recomendada); b) dejar lo vectorial para otra historia.

**Respuestas**

1. Opción a, la recomendada.

**Regla resultante**: la extracción descarta las imágenes mínimas y repetidas antes de la lectura visual, convierte a PNG las páginas de PDF con dibujo vectorial y lista las formas de Word como «no extraídas».
**Aplicada en**: `scripts/extraer_imagenes.py`; `references/imagenes.md` §1.
**PR**: https://github.com/jordansep/Agents-Skills/pull/41


## DEC-014 · Umbral de imagen mínima

- **Estado**: confirmada
- **Alcance**: agente
- **Preguntado**: 05/11/2026 · **Respondido**: 05/11/2026
- **Origen**: historia 4 (#16)
- **Contexto**: DEC-013 descarta las imágenes mínimas, pero no dice cuándo una imagen lo es.

**Preguntas**

1. ¿Cuándo una imagen es mínima?

**Respuestas**

1. Cuando su lado menor mide menos de 32 px.

**Regla resultante**: una imagen es mínima si su lado menor mide menos de 32 px. Una imagen de exactamente 32 px de lado menor se conserva. El umbral se puede cambiar por ejecución con `--lado-minimo`.
**Aplicada en**: `scripts/extraer_imagenes.py`; `references/imagenes.md` §1.
**PR**: https://github.com/jordansep/Agents-Skills/pull/41
