# Estilo visual

Define cómo se ve cada elemento. Los valores son los predeterminados del skill; si el reglamento o la marca del cliente fija otros, reemplázalos en todo el documento sin mezclar. Si el prompt declara una `plantilla` (ver `plantillas/README.md`), esa plantilla manda sobre esta referencia.

## 1. Página y grilla

| Aspecto | Impreso (A4) | Digital |
|---|---|---|
| Tamaño | A4 (21 × 29,7 cm) o carta según el medio | Ancho de lectura de 680 a 760 px |
| Márgenes | 2,5 cm en todos los lados (ajustar al reglamento si lo exige) | 16 px de margen lateral en móvil |
| Columnas | Una sola columna para el texto | Una sola columna; las tablas pueden hacer scroll horizontal |
| Largo de línea | 60 a 75 caracteres | 60 a 75 caracteres |
| Espaciado | Múltiplos de 4 pt: 4, 8, 12, 16, 24, 32 | Múltiplos de 4 px: 4, 8, 12, 16, 24, 32 |

Cada capítulo empieza en página nueva en el medio impreso. En digital, cada H1 empieza una sección con separación de 48 px antes.

## 2. Jerarquía de títulos

| Nivel | Uso | Formato de ejemplo | Tamaño (digital / impreso) |
|---|---|---|---|
| H1 | Capítulo | `1 Introducción` | 30 px / 18 pt |
| H2 | Sección | `1.1 Alcance` | 24 px / 15 pt |
| H3 | Subsección | `1.1.1 Limitaciones` | 19 px / 13 pt |
| H4 | Bloque dentro de una subsección (solo si es necesario) | `Requisitos de entrada` | 16 px en negrita / 11 pt en negrita |

Reglas:

- Numeración decimal en H1 a H3. Las partes no numeradas (Resumen, Referencias, Anexos, Glosario) llevan H1 sin número.
- En una entrega `multiarchivo`, el H1 de cada punto lleva el número de su archivo: `04 - Diseño.md` empieza con `# 4 Diseño`, también si es una parte de `sin_numerar`. Con `numeracion_textual: ninguna`, va sin número (DEC-008).
- Máximo cuatro niveles. Si necesitas un quinto, reorganiza el contenido.
- Títulos cortos: hasta ocho palabras, sin punto final, en mayúscula solo la primera letra.
- Un título nunca va solo al final de una página: se mantiene con el párrafo siguiente.

## 3. Componentes

### Párrafo

Una idea por párrafo, de 3 a 6 líneas. Sin sangría en documentos digitales. En tesis e impresos académicos, sangría de primera línea de 1,25 cm (salvo que el reglamento indique otra cosa).

### Listas

- **Viñetas**: para elementos sin orden. Máximo siete ítems; si hay más, agrúpalos.
- **Numeradas**: para pasos o secuencias. Usa números arábigos seguidos de punto (`1.`).
- **Paralelismo**: todos los ítems de una lista empiezan con la misma forma gramatical (todos verbos en infinitivo, o todos sustantivos).

### Pasos de manual

Cada paso contiene una sola acción. El resultado esperado va al final del paso, precedido por una flecha:

```
1. Se selecciona **Archivo** > **Nuevo proyecto**.
   → Se abre el asistente de creación.
2. Se escribe un nombre en el campo **Nombre del proyecto**.
```

Si un paso puede causar pérdida de datos o daño, usa un aviso de "Advertencia" antes del paso, no después.

### Tablas

- Título arriba, con número: `Tabla 1. Requisitos funcionales del módulo de ventas`.
- Fuente debajo, en texto secundario: `Fuente: elaboración propia.`
- Encabezado en negrita, con fondo `superficie`. Sin bordes verticales. Filas separadas por línea fina de `borde`.
- Las unidades van en el encabezado: `Duración (s)`, no en cada celda.
- Texto alineado a la izquierda. Números alineados a la derecha, con el mismo número de decimales.
- Máximo siete columnas en impreso. Si hay más, divide la tabla.

### Tablas estadísticas, académicas y técnicas

El configurador ofrece diecisiete tipos de tabla. Trece son académicos (de datos, frecuencia, contingencia, correlación, regresión, ANOVA, características demográficas, comparación, descriptivos, fiabilidad, pruebas de hipótesis, operacionalización y estado del arte) y cuatro, técnicos (matriz de trazabilidad, caso de uso, riesgos y endpoints de API). Los elegidos van en el campo `tablas` del prompt, cada uno con su regla. Las estadísticas siguen APA 7 con el separador decimal del prompt:

