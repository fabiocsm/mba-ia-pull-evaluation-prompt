---
description: "Tarefas da spec 001: preparação reproduzível e integridade dos experimentos"
---

# Tasks: Preparação reproduzível dos experimentos

**Input**: artefatos em `specs/001-preparar-experimentos/`.

**Prerequisites**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/preparacao.md](contracts/preparacao.md) e
[quickstart.md](quickstart.md), subordinados ao [README](../../README.md), à
[constituição](../../.specify/memory/constitution.md) e à Fase 1 do
[plano mestre](../../plan/plano-implementacao.md).

**Estado**: 28 tarefas planejadas, nenhuma executada por este comando. Branch real
`dev`; a feature é selecionada por `SPECIFY_FEATURE_DIRECTORY`, sem criar branch.

**Tests**: a spec pede verificações de execução e critérios de aceitação, não uma
nova suíte ou TDD. As tarefas incluem essas validações e os cenários negativos locais
do quickstart; não criam testes de produção adicionais. Os seis testes obrigatórios
de `tests/test_prompts.py` continuam na spec 003.

**Organization**: fases por história, mantendo US1 e US2 em P1 e US3 em P2.
Baseline e ambiente compartilhados antecedem as histórias. Este documento encerra
a geração de tarefas; a análise SDD deve preceder sua implementação.

## Format: `[ID] [P?] [Story] Description`

- `[P]`: tarefa apta a execução paralela com a outra indicada na mesma fase, depois
  dos pré-requisitos, em arquivos de saída distintos.
- `[US1]`, `[US2]`, `[US3]`: história correspondente na spec.
- Caminhos são relativos à raiz. Caminhos de arquivos protegidos em tarefas indicam
  leitura/comparação; não autorização para modificá-los.
- As tarefas de atualização do mesmo documento devem executar em sequência.
- Marcar conclusão somente após obter o resultado exigido. Tentativa falha deve
  ser registrada, sem marcar como concluída a comprovação que permaneceu pendente.

## Phase 1: Setup — registros e captura inicial

**Purpose**: criar os destinos documentais e preservar a referência inicial antes
de instalação, configuração, chamadas remotas ou alteração de arquivos do desafio.

- [ ] T001 Criar a estrutura de `docs/preparacao.md` com identificação da preparação, links para spec/manifesto, seções de ambiente, configuração, verificações, condição, custo e conclusão; aplicar as regras “Datas usam ISO 8601 com fuso” e “caminhos de artefatos são relativos ao repositório”, reservando credenciais a “Somente nome, presença e resultado de validade; nunca valor, prefixo, hash ou comprimento” (`data-model.md`).
- [ ] T002 Capturar em `docs/integridade-inicial.json` a baseline anterior a instalação/configuração: `schema_version` igual a `1`, `created_at` como “Momento de coleta”, `git_commit`/`git_branch` como “Commit completo e branch real”, `git_status` como “Estado sanitizado inicial; explicitar divergências dos protegidos”; registrar SHA-256 dos bytes de `src/evaluate.py`, `src/metrics.py`, `src/utils.py` e `datasets/bug_to_user_story.jsonl`, mantendo a regra “Exatamente os quatro caminhos protegidos, cada um com SHA-256 dos bytes e correspondência com origem”, cuja comparação será preenchida em T003.

**Checkpoint**: referência inicial capturada sem apagar mudanças locais existentes.
As seções ainda não verificadas devem estar explicitamente pendentes, sem valores
inventados. O manifesto será enriquecido na US2, conservando os dados iniciais.

## Phase 2: Foundational — pré-requisitos compartilhados

**Purpose**: confirmar integridade de origem e ambiente que bloqueiam as operações
das histórias. Depende de T001–T002; terminar antes de executar as histórias.

