"""Valida, publica e confere a revisão pública da v2, sem executar modelos."""

from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import parse_qs, urlsplit
from uuid import UUID

from dotenv import load_dotenv
from langchain_core.load import dumps
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client
from langsmith.utils import LangSmithConflictError, get_env_var, get_host_url, tracing_is_enabled
import requests
import yaml

from utils import check_env_vars, load_yaml, validate_prompt_structure

ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = ROOT / 'prompts/bug_to_user_story_v2.yml'
NAME = 'bug_to_user_story_v2'
TEXT_FIELDS = ('description', 'system_prompt', 'user_prompt', 'version')
LIST_FIELDS = ('tags', 'techniques_applied')
PENDING = re.compile(r'\b(?:TODO|FIXME|TBD)\b|\[\s*(?i:TODO|FIXME|TBD)\s*\]')
REPORTS = ('A legenda permanece visível.', '', '{"status":"erro"}; {literal}')
PERSONA = re.compile(r'\bvocê é (?:um|uma)\b[^.\n]{0,40}?\b(?:product manager|product owner|pm|'
                     r'analista de produto)\b', re.I)


def _text_values(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from _text_values(key)
            yield from _text_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _text_values(child)


def _template(data):
    template = ChatPromptTemplate.from_messages([
        ('system', data['system_prompt']), ('user', data['user_prompt']),
    ])
    if (template.input_variables != ['bug_report'] or template.partial_variables
            or template.optional_variables or template.messages[0].prompt.input_variables):
        raise ValueError('template')
    reference = None
    for report in REPORTS:
        messages = template.format_messages(bug_report=report)
        if ([m.type for m in messages] != ['system', 'human']
                or messages[1].content != report):
            raise ValueError('renderização')
        if reference is not None and messages[0].content != reference:
            raise ValueError('System variável')
        reference = messages[0].content
    return template


def _content_errors(system):
    errors = []
    instructions = system.split('## Exemplos', 1)[0]
    if not PERSONA.search(instructions):
        errors.append('system_prompt: persona ausente das regras')
    text = instructions.casefold()
    if (not all(term in text for term in ('português', 'markdown', 'como', 'eu quero',
                'para que', 'critérios de aceitação', 'verificáveis'))
            or not re.search(r'como\b[^\n]*eu quero\b[^\n]*para que\b', text)):
        errors.append('system_prompt: formato incompleto nas regras')
    try:
        if system.count('## Exemplos\n') != 1:
            raise ValueError()
        blocks = re.split(r'^### Exemplo (\d+)\s*$', system.split('## Exemplos\n')[1], flags=re.M)
        ids = [int(n) for n in blocks[1::2]]
        if not 2 <= len(ids) <= 3 or ids != list(range(1, len(ids) + 1)):
            raise ValueError()
        entries = []
        for block in blocks[2::2]:
            if block.count('#### Entrada\n') != 1 or block.count('#### Saída\n') != 1:
                raise ValueError()
            match = re.fullmatch(r'\s*#### Entrada\n(.*?)\n#### Saída\n(.*)', block, re.S)
            if not match:
                raise ValueError()
            entry, output = [part.strip() for part in match.groups()]
            if not entry or not output or entry in {'...', '…'} or output in {'...', '…'}:
                raise ValueError()
            if '**Informação insuficiente**' in output:
                if '**Esclarecimentos necessários**' not in output or '?' not in output:
                    raise ValueError()
            elif (not re.search(r'Como\b[^\n]+eu quero\b[^\n]+para que\b[^\n]+', output)
                  or '**Critérios de aceitação**' not in output
                  or not re.search(r'^\s*- .+', output, re.M)):
                raise ValueError()
            entries.append(entry)
        if len(set(entries)) != len(entries):
            raise ValueError()
    except (ValueError, IndexError):
        errors.append('system_prompt: Few-shot exige 2–3 exemplos completos e distintos')
    return errors


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """Validação pura do contrato local; não altera dados nem consulta serviços."""
    if not isinstance(prompt_data, dict):
        return False, ['definição deve ser mapping']
    errors = []
    if set(prompt_data) - set(TEXT_FIELDS + LIST_FIELDS):
        errors.append('campos inesperados na definição')
    for field in TEXT_FIELDS:
        value = prompt_data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f'{field}: string não branca obrigatória')
    for field in LIST_FIELDS:
        value = prompt_data.get(field)
        if (not isinstance(value, list) or not value
                or not all(isinstance(item, str) and item.strip() for item in value)):
            errors.append(f'{field}: lista de strings não brancas obrigatória')
    if errors:
        return False, errors
    if any(PENDING.search(text) for text in _text_values(prompt_data)):
        errors.append('marcador de pendência na definição')
    if errors:
        return False, errors
    if prompt_data['version'] != 'v2':
        errors.append('version deve ser v2')
    if prompt_data['user_prompt'] != '{bug_report}':
        errors.append('user_prompt deve ser exatamente {bug_report}')
    names = [name.strip().casefold() for name in prompt_data['techniques_applied']]
    if len(names) != len(set(names)) or len(names) < 2 or 'few-shot learning' not in names:
        errors.append('techniques_applied: pelo menos duas distintas, incluindo Few-shot Learning')
    try:
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            result = validate_prompt_structure(prompt_data)
        if (not isinstance(result, tuple) or len(result) != 2
                or type(result[0]) is not bool or not isinstance(result[1], list)
                or not all(isinstance(e, str) and e.strip() for e in result[1])
                or result[0] != (not result[1])):
            errors.append('helper: retorno inválido ou incoerente')
        else:
            remaining = [e for e in result[1] if not (
                e == 'system_prompt ainda contém TODOs'
                and not PENDING.search(prompt_data['system_prompt']))]
            if remaining:
                errors.append('helper: estrutura rejeitada')
    except Exception:
        errors.append('helper: falha na validação')
    errors.extend(_content_errors(prompt_data['system_prompt']))
    try:
        _template(prompt_data)
    except Exception:
        errors.append('template: mensagens, variáveis ou chaves incompatíveis')
    return not errors, errors


