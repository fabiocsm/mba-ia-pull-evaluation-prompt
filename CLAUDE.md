# Orientações para o Claude Code

As instruções do projeto ficam em [AGENTS.md](AGENTS.md), compartilhadas com o Codex.

@AGENTS.md

## Spec Kit no Claude Code

- As skills do Spec Kit estão em `.claude/skills/` e são invocadas como
  `/speckit-specify`, `/speckit-clarify`, `/speckit-plan`, `/speckit-tasks`,
  `/speckit-analyze`, `/speckit-implement`, entre outras.
- A integração `codex` (`.agents/skills/`) continua instalada e é a padrão em
  `.specify/integration.json`; não a remova.
- A constituição em `.specify/memory/constitution.md` vale para os dois agentes.
