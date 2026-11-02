# Registro de decisiones de estilo

Memoria persistente del agente de documentación (skills `documentacion-estilo` y `documentacion-generar`). Vale para todos los documentos que produzca el agente, en cualquier proyecto. El procedimiento está en `../references/memoria.md`.

- Las decisiones **confirmadas** mandan sobre las referencias del skill.
- Las decisiones **pendientes** son preguntas que el usuario todavía no respondió. Si el documento en curso las necesita, se hacen antes de escribir la parte afectada.

## Índice

| ID | Tema | Estado | Alcance |
|---|---|---|---|
| DEC-001 | Tratamiento y variante del español | pendiente | agente |
| DEC-002 | Convención de números | pendiente | agente |
| DEC-003 | Tipografía y paleta de color | pendiente | agente |
| DEC-004 | Estilo de citas | pendiente | agente |
| DEC-005 | Ubicación del prompt y de la documentación | pendiente | agente |
| DEC-006 | Comillas | pendiente | agente |
| DEC-007 | Plantillas tomadas de documentos de referencia | parcial | agente |

---

## DEC-001 · Tratamiento y variante del español

- **Estado**: pendiente
- **Alcance**: agente
- **Preguntado**: 02/11/2026 · **Respondido**: —
- **Origen**: creación inicial de los skills
- **Contexto**: el agente propuso por su cuenta español neutro, "usted" en manuales e impersonal en tesis y especificaciones. El usuario no lo confirmó. Los valores están en `escritura.md` §3 y §4 y en la tabla del Paso 1 de `SKILL.md`.

**Preguntas**

1. ¿Qué variante del español se usa? Opciones: a) neutro (recomendada: el documento llega a más lectores); b) rioplatense con voseo.
2. ¿Qué tratamiento se usa en manuales? Opciones: a) usted ("Seleccione el archivo"); b) tú ("Selecciona el archivo"); c) vos ("Seleccioná el archivo").
3. ¿Qué tratamiento se usa en tesis y especificaciones? Opciones: a) impersonal ("Se propone un modelo"; recomendada: es lo habitual en textos académicos); b) primera persona del plural ("Proponemos un modelo").

**Respuestas**: —

**Regla resultante**: —
**Aplicada en**: —
**PR**: —

---

## DEC-002 · Convención de números

- **Estado**: pendiente
- **Alcance**: agente
- **Preguntado**: 02/11/2026 · **Respondido**: —
- **Origen**: creación inicial de los skills
- **Contexto**: el agente propuso coma decimal, espacio para miles, espacio antes de % y fechas dd/mm/aaaa (`escritura.md` §3). El verificador lo controla con el campo `decimal: coma`.

**Preguntas**

1. ¿Qué separador decimal se usa? Opciones: a) coma, `3,5` (recomendada: norma RAE y uso en Argentina); b) punto, `3.5`.
2. ¿Cómo se separan los miles? Opciones: a) espacio, `12 500`; b) punto, `12.500`; c) sin separación.
3. ¿El símbolo % va con espacio? Opciones: a) sí, `15 %` (norma RAE); b) no, `15%`.

**Respuestas**: —

**Regla resultante**: —
**Aplicada en**: —
**PR**: —

---

## DEC-003 · Tipografía y paleta de color

- **Estado**: pendiente
- **Alcance**: agente
- **Preguntado**: 02/11/2026 · **Respondido**: —
- **Origen**: creación inicial de los skills
- **Contexto**: el agente propuso Inter o Source Sans 3 para documentos digitales, Times New Roman 12 o Arial 11 para impresos y una paleta de tokens con contraste AA verificado (`estilo-visual.md` §4 y §5). No hay guía de marca confirmada.

**Preguntas**

1. ¿Hay una guía de marca o un reglamento institucional que fije la tipografía y los colores? Opciones: a) sí (adjuntarla); b) no, usar la propuesta actual; c) no, pero se quiere otra propuesta.
2. ¿Qué familia se usa en documentos digitales? Opciones: a) Inter; b) Source Sans 3; c) otra.
3. ¿Qué color primario se usa? Opciones: a) azul `#1F4E79` (actual); b) color institucional (indicar el código).

**Respuestas**: —

**Regla resultante**: —
**Aplicada en**: —
**PR**: —

---

## DEC-004 · Estilo de citas

- **Estado**: pendiente
- **Alcance**: agente
- **Preguntado**: 02/11/2026 · **Respondido**: —
- **Origen**: creación inicial de los skills
- **Contexto**: el agente propuso APA 7 como estilo por defecto cuando un documento tiene citas.

**Preguntas**

1. ¿Qué estilo de citas se usa? Opciones: a) APA 7; b) IEEE (habitual en ingeniería y computación); c) el que fije el reglamento de la institución (indicar cuál).
2. ¿Se usa un gestor de referencias con archivo exportado? Opciones: a) sí, BibTeX (`.bib`); b) sí, otro formato; c) no, las referencias se escriben a mano.

**Respuestas**: —

**Regla resultante**: —
**Aplicada en**: —
**PR**: —

---

## DEC-005 · Ubicación del prompt y de la documentación

- **Estado**: pendiente
- **Alcance**: agente
- **Preguntado**: 02/11/2026 · **Respondido**: —
- **Origen**: creación inicial de los skills
- **Contexto**: el agente propuso guardar el prompt en `docs/prompt-estilo.md` y cada documento en una carpeta bajo `docs/`.

**Preguntas**

1. ¿Dónde se guarda el prompt de estilo? Opciones: a) `docs/prompt-estilo.md`, uno por proyecto; b) uno por documento, dentro de su carpeta (`docs/<documento>/prompt-estilo.md`).
2. ¿Dónde se guardan los documentos? Opciones: a) `docs/<documento>/`; b) otra ruta (indicarla).

**Respuestas**: —

**Regla resultante**: —
**Aplicada en**: —
**PR**: —

---

## DEC-006 · Comillas

- **Estado**: pendiente
- **Alcance**: agente
- **Preguntado**: 02/11/2026 · **Respondido**: —
- **Origen**: creación inicial de los skills
- **Contexto**: `escritura.md` §3 recomienda comillas dobles (“ ”) y admite las angulares (« ») si la institución las pide. No hay una elección confirmada.

**Preguntas**

1. ¿Qué comillas se usan? Opciones: a) dobles inglesas “así”; b) angulares «así» (recomendación de la RAE); c) rectas "así" (más simples de escribir en Markdown).

**Respuestas**: —

**Regla resultante**: —
**Aplicada en**: —
**PR**: —

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
3. Diagramas: si el de casos de uso estilo Mermaid se redibuja con el estilo de lámina, si se nombra a las personas o solo su rol, y si Mermaid queda solo para la documentación web.
4. Proforma: dónde va el código del formulario y cuántas líneas de respuesta por pregunta.
5. Ficha 1-pager: Arial o la familia del documento principal.
6. Arquitectura en láminas: número de página y pie, y si el formato sirve para otros entregables.
7. Informe de auditoría: PDF solo, o también Markdown.

**Regla resultante**: cuando el prompt declara `plantilla`, su diseño manda sobre `estilo-visual.md`. El configurador tiene un preajuste para cada plantilla y escribe el campo `plantilla` en el prompt.
**Aplicada en**: `references/plantillas/`, `SKILL.md`, `references/estilo-visual.md`, `assets/configurador.html`, `assets/plantilla-prompt-estilo.md`, `../documentacion-generar/SKILL.md`.
**PR**: —