def _definition_hash(data):
    canonical = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def _tags(data):
    result, seen = [], set()
    for tag in data['tags'] + data['techniques_applied']:
        key = tag.strip().casefold()
        if key not in seen:
            result.append(tag)
            seen.add(key)
    return result


def _configuration():
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        load_dotenv(ROOT / '.env', override=False)
    provider = os.getenv('LLM_PROVIDER', '').strip().lower()
    required = ['LANGSMITH_API_KEY', 'LANGSMITH_PROJECT', 'USERNAME_LANGSMITH_HUB',
                'LANGSMITH_TRACING', 'LLM_PROVIDER', 'LLM_MODEL', 'EVAL_MODEL']
    if provider not in {'openai', 'google'}:
        raise ValueError('provider')
    required.append('OPENAI_API_KEY' if provider == 'openai' else 'GOOGLE_API_KEY')
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        present = check_env_vars(required)
    if not present or any(not os.getenv(key, '').strip() for key in required):
        raise ValueError('configuração ausente')
    handle = os.environ['USERNAME_LANGSMITH_HUB']
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', handle):
        raise ValueError('handle inválido')
    get_env_var.cache_clear()
    if os.environ['LANGSMITH_TRACING'].strip().lower() != 'true' or tracing_is_enabled() is not True:
        raise ValueError('tracing desabilitado')
    endpoint = os.getenv('LANGSMITH_ENDPOINT', 'https://api.smith.langchain.com').rstrip('/')
    parts = urlsplit(endpoint)
    if (parts.scheme != 'https' or not parts.hostname or parts.username or parts.password
            or parts.query or parts.fragment or parts.path or parts.port not in (None, 443)):
        raise ValueError('endpoint inválido')
    workspace = os.getenv('LANGSMITH_WORKSPACE_ID', '')
    if workspace:
        UUID(workspace)
    return handle, endpoint, workspace


def _revision_prefix(url, endpoint, handle, workspace):
    if not isinstance(url, str) or not url:
        raise ValueError('URL ausente')
    parts = urlsplit(url)
    # Mesmo host que o SDK usa para montar a URL devolvida pelo push (inclui EU/AWS/APAC).
    host = urlsplit(get_host_url(None, endpoint)).hostname
    if (parts.scheme != 'https' or parts.hostname != host or parts.port not in (None, 443)
            or parts.username or parts.password or parts.fragment):
        raise ValueError('URL incompatível')
    query = parse_qs(parts.query, keep_blank_values=True)
    if parts.query and (set(query) != {'organizationId'} or query['organizationId'] != [workspace]):
        raise ValueError('parâmetros inesperados')
    match = re.fullmatch(r'/prompts/' + NAME + r'/([a-f0-9]{8,64})', parts.path)
    if not match:
        match = re.fullmatch(r'/hub/' + re.escape(handle) + '/' + NAME + r':([a-f0-9]{8,64})', parts.path)
    if not match:
        raise ValueError('revisão ausente ou destino incompatível')
    return match[1]


