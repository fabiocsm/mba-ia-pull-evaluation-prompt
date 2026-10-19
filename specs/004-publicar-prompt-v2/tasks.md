---
description: "Tarefas da spec 004: publicação pública e rastreável da v2"
---

# Tasks: Publicação pública e rastreável da v2

**Input**: documentos em `specs/004-publicar-prompt-v2/`.
**Data**: 2026-10-18 | **Branch Git**: `dev` | **Feature ativa**: 004.

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contrato C01–C10](contracts/publicacao-v2.md),
[quickstart V01–V12](quickstart.md), [README](../../README.md) e
[constituição v1.0.0](../../.specify/memory/constitution.md).
As evidências da 001/003 são pré-requisitos; não repetir suas chamadas LLM ou o pull.

**Estado**: 35 tarefas geradas, todas pendentes. Análise SDD realizada; A1
corrigido no contrato e nas tarefas, com revalidação documental. Implementação
e publicação real ainda não executadas. Esta lista não comprova resultados no Hub.

**Tests**: incluídos para os testes independentes das três histórias e SC-002/
SC-004 da spec, operacionalizados pela matriz obrigatória C09 do desenho.
Preservar os seis métodos da 003 e acrescentar testes no entregável
`tests/test_prompts.py`. Escrever os casos de cada incremento antes do código,
observar falha pertinente ao contrato ausente, depois implementar e reexecutar;
import quebrado ou falha incidental não é prova. Dublês não são evidência remota.

**Organization**: histórias organizadas por prioridade. US2 e US1 são P1;
desempatar por dependência: rejeição antes de escrita (US2), publicação (US1),
rastreabilidade/invalidação P2 (US3). Manter os rótulos originais da spec.
Incrementos têm verificações offline próprias; o aceite remoto integrado de
US1/US3 ocorre somente em T032–T034, após todos os gates locais. Não publicar
um incremento parcial para demonstrar a história.

## Format: `[ID] [P?] [Story] Description`

- Todos os IDs são sequenciais; cada tarefa tem checkbox pendente e caminho exato.
- Rótulos de história aparecem somente nas respectivas fases.
- `[P]` identifica três pares em arquivos diferentes, após os pré-requisitos
  explícitos. Não paralelizar edições em `src/push_prompts.py`,
  `tests/test_prompts.py`, `README.md` ou `docs/publicacao-v2.md` entre pares/fases.
- FR/SC são locais à 004; C01–C10 são do contrato e V01–V12 do guia acima.

## Path Conventions

Projeto único com `src/`, `tests/`, `prompts/`, `docs/` e `README.md` na raiz.
Referências documentais são relativas à raiz; ferramentas devem resolver os
caminhos a partir da raiz absoluta do repositório.

Implementar somente o script de push, os testes e documentação prevista. Nesta
feature, consumir v2 sem refiná-la; preservar v1 e os quatro protegidos
`src/evaluate.py`, `src/metrics.py`, `src/utils.py`,
`datasets/bug_to_user_story.jsonl`, seus 15 exemplos/referências 5/7/3 e providers.
Não avaliar, compartilhar dataset, chamar LLM ou fazer push Git nesta lista.

## Phase 1: Setup — ambiente e integridade

**Purpose**: conferir as dependências concluídas e registrar baseline local.

- [ ] T001 Conferir Python 3.10+, ativar `venv/` e executar `python -m pip check` conforme `specs/004-publicar-prompt-v2/quickstart.md`; reutilizar os pins de `requirements.txt` e `requests` já instalado, criando/ativando venv antes de instalar somente se o ambiente não existir; registrar comandos, versões e resultado no registro de execução deste `specs/004-publicar-prompt-v2/tasks.md`, sem reinstalação rotineira ou alteração de dependências.
- [ ] T002 Conferir V01 de `specs/004-publicar-prompt-v2/quickstart.md` contra `docs/integridade-inicial.json` e `docs/recuperacao-v1.md`, confirmar aceite da 003 em `specs/003-otimizar-validar-v2/tasks.md` e capturar bytes/hash inicial da v2 e referência Git neste `specs/004-publicar-prompt-v2/tasks.md`; preservar quatro protegidos, v1 e 15 exemplos/referências 5/7/3, sem repetir pull ou chamadas mínimas.

## Phase 2: Foundational — isolamento e registro comum

**Purpose**: preparar fronteiras de teste e documentação para todas as histórias.
T003/T004 bloqueiam o início das histórias.

