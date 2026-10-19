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
`CIC-01` como avaliação da v2 da 003). Estado final: **aprovado** (regra integral C06).

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

**Em andamento** — aberto em 2026-10-19 por **decisão explícita do autor** após a aprovação de `CIC-01`:
a margem do F1-Score (0.8057, e 0.7809 nos casos `medium`) foi considerada pequena demais
para a entrega. Não é ciclo para completar contagem: há problema observado em `CIC-01`.
Pela FR-010, a edição da v2 torna o experimento de `CIC-01` `substituído` para fins de
entrega; o resultado de `CIC-01` permanece no histórico.

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

### CIC-03

**Não aplicável** — `CIC-03` não foi executado.

**Justificativa**: `CIC-01` foi aprovado pela regra integral (C06) com experimento completo e
estável. C09 e FR-009 determinam encerrar com justificativa e proíbem executar ciclos apenas
para completar a contagem de 3–5; nenhuma métrica ficou abaixo de 0.8, portanto não há
problema observado que fundamente uma hipótese de ajuste (C08/FR-007). Nenhuma edição da v2,
publicação ou experimento foi feito para este ciclo.


### CIC-04

**Não aplicável** — `CIC-04` não foi executado.

**Justificativa**: `CIC-01` foi aprovado pela regra integral (C06) com experimento completo e
estável. C09 e FR-009 determinam encerrar com justificativa e proíbem executar ciclos apenas
para completar a contagem de 3–5; nenhuma métrica ficou abaixo de 0.8, portanto não há
problema observado que fundamente uma hipótese de ajuste (C08/FR-007). Nenhuma edição da v2,
publicação ou experimento foi feito para este ciclo.


### CIC-05

**Não aplicável** — `CIC-05` não foi executado.

**Justificativa**: `CIC-01` foi aprovado pela regra integral (C06) com experimento completo e
estável. C09 e FR-009 determinam encerrar com justificativa e proíbem executar ciclos apenas
para completar a contagem de 3–5; nenhuma métrica ficou abaixo de 0.8, portanto não há
problema observado que fundamente uma hipótese de ajuste (C08/FR-007). Nenhuma edição da v2,
publicação ou experimento foi feito para este ciclo.


## Comparação dos ciclos

Todas as tentativas executadas, sem remoção de linhas. Uma única condição (`COND-001`).

| Ciclo | Condição | Revisão | Experimento | Helpfulness | Correctness | F1-Score | Clarity | Precision | Média geral | Completude | Decisão | Custo (US$) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CIC-01 | COND-001 | `4278de75` | `86196746-1c83-42cc-868b-6b57f977f19b` | 0.8687 | 0.8492 | 0.8057 | 0.8447 | 0.8927 | 0.8522 | 15 runs / 75 notas | aprovado | 0,222376 |
| CIC-02–05 | — | — | — | — | — | — | — | — | — | — | não aplicável | 0 |

Resumo das mudanças: nenhuma edição da v2 na 005; a revisão aprovada é a publicada na 004.
Não houve repetição por falha de infraestrutura nem experimento descartado. Comparação
numérica com a v1 não foi executada (opcional; exigiria experimento adicional e decisão
explícita do autor). A comparação qualitativa v1/v2 fica para a documentação da 006.

## Decisão de parada

**Reaberta** em 2026-10-19 pela abertura de `CIC-02` por decisão do autor. O registro abaixo é histórico e não é mais a decisão vigente.

### Registro anterior — aprovação antecipada em CIC-01

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
- Experimento final `fabiocsm-bug_to_user_story_v2-31a99eea`, ID
  `86196746-1c83-42cc-868b-6b57f977f19b`, revisão `4278de75a2fca03a17cc1e3ab9d66d552c2c1aaebe543a085a34772637fa9595`,
  `COND-001`. Médias: Helpfulness 0.8687, Correctness 0.8492, F1-Score 0.8057, Clarity
  0.8447, Precision 0.8927; média geral 0.8522; aprovado.
- Traces: #1 simple `01a15217-85ee-77f0-b508-18fea1259ad1`, #12 medium
  `01a15217-3f2f-7b30-88a4-4556de32786e`, #14 complex `01a15217-1929-79c1-856f-58ea0690a751`.

Pendente na 006: acesso público ao dataset e aos experimentos (links privados de workspace
não bastam), screenshots das cinco notas e dos traces, seções `Técnicas Aplicadas (Fase 2)`,
`Resultados Finais` e `Como Executar` finais no README, comparação v1/v2 e push Git.
