# Implementation Plan: Prompt otimizado e validação estrutural efetiva

**Branch**: `dev` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

**Input**: `specs/003-otimizar-validar-v2/spec.md`, Fases 3–4 e
R04/R05/R06/R11/R12/R14 do [plano mestre](../../plan/plano-implementacao.md).

**Estado**: planejamento, tarefas e análise SDD concluídos; achado I1 corrigido no
desenho e revalidado. Implementação concluída localmente: 30/30 tarefas,
188 testes da v2 e 266 regressões aprovados. Evidências no
[registro de execução](tasks.md#registro-de-execução); publicação e notas pendentes.
O setup retornou `BRANCH=003-otimizar-validar-v2` como identificador da feature;
a branch Git continua `dev`. O ponteiro local `.specify/feature.json` seleciona
`specs/003-otimizar-validar-v2`. Nenhuma branch foi criada ou trocada.

## Summary

Criar `prompts/bug_to_user_story_v2.yml` para converter relatos em User Stories
fundamentadas, em português e Markdown, com critérios verificáveis. Partir da
v1 realmente recuperada pela 002, preservando-a: ela repete `{bug_report}` nas
duas mensagens e não define formato, exemplos ou tratamento de informação ausente.

Aplicar Few-shot Learning com três exemplos próprios completos e Role Prompting
com persona de produto; manter regras e exemplos em System e somente o relato
em User. Definir estrutura proporcional à complexidade, sem declarar Skeleton
of Thought apenas por usar títulos. Não inventar fatos nem executar instruções
contidas no relato. Validar o YAML real, os seis testes obrigatórios e a montagem
de `ChatPromptTemplate` sem rede. Acrescentar justificativas e trechos efetivos
na seção `Técnicas Aplicadas (Fase 2)` do README, preservando o contrato acadêmico.

Fora do escopo: alterar pull, implementar push, publicar prompt, executar LLM,
experimentos ou compartilhamento público. As specs 004/005/006 continuam responsáveis
por essas provas. Sucesso estrutural não é aprovação nas cinco métricas.

## Technical Context

**Language/Version**: Python 3.10+; ambiente existente CPython 3.11.14 em `venv/`.

**Primary Dependencies**: pins existentes `langchain-core==1.6.4`,
`pyyaml==6.0.3`, `pytest==9.1.1`; utilitários `load_yaml` e
`validate_prompt_structure` reutilizados sem alteração. `langsmith==0.13.0` e
providers continuam instalados, mas nenhum cliente remoto é necessário nesta spec.
Biblioteca padrão para caminhos, expressões regulares e cópias de dados de teste.

**Storage**: um YAML UTF-8 versionado, metadados e exemplos dentro da definição
`bug_to_user_story_v2`; documentação versionada no README e nesta pasta SDD.
Sem banco ou novo formato intermediário de prompt.

**Testing**: implementar os seis métodos existentes em `tests/test_prompts.py`,
com fixture que lê o arquivo real e helpers de asserção locais. Acrescentar nesse
mesmo arquivo testes de contrato e defeitos isolados em cópias em memória ou
temporários. Verificar rejeição efetiva sem modificar o YAML versionado, executar
sem rede e sem exigir credenciais. Revisão semântica complementa as verificações
sintáticas; pytest não comprova comportamento de um modelo.

**Target Platform**: execução local da raiz do repositório; ambiente comprovado
macOS/POSIX. Resolver caminhos dos testes por `Path(__file__)`, sem alegar prova
em sistemas ainda não usados.

**Project Type**: artefato de prompt consumido pelos scripts CLI existentes.

**Performance Goals**: validação offline sem chamadas a modelos, custo de inferência
zero nesta etapa. Três exemplos concisos, sem meta artificial de latência ou tokens.
As 3–5 iterações e estimativa global de US$ 1–5 continuam previstas na spec 005;
o tamanho da v2 deve ser considerado no custo dos experimentos futuros.

**Constraints**: única variável `bug_report`, System/User separados, `version: v2`,
campos completos, nenhum marcador de pendência. Não alterar a v1, os quatro
materiais protegidos, os 15 exemplos/referências (5/7/3), métricas ou providers.
Exemplos próprios, sem copiar referências ou instruir juízes a elevar notas.

**Scale/Scope**: um prompt, três pares de exemplo, seis verificações obrigatórias,
casos negativos e de template, documentação de duas técnicas. A condição
`COND-001` da [preparação](../../docs/preparacao.md#condição-experimental)
é apenas referência para a 005: OpenAI, geração/avaliação
`gpt-4.1-2025-04-14`, temperatura zero. Não há seleção ou nova chamada de modelo
nesta spec; revalidar documentação e acesso antes da execução correspondente.

## Constitution Check

Gate avaliado antes da pesquisa e reavaliado após o desenho. A implementação
foi conferida contra essas regras; resultados locais no registro de execução.
PASS não representa aprovação nas métricas reais.

| Regra | Antes da Fase 0 | Após a Fase 1 |
| --- | --- | --- |
| I — Integridade/escopo | PASS: v2, testes e documentação | PASS: v1 e quatro protegidos somente leitura; hashes conferidos no guia |
| II — Engenharia verificável | PASS: persona, Few-shot, formato e bordas | PASS: três pares completos, duas técnicas reais, entrada única e matriz de bordas |
| III — Rastreabilidade | PASS: v1 recuperada disponível | PASS: origem/revisão citadas; entrega local para 004, sem alegar publicação |
| IV — Avaliação íntegra | PASS: sem avaliações nesta etapa | PASS: zero notas fabricadas; cinco métricas e média >= 0.8 reservadas à 005 |
| V — Reprodução | PASS: seis testes efetivos previstos | PASS: artefato real, defeitos controlados, README e guia offline |
| Stack/configuração | PASS: ambiente da 001 e pins preservados | PASS: ChatPromptTemplate/utilitários existentes; nenhuma credencial exigida para pytest |

Nenhuma violação ou dúvida bloqueante identificada. A recuperação da 002 está
comprovada em [docs/recuperacao-v1.md](../../docs/recuperacao-v1.md), revisão
`2950c33dbd7ffaed2e440b50adfd7769d183f90faf0bae5aa4864354f88e4073`.
Incompatibilidade futura deve ser registrada antes de alterar um contrato protegido.

## Project Structure

### Documentation (this feature)

```text
specs/003-otimizar-validar-v2/
├── spec.md
├── checklists/requirements.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/otimizacao-v2.md
├── quickstart.md
└── tasks.md
```

As [30 tarefas](tasks.md) foram geradas por `$speckit-tasks` em 2026-10-18:
Setup (2), Foundational (2), US1 (7), US2 (6), US3 (8) e revisão final (5).
Todas foram executadas e marcadas `[X]`; I1 está implementado com controles
positivos/negativos, preservando o helper. Próximo trabalho: planejar a 004.

### Source Code (repository root)

```text
prompts/bug_to_user_story_v1.yml     # referência recuperada, somente leitura
prompts/bug_to_user_story_v2.yml     # criado e validado localmente
tests/test_prompts.py               # seis métodos + contratos/negativos aprovados
README.md                           # técnicas, comparação qualitativa e execução local
src/utils.py                        # reutilizar load_yaml/validate_prompt_structure
src/push_prompts.py                 # consumidor futuro, implementação na 004
src/evaluate.py                     # consumidor futuro, protegido
```

**Structure Decision**: manter o formato e os scripts existentes. Asserções auxiliares
ficam no próprio módulo de testes; não criar serviço, framework de validação ou
camada de produção nova. Validação de publicação permanece em `validate_prompt()`
na 004, orientada pelo contrato desta spec, sem importar código de teste.

## Phase 0 — Pesquisa e decisões

[research.md](research.md) resolve representação dos exemplos, técnicas, montagem
das mensagens, limites dos helpers e comprovação negativa. A pesquisa de validação
foi delegada conforme a skill; fontes são requisitos e código local dos pins
instalados, com ensaio offline de chaves literais. Sem acesso a `.env`, Hub ou LLM.

## Phase 1 — Desenho e sequência de execução

1. Conferir v1/hash contra o registro da 002 e protegidos contra o manifesto da 001.
   Registrar diagnóstico qualitativo da semente, sem regravá-la ou repetir o pull.
2. Criar os seis campos obrigatórios da v2, persona e regras de comportamento.
   System contém contexto/regras/exemplos; User contém apenas `{bug_report}`.
3. Definir saída: User Story e critérios; contexto somente quando informado;
   dúvidas/recomendações identificadas e somente quando úteis. Para insuficiência
   impeditiva, explicitar lacunas e pedir esclarecimentos sem história inventada.
4. Escrever três exemplos próprios: simples suficiente; incompleto/ambíguo;
   múltiplos problemas com log e instrução conflitante como dados. Revisar entrada
   e saída para cobertura e ausência de fatos sem fundamento. Não copiar referências.
5. Implementar os seis testes preservando nomes e coleta. Complementar tipos/campos,
   técnicas distintas, exemplos delimitados e montagem/renderização offline. Cada
   defeito deve acionar a asserção específica, não uma falha incidental de fixture.
6. Exercitar negativos em cópias isoladas e o contrato de variável/chaves. Executar
   suíte da v2 e regressão existente; conferir coleta, ausência de skip/xfail e hashes.
7. Documentar duas técnicas com trechos reais, diagnóstico v1/v2 e comandos locais
   no README. Publicação e métricas permanecem explicitamente pendentes.
8. Entregar à 004 apenas após o aceite local: YAML, metadados, testes, revisão
   qualitativa e documentação coerentes. Toda edição futura exige repetir testes,
   publicar e avaliar nas specs correspondentes.

Campos em [data-model.md](data-model.md), interfaces e invariantes em
[contracts/otimizacao-v2.md](contracts/otimizacao-v2.md), verificações V01–V12 em
[quickstart.md](quickstart.md). O plano encerra na Fase 1 de design.

## Rastreabilidade e aceite

| Requisito | Plano mestre | Decisão/artefato | Verificação / critério |
| --- | --- | --- | --- |
| FR-001 | R04 | Seis campos e identidade YAML | V01/V08; SC-002/SC-003 |
| FR-002 | R06 | Persona, PT-BR, Markdown, história e critérios | V03/V09; SC-004 |
| FR-003 | R06/R12 | Seis bordas, fatos/dúvidas/recomendações | V09; SC-004 |
| FR-004 | R05 | Três pares próprios e persona | V04/V09; SC-001/SC-004 |
| FR-005 | R05 | Few-shot Learning + Role Prompting distintas | V06/V10; SC-001/SC-005 |
| FR-006 | R14 | Seção do README com razão e trechos reais | V10; SC-005 |
| FR-007 | R11 | Seis testes reais + negativos correspondentes | V02–V07; SC-002 |
| FR-008 | R04/R06 | System/User e única variável bug_report | V08; SC-003 |
| FR-009 | R04/R11 | Validação local sem equivalência a métricas | V01/V05/V08/V12; SC-002/SC-003 |
| Restrição transversal | R12/R13 | v1, protegidos, dataset e providers intactos | V11/V12 |

## Complexity Tracking

Sem violações a justificar. Asserções locais complementam o helper protegido, que
não cobre o contrato completo; não é necessário modificar `src/utils.py`.

### Correção da análise — I1

O helper protegido considera `TODOS` uma ocorrência de TODO. C04 define um
adaptador local: detectar marcadores delimitados nos campos textuais; chamar o
helper sobre os dados originais; desconsiderar apenas o diagnóstico exato de TODO
se não há marcador real no System. Qualquer outro erro ou retorno inesperado
continua reprovando. Não sanitizar o prompt nem alterar o helper.

T018/T020 exigem controles positivos de prosa comum, marcadores reais e falso
positivo combinado com outro defeito. A política foi conferida offline na correção;
a implementação do adaptador e seus testes pytest ainda estavam pendentes nesse
ensaio; agora estão comprovados no registro de execução.

Revalidação de I1 em 2026-10-18: 13 cenários da política passaram em ensaio em
memória, com entrada intacta (três palavras comuns, seis marcadores, marcador em
User/tags e dois casos com outro erro); dois retornos inesperados/incoerentes
também foram rejeitados. O ensaio executou a função extraída por AST do helper
existente, sem importar seus efeitos dotenv, alterar arquivos ou chamar rede/LLM.
Não equivale à implementação ou execução dos testes da v2. Conferidos ainda os
87 links locais, formato das 30 tarefas pendentes, sintaxe dos blocos Bash e
integridade dos quatro protegidos/v1; `git diff --check` aprovado.

## Conferência do planejamento

Artefatos de pesquisa e desenho concluídos, sem esclarecimentos pendentes.
`.specify/extensions.yml` ausente nas verificações antes/depois: nenhum hook
registrado para executar. Pré-requisitos e resolução de paths sem override de
ambiente confirmaram a 003 ativa; a branch Git permanece `dev`.

Conferidos 72 links locais em sete documentos e a sintaxe de sete blocos de comandos,
incluindo o Python embutido no guia. `git diff --check` aprovado; quatro protegidos
iguais ao manifesto da 001 e v1 igual ao hash da recuperação da 002. Na conferência do planejamento, testes da v2 e implementação ainda estavam
pendentes. A execução posterior está registrada abaixo; publicação e notas reais
continuam pendentes.


## Aceite da implementação — 2026-10-18

Concluídas as 30 tarefas, V01–V12 e FR-001–FR-009/SC-001–SC-005 conforme
[registro detalhado](tasks.md#registro-de-execução). YAML real com três pares próprios,
Few-shot Learning e Role Prompting, System/User separados e variável única.
188 testes da v2 e 266 regressões offline aprovados, sem skip/xfail. Revisão
semântica/documental no [README](../../README.md#técnicas-aplicadas-fase-2).
Hashes da v1 e quatro protegidos intactos. Sem chamadas remotas nesta spec.
A 003 continua ativa e a branch continua `dev`; planejar 004 antes de publicar.