- [ ] T003 Preparar em `tests/test_prompts.py` fixtures de importação isolada do script e dublês de `Client`, settings, push, commits, prompts e sessão HTTP; adaptar o bloqueio offline existente para controlar também aliases importados em `src/push_prompts.py`, sem abrir rede real, carregar dotenv real, usar chaves externas ou criar modelo/juiz; preservar os seis testes existentes e isolar `sys.modules`/monkeypatch para não interferir nas suítes de pull/preparação.
- [ ] T004 Criar `docs/publicacao-v2.md` como registro versionado com contexto, matriz FR/SC/C/V, seções de validação local e tentativas remotas inicialmente pendentes; prever estados separados de publicação e conferência, histórico por tentativa e links futuros de evidência, sem inventar hash remoto, URL, screenshot ou resultado; usar a entidade 5 de `specs/004-publicar-prompt-v2/data-model.md` como esquema do registro.

**Checkpoint**: testes podem importar o script sem acesso externo. Registro existe,
mas nenhum resultado de execução é presumido.

## Phase 3: User Story 2 — Rejeitar artefatos incompatíveis (Priority: P1)

**Goal**: rejeitar arquivo, definição, conteúdo e template inválidos antes de
instanciar cliente/escrever, também em chamada direta da função de push.

**Independent Test**: casos inválidos em temporários/cópias retornam diagnóstico
específico e zero chamadas de cliente/push; YAML real e prosa comum passam na
validação pura. FR-005; SC-002/SC-004; C01–C03/C09; V02–V04/V06.

### Tests for User Story 2

- [ ] T005 [US2] Escrever primeiro em `tests/test_prompts.py` os casos de `validate_prompt()` e entrada de `main()` para arquivo ausente/ilegível, YAML inválido/vazio, raiz nula/lista/escalar, definição ausente/nula/extra, seis campos ausentes individualmente, campo extra, tipos incorretos, strings vazias/espaços e versão diferente; exigir motivo pertinente, retorno `(False, list)` ou status 1 e nenhum cliente/push, usando cópias/temporários sem regravar `prompts/bug_to_user_story_v2.yml` (C01/C02/C09).
- [ ] T006 [US2] Escrever primeiro em `tests/test_prompts.py` controles de listas/técnicas insuficientes ou duplicadas por strip/casefold, Few-shot ausente ou sem pares completos, persona/formato ausentes das regras, TODO/FIXME/TBD em campos textuais/chaves, política I1 com `TODOS`/`todos`/`todo`, falso positivo combinado com outro defeito e retorno helper inválido/incoerente; incluir User decorado/repetido, variável extra/ausente e chaves desequilibradas, mais positivos com relato comum/vazio/JSON, entrada intacta e sem variáveis ocultas (C02/C03/C09).

### Implementation for User Story 2

- [ ] T007 [P] [US2] Implementar a função pura `validate_prompt(prompt_data: dict) -> tuple[bool, list]` em `src/push_prompts.py`: exigir seis campos, `description` como "string não branca, preservada sem alterações", `system_prompt` como "string com regras, persona e exemplos completos", `user_prompt` como "string exatamente `{bug_report}`", `version` como "string exatamente `v2`", `tags` como "lista não vazia de strings não brancas" e `techniques_applied` como "lista distinta por strip/casefold, inclui Few-shot e outra aplicada"; reutilizar `validate_prompt_structure` após tipos, manter só a exceção I1 exata quando não há marcador real, reprovar todos os demais erros/retornos incoerentes e montar/renderizar duas mensagens sem modificar o dict nem importar código de testes (C02/C03; depende de T005/T006).
- [ ] T008 [P] [US2] Detalhar em `docs/publicacao-v2.md` a matriz esperada de rejeições C01–C03/C09 e controles I1, com colunas para teste, diagnóstico, ausência de escrita e estado ainda pendente, distinguindo teste sintético de prova remota; não preencher aprovação antes da execução (depende de T005/T006; pode ocorrer junto de T007).
- [ ] T009 [US2] Implementar a leitura/guardas locais de `main()` em `src/push_prompts.py`, resolvendo `prompts/bug_to_user_story_v2.yml` por `Path(__file__)`, reutilizando `load_yaml` sob captura segura de saída e exigindo `definition_name` "constante `bug_to_user_story_v2`, raiz única"; detectar ilegibilidade e mudança entre leitura dos bytes e carregamento, validar antes de criar cliente e retornar 1 com categoria/etapa segura sem YAML bruto ou fallback; deixar caminho válido explicitamente sem liberação enquanto o push/conferência não estiver implementado (C01/C08).
- [ ] T010 [US2] Implementar as guardas de chamada direta de `push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool` em `src/push_prompts.py`: aceitar somente `prompt_name == "bug_to_user_story_v2"`, chamar a validação pura antes de criar cliente e retornar False em dados incompatíveis com diagnóstico seguro; não retornar True no caminho ainda não implementado e não alterar assinaturas do esqueleto (C02/C04/C08).
- [ ] T011 [US2] Completar em `tests/test_prompts.py` a integração das guardas de T009/T010 com loader/helper emitindo sentinelas sintéticas, chamando `main()` e a função direta; comprovar sentinela ausente de stdout/stderr, entradas/bytes intactos, motivo pertinente e nenhuma instanciação de cliente, HTTP, modelo ou push para artefato inválido, incluindo falha simultânea ao falso positivo de TODO (C01/C02/C08/C09).
- [ ] T012 [US2] Executar em `tests/test_prompts.py` o subconjunto US2 definido na seção de execução incremental deste `specs/004-publicar-prompt-v2/tasks.md` e os seis métodos existentes, corrigir falhas e registrar comandos/totais reais e cobertura das categorias em `docs/publicacao-v2.md`; nenhum teste negativo deve passar por exceção incidental, skip/xfail ou alteração do YAML real (SC-002; V02–V04/V06).

