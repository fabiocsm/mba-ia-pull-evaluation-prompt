# Preparação dos experimentos — PREP-001

Coleta inicial: 2026-10-17T19:05:19-03:00. Commit: `932277f2815da4f4a038354f35d754abc2ec7794`; branch: `dev`.

Fontes: [spec](../specs/001-preparar-experimentos/spec.md), [tarefas](../specs/001-preparar-experimentos/tasks.md), [manifesto inicial](integridade-inicial.json).

## Ambiente

Pronto: `venv/` com Python 3.11.14; instalação dos pins, `pip check`, imports dos dois providers e contratos SDK aprovados. Detalhes e hashes no histórico; [inventário instalado](dependencias-preparacao.txt).

## Configuração e credenciais

Pronta: `LANGSMITH_API_KEY` adicionada pelo autor e validada por consultas autenticadas. `OPENAI_API_KEY` validada pelas quatro respostas reais. Handle `fabiocsm`, provider `openai`, tracing `true`, projeto `mba-ia-pull-evaluation-prompt`, ambos os modelos `gpt-4.1-2025-04-14`. Workspace/tenant `15dd5852-a835-4163-826c-e78668fd2a9c`, endpoint `https://api.smith.langchain.com`. Nenhum valor de credencial registrado; ambiente exportado tem precedência sobre `.env`.

## Verificações

