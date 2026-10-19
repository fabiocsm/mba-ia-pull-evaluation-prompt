# Implementation Plan: Preparação reproduzível dos experimentos

**Branch**: `dev` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

**Input**: `specs/001-preparar-experimentos/spec.md`, Fase 1 e seções 3, 6–8 do
[plano mestre](../../plan/plano-implementacao.md).

**Estado**: planejamento concluído; preparação e comprovações remotas não executadas.
O setup retornou `BRANCH=001-preparar-experimentos` como identificador da feature;
`git branch --show-current` confirmou `dev`. Nenhuma branch foi criada ou trocada.

## Summary

Preparar uma execução reproduzível e registrar sua prontidão antes das operações
dependentes. A implementação desta feature produzirá um registro sanitizado de
ambiente, configuração, acessos, modelos, custo e impedimentos; um manifesto inicial
de integridade; e um inventário de dependências instaladas. Os comandos usam Python,
Git, o SDK LangSmith e, como apoio, o CLI existente. Não criar framework, serviço,
banco de dados ou novo comando de aplicação.

Validar primeiro integridade e ambiente, depois configuração e acessos, e finalmente
as duas funções de modelo com `temperature=0`. Documentação oficial fundamenta os
candidatos; somente chamadas reais comprovam acesso da conta. Cada pré-requisito tem
estado próprio e determina quais operações das próximas specs podem executar.

Fora do escopo: implementar pull/push, recuperar a semente, criar a v2 ou seus seis
testes, executar experimentos completos, criar/compartilhar datasets e entregar
evidências finais. Essas responsabilidades continuam nas specs 002–006.

## Technical Context

**Language/Version**: Python 3.10+; preferir Python 3.11 para a primeira instalação,
condicionado aos pins fornecidos e ao `pip check`.

**Primary Dependencies**: `langchain-core==1.6.4`, `langsmith==0.13.0`,
`langchain-openai==1.6.2`, `langchain-google-genai==4.4.0`, `python-dotenv==1.2.3`,
`pyyaml==6.0.3`, `pydantic==2.13.5`, `pytest==9.1.1`, conforme `requirements.txt`.
Reutilizar `langsmith.Client`, `ChatPromptTemplate`, `utils.get_llm` e
`utils.get_eval_llm`. Git e LangSmith CLI apoiam a inspeção.

**Storage**: `.env` e `venv/` locais ignorados; registros versionados
`docs/preparacao.md`, `docs/integridade-inicial.json` e
`docs/dependencias-preparacao.txt`. Não persistir respostas de autenticação completas.

**Testing**: instalação, `pip check`, imports sem rede, comparação SHA-256/Git,
validação JSONL, leituras remotas e duas chamadas reais curtas, uma por papel.
Os testes ainda vazios do prompt na spec 003 não comprovam esta preparação.

**Target Platform**: execução local na raiz, inicialmente macOS/shell POSIX;
documentar ativação equivalente de venv para Windows.

**Project Type**: scripts CLI existentes e documentação de operação acadêmica.

**Performance Goals**: sem meta de latência. Planejar 3–5 ciclos de 15 gerações e
45 juízes: 180–300 chamadas, além das verificações e retries. Candidato inicial
`gpt-4.1-2025-04-14` nos dois papéis; estimativa ilustrativa de US$ 1,50–2,51 para
os ciclos, conforme [pesquisa e hipóteses](research.md). Revalidar disponibilidade:
a documentação consultada anuncia desligamento em 14/01/2027.

**Constraints**: quatro arquivos protegidos imutáveis; 15 casos (5/7/3); OpenAI
inicialmente, suporte `google` preservado; dois modelos explícitos; temperatura zero;
nenhum segredo nos artefatos; orçamento orientado a US$ 1–5, sem garantia de gasto.

**Scale/Scope**: uma configuração inicial, um fork, um workspace LangSmith, um projeto
de tracing, handle `fabiocsm`, dois papéis de modelo e um dataset local.

## Constitution Check

Gate de desenho antes da Fase 0 e novamente após a Fase 1. `PASS` indica conformidade
do plano; não comprova execução ou sucesso no LangSmith.

| Regra | Antes da pesquisa | Após o desenho |
| --- | --- | --- |
| I — Escopo e integridade | PASS: preparação e documentação | PASS: manifesto de commit, quatro arquivos e 15 casos; nenhum protegido alterado |
| II — Prompts verificáveis | PASS: v2 reservada à 003 | PASS: inspecionar template sem criar a v2 |
| III — LangSmith e rastreabilidade | PASS: acessos devem ser comprovados | PASS: contexto e evidência por operação; push real na 004 |
| IV — Medição íntegra | PASS: não produzir notas nesta feature | PASS: custo previsto e consumo observado separados; regras de avaliação preservadas |
| V — Reprodução e entrega | PASS: registros sem segredos | PASS: guia e referência no README; testes e evidências finais nas specs próprias |
| Stack e configuração | PASS: venv antes de instalar; pins preservados | PASS: imports, pip check, fontes oficiais e chamadas pelos utilitários |

Sem exceção à constituição ou decisão de desenho pendente. Disponibilidade de
pacotes, credenciais e modelos são verificações de execução: falhas geram impedimento
antes da operação dependente, sem relaxar gates nem editar arquivos protegidos.

## Project Structure

### Documentation (this feature)

```text
specs/001-preparar-experimentos/
├── spec.md
├── checklists/requirements.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/preparacao.md
└── quickstart.md
```

`tasks.md` será produzido por `$speckit-tasks`, fora deste comando.

### Source Code (repository root)

