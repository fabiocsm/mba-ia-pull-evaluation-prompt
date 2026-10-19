"""Contrato V01–V11: clientes sintéticos e I/O isolado, nunca a API ou .env real."""

import importlib.util
import logging
import os
from pathlib import Path
import socket
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import dotenv
from langchain_core.prompts import ChatPromptTemplate
from langsmith import utils as ls_utils
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SECRET = "segredo-sintetico-nao-publicar"
REVISION = "a" * 64


@pytest.fixture
def pull(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(os, "environ", {
        "LANGSMITH_API_KEY": SECRET, "LANGSMITH_PROJECT": "projeto-teste",
        "USERNAME_LANGSMITH_HUB": "handle-configurado", "LANGSMITH_TRACING": "true",
        "LLM_PROVIDER": "openai", "LLM_MODEL": "modelo-configurado",
        "EVAL_MODEL": "juiz-configurado", "OPENAI_API_KEY": SECRET,
    })
    def no_network(*args, **kwargs):
        raise AssertionError("Rede proibida nos testes offline")
    monkeypatch.setattr(socket.socket, "connect", no_network)
    # utils carrega dotenv ao importar: desabilitar antes de qualquer import local.
    real_load = dotenv.load_dotenv
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *a, **kw: False)
    monkeypatch.syspath_prepend(str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("pull_under_test", ROOT / "src/pull_prompts.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "DESTINATION", tmp_path / "prompts/bug_to_user_story_v1.yml")
    monkeypatch.setattr(module, "load_dotenv", real_load)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "  Você é um assistente.\nRelato: {bug_report}\n{{chaves literais}}\n\n"),
        ("human", " {bug_report} \n"),
    ])
    prompt.metadata = {"lc_hub_owner": "leonanluppi", "lc_hub_repo": "bug_to_user_story_v1",
                       "lc_hub_commit_hash": REVISION, "extra": {"bool": True, "n": 3.5}}
    prompt.tags = ["tag-do-template"]
    snapshot = {"description": "Descrição remota áé", "tags": ["remota"],
                "created_at": "2026-01-02T03:04:05+00:00", "last_commit_hash": "b" * 64,
                "extra": {"campo": [True, None, 42]}}
    repository = SimpleNamespace(model_dump=Mock(return_value=snapshot))
    client = Mock()
    client.pull_prompt.return_value = prompt
    client.get_prompt.return_value = repository
    factory = Mock(return_value=client)
    monkeypatch.setattr(module, "Client", factory)
    ls_utils.get_env_var.cache_clear()
    yield SimpleNamespace(module=module, prompt=prompt, snapshot=snapshot,
                          client=client, factory=factory, tmp=tmp_path)
    ls_utils.get_env_var.cache_clear()


def exported(pull):
    return yaml.safe_load(pull.module.DESTINATION.read_text(encoding="utf-8"))


def test_v01_cli_origin_flags_and_persistence(pull, capsys):
    assert pull.module.main() == 0
    pull.factory.assert_called_once_with()
    pull.client.pull_prompt.assert_called_once_with(
        "leonanluppi/bug_to_user_story_v1", include_model=False,
        skip_cache=True, dangerously_pull_public_prompt=True)
    pull.client.get_prompt.assert_called_once_with("leonanluppi/bug_to_user_story_v1")
    pull.client.get_prompt.return_value.model_dump.assert_called_once_with(mode="json")
    data = exported(pull)
    assert list(data) == ["bug_to_user_story_v1"]
    text = capsys.readouterr().out
    assert "persistido" in text and REVISION in text
    assert str(pull.module.DESTINATION) in text
    assert SECRET not in text
    assert not list(pull.module.DESTINATION.parent.glob("*.tmp"))


def test_v01_function_returns_bool(pull):
    assert pull.module.pull_prompts_from_langsmith() is True


def test_v02_exact_templates_unicode_whitespace_braces_and_duplicate_variable(pull):
    assert pull.module.main() == 0
    data = exported(pull)["bug_to_user_story_v1"]
    assert data["system_prompt"] == pull.prompt.messages[0].prompt.template
    assert data["user_prompt"] == pull.prompt.messages[1].prompt.template
    assert data["input_variables"] == pull.prompt.input_variables == ["bug_report"]
    rebuilt = ChatPromptTemplate.from_messages([
        ("system", data["system_prompt"]), ("human", data["user_prompt"])])
    assert rebuilt.input_variables == pull.prompt.input_variables
    assert data["version"] == "v1"
    assert data["source"]["template_metadata"] == pull.prompt.metadata
    assert data["source"]["template_tags"] == pull.prompt.tags


