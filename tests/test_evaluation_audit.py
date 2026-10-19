"""Offline coverage for the executable evaluation blocks in docs/avaliacao-v2.md.

The blocks run against copies of the protected files in a temporary directory,
with a dummy .env, a fake LangSmith client, a fake Git and every LLM boundary
blocked. Nothing here is remote evidence; real scores only come from evaluate.py.
"""

from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import io
import json
import logging
import math
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
from types import SimpleNamespace
import uuid
import warnings

import langchain_google_genai
import langchain_openai
import langsmith
from langsmith import utils as langsmith_utils
import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "avaliacao-v2.md"
HUB = "4278de75a2fca03a17cc1e3ab9d66d552c2c1aaebe543a085a34772637fa9595"
OTHER_HUB = "1" * 64
WORKSPACE = "15dd5852-a835-4163-826c-e78668fd2a9c"
PROJECT = "mba-ia-pull-evaluation-prompt"
DATASET = PROJECT + "-eval"
V2 = "prompts/bug_to_user_story_v2.yml"
SECRETS = ("sentinela-langsmith-secreta", "sentinela-openai-secreta")
KEYS = ["helpfulness", "correctness", "f1_score", "clarity", "precision"]
COPIED = ["src/evaluate.py", "src/metrics.py", "src/utils.py",
          "datasets/bug_to_user_story.jsonl", "prompts/bug_to_user_story_v1.yml", V2,
          "docs/integridade-inicial.json", "docs/avaliacao-v2.md"]
DOTENV = {
    "LANGSMITH_API_KEY": SECRETS[0],
    "OPENAI_API_KEY": SECRETS[1],
    "LANGSMITH_PROJECT": PROJECT,
    "USERNAME_LANGSMITH_HUB": "fabiocsm",
    "LANGSMITH_TRACING": "true",
    "LLM_PROVIDER": "openai",
    "LLM_MODEL": "gpt-4.1-2025-04-14",
    "EVAL_MODEL": "gpt-4.1-2025-04-14",
}


class ExternalBoundary(BaseException):
    """Stop a block at an unexpected external operation, even inside try."""


class FakeClient:
    """In-memory LangSmith client; anything not modelled here is a boundary."""

    def __init__(self, calls):
        self.calls = calls
        self.writes = []
        self.datasets = []
        self.examples = {}
        self.prompt = SimpleNamespace(last_commit_hash=HUB, is_public=True)
        self.prompt_heads = []
        self.prompt_identifiers = []
        self.main_project = SimpleNamespace(id=str(uuid.uuid4()), name=PROJECT,
                                            tenant_id=WORKSPACE)
        self.named_projects = {PROJECT: self.main_project}
        self.workspace_id = WORKSPACE
        self.client_options = []
        self.projects = {}
        self.runs = {}
        self.feedback = []
        self.source_runs = {}
        self.fail_example_after = None

    def __getattr__(self, name):
        def boundary(*args, **kwargs):
            self.calls.append("sdk:" + name)
            self.writes.append(name)
            raise ExternalBoundary(name)
        return boundary

    def list_datasets(self, dataset_name=None, **kwargs):
        return iter([item for item in self.datasets
                     if dataset_name is None or item.name == dataset_name])

    def create_dataset(self, dataset_name, **kwargs):
        self.writes.append("create_dataset")
        dataset = SimpleNamespace(id=uuid.uuid4(), name=dataset_name,
                                  url="https://example.invalid/datasets/new")
        self.datasets.append(dataset)
        self.examples[str(dataset.id)] = []
        return dataset

    def create_example(self, dataset_id, inputs, outputs, **kwargs):
        self.writes.append("create_example")
        examples = self.examples[str(dataset_id)]
        if self.fail_example_after is not None and len(examples) >= self.fail_example_after:
            raise RuntimeError("falha simulada de transporte")
        examples.append(SimpleNamespace(id=uuid.uuid4(), inputs=inputs, outputs=outputs))

    def list_examples(self, dataset_id=None, **kwargs):
        return iter(list(self.examples.get(str(dataset_id), [])))

    def read_project(self, project_name=None, project_id=None, **kwargs):
        if project_id is not None:
            return self.projects[str(project_id)]
        if project_name not in self.named_projects:
            raise langsmith_utils.LangSmithNotFoundError("Projeto ausente")
        return self.named_projects[project_name]

    def create_project(self, project_name, *, upsert=False):
        assert upsert is False
        self.writes.append("create_project")
        if project_name in self.named_projects:
            raise langsmith_utils.LangSmithConflictError("Projeto existente")
        project = SimpleNamespace(id=str(uuid.uuid4()), name=project_name,
                                  tenant_id=self.workspace_id)
        self.named_projects[project_name] = project
        return project

    def list_projects(self, reference_dataset_id=None, **kwargs):
        return iter([item for item in self.projects.values()
                     if reference_dataset_id is None
                     or str(item.reference_dataset_id) == str(reference_dataset_id)])

    def get_prompt(self, identifier):
        self.prompt_identifiers.append(identifier)
        if self.prompt_heads:
            return SimpleNamespace(last_commit_hash=self.prompt_heads.pop(0),
                                   is_public=self.prompt.is_public)
        return self.prompt

    def list_runs(self, project_id=None, is_root=None, run_type=None, **kwargs):
        runs = self.runs.get(str(project_id), [])
        if is_root:
            runs = [run for run in runs if run.parent_run_id is None]
        if run_type:
            runs = [run for run in runs if run.run_type == run_type]
        return iter(list(runs))

    def list_feedback(self, run_ids=None, **kwargs):
        wanted = {str(run_id) for run_id in run_ids or []}
        return iter([item for item in self.feedback if str(item.run_id) in wanted])

    def read_run(self, run_id, **kwargs):
        return self.source_runs[str(run_id)]


