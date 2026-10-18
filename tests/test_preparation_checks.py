"""Offline regression coverage for the executable preparation instructions."""

import logging
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
from types import SimpleNamespace
import warnings

import langsmith
from langsmith import utils as langsmith_utils
import pytest


ROOT = Path(__file__).resolve().parents[1]
BLOCKS = [
    pytest.param("README.md", "required =", False, None, id="readme-config"),
    pytest.param("specs/001-preparar-experimentos/quickstart.md", "required =",
                 False, None, id="quickstart-config"),
    pytest.param("specs/001-preparar-experimentos/quickstart.md", "for role, factory",
                 True, "llm", id="quickstart-calls"),
    pytest.param("docs/preparacao.md", "class CheckFailure", False, "cli",
                 id="context-existing-traces"),
    pytest.param("docs/preparacao.md", "class CheckFailure", True, "cli",
                 id="context-new-calls"),
]


class ExternalBoundary(BaseException):
    """Stop a documented block at its first external operation, even inside try."""


@pytest.fixture
def isolated_preparation(monkeypatch, tmp_path):
    # Only dummy configuration is read; the real .env is never opened by a block.
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(os, "environ", {"PATH": os.defpath})
    monkeypatch.setattr(sys, "path", sys.path.copy())
    monkeypatch.setattr(warnings, "filters", warnings.filters.copy())
    monkeypatch.setattr(logging.root.manager, "disable", logging.root.manager.disable)
    (tmp_path / ".env").write_text(
        "LANGSMITH_API_KEY=dummy-langsmith-key\n"
        "OPENAI_API_KEY=dummy-openai-key\n"
        "LANGSMITH_PROJECT=mba-ia-pull-evaluation-prompt\n"
        "USERNAME_LANGSMITH_HUB=fabiocsm\n"
        "LANGSMITH_TRACING=true\n"
        "LLM_PROVIDER=openai\n"
        "LLM_MODEL=gpt-4.1-2025-04-14\n"
        "EVAL_MODEL=gpt-4.1-2025-04-14\n",
        encoding="utf-8",
    )
    calls = []

    def boundary(name):
        def stop(*args, **kwargs):
            calls.append(name)
            raise ExternalBoundary(name)
        return stop

    monkeypatch.setattr(subprocess, "run", boundary("cli"))
    monkeypatch.setattr(langsmith, "Client", boundary("sdk"))
    monkeypatch.setattr(socket, "create_connection", boundary("network"))
    monkeypatch.setattr(socket.socket, "connect", boundary("network"))
    monkeypatch.setitem(sys.modules, "utils", SimpleNamespace(
        get_llm=boundary("llm"), get_eval_llm=boundary("llm")))
    langsmith_utils.get_env_var.cache_clear()
    yield calls
    langsmith_utils.get_env_var.cache_clear()


def execute_block(path, marker, fresh):
    document = (ROOT / path).read_text(encoding="utf-8")
    blocks = re.findall(r"^[^\n]*python - <<'PY'\n(.*?)^PY$", document,
                        flags=re.MULTILINE | re.DOTALL)
    selected = [block for block in blocks if marker in block]
    if len(selected) != 1:
        raise ValueError("Expected exactly one documented preparation block")
    os.environ["PREPARACAO_NOVAS_CHAMADAS"] = "1" if fresh else "0"
    exec(compile(selected[0], path, "exec"), {"__name__": "__main__"})


@pytest.mark.parametrize("path,marker,fresh,first_call", BLOCKS)
@pytest.mark.parametrize("variable,value", [
    ("LANGSMITH_TRACING", "false"),
    ("LANGSMITH_TRACING_V2", "false"),
    ("LANGCHAIN_TRACING_V2", "false"),
    ("LANGSMITH_TRACING_V2", "local"),
])
def test_disabled_effective_tracing_stops_before_external_work(
        path, marker, fresh, first_call, variable, value,
        isolated_preparation, capsys):
    # Prime an enabled cache before the exported override and dotenv loading.
    os.environ["LANGSMITH_TRACING"] = "true"
    assert langsmith_utils.tracing_is_enabled() is True
    os.environ.pop("LANGSMITH_TRACING")
    os.environ[variable] = value
    with pytest.raises((AssertionError, SystemExit)) as failure:
        execute_block(path, marker, fresh)
    output = capsys.readouterr().out
    if isinstance(failure.value, SystemExit):
        assert failure.value.code == 1
        assert '"causa": "tracing_desabilitado"' in output
    assert "dummy-langsmith-key" not in output
    assert "dummy-openai-key" not in output
    assert isolated_preparation == []


@pytest.mark.parametrize("path,marker,fresh,first_call", BLOCKS)
@pytest.mark.parametrize("prime_disabled_cache", [False, True])
def test_effective_tracing_from_dotenv_allows_valid_configuration(
        path, marker, fresh, first_call, prime_disabled_cache, isolated_preparation):
    if prime_disabled_cache:
        assert langsmith_utils.tracing_is_enabled() is False
    if first_call:
        with pytest.raises(ExternalBoundary, match=first_call):
            execute_block(path, marker, fresh)
        assert isolated_preparation == [first_call]
    else:
        execute_block(path, marker, fresh)
        assert isolated_preparation == []