@pytest.mark.parametrize("optional", ["absent", "null", "present"])
def test_v03_optional_metadata_and_independent_latest(pull, optional):
    if optional == "absent":
        pull.snapshot.pop("description")
        pull.snapshot.pop("created_at")
    elif optional == "null":
        pull.snapshot["description"] = None
        pull.snapshot["created_at"] = None
    pull.prompt.tags = None
    assert pull.module.main() == 0
    data = exported(pull)["bug_to_user_story_v1"]
    source = data["source"]
    assert source["commit_hash"] == REVISION != pull.snapshot["last_commit_hash"]
    assert source["repository_metadata"] == pull.snapshot
    assert source["template_tags"] is None
    assert data["description"] == pull.snapshot.get("description")
    assert data["tags"] == pull.snapshot["tags"]
    if optional == "absent":
        assert "created_at" not in data
    else:
        assert data["created_at"] == pull.snapshot["created_at"]
    from datetime import datetime, timezone
    for name in ("retrieved_at", "repository_observed_at"):
        assert datetime.fromisoformat(source[name]).utcoffset() == timezone.utc.utcoffset(None)


@pytest.fixture(params=[False, True], ids=["ausente", "sentinela"])
def previous(pull, request):
    path = pull.module.DESTINATION
    if request.param:
        path.parent.mkdir(parents=True)
        path.write_text(
            "bug_to_user_story_v1:\n  system_prompt: 'original {bug_report}'\n"
            "  user_prompt: '{bug_report}'\n  version: v1\n", encoding="utf-8")
    return path.read_bytes() if path.exists() else None


def assert_failed(pull, previous, capsys, category=None, residue=False):
    assert pull.module.main() == 1
    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert SECRET not in text and "Traceback" not in text
    assert "persistido" not in text
    if category:
        assert category in text
    path = pull.module.DESTINATION
    assert (path.read_bytes() if path.exists() else None) == previous
    if not residue and path.parent.exists():
        assert not list(path.parent.glob(".pull-v1-*.tmp"))
    for artifact in path.parent.glob("*"):
        if artifact.is_file():
            assert SECRET not in artifact.read_text(encoding="utf-8")
    return text


REPRESENTATION_CASES = [
    "not-chat", "swapped", "extra-message", "placeholder", "multimodal",
    "parser", "partial", "optional", "input-types", "name", "validate-template",
    "kwargs", "inner-parser", "inner-partial", "inner-optional", "inner-types",
    "inner-metadata", "inner-tags", "inner-name", "inner-validate", "jinja", "mustache",
    "inner-variables", "variables", "empty-system", "empty-user", "metadata-null",
    "owner", "repo", "revision", "revision-invalid", "revision-short", "revision-upper",
    "template-tags",
]


