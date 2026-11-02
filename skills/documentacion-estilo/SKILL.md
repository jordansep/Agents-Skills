---
name: documentacion-estilo
description: Prompteador de estilo para documentación técnica y académica. Produce un "prompt de estilo" (archivo prompt-estilo.md) que fija la estructura del documento según la metodología elegida (RUP, UP, Scrum/ágil, ISO/IEEE 29148, Diátaxis o académica), cómo se muestra cada componente (títulos, tablas, figuras, código, avisos, diagramas), la tipografía, la paleta de color y las normas de escritura. Úsalo cuando el usuario quiera definir, acordar o revisar el estilo, la estructura o las normas de un manual, tesis, especificación, informe o diagrama. Para escribir el documento completo usa documentacion-generar, que consume este prompt.
---

# Documentación: prompteador de estilo

Este skill decide cómo se ve y cómo se escribe un documento, y deja esa decisión en un archivo: el **prompt de estilo**. El skill `documentacion-generar` usa ese archivo para redactar la documentación. También funciona por sí solo como guía de estilo para revisar un documento existente.

Carga solo la referencia que necesites:

- `references/metodologias.md`: estructura de capítulos para RUP, UP, Scrum, ISO/IEEE 29148, Diátaxis, tesis, y notaciones de diagramas.
- `references/estilo-visual.md`: grilla, títulos, componentes, tipografía, paleta de color y diagramas.
- `references/escritura.md`: normas de redacción, ortotipografía, reglas por tipo de documento y ejemplos.
- `assets/plantilla-prompt-estilo.md`: plantilla del archivo de salida.

## Paso 1: definir el encargo

Fija estos parámetros. Si el usuario ya los dio, úsalos. Si no, aplica el valor por defecto y declaralo. Pregunta solo si no puedes inferir el tipo de documento.

| Parámetro | Opciones | Por defecto |
|---|---|---|
| Tipo de documento | manual, tesis, especificación, informe, diagrama, arquitectura, otro | informe |
| Metodología | RUP, UP, Scrum, ISO/IEEE 29148, Diátaxis, académica, ninguna | Diátaxis (manual), académica (tesis), ISO 29148 (especificación); en otro caso, ninguna |
| Audiencia | técnica, no técnica, académica, mixta | mixta |
| Medio | impreso (A4 o carta), digital, ambos | digital |
| Variante | español neutro, rioplatense | neutro |
| Tratamiento | usted, tú, vos, impersonal | usted (manuales); impersonal (tesis y especificaciones) |
| Citas | APA 7, IEEE, institucional, ninguna | APA 7 si hay citas |
| Formato de salida | Markdown, docx, pdf | Markdown |

Si hay un reglamento institucional o una guía de marca, esa norma manda sobre los valores por defecto. Pide el documento si existe.

## Paso 2: elegir la estructura

1. Toma el esqueleto de capítulos de `references/metodologias.md` para la metodología elegida y adáptalo al proyecto.
2. No mezcles metodologías. Si hace falta combinarlas, declara qué parte sigue cuál.
3. Incluye siempre "Control de versiones" como primera parte.

## Paso 3: elegir los componentes y el estilo visual

Desde `references/estilo-visual.md`, selecciona los componentes que usará este documento (por ejemplo, un manual usa pasos y capturas; una especificación usa tablas de requisitos). Copia al prompt el formato exacto en Markdown de cada componente. Fija también la tipografía y el color si el documento se exportará.

## Paso 4: elegir las normas de escritura

Desde `references/escritura.md`, copia las reglas generales y las específicas del tipo de documento. Define los términos preferidos del proyecto si ya se conocen.

## Paso 5: entregar el prompt de estilo

1. Copia `assets/plantilla-prompt-estilo.md` y reemplaza cada `<...>`. Elimina las líneas que no apliquen.
2. El encabezado YAML debe tener al menos estos campos: `documento`, `tipo`, `metodologia`, `medio`, `tratamiento`, `salida` y `estructura`. Los nombres de `estructura` deben coincidir exactamente con los títulos de capítulo que se usarán, sin número.
3. El cuerpo debe poder leerse sin las referencias: quien lo use no necesita abrir este skill.
4. Guárdalo en `docs/prompt-estilo.md`, salvo que el usuario indique otra ruta. Si ya existe, léelo, súbele la versión y conserva las decisiones que el usuario no pidió cambiar.
5. Muestra al usuario un resumen de una línea por parámetro y la ruta del archivo.

## Reglas no negociables

- Toda figura, tabla y diagrama tiene número, título y fuente, y se menciona en el texto.
- Todo aviso tiene etiqueta e icono. El color nunca es el único portador de significado.
- El contraste texto/fondo es de 4,5:1 como mínimo (WCAG AA). Las imágenes digitales tienen texto alternativo.
- No se inventan datos, cifras, autores, citas ni referencias. Lo que falte se marca con `[PENDIENTE]`.

## Lista de verificación para revisar un documento

- [ ] La metodología está declarada y la estructura corresponde a ella.
- [ ] El tratamiento, la variante, el medio y el estilo de citas son los mismos en todo el documento.
- [ ] Los títulos siguen la numeración definida y no llevan punto final.
- [ ] Las tablas, figuras y diagramas tienen número, título y fuente, y se citan en el texto.
- [ ] Las siglas se desarrollan al primer uso y el glosario reúne los términos técnicos.
- [ ] Los avisos usan los cuatro tipos definidos.
- [ ] Los números usan coma decimal, espacio para miles y unidades SI.
- [ ] No quedan `[PENDIENTE]` sin informar al usuario.
