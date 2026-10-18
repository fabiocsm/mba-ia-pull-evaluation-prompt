"""Recupere a semente do desafio sem alterar seu conteúdo ou a cópia anterior."""

import os
import sys
import io
import json
import logging
import math
import re
import tempfile
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

import yaml
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.prompts.chat import (
    HumanMessagePromptTemplate, SystemMessagePromptTemplate,
)
from langsmith import Client
from langsmith import utils as ls_utils

from utils import check_env_vars, print_section_header, save_yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "leonanluppi/bug_to_user_story_v1"
DESTINATION = ROOT / "prompts/bug_to_user_story_v1.yml"


class RepresentationError(Exception):
    """Campo conhecido que não pode ser preservado pelo contrato YAML."""


@contextmanager
def _quiet_external_output():
    """Descarte diagnósticos externos que podem conter credenciais ou corpo HTTP."""
    previous = logging.root.manager.disable
    try:
        logging.disable(logging.CRITICAL)
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            yield
    finally:
        logging.disable(previous)


def _configuration_ready():
    load_dotenv(ROOT / ".env", override=False)
    required = ["LANGSMITH_API_KEY", "LANGSMITH_PROJECT", "USERNAME_LANGSMITH_HUB",
                "LANGSMITH_TRACING", "LLM_PROVIDER", "LLM_MODEL", "EVAL_MODEL"]
    present = check_env_vars(required)
    blank = [name for name in required if not os.getenv(name, "").strip()]
    if not present or blank:
        print("Falha [configuração]: configure variáveis não vazias: " + ", ".join(blank))
        return False
    provider = os.environ["LLM_PROVIDER"].lower()
    if provider not in ("openai", "google"):
        print("Falha [configuração]: configure LLM_PROVIDER como openai ou google.")
        return False
    key = "OPENAI_API_KEY" if provider == "openai" else "GOOGLE_API_KEY"
    if not check_env_vars([key]) or not os.getenv(key, "").strip():
        print("Falha [configuração]: configure variável não vazia: " + key)
        return False
    ls_utils.get_env_var.cache_clear()
    if (os.environ["LANGSMITH_TRACING"].lower() != "true"
            or ls_utils.tracing_is_enabled() is not True):
        print("Falha [configuração]: habilite LANGSMITH_TRACING e confira seus aliases.")
        return False
    return True


def _require(condition, field):
    # field é sempre um rótulo estático local, nunca texto de uma resposta externa.
    if not condition:
        raise RepresentationError(field)


def _plain_data(value, ancestors=None):
    """Aceite apenas dados simples, finitos e sem ciclos, sem coerção de valores."""
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float:
        _require(math.isfinite(value), "metadados: número não finito")
        return
    _require(type(value) in (dict, list), "metadados: tipo não serializável")
    ancestors = set() if ancestors is None else ancestors
    _require(id(value) not in ancestors, "metadados: ciclo")
    ancestors.add(id(value))
    try:
        if isinstance(value, dict):
            _require(all(type(k) is str for k in value), "metadados: chaves não textuais")
            values = value.values()
        else:
            values = value
        for item in values:
            _plain_data(item, ancestors)
    finally:
        ancestors.remove(id(value))


def _default_options(obj, expected_type, preserved, field):
    _require(type(obj) is expected_type, field + ": tipo")
    _require(not obj.model_extra, field + ": campos extras")
    for name, info in expected_type.model_fields.items():
        if name not in preserved:
            _require(getattr(obj, name) == info.get_default(call_default_factory=True),
                     field + ": opções internas")


def _extract_templates(prompt):
    _default_options(prompt, ChatPromptTemplate,
                     {"messages", "input_variables", "metadata", "tags"}, "template")
    _require(prompt.input_variables == ["bug_report"], "input_variables")
    _require(len(prompt.messages) == 2, "messages: quantidade")
    texts = []
    for message, expected, field in zip(
            prompt.messages, (SystemMessagePromptTemplate, HumanMessagePromptTemplate),
            ("system_prompt", "user_prompt")):
        _default_options(message, expected, {"prompt"}, field)
        _default_options(message.prompt, PromptTemplate,
                         {"template", "input_variables"}, field + ".prompt")
        text = message.prompt.template
        _require(type(text) is str and bool(text.strip()), field + ": texto vazio")
        # Reconstruir sem format/invoke detecta variáveis declaradas inconsistentes.
        rebuilt = PromptTemplate.from_template(text)
        _require(rebuilt.input_variables == message.prompt.input_variables,
                 field + ": variáveis internas")
        texts.append(text)
    _require(type(prompt.metadata) is dict, "template_metadata")
    _plain_data(prompt.metadata)
    _plain_data(prompt.tags)
    _require(prompt.tags is None or (type(prompt.tags) is list
             and all(type(tag) is str for tag in prompt.tags)), "template_tags")
    owner, repo = SOURCE.split("/")
    _require(prompt.metadata.get("lc_hub_owner") == owner, "lc_hub_owner")
    _require(prompt.metadata.get("lc_hub_repo") == repo, "lc_hub_repo")
    revision = prompt.metadata.get("lc_hub_commit_hash")
    _require(type(revision) is str and bool(re.fullmatch(r"[0-9a-fA-F]+", revision)),
             "lc_hub_commit_hash")
    return texts, revision


