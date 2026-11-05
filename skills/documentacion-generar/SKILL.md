---
name: documentacion-generar
description: Genera la documentación completa (manual de usuario, tesis, especificación de requisitos, informe, documento de arquitectura o diagramas) a partir de un prompt de estilo. Si no hay prompt de estilo, primero lo crea con el skill documentacion-estilo, preguntando al usuario lo que no esté definido, y después redacta el documento, lo verifica con un script y entrega los archivos. Nunca decide el estilo por su cuenta; lo que no está definido se pregunta y se guarda en la memoria del skill. Úsalo cuando el usuario pida escribir, generar, redactar, producir o actualizar documentación, con o sin un prompt de estilo previo.
---

# Documentación: generador

Este skill escribe el documento. Recibe el **prompt de estilo** que produce `documentacion-estilo`. Si no lo recibe, lo crea primero. Después redacta el contenido, lo verifica con `scripts/verificar_doc.py` y entrega los archivos.

El flujo es siempre el mismo: prompt, contenido, plan, redacción, verificación, exportación e informe.

**No decidas nada por tu cuenta.** Antes de empezar, lee las dos memorias: la del agente (`../documentacion-estilo/memoria/decisiones.md`) y la del proyecto (`decisiones-estilo.md` en la carpeta del prompt de estilo, si existe). Si en cualquier paso aparece algo que el prompt, las memorias y las referencias no definen, aplica `../documentacion-estilo/references/memoria.md`: detén solo la parte afectada, pregunta al usuario (incluido el alcance), registra las preguntas y las respuestas en la memoria que corresponda e incorpora la regla. Las decisiones del proyecto se commitean en el repositorio del proyecto. Las de alcance de agente quedan como `propuesta` en esa misma memoria del proyecto: nunca edites la carpeta instalada del skill ni abras PRs en el repositorio del agente desde otro repositorio.

## Paso 1: obtener el prompt de estilo

Busca el prompt en este orden:

1. El que el usuario pegó en la conversación o cuya ruta indicó.
2. `docs/prompt-estilo.md` en el proyecto.
3. Cualquier archivo `**/prompt-estilo*.md`. Si hay varios, usa el que tenga en `documento` el título pedido. Si sigue habiendo ambigüedad, pregunta cuál usar.

**Si no hay prompt:**

1. Invoca el skill `documentacion-estilo`. Si no puedes invocarlo, lee `../documentacion-estilo/SKILL.md` y sigue sus pasos.
2. Ese skill abre primero el configurador visual en el navegador del usuario. **No preguntes los parámetros en la terminal.** Espera a que el usuario descargue el prompt y escriba «listo».
3. Sigue los pasos 2 a 4 de `documentacion-estilo`: recibir el prompt, completar los `[PENDIENTE]` y actualizar la memoria. Después continúa con el Paso 2 de este skill.

**Si el prompt existe, valídalo.** El encabezado YAML debe tener `documento`, `tipo`, `metodologia`, `medio`, `tratamiento`, `salida` y `estructura`. Si faltan campos, complétalos siguiendo `documentacion-estilo`, sube la versión del prompt y guárdalo.

Si el prompt pegado no tiene encabezado YAML, conviértelo al formato de `../documentacion-estilo/assets/plantilla-prompt-estilo.md` y guárdalo en `docs/prompt-estilo.md` antes de seguir. El verificador lo necesita en ese formato.

**El prompt manda.** Si el usuario pide algo que lo contradice (por ejemplo, otro tratamiento), primero actualiza el prompt y su versión, y después escribe. Así el documento y su estilo no se separan.

## Paso 2: reunir el contenido

1. Identifica las fuentes: el pedido del usuario, archivos adjuntos, notas, documentos anteriores y, en documentación de software, el código del proyecto.
2. En documentación de software, toma los nombres reales del código y de la interfaz: pantallas, menús, campos, endpoints, parámetros, comandos y mensajes de error. No los traduzcas ni los inventes.
3. Asigna cada capítulo de `estructura` a sus fuentes. Si un capítulo no tiene fuente, se escribe con `[PENDIENTE: qué falta y quién puede darlo]`.
4. No inventes datos, cifras, nombres de personas, resultados, citas ni referencias bibliográficas.

