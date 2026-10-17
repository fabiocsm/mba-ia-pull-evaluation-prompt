# Guia de validação da preparação

Este roteiro será executado na implementação da spec 001. Não representa ambiente,
acessos ou chamadas já validados pelo planejamento. Executar os comandos da raiz.
Contrato de entrada/saída em [contracts/preparacao.md](contracts/preparacao.md);
campos dos registros em [data-model.md](data-model.md).

## 1. Pré-requisitos e referência inicial

Ter Python 3.10+, Git, acesso ao fork e ao LangSmith, chave OpenAI local existente e
documentação oficial de modelos disponível. Não imprimir `.env` nem usar `set -x`.
Antes de instalação ou configuração:

```bash
git rev-parse HEAD
git branch --show-current
git status --short
git diff --exit-code HEAD -- src/evaluate.py src/metrics.py src/utils.py datasets/bug_to_user_story.jsonl
python3 --version
```

Guardar commit, branch e estado inicial. O diff contra HEAD só confere alterações
locais: identificar também uma revisão do repositório base para comparar os quatro
protegidos. Obter essa referência por consulta pública e, se necessário, fetch do Git
sem alterar o checkout; registrar o commit exato usado. Não aprovar uma divergência
pré-existente como se fosse material original.

Consultar no GitHub a identidade do fork, visibilidade e repositório pai. Se `gh`
estiver disponível e autenticado, a consulta de leitura abaixo retorna somente os
campos necessários; a interface pública é alternativa equivalente:

```bash
gh api repos/fabiocsm/mba-ia-pull-evaluation-prompt --jq '{full_name,html_url,visibility,fork,parent:.parent.full_name}'
```

Esperado: público, `fork=true`, parent
`devfullcycle/mba-ia-pull-evaluation-prompt`. Sem confirmação, registrar pendência;
não alterar visibilidade ou recriar repositório neste roteiro.

Conferência local de hashes e estrutura, sem modificar o dataset:

```bash
python3 - <<'PY'
import hashlib, json
from collections import Counter
from pathlib import Path
files = ('src/evaluate.py', 'src/metrics.py', 'src/utils.py',
         'datasets/bug_to_user_story.jsonl')
for name in files:
    print(name, hashlib.sha256(Path(name).read_bytes()).hexdigest())
rows = [json.loads(line) for line in Path(files[-1]).read_text(encoding='utf-8').splitlines() if line.strip()]
assert len(rows) == 15
assert all(isinstance(r['inputs']['bug_report'], str) and r['inputs']['bug_report'].strip()
           and isinstance(r['outputs']['reference'], str) and r['outputs']['reference'].strip() for r in rows)
counts = Counter(r['metadata']['complexity'] for r in rows)
assert counts == {'simple': 5, 'medium': 7, 'complex': 3}
print('dataset:', len(rows), dict(counts))
PY
```

Na implementação, persistir o manifesto completo, incluindo os hashes por caso e a
comparação com a origem, segundo o modelo de dados. O comando acima é uma conferência,
não substitui o registro. Esperado: quatro hashes e distribuição 5/7/3 sem erro.

## 2. Criar o ambiente isolado

Selecionar o interpretador compatível antes de criar `venv`; preferir Python 3.11 se
disponível. Os comandos abaixo usam o `python3` selecionado, sempre 3.10+:

```bash
python3 -m venv venv
source venv/bin/activate
python -c 'import sys; assert sys.version_info >= (3,10); assert sys.prefix != sys.base_prefix; print(sys.version)'
pip install -r requirements.txt
python -m pip check
python -c 'import langsmith, langchain_core, langchain_openai, langchain_google_genai, dotenv, yaml, pydantic, pytest; print("imports OK")'
python -m pip list --format=freeze
```

Windows PowerShell: ativar com `venv\Scripts\Activate.ps1`. Esperado: ambiente isolado,
instalação bem-sucedida, nenhuma dependência quebrada e ambos os providers importáveis.
Revisar e guardar versões resolvidas em `docs/dependencias-preparacao.txt`; registrar
SO, Python, pip, hash de requirements e versão CLI em `docs/preparacao.md`.
Não editar pins para mascarar falha de instalação. A compatibilidade deve ser provada
com os requisitos fornecidos antes das operações dependentes.

