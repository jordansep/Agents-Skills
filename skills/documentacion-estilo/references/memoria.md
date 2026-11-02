# Memoria de estilo: casos no definidos y mejora incremental

Estas reglas son del agente de documentación (skills `documentacion-estilo` y `documentacion-generar`), no del repositorio donde se use. El agente trabaja siempre con el mismo estilo, guardado en su memoria (`memoria/decisiones.md`, dentro de este skill), y **no decide nada por su cuenta**. Si aparece algo que el estilo no cubre, pregunta al usuario, registra las preguntas y las respuestas en la memoria, incorpora la regla al skill y envía la memoria al repositorio del agente con un pull request.

## 1. Fuentes del estilo y prioridad

1. `memoria/decisiones.md`: decisiones **confirmadas** por el usuario. Mandan sobre todo lo demás.
2. `docs/prompt-estilo.md` (o el prompt del documento en curso).
3. Las referencias del skill: `metodologias.md`, `estilo-visual.md` y `escritura.md`.

Lee `memoria/decisiones.md` antes de empezar cualquier tarea de documentación.

## 2. Qué cuenta como caso no definido

Es cualquier elemento que el documento necesita y que ninguna de las fuentes anteriores resuelve de forma explícita. Por ejemplo:

- Un tipo de documento o una metodología que no está en `metodologias.md`.
- Un componente sin formato definido: una línea de tiempo, una matriz de trazabilidad con otras columnas, una tabla con celdas combinadas, un formulario.
- Una notación de diagrama, un tipo de cita o una norma institucional nueva.
- Un parámetro del encargo que el usuario no indicó y que no está fijado en la memoria (tipo, metodología, audiencia, medio, variante, tratamiento, citas, formato).
- Una contradicción entre dos reglas, o entre una regla y un pedido del usuario.
- Una decisión que en `decisiones.md` figura como **pendiente** y que el documento en curso necesita.

Si dudas de si algo está definido, trátalo como no definido y pregunta.

## 3. Procedimiento

### 3.1 Detener solo lo afectado

No escribas la parte afectada. Sigue con el resto del documento si no depende de esa decisión. En el lugar afectado, escribe `[PENDIENTE: estilo no definido, ver DEC-NNN]`.

### 3.2 Preguntar

Haz una serie de preguntas cerradas, de una a cuatro por caso. Cada pregunta:

- Nombra el caso concreto y el documento donde apareció.
- Ofrece de dos a cuatro opciones, con un ejemplo breve de cómo se vería cada una.
- Puede marcar una opción como recomendada, con el motivo en una línea. Recomendar no es decidir: sin respuesta del usuario, no se aplica.
- Pregunta también **el alcance**: si la regla vale solo para este documento o para todos los documentos del agente.

Si la herramienta de preguntas está disponible, úsala. Si no, escribe las preguntas numeradas en el chat.

### 3.3 Registrar las preguntas de inmediato

Antes de esperar la respuesta, agrega una entrada en `memoria/decisiones.md` con estado `pendiente` y las preguntas tal como se hicieron. Así no se pierden si la sesión termina.

### 3.4 Registrar las respuestas e incorporar la regla

Cuando el usuario responde:

1. Completa la entrada con las respuestas, la regla resultante y la fecha. Cambia el estado a `confirmada`, o a `descartada` si el usuario decide no fijar regla.
2. Si el alcance es todo el agente, escribe la regla en la referencia que corresponda (`metodologias.md`, `estilo-visual.md`, `escritura.md` o la plantilla del prompt). Marca la regla con `(DEC-NNN)` para poder rastrearla.
3. Si el alcance es solo un documento, escribe la regla en el prompt de estilo de ese documento.
4. Reemplaza los `[PENDIENTE: estilo no definido, ver DEC-NNN]` del documento con contenido que siga la nueva regla.

### 3.5 Enviar la memoria al repositorio del agente

El repositorio del agente es el que contiene la carpeta de este skill (por ejemplo, `Agents-Skills`). Puede no ser el proyecto que se está documentando. Si el skill está instalado mediante un enlace simbólico, la ruta real de `memoria/` indica a qué repositorio pertenece. No escribas la memoria ni las reglas del agente en archivos generales del proyecto, como `CLAUDE.md` o plantillas de PR de todo el repositorio.

1. Rama: usa la que indique el entorno de trabajo. Si no indica ninguna, crea `estilo/DEC-NNN-tema` desde la rama principal.
2. Commit con los archivos de memoria y las referencias modificadas. Mensaje: `estilo: DEC-NNN tema`.
3. Abre un pull request hacia la rama principal. El título es `Estilo: DEC-NNN tema` y el cuerpo sigue `assets/plantilla-pr.md` de este skill, con tres secciones obligatorias:
   - **Qué**: las decisiones registradas y las reglas agregadas o modificadas, con sus archivos.
   - **Por qué**: el caso que surgió, en qué documento, y por qué el estilo no lo cubría.
   - **Cómo**: las preguntas hechas, las respuestas del usuario y dónde se incorporó cada regla.
4. Si la sesión va a terminar con preguntas sin responder, envía igual la entrada `pendiente` en un pull request. En la nube, lo que no está en el repositorio del agente se pierde.

## 4. Formato de una entrada en `decisiones.md`

```markdown
## DEC-NNN · Tema corto

- **Estado**: pendiente | confirmada | descartada
- **Alcance**: agente | documento <nombre>
- **Preguntado**: dd/mm/aaaa · **Respondido**: dd/mm/aaaa
- **Origen**: documento o tarea donde surgió
- **Contexto**: qué apareció y por qué el estilo no lo cubría

**Preguntas**

1. ¿Pregunta? Opciones: a) ... (recomendada: motivo); b) ...; c) ...

**Respuestas**

1. Opción elegida o respuesta textual del usuario.

**Regla resultante**: texto exacto de la regla.
**Aplicada en**: archivo y sección.
**PR**: enlace.
```

Los números DEC son correlativos y nunca se reutilizan. Si una decisión reemplaza a otra, la nueva lo indica ("Reemplaza a DEC-NNN") y la anterior pasa a `descartada`.
