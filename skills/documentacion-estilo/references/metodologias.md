# Metodologías y estructuras de documento

Cada sección indica cuándo usar la metodología, sus artefactos y el esqueleto de capítulos. Los esqueletos son puntos de partida: adapta los nombres al proyecto, pero conserva el orden y la numeración.

## Selección rápida

| Situación | Metodología |
|---|---|
| Proyecto de software con fases formales, trazabilidad y control de riesgos | RUP |
| Mismo enfoque que RUP, con menos artefactos obligatorios | UP |
| Equipo ágil con entregas por iteraciones (sprints) | Scrum / ágil |
| Solo hay que especificar qué debe hacer el sistema | ISO/IEEE 29148 |
| Manual de uso, guía de producto o documentación técnica para usuarios | Diátaxis |
| Tesis, trabajo final o informe de investigación | Académica |
| Diagrama de arquitectura, proceso o datos | Ver "Notaciones de diagramas" |

## RUP y UP

**UP (Unified Process)** es un marco de proceso iterativo e incremental, dirigido por casos de uso, centrado en la arquitectura y guiado por riesgos. Lo describieron Jacobson, Booch y Rumbaugh. **RUP (Rational Unified Process)** es la implementación comercial de IBM que parte de UP y agrega más disciplinas y artefactos. Usa UP cuando quieras el marco sin la carga de RUP.

### Fases (comunes a UP y RUP)

| Fase | Pregunta que responde | Hito de cierre |
|---|---|---|
| Inicio (Inception) | ¿Vale la pena construirlo? | Objetivos del ciclo de vida |
| Elaboración (Elaboration) | ¿Es viable la arquitectura y se conocen los riesgos clave? | Arquitectura de referencia |
| Construcción (Construction) | ¿Está listo para usarse en un entorno controlado? | Capacidad operativa inicial |
| Transición (Transition) | ¿Se entrega a los usuarios reales? | Versión de producto |

### Disciplinas y artefactos

| Disciplina | Artefactos típicos |
|---|---|
| Modelado del negocio | Modelo de dominio, glosario de negocio |
| Requisitos | Documento de visión, modelo de casos de uso, especificación de requisitos suplementarios, glosario |
| Análisis y diseño | Documento de arquitectura de software (SAD), modelo de diseño, modelo de datos |
| Implementación | Modelo de implementación, guía de codificación |
| Pruebas | Plan de pruebas, casos de prueba, registro de defectos |
| Despliegue | Plan de despliegue, notas de la versión, manual de usuario |
| Gestión de configuración y cambios | Plan de gestión de configuración, solicitudes de cambio |
| Gestión de proyecto | Plan de desarrollo de software, lista de riesgos, plan de iteración, evaluación de iteración |
| Entorno | Guía del entorno de desarrollo, proceso adaptado |

### Esqueleto del documento de arquitectura (SAD) y del plan de desarrollo

```
Control de versiones
1. Introducción
   1.1 Propósito
   1.2 Alcance
   1.3 Definiciones, siglas y abreviaturas
   1.4 Referencias
2. Representación de la arquitectura
3. Objetivos y restricciones de la arquitectura
4. Vista de casos de uso
5. Vista lógica
   5.1 Paquetes o capas significativos
   5.2 Clases o componentes clave
6. Vista de procesos (concurrencia, comunicación)
7. Vista de despliegue
8. Vista de implementación
9. Vista de datos
10. Calidad (atributos de calidad y cómo se cumplen)
11. Riesgos técnicos y decisiones de arquitectura (ADR)
Glosario
```

## Scrum / ágil

Documentación mínima y viva. Lo que se documenta debe servir para tomar decisiones en la siguiente iteración.

| Artefacto | Contenido | Formato |
|---|---|---|
| Visión del producto | Problema, usuarios, propuesta de valor, métricas de éxito | 1 página |
| Product backlog | Lista priorizada de historias de usuario | Tabla o gestor de tareas |
| Historia de usuario | Qué se quiere y por qué | "Como [rol], quiero [acción], para [beneficio]." |
| Criterios de aceptación | Condiciones verificables de la historia | Dado / Cuando / Entonces |
| Definición de terminado (DoD) | Lista de condiciones que toda historia debe cumplir | Lista de verificación |
| Objetivo del sprint | Una frase con el resultado esperado | Párrafo corto |
| Notas de revisión del sprint | Qué se entregó, qué quedó pendiente, decisiones | Lista |

Esqueleto de un documento de iteración:

```
Control de versiones
1. Objetivo de la iteración
2. Historias comprometidas (tabla: ID, historia, criterios, estado)
3. Decisiones y cambios respecto a la iteración anterior
4. Riesgos y bloqueos
5. Resultados de revisión
```

