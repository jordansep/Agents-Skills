# Changelog: agente de documentación

Cambios relevantes del agente (`skills/documentacion-estilo` y `skills/documentacion-generar`). El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y las versiones siguen [SemVer](https://semver.org/lang/es/), según las reglas de [`VERSIONADO.md`](../../VERSIONADO.md).

## [0.14.0] - 2026-11-03

### Agregado

- Configurador: plantilla como primer paso; cada plantilla carga un punto de partida completo (ejes, estructura en tres zonas, componentes, presentación y sus componentes propios), todo editable
- Componentes propios de las seis plantillas, con ejemplo en la vista previa y en «Ver todo» y su regla en el prompt (componentes_plantilla): portada institucional, documento fuente y viñetas con término (Trabajo de campo UNC); datos del documento (Informe técnico); ficha de corrida, estado y completitud, criterio y evidencia y etiquetas de certeza (auditoría); barras de sección, campos para completar, agenda y preguntas con líneas (proforma); familia, intención, cuándo sí y cuándo no y dos columnas (ficha); antetítulo y bajada, una idea por lámina, tarjetas y colores de C4 (láminas)
- Estructura: numeración de los capítulos (decimal o sin número) y niveles numerados (numeracion_textual y niveles_numerados en el prompt)
- Verificador: revisa los componentes propios que se ven en Markdown (documento fuente, dos puntos del término, datos y ficha antes del primer capítulo, estados y completitud, criterio y evidencia, agenda, preguntas, intención, cuándo usar, antetítulo, bajada y una idea por lámina) y respeta niveles_numerados

### Cambiado

- Tipografía conserva solo los preajustes de letra (Digital, Tesis impresa, Manual impreso), que ya no quitan la plantilla elegida
- La vista previa usa las leyendas APA 7 con la plantilla Trabajo de campo UNC y la composición de cada plantilla (barras, dos columnas, láminas)
- references/plantillas: cada plantilla tiene la sección «En el configurador» con sus componentes, la regla que copia el prompt y lo que revisa el verificador

### Corregido

- Verificador: un título «N · Nombre» (punto de una auditoría) ya no se toma como numeración decimal, y el número de pregunta en negrita («**1.2**») no se marca como punto decimal

## [0.13.0] - 2026-11-02

### Agregado

- Configurador: estructura en tres zonas (pretextual, textual y postextual) con catálogo, orden y elementos propios; cada elemento trae su regla de contenido (references/escritura.md, §4 ter)
- Configurador: formato por zona (paginación romana, arábiga o ninguna y página nueva) y alineación y estilo de la dedicatoria y del epígrafe
- Prólogo distinto del prefacio: el prólogo lo escribe otra persona y el agente nunca lo redacta y deja el marcador del prologuista; el verificador advierte si la sección «Prólogo» tiene otro texto

### Cambiado

- El prompt escribe pretextuales, postextuales y el formato de las zonas; estructura y sin_numerar se derivan de las zonas y siguen siendo válidos. estructura deja fuera Portada, Dedicatoria y Epígrafe, que no llevan título, así que el verificador ya no les exige un H1; sin_numerar nunca incluye un capítulo de la zona textual
- Las configuraciones sin zonas se reparten solas al importarlas: las partes sin número anteriores al primer capítulo van a pretextual, las posteriores al último a postextual, y una parte sin número que quedó entre capítulos va a su zona según el catálogo (o a postextual como elemento propio), con un aviso. «Cargar esqueleto» y «usar capítulos» usan la misma regla
- Control de versiones va primero por defecto en la zona pretextual: en el catálogo, al volver a marcarlo y al repartir capítulos; el usuario puede moverlo
- Verificador: prefacio, prólogo, epígrafe, índice alfabético y colofón se reconocen como partes sin número

## [0.12.0] - 2026-11-02

### Agregado

- Ejes de clasificación propósito y ámbito en el configurador y en el prompt, con sus reglas de redacción en la sección 5 (references/escritura.md, §4 bis)
- Reglas de divulgación automáticas con ámbito científico o técnico, lector público general y propósito expositivo o narrativo
- El verificador advierte sobre valores desconocidos en proposito, ambito y lector

### Cambiado

- Audiencia pasa a Lector (experto, especialista de otra área, público general, mixto); las configuraciones del configurador con audiencia se traducen solas (propósito y ámbito se completan según el tipo); los prompts con audiencia siguen siendo válidos

## [0.11.0] - 2026-11-02

### Agregado

- Configurador: tipos de tabla técnicos (matriz de trazabilidad, caso de uso, riesgos y endpoints de API), con ejemplo, «Útil para» y regla en el prompt
- Verificador: con esos tipos en el prompt, revisa los métodos HTTP de los endpoints, que el nivel de riesgo sea probabilidad × impacto con su categoría y orden, y que cada requisito de la trazabilidad tenga caso de prueba

### Cambiado

- Verificador: GET, POST, PUT, PATCH, DELETE, HEAD y OPTIONS ya no se marcan como siglas sin desarrollar

### Corregido

- Configurador: los identificadores como R-01 o RF-001 ya no se cortan en dos líneas en las tablas de ejemplo

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
