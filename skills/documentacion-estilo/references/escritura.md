# Normas de escritura

Aplican a todo el documento. La sección 4 agrega reglas según el tipo de documento.

## 1. Principios

1. **Claridad**: el lector entiende la idea en la primera lectura.
2. **Precisión**: cada afirmación se puede verificar, cuantificar o citar.
3. **Concisión**: cada palabra aporta algo. Lo que no aporta, se elimina.
4. **Consistencia**: el mismo concepto tiene el mismo nombre en todo el documento.

## 2. Oraciones y párrafos

- **Voz activa** por defecto: "El sistema envía el correo", no "El correo es enviado por el sistema". La voz pasiva solo se usa cuando el agente no importa o no se conoce.
- **Longitud**: hasta 25 palabras por oración. Promedio de 15 a 20.
- **Sujeto, verbo, complemento**: el verbo principal aparece pronto. Evita dejar la idea principal al final de una oración larga.
- **Una idea por párrafo**. La primera oración de cada párrafo anuncia la idea.
- **Evita encadenar "que"**: si una oración tiene tres o más "que", divídela.
- **Gerundios**: evita el gerundio de posterioridad ("Se guardó el archivo, mostrando un mensaje"). Usa dos oraciones o un conector: "Se guardó el archivo y se mostró un mensaje".

### Expresiones a evitar

| Evitar | Usar |
|---|---|
| a nivel de | en, para, respecto de (según el caso) |
| en base a | con base en, a partir de |
| previamente a | antes de |
| dar solución a | resolver |
| hacer uso de | usar |
| en el día de la fecha | hoy |
| feedback | retroalimentación, comentarios |
| setup | configuración, instalación |
| click | clic (sustantivo), hacer clic (verbo) |
| performance | rendimiento |
| reportar un bug | informar un error |

Si la interfaz usa un término en inglés (por ejemplo, "Login"), escribe el término tal cual aparece en la interfaz, en negrita, y no lo traduzcas.

## 3. Ortografía, números y ortotipografía

- **Ortografía**: normas de la RAE. El español neutro es el predeterminado. Si el documento es rioplatense, el voseo se aplica de forma coherente en todo el texto (vos tenés, sos, podés).
- **Números decimales**: coma. Ejemplo: `3,5 %`. Los decimales se separan con coma, nunca con punto.
- **Miles**: espacio fino. Ejemplo: `12 500 usuarios`. Para cifras de cuatro dígitos, la separación es opcional, pero debe ser la misma en todo el documento.
- **Porcentajes**: un espacio antes del signo: `15 %`.
- **Unidades**: sistema internacional. Un espacio entre el número y la unidad: `10 km`, `250 ms`, `2 GB`. Los símbolos no llevan punto ni plural: `5 kg`, no `5 kgs.`.
- **Fechas**: en texto, "12 de marzo de 2026". En tablas y encabezados, `12/03/2026` (dd/mm/aaaa).
- **Horas**: formato de 24 horas, `14:30`.
- **Comillas**: elige un solo estilo. Recomendado: comillas dobles en español (“así”) para citas breves; comillas angulares (« ») si la institución las pide. Los términos dentro de texto se escriben en cursiva, no entre comillas, salvo que sea una cita.
- **Signos de apertura**: siempre usa ¿ y ¡.
- **Espacios**: un espacio después de coma, punto, punto y coma y dos puntos. Ningún espacio antes de los signos de cierre.
- **Mayúsculas**: se escriben en mayúscula solo los nombres propios, la primera palabra de una oración y las siglas. Los cargos y disciplinas van en minúscula: "el jefe de proyecto", "la ingeniería de software".
- **Siglas**: la primera vez que aparecen se escriben desarrolladas, seguidas de la sigla entre paréntesis: "Interfaz de programación de aplicaciones (API)". Después se usa solo la sigla. Si la sigla es de uso general (URL, PDF), no hace falta desarrollarla.

## 4. Reglas por tipo de documento

### Manual de usuario

- **Imperativo con el tratamiento definido**. Con usted: "Seleccione el archivo", "Haga clic en Guardar". Con tú: "Selecciona el archivo".
- **Títulos de tareas en infinitivo**: "Exportar un informe", "Cambiar la contraseña".
- **Una acción por paso**. Si el paso tiene dos acciones, divídelo.
- **Describe la pantalla antes de la acción** cuando el lector la ve por primera vez: "En el panel izquierdo, aparece la lista de proyectos."
- **Avisos antes del paso** al que se refieren.
- **Sin jerga**. Si un término técnico es necesario, defínelo en el glosario y en su primera aparición.
- **Nombres de la interfaz** en negrita y con la misma capitalización que en la pantalla.

