# Especificações do desafio

**Data:** 2026-10-18

**Estado:** seis especificações iniciais revisadas; planejamento, tarefas e análise
da 001 concluídos. Preparação implementada: 30/30 tarefas (incluindo duas de convergência), ambiente, integridade,
fork público, API key/contexto LangSmith, modelos com temperatura zero e tracing
comprovados. Reprodução automatizada em novo venv na mesma máquina concluída,
com ocorrência na conferência de traces registrada e resolvida por reconsulta.
Planejamento e geração de tarefas da 002 concluídos.
A análise da 002 foi realizada e seus achados I1/I2 corrigidos e revalidados:
sequência incremental de validação alinhada e caminho do contrato em T005 corrigido.
A 002 foi implementada e comprovada: pull real, comparação de 2/2 mensagens idênticas,
236 testes offline do pull e integridade preservada. Planejamento e geração de
tarefas da 003 concluídos; análise realizada com I1 corrigido e revalidado.
Ela foi implementada: 30/30 tarefas, 188 testes da v2 e
266 regressões aprovados, revisão semântica/documental e integridade conferidas.
O planejamento, as tarefas e a análise da 004 foram concluídos em 2026-10-18;
A1 corrigido e revalidado documentalmente. A 004 está implementada e comprovada: 35/35 tarefas, 437 testes de prompt/publicação e 266 regressões, escrita real e leitura pública/visual da revisão 4278de75. Em 2026-10-18 a 005 passou a ser a spec ativa e teve plano técnico e 35 tarefas concluídos ([plano](005-avaliar-iterar-v2/plan.md), [tarefas](005-avaliar-iterar-v2/tasks.md)) e duas análises SDD com achados corrigidos; Em 2026-10-19 a implementação da 005 foi concluída: 35/35 tarefas, 85 testes offline dos blocos de auditoria (817 na suíte), dataset `8c78638d-37a5-4175-9984-8db0e3473228` criado e auditado idêntico, três ciclos reais: `CIC-01` (revisão 4278de75, F1-Score 0.8057) e, por decisão do autor, `CIC-02` (25b881d1) e `CIC-03` (revisão 36a96c05, experimento `d864cfbb-6ab9-4901-ab06-62f68ccd96fc`) completo, vinculado e aprovado pela regra integral (média geral 0.8709; menor média F1-Score 0.8474), com custo estimado acumulado de US$ 0,76 ([registro](../docs/avaliacao-v2.md)). A spec 006 e as evidências públicas permanecem pendentes. Evidências e limites nos registros de
[preparação](../docs/preparacao.md) e [recuperação](../docs/recuperacao-v1.md).

