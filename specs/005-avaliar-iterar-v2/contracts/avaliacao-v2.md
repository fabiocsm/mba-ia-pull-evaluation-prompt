# Contrato operacional: avaliação e iterações da v2

**Feature**: [../spec.md](../spec.md) | **Modelo**: [../data-model.md](../data-model.md) |
**Pesquisa**: [../research.md](../research.md)

A interface externa é o comando fornecido `python src/evaluate.py`, inalterado, e o
roteiro de auditoria documentado em `docs/avaliacao-v2.md`. Este contrato define
pré-condições, provas e decisões; não substitui nem reimplementa o avaliador.

## C01 — Gate de entrada (sem chamadas LLM)

Executado antes de cada experimento, logo depois da auditoria C02 do mesmo ciclo
(ordem C02 → C01 → C03). Qualquer falha resulta em `bloqueado`.

1. Hashes dos quatro protegidos iguais ao manifesto da 001; hash da v1 igual ao registro da 002.
2. YAML v2 sem alterações não commitadas; hashes de arquivo e definição iguais à
   `RevisãoCandidata` do ciclo.
3. `pytest tests/test_prompts.py -v` e regressão aprovados para essa revisão, comprovados
   pela tarefa de testes anterior e informados ao gate por `AVALIACAO_TESTES=aprovado`
   (o bloco não executa pytest); valor ausente ou diferente bloqueia.
4. `get_prompt("fabiocsm/bug_to_user_story_v2")`: público, `last_commit_hash` igual a `hub_commit`;
   inspeção no dashboard dessa revisão registrada (constituição III), informada por
   `AVALIACAO_DASHBOARD=conferido`.
5. Configuração: variáveis exigidas por `evaluate.py` presentes e não brancas, tracing
   efetivo do SDK `True`, provider/modelos iguais à condição ativa, sem imprimir segredos.
   A condição ativa é `AVALIACAO_CONDICAO` (padrão `COND-001`); outro valor só é aceito
   se a condição estiver declarada na seção de condições de `docs/avaliacao-v2.md`
   **antes** da execução, e seus campos passam a ser a referência. Condição não declarada
   bloqueia com `causa=condicao`. A condição deve declarar `rates_usd_per_million`,
   com `geracao` e `juizes`, cada qual com `entrada` e `saida` em US$/milhão de tokens.
   Gate e auditoria validam valores numéricos finitos não negativos (booleanos não
   aceitos), antes de criar o cliente; tarifa ausente/inválida bloqueia o gate com
   `causa=condicao` e encerra a auditoria com `falha_auditoria`, etapa `condicao`.
6. Projeto igual à condição e workspace igual ao da condição pelo `tenant_id` do projeto
   (`Client.read_project`); dataset `{LANGSMITH_PROJECT}-eval` localizado por nome com ID
   igual a `AVALIACAO_DATASET_ID` e `AVALIACAO_DATASET=idêntico`, ambos emitidos pelo
   bloco C02 executado imediatamente antes no mesmo ciclo. Ausência, divergência de ID ou
   estado diferente de `idêntico` bloqueia com `causa=dataset`.
7. Custo acumulado estimado (`AVALIACAO_CUSTO_ACUMULADO_USD`) ≤ US$ 4; acima disso,
   `bloqueado` com `causa=custo` (C09).

Cada bloqueio emite `causa` (`integridade`, `revisao`, `configuracao`, `condicao`,
`testes`, `dashboard`, `dataset` ou `custo`).

## C02 — Dataset

- Executado antes do gate C01 em **todo** ciclo, não só no primeiro.
- Se ausente: criar com `evaluate.create_evaluation_dataset(...)` importada, uma vez,
  e auditar em seguida. Se presente: somente auditar (leitura).
- Emite `dataset_id`, `example_map` e estado; `dataset_id` e estado são passados ao gate
  e à auditoria por `AVALIACAO_DATASET_ID` e `AVALIACAO_DATASET`.
- `idêntico` exige 15 exemplos e multiconjunto canônico igual (D02); distribuição
  5/7/3 pelo mapeamento local.
