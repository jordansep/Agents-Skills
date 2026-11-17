# Changelog: agente de auditoría

Cambios relevantes del agente (`skills/auditoria-sistemas`). El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y las versiones siguen [SemVer](https://semver.org/lang/es/), según las reglas de [`VERSIONADO.md`](../../VERSIONADO.md).

## [0.13.0] - 2026-11-17

### Agregado

- En nivel medio se leen todas las imágenes con texto o cifras; una imagen sin leer deja en Parcial las filas que dependen de ella.
- La etiqueta de un chequeo del plan señala una sola fila del mismo punto.

### Cambiado

- Dónde va cada defecto: si lo cubren chequeos del plan, va en cada una de esas filas con la misma severidad; si no, en una sola fila, la del punto cuya sección hay que corregir. Una sección que sólo lo nombra o lo resume (glosario, índice) nunca recibe lo que falta en otra. Reemplaza «una contradicción entre dos puntos es No en los dos», que duplicaba defectos.
- FUERA DEL DOCUMENTO va siempre en Parcial y sin severidad, y cubre sólo el contenido detrás de una remisión que sí está; lo que la sección dice traer y no trae es No.
- Un PROBABLE lleva la severidad que tendría si se confirmara; una regla de conducta o de proceso sin registro de cumplimiento es Parcial y sin severidad; las cantidades declaradas se cuentan con lo vigente.
- Más ejemplos de severidad (confidencialidad con servicios de terceros y etapa contradictoria como Alta; subtotal que no cierra, cita atribuida a otra persona, cargo contradictorio, regla propia incumplida, casillas excluyentes y acción ejecutada en parte como Media; número de sprint contra sus fechas como Baja). Medido en tres corridas sobre el mismo documento: veredicto igual 96-97 %, gravedad igual 86-88 %, Crítica y Alta coinciden al 100 %.

## [0.12.0] - 2026-11-15

### Agregado

- Plan de auditoría por sistema (references/plan-de-auditoria.md): en nivel medio y exhaustivo, toda corrida usa los mismos puntos, filas y chequeos; el plan se aprueba antes de auditar y crece con chequeos aprobados.
- Reglas para juzgar igual en cada corrida: un defecto va en una sola fila, qué cubre cada fila fija, cuándo es Parcial, secciones históricas y lo que está fuera del documento.

### Cambiado

- Severidad de Documentos sin consigna con ejemplos para los cortes Baja/Media y Media/Alta; sus puntos y filas pasan a references/plan-de-auditoria.md, y una fila que no aplica queda en el plan con su motivo. Medido en tres corridas sobre el mismo documento: veredicto igual 91-95 %, gravedad igual 78-84 %.

## [0.11.0] - 2026-11-06

### Agregado

- Memoria de errores: registra los errores del auditor sin datos del objetivo ni del usuario, y propone una regla cuando un error aparece en 2 auditorías; sólo se activa si el usuario la aprueba
- Control estricto antes de guardar: sólo pasan palabras de un vocabulario cerrado, sin números ni datos de la corrida o del usuario, y se repite justo antes de cada escritura

## [0.10.0] - 2026-11-06

### Agregado

- La exhaustiva por lotes cuenta los enlaces internos y externos de cada PDF y señala la numeración salteada de los identificadores, como señales para revisar
- Preparar rasteriza las páginas con imagen y los prompts de los lectores nombran los PNG; sin pymupdf, avisa lo que no pudo hacer y conserva la instrucción anterior

### Cambiado

- Los prompts de verificación ya traen el texto citado, con lo que el patrón de secretos reconoce tapado (no todo secreto posible; `ver` muestra el texto sin tapar), y las citas sobre imágenes van en su propia tanda en sonnet, con los PNG; el resto, en haiku
- Un hallazgo sin ningún número de página o línea no se verifica y queda en «Para decidir»

### Corregido

- Las citas «p. N», «pp. N-M», «pág.» y «página», también en listas, se reconocen en un lote de un solo PDF como citas de ese archivo; fuera de tramo dan un aviso y no invalidan la ficha

## [0.9.0] - 2026-11-06

### Cambiado

- Cada tarea de revisión indica su modelo: verificación en haiku (sonnet si cita una página con imagen), segunda pasada y coherencia en opus; los lectores siguen en el modelo de la sesión

### Corregido

- El presupuesto se ajusta a una corrida real: en la corrida medida, el anterior daba cerca de un tercio del peor caso

## [0.8.0] - 2026-11-05

### Agregado

- Exhaustiva por lotes: el objetivo queda fuera del hilo principal, con lectores que guardan fichas en disco y responden una línea
- Subagentes livianos `lector-auditoria` y `revisor-auditoria`, con pocas herramientas; el instalador los copia en `~/.claude/agents`
- Script auditoria_lotes.py: parte el objetivo, valida fichas y citas, cruza hechos, calcula estados y arma el HTML del informe

### Cambiado

- La corrida se puede retomar desde disco y el presupuesto se informa antes de lanzar los lectores
- La verificación de hallazgos y la segunda pasada releen sólo lo citado o la parte del punto

## [0.7.0] - 2026-11-05

### Cambiado

- La variante docente pasa a ser la variante de entrega académica, sin datos de ninguna materia: puntos y criterios salen de la consigna auditada

## [0.6.2] - 2026-11-05

### Corregido

- Quita de la carpeta del skill los datos de un proyecto puntual y las rutas locales

## [0.6.1] - 2026-11-05

### Corregido

- La lista de tareas no agrupa correcciones distintas en una sola casilla

## [0.6.0] - 2026-11-05

### Agregado

- Regla para documentos sin consigna: puntos, filas, severidad y veredicto fijos para que dos corridas sean comparables

## [0.5.0] - 2026-11-05

### Cambiado

- El nivel medio agrega cruces de detalle: nombre, actor y relaciones por ID, y métodos públicos que puedan saltear una regla

### Corregido

- La variante docente no parte los ítems de su lista de criterios

## [0.4.0] - 2026-11-05

### Agregado

- Punto fijo para lo que queda fuera de la consigna

### Cambiado

- El skill pasa a llamarse auditoria-sistemas y deja de ser experimental; la description vuelve a incluir cuándo usarlo
- Toda falla verificada es No, con la cuenta en la evidencia; Parcial queda para lo que no se pudo verificar
- Si un criterio admite dos lecturas se usa la más exigente; hay una fila por requisito en lugar de una por línea
- Falta queda para cuando no hay material; 0 % con material es Inicial
- La variante docente vuelve a la escala de la cátedra

### Eliminado

- Promedio general del sistema

## [0.3.0] - 2026-11-05

### Agregado

- Reglas para auditar artefactos sin una herramienta fija

### Cambiado

- Un punto sólo queda Completo sin defectos abiertos, aunque cumpla todos los criterios
- La escala Sí/Parcial/No y la severidad tienen criterios fijos, con una fila por línea del criterio
- Cada nivel exige más que el anterior: el simple no certifica, el medio registra cobertura e intenta refutar, y el exhaustivo suma una segunda pasada independiente
- El informe usa una plantilla general; la devolución docente pasa a ser una variante en references/

## [0.2.0] - 2026-11-04

### Cambiado

- El skill ya no depende de REA ni de reverse-engineer-anything: las fases describen qué revisar en los artefactos, sin nombrar herramientas
- La carpeta de los PDF sale de la memoria del usuario; si no está registrada, el skill la pregunta y la guarda

### Corregido

- La descripción del skill bajó de 1267 a 909 caracteres, dentro del límite de 1024

## [0.1.0] - 2026-11-04

### Agregado

- Skill `auditoria-sistemas-experimental` (versión interna 1.1): auditoría en tres niveles con informe de completitud en el formato de la devolución docente