**Checkpoint**: rejeição e validação pura comprovadas offline. O caminho válido
de publicação ainda não está pronto; nenhum push real é permitido neste incremento.

## Phase 4: User Story 1 — Publicar uma revisão válida (Priority: P1) — MVP funcional

**Goal**: publicar o objeto correto no handle configurado, com metadados
suportados, confirmar a escrita e conferir conteúdo/publicidade antes de retornar True.

**Independent Test**: executar função de push com YAML real em memória e SDK/HTTP
controlados, verificando payload, revisão exata e prova anônima, sem inferência;
falhas são distinguíveis do sucesso. A prova real do cenário da spec será T032/T033,
após US3. FR-001–FR-004; SC-001/SC-004; C03–C09; V05–V10.

### Tests for User Story 1

- [ ] T013 [US1] Escrever primeiro em `tests/test_prompts.py` positivos e negativos de configuração/contexto: dotenv sem override, variáveis ausentes/brancas, provider OpenAI/Google e chave correspondente, tracing efetivo/aliases, endpoint/workspace e `tenant_handle` divergentes; verificar handle lido do ambiente e igualdade autenticada sem `fabiocsm` fixo, timeout finito e zero escrita quando configuração falha; testar projeção de descrição/tags/técnicas e serialização apenas de ChatPromptTemplate, sem modelo/chaves (C04/C05/C09).
- [ ] T014 [US1] Escrever primeiro em `tests/test_prompts.py` testes do ciclo SDK/HTTP: create/update, commit reutilizado, URL/prefixo reconhecidos, recuperação por hash completo sem cache com opt-in público, comparação de templates/renderização/metadata e repo, GET anônimo sem auth/cookies/redirects e manifesto equivalente; comprovar que sucesso em C07.1–C07.4 permite True/status 0 com inspeção visual C07.5 ainda pendente, sem declarar aceite da 004, e que falha automatizada continua retornando insucesso; cobrir auth/acesso/conexão/timeout, retorno vazio/URL inválida, prefixo ambíguo/hash divergente, pull/tipo/conteúdo/metadados incorretos, privado, HTTP negado/HTML/JSON inválido e estado parcial seguro sem push extra (C05–C09).

### Implementation for User Story 1

