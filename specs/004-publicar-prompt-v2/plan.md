# Implementation Plan: Publicação pública e rastreável da v2

**Branch**: `dev` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

**Input**: `specs/004-publicar-prompt-v2/spec.md`, Fase 5 e R07/R12 do
[plano mestre](../../plan/plano-implementacao.md), com as dependências 001 e 003.

**Estado**: planejamento, desenho, tarefas e análise SDD concluídos; A1 corrigido
e revalidado documentalmente. Implementação e publicação real concluídas em 2026-10-18: 35/35 tarefas; evidências no registro abaixo. O setup retornou
`BRANCH=004-publicar-prompt-v2` como identificador da feature; a branch Git
continua `dev`. O ponteiro local `.specify/feature.json` seleciona a 004.
Nenhuma branch foi criada ou trocada.

## Summary

Implementar as três funções existentes em `src/push_prompts.py` para validar o
YAML otimizado, publicar o prompt configurado como público e conferir a revisão
exata contra o artefato local. Reutilizar `load_yaml`, `check_env_vars`,
`validate_prompt_structure`, `langsmith.Client` e `ChatPromptTemplate`, sem
modificar os utilitários ou o avaliador fornecidos.

O destino combina `USERNAME_LANGSMITH_HUB` com `bug_to_user_story_v2`; nesta
entrega resulta em `fabiocsm/bug_to_user_story_v2`, sem fixar o handle no código.
Preservar descrição e tags locais, representar técnicas nos metadados suportados
e manter exatamente System/User e a única variável `bug_report`.

O retorno do push confirma uma escrita, mas não comprova equivalência ou
publicidade. Resolver a revisão indicada pela URL retornada, recuperar pelo hash
completo, comparar mensagens, variáveis e metadados e provar leitura sem
autenticação. Registrar hashes locais, revisão, data e endereços em documentação
versionada. Falha posterior ao push deve informar que a publicação pode existir,
mas continua sem liberação para avaliação; não apagar nem sobrescrever históricos.

O sucesso do CLI depende das verificações automatizadas C07.1–C07.4 e da
estabilidade local. A inspeção visual C07.5 é posterior e, junto ao registro de
evidências, obrigatória para o aceite da 004 antes da entrega à 005. O retorno
zero pode coexistir com inspeção visual pendente, sem representar esse aceite.

Fora do escopo: refinar a v2, repetir pull da v1, executar modelos, avaliar,
compartilhar dataset ou publicar alterações no GitHub. As specs 005/006 mantêm
as 3–5 iterações, aprovação das cinco métricas e média `>= 0.8`, e evidências finais.

## Technical Context

**Language/Version**: Python 3.10+; ambiente existente CPython 3.11.14 em `venv/`.

**Primary Dependencies**: pins existentes `langsmith==0.13.0`,
`langchain-core==1.6.4`, `pyyaml==6.0.3`, `python-dotenv==1.2.3`,
`pytest==9.1.1`; `requests` já instalado como dependência do SDK para leitura
anônima. Biblioteca padrão para SHA-256, JSON, datas, caminhos e captura de
diagnósticos. Nenhuma instalação ou mudança de dependências prevista.

**Storage**: YAML v2 somente leitura nesta feature; metadados e commits no Hub;
registro de publicação em `docs/publicacao-v2.md`, versionado e vinculado no README.
Saída do script contém os dados para o registro; sem banco ou manifesto paralelo
obrigatório. `results/` e `screenshots/` não serão a única cópia das evidências.

**Testing**: manter os seis testes da 003; adicionar casos de publicação,
configuração, retorno e falhas em `tests/test_prompts.py`, com dublês do SDK e
HTTP, isolamento de dotenv/credenciais e bloqueio de rede. Rodar esse módulo
e regressão existente. Round-trip e leitura pública reais são provas separadas.

