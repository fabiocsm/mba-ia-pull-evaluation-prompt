# Recuperação fiel da v1 — spec 002

Registro de 2026-10-18 (America/Sao_Paulo). Implementação e aceite da 002 concluídos.
Fonte de requisitos: [spec](../specs/002-recuperar-prompt-v1/spec.md),
[contrato](../specs/002-recuperar-prompt-v1/contracts/recuperacao-v1.md) e
[guia V01–V12](../specs/002-recuperar-prompt-v1/quickstart.md).

## Baseline e pré-requisitos — T001–T004

Branch `dev`, árvore inicialmente limpa e ponteiro da 002 confirmados.
[Preparação](preparacao.md#matriz-atual) e [manifesto](integridade-inicial.json)
conferidos. V15 da 001 permanece reservado ao push da 004; não bloqueia o pull.
Venv existente ativado; Python 3.11.14, imports obrigatórios e `python -m pip check`
passaram (status 0). Pins preservados; nenhuma instalação necessária.
SHA-256 de 4/4 arquivos protegidos iguais ao manifesto; hashes canônicos de
15/15 casos, entradas e referências iguais; distribuição 5 simples/7 médios/3 complexos.
`.gitignore` cobre Python, venvs, credenciais e temporários; nenhuma inclusão necessária.
Não há configuração Docker, Node/publicação npm, Terraform ou Helm aplicável.

## Rastreabilidade e representação — T006

| Requisito | Verificação | Estado inicial |
| --- | --- | --- |
| FR-001/FR-002 → SC-001 | V01/V12: origem, flags, CLI, arquivo e pull real | pendente |
| FR-003 → SC-001 | V02–V05/V12: igualdade das mensagens e metadados | pendente |
| FR-004 → SC-003 | V02/V03/V12 e diff: sem melhoria/interpolação | pendente |
| FR-005/FR-006 → SC-002 | V04–V11: diagnóstico, status 1 e preservação | pendente |

YAML: raiz única `bug_to_user_story_v1`, textos literais System/Human,
`input_variables`, rótulo local `version: v1`, descrição/tags/data projetadas
somente quando devolvidas pelo repositório. `source` preserva identidade/revisão,
metadados/tags do template e snapshot integral do repositório com dois instantes UTC.
A revisão do objeto é `template_metadata.lc_hub_commit_hash`; o snapshot de
`get_prompt` é observado separadamente e pode apontar latest diferente.
Descrição/tags/data não são metadados históricos comprovados daquela revisão.

## Execuções e evidências

Pull real, comparação da revisão, hash local e V01–V12 comprovados abaixo.
A sequência registra também os estados e as falhas intermediárias.
Nenhuma nota ou experimento acadêmico é declarado por este registro.

### T005 — testes antes da implementação

`source venv/bin/activate; pytest tests/test_pull_prompts.py -q`: status 1,
6 falhas funcionais esperadas (CLI retorna 1/função False antes do fluxo),
coleta/imports concluídos. Cenários V01–V03 sintéticos; sem .env real ou rede.

### T007–T011 — US1 offline

`source venv/bin/activate; pytest tests/test_pull_prompts.py -q`: status 0,
6 testes aprovados (V01–V03). Comprovados origem/flags, bool/exit 0, Unicode,
espaços, quebras finais, chaves literais, variável repetida, round-trip seguro,
nulos/ausências opcionais e snapshot de latest independente da revisão recuperada.
Validação estrita e persistência atômica implementadas. Isso ainda não comprova SC-001 real.

### T012–T013 — recuperação real e V12

Pré-requisitos da COND-001 revalidados sem inferência: configuração presente,
handle `fabiocsm`, provider OpenAI, modelos `gpt-4.1-2025-04-14`, endpoint e
workspace/projeto autenticados conferidos (status 0). Ajuda instalada do CLI
consultada antes de workspace list/api settings; só saídas filtradas.

`source venv/bin/activate; python src/pull_prompts.py`: status 0.
Origem `leonanluppi/bug_to_user_story_v1`; revisão
`2950c33dbd7ffaed2e440b50adfd7769d183f90faf0bae5aa4864354f88e4073`;
destino `prompts/bug_to_user_story_v1.yml`, 1738 bytes.
`retrieved_at=2026-10-18T08:09:43.707861+00:00`
(05:09:43 em America/Sao_Paulo),
`repository_observed_at=2026-10-18T08:09:43.929044+00:00`.
SHA-256: `2cddcf8f8183b4d29a5bca4d4efca17601962aa98ac75323f7dabbfa905c0d70`.

Comparação V12 do quickstart executada em processo separado com revisão fixada,
status 0: mensagens 2/2 integralmente idênticas (100%), System/Human na ordem,
variáveis `['bug_report']`, metadados/tags do template e projeções de
descrição/tags/created_at conferidos. Último commit do snapshot coincide com
a revisão acima nesta observação; isso não transforma o snapshot em histórico.
Nenhuma melhoria ou substituição de variável foi feita (SC-001/SC-003 comprovados
na US1, sujeitos à conferência do código final). Sem chamada LLM, push ou experimento.

### T017 — matriz de falhas planejada para US2

| ID | Etapa/categoria planejada | Preservação esperada | Ação | Estado inicial |
| --- | --- | --- | --- | --- |
| V04 | Representação de mensagens/opções | ausência ou sentinela intacta | Rever representação | pendente |
| V05 | Metadados não representáveis | ausência ou sentinela intacta | Rever tipos sem coerção | pendente |
| V06 | Configuração incompleta/branca | sem criar cliente, destino intacto | Configurar variável | pendente |
| V07 | Acesso, origem, rede/get_prompt | ausência ou sentinela intacta | Conferir acesso/tentar depois | pendente |
| V08 | Diretório/temporário | ausência ou sentinela intacta | Conferir permissões | pendente |
| V09 | save_yaml falso/exceção/parcial | destino intacto; limpar temporário | Corrigir escrita | pendente |
| V10 | Releitura/reconstrução | destino intacto; limpar temporário | Corrigir round-trip | pendente |
| V11 | Substituição/limpeza | destino intacto; resíduo não é referência | Corrigir I/O/remover resíduo | pendente |

FR-005/FR-006 → SC-002 exigem todos esses cenários controlados aprovados.
Uma falha de comparação/documentação após commit é pendência de evidência,
não falha de persistência nem promessa de conservar a cópia anterior.

### T014–T020 — diagnóstico e preservação offline

Primeira execução após acrescentar US2: `pytest tests/test_pull_prompts.py -q --tb=no`,
status 1, **140 passaram/96 falharam**. As falhas apontaram diagnósticos genéricos
sem campo/categoria específica; a proteção já implementada na US1 permaneceu ativa.
Após classificação por etapa/categoria, uma execução mostrou 172 passaram/64 falharam:
os 64 casos restantes eram uma asserção de teste procurando `campo` em minúsculas,
enquanto o diagnóstico dizia `Campo:`. A asserção foi corrigida para o rótulo emitido,
sem remover verificações de segurança, conteúdo ou preservação.

Validação final: `source venv/bin/activate` e `pytest tests/test_pull_prompts.py -v`,
**status 0, 236 passaram**. Em seguida,
`pytest tests/test_preparation_checks.py tests/test_pull_prompts.py -q`,
**status 0, 266 passaram** (30 da preparação + 236 do pull).
As fixtures bloqueiam sockets e carregam apenas dotenv sintético; as falhas não
alteraram o destino real nem as credenciais locais. Mocks comprovam controles,
não substituem o pull e a comparação real de T012–T013.

| ID | Casos aprovados | Prova efetivamente executada |
| --- | ---: | --- |
| V01 | 2 | Origem/flags/destino, CLI 0 e função bool, snapshot JSON |
| V02 | 1 | Texto exato com acentos/espaços/quebras/chaves e variável duplicada |
| V03 | 3 | Opcionais ausentes/nulos/presentes, tags null, latest diferente |
| V04 | 64 | 32 incompatibilidades × destino ausente/sentinela: tipos, ordem/quantidade, placeholder, multimodal, parser/partials, formatos, opções internas, variáveis, identidade e revisão |
| V05 | 43 | 8 tipos inválidos × 2 locais × 2 destinos; 5 projeções inválidas × 2; snapshot simples extra preservado com aviso |
| V06 | 63 | Ausência/vazio/espaços, precedência dotenv, tracing efetivo/aliases, provider e chave Google; sucesso Google sem inferência |
| V07 | 38 | 6 classes de erro × 3 operações × 2 destinos; get_prompt None × 2; saída/log/HTTP sintéticos não expostos |
| V08 | 4 | mkdir/temporário falham, ambos os estados anteriores preservados |
| V09 | 6 | save_yaml False/exceção/parcial, stdout/stderr capturados |
| V10 | 8 | Releitura, divergência de dados/tipo bool→int e reconstrução falham |
| V11 | 4 | Replace/limpeza falham; resíduo explicitamente inválido |
| V12 | 1 comparação real | 2/2 mensagens da revisão fixada idênticas; variáveis e metadados conferidos |

Total offline: 236; V12 é prova remota separada, não incluída nessa contagem.
Para V04–V11, todos os cenários de falha são parametrizados com destino ausente e
sentinela YAML anterior; bytes anteriores/ausência, status 1, ausência de falso sucesso
e limpeza quando possível foram conferidos. Cada artefato de teste também foi
checado contra o marcador secreto sintético. A limpeza que falha deixa somente
um temporário identificado como resíduo, nunca uma v1 válida.

T018 alterou somente diagnóstico; T019 ampliou o tratamento da falha de limpeza.
Não houve mudança no caminho de sucesso/serialização após T013: sua prova remota
continua válida e não foi repetida desnecessariamente. A v1 e seu SHA-256 permaneceram
os mesmos. Nenhuma chamada LLM ou escrita remota foi feita nessa fase.

## Aceite consolidado e limites

| Requisito/critério | Implementação/tarefas | Evidência final |
| --- | --- | --- |
| FR-001 | Origem/flags, T010 | V01 e pull real T012 |
| FR-002 | Projeção/persistência/CLI, T008–T010/T021 | V01/V08 e V12; comando no README |
| FR-003 | Extração/metadados, T007–T008 | V02–V05 e V12 |
| FR-004 | Extração literal, T007–T008 | V02/V03, V12 e revisão do diff |
| FR-005 | Configuração/diagnóstico, T003/T010/T018 | V04–V11, saídas sanitizadas |
| FR-006 | Commit atômico/limpeza, T009/T019 | V06–V11, destino anterior preservado |
| SC-001 | T012/T013/T023 | Pull real e igualdade de 100% das 2 mensagens |
| SC-002 | T020/T023 | 100% dos cenários de falha definidos aprovados |
| SC-003 | T013/T023/T025 | Zero melhorias/substituições; apenas conteúdo recuperado e proveniência |

Versões da execução: CPython 3.11.14, langsmith 0.13.0, langchain-core 1.6.4,
python-dotenv 1.2.3, PyYAML 6.0.3, pytest 9.1.1. Execução em macOS/POSIX;
portabilidade Windows não foi testada. Não se promete coordenação de escritores
concorrentes ou durabilidade contra queda de energia.

O YAML anterior era ilustrativo: sua descrição/tags/data não tinham prova de origem.
O Hub devolveu descrição vazia, tag `ChatPromptTemplate` e data de criação
`2025-11-19T19:31:30.951363`; os campos foram preservados como retornados, sem
completar fuso ausente nem copiar `2025-01-15`. Texto e duplicação de `{bug_report}`
continuam originais. A apresentação YAML mudou (inclusive âncoras para listas
compartilhadas), mas os valores foram conferidos por safe_load e comparação remota.
A limitação de historicidade do snapshot é explicitada no CLI e neste registro.

Fontes de integração: [documentação oficial de prompts](https://docs.langchain.com/langsmith/manage-prompts-programmatically)
e inspeção das assinaturas/campos das versões instaladas, conforme a
[pesquisa da feature](../specs/002-recuperar-prompt-v1/research.md).
A documentação oficial descreve recuperação por revisão; o opt-in público e
as flags efetivas foram conferidos na assinatura local 0.13.0 e no teste V01.

Não há pendência conhecida no aceite da 002. V2, seis testes estruturais,
push público, experimentos/notas e evidências acadêmicas pertencem às specs 003–006
e permanecem pendentes. O estado ativo da 002 foi conservado até nova solicitação.

## Revisão final — T021–T025

Conferência em 2026-10-18T05:13:40-03:00: hashes de 4/4 protegidos, de 15/15
casos/entradas/referências e distribuição 5/7/3 iguais ao manifesto inicial.
Todos os pins instalados iguais a requirements.txt; suporte OpenAI/Google preservado.
Diff dos protegidos vazio e `git diff --check` status 0. Trinta e nove links locais
de README, índice e registro conferidos; valores das credenciais do ambiente/.env
procurados em memória nos arquivos alterados/novos, sem ocorrência nem divulgação.

Revisão dos artefatos executados (SHA-256):

- `src/pull_prompts.py`: `bfe9d6207dbe9066eb593f37cdb764109f5f158d322f9ac790254b95abe5a640`.
- `tests/test_pull_prompts.py`: `70e34d8560f4dd48c8f1d775d3d13336d5fd9fedfef7b2eafeadba8e409ca27a`.
- `prompts/bug_to_user_story_v1.yml`: `2cddcf8f8183b4d29a5bca4d4efca17601962aa98ac75323f7dabbfa905c0d70`.

As 25 tarefas foram auditadas contra as evidências e concluídas; checklist
de requisitos permaneceu intocado. `.specify/extensions.yml` ausente nas
conferências antes/depois da implementação: nenhum hook registrado a executar.
README e índice atualizados, sem alterar o enunciado acadêmico. Branch `dev` e
ponteiro da 002 preservados. Não houve commit/push Git, publicação de prompt,
criação/compartilhamento de dataset ou experimento nesta implementação.