- [ ] T015 [US1] Implementar o gate de configuração em `src/push_prompts.py` com dotenv sem override, `check_env_vars` mais checagem não branca, provider/chave, modelos presentes sem inferência, tracing efetivo e contexto da 001; validar `configured_handle` como "texto não branco, um segmento válido, sem `/`, `:` ou URL", `authenticated_handle` como "handle do workspace confirmado pelo serviço", `workspace_id`/`endpoint` como "contexto confirmado conforme preparação; sem credenciais na URL" e `project`/`tracing` como "configuração não secreta e tracing efetivo"; consultar `/settings` via `client.request_with_retries` em cliente novo com timeout e exigir `configured_handle == authenticated_handle` antes de escrever (C04).
- [ ] T016 [US1] Implementar construção/publicação em `src/push_prompts.py` para `destination` "`{configured_handle}/bug_to_user_story_v2`": mensagens "exatamente System/Human, nesta ordem; templates idênticos aos locais", `input_variables` "lista exatamente `["bug_report"]`", metadata.version "`v2`", metadata.techniques_applied "lista igual à local, inclusive ordem e texto" e metadata.local_definition_sha256 "hash canônico local"; usar JSON `ensure_ascii=False`, `sort_keys=True`, `separators=(',', ':')`, UTF-8 sem newline para os seis campos originais, tags em união estável por strip/casefold e descrição intacta; chamar `Client.push_prompt` uma vez com `is_public=True`, sem parâmetros inventados ou chain com modelo (C03/C05).
- [ ] T017 [US1] Implementar resolução/conferência autenticada em `src/push_prompts.py`: `returned_url` é "URL válida do serviço retornada pelo push, pode ser privada/de workspace"; validar host/prompt/ausência de segredo, extrair prefixo reconhecido e obter `commit_hash` como "hash completo retornado em `PromptCommit`, 64 caracteres hexadecimais no pin atual" via `pull_prompt_commit` sem cache; recuperar por hash completo com opt-in público, comparar mensagens/entrada/metadata autoral e separar campos `lc_hub_*`; conferir owner/repo_handle/full_name como "destino configurado, sem identidade inesperada", description como "igualdade exata com descrição local", tags como "conjunto igual à união estável de tags locais + nomes das técnicas", is_public como "booleano `True` observado, não apenas solicitado" e last_commit_hash como "igual à revisão conferida no momento da liberação"; nunca identificar o próprio push por latest (C06/C07).
- [ ] T018 [US1] Implementar em `src/push_prompts.py` a conferência pública com nova `requests.Session`, `trust_env=False`, timeout `(10, 30)`, `allow_redirects=False` e requests efetivos sem Authorization/X-API-Key/Cookie; GET nas rotas configuradas de repo e commit completo, exigir HTTP 200/JSON com identidade/publicidade/metadados corretos e manifesto estruturalmente igual ao `PromptCommit` autenticado, sem deserializar o objeto anônimo nem reutilizar sessão do cliente; rejeitar HTML/login, redirects, campos ausentes e divergências (C07).
- [ ] T019 [P] [US1] Integrar em `src/push_prompts.py` configuração, escrita e conferência à função de push e ao caminho válido de `main()`, preservando bool/status e etapa; `True` somente com C04, C05, C06 e C07.1–C07.4 completos, código 0 somente no caminho validado/conferido automaticamente, falhas automatizadas com status 1; concluir o CLI sem aguardar C07.5 e informar que inspeção visual/registro posteriores ainda são obrigatórios para o aceite da 004 e entrega à 005, sem retorno de sucesso antecipado, exceção bruta, rollback ou repetição automática de push; distinguir escrita não confirmada de confirmada com conferência pendente/divergente e não alegar ausência de escrita após timeout (C08; após T015–T018; estabilidade final será ampliada em T025).
- [ ] T020 [P] [US1] Acrescentar em `README.md` a seção de publicação em `Como Executar`, com comando obrigatório `python src/push_prompts.py`, configuração/handle, metadados suportados e interpretação dos estados esperados, vinculando `docs/publicacao-v2.md` e mantendo a operação real pendente; preservar o enunciado e não qualificar URL do workspace ou exemplo de saída como evidência pública (C04–C08; após T015–T018; pode ocorrer junto de T019).
- [ ] T021 [US1] Executar em `tests/test_prompts.py` o subconjunto US1 definido neste `specs/004-publicar-prompt-v2/tasks.md`, repetir US2 e conferir que create/update usam os mesmos gates, duplicação de commit é aceita quando equivalente e falhas não disparam push extra; corrigir implementação e comprovar sigilo de sentinelas em erro de SDK, URL e HTTP e ausência de chamadas a providers (C09; V05–V10 offline).
- [ ] T022 [US1] Registrar os resultados reais dos testes US1 em `docs/publicacao-v2.md`, separando contrato comprovado por dublês das provas remotas ainda pendentes, explicando metadados de repo mutáveis versus commit e anotando que retorno do push não prova sozinho equivalência/publicidade; não preencher revisão/URLs remotas a partir de mocks nem executar publicação nesta tarefa (SC-004; V11).

**Checkpoint**: MVP funcional de publicação/conferência exercitado offline,
apoiado pela US2. A rastreabilidade dos bytes locais e o aceite remoto completo
ainda dependem da US3 e da revisão final; não liberar avaliação na 005.

## Phase 5: User Story 3 — Relacionar a versão local à publicada (Priority: P2)

**Goal**: associar a leitura local estável à revisão exata, emitir registro
auditável e invalidar a associação para alterações posteriores.