@pytest.fixture
def audit(monkeypatch, tmp_path):
    for relative in COPIED:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    (tmp_path / "results").mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(os, "environ", {"PATH": os.defpath})
    monkeypatch.setattr(sys, "path", [str(tmp_path / "src"), *sys.path])
    monkeypatch.setattr(warnings, "filters", warnings.filters.copy())
    monkeypatch.setattr(logging.root.manager, "disable", logging.root.manager.disable)
    calls = []

    def boundary(name):
        def stop(*args, **kwargs):
            calls.append(name)
            raise ExternalBoundary(name)
        return stop

    git = SimpleNamespace(status="", head="a" * 40)

    def fake_run(args, *positional, **kwargs):
        command = list(args)
        if command == ["git", "status", "--porcelain", "--", V2]:
            return subprocess.CompletedProcess(command, 0, stdout=git.status, stderr="")
        if command == ["git", "rev-parse", "HEAD"]:
            return subprocess.CompletedProcess(command, 0, stdout=git.head + "\n", stderr="")
        calls.append("subprocess")
        raise ExternalBoundary("subprocess")

    client = FakeClient(calls)
    def fake_client(*args, **kwargs):
        client.client_options.append(kwargs)
        client.workspace_id = kwargs.get("workspace_id", WORKSPACE)
        return client

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(langsmith, "Client", fake_client)
    monkeypatch.setattr(socket, "create_connection", boundary("network"))
    monkeypatch.setattr(socket.socket, "connect", boundary("network"))
    monkeypatch.setattr(langchain_openai, "ChatOpenAI", boundary("llm"))
    monkeypatch.setattr(langchain_google_genai, "ChatGoogleGenerativeAI", boundary("llm"))
    for name in ("utils", "metrics", "evaluate"):
        monkeypatch.delitem(sys.modules, name, raising=False)
    utils = importlib.import_module("utils")
    monkeypatch.setitem(sys.modules, "utils", utils)
    monkeypatch.setattr(utils, "get_llm", boundary("llm"))
    monkeypatch.setattr(utils, "get_eval_llm", boundary("llm"))
    # Written after importing utils, whose module-level load_dotenv would pre-fill it.
    write_dotenv(tmp_path, DOTENV)
    langsmith_utils.get_env_var.cache_clear()
    yield SimpleNamespace(root=tmp_path, client=client, git=git, calls=calls)
    for name in ("metrics", "evaluate"):
        sys.modules.pop(name, None)
    langsmith_utils.get_env_var.cache_clear()


def write_dotenv(root, values):
    (root / ".env").write_text("".join(f"{key}={value}\n" for key, value in values.items()),
                               encoding="utf-8")


def execute_block(marker):
    document = DOC.read_text(encoding="utf-8")
    blocks = re.findall(r"^[^\n]*python - <<'PY'\n(.*?)^PY$", document,
                        flags=re.MULTILINE | re.DOTALL)
    selected = [block for block in blocks if block.startswith(f"# {marker} — ")]
    if len(selected) != 1:
        raise ValueError("Expected exactly one documented evaluation block")
    exec(compile(selected[0], str(DOC), "exec"), {"__name__": "__main__"})


def run_block(marker, capsys):
    code = 0
    try:
        execute_block(marker)
    except SystemExit as exit_:
        code = exit_.code
    out, err = capsys.readouterr()
    payloads = [json.loads(line) for line in out.splitlines() if line.startswith("{")]
    assert payloads, out
    for secret in SECRETS:
        assert secret not in out and secret not in err
    return code, payloads[-1], out


def local_cases():
    lines = (ROOT / "datasets" / "bug_to_user_story.jsonl").read_text(encoding="utf-8")
    return [json.loads(line) for line in lines.splitlines() if line.strip()]


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def definition_sha(path):
    data = yaml.safe_load(Path(path).read_bytes())["bug_to_user_story_v2"]
    canonical = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def seed_dataset(client, cases=None):
    dataset = SimpleNamespace(id=uuid.uuid4(), name=DATASET,
                              url="https://example.invalid/datasets/existing")
    client.datasets.append(dataset)
    client.examples[str(dataset.id)] = [
        SimpleNamespace(id=uuid.uuid4(), inputs=case["inputs"], outputs=case["outputs"])
        for case in (local_cases() if cases is None else cases)]
    return dataset


def gate_env(dataset):
    os.environ.update({
        "AVALIACAO_CICLO": "CIC-01",
        "AVALIACAO_HUB_COMMIT": HUB,
        "AVALIACAO_V2_FILE_SHA256": file_sha(V2),
        "AVALIACAO_V2_DEFINITION_SHA256": definition_sha(V2),
        "AVALIACAO_DATASET_ID": str(dataset.id),
        "AVALIACAO_DATASET": "idêntico",
        "AVALIACAO_TESTES": "aprovado",
        "AVALIACAO_DASHBOARD": "conferido",
        "AVALIACAO_CUSTO_ACUMULADO_USD": "0",
    })


def full_scores(f1=0.9, clarity=0.9, precision=0.9):
    return {"f1_score": f1, "clarity": clarity, "precision": precision,
            "helpfulness": round((clarity + precision) / 2, 4),
            "correctness": round((f1 + precision) / 2, 4)}


def seed_experiment(client, dataset, scores=None, missing_judge_tokens=()):
    """Fifteen root runs, template runs and five feedbacks per run."""
    scores = scores or [full_scores(0.80 + index * 0.01, 0.95 - index * 0.005, 0.9)
                        for index in range(15)]
    experiment = SimpleNamespace(
        id=str(uuid.uuid4()), name="fabiocsm-bug_to_user_story_v2-1a2b3c4d",
        tenant_id=WORKSPACE, reference_dataset_id=dataset.id,
        start_time=datetime.now(timezone.utc))
    client.projects[experiment.id] = experiment
    runs, feedback = [], []
    for index, example in enumerate(client.examples[str(dataset.id)]):
        root_id = uuid.uuid4()
        runs.append(SimpleNamespace(
            id=root_id, trace_id=root_id, parent_run_id=None, name="target",
            run_type="chain", error=None, outputs={"answer": f"História {index}"},
            reference_example_id=example.id, prompt_tokens=1000, completion_tokens=200,
            extra={"metadata": {}}))
        runs.append(SimpleNamespace(
            id=uuid.uuid4(), trace_id=root_id, parent_run_id=root_id,
            name="ChatPromptTemplate", run_type="prompt", error=None, outputs={},
            reference_example_id=None, prompt_tokens=None, completion_tokens=None,
            extra={"metadata": {"lc_hub_owner": "fabiocsm",
                                "lc_hub_repo": "bug_to_user_story_v2",
                                "lc_hub_commit_hash": HUB}}))
        judge_id = str(uuid.uuid4())
        missing = index in missing_judge_tokens
        client.source_runs[judge_id] = SimpleNamespace(
            id=judge_id, prompt_tokens=None if missing else 3000,
            completion_tokens=None if missing else 300)
        for key in KEYS:
            feedback.append(SimpleNamespace(
                id=uuid.uuid4(), run_id=root_id, key=key,
                score=scores[index % len(scores)][key],
                comment=f"Raciocínio do juiz {index} para {key}",
                feedback_source=SimpleNamespace(metadata={"__run": {"run_id": judge_id}})))
    client.runs[experiment.id] = runs
    client.feedback = feedback
    return experiment


