---
description: "Tarefas da spec 003: prompt otimizado e validação estrutural efetiva"
---

# Tasks: Prompt otimizado e validação estrutural efetiva

**Input**: documentos em `specs/003-otimizar-validar-v2/`.
**Data**: 2026-10-18 | **Branch Git**: `dev` | **Feature ativa**: 003.

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contrato C01–C06](contracts/otimizacao-v2.md),
[quickstart V01–V12](quickstart.md), README e constituição v1.0.0.
Specs 001/002 concluídas; suas evidências são pré-requisitos, não tarefas a refazer.

**Estado**: 30/30 tarefas executadas e marcadas `[X]`. Implementação validada
localmente em 2026-10-18: 188 testes da v2 e 266 regressões aprovados; execução
conjunta confirmou 454 aprovados. Análise SDD com I1 corrigido e comprovado nos
controles positivos/negativos. Publicação e notas acadêmicas permanecem pendentes.

**Tests**: obrigatórios nesta feature (FR-007–FR-009 e SC-002/SC-003). Implementar
os seis métodos existentes e testes complementares/negativos no mesmo arquivo.
Escrever primeiro os testes pertinentes ao incremento e observar sua falha pelo
contrato ainda não implementado, sem considerar erro de importação ou falha
incidental como prova. Depois implementar e validar o incremento selecionado.

**Organization**: três histórias P1, na ordem da spec. US1 entrega as regras;
US2 completa os exemplos/técnicas/documentação; US3 comprova resistência a regressões.
A independência de verificação não implica independência de edição: YAML e testes
são compartilhados. Nenhum incremento parcial autoriza publicação.

## Format: `[ID] [P?] [Story] Description`

- Cada tarefa usa checkbox pendente, ID sequencial e caminho exato relativo à raiz.
- `[US1]`, `[US2]`, `[US3]` aparecem somente nas fases das respectivas histórias.
- `[P]` identifica pares de trabalho em arquivos diferentes, após seus pré-requisitos.
  Não paralelizar edições no mesmo YAML, módulo de testes ou README.
- As referências FR/SC são locais à spec 003; C01–C06 vêm do contrato e V01–V12 do guia.

## Path Conventions

Projeto único: `prompts/`, `tests/`, `src/`, `README.md` e documentação SDD em
`specs/003-otimizar-validar-v2/`. Caminhos em documentação são relativos à raiz;
operações de ferramentas devem resolvê-los a partir da raiz absoluta do repositório.

Escopo de implementação: criar `prompts/bug_to_user_story_v2.yml`, implementar
`tests/test_prompts.py` e atualizar `README.md`/estado SDD. Não editar a v1,
`src/evaluate.py`, `src/metrics.py`, `src/utils.py` ou o dataset. Não implementar
push, chamar LLM/Hub ou fabricar notas nesta feature.

## Phase 1: Setup — ambiente e referências

**Purpose**: conferir o ambiente existente e as evidências das dependências.

- [X] T001 Conferir Python 3.10+, ativação de `venv/`, pins de `requirements.txt` e `python -m pip check` conforme `specs/003-otimizar-validar-v2/quickstart.md`; criar/ativar venv e instalar requisitos somente se não houver ambiente preparado, sem sobrescrever o existente, e registrar comandos/status no registro de execução deste `specs/003-otimizar-validar-v2/tasks.md`.
- [X] T002 Conferir os quatro hashes em `docs/integridade-inicial.json` e o hash/revisão de `prompts/bug_to_user_story_v1.yml` contra `docs/recuperacao-v1.md` usando V11 de `specs/003-otimizar-validar-v2/quickstart.md`; registrar resultado neste `specs/003-otimizar-validar-v2/tasks.md`, sem novo pull, alteração de baseline ou leitura/exposição de credenciais.

## Phase 2: Foundational — suporte comum aos testes

**Purpose**: preparar a leitura do artefato real e a execução offline, bloqueando
as histórias até a conclusão de T003/T004.

