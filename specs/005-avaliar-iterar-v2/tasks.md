---
description: "Tarefas da spec 005: avaliação íntegra e otimização guiada por evidências"
---

# Tasks: Avaliação íntegra e otimização guiada por evidências

**Input**: documentos em `specs/005-avaliar-iterar-v2/`.
**Data**: 2026-10-18 | **Branch Git**: `dev` | **Feature ativa**: 005.

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contrato C01–C10](contracts/avaliacao-v2.md),
[quickstart V01–V11](quickstart.md), [README](../../README.md) e
[constituição v1.0.0](../../.specify/memory/constitution.md).
Aceite da 004 e revisão `4278de75a2fca03a17cc1e3ab9d66d552c2c1aaebe543a085a34772637fa9595`
em [publicação da v2](../../docs/publicacao-v2.md) são pré-requisitos.

**Estado**: 35/35 tarefas concluídas em 2026-10-19. `CIC-01` aprovado; por decisão do autor, `CIC-02` (T024–T025) e `CIC-03` (T026) executados, `CIC-03` aprovado como final; T027–T028 não aplicáveis com justificativa; ver [registro de execução](#registro-de-execução).
Duas análises SDD realizadas. Achados C1, I1, I2, U1, D1, I3, P1, U2, A1, I4 e U3 da
primeira (ver [correção da análise](#correção-da-análise--2026-10-18)) e G1, U1, U2, I1,
I2, U3, U4, I3 e A1 da segunda (ver [segunda correção](#segunda-correção-da-análise--2026-10-18))
corrigidos nesta lista e nos artefatos.

**Commits locais**: autorizados pelo autor em 2026-10-18 para cada ciclo (v2, testes e
registros do ciclo) e para os incrementos desta lista. Push Git para o remoto não está
autorizado por esta lista.

**Tests**: incluídos. O plano prevê `tests/test_evaluation_audit.py` para os blocos
de auditoria; as histórias exigem detectar experimento incompleto (US1) e decisão
integral (US2). Escrever os casos antes dos blocos, observar falha pertinente ao bloco
ausente, depois implementar e reexecutar. Dublês não são evidência remota; notas
vêm somente de `python src/evaluate.py`.

**Organization**: US1 e US2 são P1; US1 vem primeiro porque a decisão só se aplica a
experimento completo. US3 (P2) depende da decisão de US2 sobre o primeiro ciclo.
Tarefas de execução real (chamadas LLM) aparecem apenas depois dos gates offline.

## Format: `[ID] [P?] [Story] Description`

- IDs sequenciais; cada tarefa tem checkbox e caminho exato.
- Rótulos de história somente nas fases das histórias.
- `[P]` marca três pares em arquivos diferentes. Não paralelizar edições em
  `docs/avaliacao-v2.md`, `tests/test_evaluation_audit.py` ou
  `prompts/bug_to_user_story_v2.yml` dentro do mesmo par.
- FR/SC são locais à 005; C01–C10 do contrato; V01–V11 do guia; D01–D11 da pesquisa.

## Path Conventions

Projeto único com `src/`, `tests/`, `prompts/`, `docs/`, `results/` e `README.md` na raiz.
Blocos executáveis ficam em `docs/avaliacao-v2.md` no formato `python - <<'PY' … PY`,
cada um com marcador único (`AVALIACAO_GATE`, `AVALIACAO_DATASET`, `AVALIACAO_AUDITORIA`),
como em `docs/preparacao.md`. Entradas dos blocos chegam por variáveis de ambiente
não secretas (`AVALIACAO_CICLO`, `AVALIACAO_CONDICAO` (padrão `COND-001`),
`AVALIACAO_HUB_COMMIT`, `AVALIACAO_V2_FILE_SHA256`, `AVALIACAO_V2_DEFINITION_SHA256`,
`AVALIACAO_DATASET_ID`, `AVALIACAO_DATASET`, `AVALIACAO_TESTES`, `AVALIACAO_DASHBOARD`,
`AVALIACAO_CUSTO_ACUMULADO_USD`, `AVALIACAO_LOG`, `AVALIACAO_EXIT_CODE`).
`AVALIACAO_DATASET_ID` e `AVALIACAO_DATASET` vêm da saída do bloco `AVALIACAO_DATASET`
executado no mesmo ciclo, sempre antes do gate.

Protegidos e somente leitura: `src/evaluate.py`, `src/metrics.py`, `src/utils.py`,
`datasets/bug_to_user_story.jsonl` (15 exemplos, 5/7/3), `prompts/bug_to_user_story_v1.yml`.
Não compartilhar dataset, publicar evidências públicas nem fazer push Git nesta lista.

## Phase 1: Setup — ambiente, integridade e ferramentas

**Purpose**: confirmar dependências concluídas e registrar baseline.

- [X] T001 Ativar `venv/`, conferir Python 3.10+ e executar `python -m pip check`; registrar versões de `langsmith`, `langchain-core` e `langchain-openai` (esperado 0.13.0 / 1.6.4 / 1.6.2) no registro de execução de `specs/005-avaliar-iterar-v2/tasks.md`, sem instalar ou alterar dependências.
- [X] T002 Executar V01 de `specs/005-avaliar-iterar-v2/quickstart.md`: hashes dos quatro protegidos contra `docs/integridade-inicial.json`, hash da v1 contra `docs/recuperacao-v1.md`, hashes de arquivo/definição da v2 contra `docs/publicacao-v2.md` (PUB-004-04: arquivo `49ffb35893ae86769d22b555b9b0017e1910e08c49373e89a1931f58ec06c46d`, definição `ab661782f912303d01a38d45d8a0f89074b84a1a5756fd6d6df7aa7f0489b89c`), `git rev-parse HEAD`, `git status` e HEAD remoto via `Client.get_prompt` igual a `4278de75a2fca03a17cc1e3ab9d66d552c2c1aaebe543a085a34772637fa9595` e público; registrar em `specs/005-avaliar-iterar-v2/tasks.md`.
- [X] T003 Consultar `langsmith --help`, `langsmith dataset --help`, `langsmith experiment --help` e `langsmith trace --help` (e subcomandos usados depois), registrando em `specs/005-avaliar-iterar-v2/tasks.md` quais leituras o CLI cobre; autenticação passada explicitamente, sem presumir leitura do `.env`.

---

## Phase 2: Foundational — registro e isolamento de testes

**Purpose**: estrutura comum aos três blocos e às três histórias.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [X] T004 [P] Criar `docs/avaliacao-v2.md` com: escopo e limites; rastreabilidade FR/SC → C/V; condição `COND-001` (provider `openai`, `llm_model=eval_model=gpt-4.1-2025-04-14`, temperatura 0, projeto `mba-ia-pull-evaluation-prompt`, dataset `mba-ia-pull-evaluation-prompt-eval`, workspace `15dd5852-a835-4163-826c-e78668fd2a9c`) numa seção de condições que também recebe, antes da execução, qualquer `COND-00N` declarada por isolamento (D03); formatos de registro de `RevisãoCandidata`, `AuditoriaDataset`, `Experimento` (estados `planejado`, `gate_ok`, `bloqueado`, `executado`, `falha_execução`, `auditado`, `incompleto`, `invalidado`, `reprovado`, `aprovado`, `substituído`), `CicloOtimização`, `EvidênciaTrace` e `RegistroCusto` conforme `specs/005-avaliar-iterar-v2/data-model.md`; seções vazias reservadas para os três blocos e para `CIC-01`…`CIC-05`.
- [X] T005 [P] Criar `tests/test_evaluation_audit.py` com fixture de isolamento no padrão de `tests/test_preparation_checks.py` (diretório temporário, `.env` fictício, `os.environ` substituído, bloqueio de `socket`); `subprocess.run` substituído por um falso do Git que responde somente a `git status --porcelain -- prompts/bug_to_user_story_v2.yml` e `git rev-parse HEAD` conforme o cenário e interrompe qualquer outro comando; `src/` no `sys.path` com o `utils` real importável (para que `import evaluate` resolva `check_env_vars`, `format_score` e `print_section_header`), mas `utils.get_llm`, `utils.get_eval_llm`, `langchain_openai.ChatOpenAI` e `langchain_google_genai.ChatGoogleGenerativeAI` substituídos por fronteiras que falham e registram a chamada; helper `execute_block(marker)` que extrai exatamente um bloco `python - <<'PY'` de `docs/avaliacao-v2.md`, e um cliente LangSmith falso configurável (datasets, exemplos, prompt/HEAD, projeto de experimento, runs raiz e de prompt, feedback) que registra chamadas de escrita.

**Checkpoint**: registro e infraestrutura de teste prontos; nenhuma chamada remota feita.

---

## Phase 3: User Story 1 — Obter um experimento completo e auditável (Priority: P1) 🎯 MVP

**Goal**: dataset idêntico conferido antes, primeiro experimento real da revisão publicada
e auditoria que comprova 15 respostas, 75 notas válidas e vínculo com a revisão.

**Independent Test**: executar `CIC-01` com a v2 publicada sem edição e auditar
respostas e feedbacks (V03–V07), sem depender de ciclos posteriores ou da 006.

### Tests for User Story 1

> Escrever primeiro; devem falhar porque os blocos ainda não existem.

- [X] T006 [US1] Em `tests/test_evaluation_audit.py`, testes do bloco `AVALIACAO_GATE` (C01): positivo com tudo íntegro; negativos para hash de protegido divergente, v1 divergente, hash da v2 diferente de `AVALIACAO_V2_*`, YAML v2 com alteração não commitada, HEAD ≠ `AVALIACAO_HUB_COMMIT`, prompt não público, variável exigida ausente ou em branco, tracing efetivo `False` (incluindo aliases `LANGSMITH_TRACING_V2`/`LANGCHAIN_TRACING_V2`), provider/modelo/projeto ≠ condição ativa, `tenant_id` do projeto ≠ workspace da condição, `AVALIACAO_CONDICAO` apontando para condição não declarada em `docs/avaliacao-v2.md` (`causa=condicao`), `AVALIACAO_DATASET_ID` ausente ou ≠ ID do dataset `{LANGSMITH_PROJECT}-eval` localizado por nome, `AVALIACAO_DATASET` ≠ `idêntico` (`causa=dataset`), `AVALIACAO_TESTES` diferente de `aprovado`, `AVALIACAO_DASHBOARD` diferente de `conferido`, `AVALIACAO_CUSTO_ACUMULADO_USD` > 4 (limite 4,00 aceito); positivo adicional com `AVALIACAO_CONDICAO=COND-002` declarada no registro e configuração igual a ela; cada negativo sai com código 1, estado `bloqueado` e `causa` específica (`custo` no gate de custo); nenhuma sentinela de segredo em stdout/stderr; zero chamadas LLM.
- [X] T007 [US1] Em `tests/test_evaluation_audit.py`, testes do bloco `AVALIACAO_DATASET` (C02, D01–D03): dataset ausente → `evaluate.create_evaluation_dataset` chamada exatamente uma vez e auditoria em seguida; presente e idêntico → nenhuma escrita; negativos com 14 exemplos, referência alterada, exemplo extra, duplicata e criação parcial → código 1, estado `divergente`, nenhuma chamada de exclusão/edição; distribuição 5/7/3 derivada do mapeamento local; saída com `dataset_id` e estado prontos para `AVALIACAO_DATASET_ID`/`AVALIACAO_DATASET`; `share_dataset` nunca chamado.
- [X] T008 [US1] Em `tests/test_evaluation_audit.py`, testes do bloco `AVALIACAO_AUDITORIA` (C04/C05, D04–D06): positivo com 15 runs e 75 notas válidas e log fixture completo (15 linhas por exemplo, cinco médias, média geral e linha `STATUS` coerentes com as notas, para continuar válido após C06/T019); negativos com URL sem `selectedSessions`, `reference_dataset_id` diferente de `AVALIACAO_DATASET_ID`, dataset relido sem reconstrução completa do `example_map`, 14 runs, `reference_example_id` repetido, run com erro, `outputs.answer` vazio, feedback ausente, feedback duplicado, nota `None`, `NaN`, `inf`, `-0.1` e `1.2`, comentários contendo `Erro na avaliação`, `Erro ao processar resposta` ou `Resposta vazia`, derivada inconsistente com `round((clarity+precision)/2, 4)` ou `round((f1_score+precision)/2, 4)`, HEAD depois ≠ antes, `lc_hub_commit_hash` divergente em um run, hash local da v2 alterado após a execução, hash de um protegido alterado após a execução; estados esperados `incompleto` ou `invalidado`; ausência total de `lc_hub_commit_hash` registra limitação sem invalidar se HEAD e hashes conferem; log sem URL com projeto parcial existente → `falha_execução`, projeto listado e nenhuma decisão; positivo emite `by_complexity` (5/7/3) e `lowest` corretos e soma tokens de geração e juízes, marcando ausentes como `estimado`.

### Implementation for User Story 1

- [X] T009 [US1] Escrever o bloco `AVALIACAO_GATE` em `docs/avaliacao-v2.md` conforme C01: carregar `.env` sem sobrescrever exportadas, limpar cache de env do SDK, conferir hashes, árvore Git da v2, variáveis exigidas por `src/evaluate.py`, tracing efetivo, condição ativa por `AVALIACAO_CONDICAO` (padrão `COND-001`; outra só se declarada na seção de condições), projeto e workspace (`tenant_id` de `Client.read_project`), dataset localizado por nome com ID igual a `AVALIACAO_DATASET_ID` e `AVALIACAO_DATASET=idêntico`, HEAD/publicidade por `Client.get_prompt`, `AVALIACAO_TESTES=aprovado` (C01.3 comprovado pela tarefa anterior de testes), `AVALIACAO_DASHBOARD=conferido` (inspeção registrada da revisão) e custo acumulado ≤ US$ 4; emitir JSON sanitizado com estado `gate_ok` ou `bloqueado` (com `causa`) e sair 0/1; nenhuma chamada LLM ou escrita remota.
- [X] T010 [US1] Escrever o bloco `AVALIACAO_DATASET` em `docs/avaliacao-v2.md` conforme C02: localizar por nome exato; se ausente, importar `evaluate` de `src/` e chamar `create_evaluation_dataset(client, dataset_name, "datasets/bug_to_user_story.jsonl")` uma vez; comparar multiconjunto canônico `json.dumps({"inputs":…, "outputs":…}, sort_keys=True, ensure_ascii=False)` remoto × local com multiplicidade; exigir 15; emitir `dataset_id`, `example_map` (`example_id → índice local, complexidade`) e estado `idêntico`/`divergente`, com as linhas `AVALIACAO_DATASET_ID=…` e `AVALIACAO_DATASET=…` para exportação; em divergência instruir D03 sem apagar nada.
- [X] T011 [US1] Escrever o bloco `AVALIACAO_AUDITORIA` em `docs/avaliacao-v2.md` conforme C04/C05: ler `AVALIACAO_LOG`, extrair URL e `selectedSessions`; ler o projeto do experimento e conferir `reference_dataset_id` contra `AVALIACAO_DATASET_ID`; reler esse dataset somente por leitura e reconstruir o `example_map` pela comparação canônica de C02; listar runs raiz e runs do template; listar feedback dos 15 runs; validar regras de D06; conferir HEAD e hashes da v2 e dos quatro protegidos depois; calcular por dificuldade (via `example_map` reconstruído) as médias `by_complexity` e as três menores notas por métrica base com comentário (`lowest`); somar tokens dos runs LLM da geração e das árvores dos runs do avaliador (via `source_run_id` do feedback ou projeto do avaliador), marcando como `estimado` o que não tiver contagem, e estimar custo a US$ 2/M entrada e US$ 8/M saída; emitir JSON com tabela por exemplo e estado. Sem URL no log, listar somente para registro projetos com `reference_dataset_id` do dataset auditado, prefixo `fabiocsm-bug_to_user_story_v2` e início posterior ao comando, sem avaliá-los, e emitir `falha_execução`.
- [X] T012 [US1] Executar `pytest tests/test_evaluation_audit.py -v` até T006–T008 passarem, depois `pytest -q` para regressão (base 732); registrar contagens e a falha pertinente observada antes dos blocos em `specs/005-avaliar-iterar-v2/tasks.md`.
- [X] T013 [US1] Executar V04: bloco `AVALIACAO_DATASET` real (criação única + auditoria); registrar `dataset_id`, contagem, igualdade e distribuição 5/7/3 em `docs/avaliacao-v2.md` e exportar `AVALIACAO_DATASET_ID`/`AVALIACAO_DATASET` emitidos. Divergência → registrar, declarar nova condição `COND-00N` com novo `LANGSMITH_PROJECT` na seção de condições de `docs/avaliacao-v2.md` (D03), exportar `AVALIACAO_CONDICAO=COND-00N` antes de qualquer LLM, executar o bootstrap opcional `AVALIACAO_PROJETO` e repetir T013.
- [X] T014 [US1] Executar V03: bloco `AVALIACAO_GATE` real para `CIC-01`, depois de T013, com `AVALIACAO_CONDICAO` (padrão `COND-001`), `AVALIACAO_DATASET_ID` e `AVALIACAO_DATASET` de T013, `AVALIACAO_HUB_COMMIT=4278de75a2fca03a17cc1e3ab9d66d552c2c1aaebe543a085a34772637fa9595`, `AVALIACAO_V2_FILE_SHA256=49ffb35893ae86769d22b555b9b0017e1910e08c49373e89a1931f58ec06c46d`, `AVALIACAO_V2_DEFINITION_SHA256=ab661782f912303d01a38d45d8a0f89074b84a1a5756fd6d6df7aa7f0489b89c`, `AVALIACAO_TESTES=aprovado` (T012), `AVALIACAO_DASHBOARD=conferido` (inspeção visual de 2026-10-18 registrada em `docs/publicacao-v2.md`) e `AVALIACAO_CUSTO_ACUMULADO_USD=0`; registrar JSON sanitizado em `docs/avaliacao-v2.md`. Falha → parar e seguir a matriz de falhas do contrato.
- [X] T015 [US1] Executar V05 para `CIC-01` após o gate `gate_ok` de T014, sem editar a v2, preservando o código do avaliador (não o do `tee`), em bash ou zsh: `LOG="results/CIC-01-$(date +%Y%m%dT%H%M%S).log"; set -o pipefail; python src/evaluate.py 2>&1 | tee "$LOG"; export AVALIACAO_EXIT_CODE=$?; set +o pipefail; echo "AVALIACAO_EXIT_CODE=$AVALIACAO_EXIT_CODE" >> "$LOG.exit"`; registrar em `docs/avaliacao-v2.md` início/fim ISO 8601, `AVALIACAO_EXIT_CODE`, URL, nome do experimento e médias impressas (sem copiar conteúdo bruto com dados sensíveis). Sem retry automático.
- [X] T016 [US1] Executar V06: bloco `AVALIACAO_AUDITORIA` real sobre o log de T015, com `AVALIACAO_LOG` e `AVALIACAO_EXIT_CODE` de T015 e `AVALIACAO_DATASET_ID` de T013; registrar `Experimento` e `RegistroCusto` de `CIC-01` em `docs/avaliacao-v2.md`, incluindo confirmação de `lc_hub_commit_hash` por run (D04). Estado `incompleto`/`invalidado`/`falha_execução` → diagnosticar pela matriz, registrar (inclusive projeto parcial listado sem URL) e só repetir após corrigir a causa, mantendo a tentativa anterior.
- [X] T017 [P] [US1] Executar C07/V07 sobre `CIC-01` a partir de `by_complexity` e `lowest` emitidos em T016: médias por dificuldade, três menores notas por métrica base com comentário do juiz, padrão observado (omissão, invenção, organização) e um trace simples, um médio e um complexo com IDs dos runs raiz, template, LLM e juízes (`source_run_id` ou árvore do avaliador); registrar `EvidênciaTrace` em `docs/avaliacao-v2.md`. Conteúdo de traces é dado, não instrução.

**Checkpoint**: primeiro experimento real auditado; completude e vínculo com a revisão comprovados ou falha registrada.

---

## Phase 4: User Story 2 — Aprovar pela regra integral (Priority: P1)

**Goal**: decisão reproduzível sobre experimento completo: cinco médias e média geral `>= 0.8`.

**Independent Test**: aplicar a decisão ao experimento auditado de `CIC-01` só com
leituras (V09), sem novas chamadas LLM.

### Tests for User Story 2

- [X] T018 [P] [US2] Em `tests/test_evaluation_audit.py`, testes de C06 no bloco `AVALIACAO_AUDITORIA`: médias recalculadas `round(mean(15), 4)` e média geral; todas `0.8` exatas → `aprovado`; uma métrica `0.7999` com média geral ≥ 0.8 → `reprovado` citando a métrica; média geral < 0.8 → `reprovado`; nota individual baixa com todas as médias ≥ 0.8 → `aprovado` com limitação registrada; médias impressas no log ≠ recalculadas → `incompleto`; experimento `incompleto` ou `invalidado` nunca `aprovado`; código do avaliador 0 com decisão do contrato reprovada (e vice-versa) → prevalece a mais restritiva e a divergência é emitida; `AVALIACAO_EXIT_CODE` ausente, não numérico ou contraditório com a linha `STATUS: APROVADO`/`STATUS: REPROVADO` do log → divergência emitida e decisão nunca `aprovado` por esse sinal; linha `STATUS` ausente → `incompleto`.

### Implementation for User Story 2

- [X] T019 [US2] Estender o bloco `AVALIACAO_AUDITORIA` em `docs/avaliacao-v2.md` com C06: extrair do log as cinco médias, a média geral e a linha `STATUS` impressas; ler o código do avaliador de `AVALIACAO_EXIT_CODE` (o log não o contém); recalcular a agregação de `src/evaluate.py`; emitir `means`, `overall`, `printed_means`, `printed_status`, `exit_code`, decisão do avaliador e decisão do contrato.
- [X] T020 [US2] Executar `pytest tests/test_evaluation_audit.py -v` e `pytest -q`; registrar contagens em `specs/005-avaliar-iterar-v2/tasks.md`.
- [X] T021 [US2] Reexecutar o bloco `AVALIACAO_AUDITORIA` somente leitura sobre o experimento de `CIC-01`, com o log e `AVALIACAO_EXIT_CODE` registrados em T015, e registrar a decisão em `docs/avaliacao-v2.md`. `aprovado` → registrar justificativa de aprovação antecipada (C09), marcar somente T024–T028 como não aplicáveis com justificativa e executar T022, T023, T029 e T030 sobre `CIC-01`; `reprovado` → identificar métricas abaixo do limiar como entrada de US3.

**Checkpoint**: decisão integral registrada para o primeiro experimento.

---

## Phase 5: User Story 3 — Melhorar a v2 com histórico comparável (Priority: P2)

**Goal**: ciclos `CIC-02`…`CIC-05` com problema, hipótese, alteração, revisão, experimento e conclusão, sob a mesma condição.

**Independent Test**: conferir em `docs/avaliacao-v2.md` a sequência de ciclos reais,
cada um com revisão publicada e experimento acessíveis e condição declarada (SC-003).

### Tests for User Story 3

- [X] T022 [US3] Em `tests/test_evaluation_audit.py`: teste documental (condição e custo já cobertos por T006/T009) que exige em cada seção `### CIC-0N` de `docs/avaliacao-v2.md` os campos de FR-005 (data, provedor, modelos, dataset, identificação local da v2, revisão publicada, ID e URL do experimento, cinco médias, média geral, completude, decisão) mais problema, hipótese, `RevisãoCandidata` com inspeção no dashboard e custo acumulado; seções marcadas como não aplicáveis exigem apenas justificativa.

### Implementation for User Story 3

- [X] T023 [US3] Ajustar o formato de registro de ciclo em `docs/avaliacao-v2.md` até o teste de T022 passar também para o registro existente de `CIC-01`; executar `pytest tests/test_evaluation_audit.py -v` e `pytest -q`; registrar contagens.
- [X] T024 [US3] `CIC-02` — preparação: registrar em `docs/avaliacao-v2.md` problema e hipótese ligados às métricas/comentários de `CIC-01` (D10: F1 → omissões; Precision → invenção/excesso; Clarity → organização); editar somente `prompts/bug_to_user_story_v2.yml` mantendo Few-shot próprio e Role Prompting, sem casos ou referências do dataset e sem instruções ao juiz; ajustar `tests/test_prompts.py` só se um contrato local mudar, com justificativa e sem enfraquecer os seis obrigatórios; executar `pytest tests/test_prompts.py -v` e `pytest -q`; executar `python src/push_prompts.py` (código 0, revisão conferida); conferir a nova revisão no dashboard do LangSmith sem login (badge Public, `fabiocsm/bug_to_user_story_v2`, revisão, tags/técnicas, System com persona/regras/exemplos e User `{bug_report}`), como na C07.5 da 004; registrar `RevisãoCandidata` (hashes, commit do Hub, data, inspeção) e fazer o commit local autorizado do ciclo (v2, testes e registro), sem push Git.
- [X] T025 [US3] `CIC-02` — avaliação: bloco `AVALIACAO_DATASET` (somente auditoria, `idêntico`) → bloco `AVALIACAO_GATE` de `docs/avaliacao-v2.md` com `AVALIACAO_DATASET_ID`/`AVALIACAO_DATASET` recém-emitidos, a nova revisão, seus hashes, `AVALIACAO_TESTES=aprovado`, `AVALIACAO_DASHBOARD=conferido` e o custo acumulado → comando de T015 com `CIC-02` no nome do log e `AVALIACAO_EXIT_CODE` preservado → bloco `AVALIACAO_AUDITORIA` (C04–C06) → análise C07 sem traces obrigatórios; registrar `Experimento`, custo, decisão e conclusão de `CIC-02` em `docs/avaliacao-v2.md`.
- [X] T026 [US3] `CIC-03` em `prompts/bug_to_user_story_v2.yml` e `docs/avaliacao-v2.md`: se `CIC-02` não aprovado e gate de custo aberto, repetir T024–T025 com hipótese baseada em `CIC-02`; senão registrar não aplicável com justificativa.
- [X] T027 [US3] `CIC-04` em `prompts/bug_to_user_story_v2.yml` e `docs/avaliacao-v2.md`: mesma regra de T026, com base em `CIC-03`.
- [X] T028 [US3] `CIC-05` em `prompts/bug_to_user_story_v2.yml` e `docs/avaliacao-v2.md`: mesma regra de T026, com base em `CIC-04`.
- [X] T029 [US3] Registrar a decisão de parada em `docs/avaliacao-v2.md` conforme C09: aprovação (ciclo, justificativa, sem ciclos para completar contagem); reprovação após `CIC-05` (diagnóstico, plano `CIC-06+`, 005 aberta, sem declarar sucesso); gate de custo (estado `bloqueado`, causa `custo`, e pedido de decisão ao autor). Repetições por falha de infraestrutura listadas com as demais execuções.
- [X] T030 [P] [US3] Montar em `docs/avaliacao-v2.md` a tabela comparativa de todos os ciclos e tentativas (condição, revisão, experimento, cinco médias, média geral, completude, decisão, custo) e o resumo das mudanças; marcar nova condição, se houver, antes de comparar; nenhuma linha removida.

**Checkpoint**: histórico completo e comparável; revisão aprovada ou pendência explícita.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: correspondência final, traces finais, integridade e entrega à 006.

- [X] T031 Verificar SC-005 em `docs/avaliacao-v2.md`: hashes do YAML local, HEAD do Hub e `hub_commit` do experimento aprovado iguais, e inspeção no dashboard da revisão final registrada (constituição III); qualquer edição da v2 posterior à aprovação reabre um ciclo completo (T024–T025) e marca o anterior como `substituído`.
- [X] T032 Se o experimento final não for `CIC-01`, repetir V07 sobre ele (um simples, um médio, um complexo) e registrar `EvidênciaTrace` em `docs/avaliacao-v2.md` (SC-004).
- [X] T033 [P] Atualizar `README.md` com link para `docs/avaliacao-v2.md` e os comandos de gate/dataset/avaliação/auditoria, preservando o enunciado; seções `Resultados Finais` e evidências públicas ficam para a 006.
- [X] T034 Executar V11: hashes dos protegidos e da v1, `git status`, `git diff --check`, busca de segredos nos arquivos alterados (`docs/avaliacao-v2.md`, `tests/test_evaluation_audit.py`, `prompts/bug_to_user_story_v2.yml`, `README.md`), `pytest -q`; confirmar que `results/` não é a única evidência; registrar em `specs/005-avaliar-iterar-v2/tasks.md`.
- [X] T035 Atualizar estado em `specs/005-avaliar-iterar-v2/plan.md`, `specs/README.md` e `plan/plano-implementacao.md`; registrar no fim de `docs/avaliacao-v2.md` a entrega à 006 (dataset ID, experimento final ID/URL, revisão, médias, traces), diferenciando o que foi verificado no LangSmith do que permanece pendente.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (T001–T003)**: sem dependências; T002 bloqueia toda execução real.
- **Foundational (T004–T005)**: depende do Setup; bloqueia as histórias.
- **US1 (T006–T017)**: depende da Foundational. Testes T006–T008 → blocos T009–T011 → T012 → execução real: dataset T013 → gate T014 → avaliação T015 → auditoria T016 → T017.
- **US2 (T018–T021)**: T018 pode começar após T011; T019 depende de T018 e T011; T021 depende de T016 e T020.
- **US3 (T022–T030)**: depende de T021. Com `reprovado`: T022 → T023 → T024 → T025 → T026 → T027 → T028 → T029 → T030. Com `aprovado`: T022 → T023 → T029 → T030, com T024–T028 registradas como não aplicáveis.
- **Polish (T031–T035)**: depende de T029 nos dois caminhos; T033 pode correr em paralelo a T030.

### User Story Dependencies

- **US1 (P1)**: independente; entrega o MVP (experimento completo e auditado).
- **US2 (P1)**: usa o bloco e o experimento de US1; sem novas chamadas LLM.
- **US3 (P2)**: usa gate, auditoria e decisão de US1/US2 em cada ciclo.

### Within Each User Story

- Testes escritos e com falha pertinente antes dos blocos.
- Blocos e testes offline aprovados antes de qualquer chamada LLM.
- Dataset (auditoria) → gate → avaliação → auditoria → decisão, sempre nessa ordem e em todo ciclo.
- Edição da v2 → testes → push conferido → commit → dataset → gate, em cada ciclo.

### Parallel Opportunities

- T004 (`docs/avaliacao-v2.md`) ∥ T005 (`tests/test_evaluation_audit.py`).
- T017 (registro em `docs/avaliacao-v2.md`) ∥ T018 (`tests/test_evaluation_audit.py`).
- T030 (`docs/avaliacao-v2.md`) ∥ T033 (`README.md`).
- Execuções reais nunca em paralelo (`max_concurrency=1`, revisão estável).

---

## Parallel Example: Foundational

```bash
Task: "T004 Criar docs/avaliacao-v2.md com condição, formatos e seções reservadas"
Task: "T005 Criar tests/test_evaluation_audit.py com isolamento e cliente falso"
```

## Parallel Example: User Story 1 → User Story 2

```bash
Task: "T017 Registrar análise C07 e três traces de CIC-01 em docs/avaliacao-v2.md"
Task: "T018 Escrever testes de C06 em tests/test_evaluation_audit.py"
```

## Parallel Example: User Story 3 → Polish

```bash
Task: "T030 Tabela comparativa de ciclos em docs/avaliacao-v2.md"
Task: "T033 Link e comandos no README.md"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Setup e Foundational.
2. Testes e blocos offline (T006–T012).
3. Dataset, gate, `CIC-01` e auditoria (T013–T017).
4. **Parar e validar**: 15 respostas, 75 notas válidas, vínculo com `4278de75…`.

### Incremental Delivery

1. US1 → experimento completo comprovado.
2. US2 → decisão integral sobre `CIC-01`, sem novo custo.
3. US3 → ciclos até aprovação, cinco ciclos ou gate de custo.
4. Polish → correspondência final, traces, integridade e entrega à 006.

### Custo esperado

≈ US$ 0,31 por experimento (D08); `CIC-01`…`CIC-05` ≈ US$ 1,6–2,5. Gate de decisão
em US$ 4 acumulados. Consumo real vem dos tokens registrados em T016/T025.

---

## Rastreabilidade

| Requisito | Tarefas | Contrato / guia |
| --- | --- | --- |
| FR-001 | T007, T010, T013, T025 | C01.6/C02 / V04 |
| FR-002 | T002, T006, T009, T014, T015, T016 | C01/C03/C04 / V03/V05/V06 |
| FR-003 | T008, T011, T016 | C05 / V06 |
| FR-004 | T018, T019, T021 | C06 / V09 |
| FR-005 | T004, T016, T022, T025, T030 | Modelo / V06/V08 |
| FR-006 | T017, T032 | C07 / V07 |
| FR-007 | T024, T026–T028 | C08 / V08 |
| FR-008 | T006, T009, T013, T022, T023, T030 | C01.5/C09/C10 / V08/V10 |
| FR-009 | T021, T026–T029 | C09 / V10 |
| FR-010 | T024, T031 | C08/C09 / V10/V11 |
| SC-001 | T016 | C05 |
| SC-002 | T021, T025, T029 | C06 |
| SC-003 | T022, T029, T030 | C08/C09 |
| SC-004 | T017, T032 | C07 |
| SC-005 | T031 | C04 |
| Integridade/sigilo | T002, T006, T034 | C01/C10 / V01/V11 |

---

## Notes

- `[P]` = arquivos diferentes, sem dependência pendente.
- Toda execução real registrada, inclusive falhas e repetições; nada é apagado.
- Nunca alterar protegidos, dados, juízes, limiar ou concorrência; nunca copiar referências.
- Estados finais distinguem implementação concluída de resultado verificado no LangSmith.

## Conferência da geração — 2026-10-18

35 tarefas: Setup (3), Foundational (2), US1 (12), US2 (4), US3 (9), Polish (5).
Três pares `[P]` em arquivos distintos. `.specify/extensions.yml` ausente: nenhum hook.
Nenhum código, YAML, dataset ou experimento criado nesta geração.

## Correção da análise — 2026-10-18

Achados de `$speckit-analyze` corrigidos antes da implementação, sem mudar requisitos:

| ID | Severidade | Correção |
| --- | --- | --- |
| C1 | CRITICAL | Constituição III: inspeção no dashboard de cada nova revisão (T024) e da final (T031); gate exige `AVALIACAO_DASHBOARD=conferido` (T006/T009) |
| I1 | HIGH | Código do avaliador preservado com `pipefail` em `AVALIACAO_EXIT_CODE` (T015/T016/T021/T025); T018/T019 usam esse valor e a linha `STATUS`, nunca o log como fonte do código |
| I2 | MEDIUM | `by_complexity` e `lowest` movidos para T011/T008; T017 os consome; T018 continua `[P]` |
| U1 | MEDIUM | T005 define falso do Git e `utils` real com fábricas LLM bloqueadas, permitindo `import evaluate` |
| D1 | MEDIUM | Condição e custo concentrados em T006/T009; T022/T023 ficam com o teste documental dos ciclos |
| I3 | MEDIUM | `pausa` substituído por `bloqueado` com `causa=custo` |
| P1 | MEDIUM | Commits locais por ciclo autorizados pelo autor; push Git não autorizado |
| U2 | LOW | Experimento parcial sem URL listado para registro, com `falha_execução` (T008/T011/T016) |
| A1 | LOW | Hashes completos em T002/T013 (gate em T014 após a segunda correção) |
| I4 | LOW | C01.3 comprovado pela tarefa de testes e informado ao gate por `AVALIACAO_TESTES` |
| U3 | LOW | Tokens de geração e juízes somados; ausentes marcados como `estimado` |

Contagem inalterada: 35 tarefas e mesmas fases; T017 recebeu `[P]` explícito, completando os três pares declarados.

## Segunda correção da análise — 2026-10-18

Achados da segunda execução de `/speckit-analyze` corrigidos antes da implementação,
sem mudar requisitos:

| ID | Severidade | Correção |
| --- | --- | --- |
| G1 | HIGH | C01.6 implementado e testado: gate confere workspace (`tenant_id`) e dataset (`AVALIACAO_DATASET_ID`, `AVALIACAO_DATASET=idêntico`); a auditoria do dataset precede o gate em todo ciclo (T013 ↔ T014 trocadas; T025 inclui o bloco de dataset) |
| U1 | MEDIUM | `AVALIACAO_DATASET_ID`/`AVALIACAO_DATASET` definidos; a auditoria relê o dataset e reconstrói `example_map` (C04.4, T008/T011/T016) |
| U2 | MEDIUM | `AVALIACAO_CONDICAO` com condição declarada em `docs/avaliacao-v2.md` antes da execução (C01.5, T004/T006/T009/T013) |
| I1 | MEDIUM | Aprovação antecipada executa T022, T023, T029 e T030; só T024–T028 ficam não aplicáveis; dependências alinhadas |
| I2 | LOW | Estado `auditado` incluído em T004 |
| U3 | LOW | Negativo com protegido alterado após a execução (T008) e conferência em T011 |
| U4 | LOW | Repetição por falha de infraestrutura limitada a uma; nova falha → `falha_execução` final e decisão do autor (C09 e matriz) |
| I3 | LOW | Log fixture positivo de T008 inclui médias e linha `STATUS` coerentes |
| A1 | LOW | Faixa de custo do plano corrigida para 3–5 ciclos |

Contagem inalterada: 35 tarefas e mesmas fases; T013 e T014 trocaram de conteúdo para
seguir a ordem dataset → gate.

## Registro de execução

### Setup — 2026-10-18

- **T001**: `venv/` com CPython 3.11.14; `python -m pip check` → `No broken requirements found.`
  Versões instaladas `langsmith` 0.13.0, `langchain-core` 1.6.4, `langchain-openai` 1.6.2,
  iguais às esperadas. Nenhuma instalação ou alteração de dependência.
- **T002 (V01)**: SHA-256 de `src/evaluate.py` `fba51aa7…3b57`, `src/metrics.py`
  `aee4e470…1ead`, `src/utils.py` `7a3bcef8…cdf5` e `datasets/bug_to_user_story.jsonl`
  `4b1ef15e…f60b` iguais a `docs/integridade-inicial.json`; v1 `2cddcf8f…0d70` igual a
  `docs/recuperacao-v1.md`; v2 arquivo `49ffb358…c46d` e definição `ab661782…b89c` iguais
  à PUB-004-04. `git rev-parse HEAD` = `60ca942cc1c624d11beb48924df03cf221e6301d`,
  `git status --porcelain` vazio. `Client.get_prompt("fabiocsm/bug_to_user_story_v2")`:
  `last_commit_hash=4278de75a2fca03a17cc1e3ab9d66d552c2c1aaebe543a085a34772637fa9595`,
  `is_public=true`, 1 commit. Leitura extra: nenhum dataset
  `mba-ia-pull-evaluation-prompt-eval`; projeto `10e3f705-af88-4cee-9d79-4a9fdb4a959f`
  no tenant `15dd5852-a835-4163-826c-e78668fd2a9c`; condição `COND-001` presente no `.env`
  (valores secretos não impressos).
- **T003**: LangSmith CLI 0.3.3 (commit 31ddadd). Ajuda consultada: `langsmith --help`,
  `dataset --help` (create, delete, export, get, list, upload), `experiment --help`
  (get, list), `trace --help` (export, get, list, messages, setup, stats) e
  `experiment get --help`. Leituras cobertas pelo CLI: lista/detalhe de datasets e
  experimentos, árvore de traces e estatísticas de tokens. A auditoria usa o SDK
  (`list_runs`, `list_feedback`, `read_project`) por precisar de `reference_example_id`,
  metadata do template e `feedback_source`; o CLI fica como conferência complementar,
  com `LANGSMITH_API_KEY`/`--workspace` passados explicitamente. Nenhuma escrita.

### Foundational e US1 offline — 2026-10-18

- **T004**: `docs/avaliacao-v2.md` criado com escopo, rastreabilidade, `COND-001` em bloco
  `json condicao` (lido pelo gate), formatos de registro e seções reservadas.
- **T005**: `tests/test_evaluation_audit.py` com cópias temporárias dos protegidos, `.env`
  fictício com sentinelas, `os.environ` substituído, `socket` bloqueado, Git falso restrito
  a `status --porcelain -- v2` e `rev-parse HEAD`, `utils` real com `get_llm`/`get_eval_llm`,
  `ChatOpenAI` e `ChatGoogleGenerativeAI` bloqueados, e `FakeClient` que registra escritas.
- **T006–T008**: 68 casos (gate 33, dataset 7, auditoria 28). Antes dos blocos: **68 falharam**,
  todos por `ValueError: Expected exactly one documented evaluation block` (falha pertinente).
- **T009–T011**: blocos `AVALIACAO_DATASET`, `AVALIACAO_GATE` e `AVALIACAO_AUDITORIA` escritos.
  Duas correções de teste durante T012, sem alterar asserções: seleção do bloco pelo cabeçalho
  `# MARCADOR — ` (o nome `AVALIACAO_DATASET` aparece nos três blocos) e escrita do `.env`
  fictício depois de importar `utils`, cujo `load_dotenv` de módulo pré-carregava as variáveis
  e mascarava os casos de variável ausente.
- **T012**: `pytest tests/test_evaluation_audit.py -v` → **68 passed**; `pytest -q` →
  **800 passed** (732 da base + 68 novos), zero skip/xfail.

### US2 offline — 2026-10-18

- **T018**: 16 casos de C06 (médias recalculadas, limiar exato, métrica 0.7999 com média
  geral ≥ 0.8, média geral < 0.8, nota individual baixa, médias impressas divergentes,
  incompleto/invalidado, código 0/1 contraditório, código ausente/vazio/não numérico/2,
  `STATUS` contraditório ou ausente). Antes da extensão: **16 falharam** por ausência dos
  campos de decisão (`KeyError: 'decisao'`, `'decisao_contrato'`, `'printed_means'`,
  `'printed_status'`) ou código de saída 0 onde se esperava 1; os 68 anteriores passaram.
- **T019**: C06 acrescentado ao bloco `AVALIACAO_AUDITORIA`.
- **T020**: `pytest tests/test_evaluation_audit.py -v` → **84 passed**; `pytest -q` →
  **816 passed**, zero skip/xfail.

### US1/US2 real — 2026-10-18/19

- **T013 (V04)**: 2026-10-18T23:56:18-03:00, bloco `AVALIACAO_DATASET` código 0. Dataset
  ausente criado uma vez pela função fornecida: `8c78638d-37a5-4175-9984-8db0e3473228`,
  15 exemplos, `matches_local=true`, 5/7/3, `idêntico`. Sem divergência; `COND-001` mantida.
- **T014 (V03)**: 2026-10-18T23:56:29-03:00, bloco `AVALIACAO_GATE` código 0, `gate_ok`,
  HEAD antes `4278de75…9595`, workspace e dataset conferidos, custo acumulado 0.
- **T015 (V05)**: `python src/evaluate.py` de 02:56:38 a 02:57:54 UTC (2026-10-19), com
  `pipefail`; `AVALIACAO_EXIT_CODE=0`; `STATUS: APROVADO`; experimento
  `fabiocsm-bug_to_user_story_v2-31a99eea` (`86196746-1c83-42cc-868b-6b57f977f19b`).
  Log local `results/CIC-01-20261018T235638.log` (ignorado). Sem retry.
- **T016 (V06)**: 2026-10-18T23:58:27-03:00, bloco `AVALIACAO_AUDITORIA` código 0: 15 runs,
  75 notas válidas, HEAD/hashes estáveis, `lc_hub_commit_hash` confirmado nos 15 runs,
  médias recalculadas iguais às impressas. Tokens 70.664 entrada / 10.131 saída, nenhum
  estimado; US$ 0,222376.
- **T017 (V07)**: `by_complexity`, três menores por métrica com comentários e três traces
  (#1 simple, #12 medium, #14 complex) com IDs de raiz, template, LLM, run do avaliador e
  três LLMs de juiz registrados em `docs/avaliacao-v2.md`.
- **T021 (V09)**: 2026-10-19T00:00:28-03:00, reexecução somente leitura idêntica; decisão
  `aprovado`, sem divergência → aprovação antecipada (C09).

### US3 e Polish — 2026-10-19

- **T022**: teste documental `test_cycle_records_have_every_required_field`; antes do ajuste,
  **falhou** em `CIC-01` por campos ausentes.
- **T023**: registro de `CIC-01` reformatado com os 14 campos; o teste passou a ler o bullet
  inteiro (incluindo linhas quebradas). `pytest tests/test_evaluation_audit.py -v` →
  **85 passed**; `pytest -q` → **817 passed**.
- **T024–T028**: **não aplicáveis** — `CIC-01` aprovado; C09/FR-009 proíbem ciclos só para
  completar a contagem e C08/FR-007 exigem problema observado. Seções `CIC-02`…`CIC-05`
  registram a justificativa. Nenhuma edição da v2, push ou experimento adicional.
- **T029**: decisão de parada registrada (aprovação antecipada, 1 ciclo executado, gate de
  custo não acionado, limitações e risco de oscilação).
- **T030**: tabela comparativa com `CIC-01` e `CIC-02–05` não aplicáveis; condição única.
- **T031**: SC-005 conferido: YAML local, HEAD e `lc_hub_commit_hash` do experimento são a
  mesma revisão; inspeção sem login repetida em 2026-10-19 no navegador integrado (Log in,
  Public, 1 commit `4278de75`, cinco tags, persona, exemplos, `{bug_report}`).
- **T032**: não aplicável — o experimento final é `CIC-01`, cujos três traces já constam.
- **T033**: README com a subseção “Avaliação e iterações — spec 005” (ordem dos blocos,
  comando com `pipefail`, testes offline) e estado da 005 em `Resultados Finais`, sem
  publicar evidências; enunciado preservado.
- **T034 (V11)**: hashes dos quatro protegidos, v1 e v2 inalterados; `git diff --check`
  aprovado; nenhum valor de credencial do `.env` nem padrão de chave nos cinco arquivos
  alterados; `pytest -q` 817 e `pytest tests/test_prompts.py -q` 466 aprovados; fatos
  sanitizados em `docs/avaliacao-v2.md`, `results/` não é a única evidência.
- **T035**: estado atualizado em `plan.md`, `specs/README.md` e `plan/plano-implementacao.md`;
  entrega à 006 registrada em `docs/avaliacao-v2.md`. Verificado no LangSmith: dataset,
  experimento, notas, vínculo e traces (workspace do autor). Pendente (006): acesso público
  ao dataset/experimentos, screenshots, seções finais do README e push Git.

`.specify/extensions.yml` ausente: nenhum hook antes ou depois da implementação.

### Reabertura por decisão do autor — CIC-02, 2026-10-19

Pedido do autor após o aceite: “F1 at 0.8057 is too tight. Open CIC-02 with an F1/omission
hypothesis and run a full cycle.” T024/T025 deixaram de ser não aplicáveis e foram executadas;
T029–T035 foram refeitas sobre o novo experimento final.

- **T024**: problema/hipótese registrados às 00:47:45-03:00, antes da edição (F1 → omissões,
  D10). Edição só da v2 (critérios Dado/Quando/Então com resultados decorrentes, critérios
  técnicos, 3–5 critérios em bug simples, dúvidas só bloqueantes; Exemplos 1 e 3). Testes:
  `tests/test_prompts.py` 466 e suíte 817 aprovados (o teste documental foi ajustado para
  aceitar ciclo **Em andamento** apenas com a decisão de parada reaberta). Push 00:48:49-03:00
  código 0, `publication=confirmada`, revisão `25b881d1…5e15`; inspeção sem login no navegador
  integrado; commit local `c40f511`.
- **T025**: dataset `idêntico` (leitura) → gate `gate_ok` (custo 0.222376) → avaliação
  03:49:37–03:50:50 UTC, `AVALIACAO_EXIT_CODE=0` → auditoria `aprovado`: experimento
  `c7d175e1-0f37-4afe-9b2a-88e061b01666`, 15 runs, 75 notas válidas, vínculo confirmado,
  médias 0.8837/0.8738/0.8416/0.8613/0.9060, média geral 0.8733, US$ 0,262344.
- **T026–T028**: não aplicáveis — `CIC-02` aprovado; C09 proíbe ciclos só para completar a contagem.
- **T029/T030**: decisão de parada (aprovação em `CIC-02`, 2 ciclos, acumulado US$ 0,484720) e
  tabela comparativa com as duas linhas; `CIC-01` marcado `substituído` (FR-010).
- **T031/T032**: SC-005 conferido para `25b881d1`; três traces de `CIC-02` (#1 simple, #10
  medium, #15 complex) registrados, com a limitação do número “1 segundo” inventado em #10.
- **T033–T035**: README (citação do Exemplo 1 e resultados), índices e `plan.md` atualizados;
  verificações finais abaixo.
- **V11 após CIC-02**: hashes dos quatro protegidos e da v1 inalterados; v2 `5222d484…7857`
  igual à revisão avaliada; `git diff --check` aprovado; nenhum valor de credencial ou padrão
  de chave nos arquivos alterados; links locais resolvidos; `pytest -q` → **817 passed**.

### Reabertura por decisão do autor — CIC-03, 2026-10-19

Pedido do autor: “Open CIC-03 to stop invented thresholds like the 1-second one in trace
#10, and run a full cycle.” T026 deixou de ser não aplicável; T029–T035 refeitas.

- **T026**: varredura das 30 respostas anteriores por valores ausentes do relato (#10 “1
  segundo” nos dois ciclos; #8 “ex: 403 ou 401” em `CIC-02`); problema/hipótese registrados
  às 01:11:45-03:00. Edição só da v2: regra **Valores** e demonstração no Exemplo 3. Testes
  466/817; push 01:12:15-03:00 código 0, `publication=confirmada`, revisão `36a96c05…696f`;
  inspeção sem login; commit local `9386438`. Dataset `idêntico` → gate `gate_ok` (custo
  0.484720) → avaliação 04:13:00–04:14:18 UTC, código 0 → auditoria `aprovado`: experimento
  `d864cfbb-6ab9-4901-ab06-62f68ccd96fc`, 15/75, vínculo confirmado, médias
  0.8773/0.8754/0.8474/0.8513/0.9033, média geral 0.8709, US$ 0,270298. Nova varredura:
  #10 corrigido, #8 limítrofe (opções numa dúvida), nova meta inventada em #14 (CPU 80%) —
  hipótese parcialmente confirmada.
- **T027–T028**: não aplicáveis — `CIC-03` aprovado.
- **T029–T032**: parada (3 ciclos, acumulado US$ 0,755018), comparação com três linhas e
  contagem de invenções, `CIC-02` `substituído`, SC-005 para `36a96c05`, traces #1/#10/#14.
- **T033–T035**: README (Exemplo 3 e resultados), índices e `plan.md` atualizados.
- **V11 após CIC-03**: protegidos e v1 inalterados; v2 `692df6ae…8974` igual à revisão
  avaliada; `git diff --check` aprovado; nenhum segredo nos arquivos alterados; links locais
  resolvidos; `pytest -q` → **817 passed**.

### Revisão dos commits — 2026-10-19

Escopo solicitado: commits da 005 contra `main`, uma iteração de `review-loop`, com
commit local das correções após os gates. Revisão por três subagentes, com triagem
e conferência do orquestrador. Os resultados de CIC-01–03 são históricos; esta revisão
não executa novos experimentos nem altera o prompt avaliado.

- [X] T036 Corrigir R1-1 (C10): suprimir a saída bruta do helper de criação em
  `docs/avaliacao-v2.md`, com regressão de sentinelas em `tests/test_evaluation_audit.py`.
- [X] T037 Corrigir R1-2 (C01.4): bloquear handle divergente antes das consultas do
  gate e da auditoria, com testes negativos nos mesmos arquivos.
- [X] T038 Corrigir R1-3 (D03/C01.6): viabilizar a inicialização explícita do projeto
  isolado antes do gate somente leitura, atualizar o roteiro/contrato/pesquisa e testar
  projeto inexistente com um dublê fiel ao SDK.
- [X] T039 Corrigir R1-4 (FR-008/RegistroCusto/C09): registrar e usar tarifas por papel
  da condição ativa, rejeitar configuração de preço ausente/inválida e testar custo
  de condição alternativa e seu efeito no gate.
- [X] T040 Revisar as correções, executar a suíte completa offline, conferir integridade,
  sintaxe, links e `git diff --check main <árvore>`, registrar evidências da revisão
  e criar o commit local autorizado sobre a mesma árvore validada.

Resultado da revisão: R1-1–R1-4 corrigidos; propagação documental H1-1 resolvida;
revisão adicional das correções sem novos achados. Suíte completa: **855 aprovados**
(baseline 817); testes da auditoria: 123. Sintaxe, integridade dos protegidos/v1/v2,
dataset 15/5/7/3, links locais, sigilo e diff-check contra `main` aprovados. Evidências
e retornos literais dos fixers no [relatório da revisão](../../docs/revisao-spec005.md).
Nenhum experimento ou chamada LLM nova; nenhuma publicação ou push Git nesta revisão.