def write_log(audit, dataset, experiment, scores=None, url=True, status=None,
              printed_override=None):
    """Evaluator-like log; the summary comes from the real display_results."""
    import evaluate

    scores = scores or [{key: item.score for item in audit.client.feedback
                         if item.run_id == run.id for key in [item.key]}
                        for run in audit.client.runs[experiment.id] if run.parent_run_id is None]
    means = {key: round(sum(row[key] for row in scores) / len(scores), 4) for key in KEYS}
    means.update(printed_override or {})
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        for index, row in enumerate(scores, 1):
            print(f"      [{index}] F1:{row['f1_score']:.2f} "
                  f"Clarity:{row['clarity']:.2f} Precision:{row['precision']:.2f}")
        passed = evaluate.display_results("fabiocsm/bug_to_user_story_v2", means)
        print("\nResultados no LangSmith (notas gravadas como feedback no experimento):")
        print("  fabiocsm/bug_to_user_story_v2")
        if url is True:
            print(f"    https://smith.langchain.com/o/{WORKSPACE}/datasets/{dataset.id}"
                  f"/compare?selectedSessions={experiment.id}")
        elif url:
            print(f"    {url}")
    text = buffer.getvalue()
    if status is not None:
        text = re.sub(r"STATUS: (APROVADO|REPROVADO)", status, text)
    path = audit.root / "results" / "CIC-01-20261018T220000.log"
    path.write_text(text, encoding="utf-8")
    return path, passed


def audit_env(audit, dataset, experiment=None, exit_code=None, **log_options):
    gate_env(dataset)
    path, passed = (write_log(audit, dataset, experiment, **log_options)
                    if experiment is not None else (audit.root / "results" / "vazio.log", False))
    if experiment is None:
        path.write_text("❌ Falha ao avaliar\n", encoding="utf-8")
    os.environ["AVALIACAO_LOG"] = str(path)
    os.environ["AVALIACAO_EXIT_CODE"] = ("0" if passed else "1") if exit_code is None else exit_code
    os.environ["AVALIACAO_INICIO"] = (datetime.now(timezone.utc)
                                      - timedelta(minutes=5)).isoformat()
    return passed


# --- C01: AVALIACAO_GATE -------------------------------------------------------

def test_gate_accepts_complete_preconditions(audit, capsys):
    gate_env(seed_dataset(audit.client))
    code, result, _ = run_block("AVALIACAO_GATE", capsys)
    assert code == 0
    assert result["estado"] == "gate_ok"
    assert result["condicao"] == "COND-001"
    assert result["head_before"] == HUB and result["workspace_id"] == WORKSPACE
    assert result["git_commit"] == "a" * 40
    assert audit.client.prompt_identifiers == ["fabiocsm/bug_to_user_story_v2"]
    assert audit.calls == [] and audit.client.writes == []


def test_gate_accepts_cost_exactly_at_limit(audit, capsys):
    gate_env(seed_dataset(audit.client))
    os.environ["AVALIACAO_CUSTO_ACUMULADO_USD"] = "4.00"
    code, result, _ = run_block("AVALIACAO_GATE", capsys)
    assert code == 0 and result["estado"] == "gate_ok"


@pytest.mark.parametrize("marker", ["AVALIACAO_GATE", "AVALIACAO_AUDITORIA"])
@pytest.mark.parametrize("owner", ["outro-owner", " fabiocsm", "fabiocsm ", ""])
def test_prompt_owner_mismatch_stops_before_client_creation(
        marker, owner, audit, capsys, monkeypatch):
    dataset = seed_dataset(audit.client)
    experiment = seed_experiment(audit.client, dataset)
    audit_env(audit, dataset, experiment)
    os.environ["USERNAME_LANGSMITH_HUB"] = owner
    clients = []

    def permissive_client(*args, **kwargs):
        clients.append(audit.client)
        return audit.client  # Accepts every owner, including a matching public revision.

    monkeypatch.setattr(langsmith, "Client", permissive_client)
    code, result, _ = run_block(marker, capsys)
    assert code == 1
    if marker == "AVALIACAO_GATE":
        assert result["estado"] == "bloqueado" and result["causa"] == "configuracao"
    else:
        assert result["estado"] == "falha_auditoria" and result["etapa"] == "configuracao"
    assert clients == []
    assert audit.client.prompt_identifiers == []
    assert audit.calls == [] and audit.client.writes == []


def alternative_condition(audit):
    other = PROJECT + "-c2"
    declaration = {"condicao": "COND-002", "provider": "openai",
                   "llm_model": "gpt-4.1-2025-04-14", "eval_model": "gpt-4.1-2025-04-14",
                   "temperature": 0, "langsmith_project": other,
                   "dataset_name": other + "-eval", "workspace_id": WORKSPACE,
                   "endpoint": "https://api.smith.langchain.com",
                   "rates_usd_per_million": RATES}
    with (audit.root / "docs" / "avaliacao-v2.md").open("a", encoding="utf-8") as doc:
        doc.write("\n```json condicao\n" + json.dumps(declaration) + "\n```\n")
    dataset = seed_dataset(audit.client)
    dataset.name = other + "-eval"
    gate_env(dataset)
    os.environ.update(AVALIACAO_CONDICAO="COND-002", LANGSMITH_PROJECT=other)
    return other


def test_gate_accepts_declared_alternative_condition(audit, capsys):
    other = alternative_condition(audit)
    audit.client.named_projects[other] = SimpleNamespace(
        id=str(uuid.uuid4()), name=other, tenant_id=WORKSPACE)
    code, result, _ = run_block("AVALIACAO_GATE", capsys)
    assert code == 0 and result["condicao"] == "COND-002"


def test_new_condition_bootstrap_unblocks_gate_without_llm(audit, capsys):
    other = alternative_condition(audit)
    code, result, _ = run_block("AVALIACAO_GATE", capsys)
    assert code == 1 and result["causa"] == "configuracao"
    assert audit.client.writes == []

    code, result, _ = run_block("AVALIACAO_PROJETO", capsys)
    assert code == 0 and result["estado"] == "pronto" and result["criado"] is True
    assert result["projeto"] == other and result["workspace_id"] == WORKSPACE
    assert audit.client.client_options[-1]["workspace_id"] == WORKSPACE
    assert audit.client.writes == ["create_project"]

    code, result, _ = run_block("AVALIACAO_GATE", capsys)
    assert code == 0 and result["estado"] == "gate_ok"
    assert audit.client.writes == ["create_project"] and audit.calls == []


def test_project_bootstrap_is_idempotent(audit, capsys):
    alternative_condition(audit)
    for created in (True, False):
        code, result, _ = run_block("AVALIACAO_PROJETO", capsys)
        assert code == 0 and result["criado"] is created
    assert audit.client.writes == ["create_project"] and audit.calls == []


