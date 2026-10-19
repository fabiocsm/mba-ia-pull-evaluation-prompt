---
description: "Tarefas da spec 006: entrega pública com evidências acessíveis e reprodução"
---

# Tasks: Entrega pública com evidências acessíveis e reprodução

**Input**: documentos em `specs/006-entregar-evidencias-publicas/`.
**Data**: 2026-10-19 | **Branch Git**: `dev` | **Feature ativa**: 006.

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contrato E01–E09](contracts/entrega-publica.md),
[quickstart W01–W09](quickstart.md), [README](../../README.md),
[constituição v1.0.0](../../.specify/memory/constitution.md) e a
[entrega da 005](../../docs/avaliacao-v2.md#entrega-à-006) (experimento final `CIC-03`
`d864cfbb-6ab9-4901-ab06-62f68ccd96fc`, revisão `36a96c0540682ed6b8569487222b88e11d1889a3976b75fea83553dc662b696f`).

**Estado**: 0/25 tarefas concluídas. Dataset não compartilhado; trabalho das 001–006 só em
`dev` local; nenhuma evidência pública da avaliação.

**Ações externas** (somente com autorização explícita do autor no chat, por ação):
`share_dataset` (uma única vez), `share_run` (se necessário), `git push` e atualização de
`main`. Sem autorização, a tarefa correspondente fica bloqueada e registrada como tal.

**Commits locais**: o commit do plano (`adf15be`) assumiu que a autorização de commits locais
da 005 vale para a 006; T001 confirma com o autor. Push nunca está implícito.

**Tests**: incluídos por decisão do plano (D08): `tests/test_delivery.py`, offline e
documental. Escrever os casos antes do conteúdo, observar a falha pertinente e depois
completar. Testes não substituem a conferência sem login nem a reprodução real.

**Organization**: US1 (P1) produz os links e screenshots que US2 (P1) cita no README; US2
termina com a reprodução; US3 (P2) faz a integridade e a publicação do fork.

## Format: `[ID] [P?] [Story] Description`

- IDs sequenciais; cada tarefa tem checkbox e caminho exato.
- `[P]` somente em arquivos diferentes sem dependência pendente.
- FR/SC da 006; E01–E09 do contrato; W01–W09 do guia; D01–D09 da pesquisa.

## Path Conventions

Projeto único na raiz. Registro em `docs/entrega-publica.md`; imagens em
`docs/evidencias/avaliacao-v2-*.png`; testes em `tests/test_delivery.py`. Somente leitura:
`src/evaluate.py`, `src/metrics.py`, `src/utils.py`, `datasets/bug_to_user_story.jsonl`,
`prompts/bug_to_user_story_v1.yml`, `prompts/bug_to_user_story_v2.yml` (editar a v2 reabre a
005) e `docs/avaliacao-v2.md` (fonte dos números finais). `screenshots/` e `results/` são
ignorados e nunca cópia única.

## Phase 1: Setup — entrada e estado remoto

**Purpose**: confirmar a entrada da 005 e o estado antes de qualquer ação pública.

