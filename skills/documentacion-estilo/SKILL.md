---
name: documentacion-estilo
description: Prompteador de estilo para documentación técnica y académica. Produce un "prompt de estilo" (archivo prompt-estilo.md) que fija la estructura del documento según la metodología elegida (RUP, UP, Scrum/ágil, ISO/IEEE 29148, Diátaxis o académica), cómo se muestra cada componente (títulos, tablas, figuras, código, avisos, diagramas), la tipografía, la paleta de color y las normas de escritura. Lo primero que hace es abrir el configurador visual (assets/configurador.html) en el navegador para que el usuario elija los parámetros con vista previa, en lugar de preguntar en la terminal. Úsalo cuando el usuario quiera definir, acordar o revisar el estilo, la estructura o las normas de un manual, tesis, especificación, informe o diagrama. No decide nada por su cuenta; lo que no esté definido lo pregunta al usuario y lo guarda en su memoria (memoria/decisiones.md) para mejorar el estilo de forma incremental. Para escribir el documento completo usa documentacion-generar, que consume este prompt.
---

# Documentación: prompteador de estilo

Este skill decide cómo se ve y cómo se escribe un documento, y deja esa decisión en un archivo: el **prompt de estilo**. El skill `documentacion-generar` usa ese archivo para redactar la documentación. También funciona por sí solo como guía de estilo para revisar un documento existente.

Carga solo la referencia que necesites:

- `references/metodologias.md`: estructura de capítulos para RUP, UP, Scrum, ISO/IEEE 29148, Diátaxis, tesis, y notaciones de diagramas.
- `references/estilo-visual.md`: grilla, títulos, componentes, tipografía, paleta de color y diagramas.
- `references/escritura.md`: normas de redacción, ortotipografía, reglas por tipo de documento, catálogo de partes pretextuales y postextuales (§4 ter) y ejemplos.
- `assets/plantilla-prompt-estilo.md`: plantilla del archivo de salida.
- `assets/configurador.html`: configurador visual para que el usuario elija los parámetros, con vista previa en vivo. Genera el prompt de estilo y las respuestas para la memoria.
- `references/plantillas/`: diseños tomados de documentos que el usuario entregó como modelo (Trabajo de campo UNC, informe técnico, informe de auditoría, proforma de entrevista, ficha 1-pager, arquitectura en láminas y diagramas). Mandan sobre `estilo-visual.md` cuando el prompt los declara en `plantilla`. El `README.md` de la carpeta dice cuál usar.
- `scripts/extraer_estilo_docx.py`: extrae el diseño de un .docx de referencia (página, fuentes, títulos, tablas, leyendas, pie) para crear o revisar una plantilla.
- `references/memoria.md`: qué hacer cuando algo no está definido y cómo se guarda la memoria.
- `memoria/decisiones.md`: memoria del agente, con las decisiones que valen para todos los documentos. Se lee en el Paso 4 y en los casos no definidos.
- `assets/plantilla-decisiones-proyecto.md`: plantilla de la memoria de un proyecto (`decisiones-estilo.md`).

## Regla principal: no decidir por cuenta propia

**Aislamiento:** la carpeta instalada de este skill es de solo lectura. Una sesión solo escribe en el repositorio donde trabaja; desde otro repositorio nunca se editan los archivos del skill ni se abren ramas o PRs en el repositorio del agente (`references/memoria.md`, «Aislamiento entre repositorios»).

No elijas, infieras ni apliques por defecto nada que el usuario no haya definido. Si algo no está definido, pregunta, registra las preguntas y las respuestas en la memoria e incorpora la regla. El procedimiento completo está en `references/memoria.md`.

La memoria tiene dos niveles, cada uno en su repositorio:

- **Agente**: `memoria/decisiones.md` de este skill (IDs `DEC-NNN`). Solo reglas para todos los documentos. Solo se modifica desde una sesión en el repositorio del agente, y se envía con un PR.
- **Proyecto**: `decisiones-estilo.md` en el repositorio que se documenta, junto a su prompt de estilo (IDs `DP-NNN`). Las decisiones de ese proyecto se commitean ahí y nunca se escriben en la memoria del agente.