def test_project_bootstrap_rejects_existing_wrong_workspace(audit, capsys):
    other = alternative_condition(audit)
    project = SimpleNamespace(id=str(uuid.uuid4()), name=other, tenant_id=str(uuid.uuid4()))
    audit.client.named_projects[other] = project
    code, result, _ = run_block("AVALIACAO_PROJETO", capsys)
    assert code == 1 and result["estado"] == "bloqueado" and result["causa"] == "workspace"
    assert audit.client.named_projects[other] is project
    assert audit.client.writes == [] and audit.calls == []


def test_project_bootstrap_does_not_create_after_transport_error(audit, capsys, monkeypatch):
    alternative_condition(audit)

    def unavailable(**kwargs):
        raise langsmith_utils.LangSmithConnectionError(" ".join(SECRETS))

    monkeypatch.setattr(audit.client, "read_project", unavailable)
    code, result, _ = run_block("AVALIACAO_PROJETO", capsys)
    assert code == 1 and result["estado"] == "bloqueado"
    assert audit.client.writes == [] and audit.calls == []


def _change_file(relative):
    def mutate(audit, dataset):
        with (audit.root / relative).open("a", encoding="utf-8") as handle:
            handle.write("\n# alterado\n")
    return mutate


def _env(**values):
    def mutate(audit, dataset):
        for key, value in values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    return mutate


def _dotenv_without(name):
    def mutate(audit, dataset):
        write_dotenv(audit.root, {k: v for k, v in DOTENV.items() if k != name})
    return mutate


def _set(path, value):
    def mutate(audit, dataset):
        target = audit
        *parents, last = path.split(".")
        for part in parents:
            target = getattr(target, part)
        setattr(target, last, value)
    return mutate


def _remove_dataset(audit, dataset):
    audit.client.datasets.clear()


GATE_NEGATIVES = [
    pytest.param(_change_file("src/metrics.py"), "integridade", id="protegido"),
    pytest.param(_change_file("datasets/bug_to_user_story.jsonl"), "integridade",
                 id="dataset-local"),
    pytest.param(_change_file("prompts/bug_to_user_story_v1.yml"), "integridade", id="v1"),
    pytest.param(_env(AVALIACAO_V2_FILE_SHA256="0" * 64), "revisao", id="hash-arquivo-v2"),
    pytest.param(_env(AVALIACAO_V2_DEFINITION_SHA256="0" * 64), "revisao",
                 id="hash-definicao-v2"),
    pytest.param(_set("git.status", " M " + V2 + "\n"), "revisao", id="v2-nao-commitada"),
    pytest.param(_env(AVALIACAO_HUB_COMMIT=OTHER_HUB), "revisao", id="head-divergente"),
    pytest.param(_set("client.prompt.is_public", False), "revisao", id="nao-publico"),
    pytest.param(_env(AVALIACAO_HUB_COMMIT=None), "revisao", id="revisao-ausente"),
    pytest.param(_env(LANGSMITH_API_KEY="   "), "configuracao", id="chave-em-branco"),
    pytest.param(_dotenv_without("OPENAI_API_KEY"), "configuracao", id="chave-ausente"),
    pytest.param(_dotenv_without("EVAL_MODEL"), "configuracao", id="modelo-ausente"),
    pytest.param(_env(LANGSMITH_TRACING="false"), "configuracao", id="tracing-false"),
    pytest.param(_env(LANGSMITH_TRACING_V2="false"), "configuracao", id="alias-v2"),
    pytest.param(_env(LANGCHAIN_TRACING_V2="false"), "configuracao", id="alias-langchain"),
    pytest.param(_env(LLM_PROVIDER="google", GOOGLE_API_KEY="x"), "configuracao",
                 id="provider"),
    pytest.param(_env(LLM_MODEL="gpt-4.1-mini"), "configuracao", id="modelo-geracao"),
    pytest.param(_env(EVAL_MODEL="gpt-4.1-mini"), "configuracao", id="modelo-juiz"),
    pytest.param(_env(LANGSMITH_PROJECT="outro-projeto"), "configuracao", id="projeto"),
    pytest.param(_set("client.main_project.tenant_id", "outro-tenant"), "configuracao",
                 id="workspace"),
    pytest.param(_env(AVALIACAO_CONDICAO="COND-009"), "condicao", id="condicao"),
    pytest.param(_env(AVALIACAO_DATASET_ID=None), "dataset", id="dataset-id-ausente"),
    pytest.param(_env(AVALIACAO_DATASET_ID=str(uuid.uuid4())), "dataset",
                 id="dataset-id-divergente"),
    pytest.param(_env(AVALIACAO_DATASET="divergente"), "dataset", id="dataset-divergente"),
    pytest.param(_remove_dataset, "dataset", id="dataset-remoto-ausente"),
    pytest.param(_env(AVALIACAO_TESTES=None), "testes", id="testes-ausentes"),
    pytest.param(_env(AVALIACAO_TESTES="reprovado"), "testes", id="testes-reprovados"),
    pytest.param(_env(AVALIACAO_DASHBOARD="pendente"), "dashboard", id="dashboard"),
    pytest.param(_env(AVALIACAO_CUSTO_ACUMULADO_USD="4.01"), "custo", id="custo-acima"),
    pytest.param(_env(AVALIACAO_CUSTO_ACUMULADO_USD="abc"), "custo", id="custo-invalido"),
]


@pytest.mark.parametrize("mutate,cause", GATE_NEGATIVES)
def test_gate_blocks_with_specific_cause(mutate, cause, audit, capsys):
    dataset = seed_dataset(audit.client)
    gate_env(dataset)
    mutate(audit, dataset)
    code, result, _ = run_block("AVALIACAO_GATE", capsys)
    assert code == 1
    assert result["estado"] == "bloqueado"
    assert result["causa"] == cause
    assert "llm" not in audit.calls and audit.client.writes == []


# --- C02: AVALIACAO_DATASET ----------------------------------------------------

def _dataset_lines(out):
    return dict(line.split("=", 1) for line in out.splitlines()
                if line.startswith("AVALIACAO_DATASET"))


def test_dataset_absent_is_created_once_by_provided_function(audit, capsys):
    os.environ["AVALIACAO_CICLO"] = "CIC-01"
    code, result, out = run_block("AVALIACAO_DATASET", capsys)
    assert code == 0
    assert result["estado"] == "idêntico" and result["criado"] is True
    assert "Criando dataset de avaliação" not in out
    assert audit.client.writes == ["create_dataset"] + ["create_example"] * 15
    assert result["example_count"] == 15 and result["matches_local"] is True
    assert result["distribution"] == {"simple": 5, "medium": 7, "complex": 3}
    assert len(result["example_map"]) == 15
    exported = _dataset_lines(out)
    assert exported == {"AVALIACAO_DATASET_ID": result["dataset_id"],
                        "AVALIACAO_DATASET": "idêntico"}
    assert "llm" not in audit.calls


