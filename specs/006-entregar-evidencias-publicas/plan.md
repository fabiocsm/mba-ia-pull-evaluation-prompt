# Implementation Plan: Entrega pública com evidências acessíveis e reprodução

**Branch**: `dev` | **Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

**Input**: `specs/006-entregar-evidencias-publicas/spec.md`, Fase 8, seção 9 e R12–R18 do
[plano mestre](../../plan/plano-implementacao.md), com a entrega da
[005](../../docs/avaliacao-v2.md#entrega-à-006) aprovada.

**Estado**: planejamento e desenho concluídos em 2026-10-19; [25 tarefas](tasks.md) geradas;
implementação pendente. O setup retornou `BRANCH=006-entregar-evidencias-publicas` como identificador da
feature; a branch Git continua `dev`. O ponteiro local `.specify/feature.json` (ignorado
pelo Git) seleciona a 006 por pedido do autor. Nenhuma branch criada ou trocada.

## Summary

Tornar a entrega avaliável sem acesso ao workspace: compartilhar uma única vez o dataset de
avaliação (que expõe os três experimentos, incluindo o final `CIC-03`), conferir os links sem
login, versionar screenshots legíveis das cinco médias, do dataset e de três traces
(simples, médio, complexo), consolidar o README nas três seções obrigatórias preservando o
enunciado, reproduzir o roteiro em clone limpo e, com autorização do autor, publicar `dev` e
atualizar `main` no fork público.

Insumos da 005: experimento final `d864cfbb-6ab9-4901-ab06-62f68ccd96fc` (revisão
`36a96c05…696f`, aprovado, média geral 0.8709), dataset `8c78638d-37a5-4175-9984-8db0e3473228`
ainda não compartilhado, traces #1/#10/#14 registrados e a limitação de #14 (meta de CPU
inventada), que deve aparecer nos resultados.

Decisões centrais da [pesquisa](research.md): `share_dataset` uma vez, com autorização (D01);
screenshots sempre, `share_run` só se o trace não for público (D02); PNG em
`docs/evidencias/` (D03); README reorganizado sobre o enunciado intacto (D04); comparação v1/v2
qualitativa, numérica não executada (D05); reprodução em clone limpo como `REP-006` (D06), mais
`REP-006B` por um segundo executor para o SC-004 ou pendência declarada; push e `main` só com
autorização (D07); testes offline da entrega (D08). US2 depende das evidências de US1 (links e
PNG citados no README); a independência da spec vale para a revisão do conteúdo.

Fora do escopo: editar a v2 (reabre a 005), novo avaliador, métricas ou dados; serviços novos.

## Technical Context

**Language/Version**: Python 3.10+; ambiente existente CPython 3.11.14 em `venv/`.

**Primary Dependencies**: pins existentes (`langsmith==0.13.0`, `langchain-core==1.6.4`,
`langchain-openai==1.6.2`, `langchain-google-genai==4.4.0`, `python-dotenv==1.2.3`,
`pyyaml==6.0.3`, `pytest==9.1.1`); `gh` CLI e Git para o fork; navegador integrado para
conferência anônima e capturas. Nenhuma instalação nova.

**Storage**: `docs/entrega-publica.md` (registro), `docs/evidencias/*.png` (versionado),
README; LangSmith (dataset/experimentos/traces) e GitHub (fork). `results/` e `screenshots/`
ignorados, nunca cópia única.

**Testing**: `tests/test_delivery.py` (offline, documental) + suíte existente (817); a
reprodução real é verificação independente.

**Target Platform**: CLI local macOS/POSIX; navegador para conferência pública.

**Project Type**: scripts CLI existentes e documentação; nenhum serviço novo.

**Performance Goals**: N/A. Uma avaliação de reprodução (60 chamadas LLM).

**Constraints**: um único `share_dataset`; ações públicas (compartilhar, `share_run`, push,
`main`) só com autorização explícita no chat; nenhum segredo em arquivos, logs ou PNG;
protegidos, v1 e v2 intactos; histórico de experimentos preservado.

**Scale/Scope**: 1 dataset, ~5–6 PNG, 3 seções do README, 1 reprodução (≈ US$ 0,27; acumulado
≈ US$ 1,03, dentro de US$ 1–5), 1 fork.

## Constitution Check

Gate avaliado antes da pesquisa e reavaliado após o desenho. PASS refere-se ao plano.

| Regra | Antes da Fase 0 | Após a Fase 1 |
| --- | --- | --- |
| I — Integridade/escopo | PASS: nenhum arquivo protegido ou dado alterado | PASS: E01/E07 conferem hashes; v2 intacta; edição reabre a 005 |
| II — Prompt verificável | PASS: v2 final já validada | PASS: README cita trechos reais da v2 final e as técnicas aplicadas |
| III — Hub/rastreabilidade | PASS: links e revisão da 005 | PASS: evidências ligadas a `CIC-03`, `36a96c05` e IDs de trace; link do dataset guardado (E02) |
| IV — Avaliação íntegra | PASS: notas só do experimento real | PASS: resultados finais iguais ao registro; ilustrativas proibidas; reprodução não substitui o final |
| V — Validação/entrega reproduzível | PASS: exige três seções, fork público, evidências acessíveis | PASS: testes de entrega, reprodução limpa, conferência sem login, PNG fora de pastas ignoradas |
| Restrições (credenciais, compartilhamento único) | PASS | PASS: varredura de segredos, `.env` nunca versionado, um único `share_dataset` |

