# Data Model: Entrega pública com evidências acessíveis e reprodução

**Feature**: [spec.md](spec.md) | **Contrato**: [contracts/entrega-publica.md](contracts/entrega-publica.md)

Entidades são registros documentais em `docs/entrega-publica.md` (versionado), arquivos em
`docs/evidencias/` e objetos remotos já existentes (LangSmith, GitHub). Não há banco ou
formato novo de prompt. A entrada vem da [entrega da 005](../../docs/avaliacao-v2.md#entrega-à-006).

## ResultadoAprovado (entrada, somente leitura)

| Campo | Valor herdado da 005 |
| --- | --- |
| `cycle_id` | `CIC-03` |
| `experiment_id`, `experiment_name` | `d864cfbb-6ab9-4901-ab06-62f68ccd96fc`, `fabiocsm-bug_to_user_story_v2-9c836e20` |
| `hub_commit` | `36a96c0540682ed6b8569487222b88e11d1889a3976b75fea83553dc662b696f` |
| `local_file_sha256`, `local_definition_sha256` | `692df6ae…8974`, `f94735be…7ca2` |
| `means`, `overall` | 0.8773 / 0.8754 / 0.8474 / 0.8513 / 0.9033; 0.8709 |
| `dataset_id` | `8c78638d-37a5-4175-9984-8db0e3473228` |
| `traces` | #1 simple `01a1525d-899e-…`, #10 medium `01a1525d-3ff5-…`, #14 complex `01a1525d-0432-…` |
| `limitations` | Notas individuais < 0.8; meta inventada em #14 (CPU 80%); opções de código numa dúvida em #8 |

Invariante: a v2 local, o HEAD do Hub e `hub_commit` coincidem no início da 006. Qualquer
edição da v2 invalida a entrada e reabre a 005 (FR-010).

## EvidênciaPública

| Campo | Regra |
| --- | --- |
| `id` | `EV-01`… |
| `tipo` | `link_dataset` · `link_experimento` · `link_prompt` · `link_trace` · `screenshot` · `fork` |
| `alvo` | O que comprova: dataset 15, experimento final, cinco médias, trace simples/médio/complexo, prompt, código |
| `endereco` | URL pública ou caminho em `docs/evidencias/` (nunca `screenshots/`/`results/`) |
| `relacao` | `experiment_id`, `hub_commit` e/ou `example_id` correspondentes; para traces, também o run do avaliador (`source_run_id`) |
| `conferencia_anonima` | Data, navegador sem login, resultado (`visível` · `parcial` · `exige_login`) |
| `sigilo` | Inspeção: nenhuma chave, e-mail, cabeçalho ou configuração privada visível |

Regras: `link_dataset` existe uma única vez (FR-004); `parcial` ou `exige_login` exige
`screenshot` complementar ligado ao mesmo alvo (FR-003); o alvo “experimento final” tem
`link_experimento` público alcançado pelo link do dataset (FR-006); URLs de workspace
(`smith.langchain.com/o/…`) nunca são `endereco` de evidência pública (constituição V).

## CompartilhamentoDataset

| Campo | Regra |
| --- | --- |
| `estado_antes` | `não_compartilhado` confirmado por leitura imediatamente antes |
| `autorizacao` | Mensagem do autor no chat, data |
| `executado_em`, `url` | Uma única chamada `share_dataset`; URL `https://smith.langchain.com/public/<token>/d` |
| `estado_depois` | Leitura confirmando o mesmo token |

Transição única: `não_compartilhado → compartilhado`. Nenhuma volta, nenhuma repetição.

## RegistroReprodução

| Campo | Regra |
| --- | --- |
| `id` | `REP-006` (autor, clone limpo) e `REP-006B` (segundo executor, a partir do fork) |
| `executor` | `autor` ou `segundo_executor` (sem dados pessoais além do papel); só `segundo_executor` satisfaz o SC-004 |
| `origem` | Commit de entrega clonado **ou** cópia da árvore de trabalho (se commits não autorizados), diretório temporário; venv novo, Python e pins |
| `configuracao` | Variáveis presentes (nomes, sem valores), `COND-001` |
| `passos` | Cada comando de `Como Executar` com código de saída e observação |
| `experimento` | ID/URL do novo experimento, decisão da auditoria; marcado como reprodução, não final, e identificado no README por aparecer no link público do dataset |
| `escritas_remotas` | Esperadas: novo experimento; reaplicação de descrição/tags pelo push sem nova revisão (HEAD inalterado) |
| `custo` | Tokens e US$ do novo experimento; acumulado do projeto |
| `divergencias` | Diferenças em relação ao documentado, resolvidas ou pendentes |

## ConferênciaIntegridade

| Campo | Regra |
| --- | --- |
| `protected_hashes` | Quatro protegidos iguais ao [manifesto](../../docs/integridade-inicial.json) |
| `v1_hash`, `dataset` | v1 igual à 002; 15 exemplos 5/7/3 |
| `providers` | `utils.py` intacto; `langchain-openai` e `langchain-google-genai` instalados |
| `secret_scan` | Arquivos versionados e PNG sem segredos |
| `v2_match` | v2 local = `hub_commit` aprovado |
| `tests` | `pytest -q` aprovado |

## PacoteEntrega

| Campo | Regra |
| --- | --- |
| `fork_url` | `https://github.com/fabiocsm/mba-ia-pull-evaluation-prompt`, público |
| `delivery_commit` | Commit de `dev` publicado; `main` atualizada para ele com autorização |
| `readme_sections` | `Técnicas Aplicadas (Fase 2)`, `Resultados Finais`, `Como Executar` completas |
| `evidencias` | Lista de `EvidênciaPública` com conferência anônima |
| `estado` | `preparado` → `autorizado` → `publicado` → `conferido` |

`conferido` exige: fork, README, v2 e todas as evidências abertos sem login após o push.