def test_dataset_present_and_identical_is_only_read(audit, capsys):
    dataset = seed_dataset(audit.client)
    code, result, out = run_block("AVALIACAO_DATASET", capsys)
    assert code == 0 and result["estado"] == "idêntico" and result["criado"] is False
    assert result["dataset_id"] == str(dataset.id)
    assert audit.client.writes == []
    by_index = sorted(result["example_map"].values(), key=lambda item: item["indice"])
    assert [item["complexidade"] for item in by_index] == [
        case["metadata"]["complexity"] for case in local_cases()]


def _altered_reference():
    cases = local_cases()
    cases[3] = {**cases[3], "outputs": {"reference": cases[3]["outputs"]["reference"] + "!"}}
    return cases


DATASET_NEGATIVES = [
    pytest.param(lambda: local_cases()[:14], id="14-exemplos"),
    pytest.param(_altered_reference, id="referencia-alterada"),
    pytest.param(lambda: local_cases() + [local_cases()[0]], id="exemplo-extra"),
    pytest.param(lambda: local_cases()[:14] + [local_cases()[0]], id="duplicata"),
]


@pytest.mark.parametrize("cases", DATASET_NEGATIVES)
def test_dataset_divergent_is_reported_without_writes(cases, audit, capsys):
    seed_dataset(audit.client, cases())
    code, result, out = run_block("AVALIACAO_DATASET", capsys)
    assert code == 1
    assert result["estado"] == "divergente" and result["matches_local"] is False
    assert "D03" in result["acao"]
    assert _dataset_lines(out)["AVALIACAO_DATASET"] == "divergente"
    assert audit.client.writes == []


def test_dataset_partial_creation_is_divergent(audit, capsys):
    audit.client.fail_example_after = 10
    code, result, _ = run_block("AVALIACAO_DATASET", capsys)
    assert code == 1
    assert result["estado"] == "divergente" and result["example_count"] == 10
    assert set(audit.client.writes) == {"create_dataset", "create_example"}
    assert audit.client.writes.count("create_dataset") == 1


def test_dataset_creation_failure_suppresses_raw_output(audit, capsys, monkeypatch):
    create_example = audit.client.create_example

    def fail_after_three(**kwargs):
        if len(audit.client.examples[str(kwargs["dataset_id"])]) == 3:
            print(f"x-api-key: {SECRETS[0]}", file=sys.stderr)
            raise RuntimeError(f"headers: {SECRETS[0]} {SECRETS[1]}")
        create_example(**kwargs)

    monkeypatch.setattr(audit.client, "create_example", fail_after_three)
    code, result, out = run_block("AVALIACAO_DATASET", capsys)
    assert code == 1
    assert result["estado"] == "divergente" and result["example_count"] == 3
    assert result["matches_local"] is False
    assert audit.client.writes.count("create_dataset") == 1
    assert audit.client.writes.count("create_example") == 3
    assert "headers:" not in out and "Erro ao criar dataset" not in out


# --- C04/C05: AVALIACAO_AUDITORIA ----------------------------------------------

def test_audit_accepts_complete_and_linked_experiment(audit, capsys):
    dataset = seed_dataset(audit.client)
    experiment = seed_experiment(audit.client, dataset, missing_judge_tokens={4})
    audit_env(audit, dataset, experiment)
    code, result, _ = run_block("AVALIACAO_AUDITORIA", capsys)
    assert code == 0
    assert result["estado"] not in {"incompleto", "invalidado", "falha_execução"}
    assert result["experimento"]["id"] == experiment.id
    assert result["experimento"]["nome"] == experiment.name
    assert result["completude"] == {"estado": "completo", "runs": 15, "notas_validas": 75,
                                    "problemas": []}
    assert result["vinculo"]["estado"] == "estavel"
    assert result["vinculo"]["lc_hub_commit_hash"] == "confirmado"
    assert result["vinculo"]["head_depois"] == HUB
    assert audit.client.prompt_identifiers == ["fabiocsm/bug_to_user_story_v2"]
    assert len(result["exemplos"]) == 15
    assert {row["prompt_commit"] for row in result["exemplos"]} == {HUB}
    counts = {name: item["exemplos"] for name, item in result["by_complexity"].items()}
    assert counts == {"simple": 5, "medium": 7, "complex": 3}
    lowest = result["lowest"]["f1_score"]
    assert [item["nota"] for item in lowest] == [0.8, 0.81, 0.82]
    assert [item["indice"] for item in lowest] == [1, 2, 3]
    assert lowest[0]["comentario"] == "Raciocínio do juiz 0 para f1_score"
    tokens = result["tokens"]
    assert tokens["geracao"] == {"entrada": 15000, "saida": 3000, "estimados": 0}
    assert tokens["juizes"]["estimados"] == 1
    assert tokens["juizes"]["entrada"] > 14 * 3000 and tokens["juizes"]["saida"] > 14 * 300
    assert tokens["estimado"] is True
    assert result["rates_usd_per_million"] == RATES
    assert result["custo_estimado_usd"] == pytest.approx(0.184402)
    assert audit.calls == [] and audit.client.writes == []


def test_audit_records_missing_hub_commit_metadata_as_limitation(audit, capsys):
    dataset = seed_dataset(audit.client)
    experiment = seed_experiment(audit.client, dataset)
    for run in audit.client.runs[experiment.id]:
        run.extra["metadata"].pop("lc_hub_commit_hash", None)
    audit_env(audit, dataset, experiment)
    code, result, _ = run_block("AVALIACAO_AUDITORIA", capsys)
    assert code == 0
    assert result["vinculo"]["estado"] == "estavel"
    assert result["vinculo"]["lc_hub_commit_hash"] == "ausente"
    assert "lc_hub_commit_hash_ausente" in result["limitacoes"]


def _roots(audit, experiment):
    return [run for run in audit.client.runs[experiment.id] if run.parent_run_id is None]


def _drop_root(audit, experiment, dataset):
    victim = _roots(audit, experiment)[0]
    audit.client.runs[experiment.id].remove(victim)


def _repeat_example(audit, experiment, dataset):
    roots = _roots(audit, experiment)
    roots[1].reference_example_id = roots[0].reference_example_id


def _root_error(audit, experiment, dataset):
    _roots(audit, experiment)[2].error = "RateLimitError"