## Paso 1 (siempre primero): abrir el configurador

Antes de preguntar nada en la terminal, abre el configurador visual en el navegador del usuario. Ahí el usuario elige todos los parámetros, ve la vista previa y descarga el prompt de estilo.

1. La ruta es `assets/configurador.html` dentro del directorio de este skill (el directorio base que se indica al cargar el skill).
2. Ábrelo con el navegador predeterminado:
   - **Windows** (sirve desde Git Bash y desde PowerShell): `powershell.exe -NoProfile -Command "Start-Process -FilePath '<ruta completa al configurador.html>'"`
   - **macOS**: `open "<ruta completa>"`
   - **Linux**: `xdg-open "<ruta completa>"`
3. Si el comando falla o no hay entorno gráfico (SSH, contenedor), dale al usuario la ruta completa para que lo abra con doble clic.
4. Dile al usuario, en pocas líneas, qué hacer:
   - Elegir los parámetros. Si ya tiene un documento en curso, puede subirlo con **Subir documento…** y verlo con el estilo.
   - Pulsar **Descargar prompt-estilo.md**.
   - Volver a la terminal y escribir «listo».
   - Si en su pedido ya dio algún dato (por ejemplo, "un manual del sistema X"), recuérdale en qué campo ponerlo. No lo completes por él.
5. **Detente y espera.** No preguntes en la terminal los parámetros del encargo. Usa el modo terminal (anexo al final) solo si el usuario lo pide explícitamente o si no puede usar un navegador.

## Paso 2: recibir el prompt

Cuando el usuario diga que terminó:

1. Busca el archivo en este orden:
   1. La ruta que indique el usuario, o el texto que haya pegado.
   2. El `prompt-estilo*.md` más reciente de su carpeta de descargas: `~/Downloads` en macOS y Linux, y `$USERPROFILE/Downloads` en Windows (en Git Bash también es `~/Downloads`). Por ejemplo: `ls -t ~/Downloads/prompt-estilo*.md | head -1`.
2. Usa el archivo de descargas solo si se modificó en las últimas horas. Si no, pide la ruta.
3. Valida el encabezado YAML: debe tener `documento`, `tipo`, `metodologia`, `medio`, `tratamiento`, `salida` y `estructura`.
4. Copia el archivo al destino que indica su campo `prompt`, relativo al proyecto en el que trabaja el usuario. No lo borres de descargas.
5. Muestra un resumen de una línea por parámetro y la ruta donde quedó.

## Paso 3: completar lo pendiente

- Busca los `[PENDIENTE: ...]` del prompt (por ejemplo, el propósito de un capítulo nuevo o un color sin contraste suficiente). Esas son las únicas preguntas que se hacen en la terminal, de hasta cuatro por vez.
- Escribe las respuestas en el prompt y súbele la versión.
- Si el usuario quiere cambiar algo más, puede volver al configurador e importar el prompt con **Importar prompt…**.

## Paso 4: actualizar la memoria

1. Lee `memoria/decisiones.md` y, si existe, `decisiones-estilo.md` del proyecto (en la carpeta del prompt).
2. Los parámetros del prompt responden las decisiones pendientes:
   - DEC-001: `variante` y `tratamiento`.
   - DEC-002: `decimal`, `miles`, `porcentaje_con_espacio` y `formato_fecha`.
   - DEC-003: `fuente_*`, tamaños y `color_primario`.
   - DEC-004: `citas`.
   - DEC-005: `prompt` y `salida`.
   - DEC-006: `comillas`.
3. El alcance lo indica `alcance_decisiones`:
   - `agente`: en una sesión del repositorio del agente, confirma esas DEC en `memoria/decisiones.md` y envíalas con un PR. En una sesión de otro repositorio, regístralas en `decisiones-estilo.md` del proyecto con estado `propuesta` (`references/memoria.md` §3.4).
   - `documento`: las DEC del agente siguen pendientes. Registra los parámetros como una entrada `DP-NNN` en `decisiones-estilo.md` del proyecto y commitéala en ese repositorio.
