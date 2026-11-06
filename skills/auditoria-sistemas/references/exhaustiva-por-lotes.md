# Exhaustiva por lotes

Cómo cumplir todo lo del nivel exhaustivo sin agotar los tokens. **El hilo principal no lee el objetivo:**
cada parte la lee un lector, que guarda su ficha en disco. Vos trabajás con el plan, lo consolidado y
las citas puntuales. No baja ninguna exigencia: todo el entregable se lee, sólo que no acá.

Los comandos son de `scripts/auditoria_lotes.py` (`A` abajo) y siempre llevan `--trabajo <carpeta>`, en
el scratchpad. Todo el estado queda ahí: si la corrida se corta, `A estado` dice cómo seguir.

## 1. Preparar

`A preparar <objetivo…> --foco "<foco>" [--puntos puntos.json] [--limite 20000]`

Admite PDF, Word (con pandoc), texto y carpetas. Imprime el índice y el presupuesto; no leas los lotes.

- **Sin consigna:** los puntos salen del índice del documento. Si avisa que no hay índice, mirá las
  primeras páginas con `A ver` y pasale `--puntos`.
- **Con consigna:** leé sólo la consigna y escribí `puntos.json`, usando el índice para ubicar cada punto:
  `[{"n": 1, "nombre": "…", "criterios": ["…"], "fuentes": ["a.pdf:10-30", "docs/b.md"]}]`.

**Presupuesto.** Decile al usuario en una línea cuántos lotes y tokens estimó. Es una estimación: cada
subagente liviano cuesta unos 12.000 tokens aunque lea poco, y uno `general-purpose`, unos 50.000. Si el script dice que supera el umbral, o si el usuario
sabe que le queda poca cuota, preguntale antes de lanzar: seguir, partir en varias sesiones (el trabajo queda
en disco), usar `sonnet` en los lectores o acotar puntos. Lo que no se lea queda `sin_leer` y ese punto
no llega a Completo.

## 2. Leer

Por cada lote, un subagente `lector-auditoria` con este único prompt:
`Leé y seguí <trabajo>/lotes/L03.prompt.md`

**Si `lector-auditoria` o `revisor-auditoria` no figuran entre tus tipos de agente, frená y avisale al
usuario:** se instalan con `scripts/instalar_skills.ps1` o copiando `agents/` del skill en `~/.claude/agents/`,
y se cargan al abrir una sesión nueva. Sólo si elige seguir igual, usá `general-purpose`, que multiplica el
piso por cuatro.

- **De a tres por vez**, en segundo plano. No lances todos juntos: si se acaba la cuota, se pierde lo que
  esté en curso. Lanzá los siguientes a medida que terminan.
- **Nunca `fork`** (arrastra todo el contexto) **ni `Explore`** (lee fragmentos, no todo el texto).
- Usá el modelo que el usuario haya elegido para los lectores; si no eligió, el de la sesión.
- El archivo de cada lote ya trae las reglas y el texto. No lo leas ni lo copies en el prompt, y no pidas
  un resumen: la respuesta es una línea.
- Si uno falla, corré `A estado` antes de relanzarlo: la ficha puede estar escrita. Relanzá sólo lo que
  figure pendiente o inválido.

## 3. Consolidar y revisar

`A consolidar` escribe `consolidado.md`, que **es lo único que leés completo**, y genera los prompts de
la revisión. Lanzá, con las mismas reglas de arriba, lo que indique: la segunda pasada con
`lector-auditoria`, y la verificación y la coherencia con `revisor-auditoria`.

| Prompt | Qué hace | Cuándo |
|---|---|---|
| `lotes/Lxx.segunda.prompt.md` | Segunda pasada a ciegas del lote, sin ver la ficha | Lotes con un punto candidato a Completo |
| `verifica/Vxx.prompt.md` | Relee sólo las páginas citadas, por tandas de 40 hallazgos | Si hay hallazgos |
| `coherencia.prompt.md` | Busca contradicciones entre capítulos usando sólo los hechos | Una vez |

