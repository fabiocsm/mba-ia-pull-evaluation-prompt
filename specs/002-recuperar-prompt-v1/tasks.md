---
description: "Tarefas de implementação e comprovação da recuperação fiel da v1"
---

# Tasks: Recuperação fiel do prompt original

**Input**: artefatos de `specs/002-recuperar-prompt-v1/`.
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contrato](contracts/recuperacao-v1.md) e
[quickstart.md](quickstart.md). Constituição v1.0.0 e contrato acadêmico preservados.
**Data**: 2026-10-18. **Branch Git**: `dev`. **Feature ativa**: 002.
**Estado**: tarefas geradas e analisadas; achados I1/I2 corrigidos e revalidados
em 2026-10-18. Implementação, testes do pull e comprovação remota pendentes.

**Tests**: incluídos para os testes independentes e cenários de aceite solicitados
na spec (US1/US2, SC-001–SC-003), detalhados em V01–V12 do quickstart e no plano.
Mocks comprovam somente comportamento controlado; recuperação real é obrigatória.
Os seis testes de qualidade da v2 em `tests/test_prompts.py` pertencem à spec 003.

**Organization**: fases compartilhadas, US1 (P1), US2 (P2) e revisão transversal.
Não marcar tarefas como concluídas apenas porque foram descritas ou implementadas:
atividades de validação exigem suas evidências reais, inclusive falhas/impedimentos.

## Format: `[ID] [P?] [Story] Description`

- `[P]`: execução paralela possível nos pares explicitados ao final, com arquivos
  distintos e pré-requisitos concluídos; não autoriza alterar arquivos concorrentes.
- `[US1]` e `[US2]`: histórias da spec; ausentes em tarefas compartilhadas/finais.
- IDs e caminhos são relativos à raiz. IDs V01–V12 são da 002, não os da 001.
- Restrições do modelo de dados aparecem entre aspas nas tarefas correspondentes.

## Path Conventions

Scripts em `src/`, YAML em `prompts/`, testes em `tests/`, evidência versionada em
`docs/recuperacao-v1.md` e documentação operacional no `README.md`.
Não modificar `src/evaluate.py`, `src/metrics.py`, `src/utils.py`,
`datasets/bug_to_user_story.jsonl`, a v2 ou as implementações das demais specs.
Não criar banco, serviço, framework, modelo de domínio ou dependência adicional.

## Phase 1: Setup — contexto e ambiente existentes

**Purpose**: confirmar o contexto sem repetir a preparação já comprovada da 001.

- [ ] T001 Conferir `.specify/feature.json` apontando para `specs/002-recuperar-prompt-v1`, ler os artefatos dessa feature, `README.md`, `AGENTS.md` e `.specify/memory/constitution.md`, verificar o estado Git/branch e a matriz `docs/preparacao.md#matriz-atual`; identificar alterações preexistentes e pendências de acesso sem sobrescrevê-las ou trocar a branch `dev`.
- [ ] T002 Ativar `venv/`, conferir Python 3.10+, pins de `requirements.txt`, imports e `python -m pip check`; comparar SHA-256 dos quatro protegidos com `docs/integridade-inicial.json` e os 15 exemplos/referências (5/7/3); somente se não houver ambiente utilizável, criá-lo e ativá-lo antes de instalar `requirements.txt`, registrando impedimentos sem mudar pins ou materiais protegidos.

**Checkpoint**: ambiente e integridade disponíveis; divergências bloqueiam operação
afetada. O `.env` existente é preservado; nenhum acesso remoto nesta fase.

## Phase 2: Foundational — configuração e registro compartilhados

**Purpose**: estabelecer pré-requisitos comuns às duas histórias.

- [ ] T003 [P] Implementar em `src/pull_prompts.py` o carregamento de configuração com dotenv sem sobrescrever ambiente exportado e checagem por `check_env_vars` mais rejeição de valores só com espaços antes de criar `Client`; conferir presença das variáveis LangSmith/projeto/handle/tracing/provedor/dois modelos e chave do provedor conforme a 001, sem fixar `fabiocsm` no código nem expor valores ou fazer inferência; preparar resultado bool e `main()` com códigos 0/1, inicialmente falhando enquanto o fluxo estiver incompleto.
- [ ] T004 [P] Criar `docs/recuperacao-v1.md` com pré-requisitos e baseline comprovados em T001–T002, campos para comando/status, data/fuso, versões, revisão/hash, metadados/limitações e resultados V01–V12; diferenciar pendente/impedido/comprovado e referenciar `docs/preparacao.md` e `docs/integridade-inicial.json`, sem preencher resultados de pull ainda não executado.

