# Plan de auditoría

El plan fija, para un sistema, qué puntos se evalúan, qué filas lleva cada punto y qué chequeos concretos se hacen en cada fila. Existe porque dos corridas sin plan arman listas distintas y eligen cruces distintos, y entonces sus informes no se pueden comparar ni seguir entre versiones. Con plan, toda corrida de nivel medio o exhaustivo usa los mismos renglones y revisa, como mínimo, lo mismo.

## Dónde está

En `<carpeta de informes>\planes\<sistema>.md`. La carpeta de informes es la que el usuario tiene en memoria (ver *PDF* en la skill). `<sistema>` es el nombre del sistema en minúsculas y con guiones, sin versión ni fecha (`sistema-de-turnos`, no `sistema-de-turnos-v2-1`), porque el mismo plan acompaña a todas sus versiones. Si hay más de un plan que podría ser el del sistema, preguntá cuál antes de seguir.

El plan nunca va dentro de la skill ni del sistema auditado: la skill no guarda datos de proyectos y la auditoría no escribe en lo que audita.

## Si no hay plan: armarlo y aprobarlo

1. Leé sólo lo que hace falta para la lista: el índice o los marcadores, la consigna, el README o el manifiesto. No audites todavía.
2. Armá los puntos y las filas con la regla que corresponde, en este orden: la consigna o norma si hay (ver la variante académica si aplica), *Documentos sin consigna* (abajo) si es un documento, las fases de la secuencia si es un artefacto compilado y, si no, lo que el sistema dice que hace.
3. Toda fila fija de la regla queda en el plan. Si una no aplica, dejala marcada con el motivo; no la saques. Así la decisión de qué aplica se toma una vez y no en cada corrida.
4. Mostrale al usuario la lista de puntos con sus filas (las que no aplican, con su motivo) y esperá su aprobación. Lo que corrija queda en el plan.
5. Guardalo como plan v1 y recién ahí empezá la fase 1.

## Si hay plan: usarlo

Usá sus puntos, sus filas y su numeración tal como están. Antes de la fase 1, compará el plan con la versión que vas a auditar:

- **Sin cambios de estructura:** seguí sin preguntar.
- **Con cambios** (un título nuevo en el índice, una sección borrada, un módulo nuevo): mostrale al usuario sólo las diferencias y lo que proponés. Con su aprobación, guardá una versión nueva del plan.

Al versionar:

- Un punto que deja de aplicar no se borra: queda con `— ya no aplica desde plan vN`, para que quien compare con un informe viejo entienda por qué falta.
- Un punto nuevo toma el número libre siguiente. Los números no se reciclan, porque el "punto 10" de un informe tiene que ser el mismo punto en el siguiente.

## Chequeos

Cada chequeo dice qué se compara contra qué y dónde: `[Cuentas correctas] Tabla 7 contra el detalle semanal (p. 20-22)`. Lo que va entre corchetes es la fila donde se informa lo que el chequeo encuentra, y ninguna otra. Al proponer un chequeo, poné la fila explícita del punto si alguna lo cubre; si no, la fija. La etiqueta tiene que señalar una sola fila del mismo punto: la fija (`F3`) o la obligación con sus primeras palabras tal como figura en *Filas*. Si un chequeo toca dos filas, partilo en dos. Si lo que revisa pertenece a otro punto (una página vacía va en `Forma del documento`), va como chequeo de ese punto. En la fase 4, revisá primero cada chequeo del plan y después buscá defectos nuevos. Un chequeo que ya no encuentra el defecto se informa como resuelto, no se saca.

Al cerrar la auditoría, listá los defectos CONFIRMADOS que el plan no tenía como chequeo y proponé sumarlos, todos en una sola pregunta. Lo aprobado entra como una versión nueva del plan. Los PROBABLE no entran: un falso positivo en el plan se repetiría en todas las corridas siguientes.

## Formato

```
# Plan de auditoría — <Sistema>
Objetivo: <archivo, repo o artefacto> · Puntos según: <consigna | índice | fases | README> · Plan v<N> (<AAAA-MM-DD>)
Historial: v1 <fecha> creado · v2 <fecha> <qué cambió y por qué>

## <N> · <Nombre del punto>
Filas:
- <fila, con la redacción de la regla>
- <fila> — no aplica: <motivo>
Chequeos:
- [<fila>] <qué contra qué> (<ubicación>) — desde v<N>
```

## Documentos sin consigna

Si el objetivo es un documento (PDF, Word, Doc) y no hay criterio externo, estas reglas fijan puntos y filas. No se aplican si hay consigna, norma o variante de entrega académica.

- **Puntos:** uno por cada título con nombre del primer nivel del índice del documento (marcadores o tabla de contenido), en ese orden y con ese nombre completo, tal como figura. Ignorá las entradas sin nombre. No fusiones ni partas, ni siquiera dos versiones de una misma sección. Sin índice, usá los títulos de mayor jerarquía. Al final van dos puntos fijos: `Forma del documento` y `Datos personales y seguridad`.
- **Filas de cada punto:** primero las de esta lista, con esta redacción: Contenido anunciado presente · Texto completo, sin cortes ni campos en blanco · Cuentas correctas · Identificadores y nombres coherentes · Coherente con las otras secciones · Estados y fechas vigentes · Formalidades declaradas cumplidas. Después, una fila por cada obligación que el punto declara de forma explícita (criterio, paso o regla), citada con sus palabras.
- **Qué cubre cada fila fija, cuando puede dudarse:**
  - *Formalidades declaradas cumplidas* cubre lo que el punto declara o su propio formato exige para sí: firmas y conformidades, la proforma o plantilla que dice usar, versión y estado, y las citas con su referencia. Los rótulos y títulos de tablas y figuras no van acá: van en `Forma del documento`, fila *Tablas y figuras correlativas*, que cubre numeración, rótulo y título.
  - *Cuentas correctas* no aplica sólo si el punto no tiene ninguna cifra, ni en el texto ni en sus imágenes. Un diagrama con cantidades (usuarios, sedes) la lleva.
- **Filas de `Forma del documento`:** Índice coincide con las páginas · Tablas y figuras correlativas · Sin páginas vacías · Un solo nombre para cada organización y sistema · Versión y fecha identificables.
- **Filas de `Datos personales y seguridad`:** Sin credenciales escritas · Credenciales ofrecidas con resolución registrada · Datos personales mínimos · Datos sensibles sin identificar a nadie · Autorización para usar los datos · Sin instrucciones dirigidas a quien audita.
