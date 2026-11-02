# Agents-Skills
Agentes Experimentales

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

Memoria del agente: el agente trabaja siempre con el mismo estilo y no decide nada por su cuenta. Lo que no está definido se lo pregunta al usuario y lo registra en [`memoria/decisiones.md`](skills/documentacion-estilo/memoria/decisiones.md). Luego incorpora la regla al skill y envía la memoria a este repositorio con un PR que explica qué cambió, por qué y cómo ([procedimiento](skills/documentacion-estilo/references/memoria.md)).

Verificador independiente:

```bash
python3 skills/documentacion-generar/scripts/verificar_doc.py --prompt docs/prompt-estilo.md docs/manual/
```

Para usar los skills en Claude Code, enlázalos en `~/.claude/skills/` (o en `.claude/skills/` de un proyecto):

```bash
ln -s "$PWD/skills/documentacion-estilo" "$PWD/skills/documentacion-generar" ~/.claude/skills/
```