def _export_mapping(prompt, texts, revision, snapshot, retrieved_at, observed_at):
    _plain_data(snapshot)
    _require(type(snapshot) is dict, "repository_metadata")
    description = snapshot.get("description")
    _require(description is None or type(description) is str, "description")
    tags = snapshot.get("tags", [])
    _require(type(tags) is list and all(type(tag) is str for tag in tags), "tags")
    data = {
        "system_prompt": texts[0], "user_prompt": texts[1], "version": "v1",
        "input_variables": list(prompt.input_variables), "description": description,
        "tags": tags,
        "source": {
            "identifier": SOURCE, "commit_hash": revision, "retrieved_at": retrieved_at,
            "template_metadata": prompt.metadata, "template_tags": prompt.tags,
            "repository_observed_at": observed_at, "repository_metadata": snapshot,
        },
    }
    if "created_at" in snapshot:
        created = snapshot["created_at"]
        _require(created is None or type(created) is str, "created_at")
        if created is not None:
            try:
                datetime.fromisoformat(created.replace("Z", "+00:00"))
            except ValueError:
                raise RepresentationError("created_at: formato ISO 8601") from None
        data["created_at"] = created
    return {"bug_to_user_story_v1": data}


def _verify_temporary(temporary, expected):
    with temporary.open("r", encoding="utf-8") as stream:
        actual = yaml.safe_load(stream)
    _plain_data(actual)
    # JSON distingue, por exemplo, True de 1, que igualdade Python equipara.
    _require(json.dumps(actual, sort_keys=True, ensure_ascii=False)
             == json.dumps(expected, sort_keys=True, ensure_ascii=False),
             "releitura: dados divergentes")
    data = actual["bug_to_user_story_v1"]
    rebuilt = ChatPromptTemplate.from_messages([
        ("system", data["system_prompt"]), ("human", data["user_prompt"])])
    _require(rebuilt.input_variables == data["input_variables"], "reconstrução: variáveis")
    _require(rebuilt.messages[0].prompt.template == data["system_prompt"]
             and rebuilt.messages[1].prompt.template == data["user_prompt"],
             "reconstrução: mensagens")


def _persist(mapping):
    temporary = None
    try:
        DESTINATION.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=DESTINATION.parent, prefix=".pull-v1-",
                                         suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
        with _quiet_external_output():
            saved = save_yaml(mapping, str(temporary))
        if saved is not True:
            raise OSError("save_yaml")
        _verify_temporary(temporary, mapping)
        os.replace(temporary, DESTINATION)
        temporary = None  # Commit concluído: nenhuma validação obrigatória depois.
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except Exception:
                print("Aviso [limpeza]: resíduo temporário .pull-v1-*.tmp no diretório "
                      "de destino; não é referência válida. Remova-o antes de repetir.")


def _report_failure(error, stage, revision):
    if stage == "persistência":
        category, action = "escrita", "Confira permissões, espaço e integridade da gravação."
    elif isinstance(error, RepresentationError):
        category, action = "representação", "Confira o contrato; não adapte a semente."
    elif isinstance(error, ls_utils.LangSmithAuthError):
        category, action = "acesso", "Confira credencial, endpoint e workspace."
    elif isinstance(error, ls_utils.LangSmithNotFoundError):
        category, action = "origem ausente", "Confira a disponibilidade da origem obrigatória."
    elif isinstance(error, (ls_utils.LangSmithConnectionError, ls_utils.LangSmithAPIError,
                            ls_utils.LangSmithRateLimitError, TimeoutError, ConnectionError)):
        category, action = "indisponibilidade", "Confira a conexão e tente novamente depois."
    else:
        category, action = "inesperado", "Confira ambiente e versões antes de repetir."
    field = f" Campo: {error.args[0]}." if isinstance(error, RepresentationError) else ""
    known_revision = f" Revisão recuperada (não persistida): {revision}." if revision else ""
    print(f"Falha [{category}]; etapa {stage}.{field} Origem {SOURCE}; "
          f"destino {DESTINATION}.{known_revision} {action} "
          "A cópia anterior foi preservada; sem cópia anterior, o destino permanece ausente.")


def pull_prompts_from_langsmith():
    """Retorne True somente após a persistência completa da referência."""
    stage = "configuração"
    revision = None
    try:
        if not _configuration_ready():
            return False
        stage = "acesso/pull"
        with _quiet_external_output():
            client = Client()
            prompt = client.pull_prompt(SOURCE, include_model=False, skip_cache=True,
                                        dangerously_pull_public_prompt=True)
        retrieved_at = datetime.now(timezone.utc).isoformat()
        stage = "representação"
        texts, revision = _extract_templates(prompt)
        stage = "acesso/metadados"
        with _quiet_external_output():
            repository = client.get_prompt(SOURCE)
        observed_at = datetime.now(timezone.utc).isoformat()
        _require(repository is not None, "repository_metadata: ausente")
        stage = "representação"
        snapshot = repository.model_dump(mode="json")
        mapping = _export_mapping(prompt, texts, revision, snapshot, retrieved_at, observed_at)
        stage = "persistência"
        _persist(mapping)
    except Exception as error:
        _report_failure(error, stage, revision)
        return False
    print(f"Prompt persistido: {SOURCE}; revisão {revision}; destino {DESTINATION}")
    print("Aviso [metadados]: snapshot do repositório observado separadamente; "
          "campos adicionais preservados em source.repository_metadata, "
          "sem garantia de historicidade na revisão das mensagens.")
    return True


def main():
    """Converta o resultado da recuperação em código de processo 0/1."""
    print_section_header("Recuperação do prompt original")
    return 0 if pull_prompts_from_langsmith() else 1


if __name__ == "__main__":
    sys.exit(main())
