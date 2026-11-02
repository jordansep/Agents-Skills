# Plantilla: Documento de arquitectura en láminas

Diseño tomado de *arquitectura-sistema-gestion-aula-virtual.pdf* (12 láminas), que el usuario entregó como modelo (DEC-007). Es un documento de arquitectura **en formato de presentación**: cada página es una lámina horizontal con una sola idea.

## 1. Página

| Aspecto | Valor |
|---|---|
| Papel | A4 **horizontal** (29,7 × 21 cm) |
| Márgenes | Unos 1,5 cm |
| Estructura | Una idea por lámina: antetítulo, título, bajada de 1 a 3 líneas y el contenido (tarjetas o diagrama) |
| Medio | PDF digital |

## 2. Tipografía

| Elemento | Fuente | Estilo | Color |
|---|---|---|---|
| Antetítulo | Segoe UI | Negrita, unos 7 pt, mayúsculas con espaciado amplio («C4 · NIVEL 1») | Azul `#1F5FBF` |
| Título de lámina | Segoe UI | Negrita, 20 a 26 pt; en la portada, en dos líneas | Azul muy oscuro `#173A6D` |
| Bajada | Segoe UI | Regular, unos 9 pt | Gris azulado `#5B6C85` |
| Texto de tarjetas y cajas | Segoe UI | Regular, 7 a 8 pt; título de la tarjeta en negrita | `#213455` |
| Código | Consolas | Regular | — |

## 3. Color

| Uso | Fondo | Borde |
|---|---|---|
| Tarjeta neutra (Objetivo, Estado) | Blanco | Gris claro `#DFE5EA`, esquinas redondeadas |
| Límite del sistema (C4) | `#F7FAFF` | Azul `#6C84A5` |
| Sistema o contenedor propio | `#E8F1FF` | Azul `#1F5FBF` |
| Persona o actor | `#FFF4D6` (amarillo) | Ocre `#C9A040` |
| Sistema externo o almacenamiento | `#E7F5ED` (verde) | Verde `#3D8B5A` |
| Elemento futuro o fuera de alcance | Blanco | Gris, **línea discontinua** |
| Aviso positivo («Primera demo: …») | `#E7F5ED` | Barra verde a la izquierda |
| Aviso de alcance («Fuera del alcance…») | `#FFF4D6` | Barra ocre a la izquierda |

El significado de cada color es el mismo en todos los diagramas del documento.

## 4. Diagramas

- Notación **C4**: nivel 1 (contexto) y nivel 2 (contenedores y despliegue).
- Caja: nombre en negrita y debajo una línea pequeña con su responsabilidad o tecnología («API NestJS · un backend modular»).
- Flechas finas grises con la etiqueta pequeña sobre la línea («SQL», «URLs firmadas», «REST / OpenAPI»).
- El límite del sistema es un rectángulo redondeado con su nombre en negrita arriba a la izquierda.
- Flujo de izquierda a derecha: actores a la izquierda, sistema al centro y externos a la derecha.

## 5. Puntos abiertos

1. ¿Las láminas llevan número de página y pie con el nombre del documento? El modelo no los tiene.
2. ¿Se usa este formato solo para arquitectura o también para presentar otros entregables?