### Tesis e informes de investigación

- **Tercera persona o impersonal**. "Se propone un modelo", "Este trabajo propone". Evita "yo" y "nosotros" salvo que el reglamento lo permita.
- **Tiempos verbales**: pasado para métodos y resultados ("Se aplicó la encuesta"). Presente para marco teórico, discusión y conclusiones ("Los resultados indican").
- **Cautela**: usa verbos moderados cuando la evidencia no es concluyente: "los resultados sugieren", "parece indicar". Evita "prueba que" o "demuestra" salvo en sentido matemático.
- **Citas**: toda idea ajena lleva cita en el estilo definido. Verifica que cada cita esté en la lista de referencias y viceversa.
- **Conectores** de razonamiento: "por lo tanto", "en cambio", "no obstante", "en consecuencia". Un conector por párrafo como máximo, para no saturar el texto.
- **Objetivos**: el general empieza con un verbo en infinitivo ("Desarrollar un prototipo..."). Los específicos también, y cada uno corresponde a un capítulo o resultado.

### Especificación de requisitos

- **Forma del enunciado**: "El sistema deberá [acción] [condición]." o "[Actor] deberá poder [acción]." Usa "deberá" para requisitos obligatorios y "debería" para deseables.
- **Un requisito por enunciado**. Si el enunciado tiene "y" para unir dos acciones, sepáralo en dos requisitos.
- **ID único** y estable: `RF-001` (funcional), `RNF-001` (no funcional), `RI-001` (interfaz).
- **Verificable**: cada requisito debe poder probarse. Evita términos ambiguos: "rápido", "adecuado", "amigable", "etc.", "entre otros", "según corresponda".
- **Cuantifica los atributos de calidad**: "La página de inicio carga en menos de 2 s en el percentil 95 con 500 usuarios concurrentes", no "La página carga rápido".
- **Trazabilidad**: cada requisito apunta a su origen (stakeholder, caso de uso) y a su caso de prueba.

### Historias de usuario

- **Formato**: "Como [rol], quiero [acción], para [beneficio]."
- **Criterios de aceptación** en formato Dado / Cuando / Entonces:

```
Dado que el usuario tiene una sesión iniciada
Cuando selecciona "Exportar"
Entonces se descarga un archivo PDF con los datos visibles en pantalla
```

- **Un criterio por comportamiento**. Incluye al menos un caso de error.

### Diagramas y pies

- **Etiquetas cortas**: hasta cuatro palabras.
- **El pie de figura explica qué mira el lector**, no repite el título: "La flecha punteada indica dependencia en tiempo de ejecución."

### Documentos de proyecto (visión, informes, planes)

- **Empieza por la conclusión**: resumen ejecutivo de media página con decisión, riesgo principal y próximo paso.
- **Cifras con fuente**: cada dato tiene su origen o se marca como estimación.
- **Decisiones con motivo**: cada decisión de arquitectura o de alcance indica por qué se tomó y qué alternativa se descartó.

## 4 bis. Propósito, ámbito y lector

Además del tipo de documento, el prompt clasifica el texto en tres ejes independientes: **propósito** (qué busca el texto), **ámbito** (en qué campo circula) y **lector** (quién lo lee). Cada valor suma sus reglas a la sección 5 del prompt, después de las del tipo. El configurador emite exactamente estos textos. En el frontmatter, los valores se escriben como identificadores, en minúscula y sin tildes (`proposito`, `ambito`, `lector`).

Los prompts anteriores traen `audiencia` en lugar de `lector` y siguen siendo válidos. Al importar una configuración anterior en el configurador, `audiencia` se traduce así: `técnica` y `académica` → `experto`; `no técnica` → `publico_general`; `mixta` → `mixto`.

Esa configuración tampoco trae `proposito` ni `ambito`, así que se completan según el tipo. Si `audiencia` es `académica`, el ámbito pasa a ser `academico`. Esta tabla solo se usa en la migración: cambiar el tipo en el configurador no modifica los ejes.

| Tipo | Propósito | Ámbito |
|---|---|---|
| Manual | `instructivo` | `tecnico` |
| Tesis | `argumentativo` | `academico` |
| Especificación y arquitectura | `expositivo` | `tecnico` |
| Informe | `analitico` | `tecnico` |
| Diagrama y otro | `expositivo` | `tecnico` |

### Propósito