- [X] T003 Preparar em `tests/test_prompts.py` fixture/carregador com caminho derivado de `Path(__file__)`, reutilizando `load_yaml` de `src/utils.py` sem alterá-lo e com dotenv controlado para não depender de credenciais reais; exigir arquivo real `prompts/bug_to_user_story_v2.yml`, raiz mapping e definição mapping `bug_to_user_story_v2`, sem fallback, sem fixture sintética no lugar do artefato e sem validar todo o conteúdo na fixture a ponto de mascarar a asserção de cada teste.
- [X] T004 Preparar em `tests/test_prompts.py` bloqueio de rede de escopo local à suíte e isolamento de variáveis de credenciais durante testes, sem nova dependência; garantir que o carregamento e as verificações locais não criem cliente LangSmith, modelo, chain com LLM ou juiz, preservando a execução dos testes existentes de outras features.

**Checkpoint**: infraestrutura pronta. YAML ausente deve produzir diagnóstico
explícito, não sucesso; a fixture não deve encobrir defeitos nas verificações específicas.

## Phase 3: User Story 1 — Produzir histórias claras e fundamentadas (Priority: P1) — MVP

**Goal**: instruções de produto, formato proporcional e bordas, com entrada única.
**Independent Test**: revisar regras e formatar mensagens com relatos próprios,
sem inferência; executar os testes de System/persona/formato, schema e template.
V01–V03/V08 e revisão inicial V09; FR-001–FR-003/FR-008; SC-003/SC-004 parciais.

### Tests for User Story 1

- [X] T005 [US1] Implementar primeiro em `tests/test_prompts.py` os métodos `TestPrompts.test_prompt_has_system_prompt`, `TestPrompts.test_prompt_has_role_definition` e `TestPrompts.test_prompt_mentions_format`, com asserções locais reutilizáveis: System existente e "string não branca", persona explícita de Product Manager/analista de produto e instruções de português, Markdown, Como… eu quero… para que… e critérios verificáveis antes de `## Exemplos`; observar falha do artefato ainda ausente/incompleto, sem aceitar persona/formato encontrados somente nos exemplos (C03/C04; V02/V03).
- [X] T006 [US1] Implementar primeiro `test_prompt_schema` e `test_prompt_template_contract` em `tests/test_prompts.py`: checar os seis campos de C01, `description`/`system_prompt` como "string não branca", `user_prompt` com "Valor `{bug_report}`; sem regras/exemplos adicionais", `version` "Exatamente `v2`", `tags` como "lista não vazia de strings não brancas" e técnicas como lista de strings não brancas; montar duas mensagens System/Human nessa ordem, conferir `input_variables == ["bug_report"]` sem opcionais/partials e renderizar relato simples, vazio, log com chaves e instrução conflitante mantendo Human idêntico e System estável (C01/C02; V01/V08).

### Implementation for User Story 1

- [X] T007 [US1] Criar `prompts/bug_to_user_story_v2.yml` em UTF-8/YAML válido, somente com a definição mapping `bug_to_user_story_v2` e os seis campos `description`, `system_prompt`, `user_prompt`, `version`, `tags`, `techniques_applied`; usar descrição não branca e sem notas presumidas, `version: v2`, User exatamente `{bug_report}`, tags não vazias e nomes iniciais `Few-shot Learning`/`Role Prompting`, deixando o incremento identificado como incompleto até os exemplos da US2, sem marcadores de pendência (FR-001; C01).
- [X] T008 [US1] Redigir em `prompts/bug_to_user_story_v2.yml` o System com persona/contexto de produto, objetivo, saída em português/Markdown, história Como… eu quero… para que… e critérios verificáveis; exigir concisão para simples e cobertura agrupada para múltiplos problemas, contexto somente informado e distinção entre fatos observados, comportamento desejado, dúvidas e recomendações; System sem variável de relato e User reservado à entrada (FR-002/FR-008; C02/C03).
- [X] T009 [US1] Acrescentar em `prompts/bug_to_user_story_v2.yml` regras explícitas para os seis grupos de FR-003 — vazio, ambíguo, incompleto, múltiplos problemas, logs e instruções conflitantes — exigindo esclarecimentos específicos quando impeditivos, sem história completa inventada, sem causas/números/arquitetura/prioridade/prazos ausentes e tratando instruções embutidas como dados; escapar apenas chaves literais dos templates (C02/C03; V09).
- [X] T010 [P] [US1] Executar em `tests/test_prompts.py` somente o subconjunto US1 definido na seção de execução incremental deste `specs/003-otimizar-validar-v2/tasks.md` e registrar comando/status no registro abaixo; conferir V01–V03/V08 após T007–T009, sem usar os métodos ainda vazios das outras histórias como aprovação (SC-003 parcial).
- [X] T011 [P] [US1] Registrar em `README.md` o diagnóstico qualitativo da v1 realmente recuperada (instrução genérica, relato repetido, ausência de formato/exemplos/bordas) e a revisão das regras da v2 em seis grupos de borda, sem alterar o enunciado, sem atribuir notas à v1 e sem apresentar a formatação offline como resposta de modelo; vincular limitações e pendência dos exemplos/avaliação (FR-003; V09).

