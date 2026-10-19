# Avaliação e iterações da v2 — spec 005

Registro de execução real da [spec 005](../specs/005-avaliar-iterar-v2/spec.md), separado
dos dublês de teste. Fontes: [contrato C01–C10](../specs/005-avaliar-iterar-v2/contracts/avaliacao-v2.md),
[modelo de dados](../specs/005-avaliar-iterar-v2/data-model.md),
[guia V01–V11](../specs/005-avaliar-iterar-v2/quickstart.md) e
[publicação da v2](publicacao-v2.md).

## Escopo e limites

- Notas vêm **somente** de `python src/evaluate.py`, inalterado. Os blocos abaixo conferem
  pré-condições, leem resultados e recalculam a agregação fornecida para detectar
  incompletude; não reimplementam métricas nem substituem o avaliador.
- Protegidos e somente leitura: `src/evaluate.py`, `src/metrics.py`, `src/utils.py`,
  `datasets/bug_to_user_story.jsonl` (15 exemplos, 5/7/3) e `prompts/bug_to_user_story_v1.yml`.
- Mudanças de comportamento só em `prompts/bug_to_user_story_v2.yml`, com problema e
  hipótese registrados antes, Few-shot próprio e Role Prompting preservados.
- Proibido nesta feature: compartilhar o dataset (`share_dataset`), publicar evidências
  públicas finais, push Git, apagar ou editar dataset, experimentos ou commits do Hub.
- Logs brutos ficam em `results/` (ignorado); este arquivo guarda os fatos sanitizados.
  Nenhum valor de credencial é registrado.

## Rastreabilidade