- **Expositivo** (`expositivo`): Define cada concepto antes de usarlo y ordena el contenido de lo general a lo particular.
- **Analítico** (`analitico`): Separa los datos de su interpretación y declara los criterios del análisis antes de aplicarlos.
- **Argumentativo** (`argumentativo`): Enuncia la tesis al comienzo, sostiene cada afirmación con evidencia o cita y responde la objeción principal.
- **Instructivo** (`instructivo`): Una acción por paso, en el orden de ejecución, con el resultado esperado de cada paso.
- **Narrativo** (`narrativo`): Sigue el orden cronológico y marca las fechas o etapas de cada hecho.
- **Mixto** (`mixto`): Declara el propósito de cada capítulo en su primer párrafo.

### Ámbito

- **Científico** (`cientifico`): Precisión terminológica (un término, un solo significado), cautela epistémica (distingue lo demostrado de lo probable) y verificabilidad (cada afirmación remite a su fuente o a su método).
- **Técnico** (`tecnico`): Nombres exactos del sistema y de sus componentes, con su versión, y cada magnitud con su unidad.
- **Académico** (`academico`): Sigue las normas de la institución y cita en el estilo elegido.
- **Institucional** (`institucional`): Registro formal e impersonal; cada obligación remite a la normativa que la establece.
- **Profesional** (`profesional`): Orientado a decisiones: las conclusiones y las acciones van primero y el detalle después.

### Lector

- **Experto** (`experto`): Usa la terminología del campo sin definirla.
- **Especialista de otra área** (`especialista`): Define los términos del campo en su primera aparición y relaciona cada concepto con su uso.
- **Público general** (`publico_general`): Sin jerga, un ejemplo concreto por cada concepto abstracto y oraciones cortas.
- **Mixto** (`mixto`): Abre cada capítulo con un resumen sin jerga y deja el detalle técnico para después.

### Divulgación

No es una opción de ningún eje. Se activa sola cuando se dan tres condiciones a la vez: el ámbito es científico o técnico, el lector es público general y el propósito es expositivo o narrativo. Así, un manual instructivo no la recibe. Suma estas reglas:

- Parte de una pregunta o de una situación cotidiana.
- Usa analogías y márcalas como tales («es como…»).
- No simplifiques hasta volver falso un enunciado.

## 5. Inclusividad

- Usa términos neutros cuando el sentido lo permita: "personas usuarias", "equipo de desarrollo", "la población estudiantil".
- No uses el masculino genérico cuando haya alternativa clara ("el usuario" puede ser "la persona usuaria" o "quien usa el sistema").
- Elige una estrategia y aplícala igual en todo el documento. No mezcles "usuarios/as", "usuarios" y "personas usuarias".
- Evita expresiones que asocien discapacidad con limitación ("sufre de", "padece"). Usa "tiene" o "vive con".

## 6. Ejemplos: mal y bien

| Mal | Bien | Regla |
|---|---|---|
| Se procede a la apertura del menú de configuración. | Abra el menú **Configuración**. | Voz activa, verbo directo, tratamiento usted |
| El sistema debe ser rápido y amigable. | El sistema debe responder cada solicitud en menos de 2 s. | Verificable y cuantificado |
| Se realizó un análisis en base a los datos previamente recolectados. | Se analizaron los datos recolectados en la encuesta. | Sin expresiones vagas, pasado simple |
| El 3.5% de los encuestados... | El 3,5 % de los encuestados... | Coma decimal, espacio antes del % |
| Haga click en el botón setup. | Haga clic en **Configuración**. | Sin anglicismos, nombre exacto de la interfaz |
| Este trabajo demuestra que la solución es la mejor. | Los resultados sugieren que la solución mejora el tiempo de respuesta en un 20 %. | Cautela y cifra con respaldo |
| Ver tabla abajo. | En la Tabla 2 se comparan los tiempos de respuesta. | Referencia explícita a la numeración |

## 7. Revisión final de redacción

Recorre el texto una vez con estas preguntas:

1. ¿Cada oración tiene un sujeto claro y un verbo activo, salvo que el agente sea irrelevante?
2. ¿Hay términos distintos para el mismo concepto? Unifícalos.
3. ¿Cada sigla está desarrollada en su primera aparición?
4. ¿Los números siguen la convención del documento?
5. ¿Hay afirmaciones sin cifra, cita o fuente? Respáldalas o márcalas `[PENDIENTE]`.
6. ¿El tratamiento (usted, tú, vos, impersonal) es el mismo en todo el texto?
