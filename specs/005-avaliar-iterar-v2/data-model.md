# Data Model: Avaliação íntegra e otimização guiada por evidências

**Feature**: [spec.md](spec.md) | **Contrato**: [contracts/avaliacao-v2.md](contracts/avaliacao-v2.md)

Entidades são registros documentais em `docs/avaliacao-v2.md` (versionado) e
objetos remotos já existentes no LangSmith. Não há banco, manifesto paralelo
obrigatório ou novo formato de prompt. Saídas brutas em `results/` são cópias locais
ignoradas pelo Git e nunca a única evidência.

## CondiçãoExperimental

| Campo | Regra |
| --- | --- |
| `id` | `COND-001` herdada da [preparação](../../docs/preparacao.md#condição-experimental); nova condição recebe `COND-00N` |
| `provider`, `llm_model`, `eval_model` | `openai`, `gpt-4.1-2025-04-14` nos dois papéis; temperatura `0` (fixada pelo código fornecido) |
| `langsmith_project`, `dataset_name` | `mba-ia-pull-evaluation-prompt` e `{project}-eval` |
| `workspace_id`, `endpoint` | Iguais ao preflight da 004 |
| `protected_hashes` | SHA-256 dos quatro protegidos iguais ao [manifesto](../../docs/integridade-inicial.json) |
| `rates_usd_per_million` | Objeto com `geracao` e `juizes`, cada um com `entrada`/`saida` em US$/milhão; valores numéricos finitos ≥ 0, sem booleanos; obrigatório no gate e auditoria antes de acesso remoto |
| `sdk_versions` | `langsmith`, `langchain-core` instalados |

Mudança de qualquer campo, exceto revisão do prompt, cria nova condição registrada
**antes** da execução. Resultados de condições diferentes não são comparados diretamente.
A condição ativa é informada ao gate por `AVALIACAO_CONDICAO` (padrão `COND-001`); uma
`COND-00N` só é aceita se já estiver declarada, com todos os campos acima, na seção de
condições de `docs/avaliacao-v2.md`.

## RevisãoCandidata

| Campo | Regra |
| --- | --- |
| `cycle_id` | Ciclo que a produziu |
| `git_commit` | Commit local que contém o YAML avaliado; árvore da v2 sem alterações pendentes |
| `local_file_sha256`, `local_definition_sha256` | Calculados como na 004 |
| `hub_commit` | Hash completo conferido pelo push (C07 da 004) |
| `published_at`, `push_record` | Data e saída do `push_prompts.py` com código 0 |
| `dashboard_check` | Data e resultado da inspeção sem login (badge Public, identidade, revisão, tags/técnicas, System/User); obrigatória (constituição III) |
| `tests` | Resultado de `pytest tests/test_prompts.py -v` e da regressão para estes hashes |

Invariante: `hub_commit` só é aceito se o push conferiu equivalência com os mesmos
hashes locais. Reuso de commit equivalente (`existing_after_conflict`) é válido.

## AuditoriaDataset

| Campo | Regra |
| --- | --- |
| `dataset_id`, `example_count` | Remoto; contagem exatamente 15 |
| `matches_local` | Multiconjunto canônico igual ao JSONL (D02) |
| `distribution` | 5 simple / 7 medium / 3 complex, via mapeamento local |
| `example_map` | `example_id → (índice local, complexidade)`, usado na análise |
| `status` | `idêntico` · `divergente` · `ausente` |

`divergente` bloqueia a condição; resolução por isolamento (D03), nunca por edição.
A auditoria é refeita antes do gate em todo ciclo; `dataset_id` e `status` seguem para o
gate e para a auditoria do experimento por `AVALIACAO_DATASET_ID` e `AVALIACAO_DATASET`.
A auditoria do experimento reconstrói `example_map` relendo o dataset por esse ID.

## Experimento

| Campo | Regra |
| --- | --- |
| `experiment_id`, `experiment_name`, `url` | Extraídos de `selectedSessions` e conferidos no LangSmith |
| `condition_id`, `hub_commit`, `dataset_id` | Ligações obrigatórias |
| `started_at`, `finished_at`, `exit_code` | Do comando real `python src/evaluate.py`; `exit_code` é o do avaliador (`pipefail`), não o do `tee` |
| `printed_status` | Linha `STATUS: APROVADO`/`STATUS: REPROVADO` do log |
| `block_cause` | Para `bloqueado`: `integridade`, `revisao`, `configuracao`, `condicao`, `testes`, `dashboard`, `dataset` ou `custo` |
| `head_before`, `head_after`, `hashes_before`, `hashes_after` | Gate de estabilidade |
| `runs` | Lista de `ResultadoExemplo` |
| `summary` | `ResumoAgregado` |
| `tokens`, `estimated_cost_usd` | Soma dos runs LLM da geração e das árvores dos runs do avaliador (juízes); valores sem contagem marcados como `estimado` |
| `status` | Ver transições |

### Transições

```text
planejado → gate_ok → executado → auditado ─┬─ aprovado
            │            │                  ├─ reprovado
            └─ bloqueado └─ falha_execução  ├─ incompleto
                                            └─ invalidado
aprovado → substituído   (nova edição da v2 após a aprovação)
```

- `bloqueado`: gate C01/C02 falhou, inclusive gate de custo (`block_cause=custo`); nenhuma chamada LLM.
- `falha_execução`: processo encerrou sem URL de experimento; projeto parcial, se houver, é listado só para registro.
- `incompleto`: menos de 15 runs válidos ou 75 notas válidas (C05).
- `invalidado`: revisão, YAML ou dataset mudou durante a execução (C04).
- `reprovado`: completo e estável, mas alguma média ou a média geral `< 0.8`.
- `aprovado`: completo, estável, cinco médias e média geral `>= 0.8`.
- Estados finais nunca são apagados; uma repetição gera novo `Experimento`.

## ResultadoExemplo

| Campo | Regra |
| --- | --- |
| `example_id`, `local_index`, `complexity` | Pelo `example_map` |
| `root_run_id`, `error` | Run raiz sem erro |
| `answer_chars` | `outputs.answer` string não vazia |
| `prompt_commit` | `metadata.lc_hub_commit_hash` do run do template (D04) |
| `feedback` | Exatamente um `Feedback` por chave das cinco |

## Feedback

| Campo | Regra |
| --- | --- |
| `key` | `helpfulness`, `correctness`, `f1_score`, `clarity`, `precision` |
| `score` | Numérico, finito, em `[0,1]` |
| `comment` | Sem marcadores de falha (D06); raciocínio do juiz nas três métricas base |
| `source_run_id` | Run do avaliador, quando exposto, para a inspeção de traces |
| `valid` | Todas as regras acima e consistência das derivadas |

## ResumoAgregado

| Campo | Regra |
| --- | --- |
| `means` | Média por chave sobre as 15 notas válidas, arredondada a 4 casas como em `evaluate.py` |
| `overall` | Média simples das cinco médias |
| `printed_means` | Valores impressos pelo avaliador; devem coincidir com `means` |
| `by_complexity` | Médias por dificuldade (somente análise) |
| `lowest` | Menores notas por métrica, com exemplo e comentário |
| `decision` | Regra integral FR-004; nota individual baixa não reprova sozinha |

## EvidênciaTrace

| Campo | Regra |
| --- | --- |
| `experiment_id`, `example_id`, `complexity` | Um por dificuldade, no mínimo |
| `root_run_id`, `prompt_run_id`, `llm_run_id`, `judge_run_ids` | IDs inspecionáveis |
| `observação` | Entrada, instruções, resposta, julgamentos e feedback relacionados |
| `screenshot` | Opcional na 005; obrigatório e público na 006 |

## CicloOtimização

| Campo | Regra |
| --- | --- |
| `id` | `CIC-01` a `CIC-05`; continuidade após cinco recebe `CIC-06+` com plano registrado |
| `problem`, `hypothesis` | Ligados a notas/comentários do ciclo anterior; `CIC-01` usa a v2 da 003 como referência inicial |
| `change` | Diff resumido da v2 (e testes/documentação acompanhantes) |
| `git_commit` | Commit local do ciclo (autorizado em 2026-10-18; sem push Git) |
| `validation` | Resultado do pytest, push e gate |
| `revision`, `experiment` | `RevisãoCandidata` e `Experimento` |
| `conclusion` | Decisão e próximo passo |

### Transições

```text
aberto → hipótese → editado → testado → publicado → avaliado → concluído
                       └──── falha de teste/push: volta a editado, sem experimento
```

Uma edição após `aprovado` abre novo ciclo e marca o experimento anterior como
`substituído` para fins de entrega (FR-010).

## RegistroCusto

| Campo | Regra |
| --- | --- |
| `experiment_id`, `input_tokens`, `output_tokens` | Lidos dos runs de geração e dos juízes; estimativa marcada como tal se indisponível |
| `rates_usd_per_million` | Tarifas oficiais da condição ativa, por papel (`geracao`, `juizes`) e direção (`entrada`, `saida`); COND-001 preserva 2/8 nos dois papéis |
| `estimated_usd`, `cumulative_usd` | Soma de `tokens[role][direction] × rates_usd_per_million[role][direction] / 1_000_000`, e acumulado dos experimentos; novas condições exigem consulta oficial e declaração prévia das tarifas |
| `gate` | Acumulado > US$ 4 sem aprovação: `Experimento` seguinte `bloqueado` com `block_cause=custo` até decisão do autor |
