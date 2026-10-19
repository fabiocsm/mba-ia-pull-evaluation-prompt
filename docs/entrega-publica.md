# Entrega pública — spec 006

Registro iniciado em 2026-10-19. Fonte dos resultados: [avaliação da 005](avaliacao-v2.md#entrega-à-006).
O dataset, os três experimentos e seis traces estão públicos e foram conferidos sem login.
Nenhuma nota nova foi produzida nesta etapa.

## Escopo e limites

Preservar o prompt final, os quatro arquivos protegidos, a v1, o dataset e todo o histórico.
Compartilhar o dataset uma única vez, depois da autorização explícita do autor no chat;
reutilizar qualquer link existente. Compartilhar runs somente se necessário e autorizado.
Push e atualização de main dependem de autorização própria. Commits locais autorizados pelo autor no chat em 2026-10-19: “Sim, autorizar commits locais”.
Compartilhamento único autorizado: “Sim, compartilhar uma única vez”. Push e main seguem pendentes.
Screenshots serão capturas reais, inspecionadas e versionadas em `docs/evidencias/`.

## Rastreabilidade

| Requisito | Contrato | Guia | Tarefas |
| --- | --- | --- | --- |
| FR-001 | E02/E03 | W03/W04 | T006–T008 |
| FR-002 | E04 | W05 | T009–T011 |
| FR-003 | E03/E04 | W04/W05 | T005/T008–T010 |
| FR-004 | E02 | W03 | T005–T007 |
| FR-005 | E05 | W06 | T012–T014/T016 |
| FR-006 | E03/E05 | W04/W06 | T008/T012/T015 |
| FR-007 | E05/E06 | W07 | T016–T018 |
| FR-008 | E08 | W09 | T020–T022 |
| FR-009 | E01/E07 | W01/W08 | T001/T019 |
| FR-010 | E06/E09 | W07 | T017/T018/T023 |

## ResultadoAprovado

| Campo | Valor |
| --- | --- |
| Ciclo | CIC-03 — aprovado, final |
| Experimento | `d864cfbb-6ab9-4901-ab06-62f68ccd96fc` |
| Nome | `fabiocsm-bug_to_user_story_v2-9c836e20` |
| Dataset | `8c78638d-37a5-4175-9984-8db0e3473228` — 15 casos, 5 simples/7 médios/3 complexos |
| Revisão | `36a96c0540682ed6b8569487222b88e11d1889a3976b75fea83553dc662b696f` |
| SHA-256 arquivo v2 | `692df6ae86848e2dce0fc1a9c2d1f6fec95fc48721a960837fbdd8de3f958974` |
| SHA-256 definição v2 | `f94735be2936253b11eb2696fb957db67e4d6529629f903720845f078e467ca2` |
| Condição | COND-001: openai, gpt-4.1-2025-04-14 para geração e juízes, temperatura 0 |
| Médias | Helpfulness 0.8773; Correctness 0.8754; F1-Score 0.8474; Clarity 0.8513; Precision 0.9033 |
| Média geral | 0.8709 |
| Custo herdado dos ciclos | US$ 0,755018 |
| Limitações | Notas individuais abaixo de 0.8; meta de CPU inventada em #14 (80%); opções de código na dúvida de #8 |

## CompartilhamentoDataset

Estado antes: **não_compartilhado**. Consulta GET em 2026-10-19 retornou HTTP 200 e JSON
`null`; o SDK 0.13.0 levanta `TypeError` ao tentar montar o schema desse corpo.
Autorização explícita no chat: “Sim, compartilhar uma única vez”.
Execução em 2026-10-19T02:45:50.314707-03:00: Uma única chamada Client.share_dataset executada com autorização explícita.
URL original: https://smith.langchain.com/public/72eee98c-a991-4c8e-b825-b2b9b898df14/d
Conferência posterior por leitura: mesmo token e mesma URL confirmados; nunca repetir share_dataset.

## EvidênciaPública

Conferência em 2026-10-19, navegador integrado sem login (botão “Log in” conferido
no Hub na mesma sessão; páginas públicas de dataset/traces usam cabeçalho compacto). Estados permitidos: `visível`, `parcial`, `exige_login`;
`parcial`/`exige_login` exige screenshot complementar para o mesmo alvo. Tipos permitidos:
`link_dataset`, `link_experimento`, `link_prompt`, `link_trace`, `screenshot`, `fork`.

| id | tipo | alvo | endereco | relacao | conferencia_anonima | sigilo |
| --- | --- | --- | --- | --- | --- | --- |
| EV-01 | link_dataset | dataset 15 | https://smith.langchain.com/public/72eee98c-a991-4c8e-b825-b2b9b898df14/d | dataset_id 8c78638d-37a5-4175-9984-8db0e3473228 | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-02 | link_experimento | experimento final | https://smith.langchain.com/public/72eee98c-a991-4c8e-b825-b2b9b898df14/d/compare?selectedSessions=d864cfbb-6ab9-4901-ab06-62f68ccd96fc | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-03 | link_prompt | prompt | https://smith.langchain.com/hub/fabiocsm/bug_to_user_story_v2/36a96c05?tab=0 | hub_commit 36a96c0540682ed6b8569487222b88e11d1889a3976b75fea83553dc662b696f | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-04 | link_trace | trace simples | https://smith.langchain.com/public/0f791884-477a-4a1b-ba28-fe172098051e/r | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc; example_id 2d3d7a29-14bf-4df7-bc8e-3681ba191140 | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-05 | link_trace | juízes simples | https://smith.langchain.com/public/324bbbae-32ff-4493-a879-34bca11068a5/r | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc; source_run_id b7973768-c22d-4614-b359-a49e6df21293; example_id 2d3d7a29-14bf-4df7-bc8e-3681ba191140 | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-06 | link_trace | trace médio | https://smith.langchain.com/public/a8211760-0517-47a8-8909-85f0fdc4bbbb/r | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc; example_id 307a4c8c-710f-4287-b880-07a10752cec2 | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-07 | link_trace | juízes médio | https://smith.langchain.com/public/4d521f2b-a4ca-4199-bb09-11baed8ba8c5/r | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc; source_run_id 6c19d03a-dbda-40ea-bf80-382f2cbb4010; example_id 307a4c8c-710f-4287-b880-07a10752cec2 | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-08 | link_trace | trace complexo | https://smith.langchain.com/public/c21a85d7-e3a0-4e0e-b770-5f030b785160/r | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc; example_id 28c9bca9-e7be-4f93-b1e4-fe1637222566 | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-09 | link_trace | juízes complexo | https://smith.langchain.com/public/af97f925-10c2-42c1-932b-97373b323e24/r | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc; source_run_id 8b32f3ca-937d-4872-9fbd-a7cf63fadd63; example_id 28c9bca9-e7be-4f93-b1e4-fe1637222566 | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-10 | screenshot | dataset 15 | evidencias/avaliacao-v2-dataset.png | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-11 | screenshot | trace complexo | evidencias/avaliacao-v2-juizes-complexo.png | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-12 | screenshot | trace médio | evidencias/avaliacao-v2-juizes-medio.png | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-13 | screenshot | trace simples | evidencias/avaliacao-v2-juizes-simples-f1.png | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-14 | screenshot | trace simples | evidencias/avaliacao-v2-juizes-simples.png | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-15 | screenshot | cinco médias | evidencias/avaliacao-v2-medias-f1-helpfulness.png | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-16 | screenshot | cinco médias | evidencias/avaliacao-v2-medias.png | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-17 | screenshot | trace complexo | evidencias/avaliacao-v2-mensagens-complexo.png | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-18 | screenshot | trace médio | evidencias/avaliacao-v2-mensagens-medio.png | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-19 | screenshot | trace simples | evidencias/avaliacao-v2-mensagens-simples.png | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-20 | screenshot | trace complexo | evidencias/avaliacao-v2-trace-complexo-cpu.png | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-21 | screenshot | trace complexo | evidencias/avaliacao-v2-trace-complexo-resposta.png | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-22 | screenshot | trace complexo | evidencias/avaliacao-v2-trace-complexo.png | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-23 | screenshot | trace médio | evidencias/avaliacao-v2-trace-medio-resposta.png | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-24 | screenshot | trace médio | evidencias/avaliacao-v2-trace-medio.png | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-25 | screenshot | trace simples | evidencias/avaliacao-v2-trace-simples.png | experiment_id d864cfbb-6ab9-4901-ab06-62f68ccd96fc | visível — 2026-10-19 | inspecionado; sem credenciais ou dados de acesso |
| EV-26 | link_experimento | reprodução REP-006 | https://smith.langchain.com/public/72eee98c-a991-4c8e-b825-b2b9b898df14/d/compare?selectedSessions=e3211f91-99f5-41d6-bb7e-36aad1085974 | experiment_id e3211f91-99f5-41d6-bb7e-36aad1085974; hub_commit 36a96c05 | visível — 2026-10-19 | inspecionado; sem dados de acesso |
| EV-27 | fork | código e evidências em dev | https://github.com/fabiocsm/mba-ia-pull-evaluation-prompt/tree/dev | publicação inicial 017e724; v2 692df6ae | visível — 2026-10-19 | inspecionado; sem credenciais |
| EV-28 | fork | PR de dev para main | https://github.com/fabiocsm/mba-ia-pull-evaluation-prompt/pull/1 | PR 1; base main; head dev | visível — 2026-10-19 | inspecionado; sem credenciais |

### Capturas reais

Nas capturas anteriores à reprodução, a primeira linha do dashboard é CIC-03 (`9c836e20`); a interface arredonda as médias para
0.88 / 0.88 / 0.85 / 0.85 / 0.90. A tabela foi rolada horizontalmente em duas capturas,
sem editar o conteúdo. O navegador devolveu capturas em JPEG; foram recodificadas para PNG via sips, sem
recorte, retoque ou alteração de conteúdo. Originais locais em results/capturas-originais/.
As notas com quatro casas vêm da auditoria da 005, cuja agregação
arredonda cada média antes de calcular a média geral (0.8709).
Os links permitem ler todo o conteúdo; as capturas registram trechos representativos.
A inspeção não encontrou chaves, e-mails de acesso, cabeçalhos ou configurações privadas.

![avaliacao-v2-dataset](evidencias/avaliacao-v2-dataset.png)

![avaliacao-v2-juizes-complexo](evidencias/avaliacao-v2-juizes-complexo.png)

![avaliacao-v2-juizes-medio](evidencias/avaliacao-v2-juizes-medio.png)

![avaliacao-v2-juizes-simples-f1](evidencias/avaliacao-v2-juizes-simples-f1.png)

![avaliacao-v2-juizes-simples](evidencias/avaliacao-v2-juizes-simples.png)

![avaliacao-v2-medias-f1-helpfulness](evidencias/avaliacao-v2-medias-f1-helpfulness.png)

![avaliacao-v2-medias](evidencias/avaliacao-v2-medias.png)

![avaliacao-v2-mensagens-complexo](evidencias/avaliacao-v2-mensagens-complexo.png)

![avaliacao-v2-mensagens-medio](evidencias/avaliacao-v2-mensagens-medio.png)

![avaliacao-v2-mensagens-simples](evidencias/avaliacao-v2-mensagens-simples.png)

![avaliacao-v2-trace-complexo-cpu](evidencias/avaliacao-v2-trace-complexo-cpu.png)

![avaliacao-v2-trace-complexo-resposta](evidencias/avaliacao-v2-trace-complexo-resposta.png)

![avaliacao-v2-trace-complexo](evidencias/avaliacao-v2-trace-complexo.png)

![avaliacao-v2-trace-medio-resposta](evidencias/avaliacao-v2-trace-medio-resposta.png)

![avaliacao-v2-trace-medio](evidencias/avaliacao-v2-trace-medio.png)

![avaliacao-v2-trace-simples](evidencias/avaliacao-v2-trace-simples.png)

## RegistroReprodução

`REP-006` (autor, clone limpo): **concluída e aprovada**, após correção documental. Commit inicial `460bc3c227d4f5e002839f662a276bfb0ac15015`,
clone local sem hardlinks em diretório temporário da sessão, Python 3.11.14/venv novo,
requirements.txt instalado, pip check aprovado, .env local copiado sem versionamento.

Primeira tentativa: pull código 0, 466 testes estruturais aprovados; suíte conjunta
812 aprovados/57 falhas da auditoria. Diagnóstico: a nova coleta mudou somente datas
`retrieved_at`/`repository_observed_at` e estatística `num_downloads`; mensagens e revisão
continuaram idênticas, mas o hash da v1 divergiu. Push, gate e avaliação não foram executados
nessa tentativa. Correção documental: guardar `results/v1-nova-coleta.yml`, comparar conteúdo,
revisão e metadados do template e restaurar baseline versionada somente com igualdade.
Três testes offline verificam os caminhos de metadados dinâmicos, mensagem alterada e revisão
divergente. Nenhuma alteração em pull_prompts.py, na v1 da entrega ou nos protegidos.
A tentativa foi retomada no passo afetado a partir do commit corrigido
`22e1e090a9786c79be8e11855e21430f264d9297` (`COMMIT_ENTREGA` efetivamente reproduzido).
Até a retomada não houve custo LLM. O clone recebeu esse commit pelo fetch do repositório
local, mantendo o venv novo e o .env local; nenhuma cópia de venv ou dependências da raiz.

| Passo literal do README | Código | Resultado |
| --- | --- | --- |
| python3 -m venv / ativação / pip install | 0 | CPython 3.11.14; pins do requirements.txt instalados em venv novo |
| pip check | 0 | Nenhum conflito |
| Bloco de configuração | 0 | Variáveis presentes, tracing efetivo habilitado, COND-001 |
| python src/pull_prompts.py | 0 | Origem/revisão iguais; snapshot da coleta arquivado |
| PRESERVAR_BASELINE_V1 | 0 | Mensagens e revisão iguais; baseline v1 original preservada |
| pytest tests/test_prompts.py -v | 0 | 466 aprovados |
| pytest -q | 0 | 872 aprovados no clone corrigido |
| python src/push_prompts.py | 0 | Revisão existente conferida após conflito; descrição/tags reaplicadas; nenhuma nova revisão |
| AVALIACAO_DATASET | 0 | 15 casos, 5/7/3, idêntico; criado=false |
| AVALIACAO_GATE | 0 | gate_ok; custo anterior 0.755018; HEAD 36a96c05 |
| python src/evaluate.py com pipefail | 0 | APROVADO; novo experimento abaixo |
| AVALIACAO_AUDITORIA | 0 | Completo, estável, aprovado; zero divergências |

REP-006_EXPERIMENT_ID: `e3211f91-99f5-41d6-bb7e-36aad1085974`

[Reprodução pública — não é o experimento final](https://smith.langchain.com/public/72eee98c-a991-4c8e-b825-b2b9b898df14/d/compare?selectedSessions=e3211f91-99f5-41d6-bb7e-36aad1085974), nome
`fabiocsm-bug_to_user_story_v2-c6bb5cf0`. Execução iniciada em 2026-10-19T02:57:38-03:00;
15 respostas/75 notas válidas, mesma revisão final nos 15 templates, HEAD antes/depois igual,
nenhuma divergência da auditoria. Acesso público conferido no navegador integrado sem login.

| Métrica da reprodução | Média |
| --- | --- |
| Helpfulness | 0.8767 |
| Correctness | 0.8758 |
| F1-Score | 0.8469 |
| Clarity | 0.8487 |
| Precision | 0.9047 |
| Média geral | 0.8706 |

Tokens reportados (nenhum substituído por estimativa): geração 27.671 entrada/6.455 saída;
juízes 57.267 entrada/5.723 saída. Custo estimado US$ 0,267300 pelas tarifas de COND-001;
acumulado das avaliações US$ 1,022318. Preparação anterior US$ 0,000248; total conhecido
incluindo preparação US$ 1,022566. Cobrança efetiva não consultada; cálculo não desconta cache.
Há notas individuais abaixo de 0.8, como Clarity/Precision 0.70 do caso #1. A reprodução
não substitui CIC-03 nem afirma ausência de alucinações. Não houve edição da v2.
Logs completos locais em results/REP-006-preflight.log e results/REP-006-execucao-auditoria.log;
resumo auditado acima e experimento público são as evidências entregues, além dos logs locais.

`REP-006B` (segundo_executor, fork público, credenciais próprias): **pendente**, conforme
resposta explícita do autor em 2026-10-19: “Registrar segundo executor como pendente”.
SC-004 não é satisfeito pela reprodução do próprio autor.

## ConferênciaIntegridade

Entrada em 2026-10-19: quatro hashes iguais a [integridade-inicial.json](integridade-inicial.json);
v1 SHA-256 `2cddcf8f8183b4d29a5bca4d4efca17601962aa98ac75323f7dabbfa905c0d70`;
v2 igual ao hash acima e HEAD público conferido. Dataset local: 15 casos, distribuição 5/7/3.
Diff `main..dev` dos quatro protegidos vazio. Conferência final T019 em 2026-10-19: quatro protegidos e ambos os prompts iguais;
OpenAI 1.6.2/Gemini 4.4.0 instalados; utils.py intacto. Varredura de 140 arquivos versionados
por valores secretos reais do .env e padrões de chaves: zero ocorrências. Imagens inspecionadas
visualmente. Testes 872 aprovados; git diff --check limpo. Links Markdown locais conferidos,
incluindo âncoras; zero erros. Nova leitura do Hub após reprodução confirmou HEAD estável.

## PacoteEntrega

Fork: [fabiocsm/mba-ia-pull-evaluation-prompt](https://github.com/fabiocsm/mba-ia-pull-evaluation-prompt),
público, fork de `devfullcycle/mba-ia-pull-evaluation-prompt`, branch padrão `main`.
`origin/main` local aponta para `a94ce44`; consulta ao GitHub confirma o fork, sem fetch ou push.

Estado: **publicado em dev**, com [PR #1](https://github.com/fabiocsm/mba-ia-pull-evaluation-prompt/pull/1) aberto de `dev` para `main`.
A conferência final de `main` (T022) aguarda o merge do PR. A autorização do autor em
2026-10-19 foi “Autorizar dev e criar PR para main”; não houve merge nem atualização direta
de main. O PR foi anexado ao chat e conferido sem login, com “Sign in” e estado “Open”.

Publicação inicial: `git push -u origin dev`, código 0, HEAD
`017e72492a6cd247b996f4b93e13617b8bcaaa32`, 27 commits da entrega. `gh pr create` retornou
PR #1, aberto e pronto para revisão, base main/head dev, sem conflitos. O registro desta
operação integra o mesmo PR; o histórico de commits identifica sua revisão final.

[Conteúdo público em dev](https://github.com/fabiocsm/mba-ia-pull-evaluation-prompt/tree/dev): README, scripts, v2 e 16 PNG conferidos por HTTP sem
credenciais (24 arquivos idênticos byte a byte ao payload local inicial). V2 SHA-256
`692df6ae86848e2dce0fc1a9c2d1f6fec95fc48721a960837fbdd8de3f958974`.
Varredura dos 233 objetos de arquivo do histórico inicialmente enviado, além da árvore
atual: nenhuma credencial real ou padrão de chave encontrado. O PR descreve os resultados,
verificações e pendências; links LangSmith originais preservados.

`main` remoto permanece em `a94ce443299b4928d0f1e08cecdacf7a36ff5fb1`. Publicação em dev e
conferência do PR não substituem a conferência pós-merge da branch padrão (T022).

## Encerramento

Encerramento parcial: evidências LangSmith públicas e conferidas; 16 PNG versionadas;
README/testes/integração íntegros; REP-006 aprovada, custo acumulado das avaliações US$ 1,022318.
CIC-03 continua final, média 0.8709. T020/T021 concluídas pela opção autorizada de PR:
dev publicada e PR #1 aberto. T022 aguarda merge e conferência em main.
SC-004 por segundo executor (REP-006B) permanece **pendente** por decisão explícita do autor,
sem execução independente apresentada. A reprodução do autor não o substitui.
Este registro não declara a entrega integral concluída.

## Compartilhamento dos traces

Autorização explícita do autor em 2026-10-19: “Sim, compartilhar os seis traces”.

| Caso | Run | URL original |
| --- | --- | --- |
| simples_geracao | `01a1525d-899e-7711-835f-249803cf7318` | https://smith.langchain.com/public/0f791884-477a-4a1b-ba28-fe172098051e/r |
| medio_geracao | `01a1525d-3ff5-7ae0-8915-df303b9a69b8` | https://smith.langchain.com/public/a8211760-0517-47a8-8909-85f0fdc4bbbb/r |
| complexo_geracao | `01a1525d-0432-7f50-99c6-c059ec587aa2` | https://smith.langchain.com/public/c21a85d7-e3a0-4e0e-b770-5f030b785160/r |
| simples_avaliador | `b7973768-c22d-4614-b359-a49e6df21293` | https://smith.langchain.com/public/324bbbae-32ff-4493-a879-34bca11068a5/r |
| medio_avaliador | `6c19d03a-dbda-40ea-bf80-382f2cbb4010` | https://smith.langchain.com/public/4d521f2b-a4ca-4199-bb09-11baed8ba8c5/r |
| complexo_avaliador | `8b32f3ca-937d-4872-9fbd-a7cf63fadd63` | https://smith.langchain.com/public/af97f925-10c2-42c1-932b-97373b323e24/r |
