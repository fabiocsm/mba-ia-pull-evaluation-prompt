# Research: Entrega pública com evidências acessíveis e reprodução

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md) | **Data**: 2026-10-19

Pesquisa feita **somente por leitura**: SDK instalado (`langsmith==0.13.0`), consultas
autenticadas sem escrita, `gh repo view` e Git local. Nenhum compartilhamento, push Git,
chamada LLM ou experimento foi executado nesta etapa.

## Estado observado em 2026-10-19

| Item | Observação (somente leitura) | Consequência |
| --- | --- | --- |
| Dataset `mba-ia-pull-evaluation-prompt-eval` (`8c78638d-37a5-4175-9984-8db0e3473228`) | Não compartilhado: `GET /datasets/{id}/share` devolve corpo vazio e o SDK 0.13.0 levanta `TypeError` em `read_dataset_shared_schema` | Nenhum link público existe; o primeiro `share_dataset` define o endereço definitivo (FR-004) |
| Experimentos do dataset | Três: `CIC-01` `86196746…`, `CIC-02` `c7d175e1…`, `CIC-03` `d864cfbb…` (final, aprovado) | O compartilhamento expõe o histórico completo, como pede o README |
| Traces finais | `read_run_shared_link` do trace #1 de `CIC-03` devolve `None` | Nenhum run compartilhado individualmente |
| Prompt `fabiocsm/bug_to_user_story_v2` | Público, HEAD `36a96c05…696f`, três commits | Link público do prompt já existe ([004/005](../../docs/avaliacao-v2.md)) |
| Fork `fabiocsm/mba-ia-pull-evaluation-prompt` | Público, fork de `devfullcycle/…`, branch padrão `main`; `origin/main` = `a94ce44` (base); sem `origin/dev` | Todo o trabalho das 001–005 está **somente local** em `dev`; a entrega exige push autorizado |
| Evidências versionadas | `docs/evidencias/` com três PNG da 004; `screenshots/` e `results/` ignorados | Novas capturas vão para `docs/evidencias/` |

## D01 — Compartilhar o dataset uma única vez, com autorização

- **Decision**: executar exatamente o trecho do README
  (`Client().share_dataset(dataset_name="mba-ia-pull-evaluation-prompt-eval")["url"]`) **uma
  vez**, somente após autorização explícita do autor no chat e depois de conferir de novo que
  não há compartilhamento prévio. Registrar a URL pública retornada (o token faz parte dela e
  só dá leitura ao dataset compartilhado, não ao workspace). Nunca chamar `unshare_dataset`
  nem repetir `share_dataset`.
- **Experimentos**: o link público de cada experimento é o que se alcança **a partir do link
  compartilhado** do dataset (página pública de comparação/experimento sob `/public/<token>/`),
  registrado na conferência anônima. URLs de workspace (`smith.langchain.com/o/…`), como as do
  registro da 005, não são evidência pública (constituição V) e não aparecem como tal no README.
- **Rationale**: FR-001/FR-004/FR-006 e o README (“ao compartilhar de novo, o link muda”).
  Compartilhar torna dados públicos: ação externa que exige confirmação.
- **Alternatives considered**: somente screenshots (o README aceita, mas o link público é a
  forma principal e a spec exige links conferidos sem login); compartilhar antes do
  experimento final (já não se aplica; a 005 terminou).

## D02 — Traces: link público quando visível, screenshots sempre