def _empty_answer(audit, experiment, dataset):
    _roots(audit, experiment)[3].outputs = {"answer": "  "}


def _feedback(index=0, key="clarity"):
    def select(audit, experiment):
        run = _roots(audit, experiment)[index]
        return next(item for item in audit.client.feedback
                    if item.run_id == run.id and item.key == key)
    return select


def _missing_feedback(audit, experiment, dataset):
    audit.client.feedback.remove(_feedback()(audit, experiment))


def _duplicate_feedback(audit, experiment, dataset):
    item = _feedback()(audit, experiment)
    audit.client.feedback.append(SimpleNamespace(**{**vars(item), "id": uuid.uuid4()}))


def _score(value, key="clarity"):
    def mutate(audit, experiment, dataset):
        _feedback(key=key)(audit, experiment).score = value
    return mutate


def _comment(text):
    def mutate(audit, experiment, dataset):
        _feedback(key="precision")(audit, experiment).comment = text
    return mutate


def _head_after(audit, experiment, dataset):
    audit.client.prompt.last_commit_hash = OTHER_HUB


def _template_commit(audit, experiment, dataset):
    template = next(run for run in audit.client.runs[experiment.id]
                    if run.name == "ChatPromptTemplate")
    template.extra["metadata"]["lc_hub_commit_hash"] = OTHER_HUB


def _reference_dataset(audit, experiment, dataset):
    experiment.reference_dataset_id = uuid.uuid4()


def _remote_example_changed(audit, experiment, dataset):
    example = audit.client.examples[str(dataset.id)][5]
    example.outputs = {"reference": "outra referência"}


def _local_change(relative):
    def mutate(audit, experiment, dataset):
        with (audit.root / relative).open("a", encoding="utf-8") as handle:
            handle.write("\n# alterado depois da execução\n")
    return mutate


AUDIT_NEGATIVES = [
    pytest.param(_reference_dataset, "invalidado", id="reference-dataset"),
    pytest.param(_remote_example_changed, "invalidado", id="example-map"),
    pytest.param(_drop_root, "incompleto", id="14-runs"),
    pytest.param(_repeat_example, "incompleto", id="exemplo-repetido"),
    pytest.param(_root_error, "incompleto", id="run-com-erro"),
    pytest.param(_empty_answer, "incompleto", id="resposta-vazia"),
    pytest.param(_missing_feedback, "incompleto", id="feedback-ausente"),
    pytest.param(_duplicate_feedback, "incompleto", id="feedback-duplicado"),
    pytest.param(_score(None), "incompleto", id="nota-none"),
    pytest.param(_score(math.nan), "incompleto", id="nota-nan"),
    pytest.param(_score(math.inf), "incompleto", id="nota-inf"),
    pytest.param(_score(-0.1), "incompleto", id="nota-negativa"),
    pytest.param(_score(1.2), "incompleto", id="nota-acima-de-1"),
    pytest.param(_score(True), "incompleto", id="nota-booleana"),
    pytest.param(_comment("Erro na avaliação: timeout"), "incompleto", id="marcador-juiz"),
    pytest.param(_comment("Erro ao processar resposta"), "incompleto", id="marcador-json"),
    pytest.param(_comment("Resposta vazia"), "incompleto", id="marcador-vazia"),
    pytest.param(_score(0.1, key="helpfulness"), "incompleto", id="helpfulness-inconsistente"),
    pytest.param(_score(0.1, key="correctness"), "incompleto", id="correctness-inconsistente"),
    pytest.param(_head_after, "invalidado", id="head-depois"),
    pytest.param(_template_commit, "invalidado", id="lc-hub-commit-divergente"),
    pytest.param(_local_change(V2), "invalidado", id="v2-alterada"),
    pytest.param(_local_change("src/evaluate.py"), "invalidado", id="protegido-alterado"),
    pytest.param(_local_change("prompts/bug_to_user_story_v1.yml"), "invalidado",
                 id="v1-alterada"),
]


@pytest.mark.parametrize("mutate,state", AUDIT_NEGATIVES)
def test_audit_rejects_incomplete_or_unlinked_experiment(mutate, state, audit, capsys):
    dataset = seed_dataset(audit.client)
    experiment = seed_experiment(audit.client, dataset)
    audit_env(audit, dataset, experiment)
    mutate(audit, experiment, dataset)
    code, result, _ = run_block("AVALIACAO_AUDITORIA", capsys)
    assert code == 1
    assert result["estado"] == state
    assert result.get("decisao") in (None, state)
    assert audit.calls == [] and audit.client.writes == []


@pytest.mark.parametrize("url", [False, "https://smith.langchain.com/o/x/datasets/y/compare"],
                         ids=["sem-url", "url-sem-selected-sessions"])
def test_audit_without_experiment_url_lists_partial_projects_only(url, audit, capsys):
    dataset = seed_dataset(audit.client)
    experiment = seed_experiment(audit.client, dataset)
    old = SimpleNamespace(id=str(uuid.uuid4()), name="fabiocsm-bug_to_user_story_v2-old",
                          tenant_id=WORKSPACE, reference_dataset_id=dataset.id,
                          start_time=datetime.now(timezone.utc) - timedelta(days=1))
    unrelated = SimpleNamespace(id=str(uuid.uuid4()), name="outro-prefixo-1",
                                tenant_id=WORKSPACE, reference_dataset_id=dataset.id,
                                start_time=datetime.now(timezone.utc))
    audit.client.projects.update({old.id: old, unrelated.id: unrelated})
    audit_env(audit, dataset, experiment, url=url)
    code, result, _ = run_block("AVALIACAO_AUDITORIA", capsys)
    assert code == 1
    assert result["estado"] == "falha_execução"
    assert [item["id"] for item in result["projetos_parciais"]] == [experiment.id]
    assert "decisao" not in result and "means" not in result
    assert audit.client.writes == []


# --- C06: agregação e decisão no bloco AVALIACAO_AUDITORIA ---------------------

def _audit_with(audit, capsys, scores, exit_code=None, **log_options):
    dataset = seed_dataset(audit.client)
    experiment = seed_experiment(audit.client, dataset, scores=scores)
    audit_env(audit, dataset, experiment, exit_code=exit_code, **log_options)
    return run_block("AVALIACAO_AUDITORIA", capsys)