- Símbolos estadísticos en cursiva: *n*, *M*, *DE*, *p*, *t*, *F*, *r*.
- Sin cero inicial en los valores que no pueden superar 1 (*p*, *r*, β, α, ω, η²): `,031`.
- *p* exacto con tres decimales; `< ,001` para los menores.
- Asteriscos de significación solo con su nota debajo: `*p < ,05. **p < ,01.`
- La tabla cierra con `*Nota.*`, el *N* y las abreviaturas usadas.

`verificar_doc.py` revisa el cero inicial, el separador decimal y la nota de los asteriscos cuando `tablas` incluye algún tipo estadístico.

Las tablas técnicas siguen estas reglas, que el verificador revisa cuando el tipo está en `tablas`:

- **Matriz de trazabilidad**: una fila por requisito, con ID, Requisito, Origen, Elemento de diseño, Caso de prueba y Estado. (Ningún requisito sin caso de prueba; si falta, `[PENDIENTE: caso de prueba]`.)
- **Caso de uso**: ficha de dos columnas con ID `CU-NN`, Nombre, Actor principal, Precondiciones, Flujo principal numerado, Flujos alternativos (`2a.`) y Postcondiciones.
- **Riesgos**: probabilidad e impacto de 1 a 5; Nivel = probabilidad × impacto con su categoría (1 a 4 bajo, 5 a 9 medio, 10 a 16 alto, 20 a 25 crítico); de mayor a menor nivel. (El producto, la categoría y el orden.)
- **Endpoints de API**: Método, Ruta, Descripción y Respuestas; método en mayúsculas y ruta en código con parámetros entre llaves (`/api/cursos/{id}`). (Que el método sea GET, POST, PUT, PATCH o DELETE.)

### Figuras (imágenes, diagramas, capturas)

- Título y número debajo: `Figura 3. Pantalla de inicio de sesión`. Fuente debajo, igual que en tablas.
- Impreso: resolución mínima de 300 ppp. Digital: texto alternativo obligatorio.
- Capturas de pantalla con borde de 1 px en color `borde`. Si hay elementos a señalar, usa marcadores numerados (círculos con número) y explícalos en el texto o en una lista debajo.
- Cada figura se menciona en el texto antes de aparecer: "En la Figura 3 se muestra...".

### Código

- Bloque con fuente monoespaciada, fondo `superficie` y nombre del lenguaje en la esquina superior derecha.
- Máximo 40 líneas por bloque. Si hay más, divídelo y explica cada parte.
- Comentarios del código en el idioma del documento.
- Código en línea: fuente monoespaciada dentro de la oración, sin cambiar el tamaño.

### Avisos

Hay cuatro tipos. Todos tienen la misma forma: barra vertical de color a la izquierda, icono, etiqueta en negrita y texto de hasta tres líneas.

| Tipo | Etiqueta | Uso | Icono | Color de texto / fondo |
|---|---|---|---|---|
| Nota | **Nota** | Información complementaria | ℹ | `info` / `info-fondo` |
| Consejo | **Consejo** | Atajo o buena práctica | ✔ | `exito` / `exito-fondo` |
| Advertencia | **Advertencia** | Algo puede salir mal si no se tiene en cuenta | ⚠ | `advertencia` / `advertencia-fondo` |
| Peligro | **Peligro** | Pérdida de datos, daño o riesgo de seguridad | ✖ | `peligro` / `peligro-fondo` |

En Markdown, el aviso se escribe como blockquote con la etiqueta en negrita: `> **Advertencia.** Esta acción elimina el proyecto y no se puede deshacer.`

### Ecuaciones

Centradas, con número entre paréntesis a la derecha: `(1)`. Cada símbolo se define en una lista debajo de la ecuación. Las ecuaciones se citan en el texto como "la ecuación (1)".

### Glosario

Término en negrita, seguido de dos puntos y una definición de una sola oración. Orden alfabético. Las siglas aparecen en el glosario y, además, desarrolladas en la primera aparición del texto.

### Elementos académicos

Se activan desde los componentes del configurador y quedan en `componentes` del prompt. `verificar_doc.py` revisa lo que puede comprobar un script, que aparece entre paréntesis.

