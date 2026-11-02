# Changelog: agente de documentación

Cambios relevantes del agente (`skills/documentacion-estilo` y `skills/documentacion-generar`). El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y las versiones siguen [SemVer](https://semver.org/lang/es/), según las reglas de [`VERSIONADO.md`](../../VERSIONADO.md).

## [0.10.0] - 2026-11-02

### Agregado

- Configurador: elementos académicos (resumen y palabras clave, notas al pie, citas en bloque, hipótesis numeradas, índices de tablas y figuras, y anexos), cada uno con su ejemplo en la vista previa, en «Ver todo» y su regla en el prompt
- Configurador: los índices de tablas y figuras de la vista previa se arman con las leyendas reales del ejemplo
- Verificador: notas al pie sin definición o sin uso; y, según los componentes del prompt, citas en bloque de menos de 40 palabras o citas largas entre comillas, numeración de hipótesis, palabras clave, orden y mención de anexos e índices faltantes

### Cambiado

- Verificador: las citas en bloque ya no cuentan para el largo máximo de oración

## [0.9.0] - 2026-11-02

### Agregado

- Configurador: «Tipos de tabla» (de datos, frecuencia, contingencia, correlación, regresión, ANOVA, características demográficas, comparación, descriptivos, fiabilidad, pruebas de hipótesis, operacionalización y estado del arte), visibles con «Tablas», cada uno con su ejemplo y su regla en el prompt (campo tablas)
- Configurador: botón «Ver todo», que agrega a la vista previa un apéndice de prueba con todos los elementos sin cambiar la selección ni el prompt
- Verificador: si el prompt declara tablas estadísticas, avisa del cero inicial en p, r, β, α, ω y η², del separador decimal y de los asteriscos sin nota (APA 7)

## [0.8.1] - 2026-11-02

### Corregido

- Configurador: al cambiar tipografía, tamaños, color o comillas con bloques seleccionados, el cambio se aplica solo a la selección aunque no se haya apretado «Ajustar estilo de la selección»; antes iba a todo el documento

## [0.8.0] - 2026-11-02

### Agregado

- Configurador: filtro «Útil para» por tipo de documento, chips «Ir a» por sección e íconos en las tarjetas de opción
- Configurador: la vista previa se puede cerrar y el formulario pasa a ocupar todo el ancho; se recuerda si quedó abierta
- Configurador: botón para cambiar entre modo claro y oscuro
- Configurador: las secciones se pliegan y despliegan desde su título; se recuerda cuáles quedaron plegadas y saltar a una sección la despliega

### Cambiado

- Configurador: nuevo diseño con encabezado fijo y resumen en píldoras, secciones abiertas con contador, listas desplegables convertidas en tarjetas de elección y contadores − / + en los campos numéricos

### Corregido

- Configurador: sin opciones redundantes ni sin efecto. Los tipos de aviso solo aparecen con el componente Avisos; el resultado tras cada paso, con Pasos numerados; borde y marcadores de capturas, con Figuras en un manual; los tipos de Diátaxis, en un manual con Diátaxis; y los ajustes de diagramas, con al menos una notación. Ocultarlas no borra su valor.
- Configurador: Avisos tiene ícono propio (era igual al de Advertencia) y su «Útil para» coincide con el de sus tipos.

## [0.7.0] - 2026-11-02

### Agregado

- Instalación aislada: scripts/instalar_skills.ps1 instala los skills desde una copia fija en origin/main (git worktree) con junctions en ~/.claude/skills

### Cambiado

- La carpeta instalada del skill es de solo lectura; desde otro repositorio, las decisiones con alcance de agente quedan como propuesta en decisiones-estilo.md del proyecto y se incorporan desde una sesión en el repositorio del agente
- Configurador: la pestaña Para la memoria describe el alcance de agente como propuesta y su instrucción ya no pide PRs desde otro repositorio
- Verificador: error cuando el texto cita una «Tabla N» o «Figura N» que no existe.
- Verificador: comprueba que los DEC-NNN citados existan en la memoria del agente y los DP-NNN en la del proyecto (opciones --memoria-agente y --memoria-proyecto).
- Tests del verificador y del configurador (tests/, unittest) y workflow de CI «Tests».

## [0.6.0] - 2026-11-02

### Agregado

- Plantilla de la memoria de proyecto (assets/plantilla-decisiones-proyecto.md).

### Cambiado

- La memoria se separa en dos niveles: la del agente (memoria/decisiones.md, DEC-NNN) guarda solo reglas para todos los documentos, y cada proyecto documentado guarda las suyas en decisiones-estilo.md, junto a su prompt de estilo (DP-NNN). Las decisiones de proyecto se commitean en ese repositorio y no generan PR ni versión del agente.

### Corregido

- Configurador: al cambiar de plantilla o de cualquier opción, la vista previa conserva la parte del documento que se estaba leyendo.

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
