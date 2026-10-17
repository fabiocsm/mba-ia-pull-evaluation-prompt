# Modelo dos registros de preparação

Modelo documental, sem classes de domínio ou banco de dados. Os arquivos abaixo
serão criados na implementação. Datas usam ISO 8601 com fuso; caminhos de artefatos
são relativos ao repositório. Credenciais nunca são campos destes registros.

## Registro de preparação — `docs/preparacao.md`

| Campo/seção | Conteúdo e validação |
| --- | --- |
| Identificação | ID da execução de preparação, data, commit Git e links para spec/manifesto |
| Ambiente | SO, arquitetura, Python, pip, localização relativa de venv, versão CLI, hash de requirements e link para inventário de versões |
| Configuração | Provider, nomes dos dois modelos, tracing, projeto, endpoint e workspace sem componentes secretos |
| Credenciais | Somente nome, presença e resultado de validade; nunca valor, prefixo, hash ou comprimento |
| Verificações | Lista de pré-requisitos conforme entidade abaixo |
| Condição experimental | Identificador e campos conforme entidade abaixo |
| Custo | Preços/fontes/data, hipóteses, chamadas previstas, tokens observados disponíveis, custo estimado e cobrança observada quando acessível |
| Conclusão | Prontidão por operação, impedimentos, próxima ação e evidência de revalidação |

Acrescentar histórico datado ao corrigir falhas; não apagar o diagnóstico anterior.
Registrar `não disponível` quando não houver acesso à cobrança, nunca presumir zero.
O registro público pode referenciar evidências autenticadas, mas deve incluir fatos
sanitizados suficientes à auditoria sem depender apenas de URL privada.

## Verificação de pré-requisito

| Campo | Regra |
| --- | --- |
| `id` | Único na execução, ligado a FR/SC e operação dependente |
| `requisito` | Descrição do que será comprovado |
| `estado` | `pendente`, `pronto` ou `impedido` |
| `verificado_em` | Data da tentativa, ausente somente se ainda não tentada |
| `evidencia` | Comando/método, resultado resumido e referência versionada ou URL sanitizada |
| `causa` / `proxima_acao` | Obrigatórias em falha; pendência deve indicar o que falta verificar |
| `operacoes_afetadas` | Pull, preparação da v2, push, avaliação ou entrega pública |

Transições: `pendente → pronto` somente com evidência; `pendente → impedido` ao
constatar falha; `impedido → pronto` somente após correção e nova verificação.
Mudança de credencial, workspace, dependências ou modelos invalida as verificações
afetadas, que retornam a `pendente`. Evidências anteriores permanecem no histórico.

Uma operação está `pronto` quando todas as suas dependências estão prontas;
`impedido` se alguma está impedida; caso contrário, `pendente`. Estado global não
substitui a matriz por operação. Permissão de publicação ainda não exercida fica
explicitamente a comprovar no push da 004, sem transformar leitura em prova de escrita.

A verificação de contexto autenticado e a de existência do projeto são distintas.
T009 pode concluir com contexto comprovado e apenas a existência do projeto
`pendente`, quando a consulta confirmar sua ausência. Essa pendência não é um
pré-requisito das duas chamadas mínimas; T013 deve comprovar projeto e traces depois
delas. Não converter falhas de autenticação/acesso em ausência de projeto nem marcar
a prontidão global antes dessa comprovação.

## Condição experimental

- `id`, data de definição e motivo da eventual substituição.
- `provider`: `openai` inicialmente; `google` é a alternativa existente.
- `llm_model` e `eval_model`: valores explícitos, preferencialmente snapshots.
- `temperature`: exatamente `0`, para ambos os papéis.
- Fontes oficiais, data da consulta e eventual data de desligamento anunciada.
- Workspace/projeto esperados e constatados; nome futuro do dataset
  `{LANGSMITH_PROJECT}-eval`.
- Evidência por papel: data, modelo solicitado/retornado quando disponível, sucesso,
  tokens reportados, trace e diagnóstico de falha sanitizado.
- Hash do inventário de dependências e vínculo ao manifesto de integridade.

A condição pertence a uma preparação e será referenciada pelos experimentos da 005.
Trocar modelo/provedor cria nova condição; não comparar revisões como se fossem
executadas sob a mesma configuração. Esta entidade não contém métricas da v2.

## Referência de integridade — `docs/integridade-inicial.json`

| Campo | Regra |
| --- | --- |
| `schema_version` | `1` para este desenho |
| `created_at` | Momento de coleta |
| `git_commit` / `git_branch` | Commit completo e branch real |
| `git_status` | Estado sanitizado inicial; explicitar divergências dos protegidos |
| `upstream` | URL pública do repositório base, revisão completa usada e resultado da comparação |
| `repository` | URL pública da entrega, visibilidade, indicador de fork, parent e data da consulta |
| `files` | Exatamente os quatro caminhos protegidos, cada um com SHA-256 dos bytes e correspondência com origem |
| `dataset` | SHA-256 bruto, contagem 15, distribuição original e lista dos casos |

Cada caso guarda linha física (base 1), `complexity` (`simple`, `medium`, `complex`),
SHA-256 canônico do registro e hashes canônicos separados de `inputs` e `outputs`.
Canonicalização: JSON UTF-8, `ensure_ascii=False`, `sort_keys=True`,
`separators=(',', ':')`, sem quebra final. Isso permite comparar casos/remoto por
conteúdo mesmo que IDs e ordem remota difiram. Nenhuma entrada/referência é alterada.

O hash bruto detecta alterações de bytes; os hashes canônicos localizam diferenças
de conteúdo. Exigir `inputs.bug_report` e `outputs.reference` como strings não vazias,
15 registros e distribuição `simple=5`, `medium=7`, `complex=3`. Na 005 comparar
multiconjuntos de pares inputs/outputs, preservando multiplicidade. Metadados remotos
não são exigidos pelo avaliador fornecido.

Baseline divergente da origem não recebe aprovação. Guardar a divergência e resolver
o conflito antes da execução dependente; não sobrescrever a referência inicial para
ocultar alteração. A revisão final compara com o mesmo manifesto, inclusive após commits.

## Inventário de dependências — `docs/dependencias-preparacao.txt`

Versões efetivamente instaladas após sucesso de `pip check`, em linhas `pacote==versão`.
Registrar Python e pip no relatório. Revisar a saída antes de versionar: não incluir
URLs privadas, credenciais, caminhos pessoais ou configuração de índices autenticados.

Relacionamentos: preparação referencia uma baseline de integridade, um inventário
de ambiente e uma ou mais condições experimentais históricas; cada verificação
pertence à preparação e aponta para a condição quando depender de modelos.
