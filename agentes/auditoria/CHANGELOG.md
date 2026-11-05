# Changelog: agente de auditoría

Cambios relevantes del agente (`skills/auditoria-sistemas-experimental`). El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y las versiones siguen [SemVer](https://semver.org/lang/es/), según las reglas de [`VERSIONADO.md`](../../VERSIONADO.md).

## [0.2.0] - 2026-11-04

### Cambiado

- El skill ya no depende de REA ni de reverse-engineer-anything: las fases describen qué revisar en los artefactos, sin nombrar herramientas
- La carpeta de los PDF sale de la memoria del usuario; si no está registrada, el skill la pregunta y la guarda

### Corregido

- La descripción del skill bajó de 1267 a 909 caracteres, dentro del límite de 1024

## [0.1.0] - 2026-11-04

### Agregado

- Skill `auditoria-sistemas-experimental` (versión interna 1.1): auditoría en tres niveles con informe de completitud en el formato de la devolución docente