- **Resumen y palabras clave** (`palabras_clave`): resumen de un solo párrafo de 150 a 250 palabras; debajo, `**Palabras clave:**` con 3 a 5 términos en minúscula separados por punto y coma. El Abstract lleva `**Keywords:**` con los mismos términos. (Que exista la línea y que tenga de 3 a 5 términos separados por «;».)
- **Notas al pie** (`notas_pie`): solo para aclaraciones, nunca para citas. Numeración continua; en Markdown, `[^1]` y `[^1]: texto` al final del capítulo. (Que cada llamada tenga su definición, en cualquier documento.)
- **Citas en bloque** (`cita_bloque`): 40 palabras o más, en párrafo aparte con sangría izquierda de 1,27 cm, sin comillas y con la cita bibliográfica después del punto final. En Markdown, `>` sin rótulo de aviso. (Bloques de menos de 40 palabras y citas de 40 o más entre comillas.)
- **Hipótesis** (`hipotesis`): `**H1.**`, `**H2.**`… con numeración continua; la nula, `**H0.**`, debajo de su alternativa. (La numeración.)
- **Índices de tablas y figuras** (`indices`): después del índice general, con número y título exacto de cada leyenda; página en impreso y enlace en digital. (Que existan si el documento tiene tablas o figuras.)
- **Anexos** (`anexos`): `## Anexo A. Título`, letras en orden y mencionados en el texto antes de aparecer; sus tablas y figuras siguen la numeración continua. (El orden de las letras y la mención.)

### Control de versiones

Primera página después de la portada. Tabla con columnas: Versión, Fecha, Autor, Descripción del cambio. Las fechas en formato dd/mm/aaaa.

### Entregas en varios archivos

Reglas para `entrega: multiarchivo`. Con `entrega: unico`, o sin el campo, el documento puede estar partido en varios archivos, pero es un solo documento lógico, con numeración continua (DEC-008).

- **Archivos** (DEC-008): un archivo índice (`entrega_indice`, por defecto `README.md`) y un archivo por punto (`entrega_patron`, por defecto `NN - Nombre.md`), en el primer nivel de la carpeta. El índice enlaza cada punto, en el orden de los archivos.
- **Tablas y figuras** (DEC-009): se numeran por archivo, con el número del archivo como prefijo: en `04 - Diseño.md` van `Tabla 4.1`, `Tabla 4.2` y `Figura 4.1`. Las del índice van sin prefijo y con numeración propia: `Tabla 1`. Con leyendas APA 7 se mantiene su formato y se admite ese número, como excepción explícita a APA 7.
- **Citas** (DEC-009): desde otro archivo, una tabla o figura se cita con su número completo. La mención que la presenta va en su propio archivo.
- **Control de versiones** (DEC-010): hay una sola tabla, en el índice. Sus filas se proponen desde el `git log` de la carpeta y el usuario confirma la versión y la descripción. Sin repositorio, o si la carpeta no tiene historial, quedan como `[PENDIENTE: versión, fecha, autor y descripción]`.

`verificar_doc.py` revisa los archivos, los enlaces del índice, los números, las citas, las menciones y que haya una sola tabla de control de versiones, en el índice. No revisa las filas de esa tabla, el `git log` ni la confirmación del usuario.

### Encabezado, pie y portada

- Encabezado: título corto del documento (impreso, páginas impares a la derecha con el capítulo activo).
- Pie: número de página centrado o a la derecha. Sin número en portada.
- Portada: título, subtítulo, autor, institución o empresa, versión, fecha. Sin decoración innecesaria.

## 4. Tipografía

### Familias

| Rol | Digital | Impreso académico | Monoespaciada |
|---|---|---|---|
| Títulos | Calibri (DEC-003) | Calibri, en negrita (DEC-003) | Consolas (DEC-003) |
| Cuerpo | Calibri (DEC-003) | Calibri (DEC-003) | Consolas (DEC-003) |

**Catálogo formal (DEC-003)**: se admiten fuentes que respeten la integridad formal, académica y científica del documento. Sin serifa (Sans Serif): Calibri, Arial, Helvetica, Source Sans 3. Con serifa: Times New Roman, Cambria, Georgia, Palatino Linotype, Garamond, STIX Two Text.

Usa como máximo dos familias por documento. Si el reglamento exige una fuente específica, esa manda sobre la tabla.

### Escala y ritmo

| Elemento | Digital | Impreso |
|---|---|---|
| Cuerpo | 16 px, interlineado 1,5 | 11 a 12 pt, interlineado 1,15 (manuales) o 1,5 (tesis) |
| Código | 0,9 em, interlineado 1,4 | 9 a 10 pt |
| Tablas y figuras (texto) | 14 px | 10 pt |
| Fuente y notas | 13 px | 9 pt |

### Pesos y estilos