**Checkpoint**: checagem local pronta e registro criado. T003/T004 só dependem da
Fase 1 e não editam o mesmo arquivo. Todas as histórias dependem desta fase.

## Phase 3: User Story 1 — Guardar a referência original (Priority: P1) — MVP

**Goal**: recuperar a semente real e preservar sua referência em YAML com proveniência.
**Independent Test**: executar o CLI e comparar duas mensagens, variáveis e metadados
do YAML à revisão efetivamente recuperada, sem v2, push ou experimentos.

### Tests for User Story 1

Escrever os testes antes do fluxo correspondente e confirmar falha funcional pelo
comportamento ainda ausente, não apenas por erro de importação ou coleta.

- [ ] T005 [P] [US1] Criar em `tests/test_pull_prompts.py` fixtures sintéticas de `ChatPromptTemplate` e cliente simulado, sem ler `.env` real ou usar rede, para V01–V03: origem/flags/destino/exit code, acentos/espaços/quebras finais/chaves literais/variável duplicada, round-trip YAML, metadados opcionais nulos/ausentes, snapshot e revisão distintos quando latest muda; usar a interface definida em `specs/002-recuperar-prompt-v1/contracts/recuperacao-v1.md` e confirmar falha antes de T007–T010.
- [ ] T006 [P] [US1] Documentar em `docs/recuperacao-v1.md` o vínculo de FR-001–FR-004 e SC-001/SC-003 com V01–V03/V12, os campos da projeção YAML e a distinção entre revisão do objeto e snapshot mutável do repositório; deixar a comparação real e os valores remotos pendentes, sem copiar metadados do YAML ilustrativo.

### Implementation for User Story 1

- [ ] T007 [US1] Implementar em `src/pull_prompts.py` validação e extração estrita: mensagens “System, depois Human; texto `f-string`”, exatamente duas, `system_prompt` como “Valor literal de `messages[0].prompt.template`, não vazio” e `user_prompt` como “Valor literal de `messages[1].prompt.template`, não vazio”; `input_variables` como “Cópia exata da lista retornada, igual a `[bug_report]`”. Rejeitar parser/bindings/opções internas/mensagens não representáveis antes de escrever, sem `format`, `invoke`, normalização, concatenação ou omissão silenciosa (FR-003/FR-004).
- [ ] T008 [US1] Construir em `src/pull_prompts.py` o mapping de chave única `bug_to_user_story_v1`, `version` “`v1`, rótulo local da entrega”; `source.identifier` “Sempre `leonanluppi/bug_to_user_story_v1`”, `commit_hash` “Obtido de `metadata.lc_hub_commit_hash`, não vazio”, validando também owner/repo; preservar `template_metadata` (“mapping ou null”), `template_tags` (“lista ou null”) e snapshot `get_prompt().model_dump(mode="json")`. Projetar `description` (“string ou null”, sem fallback), `tags` (“lista de strings”) e `created_at` (“ISO 8601 retornado no snapshot, se disponível”); usar instantes locais UTC `retrieved_at`/`repository_observed_at` separados. Aceitar somente “mappings com chaves string, listas, strings, bool, números finitos e null”; rejeitar demais tipos antes da escrita e registrar limitações sem transformar por `str()` (FR-002/FR-003).
- [ ] T009 [US1] Implementar em `src/pull_prompts.py` persistência do mapping por `save_yaml` em temporário único adjacente a `prompts/bug_to_user_story_v1.yml`, capturando saída bruta do helper; conferir retorno bool, reler com `yaml.safe_load`, exigir igualdade integral e reconstrução offline System/Human/variáveis; fechar arquivos e somente então `os.replace`, com limpeza em `finally` e erro controlado antes do commit, sem editar `src/utils.py` (FR-006).
- [ ] T010 [US1] Completar `pull_prompts_from_langsmith()` e `main()` em `src/pull_prompts.py`: chamar `Client.pull_prompt` exclusivamente na semente com `dangerously_pull_public_prompt=True`, `include_model=False`, `skip_cache=True`; obter snapshot com `get_prompt`, integrar T007–T009 e informar origem/revisão/destino somente com persistência completa. A função “retorna bool” e “`main()` converte para 0/1”; falha informa etapa sanitizada e revisão “Apenas se já recuperado; sem declarar persistência”. Não executar validação obrigatória falível após `os.replace` (FR-001/FR-002/FR-005/FR-006).
- [ ] T011 [US1] Executar os casos US1 em `tests/test_pull_prompts.py` para V01–V03, corrigir defeitos apenas nos arquivos permitidos e registrar comando/status/casos efetivamente aprovados em `docs/recuperacao-v1.md`; não apresentar mocks como SC-001 real.
- [ ] T012 [US1] Revalidar pré-requisitos da 001 e executar da raiz `python src/pull_prompts.py` para gerar `prompts/bug_to_user_story_v1.yml`; registrar em `docs/recuperacao-v1.md` comando/status, origem/revisão/destino e diagnóstico sanitizado. Em falha/incompatibilidade, conservar a cópia anterior, registrar causa/próxima ação e bloquear a conclusão da história, sem editar a semente para caber no formato.
- [ ] T013 [US1] Executar a comparação V12 de `specs/002-recuperar-prompt-v1/quickstart.md` fixando a revisão de `source.commit_hash`; comprovar 2/2 mensagens 100% idênticas, papéis/ordem/variáveis, metadados do template e projeções do snapshot em `prompts/bug_to_user_story_v1.yml`, sem melhorias/substituições; registrar revisão, SHA-256 local, instantes e limitações em `docs/recuperacao-v1.md`. Se a leitura posterior falhar, manter a cópia e SC-001 pendente até comparar a mesma revisão, sem refazer pull de latest.