- [ ] T003 Comparar os quatro arquivos protegidos da baseline com uma revisão identificada de `devfullcycle/mba-ia-pull-evaluation-prompt` e preencher `upstream` em `docs/integridade-inicial.json` com “URL pública do repositório base, revisão completa usada e resultado da comparação”; guardar a revisão exata e divergências, pois “Baseline divergente da origem não recebe aprovação”; resolver conflito antes de instalação/chamadas dependentes, sem editar protegidos ou substituir a captura inicial (FR-006).
- [ ] T004 Selecionar Python 3.10+ compatível, preferindo 3.11, criar e ativar `venv/` antes de instalar os pins de `requirements.txt`, executar `python -m pip check` e registrar em `docs/preparacao.md` os comandos, resultados, Python/pip/SO e eventuais impedimentos; não instalar globalmente nem trocar pins para contornar erro (FR-008).
- [ ] T005 [P] Conferir imports de ambos os providers e demais dependências, inspecionar `Client.read_project`, `get_prompt`, `pull_prompt`, `pull_prompt_commit`, `push_prompt` e montagem System/User com `ChatPromptTemplate`, consultar `langsmith --help` e ajuda de cada subcomando utilizado e guardar em `docs/preparacao.md` versões, contratos de pull público, serialização, push/metadados/revisão e limites da prova, sem recuperar/publicar prompt nem inventar interfaces ausentes (FR-008).
- [ ] T006 [P] Gerar e revisar `docs/dependencias-preparacao.txt` após T004, respeitando “Versões efetivamente instaladas após sucesso de `pip check`, em linhas `pacote==versão`” e “não incluir URLs privadas, credenciais, caminhos pessoais ou configuração de índices autenticados”; incluir as versões transitivas resolvidas, sem alterar `requirements.txt` (FR-008).

**Checkpoint**: T003 e T004 comprovadas, T005 e T006 concluídas. Falha de instalação
ou divergência dos materiais permanece impedimento, com causa/ação registradas.
Não executar etapas que dependam desse resultado enquanto não resolvido.

## Phase 3: User Story 1 — Confirmar prontidão da execução (Priority: P1) — MVP

**Goal**: comprovar configuração, identidade, acesso aos dois papéis de modelo e
tracing; distinguir operações prontas, pendentes e impedidas.

**Independent Test**: conferir o relatório e suas evidências sem pull, push, v2 ou
experimento completo. Cada pré-requisito tem estado e evidência; os dois papéis têm
resposta real com temperatura zero e trace correto. Falha impede a operação afetada,
com causa/ação, sem expor chave (SC-001/SC-002).

### Implementation and validation