## 3. Conferir configuração sem revelar chaves

Primeiro, reconsultar as fontes de [research.md](research.md) e selecionar os dois
modelos (T007), sem exigir que suas variáveis já estejam preenchidas. Depois configurar
localmente os valores não secretos `USERNAME_LANGSMITH_HUB=fabiocsm`, `LLM_PROVIDER=openai`,
tracing habilitado e os modelos selecionados em `LLM_MODEL`/`EVAL_MODEL` (T008).
Preservar as credenciais existentes e a precedência de variáveis exportadas; não
substituir `.env` pelo template. Só então executar a validação abaixo.

```bash
python - <<'PY'
import os
from dotenv import load_dotenv
load_dotenv('.env')
required = ('LANGSMITH_API_KEY', 'LANGSMITH_PROJECT', 'USERNAME_LANGSMITH_HUB',
            'LANGSMITH_TRACING', 'LLM_PROVIDER', 'LLM_MODEL', 'EVAL_MODEL', 'OPENAI_API_KEY')
missing = [name for name in required if not os.getenv(name, '').strip()]
print('ausentes:', missing)
assert not missing, 'Configuração incompleta'
assert os.getenv('USERNAME_LANGSMITH_HUB') == 'fabiocsm', 'Handle divergente'
assert os.getenv('LLM_PROVIDER') == 'openai', 'Validar condição inicial OpenAI'
assert os.getenv('LANGSMITH_TRACING', '').lower() == 'true', 'Tracing desabilitado'
print('presença e configuração inicial OK; validade remota ainda a comprovar')
PY
```

Esperado: nenhuma ausente e asserções satisfeitas. Esse teste não autentica, não prova
saldo/permissão e não aceita o fallback implícito de `EVAL_MODEL`.

## 4. Contexto LangSmith e contratos instalados

```bash
langsmith --help
langsmith workspace --help
langsmith workspace list --help
langsmith prompt --help
python - <<'PY'
import inspect
from langsmith import Client
for method in ('read_project', 'get_prompt', 'pull_prompt', 'pull_prompt_commit', 'push_prompt'):
    print(method, inspect.signature(getattr(Client, method)))
PY
```

Depois das ajudas, consultar workspaces pelo CLI com autenticação explicitamente
herdada de um subprocesso cujo ambiente foi carregado por dotenv. Processar JSON e
guardar apenas identificação do contexto necessário. A interface autenticada pode
comprovar o handle quando o SDK não oferecer método público. Não usar comando que
imprima token. Conferir endpoint e workspace selecionados, comparando com o projeto
consultado por `Client.read_project(project_name=...)`.

Esperado para concluir T009: identidade autenticada compatível com `fabiocsm`,
workspace/endpoint corretos e consulta ao projeto documentada. Se somente o projeto
ainda não existir, concluir a verificação de contexto e manter sua existência
separadamente `pendente`: isso libera T010–T012. Autenticação inválida, acesso negado
ou contexto incorreto/ambíguo devem ser resolvidos antes de chamar modelos.
Leitura de um prompt público não comprova posse do handle ou permissão de publicação.

Assinaturas devem permitir os contratos do desafio: flag de pull público, mensagens
System/User e parâmetros públicos de push/metadados/revisão. Não realizar pull, push
ou criação de dataset para este teste. Registrar tipos/assinaturas e limites da prova.

## 5. Duas chamadas mínimas reais e tracing

Somente após ambiente, configuração e workspace corretos, executar o cenário abaixo.
Estas chamadas consomem API e podem criar traces; incluir seu consumo no registro.
O exemplo usa entrada sintética curta, não os 15 casos de avaliação.