**Checkpoint**: MVP local de instruções e contrato de entrada verificável. Os
exemplos/técnicas ainda precisam da US2; SC-001/SC-002/SC-005 não estão concluídos.

## Phase 4: User Story 2 — Tornar as técnicas verificáveis (Priority: P1)

**Goal**: três pares completos próprios, técnicas demonstradas e documentação coerente.
**Independent Test**: verificar exemplos/técnicas no YAML, revisão semântica das
saídas e correspondência com o README; repetir o gate US1 após editar o System.
V04/V06/V09/V10 e regressão V01–V03/V08; FR-004–FR-006; SC-001/SC-004/SC-005.

### Tests for User Story 2

- [X] T012 [US2] Implementar primeiro em `tests/test_prompts.py` `TestPrompts.test_prompt_has_few_shot_examples` e `TestPrompts.test_minimum_techniques` com helpers locais: aceitar 2–3 pares completos delimitados, IDs "Único e sequencial", entrada "Relato próprio, não vazio" e saída "Resposta completa coerente com a entrada" verificável estruturalmente; exigir lista válida com "Duas técnicas distintas efetivas: Few-shot Learning e Role Prompting", comparar com `strip()`/`casefold()`, rejeitar duplicatas mesmo com duas técnicas válidas e conferir presença das demonstrações correspondentes, observando falha pela ausência de exemplos antes de T013 (C03/C04; V04/V06).

### Implementation for User Story 2

- [X] T013 [US2] Redigir em `prompts/bug_to_user_story_v2.yml`, após `## Exemplos`, três pares completos próprios `### Exemplo 1` a `### Exemplo 3`, com `#### Entrada`/`#### Saída` não brancas e identificadores únicos/sequenciais: simples suficiente; insuficiente/ambíguo com esclarecimentos em vez de história inventada; múltiplos problemas com log e instrução conflitante; não criar chave YAML extra nem copiar entradas ou referências de `datasets/bug_to_user_story.jsonl` (FR-004; C03; V04/V09).
- [X] T014 [US2] Finalizar em `prompts/bug_to_user_story_v2.yml` `techniques_applied` com `Few-shot Learning` e `Role Prompting` efetivamente presentes, confirmar tipos/tags e coerência entre persona, instruções e exemplos; não declarar Skeleton of Thought apenas por títulos, nem acrescentar técnica sem aplicação/documentação, e garantir a variável única após o acréscimo dos exemplos (FR-005; C01–C03; V06/V08).
- [X] T015 [US2] Revisar os três pares de `prompts/bug_to_user_story_v2.yml` contra os seis grupos de C03/V09 e registrar em `README.md` a cobertura, a origem própria e a distinção entre fatos/dúvidas/recomendações; conferir saídas completas e zero fatos inventados, sem copiar referências do dataset nem confundir comportamento desejado com fato observado; corrigir o YAML antes de estabilizá-lo para T016/T017 (FR-003/FR-004; SC-004).
- [X] T016 [P] [US2] Completar em `README.md` a seção `Técnicas Aplicadas (Fase 2)` com nome, justificativa e trechos reais de Few-shot Learning e Role Prompting, incluindo exemplos práticos e comparação qualitativa v1/v2, mantendo o enunciado e as notas ilustrativas identificadas como tais; documentar publicação/avaliação pendentes, sem adicionar resultados fabricados (FR-006; C05; V10).
- [X] T017 [P] [US2] Executar em `tests/test_prompts.py` o subconjunto US2 e repetir o subconjunto US1 definidos neste `specs/003-otimizar-validar-v2/tasks.md`, após estabilizar T013–T015; registrar resultados no registro abaixo e corrigir qualquer variável acidental ou regressão antes de avançar (V01–V04/V06/V08; SC-001/SC-003).

**Checkpoint**: técnicas e exemplos verificáveis, documentação correspondente e
contrato de entrada preservado. A prova completa de regressões permanece na US3.