- [ ] T007 [US1] Reconsultar documentação oficial de disponibilidade, parâmetros e preços para escolher os dois modelos antes da validação da configuração, considerando os candidatos e a depreciação descritos em `specs/001-preparar-experimentos/research.md`; guardar em `docs/preparacao.md` URLs/data, modelos explícitos, justificativa e compatibilidade documentada com `temperature=0`; esta pesquisa não exige credenciais ou modelos previamente preenchidos, e um candidato inacessível/desligado exige alternativa compatível com `src/utils.py`, sem alterar o helper (FR-003/FR-004).
- [ ] T008 [US1] Configurar localmente os valores não secretos escolhidos em T007 e carregar `.env` com dotenv preservando a precedência do ambiente e as credenciais existentes; validar e registrar em `docs/preparacao.md` presença de `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `USERNAME_LANGSMITH_HUB=fabiocsm`, `LANGSMITH_TRACING=true`, `LLM_PROVIDER=openai`, `LLM_MODEL` e `EVAL_MODEL` explicitamente iguais às escolhas e `OPENAI_API_KEY`; não sobrescrever o arquivo com o template nem exibir a chave, e preservar `google` como alternativa sem exigir sua chave nesta condição; para verificações aplicar `id` “Único na execução, ligado a FR/SC e operação dependente”, `estado` “`pendente`, `pronto` ou `impedido`”, `verificado_em` “Data da tentativa, ausente somente se ainda não tentada”, `evidencia` “Comando/método, resultado resumido e referência versionada ou URL sanitizada” e `causa`/`proxima_acao` “Obrigatórias em falha; pendência deve indicar o que falta verificar” (FR-001/FR-004/FR-005).
- [ ] T009 [US1] Comprovar identidade autenticada, handle `fabiocsm`, workspace e endpoint corretos via CLI/interface e consultar o projeto por `Client.read_project(project_name=...)`, guardando nome/ID/tenant e resultado sanitizado em `docs/preparacao.md`; se usar CLI, consultar ajuda e passar ambiente carregado por dotenv em subprocesso, sem tokens em argumentos; concluir esta tarefa com o contexto autenticado comprovado e a consulta documentada, permitindo somente a ausência confirmada do projeto ficar `pendente` até T013, sem bloquear as duas chamadas mínimas; autenticação inválida, acesso negado, workspace ambíguo ou projeto existente em contexto divergente impedem o avanço, e leitura pública não comprova posse do handle ou escrita (FR-002/FR-005).
- [ ] T010 [US1] Registrar em `docs/preparacao.md` a condição experimental com “`id`, data de definição e motivo da eventual substituição”, `provider` “`openai` inicialmente; `google` é a alternativa existente”, `llm_model`/`eval_model` “valores explícitos, preferencialmente snapshots”, `temperature` “exatamente `0`, para ambos os papéis”, fontes/data/desligamento, workspace/projeto esperados e constatados e nome futuro “`{LANGSMITH_PROJECT}-eval`”; se T009 confirmou projeto ausente, registrar seu nome esperado e ID ainda não constatado, sem inventar valor; vincular manifesto e hash do inventário de dependências, criar nova condição ao trocar provedor/modelo e retornar verificações afetadas a `pendente` preservando histórico (FR-003/FR-004/FR-005).
- [ ] T011 [US1] Executar a chamada mínima de geração do quickstart com mensagens System/User sintéticas e `utils.get_llm(temperature=0)` de `src/utils.py`, somente após T007–T010; guardar em `docs/preparacao.md` “data, modelo solicitado/retornado quando disponível, sucesso, tokens reportados, trace e diagnóstico de falha sanitizado”, exigindo resposta não vazia e registrando consumo/tentativas sem avaliar o dataset (FR-003/FR-004).
- [ ] T012 [US1] Executar a chamada mínima do papel de avaliação com `utils.get_eval_llm(temperature=0)` de `src/utils.py` e mensagens System/User curtas, mesmo se o modelo coincidir com o gerador; registrar em `docs/preparacao.md` os mesmos campos de T011, retorno não vazio, uso disponível e eventual falha sanitizada, sem executar os juízes completos ou modificar métricas (FR-003/FR-004).
- [ ] T013 [US1] Conferir os traces reais de T011–T012 no projeto/workspace esperado, aguardando envio do tracing e consultando ajuda antes de subcomandos CLI; consultar novamente `Client.read_project(project_name=...)` quando o projeto estava ausente em T009 e registrar em `docs/preparacao.md` data, IDs/links sanitizados, nome/ID do projeto, correspondência do tenant e estado de tracing; resolver a pendência somente com projeto e traces comprovados no contexto esperado, mantendo impedimento se a criação ou o envio falhar (FR-002/FR-005).
- [ ] T014 [US1] Exercitar ausência de variável e precedência de configuração em subprocesso isolado conforme `specs/001-preparar-experimentos/quickstart.md`, registrar em `docs/preparacao.md` que a validação identifica o nome ausente e bloqueia a etapa; não modificar `.env` real nem provocar erros remotos pagos, e documentar falhas reais por categoria/status sem resposta HTTP bruta (FR-001/FR-005).
- [ ] T015 [US1] Consolidar em `docs/preparacao.md` a matriz de prontidão por operação do contrato, com `operacoes_afetadas` “Pull, preparação da v2, push, avaliação ou entrega pública”; aplicar “`pendente → pronto` somente com evidência”, “`impedido → pronto` somente após correção e nova verificação”, histórico de falhas e causa/próxima ação; comprovar 100% dos pré-requisitos desta história ou manter impedimento explícito, sem transformar leitura em prova de permissão de push ou registrar métricas inexistentes (FR-005; SC-001/SC-002).

**Checkpoint**: MVP de prontidão auditável. US1 somente concluída com as provas
requeridas; um diagnóstico completo de falha não equivale a modelo/tracing pronto.
US2 pode avançar independentemente de falha de modelo, se a fundação estiver pronta.

T009 conclui a verificação de contexto; a verificação de existência do projeto é
separada. Quando apenas o projeto ainda não existe, o contexto comprovado libera
T010–T012, conservando a existência do projeto como `pendente`. T013 exige sua
confirmação e os dois traces para concluir. Isso não declara prontidão global nem
dispensa autenticação, seleção correta de workspace ou tracing habilitado.

## Phase 4: User Story 2 — Preservar o ponto de partida (Priority: P1)

**Goal**: completar a referência verificável dos materiais e da origem pública da
entrega, conservando a baseline capturada antes da preparação.

**Independent Test**: ler o manifesto, recomputar hashes contra a origem/captura e
confirmar os 15 casos com referências/dificuldades; consultar vínculo e visibilidade
do fork sem depender das chamadas de modelo (SC-003).

### Implementation and validation

- [ ] T016 [P] [US2] Consultar por leitura os metadados públicos de `fabiocsm/mba-ia-pull-evaluation-prompt` no GitHub e guardar em `docs/preparacao.md` “URL pública da entrega, visibilidade, indicador de fork, parent e data da consulta”; comprovar público, `fork=true` e parent `devfullcycle/mba-ia-pull-evaluation-prompt`, ou registrar pendência/impedimento e ação sem alterar visibilidade ou recriar repositório (FR-007).
- [ ] T017 [P] [US2] Completar `dataset` em `docs/integridade-inicial.json` após comparar o SHA-256 bruto com T002; exigir “`inputs.bug_report` e `outputs.reference` como strings não vazias”, “15 registros e distribuição `simple=5`, `medium=7`, `complex=3`”; por caso guardar “linha física (base 1), `complexity` (`simple`, `medium`, `complex`), SHA-256 canônico do registro e hashes canônicos separados de `inputs` e `outputs`”, usando “JSON UTF-8, `ensure_ascii=False`, `sort_keys=True`, `separators=(',', ':')`, sem quebra final”, sem editar relatos, referências ou metadados (FR-006).
- [ ] T018 [US2] Incorporar o resultado de T016 em `repository` de `docs/integridade-inicial.json` e conferir esquema/links/revisão de origem e exatamente quatro arquivos de T002–T003, preservando os valores iniciais; registrar o vínculo entre manifesto e preparação, indicando que futura auditoria remota da 005 compara multiconjuntos de pares inputs/outputs com multiplicidade, sem exigir `metadata.complexity` remoto que o avaliador não envia (FR-006/FR-007).
- [ ] T019 [US2] Validar `docs/integridade-inicial.json` como JSON, recomputar hashes dos quatro protegidos e casos e conferir 15/5/7/3 e evidência pública do fork; exercitar detecção de mudança em cópia temporária fora do Git, sem tocar o original, e registrar o resultado em `docs/preparacao.md`; não substituir baseline divergente para ocultar modificação (FR-006/FR-007; SC-003).

**Checkpoint**: materiais e referências auditáveis; origem da entrega comprovada
ou pendência explícita conforme o cenário da spec. Nenhuma nota de modelo é
necessária para verificar esta história.

## Phase 5: User Story 3 — Planejar reprodução e consumo (Priority: P2)

**Goal**: documentar condições reproduzíveis, estimar 3–5 ciclos e contabilizar
verificações mínimas, sem confundir custo previsto com consumo observado.

**Independent Test**: segundo executor repetir a preparação em ambiente isolado,
conferindo instalação/compatibilidade/condição e memória de cálculo; qualquer
divergência deve estar registrada antes de experimentos completos (SC-004).

### Implementation and validation

- [ ] T020 [P] [US3] Completar ambiente e relacionamentos em `docs/preparacao.md` com “SO, arquitetura, Python, pip, localização relativa de venv, versão CLI, hash de requirements e link para inventário de versões”; vincular baseline, inventário `docs/dependencias-preparacao.txt`, condição e verificações, conferindo os pins e preservação dos dois providers comprovados na fundação (FR-008/FR-009).
- [ ] T021 [P] [US3] Acrescentar ao `README.md` a seção de preparação em `Como Executar`, preservando integralmente o enunciado e seções existentes; documentar pré-requisitos, venv antes de instalação, `pip check`, configuração sem segredos, modelos efetivamente escolhidos, consultas e duas chamadas mínimas, leitura dos estados e links para os três registros e `specs/001-preparar-experimentos/quickstart.md`; indicar que comandos das specs 002–006 dependem de suas implementações (FR-008/FR-009).
- [ ] T022 [US3] Registrar em `docs/preparacao.md` preços/fontes/data e memória de cálculo para 3–5 ciclos com 15 gerações e 45 juízes/ciclo (180–300 chamadas), usando a fórmula da pesquisa e hipóteses de tokens por papel/juiz, cenários de 3 e 5 ciclos e reserva; separar US$ 1–5 como orientação e acrescentar verificações/retries/extras, sem incluir baseline v1 opcional como se já executada (FR-009).
- [ ] T023 [US3] Consolidar em `docs/preparacao.md` tentativas, tokens reportados e custo estimado das duas chamadas mínimas e de falhas/retries, separando projeção de cobrança observada; aplicar “Registrar `não disponível` quando não houver acesso à cobrança, nunca presumir zero” e “Acrescentar histórico datado ao corrigir falhas; não apagar o diagnóstico anterior”, mantendo consumo adicional da reprodução em aberto até T024 (FR-009).
- [ ] T024 [US3] Validar as instruções do `README.md` e do quickstart por segundo executor em ambiente isolado limpo, sem reutilizar/apagar `venv/` original; repetir instalação/pip check/imports, configuração, integridade, contexto e duas chamadas mínimas sob a condição registrada, contabilizar novas tentativas/tokens e guardar em `docs/preparacao.md` identificação da reprodução, comandos, resultados e divergências, sem afirmar SC-004 quando a reprodução não tiver ocorrido (FR-008/FR-009; SC-004).
- [ ] T025 [US3] Atualizar em `docs/preparacao.md` o balanço de custo incluindo T024, correspondência da condição entre executores e ações para divergências; verificar que um segundo executor consegue seguir o registro sem informações secretas publicadas, distinguindo orçamento estimado, consumo reportado e cobrança disponível, e manter impedimentos reais abertos antes dos futuros experimentos (FR-009; SC-004).

**Checkpoint**: reprodução comprovada e custo registrado, ou falhas identificadas
sem declarar prontidão/reprodução obtidas. Critério de métricas `>= 0.8` permanece
na spec 005; custo estimado não comprova aprovação ou qualidade do prompt.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: revisar rastreabilidade, integridade e disponibilidade dos registros
após as histórias, preservando resultados reais e os limites da preparação.

- [ ] T026 Revisar `docs/preparacao.md`, `docs/integridade-inicial.json`, `docs/dependencias-preparacao.txt` e `README.md` para garantir registros sanitizados e fatos suficientes sem depender apenas de URL privada; conferir links, JSON válido e que os três arquivos em `docs/` não estão ignorados, sem usar `results/` ou `screenshots/` como única evidência (FR-001/FR-009).
- [ ] T027 Recalcular os quatro hashes e os 15 casos contra `docs/integridade-inicial.json` original, mesmo após commits intermediários, conferir diff de protegidos, preservação OpenAI/Google e `git diff --check`, registrando em `docs/preparacao.md` o resultado final e qualquer divergência sem reescrever a captura inicial (FR-006; SC-003).
- [ ] T028 Conferir a matriz FR/SC deste `specs/001-preparar-experimentos/tasks.md` contra os registros, atualizar somente os estados efetivamente comprovados em `docs/preparacao.md`, `specs/README.md` e `plan/plano-implementacao.md` e resumir pendências e operações liberadas; não declarar pull/push/experimentos/entrega concluídos nem marcar comprovações ausentes como executadas (SC-001–SC-004).

## Dependencies & Execution Order

### Dependências por fase

```text
T001 → T002 → T003 → T004 → (T005 || T006)
                                  │
                 Fundação completa (T001–T006)
                         ┌────────┴────────┐
                         ▼                 ▼
                 US1 / T007–T015    US2 / T016–T019
                         └────────┬────────┘
                                  ▼
                         US3 / T020–T025
                                  ▼
                         Revisão / T026–T028