Volvé a correr `A consolidar`: compara las pasadas, aplica la verificación y deja sólo lo que requiere
decisión. Los otros frentes (historia, CVE, normas, devoluciones) van cada uno a un subagente que escribe
`frentes/<tema>.md`, de 40 líneas como máximo, con citas.

## 4. Resolver sólo lo discutido

Por cada diferencia, hallazgo que no se sostuvo, hallazgo Crítica o Alta y contradicción, **releé vos** la
fuente con `A ver a.pdf:12 docs/b.md:10-20`. No abras un lote entero: si una decisión exige más
de unas páginas, lanzá un subagente sobre esas páginas. Lo que no sea discutido no se relee.

## 5. Sintetizar y entregar

Escribí `sintesis.json` con **sólo lo que requiere criterio**. El script calcula completitud y estado,
arma el detalle, las tareas y los anexos: no los redactes ni los copies.

```json
{
  "equipo": "…", "sistema": "…", "corregido": "abc1234 del 2026-11-05", "corte": "sin corte",
  "linea_chica": "Versión, criterio, herramientas y MCP o API usados, y los que no se pudieron usar",
  "variante": "general",
  "resumen": "Qué está bien, qué falta, la consecuencia y «Lo mejor logrado: …».",
  "falta": {"4": "Si querés cambiar «lo principal que falta» de un punto"},
  "conciliacion": [
    {"id": "P4:id-de-consolidado", "resolucion": "Qué se releyó y por qué",
     "fila": {"cumple": "Sí", "evidencia": "… (a.pdf:12)"}, "descartar": false, "defecto": null}
  ],
  "puntos_extra": [{"n": 20, "nombre": "Forma del documento", "cobertura": {"completo": ["a.pdf"], "parcial": [], "sin_leer": []},
    "filas": [], "defectos": [], "observaciones": [], "refutar": "…", "para_completar": [], "segunda_pasada": false}],
  "coherencia": [{"tema": "…", "texto": "El capítulo 2 dice «…» (a.pdf:9). El 5 dice «…» (a.pdf:40). Decidan cuál vale.",
    "tarea": "Unificar …", "puntos": [2, 5]}],
  "coherencia_bien": "Los cruces que sí cierran, y lo que no se pudo verificar y por qué.",
  "listo_para": "implementar",
  "listo": [{"pieza": "…", "veredicto": "no listo", "preguntas": ["¿…?"]}],
  "tareas_primero": ["P6-1"], "destraba": {"P6-1": "Destraba los puntos 7 y 8."},
  "version": [{"hallazgo": "…", "estado": "Sigue en la versión vigente"}],
  "sin_analizar": ["Qué no se pudo analizar y por qué"]
}
```

`puntos_extra` lleva los puntos que no salen de un lote: `Forma del documento`, `Datos personales y
seguridad` o `Adicional · Seguridad y otros defectos`. Se evalúan con el barrido y las notas transversales
del consolidado; el barrido no copia valores. En un punto extra, `segunda_pasada` va en `true` sólo si un
subagente lo auditó a ciegas.

`variante` es `general` o `academica`; con consigna, `"umbrales": [90, 50, 1]` fija otra escala de estados.

Después:

1. `A armar --sintesis sintesis.json --salida informe.html`. Si avisa de faltantes, corregí la síntesis.
2. Generá el PDF con el comando del *Entregable*.
3. `A revisar-pdf <pdf>`: en lugar de leer todo el PDF, mirá sólo las páginas que marque.
4. Seguí con la carpeta de informes y el cierre del *Entregable*.

## Reglas que no se aflojan

- **Coherencia entre capítulos:** nunca la declares sin haber corrido `coherencia.prompt.md`. Sin ella, el
  script deja «Coherente con las otras secciones» en Parcial.
- **Completo:** el script sólo lo da con 100 %, sin defectos abiertos, sin partes sin leer, con intento de
  refutar y con la segunda pasada conciliada. Si no podés lanzar subagentes, decilo: no hay lectores ni
  segunda pasada, y ningún punto queda Completo.
- **Texto extraído:** las páginas con imagen o sin texto figuran en el prompt de cada lector, que las mira
  como imagen. Si no puede, quedan en `cobertura.parcial`.