def _repo_snapshot(repo, destination, data, commit):
    def field(key):
        return repo.get(key) if isinstance(repo, dict) else getattr(repo, key, None)
    owner, name = destination.split('/')
    expected = dict(owner=owner, repo_handle=name, full_name=destination,
                    description=data['description'], is_public=True, last_commit_hash=commit)
    if any(field(key) != value for key, value in expected.items()) or field('is_public') is not True:
        raise ValueError('repositório divergente')
    tags = field('tags')
    expected_tags = set(_tags(data))
    if (not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags)
            or not expected_tags.issubset(set(tags))
            or set(tags) - expected_tags - {'ChatPromptTemplate'}):
        raise ValueError('tags divergentes')
    return dict(expected, tags=tags, observed_at=datetime.now(timezone.utc).isoformat())


def _compare_template(remote, local, handle, commit):
    if not isinstance(remote, ChatPromptTemplate):
        raise ValueError('tipo remoto incompatível')
    if (len(remote.messages) != 2 or remote.input_variables != ['bug_report']
            or remote.optional_variables or remote.partial_variables):
        raise ValueError('entrada remota divergente')
    for actual, expected in zip(remote.messages, local.messages):
        if type(actual) is not type(expected) or actual.prompt != expected.prompt:
            raise ValueError('mensagens divergentes')
    expected_metadata = dict(local.metadata, lc_hub_owner=handle, lc_hub_repo=NAME,
                             lc_hub_commit_hash=commit)
    if remote.metadata != expected_metadata:
        raise ValueError('metadados do commit divergentes')
    for report in REPORTS:
        if remote.format_messages(bug_report=report) != local.format_messages(bug_report=report):
            raise ValueError('renderização divergente')


def _anonymous(endpoint, destination, data, commit, manifest):
    urls = [f'{endpoint}/repos/{destination}', f'{endpoint}/commits/{destination}/{commit}']
    session = requests.Session()
    session.trust_env = False
    try:
        if session.auth or session.cookies:
            raise ValueError('sessão anônima incompatível')
        for index, url in enumerate(urls):
            response = session.get(url, timeout=(10, 30), allow_redirects=False)
            if any(key.lower() in {'authorization', 'x-api-key', 'cookie'} for key in response.request.headers):
                raise ValueError('request não anônimo')
            if response.status_code != 200:
                raise ValueError('HTTP anônimo negado')
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError('JSON incompatível')
            if index == 0:
                _repo_snapshot(payload.get('repo'), destination, data, commit)
            elif payload.get('commit_hash') != commit or payload.get('manifest') != manifest:
                raise ValueError('manifesto anônimo divergente')
        return urls
    finally:
        session.close()