## Paso 3: planificar

1. Arma el índice. Para cada capítulo de `estructura`, define sus secciones (H2 y H3), sus fuentes y los componentes que llevará (tablas, figuras, pasos, avisos).
2. Elige la organización de los archivos en la carpeta `salida` del prompt:
   - **Un archivo** (`documento.md`) si el documento es corto, hasta unas 15 páginas.
   - **Un archivo por capítulo** (`00-control-de-versiones.md`, `01-introduccion.md`, ...) si es más largo. El prefijo numérico mantiene el orden. Sigue siendo un documento lógico (`entrega: unico`, o sin el campo), con numeración continua (DEC-008).
   - **Entrega en varios archivos**, solo si el prompt dice `entrega: multiarchivo` (DEC-008): un archivo índice (`entrega_indice`, por defecto `README.md`) y un archivo por punto, en el primer nivel de la carpeta, con el patrón `entrega_patron` (por defecto `NN - Nombre.md`). Asigna a cada capítulo de `estructura` su archivo: el índice o un punto.
   - Diagramas e imágenes en `salida/figuras/`.
3. Si la carpeta `salida` ya tiene documentación, léela antes de escribir. Actualiza lo existente en lugar de reemplazarlo y agrega una fila nueva en el control de versiones.
4. Con `entrega: multiarchivo`, propón las filas del control de versiones desde el historial de la carpeta (DEC-010): `git log --date=format:%d/%m/%Y --format="%ad | %an | %s" -- <carpeta>`. Git da la fecha, el autor y el mensaje, pero no la versión ni la descripción del cambio: muestra la propuesta y pide al usuario que confirme la versión y la descripción de cada fila. Nunca escribas filas sin esa confirmación. Sin repositorio, o si la carpeta no tiene historial, las filas quedan como `[PENDIENTE: versión, fecha, autor y descripción]`.

## Paso 4: redactar

Sigue el prompt al pie de la letra: estructura, componentes, tratamiento y normas de escritura. Además, usa estas convenciones de Markdown, que son las que revisa el verificador:

- **Título del documento**: un H1 inicial con el texto exacto de `documento`, o ningún título.
- **Capítulos**: `# 1 Introducción`, `## 1.1 Alcance`, `### 1.1.1 Limitaciones`. Las partes de `sin_numerar` van sin número: `# Glosario`. Con `numeracion_textual: ninguna`, los capítulos de la zona textual también van sin número (están en `sin_numerar`); con `niveles_numerados: 2`, los `###` van sin número. Los nombres de capítulo coinciden exactamente con `estructura`. Las partes pretextuales y postextuales (`pretextuales` y `postextuales`, si el prompt las trae) siguen la regla de su fila en la sección 3.
- **Prólogo**: lo escribe otra persona. No lo redactes: `# Prólogo` lleva solo `[PENDIENTE: texto del prologuista]`. El verificador da una advertencia si tiene otro texto.
- **Control de versiones**: va primero por defecto, salvo que el prompt lo ubique en otro lugar de `pretextuales`. Tabla con columnas Versión, Fecha, Autor y Descripción del cambio. La primera versión es la 0.1 (borrador), con la fecha de hoy. Como autor, usa el que indicó el usuario o el de `git config user.name`. Con `entrega: multiarchivo`, hay una sola tabla, en el índice, con las filas confirmadas en el Paso 3 (DEC-010).
- **Tablas**: `**Tabla N.** Título` antes de la tabla y `Fuente: ...` después.
- **Figuras**: después de la imagen o del bloque `mermaid`, va `**Figura N.** Título` y luego `Fuente: ...`. Las imágenes llevan texto alternativo: `![Pantalla de inicio de sesión](figuras/login.png)`.
- **Numeración continua** de tablas y figuras en todo el documento, también entre archivos. Cada una se menciona en el texto antes de aparecer ("En la Figura 2 se muestra...").
- **Con `entrega: multiarchivo`**:
  - **Índice** (DEC-008): lleva el H1 con el texto exacto de `documento`, y enlaza cada punto en el orden de los archivos, con enlaces en línea: el verificador no reconoce los enlaces por referencia. Si el nombre tiene espacios, el enlace usa `%20` o `<…>`: `[Alcance](<01 - Alcance.md>)`.
  - **Puntos** (DEC-008): el H1 lleva el número del archivo: `04 - Diseño.md` empieza con `# 4 Diseño`, y sus secciones son `## 4.1`, `## 4.2`… También lleva número una parte de `sin_numerar` que va en un punto: `05 - Glosario.md` empieza con `# 5 Glosario`. Con `numeracion_textual: ninguna`, el H1 no lleva número.
  - **Numeración** (DEC-009): reemplaza a la numeración continua. Tablas y figuras se numeran por archivo con el número del archivo como prefijo: en `04 - Diseño.md`, `**Tabla 4.1.**` y `**Figura 4.1.**`. Las del índice van sin prefijo: `**Tabla 1.**`. Con leyendas APA 7 se mantiene su formato y se admite ese número, como excepción explícita a APA 7: `**Tabla 4.1**`. Cada una se menciona en su propio archivo; desde otro archivo se cita con su número completo.
