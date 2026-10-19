# Contrato operacional da preparação

Interface com o executor via configuração, comandos existentes e registros.
Não introduz API web nem novo script de produção. Regras de persistência e estados
estão em [data-model.md](../data-model.md).

## Entradas

Executar da raiz, em Python 3.10+ com `venv` ativo. Carregar `.env` usando dotenv;
variáveis já exportadas têm precedência, como na infraestrutura fornecida.
Selecionar os dois modelos pela documentação oficial antes de preencher e validar
`LLM_MODEL`/`EVAL_MODEL`. Ajustar somente os valores não secretos necessários na
configuração local, preservando as credenciais existentes.

| Variável | Exigência | O que pode aparecer no registro |
| --- | --- | --- |
| `LANGSMITH_API_KEY` | Presente e válida no contexto esperado | Presença/validade, sem valor |
| `LANGSMITH_PROJECT` | Não vazio; projeto dedicado identificado | Nome e ID do projeto confirmado |
| `USERNAME_LANGSMITH_HUB` | `fabiocsm` | Handle e forma de confirmação autenticada |
| `LANGSMITH_TRACING` | Habilitado (`true` na configuração documentada) | Estado e trace comprovado |
| `LLM_PROVIDER` | `openai` inicialmente; alternativa suportada `google` | Valor efetivo |
| `LLM_MODEL` | Explícito, compatível com temperatura zero | Nome solicitado/retornado |
| `EVAL_MODEL` | Explícito, mesmo se igual ao gerador | Nome solicitado/retornado |
| `OPENAI_API_KEY` | Exigida com `openai`; reutilizar chave existente | Presença/validade, sem valor |
| `GOOGLE_API_KEY` | Exigida somente se `google` for escolhido | Presença/validade, sem valor |
| `LANGSMITH_ENDPOINT` | Endpoint efetivo, padrão ou configurado | URL sanitizada sem credenciais |
| `LANGSMITH_WORKSPACE_ID` | Quando necessário para desambiguar workspaces | ID esperado e correspondência constatada |

Não fixar handle nos scripts futuros. A igualdade exigida nesta preparação é uma
regra da configuração deste projeto. Não exigir chave Google na execução OpenAI.
Não copiar `.env.example` sobre o `.env` existente. Não invocar CLI supondo que ele
carregue dotenv: usar subprocesso com ambiente carregado e sem segredos em argumentos.

## Verificações e resultados observáveis

| Operação | Verificação | Resultado de sucesso / limite |
| --- | --- | --- |
| Instalação | Venv ativo; instalar requirements; `pip check`; imports | Status zero, dependências consistentes, dois providers importáveis |
| Integridade | Git, SHA-256 e JSONL | Quatro arquivos iguais à origem identificada; 15 casos e 5/7/3 |
| Fork | Metadados públicos do GitHub | Fork público com parent `devfullcycle/mba-ia-pull-evaluation-prompt` |
| Identidade | CLI/interface autenticada e SDK | Workspace/handle corretos; não apenas leitura de recurso público |
| Projeto | `Client.read_project(project_name=...)` | Nome/ID e workspace correspondentes; escrita não é provada pela leitura |
| SDK | Inspecionar assinaturas instaladas | Pull público, montagem System/User, parâmetros de push e revisão confirmados sem publicar |
| Modelos | Utilitários existentes com `temperature=0` | Duas respostas curtas não vazias, um sucesso por papel, uso registrado quando fornecido |
| Tracing | Inspecionar os traces mínimos | Projeto e workspace esperados, data e identificador da verificação |

Concluir a tarefa de contexto (T009) exige identidade, handle, workspace e endpoint
comprovados e o resultado da consulta ao projeto registrado. Se somente o projeto
estiver comprovadamente ausente, a tarefa pode concluir com a verificação de sua
existência separadamente `pendente`, liberando T010–T012. T013 deve consultar novamente
o projeto e comprovar nome/ID, tenant e os dois traces para resolver essa pendência.
Autenticação inválida, acesso negado ou contexto divergente/ambíguo bloqueiam as
chamadas; não tratar essas falhas como ausência de projeto. Não criar dataset ou
experimento para testar acesso. Erros HTTP são resumidos por
categoria/status; não copiar resposta bruta, headers nem objetos Client.

O SDK será usado nos scripts obrigatórios das specs seguintes. CLI/UI servem para
confirmar contexto; o planejamento não assume interfaces inexistentes. Fontes e
limites das provas estão na [pesquisa](../research.md).

## Saídas

- `docs/preparacao.md`: fatos, datas, condições, estados, evidências e memória de custo.
- `docs/integridade-inicial.json`: baseline conforme modelo, sem segredos.
- `docs/dependencias-preparacao.txt`: inventário sanitizado das versões instaladas.
- `README.md`: instruções acrescentadas e link para os registros, preservando o contrato.

Consultas e comandos devem retornar sucesso real para marcar `pronto`. Falhas de
validação local usam saída não zero ou asserção explícita; falhas remotas geram
`impedido`, causa e ação. Ausência de execução é `pendente`, nunca sucesso presumido.
Os registros não podem declarar publicação, métrica aprovada ou permissão de escrita
com base apenas nas leituras da preparação.

## Dependências por operação futura

| Operação | Pré-requisitos necessários |
| --- | --- |
| Pull — 002 | Ambiente, integridade, autenticação/contexto LangSmith e acesso à origem; modelo não é usado no pull |
| Validação local da v2 — 003 | Ambiente e v1 recuperada; testes estruturais não exigem API do modelo |
| Push — 004 | Ambiente, identidade/handle, v2/testes aprovados; escrita comprovada no push real |
| Avaliação — 005 | Todos os anteriores, dois papéis de modelo, tracing e condição registrada; auditar dataset remoto nessa spec |
| Entrega — 006 | Fork público, baseline e resultados/evidências das specs próprias |

Para concluir a prontidão global da 001, comprovar ambiente, identidade/configuração,
integridade, fork, ambos os modelos e tracing. Se falhar apenas modelo, o relatório
deve mostrar essa limitação e quais operações independentes continuam possíveis.

## Falhas que devem ser distinguíveis

- Chave ausente ou inválida: identificar variável/serviço, sem mostrar valor.
- Workspace incorreto: impedir chamada no contexto ambíguo e indicar seleção necessária.
- Modelo incompatível/inacessível: escolher alternativa documentada e repetir os dois
  papéis afetados; não remover temperatura zero do contrato.
- Instalação incompatível: registrar versão/erro sanitizado e resolver interpretador.
- Arquivo protegido divergente: registrar conflito com origem; não normalizar baseline.
- Limite de API ou timeout: registrar tentativa/consumo disponível; evitar retries cegos.

Não modificar `.env` real para provocar falhas. Cenários negativos usam subprocessos
com ambiente isolado ou cópias temporárias não versionadas. Nenhuma falha autoriza
alterar métricas, dados ou arquivos fornecidos como prontos.