4. Si una decisión **confirmada** de alguna memoria contradice el prompt, no elijas tú: pregunta al usuario cuál prevalece.
5. Las **excepciones locales** (sección 8 del prompt) son ajustes que el usuario hizo solo sobre una parte de su documento. Regístralas en la memoria del proyecto y pregunta si alguna debe pasar a ser regla del agente.
6. Guarda cada memoria en su repositorio según `references/memoria.md` (§3.5 proyecto, §3.6 agente).

## Documentos de referencia del usuario

Si el usuario entrega un documento como modelo («así lo quiero»):

1. Sigue `references/plantillas/README.md`: extrae el diseño con `scripts/extraer_estilo_docx.py` (si es .docx), conviértelo a PDF y mira la portada, una tabla y una figura.
2. Si coincide con una plantilla existente, compárala: lo que coincide la confirma y lo que difiere va a «Puntos abiertos». Si no coincide, crea una plantilla nueva.
3. No resuelvas las inconsistencias del documento por tu cuenta: pregúntalas y regístralas en DEC-007.

## Casos no definidos

Si un paso necesita algo que no está en la memoria ni en las referencias (una metodología nueva, un componente sin formato, una notación, una norma, una contradicción entre reglas), aplica `references/memoria.md`:

1. Detén solo la parte afectada y márcala con `[PENDIENTE: estilo no definido, ver DEC-NNN]`.
2. Si el caso es un parámetro que cubre el configurador, ábrelo (Paso 1) en lugar de preguntar en la terminal. Si no, haz de una a cuatro preguntas cerradas con opciones y ejemplos. Incluye una pregunta sobre el alcance: solo este documento o todos los documentos del agente.
3. Registra las preguntas con estado `pendiente` antes de esperar la respuesta: en `decisiones-estilo.md` del proyecto si el caso es propio de ese proyecto, o en `memoria/decisiones.md` si puede valer para todo el agente.
4. Con la respuesta, confirma la entrada en la memoria que corresponda al alcance. Escribe la regla en la referencia del skill (agente, `(DEC-NNN)`) o en el prompt del proyecto (proyecto, `(DP-NNN)`).
5. La memoria del proyecto se commitea en el repositorio del proyecto. La del agente se envía a su repositorio en un PR, con el cuerpo de `assets/plantilla-pr.md` (secciones Qué, Por qué y Cómo).

## Reglas no negociables

- Toda figura, tabla y diagrama tiene número, título y fuente, y se menciona en el texto.
- Todo aviso tiene etiqueta e icono. El color nunca es el único portador de significado.
- El contraste texto/fondo es de 4,5:1 como mínimo (WCAG AA). Las imágenes digitales tienen texto alternativo.
- No se inventan datos, cifras, autores, citas ni referencias. Lo que falte se marca con `[PENDIENTE]`.

## Lista de verificación para revisar un documento

- [ ] La metodología está declarada y la estructura corresponde a ella.
- [ ] El tratamiento, la variante, el medio y el estilo de citas son los mismos en todo el documento.
- [ ] Los títulos siguen la numeración definida y no llevan punto final.
- [ ] Las tablas, figuras y diagramas tienen número, título y fuente, y se citan en el texto.
- [ ] Las siglas se desarrollan al primer uso y el glosario reúne los términos técnicos.
- [ ] Los avisos usan los cuatro tipos definidos.
- [ ] Los números usan coma decimal, espacio para miles y unidades SI.
- [ ] No quedan `[PENDIENTE]` sin informar al usuario.

## Anexo: modo terminal

Úsalo solo si el usuario lo pide explícitamente o si no puede abrir un navegador. Fija estos parámetros preguntando, en una sola tanda de hasta cuatro preguntas por vez. Ofrece las opciones y marca la recomendada, pero no la apliques sin respuesta. Las decisiones confirmadas en la memoria no se vuelven a preguntar.