**Checkpoint/MVP**: V01–V03 e V12 comprovados, YAML fiel e registro auditável.
SC-001/SC-003 podem ser comprovados; SC-002 e aceite integral dependem da US2.
Não prosseguir à 003 como se a 002 estivesse concluída antes das falhas/revisão final.

## Phase 4: User Story 2 — Diagnosticar recuperação malsucedida (Priority: P2)

**Goal**: identificar falhas sem segredo, falso sucesso ou perda da referência anterior.
**Independent Test**: simular credencial ausente, acesso/indisponibilidade, conteúdo
incompatível e falhas de escrita; exigir status 1 e cópia anterior byte a byte.
Não depender de novas chamadas remotas para comprovar esses cenários.

### Tests for User Story 2

- [ ] T014 [P] [US2] Acrescentar a `tests/test_pull_prompts.py` V04–V05 parametrizados: tipo/ordem/quantidade de mensagens, placeholders/multimodal, parser/bindings, formato não suportado, opções internas ou metadados não serializáveis; exigir saída 1 antes da gravação e diagnóstico controlado, e verificar preservação de metadados simples fora da projeção com limitação registrada (FR-003/FR-005).
- [ ] T015 [US2] Acrescentar a `tests/test_pull_prompts.py` V06–V07: configuração ausente/branca e precedência de ambiente vazio sobre dotenv controlado, credencial inválida/acesso negado, origem ausente, rede/serviço indisponível, `get_prompt` com erro/None e exceção inesperada; checar status 1, ausência de cliente quando configuração falha e nenhuma divulgação de marcadores secretos em stdout/stderr/artefatos, sem ler ou alterar `.env` real (FR-005/FR-006).
- [ ] T016 [US2] Acrescentar a `tests/test_pull_prompts.py` V08–V11 com falhas injetadas em criar diretório/temporário, `save_yaml` False/exceção/escrita parcial, releitura/dados divergentes/reconstrução, `os.replace` e limpeza; parametrizar V04–V11 com destino ausente ou sentinela válida e verificar ausência final ou bytes/hash anteriores intactos, nenhum sucesso anunciado e temporário limpo quando possível. Resíduo de limpeza nunca é apresentado como v1; capturar também segredo simulado na saída bruta do helper (FR-005/FR-006).
- [ ] T017 [P] [US2] Acrescentar a `docs/recuperacao-v1.md` a matriz planejada V04–V11 com categorias, etapa, preservação esperada e próxima ação, ligando FR-005/FR-006 a SC-002; diferenciar falha anterior ao commit de pendência de comparação/documentação posterior, sem registrar cenários não executados como aprovados.

### Implementation for User Story 2