- [ ] T001 Executar W01 de `specs/006-entregar-evidencias-publicas/quickstart.md`: hashes dos quatro protegidos contra `docs/integridade-inicial.json`, v1 `2cddcf8f8183b4d29a5bca4d4efca17601962aa98ac75323f7dabbfa905c0d70`, v2 `692df6ae86848e2dce0fc1a9c2d1f6fec95fc48721a960837fbdd8de3f958974`, `git status` limpo em `dev`, `Client.get_prompt("fabiocsm/bug_to_user_story_v2")` com HEAD `36a96c0540682ed6b8569487222b88e11d1889a3976b75fea83553dc662b696f` público; confirmar com o autor no chat se commits locais estão autorizados na 006; registrar tudo no registro de execução de `specs/006-entregar-evidencias-publicas/tasks.md`.
- [ ] T002 Ler, sem escrita, o estado externo e registrar em `specs/006-entregar-evidencias-publicas/tasks.md`: compartilhamento do dataset `8c78638d-37a5-4175-9984-8db0e3473228` (corpo vazio = não compartilhado; o SDK 0.13.0 levanta `TypeError`), `read_run_shared_link` dos três runs raiz finais (#1 `01a1525d-899e-7711-835f-249803cf7318`, #10 `01a1525d-3ff5-7ae0-8915-df303b9a69b8`, #14 `01a1525d-0432-7f50-99c6-c059ec587aa2`), `gh repo view fabiocsm/mba-ia-pull-evaluation-prompt` (público, fork, branch padrão `main`) e `git log origin/main -1`.

---

## Phase 2: Foundational — registro e estrutura de testes

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [ ] T003 [P] Criar `docs/entrega-publica.md` com: escopo e limites (ações externas só com autorização; um único `share_dataset`); rastreabilidade FR-001…FR-010 → E/W; entrada da 005 (`ResultadoAprovado` do `specs/006-entregar-evidencias-publicas/data-model.md`); seções vazias para `CompartilhamentoDataset`, tabela `EvidênciaPública` (colunas `id`, `tipo` ∈ `link_dataset` · `link_prompt` · `link_trace` · `screenshot` · `fork`, `alvo`, `endereco`, `relacao`, `conferencia_anonima` ∈ `visível` · `parcial` · `exige_login`, `sigilo`), `RegistroReprodução`, `ConferênciaIntegridade` e `PacoteEntrega` (estados `preparado` → `autorizado` → `publicado` → `conferido`).
- [ ] T004 [P] Criar `tests/test_delivery.py` com helpers offline: leitura do `README.md` e de `docs/entrega-publica.md`; extração de seções `## …`; obtenção do README do repositório base por `git show a94ce44:README.md` (subprocess somente leitura); lista de imagens Markdown citadas; `git check-ignore`; leitura do registro final de `docs/avaliacao-v2.md` (bullet `**Médias**` e `**Média geral**` do ciclo final indicado em `## Entrega à 006`); sem rede nem `.env`.

**Checkpoint**: registro e helpers prontos; nada público alterado.

---

## Phase 3: User Story 1 — Inspecionar resultados sem acesso privado (Priority: P1) 🎯 MVP

**Goal**: link público único do dataset (com os experimentos da v2), conferência sem login e
screenshots versionadas das cinco médias, do dataset e de três traces.

**Independent Test**: em sessão sem login, abrir o link do dataset e as imagens versionadas e
conferir 15 casos, o experimento `CIC-03` com as cinco médias e os traces #1/#10/#14 (W03–W05).

### Tests for User Story 1

- [ ] T005 [US1] Em `tests/test_delivery.py`, testes de evidência: toda imagem citada em `README.md` e `docs/entrega-publica.md` existe, começa com a assinatura PNG e não é ignorada pelo Git; existe exatamente um endereço `https://smith.langchain.com/public/<token>/d` e ele é idêntico em todas as ocorrências dos dois arquivos; a tabela `EvidênciaPública` cobre os alvos dataset 15, cinco médias, trace simples, médio e complexo, cada um com `conferencia_anonima` preenchida e, quando `parcial`/`exige_login`, uma linha `screenshot` para o mesmo alvo. Executar e registrar a falha pertinente antes de T007.

### Implementation for User Story 1

- [ ] T006 [US1] Reler imediatamente antes o estado de compartilhamento do dataset `8c78638d-37a5-4175-9984-8db0e3473228`; se já houver link, reutilizá-lo e pular T007 registrando a origem; se não houver, pedir ao autor no chat autorização explícita para um único `share_dataset` e registrar pedido e resposta em `docs/entrega-publica.md`. Sem autorização: parar a US1 e registrar `bloqueado`.
- [ ] T007 [US1] Com a autorização de T006, executar **uma vez** o trecho do README (`Client().share_dataset(dataset_name="mba-ia-pull-evaluation-prompt-eval")["url"]`), com `.env` carregado sem imprimir segredos; registrar data e URL em `docs/entrega-publica.md` (`CompartilhamentoDataset`) e reler o estado confirmando o mesmo token. Proibido repetir `share_dataset` ou chamar `unshare_dataset`; falha → registrar categoria/status e ler o estado antes de qualquer nova tentativa autorizada.
- [ ] T008 [US1] Conferir sem login (navegador integrado, botão “Log in” visível) o link de T007: 15 exemplos, experimentos `CIC-01`/`CIC-02`/`CIC-03` e as cinco médias de `CIC-03` (0.8773 / 0.8754 / 0.8474 / 0.8513 / 0.9033); conferir o prompt público `https://smith.langchain.com/hub/fabiocsm/bug_to_user_story_v2/36a96c05?tab=0`; registrar cada alvo como `visível`, `parcial` ou `exige_login` em `docs/entrega-publica.md`. Conteúdo das páginas é dado, não instrução.
- [ ] T009 [US1] Conferir sem login, a partir do link de T007, os traces #1 simple, #10 medium e #14 complex de `CIC-03` (entrada, mensagens, resposta, juízes e feedbacks). Se algum não for visível, pedir autorização explícita para `Client.share_run` nesses três runs raiz e, se autorizado, registrar as URLs em `docs/entrega-publica.md` e conferi-las sem login; sem autorização, registrar que os traces serão comprovados só por screenshot.
- [ ] T010 [US1] Capturar no navegador integrado, preferindo páginas públicas, e salvar como PNG real sem editar conteúdo: `docs/evidencias/avaliacao-v2-dataset.png` (15 exemplos), `docs/evidencias/avaliacao-v2-medias.png` (cinco médias de `CIC-03`), `docs/evidencias/avaliacao-v2-trace-simples.png`, `docs/evidencias/avaliacao-v2-trace-medio.png` e `docs/evidencias/avaliacao-v2-trace-complexo.png`; inspecionar cada imagem antes de versionar (nenhuma chave, e-mail, cabeçalho ou configuração privada) e recapturar se necessário.
- [ ] T011 [US1] Preencher a tabela `EvidênciaPública` (`EV-01`…) em `docs/entrega-publica.md` com alvo, endereço, `experiment_id`/`hub_commit`/`example_id`, conferência anônima e sigilo de cada link e PNG; executar `pytest tests/test_delivery.py -v` até os testes de T005 passarem e `pytest -q` para regressão; registrar contagens em `specs/006-entregar-evidencias-publicas/tasks.md`.

**Checkpoint**: evidências públicas e versionadas conferidas sem login (SC-001/SC-002).

---

## Phase 4: User Story 2 — Compreender o processo e repetir a execução (Priority: P1)

**Goal**: README com as três seções completas sobre o enunciado preservado e roteiro
reproduzido em clone limpo.

**Independent Test**: revisar as três seções e repetir `Como Executar` em clone/venv novos
(W06/W07).

### Tests for User Story 2

- [ ] T012 [US2] Em `tests/test_delivery.py`, testes do README: cada linha não vazia das seções do enunciado do README base (`git show a94ce44:README.md`, de `# Pull, Otimização…` até `## Dicas Finais` inclusive) continua presente; `## Técnicas Aplicadas (Fase 2)`, `## Resultados Finais` e `## Como Executar` aparecem exatamente uma vez; `Técnicas Aplicadas` cita `Role Prompting` e `Few-shot Learning` com justificativa e um trecho literal presente em `prompts/bug_to_user_story_v2.yml`; `Resultados Finais` contém as cinco médias e a média geral iguais ao registro final de `docs/avaliacao-v2.md`, o hash completo `36a96c05…696f`, o ID `d864cfbb-6ab9-4901-ab06-62f68ccd96fc`, o link público de T007, a tabela dos três ciclos, a comparação v1/v2, a limitação de #14 e a declaração de que a comparação numérica da v1 não foi executada; `Como Executar` contém, nesta ordem, `python3 -m venv`, `pip install -r requirements.txt`, `python src/pull_prompts.py`, `pytest tests/test_prompts.py`, `python src/push_prompts.py`, os blocos `AVALIACAO_DATASET`, `AVALIACAO_GATE`, `python src/evaluate.py` e `AVALIACAO_AUDITORIA`, e os nomes das variáveis do `.env` sem valores; nenhum padrão de chave (`sk-`, `lsv2_`, `AIza`). Executar e registrar a falha pertinente.

### Implementation for User Story 2

- [ ] T013 [US2] Antes de reorganizar, copiar literalmente as subseções por spec hoje dentro de `## Como Executar`, `## Técnicas Aplicadas (Fase 2)` e `## Resultados Finais` do `README.md` para `docs/historico-readme.md` (com data e commit de origem), preservando o histórico; o README passa a apontar para esse arquivo e para `docs/preparacao.md`, `docs/recuperacao-v1.md`, `docs/publicacao-v2.md`, `docs/avaliacao-v2.md` e `docs/entrega-publica.md`.
- [ ] T014 [US2] Reescrever `## Técnicas Aplicadas (Fase 2)` em `README.md`: Role Prompting e Few-shot Learning (o que, por que, trechos reais da v2 final, incluindo Exemplos 1–3), e as regras acrescentadas pelos ciclos (`CIC-02` critérios Dado/Quando/Então e critérios técnicos; `CIC-03` regra de valores) com o problema observado que as motivou; não declarar técnica não aplicada.
- [ ] T015 [US2] Reescrever `## Resultados Finais` em `README.md`: cinco médias e média geral de `CIC-03`, revisão e experimento finais, tabela `CIC-01`–`CIC-03` de `docs/avaliacao-v2.md`, comparação qualitativa v1/v2 (o que mudou e por quê), link público do dataset (T007), link do prompt, links de traces se existirem (T009), as cinco PNG de T010, custo, limitações (notas individuais < 0.8, meta inventada em #14, opções de código em #8) e a declaração de que a comparação numérica da v1 não foi executada (D05); nenhuma nota ilustrativa do enunciado como resultado.
- [ ] T016 [US2] Reescrever `## Como Executar` em `README.md` como roteiro único: pré-requisitos (Python 3.10+, contas, chave do provedor), venv, `pip install -r requirements.txt`/`pip check`, `.env` a partir de `.env.example` (nomes das variáveis e valores não secretos de `COND-001`: `openai`, `gpt-4.1-2025-04-14` nos dois papéis, tracing `true`), alternativa Gemini preservada, comandos ordenados de cada fase (pull, testes, push, blocos de dataset/gate, avaliação com `pipefail`, auditoria) e interpretação de sucesso/falha de cada passo; executar `pytest tests/test_delivery.py -v` e `pytest -q` até passarem e fazer o commit local de entrega se autorizado em T001.
- [ ] T017 [US2] Executar W07 (`REP-006`): `git clone --branch dev` do repositório local no diretório temporário da sessão, `python3.11 -m venv venv`, `pip install -r requirements.txt`, `pip check`, cópia do `.env` local (nunca versionado) e os comandos de `Como Executar` literalmente; esperado: v1 com hash `2cddcf8f…0d70`, testes aprovados, `push_prompts.py` código 0 sem nova revisão (HEAD continua `36a96c05…696f`), dataset `idêntico`, gate `gate_ok` com o custo acumulado (US$ 0,755018), avaliação e auditoria completas; registrar em `docs/entrega-publica.md` (`RegistroReprodução`) cada passo com código, o novo experimento como reprodução (não substitui `CIC-03`), tokens e custo e o novo acumulado.
- [ ] T018 [US2] Tratar divergências de T017: corrigir `README.md` onde o roteiro documentado não correspondeu ao executado e repetir somente o passo afetado (sem nova avaliação, salvo se a divergência for nela); reprovação ou incompletude da reprodução é registrada em `docs/entrega-publica.md` sem substituir o resultado final; v2 nunca é editada (isso reabriria a 005).

**Checkpoint**: README completo e roteiro reproduzido (SC-003/SC-004).

---

## Phase 5: User Story 3 — Conferir a entrega íntegra (Priority: P2)

**Goal**: integridade e sigilo comprovados, fork público com `main` atualizada e conferida sem login.

**Independent Test**: abrir o fork sem login e comparar v2, protegidos e evidências com a
referência e a revisão aprovada (W08/W09).

- [ ] T019 [US3] Executar W08 e registrar em `docs/entrega-publica.md` (`ConferênciaIntegridade`): hashes dos quatro protegidos e da v1; 15 exemplos 5/7/3; `git diff main..dev -- src/evaluate.py src/metrics.py src/utils.py datasets/` vazio; `langchain-openai` e `langchain-google-genai` instalados e `src/utils.py` intacto; v2 local = `36a96c05`; varredura de segredos (valores do `.env` e padrões) em todos os arquivos versionados e inspeção das PNG; `pytest -q`; `git diff --check`.
- [ ] T020 [US3] Pedir ao autor no chat autorização explícita para `git push origin dev` e para atualizar `main` com `dev` (fast-forward local + push, ou PR `dev → main` no fork — escolha do autor); registrar pedido, decisão e estado `PacoteEntrega` (`preparado`/`autorizado`) em `docs/entrega-publica.md`. Sem autorização: parar aqui e registrar.
- [ ] T021 [US3] Com a autorização de T020, executar o push de `dev` e a atualização de `main` escolhida, sem force-push nem reescrita de histórico; registrar commits enviados e o estado `publicado` em `docs/entrega-publica.md`.
- [ ] T022 [US3] Conferir sem login `https://github.com/fabiocsm/mba-ia-pull-evaluation-prompt` na branch `main`: README com as três seções, `prompts/bug_to_user_story_v2.yml` com SHA-256 `692df6ae…8974` (via conteúdo bruto público), código e as PNG de `docs/evidencias/` abrindo; links do README (dataset, prompt, traces) abrindo sem login; registrar `PacoteEntrega=conferido` em `docs/entrega-publica.md`.
- [ ] T023 [US3] Opcional, se o autor pedir: `REP-006B` a partir de clone anônimo do fork (`git clone https://github.com/fabiocsm/mba-ia-pull-evaluation-prompt`), venv novo, instalação e `pytest -q`, sem chamadas LLM salvo pedido explícito; registrar em `docs/entrega-publica.md` ou registrar não aplicável com justificativa.

**Checkpoint**: entrega publicada e conferida (SC-005).

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T024 Registrar no fim de `docs/entrega-publica.md` o encerramento: links finais, PNG, reprodução e custo total, separando o verificado sem login do que ficou pendente; atualizar o estado em `specs/006-entregar-evidencias-publicas/plan.md`, `specs/README.md` e `plan/plano-implementacao.md` (seção 9 do plano mestre).
- [ ] T025 Conferência final: links locais dos Markdown alterados, `pytest -q`, `git diff --check`, todas as tarefas marcadas ou justificadas em `specs/006-entregar-evidencias-publicas/tasks.md`; commit local final se autorizado; push adicional somente com nova autorização.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (T001–T002)**: sem dependências; bloqueiam tudo.
- **Foundational (T003–T004)**: depois do Setup; bloqueiam as histórias.
- **US1 (T005–T011)**: T005 → T006 → T007 → T008 → T009 → T010 → T011.
- **US2 (T012–T018)**: depende de T011 (links e PNG citados). T012 → T013 → T014 → T015 → T016 → T017 → T018.
- **US3 (T019–T023)**: depende de T018 (conteúdo final). T019 → T020 → T021 → T022 → T023.
- **Polish (T024–T025)**: depois de T022 (ou do bloqueio registrado em T020).

### User Story Dependencies

- **US1 (P1)**: MVP; entrega as evidências públicas.
- **US2 (P1)**: cita as evidências de US1 e reproduz o roteiro.
- **US3 (P2)**: publica o que US1/US2 produziram.

### Parallel Opportunities

- T003 (`docs/entrega-publica.md`) ∥ T004 (`tests/test_delivery.py`).
- Ações externas e edições do `README.md` nunca em paralelo.

## Parallel Example: Foundational

```bash
Task: "T003 Criar docs/entrega-publica.md com seções e formatos"
Task: "T004 Criar tests/test_delivery.py com helpers offline"
```

## Implementation Strategy

### MVP First (User Story 1)

1. Setup e Foundational.
2. Autorização → `share_dataset` único → conferência sem login → PNG.
3. **Parar e validar**: avaliador abre dataset, médias e traces sem login.

### Incremental Delivery

1. US1 → evidências públicas.
2. US2 → README final e reprodução.
3. US3 → integridade, autorização e publicação do fork.
4. Polish → estado final e pendências explícitas.

### Custo esperado

Uma avaliação de reprodução (≈ US$ 0,27, como `CIC-03`); acumulado ≈ US$ 1,03. `REP-006B`
com LLM só por pedido explícito.

---

## Rastreabilidade

| Requisito | Tarefas | Contrato / guia |
| --- | --- | --- |
| FR-001 | T006, T007, T008 | E02/E03 / W03/W04 |
| FR-002 | T009, T010, T011 | E04 / W05 |
| FR-003 | T005, T008, T009, T010 | E03/E04 / W04/W05 |
| FR-004 | T005, T006, T007 | E02 / W03 |
| FR-005 | T012, T013, T014, T016 | E05 / W06 |
| FR-006 | T012, T015 | E05 / W06 |
| FR-007 | T016, T017, T018 | E05/E06 / W07 |
| FR-008 | T020, T021, T022 | E08 / W09 |
| FR-009 | T001, T019 | E01/E07 / W01/W08 |
| FR-010 | T017, T018, T023 | E06/E09 / W07 |
| SC-001 | T008, T009, T022 | E03 |
| SC-002 | T010, T011 | E04 |
| SC-003 | T012, T014, T015, T016 | E05 |
| SC-004 | T017, T018, T023 | E06 |
| SC-005 | T019, T022 | E07/E08 |

## Conferência da geração — 2026-10-19

25 tarefas: Setup (2), Foundational (2), US1 (7), US2 (7), US3 (5), Polish (2). Um par
`[P]` (T003 ∥ T004). `.specify/extensions.yml` ausente: nenhum hook antes/depois. Nenhum
compartilhamento, push, chamada LLM ou edição de conteúdo nesta geração.

## Registro de execução

Pendente.
