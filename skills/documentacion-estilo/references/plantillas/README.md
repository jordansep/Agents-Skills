# Plantillas de referencia

Una plantilla es el diseño tomado de un documento real que el usuario entregó como modelo («así es como lo quiero»). Funciona como una guía de marca: cuando el prompt de estilo la declara en `plantilla`, sus valores mandan sobre los predeterminados de `estilo-visual.md`.

| Plantilla | Archivo | Origen | Preajuste del configurador |
|---|---|---|---|
| Trabajo de campo (UNC · AUSI) | `trabajo-campo-unc.md` | *Trabajo de Campo v3.6* (y v2.2, *Ponderación de metodologías v3*) | Trabajo de campo UNC |
| Proforma de entrevista | `proforma-entrevista.md` | *Proforma de entrevista académica* (A4) | Proforma de entrevista |
| Ficha de una página | `ficha-1pager.md` | *State 1-pager* | Ficha 1-pager |
| Arquitectura en láminas | `arquitectura-presentacion.md` | *Arquitectura del sistema de gestión y aula virtual* | Arquitectura en láminas |
| Informe técnico / especificación | `informe-especificacion.md` | *Informe de relevamiento y diseño de arquitectura* (informe_av_v2) | Informe técnico |
| Informe de completitud (auditoría) | `informe-auditoria.md` | *Informe de completitud — Hemocentro* | Informe de auditoría |
| Diagramas de relevamiento | `diagramas.md` | Contexto, organigrama y secuencias AS-IS del Instituto; página Mermaid de la pasarela de pagos | — |

Para elegir: un entregable académico largo (informe, trabajo de campo) usa *Trabajo de campo*; un formulario para completar a mano, *Proforma*; un resumen de estudio de una página, *Ficha*; una arquitectura o propuesta para presentar, *Arquitectura en láminas*; una especificación o informe técnico, *Informe técnico*; la revisión de un entregable contra criterios, *Informe de completitud*. Los diagramas de cualquiera de ellos siguen *Diagramas de relevamiento*. Si no está claro, pregunta.

## Cómo se crea una plantilla a partir de un documento

1. Ejecuta el extractor sobre el documento (.docx):

   ```bash
   python3 scripts/extraer_estilo_docx.py ruta/al/documento.docx
   ```

   Informa página y márgenes, fuentes, estilos de título, tamaños, alineación, interlineado, tablas (rellenos, bordes y tamaño de celdas), leyendas («Tabla N», «Figura N», «Nota.»), encabezado y pie.
2. Convierte el documento a PDF (`soffice --headless --convert-to pdf`) y mira la portada, una página con tabla y una con figura. El extractor no ve la composición de la portada ni cómo se usa el color.
3. Escribe `references/plantillas/<nombre>.md` con las mismas secciones que `trabajo-campo-unc.md`: página, tipografía, color, tablas, figuras, portada, estructura y puntos abiertos.
4. Si el documento es inconsistente en algo, no elijas tú: anótalo en «Puntos abiertos» y pregúntalo según `memoria.md`.
5. Registra la plantilla en `memoria/decisiones.md` y agrégala a la tabla de arriba.
6. Si conviene, agrega un preajuste en `assets/configurador.html` (`PRESETS` y un botón `data-preset`).

Si llega un segundo documento del mismo tipo, compáralo con la plantilla existente. Lo que coincide confirma la regla; lo que difiere es un punto abierto, no un cambio automático.