- **Avisos**: `> **Nota.**`, `> **Consejo.**`, `> **Advertencia.**` o `> **Peligro.**`.
- **Diagramas**: en Mermaid dentro del documento, con la notación que fija el prompt (UML, BPMN, C4 o ER). Si el diagrama no se puede expresar en Mermaid, usa PlantUML en `figuras/` y enlaza la imagen exportada.
- **Pendientes**: `[PENDIENTE: descripción]`, nunca texto inventado.
- **Glosario y siglas**: anota cada término técnico y cada sigla mientras escribes. Al final, completa el glosario y la lista de siglas.

Si el prompt tiene `plantilla`, lee ese archivo (la ruta es relativa al directorio del skill `documentacion-estilo`) y aplica su diseño: manda sobre las convenciones anteriores donde difieran. Por ejemplo, con *Trabajo de campo UNC* las leyendas siguen APA 7 (`**Tabla N**` y el título en cursiva en la línea siguiente, ambos arriba, y `*Nota.*` debajo, también en las figuras). El verificador reconoce ese formato cuando el prompt declara una plantilla APA 7 o el campo `leyendas: apa7`:

  ```
  **Tabla 1**
  *Calificaciones del equipo*

  | Atributo | Promedio |
  |---|---|

  *Nota.* Escala del 1 al 10.
  ```

  En las figuras, la leyenda va antes de la imagen o del bloque `mermaid`, y la nota después. Los «Puntos abiertos» de la plantilla no se aplican: si el documento los necesita, pregúntalos.

Si el prompt trae `componentes_plantilla`, sus reglas están en la sección 4 («Componentes propios de la plantilla») y en la sección «En el configurador» de la plantilla. El verificador revisa los que se pueden ver en Markdown:

| Componente | Qué revisa |
|---|---|
| Documento fuente | Que cada capítulo de la zona textual cierre con `**Documento fuente: *nombre*.**` |
| Viñetas con término | Que los dos puntos queden dentro de la negrita: `- **Término:** texto` |
| Datos del documento, ficha de corrida y familia | Que sus líneas (`**Sistema:**`, `**Commit:**`, `**Familia:**`…) estén antes del primer capítulo; el commit, en código |
| Estado y completitud | Estado Completo, Parcial o No; Completo con 100 % |
| Criterio y evidencia | Título `### N · Nombre — Estado (NN %)`, línea `Archivo:`, ¿Cumple? Sí, Parcial o No, evidencia con su lugar entre paréntesis y el párrafo `**Para completar:**` |
| Agenda con tiempos | Última fila `**Tiempo total**` con la suma de los tiempos estimados |
| Preguntas con líneas | Numeración `**1.1**`, `**1.2**`… continua por bloque y de 3 a 4 líneas `___` por pregunta |
| Intención y Cuándo sí y cuándo no | Intención de una o dos oraciones; tabla de solo dos columnas, `Sí usarlo` y `No usarlo` |
| Antetítulo y bajada, una idea por lámina | Cada lámina empieza con el antetítulo en negrita, la bajada no pasa de tres oraciones y no hay `##` adentro |