- [ ] T018 [US2] Refinar em `src/pull_prompts.py` a classificação de erros de configuração, acesso, origem ausente, indisponibilidade, representação, escrita e inesperados para cumprir V04–V10; emitir categoria/etapa/ação e códigos 0/1 do contrato, nunca traceback, `repr(exception)`, headers ou corpo HTTP; incluir aviso de limitação de metadados sem despejar conteúdo remoto (FR-005).
- [ ] T019 [US2] Concluir em `src/pull_prompts.py` as garantias V08–V11: falhas anteriores a `os.replace` preservam bytes ou ausência do destino, `finally` tenta remover temporário e falha de limpeza gera diagnóstico sanitizado sobre resíduo, sem anunciar referência válida; `os.replace` concluído é commit e pendência posterior de evidência não se transforma em falsa falha de recuperação (FR-006).
- [ ] T020 [US2] Executar `pytest tests/test_pull_prompts.py -v` com todos os cenários V01–V11 e integrar correções em `src/pull_prompts.py`; comprovar 100% dos cenários de falha definidos, status 1, ausência de vazamento/falso sucesso e preservação anterior em `docs/recuperacao-v1.md`. Se T018/T019 alterarem caminho de sucesso/serialização, repetir T012–T013 e vincular evidência à revisão/código finais; caso contrário, reutilizar sua prova sem nova chamada redundante.

**Checkpoint**: US2 validada offline sem alterar destino real para provocar falhas.
A história usa o fluxo da US1, mas seus testes independem de acesso externo.
SC-002 exige todos os cenários aplicáveis, não somente alguns exemplos.

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: concluir documentação e conferir integridade/evidência das duas histórias.

- [ ] T021 Atualizar `README.md` na seção `Como Executar` com comando de pull, pré-requisitos, saída/códigos e ligação a `docs/recuperacao-v1.md`; manter requisitos acadêmicos originais e distinguir recuperação da 002 de otimização/testes/publicação/experimentos posteriores, sem alegar aprovação acadêmica.
- [ ] T022 Recomparar SHA-256 de `src/evaluate.py`, `src/metrics.py`, `src/utils.py` e `datasets/bug_to_user_story.jsonl` com `docs/integridade-inicial.json`, conferir 15 exemplos/referências e distribuição 5/7/3 e ausência de alterações no suporte aos provedores; registrar resultado efetivo em `docs/recuperacao-v1.md` e bloquear conclusão em divergência, sem redefinir baseline.
- [ ] T023 Auditar `docs/recuperacao-v1.md` contra V01–V12 de `specs/002-recuperar-prompt-v1/quickstart.md` e o contrato: ligar cada FR/SC aos comandos/resultados reais, conferir revisão/hash da v1 final, datas/versões, limitações do snapshot e falhas/tentativas; manter pendência explícita se faltar prova, sem rerodar verificações já válidas ou armazenar evidência apenas em diretórios ignorados.
- [ ] T024 Atualizar `specs/README.md` com o estado efetivamente comprovado da 002 e a dependência da 003; revisar os marcadores de `specs/002-recuperar-prompt-v1/tasks.md` contra as evidências sem marcar validação ainda pendente como concluída, conservando a 002 ativa até nova solicitação.
- [ ] T025 Conferir diff final/`git diff --check`, links locais em `README.md`, `specs/README.md` e `docs/recuperacao-v1.md`, ausência de credenciais nos artefatos alterados e preservação do contrato da v1; registrar a revisão final e eventuais pendências em `docs/recuperacao-v1.md`, sem push, criação de dataset, chamadas LLM ou experimentos nesta feature.

**Checkpoint final**: implementação e comprovação são estados separados. A 002 só
termina com SC-001–SC-003 atendidos e evidência versionável acessível pelo README.

## Dependencies & Execution Order

### Phase Dependencies

```text
Fase 1: T001 → T002
             ↓
Fase 2: T003 || T004
             ↓
US1: (T005 || T006) → T007 → T008 → T009 → T010 → T011 → T012 → T013
             ↓
US2: (T014 → T015 → T016) || T017
             ↓
       T018 → T019 → T020
             ↓
Fase 5: T021 → T022 → T023 → T024 → T025
```

`||` indica tarefas em arquivos diferentes. Dentro de um par, todas as dependências
da fase anterior precisam estar concluídas. A numeração organiza execução padrão;
T017 pode começar com T014 por não depender dos novos testes ou de sua execução.
T014–T016 editam o mesmo arquivo e são sequenciais.

### User Story Dependencies

- US1 depende da fundação e da prontidão remota da 001 para T012–T013; seus testes
  offline não dependem da rede. Persistência segura básica já integra o MVP.
- US2 depende do fluxo US1 neste script único. Após T011, seus cenários offline
  podem avançar mesmo se T012–T013 estiverem impedidos; isso não conclui US1/SC-001.
- Com ambas comprovadas, executar revisão final. Mudança posterior no fluxo de
  sucesso exige atualizar a prova remota antes de fechar a feature.
