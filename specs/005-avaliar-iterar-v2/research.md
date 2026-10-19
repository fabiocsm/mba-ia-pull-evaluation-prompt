# Research: Avaliação íntegra e otimização guiada por evidências

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md) | **Data**: 2026-10-18

Pesquisa feita **somente por leitura**: código protegido, SDK instalado
(`langsmith==0.13.0`, `langchain-core==1.6.4`) e consultas autenticadas sem escrita.
Nenhuma chamada LLM, criação de dataset, publicação ou experimento foi executada.

## Estado remoto observado em 2026-10-18

| Item | Observação (somente leitura) | Consequência |
| --- | --- | --- |
| Dataset `mba-ia-pull-evaluation-prompt-eval` | Inexistente (0 datasets com o nome) | Não há colisão hoje; será criado pela função fornecida |
| `fabiocsm/bug_to_user_story_v2` | HEAD `4278de75…9595`, público, 1 commit | Igual ao [registro da 004](../../docs/publicacao-v2.md) |
| Experimentos `*bug_to_user_story_v2*` | Nenhum | O primeiro ciclo será o primeiro experimento |

O estado pode mudar até a execução; a auditoria C02 e o gate C01 do
[contrato](contracts/avaliacao-v2.md), nessa ordem e em todo ciclo, o reconferem.

## D01 — Criar e auditar o dataset antes do primeiro experimento

- **Decision**: antes do primeiro `python src/evaluate.py`, chamar a própria
  `evaluate.create_evaluation_dataset(client, dataset_name, jsonl_path)` por import,
  sem alterar o módulo; auditar o resultado e só então executar o avaliador, que
  reutiliza o dataset existente pelo nome. Nos ciclos seguintes, a auditoria (sem
  criação) é repetida antes do gate de cada experimento.
- **Rationale**: FR-001 exige conferência **antes** da avaliação. Em `main()` a criação
  e o experimento ocorrem no mesmo processo; além disso a função captura exceções e
  retorna o nome mesmo após criação parcial, e execuções seguintes reutilizam o nome
  sem conferir conteúdo. Chamar a função fornecida preserva exatamente seu formato
  (só `inputs`/`outputs`, sem `metadata`).
- **Alternatives considered**: auditar só depois do primeiro experimento (descumpre
  FR-001 e pode gastar uma avaliação em dataset parcial); criar com código próprio
  (formato poderia divergir do avaliador); compartilhar o dataset agora (pertence à 006).

## D02 — Igualdade do dataset por multiconjunto canônico

- **Decision**: comparar o multiconjunto de pares canônicos
  `json.dumps({"inputs":…, "outputs":…}, sort_keys=True, ensure_ascii=False)` remotos
  com os 15 locais, com multiplicidade; exigir 15 exemplos remotos e nenhum extra. A
  distribuição 5/7/3 é derivada pelo mapeamento local par → `metadata.complexity`.
- **Rationale**: o avaliador não envia `metadata`; ordem e IDs remotos não são estáveis.
  A [preparação](../../docs/preparacao.md) já registrou hashes canônicos por registro
  e definiu essa regra para a 005.
- **Alternatives considered**: exigir `metadata` remoto (o avaliador não o envia);
  comparar só contagem (não detecta referência alterada).

## D03 — Divergência ou colisão: isolamento por novo projeto

- **Decision**: se o dataset remoto divergir, não apagar nem editar. Definir localmente
  um novo `LANGSMITH_PROJECT` (ex.: `mba-ia-pull-evaluation-prompt-c2`), registrar
  nova condição `COND-00N` em `docs/avaliacao-v2.md` antes de executar, informá-la ao
  gate por `AVALIACAO_CONDICAO`, executar o bootstrap opcional `AVALIACAO_PROJETO`
  antes de C02 e repetir D01/D02 no novo nome. O bootstrap usa
  `Client(workspace_id=condition['workspace_id'])`, lê o projeto e cria um projeto
  vazio somente em `LangSmithNotFoundError`, com `upsert=False`; confirma `tenant_id`.
  Projeto existente nunca é alterado; outras falhas bloqueiam, sem chamadas LLM.
