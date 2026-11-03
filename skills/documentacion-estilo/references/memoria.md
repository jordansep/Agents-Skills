# Memoria de estilo: casos no definidos y mejora incremental

Estas reglas son del agente de documentación (skills `documentacion-estilo` y `documentacion-generar`). El agente **no decide nada por su cuenta**. Si aparece algo que el estilo no cubre, pregunta al usuario, registra las preguntas y las respuestas en la memoria que corresponda e incorpora la regla.

La memoria tiene dos niveles, y cada uno vive en su propio repositorio:

| Nivel | Archivo | Repositorio | Qué guarda | IDs |
|---|---|---|---|---|
| **Agente** | `memoria/decisiones.md`, dentro de este skill | El del agente (el que contiene este skill, por ejemplo `Agents-Skills`) | Reglas que valen para **todos** los documentos del agente | `DEC-NNN` |
| **Proyecto** | `decisiones-estilo.md`, en la misma carpeta que el prompt de estilo del proyecto (por defecto `docs/`) | El del proyecto que se documenta | Decisiones que valen **solo** para ese proyecto | `DP-NNN` |

Nunca escribas en la memoria del agente una decisión de un solo proyecto, ni en la memoria de un proyecto una regla de todo el agente. Las dos numeraciones son independientes: cada proyecto empieza en `DP-001`.

### Aislamiento entre repositorios

Una sesión solo escribe en el repositorio donde se trabaja (el directorio de trabajo de la sesión):

- **La carpeta instalada del skill es de solo lectura.** No edites, crees ni borres archivos dentro de ella (incluida `memoria/decisiones.md`), aunque el sistema de archivos lo permita. Se instala con `scripts/instalar_skills.ps1` del repositorio del agente, desde una copia fija en `origin/main`.
- **Desde otro repositorio**, no abras ramas, commits ni PRs en el repositorio del agente. Una decisión con alcance de agente que surja ahí se registra en la memoria **del proyecto** con estado `propuesta` (ver §3.4). Al usuario se le avisa en el informe final que hay propuestas para llevar al agente.
- **Desde el repositorio del agente** (el directorio de trabajo es, por ejemplo, `Agents-Skills`), las propuestas se incorporan a `memoria/decisiones.md` de esa carpeta de trabajo, no de la copia instalada, y se envían con un PR (§3.6).

## 1. Fuentes del estilo y prioridad

1. La memoria del proyecto: decisiones **confirmadas** en `decisiones-estilo.md`. Mandan dentro de ese proyecto.
2. La memoria del agente: decisiones **confirmadas** en `memoria/decisiones.md`.
3. El prompt de estilo del documento en curso (`docs/prompt-estilo.md` o el que indique el usuario).
4. Las referencias del skill: `metodologias.md`, `estilo-visual.md` y `escritura.md`.

Antes de empezar cualquier tarea de documentación, lee las dos memorias. Si el proyecto todavía no tiene `decisiones-estilo.md`, no lo crees hasta que haya una decisión de proyecto que registrar.

Si una decisión del proyecto contradice una confirmada del agente, la del proyecto manda solo en ese proyecto, y su entrada lo indica («Se aparta de DEC-NNN»).

## 2. Qué cuenta como caso no definido

Es cualquier elemento que el documento necesita y que ninguna de las fuentes anteriores resuelve de forma explícita. Por ejemplo:

- Un tipo de documento o una metodología que no está en `metodologias.md`.
- Un componente sin formato definido: una línea de tiempo, una matriz de trazabilidad con otras columnas, una tabla con celdas combinadas, un formulario.
- Una notación de diagrama, un tipo de cita o una norma institucional nueva.
- Un parámetro del encargo que el usuario no indicó y que no está fijado en ninguna de las dos memorias (tipo, metodología, propósito, ámbito, lector, medio, variante, tratamiento, citas, formato).
- Una contradicción entre dos reglas, o entre una regla y un pedido del usuario.
- Una decisión que figura como **pendiente** y que el documento en curso necesita.