def test_decision_recalculates_means_like_the_evaluator(audit, capsys):
    scores = [full_scores(0.80 + index * 0.01, 0.95 - index * 0.005, 0.9)
              for index in range(15)]
    code, result, _ = _audit_with(audit, capsys, scores)
    expected = {key: round(sum(row[key] for row in scores) / 15, 4) for key in KEYS}
    assert code == 0
    assert result["means"] == expected
    assert result["overall"] == pytest.approx(sum(expected.values()) / 5)
    assert result["printed_means"] == {key: f"{value:.2f}" for key, value in expected.items()}
    assert result["printed_overall"] == f"{sum(expected.values()) / 5:.4f}"
    assert result["printed_status"] == "APROVADO" and result["exit_code"] == 0
    assert result["decisao_avaliador"] == result["decisao_contrato"] == "aprovado"
    assert result["decisao"] == result["estado"] == "aprovado"
    assert result["divergencias"] == []


def test_decision_accepts_every_mean_exactly_at_threshold(audit, capsys):
    code, result, _ = _audit_with(audit, capsys, [full_scores(0.8, 0.8, 0.8)] * 15)
    assert code == 0
    assert all(value == 0.8 for value in result["means"].values())
    assert result["decisao"] == "aprovado" and result["metricas_abaixo"] == []


def test_decision_rejects_one_metric_below_threshold_despite_overall(audit, capsys):
    code, result, _ = _audit_with(audit, capsys, [full_scores(0.7999, 0.95, 0.95)] * 15)
    assert code == 0
    assert result["overall"] >= 0.8
    assert result["means"]["f1_score"] == 0.7999
    assert result["decisao_contrato"] == result["decisao"] == "reprovado"
    assert result["metricas_abaixo"] == ["f1_score"]
    assert result["divergencias"] == []


def test_decision_rejects_overall_below_threshold(audit, capsys):
    code, result, _ = _audit_with(audit, capsys, [full_scores(0.7, 0.7, 0.7)] * 15)
    assert code == 0
    assert result["overall"] < 0.8 and result["decisao"] == "reprovado"
    assert result["metricas_abaixo"] == KEYS


def test_decision_keeps_low_individual_score_as_limitation(audit, capsys):
    scores = [full_scores(0.3, 0.95, 0.95)] + [full_scores(0.95, 0.95, 0.95)] * 14
    code, result, _ = _audit_with(audit, capsys, scores)
    assert code == 0 and result["decisao"] == "aprovado"
    assert "notas_individuais_abaixo_do_limiar" in result["limitacoes"]


def test_decision_marks_printed_means_mismatch_as_incomplete(audit, capsys):
    code, result, _ = _audit_with(audit, capsys, [full_scores(0.9, 0.9, 0.9)] * 15,
                                  printed_override={"f1_score": 0.5})
    assert code == 1
    assert result["estado"] == result["decisao"] == "incompleto"
    assert "medias_impressas_divergentes" in result["completude"]["problemas"]


@pytest.mark.parametrize("mutate,state", [
    pytest.param(_missing_feedback, "incompleto", id="incompleto"),
    pytest.param(_head_after, "invalidado", id="invalidado"),
])
def test_decision_never_approves_incomplete_or_invalid_experiment(mutate, state, audit, capsys):
    dataset = seed_dataset(audit.client)
    experiment = seed_experiment(audit.client, dataset,
                                 scores=[full_scores(0.95, 0.95, 0.95)] * 15)
    audit_env(audit, dataset, experiment)
    mutate(audit, experiment, dataset)
    code, result, _ = run_block("AVALIACAO_AUDITORIA", capsys)
    assert code == 1
    assert result["decisao"] == state and result["decisao_contrato"] == state


def test_decision_exit_zero_cannot_override_contract_rejection(audit, capsys):
    code, result, _ = _audit_with(audit, capsys, [full_scores(0.7, 0.7, 0.7)] * 15,
                                  exit_code="0")
    assert result["decisao_contrato"] == result["decisao"] == "reprovado"
    assert "codigo_contraditorio_com_status" in result["divergencias"]


def test_decision_exit_one_prevails_over_contract_approval(audit, capsys):
    code, result, _ = _audit_with(audit, capsys, [full_scores(0.9, 0.9, 0.9)] * 15,
                                  exit_code="1")
    assert result["decisao_contrato"] == "aprovado"
    assert result["decisao_avaliador"] == "reprovado"
    assert result["decisao"] == "reprovado"
    assert "codigo_contraditorio_com_status" in result["divergencias"]
    assert "decisao_avaliador_divergente" in result["divergencias"]


@pytest.mark.parametrize("exit_code", [None, "", "abc", "2"],
                         ids=["ausente", "vazio", "nao-numerico", "inesperado"])
def test_decision_missing_or_invalid_exit_code_never_approves(exit_code, audit, capsys):
    dataset = seed_dataset(audit.client)
    experiment = seed_experiment(audit.client, dataset,
                                 scores=[full_scores(0.9, 0.9, 0.9)] * 15)
    audit_env(audit, dataset, experiment)
    if exit_code is None:
        os.environ.pop("AVALIACAO_EXIT_CODE")
    else:
        os.environ["AVALIACAO_EXIT_CODE"] = exit_code
    code, result, _ = run_block("AVALIACAO_AUDITORIA", capsys)
    assert result["decisao_contrato"] == "aprovado"
    assert result["decisao"] != "aprovado"
    assert "codigo_ausente_ou_invalido" in result["divergencias"]


def test_decision_status_contradicting_exit_code_is_divergent(audit, capsys):
    code, result, _ = _audit_with(audit, capsys, [full_scores(0.9, 0.9, 0.9)] * 15,
                                  exit_code="0", status="STATUS: REPROVADO")
    assert result["printed_status"] == "REPROVADO"
    assert result["decisao"] == "reprovado"
    assert "codigo_contraditorio_com_status" in result["divergencias"]


def test_decision_missing_status_line_is_incomplete(audit, capsys):
    code, result, _ = _audit_with(audit, capsys, [full_scores(0.9, 0.9, 0.9)] * 15,
                                  status="situação omitida")
    assert code == 1
    assert result["printed_status"] is None
    assert result["estado"] == result["decisao"] == "incompleto"
    assert "status_ausente" in result["completude"]["problemas"]


# --- FR-005 / SC-003: registro documental de cada ciclo -------------------------

CYCLE_FIELDS = ["**Data**", "**Condição**", "**Dataset**", "**v2 local**",
                "**Revisão publicada**", "**Inspeção no dashboard**", "**Experimento**",
                "**Médias**", "**Média geral**", "**Completude**", "**Decisão**",
                "**Custo acumulado**", "**Problema**", "**Hipótese**"]


def _cycle_sections():
    document = DOC.read_text(encoding="utf-8")
    cycles = document.split("\n## Ciclos\n", 1)[1].split("\n## ", 1)[0]
    parts = re.split(r"^### (CIC-0\d)\n", cycles, flags=re.MULTILINE)[1:]
    return document, dict(zip(parts[::2], parts[1::2]))