- **Rationale**: FR-001/FR-008 e a constituição exigem preservar dados e experimentos;
  o nome do dataset deriva de `LANGSMITH_PROJECT` no avaliador. Criar o dataset não
  cria o projeto de tracing exigido por C01; inicializá-lo antes evita bloquear a
  recuperação. O gate permanece somente leitura.
- **Alternatives considered**: excluir/recriar o dataset (destrói histórico);
  alterar `evaluate.py` para outro nome (arquivo protegido).

## D04 — Vínculo entre experimento e revisão do Hub

- **Decision**: três provas cumulativas: (1) `get_prompt(...).last_commit_hash` igual
  à revisão conferida **antes** e **depois** da execução; (2) cada run do
  `ChatPromptTemplate` no experimento contém `metadata.lc_hub_commit_hash` igual a ela;
  (3) hashes do YAML local iguais aos da publicação conferida, antes e depois.
- **Rationale**: `evaluate.py` puxa `latest` e grava em metadata apenas o nome do
  prompt. O SDK instalado (`langsmith/client.py`, `_process_prompt_manifest`) acrescenta
  `lc_hub_owner`, `lc_hub_repo` e `lc_hub_commit_hash` à metadata do template, que o
  `langchain-core` propaga ao run. A prova (2) é por exemplo e não depende de horário.
- **Alternatives considered**: comparar só o HEAD antes (não detecta troca durante a
  execução); fixar commit no pull (exigiria alterar o avaliador).
- **Confirmação pendente**: a presença do campo nos runs reais será conferida no
  primeiro experimento. Se ausente, (1)+(3) sustentam o vínculo e o limite é registrado.

## D05 — Identificar o experimento pela URL impressa

- **Decision**: capturar a saída do avaliador em arquivo local ignorado
  (`results/`), extrair `selectedSessions=<uuid>` da URL e auditar por esse ID de
  projeto; conferir `reference_dataset_id` igual ao dataset auditado e prefixo
  `fabiocsm-bug_to_user_story_v2`.
- **Rationale**: o SDK monta a URL com `datasets/{dataset_id}/compare?selectedSessions={experiment.id}`.
  Seleção por "mais recente" é frágil quando houver repetição.
- **Alternatives considered**: procurar por nome/horário (ambíguo); alterar o avaliador
  para imprimir o ID (protegido).

## D06 — Nota válida exige ausência de marcador de falha

- **Decision**: uma nota só é válida se for numérica, finita, em `[0,1]`, única por
  (run, chave), e o comentário **não** contiver os marcadores do código protegido:
  `Erro na avaliação`, `Erro ao processar resposta` ou `Resposta vazia`. Conferir também
  `helpfulness = round((clarity+precision)/2, 4)` e
  `correctness = round((f1_score+precision)/2, 4)` por exemplo.
- **Rationale**: `metrics.py` converte exceções e JSON inválido em `score: 0.0`;
  `evaluate.py` converte resposta vazia em cinco zeros. Esses zeros são numéricos e
  entrariam na média como se fossem julgamentos reais. A agregação também ignora
  `None`, aceitando médias sobre menos de 15 notas.
- **Alternatives considered**: aceitar qualquer número em `[0,1]` (esconde falha de
  juiz); exigir nota > 0 (rejeitaria zero legítimo).

## D07 — Auditoria como roteiro executável documentado

- **Decision**: implementar a auditoria como blocos `python - <<'PY'` em
  `docs/avaliacao-v2.md` (gate de entrada, dataset, auditoria do experimento),
  somente leitura exceto a criação explícita de D01 e o bootstrap opcional de D03;
  cobrir os blocos com testes
  offline em `tests/test_evaluation_audit.py`, seguindo o padrão de
  `tests/test_preparation_checks.py`.