def _publication_result(prompt_name: str, prompt_data: dict, local_file_sha256=None):
    """Publica uma vez e confere identidade, revisão fixa e leitura anônima."""
    valid, errors = validate_prompt(prompt_data)
    if prompt_name != NAME or not valid:
        print('Validação rejeitada: destino ou definição incompatível.')
        return None
    stage, publication = 'configuração', 'não iniciada'
    client = None
    definition_sha256 = _definition_hash(prompt_data)
    attempt = dict(local_definition_sha256=definition_sha256,
                   observed_at=datetime.now(timezone.utc).isoformat(), visual_inspection='pendente')
    if local_file_sha256 is not None:
        attempt['local_file_sha256'] = local_file_sha256
    try:
        handle, endpoint, workspace = _configuration()
        stage = 'contexto autenticado'
        client = Client(api_url=endpoint, api_key=os.environ['LANGSMITH_API_KEY'],
                        workspace_id=workspace or None, timeout_ms=(10000, 30000),
                        auto_batch_tracing=False)
        response = client.request_with_retries('GET', '/settings')
        response.raise_for_status()
        settings = response.json()
        if (settings.get('tenant_handle') != handle or not settings.get('id')
                or (workspace and settings['id'] != workspace)):
            raise ValueError('identidade divergente')
        workspace = settings['id']
        UUID(workspace)
        destination = f'{handle}/{NAME}'
        attempt.update(destination=destination, endpoint=endpoint, workspace_id=workspace)
        template = _template(prompt_data)
        template.metadata = dict(version=prompt_data['version'],
            techniques_applied=prompt_data['techniques_applied'].copy(),
            local_definition_sha256=definition_sha256)
        stage, publication = 'push', 'não confirmada; remoto pode ter mudado'
        options = dict(include_model=False, skip_cache=True, dangerously_pull_public_prompt=True)
        revision_source = 'push_return'
        try:
            returned_url = client.push_prompt(destination, object=template, is_public=True,
                description=prompt_data['description'], tags=_tags(prompt_data))
        except LangSmithConflictError:
            # O HEAD é candidato existente, jamais identidade atribuída ao próprio push.
            # Não repetir escrita. Todos os gates abaixo continuam obrigatórios.
            stage = 'revisão existente após conflito'
            candidate = client.get_prompt(destination)
            prefix = getattr(candidate, 'last_commit_hash', None)
            if not isinstance(prefix, str) or not re.fullmatch(r'[a-f0-9]{64}', prefix):
                raise ValueError('revisão existente ausente')
            returned_url = None
            revision_source = 'existing_after_conflict'
        else:
            stage = 'resolução da revisão'
            prefix = _revision_prefix(returned_url, endpoint, handle, workspace)
            publication = 'confirmada'
        attempt['returned_url'] = returned_url
        attempt['revision_source'] = revision_source
        fixed = client.pull_prompt_commit(f'{destination}:{prefix}', **options)
        commit = fixed.commit_hash
        if (not isinstance(commit, str) or not re.fullmatch(r'[a-f0-9]{64}', commit)
                or not commit.startswith(prefix) or fixed.owner != handle or fixed.repo != NAME
                or not isinstance(fixed.manifest, dict)):
            raise ValueError('hash ou identidade do commit divergente')
        attempt['commit_hash'] = commit
        stage = 'manifesto autenticado'
        if fixed.manifest != json.loads(dumps(template)):
            raise ValueError('manifesto autenticado divergente')
        stage = 'conteúdo e metadados do commit'
        remote = client.pull_prompt(f'{destination}:{commit}', **options)
        _compare_template(remote, template, handle, commit)
        stage = 'snapshot do repo'
        snapshot = _repo_snapshot(client.get_prompt(destination), destination, prompt_data, commit)
        stage = 'acesso público anônimo'
        urls = _anonymous(endpoint, destination, prompt_data, commit, fixed.manifest)
        stage = 'estabilidade final do repo'
        snapshot = _repo_snapshot(client.get_prompt(destination), destination, prompt_data, commit)
        if revision_source == 'existing_after_conflict':
            publication = 'revisão existente conferida; push em conflito'
        summary = dict(observed_at=datetime.now(timezone.utc).isoformat(), destination=destination,
            endpoint=endpoint, workspace_id=workspace, local_definition_sha256=definition_sha256,
            commit_hash=commit, returned_url=returned_url, public_urls=urls, repo_snapshot=snapshot,
            publication=publication, revision_source=revision_source, content='conferido', metadata='conferido', public_access='conferido',
            visual_inspection='pendente')
        if local_file_sha256 is not None:
            summary['local_file_sha256'] = local_file_sha256
        return summary
    except Exception as error:
        print(f'Publicação {publication}; conferência pendente/divergente; etapa={stage}.')
        status = getattr(getattr(error, 'response', None), 'status_code', None)
        attempt.update(publication=publication, verification='pendente/divergente', stage=stage,
                       error_category=type(error).__name__,
                       http_status=status if type(status) is int else None)
        print(json.dumps(attempt, ensure_ascii=False, sort_keys=True))
        return None
    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass


def _report(summary):
    print('Revisão conferida automaticamente; inspeção visual e registro obrigatórios para aceite da 004.')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """True somente após publicação e todas as conferências automatizadas."""
    summary = _publication_result(prompt_name, prompt_data)
    if summary is None:
        return False
    _report(summary)
    return True


def main():
    """Valida uma leitura estável e associa seus dois hashes à revisão conferida."""
    try:
        original = PROMPT_PATH.read_bytes()
        original.decode('utf-8')
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            data = load_yaml(str(PROMPT_PATH))
            if data != yaml.safe_load(original):
                raise ValueError('conteúdo carregado divergente dos bytes originais')
        if PROMPT_PATH.read_bytes() != original:
            raise ValueError('arquivo alterado')
    except Exception:
        print('Validação rejeitada: arquivo ausente, ilegível, inválido ou alterado na leitura.')
        return 1
    if data is None:
        print('Validação rejeitada: YAML inválido ou vazio.')
        return 1
    if not isinstance(data, dict) or set(data) != {NAME} or not isinstance(data[NAME], dict):
        print('Validação rejeitada: raiz deve conter somente a definição v2 mapping.')
        return 1
    valid, errors = validate_prompt(data[NAME])
    if not valid:
        print('Validação rejeitada: ' + '; '.join(errors))
        return 1
    file_sha256 = hashlib.sha256(original).hexdigest()
    summary = _publication_result(NAME, data[NAME], file_sha256)
    if summary is None:
        return 1
    try:
        if PROMPT_PATH.read_bytes() != original:
            raise ValueError('arquivo alterado')
    except Exception:
        print('Publicação confirmada; conferência local divergente; etapa=estabilidade final do arquivo. '
              'O remoto pode ter mudado; repetir o ciclo para os novos bytes.')
        summary.update(local_stability='divergente', stage='estabilidade final do arquivo')
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 1
    _report(summary)
    return 0


if __name__ == '__main__':
    sys.exit(main())
