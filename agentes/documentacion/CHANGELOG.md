# Changelog: agente de documentación

Cambios relevantes del agente (`skills/documentacion-estilo` y `skills/documentacion-generar`). El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y las versiones siguen [SemVer](https://semver.org/lang/es/), según las reglas de [`VERSIONADO.md`](../../VERSIONADO.md).

## [0.5.0] - 2026-11-02

### Agregado

- Versionado del agente: manifiesto `agentes/documentacion/agente.json` y este changelog.
- El procedimiento de memoria sube la versión del agente al registrar decisiones de estilo: MINOR para una regla confirmada con alcance de agente y PATCH para preguntas pendientes o decisiones de un solo documento.

## [0.4.0] - 2026-11-02

### Cambiado

- `documentacion-estilo` abre primero el configurador en el navegador y espera a que el usuario escriba «listo». Las preguntas en la terminal pasan a un modo alternativo, que solo se usa a pedido o sin navegador.
- El agente toma el `prompt-estilo*.md` más reciente de la carpeta de descargas, pregunta solo los `[PENDIENTE]` y actualiza la memoria con los parámetros elegidos.
- `documentacion-generar` sigue el mismo flujo cuando no encuentra un prompt.

### Agregado

- Campo `alcance_decisiones` en el prompt que genera el configurador.

## [0.3.0] - 2026-11-02

### Agregado

- Configurador visual (`assets/configurador.html`). Permite elegir metodología, estructura, componentes, diagramas, tipografía, tamaños, color y normas, con vista previa digital o impresa. Genera el prompt de estilo y las respuestas para la memoria.
- Subida de un documento propio (.md, .docx, .html o .txt) para verlo con el estilo, con revisión de desvíos.
- Ajustes locales sobre una parte seleccionada del documento. Se registran como «Excepciones locales» en el prompt y en la memoria.

### Corregido

- `verificar_doc.py` decodifica los valores YAML entre comillas dobles.

## [0.2.0] - 2026-11-02

### Agregado

- Skill `documentacion-generar`, que redacta el documento a partir del prompt de estilo y lo valida con `scripts/verificar_doc.py`.
- Prompt de estilo como salida de `documentacion-estilo` (`assets/plantilla-prompt-estilo.md`).
- Memoria del agente (`memoria/decisiones.md`, con DEC-001 a DEC-006 pendientes) y procedimiento para casos no definidos, con PR de secciones Qué, Por qué y Cómo.

### Cambiado

- Los skills ya no aplican valores por defecto: preguntan lo que no está definido.

## [0.1.0] - 2026-11-02

### Agregado

- Skill `documentacion-estilo`: estructuras por metodología (RUP, UP, Scrum, ISO/IEEE 29148, Diátaxis y académica), estilo visual (componentes, tipografía y paleta con contraste AA) y normas de escritura en español.
