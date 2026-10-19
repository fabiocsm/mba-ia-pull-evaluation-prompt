# Quickstart: validar a avaliação e as iterações da v2

**Feature**: [spec.md](spec.md) | **Contrato**: [contracts/avaliacao-v2.md](contracts/avaliacao-v2.md)

Guia de validação, não implementação. Os blocos executáveis de gate, dataset e
auditoria serão escritos em `docs/avaliacao-v2.md` na implementação; aqui ficam os
cenários e resultados esperados. Executar da raiz, com o venv da 001.

Ordem de execução de cada ciclo: V04 (dataset) → V03 (gate) → V05 → V06. A numeração
segue o documento; a auditoria do dataset sempre precede o gate.

## Pré-requisitos

- Specs 001–004 aceitas; registro da [publicação](../../docs/publicacao-v2.md) com revisão conferida.
- `.env` com a condição `COND-001`; segredos nunca impressos.
- Ajuda do CLI consultada antes de usar subcomandos (`langsmith --help`).

```bash
source venv/bin/activate
```

## V01 — Integridade e testes locais (offline)

```bash
shasum -a 256 src/evaluate.py src/metrics.py src/utils.py datasets/bug_to_user_story.jsonl prompts/bug_to_user_story_v1.yml
```

```bash
pytest tests/test_prompts.py -v
```

Esperado: hashes iguais ao [manifesto](../../docs/integridade-inicial.json) e ao registro
da 002; seis testes obrigatórios coletados e aprovados, sem skip/xfail.

## V02 — Testes offline da auditoria

```bash
pytest tests/test_evaluation_audit.py -v
```

Esperado: blocos de `docs/avaliacao-v2.md` exercitados com dublês, rede/LLM bloqueados;
casos negativos de C04–C06 (nota ausente, duplicada, fora de faixa, marcador de falha,
derivada inconsistente, 14 runs, HEAD alterado, dataset divergente) reprovam; positivo
com 15×5 notas válidas aprova somente com todas as médias ≥ 0.8.

## V03 — Gate de entrada (somente leitura)

Executar o bloco "gate de entrada" de `docs/avaliacao-v2.md`, depois de V04 no mesmo
ciclo, com as variáveis da revisão do ciclo, `AVALIACAO_CONDICAO` (padrão `COND-001`),
`AVALIACAO_DATASET_ID` e `AVALIACAO_DATASET=idêntico` emitidos por V04,
`AVALIACAO_TESTES=aprovado`, `AVALIACAO_DASHBOARD=conferido` e o custo acumulado.
Esperado: JSON sanitizado com hashes, HEAD, condição, workspace, dataset, tracing e
custo; código 0. Com HEAD diferente, condição não declarada, dataset não auditado ou
de outro ID, testes/inspeção não informados ou custo > US$ 4, código 1, estado
`bloqueado` e `causa` correspondente.

## V04 — Dataset antes de cada experimento

Executar o bloco "dataset" de `docs/avaliacao-v2.md` antes do gate de cada ciclo. Na
primeira vez cria o dataset com a função fornecida; depois apenas audita.
Esperado: `example_count=15`, `matches_local=true`, distribuição 5/7/3, `dataset_id`
registrado e exportado em `AVALIACAO_DATASET_ID`/`AVALIACAO_DATASET`. Em divergência:
código 1, nada apagado, isolamento conforme D03 com nova condição declarada e
`AVALIACAO_CONDICAO` atualizada.

## V05 — Experimento real

```bash
mkdir -p results && LOG="results/CIC-01-$(date +%Y%m%dT%H%M%S).log"; set -o pipefail; python src/evaluate.py 2>&1 | tee "$LOG"; export AVALIACAO_EXIT_CODE=$?; set +o pipefail; echo "AVALIACAO_EXIT_CODE=$AVALIACAO_EXIT_CODE"
```

Esperado: 15 linhas `[i] F1:… Clarity:… Precision:…`, resumo com cinco métricas e
média geral, linha `STATUS`, URL com `selectedSessions=`. `AVALIACAO_EXIT_CODE` é o
código do avaliador (sem `pipefail` seria o do `tee`); 0 ou 1 é registrado e nenhum dos
dois basta para a decisão.

## V06 — Auditoria do experimento

Executar o bloco "auditoria" de `docs/avaliacao-v2.md` com o ID extraído da URL e
`AVALIACAO_DATASET_ID`; o bloco relê o dataset e reconstrói `example_map`.
Esperado: C04 (HEAD antes/depois, `lc_hub_commit_hash` por run, hashes), C05
(15 runs, 75 notas válidas), C06 (médias recalculadas iguais às impressas e decisão),
C07 (`by_complexity`, `lowest`), tokens de geração e juízes e custo estimado. Sem URL
no log: `falha_execução`, projeto parcial listado só para registro.

## V07 — Traces

No experimento final, abrir um exemplo simples, um médio e um complexo; registrar
IDs dos runs raiz, prompt, LLM e juízes, e relacionar entrada, mensagens, resposta,
raciocínios e feedbacks. Esperado: três `EvidênciaTrace` completas.

## V08 — Ciclo de otimização

1. Registrar problema e hipótese com base em V06/V07.
2. Editar somente `prompts/bug_to_user_story_v2.yml` (e testes/documentação acompanhantes).
3. V01, depois `python src/push_prompts.py` com código 0 e revisão conferida.
4. Inspecionar a nova revisão no dashboard sem login e registrar (constituição III).
5. Commit local do ciclo (autorizado pelo autor; sem push Git); V04 → V03 → V05 → V06.

Esperado: novo `CicloOtimização` completo; histórico anterior intacto.

## V09 — Decisão integral

Com o experimento auditado, conferir: aprovado só com C04/C05 aprovados, cinco médias
≥ 0.8 e média geral ≥ 0.8. Métrica < 0.8 com média ≥ 0.8 permanece reprovada.

## V10 — Parada e candidata final

- Aprovação antecipada: justificativa registrada, sem ciclos extras.
- Cinco ciclos reprovados: diagnóstico e plano de continuidade registrados.
- Revisão final: YAML local, HEAD do Hub e `hub_commit` do experimento aprovado iguais
  (SC-005), com inspeção no dashboard registrada; qualquer edição posterior reabre V08.

## V11 — Integridade final

Repetir V01, `git status`, `git diff --check` e busca de segredos nos arquivos alterados.
Esperado: protegidos/v1 íntegros, nenhuma credencial, `results/` não referenciado como
única evidência.