**Target Platform**: CLI local a partir da raiz; macOS/POSIX comprovado na 001.
Resolver o YAML por `Path(__file__)`, sem depender da localização incidental do
processo. Outros sistemas exigem reprodução antes de alegar compatibilidade.

**Project Type**: script CLI existente; nenhuma API própria ou serviço novo.

**Performance Goals**: validação offline antes de toda escrita; zero chamadas
LLM e custo de inferência zero nesta feature. Uma publicação por execução e
leituras necessárias à conferência, sem loop de republicação nem meta artificial
de latência. Consultas remotas devem ter timeout finito.

**Constraints**: seis campos exatos do contrato da 003; `version: v2`;
User igual a `{bug_report}`; sem pendências, técnicas duplicadas ou entrada
inesperada. Preservar v1, quatro protegidos, dataset 15/5/7/3, providers,
juízes e limiares. Nunca emitir credenciais, YAML bruto inválido ou exceções remotas
sem filtragem. Preservar assinaturas e retorno booleano do esqueleto.

**Scale/Scope**: um YAML, um prompt remoto, múltiplas revisões auditáveis nas
iterações futuras. A condição `COND-001` e seus modelos continuam definidos na
[preparação](../../docs/preparacao.md#condição-experimental); não há nova seleção
de modelo nesta feature. Revalidar documentação/acesso antes da avaliação da 005,
considerando a estimativa global de US$ 1–5.

## Constitution Check

Gate avaliado antes da pesquisa e reavaliado após o desenho. PASS refere-se ao
plano, sem declarar testes da implementação, escrita remota ou métricas obtidas.

| Regra | Antes da Fase 0 | Após a Fase 1 |
| --- | --- | --- |
| I — Integridade/escopo | PASS: script, testes e documentação | PASS: v1, dados e quatro protegidos somente leitura; guia confere hashes |
| II — Prompt verificável | PASS: consumir v2 da 003 | PASS: contrato herdado, duas técnicas reais, System/User e entrada única |
| III — Hub/rastreabilidade | PASS: handle configurado, push público | PASS: revisão exata, metadados, hashes locais e leitura anônima; latest não identifica o próprio push |
| IV — Avaliação íntegra | PASS: sem LLM/juízes nesta feature | PASS: sucesso de publicação não é aprovação; revisão estável exigida na 005 |
| V — Validação/reprodução | PASS: seis testes preservados | PASS: negativos por requisito, guia executável e registro versionado; evidência real independente |
| Stack/configuração | PASS: pins/utilitários da 001 | PASS: três assinaturas preservadas, SDK real pesquisado e TODO compatível com I1 da 003 |

Nenhuma exceção à constituição ou esclarecimento de escopo é necessário.
Indisponibilidade, credencial inválida ou handle sem permissão bloqueiam a operação
correspondente na implementação, sem autorizar alteração do contrato acadêmico.

## Project Structure

### Documentation (this feature)

```text
specs/004-publicar-prompt-v2/
├── spec.md
├── checklists/requirements.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/publicacao-v2.md
├── quickstart.md
└── tasks.md
```

As [35 tarefas](tasks.md) foram geradas posteriormente por `$speckit-tasks` em
2026-10-18: Setup (2), Foundational (2), US2 (8), US1 (10), US3 (7) e revisão
final (6). US2/US1 são P1 e seguem a dependência rejeição → escrita; US3 é P2.
Há seis marcadores de paralelismo, em três pares sem conflito de arquivos.
Todas foram concluídas na implementação posterior, registrada ao final. A análise SDD identificou A1, corrigido no contrato
e em T014/T019/T026/T032–T034, com estados automatizado/visual separados.

### Source Code (repository root)

```text
src/push_prompts.py                 # implementar três funções e helpers locais mínimos
tests/test_prompts.py               # preservar seis testes; acrescentar contratos de push
prompts/bug_to_user_story_v2.yml     # consumir sem editar nesta feature
prompts/bug_to_user_story_v1.yml     # referência recuperada, somente leitura
src/utils.py                       # helpers reutilizados, protegido
src/evaluate.py                     # consumidor da 005, protegido
src/metrics.py                      # protegido
datasets/bug_to_user_story.jsonl     # protegido
docs/publicacao-v2.md               # criar na implementação, registro real por revisão
README.md                          # instruções/links da publicação, preservar enunciado
```

**Structure Decision**: concentrar a lógica no script e os testes no entregável
existente, sem importar helpers de testes em produção. Metadados do template e
tags do Hub completam o YAML sem criar formato de prompt novo. Documentação
versionada registra as provas reais e distingue-as do desenho aqui descrito.

## Phase 0 — Pesquisa e decisões

[research.md](research.md) resolve validação herdada, contratos do SDK instalado,
metadados suportados, resolução do commit e acesso público. Pesquisa de SDK/Hub
e de validação foi delegada conforme a skill, somente para leitura; resultados
consolidados sem executar publicação ou modelos. Não há incertezas de desenho
pendentes. Dependências externas continuam sujeitas a comprovação na execução.

## Phase 1 — Desenho e sequência de execução

1. Revalidar integridade e aceite da 003. Preservar os seis testes e seu contrato,
   incluindo correção I1: detectar marcadores reais sem rejeitar prosa como `TODOS`.
2. Implementar `validate_prompt()` como validação pura: tipos antes do helper,
   seis campos, técnicas, pendências e template. Não alterar o dict recebido.
3. Implementar `main()`: ler YAML com `load_yaml`, tratar saída potencialmente
   sensível do helper, exigir definição única e validar antes de criar cliente.
   Calcular SHA-256 dos bytes locais e da definição canônica; conferir arquivo
   estável entre leitura e fim da operação.
4. Validar configuração da operação com `check_env_vars`, complementado por
   valores não brancos, tracing efetivo e contexto/handle autenticado. Ler
   `USERNAME_LANGSMITH_HUB` sem valor padrão fixo e rejeitar identidade divergente.
5. Implementar `push_prompt_to_langsmith()` com validação própria para chamadas
   diretas; construir ChatPromptTemplate sem modelo, incorporar metadados locais,
   publicar uma vez com `is_public=True`, descrição e tags projetadas.
6. Validar a URL retornada, extrair o prefixo da revisão e resolver o hash completo
   via SDK sem cache. Conferir pelo hash completo, nunca descobrir a própria
   publicação consultando apenas `latest`. Verificar conteúdo/metadados e leitura
   anônima do mesmo commit; conferir também os metadados atuais do repositório.
7. Separar estados, emitir resumo auditável e códigos de saída conforme contrato.
   Falha de conferência não desfaz a escrita nem dispara outra publicação.
8. Exercitar positivos e negativos offline; conferir sentinelas de segredo, nenhum
   push em artefato inválido e nenhuma chamada de modelo. Rodar regressão.
9. Executar publicação real, conferir dashboard e acesso anônimo, registrar prova
   em `docs/publicacao-v2.md` e README; concluir V15 da preparação somente com essa
   evidência. Não executar avaliação nem compartilhar dataset nesta feature.

Entidades em [data-model.md](data-model.md); funções, estados e matriz de falhas
em [contracts/publicacao-v2.md](contracts/publicacao-v2.md); validações V01–V12
em [quickstart.md](quickstart.md). O planejamento termina após o desenho da Fase 1.

## Rastreabilidade e aceite

| Requisito | Plano mestre | Decisão/artefato | Verificação / critério |
| --- | --- | --- | --- |
| FR-001 | R07/R06 | C01–C03: YAML, mensagens e entrada única | V02–V04/V08; SC-001/SC-002 |
| FR-002 | R02/R07 | C04: handle do ambiente e contexto autenticado | V05/V07; SC-001/SC-004 |
| FR-003 | R07 | C05/C07: publicidade, tags, descrição e técnicas | V06/V08–V10; SC-001 |
| FR-004 | R07 | C06/C08: confirmação, URL, estágios e saída | V06/V07/V11; SC-004 |
| FR-005 | R04/R07/R11 | C01–C03/C09: rejeição anterior à escrita | V02–V06; SC-002 |
| FR-006 | R07/R12 | C07/C08: revisão completa, comparação e hashes | V08–V11; SC-001/SC-003 |
| FR-007 | R07/R10 | C10: invalidação e entrega à 005 | V11/V12; SC-003/SC-004 |
| Restrição transversal | R12/R13/R16 | integridade, sigilo e roteiro reproduzível | V01/V06/V12 |

Aceite da implementação exige matriz negativa coberta, regressão aprovada, push
real confirmado, revisão equivalente, acesso público comprovado e registro
versionado. Uma falha externa permanece pendência explícita, mesmo com código pronto.

## Complexity Tracking

Sem violações a justificar. São necessários apenas helpers locais para complementar
o utilitário protegido e conferir a fronteira externa; não criar serviço,
framework de validação, banco ou suíte que replique as métricas.

## Conferência do planejamento

Planejamento sem implementação, publicações ou chamadas LLM. Pesquisa incluiu
leitura anônima da v1 para confirmar a interface, sem repetir o pull/exportação.
`.specify/extensions.yml` ausente nas verificações antes/depois: nenhum hook
registrado para executar.

Conferidos 78 links locais nos cinco artefatos e nos dois índices atualizados,
sete blocos Bash e dois trechos Python embutidos. Hashes de quatro protegidos
iguais ao manifesto da 001 e hash da v1 igual ao registro da 002. A regressão
existente de prompts, pull e preparação passou: **454 testes em 0,66 s**; isso
não testa a implementação ainda ausente do push nem comprova publicidade da v2.
`git diff --check` aprovado. Contexto persistido e resolução de paths confirmam
a 004; branch Git `dev`, sem criação de `tasks.md` naquela execução ou alteração
de código/YAML. A geração posterior das tarefas está registrada acima.

### Correção da análise — A1

Em 2026-10-18, corrigida a ambiguidade entre sucesso do CLI e aceite visual,
conforme [registro de A1](tasks.md#correção-da-análise--a1). C08 referencia
C04–C06 e C07.1–C07.4 para o booleano; `main()` exige ainda estabilidade local.
C07.5 ocorre depois, em T033, e seu registro é obrigatório antes do aceite em
T034 e entrega à 005. Os testes planejados em T014 comprovam sucesso do CLI
com inspeção visual pendente e reprovação em qualquer falha automatizada.

Revalidação documental da correção concluída, sem novo achado nessa relação.
Próxima etapa: `$speckit-implement` para a 004, mantendo todas as tarefas pendentes
até sua execução e as provas remotas até a publicação real.

## Implementação concluída — 2026-10-18

35/35 tarefas executadas; 437 testes de v2/publicação e 266 regressões passaram.
[Publicação e três capturas reais](../../docs/publicacao-v2.md): primeira escrita
real confirmada, falhas preservadas, CLI final zero com conferência do commit
`4278de75a2fca03a17cc1e3ab9d66d552c2c1aaebe543a085a34772637fa9595`.

Duas suposições de desenho foram corrigidas com provas reais e testes prévios:
tag técnica opcional `ChatPromptTemplate` acrescentada pelo serviço; conflito
no reenvio de conteúdo idêntico. O conflito leva somente à conferência integral
de revisão existente, sem atribuir HEAD ao próprio push nem fabricar URL retornada.
Detalhes nos complementos C05–C08/modelo/pesquisa/guia. Não relaxam o README.

004 permanece ativa e `dev` preservada. V1/v2/quatro protegidos íntegros, nenhum
modelo/juiz, avaliação, dataset compartilhado ou push Git. Entrega à 005 habilitada
com os hashes/revisão do registro; requer revalidar HEAD/metadados antes/depois dos
experimentos. Aprovação acadêmica e entrega final continuam nas specs 005/006.