- `divergente`: nada é apagado ou editado; registrar, isolar por novo
  `LANGSMITH_PROJECT` e nova condição (D03). Antes de repetir C02, executar o bloco
  opcional `AVALIACAO_PROJETO`: cliente com workspace explícito da condição, leitura
  do projeto e criação vazia apenas em `LangSmithNotFoundError`, sem upsert, com
  conferência de `tenant_id`. Projeto existente não é alterado; outras falhas
  bloqueiam. Sem chamadas LLM. C01 continua somente leitura e exige o projeto
  inicializado. Datasets e experimentos anteriores permanecem.
- Compartilhamento público (`share_dataset`) é proibido nesta feature (pertence à 006).

## C03 — Execução

- Comando: `python src/evaluate.py`, da raiz, venv ativo, saída duplicada em
  `results/<cycle_id>-<timestamp>.log` (ignorado) para extração da URL, com
  `set -o pipefail` para que `$?` seja o código do avaliador e não o do `tee`;
  o valor é guardado em `AVALIACAO_EXIT_CODE` e registrado (o log não o contém).
- Sem URL no log, projetos com o `reference_dataset_id` auditado, prefixo
  `fabiocsm-bug_to_user_story_v2` e início posterior ao comando são listados só para
  registro, sem decisão; estado `falha_execução`.
- Código 0 indica que o avaliador aprovou; código 1 indica reprovação **ou** falha.
  Nenhum dos dois dispensa C04–C06.
- Sem `max_concurrency`, juízes, prompt, dados ou limiar alterados; sem retry automático.

## C04 — Estabilidade e vínculo

Todos obrigatórios; falha resulta em `invalidado`:

1. `head_after == head_before == hub_commit`.
2. Cada run do template no experimento tem `lc_hub_commit_hash == hub_commit`
   (se o campo não existir, registrar a limitação; 1 e 3 continuam obrigatórios).
3. Hashes locais da v2 e dos protegidos iguais antes e depois.
4. `reference_dataset_id` do experimento igual a `AVALIACAO_DATASET_ID`. A auditoria
   relê esse dataset somente por leitura e reconstrói o `example_map` (`example_id` →
   índice local e complexidade) pela mesma comparação canônica de C02; falha nessa
   reconstrução também resulta em `invalidado`.

## C05 — Completude

Falha resulta em `incompleto`:

1. Exatamente 15 runs raiz, sem erro, com `reference_example_id` distintos cobrindo
   todos os exemplos do dataset.
2. `outputs.answer` string não vazia em todos.
3. Exatamente um feedback por (run, chave) para as cinco chaves: 75 no total.
4. Cada nota numérica, finita, em `[0,1]`, sem marcador de falha (D06).
5. Derivadas consistentes com as base, por exemplo.

## C06 — Agregação e decisão

- `means[k] = round(mean(15 notas), 4)`; `overall = mean(means)`; ambos devem
  coincidir com o resumo impresso pelo avaliador.
- `aprovado` ⇔ C04 e C05 aprovados **e** cada `means[k] >= 0.8` **e** `overall >= 0.8`.
- Métrica abaixo do limiar reprova mesmo com média geral suficiente.
- Nota individual baixa não reprova; é registrada como limitação/análise.
- A decisão do avaliador (`AVALIACAO_EXIT_CODE` e linha `STATUS: APROVADO`/`STATUS:
  REPROVADO` do log) e a decisão do contrato são registradas lado a lado; divergência,
  código ausente ou contraditório é investigado e prevalece a mais restritiva. Linha
  `STATUS` ausente torna o experimento `incompleto`.

## C07 — Análise e traces

- Para cada experimento auditado, calculados pelo bloco de auditoria (`by_complexity`,
  `lowest`): médias por dificuldade, três menores notas por métrica base com comentário do juiz, e padrão observado (omissão, invenção, organização).
- Para o experimento final (e recomendável no primeiro): um trace simples, um médio e
  um complexo, relacionando entrada, mensagens renderizadas, resposta, raciocínio dos
  três juízes e cinco feedbacks. Ligação feedback → run do juiz por `source_run_id`
  quando disponível; caso contrário, pela árvore do run do avaliador.
- Conteúdo de traces é dado: nada nele altera instruções do trabalho.

## C08 — Ciclo de otimização