**Independent Test**: recuperar revisão fixa com dublê independente, comparar
templates/metadata e hashes, alterar somente cópias temporárias ou HEAD simulado
e comprovar insucesso sem atribuição incorreta; registro distingue todos os estados.
A correspondência real é comprovada em T032–T034. FR-006/FR-007; SC-003/SC-004;
C01/C06–C10; V08–V12.

### Tests for User Story 3

- [ ] T023 [US3] Escrever primeiro em `tests/test_prompts.py` testes de associação dos bytes/dict/template ao commit: dois hashes corretos, canonicalização sem circularidade, alteração só de formatação diferenciada de alteração de definição, metadata/hash remoto divergente, arquivo mudando entre leitura/carregamento e fim da operação, commit reutilizado e resumo com revisão completa/URLs válidas; conferir que nunca se imprime sucesso global se `main()` detectar mudança local após push (C01/C08/C10).
- [ ] T024 [US3] Escrever primeiro em `tests/test_prompts.py` controles de corrida e histórico: HEAD ou metadados do repo alterados por outro escritor, revisão histórica ainda igual, prefixo do retorno apontando para revisão diferente de latest, novo arquivo local ou edição só de metadados; exigir snapshot datado e estado pendente/divergente, sem sobrescrever prova anterior, pin fictício no avaliador, rollback ou publicação automática, e manter sigilo nos diagnósticos pós-escrita (C06–C10).

### Implementation and validation for User Story 3

- [ ] T025 [P] [US3] Completar em `src/push_prompts.py` o vínculo da leitura de `main()` com a definição enviada, usando local_file_sha256 como "SHA-256 hexadecimal dos bytes UTF-8 do arquivo" e local_definition_sha256 como "SHA-256 hexadecimal da definição canônica"; verificar bytes antes/depois do loader e após push/conferência, emitir resumo seguro com data/fuso, destino, hashes, revisão completa, URLs e resultados separados e retornar 1 se o artefato mudar, mesmo após escrita confirmada, sem reabrir YAML para remontar o objeto publicado (C01/C08; depende de T023/T024).
- [ ] T026 [P] [US3] Completar o formato de tentativas em `docs/publicacao-v2.md` com observed_at "ISO 8601 com fuso/UTC explícito", public_url como "endereço público de conteúdo/revisão efetivamente conferido sem credenciais", contexto não secreto/versões, ambos hashes, revisão, URL retornada, snapshot, resultados de mensagens/variáveis/metadata/publicidade, código/etapa, inspeção visual posterior com estado próprio/data/prova e relação com registro anterior; permitir código zero do CLI com inspeção visual pendente, mantendo aceite da 004/entrega à 005 bloqueados até C07.5 e seu registro; manter as tentativas remotas pendentes até T032/T033, sem copiar payloads brutos/chaves/cookies (C08; depende de T023/T024; pode ocorrer junto de T025).
- [ ] T027 [US3] Documentar em `README.md` e `docs/publicacao-v2.md` o gate operacional de C10: qualquer edição exige teste → push → conferência antes do experimento, registros antigos são históricos, commit pode ser deduplicado e a 005 deve revalidar hashes/HEAD/metadados antes/depois e manter revisão estável; não alterar `src/evaluate.py`, alegar trava automática inexistente ou executar avaliação nesta feature (FR-007).
- [ ] T028 [US3] Executar coleta, seis métodos obrigatórios e suíte ampliada de `tests/test_prompts.py` conforme o subconjunto US3 deste `specs/004-publicar-prompt-v2/tasks.md`, conferir todos os grupos C09, zero skip/xfail, bytes/hash da v2 e argumentos intactos, rede/LLM bloqueados e nenhum resultado artificial tratado como comprovação remota; corrigir falhas antes de avançar (V02–V06/V08–V12 offline).
- [ ] T029 [US3] Consolidar em `docs/publicacao-v2.md` os comandos/totais e resultados locais efetivos, a demonstração de invalidação por alteração local/HEAD e a correspondência entre FR-006/FR-007, C01/C06–C10 e V08–V12; deixar campos de publicação/visibilidade reais pendentes e declarar apenas prontidão local para o ciclo integrado final (SC-003/SC-004).

**Checkpoint**: validação, publicação/conferência e rastreabilidade comprovadas
offline; a ausência de prova remota impede concluir SC-001/SC-003 reais.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: validar regressão, executar uma publicação real do artefato final
e registrar evidências públicas antes da entrega à 005.