## Phase 5: User Story 3 — Detectar regressões antes da publicação (Priority: P1)

**Goal**: seis testes efetivos e matriz negativa, offline, sobre o artefato real.
**Independent Test**: coletar/executar a suíte completa e demonstrar rejeição específica
dos defeitos correspondentes sem alterar o YAML real. V01–V08/V12;
FR-007–FR-009; SC-002/SC-003.

### Tests for User Story 3

- [X] T018 [US3] Implementar `TestPrompts.test_prompt_no_todos` em `tests/test_prompts.py` com o detector de C04/I1 sobre todos os campos textuais: tokens isolados maiúsculos `TODO`/`FIXME`/`TBD` e formas entre colchetes sem distinção de caixa/espaços internos; comprovar rejeição de marcadores em System/User/metadados e aprovação de `TODOS`, `todos` e `todo` em prosa comum, usando limites de palavra Unicode e cópias isoladas sem alterar o YAML real (C01/C04; V05).
- [X] T019 [US3] Acrescentar em `tests/test_prompts.py` testes negativos parametrizados para os seis métodos obrigatórios, reutilizando as mesmas asserções sobre cópias isoladas da v2 real: System ausente/branco/tipo inválido; persona/formato ausentes das regras mesmo presentes em exemplos; pares incompletos/brancos/fora de 2–3; pendência em System/User/metadados; técnica obrigatória ausente, menos de duas distintas ou duplicatas normalizadas; exigir motivo pertinente, sem `skip`, `xfail` ou aprovação por exceção genérica (C04; V02–V07).
- [X] T020 [US3] Acrescentar em `tests/test_prompts.py` negativos de C01 para arquivo ausente/YAML inválido em temporários, raiz nula/lista/escalar, definição ausente/não mapping, campos ausentes/brancos/tipos inválidos, versão diferente de `v2` e listas inválidas; após validar tipos, chamar `validate_prompt_structure` de `src/utils.py` sobre os dados originais e aplicar o adaptador C04/I1, desconsiderando somente `system_prompt ainda contém TODOs` quando o detector local não encontrar marcador real no System; manter reprovação para qualquer outro erro, marcador em outro campo ou retorno inesperado/incoerente, provar controles com `TODOS` junto de descrição ausente/técnicas insuficientes e entrada intacta, sem sanitizar texto nem alterar o helper (FR-009; V01/V07).
- [X] T021 [US3] Acrescentar em `tests/test_prompts.py` negativos de C02 para User vazio/incorreto, `{bug_report}` no System, variável adicional como `{variavel_extra}`, chaves literais desequilibradas e montagem incompatível; manter positivos de logs/JSON escapados, relato vazio/com chaves/conflito e invariância de System/Human, sem opcionais/partials para esconder entradas extras (FR-008; V07/V08).
- [X] T022 [US3] Comprovar em `tests/test_prompts.py` que o bloqueio de rede rejeita uma tentativa controlada e que a suíte funciona sem credenciais e sem depender do `.env` real; preservar os utilitários protegidos, não importar avaliador nem gerar notas simuladas, e registrar a prova offline neste `specs/003-otimizar-validar-v2/tasks.md` (FR-007; C04; V07/V12).

### Integration and validation for User Story 3

- [X] T023 [US3] Conferir em `tests/test_prompts.py` que negativos usam cópias descartáveis/temporários e não alteram `prompts/bug_to_user_story_v2.yml`, comparando seus bytes/hash antes/depois da execução; revisar que cada negativo falha pela condição correspondente, que os seis métodos principais leem o arquivo real e que não restam corpos vazios, fallback ou asserções incondicionais (FR-007/FR-009; V07).
- [X] T024 [P] [US3] Executar `pytest tests/test_prompts.py --collect-only -q` e `pytest tests/test_prompts.py -v -rA` sobre `tests/test_prompts.py`, conferir os seis nomes obrigatórios e extras coletados/executados com zero skip/xfail, e registrar comandos, totais reais e status neste `specs/003-otimizar-validar-v2/tasks.md`; corrigir falhas e repetir antes do aceite (SC-002/SC-003; V12).
- [X] T025 [P] [US3] Atualizar em `README.md` a seção `Como Executar` com pré-requisitos do venv, validação offline, coleta/execução dos testes e interpretação dos resultados; explicar o requisito de os seis testes serem efetivos, separar aprovação estrutural de notas reais e indicar que push/avaliação seguem nas specs 004/005, sem alegar comandos/resultados ainda não executados (FR-009; C05/C06; V10).