Nenhuma violação. Decisões que dependem do autor (compartilhar, `share_run`, push/`main`) são
gates de execução, não lacunas de requisito.

## Project Structure

### Documentation (this feature)

```text
specs/006-entregar-evidencias-publicas/
├── spec.md
├── checklists/requirements.md
├── plan.md                      # este arquivo
├── research.md                  # D01–D09
├── data-model.md                # entrada, evidência, compartilhamento, reprodução, integridade, pacote
├── contracts/entrega-publica.md # E01–E09 e matriz de falhas
├── quickstart.md                # W01–W09
└── tasks.md                     # gerado depois por $speckit-tasks
```

### Source Code (repository root)

```text
README.md                        # três seções obrigatórias sobre o enunciado preservado
docs/entrega-publica.md          # criar: registro de compartilhamento, conferências, reprodução, integridade
docs/evidencias/avaliacao-v2-*.png  # criar: dataset, cinco médias, três traces
docs/historico-readme.md         # criar: subseções por spec retiradas do README, copiadas literalmente
tests/test_delivery.py           # criar: testes offline da documentação de entrega
docs/avaliacao-v2.md             # somente leitura (fonte dos números finais)
prompts/bug_to_user_story_v2.yml # somente leitura (revisão 36a96c05)
src/, datasets/                  # somente leitura
```

**Structure Decision**: entrega documental e de evidências, sem código de produção novo; o
único código é o teste offline da documentação.

## Phase 0 — Pesquisa

[research.md](research.md): estado remoto (dataset não compartilhado, três experimentos,
fork público sem o trabalho publicado), decisões D01–D09. Nenhum `NEEDS CLARIFICATION`.

## Phase 1 — Desenho e sequência

1. **Entrada** (W01): revalidar hashes, HEAD e `CIC-03`.
2. **Testes offline** (W02): escrever `tests/test_delivery.py` com falha pertinente antes do README final.
3. **Compartilhamento** (W03): ler estado → autorização → `share_dataset` uma vez → registrar.
4. **Conferência anônima e screenshots** (W04/W05); `share_run` só se necessário e autorizado.
5. **README** (W06): três seções; testes de entrega passam.
6. **Reprodução** (W07): clone limpo, `REP-006`, custo e divergências registrados.
7. **Integridade** (W08) e commit local.
8. **Publicação** (W09): autorização → push de `dev` e atualização de `main` → conferência sem login.

Entidades em [data-model.md](data-model.md); contrato em
[contracts/entrega-publica.md](contracts/entrega-publica.md); validações em [quickstart.md](quickstart.md).

## Rastreabilidade e aceite

| Requisito | Plano mestre | Decisão/contrato | Verificação / critério |
| --- | --- | --- | --- |
| FR-001 | R17 | D01, E02 | W03/W04; SC-001 |
| FR-002 | R15/R17 | D02/D03, E04 | W05; SC-002 |
| FR-003 | R17 | D02, E03/E04 | W04/W05; SC-001 |
| FR-004 | R17 | D01, E02 | W03; SC-001 |
| FR-005 | R14/R15/R16 | D04, E05 | W02/W06; SC-003 |
| FR-006 | R15 | D04/D05, E05 | W02/W06; SC-003 |
| FR-007 | R16 | D06, E05/E06 | W07; SC-004 |
| FR-008 | R18 | D07, E08 | W09; SC-005 |
| FR-009 | R12/R13 | D09, E07 | W08; SC-005 |
| FR-010 | R10/R12 | D06, E06/E09 | W07; SC-004/SC-005 |

Aceite da implementação: link público do dataset e do experimento final registrados e
conferidos sem login; cinco médias, dataset e três traces (com julgamentos) com evidência
pública legível; README com as três seções, números iguais ao registro e `REP-006`
identificado; reprodução registrada; SC-004 por segundo executor (`REP-006B`) ou pendência
declarada; integridade aprovada; fork `main` publicado e conferido sem login após autorização.

### Correção da análise — 2026-10-19

`/speckit-analyze` apontou 9 achados (2 HIGH, 4 MEDIUM, 3 LOW), todos corrigidos na pesquisa,
contrato, modelo, guia, tarefas e neste plano, sem mudar requisitos; ver o
[registro](tasks.md#correção-da-análise--2026-10-19). O SC-004 não foi reinterpretado: exige
segundo executor ou fica pendente e declarado.

## Complexity Tracking

Sem violações a justificar.

## Conferência do planejamento

Planejamento sem compartilhamento, push, chamada LLM ou experimento. Consultas somente de
leitura (`read_dataset_shared_schema`, `read_run_shared_link`, `list_projects`, `gh repo view`).
`.specify/extensions.yml` ausente: nenhum hook antes/depois. Próxima etapa: `$speckit-tasks`.