- [ ] T030 Executar os checks locais do guia `specs/004-publicar-prompt-v2/quickstart.md`, incluindo `pytest tests/test_prompts.py -v`, regressão `pytest tests/test_pull_prompts.py tests/test_preparation_checks.py -q` e execução conjunta se necessária para isolamento de imports; comparar quatro protegidos/v1 com `docs/integridade-inicial.json` e `docs/recuperacao-v1.md`, conferir v2 intacta, diff/novos arquivos/segredos e `git diff --check`, registrando comandos e resultados reais neste `specs/004-publicar-prompt-v2/tasks.md`; corrigir falhas antes de rede/escrita.
- [ ] T031 Conferir configuração/contexto da 001 pelo roteiro sem novas chamadas LLM em `docs/preparacao.md` e gate do guia `specs/004-publicar-prompt-v2/quickstart.md`: ambiente atual, handle/workspace, provider/modelos/chave e tracing efetivo, sem expor valores secretos; consultar `langsmith --help` e `langsmith prompt --help` antes de qualquer uso do CLI, carregar autenticação/workspace explicitamente sem presumir dotenv e registrar impedimentos reais em `docs/publicacao-v2.md` antes de T032.
- [ ] T032 Executar da raiz, no venv ativo, `python src/push_prompts.py` para o destino real configurado `fabiocsm/bug_to_user_story_v2`, após T030/T031 aprovados; registrar em `docs/publicacao-v2.md` código/etapa e confirmação, ambos hashes locais, revisão completa, URL retornada, comparação de mensagens/variáveis/metadata, snapshot e URLs anônimas efetivamente conferidas; interpretar código 0 como sucesso automatizado de C07.1–C07.4, com inspeção visual C07.5 ainda pendente até T033 e aceite final em T034; em falha preservar tentativa/histórico e investigar por leitura sem declarar publicação/aceite concluídos nem repetir escrita por reflexo (V07–V11).
- [ ] T033 Após o sucesso automatizado de T032, cumprir C07.5: conferir a revisão real no dashboard e abrir o endereço público sem autenticação, verificar conteúdo/descrição/tags/técnicas e publicidade, capturar prova visual em `docs/evidencias/publicacao-v2.png` ou URL pública estável e vinculá-la em `docs/publicacao-v2.md`; confirmar que a prova não depende do workspace ou apenas de diretórios ignorados, não expõe credenciais e corresponde à mesma revisão de T032, registrar o estado da inspeção visual separadamente do código do CLI e manter aceite da 004/entrega à 005 bloqueados se inspeção visual/acesso/evidência não puderem ser comprovados (V10/V11).
- [ ] T034 Consolidar resultados reais e interpretação dos comandos em `README.md`, concluir aceite da 004 somente com sucesso automatizado de T032 mais inspeção visual/evidência de T033 comprovados, atualizar V15 de `docs/preparacao.md` somente com escrita pública e conferência comprovadas e auditar FR-001–FR-007/SC-001–SC-004 e V01–V12 em `docs/publicacao-v2.md`; repetir integridade/diff ao encerrar, resolver lacunas e manter implementação concluída distinta de prova remota pendente quando aplicável, sem inventar notas, executar avaliação ou compartilhar dataset (V12).
- [ ] T035 Atualizar `specs/004-publicar-prompt-v2/plan.md`, `specs/README.md`, `plan/plano-implementacao.md` e o registro deste `specs/004-publicar-prompt-v2/tasks.md` com tarefas realmente executadas, evidências e pendências; manter a 004 ativa em `.specify/feature.json` e branch `dev`, entregar hashes/revisão/URLs à 005 apenas se o aceite estiver completo e preservar métricas, 3–5 iterações e evidências finais como trabalho posterior.

## Dependencies & Execution Order

### Phase Dependencies

```text
Setup T001–T002
  → Foundational T003–T004
    → US2 (P1) T005–T012: rejeitar antes de escrever
      → US1 (P1) T013–T022: publicação e conferência
        → US3 (P2) T023–T029: vínculo local, histórico e invalidação
          → Polish T030–T035: gates locais → preflight → push real → prova pública → aceite
```

As três histórias são verificáveis pelos testes próprios, mas compartilham o
script/testes e têm dependências de execução. O empate P1 foi resolvido em favor
da segurança do fluxo; não mudou a prioridade da spec. US1 inclui conferência de
conteúdo/publicidade porque seu próprio aceite exige revisão pública correta;
US3 amplia o vínculo aos bytes locais, histórico e uso posterior. Não implementar
um segundo comparador ou uma segunda rotina de push na US3.

### Within Each User Story