Si dudas de si algo está definido, trátalo como no definido y pregunta.

## 3. Procedimiento

### 3.1 Detener solo lo afectado

No escribas la parte afectada. Sigue con el resto del documento si no depende de esa decisión. En el lugar afectado, escribe `[PENDIENTE: estilo no definido, ver DEC-NNN]` (o `DP-NNN` si la pregunta es del proyecto).

### 3.2 Preguntar

Haz una serie de preguntas cerradas, de una a cuatro por caso. Cada pregunta:

- Nombra el caso concreto y el documento donde apareció.
- Ofrece de dos a cuatro opciones, con un ejemplo breve de cómo se vería cada una.
- Puede marcar una opción como recomendada, con el motivo en una línea. Recomendar no es decidir: sin respuesta del usuario, no se aplica.
- Pregunta también **el alcance**: si la regla vale solo para este proyecto o para todos los documentos del agente. El alcance decide en qué memoria se guarda.

Si la herramienta de preguntas está disponible, úsala. Si no, escribe las preguntas numeradas en el chat. Si las preguntas son sobre parámetros que cubre el configurador (`assets/configurador.html`), ábrelo en el navegador del usuario en lugar de preguntar en la terminal (ver el Paso 1 de `SKILL.md`). El prompt que descargue y las respuestas de su pestaña "Para la memoria" se registran igual que las del chat.

### 3.3 Registrar las preguntas de inmediato

Antes de esperar la respuesta, agrega una entrada con estado `pendiente` y las preguntas tal como se hicieron. Así no se pierden si la sesión termina.

- Si el caso es propio del proyecto (un formato que solo usa ese documento, una consigna de cátedra, una excepción local), regístralo en `decisiones-estilo.md` del proyecto.
- Si puede valer para todo el agente, o todavía no se sabe el alcance:
  - en una sesión **del repositorio del agente**, regístralo en `memoria/decisiones.md` de esa carpeta de trabajo;
  - en una sesión **de otro repositorio**, regístralo también en `decisiones-estilo.md` del proyecto, como `DP-NNN`. Nunca en la carpeta instalada del skill.

### 3.4 Registrar las respuestas e incorporar la regla

Cuando el usuario responde:

1. Completa la entrada con las respuestas, la regla resultante y la fecha. Cambia el estado a `confirmada`, o a `descartada` si el usuario decide no fijar regla.
2. **Alcance de agente**:
   - En una sesión del repositorio del agente: la entrada queda en `memoria/decisiones.md`. Escribe la regla en la referencia que corresponda (`metodologias.md`, `estilo-visual.md`, `escritura.md` o la plantilla del prompt) y márcala con `(DEC-NNN)`.
   - En una sesión de otro repositorio: la entrada queda en `decisiones-estilo.md` del proyecto con estado `propuesta` y alcance `agente`. La regla se aplica ya en el prompt de ese proyecto, marcada con `(DP-NNN)`. En el informe final, avisa al usuario que para incorporarla al agente tiene que abrir una sesión en el repositorio del agente y pedir «incorporar las propuestas de <ruta del decisiones-estilo.md>». Esa sesión la copia como `DEC-NNN`, la envía con un PR (§3.6) y, después del merge, la entrada del proyecto pasa a `confirmada` con «Incorporada como DEC-NNN».
3. **Alcance de proyecto**: la entrada va a `decisiones-estilo.md` del proyecto con un `DP-NNN`. Escribe la regla solo en el prompt de estilo del proyecto y márcala con `(DP-NNN)`. Si la pregunta se había registrado como `DEC-NNN` pendiente en el agente, quítala de la memoria del agente cuando el usuario elija este alcance, salvo que la DEC sea una de las decisiones generales (DEC-001 a DEC-006): esas siguen pendientes para el agente.
4. Reemplaza los `[PENDIENTE: estilo no definido, ver ...]` del documento con contenido que siga la nueva regla.

### 3.5 Guardar la memoria del proyecto

La memoria del proyecto se guarda en el repositorio del proyecto, junto con el prompt de estilo:

1. Si no existe, crea `decisiones-estilo.md` a partir de `assets/plantilla-decisiones-proyecto.md`, en la misma carpeta que el prompt de estilo.
2. Haz commit en el repositorio del proyecto, en la rama de trabajo de esa tarea. Mensaje: `estilo: DP-NNN tema`.
3. No abras un PR en el repositorio del agente ni subas su versión: el agente no cambió.

### 3.6 Enviar la memoria del agente a su repositorio

Solo para decisiones con alcance de agente, y **solo desde una sesión cuyo directorio de trabajo es el repositorio del agente** (por ejemplo, `Agents-Skills`). Desde cualquier otro repositorio, no se hace: se deja la propuesta en la memoria del proyecto (§3.4). Trabaja sobre la carpeta de trabajo de esa sesión, nunca sobre la copia instalada del skill. No escribas la memoria ni las reglas del agente en archivos generales de un proyecto, como `CLAUDE.md` o plantillas de PR de todo el repositorio.

1. Rama: usa la que indique el entorno de trabajo. Si no indica ninguna, crea `estilo/DEC-NNN-tema` desde la rama principal.
2. Sube la versión del agente desde la raíz de su repositorio, según `VERSIONADO.md`:
   - **MINOR** si se confirmó una regla con alcance de agente: `python3 scripts/versionado.py subir documentacion minor --agregado "DEC-NNN: regla"` (o `--cambiado` si modifica una regla existente).
   - **PATCH** si solo se registraron preguntas pendientes: `python3 scripts/versionado.py subir documentacion patch --cambiado "DEC-NNN: preguntas pendientes sobre tema"`.
   - **Varias decisiones en el mismo PR**: se sube una sola vez, con el nivel más alto que corresponda y una entrada por decisión.
3. Commit con los archivos de memoria, las referencias modificadas, `agentes/documentacion/agente.json` y `agentes/documentacion/CHANGELOG.md`. Mensaje: `estilo: DEC-NNN tema`.
4. Abre un pull request hacia la rama principal. El título es `Estilo: DEC-NNN tema` y el cuerpo sigue `assets/plantilla-pr.md` de este skill, con tres secciones obligatorias:
   - **Qué**: las decisiones registradas, las reglas agregadas o modificadas con sus archivos, y la versión del agente (anterior → nueva).
   - **Por qué**: el caso que surgió, en qué documento, y por qué el estilo no lo cubría.
   - **Cómo**: las preguntas hechas, las respuestas del usuario y dónde se incorporó cada regla.
5. Si la sesión va a terminar con preguntas de alcance de agente sin responder, envía igual la entrada `pendiente` en un pull request. En la nube, lo que no está en el repositorio del agente se pierde.

## 4. Formato de una entrada

El mismo formato sirve para las dos memorias. En la del agente el ID es `DEC-NNN` y el alcance es siempre `agente`. En la del proyecto el ID es `DP-NNN` y el alcance es `proyecto`.

```markdown
## DEC-NNN · Tema corto

- **Estado**: pendiente | confirmada | descartada | propuesta (solo en la memoria del proyecto: regla para el agente que todavía no se incorporó)
- **Alcance**: agente | proyecto
- **Preguntado**: dd/mm/aaaa · **Respondido**: dd/mm/aaaa
- **Origen**: documento o tarea donde surgió
- **Contexto**: qué apareció y por qué el estilo no lo cubría

**Preguntas**

1. ¿Pregunta? Opciones: a) ... (recomendada: motivo); b) ...; c) ...

**Respuestas**

1. Opción elegida o respuesta textual del usuario.

**Regla resultante**: texto exacto de la regla.
**Aplicada en**: archivo y sección.
**PR**: enlace (en la memoria del proyecto, el commit o PR de ese repositorio).
```

Los números son correlativos dentro de cada memoria y nunca se reutilizan. Si una decisión reemplaza a otra, la nueva lo indica («Reemplaza a DEC-NNN» o «Reemplaza a DP-NNN») y la anterior pasa a `descartada`.
