---
name: documentacion-generar
description: Genera la documentación completa (manual de usuario, tesis, especificación de requisitos, informe, documento de arquitectura o diagramas) a partir de un prompt de estilo. Si no hay prompt de estilo, primero lo crea con el skill documentacion-estilo, preguntando al usuario lo que no esté definido, y después redacta el documento, lo verifica con un script y entrega los archivos. Nunca decide el estilo por su cuenta; lo que no está definido se pregunta y se guarda en la memoria del skill. Úsalo cuando el usuario pida escribir, generar, redactar, producir o actualizar documentación, con o sin un prompt de estilo previo.
---

# Documentación: generador

Este skill escribe el documento. Recibe el **prompt de estilo** que produce `documentacion-estilo`. Si no lo recibe, lo crea primero. Después redacta el contenido, lo verifica con `scripts/verificar_doc.py` y entrega los archivos.

El flujo es siempre el mismo: prompt, contenido, plan, redacción, verificación, exportación e informe.

**No decidas nada por tu cuenta.** Antes de empezar, lee `../documentacion-estilo/memoria/decisiones.md`. Si en cualquier paso aparece algo que el prompt, la memoria y las referencias no definen, aplica `../documentacion-estilo/references/memoria.md`: detén solo la parte afectada, pregunta al usuario, registra las preguntas y las respuestas en la memoria, incorpora la regla y envía la memoria al repositorio del agente con un PR (secciones Qué, Por qué y Cómo).

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
   - **Un archivo por capítulo** (`00-control-de-versiones.md`, `01-introduccion.md`, ...) si es más largo. El prefijo numérico mantiene el orden.
   - Diagramas e imágenes en `salida/figuras/`.
3. Si la carpeta `salida` ya tiene documentación, léela antes de escribir. Actualiza lo existente en lugar de reemplazarlo y agrega una fila nueva en el control de versiones.

## Paso 4: redactar

Sigue el prompt al pie de la letra: estructura, componentes, tratamiento y normas de escritura. Además, usa estas convenciones de Markdown, que son las que revisa el verificador:

- **Título del documento**: un H1 inicial con el texto exacto de `documento`, o ningún título.
- **Capítulos**: `# 1 Introducción`, `## 1.1 Alcance`, `### 1.1.1 Limitaciones`. Las partes de `sin_numerar` van sin número: `# Glosario`. Los nombres de capítulo coinciden exactamente con `estructura`.
- **Control de versiones**: es la primera parte. Tabla con columnas Versión, Fecha, Autor y Descripción del cambio. La primera versión es la 0.1 (borrador), con la fecha de hoy. Como autor, usa el que indicó el usuario o el de `git config user.name`.
- **Tablas**: `**Tabla N.** Título` antes de la tabla y `Fuente: ...` después.
- **Figuras**: después de la imagen o del bloque `mermaid`, va `**Figura N.** Título` y luego `Fuente: ...`. Las imágenes llevan texto alternativo: `![Pantalla de inicio de sesión](figuras/login.png)`.
- **Numeración continua** de tablas y figuras en todo el documento, también entre archivos. Cada una se menciona en el texto antes de aparecer ("En la Figura 2 se muestra...").
- **Avisos**: `> **Nota.**`, `> **Consejo.**`, `> **Advertencia.**` o `> **Peligro.**`.
- **Diagramas**: en Mermaid dentro del documento, con la notación que fija el prompt (UML, BPMN, C4 o ER). Si el diagrama no se puede expresar en Mermaid, usa PlantUML en `figuras/` y enlaza la imagen exportada.
- **Pendientes**: `[PENDIENTE: descripción]`, nunca texto inventado.
- **Glosario y siglas**: anota cada término técnico y cada sigla mientras escribes. Al final, completa el glosario y la lista de siglas.

Si una sección necesita un componente, formato o término que el prompt no define, no lo improvises. Escribe `[PENDIENTE: estilo no definido, ver DEC-NNN]`, haz las preguntas del procedimiento de memoria y sigue con las secciones que no dependen de esa decisión. Cuando llegue la respuesta, vuelve a esa sección.

## Paso 5: verificar

Ejecuta el verificador, que está en la carpeta `scripts/` de este skill:

```bash
python3 <carpeta-de-este-skill>/scripts/verificar_doc.py --prompt docs/prompt-estilo.md <carpeta-salida>/
```

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
5. Las decisiones de estilo nuevas (DEC-NNN): preguntas, respuestas, estado y enlace al PR que las envió al repositorio del agente.
6. Cualquier desvío del prompt y su motivo.
