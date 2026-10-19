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

Pendente.

### CIC-02

Pendente.

### CIC-03

Pendente.

### CIC-04

Pendente.

### CIC-05

Pendente.

## Comparação dos ciclos

Pendente.

## Decisão de parada

Pendente.

## Entrega à 006

Pendente.
