# Variante de entrega académica

Variante del *Entregable* de la skill. Se aplica sobre la plantilla general cuando se audita una
entrega académica contra su consigna, su rúbrica o una devolución docente, o cuando el usuario la
pide. Mantiene las cinco secciones y cambia sólo esto:

- **Encabezado:** `Informe de completitud — <Grupo> — <Caso>` y, abajo,
  `Corregido: <commit corto> del <AAAA-MM-DD> · Corte: <fecha o "sin corte"> · Modo: devolucion`.
- **Nombres de sección:** `Coherencia entre documentos`, `¿Listo para implementar?` y
  `Lista de tareas para el grupo`.
- **Tono:** se le habla al grupo, como en una devolución.
- **Severidad:** no se usa. El orden de la lista de tareas y la columna "Lo principal que falta"
  cumplen esa función; si algo es grave, decilo en el texto ("Sin esto no se puede entregar").
  Los secretos y demás hallazgos de seguridad sí la llevan.
- **Estado:** **Completo** de 90 a 100 %, **Avanzado** de 50 a 89 %, **Inicial** de 1 a 49 % y
  **Falta** con 0 %. Si la consigna trae otra escala, usá esa, para que se pueda comparar con su
  devolución.
- **Criterios:** también se evalúa como en una devolución: Sí se cumple, Parcial se cumple en parte
  y No no se cumple.
- **Marca obligatoria:** si un punto queda Completo con defectos abiertos, escribí
  `Completo con defectos abiertos` en el estado y en el resumen. Lo demás de la skill sigue valiendo,
  incluido lo que cada nivel exige.
- **¿Listo para implementar?:** responde por las piezas que la consigna pide terminadas o por las
  del próximo tramo de trabajo. Si no hay ninguna elegida, usá la primera del plan.

## Puntos y criterios

Salen de la consigna, no de lo que el trabajo dice hacer:

- **Puntos:** uno por cada punto de la consigna, en su orden y con su nombre. Si la consigna fija un
  archivo por punto, usalo en la línea `Archivo:`.
- **Filas:** cada ítem de la consigna es una fila, tal como está escrito. No lo partas aunque diga
  «y»: «Título y estado» es una sola fila.
- **Consigna y devolución:** si difieren, chequeá los dos criterios y decí cuál se aplicó.
- **Lo que no se entrega:** lo que la consigna aclare que no cuenta como entregable no se evalúa.

## Estructura del informe

1. **Resumen:** un párrafo (qué está bien hecho, qué falta, la consecuencia y "Lo mejor
   logrado: …") y una tabla `Punto | Estado | Completitud | Lo principal que falta`.
2. **Detalle por punto:** título `N · Nombre — Estado (X %)`, línea `Archivo: …`, tabla
   `Criterio | ¿Cumple? | Evidencia`, "Observaciones de …" si hay algo para observar y
   "Para completarlo:".
3. **Coherencia entre documentos:** un párrafo por tema, con lo que dice cada fuente y su ubicación,
   y al final "Lo que está bien: …".
4. **¿Listo para implementar?:** por pieza, la lista de preguntas que haría quien la tome con lo que
   hay hoy (formato de datos, campos y tipos, mensajes exactos, carga inicial, casos borde, qué pasa
   si se corrige o vence, qué ve el usuario).
5. **Lista de tareas para el grupo:** casillas `[ ]`, ordenadas por dependencia, cada una con el
   punto o el lugar ("Punto 6: …. Destraba los puntos 7, 8 y 9.").