Preparação concluída: integridade/origem, ambiente, configuração, contexto autenticado, duas chamadas iniciais e duas em reprodução, com quatro traces conferidos. A [matriz atual](#matriz-atual) substitui, para o estado operacional, as matrizes históricas do período bloqueado. Permissão de push será comprovada na spec 004.

## Condição experimental

Condição `COND-001`: provedor `openai`, `llm_model=eval_model=gpt-4.1-2025-04-14`, temperatura `0` em ambos os papéis. Seleção oficial documentada no histórico; modelo solicitado e retornado correspondente nas quatro chamadas.

Workspace `15dd5852-a835-4163-826c-e78668fd2a9c`, handle `fabiocsm`; projeto `mba-ia-pull-evaluation-prompt`, ID `10e3f705-af88-4cee-9d79-4a9fdb4a959f`, tenant correspondente. Nome futuro do dataset `mba-ia-pull-evaluation-prompt-eval`; não criado/compartilhado.

[Manifesto](integridade-inicial.json) e [inventário](dependencias-preparacao.txt), SHA-256 `c41618f427569c9cd60793c384248f1d45354f87e8bbb02f5440c5a8f0d08ef4`. Nova seleção de modelo/provedor ou alteração de credencial/workspace/dependências exige revalidar as verificações afetadas, conservando o histórico.

## Custo

Projeção de 3–5 ciclos documentada: US$ 1,9539–3,2565 com reserva de 30%, antes das verificações/extras. Consumo real da preparação: quatro chamadas, 92 tokens de entrada + 8 de saída, total 100 tokens. Estimativa desse consumo: US$ 0,000248. Cobrança observada: **não disponível**. Estimativa de ciclos não constitui gasto observado.

## Conclusão

**30/30 tarefas da spec 001 concluídas**, incluindo T029/T030 de convergência. API key LangSmith e contexto `fabiocsm` confirmados; dois papéis de modelo e tracing comprovados, reprodução automatizada em novo venv conferida. Ocorrência na primeira conferência dos traces da reprodução registrada e resolvida por reconsulta sem nova chamada LLM. Os fluxos de pull, v2/testes, push, avaliação completa e entrega das specs 002–006 ainda não foram executados. A preparação não demonstra aprovação nas métricas acadêmicas.

## Histórico — integridade de origem

2026-10-17T19:05:29-03:00: quatro arquivos comparados por SHA-256 com a revisão `a94ce443299b4928d0f1e08cecdacf7a36ff5fb1` do [repositório base](https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt/tree/a94ce443299b4928d0f1e08cecdacf7a36ff5fb1). Correspondência integral: True.

## Histórico — ambiente e contratos instalados

2026-10-17T19:06:09-03:00: T004–T006 concluídas. Ambiente `venv/`, Python 3.11.14, Darwin 25.6.0, arm64, pip 24.0. LangSmith CLI 0.3.3 (commit 31ddadd).

Interpretador selecionado por `uv python list --only-installed`: CPython 3.11.14, já instalado. Comandos: criação com esse interpretador via `python3.11 -m venv venv`; `source venv/bin/activate`; `python -m pip install -r requirements.txt`; `python -m pip check`. Instalação status 0, `No broken requirements found.` Imports dos oito pacotes e ambos os providers aprovados. Nenhum pin alterado.

SHA-256 de `requirements.txt`: `9ded17274b1bfb91eaa03992e3eeed9deb3e2e87bf800b43589cc37af790988d`. Inventário efetivamente instalado: [dependências](dependencias-preparacao.txt), SHA-256 `c41618f427569c9cd60793c384248f1d45354f87e8bbb02f5440c5a8f0d08ef4`.

Versões diretas: `{"langsmith": "0.13.0", "langchain-core": "1.6.4", "langchain-openai": "1.6.2", "langchain-google-genai": "4.4.0", "python-dotenv": "1.2.3", "pyyaml": "6.0.3", "pydantic": "2.13.5", "pytest": "9.1.1"}`.

Ajuda consultada: `langsmith --help`, `--version`, `workspace --help`, `workspace list --help`, `prompt --help`, `auth --help`, `api --help`. Consultas CLI futuras receberão ambiente carregado por dotenv; leitura não comprova escrita.

Assinaturas instaladas:

- `Client.read_project(self, *, project_id: 'Optional[str]' = None, project_name: 'Optional[str]' = None, include_stats: 'bool' = False) -> 'ls_schemas.TracerSessionResult'`
- `Client.get_prompt(self, prompt_identifier: 'str') -> 'Optional[ls_schemas.Prompt]'`
- `Client.pull_prompt(self, prompt_identifier: 'str', *, include_model: 'bool | None' = False, secrets: 'dict[str, str] | None' = None, secrets_from_env: 'bool' = False, skip_cache: 'bool' = False, dangerously_pull_public_prompt: 'bool' = False) -> 'Any'`
- `Client.pull_prompt_commit(self, prompt_identifier: 'str', *, include_model: 'Optional[bool]' = False, skip_cache: 'bool' = False, dangerously_pull_public_prompt: 'bool' = False) -> 'ls_schemas.PromptCommit'`
- `Client.push_prompt(self, prompt_identifier: 'str', *, object: 'Optional[Any]' = None, parent_commit_hash: 'str' = 'latest', is_public: 'Optional[bool]' = None, description: 'Optional[str]' = None, readme: 'Optional[str]' = None, tags: 'Optional[Sequence[str]]' = None, commit_tags: 'Optional[str | list[str]]' = None, commit_description: 'Optional[str]' = None) -> 'str'`

`ChatPromptTemplate.from_messages` validado offline com System/User separados, somente `bug_report`, formatação e serialização `langchain_core.load.dumps`. Pull público exige opt-in; `pull_prompt_commit` fornece manifesto/revisão sem inferir fidelidade da futura exportação YAML. Push suporta `is_public`, descrição e tags; não aceita parâmetro arbitrário `metadata`. Técnicas podem ser identificadas nas tags/descrição e nos metadados do template serializado. Nenhum prompt recuperado/publicado neste teste. Prova de revisão efetiva somente nas specs 002/004.

`.gitignore` conferido: venv, caches, artefatos Python, credenciais e temporários ignorados; `.env.example` permanece versionável. Não foram detectadas outras stacks que exijam novos arquivos ignore.

## Histórico — seleção e configuração (T007–T008)

2026-10-17T19:06:22-03:00: candidato do plano mantido para ambos os papéis: `gpt-4.1-2025-04-14`, provedor `openai`, temperatura `0`. Snapshot reduz alterações de versão entre ciclos e é compatível com o helper protegido; acesso da conta ainda será comprovado. Fontes oficiais reabertas nesta execução: [modelo e preços](https://developers.openai.com/api/docs/models/gpt-4.1), [exemplo GPT-4.1 com temperatura zero](https://developers.openai.com/api/docs/guides/speech-to-text), [depreciações](https://developers.openai.com/api/docs/deprecations). Desligamento anunciado: 2027-01-14; repetir seleção/comprovação se executar após essa data ou se a conta rejeitar o modelo. Preços: US$ 2 entrada e US$ 8 saída por milhão de tokens, sem desconto de cache/Batch.

Somente valores não secretos ajustados no `.env` existente com `dotenv.set_key`; credenciais preservadas. `load_dotenv('.env', override=False)` mantém precedência das variáveis exportadas.

| Variável | Presença | Validade nesta etapa |
| --- | --- | --- |
| `LANGSMITH_API_KEY` | ausente | remota pendente |
| `LANGSMITH_PROJECT` | ausente | impedida |
| `USERNAME_LANGSMITH_HUB` | presente | presença verificada; valor conforme condição |
| `LANGSMITH_TRACING` | presente | presença verificada; valor conforme condição |
| `LLM_PROVIDER` | presente | presença verificada; valor conforme condição |
| `LLM_MODEL` | presente | presença verificada; valor conforme condição |
| `EVAL_MODEL` | presente | presença verificada; valor conforme condição |
| `OPENAI_API_KEY` | presente | remota pendente |

Asserções locais: `{'handle': True, 'provider': True, 'tracing': True, 'generator': True, 'judge': True}`. Ausentes: `['LANGSMITH_API_KEY', 'LANGSMITH_PROJECT']`. `GOOGLE_API_KEY` não é exigida na condição OpenAI; ramo Google preservado e importado.

2026-10-17T19:06:51-03:00: nome não secreto `LANGSMITH_PROJECT=mba-ia-pull-evaluation-prompt` preenchido conforme `.env.example`. Falha anterior preservada. `LANGSMITH_API_KEY` permanece ausente; configuração impedida. Próxima ação: autor configurar a chave localmente e revalidar. `langsmith auth info --help` consultado; inspeção autenticada status 0, sem registrar saída bruta.

## Histórico — origem da entrega e casos (T016–T018)

2026-10-17T19:06:51-03:00: consulta pública `GET /repos/fabiocsm/mba-ia-pull-evaluation-prompt` no GitHub: `{"url": "https://github.com/fabiocsm/mba-ia-pull-evaluation-prompt", "visibility": "public", "fork": true, "parent": "devfullcycle/mba-ia-pull-evaluation-prompt", "checked_at": "2026-10-17T19:06:51-03:00", "status": "pronto"}`.

[Manifesto](integridade-inicial.json) enriquecido sem substituir coleta inicial: exatamente quatro arquivos; revisão completa da origem; 15 casos com relato/referência não vazios; distribuição 5 simples, 7 médios e 3 complexos. Hash bruto do JSONL igual à captura inicial, hashes canônicos por registro e por inputs/outputs. Auditoria remota futura na 005 deve comparar multiconjuntos de pares inputs/outputs com multiplicidade; não exigir `metadata.complexity` remoto, que o avaliador não envia. Nenhum dataset remoto criado ou compartilhado.

## Histórico — validações locais (T014/T019)

2026-10-17T19:07:26-03:00: JSON do manifesto válido; exatamente quatro hashes idênticos à captura inicial e à revisão de origem; 15 registros e hashes canônicos de relatos/referências conferidos; fork público e parent esperado comprovados. Cópia temporária fora do Git com quebra de linha adicional foi rejeitada pelo hash bruto; alteração sintética da referência foi detectada pelo hash de outputs sem mudar inputs. Originais intactos.

Subprocesso isolado importou `utils.check_env_vars`, removeu `LANGSMITH_API_KEY` somente da cópia do ambiente e bloqueou a etapa com status 7, nomeando a variável ausente. Outro subprocesso com fixture dotenv temporária comprovou `override=False`: variável exportada prevaleceu sobre o arquivo. Nenhum valor de credencial, modificação do `.env` real para falha, chamada remota paga ou teste de produção adicional.

## Prontidão por pré-requisito — 2026-10-17T19:08:46-03:00

Cada ID vale para PREP-001 e referencia requisitos da spec 001. Datas de verificações
concluídas estão no histórico; abaixo, a data desta consolidação. Provas ainda não
executadas não têm data de tentativa. Ausência de chave foi constatada localmente,
sem requisição HTTP; não é uma rejeição de autenticação do serviço.

| ID | FR / SC | Pré-requisito | Estado | Verificado em | Evidência / causa e próxima ação | Operações afetadas |
| --- | --- | --- | --- | --- | --- | --- |
| V01 | FR-008 / SC-001,004 | Ambiente e pins | pronto | 2026-10-17T19:08:46-03:00 | Instalação, pip check e imports; inventário versionável | Pull, preparação da v2, push, avaliação |
| V02 | FR-006 / SC-003 | Quatro protegidos e 15 casos | pronto | 2026-10-17T19:08:46-03:00 | Hashes locais/origem e cenários negativos no manifesto/histórico | Todas |
| V03 | FR-007 / SC-003 | Fork público com parent correto | pronto | 2026-10-17T19:08:46-03:00 | GET público GitHub; repository no manifesto | Entrega pública |
| V04 | FR-003 / SC-002 | Escolha documentada de modelos | pronto | 2026-10-17T19:08:46-03:00 | Fontes oficiais reabertas; snapshot candidato definido | Avaliação |
| V05 | FR-001,004,005 / SC-001 | Configuração LangSmith | impedido | 2026-10-17T19:08:46-03:00 | LANGSMITH_API_KEY ausente; configurar localmente e repetir T008 | Pull, push, avaliação |
| V06 | FR-001 / SC-001 | Credencial OpenAI | pendente | — | Presente; validade remota ainda não tentada; comprovar em T011/T012 após contexto | Avaliação |
| V07 | FR-002 / SC-001 | Identidade, handle, workspace e endpoint | pendente | — | CLI tem perfil OAuth e endpoint esperado; isso não comprova contexto. Após T008, executar T009 pelo CLI/interface e SDK | Pull, push, avaliação |
| V08 | FR-002,005 / SC-001 | Existência do projeto | pendente | — | SDK ainda não consultado; T009 distingue ausência confirmada de falha de acesso | Avaliação |
| V09 | FR-003,004 / SC-002 | Geração real com temperatura zero | pendente | — | Não tentada: T008/T009 impedem T010/T011; executar após sanar | Avaliação |
| V10 | FR-003,004 / SC-002 | Avaliação real com temperatura zero | pendente | — | Não tentada: T008/T009 impedem T010/T012; executar após sanar | Avaliação |
| V11 | FR-002 / SC-001,002 | Dois traces no projeto/workspace | pendente | — | Dependem das duas chamadas e conferência T013 | Avaliação |
| V12 | FR-001,005 / SC-001 | Diagnóstico e precedência de ambiente | pronto | 2026-10-17T19:08:46-03:00 | Subprocessos isolados, variável ausente bloqueada e override=False comprovado | Todas |
| V13 | FR-008 / SC-001 | Contratos SDK/CLI | pronto | 2026-10-17T19:08:46-03:00 | Assinaturas e template offline no histórico; nenhuma publicação | Pull, preparação da v2, push |
| V14 | FR-008,009 / SC-004 | Reprodução completa por segundo executor | pendente | — | Exige ambiente limpo e gates remotos; não concluída por falta da chave | Todas |
| V15 | FR-002 / SC-001 | Permissão efetiva de publicação | pendente | — | Prova reservada ao push real da 004, sem publicação de teste | Push |
| V16 | FR-001,004 / SC-001 | Valores não secretos iniciais | pronto | 2026-10-17T19:08:46-03:00 | Handle, provider, tracing, projeto e dois modelos configurados; credenciais preservadas | Pull, push, avaliação |

A transição a pronto exige nova evidência: não promover V05 após mera informação
de que a chave foi preenchida, nem V07 com leitura pública. Alterar credencial,
workspace, dependências ou modelo retorna verificações afetadas a pendente e preserva
o histórico.

| Operação futura | Estado atual | Motivo / dependência que falta |
| --- | --- | --- |
| Pull — 002 | impedido | Ambiente/integridade prontos; chave/contexto LangSmith e acesso à origem a comprovar |
| Preparação local da v2 — 003 | pendente | Ambiente pronto; v1 ainda não recuperada na 002 |
| Push — 004 | impedido | Chave/contexto; v2 e testes na 003; escrita será comprovada no push real |
| Avaliação — 005 | impedido | Chave/contexto, ambos os modelos e tracing, além das specs 002–004 |
| Entrega pública — 006 | pendente | Fork e baseline prontos; resultados/evidências das specs seguintes ainda ausentes |

## Memória de custo — T022

Consulta de preços em 2026-10-17T19:08:46-03:00; [fonte oficial](https://developers.openai.com/api/docs/models/gpt-4.1).
GPT-4.1: entrada US$ 2 e saída US$ 8 por milhão de tokens. Hipóteses ilustrativas,
sem desconto de cache ou Batch; não são tokens medidos da v2, que ainda não existe.

| Papel | Chamadas/ciclo | Tokens de entrada/chamada | Saída/chamada | Estimativa US$/ciclo |
| --- | ---: | ---: | ---: | ---: |
| Geração | 15 | 4.000 | 700 | 0,204 |
| Juiz F1 | 15 | 2.500 | 200 | 0,099 |
| Juiz Clarity | 15 | 2.500 | 200 | 0,099 |
| Juiz Precision | 15 | 2.500 | 200 | 0,099 |
| Total | 60 | — | — | 0,501 |

```text
C_ciclo = [15 × (Ig × Pg_in + Og × Pg_out)
           + Σ_juiz 15 × (Ij × Pj_in + Oj × Pj_out)] / 1.000.000
C_total = ciclos × C_ciclo + C_verificacoes + C_retries + C_extras
```

Helpfulness/Correctness são derivadas: não há dois juízes adicionais. Refinar tokens
por juiz quando a v2 e as respostas existirem, especialmente para casos complexos.

| Ciclos | Chamadas | Custo base US$ | Reserva de 30% US$ | Base + reserva US$ |
| --- | ---: | ---: | ---: | ---: |
| 3 | 180 | 1,503 | 0,4509 | 1,9539 |
| 5 | 300 | 2,505 | 0,7515 | 3,2565 |

Somar duas verificações mínimas iniciais e duas na reprodução (ainda não executadas).
Como mera previsão, 50 tokens de entrada e 10 de saída por chamada custariam
US$ 0,00018 cada: US$ 0,00036 por dupla, US$ 0,00072 pelas quatro. Totais previstos
com reserva e essas quatro chamadas: US$ 1,95462 a US$ 3,25722; não são cobrança.
Retries/extras reais devem ser acrescentados ao histórico, sem considerar a reserva
como medição de gasto. Baseline numérica opcional da v1 não está incluída e não foi
executada. US$ 1–5 é orientação do desafio, não teto automático nem garantia.

## Consumo provisório e reprodução

2026-10-17T19:08:46-03:00: chamadas LLM tentadas: 0; sucessos: 0; retries LLM: 0. T011/T012
não executadas devido à chave LangSmith ausente. Tokens e custo reportados por modelo:
não se aplicam a chamadas inexistentes. Cobrança observada: **não disponível**.
Consultas GitHub, ajuda CLI e inspeções locais não são execuções LLM do experimento.
T023–T025 permanecem abertos até executar/contabilizar as chamadas e comprovar a
reprodução completa. Não foi apresentado resultado simulado nem métrica do dataset.

### Reprodução parcial isolada — REP-001A

2026-10-17T19:09:13-03:00: este executor iniciou um subprocesso com novo venv temporário, fora do Git,
sem reutilizar/apagar `venv/`. Comandos executados pelo Python base 3.11.14:
`python3.11 -m venv <temporário>/venv-reproducao`,
`<python-isolado> -m pip install -r requirements.txt`, `-m pip check`, imports
dos oito pacotes/dois providers e `-m pip list --format=json`. Resultados:
`[{"etapa": "instalação", "status": 0}, {"etapa": "pip check", "status": 0}, {"etapa": "imports", "status": 0}]`. Inventário completo idêntico ao inicial: True.

O mesmo subprocesso carregou `.env` com precedência preservada e encontrou ausentes
`['LANGSMITH_API_KEY']`; validação terminou com status 7. Não houve tentativa remota
nem chamada LLM. Ambiente temporário descartado após inspeção. É prova parcial de
reprodução de instalação, não comprovação por segundo executor do roteiro completo:
contexto LangSmith, duas chamadas e traces não foram repetidos. T024 e SC-004
permanecem pendentes até reprodução integral; consumo adicional LLM desta tentativa: nenhuma chamada.

## Revisão final local — T026/T027

2026-10-17T19:09:46-03:00: manifesto JSON validado; conjunto de arquivos exatamente igual aos quatro
protegidos; hashes brutos e canônicos dos 15 casos conferidos contra a captura
inicial e origem. `git diff --exit-code HEAD --` para os quatro protegidos: status 0.
OpenAI/Google preservados no mesmo helper, imports aprovados em dois ambientes.
`git diff --check`: status 0. Enunciado original do README conservado integralmente
como prefixo; instruções acrescentadas após ele. Links locais conferidos e
inventário em formato `pacote==versão`. Credenciais existentes verificadas contra os
arquivos de entrega sem registrar valores: nenhuma ocorrência. Três registros em
`docs/` não ignorados; `.env.example` versionável; `.env` e `venv/` permanecem locais.
Nenhuma evidência depende de `results/` ou `screenshots/`.

`.specify/extensions.yml` ausente na verificação inicial e final: não há hooks
antes/depois de implementação a executar. Se o arquivo surgir ao retomar, ler
novamente antes de seguir. Nenhum commit, push Git, publicação de prompt ou
compartilhamento de dataset realizado nesta preparação.

## Rastreabilidade e encerramento parcial — T028

2026-10-17T19:10:12-03:00: 19/28 tarefas comprovadas; abertas: T008, T009, T010, T011, T012, T013, T023, T024, T025.
Índice de specs e plano mestre atualizados somente com resultados obtidos.

| Requisito / critério | Resultado atual | Evidência / próximo passo |
| --- | --- | --- |
| FR-001 | impedido | Presença conferida; falta LANGSMITH_API_KEY. Configurar localmente e repetir T008 |
| FR-002 | pendente | SDK/projeto/workspace/handle e tracing não comprovados; T009/T013 |
| FR-003 | parcial | Modelo escolhido em fonte oficial; faltam duas provas reais T011/T012 |
| FR-004 | parcial | OpenAI configurado; Google intacto/importável; execução real ainda pendente |
| FR-005 | pronto | Estados, causas, ações e gates registrados; falha local isolada comprovada |
| FR-006 | pronto | Quatro hashes iguais à origem, 15 casos e referências preservados |
| FR-007 | pronto | Fork público com parent correto via GitHub |
| FR-008 | parcial | Instalação/contratos/imports e repetição limpa aprovados; roteiro completo ainda sem reprodução |
| FR-009 | parcial | Guia e projeção disponíveis; custo das chamadas/reprodução só após executá-las |
| SC-001 | parcial | Todos os pré-requisitos catalogados antes de chamadas; prontidão global ainda impedida |
| SC-002 | pendente | Nenhum dos dois papéis nem seus traces comprovados |
| SC-003 | pronto | Origem, materiais, referências, distribuição e manifesto conferidos |
| SC-004 | pendente | Instalação limpa aprovada, mas segundo executor não repetiu contexto/chamadas/tracing |

T001–T007, T014–T022 e T026–T028 concluídas. T008 foi tentada e falhou;
T009–T013 e T023–T025 conservam as comprovações faltantes, sem marcar sucesso
com diagnóstico parcial. O registro candidato de condição não conclui T010 sem
contexto autenticado. A consolidação provisória de consumo não conclui T023 sem
as duas chamadas. T024 não pode ser aprovado pela repetição apenas da instalação.

Ação necessária: preencher `LANGSMITH_API_KEY` no `.env` local, sem publicá-la, e
retomar `$speckit-implement`. Revalidar a configuração com precedência de ambiente,
comprovar contexto (T009), completar condição (T010), duas chamadas (T011/T012) e
traces (T013). Depois contabilizar consumo e executar reprodução integral
T023–T025. Atualizar os registros/revisão final com os novos fatos, sem reescrever
baseline nem apagar o histórico de falha. Os fluxos das specs seguintes continuam
não executados; nenhuma métrica acadêmica foi obtida ou declarada aprovada.

## Retomada — API key e contexto confirmados (T008/T009)

2026-10-17T19:35:27-03:00: autor adicionou a chave ao `.env`. T008 reexecutada: todas as oito variáveis
obrigatórias presentes e valores não secretos conforme a condição candidata; chave
efetiva corresponde à configuração local, sem valor registrado.
`langsmith auth info --format json` recebeu ambiente carregado por dotenv: autenticação
`api_key`, origem `env`, `authenticated=true`, endpoint
`https://api.smith.langchain.com`. Validade da chave comprovada por consulta remota
`langsmith workspace list --format json`, status 0, um workspace acessível.

Ajudas de `api ls` e `api info` consultadas. A API pública documenta
`GET /api/v1/settings` com `id`, `display_name` e `tenant_handle`. Consulta autenticada
via `langsmith api settings --workspace <workspace-id> --format json`, status 0:
workspace `Workspace 1`, ID `15dd5852-a835-4163-826c-e78668fd2a9c`, handle `fabiocsm`.
Organização `01a14b62-dc92-7cd0-a97a-9b45a9495001`. ID do tenant corresponde ao workspace
listado. `LANGSMITH_WORKSPACE_ID` definido localmente para esse ID não secreto;
nenhum handle criado ou alterado. Isso comprova contexto de leitura, não permissão
de push.

`Client.read_project(project_name="mba-ia-pull-evaluation-prompt")` retornou
`LangSmithNotFoundError` no contexto autenticado válido: projeto ainda não encontrado.
Sua existência continua pendente, distinta da autenticação agora comprovada. Conforme
T009/T013, as chamadas mínimas podem produzir o projeto e a comprovação deve vir
após seus traces. Histórico da chave ausente preservado.

## Condição habilitada — COND-001 (T010)

2026-10-17T19:35:46-03:00: condição candidata confirmada para execução; sem troca de modelo/provedor.
`provider=openai`, `llm_model=eval_model=gpt-4.1-2025-04-14`, temperatura `0` em
ambos os papéis. Fontes oficiais/preços/desligamento da seleção inicial mantidos
(consulta nesta mesma data; desligamento anunciado 2027-01-14).
Workspace esperado/constatado: `Workspace 1` / `15dd5852-a835-4163-826c-e78668fd2a9c`,
handle `fabiocsm`. Projeto esperado `mba-ia-pull-evaluation-prompt`; existência/ID ainda
pendentes, pois a consulta confirmou ausência. T013 deve comprovar projeto/tenant
e dois traces após as chamadas. Nome futuro do dataset `mba-ia-pull-evaluation-prompt-eval`.
Vínculo com [manifesto](integridade-inicial.json) e [inventário](dependencias-preparacao.txt),
SHA-256 `c41618f427569c9cd60793c384248f1d45354f87e8bbb02f5440c5a8f0d08ef4`.
Acesso aos modelos ainda depende de T011/T012; nenhuma métrica acadêmica produzida.

### Chamada mínima — T011

```json
{
  "task": "T011",
  "role": "geracao",
  "started_at": "2026-10-17T19:35:47-03:00",
  "requested_model": "gpt-4.1-2025-04-14",
  "run_id": "2b6fc47f-6035-44d3-9b79-14c40fac8d01",
  "temperature": 0,
  "condition": "COND-001",
  "success": true,
  "nonempty": true,
  "returned_model": "gpt-4.1-2025-04-14",
  "usage": {
    "input_tokens": 23,
    "output_tokens": 2,
    "total_tokens": 25,
    "input_token_details": {
      "audio": 0,
      "cache_read": 0
    },
    "output_token_details": {
      "audio": 0,
      "reasoning": 0
    }
  }
}
```

Mensagens System/User sintéticas do quickstart; nenhum exemplo do dataset avaliado.

### Chamada mínima — T012

```json
{
  "task": "T012",
  "role": "avaliacao",
  "started_at": "2026-10-17T19:35:50-03:00",
  "requested_model": "gpt-4.1-2025-04-14",
  "run_id": "2d4513ae-ad75-45f6-a64b-bf49f97b0b44",
  "temperature": 0,
  "condition": "COND-001",
  "success": true,
  "nonempty": true,
  "returned_model": "gpt-4.1-2025-04-14",
  "usage": {
    "input_tokens": 23,
    "output_tokens": 2,
    "total_tokens": 25,
    "input_token_details": {
      "audio": 0,
      "cache_read": 0
    },
    "output_token_details": {
      "audio": 0,
      "reasoning": 0
    }
  }
}
```

Mensagens System/User sintéticas do quickstart; nenhum exemplo do dataset avaliado.

## Tracing confirmado — T013

2026-10-17T19:36:14-03:00: após `wait_for_all_tracers()`, `Client.read_project` encontrou
`mba-ia-pull-evaluation-prompt`, ID `10e3f705-af88-4cee-9d79-4a9fdb4a959f`, tenant `15dd5852-a835-4163-826c-e78668fd2a9c`, igual ao workspace
esperado e autenticado. Projeto anteriormente ausente agora comprovado.
`Client.read_run` confirmou ambos os IDs: sessão igual ao projeto, término presente,
sem erro e metadados `condition=COND-001`/papel correspondentes.

| Papel | Run ID | Trace autenticado | Tokens entrada / saída |
| --- | --- | --- | --- |
| geracao | `2b6fc47f-6035-44d3-9b79-14c40fac8d01` | [Abrir trace](https://smith.langchain.com/o/15dd5852-a835-4163-826c-e78668fd2a9c/projects/p/10e3f705-af88-4cee-9d79-4a9fdb4a959f/r/2b6fc47f-6035-44d3-9b79-14c40fac8d01?poll=true) | 23 / 2 |
| avaliacao | `2d4513ae-ad75-45f6-a64b-bf49f97b0b44` | [Abrir trace](https://smith.langchain.com/o/15dd5852-a835-4163-826c-e78668fd2a9c/projects/p/10e3f705-af88-4cee-9d79-4a9fdb4a959f/r/2d4513ae-ad75-45f6-a64b-bf49f97b0b44?poll=true) | 23 / 2 |

Links exigem acesso ao workspace; os fatos sanitizados necessários estão neste registro. São traces mínimos de preparação, não as evidências acadêmicas de três exemplos, nem experimento/dataset.

## Consumo medido das verificações iniciais — T023

2026-10-17T19:36:14-03:00: duas tentativas reais, dois sucessos, nenhuma falha/retry observado.
Modelo solicitado e retornado `gpt-4.1-2025-04-14` em ambos os papéis.
Tokens reportados: 46 entrada + 4 saída = 50. Cache de entrada: 0.
Estimativa pelos preços documentados US$ 2/8 por milhão: **US$ 0.000124**
(US$ 0.000062 por chamada). Cobrança observada: **não disponível**; não é
comprovante de faturamento. Reprodução integral T024 ainda em aberto; seu consumo
será somado após executar. Histórico das tentativas locais sem chave preservado.

## Reprodução integral — REP-001B (T024)

Início 2026-10-17T19:36:52-03:00; conferência concluída 2026-10-17T19:37:45-03:00. Executor: processo Python
separado em novo venv temporário fora do Git, na mesma máquina/arquitetura e com
as credenciais locais herdadas por ambiente; não é revisão independente por pessoa.
`venv/` original preservado. O executor repetiu os passos do README/quickstart:

1. `python3.11 -m venv <temporário>/venv-reproducao`.
2. `<python-isolado> -m pip install -r requirements.txt` e `-m pip check`: status 0.
3. Imports dos oito pacotes e dois providers; inventário `pip list --format=json`
   idêntico ao registro inicial; configuração dotenv com precedência preservada.
4. Recomputação dos quatro hashes e hashes canônicos dos 15 casos: iguais ao manifesto.
5. Ajudas CLI, autenticação por API key do ambiente, workspaces e settings: workspace
   e handle esperados; `Client.read_project` com ID/tenant iguais aos da condição.
6. Duas chamadas sintéticas pelos mesmos helpers e modelos, temperatura zero,
   `condition=COND-001`, `reproduction_id=REP-001B`; respostas não vazias.
7. Envio de tracing aguardado; reconsulta remota confirmou sessão, término sem erro
   e metadados das duas execuções. Venv temporário descartado após a execução.

Divergência registrada: o primeiro subprocesso terminou com status 1 na fase posterior
às duas respostas; causa original não capturada de forma sanitizada. A reconsulta
posterior por `Client.read_run` encontrou ambos os traces completos, no mesmo
projeto/tenant e com o identificador de reprodução correto. Conferência recuperada
sem repetir chamada LLM. Não atribuir causa específica sem evidência da falha original.

| Papel reproduzido | Modelo solicitado / retornado | Run ID / trace autenticado | Tokens entrada / saída |
| --- | --- | --- | --- |
| geracao | `gpt-4.1-2025-04-14` / `gpt-4.1-2025-04-14` | [1d760df9-5253-46d8-a501-b6f609039e63](https://smith.langchain.com/o/15dd5852-a835-4163-826c-e78668fd2a9c/projects/p/10e3f705-af88-4cee-9d79-4a9fdb4a959f/r/1d760df9-5253-46d8-a501-b6f609039e63?poll=true) | 23 / 2 |
| avaliacao | `gpt-4.1-2025-04-14` / `gpt-4.1-2025-04-14` | [33f5dae2-acff-47ea-b73a-28eb5b45ad04](https://smith.langchain.com/o/15dd5852-a835-4163-826c-e78668fd2a9c/projects/p/10e3f705-af88-4cee-9d79-4a9fdb4a959f/r/33f5dae2-acff-47ea-b73a-28eb5b45ad04?poll=true) | 23 / 2 |

A reprodução é automatizada, na mesma máquina, com processo e ambiente de pacotes
separados. Não comprova portabilidade para outro SO nem revisão humana. O roteiro
completo foi repetido e as evidências correspondem à mesma COND-001. Não houve
troca de modelo, dataset, prompt ou utilitário protegido.

## Balanço final da preparação — T025

2026-10-17T19:37:45-03:00: quatro chamadas LLM tentadas/concluídas, duas iniciais e duas de reprodução;
nenhuma falha ou retry LLM observado. Houve a falha local de conferência de tracing
registrada acima, resolvida por leitura posterior. Consumo reportado agregado:
**92 tokens de entrada + 8 de saída = 100 tokens**, cache 0.
Custo estimado inicial US$ 0,000124; reprodução US$ 0,000124; total
**US$ 0.000248**, pelos preços documentados, sem desconto de cache.
Cobrança observada: **não disponível**. A estimativa de ciclos futuros continua
separada deste consumo; incluir novos testes, retries e experimentos quando realizados.
A preparação não executou os 15 casos nem produziu notas acadêmicas.

## Revisão de conclusão após retomada — 2026-10-17T19:38:48-03:00

28/28 tarefas concluídas e marcadas. Revalidados após a adição da chave: manifesto
e hashes dos quatro protegidos/15 casos; distribuição 5/7/3; diff de protegidos vazio;
`git diff --check` status 0; links locais válidos; README original preservado como
prefixo; nenhum valor de credencial nos artefatos de entrega; `.env` e `venv/`
ignorados e registros em `docs/` disponíveis para versionamento.
Hooks: `.specify/extensions.yml` continua ausente; nenhum hook anterior/posterior
a despachar. Baseline inicial mantida sem substituição.

| Requisito / critério | Estado final da preparação | Evidência |
| --- | --- | --- |
| FR-001 | pronto | Todas as variáveis presentes; LangSmith autenticado e OpenAI respondeu |
| FR-002 | pronto | Handle, workspace, projeto/tenant e quatro traces correspondentes |
| FR-003 | pronto | Fontes oficiais e dois papéis com modelo solicitado/retornado igual |
| FR-004 | pronto | Condição OpenAI comprovada; helper Google intacto/importável |
| FR-005 | pronto | Falhas, transições e próximas etapas registradas sem apagar histórico |
| FR-006 | pronto | Baseline/origem e 15 casos/referências preservados |
| FR-007 | pronto | Fork público e parent comprovados no GitHub |
| FR-008 | pronto | Venv, pins, pip check/imports/SDK e instalação limpa idêntica |
| FR-009 | pronto | Guia, estimativa 3–5 ciclos, consumo e reprodução registrados |
| SC-001 | pronto | Pré-requisitos documentados e comprovados antes das chamadas dependentes |
| SC-002 | pronto | Dois papéis comprovados e quatro traces no contexto esperado |
| SC-003 | pronto | Quatro materiais e 15 referências auditáveis contra a origem |
| SC-004 | pronto | Roteiro reproduzido por processo executor em novo venv; mesma máquina, limites e ocorrência registrados |

Os estados prontos referem-se à **spec 001**. Para a 002, ambiente/integridade e
contexto estão disponíveis; implementação/pull e acesso efetivo à origem serão
conferidos nessa feature. A 003 ainda depende da v1 recuperada. A 004 depende da
v2/testes e da prova efetiva de escrita no push real. A 005 ainda exige as specs
002–004 e auditoria do dataset remoto. A 006 depende de resultados e evidências
acadêmicos públicos, ainda não produzidos. Nenhum prompt publicado ou dataset
criado/compartilhado nesta etapa.

<a id="matriz-atual"></a>

## Matriz atual de prontidão — T029

Consolidação em 2026-10-17T20:11:53-03:00, condição `COND-001`. As datas de `verificado_em`
abaixo identificam a evidência efetivamente obtida, não a data desta consolidação.
Esta matriz substitui o estado operacional das matrizes históricas, que permanecem
no registro. Os IDs V01–V16 são os mesmos; as transições não apagam as falhas anteriores.

| ID | Requisito / critério | Pré-requisito | Estado atual | verificado_em | Evidência e resolução / próxima ação | Operações afetadas |
| --- | --- | --- | --- | --- | --- | --- |
| V01 | FR-008 / SC-001,004 | Ambiente e pins | pronto | 2026-10-17T19:06:09-03:00 | T004–T006: instalação, pip check/imports e [inventário](dependencias-preparacao.txt); repetição limpa T024 correspondente | Pull, preparação da v2, push, avaliação |
| V02 | FR-006 / SC-003 | Quatro protegidos e 15 casos | pronto | 2026-10-17T19:38:48-03:00 | T027: hashes brutos/canônicos conferidos com a captura e a origem no [manifesto](integridade-inicial.json) | Todas |
| V03 | FR-007 / SC-003 | Fork público e parent | pronto | 2026-10-17T19:06:51-03:00 | T016: consulta pública GitHub; repository no manifesto | Entrega pública |
| V04 | FR-003 / SC-002 | Escolha documentada de modelos | pronto | 2026-10-17T19:06:22-03:00 | T007: fontes oficiais e modelo explícito; reconsultar se mudar a condição | Avaliação |
| V05 | FR-001,004,005 / SC-001 | Configuração LangSmith | pronto | 2026-10-17T19:35:27-03:00 | T008: chave adicionada pelo autor, ambiente validado e API key autenticada; bloqueio por ausência resolvido | Pull, push, avaliação |
| V06 | FR-001 / SC-001 | Credencial OpenAI | pronto | 2026-10-17T19:35:50-03:00 | T011/T012: duas respostas reais, uma por papel; validade antes pendente agora comprovada | Avaliação |
| V07 | FR-002 / SC-001 | Identidade, handle, workspace e endpoint | pronto | 2026-10-17T19:35:27-03:00 | T009: settings autenticado confirma fabiocsm, tenant/workspace 15dd5852-a835-4163-826c-e78668fd2a9c | Pull, push, avaliação |
| V08 | FR-002,005 / SC-001 | Existência do projeto | pronto | 2026-10-17T19:36:14-03:00 | T013: projeto antes ausente encontrado; ID 10e3f705-af88-4cee-9d79-4a9fdb4a959f e tenant correspondentes | Avaliação |
| V09 | FR-003,004 / SC-002 | Geração real com temperatura zero | pronto | 2026-10-17T19:35:47-03:00 | T011: run 2b6fc47f-6035-44d3-9b79-14c40fac8d01, modelo solicitado/retornado e resposta não vazia | Avaliação |
| V10 | FR-003,004 / SC-002 | Papel de avaliação com temperatura zero | pronto | 2026-10-17T19:35:50-03:00 | T012: run 2d4513ae-ad75-45f6-a64b-bf49f97b0b44, modelo solicitado/retornado e resposta não vazia | Avaliação |
| V11 | FR-002 / SC-001,002 | Traces no projeto/workspace | pronto | 2026-10-17T19:36:14-03:00 | T013: dois traces iniciais completos e sem erro; T024 registra mais dois traces de reprodução | Avaliação |
| V12 | FR-001,005 / SC-001 | Diagnóstico e precedência | pronto | 2026-10-17T19:07:26-03:00 | T014: subprocessos isolados bloquearam variável ausente e provaram override=False | Todas |
| V13 | FR-008 / SC-001 | Contratos SDK/CLI | pronto | 2026-10-17T19:06:09-03:00 | T005: assinaturas e template System/User conferidos offline; não comprova publicação | Pull, preparação da v2, push |
| V14 | FR-008,009 / SC-004 | Reprodução em ambiente limpo | pronto | 2026-10-17T19:37:45-03:00 | T024/T025: REP-001B em processo/venv separados; duas chamadas e reconsulta de traces concluídas, ocorrência registrada | Todas |
| V15 | FR-002 / SC-001 | Permissão efetiva de publicação | pendente | — | Sem tentativa: comprovar escrita no push real da spec 004, após v2 e testes; não é gate de conclusão da 001 | Push |
| V16 | FR-001,004 / SC-001 | Valores não secretos iniciais | pronto | 2026-10-17T19:35:27-03:00 | T008/T010: provider, handle, tracing, projeto, workspace e dois modelos conforme COND-001 | Pull, push, avaliação |

V05 passou de impedido a pronto somente após correção e revalidação. V06–V11 e
V14 passaram de pendente a pronto pelas provas identificadas; V12/V13 já estavam
prontos e continuam apoiados nas evidências locais. A ocorrência de leitura em
REP-001B foi resolvida por reconsulta, sem presumir sua causa original. Alteração
de credencial, workspace, dependências ou modelo exige revalidar os IDs afetados.

| Operação futura | Estado atual | Dependências da 001 comprovadas | O que falta / próxima ação |
| --- | --- | --- | --- |
| Pull — 002 | pendente | V01/V02/V05/V07/V13 | Implementar o pull e conferir acesso efetivo a leonanluppi/bug_to_user_story_v1; não recuperado nesta preparação |
| Preparação local da v2 — 003 | pendente | V01/V02/V13 | Recuperar a v1 na 002; criar v2 e implementar/executar os seis testes na 003 |
| Push — 004 | pendente | V01/V05/V07/V13/V16 | v2/testes aprovados e prova V15 de escrita pública no push real |
| Avaliação — 005 | pendente | V01–V14 e V16, conforme papel | Specs 002–004; prompt publicado; auditar/criar dataset na 005 e executar avaliação completa |
| Entrega pública — 006 | pendente | V02/V03 | Resultados aprovados, evidências e compartilhamento público verificados na 006 |

Não há impedimento conhecido remanescente na preparação. As operações futuras
continuam pendentes pelos artefatos ainda não implementados; nenhum estado acima
declara o pipeline, a publicação ou as métricas acadêmicas concluídos.

<a id="roteiro-executavel"></a>

## Roteiro executável de contexto e traces — T030

Execute da raiz com o venv ativo, depois da instalação e dos checks locais do
[README](../README.md#como-executar). O [manifesto](integridade-inicial.json), o
[inventário](dependencias-preparacao.txt) e a [matriz atual](#matriz-atual) continuam
sendo as referências. O bloco é específico à condição `COND-001` documentada acima.

Por padrão, ele faz **somente leituras**: seleciona um workspace acessível, confere
o handle autenticado e o endpoint, consulta o projeto e verifica os quatro run IDs
já registrados. Não exige a chave OpenAI para ler esses traces. `LANGSMITH_WORKSPACE_ID`
exportado ou definido no `.env` prevalece sobre seleção automática; sem essa variável,
a seleção só é automática quando há exatamente um workspace acessível. Havendo vários,
configure localmente o ID correto antes de repetir. Nenhum perfil ou `.env` é alterado
pelo bloco; o ID selecionado é passado ao SDK/CLI apenas neste processo.

```bash
source venv/bin/activate
python - <<'PY'
import json
import logging
import os
import subprocess
import sys
import time
import uuid
import warnings
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from langsmith import Client
from langsmith.utils import LangSmithNotFoundError

load_dotenv('.env', override=False)
logging.disable(logging.CRITICAL)  # Não registrar corpos/headers de erros HTTP.
warnings.filterwarnings('ignore', category=DeprecationWarning)
stage = 'configuracao'


class CheckFailure(Exception):
    pass


class TracePending(Exception):
    pass


def check(ok, code):
    if not ok:
        raise CheckFailure(code)  # Somente códigos constantes, sem valores secretos.


def cli_json(*args):
    result = subprocess.run(['langsmith', *args], env=os.environ.copy(),
                            capture_output=True, text=True, timeout=30)
    result.check_returncode()  # A saída bruta não é impressa no tratamento de erro.
    return json.loads(result.stdout)


try:
    fresh = os.getenv('PREPARACAO_NOVAS_CHAMADAS', '0') == '1'
    required = ['LANGSMITH_API_KEY', 'LANGSMITH_PROJECT', 'USERNAME_LANGSMITH_HUB',
                'LANGSMITH_TRACING', 'LLM_PROVIDER', 'LLM_MODEL', 'EVAL_MODEL']
    if fresh:
        required.append('OPENAI_API_KEY')
    missing = [name for name in required if not os.getenv(name, '').strip()]
    print(json.dumps({'variaveis_ausentes': missing}))
    check(not missing, 'configuracao_incompleta')
    check(os.environ['USERNAME_LANGSMITH_HUB'] == 'fabiocsm', 'handle_configurado_divergente')
    check(os.environ['LLM_PROVIDER'] == 'openai', 'provider_divergente_da_condicao')
    check(os.environ['LANGSMITH_TRACING'].lower() == 'true', 'tracing_desabilitado')
    check(os.environ['LLM_MODEL'] == os.environ['EVAL_MODEL'] == 'gpt-4.1-2025-04-14',
          'modelos_divergentes_da_condicao')
    check(os.environ['LANGSMITH_PROJECT'] == 'mba-ia-pull-evaluation-prompt',
          'projeto_configurado_divergente_da_condicao')
    endpoint = os.getenv('LANGSMITH_ENDPOINT', 'https://api.smith.langchain.com')
    check(endpoint.rstrip('/') == 'https://api.smith.langchain.com', 'endpoint_divergente')

    stage = 'contexto_autenticado'
    for help_args in [('--help',), ('workspace', 'list', '--help'), ('api', '--help')]:
        subprocess.run(['langsmith', *help_args], capture_output=True, check=True, timeout=30)
    workspaces = cli_json('workspace', 'list', '--format', 'json')
    workspace = os.getenv('LANGSMITH_WORKSPACE_ID')
    if not workspace and len(workspaces) == 1:
        workspace = workspaces[0]['id']
    check(bool(workspace), 'selecionar_workspace_explicitamente')
    check(any(item['id'] == workspace for item in workspaces), 'workspace_sem_acesso')
    settings = cli_json('api', 'settings', '--workspace', workspace, '--format', 'json')
    check(settings['id'] == workspace, 'tenant_divergente')
    check(settings.get('tenant_handle') == os.environ['USERNAME_LANGSMITH_HUB'],
          'handle_autenticado_divergente')
    print(json.dumps({name: settings.get(name) for name in
                      ('id', 'display_name', 'tenant_handle')}))
    os.environ['LANGSMITH_WORKSPACE_ID'] = workspace
    client = Client(timeout_ms=10000)
    project_name = os.environ['LANGSMITH_PROJECT']

    stage = 'projeto'
    try:
        project = client.read_project(project_name=project_name)
    except LangSmithNotFoundError:
        project = None
        print(json.dumps({'projeto': 'pendente', 'causa': 'nao_encontrado',
                          'proxima_acao': 'confirmar_nome_ou_executar_dupla_minima'}))
    if project is not None:
        check(str(project.tenant_id) == workspace, 'projeto_em_outro_tenant')
    if project is None and not fresh:
        raise SystemExit(2)  # Ausência confirmada; não é falha de autenticação.

    runs = [('geracao', '2b6fc47f-6035-44d3-9b79-14c40fac8d01', None),
            ('avaliacao', '2d4513ae-ad75-45f6-a64b-bf49f97b0b44', None),
            ('geracao', '1d760df9-5253-46d8-a501-b6f609039e63', 'REP-001B'),
            ('avaliacao', '33f5dae2-acff-47ea-b73a-28eb5b45ad04', 'REP-001B')]
    if fresh:
        stage = 'chamadas_minimas'
        sys.path.insert(0, 'src')
        from utils import get_llm, get_eval_llm
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_core.tracers.langchain import wait_for_all_tracers

        runs = []
        reproduction = 'REP-' + datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat()
        roles = os.getenv('PREPARACAO_PAPEIS', 'geracao,avaliacao').split(',')
        check(bool(roles) and len(roles) == len(set(roles))
              and set(roles) <= {'geracao', 'avaliacao'}, 'papeis_invalidos')
        try:
            for role, factory in [('geracao', get_llm), ('avaliacao', get_eval_llm)]:
                if role not in roles:
                    continue
                run_id = str(uuid.uuid4())
                requested = os.environ['LLM_MODEL' if role == 'geracao' else 'EVAL_MODEL']
                print(json.dumps({'tentativa': role, 'run_id': run_id, 'modelo': requested,
                                  'data': datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat()}),
                      flush=True)
                response = factory(temperature=0).invoke(
                    [SystemMessage(content='Responda brevemente.'),
                     HumanMessage(content='Escreva apenas OK.')],
                    config={'run_id': uuid.UUID(run_id), 'run_name': 'preparacao-001-' + role,
                            'tags': ['preparacao-001', 'reproducao', role],
                            'metadata': {'condition': 'COND-001', 'verification_role': role,
                                         'reproduction_id': reproduction}})
                check(bool(response.content), 'resposta_vazia')
                print(json.dumps({'sucesso': role, 'run_id': run_id,
                                  'modelo_solicitado': requested,
                                  'modelo_retornado': response.response_metadata.get('model_name'),
                                  'uso': {key: (response.usage_metadata or {}).get(key) for key in
                                          ('input_tokens', 'output_tokens', 'total_tokens')}}),
                      flush=True)
                runs.append((role, run_id, reproduction))
        finally:
            wait_for_all_tracers()

    stage = 'conferencia_traces'
    for attempt in range(4):
        try:
            project = client.read_project(project_name=project_name)
            check(str(project.tenant_id) == workspace, 'projeto_em_outro_tenant')
            verified = []
            for role, run_id, reproduction in runs:
                run = client.read_run(run_id)
                if run.end_time is None:
                    raise TracePending()
                check(str(run.session_id) == str(project.id), 'trace_em_outro_projeto')
                check(not run.error and bool(run.outputs), 'trace_com_erro_ou_sem_saida')
                metadata = run.extra.get('metadata', {})
                params = run.extra.get('invocation_params', {})
                requested = os.environ['LLM_MODEL' if role == 'geracao' else 'EVAL_MODEL']
                returned = (run.outputs or {}).get('llm_output', {}).get('model_name')
                check(metadata.get('condition') == 'COND-001', 'condicao_divergente')
                check(metadata.get('verification_role') == role, 'papel_divergente')
                check(metadata.get('reproduction_id') == reproduction, 'reproducao_divergente')
                check(params.get('temperature') == 0, 'temperatura_divergente')
                check((params.get('model') or params.get('model_name')) == requested,
                      'modelo_solicitado_divergente')
                check(returned == requested, 'modelo_retornado_divergente')
                verified.append({'papel': role, 'run_id': run_id, 'modelo': returned,
                                 'input_tokens': run.prompt_tokens,
                                 'output_tokens': run.completion_tokens,
                                 'trace': client.get_run_url(run=run, project_id=project.id)})
            break
        except (LangSmithNotFoundError, TracePending):
            if attempt == 3:
                raise
            time.sleep(2)  # Reconsultar apenas ausência/incompletude; nunca repetir LLM.
    print(json.dumps({'projeto': project.name, 'project_id': str(project.id),
                      'tenant_id': str(project.tenant_id), 'traces': verified,
                      'novas_chamadas_llm': len(runs) if fresh else 0}, ensure_ascii=False))
except Exception as error:
    diagnostic = {'etapa': stage, 'estado': 'impedido', 'categoria': type(error).__name__,
                  'http_status': getattr(error, 'status_code', None),
                  'cli_exit_code': getattr(error, 'returncode', None)}
    if isinstance(error, CheckFailure):
        diagnostic['causa'] = error.args[0]
    print(json.dumps(diagnostic, ensure_ascii=False))  # Sem str(error), stderr ou headers.
    raise SystemExit(1)
PY
```

Resultado esperado no modo padrão: status 0, workspace/handle e projeto/tenant
correspondentes, quatro traces concluídos, temperatura zero, modelos correspondentes
e `novas_chamadas_llm=0`. Projeto confirmado ausente termina com status 2 e causa
`nao_encontrado`. Autenticação, permissão, workspace/handle divergente e demais falhas
terminam com status 1 e diagnóstico sanitizado; não são convertidas em projeto ausente.
Ausência/incompletude de trace admite quatro tentativas com intervalo de 2 segundos;
o timeout é por requisição. Não há repetição automática de chamadas LLM pelo roteiro;
eventuais retries do SDK devem ser conferidos nos traces/consumo.

Para uma **nova dupla mínima real**, execute esse mesmo bloco em processo iniciado
com `PREPARACAO_NOVAS_CHAMADAS=1` (por exemplo, `PREPARACAO_NOVAS_CHAMADAS=1 python -`
no lugar de `python -`). Isso consome API e produz novos IDs. Mantenha os modelos da
COND-001; mudar provedor/modelo exige nova condição, atualização do roteiro e novas
provas, sem comparar resultados de condições diferentes como se fossem iguais.
Guarde os registros sanitizados impressos no relatório, somando tentativas/tokens e
custo estimado ao balanço. Se uma chamada falhar, preserve seu ID/diagnóstico antes
de corrigir e repetir somente o papel ainda não comprovado. Uso não reportado e
cobrança inacessível devem ser registrados como não disponíveis.
Para retomar somente um papel, use também `PREPARACAO_PAPEIS=geracao` ou
`PREPARACAO_PAPEIS=avaliacao` no processo; a primeira prova de uma condição requer
os dois papéis. Não reutilize uma identificação de condição após mudar seus modelos.

Uma nova reprodução integral também exige criar/ativar outro venv limpo, repetir
instalação/pip check/imports e os checks de integridade do quickstart, preservando
o venv e a baseline iniciais. A leitura dos quatro traces antigos valida este
roteiro; não constitui uma nova reprodução integral nem um experimento acadêmico.

## Verificação da convergência — T029/T030

2026-10-17T20:14:56-03:00: T029 consolidou a [matriz atual](#matriz-atual), preservando os IDs
V01–V16 e todas as matrizes históricas. V15 continua pendente na spec 004; a
preparação pronta não declara operações futuras concluídas.

T030 publicou o [bloco executável](#roteiro-executavel) e o vinculou ao README,
ao manifesto e ao inventário. O código extraído desse próprio bloco foi executado
no venv da preparação com `PREPARACAO_NOVAS_CHAMADAS=0`: status 0, handle
`fabiocsm`, projeto `10e3f705-af88-4cee-9d79-4a9fdb4a959f` e tenant `15dd5852-a835-4163-826c-e78668fd2a9c`.
Os quatro run IDs existentes foram confirmados com término sem erro, metadados
da condição/papel/reprodução, modelo solicitado/retornado `gpt-4.1-2025-04-14`,
temperatura zero e 23/2 tokens por chamada.

**Novas chamadas LLM nesta convergência: 0.** Os 100 tokens lidos são o consumo
histórico das quatro chamadas existentes, não consumo novo. Balanço anterior
inalterado: estimativa US$ 0,000248; cobrança observada não disponível.
O modo que realiza novas chamadas está documentado como opção explícita e não foi
executado nesta validação. Não houve novo experimento ou reprodução integral.

Oito cenários locais, com respostas substituídas apenas para testar controles e
sem rede, confirmaram: chave ausente bloqueia antes das consultas; workspace
ambíguo exige seleção; handle divergente impede avanço; autenticação inválida
retorna status 1 sem se tornar projeto ausente; projeto ausente retorna status 2;
tenant divergente bloqueia; trace inicialmente ausente pode ser confirmado nas
reconsultas; ausência persistente encerra após quatro tentativas/três intervalos.
Diagnósticos não incluíram respostas HTTP, stderr ou valores sensíveis dos testes.
Esses cenários não são evidência acadêmica de qualidade nem substituem os traces reais.

Revisão final em 2026-10-17T20:15:31-03:00: 30 tarefas marcadas; V01–V16 completos na matriz atual; links locais e sintaxe do bloco aprovados; histórico preservado; hashes dos quatro protegidos e 15 casos iguais ao manifesto/origem; diff de protegidos vazio; `git diff --check` status 0; nenhum valor de credencial nos artefatos de entrega; ignores conferidos. `.specify/extensions.yml` ausente: sem hooks antes/depois de implementação.
