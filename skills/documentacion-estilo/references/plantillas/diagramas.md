# Plantilla: Diagramas de relevamiento

Diseño tomado de los diagramas que el usuario entregó como modelo (DEC-007): *Modelo de contexto y límites del sistema*, *Modelado de la organización (AS-IS)* y dos *Diagramas de secuencia AS-IS* del Instituto Serviliano Díaz. Se dibujan como SVG o HTML y se exportan a PNG para el documento.

## 1. Lámina

Cada diagrama es una lámina completa con este orden, de arriba hacia abajo:

1. **Título**: «ORGANIZACIÓN — TIPO DE DIAGRAMA» en mayúsculas sostenidas, negrita, unos 28 px, azul marino `#1F3A5F`. Ejemplo: «INSTITUTO SERVILIANO DÍAZ — DIAGRAMA DE SECUENCIA AS-IS».
2. **Subtítulo**: una línea en cursiva gris `#555555` que dice qué circuito o qué vista muestra, y la versión si la tiene («… (enfoque TGS) — v2»).
3. **Regla**: línea horizontal azul marino de 2 px en todo el ancho.
4. **Diagrama**.
5. **Recuadro de límite** (solo en contexto): fondo gris claro con borde gris, «**LÍMITE DEL SISTEMA:**» en azul marino y negrita, y el texto que dice qué queda fuera.
6. **Nota**: «Nota: relevado en entrevista a … (fecha). …» en cursiva gris, a la izquierda.
7. **Leyenda**: una fila con cada tipo de línea o marca y su significado («— Dependencia», «- - - Colaboración», «▬ Integra el Equipo de Gestión»).

Fuente: Arial / Helvetica en todo el diagrama.

## 2. Cajas

| Elemento | Formato |
|---|---|
| Entidad, área o participante | Fondo gris muy claro `#F2F4F7`, borde azul marino `#1F3A5F` de 2 px, esquinas apenas redondeadas |
| Contenido de la caja | Antetítulo opcional en mayúsculas pequeñas («ENTIDAD DE ENTORNO 1»); nombre en negrita; responsable en regular; funciones en cursiva gris, entre corchetes en el organigrama («[Gestión General, Pedagógica y Operativa]») |
| Sistema propio (contexto) | Borde azul marino **discontinuo**, nombre en mayúsculas y negrita, subtítulo en cursiva entre paréntesis |
| Bloque interno | Caja gris con títulos en mayúsculas y negrita («ESTRUCTURA OPERATIVA INTERNA») y viñetas, separados por una línea gris |
| Insignia | Pastilla azul marino con texto blanco en negrita, sobre el borde superior derecho de la caja («Equipo de Gestión») |

## 3. Líneas

- Flujo de información: línea continua gris oscura `#333333` con punta llena, y la etiqueta encima («Inscripción / Documentación»).
- En contexto, cada relación lleva dos flechas paralelas: entrada y salida, cada una con su etiqueta.
- Organigrama: conectores ortogonales sin punta para la dependencia; línea discontinua con dos puntas y etiquetas en cursiva para la colaboración.

## 4. Diagrama de secuencia

- Participantes arriba, en cajas con el nombre en negrita y el rol o sistema entre paréntesis en gris («Secretaría Docente (Aarón / Gaspar)»). Línea de vida gris discontinua.
- **Fases**: recuadros grises finos que agrupan los mensajes de una etapa, con una pestaña gris claro arriba a la izquierda y el título numerado en azul marino y negrita («1. Preinscripción a 1° Año (fines de octubre…)»).
- **Fragmentos** `alt`, `loop` y `opt`: marco negro con la pestaña del operador en negrita y la guarda en negrita entre corchetes («[Mientras falte documentación]»). En `alt`, las alternativas se separan con una línea discontinua.
- Mensajes numerados de forma correlativa en todo el diagrama («7: Registra matrícula…»): línea continua para la llamada y discontinua para la respuesta. Los mensajes a sí mismo se dibujan con un lazo.

## 5. Puntos abiertos

1. El diagrama de casos de uso que acompañó a estos (estilo Mermaid, con etiquetas cortadas como «Crear Unidades /») no sigue este diseño. ¿Se redibuja con este estilo o se descarta como modelo?
2. Los diagramas nombran a personas («Aarón Pereira»), pero el Trabajo de campo cita a las personas por su rol. ¿Cuál regla vale para los diagramas?

## 6. Variante: página web de diagramas (Mermaid)

Tomada de *mermaid.html* («Diagramas de Arquitectura — Pasarela de Pagos»), que el usuario entregó como modelo. Se usa cuando los diagramas se entregan como una página HTML y no dentro de un documento.

- Fondo de página `#F8FAFC`, texto `#1E293B`, fuente Inter. Ancho máximo de unos 1 024 px, centrado.
- Encabezado centrado: título en negrita de unos 30 px (`#1E293B`) y debajo una línea gris (`#64748B`) con el tema («Pasarela de Pagos (Patrones Chain of Responsibility & State)»).
- Una sección por diagrama: H2 numerado de unos 20 px, seminegrita, con una línea fina debajo («1. Flujo de Validación (Chain of Responsibility)»).
- El diagrama va en una tarjeta blanca con esquinas redondeadas de 12 px, sombra suave y 32 px de relleno; si es ancho, la tarjeta hace scroll horizontal.
- Debajo de la tarjeta, un párrafo de 14 px en gris `#475569` que explica qué muestra el diagrama y qué debe notar el lector.
- Diagramas en Mermaid (flowchart, stateDiagram-v2, classDiagram), con el tema de Mermaid por defecto y la fuente Inter.

Punto abierto: ¿para los diagramas de los entregables se usa el estilo de lámina (secciones 1 a 5) y Mermaid solo para la documentación web?
