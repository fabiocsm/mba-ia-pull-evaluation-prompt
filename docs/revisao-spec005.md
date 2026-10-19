# Revisão dos commits da spec 005 — 2026-10-19

Solicitação: `review-loop --base main --max-iterations 1 --commit`, com foco nos
commits da spec 005. Branch `dev`, árvore inicial limpa. Base `main` em
`a94ce443299b4928d0f1e08cecdacf7a36ff5fb1`; HEAD inicial
`dc0a87e3f9cf388818e1c75cec3f754fc6287ab2`. Snapshot inicial T0/S1:
`40c2805b4e0ceccb7c81e506e6ac4d9922cd6c10`.

## Iteração 1/1 — escopo e triagem

Três revisores cobriram `5441148..a56eaa6` (os sete commits da 005: `60ca942`,
`0380149`, `1f7aafd`, `c40f511`, `e536787`, `9386438`, `a56eaa6`): 12 arquivos,
3.572 inserções e 31 exclusões. Lentes primárias A/K/M, B/C/D/I/J e E/F/G/H/L.
Os commits anteriores e a 006 foram usados como contexto. Os gates finais cobrem
a árvore inteira contra `main`.

O orquestrador conferiu os caminhos no código, contratos e SDK instalado antes de
aceitar os achados. Duplicatas foram agrupadas por causa. Todas as unidades são
seriais porque compartilham os blocos e testes.

| ID | Severidade / lente | Problema e cenário confirmado | Disposição / correção |
| --- | --- | --- | --- |
| R1-1 | Important / F, A | C02 chama helper protegido que imprime exceções brutas; falha de criação pode expor o conteúdo de headers/credenciais antes do JSON sanitizado. | Aceito → corrigido: descartar stdout/stderr somente durante o helper e auditar o resultado; regressão com sentinelas. |
| R1-2 | Important / L, G | Outro `USERNAME_LANGSMITH_HUB` passava no gate; o prompt errado poderia consumir chamadas antes da rejeição pelo prefixo do experimento. | Aceito → corrigido: validar `fabiocsm` antes do cliente no gate e na auditoria; fake permissivo comprova ausência de consultas. |
| R1-3 | Important / C, L | D03 manda escolher projeto novo, mas C02 só cria dataset e C01 exige projeto existente: a recuperação bloqueava antes da avaliação. | Aceito → corrigido: bootstrap opcional com workspace explícito, criação apenas em NotFound e sem upsert; fake fiel ao SDK. |
| R1-4 | Important / G, A, M | Condição com outro modelo/provedor era aceita, mas o custo usava sempre a tarifa da COND-001; o acumulado poderia subestimar o limite C09. | Aceito → corrigido: tarifas por papel da condição ativa, validação e regressões de custo/limite. |