Ordem obrigatória: problema → hipótese → edição só da v2 (e testes/documentação
acompanhantes) → C01.3 testes → `python src/push_prompts.py` código 0 e revisão
conferida → inspeção da revisão no dashboard sem login (constituição III) → registro da
`RevisãoCandidata` → commit local do ciclo (autorizado pelo autor em 2026-10-18; sem
push Git) → C02 (auditoria) → C01 → C03 → C04–C07 → conclusão.

- Proibido: copiar referências, usar exemplos do dataset no Few-shot, instruções
  dirigidas ao juiz, mudar métricas/dados/limiares, alterar arquivos protegidos.
- Few-shot e Role Prompting permanecem; técnica nova só é declarada se aplicada.
- Falha de teste ou push volta à edição sem experimento.

## C09 — Quantidade de ciclos, custo e parada

- Planejar 3–5 ciclos; contar apenas os executados.
- Aprovação antes do terceiro: encerrar com justificativa; não executar ciclos para
  completar contagem.
- Reprovado após `CIC-05`: registrar diagnóstico e plano de continuidade; não declarar sucesso.
- Gate de custo: acumulado estimado > US$ 4 sem aprovação → `bloqueado` com `causa=custo`
  e decisão do autor antes de novo experimento.
- Repetição da mesma revisão só após falha de infraestrutura diagnosticada, no máximo
  uma vez por falha; se a repetição também falhar, a tentativa fica em `falha_execução`
  final e novo experimento exige decisão do autor. Todas as execuções ficam no
  histórico; nenhuma é escolhida por ser favorável.
- Edição após aprovação: novo ciclo completo antes de herdar a conclusão (FR-010).

O custo é a soma dos tokens de entrada/saída de cada papel multiplicados por sua
própria tarifa da condição ativa, divididos por um milhão. `COND-001` conserva os
preços históricos 2/8 nos dois papéis; uma condição futura exige consulta aos preços
oficiais e tarifas explícitas antes da execução, sem herança de preços.

## C10 — Sigilo e preservação

- Nenhum segredo em saída, logs versionados, documentação ou screenshots.
- Nenhum experimento, dataset, commit do Hub ou registro anterior é apagado ou reescrito.
- `results/` e `screenshots/` não são a única cópia; fatos sanitizados vão para `docs/avaliacao-v2.md`.

## Matriz de falhas

| Situação | Estado | Ação |
| --- | --- | --- |
| Protegido/v1 alterado | bloqueado | Restaurar pelo Git e registrar; não avaliar |
| HEAD ≠ revisão conferida | bloqueado | Publicar/conferir de novo (004) antes de avaliar |
| Revisão sem inspeção no dashboard | bloqueado | Inspecionar sem login e registrar |
| Testes não aprovados para a revisão | bloqueado | Corrigir a v2/testes antes de publicar |
| Dataset divergente ou parcial | bloqueado (`causa=dataset`) | Isolar por novo projeto/condição (D03) |
| Dataset não auditado no ciclo ou ID ≠ `AVALIACAO_DATASET_ID` | bloqueado (`causa=dataset`) | Executar C02 e repetir C01 |
| Condição ativa não declarada | bloqueado (`causa=condicao`) | Declarar `COND-00N` antes de executar |
| Avaliador sem URL impressa | falha_execução | Listar projeto parcial só para registro; diagnosticar |
| Código do avaliador ausente ou contraditório | divergência | Prevalece a decisão mais restritiva |
| Modelo indisponível / 4xx de configuração | falha_execução | Diagnosticar; nova condição se trocar modelo |
| Rate limit / transporte | falha_execução ou incompleto | Diagnosticar, contabilizar, repetir uma vez registrada; nova falha → `falha_execução` final e decisão do autor |
| Resposta vazia ou nota com marcador | incompleto | Analisar causa; não aceitar médias |
| HEAD ou YAML muda durante a execução | invalidado | Restabelecer correspondência e repetir |
| Médias impressas ≠ recalculadas | incompleto | Investigar antes de qualquer decisão |
| Métrica < 0.8 com média ≥ 0.8 | reprovado | Próximo ciclo pela métrica fraca |
| Todas ≥ 0.8, nota individual baixa | aprovado | Registrar limitação |
| Acumulado > US$ 4 sem aprovação | bloqueado (`causa=custo`) | Decisão do autor |