@pytest.mark.parametrize("case", REPRESENTATION_CASES)
def test_v04_incompatible_representation(pull, previous, monkeypatch, capsys, case):
    from langchain_core.prompts.chat import HumanMessagePromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser
    p = pull.prompt
    inner = p.messages[0].prompt
    if case == "not-chat":
        pull.client.pull_prompt.return_value = object()
    elif case == "swapped":
        p.messages.reverse()
    elif case == "extra-message":
        p.messages.append(p.messages[0])
    elif case == "placeholder":
        p.messages[1] = MessagesPlaceholder("history")
    elif case == "multimodal":
        p.messages[1] = HumanMessagePromptTemplate.from_template([
            {"type": "text", "text": "{bug_report}"},
            {"type": "image_url", "image_url": "https://example.test/image.png"}])
    elif case == "parser":
        p.output_parser = StrOutputParser()
    elif case == "partial":
        p.partial_variables = {"bug_report": "preenchido"}
    elif case == "optional":
        p.optional_variables = ["bug_report"]
    elif case == "input-types":
        p.input_types = {"bug_report": str}
    elif case == "name":
        p.name = "nome-extra"
    elif case == "validate-template":
        p.validate_template = True
    elif case == "kwargs":
        p.messages[0].additional_kwargs = {"hidden": SECRET}
    elif case.startswith("inner-"):
        field, value = {
            "inner-parser": ("output_parser", StrOutputParser()),
            "inner-partial": ("partial_variables", {"bug_report": "valor"}),
            "inner-optional": ("optional_variables", ["bug_report"]),
            "inner-types": ("input_types", {"bug_report": str}),
            "inner-metadata": ("metadata", {"extra": 1}),
            "inner-tags": ("tags", ["extra"]), "inner-name": ("name", "extra"),
            "inner-validate": ("validate_template", True),
            "inner-variables": ("input_variables", ["outra"]),
        }[case]
        setattr(inner, field, value)
    elif case in ("jinja", "mustache"):
        inner.template_format = "jinja2" if case == "jinja" else "mustache"
    elif case == "variables":
        p.input_variables = ["outra"]
    elif case in ("empty-system", "empty-user"):
        p.messages[0 if case == "empty-system" else 1].prompt.template = " \n"
    elif case == "metadata-null":
        p.metadata = None
    elif case in ("revision-short", "revision-upper"):
        # Hash do Hub é SHA-256 completo em minúsculas; prefixos não identificam a revisão.
        p.metadata["lc_hub_commit_hash"] = "a" * 8 if case == "revision-short" else "A" * 64
    elif case in ("owner", "repo", "revision", "revision-invalid"):
        key = {"owner": "lc_hub_owner", "repo": "lc_hub_repo",
               "revision": "lc_hub_commit_hash", "revision-invalid": "lc_hub_commit_hash"}[case]
        p.metadata[key] = SECRET if case != "revision" else ""
    elif case == "template-tags":
        p.tags = "não é lista"
    text = assert_failed(pull, previous, capsys, "representação")
    assert "Campo:" in text
    pull.client.get_prompt.assert_not_called()


@pytest.mark.parametrize("kind", ["object", "tuple", "set", "date", "nan", "inf", "key", "cycle"])
@pytest.mark.parametrize("location", ["template", "repository"])
def test_v05_nonserializable_metadata(pull, previous, capsys, kind, location):
    from datetime import datetime
    cycle = []
    cycle.append(cycle)
    value = {"object": object(), "tuple": (1, 2), "set": {1}, "date": datetime.now(),
             "nan": float("nan"), "inf": float("inf"), "key": {1: "invalid"},
             "cycle": cycle}[kind]
    target = pull.prompt.metadata if location == "template" else pull.snapshot
    target["extra"] = value
    assert_failed(pull, previous, capsys, "representação")


@pytest.mark.parametrize("field,value", [("description", 1), ("tags", None),
                                         ("tags", [1]), ("created_at", 4),
                                         ("created_at", "não ISO")])
def test_v05_invalid_projection(pull, previous, capsys, field, value):
    pull.snapshot[field] = value
    assert_failed(pull, previous, capsys, "representação")


def test_v05_simple_extra_metadata_preserved_with_limitation(pull, capsys):
    assert pull.module.main() == 0
    assert exported(pull)["bug_to_user_story_v1"]["source"]["repository_metadata"] == pull.snapshot
    assert "historicidade" in capsys.readouterr().out


@pytest.mark.parametrize("variable", ["LANGSMITH_API_KEY", "LANGSMITH_PROJECT",
    "USERNAME_LANGSMITH_HUB", "LANGSMITH_TRACING", "LLM_PROVIDER", "LLM_MODEL",
    "EVAL_MODEL", "OPENAI_API_KEY"])
@pytest.mark.parametrize("value", [None, "", "  \t"])
def test_v06_missing_or_blank_configuration(pull, previous, capsys, variable, value):
    if value is None:
        os.environ.pop(variable)
    else:
        os.environ[variable] = value
    text = assert_failed(pull, previous, capsys, "configuração")
    assert variable in text
    pull.factory.assert_not_called()


def test_v06_exported_empty_value_wins_over_dotenv(pull, previous, capsys):
    (pull.tmp / ".env").write_text("LANGSMITH_API_KEY=dotenv-value\n", encoding="utf-8")
    os.environ["LANGSMITH_API_KEY"] = ""
    assert_failed(pull, previous, capsys, "configuração")
    assert os.environ["LANGSMITH_API_KEY"] == ""
    pull.factory.assert_not_called()


@pytest.mark.parametrize("variable,value", [("LLM_PROVIDER", "invalid"),
    ("LANGSMITH_TRACING", "false"), ("LANGSMITH_TRACING_V2", "false"),
    ("LANGCHAIN_TRACING_V2", "false"), ("LANGSMITH_TRACING_V2", "local")])