**Checkpoint**: seis verificações e negativos efetivos, sem rede e com artefato
intacto. A conclusão da feature ainda exige a revisão transversal final.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: consolidar evidências locais, integridade e passagem para a 004.

- [X] T026 Executar `pytest tests/test_preparation_checks.py tests/test_pull_prompts.py -q` conforme `specs/003-otimizar-validar-v2/quickstart.md`, confirmar que as alterações em `tests/test_prompts.py` não interferem nas suites existentes e registrar comando/quantidade/status reais neste `specs/003-otimizar-validar-v2/tasks.md`, sem novas chamadas remotas (V12).
- [X] T027 Repetir V11 de `specs/003-otimizar-validar-v2/quickstart.md` contra `docs/integridade-inicial.json` e a v1 registrada em `docs/recuperacao-v1.md`, conferir os 15 exemplos/referências/distribuição 5/7/3 preservados pelos hashes e revisar `git diff --check`, diff/status e arquivos novos de prompt/testes/README; não incluir credenciais ou evidências apenas em diretórios ignorados.
- [X] T028 Auditar FR-001–FR-009, SC-001–SC-005 e V01–V12 pela matriz deste `specs/003-otimizar-validar-v2/tasks.md`, resolver lacunas no YAML/testes/README e conferir que cada técnica declarada tem aplicação real e justificativa, sem editar a v1, os quatro protegidos ou critérios acadêmicos; registrar pendências em vez de marcar aceite incompleto como concluído.
- [X] T029 Consolidar em `README.md` os comandos/resultados locais efetivamente executados, revisão semântica, comparação qualitativa e limitações da 003; informar a prontidão local para a 004 somente com V01–V12 satisfeitos, mantendo publicação, cinco métricas/média >= 0.8 e 3–5 iterações como etapas futuras da 004/005, sem apresentar exemplos redigidos como saídas reais LLM.
- [X] T030 Atualizar `specs/README.md`, `plan/plano-implementacao.md` e `specs/003-otimizar-validar-v2/plan.md` com o estado realmente comprovado e links do registro local, marcar apenas tarefas executadas neste `specs/003-otimizar-validar-v2/tasks.md` e manter a 003 ativa em `.specify/feature.json`, sem trocar a branch `dev` nem iniciar publicação/avaliação automaticamente (C06).

## Dependencies & Execution Order

### Phase Dependencies

```text
Setup T001–T002
  → Foundational T003–T004
    → US1 T005–T011
      → US2 T012–T017
        → US3 T018–T025
          → Polish T026–T030
```

As três histórias têm prioridade P1. US2 precisa das regras/artefato da US1;
US3 consolida asserções introduzidas nas duas anteriores. Todas são verificáveis
por seus critérios próprios, mas não devem editar simultaneamente os mesmos arquivos.
O mínimo demonstrável é a US1, sem publicação e sem concluir a feature.

### Within Each User Story

- US1: T005 → T006 → T007 → T008 → T009 → **T010 e T011** → checkpoint.
- US2: após US1, T012 → T013 → T014 → T015 → **T016 e T017** → checkpoint.
- US3: após US2, T018 → T019 → T020 → T021 → T022 → T023 → **T024 e T025** → checkpoint.
- Final: após as três histórias, T026 → T027 → T028 → T029 → T030.

Se uma validação encontrar regressão e exigir editar o YAML/testes, interromper o
par correspondente, aplicar correção, atualizar trechos do README se necessário e
repetir o gate afetado antes de retomar. Não há tarefa de integração remota aqui.

### Execução incremental dos testes

Após T007–T009, o gate US1 é:

```bash
pytest tests/test_prompts.py -v -k 'has_system_prompt or has_role_definition or mentions_format or prompt_schema or template_contract'
```

Após T013–T015, o gate adicional US2 é:

```bash
pytest tests/test_prompts.py -v -k 'has_few_shot_examples or minimum_techniques'
```

T017 repete os dois comandos. Em T024, executar a suíte completa de V12 conforme
o guia. Antes de T018, o método ainda vazio `test_prompt_no_todos` não conta como
validação. Não executar a suíte inteira dos esqueletos e declarar seis verificações
efetivas; a aprovação integral só existe após a implementação e negativos da US3.