- **Regular (400)** para el cuerpo. **Semibold (600)** o negrita para títulos. **Negrita** para la primera aparición de un término clave y para nombres de la interfaz.
- *Cursiva* para títulos de obras, palabras extranjeras y variables matemáticas.
- No subrayar: el subrayado se confunde con enlaces.
- No escribir en mayúsculas sostenidas en el cuerpo. Las mayúsculas se reservan para siglas y para la portada.

### Alineación

Texto alineado a la izquierda (ragged right) por defecto. En tesis impresa se permite justificar si el reglamento lo pide; en ese caso revisa que no queden espacios grandes entre palabras.

## 5. Color

### Paleta de tokens

Define estos tokens una sola vez y úsalos en todo el documento. Todos los pares de texto y fondo cumplen contraste WCAG AA (4,5:1 mínimo).

| Token | Valor | Uso | Contraste sobre blanco |
|---|---|---|---|
| `texto` | `#1F2328` | Cuerpo y títulos | 15,8 : 1 |
| `texto-secundario` | `#57606A` | Fuentes, notas, pies | 6,4 : 1 |
| `primario` | `#2E74B5` (DEC-003) | Títulos H1 y H2, enlaces, elementos de diagrama | 4,9 : 1 |
| `borde` | `#D0D7DE` | Líneas de tablas, bordes de capturas | Decorativo |
| `superficie` | `#F6F8FA` | Encabezados de tabla, fondo de código | Texto sobre superficie: 14,8 : 1 |
| `info` / `info-fondo` | `#0969DA` / `#DDF4FF` | Aviso Nota | 4,6 : 1 sobre su fondo |
| `exito` / `exito-fondo` | `#1A7F37` / `#DAFBE1` | Aviso Consejo | 4,6 : 1 sobre su fondo |
| `advertencia` / `advertencia-fondo` | `#9A6700` / `#FFF8C5` | Aviso Advertencia | 4,5 : 1 sobre su fondo |
| `peligro` / `peligro-fondo` | `#CF222E` / `#FFEBE9` | Aviso Peligro | 4,7 : 1 sobre su fondo |

Versión en CSS, para documentos digitales:

```css
:root {
  --texto: #1F2328;
  --texto-secundario: #57606A;
  --primario: #2E74B5;
  --borde: #D0D7DE;
  --superficie: #F6F8FA;
  --info: #0969DA;      --info-fondo: #DDF4FF;
  --exito: #1A7F37;     --exito-fondo: #DAFBE1;
  --advertencia: #9A6700; --advertencia-fondo: #FFF8C5;
  --peligro: #CF222E;   --peligro-fondo: #FFEBE9;
  --fondo: #FFFFFF;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --texto: #E6EDF3; --texto-secundario: #9198A1; --primario: #79B8FF;
    --borde: #3D444D; --superficie: #151B23; --fondo: #0D1117;
  }
}
```

Para modo oscuro, verifica el contraste de cada aviso de nuevo: los valores anteriores están calibrados para fondo claro.

### Reglas de uso

- El color nunca es el único portador de significado. Un aviso se distingue por su etiqueta e icono, no solo por su color.
- Usa un solo color de acento por página. En impreso, el documento debe leerse bien en escala de grises.
- El color `primario` se usa para títulos y enlaces, no para decorar párrafos.

## 6. Diagramas

- **Notación estándar** (ver `metodologias.md`, sección "Notaciones de diagramas"). No inventes símbolos.
- **Título, número, leyenda y fuente.** La leyenda explica cada color, forma o línea que aparece en el diagrama.
- **Un diagrama, una pregunta.** Si un diagrama responde a más de una pregunta, divídelo.
- **Máximo 12 elementos por diagrama.** Si hay más, usa niveles de detalle (por ejemplo, C4: contexto, luego contenedores).
- **Dirección del flujo**: de izquierda a derecha o de arriba hacia abajo, nunca en ambos sentidos sin razón.
- **Etiquetas**: hasta cuatro palabras. Los nombres de elementos son sustantivos; las acciones en las flechas son verbos en infinitivo.
- **Colores**: como máximo seis colores categóricos, con el mismo significado en todos los diagramas del documento. Sistema propio en `primario`; sistemas externos en `texto-secundario`.
- **Texto legible**: el texto del diagrama tiene el mismo tamaño que el cuerpo o uno menor, nunca por debajo de 9 pt en impreso.
- **Formato**: SVG como preferido. PNG a 2× si el medio no admite SVG. Mantén la fuente sans-serif del documento.