- **Decision**: após D01, abrir o link em sessão anônima e verificar se o experimento final
  e os três traces de `CIC-03` (#1 simple, #10 medium, #14 complex) mostram entrada,
  mensagens, resposta, juízes e feedback. Screenshots legíveis desses três traces e do
  resumo das cinco médias são capturados **sempre** (FR-002). Se o detalhe do trace não for
  público pelo link do dataset, usar `Client.share_run` nos três runs raiz, com autorização
  explícita, e registrar as URLs; o link do dataset não muda. Como os juízes rodam em traces
  **separados** (projeto `evaluators`, ligados pelo `source_run_id` do feedback), o conjunto de
  `share_run` inclui também os três runs do avaliador de `CIC-03` (#1
  `b7973768-c22d-4614-b359-a49e6df21293`, #10 `6c19d03a-dbda-40ea-bf80-382f2cbb4010`, #14
  `8b32f3ca-937d-4872-9fbd-a7cf63fadd63`); compartilhar só os runs `target` não mostraria os
  julgamentos.
- **Rationale**: FR-003 e o edge case “link não mostra detalhes”. `share_run` cria links
  independentes, sem invalidar o do dataset.
- **Alternatives considered**: só `share_run` (não mostra dataset nem notas agregadas); só
  link do dataset (não verificável antes de compartilhar).

## D03 — Captura e armazenamento das screenshots

- **Decision**: capturar no navegador integrado, em sessão **sem login** sempre que o
  conteúdo for público; converter o JPEG retornado em PNG real sem editar conteúdo, salvar em
  `docs/evidencias/avaliacao-v2-*.png` (versionado) e conferir antes que nenhuma imagem mostre
  e-mail, chave, cabeçalho ou configuração privada. Capturas exigidas: dataset com 15
  exemplos; experimento final com as cinco médias; três traces; opcionalmente comparação dos
  três experimentos.
- **Rationale**: precedente da 004 (três PNG em `docs/evidencias/`); `screenshots/` é
  ignorado e não basta (constituição V).
- **Alternatives considered**: hospedar imagens fora do repositório (outro serviço externo,
  sem ganho); usar `screenshots/` (ignorado).

## D04 — README: três seções obrigatórias sobre o enunciado preservado

- **Decision**: manter intactas as seções do enunciado (linhas até `Dicas Finais`) e
  reorganizar as seções do autor em `Como Executar` (roteiro único e ordenado, com links para
  os registros detalhados das specs), `Técnicas Aplicadas (Fase 2)` (Role Prompting e
  Few-shot com trechos da v2 final, mais as regras de critérios e de valores dos ciclos) e
  `Resultados Finais` (cinco médias e média geral de `CIC-03`, revisão `36a96c05`, tabela dos
  três ciclos, comparação qualitativa v1/v2, links públicos, screenshots, limitações
  incluindo a meta inventada de #14). Notas ilustrativas do enunciado nunca são apresentadas
  como resultado.
- **Rationale**: FR-005/FR-006/SC-003. O README atual acumula seções por spec, úteis como
  histórico mas longas para o avaliador.
- **Alternatives considered**: README novo sem o enunciado (proibido: preservar requisitos).

## D05 — Comparação v1/v2 qualitativa; numérica só com decisão do autor

- **Decision**: a comparação obrigatória é qualitativa (conteúdo e decisões). A comparação
  numérica da v1 não é executada e fica registrada como tal: `python src/evaluate.py` avalia
  somente `{username}/bug_to_user_story_v2`, e publicar a v1 com esse nome mudaria a revisão
  final. Só com decisão explícita do autor seria aberta uma atividade adicional (ver
  alternativa), com custo e condição registrados.
- **Rationale**: `evaluate.py` avalia somente `{username}/bug_to_user_story_v2`; avaliar a v1
  exigiria alterar o protegido ou o prompt final (FR-006, constituição I).
- **Alternatives considered**: script próprio chamando `run_experiment` com outro nome de
  prompt (reutiliza funções fornecidas sem alterá-las, mas cria uma via paralela de
  avaliação; só com decisão explícita do autor e custo registrado).

## D06 — Reprodução em ambiente limpo

- **Decision**: clonar o **commit de entrega** registrado (T016) em diretório temporário; se o
  autor não autorizar commits locais, copiar a árvore de trabalho (excluindo `venv/`, `.env`,
  `results/` e `screenshots/`) e registrar a origem usada. Então criar venv novo com o mesmo Python, `pip install -r requirements.txt`,
  `pip check`, copiar apenas o `.env` local (nunca versionado) e seguir `Como Executar`
  literalmente: `pull_prompts.py` (v1 com hash igual), `pytest`, `push_prompts.py` (reuso da
  revisão `36a96c05` por conflito/equivalência, código 0), blocos de dataset/gate,
  `evaluate.py` e auditoria. O `push_prompts.py` não cria revisão (conteúdo idêntico), mas
  reaplica descrição/tags no repositório do Hub — escrita remota esperada, conferida pelo HEAD
  inalterado. O experimento gerado é registrado como **reprodução** (`REP-006`), não substitui
  o final, e seu custo (~US$ 0,27) entra no acumulado. Como o link público do dataset passará a
  mostrar também `REP-006`, o README e o registro o identificam (ID, decisão, custo, “não é o
  final”).
- **Segundo executor (SC-004)**: `REP-006` é executada pelo próprio autor e comprova o roteiro,
  mas **não** satisfaz sozinha o SC-004, que exige um segundo executor. O autor é solicitado a
  indicar outra pessoa que siga `Como Executar` a partir do fork público com credenciais
  próprias (`REP-006B`); sem essa execução, o SC-004 fica registrado como **pendente**, conforme
  a própria spec permite (“explicitamente pendentes”), e a conclusão da 006 o declara.
- **Rationale**: FR-007/FR-010/SC-004. A reinterpretação do SC-004 como “o próprio autor em
  clone limpo” não é adotada: mudar o critério exigiria `/speckit-clarify`.
- **Alternatives considered**: reprodução sem avaliação (não cobre o roteiro completo);
  novo `LANGSMITH_PROJECT` (criaria outro dataset e nova condição sem necessidade).

## D07 — Publicação Git do fork

- **Decision**: o avaliador vê a branch padrão `main`. Ao final, pedir autorização explícita
  ao autor para: (1) `git push origin dev`; (2) atualizar `main` com `dev` (merge
  fast-forward local + push, ou PR `dev → main` no fork, à escolha do autor). Nenhum push
  antes disso; nenhum force-push. Conferir depois, sem login, que `main` mostra README, v2,
  código e `docs/evidencias/`.
- **Rationale**: FR-008 e instrução do autor (“push Git só com autorização explícita”).
  `main` local ainda é a base `a94ce44`; `dev` contém tudo.
- **Alternatives considered**: deixar a entrega só em `dev` (avaliador abre `main` por padrão).

## D08 — Testes offline da entrega

- **Decision**: criar `tests/test_delivery.py`, sem rede, verificando: três seções
  obrigatórias no README e enunciado preservado (títulos originais presentes); toda imagem
  referenciada existe, é PNG, está fora de pastas ignoradas (`git check-ignore`); números de
  `Resultados Finais` iguais ao registro final de `docs/avaliacao-v2.md`; um único link
  público de dataset registrado e repetido de forma idêntica; ausência de padrões de chave.
- **Rationale**: SC-003/SC-005 verificáveis a cada alteração; segue o padrão dos testes
  documentais da 005.
- **Alternatives considered**: só revisão manual (não reproduzível).

## D09 — Integridade final

- **Decision**: repetir os hashes dos quatro protegidos e da v1 contra o manifesto, conferir
  15/5/7/3, `utils.py` intacto e `langchain-google-genai` instalado (Gemini preservado),
  `git diff main..dev -- src/evaluate.py src/metrics.py src/utils.py datasets/` vazio,
  varredura de segredos (valores do `.env` e padrões) em todos os arquivos versionados e nas
  PNG (inspeção visual), `pytest -q` e `git diff --check`.
- **Rationale**: FR-009/SC-005.

Nenhum `NEEDS CLARIFICATION` remanescente. Pontos que só a execução confirma (visibilidade de
traces no link público, D02) têm alternativa definida. Decisões do autor previstas: autorizar
D01, eventual `share_run` (D02) e o push/atualização de `main` (D07).
