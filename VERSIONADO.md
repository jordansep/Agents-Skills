# Versionado de los agentes

Cada agente del repositorio tiene su propia versión, independiente de los demás. Un agente es un conjunto de skills que trabajan juntos; por ejemplo, el agente `documentacion` agrupa `documentacion-estilo` y `documentacion-generar`.

## Dónde está la versión

| Archivo | Contenido |
|---|---|
| `agentes/<agente>/agente.json` | Nombre, versión, descripción y carpetas de sus skills. |
| `agentes/<agente>/CHANGELOG.md` | Qué cambió en cada versión, de la más nueva a la más vieja. |
| Etiqueta `<agente>/vX.Y.Z` | Commit de `main` que corresponde a esa versión, con su release en GitHub. |

Los skills siguen en `skills/`. Mover carpetas rompería las instalaciones existentes, así que la versión vive aparte.

## Qué número subir

Las versiones siguen [SemVer](https://semver.org/lang/es/): `MAYOR.MENOR.PARCHE`.

| Nivel | Cuándo | Ejemplos |
|---|---|---|
| **MAYOR** | Un cambio obliga a quien usa el agente a cambiar algo de su lado. | Se renombra o elimina un skill; un prompt de estilo anterior deja de servir; cambia una ruta que rompe la instalación. |
| **MENOR** | Nueva capacidad o cambio de comportamiento, compatible con lo anterior. | Nueva metodología o componente; nueva opción del configurador; una regla de estilo confirmada que vale para todo el agente (DEC confirmada). |
| **PARCHE** | Corrección sin cambio de comportamiento esperado. | Error del configurador o del verificador; texto o documentación; preguntas pendientes registradas en la memoria; decisiones que valen para un solo documento. |

Mientras un agente esté en `0.x`, un cambio incompatible sube MENOR en lugar de MAYOR, como permite SemVer. Pasar a `1.0.0` es una decisión explícita de quien mantiene el agente: significa que su uso se considera estable.

Cualquier cambio dentro de las carpetas de skills de un agente, incluida su memoria, requiere subir la versión. Los cambios que solo tocan `agentes/<agente>/` (por ejemplo, corregir el changelog) no lo requieren.

## Flujo

1. Haz los cambios en una rama.
2. Sube la versión y describe el cambio:

   ```bash
   python3 scripts/versionado.py subir documentacion minor --agregado "Componente de línea de tiempo"
   ```

   Esto actualiza `agente.json` y agrega la entrada al changelog con la fecha de hoy. Las secciones posibles son `--agregado`, `--cambiado`, `--corregido`, `--eliminado` y `--seguridad`, y cada una se puede repetir.
3. Abre el PR hacia `main`. La GitHub Action `Versionado de agentes` comprueba que:
   - cada agente cuyos skills cambiaron tiene una versión mayor que la de `main`;
   - el changelog empieza por esa versión, con fecha, entradas y sin `[PENDIENTE]`.
4. Al fusionar, la misma acción crea la etiqueta `<agente>/vX.Y.Z` y la release con las notas del changelog.

## Comandos

```bash
python3 scripts/versionado.py listar
```

```bash
python3 scripts/versionado.py verificar --base origin/main
```

```bash
python3 scripts/versionado.py notas documentacion 0.3.0
```

## Usar una versión concreta

Las instalaciones apuntan a una copia del repositorio, así que cambiar de versión es cambiar de commit en esa copia:

```bash
git fetch --tags; git checkout documentacion/v0.3.0
```

Para volver a la última versión: `git checkout main; git pull`. Si en el mismo repositorio hay varios agentes, una etiqueta fija todo el repositorio en ese commit.

## Agregar un agente nuevo

1. Crea sus skills en `skills/<skill>/SKILL.md`.
2. Crea `agentes/<agente>/agente.json` con `nombre` (igual al nombre de la carpeta), `version` (`0.1.0`), `descripcion` y `skills`.
3. Crea `agentes/<agente>/CHANGELOG.md` con la entrada `## [0.1.0] - AAAA-MM-DD`.
4. Ejecuta `python3 scripts/versionado.py verificar`.
