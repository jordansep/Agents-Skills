# Formato de la devolución docente (MyD 2026)

Variante del *Entregable* de la skill. Sale del informe de completitud que la cátedra
envió al Grupo 3 el 29/10/2026 ("MyD 2026 · Trabajo integrador · Revisión temprana (no es
corrección) · Grupo 3"; copia local en
`D:\Experimentos\BonoCorreciones\Fuente\`). Es un modelo de estructura y de criterios: no
copies sus conclusiones, que corresponden a una versión vieja del repo.

## Variante docente

Se aplica sobre la plantilla general de la skill cuando se audita contra la consigna o la devolución
de una cátedra. Mantiene las cinco secciones y cambia sólo esto:

- **Encabezado:** `Informe de completitud — <Grupo> — <Caso>`.
- **Nombres de sección:** `Coherencia entre documentos`, `¿Listo para implementar?` y
  `Lista de tareas para el grupo`.
- **Tono:** se le habla al grupo, como en la devolución.
- **Severidad:** la devolución no usa severidades. El orden de la lista de tareas y la columna
  "Lo principal que falta" cumplen esa función; si algo es grave, decilo en el texto ("Sin esto no se
  puede liberar ninguna unidad"). Los secretos y demás hallazgos de seguridad sí la llevan.
- **Estado:** se usa la escala de la cátedra, para que se pueda comparar con su devolución:
  **Completo** de 90 a 100 %, **Avanzado** de 50 a 89 %, **Inicial** de 1 a 49 % y **Falta** con 0 %
  (Inicial se agregó para los puntos empezados que no llegan a la mitad).
- **Escala:** también es la de la cátedra, para que los porcentajes se puedan comparar: Sí se cumple,
  Parcial se cumple en parte y No no se cumple. Los criterios son los de la lista de abajo.
- **Marca obligatoria:** si un punto queda Completo con defectos abiertos, escribí
  `Completo con defectos abiertos` en el estado y en el resumen. Lo demás de la skill sigue valiendo,
  incluido lo que cada nivel exige.
- **Punto 8:** "¿Listo para implementar?" responde por las historias del punto 8 o las del próximo
  sprint. Si no hay historias elegidas, usá la del primer sprint.

## Estructura, tal como la usa la cátedra

1. **Encabezado:** `Informe de completitud — Grupo 3 — Hemocentro Municipal de Córdoba` y,
   abajo, `Corregido: e506313 del 2026-10-29 · Corte: sin corte · Modo: devolucion`.
2. **Resumen:** un párrafo (qué está bien hecho, qué falta, la consecuencia y "Lo mejor
   logrado: …") y una tabla `Punto | Estado | Completitud | Lo principal que falta` con los 11
   puntos.
3. **Detalle por punto:** título `N · Nombre — Estado (X %)`, línea `Archivo: …`, tabla
   `Criterio | ¿Cumple? | Evidencia`, viñetas opcionales de "Observaciones de …" y la sección
   "Para completarlo:".
4. **Coherencia entre documentos:** un párrafo por tema ("HU-003, el texto no coincide. El
   repo dice … (docs/01:90,123). El work item #19 dice …"), y al final "Lo que está bien: …".
5. **¿Listo para implementar?:** por historia, la lista de preguntas que haría quien la
   programe con lo que hay hoy (formato de datos, campos y tipos, mensajes exactos, carga
   inicial, qué clase y qué método, casos borde, qué pasa si se corrige, si vence, si es
   automático, qué ve el usuario).
6. **Lista de tareas para el grupo:** casillas `[ ]`, ordenadas por dependencia, cada una con
   el punto o el lugar ("Punto 6: …. Destraba los puntos 7, 8 y 9.", "Board: …", "README: …").

Valores de completitud de la devolución, que confirman la regla Sí = 1, Parcial = 0,5 y No = 0:
punto 3 con 4 criterios (Parcial, Sí, No, Sí) = 63 %; punto 4 con 6 criterios (5 Sí y 1
Parcial) = 92 %; punto 11 con 6 criterios (Parcial, Sí, No, Parcial, Sí, Sí) = 67 %.

## Criterios por punto (consigna del trabajo integrador)

| Punto | Archivo | Criterios |
|---|---|---|
| 1 · Backlog ágil desde OAS | `docs/01-vision-y-backlog.md` | Visión en un párrafo, derivada del mandato · Al menos 3 épicas · Cada épica con ≥ 2 features · ≥ 15 HU en formato Como/quiero/para · INVEST · MoSCoW y SP en cada HU · Cada épica dice de qué parte de OAS sale |
| 2 · Plan de sprints | `docs/02-plan-de-sprints.md` | Duración y capacidad con criterio · ≥ 3 sprints con objetivo y HU · Suma vs. capacidad · Se respetan las dependencias · Iterations en el Board y HU asignadas |
| 3 · Contexto y casos de uso | `docs/03-contexto-y-casos-de-uso.md` | Diagrama de contexto (caja negra, actores, externos, flujos rotulados de entrada y salida) · ≥ 6 CU con actores · include/extend donde corresponde · Trazabilidad CU ↔ HU |
| 4 · RNF y arquitectura | `docs/04-rnf-y-arquitectura.md` | ≥ 5 RNF cuantificados · Estilo elegido · Justificación desde los RNF · Diagrama de componentes · Despliegue UML (nodos, artefactos, protocolos) · Coherencia componentes ↔ despliegue |
| 5 · ADR | `docs/adr/ADR-XXX-*.md` | Título y estado · El contexto cita los RNF por id · ≥ 2 alternativas con pros y contras · Decisión explícita · Consecuencias positivas y negativas |
| 6 · Diseño de clases y patrones | `docs/06-diseno-de-clases.md` | ≥ 10 clases · Atributos tipados y firmas completas · Multiplicidad, interfaces y abstractas · ≥ 2 patrones GoF · Problema concreto por patrón · Rol → clase · Por qué ese patrón y qué pasaría sin él · Coherencia con CU y HU |
| 7 · Estados y secuencia | `docs/07-estados-y-secuencia.md` | Diagrama de estados de la entidad central · Secuencia de una HU del punto 8 · Mensajes = métodos del diagrama de clases · Camino alternativo o de error |
| 8 · HU completas | `docs/historias/HU-XXX.md` | Las 2 HU, cada una en su archivo · Historia, contexto y reglas · ≥ 4 Dado/Cuando/Entonces con uno de error · Qué queda fuera · Notas de diseño y link a capturas · Datos de prueba concretos · Dependencias, estimación y DoR · Al menos una usa un patrón del punto 6 |
| 9 · Plan de testing y casos de prueba | `docs/testing/` | Alcance · Pirámide con proporción · Prueba ligada a un RNF · Entornos, datos, herramientas, cuándo · Criterios de entrada y salida · Un caso por cada criterio de las HU del punto 8 · Formato de cada caso · Un caso negativo y uno de valor límite por HU · Matriz criterio ↔ caso |
| 10 · Prototipo y evaluación heurística | `docs/10-prototipo-y-heuristicas.md` y `prototipo/` | ≥ 2 pantallas, una con error; capturas y link · ≥ 3 heurísticas con pantalla, cumple, evidencia y severidad · Argumentación desde la heurística · ≥ 1 corrección con antes y después |
| 11 · Azure DevOps | `README.md` y el Board | Jerarquía Epic → Feature → User Story · Iterations con los sprints · HU del punto 8 completas en el work item · Estructura de repo de la consigna · README con integrantes, caso, mail, Board y tabla de los 11 puntos · Fuentes de los diagramas |

El Issue #47 de Azure (transcripción de la consigna) agrega para el punto 10 que las
heurísticas salen de las 21 reglas (Shneiderman, Nielsen, Pierotti), que son ≥ 3 **por
pantalla** y con captura señalada; y el Issue #48, para el punto 11, que el proyecto sea
**público** con el docente agregado. Cuando la consigna y la devolución difieran, chequeá
los dos criterios y decí cuál se aplicó.

Lo que la devolución aclara que **no cuenta como entregable**: las carpetas `.claude/` y
`.agents/` (configuración del asistente de IA).
