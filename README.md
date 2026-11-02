# Agents-Skills
Agentes Experimentales

| Agente | Versión | Skills |
|---|---|---|
| [Documentación](agentes/documentacion/CHANGELOG.md) | ver [`agente.json`](agentes/documentacion/agente.json) | `documentacion-estilo`, `documentacion-generar` |

Cada agente tiene su propia versión SemVer, su changelog y etiquetas `<agente>/vX.Y.Z`. Las reglas y el flujo están en [`VERSIONADO.md`](VERSIONADO.md). Para ver las versiones actuales:

```bash
python3 scripts/versionado.py listar
```

## Agente de documentación

Dos skills que trabajan juntos:

| Skill | Qué hace | Salida |
|---|---|---|
| [`documentacion-estilo`](skills/documentacion-estilo/SKILL.md) | Prompteador: define metodología (RUP, UP, Scrum, ISO/IEEE 29148, Diátaxis, académica), estructura, componentes visuales, tipografía, color y normas de escritura | `docs/prompt-estilo.md` |
| [`documentacion-generar`](skills/documentacion-generar/SKILL.md) | Ejecutable: recibe el prompt de estilo (o lo crea si no existe), redacta el documento y lo verifica | Documento en la carpeta `salida` del prompt |

Flujo:

```
pedido ──► ¿hay prompt-estilo.md? ──no──► documentacion-estilo ──► prompt-estilo.md
                     │ sí                                                  │
                     └───────────────► documentacion-generar ◄─────────────┘
                                         │
                                         ├─ redacta según el prompt
                                         ├─ scripts/verificar_doc.py
                                         └─ exporta (docx/pdf) si se pide
```

Configurador visual: [`assets/configurador.html`](skills/documentacion-estilo/assets/configurador.html) se abre en el navegador. Permite elegir metodología, estructura, componentes, diagramas, tipografía, tamaños, color y normas, con vista previa en vivo, y genera el `prompt-estilo.md` y las respuestas para la memoria. También puedes subir un documento propio (.md, .docx, .html o .txt) para verlo con el estilo en vivo, revisar sus desvíos y ajustar solo una parte seleccionada.

Plantillas: [`references/plantillas/`](skills/documentacion-estilo/references/plantillas/README.md) guarda los diseños tomados de documentos del usuario (trabajo de campo, informe técnico, auditoría, proforma, ficha, láminas de arquitectura y diagramas). Cada una tiene un preajuste en el configurador, y [`scripts/extraer_estilo_docx.py`](skills/documentacion-estilo/scripts/extraer_estilo_docx.py) extrae el diseño de un .docx nuevo.

Memoria del agente: el agente trabaja siempre con el mismo estilo y no decide nada por su cuenta. Lo que no está definido se lo pregunta al usuario y lo registra en [`memoria/decisiones.md`](skills/documentacion-estilo/memoria/decisiones.md). Luego incorpora la regla al skill y envía la memoria a este repositorio con un PR que explica qué cambió, por qué y cómo ([procedimiento](skills/documentacion-estilo/references/memoria.md)).

Verificador independiente:

```bash
python3 skills/documentacion-generar/scripts/verificar_doc.py --prompt docs/prompt-estilo.md docs/manual/
```

Para usar los skills en Claude Code, enlázalos en `~/.claude/skills/` (o en `.claude/skills/` de un proyecto):

```bash
ln -s "$PWD/skills/documentacion-estilo" "$PWD/skills/documentacion-generar" ~/.claude/skills/
```
