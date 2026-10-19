# Implementation Plan: Avaliação íntegra e otimização guiada por evidências

**Branch**: `dev` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

**Input**: `specs/005-avaliar-iterar-v2/spec.md`, Fases 6–7, seção 7 (medição e custo)
e R08–R10/R12/R17 do [plano mestre](../../plan/plano-implementacao.md), com as
dependências 001, 003 e 004.

**Estado**: planejamento, desenho e [35 tarefas](tasks.md) concluídos; duas análises SDD
realizadas e seus 11 + 9 achados corrigidos; **implementação concluída em 2026-10-19**:
35/35 tarefas, 85 testes offline da auditoria, dataset criado e auditado, `CIC-01` real
aprovado (média geral 0.8522) e, por decisão do autor, `CIC-02` (0.8733) e `CIC-03`
aprovado como final (revisão 36a96c05, média geral 0.8709, F1-Score 0.8474); ver
[registro](../../docs/avaliacao-v2.md) e [execução](tasks.md#registro-de-execução). O setup retornou `BRANCH=005-avaliar-iterar-v2` como identificador da
feature; a branch Git continua `dev`. O ponteiro local `.specify/feature.json`
seleciona a 005, que passa a ser a spec ativa. Nenhuma branch foi criada ou trocada.

## Summary

Executar o avaliador fornecido sobre a revisão publicada e conferida da v2, provar
que o experimento é completo (15 respostas, 75 notas válidas) e vinculado à revisão
avaliada, decidir pela regra integral (cinco médias e média geral `>= 0.8`) e iterar
a v2 em 3–5 ciclos registrados, sem alterar avaliador, juízes, dados ou limiar.

Abordagem: um roteiro executável em `docs/avaliacao-v2.md`, no padrão da
[preparação](../../docs/preparacao.md#roteiro-executavel), com três blocos principais: gate de
entrada (somente leitura), dataset (criação única pela função fornecida e auditoria)
e auditoria do experimento (somente leitura). No isolamento D03, um bootstrap opcional
inicializa o projeto vazio antes do dataset e do gate. Testes offline em
`tests/test_evaluation_audit.py` exercitam esses blocos com dublês. As notas vêm
exclusivamente de `python src/evaluate.py`; a auditoria só lê e recalcula.

Decisões centrais da [pesquisa](research.md): auditar o dataset **antes** do primeiro
experimento (D01–D03); vincular cada run ao commit do Hub por `lc_hub_commit_hash`,
além de HEAD e hashes antes/depois (D04); identificar o experimento pela URL impressa
(D05); tratar zeros produzidos por falha de juiz ou resposta vazia como notas
inválidas (D06); manter `COND-001` e estimar ≈ US$ 0,31 por experimento (D08); nunca
selecionar execuções favoráveis (D09).

Fora do escopo: compartilhar o dataset, publicar evidências, screenshots públicas e
seções finais do README (spec 006); baseline numérica da v1 (opcional, só com
decisão explícita e custo registrado).

## Technical Context

**Language/Version**: Python 3.10+; ambiente existente CPython 3.11.14 em `venv/`.

**Primary Dependencies**: pins existentes `langsmith==0.13.0`, `langchain-core==1.6.4`,
`langchain-openai==1.6.2`, `python-dotenv==1.2.3`, `pyyaml==6.0.3`, `pytest==9.1.1`;
`langchain-google-genai==4.4.0` preservado sem uso nesta condição; biblioteca padrão para
SHA-256, JSON, `math.isfinite`, datas e parsing da URL. Nenhuma instalação nova.

**Storage**: registros sanitizados em `docs/avaliacao-v2.md` (versionado); logs brutos
do avaliador em `results/` (ignorado, cópia local); dataset, experimentos, runs e
feedback no LangSmith. Sem banco ou manifesto paralelo obrigatório.

**Testing**: novos testes offline em `tests/test_evaluation_audit.py` para os blocos
documentados (positivo e negativos de C01–C06, sigilo, nenhum acesso de rede/LLM);
`pytest tests/test_prompts.py -v` e regressão existente a cada revisão. A avaliação
real é verificação independente e cumulativa.

**Target Platform**: CLI local a partir da raiz; macOS/POSIX comprovado na 001.

**Project Type**: scripts CLI existentes; nenhum serviço, API ou interface nova.

**Performance Goals**: `max_concurrency=1` do avaliador mantido; 60 chamadas LLM por
experimento (15 gerações + 45 julgamentos). Gate e auditoria sem chamadas LLM.

**Constraints**: quatro protegidos e v1 somente leitura; dataset 15/5/7/3 preservado;
mesma condição em todos os ciclos comparados; revisão estável durante a execução;
mudanças de comportamento só na v2; Few-shot próprio (sem casos do dataset); sem
instruções ao juiz; nenhum segredo em saídas; nenhum dado remoto apagado.

**Scale/Scope**: 1 dataset, 3–5 ciclos (≈ 180–300 chamadas LLM), estimativa total
≈ US$ 0,9–1,6 (até US$ 2,5 com a margem de US$ 0,50 por experimento de D08) e gate de
decisão em US$ 4 acumulados (C09). Consumo real lido dos runs.

## Constitution Check

Gate avaliado antes da pesquisa e reavaliado após o desenho. PASS refere-se ao
plano, sem declarar experimentos executados ou métricas obtidas.

| Regra | Antes da Fase 0 | Após a Fase 1 |
| --- | --- | --- |
| I — Integridade/escopo | PASS: avaliador e dados usados sem alteração | PASS: dataset criado pela função fornecida importada; C01 confere hashes antes e depois; isolamento sem apagar dados (D03) |
| II — Prompt verificável | PASS: ajustes só na v2 | PASS: C08 mantém Few-shot/Role Prompting, proíbe exemplos do dataset e técnica declarada sem aplicação |
| III — Hub/rastreabilidade | PASS: avaliar a revisão publicada | PASS: HEAD antes/depois, `lc_hub_commit_hash` por run, hashes locais, ID/URL do experimento por ciclo (D04/D05) |
| IV — Avaliação íntegra | PASS: limiar e agregação originais | PASS: 75 notas válidas com marcadores de falha excluídos (D06); regra integral C06; 3–5 ciclos e oscilação sem seleção favorável (C09/D09) |
| V — Validação/reprodução | PASS: seis testes preservados | PASS: testes offline da auditoria, guia V01–V11 e registro versionado; evidências públicas reservadas à 006 |
| Stack/configuração | PASS: `COND-001` da 001 | PASS: condição constante, revalidação do modelo no gate, custo planejado contra US$ 1–5 |

Nenhuma exceção ou esclarecimento de escopo necessário. Falhas externas (modelo,
rate limit, permissão) bloqueiam a execução correspondente sem relaxar o enunciado.

## Project Structure

### Documentation (this feature)

```text
specs/005-avaliar-iterar-v2/
├── spec.md
├── checklists/requirements.md
├── plan.md                    # este arquivo
├── research.md                # D01–D11
├── data-model.md              # condição, revisão, dataset, experimento, ciclo, custo
├── contracts/avaliacao-v2.md  # C01–C10 e matriz de falhas
├── quickstart.md              # V01–V11
└── tasks.md                   # 35 tarefas geradas por $speckit-tasks em 2026-10-18
```

### Source Code (repository root)

```text
docs/avaliacao-v2.md                 # criar: roteiro (gate, dataset, auditoria) e registro dos ciclos
tests/test_evaluation_audit.py       # criar: testes offline dos blocos documentados
prompts/bug_to_user_story_v2.yml     # editar somente nos ciclos, com hipótese registrada
tests/test_prompts.py                # ajustar só se um contrato local mudar no ciclo; seis obrigatórios intactos
README.md                            # link para o registro; seções finais na 006
src/evaluate.py                      # executar; protegido
src/metrics.py                       # protegido
src/utils.py                         # protegido
src/push_prompts.py                  # reutilizar a cada revisão; sem mudança prevista
datasets/bug_to_user_story.jsonl     # protegido
prompts/bug_to_user_story_v1.yml     # referência, somente leitura
results/                             # logs locais ignorados, nunca evidência única
```

**Structure Decision**: auditoria documentada e testada, sem novo módulo de produção.
O avaliador permanece a única fonte das notas; os blocos apenas conferem pré-condições,
leem resultados e recalculam a agregação fornecida para detectar incompletude.

## Phase 0 — Pesquisa e decisões

[research.md](research.md) registra o estado remoto (dataset inexistente, HEAD
`4278de75…`, nenhum experimento), a semântica de falha dos juízes, o vínculo
experimento ↔ commit pelo SDK, a identificação pela URL, condição e custo, ciclos e
estratégia de ajuste. Pesquisa somente por leitura; nenhuma pendência de desenho.

## Phase 1 — Desenho e sequência de execução

1. **Baseline**: revalidar hashes, aceite da 004 e HEAD; consultar `langsmith --help`.
2. **Roteiro e testes (offline)**: escrever os blocos de `docs/avaliacao-v2.md` e
   `tests/test_evaluation_audit.py` primeiro com casos negativos (C04–C06), depois o
   positivo; rede, `.env` real e fábricas LLM bloqueados nos testes.
3. **Dataset**: criação única com `create_evaluation_dataset` → auditoria C02 →
   registrar `dataset_id` e exportá-lo ao gate. Divergência: declarar `COND-00N` e
   isolar (D03) antes de qualquer LLM. Nos ciclos seguintes, C02 só audita.
4. **CIC-01**: avaliar a v2 publicada da 003/004 sem edição (referência inicial):
   C02 → C01 (incluindo C01.6: workspace e dataset `idêntico`) → C03 → C04–C07;
   registrar ciclo, tokens e custo.
5. **CIC-02…05**: para cada métrica fraca, problema e hipótese (D10) → editar v2 →
   testes → push conferido → commit → C02 → C01 → C03 → C04–C07. Parar conforme C09.
6. **Final**: confirmar que a última revisão editada é a aprovada (SC-005), três
   traces de dificuldades distintas (SC-004) e integridade (V11). Entregar à 006 os
   IDs, URLs e números reais; não compartilhar dataset nem publicar evidências.

Entidades em [data-model.md](data-model.md); contrato em
[contracts/avaliacao-v2.md](contracts/avaliacao-v2.md); validações em
[quickstart.md](quickstart.md). O planejamento termina após o desenho da Fase 1.

## Rastreabilidade e aceite

| Requisito | Plano mestre | Decisão/artefato | Verificação / critério |
| --- | --- | --- | --- |
| FR-001 | R08/R12/R17 | D01–D03, C02 | V04; SC-001 |
| FR-002 | R08/R12 | D04/D05, C01/C03/C04 | V03/V05/V06; SC-005 |
| FR-003 | R08 | D06, C05 | V02/V06; SC-001 |
| FR-004 | R09 | C06 | V02/V09; SC-002 |
| FR-005 | R08/R10 | Modelo `Experimento`/`CicloOtimização`, C08 | V06/V08; SC-003 |
| FR-006 | R17 | C07, `EvidênciaTrace` | V07; SC-004 |
| FR-007 | R10 | D10, C08 | V08; SC-003 |
| FR-008 | R10/R12 | D03/D08/D09, C09/C10 | V08/V10; SC-003 |
| FR-009 | R10 | C09 | V10; SC-003 |
| FR-010 | R10/R12 | D09, C08/C09 | V10/V11; SC-005 |
| Transversal | R12/R13 | C01/C10 | V01/V11 |

Aceite da implementação: testes offline e regressão aprovados; dataset auditado;
todos os ciclos executados registrados; experimento final `aprovado` pela regra C06
com revisão local/Hub correspondente e três traces. Reprovação após cinco ciclos
mantém a 005 aberta com diagnóstico e continuidade, sem declarar sucesso.

### Correção da análise — 2026-10-18

`$speckit-analyze` apontou 11 achados (1 CRITICAL, 1 HIGH, 5 MEDIUM, 4 LOW), todos
corrigidos no contrato, modelo, guia e tarefas, conforme o
[registro](tasks.md#correção-da-análise--2026-10-18). Os principais: inspeção no
dashboard de cada nova revisão (constituição III, C1); código do avaliador preservado
com `pipefail` em `AVALIACAO_EXIT_CODE` (I1); gate de entrada concentrando condição,
testes, inspeção e custo, com `causa` explícita (D1/I3/I4). Commits locais por ciclo
autorizados pelo autor; push Git continua fora desta feature. Requisitos inalterados.

### Segunda correção da análise — 2026-10-18

Nova execução de `/speckit-analyze` apontou 9 achados (1 HIGH, 3 MEDIUM, 5 LOW), todos
corrigidos no contrato, modelo, pesquisa, guia, tarefas e neste plano, conforme o
[registro](tasks.md#segunda-correção-da-análise--2026-10-18). Principal (G1): o gate
passa a conferir workspace e dataset `idêntico` (C01.6), e a auditoria C02 precede o
gate em todo ciclo; `AVALIACAO_DATASET_ID`, `AVALIACAO_DATASET` e `AVALIACAO_CONDICAO`
transportam dataset e condição declarada (U1/U2). A aprovação antecipada mantém o
teste documental e a tabela comparativa (I1). Requisitos inalterados.

## Complexity Tracking

Sem violações a justificar. O único código novo é de auditoria (blocos documentados
e seus testes), necessário porque o avaliador fornecido aceita zeros de falha e
médias sobre subconjuntos; não reimplementa métricas nem cria serviço.

## Conferência do planejamento

Planejamento sem implementação, chamadas LLM, criação de dataset, publicação ou
experimento. Consultas remotas somente de leitura (`list_datasets`, `get_prompt`,
`list_projects`). `.specify/extensions.yml` ausente: nenhum hook antes/depois.
Conferidos 102 links locais nos artefatos da 005 e nos dois índices atualizados;
hashes dos quatro protegidos iguais ao manifesto da 001; suíte existente
**732 testes aprovados** (não testa a auditoria ainda inexistente nem métricas);
`git diff --check` aprovado. Nenhum código, YAML ou `tasks.md` alterado/criado.
Tarefas geradas depois por `$speckit-tasks`: Setup (3), Foundational (2), US1 (12),
US2 (4), US3 (9) e Polish (5). Análise e correções concluídas; próxima etapa:
`$speckit-implement` da 005.