def _bullet(text, label):
    """Whole Markdown bullet starting with label, including wrapped lines."""
    match = re.search(rf"^- {re.escape(label)}.*?(?=^- \*\*|^\s*$)", text + "\n\n",
                      flags=re.MULTILINE | re.DOTALL)
    assert match, label
    return match.group(0)


def test_cycle_records_have_every_required_field():
    document, sections = _cycle_sections()
    assert list(sections) == ["CIC-01", "CIC-02", "CIC-03", "CIC-04", "CIC-05"]
    stop = document.split("\n## Decisão de parada\n", 1)[1].split("\n## ", 1)[0]
    assert sections["CIC-01"].strip() != "Pendente."
    stop_open = stop.strip().startswith(("Pendente.", "**Reaberta**"))
    for cycle, body in sections.items():
        text = body.strip()
        if text == "Pendente.":
            assert stop_open, f"{cycle} pendente após a decisão de parada"
            continue
        if text.startswith("**Em andamento**"):
            assert stop_open, f"{cycle} em andamento após a decisão de parada"
            assert "**Problema**" in text and "**Hipótese**" in text, cycle
            continue
        if text.startswith("**Não aplicável**"):
            assert "**Justificativa**" in text, cycle
            continue
        missing = [field for field in CYCLE_FIELDS if field not in text]
        assert not missing, (cycle, missing)
        means = _bullet(text, "**Médias**")
        for metric in ("Helpfulness", "Correctness", "F1-Score", "Clarity", "Precision"):
            assert metric in means, (cycle, metric)
        experiment = _bullet(text, "**Experimento**")
        assert re.search(r"selectedSessions=[0-9a-f-]{36}", experiment), cycle
        assert re.search(r"`[0-9a-f]{64}`", text.split("**Revisão publicada**", 1)[1]), cycle


# --- R1-4: tariffs belong to the active experimental condition -----------------

RATES = {"geracao": {"entrada": 2, "saida": 8},
         "juizes": {"entrada": 2, "saida": 8}}


def _rewrite_condition(audit, change):
    path = audit.root / "docs" / "avaliacao-v2.md"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^```json condicao\n(.*?)^```$", text, flags=re.M | re.S)
    condition = json.loads(match.group(1))
    change(condition)
    path.write_text(text[:match.start(1)] + json.dumps(condition) + "\n"
                    + text[match.end(1):], encoding="utf-8")


@pytest.mark.parametrize("marker", ["AVALIACAO_GATE", "AVALIACAO_AUDITORIA"])
@pytest.mark.parametrize("bad", [None, {}, {"geracao": RATES["geracao"]},
                                  {"geracao": {}, "juizes": RATES["juizes"]},
                                  {"geracao": RATES["geracao"], "juizes": {"entrada": 2}},
                                  {"geracao": RATES["geracao"],
                                   "juizes": {"entrada": 2, "saida": True}},
                                  True, "2", -1, math.nan, math.inf])
def test_condition_invalid_rates_stop_before_client_creation(
        marker, bad, audit, capsys, monkeypatch):
    dataset = seed_dataset(audit.client)
    experiment = seed_experiment(audit.client, dataset)
    audit_env(audit, dataset, experiment)

    def change(condition):
        if bad is None:
            condition.pop("rates_usd_per_million", None)
        elif isinstance(bad, dict):
            condition["rates_usd_per_million"] = bad
        else:
            condition["rates_usd_per_million"] = {
                "geracao": {"entrada": bad, "saida": 8}, "juizes": RATES["juizes"]}

    _rewrite_condition(audit, change)
    clients = []
    monkeypatch.setattr(langsmith, "Client", lambda **kwargs: clients.append(kwargs))
    code, result, _ = run_block(marker, capsys)
    assert code == 1
    if marker == "AVALIACAO_GATE":
        assert result["estado"] == "bloqueado" and result["causa"] == "condicao"
    else:
        assert result["estado"] == "falha_auditoria" and result["etapa"] == "condicao"
    assert result["categoria"] == "ValueError"
    assert clients == []
    assert audit.client.writes == [] and audit.calls == []


@pytest.mark.parametrize("marker", ["AVALIACAO_GATE", "AVALIACAO_AUDITORIA"])
def test_condition_accepts_zero_rates(marker, audit, capsys):
    dataset = seed_dataset(audit.client)
    experiment = seed_experiment(audit.client, dataset)
    audit_env(audit, dataset, experiment)
    zero = {role: {direction: 0 for direction in ("entrada", "saida")}
            for role in ("geracao", "juizes")}
    _rewrite_condition(audit, lambda condition: condition.update(rates_usd_per_million=zero))
    code, result, _ = run_block(marker, capsys)
    assert code == 0, json.dumps(result)
    assert result["rates_usd_per_million"] == zero
    if marker == "AVALIACAO_AUDITORIA":
        assert result["custo_estimado_usd"] == 0


def test_alternative_condition_cost_uses_each_role_and_blocks_next_gate(audit, capsys):
    dataset = seed_dataset(audit.client)
    experiment = seed_experiment(audit.client, dataset)
    audit_env(audit, dataset, experiment)
    path = audit.root / "docs" / "avaliacao-v2.md"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^```json condicao\n(.*?)^```$", text, flags=re.M | re.S)
    condition = json.loads(match.group(1))
    rates = {"geracao": {"entrada": 10, "saida": 20},
             "juizes": {"entrada": 100, "saida": 200}}
    condition.update(condicao="COND-002", llm_model="offline-generator",
                     eval_model="offline-judge", rates_usd_per_million=rates)
    path.write_text(text + "\n```json condicao\n" + json.dumps(condition) + "\n```\n",
                    encoding="utf-8")
    os.environ.update(AVALIACAO_CONDICAO="COND-002", LLM_MODEL="offline-generator",
                      EVAL_MODEL="offline-judge")
    code, result, _ = run_block("AVALIACAO_GATE", capsys)
    assert code == 0 and result["condicao"] == "COND-002", json.dumps(result)
    code, result, _ = run_block("AVALIACAO_AUDITORIA", capsys)
    assert code == 0 and result["estado"] == "aprovado"
    assert result["rates_usd_per_million"] == rates
    # 15k/3k generation + 45k/4.5k judging, each using its own USD/M rates.
    assert result["custo_estimado_usd"] == pytest.approx(5.61)
    os.environ["AVALIACAO_CUSTO_ACUMULADO_USD"] = str(result["custo_estimado_usd"])
    code, result, _ = run_block("AVALIACAO_GATE", capsys)
    assert code == 1 and result["causa"] == "custo"
    assert audit.client.writes == [] and audit.calls == []