## Parallel Examples by User Story

### US1 — após T009

```text
T010: executar o gate US1 e registrar em specs/003-otimizar-validar-v2/tasks.md
T011: revisar/documentar o diagnóstico e as regras em README.md
```

### US2 — após T015

```text
T016: documentar técnicas/trechos em README.md
T017: executar gates US1/US2 e registrar em specs/003-otimizar-validar-v2/tasks.md
```

### US3 — após T023

```text
T024: coletar/executar suíte completa e registrar em specs/003-otimizar-validar-v2/tasks.md
T025: documentar comandos/interpretação em README.md
```

Os seis marcadores `[P]` formam três pares, sem dependência interna. Os pares apenas
leem o YAML/testes estabilizados e escrevem em arquivos diferentes. Não são uma
instrução para criar agentes; executar conforme recursos e autorização disponíveis.

## Matriz de rastreabilidade

| Requisito / restrição | Tarefas | Contrato | Validação | Critério |
| --- | --- | --- | --- | --- |
| FR-001 / R04 | T006–T010, T020 | C01 | V01/V08 | SC-002/SC-003 |
| FR-002 / R06 | T005, T008, T010–T011, T015 | C03/C04 | V03/V09 | SC-004 |
| FR-003 / R06/R12 | T009, T011, T013, T015 | C03 | V09 | SC-004 |
| FR-004 / R05 | T012–T013, T015, T017 | C03/C04 | V04/V09 | SC-001/SC-004 |
| FR-005 / R05 | T012, T014, T016–T017, T019 | C01/C04/C05 | V06/V10 | SC-001/SC-005 |
| FR-006 / R14 | T011, T015–T016, T025, T029 | C05 | V10 | SC-005 |
| FR-007 / R11 | T003–T006, T012, T018–T024 | C04 | V02–V07/V12 | SC-002 |
| FR-008 / R04/R06 | T006–T010, T014, T017, T021 | C02 | V08 | SC-003 |
| FR-009 / R04/R11 | T006, T018, T020–T025, T029 | C01/C04–C06 | V01/V05/V08/V12 | SC-002/SC-003 |
| Integridade / R12/R13 | T002, T023, T026–T028, T030 | C06 | V11/V12 | Restrição transversal |

C06 também é coberto por T025/T029/T030. T028 confere o conjunto de V01–V12 e o
aceite semântico/documental; não introduz critérios de qualidade novos.

## Implementation Strategy

### MVP First — User Story 1

Concluir Setup/Foundational e US1; validar instruções e template com seu subconjunto
de testes e revisão de bordas. O MVP demonstra o contrato local, não a saída de um
modelo, e não atende sozinho ao requisito obrigatório de Few-shot ou publicação.

### Incremental Delivery

1. US1: regras e entrada única, com gate próprio e diagnóstico da semente.
2. US2: exemplos próprios e técnicas documentadas, repetindo o gate anterior.
3. US3: seis métodos e matriz negativa, coleta/execução completa offline.
4. Polish: regressões existentes, integridade, revisão completa e registro final.

A análise `$speckit-analyze` foi realizada; o achado I1 foi corrigido em C04 e
T018/T020 e revalidado. Prosseguir com `$speckit-implement`. Só entregar à 004 com
todos os gates locais comprovados; a avaliação real e iterações pertencem à 005.

## Registro de execução

Execução em 2026-10-18, branch `dev`, venv existente ativado em cada comando Python.

- T001: `source venv/bin/activate`, `python --version` → 3.11.14;
  `python -m pip check` → No broken requirements found; comparação por
  `importlib.metadata.version` → todos os pins de `requirements.txt` conferem.
- T002: V11 → quatro hashes protegidos e v1 iguais às referências; revisão da
  v1 `2950c33dbd7ffaed2e440b50adfd7769d183f90faf0bae5aa4864354f88e4073`.
  Sem pull ou acesso a credenciais. `.gitignore` já cobre os padrões Python,
  venv, segredos, temporários e IDE; não há outra tecnologia que exija novo ignore.
- T003/T004: carregador real por `Path(__file__)`, reutilização de `load_yaml`,
  dotenv desabilitado antes do import, ambiente sem credenciais e bloqueio de
  sockets/DNS restritos a este módulo. Prova controlada do bloqueio fica em T022.