- Setup: T001 → T002; Foundational: T003 → T004.
- US2: T005 → T006 → **T007 e T008** → T009 → T010 → T011 → T012.
- US1: T013 → T014 → T015 → T016 → T017 → T018 → **T019 e T020** → T021 → T022.
- US3: T023 → T024 → **T025 e T026** → T027 → T028 → T029.
- Final: T030 → T031 → T032 → T033 → T034 → T035.

Não iniciar fase seguinte enquanto o checkpoint local anterior estiver falhando.
Não iniciar T032 antes dos gates locais e do preflight. Se um requisito externo
impedir o aceite real, preservar evidência do impedimento e concluir somente as
tarefas independentes cabíveis; nenhuma tarefa com prova faltante recebe `[X]`.

### Parallel Opportunities

Há seis marcadores `[P]`, formando três pares. Cada par só começa após os
pré-requisitos listados acima e edita arquivos distintos. Testes do mesmo módulo
e implementação que dependem de sua falha inicial ficam sequenciais; não marcar
paralelismo apenas porque são funções diferentes. Os exemplos descrevem
possibilidades de execução futura, sem despachar agentes nesta geração.

## Parallel Example: User Story 2

```text
Após T005/T006:
T007: implementar validador em src/push_prompts.py.
T008: detalhar matriz esperada em docs/publicacao-v2.md, resultados pendentes.
```

## Parallel Example: User Story 1

```text
Após T015–T018:
T019: integrar estados/caminho válido em src/push_prompts.py.
T020: documentar interface esperada em README.md, prova real ainda pendente.
```

## Parallel Example: User Story 3

```text
Após T023/T024:
T025: implementar estabilidade/resumo em src/push_prompts.py.
T026: completar formato de tentativas em docs/publicacao-v2.md, sem resultados presumidos.
```

## Implementation Strategy

### MVP First

O menor incremento técnico é a US2: validador/guardas offline. O MVP funcional
de publicação é **Setup + Foundational + US2 + US1**, testado com dublês e sem
publicação parcial. A entrega pública utilizável pela 005 exige também US3 e
T030–T035; reduzir o MVP não relaxa revisão, publicidade ou critérios acadêmicos.

### Incremental Delivery

1. Conferir preparação/integridade e preparar testes/registro.
2. Implementar US2; validar rejeição independente e preservar os seis testes.
3. Implementar US1; validar publicação/conferência com SDK/HTTP controlados.
4. Implementar US3; validar hashes/estabilidade/invalidação e histórico.
5. Rodar regressão/preflight, publicar uma vez o artefato final e conferir provas.
6. Registrar a entrega ou o impedimento real; a 005 mantém seu gate de HEAD e
   executa os experimentos posteriormente, sem mudar o avaliador protegido.

## Execução incremental dos testes

Na implementação, nomear casos novos por `test_push_validation_*` (US2),
`test_push_publication_*` (US1) e `test_push_provenance_*` (US3), preservando os
seis nomes obrigatórios. Essas convenções tornam os subconjuntos executáveis;
nenhum teste novo foi criado por esta geração de tarefas.

```bash
# US2 — após T011; validar também os seis métodos existentes.
python -m pytest tests/test_prompts.py -k 'test_push_validation_' -v
python -m pytest tests/test_prompts.py::TestPrompts -v

# US1 — após T019/T020, antes de registrar T022.
python -m pytest tests/test_prompts.py -k 'test_push_publication_ or test_push_validation_' -v

# US3 e integração local — após T027.
python -m pytest tests/test_prompts.py --collect-only -q
python -m pytest tests/test_prompts.py -v

# Regressão final — T030.
python -m pytest tests/test_pull_prompts.py tests/test_preparation_checks.py -q
```

Cada seleção deve coletar seus testes, sem saída 5 (nenhum coletado), skip ou
xfail. As falhas iniciais esperadas são verificadas por tarefa antes do código;
a execução integral deve passar antes de T032. Bloqueio de rede/LLM é de escopo
de teste; a prova real posterior usa o script fora de pytest.

## Rastreabilidade