| Requisito | Contrato | Guia | Onde neste registro |
| --- | --- | --- | --- |
| FR-001 | C01.6 / C02 | V04 | [Bloco de dataset](#bloco-avaliacao_dataset--c02), auditorias por ciclo |
| FR-002 | C01 / C03 / C04 | V03 / V05 / V06 | [Gate](#bloco-avaliacao_gate--c01), experimentos por ciclo |
| FR-003 | C05 | V06 | [Auditoria](#bloco-avaliacao_auditoria--c04c07) |
| FR-004 | C06 | V09 | Decisão de cada ciclo |
| FR-005 | Modelo | V06 / V08 | Seções `CIC-0N` e [comparação](#comparação-dos-ciclos) |
| FR-006 | C07 | V07 | Evidências de trace |
| FR-007 | C08 | V08 | Problema/hipótese de cada ciclo |
| FR-008 | C01.5 / C09 / C10 | V08 / V10 | [Condições](#condições-experimentais), comparação |
| FR-009 | C09 | V10 | [Parada](#decisão-de-parada) |
| FR-010 | C08 / C09 | V10 / V11 | Correspondência final |

## Condições experimentais

Cada condição é declarada **antes** de qualquer execução que a use, num bloco
`json condicao` lido pelo gate. A condição ativa é informada por `AVALIACAO_CONDICAO`
(padrão `COND-001`); condição ausente desta seção bloqueia com `causa=condicao`.
Resultados de condições diferentes não são comparados diretamente.

```json condicao
{"condicao": "COND-001", "provider": "openai", "llm_model": "gpt-4.1-2025-04-14", "eval_model": "gpt-4.1-2025-04-14", "temperature": 0, "langsmith_project": "mba-ia-pull-evaluation-prompt", "dataset_name": "mba-ia-pull-evaluation-prompt-eval", "workspace_id": "15dd5852-a835-4163-826c-e78668fd2a9c", "endpoint": "https://api.smith.langchain.com"}
```

`COND-001` vem da [preparação](preparacao.md#condição-experimental): temperatura `0`
fixada pelo código fornecido, SDK `langsmith` 0.13.0 e `langchain-core` 1.6.4, hashes
dos protegidos iguais ao [manifesto](integridade-inicial.json). Preços oficiais usados
nas estimativas: US$ 2/M tokens de entrada e US$ 8/M de saída.

## Formatos de registro

Campos conforme o [modelo de dados](../specs/005-avaliar-iterar-v2/data-model.md).

- **RevisãoCandidata**: ciclo, commit Git local, SHA-256 de arquivo e definição da v2,
  `hub_commit` completo, data e resultado do `push_prompts.py`, inspeção no dashboard
  sem login (data e itens conferidos) e resultado dos testes.
- **AuditoriaDataset**: `dataset_id`, contagem, igualdade com o JSONL, distribuição
  5/7/3 e estado (`idêntico` · `divergente` · `ausente`).
- **Experimento**: ID, nome e URL; condição, `hub_commit` e dataset; início/fim ISO 8601
  e `AVALIACAO_EXIT_CODE`; linha `STATUS` impressa; HEAD antes/depois e hashes; cinco
  médias e média geral; tokens e custo; estado. Estados: `planejado`, `gate_ok`,
  `bloqueado` (com `causa`), `executado`, `falha_execução`, `auditado`, `incompleto`,
  `invalidado`, `reprovado`, `aprovado` e `substituído`.
- **CicloOtimização**: ID, problema, hipótese, alteração, commit, validação, revisão,
  experimento e conclusão. Seção não executada registra apenas a justificativa.
- **EvidênciaTrace**: experimento, exemplo, dificuldade, IDs dos runs raiz, template,
  LLM e juízes, e a relação entre entrada, mensagens, resposta, julgamentos e feedback.
- **RegistroCusto**: tokens de entrada/saída de geração e juízes (`estimado` quando o
  run não informa), custo estimado do experimento e acumulado.

## Roteiro executável

Execute da raiz com o venv ativo. Ordem obrigatória em **todo** ciclo: dataset (C02) →
gate (C01) → avaliação (C03) → auditoria (C04–C07). Entradas não secretas por variáveis
de ambiente; o `.env` é carregado sem sobrescrever variáveis exportadas.

### Bloco AVALIACAO_DATASET — C02

Localiza `{LANGSMITH_PROJECT}-eval` pelo nome exato. Se ausente, chama uma única vez a
função fornecida `evaluate.create_evaluation_dataset` (importada, sem alteração) e audita
em seguida; se presente, apenas lê. Compara o multiconjunto canônico remoto × local (D02)
e emite `dataset_id`, `example_map` e estado, mais as linhas de exportação. Nunca apaga,
edita ou compartilha. Divergência: código 1 e isolamento por D03.

```bash
source venv/bin/activate
python - <<'PY'
# AVALIACAO_DATASET — C02: criação única pela função fornecida e auditoria.
import collections
import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client
from langsmith.utils import get_env_var

load_dotenv('.env', override=False)
get_env_var.cache_clear()
logging.disable(logging.CRITICAL)  # Não registrar corpos/headers de erros HTTP.
JSONL = 'datasets/bug_to_user_story.jsonl'
DISTRIBUTION = {'simple': 5, 'medium': 7, 'complex': 3}
report = {'bloco': 'AVALIACAO_DATASET', 'ciclo': os.getenv('AVALIACAO_CICLO', '')}


def canonical(inputs, outputs):
    return json.dumps({'inputs': inputs, 'outputs': outputs}, sort_keys=True,
                      ensure_ascii=False)


try:
    project = os.getenv('LANGSMITH_PROJECT', '').strip()
    if not project:
        raise ValueError('LANGSMITH_PROJECT ausente')
    name = f'{project}-eval'
    local = [json.loads(line) for line in
             Path(JSONL).read_text(encoding='utf-8').splitlines() if line.strip()]
    pools = collections.defaultdict(list)
    for index, case in enumerate(local, 1):
        pools[canonical(case['inputs'], case['outputs'])].append(
            (index, case['metadata']['complexity']))
    client = Client(timeout_ms=15000)

    def find():
        return [item for item in client.list_datasets(dataset_name=name) if item.name == name]

    found = find()
    created = False
    if not found:
        sys.path.insert(0, 'src')
        import evaluate
        evaluate.create_evaluation_dataset(client, name, JSONL)  # Uma única chamada.
        created = True
        found = find()
    report.update(dataset_name=name, criado=created)
    if len(found) != 1:
        report.update(estado='ausente' if not found else 'divergente',
                      datasets_com_o_nome=len(found))
    else:
        dataset = found[0]
        examples = list(client.list_examples(dataset_id=dataset.id))
        remote = collections.Counter(canonical(item.inputs, item.outputs) for item in examples)
        expected = collections.Counter({key: len(value) for key, value in pools.items()})
        matches = remote == expected and len(examples) == len(local) == 15
        example_map = {}
        if matches:
            for item in examples:
                index, complexity = pools[canonical(item.inputs, item.outputs)].pop(0)
                example_map[str(item.id)] = {'indice': index, 'complexidade': complexity}
        distribution = dict(collections.Counter(
            value['complexidade'] for value in example_map.values()))
        matches = matches and distribution == DISTRIBUTION
        report.update(dataset_id=str(dataset.id), example_count=len(examples),
                      matches_local=matches, distribution=distribution,
                      example_map=example_map, estado='idêntico' if matches else 'divergente')
    if report['estado'] != 'idêntico':
        report['acao'] = ('D03: não apagar nem editar; declarar COND-00N com novo '
                          'LANGSMITH_PROJECT, exportar AVALIACAO_CONDICAO e repetir este bloco')
except Exception as error:
    report.update(estado='erro', categoria=type(error).__name__,
                  http_status=getattr(error, 'status_code', None))
print(json.dumps(report, ensure_ascii=False))  # Sem str(error), headers ou segredos.
if report.get('dataset_id'):
    print(f"AVALIACAO_DATASET_ID={report['dataset_id']}")
print(f"AVALIACAO_DATASET={report['estado']}")
if report['estado'] != 'idêntico':
    raise SystemExit(1)
PY
```

Exporte as duas últimas linhas impressas (`export AVALIACAO_DATASET_ID=…` e
`export AVALIACAO_DATASET=…`) antes do gate do mesmo ciclo.

### Bloco AVALIACAO_GATE — C01

Somente leituras, nenhuma chamada LLM. Entradas: `AVALIACAO_CICLO`, `AVALIACAO_CONDICAO`
(padrão `COND-001`), `AVALIACAO_HUB_COMMIT`, `AVALIACAO_V2_FILE_SHA256`,
`AVALIACAO_V2_DEFINITION_SHA256`, `AVALIACAO_DATASET_ID`/`AVALIACAO_DATASET` do bloco
anterior, `AVALIACAO_TESTES=aprovado` (testes da revisão comprovados pela tarefa
anterior), `AVALIACAO_DASHBOARD=conferido` (inspeção registrada) e
`AVALIACAO_CUSTO_ACUMULADO_USD`. Qualquer falha: código 1, `bloqueado` e `causa`.

```bash
source venv/bin/activate
python - <<'PY'
# AVALIACAO_GATE — C01: somente leituras; nenhuma chamada LLM ou escrita remota.
import hashlib
import json
import logging
import math
import os
import re
import subprocess
from pathlib import Path

import yaml
from dotenv import load_dotenv
from langsmith import Client
from langsmith.utils import get_env_var, tracing_is_enabled

load_dotenv('.env', override=False)
get_env_var.cache_clear()  # Reavaliar o ambiente depois de carregar dotenv.
logging.disable(logging.CRITICAL)  # Não registrar corpos/headers de erros HTTP.
V1_SHA256 = '2cddcf8f8183b4d29a5bca4d4efca17601962aa98ac75323f7dabbfa905c0d70'  # 002
V2_PATH = 'prompts/bug_to_user_story_v2.yml'
PROMPT = 'bug_to_user_story_v2'
COST_LIMIT_USD = 4.0
stage = 'condicao'
report = {'bloco': 'AVALIACAO_GATE', 'ciclo': os.getenv('AVALIACAO_CICLO', '')}


class Blocked(Exception):
    pass


def check(ok, cause, code):
    if not ok:
        raise Blocked(cause, code)  # Somente códigos constantes, sem valores secretos.


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def definition_sha256(path):
    data = yaml.safe_load(Path(path).read_bytes())[PROMPT]
    canonical = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def declared_conditions():
    text = Path('docs/avaliacao-v2.md').read_text(encoding='utf-8')
    blocks = re.findall(r'^```json condicao\n(.*?)^```$', text, flags=re.M | re.S)
    return {item['condicao']: item for item in map(json.loads, blocks)}


try:
    condition_id = os.getenv('AVALIACAO_CONDICAO', '').strip() or 'COND-001'
    conditions = declared_conditions()
    check(condition_id in conditions, 'condicao', 'condicao_nao_declarada')
    condition = conditions[condition_id]
    report['condicao'] = condition_id

    stage = 'configuracao'
    provider = os.getenv('LLM_PROVIDER', '').strip()
    required = ['LANGSMITH_API_KEY', 'LANGSMITH_PROJECT', 'USERNAME_LANGSMITH_HUB',
                'LLM_PROVIDER', 'LLM_MODEL', 'EVAL_MODEL']
    if provider == 'openai':
        required.append('OPENAI_API_KEY')
    elif provider in ('google', 'gemini'):
        required.append('GOOGLE_API_KEY')
    missing = [name for name in required if not os.getenv(name, '').strip()]
    report['variaveis_ausentes'] = missing
    check(not missing, 'configuracao', 'variavel_ausente')
    check(tracing_is_enabled() is True, 'configuracao', 'tracing_desabilitado')
    check(provider == condition['provider'], 'configuracao', 'provider_divergente')
    check(os.environ['LLM_MODEL'] == condition['llm_model'], 'configuracao',
          'modelo_geracao_divergente')
    check(os.environ['EVAL_MODEL'] == condition['eval_model'], 'configuracao',
          'modelo_juiz_divergente')
    project_name = os.environ['LANGSMITH_PROJECT']
    check(project_name == condition['langsmith_project'], 'configuracao', 'projeto_divergente')
    check(f'{project_name}-eval' == condition['dataset_name'], 'configuracao',
          'dataset_da_condicao_divergente')
    endpoint = os.getenv('LANGSMITH_ENDPOINT', 'https://api.smith.langchain.com').rstrip('/')
    check(endpoint == condition['endpoint'], 'configuracao', 'endpoint_divergente')
    report.update(provider=provider, llm_model=os.environ['LLM_MODEL'],
                  eval_model=os.environ['EVAL_MODEL'], projeto=project_name,
                  endpoint=endpoint, tracing=True)

    stage = 'integridade'
    manifest = json.loads(Path('docs/integridade-inicial.json').read_text(encoding='utf-8'))
    protected = {path: sha256(path) for path in manifest['files']}
    check(len(protected) == 4 and all(protected[path] == item['sha256']
                                      for path, item in manifest['files'].items()),
          'integridade', 'protegido_divergente')
    check(sha256('prompts/bug_to_user_story_v1.yml') == V1_SHA256, 'integridade',
          'v1_divergente')
    report['protegidos'] = protected

    stage = 'revisao'
    hub_commit = os.getenv('AVALIACAO_HUB_COMMIT', '').strip()
    expected_file = os.getenv('AVALIACAO_V2_FILE_SHA256', '').strip()
    expected_definition = os.getenv('AVALIACAO_V2_DEFINITION_SHA256', '').strip()
    check(hub_commit and expected_file and expected_definition, 'revisao',
          'revisao_nao_informada')
    status = subprocess.run(['git', 'status', '--porcelain', '--', V2_PATH],
                            capture_output=True, text=True, check=True, timeout=30)
    check(status.stdout.strip() == '', 'revisao', 'v2_com_alteracao_nao_commitada')
    git_commit = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True,
                                text=True, check=True, timeout=30).stdout.strip()
    file_sha, definition_sha = sha256(V2_PATH), definition_sha256(V2_PATH)
    check(file_sha == expected_file, 'revisao', 'hash_arquivo_v2_divergente')
    check(definition_sha == expected_definition, 'revisao', 'hash_definicao_v2_divergente')
    report.update(git_commit=git_commit, v2_file_sha256=file_sha,
                  v2_definition_sha256=definition_sha)

    stage = 'testes'
    check(os.getenv('AVALIACAO_TESTES', '') == 'aprovado', 'testes', 'testes_nao_aprovados')
    stage = 'dashboard'
    check(os.getenv('AVALIACAO_DASHBOARD', '') == 'conferido', 'dashboard',
          'inspecao_nao_registrada')
    stage = 'custo'
    try:
        cost = float(os.getenv('AVALIACAO_CUSTO_ACUMULADO_USD', ''))
    except ValueError:
        cost = math.nan
    check(math.isfinite(cost) and 0 <= cost <= COST_LIMIT_USD, 'custo',
          'custo_acumulado_acima_do_limite_ou_invalido')
    report['custo_acumulado_usd'] = cost

    stage = 'configuracao'
    client = Client(timeout_ms=15000)
    project = client.read_project(project_name=project_name)
    check(str(project.tenant_id) == condition['workspace_id'], 'configuracao',
          'workspace_divergente')
    report.update(project_id=str(project.id), workspace_id=str(project.tenant_id))

    stage = 'dataset'
    dataset_id = os.getenv('AVALIACAO_DATASET_ID', '').strip()
    check(dataset_id, 'dataset', 'dataset_nao_auditado_no_ciclo')
    check(os.getenv('AVALIACAO_DATASET', '') == 'idêntico', 'dataset', 'dataset_nao_identico')
    found = [item for item in client.list_datasets(dataset_name=condition['dataset_name'])
             if item.name == condition['dataset_name']]
    check(len(found) == 1 and str(found[0].id) == dataset_id, 'dataset',
          'dataset_id_divergente')
    report['dataset_id'] = dataset_id

    stage = 'revisao'
    prompt = client.get_prompt(f"{os.environ['USERNAME_LANGSMITH_HUB']}/{PROMPT}")
    check(prompt is not None and prompt.is_public is True, 'revisao', 'prompt_nao_publico')
    check(prompt.last_commit_hash == hub_commit, 'revisao', 'head_divergente')
    report.update(hub_commit=hub_commit, head_before=prompt.last_commit_hash, publico=True,
                  estado='gate_ok')
    print(json.dumps(report, ensure_ascii=False))
except Blocked as blocked:
    report.update(estado='bloqueado', causa=blocked.args[0], codigo=blocked.args[1])
    print(json.dumps(report, ensure_ascii=False))
    raise SystemExit(1)
except Exception as error:
    report.update(estado='bloqueado', causa=stage, codigo='erro_na_conferencia',
                  categoria=type(error).__name__,
                  http_status=getattr(error, 'status_code', None))
    print(json.dumps(report, ensure_ascii=False))  # Sem str(error), headers ou segredos.
    raise SystemExit(1)
PY
```

### Execução — C03

Somente depois de `gate_ok` no mesmo ciclo, sem editar a v2, em bash ou zsh. `pipefail`
faz `$?` ser o código do avaliador, não o do `tee`; o log não contém esse código.
Sem retry automático; `max_concurrency`, juízes, dados e limiar permanecem os fornecidos.

```bash
mkdir -p results && export AVALIACAO_INICIO="$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"; LOG="results/${AVALIACAO_CICLO}-$(date +%Y%m%dT%H%M%S).log"; set -o pipefail; python src/evaluate.py 2>&1 | tee "$LOG"; export AVALIACAO_EXIT_CODE=$?; set +o pipefail; export AVALIACAO_LOG="$LOG"; echo "AVALIACAO_EXIT_CODE=$AVALIACAO_EXIT_CODE" >> "$LOG.exit"
```

### Bloco AVALIACAO_AUDITORIA — C04–C07

Somente leituras, nenhuma chamada LLM. Entradas: `AVALIACAO_LOG`, `AVALIACAO_EXIT_CODE` e
`AVALIACAO_INICIO` da execução, `AVALIACAO_DATASET_ID`, `AVALIACAO_HUB_COMMIT` e os dois
hashes da v2 do ciclo. Identifica o experimento por `selectedSessions` (D05), confere o
dataset de referência e reconstrói `example_map`, valida 15 runs e 75 notas (D06),
estabilidade e vínculo com a revisão (D04), calcula `by_complexity`, `lowest`, tokens e
custo, e aplica C06: médias recalculadas como em `evaluate.py`, conferência com as médias,
a média geral e a linha `STATUS` impressas, código do avaliador e regra integral; prevalece
a decisão mais restritiva. Sem URL no log: lista projetos parciais só para registro e emite `falha_execução`.

```bash
source venv/bin/activate
python - <<'PY'
# AVALIACAO_AUDITORIA — C04–C07: somente leituras; nenhuma chamada LLM ou escrita remota.
import collections
import hashlib
import json
import logging
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml
from dotenv import load_dotenv
from langsmith import Client
from langsmith.utils import get_env_var

load_dotenv('.env', override=False)
get_env_var.cache_clear()
logging.disable(logging.CRITICAL)  # Não registrar corpos/headers de erros HTTP.
KEYS = ['helpfulness', 'correctness', 'f1_score', 'clarity', 'precision']
BASE = ['f1_score', 'clarity', 'precision']
MARKERS = ('Erro na avaliação', 'Erro ao processar resposta', 'Resposta vazia')  # D06
PREFIX = 'fabiocsm-bug_to_user_story_v2'
JSONL = 'datasets/bug_to_user_story.jsonl'
V1_SHA256 = '2cddcf8f8183b4d29a5bca4d4efca17601962aa98ac75323f7dabbfa905c0d70'  # 002
V2_PATH = 'prompts/bug_to_user_story_v2.yml'
PROMPT = 'bug_to_user_story_v2'
PRICE = {'entrada': 2 / 1_000_000, 'saida': 8 / 1_000_000}  # US$/token, COND-001
ESTIMATE = {'geracao': (1800, 533), 'juizes': (4533, 467)}  # D08, por exemplo sem contagem
stage = 'log'
report = {'bloco': 'AVALIACAO_AUDITORIA', 'ciclo': os.getenv('AVALIACAO_CICLO', ''),
          'condicao': os.getenv('AVALIACAO_CONDICAO', '').strip() or 'COND-001'}
invalid, incomplete, limitations = [], [], []


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def definition_sha256(path):
    data = yaml.safe_load(Path(path).read_bytes())[PROMPT]
    canonical = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def canonical(inputs, outputs):
    return json.dumps({'inputs': inputs, 'outputs': outputs}, sort_keys=True,
                      ensure_ascii=False)


def valid_score(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and 0 <= value <= 1)


def aware(moment):
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def note(target, code):
    if code not in target:
        target.append(code)


try:
    log = Path(os.environ['AVALIACAO_LOG']).read_text(encoding='utf-8')
    dataset_id = os.getenv('AVALIACAO_DATASET_ID', '').strip()
    hub_commit = os.getenv('AVALIACAO_HUB_COMMIT', '').strip()
    client = Client(timeout_ms=15000)
    match = re.search(r'https://\S*[?&]selectedSessions=([0-9a-fA-F-]{36})', log)
    if not match:
        stage = 'projetos_parciais'
        started = os.getenv('AVALIACAO_INICIO', '').strip()
        started = aware(datetime.fromisoformat(started)) if started else None
        partial = [{'id': str(item.id), 'nome': item.name,
                    'inicio': aware(item.start_time).isoformat()}
                   for item in client.list_projects(reference_dataset_id=dataset_id)
                   if item.name.startswith(PREFIX)
                   and (started is None or aware(item.start_time) >= started)]
        report.update(estado='falha_execução', causa='url_do_experimento_ausente',
                      exit_code=os.getenv('AVALIACAO_EXIT_CODE'), projetos_parciais=partial)
        print(json.dumps(report, ensure_ascii=False))
        raise SystemExit(1)
    experiment_id = match.group(1)

    stage = 'experimento'
    project = client.read_project(project_id=experiment_id)
    report['experimento'] = {'id': experiment_id, 'nome': project.name, 'url': match.group(0),
                             'reference_dataset_id': str(project.reference_dataset_id)}
    if str(project.reference_dataset_id) != dataset_id:
        note(invalid, 'dataset_do_experimento_divergente')
    if not project.name.startswith(PREFIX):
        note(invalid, 'prefixo_do_experimento_divergente')

    stage = 'dataset'
    local = [json.loads(line) for line in
             Path(JSONL).read_text(encoding='utf-8').splitlines() if line.strip()]
    pools = collections.defaultdict(list)
    for index, case in enumerate(local, 1):
        pools[canonical(case['inputs'], case['outputs'])].append(
            (index, case['metadata']['complexity']))
    example_map = {}
    for item in client.list_examples(dataset_id=dataset_id):
        candidates = pools.get(canonical(item.inputs, item.outputs))
        if candidates:
            index, complexity = candidates.pop(0)
            example_map[str(item.id)] = {'indice': index, 'complexidade': complexity}
        else:
            example_map = None
            break
    if not example_map or len(example_map) != 15 or any(pools.values()):
        note(invalid, 'example_map_nao_reconstruido')
        example_map = example_map or {}

    stage = 'runs'
    roots = list(client.list_runs(project_id=experiment_id, is_root=True))
    references = [str(run.reference_example_id) for run in roots]
    if len(roots) != 15:
        note(incomplete, 'runs_raiz_diferente_de_15')
    if len(set(references)) != len(references):
        note(incomplete, 'exemplo_repetido')
    if example_map and set(references) != set(example_map):
        note(incomplete, 'exemplos_nao_cobertos')
    if len(re.findall(r'^\s*\[\d+\] F1:', log, flags=re.M)) != 15:
        note(incomplete, 'log_sem_15_exemplos')
    templates = {}
    for run in client.list_runs(project_id=experiment_id, run_type='prompt'):
        if run.name == 'ChatPromptTemplate':
            templates[str(run.trace_id)] = ((run.extra or {}).get('metadata') or {}).get(
                'lc_hub_commit_hash')
    present = [value for value in templates.values() if value]
    if any(value != hub_commit for value in present):
        note(invalid, 'lc_hub_commit_hash_divergente')
    root_traces = {str(run.trace_id) for run in roots}
    if not present:
        hub_link = 'ausente'
    elif len(present) == 15 and set(templates) == root_traces and len(roots) == 15:
        hub_link = 'confirmado'
    else:
        hub_link = 'parcial'
    if hub_link != 'confirmado':
        note(limitations, f'lc_hub_commit_hash_{hub_link}')

    stage = 'feedback'
    grouped = collections.defaultdict(list)
    for item in client.list_feedback(run_ids=[run.id for run in roots]):
        grouped[(str(item.run_id), item.key)].append(item)
    rows = []
    for run in roots:
        answer = (run.outputs or {}).get('answer')
        if run.error:
            note(incomplete, 'run_com_erro')
        if not isinstance(answer, str) or not answer.strip():
            note(incomplete, 'resposta_vazia')
        scores, comments, judges = {}, {}, set()
        for key in KEYS:
            items = grouped.get((str(run.id), key), [])
            if not items:
                note(incomplete, 'feedback_ausente')
                continue
            if len(items) > 1:
                note(incomplete, 'feedback_duplicado')
                continue
            item = items[0]
            if not valid_score(item.score):
                note(incomplete, 'nota_invalida')
                continue
            if any(marker in (item.comment or '') for marker in MARKERS):
                note(incomplete, 'marcador_de_falha')
                continue
            scores[key], comments[key] = float(item.score), item.comment or ''
            source = getattr(item, 'feedback_source', None)
            judge = (((getattr(source, 'metadata', None) or {}).get('__run') or {})
                     .get('run_id'))
            if judge:
                judges.add(str(judge))
        if len(scores) == 5 and (
                abs(scores['helpfulness'] - round((scores['clarity'] + scores['precision']) / 2, 4)) > 1e-9
                or abs(scores['correctness'] - round((scores['f1_score'] + scores['precision']) / 2, 4)) > 1e-9):
            note(incomplete, 'derivada_inconsistente')
        info = example_map.get(str(run.reference_example_id), {})
        rows.append({'indice': info.get('indice'), 'complexidade': info.get('complexidade'),
                     'example_id': str(run.reference_example_id), 'root_run_id': str(run.id),
                     'trace_id': str(run.trace_id),
                     'answer_chars': len(answer) if isinstance(answer, str) else 0,
                     'prompt_commit': templates.get(str(run.trace_id)),
                     'judge_run_ids': sorted(judges), 'notas': scores,
                     'comentarios': {key: comments[key][:300] for key in BASE if key in comments},
                     'tokens': (run.prompt_tokens, run.completion_tokens)})
    rows.sort(key=lambda row: (row['indice'] is None, row['indice'] or 0))
    valid_notes = sum(len(row['notas']) for row in rows)
    if valid_notes != 75:
        note(incomplete, 'notas_validas_diferente_de_75')

    stage = 'estabilidade'
    prompt = client.get_prompt(f"{os.environ['USERNAME_LANGSMITH_HUB']}/{PROMPT}")
    head_after = getattr(prompt, 'last_commit_hash', None)
    if head_after != hub_commit:
        note(invalid, 'head_alterado')
    if (sha256(V2_PATH) != os.getenv('AVALIACAO_V2_FILE_SHA256', '').strip()
            or definition_sha256(V2_PATH) != os.getenv('AVALIACAO_V2_DEFINITION_SHA256', '').strip()):
        note(invalid, 'v2_alterada')
    manifest = json.loads(Path('docs/integridade-inicial.json').read_text(encoding='utf-8'))
    if (any(sha256(path) != item['sha256'] for path, item in manifest['files'].items())
            or sha256('prompts/bug_to_user_story_v1.yml') != V1_SHA256):
        note(invalid, 'protegido_alterado')

    stage = 'analise'
    complete_rows = [row for row in rows if len(row['notas']) == 5]
    by_complexity = {}
    for level in ('simple', 'medium', 'complex'):
        group = [row for row in complete_rows if row['complexidade'] == level]
        by_complexity[level] = {'exemplos': len(group), **{
            key: round(sum(row['notas'][key] for row in group) / len(group), 4)
            for key in KEYS if group}}
    lowest = {key: [{'indice': row['indice'], 'complexidade': row['complexidade'],
                     'nota': round(row['notas'][key], 4),
                     'comentario': row['comentarios'].get(key, '')}
                    for row in sorted((row for row in rows if key in row['notas']),
                                      key=lambda row: (row['notas'][key], row['indice'] or 0))[:3]]
              for key in BASE}
    tokens = {'geracao': {'entrada': 0, 'saida': 0, 'estimados': 0},
              'juizes': {'entrada': 0, 'saida': 0, 'estimados': 0}}
    for row in rows:
        prompt_tokens, completion_tokens = row.pop('tokens')
        if prompt_tokens is None or completion_tokens is None:
            prompt_tokens, completion_tokens = ESTIMATE['geracao']
            tokens['geracao']['estimados'] += 1
        tokens['geracao']['entrada'] += prompt_tokens
        tokens['geracao']['saida'] += completion_tokens
        judge = client.read_run(row['judge_run_ids'][0]) if len(row['judge_run_ids']) == 1 else None
        judge_in = getattr(judge, 'prompt_tokens', None)
        judge_out = getattr(judge, 'completion_tokens', None)
        if judge_in is None or judge_out is None:
            judge_in, judge_out = ESTIMATE['juizes']
            tokens['juizes']['estimados'] += 1
        tokens['juizes']['entrada'] += judge_in
        tokens['juizes']['saida'] += judge_out
    tokens['estimado'] = any(part['estimados'] for part in tokens.values())
    cost = sum(part['entrada'] * PRICE['entrada'] + part['saida'] * PRICE['saida']
               for part in (tokens['geracao'], tokens['juizes']))

    stage = 'decisao'  # C06: agregação de evaluate.py, regra integral e sinal do avaliador.
    means = overall = None
    if len(rows) == len(complete_rows) == 15:
        means = {key: round(sum(row['notas'][key] for row in rows) / 15, 4) for key in KEYS}
        overall = sum(means.values()) / 5
    labels = {'helpfulness': 'Helpfulness', 'correctness': 'Correctness',
              'f1_score': 'F1-Score', 'clarity': 'Clarity', 'precision': 'Precision'}
    printed = {}
    for key, label in labels.items():
        found = re.findall(rf'^\s*- {re.escape(label)}: (\d+\.\d+)', log, flags=re.M)
        printed[key] = found[-1] if found else None
    found = re.findall(r'MÉDIA GERAL: (\d+\.\d+)', log)
    printed_overall = found[-1] if found else None
    found = re.findall(r'STATUS: (APROVADO|REPROVADO)', log)
    printed_status = found[-1] if found else None
    raw_exit = os.getenv('AVALIACAO_EXIT_CODE', '').strip()
    exit_code = int(raw_exit) if re.fullmatch(r'-?\d+', raw_exit) else None
    divergences = []
    if printed_status is None:
        note(incomplete, 'status_ausente')
    if means is not None and (any(printed[key] != f'{means[key]:.2f}' for key in KEYS)
                              or printed_overall != f'{overall:.4f}'):
        note(incomplete, 'medias_impressas_divergentes')
    if exit_code not in (0, 1):
        note(divergences, 'codigo_ausente_ou_invalido')
    elif printed_status and (exit_code == 0) != (printed_status == 'APROVADO'):
        note(divergences, 'codigo_contraditorio_com_status')
    evaluator = 'aprovado' if exit_code == 0 and printed_status == 'APROVADO' else 'reprovado'
    below = [key for key in KEYS if means is not None and means[key] < 0.8]
    if invalid:
        contract = 'invalidado'
    elif incomplete:
        contract = 'incompleto'
    else:
        contract = 'aprovado' if not below and overall >= 0.8 else 'reprovado'
    if contract in ('aprovado', 'reprovado') and contract != evaluator:
        note(divergences, 'decisao_avaliador_divergente')
    decision = contract
    if contract == 'aprovado' and (evaluator != 'aprovado' or divergences):
        decision = 'reprovado'  # Prevalece a decisão mais restritiva.
    if any(score < 0.8 for row in complete_rows for score in row['notas'].values()):
        note(limitations, 'notas_individuais_abaixo_do_limiar')
    report.update(means=means, overall=overall, printed_means=printed,
                  printed_overall=printed_overall, printed_status=printed_status,
                  exit_code=exit_code, decisao_avaliador=evaluator, decisao_contrato=contract,
                  decisao=decision, metricas_abaixo=below, divergencias=divergences)
    report.update(
        completude={'estado': 'incompleto' if incomplete else 'completo', 'runs': len(roots),
                    'notas_validas': valid_notes, 'problemas': incomplete},
        vinculo={'estado': 'invalidado' if invalid else 'estavel', 'head_antes': hub_commit,
                 'head_depois': head_after, 'lc_hub_commit_hash': hub_link,
                 'v2_file_sha256': sha256(V2_PATH), 'problemas': invalid},
        exemplos=rows, by_complexity=by_complexity, lowest=lowest, tokens=tokens,
        custo_estimado_usd=round(cost, 6), limitacoes=limitations)
    report['estado'] = decision
except SystemExit:
    raise
except Exception as error:
    report.update(estado='falha_auditoria', etapa=stage, categoria=type(error).__name__,
                  http_status=getattr(error, 'status_code', None))
    print(json.dumps(report, ensure_ascii=False))  # Sem str(error), headers ou segredos.
    raise SystemExit(1)
print(json.dumps(report, ensure_ascii=False))
if report['estado'] in ('invalidado', 'incompleto'):
    raise SystemExit(1)
PY
```

## Ciclos

### CIC-01

Referência inicial: v2 publicada da 003/004, **sem edição** (o modelo de dados define
`CIC-01` como avaliação da v2 da 003). Estado final: **aprovado** (regra integral C06);
**substituído** para fins de entrega pela edição de `CIC-02` (FR-010).

- **Data**: 2026-10-18 (São Paulo); execução de 2026-10-19T02:56:38+00:00 a 02:57:54+00:00.
- **Condição**: `COND-001` — provedor `openai`, geração e juiz `gpt-4.1-2025-04-14`,
  temperatura 0 (conferida no run LLM), projeto `mba-ia-pull-evaluation-prompt`.
- **Dataset**: `mba-ia-pull-evaluation-prompt-eval`, ID `8c78638d-37a5-4175-9984-8db0e3473228`,
  auditado `idêntico` imediatamente antes (15 exemplos, 5/7/3).
- **v2 local**: commit Git `0380149697e263da4f38c7462ffb3fff6a452903`, YAML inalterado desde a
  004; SHA-256 arquivo `49ffb35893ae86769d22b555b9b0017e1910e08c49373e89a1931f58ec06c46d`,
  definição `ab661782f912303d01a38d45d8a0f89074b84a1a5756fd6d6df7aa7f0489b89c`.
- **Revisão publicada**: `4278de75a2fca03a17cc1e3ab9d66d552c2c1aaebe543a085a34772637fa9595`,
  pública; HEAD igual antes e depois e `lc_hub_commit_hash` igual nos 15 runs do template.
- **Inspeção no dashboard**: sem login em 2026-10-18T21:38:48-03:00
  ([registro](publicacao-v2.md#inspeção-visual--c07-5--t033)); revisão não mudou desde então.
- **Testes**: `pytest -q` 816 aprovados (T020), incluindo os seis obrigatórios.
- **Experimento**: `fabiocsm-bug_to_user_story_v2-31a99eea`, ID
  `86196746-1c83-42cc-868b-6b57f977f19b`,
  [URL](https://smith.langchain.com/o/15dd5852-a835-4163-826c-e78668fd2a9c/datasets/8c78638d-37a5-4175-9984-8db0e3473228/compare?selectedSessions=86196746-1c83-42cc-868b-6b57f977f19b)
  (workspace do autor; compartilhamento público pertence à 006).
- **Médias**: Helpfulness 0.8687 · Correctness 0.8492 · F1-Score 0.8057 · Clarity 0.8447 ·
  Precision 0.8927 (recalculadas; iguais às impressas 0.87/0.85/0.81/0.84/0.89).
- **Média geral**: 0.8522 (impressa `0.8522`).
- **Completude**: 15 runs raiz sem erro, 15 exemplos distintos, 75 notas válidas, nenhum
  marcador de falha, derivadas consistentes.
- **Decisão**: contrato `aprovado`; avaliador `AVALIACAO_EXIT_CODE=0` e `STATUS: APROVADO`;
  nenhuma divergência. Limitação: notas individuais abaixo de 0.8 (ver análise).
- **Custo acumulado**: US$ 0,222376 (este experimento; tokens lidos, nenhum estimado).
- **Problema**: não se aplica — referência inicial, sem ciclo anterior.
- **Hipótese**: não se aplica — a v2 da 003/004 é avaliada sem edição.

**Execução (T015)** — `python src/evaluate.py` com `pipefail`, log local
`results/CIC-01-20261018T235638.log` (ignorado), `AVALIACAO_EXIT_CODE=0`. Saída: 15 linhas
por exemplo, resumo com cinco métricas, `📊 MÉDIA GERAL: 0.8522`,
`✅ STATUS: APROVADO - Todas as métricas >= 0.8` e a URL acima. Sem retry.

**Auditoria (T016)** — 2026-10-18T23:58:27-03:00, bloco `AVALIACAO_AUDITORIA` código 0,
estado `aprovado`. C04: `reference_dataset_id` igual ao dataset auditado, `example_map`
reconstruído (15), HEAD antes/depois `4278de75…9595`, `lc_hub_commit_hash` **confirmado**
nos 15 runs do template (confirma a pendência de D04), hashes da v2, v1 e protegidos iguais.
C05: completo. C06: médias recalculadas = impressas, decisão do contrato = do avaliador.
O SDK emitiu `DeprecationWarning` para `list_runs`/`read_run` (remoção anunciada após
2027-01-31); não afeta este resultado.

**RegistroCusto** — geração: 19.166 tokens de entrada e 4.532 de saída; juízes (15 runs
`evaluate_all_metrics`, 45 chamadas): 51.498 de entrada e 5.599 de saída; nenhum valor
estimado. Custo estimado US$ 0,222376 (US$ 2/M entrada, US$ 8/M saída), abaixo da
estimativa D08 (≈ US$ 0,31). Acumulado da 005: **US$ 0,222376**. Cobrança observada: não
disponível.

**Análise C07 (T017)** — médias por dificuldade:

| Dificuldade | Exemplos | Helpfulness | Correctness | F1-Score | Clarity | Precision |
| --- | --- | --- | --- | --- | --- | --- |
| simple | 5 | 0.8880 | 0.8688 | 0.8216 | 0.8600 | 0.9160 |
| medium | 7 | 0.8664 | 0.8319 | **0.7809** | 0.8500 | 0.8829 |
| complex | 3 | 0.8417 | 0.8567 | 0.8367 | 0.8067 | 0.8767 |

Três menores notas por métrica base (índice local do JSONL, dificuldade, nota):

| Métrica | 1ª | 2ª | 3ª | Padrão nos comentários do juiz |
| --- | --- | --- | --- | --- |
| F1-Score | #12 medium 0.6154 | #1 simple 0.6857 | #10 medium 0.6857 | **Omissão** de critérios presentes na referência e ausentes do relato (confirmação visual e contador do carrinho; backdrop, largura e teclado no modal; paginação/virtualização) |
| Clarity | #1 simple 0.70 | #14 complex 0.75 | #6 medium 0.80 | **Organização**: mistura de perguntas ao usuário com requisitos; linguagem técnica em caso complexo |
| Precision | #1 simple 0.80 | #6 medium 0.83 | #7 medium 0.83 | **Excesso**: dúvidas e itens além do pedido; nenhuma alucinação apontada (1.0 nos três) |

Padrão observado: as perdas vêm de omissão de detalhes que só a referência contém e de
seções de dúvidas consideradas fora do foco; não há invenção apontada pelo juiz. Como a
média do F1-Score (0.8057) é a mais próxima do limiar, ela é o ponto de atenção para
qualquer edição futura (D10: F1 → omissões), sempre sem copiar referências.

**EvidênciaTrace** (experimento `86196746-1c83-42cc-868b-6b57f977f19b`; juízes no projeto
`evaluators` `1fd04873-c944-4efe-b95c-2201cd1ac164`, ligados por `source_run_id`):

| Exemplo | Raiz `target` | Template | LLM geração | Run do avaliador | LLMs dos juízes |
| --- | --- | --- | --- | --- | --- |
| #1 simple (`2d3d7a29-14bf-4df7-bc8e-3681ba191140`) | `01a15217-85ee-77f0-b508-18fea1259ad1` | `01a15217-85ee-7612-a528-00038c8ed05e` | `01a15217-85ef-7cb2-83aa-d89a55e73ee3` | `80f1196f-3256-4cdf-b4cd-8567994033bf` | `01a15218-0c39-7380-bde2-aac4b72212fc`, `01a15218-1143-7311-93a7-0c1960a5a5b0`, `01a15218-15c3-73f1-af55-e9a2aa27f0fb` |
| #12 medium (`39966495-cd2d-499f-9393-1319bfe1aa7b`) | `01a15217-3f2f-7b30-88a4-4556de32786e` | `01a15217-3f2f-71e3-af89-3a1904acbbcf` | `01a15217-3f30-7f00-890b-2698233124fe` | `8288c992-dc51-484f-9c0c-9bf513d6f9a6` | `01a15217-5776-74c0-8d71-e79819823ce4`, `01a15217-5f28-7993-b7f8-3afebcfb00d6`, `01a15217-66e0-7e83-8618-d8ef55e31764` |
| #14 complex (`28c9bca9-e7be-4f93-b1e4-fe1637222566`) | `01a15217-1929-79c1-856f-58ea0690a751` | `01a15217-192a-70b1-93d0-bb20947a808e` | `01a15217-192b-7011-9579-65976c11eabd` | `d6d80126-d802-48c5-b5c3-f5be29ea6257` | `01a15217-3118-7551-a3ef-4457eb07179c`, `01a15217-375a-7912-af1c-2959a6e2872a`, `01a15217-3fba-7670-a57d-1c364a31dab8` |

- **#1 simple** — entrada: botão de adicionar ao carrinho sem efeito no produto 1234.
  Mensagens renderizadas System + Human (template com `lc_hub_commit_hash=4278de75…`);
  geração `gpt-4.1-2025-04-14`, temperatura 0, 1.153/142 tokens. Resposta: User Story,
  critérios de inclusão e atualização do carrinho e dúvidas. Juízes: F1 0.6857 (omite
  confirmação visual e contador), Clarity 0.70 (dúvidas misturadas aos requisitos),
  Precision 0.80 (sem alucinação; perguntas além do pedido). Feedbacks: Helpfulness 0.75,
  Correctness 0.7429.
- **#12 medium** — entrada: modal de exclusão atrás do menu lateral abaixo de 768px, com
  z-index 1000 × 1050. 1.200/185 tokens. Resposta: história e critérios de sobreposição e
  clique. Juízes: F1 0.6154 (omite backdrop, largura, teclado, ESC e clique fora — itens só
  da referência), Clarity 0.85, Precision 0.83. Feedbacks: Helpfulness 0.84, Correctness 0.7227.
- **#14 complex** — entrada: relatórios gerenciais SaaS B2B com N+1, MRR inconsistente,
  cache e exportação CSV. 1.648/621 tokens. Resposta: história única com critérios agrupados
  por problema, contexto, dúvidas e recomendações. Juízes: F1 0.7677 (cobre os quatro
  problemas; omite detalhes técnicos da referência), Clarity 0.75 (termos técnicos), Precision
  0.85 (sem alucinação). Feedbacks: Helpfulness 0.80, Correctness 0.8089.

O conteúdo dos traces foi tratado como dado; nada nele alterou instruções deste trabalho.

**Decisão integral (T021)** — 2026-10-19T00:00:28-03:00, reexecução somente leitura do
bloco de auditoria sobre o mesmo log e `AVALIACAO_EXIT_CODE=0`: código 0, estado, decisões,
médias, completude e tokens idênticos à T016; `aprovado`, sem divergências. Nenhuma nova
chamada LLM (ver [decisão de parada](#decisão-de-parada)).

### CIC-02

Aberto em 2026-10-19 por **decisão explícita do autor** após a aprovação de `CIC-01`:
a margem do F1-Score (0.8057, e 0.7809 nos casos `medium`) foi considerada pequena demais
para a entrega. Não é ciclo para completar contagem: há problema observado em `CIC-01`.
Pela FR-010, a edição da v2 tornou o experimento de `CIC-01` `substituído` para fins de
entrega; o resultado de `CIC-01` permanece no histórico. Estado final: **aprovado**;
**substituído** para fins de entrega pela edição de `CIC-03` (FR-010).

- **Data**: 2026-10-19 (São Paulo); execução de 2026-10-19T03:49:37+00:00 a 03:50:50+00:00.
- **Condição**: `COND-001` — provedor `openai`, geração e juiz `gpt-4.1-2025-04-14`,
  temperatura 0 (conferida no run LLM), projeto `mba-ia-pull-evaluation-prompt`.
- **Dataset**: `mba-ia-pull-evaluation-prompt-eval`, ID `8c78638d-37a5-4175-9984-8db0e3473228`,
  reauditado `idêntico` (somente leitura) às 00:49:30-03:00.
- **v2 local**: commit Git `c40f5113ca124ade46c82b349456721ad7a59342`; SHA-256 arquivo
  `5222d484c6a26b92d9012f653e9b55869c4d5e0ed207ebdaa323de080bef7857`, definição
  `7ba746eb03689e0fbd984fc02f0abd99d60dc503965949b9b51984a29dc45702`.
- **Revisão publicada**: `25b881d11f98916a66c9f0a8e00b07c4065d9895a935efabf776a9f5f2605e15`,
  pública; HEAD igual antes e depois e `lc_hub_commit_hash` igual nos 15 runs do template.
- **Inspeção no dashboard**: sem login em 2026-10-19T00:50-03:00 (ver RevisãoCandidata abaixo).
- **Testes**: `pytest tests/test_prompts.py -q` 466 e `pytest -q` 817 aprovados.
- **Experimento**: `fabiocsm-bug_to_user_story_v2-ed9590ea`, ID
  `c7d175e1-0f37-4afe-9b2a-88e061b01666`,
  [URL](https://smith.langchain.com/o/15dd5852-a835-4163-826c-e78668fd2a9c/datasets/8c78638d-37a5-4175-9984-8db0e3473228/compare?selectedSessions=c7d175e1-0f37-4afe-9b2a-88e061b01666)
  (workspace do autor; compartilhamento público pertence à 006).
- **Médias**: Helpfulness 0.8837 · Correctness 0.8738 · F1-Score 0.8416 · Clarity 0.8613 ·
  Precision 0.9060 (recalculadas; iguais às impressas 0.88/0.87/0.84/0.86/0.91).
- **Média geral**: 0.8733 (impressa `0.8733`).
- **Completude**: 15 runs raiz sem erro, 15 exemplos distintos, 75 notas válidas, nenhum
  marcador de falha, derivadas consistentes.
- **Decisão**: contrato `aprovado`; avaliador `AVALIACAO_EXIT_CODE=0` e `STATUS: APROVADO`;
  nenhuma divergência. Limitação: notas individuais abaixo de 0.8 (ver análise).
- **Custo acumulado**: US$ 0,484720 (US$ 0,222376 de `CIC-01` + US$ 0,262344 deste).
- **Problema**: em `CIC-01` o F1-Score foi a métrica mais baixa (0.8057) e os comentários do
  juiz nas menores notas (#12 0.6154, #1 0.6857, #10 0.6857) apontam **omissão** de critérios
  verificáveis, não invenção (Precision sem alucinações apontadas). A v2 instrui “Para bug
  simples, prefira uma história curta e poucos critérios concretos” e só demonstra um
  critério no Exemplo 1; as respostas simples tiveram de 1 a 3 critérios. Nos casos
  `medium`/`complex`, detalhes técnicos informados no relato (valores, condições, erros)
  ficaram fora dos critérios ou apenas no contexto.
- **Hipótese**: (D10, F1 → omissões) exigir que os critérios cubram, além do fluxo principal,
  os resultados observáveis **decorrentes diretamente** do comportamento esperado (estado
  visível após a ação, retorno ao usuário, bloqueio/mensagem em validação, condições e
  limites informados) e, quando o relato trouxer detalhes técnicos, critérios técnicos
  verificáveis para cada detalhe informado, aumentará a cobertura (F1) sem inventar fatos
  — números, causas e soluções ausentes continuam proibidos. Critérios no padrão
  Dado/Quando/Então tornam cada resultado verificável. Dúvidas ficam restritas a lacunas
  que impedem um critério, para não reduzir Clarity/Precision. Few-shot próprio e Role
  Prompting mantidos; nenhum caso ou referência do dataset é usado; nenhuma instrução ao juiz.
- **Risco previsto**: Precision pode cair se critérios decorrentes forem lidos como excesso;
  será comparada com `CIC-01` (0.8927).

**Alteração** (somente `prompts/bug_to_user_story_v2.yml`): critérios no padrão Dado/Quando/
Então cobrindo também os resultados que decorrem diretamente do comportamento esperado;
nova seção opcional **Critérios técnicos** para detalhes técnicos informados; regra “3 a 5
critérios” para bug simples no lugar de “poucos critérios”; cobertura de cada sintoma,
número, condição e restrição em relatos detalhados; dúvidas só para lacunas que impedem um
critério; esclarecimento de que resultados decorrentes não são invenção (números, causas e
soluções ausentes continuam proibidos). Exemplo 1 passou de 1 para 4 critérios e o Exemplo 3
ganhou critérios simétricos e um critério técnico; Exemplo 2 inalterado. Tags, técnicas
(`Few-shot Learning`, `Role Prompting`), versão e `{bug_report}` inalterados. Teste documental
ajustado para aceitar ciclo marcado **Em andamento** só com a decisão de parada reaberta.

**RevisãoCandidata** — SHA-256 arquivo
`5222d484c6a26b92d9012f653e9b55869c4d5e0ed207ebdaa323de080bef7857`, definição
`7ba746eb03689e0fbd984fc02f0abd99d60dc503965949b9b51984a29dc45702`; testes
`pytest tests/test_prompts.py -q` 466 e `pytest -q` 817 aprovados; `python src/push_prompts.py`
em 2026-10-19T00:48:49-03:00, código 0, `publication=confirmada`, `revision_source=push_return`,
revisão `25b881d11f98916a66c9f0a8e00b07c4065d9895a935efabf776a9f5f2605e15`, conteúdo,
metadata e acesso anônimo conferidos; inspeção sem login no navegador integrado em
2026-10-19T00:50-03:00: “Log in”, badge Public, histórico com 2 commits (`25b881d1` sobre
`4278de75`), cinco tags, System com persona, regras novas e `## Exemplos`, User com `{bug_report}`.

**Dataset e gate** — bloco `AVALIACAO_DATASET` 00:49:30-03:00 código 0 (`criado=false`,
`idêntico`, 15, 5/7/3); bloco `AVALIACAO_GATE` 00:49:32-03:00 código 0, `gate_ok`, HEAD
antes `25b881d1…5e15`, commit Git `c40f511…`, custo acumulado informado 0.222376.

**Execução** — `python src/evaluate.py` com `pipefail`, log local
`results/CIC-02-20261019T004937.log` (ignorado), `AVALIACAO_EXIT_CODE=0`,
`📊 MÉDIA GERAL: 0.8733`, `✅ STATUS: APROVADO - Todas as métricas >= 0.8`. Sem retry.

**Auditoria** — 2026-10-19T00:51:21-03:00, bloco `AVALIACAO_AUDITORIA` código 0, estado
`aprovado`: C04 estável (`reference_dataset_id` correto, `example_map` reconstruído, HEAD
antes/depois `25b881d1…5e15`, `lc_hub_commit_hash` confirmado nos 15 runs, hashes da v2,
v1 e protegidos iguais); C05 completo; C06 médias recalculadas = impressas e decisão do
contrato = do avaliador.

**RegistroCusto** — geração 24.671 entrada / 6.585 saída; juízes 57.657 / 5.626; nenhum
estimado; US$ 0,262344. Acumulado **US$ 0,484720** (gate de US$ 4 não acionado).

**Análise C07** — médias por dificuldade:

| Dificuldade | Exemplos | Helpfulness | Correctness | F1-Score | Clarity | Precision |
| --- | --- | --- | --- | --- | --- | --- |
| simple | 5 | 0.8560 | 0.8609 | 0.8498 | 0.8400 | 0.8720 |
| medium | 7 | 0.8929 | 0.8657 | 0.8172 | 0.8714 | 0.9143 |
| complex | 3 | 0.9083 | 0.9141 | 0.8848 | 0.8733 | 0.9433 |

| Métrica | 1ª | 2ª | 3ª | Padrão nos comentários do juiz |
| --- | --- | --- | --- | --- |
| F1-Score | #10 medium 0.6462 | #12 medium 0.6857 | #7 medium 0.7467 | **Omissão** de soluções/valores presentes só na referência (paginação, backdrop e largura, tempo máximo) |
| Clarity | #1 simple 0.70 | #6 medium 0.80 | #3 simple 0.85 | **Organização/extensão**: critérios técnicos e dúvidas em bug simples soam excessivos |
| Precision | #1 simple 0.70 | #7 medium 0.83 | #12 medium 0.83 | **Excesso** em #1 (foco 0.6); sem alucinação apontada |

Conclusão sobre a hipótese: **confirmada para F1** — média 0.8057 → 0.8416 (+0.0359), e
`simple` 0.8216 → 0.8498, `medium` 0.7809 → 0.8172, `complex` 0.8367 → 0.8848; #1 subiu de
0.6857 para 0.8889 ao cobrir confirmação e atualização do carrinho. O risco previsto ocorreu
só localmente: Precision e Clarity de #1 caíram para 0.70 pelo excesso em bug simples, mas
as médias de Precision (0.8927 → 0.9060) e Clarity (0.8447 → 0.8613) subiram. Os três
menores F1 restantes dependem de soluções técnicas que o relato não traz e que a v2
corretamente não inventa. Uma única execução por revisão: a melhora é observada, não
estatisticamente comprovada (D09).

**Limitação observada no trace #10**: um critério fixa “não congela por mais de 1 segundo”,
valor ausente do relato (que informa 5–10 s). Isso contraria a regra da v2 contra números
inventados; o juiz não o apontou (Precision 0.93). Registrado como limitação do
comportamento do modelo; não foi corrigido nesta revisão.

**EvidênciaTrace** (experimento `c7d175e1-0f37-4afe-9b2a-88e061b01666`; juízes no projeto
`evaluators` `1fd04873-c944-4efe-b95c-2201cd1ac164`, ligados por `source_run_id`):

| Exemplo | Raiz `target` | Template | LLM geração | Run do avaliador | LLMs dos juízes |
| --- | --- | --- | --- | --- | --- |
| #1 simple (`2d3d7a29-14bf-4df7-bc8e-3681ba191140`) | `01a15248-21c5-75f1-a718-41d276c84faf` | `01a15248-21c6-7460-b7cc-8b5511ac04c8` | `01a15248-21c7-7613-96bf-0b694d62fec3` | `be5920f6-a8f4-4a08-9392-dcb89212f5e0` | `01a15248-8297-7d92-80c8-499a58e1c6d6`, `01a15248-8894-7a33-ba91-09915cca7aa6`, `01a15248-8d09-76f2-8c1a-ea9e3ca4d592` |
| #10 medium (`307a4c8c-710f-4287-b880-07a10752cec2`) | `01a15247-db4f-7923-97f7-544b4f0e64c5` | `01a15247-db50-70b0-9984-94035c2f085e` | `01a15247-db51-78e1-9a3c-71f9cbfb9ec7` | `66561163-a21d-4f66-8e41-7b58d5a558e1` | `01a15247-fd4c-79d0-a099-3f158d5c57af`, `01a15248-0185-7d32-b09a-cdb5e5597163`, `01a15248-062f-7a82-8b72-4b6c83766e78` |
| #15 complex (`d8b97b54-cf10-42af-9d04-3938fddb2e8d`) | `01a15247-80b8-72c2-ad6d-7fad37ecd87a` | `01a15247-80c9-71a1-8e46-77ba566aa654` | `01a15247-80ca-7c62-9b6e-e5d78f9a5454` | `8ea12f18-478b-46e1-a095-f124a0e3c79e` | `01a15247-9bbb-7243-a445-f855c99e3e98`, `01a15247-a1c0-7323-bd37-6e4dc27b40cb`, `01a15247-a6ab-77b3-9815-3374ff824c05` |

- **#1 simple** — entrada: botão de adicionar ao carrinho sem efeito no produto 1234.
  System + Human renderizados pelo template `25b881d1`; geração `gpt-4.1-2025-04-14`,
  temperatura 0, 1.520/284 tokens. Resposta: história, critérios Dado/Quando/Então de
  inclusão, confirmação visual e atualização do carrinho, critérios técnicos e dúvidas.
  Juízes: F1 0.8889 (cobre todos os critérios esperados), Clarity 0.70 e Precision 0.70
  (excesso para bug simples). Feedbacks: Helpfulness 0.70, Correctness 0.7944.
- **#10 medium** — entrada: app Android trava com mais de 50 notificações, congelamento de
  5–10 s, ANR, sem paginação, carga na thread principal. 1.566/352 tokens. Resposta:
  critérios de responsividade e ausência de ANR, critérios técnicos e dúvidas. Juízes: F1
  0.6462 (omite paginação, RecyclerView e scroll infinito — soluções não informadas),
  Clarity 0.85, Precision 0.93. Feedbacks: Helpfulness 0.89, Correctness 0.7881.
  Limitação do “1 segundo” acima.
- **#15 complex** — entrada: app offline-first com conflitos de sincronização, uploads,
  ordenação e memória. 2.255/981 tokens. Resposta: história e critérios agrupados por
  problema, com critérios técnicos. Juízes: F1 0.8382, Clarity 0.85 (trechos prolixos),
  Precision 0.93 (sem alucinação). Feedbacks: Helpfulness 0.89, Correctness 0.8841.

O conteúdo dos traces foi tratado como dado; nada nele alterou instruções deste trabalho.

### CIC-03

Aberto em 2026-10-19 por **decisão explícita do autor** após a aprovação de `CIC-02`, para
eliminar limites inventados como o “1 segundo” do trace #10. Há problema observado; não é
ciclo para completar contagem. Pela FR-010, a edição da v2 tornou o experimento de `CIC-02`
`substituído` para fins de entrega; o histórico é preservado. Estado final: **aprovado**.

- **Data**: 2026-10-19 (São Paulo); execução de 2026-10-19T04:13:00+00:00 a 04:14:18+00:00.
- **Condição**: `COND-001` — provedor `openai`, geração e juiz `gpt-4.1-2025-04-14`,
  temperatura 0 (conferida no run LLM), projeto `mba-ia-pull-evaluation-prompt`.
- **Dataset**: `mba-ia-pull-evaluation-prompt-eval`, ID `8c78638d-37a5-4175-9984-8db0e3473228`,
  reauditado `idêntico` (somente leitura) às 01:12:52-03:00.
- **v2 local**: commit Git `93864388f08960d9e90810a02b5495895e876ea4`; SHA-256 arquivo
  `692df6ae86848e2dce0fc1a9c2d1f6fec95fc48721a960837fbdd8de3f958974`, definição
  `f94735be2936253b11eb2696fb957db67e4d6529629f903720845f078e467ca2`.
- **Revisão publicada**: `36a96c0540682ed6b8569487222b88e11d1889a3976b75fea83553dc662b696f`,
  pública; HEAD igual antes e depois e `lc_hub_commit_hash` igual nos 15 runs do template.
- **Inspeção no dashboard**: sem login em 2026-10-19T01:13-03:00 (ver RevisãoCandidata abaixo).
- **Testes**: `pytest tests/test_prompts.py -q` 466 e `pytest -q` 817 aprovados.
- **Experimento**: `fabiocsm-bug_to_user_story_v2-9c836e20`, ID
  `d864cfbb-6ab9-4901-ab06-62f68ccd96fc`,
  [URL](https://smith.langchain.com/o/15dd5852-a835-4163-826c-e78668fd2a9c/datasets/8c78638d-37a5-4175-9984-8db0e3473228/compare?selectedSessions=d864cfbb-6ab9-4901-ab06-62f68ccd96fc)
  (workspace do autor; compartilhamento público pertence à 006).
- **Médias**: Helpfulness 0.8773 · Correctness 0.8754 · F1-Score 0.8474 · Clarity 0.8513 ·
  Precision 0.9033 (recalculadas; iguais às impressas 0.88/0.88/0.85/0.85/0.90).
- **Média geral**: 0.8709 (impressa `0.8709`).
- **Completude**: 15 runs raiz sem erro, 15 exemplos distintos, 75 notas válidas, nenhum
  marcador de falha, derivadas consistentes.
- **Decisão**: contrato `aprovado`; avaliador `AVALIACAO_EXIT_CODE=0` e `STATUS: APROVADO`;
  nenhuma divergência. Limitação: notas individuais abaixo de 0.8 e um valor inventado (#14).
- **Custo acumulado**: US$ 0,755018 (0,222376 + 0,262344 + 0,270298 deste).
- **Problema**: varredura das 30 respostas de `CIC-01`/`CIC-02` por números ausentes do
  relato encontrou duas invenções reais, contrárias à regra “Não invente … números” da v2:
  #10 (nos dois ciclos) define “a tela não congela por mais de 1 segundo”, quando o relato só
  informa congelamento de 5–10 s; #8 (`CIC-02`) cita “código de status HTTP apropriado (ex:
  403 ou 401)”, ausente do relato. Não são invenção: #9 `R$ 1.500` (soma dos valores
  informados) e #15 `1.000` (o `1000+` do relato). O juiz não penalizou as invenções
  (Precision 0.93 em #10), portanto o problema é de fidelidade ao enunciado do prompt, não de nota.
- **Hipótese**: o modelo cria uma meta quando o relato traz o valor indesejado mas não o
  aceitável, e usa “ex:” para concretizar respostas técnicas. Uma regra explícita — sem
  limites, metas, prazos, códigos, percentuais ou exemplos com “ex:” que não estejam no
  relato; critério expresso de forma qualitativa ou em relação ao valor relatado (“sem o
  congelamento de 5–10 s relatado”); limite ausente registrado em **Dúvidas** quando for
  necessário; valores calculados diretamente dos informados permitidos — mais uma
  demonstração no Exemplo 3 (trava com duração informada e sem limite) eliminará essas
  invenções sem reduzir as médias abaixo de 0.8. Few-shot próprio e Role Prompting mantidos;
  nenhum caso ou referência do dataset; nenhuma instrução ao juiz.
- **Risco previsto**: F1 pode cair levemente onde a referência traz metas numéricas que o
  relato não informa (#7, #12), pois a v2 seguirá sem inventá-las; dúvidas adicionais podem
  reduzir Clarity/Precision. Critério de sucesso: nenhuma invenção na mesma varredura e
  aprovação pela regra integral.

**Alteração** (somente `prompts/bug_to_user_story_v2.yml`): nova regra **Valores** em
“Fundamentação e casos de borda” — somente números, limites, códigos e unidades do relato ou
calculados diretamente deles; proibidos metas, tempos máximos, códigos de erro, percentuais e
exemplos com “ex.:”; critério relativo ao valor indesejado relatado e limite ausente em
**Dúvidas**. Exemplo 3: entrada ganhou uma trava de 4 a 6 s sem limite informado; saída ganhou
o grupo “Abertura de trilhas” com critério relativo ao valor relatado e a dúvida sobre o
tempo máximo aceitável; história atualizada. Exemplos 1 e 2, tags, técnicas, versão e
`{bug_report}` inalterados.

**RevisãoCandidata** — SHA-256 arquivo
`692df6ae86848e2dce0fc1a9c2d1f6fec95fc48721a960837fbdd8de3f958974`, definição
`f94735be2936253b11eb2696fb957db67e4d6529629f903720845f078e467ca2`; testes
`pytest tests/test_prompts.py -q` 466 e `pytest -q` 817 aprovados; `python src/push_prompts.py`
em 2026-10-19T01:12:15-03:00, código 0, `publication=confirmada`, `revision_source=push_return`,
revisão `36a96c0540682ed6b8569487222b88e11d1889a3976b75fea83553dc662b696f`, conteúdo,
metadata e acesso anônimo conferidos; inspeção sem login no navegador integrado em
2026-10-19T01:13-03:00: “Log in”, badge Public, histórico com 3 commits (`36a96c05` sobre
`25b881d1` e `4278de75`), cinco tags, System com persona, regra de valores e `## Exemplos`,
User com `{bug_report}`.

**Dataset e gate** — bloco `AVALIACAO_DATASET` 01:12:52-03:00 código 0 (`criado=false`,
`idêntico`, 15, 5/7/3); bloco `AVALIACAO_GATE` 01:12:53-03:00 código 0, `gate_ok`, HEAD
antes `36a96c05…696f`, commit Git `9386438…`, custo acumulado informado 0.484720.

**Execução** — `python src/evaluate.py` com `pipefail`, log local
`results/CIC-03-20261019T011300.log` (ignorado), `AVALIACAO_EXIT_CODE=0`,
`📊 MÉDIA GERAL: 0.8709`, `✅ STATUS: APROVADO - Todas as métricas >= 0.8`. Sem retry.

**Auditoria** — 2026-10-19T01:14:43-03:00, bloco `AVALIACAO_AUDITORIA` código 0, estado
`aprovado`: C04 estável (`reference_dataset_id` correto, `example_map` reconstruído, HEAD
antes/depois `36a96c05…696f`, `lc_hub_commit_hash` confirmado nos 15 runs, hashes da v2,
v1 e protegidos iguais); C05 completo; C06 médias recalculadas = impressas e decisão do
contrato = do avaliador.

**RegistroCusto** — geração 27.671 entrada / 6.628 saída; juízes 57.786 / 5.795; nenhum
estimado; US$ 0,270298. Acumulado **US$ 0,755018** (gate de US$ 4 não acionado).

**Análise C07** — médias por dificuldade:

| Dificuldade | Exemplos | Helpfulness | Correctness | F1-Score | Clarity | Precision |
| --- | --- | --- | --- | --- | --- | --- |
| simple | 5 | 0.8540 | 0.8594 | 0.8569 | 0.8460 | 0.8620 |
| medium | 7 | 0.8786 | 0.8724 | 0.8234 | 0.8357 | 0.9214 |
| complex | 3 | 0.9133 | 0.9088 | 0.8877 | 0.8967 | 0.9300 |

| Métrica | 1ª | 2ª | 3ª | Padrão nos comentários do juiz |
| --- | --- | --- | --- | --- |
| F1-Score | #10 medium 0.6857 | #7 medium 0.70 | #5 simple 0.7467 | **Omissão** de soluções só da referência (paginação) e critérios considerados extras (#7, #5) |
| Clarity | #1 simple 0.70 | #5 simple 0.80 | #6 medium 0.80 | **Extensão** em bug simples; perguntas ao usuário |
| Precision | #1 simple 0.70 | #5 simple 0.80 | #7 medium 0.80 | **Excesso** em bug simples (foco 0.5 em #1); sem alucinação apontada |

**Varredura de valores (critério de sucesso do ciclo)** — mesma regra aplicada às 15
respostas: números ausentes do relato e trechos com “ex:”/“por exemplo”.

| Caso | `CIC-02` | `CIC-03` |
| --- | --- | --- |
| #10 medium | “não congela por mais de 1 segundo” (inventado) | “não congela nem trava por 5 a 10 segundos” (valor relatado) e dúvida sobre o tempo máximo aceitável — **corrigido** |
| #8 medium | critério “status HTTP apropriado (ex: 403 ou 401)” (inventado) | sem código nos critérios; dúvida “erro 403, 404 ou outra?” — opções numa pergunta, **limítrofe** |
| #14 complex | — | “CPU do banco não ultrapassa 80%” (inventado; o relato informa 95% no pico) — **nova invenção** |
| #9, #13, #14 (“50 mil”), #15 | soma `R$ 1.500` e valores citados do relato | idem — **não são invenção** |

Conclusão sobre a hipótese: **parcialmente confirmada**. Invenções em critérios caíram de
duas para uma, e o caso-alvo #10 passou a seguir a regra; a regra não eliminou a tendência
(nova meta de CPU em #14). As médias permaneceram aprovadas: F1 0.8416 → 0.8474 (o risco
previsto de queda não ocorreu), Clarity 0.8613 → 0.8513, Precision 0.9060 → 0.9033, média
geral 0.8733 → 0.8709 — variações pequenas, compatíveis com oscilação de uma única execução
por revisão (D09).

**EvidênciaTrace** (experimento `d864cfbb-6ab9-4901-ab06-62f68ccd96fc`; juízes no projeto
`evaluators` `1fd04873-c944-4efe-b95c-2201cd1ac164`, ligados por `source_run_id`):

| Exemplo | Raiz `target` | Template | LLM geração | Run do avaliador | LLMs dos juízes |
| --- | --- | --- | --- | --- | --- |
| #1 simple (`2d3d7a29-14bf-4df7-bc8e-3681ba191140`) | `01a1525d-899e-7711-835f-249803cf7318` | `01a1525d-899f-74a0-817b-a2458e1537da` | `01a1525d-89a0-79f0-b50e-ad08e6c38a4f` | `b7973768-c22d-4614-b359-a49e6df21293` | `01a1525d-fd04-7c00-b901-9330996d9a69`, `01a1525e-027f-7a60-b7fb-22a287c156cf`, `01a1525e-0707-7332-ad67-3642a44872d6` |
| #10 medium (`307a4c8c-710f-4287-b880-07a10752cec2`) | `01a1525d-3ff5-7ae0-8915-df303b9a69b8` | `01a1525d-3ff6-7052-b5c1-ba61bd974532` | `01a1525d-3ff7-7663-9d15-4a3fdfb54a0a` | `6c19d03a-dbda-40ea-bf80-382f2cbb4010` | `01a1525d-6d14-75e3-a705-f3efa115d0c1`, `01a1525d-72cd-7923-aa51-bc5ce4990e8d`, `01a1525d-775a-7763-9604-91a5427eb210` |
| #14 complex (`28c9bca9-e7be-4f93-b1e4-fe1637222566`) | `01a1525d-0432-7f50-99c6-c059ec587aa2` | `01a1525d-0432-7fe1-a617-86e62b300206` | `01a1525d-0433-73c0-a0cd-ff6944476675` | `8b32f3ca-937d-4872-9fbd-a7cf63fadd63` | `01a1525d-20c3-72f3-88ee-099f473c07db`, `01a1525d-2a7c-7211-b12a-d3a49d5b25a7`, `01a1525d-2fd5-7e83-bb21-531ebfab3298` |

- **#1 simple** — entrada: botão de adicionar ao carrinho sem efeito no produto 1234.
  System + Human renderizados pelo template `36a96c05`; geração `gpt-4.1-2025-04-14`,
  temperatura 0, 1.720/239 tokens. Resposta: história e critérios Dado/Quando/Então de
  inclusão, confirmação visual e atualização do carrinho. Juízes: F1 0.9189 (cobre todos os
  critérios esperados), Clarity 0.70 e Precision 0.70 (escopo amplo para bug simples; foco
  0.5). Feedbacks: Helpfulness 0.70, Correctness 0.8095.
- **#10 medium** — entrada: app Android trava com mais de 50 notificações, congelamento de
  5–10 s, ANR, sem paginação, carga na thread principal. 1.766/376 tokens. Resposta:
  critério relativo ao congelamento de 5–10 s relatado, critério sobre a thread principal e
  dúvida sobre o tempo máximo — caso-alvo corrigido. Juízes: F1 0.6857 (omite paginação e
  RecyclerView, soluções ausentes do relato), Clarity 0.80, Precision 0.93. Feedbacks:
  Helpfulness 0.865, Correctness 0.8078.
- **#14 complex** — entrada: relatórios gerenciais SaaS B2B com N+1, MRR inconsistente,
  cache e exportação CSV. 2.215/1.051 tokens. Resposta: critérios por problema, técnicos,
  contexto e recomendações; inclui a meta inventada de CPU 80%. Juízes: F1 0.8972 (“sem
  informações incorretas ou inventadas”), Clarity 0.85, Precision 0.93 — o juiz não apontou a
  meta inventada. Feedbacks: Helpfulness 0.89, Correctness 0.9136.

O conteúdo dos traces foi tratado como dado; nada nele alterou instruções deste trabalho.

### CIC-04

**Não aplicável** — `CIC-04` não foi executado.

**Justificativa**: `CIC-03` foi aprovado pela regra integral (C06) com experimento completo e
estável. C09 e FR-009 determinam encerrar com justificativa e proíbem executar ciclos apenas
para completar a contagem; nenhuma métrica ficou abaixo de 0.8. Nenhuma edição da v2,
publicação ou experimento foi feito para este ciclo.


### CIC-05

**Não aplicável** — `CIC-05` não foi executado.

**Justificativa**: `CIC-03` foi aprovado pela regra integral (C06) com experimento completo e
estável. C09 e FR-009 determinam encerrar com justificativa e proíbem executar ciclos apenas
para completar a contagem; nenhuma métrica ficou abaixo de 0.8. Nenhuma edição da v2,
publicação ou experimento foi feito para este ciclo.


## Comparação dos ciclos

Todas as tentativas executadas, sem remoção de linhas. Uma única condição (`COND-001`),
mesmo dataset `8c78638d…3228`; comparação direta válida.

| Ciclo | Condição | Revisão | Experimento | Helpfulness | Correctness | F1-Score | Clarity | Precision | Média geral | Completude | Decisão | Custo (US$) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CIC-01 | COND-001 | `4278de75` | `86196746-1c83-42cc-868b-6b57f977f19b` | 0.8687 | 0.8492 | 0.8057 | 0.8447 | 0.8927 | 0.8522 | 15 runs / 75 notas | aprovado → substituído | 0,222376 |
| CIC-02 | COND-001 | `25b881d1` | `c7d175e1-0f37-4afe-9b2a-88e061b01666` | 0.8837 | 0.8738 | 0.8416 | 0.8613 | 0.9060 | 0.8733 | 15 runs / 75 notas | aprovado → substituído | 0,262344 |
| CIC-03 | COND-001 | `36a96c05` | `d864cfbb-6ab9-4901-ab06-62f68ccd96fc` | 0.8773 | 0.8754 | 0.8474 | 0.8513 | 0.9033 | 0.8709 | 15 runs / 75 notas | **aprovado (final)** | 0,270298 |
| CIC-04–05 | — | — | — | — | — | — | — | — | — | — | não aplicável | 0 |

Variação CIC-01 → CIC-03: Helpfulness +0.0086, Correctness +0.0262, F1-Score +0.0417,
Clarity +0.0066, Precision +0.0106, média geral +0.0187. Invenções de valores em critérios
(varredura): `CIC-01` 1 (#10), `CIC-02` 2 (#8, #10), `CIC-03` 1 (#14). Custo total US$ 0,755018.

Resumo das mudanças: `CIC-02` — critérios Dado/Quando/Então cobrindo resultados decorrentes,
critérios técnicos para detalhes informados, 3 a 5 critérios em bug simples e dúvidas só
bloqueantes. `CIC-03` — regra de valores (somente valores do relato ou calculados deles,
nenhuma meta/código/“ex.:” criado, limite ausente perguntado) e demonstração no Exemplo 3.
Não houve repetição por falha de infraestrutura nem experimento descartado. Comparação
numérica com a v1 não foi executada (opcional; exigiria experimento adicional e decisão
explícita do autor). A comparação qualitativa v1/v2 fica para a documentação da 006.
## Decisão de parada

**Aprovação em `CIC-03`** (C09/FR-009), 2026-10-19. Ciclos efetivamente executados: **3**,
dentro do plano de 3–5. `CIC-02` e `CIC-03` foram abertos por decisão do autor, cada um com
problema e hipótese registrados antes da edição. `CIC-03` foi aprovado com experimento
completo, estável e vinculado à revisão `36a96c05…696f`, cinco médias e média geral ≥ 0.8
(menor média 0.8474) e decisão do contrato igual à do avaliador. Ciclos 04–05 não foram
executados: C09 proíbe ciclos só para completar a contagem. Gate de custo não acionado
(acumulado US$ 0,755018 ≤ US$ 4). Repetições por falha de infraestrutura: nenhuma.

Limitações registradas: notas individuais abaixo de 0.8 em cinco exemplos (menor F1 #10
0.6857; Clarity/Precision de #1 0.70); uma meta inventada em critério (#14, CPU 80%) e
opções de código numa dúvida (#8), apesar da regra de valores; o juiz não penaliza essas
invenções. Temperatura 0 não garante determinismo e cada revisão foi avaliada uma única vez
(D09). Qualquer edição futura da v2 reabre um ciclo completo (FR-010).

### Correspondência final — SC-005 (T031)

2026-10-19: YAML local (`692df6ae…8974` / `f94735be…7ca2`, commit `9386438…`, sem
alterações pendentes), HEAD do Hub (`36a96c05…696f`, lido no gate e na auditoria) e
`lc_hub_commit_hash` dos 15 runs do experimento aprovado `d864cfbb…96fc` são a mesma
revisão. Inspeção sem login da revisão final registrada em `CIC-03`. Nenhuma edição da v2
após a aprovação. SC-004 atendido pelos três traces de `CIC-03` (T032), além dos de
`CIC-01` e `CIC-02`.

### Registro histórico — aprovação em CIC-02 (substituída)

**Aprovação em `CIC-02`** (C09/FR-009), 2026-10-19. Ciclos efetivamente executados: **2**.
`CIC-01` foi aprovado; o autor decidiu abrir `CIC-02` pela margem estreita do F1-Score,
com problema e hipótese registrados antes da edição. `CIC-02` foi aprovado com experimento
completo, estável e vinculado à revisão `25b881d1…5e15`, cinco médias e média geral ≥ 0.8
(menor média 0.8416) e decisão do contrato igual à do avaliador. Ciclos 03–05 não foram
executados: C09 proíbe ciclos só para completar a contagem de 3–5. Gate de custo não
acionado (acumulado US$ 0,484720 ≤ US$ 4). Repetições por falha de infraestrutura: nenhuma.

Limitações registradas: notas individuais abaixo de 0.8 em cinco exemplos de `CIC-02`
(menor F1 #10 0.6462, Clarity/Precision de #1 0.70); número inventado (“1 segundo”) no
trace #10; temperatura 0 não garante determinismo e cada revisão foi avaliada uma única vez
(D09). Qualquer edição futura da v2 reabre um ciclo completo (FR-010).

#### Correspondência final de CIC-02 — SC-005 (T031)

2026-10-19: YAML local (`5222d484…7857` / `7ba746eb…5702`, commit `c40f511…`, sem
alterações pendentes), HEAD do Hub (`25b881d1…5e15`, lido no gate e na auditoria) e
`lc_hub_commit_hash` dos 15 runs do experimento aprovado `c7d175e1…1666` são a mesma
revisão. Inspeção sem login da revisão final registrada em `CIC-02`. Nenhuma edição da v2
após a aprovação. SC-004 atendido pelos três traces de `CIC-02` (T032), além dos de `CIC-01`.

### Registro histórico — aprovação antecipada em CIC-01 (substituída)

**Aprovação antecipada (C09/FR-009)** em `CIC-01`, 2026-10-19. Ciclos efetivamente
executados: **1**. Justificativa: experimento completo (15 respostas, 75 notas válidas),
estável e vinculado à revisão `4278de75…9595`, com as cinco médias e a média geral
≥ 0.8 e decisão do contrato igual à do avaliador. O plano de 3–5 ciclos (constituição IV)
continua sendo o planejamento; o próprio contrato proíbe ciclos executados só para
completar a contagem e exige problema observado para cada ajuste. Gate de custo não
acionado (acumulado US$ 0,222376 ≤ US$ 4). Repetições por falha de infraestrutura: nenhuma.

Limitações registradas: F1-Score 0.8057 tem margem pequena sobre o limiar e o médio de
dificuldade `medium` ficou em 0.7809 nessa métrica; notas individuais abaixo de 0.8 em
seis exemplos (análise C07). Temperatura 0 não garante determinismo; uma nova execução
pode oscilar. Por D09, nenhuma reexecução foi feita para buscar resultado favorável, e
qualquer edição futura da v2 reabre um ciclo completo (FR-010).

#### Correspondência final de CIC-01 — SC-005 (T031)

2026-10-19: YAML local (`49ffb358…c46d` / `ab661782…b89c`, sem alterações pendentes),
HEAD do Hub (`4278de75…9595`, lido no gate e na auditoria) e `lc_hub_commit_hash` dos 15
runs do experimento aprovado são a mesma revisão. Inspeção da revisão final repetida sem
login no navegador integrado em 2026-10-19: botão “Log in”, badge Public, histórico com
um único commit `4278de75`, cinco tags (`bug-to-user-story`, `product-management`, `pt-br`,
`Few-shot Learning`, `Role Prompting`), System com persona e `## Exemplos`, User com
`{bug_report}`. Nenhuma edição da v2 após a aprovação. SC-004 atendido pelos três traces
de `CIC-01`, que é o experimento final (T032 não se aplica).

## Entrega à 006

Verificado no LangSmith nesta feature (workspace do autor, ainda **não público**):

- Dataset `mba-ia-pull-evaluation-prompt-eval`, ID `8c78638d-37a5-4175-9984-8db0e3473228`,
  15 exemplos idênticos ao JSONL (5/7/3). Não compartilhado: `share_dataset` e o registro do
  link pertencem à 006.
- Experimento final `fabiocsm-bug_to_user_story_v2-9c836e20`, ID
  `d864cfbb-6ab9-4901-ab06-62f68ccd96fc`, revisão
  `36a96c0540682ed6b8569487222b88e11d1889a3976b75fea83553dc662b696f`, `COND-001`.
  Médias: Helpfulness 0.8773, Correctness 0.8754, F1-Score 0.8474, Clarity 0.8513,
  Precision 0.9033; média geral 0.8709; aprovado.
- Traces do experimento final: #1 simple `01a1525d-899e-7711-835f-249803cf7318`, #10 medium
  `01a1525d-3ff5-7ae0-8915-df303b9a69b8`, #14 complex `01a1525d-0432-7f50-99c6-c059ec587aa2`.
- Histórico: `CIC-01` (`86196746-1c83-42cc-868b-6b57f977f19b`, `4278de75`) e `CIC-02`
  (`c7d175e1-0f37-4afe-9b2a-88e061b01666`, `25b881d1`), aprovados e substituídos; servem à
  comparação entre revisões.

Pendente na 006: acesso público ao dataset e aos experimentos (links privados de workspace
não bastam), screenshots das cinco notas e dos traces, seções `Técnicas Aplicadas (Fase 2)`,
`Resultados Finais` e `Como Executar` finais no README (incluindo as regras de critérios e de
valores da v2), comparação v1/v2 e push Git.