```bash
PYTHONPATH=src python - <<'PY'
from dotenv import load_dotenv
load_dotenv('.env')
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tracers.langchain import wait_for_all_tracers
from utils import get_llm, get_eval_llm
for role, factory in (('geracao', get_llm), ('avaliacao', get_eval_llm)):
    try:
        response = factory(temperature=0).invoke(
            [SystemMessage(content='Responda brevemente.'), HumanMessage(content='Escreva apenas OK.')],
            config={'run_name': 'preparacao-001-' + role, 'tags': ['preparacao-001', role]})
        assert response.content, 'Resposta vazia'
        print(role, 'OK', 'uso:', response.usage_metadata)
    except Exception as error:
        print(role, 'impedido:', type(error).__name__, 'status:', getattr(error, 'status_code', None))
        raise SystemExit(1)
wait_for_all_tracers()
PY
```

Esperado: dois sucessos, sem rejeição de temperatura zero, com retorno não vazio.
Guardar modelos solicitado/retornado quando disponível, datas, tokens e identificadores
dos traces. Em T013, consultar novamente o projeto se estava ausente e comprovar seu
nome/ID, tenant e os dois traces no contexto esperado antes de resolver a pendência.
Ausência de projeto ou trace mantém a respectiva verificação no estado `pendente`
ou `impedido`, mesmo que o modelo tenha respondido. Erro deve ser classificado sem
copiar a exceção HTTP completa. Se o primeiro papel falhar, corrigir e reexecutar os
papéis não comprovados; registrar chamadas tentadas, inclusive falhas/retries.

Este teste prova acesso e formato básico de mensagens; não mede qualidade como juiz
nem substitui os experimentos da 005. Não fazer avaliações completas na preparação.

## 6. Estados, custo e reprodução

Preencher os três registros previstos, ligar a documentação ao README preservando
o enunciado e aplicar a matriz de prontidão do contrato. Usar a memória de cálculo
da pesquisa para 3–5 ciclos e acrescentar o consumo das verificações, retries e extras.
Consumo indisponível deve ser marcado assim; estimativa não é cobrança observada.

Validar os caminhos entregues e protegidos ao final:

```bash
python -m json.tool docs/integridade-inicial.json > /dev/null
git check-ignore docs/preparacao.md docs/integridade-inicial.json docs/dependencias-preparacao.txt
git diff --check
```

Esperado: JSON válido; `git check-ignore` sem saída e status 1 (nenhum ignorado);
diff sem erros. Repetir hashes da seção 1 e comparar ao manifesto, não apenas ao HEAD.
Revisar os documentos para remover segredos antes de versionar.

Um segundo executor deve repetir as verificações em ambiente isolado, sem reutilizar
venv já instalado; registrar novo ambiente e eventual consumo das duas chamadas.
Não apagar o ambiente original para essa prova. Conservar a condição experimental,
registrar divergências e só afirmar SC-004 após essa reprodução real.

## 7. Cenários negativos e aceite

| Cenário | Resultado exigido |
| --- | --- |
| Variável obrigatória ausente em subprocesso isolado | Identificar nome, impedir etapa dependente; não alterar `.env` real |
| Credencial inválida/sem acesso | Estado impedido e diagnóstico sanitizado; nenhuma declaração de acesso válido |
| Modelo rejeita temperatura ou não está disponível | Alternativa documentada, nova condição e nova comprovação |
| Ambiente não resolve os pins | Impedimento de instalação sem editar protegidos |
| Hash/referência divergente em cópia temporária | Comparação detecta divergência; original permanece intacto |
| Projeto/workspace diferente | Impedir execução no contexto errado |
| Fork privado ou sem vínculo de origem | Pendência explícita da entrega; URL local não comprova visibilidade |

Validar falhas locais em subprocessos/cópias; não gastar chamadas provocando todos
os erros remotos. Falhas reais encontradas são registradas, sem dados fabricados.
Não criar suite paralela aos seis testes da 003 para reproduzir estes comandos.

Aceite: SC-001 requer todas as verificações documentadas; SC-002 exige os dois papéis
comprovados; SC-003 exige origem e integridade verificáveis; SC-004 exige reprodução.
Um relatório com impedimento pode estar completo, mas a preparação não está pronta
para as operações afetadas. Concluir o planejamento não satisfaz esses resultados.