| Parámetro | Opciones | Recomendado |
|---|---|---|
| Tipo de documento | manual, tesis, especificación, informe, diagrama, arquitectura, otro | informe |
| Metodología | RUP, UP, Scrum, ISO/IEEE 29148, Diátaxis, académica, ninguna | Diátaxis (manual), académica (tesis), ISO 29148 (especificación); en otro caso, ninguna |
| Propósito | expositivo, analítico, argumentativo, instructivo, narrativo, mixto | instructivo (manual); argumentativo (tesis); analítico (informe); expositivo en otro caso |
| Ámbito | científico, técnico, académico, institucional, profesional | académico (tesis); técnico en otro caso |
| Lector | experto, especialista de otra área, público general, mixto | público general (manual); mixto en otro caso |
| Medio | impreso (A4 o carta), digital, ambos | digital |
| Variante | español neutro, rioplatense | neutro |
| Tratamiento | usted, tú, vos, impersonal | usted (manuales); impersonal (tesis y especificaciones) |
| Citas | APA 7, IEEE, institucional, ninguna | APA 7 si hay citas |
| Formato de salida | Markdown, docx, pdf | Markdown |

Pregunta siempre si hay un reglamento institucional o una guía de marca. Si existe, manda sobre las recomendaciones y hay que pedir el documento.

Pregunta siempre si hay un reglamento institucional o una guía de marca. Si existe, manda sobre las recomendaciones y hay que pedir el documento.

### Estructura

1. Toma el esqueleto de capítulos de `references/metodologias.md` para la metodología elegida y adáptalo al proyecto.
2. No mezcles metodologías. Si hace falta combinarlas, declara qué parte sigue cuál.
3. Reparte la estructura en tres zonas (`references/escritura.md`, §4 ter):
   - **Pretextual**: elementos del catálogo, en orden, sin número. Incluye siempre "Control de versiones" como primer elemento, salvo que el usuario lo descarte.
   - **Textual**: los capítulos numerados.
   - **Postextual**: elementos del catálogo, en orden, sin número.
4. Copia en la sección 3 la regla de cada elemento pretextual y postextual tal como está en el catálogo. Si el usuario agrega un elemento propio, pregúntale su regla. El prólogo lo escribe otra persona: deja `[PENDIENTE: texto del prologuista]`.
5. Pregunta el formato de cada zona (paginación y página nueva) y, si hay dedicatoria o epígrafe, su alineación y su estilo. Los valores por defecto están en el catálogo.
6. Escribe en el encabezado `pretextuales`, `postextuales` y el formato de las zonas. Escribe también `estructura` (las tres zonas en orden, sin Portada, Dedicatoria ni Epígrafe, que no llevan título) y `sin_numerar` (pretextuales y postextuales, nunca un capítulo textual), que se derivan de las zonas. Si una configuración vieja tiene una parte sin número entre capítulos, va a su zona (pre o post según el catálogo; si no está en ninguno, a post) y se avisa al usuario.

### Componentes y estilo visual

Desde `references/estilo-visual.md`, selecciona los componentes que usará este documento (por ejemplo, un manual usa pasos y capturas; una especificación usa tablas de requisitos). Copia al prompt el formato exacto en Markdown de cada componente. Fija también la tipografía y el color si el documento se exportará.

### Normas de escritura

Desde `references/escritura.md`, copia las reglas generales y las específicas del tipo de documento. Define los términos preferidos del proyecto si ya se conocen.

### Entrega del prompt

1. Copia `assets/plantilla-prompt-estilo.md` y reemplaza cada `<...>`. Elimina las líneas que no apliquen.
2. El encabezado YAML debe tener al menos estos campos: `documento`, `tipo`, `metodologia`, `medio`, `tratamiento`, `salida` y `estructura`. Los nombres de `estructura` deben coincidir exactamente con los títulos de capítulo que se usarán, sin número.
3. El cuerpo debe poder leerse sin las referencias: quien lo use no necesita abrir este skill.
4. Guárdalo en `docs/prompt-estilo.md`, salvo que el usuario indique otra ruta. Si ya existe, léelo, súbele la versión y conserva las decisiones que el usuario no pidió cambiar.
5. Muestra al usuario un resumen de una línea por parámetro y la ruta del archivo.