## ISO/IEC/IEEE 29148 (especificación de requisitos)

Basada en la práctica de IEEE 830. Sirve para documentos de requisitos de software o de sistemas.

```
Control de versiones
1. Introducción
   1.1 Propósito
   1.2 Alcance
   1.3 Definiciones, siglas y abreviaturas
   1.4 Referencias
   1.5 Visión general del documento
2. Descripción general
   2.1 Perspectiva del producto (interfaces, restricciones de sistema)
   2.2 Funciones del producto
   2.3 Características de los usuarios
   2.4 Restricciones
   2.5 Supuestos y dependencias
3. Requisitos específicos
   3.1 Requisitos funcionales (RF-001, RF-002, ...)
   3.2 Requisitos no funcionales o atributos de calidad (RNF-001, ...)
   3.3 Interfaces externas (usuario, hardware, software, comunicación)
   3.4 Requisitos de datos
4. Trazabilidad (requisito, origen, caso de prueba)
Apéndices
```

Reglas de cada requisito: un ID único, un solo requisito por enunciado, verificable y sin ambigüedad. Ver `escritura.md`, sección "Especificaciones".

## Diátaxis (manuales y documentación técnica)

Organiza el contenido en cuatro tipos, según lo que necesita el lector en ese momento. No mezcles tipos en la misma página.

| Tipo | Lector busca | Orientación | Ejemplo |
|---|---|---|---|
| Tutorial | Aprender haciendo | Práctica guiada, paso a paso | "Crear tu primer proyecto" |
| Guía práctica (how-to) | Resolver una tarea concreta | Pasos para un objetivo | "Exportar un informe a PDF" |
| Referencia | Consultar datos exactos | Descripción neutra y completa | "Parámetros de la API de exportación" |
| Explicación | Entender el porqué | Contexto, decisiones, conceptos | "Cómo funciona el sistema de permisos" |

Esqueleto de un manual de usuario:

```
Control de versiones
Introducción (qué es, para quién, cómo usar este manual)
Primeros pasos (tutorial)
Tareas frecuentes (guías prácticas, una por tarea)
Referencia de la interfaz (pantallas, campos, menús)
Conceptos (explicación)
Solución de problemas (síntoma, causa, solución)
Preguntas frecuentes
Glosario
```

## Académica (tesis, trabajo final, informe de investigación)

Ajusta el orden y los nombres al reglamento de la institución. Este esquema es el más usado.

```
Preliminares
  Portada
  Agradecimientos y dedicatoria (opcional)
  Resumen (en español) y abstract (en inglés), con palabras clave
  Índice general
  Índice de figuras
  Índice de tablas
  Lista de siglas y abreviaturas
Cuerpo
  1. Introducción
     1.1 Planteamiento del problema
     1.2 Objetivos (general y específicos)
     1.3 Justificación
     1.4 Alcance y limitaciones
  2. Marco teórico o estado del arte
  3. Marco metodológico
     (enfoque, diseño, población o muestra, instrumentos, procedimiento)
  4. Desarrollo o resultados
  5. Discusión
  6. Conclusiones y trabajos futuros
Finales
  Referencias
  Anexos
  Apéndices
```

Convenciones: los objetivos específicos empiezan con verbos en infinitivo. Los resultados se presentan antes de interpretarlos en la discusión. Las conclusiones responden a los objetivos planteados en la introducción.

## Notaciones de diagramas

| Notación | Estándar | Qué muestra | Cuándo usarla |
|---|---|---|---|
| UML casos de uso | UML 2.5.1 | Actores, casos de uso y sus relaciones | Requisitos funcionales |
| UML clases | UML 2.5.1 | Clases, atributos, operaciones y relaciones | Diseño orientado a objetos |
| UML secuencia | UML 2.5.1 | Interacciones entre objetos en el tiempo | Flujos de llamadas, casos de uso complejos |
| UML actividad | UML 2.5.1 | Flujos de trabajo con decisiones y paralelismo | Procesos del negocio o algoritmos |
| UML componentes y despliegue | UML 2.5.1 | Partes del sistema y dónde se ejecutan | Arquitectura y despliegue |
| BPMN | BPMN 2.0 | Procesos de negocio con roles y eventos | Procesos organizacionales |
| Modelo entidad-relación | Notación de Chen o de pata de gallo | Entidades, atributos y cardinalidades | Modelo de datos |
| C4 | Modelo de Simon Brown | Contexto, contenedores, componentes y código | Arquitectura en varios niveles de detalle |

Para documentos que se versionan junto al código, usa un lenguaje de texto (Mermaid o PlantUML) como fuente y exporta a SVG para el documento final.