O [plano da 001](001-preparar-experimentos/plan.md) detalha a Fase 1 do plano mestre,
com pesquisa, modelo dos registros, contrato operacional e guia de validação.
O [plano da 002](002-recuperar-prompt-v1/plan.md) detalha a recuperação fiel da v1,
com [pesquisa](002-recuperar-prompt-v1/research.md),
[modelo de dados](002-recuperar-prompt-v1/data-model.md),
[contrato](002-recuperar-prompt-v1/contracts/recuperacao-v1.md) e
[guia de validação](002-recuperar-prompt-v1/quickstart.md). A execução e a comparação
real estão comprovadas no registro de recuperação acima.
O [plano da 003](003-otimizar-validar-v2/plan.md) detalha as Fases 3–4, com
[pesquisa](003-otimizar-validar-v2/research.md),
[modelo de dados](003-otimizar-validar-v2/data-model.md),
[contrato](003-otimizar-validar-v2/contracts/otimizacao-v2.md) e
[guia de validação](003-otimizar-validar-v2/quickstart.md). Entrega três exemplos próprios,
Few-shot Learning e Role Prompting, os seis testes efetivos e negativos offline,
preservando a v1 e separando validação local de publicação/avaliação.
As [30 tarefas da 003](003-otimizar-validar-v2/tasks.md), concluídas, cobrem
Setup (2), Foundational (2), US1 (7), US2 (6), US3 (8) e revisão final (5).
Os seis testes obrigatórios são introduzidos por história e consolidados com
negativos na US3; seis marcadores de paralelismo formam três pares sem conflito
de escrita. A análise SDD identificou I1 (falso positivo de TODO no helper);
o contrato e T018/T020 agora definem o adaptador restrito e controles de regressão,
preservando `src/utils.py`. O adaptador e seus controles passaram na implementação;
comandos, resultados e limites no [registro da 003](003-otimizar-validar-v2/tasks.md#registro-de-execução).
A v2 está pronta localmente. O [plano da 004](004-publicar-prompt-v2/plan.md)
detalha a Fase 5, com [pesquisa](004-publicar-prompt-v2/research.md),
[modelo de dados](004-publicar-prompt-v2/data-model.md),
[contrato](004-publicar-prompt-v2/contracts/publicacao-v2.md) e
[guia de validação](004-publicar-prompt-v2/quickstart.md). Define validação antes
da escrita, metadados suportados pelo SDK, revisão exata e acesso anônimo,
distinguindo confirmação de publicação de conferência completa. O plano foi
concluído sem implementação naquela etapa; publicação/conferência foram executadas posteriormente, sem chamadas LLM. Métricas continuam pendentes.
As [35 tarefas da 004](004-publicar-prompt-v2/tasks.md) foram geradas: Setup (2),
Foundational (2), US2 (8), US1 (10), US3 (7) e revisão final (6). US2 e US1 são
P1, com rejeição de artefatos inválidos antes da escrita; US3 P2 completa vínculo
local/revisão e invalidação. Seis marcadores de paralelismo formam três pares em
arquivos distintos. Testes são offline e as provas reais de publicação/acesso
foram obtidas na integração final. Todas as tarefas foram concluídas. A análise SDD
da 004 identificou A1: o retorno zero do CLI depende de verificações automatizadas;
a inspeção visual posterior e seu registro completam o aceite da 004 antes da
entrega à 005. A correção está no contrato e em T014/T019/T026/T032–T034, com
revalidação documental no [registro de A1](004-publicar-prompt-v2/tasks.md#correção-da-análise--a1).
As [25 tarefas da 002](002-recuperar-prompt-v1/tasks.md), concluídas, cobrem
Setup (2), Foundational (2), US1 (9), US2 (7) e revisão final (5). Elas separam
validação offline de falhas e comprovação real da fidelidade da v1.
As 30 tarefas da 001, incluindo duas de convergência, cobrem as três histórias, os pré-requisitos e a revisão final.
A criação desses artefatos não comprova prontidão. A execução registrada agora comprova
instalação/pip check/imports, contratos SDK, comparação com origem, 15 casos e fork público;
modelos foram selecionados documentalmente e comprovados em quatro chamadas reais,
duas iniciais e duas na reprodução, com quatro traces no projeto/workspace esperado.
Os achados I1, A1 e I2 da análise da 001 foram corrigidos: seleção de modelos antes
da validação da configuração, distinção entre contexto comprovado e projeto ainda
ausente, e remoção do caractere isolado no plano. Dependências e rastreabilidade
foram atualizadas antes da implementação; os resultados atuais estão no registro acima.

## Avaliação do plano e decisão de divisão

O [plano mestre](../plan/plano-implementacao.md) cobre os requisitos do
[README](../README.md) e os cinco princípios da
[constituição v1.0.0](../.specify/memory/constitution.md). Sua sequência preserva os
materiais fornecidos, separa validação estrutural de avaliação real e prevê auditoria
dos resultados e acesso público às evidências. Não foi identificado conflito que exija
alterar o enunciado ou a constituição para produzir estas especificações.

O plano mistura pré-requisitos, decisões técnicas, trabalho de implementação e
critérios de entrega. Para torná-lo executável por etapas SDD, a divisão abaixo:

- Trata a preparação como entrega verificável de prontidão e integridade, sem presumir
  credenciais válidas, acesso aos modelos ou instalação concluída.
- Mantém prompt e testes estruturais na mesma spec: o artefato otimizado só está pronto
  para publicação quando suas seis verificações são efetivas.
- Mantém experimento e iterações na mesma spec: análise, ajuste, teste, publicação e
  nova avaliação formam um ciclo, sem duplicar regras de aceite entre features.
- Reserva a entrega pública para uma spec própria: aprovação em ambiente privado
  não comprova acesso às evidências nem reprodução pelo avaliador.
- Mantém os detalhes obrigatórios de arquivos, configuração e ferramentas neste
  índice e nas fontes normativas; as specs descrevem comportamentos e resultados.

Pontos que o planejamento técnico deve manter explícitos:

1. As cinco médias e a média geral precisam atingir `0.8` em experimento completo:
   15 respostas e 75 feedbacks válidos. Não se cria limiar obrigatório por exemplo.
2. Planejar 3–5 ciclos não garante aprovação. Aprovação antecipada deve ser justificada;
   reprovação após cinco ciclos permanece pendente e exige continuidade planejada.
   Essa interpretação já consta no plano e não elimina o registro das iterações reais.
3. A spec 001 reconsultou fontes oficiais e selecionou `gpt-4.1-2025-04-14` nos dois
   papéis; compatibilidade documental com temperatura zero não comprova acesso da conta.
   As duas chamadas iniciais e sua reprodução passaram, com traces verificados.
4. Comparação qualitativa v1/v2 é obrigatória. Baseline numérica da v1 é opcional e
   exige experimento real adicional; os números ilustrativos do README não a substituem.
5. Uma execução não deve alterar o prompt publicado enquanto ele estiver sendo avaliado.
   Toda edição posterior exige teste, nova publicação e nova avaliação.

## Catálogo e dependências

Cada linha corresponde a uma aplicação separada de `$speckit-specify`, com uma única
feature. O campo `Input` de cada `spec.md` guarda a descrição usada nessa aplicação.
Os diretórios seguem a numeração sequencial configurada em `.specify/init-options.json`.

| Ordem | SPECIFY_FEATURE_DIRECTORY | SPEC_FILE | Qualidade | Fase de origem | Dependência para executar |
| --- | --- | --- | --- | --- | --- |
| 001 | `specs/001-preparar-experimentos` | [Preparação reproduzível](001-preparar-experimentos/spec.md) | [16/16](001-preparar-experimentos/checklists/requirements.md) | 1 | Nenhuma |
| 002 | `specs/002-recuperar-prompt-v1` | [Recuperação fiel da v1](002-recuperar-prompt-v1/spec.md) | [16/16](002-recuperar-prompt-v1/checklists/requirements.md) | 2 | 001 |
| 003 | `specs/003-otimizar-validar-v2` | [Otimização e testes da v2](003-otimizar-validar-v2/spec.md) | [16/16](003-otimizar-validar-v2/checklists/requirements.md) | 3–4 | 002 e ambiente de 001 |
| 004 | `specs/004-publicar-prompt-v2` | [Publicação pública da v2](004-publicar-prompt-v2/spec.md) | [16/16](004-publicar-prompt-v2/checklists/requirements.md) | 5 | 001 e 003 |
| 005 | `specs/005-avaliar-iterar-v2` | [Avaliação e iterações](005-avaliar-iterar-v2/spec.md) | [16/16](005-avaliar-iterar-v2/checklists/requirements.md) | 6–7 | 001, 003 e 004 |
| 006 | `specs/006-entregar-evidencias-publicas` | [Evidências e entrega pública](006-entregar-evidencias-publicas/spec.md) | [16/16](006-entregar-evidencias-publicas/checklists/requirements.md) | 8 | 001 e aprovação em 005 |

Essas dependências governam a execução, não impedem planejar as specs antes de os
acessos externos serem comprovados. A estrutura documental da 006 pode ser preparada
antecipadamente, mantendo resultados não obtidos como pendências.

## Matriz de cobertura do plano mestre

Os IDs R01–R18 são preservados da seção 6 do plano. Os IDs FR/SC são locais a cada
spec: uma referência como `003/FR-007` identifica a spec e seu requisito. As checklists
registram também a correspondência entre histórias, requisitos e resultados.

| Requisito | Responsabilidade e requisitos da spec | Critério de verificação |
| --- | --- | --- |
| R01 — Stack e ambiente | 001/FR-008 | 001/SC-001 e SC-004; instalação e preparação reproduzíveis |
| R02 — Credenciais e handle | 001/FR-001–FR-005 | 001/SC-001 e SC-002; prontidão sem exposição de segredos |
| R03 — Pull e v1 local | 002/FR-001–FR-006 | 002/SC-001–SC-003; fidelidade e falhas explícitas |
| R04 — V2 preenchida | 003/FR-001, FR-008–FR-009 | 003/SC-002 e SC-003; artefato completo e entrada compatível |
| R05 — Técnicas obrigatórias | 003/FR-004–FR-005, FR-007 | 003/SC-001 e SC-002; exemplos próprios e técnicas verificadas |
| R06 — Regras e mensagens | 003/FR-002–FR-003, FR-008 | 003/SC-003 e SC-004; estrutura, casos de borda e entrada única |
| R07 — Push público | 004/FR-001–FR-007 | 004/SC-001–SC-004; metadados, acesso, revisão e equivalência |
| R08 — Experimento real | 005/FR-001–FR-003, FR-005 | 005/SC-001 e SC-003; 15 respostas e 75 notas válidas |
| R09 — Aprovação integral | 005/FR-004 | 005/SC-002; cinco métricas e média geral >= 0.8 |
| R10 — Iterações | 005/FR-007–FR-010 | 005/SC-003 e SC-005; histórico e revisão final correspondente |
| R11 — Seis testes | 003/FR-007–FR-009 | 003/SC-002; execução real e detecção dos defeitos respectivos |
| R12 — Materiais protegidos | 001/FR-006, 002/FR-004, 005/FR-001–FR-002 e FR-010, 006/FR-009 | 001/SC-003 e 006/SC-005; integridade inicial/final e preservação durante os ciclos |
| R13 — OpenAI e Gemini | 001/FR-004, 006/FR-009 | 001/SC-001 e 006/SC-005; suporte existente conservado |
| R14 — Técnicas documentadas | 003/FR-006, 006/FR-005 | 003/SC-005 e 006/SC-003; justificativas e exemplos reais |
| R15 — Resultados e comparação | 006/FR-002 e FR-005–FR-006 | 006/SC-002 e SC-003; notas reais, screenshots e comparação |
| R16 — Como Executar | 001/FR-009, 006/FR-007 e FR-010 | 001/SC-004 e 006/SC-004; roteiro conferido em ambiente limpo |
| R17 — Dataset e traces públicos | 005/FR-001, FR-003 e FR-006, 006/FR-001–FR-004 | 005/SC-001 e SC-004, 006/SC-001 e SC-002; acesso sem login e três dificuldades |
| R18 — Fork público | 001/FR-007, 006/FR-008–FR-009 | 001/SC-001 e 006/SC-005; origem, visibilidade e conteúdo final |

R12, R13, ausência de segredos e integridade das evidências são restrições transversais
de todas as specs, mesmo quando a comprovação formal pertence à 001 ou à 006.

## Contratos técnicos a preservar nos planos de cada spec

Estes contratos vêm do README, da constituição e do plano mestre; não são escolhas novas.

| Spec | Contratos obrigatórios para o planejamento e a implementação posteriores |
| --- | --- |
| 001 | Python 3.10+; criar e ativar `venv` antes de instalar `requirements.txt`; conferir dependências com `python -m pip check`; LangChain, LangSmith, Prompt Hub, YAML e pytest; registrar referência Git e hashes dos quatro arquivos protegidos; consultar documentação oficial ao escolher modelos compatíveis com `temperature=0`. |
| 002 | Implementar `src/pull_prompts.py`, preservando seus contratos; usar `langsmith.Client` e `dangerously_pull_public_prompt=True`; origem `leonanluppi/bug_to_user_story_v1`; persistir a definição `bug_to_user_story_v1` em `prompts/bug_to_user_story_v1.yml` com `save_yaml`; não interpolar `{bug_report}` ou omitir mensagens. |
| 003 | Criar `prompts/bug_to_user_story_v2.yml`, definição `bug_to_user_story_v2`, com `description`, `system_prompt`, `user_prompt`, `version: v2`, `tags`, `techniques_applied`; montar mensagens System/User compatíveis com `ChatPromptTemplate`, cuja única variável é `bug_report`; implementar os seis testes abaixo em `tests/test_prompts.py`; executar `pytest tests/test_prompts.py -v`. |
| 004 | Implementar `validate_prompt()`, `push_prompt_to_langsmith()` e `main()` em `src/push_prompts.py`; reutilizar os utilitários existentes; ler `USERNAME_LANGSMITH_HUB` da configuração, sem fixar o username no código; publicar `fabiocsm/bug_to_user_story_v2` com `is_public=True`; descrição, tags e técnicas nos metadados suportados; conferir round-trip e registrar revisão do Hub, URL e hash local. |
| 005 | Executar `python src/evaluate.py` sem alterações; dataset remoto `{LANGSMITH_PROJECT}-eval`, idêntico ao JSONL; manter a concorrência e a agregação originais; registrar 15 respostas, 75 feedbacks, cinco médias e média geral, revisão do Hub e hash local, provedor/modelos, data e ID/URL de cada experimento. |
| 006 | Preservar o enunciado e acrescentar as três seções obrigatórias ao README; usar `Client.share_dataset` para o link público, guardando e reutilizando o endereço já gerado; evidências em `docs/evidencias/` ou URLs públicas estáveis; conferir acesso sem login e fork público com código, YAML e documentação. |

Configuração a conferir antes das operações correspondentes: `LANGSMITH_API_KEY`,
`LANGSMITH_PROJECT`, `USERNAME_LANGSMITH_HUB=fabiocsm`, `LANGSMITH_TRACING=true`,
`LLM_PROVIDER`, `LLM_MODEL`, `EVAL_MODEL` e `OPENAI_API_KEY` ou `GOOGLE_API_KEY`.
OpenAI é a opção inicial. Reutilizar a chave existente sem expor seu valor; conservar
Gemini. O LangSmith CLI é apoio: consultar a ajuda instalada antes de seus subcomandos,
configurar explicitamente a autenticação e não presumir leitura automática do `.env`.

Os seis testes obrigatórios pertencem à spec 003:

| Nome | Condição efetiva no YAML v2 real |
| --- | --- |
| `test_prompt_has_system_prompt` | System existe, é texto e não contém apenas espaços. |
| `test_prompt_has_role_definition` | A persona está explícita no conteúdo de System. |
| `test_prompt_mentions_format` | Há instrução de Markdown ou User Story padrão. |
| `test_prompt_has_few_shot_examples` | Há pares completos próprios de entrada/saída; o nome da técnica sozinho não basta. |
| `test_prompt_no_todos` | Não há marcadores de pendência, incluindo `[TODO]`. |
| `test_minimum_techniques` | Há pelo menos duas técnicas distintas nos metadados, incluindo Few-shot. |

Não alterar `src/evaluate.py`, `src/metrics.py`, `src/utils.py` ou
`datasets/bug_to_user_story.jsonl`. Conservar os 15 exemplos e referências, a
distribuição 5/7/3, fórmulas e suporte a ambos os provedores. Divergência com um contrato
deve ser registrada e resolvida antes de qualquer proposta de mudança nesses materiais.

## Artefatos iniciais e continuação do SDD

Na especificação inicial foram criados `spec.md` e `checklists/requirements.md` por
feature, além deste índice. A 001 e a 002 também têm planejamento e tarefas;
a 003 tem os cinco artefatos de planejamento e `tasks.md` listados acima;
a 004 tem os cinco artefatos de planejamento e `tasks.md`, com 35 tarefas concluídas.
As descrições estão nos campos `Input`. O template ativo foi resolvido pela
pilha local do Spec Kit e suas seções obrigatórias foram mantidas, com premissas e
dependências. A revisão de cada checklist registra 16/16 itens de qualidade atendidos,
sem dúvidas bloqueantes; isso não significa implementação ou avaliação concluída.

Não existe `.specify/extensions.yml`: os hooks antes e depois de cada aplicação
foram verificados e não havia hooks a executar. Nenhuma branch foi criada ou trocada;
`dev` é a branch de trabalho existente, independente dos diretórios de spec.

O ponteiro local `.specify/feature.json` foi atualizado em cada aplicação e agora
seleciona `specs/005-avaliar-iterar-v2`, conforme solicitação do autor. Esse
arquivo é ignorado pelo Git por ser estado local. Para selecionar explicitamente uma
spec antes da próxima skill, use a raiz do repositório e a variável reconhecida pelos
scripts locais:

```bash
export SPECIFY_FEATURE_DIRECTORY=specs/005-avaliar-iterar-v2
# Em seguida, invocar $speckit-implement nesta conversa para essa feature.
```

Troque o valor pelo diretório da spec desejada; não presuma que a branch seleciona a
feature. Prossiga com `$speckit-plan`, `$speckit-tasks` e `$speckit-analyze` por feature,
antes de `$speckit-implement`, respeitando as dependências de execução. Use
`$speckit-clarify` apenas se aparecer lacuna que altere escopo ou aceite. Planos e
tarefas das specs 005–006 ainda não foram gerados. A 001 e a 002 foram concluídas
com a baseline preservada; a 003 também foi implementada. O planejamento da 004
e a geração de tarefas foram concluídos em 2026-10-18; a análise identificou A1,
corrigido e revalidado documentalmente. Seus requisitos estão rastreados no
plano/contrato/guia e nas 35 tarefas concluídas, com tentativas e ajustes registrados.
A feature ativa passou a ser a 005, selecionada explicitamente pelo autor, sem trocar `dev`.
A implementação da 004 foi concluída. A 005 foi selecionada explicitamente como feature ativa e seu
[plano](005-avaliar-iterar-v2/plan.md) foi concluído com [pesquisa](005-avaliar-iterar-v2/research.md),
[modelo de dados](005-avaliar-iterar-v2/data-model.md),
[contrato](005-avaliar-iterar-v2/contracts/avaliacao-v2.md) e
[guia de validação](005-avaliar-iterar-v2/quickstart.md): dataset auditado antes do primeiro
experimento, vínculo por commit do Hub em cada run, 75 notas válidas sem zeros de falha
dos juízes, regra integral e 3–5 ciclos com gate de custo. As [35 tarefas da 005](005-avaliar-iterar-v2/tasks.md) foram geradas em 2026-10-18:
Setup (3), Foundational (2), US1 (12), US2 (4), US3 (9) e Polish (5). A análise SDD da 005 encontrou 11 achados
(1 CRITICAL: inspeção no dashboard das novas revisões), todos corrigidos e registrados
em [correção da análise](005-avaliar-iterar-v2/tasks.md#correção-da-análise--2026-10-18).
A segunda análise encontrou 9 achados (1 HIGH: gate sem conferir dataset/workspace e
executado antes do dataset), todos corrigidos em
[segunda correção](005-avaliar-iterar-v2/tasks.md#segunda-correção-da-análise--2026-10-18);
commits locais por ciclo autorizados pelo autor. Próxima etapa: `$speckit-implement` da 005. [Evidências e gate à avaliação](../docs/publicacao-v2.md).
A reprodução da 001 usa um executor Python separado na mesma máquina; não equivale
a revisão humana independente nem comprova portabilidade para outro SO.
A Fase 0 do plano mestre permanece parcialmente pendente.