| Requisito / critério | Tarefas principais | Contrato / validação |
| --- | --- | --- |
| FR-001 / SC-001/SC-002 | T005–T007, T013–T018, T032 | C01–C03/C05/C07; V02–V04/V08 |
| FR-002 / SC-001/SC-004 | T013, T015/T016, T031/T032 | C04/C05; V05/V07 |
| FR-003 / SC-001 | T013–T018, T032–T034 | C05/C07; V06/V08–V10 |
| FR-004 / SC-004 | T009–T011, T014, T019–T022, T025, T030–T034 | C06/C08/C09; V06/V07/V11 |
| FR-005 / SC-002 | T005–T012, T030 | C01–C03/C09; V02–V06 |
| FR-006 / SC-001/SC-003 | T016–T018, T023–T026, T028/T029, T032–T034 | C06–C08; V08–V11 |
| FR-007 / SC-003/SC-004 | T023–T029, T034/T035 | C01/C08/C10; V11/V12 |
| R12/R13 / integridade e sigilo | T002/T003, T011, T021, T028, T030/T034 | C01/C04/C08/C09; V01/V06/V12 |

### Cobertura dos grupos C09

| Grupo | Teste/implementação | Comprovação integrada |
| --- | --- | --- |
| Arquivo/raiz/campos | T005/T007/T009/T011 | T012/T028/T030 |
| Técnicas/tags/pendências/I1 | T006/T007/T011 | T012/T028/T030 |
| Mensagens/renderização | T006/T007, T014/T016/T017 | T021/T028/T032 |
| Configuração | T013/T015 | T021/T031/T032 |
| Serviço/revisão/público | T014/T016–T019 | T021/T032/T033 |
| Concorrência | T023–T025 | T028/T029/T034 |
| Sigilo | T005/T011/T013/T014/T024 | T021/T028/T030/T034 |

## Notes

- Total: 35 tarefas, sendo Setup 2, Foundational 2, US2 8, US1 10, US3 7 e final 6.
- Gate de conclusão: V01–V12 e FR-001–FR-007/SC-001–SC-004 comprovados; testes
  locais e acesso remoto são provas independentes. Falha externa não vira sucesso.
- Sem commit/push Git automático; marcar tarefas apenas depois de execução real.
- `.specify/extensions.yml` ausente nas verificações antes/depois da geração:
  nenhum hook registrado para executar.

## Conferência da geração — 2026-10-18

Confirmados 35 checkboxes pendentes, IDs T001–T035 sequenciais/únicos, caminhos
em todas as tarefas e rótulos restritos às fases das histórias. Contagens por
fase/história conferidas; seis marcadores `[P]` correspondem somente aos três
pares documentados, com pré-requisitos e arquivos distintos. Referências a IDs
existentes e cobertura FR-001–FR-007/SC-001–SC-004/C01–C10/V01–V12 conferidas.

Validados 73 links locais em tasks/plano/índices e a sintaxe Bash do bloco de
execução incremental. `git diff --check` aprovado; quatro hashes protegidos
iguais ao manifesto, v1 igual ao registro e diff de código/testes/prompts/dataset
vazio. A 004 permanece selecionada e a branch Git continua `dev`.
Nenhuma tarefa foi implementada, teste de produção executado, publicação ou
chamada LLM realizada nesta geração. Próxima etapa: `$speckit-analyze`.

## Registro de execução

Pendente. Na implementação, registrar comandos, datas, quantidades reais,
checagens por tarefa e links de evidências; a publicação tem histórico próprio
em `docs/publicacao-v2.md`. Nenhuma tarefa executada nesta geração.

## Correção da análise — A1

A análise SDD identificou ambiguidade média: C08 condicionava o retorno do CLI
a todo C07, embora C07.5 fosse uma inspeção visual posterior em T033.
Correção autorizada pelo autor em 2026-10-18: C07.1–C07.4 determinam sucesso
automatizado; C07.5 e o registro de evidência determinam o aceite posterior da
004 antes da entrega à 005. `main()` também exige arquivo local estável.

T014 exige os controles dos dois estados; T019 implementa o limite do CLI,
T026 mantém estados separados no registro e T032–T034 executam e comprovam
as etapas nessa ordem. Código zero com inspeção visual pendente é permitido;
aceite da 004/entrega à 005 nessa condição permanece bloqueado. Falha de
qualquer verificação automatizada continua exigindo insucesso do CLI.

Contrato, modelo, guia e plano foram alinhados. A revalidação documental da
correção não comprova implementação ou resultados: as 35 tarefas continuam
pendentes e não houve teste de produção, publicação ou chamada LLM.

Revalidação: condições de C08 e T014/T019/T026/T032–T034 coerentes; 35 IDs e
checkboxes pendentes preservados, três pares de paralelismo mantidos, 99 links
locais/âncoras de A1, oito blocos Bash e dois trechos Python embutidos conferidos.
`git diff --check` aprovado; quatro protegidos e v1 com hashes intactos e diff
de código/testes/prompts/dataset vazio. Nenhum achado remanescente de A1.