- **Rationale**: segue o precedente da [preparação](../../docs/preparacao.md#roteiro-executavel)
  e não cria serviço, framework ou novo entregável de produção. O avaliador continua
  sendo a única fonte das notas.
- **Alternatives considered**: script em `src/` (amplia o escopo de produção);
  inspeção apenas visual (não comprova 75 notas de forma reproduzível); reimplementar
  métricas (proibido e redundante).

## D08 — Condição experimental e custo

- **Decision**: manter `COND-001` (provider `openai`, geração e juiz
  `gpt-4.1-2025-04-14`, temperatura `0`) em todos os ciclos. Revalidar a disponibilidade
  do modelo no gate; desligamento anunciado em 2027-01-14 exige nova condição se ocorrer.
- **Estimativa** (preços oficiais registrados na preparação: US$ 2/M entrada, US$ 8/M
  saída; ~3,5 caracteres/token em português): por experimento, ~27 mil tokens de entrada
  e ~8 mil de saída na geração (System v2 ~1,6 mil tokens × 15 + relatos), ~68 mil de
  entrada e ~7 mil de saída nos 45 julgamentos. Total ~95 mil entrada / ~15 mil saída,
  **≈ US$ 0,31**, margem até US$ 0,50. Cinco ciclos ≈ US$ 1,6–2,5, dentro de US$ 1–5.
- **Rationale**: comparação válida exige condição constante; consumo real será lido dos
  tokens dos runs, não da estimativa.
- **Gate de custo**: se o acumulado estimado ultrapassar US$ 4 antes da aprovação, parar
  e pedir decisão do autor antes de novos experimentos.
- **Alternatives considered**: juiz mais capaz (nova condição sem ganho comprovado);
  modelos mais baratos (mudaria a condição e exigiria nova comprovação).

## D09 — Ciclos, oscilação e candidata final

- **Decision**: cada ciclo é uma revisão publicada distinta avaliada uma vez. Repetição
  com a mesma revisão só após falha de transporte/infraestrutura diagnosticada, e todas
  as execuções permanecem registradas. A candidata final é a **última revisão editada**
  avaliada e aprovada, nunca a melhor de várias repetições.
- **Rationale**: FR-008/FR-010 e o edge case de oscilação proíbem selecionar só
  execuções favoráveis; temperatura zero não garante determinismo.
- **Alternatives considered**: média de repetições (não é a agregação fornecida);
  descartar runs ruins (manipulação).

## D10 — Estratégia de ajuste da v2 por métrica

- **Decision**: mapear sintomas a hipóteses, conforme o plano mestre: F1 baixo →
  omissões de fatos/critérios esperados; Precision baixa → conteúdo inventado ou
  excessivo; Clarity baixa → organização/ambiguidade. Helpfulness e Correctness são
  derivadas e não recebem ajuste próprio. Ajustes ficam na v2 (instruções, regras,
  exemplos próprios), mantendo Few-shot e Role Prompting; Skeleton of Thought só entra
  em `techniques_applied` se aplicada de fato.
- **Rationale**: FR-007 exige problema e hipótese explícitos; a constituição proíbe
  copiar referências, inserir instruções dirigidas ao juiz e exemplos tirados do dataset.
- **Alternatives considered**: few-shot com casos do dataset (vazamento); instruções
  sobre o avaliador (manipulação proibida).

## D11 — Testes ao editar a v2

- **Decision**: a cada edição, rodar `pytest tests/test_prompts.py -v` e a regressão.
  Se um teste local de contrato depender de detalhe que a hipótese do ciclo muda,
  atualizá-lo no mesmo ciclo com justificativa; os seis testes obrigatórios nunca são
  enfraquecidos. Depois, `python src/push_prompts.py` com código 0 e revisão conferida.
- **Rationale**: aprovação estrutural e experimental são cumulativas (constituição V).

Nenhum `NEEDS CLARIFICATION` remanescente. Pontos a confirmar com dados reais (D04,
tokens de D08 e ligação feedback → run do juiz em C07) têm alternativa definida.