```

O diagrama representa dependências de implementação, não autorização para alterar
arquivos protegidos. A ordem padrão é fases 1–6, em prioridade da spec.

| Bloco/tarefa | Dependências diretas ou regra de execução |
| --- | --- |
| T001–T004 | Sequência indicada; captura e comparação antecedem instalação |
| T005 e T006 | Ambas dependem de T004; saídas distintas; completar ambas antes das histórias |
| US1 | Fundação completa; T007 seleciona modelos → T008 configura/valida → T009 comprova contexto → T010 registra condição → T011 → T012 → T013 confirma projeto/traces → T014 → T015 |
| US2 | Fundação completa; T016 e T017 independentes; ambas → T018 → T019 |
| US3 | US1 e US2 verificadas; T020 e T021 independentes; ambas → T022 → T023 → T024 → T025 |
| Revisão | Histórias concluídas; T026 → T027 → T028 |

US2 não depende dos modelos da US1. Se a US1 estiver impedida por modelo, a US2
pode executar com a fundação pronta. US3 pode preparar cálculo e instruções com
pendências explícitas, mas sua comprovação final depende dos resultados de US1/US2.
US1 e US2 escrevem `docs/preparacao.md`: não executar essas escritas simultaneamente.

### Falhas e avanço

Falha em credencial, contexto, modelo ou instalação registra estado/causa/ação e
mantém a comprovação pendente; não autoriza pular pré-requisito. Continuar somente
trabalho independente. A matriz por operação distingue o que pode avançar: pull não
usa modelo; validação estrutural não usa API; publicação tem sua prova de escrita
no push da 004; experimento exige os dois papéis/tracing e os gates das specs próprias.
Nada nesta lista executa esses fluxos futuros.

A ausência confirmada do projeto em T009 é o único caso que permite prosseguir com
essa verificação pendente: seu resultado é produzido pelas chamadas mínimas e
conferido em T013. As demais dependências de T010–T012 devem estar comprovadas.

### Parallel Opportunities

Há três pares potenciais, todos com pré-requisitos explícitos e arquivos distintos:
T005/T006, T016/T017 e T020/T021. Os seis marcadores `[P]` não autorizam agentes
adicionais nem execução concorrente sobre o mesmo documento compartilhado.

## Parallel Example: User Story 1

Não há par seguro de tarefas com escrita paralela dentro da US1: elas atualizam
`docs/preparacao.md` e as chamadas dependem da condição/contexto previamente
confirmados. Exemplo de execução correta: T010 → T011 → T012 → T013, conservando
rastreabilidade e contabilizando cada tentativa. O paralelismo da fundação T005/T006
pode reduzir o tempo de preparação dessa história.

## Parallel Example: User Story 2

Depois da fundação, executar as duas tarefas independentes e só então integrar:

```text
T016: conferir fork público → docs/preparacao.md
T017: inventariar os 15 casos → docs/integridade-inicial.json
Ambas concluídas → T018 → T019
```

## Parallel Example: User Story 3

Depois dos resultados de US1/US2, executar e depois consolidar:

```text
T020: completar evidência de ambiente → docs/preparacao.md
T021: documentar comandos e pré-requisitos → README.md
Ambas concluídas → T022 → T023 → T024 → T025
```

## Matriz de rastreabilidade

| Requisito local | Tarefas | Resultado verificável |
| --- | --- | --- |
| FR-001 | T001, T008, T014, T026 | Configuração/diagnóstico sem divulgação de segredos |
| FR-002 | T009, T013, T015 | Identidade, projeto/workspace e tracing corretos |
| FR-003 | T007, T010–T012 | Fontes oficiais e duas funções com temperatura zero comprovadas |
| FR-004 | T005, T007–T008, T010–T012, T027 | OpenAI inicial e suporte Google preservado |
| FR-005 | T008–T010, T013–T015, T028 | Estados, evidência, causa e próxima ação por dependência |
| FR-006 | T002–T003, T017–T019, T027 | Baseline, origem, quatro materiais e 15 referências preservadas |
| FR-007 | T016, T018–T019 | Fork público e parent verificados ou pendência explícita |
| FR-008 | T004–T006, T020–T021, T024 | Ambiente isolado, pins, imports e reprodução |
| FR-009 | T020–T026 | Comandos, condição, projeção 3–5 ciclos e consumo observado distinto |
| SC-001 | T008–T009, T013–T015, T028 | 100% dos pré-requisitos com resultado antes da operação dependente |
| SC-002 | T007, T010–T013, T026 | Dois papéis comprovados, identidade reproduzível, sem credenciais expostas |
| SC-003 | T002–T003, T016–T019, T027 | Referência inicial verificável de arquivos/casos e origem da entrega |
| SC-004 | T020–T025 | Segunda execução real e divergências registradas antes dos experimentos |

As correspondências ao plano mestre permanecem as do `plan.md`: R01, R02, R12,
R13, R16 e R18. SC-002 e SC-004 só recebem sucesso após provas reais; tarefas
planejadas e diagnóstico de impedimento não as satisfazem por si.

## Implementation Strategy

### MVP First — User Story 1

1. Completar setup/fundação (T001–T006).
2. Completar prontidão (T007–T015) e verificar o teste independente da US1.
3. Entregar registro de prontidão como primeiro incremento. Não chamar de conclusão
   da spec 001 antes da integridade/origem da US2 e reprodução/custo da US3.

### Incremental Delivery

1. Baseline e ambiente: referências preservadas antes de qualquer consumo remoto.
2. US1: acesso/contexto/modelos/tracing com limites e falhas rastreáveis.
3. US2: manifesto completo e origem pública auditáveis.
4. US3: guia e memória de consumo reproduzidos em outro ambiente/executor.
5. Revisão final: comprovar somente o obtido e manter a matriz de pendências.

### Notes

- Não criar novos scripts de produção, serviços ou suítes nesta feature.
- Não alterar `src/evaluate.py`, `src/metrics.py`, `src/utils.py` ou o JSONL.
- Não recuperar a v1, criar v2, publicar prompt, criar/compartilhar dataset ou rodar
  experimentos completos durante estas tarefas de preparação.
- Usar a chave OpenAI já existente; sem valores em logs, Git, links ou screenshots.
- Chamadas mínimas e reprodução também consomem API: registrar ambas e evitar retries
  cegos. Eventual indisponibilidade remota é impedimento, nunca prova simulada.