```text
README.md                           # Acrescentar preparação em Como Executar
requirements.txt                    # Consumir sem alterar pins nesta feature
.env.example                        # Template, não copiar sobre .env existente
.env                                # Local e ignorado
venv/                               # Criado na implementação, ignorado
docs/                               # Registros a criar na implementação
├── preparacao.md
├── integridade-inicial.json
└── dependencias-preparacao.txt
src/
├── pull_prompts.py                  # Implementação na 002
├── push_prompts.py                  # Implementação na 004
├── evaluate.py                      # Protegido
├── metrics.py                       # Protegido
└── utils.py                         # Protegido, funções reutilizadas
datasets/bug_to_user_story.jsonl     # Protegido
tests/test_prompts.py                # Implementação na 003
```

**Structure Decision**: conservar scripts e adicionar somente registros necessários
à reprodução em `docs/`, que não está ignorado. Não deixar evidência única em
`results/` ou `screenshots/`. Preservar o enunciado ao acrescentar instruções no README.

## Phase 0 — Pesquisa e decisões

[research.md](research.md) consolida ambiente, configuração, SDK, modelos, integridade
e custo. Pesquisas de modelos e ambiente/integrações foram delegadas em paralelo,
conforme a skill. Contratos locais governam o comportamento fornecido; fontes oficiais
orientam candidatos e contratos externos. Confirmar assinaturas na versão instalada.

Os candidatos de modelo são revisáveis. Na implementação, reconfirmar fontes, registrar
identificador efetivo e comprovar cada papel. Um candidato inacessível exige alternativa
compatível e nova condição registrada; não exige modificar o avaliador.

## Phase 1 — Desenho e contratos

1. Registrar baseline antes de instalar/configurar: commit completo, branch, estado
   dos protegidos, hashes dos bytes, manifesto dos 15 casos e procedência do fork.
   Hash do checkout sozinho não prova correspondência com a origem: comparar os
   protegidos com uma revisão identificada do repositório base.
2. Criar/ativar `venv`, instalar `requirements.txt`, conferir dependências e imports.
   Registrar Python, SO, pip, CLI e versões resolvidas. Não trocar pins silenciosamente.
3. Reconsultar as fontes oficiais e selecionar os dois modelos antes de exigir seus
   nomes na configuração. Configurar localmente os valores não secretos escolhidos e
   carregar `.env` com `python-dotenv`, mantendo a precedência do ambiente; validar
   a configuração efetiva sem imprimir tokens e preservar as credenciais existentes.
   Não substituir o arquivo pelo template, que usa `google` e não comprova a condição OpenAI.
4. Comprovar conta/workspace e handle por leitura; consultar o projeto esperado.
   A comprovação do contexto autenticado conclui esse gate mesmo se a consulta
   confirmar que apenas o projeto ainda não existe: registrar sua existência como
   pendente, liberando as duas chamadas mínimas. Autenticação inválida, acesso negado
   ou contexto incorreto/ambíguo bloqueiam o avanço. A existência do projeto será
   comprovada após os traces, sem criar dataset ou experimento para esse teste.
5. Inspecionar SDK instalado para pull, serialização, push, metadados e revisão.
   Consultar ajuda antes de subcomandos CLI; SDK e CLI devem usar o mesmo contexto.
   Leitura pública de prompt não comprova posse da identidade nem permissão de push.
6. Executar duas chamadas curtas via utilitários, com `temperature=0`; verificar resposta
   não vazia e trace no projeto/workspace esperado. Registrar modelos solicitado e
   retornado, quando informado, tokens e diagnóstico sanitizado. Se o projeto estava
   ausente, consultá-lo novamente e comprovar nome/ID, tenant e os dois traces antes
   de concluir a prontidão. Não rodar os 15 casos.
7. Registrar custo, consumo disponível, prontidão por operação e próximas ações.
   Conferir novamente hashes e diff; ligar os registros ao README.

Campos em [data-model.md](data-model.md), contrato em
[contracts/preparacao.md](contracts/preparacao.md) e cenários em
[quickstart.md](quickstart.md). Os registros em `docs/` serão produzidos na
implementação e não contêm resultados presumidos deste planejamento.

## Rastreabilidade e aceite

| Requisito | Plano mestre | Desenho/registro | Verificação |
| --- | --- | --- | --- |
| FR-001 | R02 | Presença e validade sem segredos | Configuração; SC-001 |
| FR-002 | R02 | Workspace, projeto e handle | Leituras e trace mínimo; SC-001 |
| FR-003 | R02 | Fontes oficiais e dois papéis | Duas chamadas com temperatura zero; SC-002 |
| FR-004 | R13 | OpenAI inicial, ramo Google preservado | Imports e hashes; SC-001/SC-002 |
| FR-005 | R02 | Estado, causa e ação por operação | Cenários de falha; SC-001 |
| FR-006 | R12 | Commit/hash/casos no manifesto | Origem e comparação final; SC-003 |
| FR-007 | R18 | Identidade e metadados públicos do fork | GitHub com origem/visibilidade; SC-001/SC-003 |
| FR-008 | R01 | Venv e versões resolvidas | Instalação, pip check, imports; SC-004 |
| FR-009 | R01/R13/R16 | Guia e memória de cálculo | Reprodução e consumo separado; SC-004 |

Registro completo com impedimentos atende ao diagnóstico, mas não significa prontidão
para as specs afetadas. SC-002/SC-004 exigem provas reais. Nenhuma operação executa
com dependência pendente/impedida. Para as chamadas mínimas, os pré-requisitos são
ambiente/configuração e contexto autenticado corretos; existência do projeto e traces
são resultados a comprovar em T013, não gates prévios dessas chamadas.
A publicação real pertence à 004 e não é condição
para concluir a preparação; sua permissão efetiva será comprovada naquele push.

## Complexity Tracking

Sem violações ou complexidade adicional que exija justificativa.