- T005/T006: primeiro gate US1 antes do YAML → 5 erros esperados de setup com
  diagnóstico explícito `Arquivo v2 ausente`; nenhum erro de importação.
  Isso comprova ausência detectada, não sensibilidade individual de persona/formato,
  que será demonstrada nos negativos de T019/T021.
- T007–T009: seis campos, regras de produto, formato e seis bordas redigidos;
  incremento ainda sem exemplos, portanto sem aprovação integral.
- T010: `pytest tests/test_prompts.py -v -k 'has_system_prompt or has_role_definition or mentions_format or prompt_schema or template_contract'`
  → 5 passed, saída 0. Renderização de quatro relatos, sem inferência.
- T011: diagnóstico da v1 e revisão inicial das seis bordas registrados no README;
  exemplos/técnicas completos e notas continuam pendentes neste checkpoint.

- T012: gate US2 escrito antes dos exemplos → 2 failed, motivo específico
  `Seção Exemplos ausente ou duplicada`; rótulos de técnica sozinhos não bastaram.
- T013/T014: três pares próprios completos adicionados ao System; duas técnicas
  efetivas, tags e variável única conferidas, incluindo escape do JSON.
- T015/T016: revisão semântica dos seis grupos e comparação com entradas/referências
  do dataset → nenhum exemplo copiado nem fato inventado identificado; origem,
  fatos/dúvidas/recomendações, razões e trechos reais documentados no README.
- T017: gate US2 → 2 passed / 5 deselected; gate US1 repetido → 5 passed /
  2 deselected. Ambos saída 0. Sem inferência ou notas; detecção de pendências
  e negativos ainda serão consolidados na US3.

- T018: sexto método e detector Unicode implementados sobre todos os campos;
  controles de TODOS/todos/todo aprovam, tokens e colchetes de TODO/FIXME/TBD
  reprovam em System, User e metadados. Sem alteração do helper.
- T019: negativos compartilham as asserções dos seis métodos, usando `deepcopy`
  do YAML real; incluem persona/formato apenas nos exemplos, pares incompletos,
  1/4 pares, IDs duplicados/não sequenciais e técnicas duplicadas normalizadas.
- T020: carregador rejeita ausência/YAML inválido e raiz/definição incompatíveis;
  schema verifica seis campos, tipos, versão e listas. Helper recebe dados originais:
  só o falso positivo exato conhecido é desconsiderado; outros erros e retornos
  inesperados/incoerentes reprovam. Controles combinados e entrada intacta comprovados.
- T021: negativos de User, variável no System, variável extra, chaves desequilibradas
  e montagem incompatível reprovam pelos motivos previstos; logs/JSON escapados,
  relato vazio e instruções conflitantes preservam as duas mensagens na formatação.
- T022: tentativas controladas de socket/cliente/modelo bloqueadas; import fresco dos
  utilitários com dotenv desabilitado e guarda de abertura de `.env`, sem credenciais,
  aprovado. Não houve import de avaliador, chamada de modelo ou geração de notas.
- T023: fixture de módulo compara bytes e SHA-256 do YAML antes/depois da suíte;
  revisão confirmou cópias/temporários e seis verificações efetivas sem fallback.
- T024: `pytest tests/test_prompts.py --collect-only -q` → 188 coletados;
  `pytest tests/test_prompts.py -v -rA` → 188 passed, saída 0, zero skip/xfail.
  Durante o desenvolvimento, a primeira suíte completa teve 185 passed/2 failed:
  diagnóstico esperado do padrão Como e variável interna `PYTEST_CURRENT_TEST`.
  Ajustados somente diagnóstico e checagem do ambiente de teste; nova suíte passou.
  Após reforçar que o papel de visitante está explícito na entrada do exemplo 1,
  a coleta/execução integral foi repetida com os mesmos 188 aprovados.
- T025: fluxo offline, interpretação dos seis testes, limitações e continuidade
  nas specs 004/005 documentados em Como Executar, preservando o enunciado.
- T026: `pytest tests/test_preparation_checks.py tests/test_pull_prompts.py -q`
  → 266 passed, saída 0, sem chamadas remotas. Regressões da 001/002 preservadas.

