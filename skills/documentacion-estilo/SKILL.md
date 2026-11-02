---
name: documentacion-estilo
description: Prompteador de estilo para documentación técnica y académica. Define la estructura del documento según la metodología elegida (RUP, UP, Scrum/ágil, ISO/IEEE 29148, Diátaxis o estructura académica), cómo se muestra cada componente (títulos, tablas, figuras, código, avisos, diagramas), la tipografía, la paleta de color y las normas de escritura. Úsalo para redactar, estructurar, diseñar o revisar manuales de usuario, tesis, especificaciones de requisitos, informes, diagramas o cualquier documento que deba seguir un estilo uniforme.
---

# Documentación — prompteador de estilo

Este skill fija cómo se ve y cómo se escribe un documento. Sirve para manuales, tesis, especificaciones, informes y diagramas. El documento final debe cumplir tres cosas: la estructura corresponde a la metodología declarada, cada componente se ve igual en todo el texto y la redacción sigue las mismas normas.

Carga solo la referencia que necesites:

- `references/metodologias.md`: estructuras (esqueletos de capítulos) para RUP, UP, Scrum, ISO/IEEE 29148, Diátaxis, tesis, y notaciones de diagramas.
- `references/estilo-visual.md`: grilla, jerarquía de títulos, componentes, tipografía, paleta de color y reglas para diagramas.
- `references/escritura.md`: normas de redacción en español, ortotipografía, reglas por tipo de documento y ejemplos.

## Paso 1: definir el encargo

Antes de escribir, fija estos parámetros. Si el usuario ya los dio, úsalos. Si no, aplica el valor por defecto y declaralo en la primera línea de tu respuesta. Pregunta solo si el tipo de documento es ambiguo y no puedes inferirlo.

| Parámetro | Opciones | Por defecto |
|---|---|---|
| Tipo de documento | manual de usuario, tesis, especificación de requisitos, informe técnico, diagrama, documento de arquitectura, otro | informe técnico |
| Metodología | RUP, UP, Scrum/ágil, ISO/IEEE 29148, Diátaxis, académica, ninguna | ninguna (estructura genérica) |
| Audiencia | técnica, no técnica, académica, mixta | mixta |
| Medio | impreso (A4 o carta), digital, ambos | digital |
| Idioma y variante | español neutro, español rioplatense | español neutro |
| Tratamiento | usted, tú, vos, impersonal | usted (manuales); impersonal (tesis y especificaciones) |
| Citas | APA 7, IEEE, normas institucionales | APA 7 (solo si hay citas) |

Si la institución o la empresa tiene reglamento propio (por ejemplo, el de la facultad para una tesis), ese reglamento manda sobre los valores por defecto. Dilo explícitamente y pide el documento si lo tienes.

## Paso 2: construir la estructura

1. Elige el esqueleto de capítulos de `references/metodologias.md` según la metodología.
2. No mezcles metodologías en el mismo documento. Si hace falta combinarlas (por ejemplo, RUP para el proceso y Diátaxis para el manual), declara qué parte sigue cuál.
3. Cada documento lleva al inicio una tabla de control de versiones (versión, fecha, autor, cambios) y un índice generado.
4. Si falta información, escribe `[PENDIENTE: descripción]` en lugar de inventar datos, cifras, citas o referencias.

## Paso 3: aplicar el estilo visual

Sigue `references/estilo-visual.md` para:

- Jerarquía de títulos: máximo cuatro niveles (1, 1.1, 1.1.1, 1.1.1.1). Los títulos no llevan punto final.
- Componentes: párrafos, listas, pasos de manual, tablas, figuras, código, avisos, ecuaciones y glosario se construyen siempre igual.
- Tipografía: dos familias como máximo, con la escala definida para medio impreso o digital.
- Color: usa solo los tokens de la paleta. Nunca transmitas significado únicamente con color.
- Diagramas: notación estándar, título, número, leyenda y fuente.

## Paso 4: aplicar las normas de escritura

Sigue `references/escritura.md`. Como mínimo:

- Una idea por párrafo. Oraciones de hasta 25 palabras, con voz activa.
- Mismo tratamiento (usted, tú o impersonal) en todo el documento.
- Mismo término para el mismo concepto. Cada sigla se define la primera vez que aparece.
- Los nombres de botones, menús y campos de la interfaz se escriben tal cual aparecen en la interfaz, en negrita.

## Reglas no negociables

- Toda figura, tabla y diagrama tiene número, título y fuente, y se menciona en el texto.
- Todo aviso sigue la misma forma: etiqueta, icono y texto. No hay avisos sin etiqueta.
- El contraste texto/fondo es de 4,5:1 como mínimo (WCAG AA). Las imágenes digitales tienen texto alternativo.
- No inventes datos, cifras, autores, citas ni referencias. Marca lo que falte con `[PENDIENTE]`.
- Si el usuario pide un formato de archivo concreto (.docx, .pdf, .pptx), genera el contenido con este estilo y usa el skill de ese formato para el archivo.

## Lista de verificación antes de entregar

- [ ] La metodología está declarada y la estructura de capítulos corresponde a ella.
- [ ] Los parámetros del Paso 1 (tratamiento, variante, medio, citas) son los mismos en todo el documento.
- [ ] Los títulos siguen la numeración y la jerarquía definidas, sin punto final.
- [ ] Tablas, figuras y diagramas tienen número, título, fuente y están citados en el texto.
- [ ] Las siglas se definen al primer uso y el glosario contiene los términos técnicos.
- [ ] Los avisos usan los cuatro tipos definidos con etiqueta e icono.
- [ ] Los pares de color cumplen contraste de 4,5:1.
- [ ] Los números siguen la convención del documento (coma decimal, espacio para miles, unidades SI).
- [ ] No quedan marcadores sin resolver salvo los `[PENDIENTE]` que se señalaron al usuario.