- Dependências nas próximas specs são somente informativas: esta lista não executa
  003–006 nem adiciona tarefas de inferência, publicação ou avaliação.

### Within Each User Story

Testes de contrato antes da implementação correspondente; confirmar falha do
comportamento ausente quando aplicável. Teste já aprovado por proteção implementada
na US1 deve permanecer aprovado, sem remover a proteção para fazê-lo falhar.
Validar dados antes de persistir; gravar temporário antes do commit final;
comprovar o arquivo antes de documentar sucesso. Código do script é editado
sequencialmente; não criar paralelismo artificial entre T007–T010 ou T018–T019.

### Parallel Opportunities

Pares permitidos: T003/T004 (configuração/registro), T005/T006 (contrato US1/registro)
e T014/T017 (contrato US2/matriz documental). Não há autorização para delegação
automática: são oportunidades de execução, não criação de agentes por este comando.
Todos os outros trabalhos seguem as dependências indicadas.

## Parallel Example: User Story 1

Após concluir T003/T004, iniciar separadamente:

```text
T005: escrever testes V01–V03 em tests/test_pull_prompts.py.
T006: registrar projeção/proveniência planejadas em docs/recuperacao-v1.md.
Aguardar ambos antes de implementar T007–T010 em src/pull_prompts.py.
```

## Parallel Example: User Story 2

Após US1 (ou T011 quando houver impedimento apenas remoto), iniciar separadamente:

```text
T014: escrever testes de representação V04–V05 em tests/test_pull_prompts.py.
T017: registrar matriz de falhas planejadas em docs/recuperacao-v1.md.
T015/T016 seguem T014 no mesmo arquivo; aguardar também T017 antes de T018.
```

## Implementation Strategy

### MVP First — US1

Completar Setup e Foundational, testes V01–V03, fluxo seguro e recuperação real
com comparação V12. Esse incremento entrega referência fiel para revisão, sem
atestar o aceite completo da feature antes dos cenários US2.

### Incremental Delivery

Acrescentar diagnósticos e comprovação de falhas sem regressão no sucesso; revisar
se a evidência real ainda corresponde ao código final e só então consolidar README,
integridade e rastreabilidade. Impedimento de rede não impede testes offline,
mas impede declarar fidelidade real ou liberar a 003 como dependência atendida.
Não executar chamadas repetidas apenas para preencher uma lista.

## Rastreabilidade

| Requisito | Implementação/registro | Verificação |
| --- | --- | --- |
| FR-001 | T010 | T005/T011/T012–T013 (V01/V12) |
| FR-002 | T008–T010/T021 | T005/T011/T012–T013 (V01/V12) |
| FR-003 | T007–T008/T006 | T005/T011/T013/T014/T020 (V02–V05/V12) |
| FR-004 | T007–T008 | T005/T011/T013 (V02–V03/V12); T023/T025 |
| FR-005 | T003/T010/T018 | T014–T016/T020 (V04–V11) |
| FR-006 | T009–T010/T019 | T015–T016/T020 (V06–V11) |
| SC-001 | US1 | T012/T013 e T023; recuperação real e mensagens 100% idênticas |
| SC-002 | US2 | T020 e T023; todos os cenários de falha definidos |
| SC-003 | US1 e revisão | T013/T023/T025; zero melhorias/substituições |
| R12 / constituição I | Compartilhado | T002/T022; hashes/referências/distribuição intactos |

## Notes

25 tarefas: Setup 2, Foundational 2, US1 9, US2 7, Polish 5.
Todos os marcadores permanecem abertos na geração. Evidências serão produzidas na
implementação; não são notas acadêmicas. A geração usa o template resolvido pelo
setup local; a análise foi realizada e seus dois achados foram corrigidos.
A próxima etapa é `$speckit-implement`.

Conferência da geração: 25/25 tarefas no formato exigido, IDs sequenciais,
rótulos por história, caminhos e links locais válidos; ponteiro da 002 confirmado,
quatro hashes protegidos iguais ao manifesto e `git diff --check` aprovado.
`.specify/extensions.yml` ausente nas verificações antes/depois: nenhum hook
registrado para executar. Nenhuma tarefa de implementação, teste do pull ou
chamada ao Hub foi executada nesta geração.

Revisão após análise (2026-10-18): I1 resolvido pela explicitação da validação
incremental no plano e no quickstart, mantendo V01–V03 antes de T012–T013 e
V04–V11 antes do aceite final em T020; I2 resolvido pelo caminho completo do
contrato em T005. IDs, dependências e 25 tarefas abertas preservados.