- T027: V11 repetido → quatro protegidos e v1 com hashes originais; hashes
  canônicos dos 15 registros, inputs e referências também conferem individualmente.
  Distribuição preservada: simple=5, medium=7, complex=3. `git diff --check`
  aprovado; diff/status e YAML novo inspecionados. Sem arquivos secretos ou evidências
  dependentes de diretórios ignorados.
- T028: matriz FR-001–FR-009/SC-001–SC-005 auditada; V01–V12 aprovados conforme
  tabela abaixo. Seis métodos conferidos por AST e coleta, sem `pass`/skip/xfail.
  109 links locais existentes conferidos antes da consolidação final.
- T029: README consolida comandos e resultados, comparação qualitativa, técnicas,
  revisão semântica e limites. Publicação, notas reais, 3–5 ciclos e evidências
  públicas continuam nas 004/005/006. Nenhum resultado acadêmico foi presumido.
- T030: índice SDD, plano mestre, plano da 003 e estados de spec/quickstart
  atualizados com links para este registro. Ponteiro `.specify/feature.json`
  continua na 003, branch Git `dev`, sem iniciar publicação ou avaliação.
- Integração final: `pytest tests -q` → **454 passed**, saída 0 (188 v2 + 266
  regressões), sem skip/xfail. Executada para conferir os patches de fixtures na
  mesma sessão das suites anteriores, além dos comandos separados de V12.
- Hooks: `.specify/extensions.yml` ausente antes e depois da implementação;
  nenhum hook registrado a executar. Checklist `requirements.md` preservada, 16/16.

SHA-256 do artefato v2 validado:
`49ffb35893ae86769d22b555b9b0017e1910e08c49373e89a1931f58ec06c46d`.
Custos novos de inferência nesta spec: zero; nenhuma chamada remota.

### Aceite por verificação

| Gate | Resultado e evidência |
| --- | --- |
| V01 | PASS — schema, carregador, helper e negativos de campos/tipos |
| V02 | PASS — System real e negativos de ausência/brancos/tipos |
| V03 | PASS — persona/formato nas regras e negativos mantendo exemplos |
| V04 | PASS — três pares completos; pares/IDs/saídas inválidos rejeitados |
| V05 | PASS — marcadores em seis campos rejeitados; prosa comum aceita |
| V06 | PASS — duas técnicas demonstradas, duplicatas e ausências rejeitadas |
| V07 | PASS — negativos específicos e I1 sem alterar a entrada |
| V08 | PASS — duas mensagens, variável única e renderização literal |
| V09 | PASS — revisão dos seis grupos e três pares; zero fatos inventados identificados, sem cópia de referências |
| V10 | PASS — técnicas/trechos/razões, comparação e execução no README |
| V11 | PASS — quatro protegidos/v1 íntegros; 15 casos e referências 5/7/3 |
| V12 | PASS — 188 coletados/aprovados, 266 regressões e 454 juntos; zero skip/xfail |

SC-001 liga V04/V06; SC-002 liga V02–V07/V12; SC-003 liga V01/V08;
SC-004 liga V09; SC-005 liga V10. FR e tarefas correspondentes estão na matriz
acima. Todos satisfeitos no escopo local. Pronta para planejar a 004;
aprovação acadêmica depende das evidências reais futuras.

## Conferência da geração

Geradas 30 tarefas: Setup 2, Foundational 2, US1 7, US2 6, US3 8 e Polish 5.
A contagem dos campos do YAML foi corrigida de sete para seis na documentação de
planejamento, seguindo os campos já enumerados no contrato, sem mudar requisitos.
Conferidos os 30 checkboxes/IDs sequenciais, rótulos/caminhos, seis testes obrigatórios,
cobertura FR-001–FR-009/SC-001–SC-005, 87 links locais e sintaxe de dois blocos Bash.
Scripts de pré-requisitos confirmaram `tasks.md` e a 003 ativa. Quatro protegidos e
v1 permanecem iguais às referências; `git diff --check` aprovado.
`.specify/extensions.yml` ausente antes/depois: nenhum hook registrado para executar.
Essa conferência documental foi seguida pela análise SDD, que identificou I1.
Sua correção explicita o adaptador restrito e controles positivos/negativos em
C04/T018/T020. Na geração e correção documental, implementação e testes da v2
ainda estavam pendentes e nenhuma tarefa foi marcada como executada. A execução
posterior, com aceite local, está documentada no registro acima.