Si una sección necesita un componente, formato o término que el prompt no define, no lo improvises. Escribe `[PENDIENTE: estilo no definido, ver DEC-NNN]` (o `DP-NNN` si es una decisión del proyecto), haz las preguntas del procedimiento de memoria y sigue con las secciones que no dependen de esa decisión. Cuando llegue la respuesta, vuelve a esa sección.

## Paso 5: verificar

Ejecuta el verificador, que está en la carpeta `scripts/` de este skill:

```bash
python3 <carpeta-de-este-skill>/scripts/verificar_doc.py --prompt docs/prompt-estilo.md <carpeta-salida>/
```

Con `entrega: multiarchivo`, la ruta debe ser una sola carpeta: si recibe otra cosa, o un valor de `entrega` desconocido, el script termina con código 2.

Además de títulos, estructura, leyendas, avisos y normas de escritura, comprueba que:

- cada «Tabla N» o «Figura N» citada en el texto exista en el documento;
- cada `DEC-NNN` citado exista en la memoria del agente y cada `DP-NNN`, en la memoria del proyecto (`decisiones-estilo.md` junto al prompt). Las rutas se pueden cambiar con `--memoria-agente` y `--memoria-proyecto`.

Con `entrega: multiarchivo`, lee el índice primero y luego los puntos por número, solo del primer nivel de la carpeta y sin el prompt ni `decisiones-estilo.md`. Además comprueba que:

- exista el índice, cada archivo cumpla el patrón y no se repita un número; un salto en los números da advertencia (DEC-008);
- el índice enlace cada punto, sin enlaces rotos y en el orden de los archivos (DEC-008);
- el H1 de cada punto lleve el número de su archivo, y `estructura` esté completa en el conjunto de la entrega (DEC-008);
- tablas y figuras tengan el prefijo de su archivo y no salten números; las citas se resuelven contra toda la entrega, y la mención se busca en el archivo de cada tabla o figura (DEC-009);
- haya exactamente una tabla de control de versiones, en el índice, reconocida por sus columnas Versión y Fecha (DEC-010).

Con `entrega: unico`, `Tabla 2.1` da error: ya no se lee como `Tabla 2`.

- **Errores**: corrígelos todos y vuelve a ejecutar el script hasta que no quede ninguno.
- **Advertencias**: corrígelas. Si alguna es un falso positivo (por ejemplo, un número de versión con punto), déjala y menciónala en el informe final.
- **Pendientes**: el script los lista. Se informan al usuario y no se rellenan inventando.

Luego revisa a mano lo que el script no ve, con la lista de verificación de `documentacion-estilo`: voz activa, tratamiento coherente, un término por concepto, cautela en las conclusiones y criterios de aceptación propios del prompt.

## Paso 6: exportar (solo si el prompt o el usuario lo piden)

- **docx** o **pdf**: usa el skill de ese formato, si está disponible. Si no, usa `pandoc` si está instalado. Aplica la tipografía y los colores del prompt.
- **Diagramas Mermaid**: si hay `mmdc` (mermaid-cli), exporta cada diagrama a SVG en `figuras/`. Si no, deja el código Mermaid y avisa.
- La fuente en Markdown se conserva siempre junto al archivo exportado.

## Paso 7: informe final

Entrega al usuario un mensaje breve con:

1. El prompt usado, su ruta y si se creó en esta ejecución o ya existía.
2. Los archivos generados o actualizados.
3. El resultado del verificador: errores (deben ser 0) y advertencias que quedaron, con su motivo.
4. La lista de `[PENDIENTE]` con lo que hace falta para completarlos.
5. Las decisiones de estilo nuevas (DP-NNN): preguntas, respuestas y estado. Si hay alguna `propuesta` para el agente, indica que se incorpora abriendo una sesión en el repositorio del agente y pidiendo «incorporar las propuestas de <ruta del decisiones-estilo.md>».
6. Cualquier desvío del prompt y su motivo.