Rastreabilidade das correções: [T036–T040](../specs/005-avaliar-iterar-v2/tasks.md#revisão-dos-commits--2026-10-19),
[blocos executáveis](avaliacao-v2.md#roteiro-executável),
[testes](../tests/test_evaluation_audit.py) e
[contrato](../specs/005-avaliar-iterar-v2/contracts/avaliacao-v2.md).

## Retornos dos fixers (literais)

### U1 — R1-1

```text
STATUS: fixed

FINDINGS: [R1-1]

FILES CHANGED:
- docs/avaliacao-v2.md — descarta stdout e stderr somente durante a criação pelo helper protegido.
- tests/test_evaluation_audit.py — adiciona regressão de sigilo e ajusta expectativa da saída original.

FIX: A chamada permanece única e a auditoria posterior continua detectando criação parcial. Mensagens brutas do helper não chegam à saída; arquivos protegidos preservados.

TESTS: Regressão observada falhando antes da correção: 1 failed, 85 deselected, com sentinelas na saída. Depois: `venv/bin/python -m pytest tests/test_evaluation_audit.py -k dataset -q` — 14 passed, 72 deselected. `git diff --check` aprovado.

DEVIATIONS: none
```

### U2 — R1-2

```text
STATUS: fixed
FINDINGS: [R1-2]
FILES CHANGED:
- docs/avaliacao-v2.md — valida handle exato no gate e na auditoria antes de criar o cliente.
- tests/test_evaluation_audit.py — oito cenários de handle inválido e verificação explícita do identificador válido; fake permissivo registra consultas sem mascarar o defeito.

FIX: `USERNAME_LANGSMITH_HUB` continua vindo do ambiente, mas deve ser exatamente `fabiocsm`. Outro owner, espaços ou vazio bloqueiam sem cliente, consultas remotas ou escritas. A auditoria aplica a mesma proteção. U1 preservada; arquivos protegidos intactos.

TESTS: Red observado: sete falhas e um caso já aprovado entre os oito novos cenários. Green: `venv/bin/python -m pytest tests/test_evaluation_audit.py -q` — 94 aprovados. `git diff --check` sem erros.

DEVIATIONS: none. A alteração concorrente em tasks.md pertence ao orquestrador; não foi editada nesta unidade. Sem remoto, LLM ou commit.
```

### U3 — R1-3

```text
STATUS: fixed

FINDINGS: [R1-3]

FILES CHANGED:
- docs/avaliacao-v2.md — bootstrap opcional `AVALIACAO_PROJETO` antes de C02 e orientação de recuperação.
- tests/test_evaluation_audit.py — cliente falso fiel, criação explícita e quatro regressões.
- specs/005-avaliar-iterar-v2/research.md — D03/D07 alinhados ao bootstrap.
- specs/005-avaliar-iterar-v2/contracts/avaliacao-v2.md — contrato de inicialização sem alterar projetos existentes.
- specs/005-avaliar-iterar-v2/quickstart.md — sequência reproduzível para nova condição.

FIX: O bootstrap seleciona explicitamente o workspace, cria projeto vazio somente após `LangSmithNotFoundError`, usa `upsert=False` e confirma `tenant_id`. Projetos existentes são apenas lidos; demais falhas bloqueiam. Gate permanece somente leitura. U1/U2 preservadas.

TESTS: Red observado: integração confirmou bloqueio do gate para projeto inexistente e falhou pela ausência do bootstrap. Green: seleção `bootstrap or gate` — 41 passed, 57 deselected; arquivo completo — 98 passed. Cobertos desbloqueio, idempotência, workspace incorreto e falha de transporte sem criação. `git diff --check` aprovado.

DEVIATIONS: none
```

### U4 — R1-4

```text
STATUS: concluído.

FINDINGS: R1-4 corrigido; nenhum impedimento remanescente nesta unidade.

FILES CHANGED:

- `docs/avaliacao-v2.md`
- `tests/test_evaluation_audit.py`
- `specs/005-avaliar-iterar-v2/contracts/avaliacao-v2.md`
- `specs/005-avaliar-iterar-v2/data-model.md`

FIX: tarifas em US$/milhão declaradas por papel e direção na condição ativa. COND-001 mantém 2/8 para geração e juízes. Gate/auditoria rejeitam tarifas ausentes, incompletas, booleanas, não numéricas, negativas ou não finitas antes de criar o cliente. Auditoria calcula por papel e informa as tarifas utilizadas. Contrato/modelo orientam consulta oficial para condições futuras.

TESTS:

- Red inicial: **21 falhas pertinentes**.
- Green inicial direcionado: **21 aprovados**.
- Green final do arquivo: **123 aprovados**, incluindo quatro casos adicionais de limites.
- Condição fictícia offline: custo exato **US$ 5,61**, bloqueando o próximo gate.
- Regressão histórica com tokens estimados: **US$ 0,184402**.
- `git diff --check`: aprovado.

DEVIATIONS: nenhuma material. Preservadas alterações U1/U2/U3, protegidos, prompt e tarefas. Sem chamadas remotas, pesquisa, LLM ou commit.
```

## Revisão do orquestrador e hardening

As quatro unidades preservam os arquivos protegidos e o prompt. Os testes novos
exercitam os blocos documentados e os caminhos reais do helper importado. Os conjuntos
de arquivos correspondem às unidades; o relatório e as tarefas são registros do
orquestrador. Não houve codegen nem alterações de dependências.
Como o delta passou de 400 linhas, houve uma revisão adicional independente do
checkpoint `40c2805..cc7e72b`: nenhum achado adicional com confiança ≥80, nenhuma
correção incompleta e nenhum conflito entre as quatro unidades.

| ID | Tipo | Evidência | Resolução |
| --- | --- | --- | --- |
| H1-1 | missed sibling | README/plan ainda descreviam apenas três blocos e T013 repetia D03 sem inicializar o projeto. | Orquestrador alinhou README, plan e T013 ao bootstrap opcional, preservando a ordem dos três blocos principais. |

## Gates e relatório final

Resultado: **clean no escopo revisado, após uma iteração**. R1-1–R1-4 corrigidos;
H1-1 resolvido. Nenhum achado aceito sem correção e nenhuma decisão normativa
pendente. O limite de uma iteração foi respeitado.

| Verificação | Resultado observado |
| --- | --- |
| Baseline `python -m pytest -q` | 817 aprovados. |
| Suíte completa após correções `python -m pytest -q` | 855 aprovados (38 novos casos); inclui os seis testes obrigatórios. |
| `tests/test_evaluation_audit.py` pelo fixer | 123 aprovados; cenários red/green registrados acima. |
| Análise sem executar os blocos | AST de todos os Python alterados contra `main` e dos quatro blocos documentados válida. |
| Integridade | Quatro protegidos iguais ao manifesto; protegidos, v1 e v2 idênticos a T0; dataset com 15 exemplos e distribuição 5/7/3. |
| Documentação/sigilo | Links locais dos arquivos desta revisão resolvidos; nenhum valor secreto do `.env` nos arquivos alterados. |
| `git diff --check main <snapshot>` | Sem erros na árvore completa, incluindo novos arquivos capturados pelo snapshot. |
| Snapshot pós-gates | Igual ao snapshot utilizado nos gates; identidade final conferida novamente antes do commit. |
| build_runner / Dart format / Flutter analyze | Não aplicáveis: projeto Python, sem codegen nem configuração de formatter/linter Python. Sintaxe e suíte são os gates aplicáveis. |

O commit local autorizado deve conter exatamente a árvore validada, com assunto
`fix(evaluation-audit): address review-loop iteration 1 findings` e os quatro IDs no
corpo. A revisão não autoriza push Git. A identidade da árvore final e do commit é
informada no chat, evitando que registrar o próprio hash altere esta árvore.

## Limites da revisão

As regressões usam dublês offline; não são notas acadêmicas. Não houve novo
experimento, publicação no Hub ou compartilhamento de dataset. As evidências reais
de CIC-01–03 continuam no [registro histórico](avaliacao-v2.md#ciclos). A conferência
pública e as screenshots continuam na spec 006.

O revisor observou risco residual de colapso de múltiplos templates pelo mesmo
`trace_id`, mas não encontrou caminho normal no avaliador fornecido que produza
esse cenário; não foi elevado a achado. Esta revisão não revalidou serviços remotos.