def test_v06_invalid_configuration_or_effective_tracing(pull, previous, capsys, variable, value):
    os.environ[variable] = value
    assert_failed(pull, previous, capsys, "configuração")
    pull.factory.assert_not_called()


def test_v06_google_key_required(pull, previous, capsys):
    os.environ["LLM_PROVIDER"] = "google"
    assert "GOOGLE_API_KEY" in assert_failed(pull, previous, capsys, "configuração")
    pull.factory.assert_not_called()


def test_v06_google_supported_without_inference(pull):
    os.environ["LLM_PROVIDER"] = "google"
    os.environ["GOOGLE_API_KEY"] = SECRET
    os.environ.pop("OPENAI_API_KEY")
    assert pull.module.main() == 0


@pytest.mark.parametrize("operation", ["client", "pull", "get"])
@pytest.mark.parametrize("error,category", [
    (ls_utils.LangSmithAuthError, "acesso"),
    (ls_utils.LangSmithNotFoundError, "origem ausente"),
    (ls_utils.LangSmithConnectionError, "indisponibilidade"),
    (ls_utils.LangSmithRateLimitError, "indisponibilidade"),
    (ls_utils.LangSmithAPIError, "indisponibilidade"),
    (RuntimeError, "inesperado"),
])
def test_v07_external_failures_sanitized(pull, previous, capsys, operation, error, category):
    target = {"client": pull.factory, "pull": pull.client.pull_prompt,
              "get": pull.client.get_prompt}[operation]
    def noisy(*args, **kwargs):
        print(SECRET)
        print(SECRET, file=sys.stderr)
        logging.getLogger("langsmith").error(SECRET)
        raise error(SECRET)
    target.side_effect = noisy
    assert_failed(pull, previous, capsys, category)


def test_v07_repository_missing(pull, previous, capsys):
    pull.client.get_prompt.return_value = None
    assert_failed(pull, previous, capsys, "repository_metadata")


@pytest.mark.parametrize("point", ["mkdir", "temporary", "save-false", "save-exception",
    "save-partial", "read", "different-data", "different-type", "rebuild", "replace", "cleanup"])
def test_v08_v11_io_failures(pull, previous, monkeypatch, capsys, point):
    m = pull.module
    def fail(*args, **kwargs):
        raise OSError(SECRET)
    if point == "mkdir":
        monkeypatch.setattr(Path, "mkdir", fail)
    elif point == "temporary":
        monkeypatch.setattr(m.tempfile, "NamedTemporaryFile", fail)
    elif point.startswith("save-") or point == "cleanup":
        def broken_save(data, filename):
            print(SECRET)
            print(SECRET, file=sys.stderr)
            if point in ("save-partial", "cleanup"):
                Path(filename).write_text("partial", encoding="utf-8")
            if point == "save-exception":
                raise OSError(SECRET)
            return False
        monkeypatch.setattr(m, "save_yaml", broken_save)
        if point == "cleanup":
            monkeypatch.setattr(Path, "unlink", fail)
    elif point == "read":
        monkeypatch.setattr(m.yaml, "safe_load", fail)
    elif point in ("different-data", "different-type"):
        real_load = m.yaml.safe_load
        def corrupt(stream):
            value = real_load(stream)
            if point == "different-data":
                value["bug_to_user_story_v1"]["system_prompt"] += "corrupt"
            else:
                value["bug_to_user_story_v1"]["source"]["template_metadata"]["extra"]["bool"] = 1
            return value
        monkeypatch.setattr(m.yaml, "safe_load", corrupt)
    elif point == "rebuild":
        def broken_rebuild(*args, **kwargs):
            raise ValueError(SECRET)
        monkeypatch.setattr(m.ChatPromptTemplate, "from_messages", broken_rebuild)
    elif point == "replace":
        monkeypatch.setattr(m.os, "replace", fail)
    text = assert_failed(pull, previous, capsys, "persistência", residue=point == "cleanup")
    # Releitura divergente é falha de representação, não de escrita em disco.
    expected = "representação" if point in ("different-data", "different-type") else "escrita"
    assert f"Falha [{expected}]" in text
    if point == "cleanup":
        assert "resíduo temporário" in text and "não é referência válida" in text
        assert len(list(m.DESTINATION.parent.glob(".pull-v1-*.tmp"))) == 1
