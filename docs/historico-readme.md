# Histórico literal do README

Snapshot de 2026-10-19, commit `a3062e468a9d906e2be1bded7634f241e7514365`, antes da consolidação da 006.
O bloco preserva literalmente as três seções; seus caminhos são relativos à raiz
do repositório original. Consulte os registros atuais de [preparação](preparacao.md),
[recuperação](recuperacao-v1.md), [publicação](publicacao-v2.md),
[avaliação](avaliacao-v2.md) e [entrega](entrega-publica.md).

````markdown
## Como Executar

### Preparação — spec 001

Consulte o [registro de prontidão](docs/preparacao.md),
o [manifesto de integridade](docs/integridade-inicial.json) e o
[inventário de dependências instalado](docs/dependencias-preparacao.txt).
A [matriz atual por pré-requisito e operação](docs/preparacao.md#matriz-atual)
registra V01–V16, datas e evidências: os pré-requisitos da 001 passaram; a prova
de escrita pública V15 está comprovada no [registro da 004](docs/publicacao-v2.md). A recuperação da 002 foi concluída;
seu [registro de execução](docs/recuperacao-v1.md) comprova o acesso à origem.
A otimização e os testes da 003 foram concluídos localmente; a publicação/conferência da 004 foi concluída; as operações das
specs 005–006 continuam pendentes.
A instalação, a integridade e a autenticação LangSmith passaram. A API key local
confirmou o workspace com handle `fabiocsm`; os dois papéis de modelo responderam
com temperatura zero e seus traces foram conferidos. Não há resultados de avaliação
acadêmica obtidos nesta etapa. O pull tem comprovação própria na 002;
publicação e conferência estão comprovadas na 004; experimentos e evidências
finais pertencem às specs 005–006 e dependem de seus pré-requisitos.

Pré-requisitos: Git, Python 3.10+ (validado com CPython 3.11.14), LangSmith CLI,
acesso ao workspace/handle `fabiocsm` e chaves locais LangSmith/OpenAI. Execute da raiz.
Selecione um Python compatível; neste ambiente, `uv python find 3.11` localiza o
interpretador já instalado. Crie e ative o ambiente antes de instalar:

```bash
python3 -m venv venv  # Use o Python 3.11 selecionado, quando disponível.
source venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python -c 'import langsmith, langchain_core, langchain_openai, langchain_google_genai, dotenv, yaml, pydantic, pytest; print("imports OK")'
```

No PowerShell, use `venv\Scripts\Activate.ps1`. Não copie o template sobre o `.env`
existente. Preserve as credenciais; configure-as somente nesse arquivo local ignorado,
sem incluí-las no Git ou no terminal. Valores não secretos escolhidos:

```dotenv
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=mba-ia-pull-evaluation-prompt
LANGSMITH_WORKSPACE_ID=15dd5852-a835-4163-826c-e78668fd2a9c
USERNAME_LANGSMITH_HUB=fabiocsm
LANGSMITH_TRACING=true
LLM_PROVIDER=openai
LLM_MODEL=gpt-4.1-2025-04-14
EVAL_MODEL=gpt-4.1-2025-04-14
```

Os modelos foram selecionados após consulta à documentação oficial e devem ser
comprovados em chamadas reais com `temperature=0`. Ambos os papéis passaram nessa
verificação mínima; isso não mede a qualidade das User Stories ou dos juízes.
O [modelo](https://developers.openai.com/api/docs/models/gpt-4.1) tem
[desligamento anunciado para 2027-01-14](https://developers.openai.com/api/docs/deprecations):
reconsulte as fontes antes de repetir. Uma troca exige nova condição experimental.
O suporte a `LLM_PROVIDER=google` permanece disponível; exige seleção documentada de
modelos e `GOOGLE_API_KEY` quando usado.

Confira a presença sem revelar valores. Variáveis exportadas têm precedência sobre `.env`:

```bash
python - <<'PY'
import os
from dotenv import load_dotenv
from langsmith.utils import get_env_var, tracing_is_enabled
load_dotenv('.env', override=False)
get_env_var.cache_clear()  # Reavaliar o ambiente depois de carregar dotenv.
required = ('LANGSMITH_API_KEY', 'LANGSMITH_PROJECT', 'USERNAME_LANGSMITH_HUB',
            'LANGSMITH_TRACING', 'LLM_PROVIDER', 'LLM_MODEL', 'EVAL_MODEL', 'OPENAI_API_KEY')
missing = [name for name in required if not os.getenv(name, '').strip()]
print('Variáveis ausentes:', missing)
assert not missing, 'Resolver configuração antes das chamadas'
assert os.getenv('USERNAME_LANGSMITH_HUB') == 'fabiocsm'
assert os.getenv('LLM_PROVIDER') == 'openai'
assert os.getenv('LANGSMITH_TRACING', '').lower() == 'true'
assert tracing_is_enabled() is True, 'Tracing efetivo desabilitado'
assert os.getenv('LLM_MODEL') == os.getenv('EVAL_MODEL') == 'gpt-4.1-2025-04-14'
PY
```

O gate também verifica o tracing efetivo do SDK: aliases `LANGSMITH_TRACING_V2`
ou `LANGCHAIN_TRACING_V2` podem prevalecer sobre `LANGSMITH_TRACING`. Resolva
qualquer configuração conflitante antes das consultas ou chamadas mínimas.

Copie e execute o [roteiro de contexto e traces](docs/preparacao.md#roteiro-executavel).
Ele consulta a ajuda do CLI, carrega dotenv sem sobrescrever variáveis exportadas,
seleciona o workspace, confere o handle autenticado e consulta o projeto pelo SDK.
Por padrão, valida os quatro run IDs existentes com **zero novas chamadas LLM**,
conferindo tenant/projeto, modelo, temperatura, término, uso e metadados da condição.
As saídas são filtradas; erros de acesso não são tratados como projeto ausente.

O ID de workspace acima é o desta entrega. Se a variável não for definida, o roteiro
só seleciona automaticamente quando há um único workspace acessível. Em outro
contexto, escolha explicitamente o workspace que possui o handle esperado.

Para uma nova reprodução integral, siga os checks locais do
[guia de validação](specs/001-preparar-experimentos/quickstart.md), em outro venv limpo,
e execute o mesmo bloco documentado com `PREPARACAO_NOVAS_CHAMADAS=1` no processo.
Essa opção executa a dupla mínima real pelos utilitários, com captura de run IDs,
modelos e uso, espera de tracing e até quatro consultas para confirmar os traces.
Ela consome API; registre novas tentativas, tokens e custo no relatório. Projeto
confirmadamente ausente pode surgir após as chamadas; autenticação inválida bloqueia
o avanço. O modo de leitura dos quatro traces não substitui essa nova reprodução.

Estados do registro: `pronto` exige evidência; `impedido` exige causa e próxima ação;
`pendente` identifica prova ainda não realizada. Leitura de recurso público não
comprova posse do handle nem permissão de push. Para reproduzir em outro ambiente,
outro executor deve seguir o guia com um venv limpo separado, sem apagar `venv/`,
repetir os gates e contabilizar as duas novas chamadas. A reprodução automatizada foi concluída em um venv separado na mesma máquina;
seus resultados, a ocorrência na conferência de traces e os limites dessa prova
estão no registro. Quatro chamadas mínimas consumiram 100 tokens, com custo
estimado de US$ 0,000248; cobrança observada não disponível.

### Recuperação do prompt original — spec 002

Com o ambiente virtual ativo e a configuração acima conferida, execute da raiz:

```bash
source venv/bin/activate
pytest tests/test_pull_prompts.py -v
python src/pull_prompts.py
```

O script usa `Client.pull_prompt` na origem obrigatória
`leonanluppi/bug_to_user_story_v1`, com `dangerously_pull_public_prompt=True`,
`include_model=False` e `skip_cache=True`. A configuração exportada prevalece
sobre `.env`, inclusive valores vazios; configure as variáveis sem espaços em branco.
O pull confere configuração de provedor e modelos, sem executar inferência.

O código de saída **0** confirma a persistência e imprime origem, revisão e destino
`prompts/bug_to_user_story_v1.yml`. O código **1** informa categoria, etapa e ação
para falhas de configuração, acesso, disponibilidade, representação ou escrita.
Falhas anteriores à substituição atômica conservam a cópia anterior byte a byte;
sem cópia anterior, não criam uma referência parcial no destino. Eventual resíduo
temporário é diagnosticado separadamente e deve ser removido antes de repetir.

O [registro da recuperação](docs/recuperacao-v1.md) guarda revisão, SHA-256,
versões, comandos, cenários de falha e a comparação real de 2/2 mensagens idênticas.
O [guia V12](specs/002-recuperar-prompt-v1/quickstart.md#recuperação-real-e-comparação--v12)
permite repetir a comparação fixando a revisão salva, sem recuperar outra latest.
Metadados do repositório são um snapshot observado separadamente; datas/tags do
arquivo ilustrativo foram substituídas apenas pelos valores efetivamente retornados.

A 002 passou em 236 testes offline e na comparação real da revisão recuperada.
Os seis testes obrigatórios da v2 em `tests/test_prompts.py` foram implementados
na 003, com resultados locais abaixo. A publicação foi comprovada posteriormente
na 004; notas e experimentos acadêmicos continuam pendentes.

### Otimização e validação offline — spec 003

Use o venv preparado acima, Python 3.10+ e os pins de `requirements.txt`. Para
validar a [v2 local](prompts/bug_to_user_story_v2.yml), execute da raiz:

```bash
source venv/bin/activate
python -m pip check
pytest tests/test_prompts.py --collect-only -q
pytest tests/test_prompts.py -v -rA
pytest tests/test_preparation_checks.py tests/test_pull_prompts.py -q
```

Em 2026-10-18: coleta de **188 testes**, **188 aprovados** na suíte v2, incluindo
os seis métodos obrigatórios de `TestPrompts`, e **266 aprovados** nas regressões
de preparação/pull. A execução conjunta `pytest tests -q` confirmou **454 aprovados**.
Nenhum skip/xfail. Os seis carregam o YAML real e compartilham
suas asserções com defeitos em cópias isoladas; YAML ausente/inválido, persona só
nos exemplos, pares incompletos, técnicas duplicadas e variáveis extras reprovam.
A suíte bloqueia rede e criação de cliente/modelos, isola o ambiente e desabilita
dotenv; os testes não precisam das chaves locais. O YAML é comparado byte a byte
antes/depois. A política delimitada de pendências aceita `TODOS`, `todos` e `todo`
em prosa e rejeita marcadores reais, sem mudar `src/utils.py` nem ocultar seus
outros erros. Detalhes e comandos incrementais estão no
[registro da 003](specs/003-otimizar-validar-v2/tasks.md#registro-de-execução).

Saída zero comprova o contrato estrutural e a sensibilidade dos testes. A revisão
semântica está abaixo; comportamento de LLM e notas reais continuam por verificar.
A publicação e a conferência posteriores na 004 estão documentadas a seguir.
A 005 executará `python src/evaluate.py` com a revisão publicada após seu preflight. Cada alteração futura exige testar, publicar novamente e
avaliar. As 3–5 iterações e a exigência de cada métrica e média >= 0.8 permanecem.


### Publicação e conferência — spec 004

Após os testes da v2, execute da raiz no venv ativo:

```bash
python -m pytest tests/test_prompts.py -v
python src/push_prompts.py
```

O script lê `USERNAME_LANGSMITH_HUB` e confirma o handle/workspace autenticado
antes de escrever. Reutiliza dotenv sem sobrescrever variáveis exportadas e exige
as variáveis de prontidão acima, provider/chave correspondente e tracing efetivo.
Publica somente System/Human, sem modelo, com descrição intacta, união das tags e
nomes das técnicas; metadata do template contém versão, técnicas e hash canônico.

Status 1 significa validação rejeitada, publicação não confirmada ou conferência
pendente/divergente, com etapa segura. Timeout pode ocorrer após escrita; investigar
por leitura antes de tentar publicar outra vez. Status 0 exige revisão completa
resolvida do retorno, round-trip idêntico, repo público, HEAD correspondente,
leitura HTTP sem autenticação e bytes locais estáveis. A inspeção visual posterior
e seu registro continuam obrigatórios para aceitar a 004. Acompanhe as tentativas
e provas em [publicação da v2](docs/publicacao-v2.md).

Qualquer edição local, inclusive só metadados ou formatação, exige testes → push →
conferência antes do próximo experimento. Commits equivalentes podem ser
reutilizados; registros anteriores conservam valor histórico. A 005 deve conferir
hashes/HEAD/metadados antes e depois e manter a revisão estável durante a execução:
o avaliador fornecido usa HEAD e não implementa esse gate automaticamente.
A publicação real e a inspeção pública passaram: revisão `4278de75a2fca03a17cc1e3ab9d66d552c2c1aaebe543a085a34772637fa9595`,
CLI final com status 0 e 437 testes de prompt/publicação + 266 regressões aprovados.
[Abra a revisão pública](https://smith.langchain.com/hub/fabiocsm/bug_to_user_story_v2/4278de75?tab=0).
O serviço pode acrescentar a tag técnica `ChatPromptTemplate` e devolver conflito
no reenvio idêntico. Nesse conflito, o script confere uma revisão existente por
leitura, com todos os gates, registra `returned_url: null` e não alega nova escrita.
Outras falhas continuam retornando 1; não há repetição automática de push.

### Avaliação e iterações — spec 005

O [registro da avaliação](docs/avaliacao-v2.md) contém três blocos principais, o
bootstrap opcional `AVALIACAO_PROJETO` para inicializar um projeto isolado antes do
dataset, e o histórico dos ciclos. Em **todo** ciclo, da raiz com o venv ativo e nesta ordem: bloco
`AVALIACAO_DATASET` (cria o dataset uma vez pela função fornecida e audita os 15 exemplos),
bloco `AVALIACAO_GATE` (integridade, revisão publicada, condição, workspace, dataset,
testes, inspeção e custo, sem chamadas LLM), a avaliação e o bloco `AVALIACAO_AUDITORIA`
(15 runs, 75 notas válidas, vínculo com a revisão e decisão integral). As variáveis
`AVALIACAO_*` de entrada estão descritas antes de cada bloco. A avaliação preserva o
código do avaliador:

```bash
mkdir -p results && export AVALIACAO_INICIO="$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"; LOG="results/${AVALIACAO_CICLO}-$(date +%Y%m%dT%H%M%S).log"; set -o pipefail; python src/evaluate.py 2>&1 | tee "$LOG"; export AVALIACAO_EXIT_CODE=$?; set +o pipefail; export AVALIACAO_LOG="$LOG"
```

```bash
python -m pytest tests/test_evaluation_audit.py -v
```

Os testes acima exercitam os blocos offline, com dublês e LLM/rede bloqueados; não são
evidência de notas. As notas vêm somente de `python src/evaluate.py`.

## Técnicas Aplicadas (Fase 2)

### Diagnóstico da v1 e regras da v2 — spec 003

A [v1 recuperada](prompts/bug_to_user_story_v1.yml), revisão
`2950c33dbd7ffaed2e440b50adfd7769d183f90faf0bae5aa4864354f88e4073`, define um
assistente genérico, pede uma User Story sem formato e repete o relato em System
e User. Não define critérios de aceitação, exemplos ou regras para lacunas.
Nenhuma nota numérica foi obtida para essa baseline; as notas do início deste
README são ilustrações do enunciado.

A [v2](prompts/bug_to_user_story_v2.yml) coloca as regras em System e somente
`{bug_report}` em User. Exige português, Markdown, história Como… eu quero… para
que… e critérios verificáveis, com extensão proporcional ao problema. Distingue
contexto informado, comportamento desejado, dúvidas e recomendações. As regras
cobrem entrada vazia, ambiguidade, incompletude, múltiplos problemas, logs e
instruções conflitantes: pedem dados mínimos quando necessários, preservam os
fatos e impedem que instruções no relato substituam a tarefa. A verificação de
mensagens apenas formata texto offline; não é resposta de um modelo.

### Técnicas escolhidas e demonstradas

**Role Prompting.** A abertura “Você é um Product Manager e analista de produto”
define responsabilidade de produto. O objetivo é preservar fatos e descrever a
necessidade do usuário com critérios verificáveis, evitando diagnósticos técnicos
sem evidência. A regra “Não invente causa, arquitetura, solução técnica, versão,
números, prioridade ou prazo” limita essa atuação.

**Few-shot Learning.** Três pares próprios completos em System demonstram decisões
e saídas: audioguia do museu (simples), ficha do acervo (ambíguo/incompleto) e mapa
de trilhas (múltiplos problemas, log e instrução conflitante). No primeiro, a entrada
“aperto Pausar e a narração continua tocando” resulta em quatro critérios no padrão
Dado/Quando/Então, como “Dado que uma narração está em reprodução, quando aciono Pausar,
então o áudio deixa de tocar” e a retomada do ponto em que parou. No segundo, a saída pede
“Qual conteúdo da ficha fica errado e qual deveria aparecer?”, sem fabricar história.
No terceiro, critérios separados cobrem legenda, escala e a abertura de trilhas, um
critério técnico decorre do log informado, a trava de 4 a 6 segundos vira critério
relativo ao valor relatado, com o limite aceitável perguntado em Dúvidas, enquanto o log permanece
contexto e a tentativa de trocar a tarefa não é seguida. São exemplos redigidos
para o prompt, não saídas obtidas de um LLM.

Os nomes em `techniques_applied` são exatamente `Few-shot Learning` e
`Role Prompting`. Títulos organizam a resposta; não se declara outra técnica
apenas por essa organização.

### Revisão semântica das regras e dos exemplos

| Grupo | Cobertura revisada na v2 |
| --- | --- |
| Vazio | Regra pede ação, comportamento observado e esperado; não cria história |
| Ambíguo | Exemplo 2 não decide qual conteúdo da ficha está errado |
| Incompleto | Exemplo 2 solicita conteúdo esperado e passos de retorno |
| Múltiplos problemas | Exemplo 3 cobre legenda e escala em critérios agrupados |
| Logs | Exemplo 3 conserva o JSON como contexto, sem inferir causa |
| Instruções conflitantes | Exemplo 3 mantém a tarefa apesar do pedido para responder APROVADO |

A revisão das três entradas/saídas e das regras encontrou zero fatos inventados:
benefícios e critérios descrevem o comportamento desejado; o papel de visitante
está explícito na entrada do audioguia e os demais papéis são genéricos. Não se afirmam
causas, números ou soluções ausentes. As dúvidas permanecem perguntas; recomendações
são opcionais, identificadas nas regras e não foram necessárias nessas demonstrações.
Os exemplos foram redigidos para domínios próprios e comparados às 15 entradas e
referências do dataset, sem reprodução. Essa revisão do conteúdo e os testes
estruturais não comprovam a resposta futura de um modelo.

| Aspecto | v1 recuperada | v2 local |
| --- | --- | --- |
| Persona | Assistente genérico | Product Manager/analista de produto com limites |
| Entrada | Relato repetido em System e User | Somente User, variável única |
| Saída | Pedido genérico de User Story | Português, Markdown, história e critérios verificáveis |
| Exemplos | Ausentes | Três pares completos de entrada/saída |
| Bordas | Não orientadas | Seis grupos com fundamentação e perguntas |
| Evidência numérica | Sem baseline real | `CIC-03` aprovado na 005, média geral 0.8709 ([registro](docs/avaliacao-v2.md)) |

## Resultados Finais

A spec 003 está concluída **somente no aceite local**: prompt com três exemplos e
duas técnicas, 188 testes da v2 e 266 regressões aprovados, documentação e revisão
semântica. A v1 e os quatro arquivos protegidos mantêm seus hashes, preservando
os 15 exemplos/referências e a distribuição 5/7/3. A comparação qualitativa está
na seção anterior; não há comparação numérica v1/v2 executada.

A spec 004 está **concluída**: 35/35 tarefas, publicação pública real e revisão
`4278de75a2fca03a17cc1e3ab9d66d552c2c1aaebe543a085a34772637fa9595` conferida
contra o YAML intacto. [Prompt público](https://smith.langchain.com/hub/fabiocsm/bug_to_user_story_v2/4278de75?tab=0),
[histórico e três capturas reais](docs/publicacao-v2.md). O script final retornou 0;
437 testes de prompt/publicação e 266 regressões passaram. As tentativas com
falhas e os ajustes de compatibilidade estão preservados no registro.

A spec 005 executou três ciclos reais sob a mesma condição. `CIC-01` avaliou essa revisão
(aprovada com F1-Score 0.8057). Por decisão do autor, `CIC-02` passou a exigir critérios
Dado/Quando/Então que cobrem os resultados decorrentes do comportamento esperado e critérios
técnicos para detalhes informados (F1-Score 0.8416), e `CIC-03` acrescentou a regra de
valores — nenhuma meta, código ou exemplo numérico ausente do relato — publicada como revisão
`36a96c0540682ed6b8569487222b88e11d1889a3976b75fea83553dc662b696f`. O experimento final é
completo (15 respostas, 75 notas válidas), vinculado à revisão e **aprovado** pela regra
integral — Helpfulness 0.8773, Correctness 0.8754, F1-Score 0.8474, Clarity 0.8513,
Precision 0.9033, média geral 0.8709 — com custo estimado acumulado de US$ 0,76. Detalhes,
análise, traces e limitações no [registro da avaliação](docs/avaliacao-v2.md). Link público do
dataset/experimentos, screenshots das cinco notas e tracing detalhado de três
exemplos: **pendentes na 006**. O link público acima comprova o prompt; o dataset e o
experimento ainda estão apenas no workspace do autor, sem acesso público. As ilustrações do enunciado não representam resultados desta entrega.
````
