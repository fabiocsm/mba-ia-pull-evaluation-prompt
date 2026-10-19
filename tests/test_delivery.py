"""Offline checks of delivery documents; these never prove anonymous access.

Read only local files and Git metadata. No dotenv, credentials, SDK or LLM calls.
"""

from pathlib import Path
import re
import subprocess

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
DATASET_URL = re.compile(r"https://smith\.langchain\.com/public/[a-zA-Z0-9-]+/d\b")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def read_document(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def section(document, title, level=2):
    marker = "#" * level
    found = re.search(
        rf"^{marker} {re.escape(title)}\s*\n(.*?)(?=^#{{1,{level}}} |\Z)",
        document, re.M | re.S,
    )
    assert found, f"Missing section: {title}"
    return found.group(1)


def base_readme():
    return subprocess.run(
        ["git", "show", "a94ce44:README.md"], cwd=ROOT,
        check=True, text=True, capture_output=True,
    ).stdout


def markdown_images(document):
    return re.findall(r"!\[[^\]]*\]\(<?([^\s)>]+)>?(?:\s+\"[^\"]*\")?\)", document)


def is_ignored(path):
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--", str(path)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode in (0, 1), result.stderr
    return result.returncode == 0


def final_result():
    document = read_document("docs/avaliacao-v2.md")
    handoff = section(document, "Entrega à 006")
    final = re.search(r"^- Experimento final(.*?)(?=^- |\Z)", handoff, re.M | re.S)
    assert final, "Missing final experiment in handoff"
    commit = re.search(r"revisão\s*\n?\s*`([a-f0-9]{64})`", final.group(1)).group(1)
    cycles = re.findall(r"^### (CIC-\d+)\n(.*?)(?=^### |^## |\Z)", document, re.M | re.S)
    matches = [(name, body) for name, body in cycles if commit in body]
    assert len(matches) == 1, "Final revision must identify exactly one cycle"
    name, body = matches[0]
    means = re.search(r"- \*\*Médias\*\*: (.*?)(?=\n- )", body, re.S).group(1)
    scores = {key: float(re.search(rf"{re.escape(key)} (0\.\d+)", means).group(1))
              for key in ("Helpfulness", "Correctness", "F1-Score", "Clarity", "Precision")}
    overall = float(re.search(r"- \*\*Média geral\*\*: (0\.\d+)", body).group(1))
    return name, scores, overall


def evidence_rows(document):
    table = section(document, "EvidênciaPública")
    rows = []
    for line in table.splitlines():
        if re.match(r"\|\s*EV-\d+\s*\|", line):
            cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
            assert len(cells) == 7, f"Invalid evidence row: {line}"
            rows.append(dict(zip(("id", "tipo", "alvo", "endereco", "relacao",
                                  "conferencia_anonima", "sigilo"), cells)))
    return rows


@pytest.mark.parametrize("relative", ["README.md", "docs/entrega-publica.md"])
def test_cited_images_are_versionable_pngs(relative):
    document = read_document(relative)
    images = markdown_images(document)
    assert images, f"No screenshots cited in {relative}"
    for target in images:
        assert not re.match(r"https?://", target), "Evidence must be versioned locally"
        path = (ROOT / relative).parent / target
        assert path.is_file(), f"Missing image: {target}"
        assert path.read_bytes().startswith(PNG_SIGNATURE), f"Invalid PNG: {target}"
        assert not is_ignored(path.relative_to(ROOT)), f"Ignored image: {target}"


def test_one_public_dataset_url_reused_in_both_documents():
    sets = [set(DATASET_URL.findall(read_document(path)))
            for path in ("README.md", "docs/entrega-publica.md")]
    assert all(len(urls) == 1 for urls in sets), "Each document must cite one shared dataset URL"
    assert sets[0] == sets[1], "Reuse the original share token"


def test_evidence_covers_dataset_metrics_and_three_traces():
    rows = evidence_rows(read_document("docs/entrega-publica.md"))
    assert rows, "No accepted public evidence yet"
    assert len({row["id"] for row in rows}) == len(rows)
    assert sum(row["tipo"] == "link_dataset" for row in rows) == 1
    allowed = {"link_dataset", "link_experimento", "link_prompt", "link_trace", "screenshot", "fork"}
    for row in rows:
        assert row["tipo"] in allowed
        assert "smith.langchain.com/o/" not in row["endereco"]
        assert row["relacao"] and row["sigilo"]
        assert any(state in row["conferencia_anonima"] for state in ("visível", "parcial", "exige_login"))
        if any(state in row["conferencia_anonima"] for state in ("parcial", "exige_login")):
            assert any(other["tipo"] == "screenshot" and other["alvo"] == row["alvo"]
                       for other in rows), f"Missing screenshot fallback for {row['alvo']}"
    for target in ("dataset 15", "cinco médias", "trace simples", "trace médio", "trace complexo"):
        assert any(row["alvo"] == target for row in rows), f"Missing evidence: {target}"


def test_final_source_is_complete_and_approved():
    cycle, scores, overall = final_result()
    assert cycle == "CIC-03"
    assert len(scores) == 5 and all(0.8 <= value <= 1 for value in scores.values())
    assert 0.8 <= overall <= 1


def test_original_assignment_lines_are_preserved():
    current = set(read_document("README.md").splitlines())
    for line in base_readme().splitlines():
        if line.strip():
            assert line in current, f"Changed original requirement: {line}"


@pytest.mark.parametrize("title", ["Técnicas Aplicadas (Fase 2)", "Resultados Finais", "Como Executar"])
def test_required_sections_appear_once(title):
    assert read_document("README.md").splitlines().count("## " + title) == 1


def test_techniques_explain_actual_final_prompt():
    techniques = section(read_document("README.md"), "Técnicas Aplicadas (Fase 2)")
    prompt = yaml.safe_load(read_document("prompts/bug_to_user_story_v2.yml"))["bug_to_user_story_v2"]
    for name in ("Role Prompting", "Few-shot Learning"):
        assert name in techniques and name in prompt["techniques_applied"]
    for literal in ("Você é um Product Manager e analista de produto",
                    "Qual conteúdo da ficha fica errado e qual deveria aparecer?"):
        assert literal in techniques and literal in prompt["system_prompt"]
    for number in range(1, 4):
        assert f"Exemplo {number}" in techniques
    assert "CIC-02" in techniques and "CIC-03" in techniques
    assert "por" in techniques.lower(), "Explain why each technique was chosen"


def test_final_results_match_record_and_public_evidence():
    results = section(read_document("README.md"), "Resultados Finais")
    _, scores, overall = final_result()
    for label, value in scores.items():
        assert re.search(rf"\| {re.escape(label)} \| {value:.4f} \|", results), label
    assert re.search(rf"\| Média geral \| {overall:.4f} \|", results)
    for identifier in ("36a96c0540682ed6b8569487222b88e11d1889a3976b75fea83553dc662b696f",
                       "d864cfbb-6ab9-4901-ab06-62f68ccd96fc"):
        assert identifier in results
    rows = evidence_rows(read_document("docs/entrega-publica.md"))
    for row in rows:
        if row["tipo"] in ("link_dataset", "link_experimento"):
            assert row["endereco"] in results
    assert "smith.langchain.com/o/" not in results
    for name in ("CIC-01", "CIC-02", "CIC-03"):
        source = re.search(rf"^\| {name} \|.*$", read_document("docs/avaliacao-v2.md"), re.M).group(0)
        assert source in results, f"Missing original cycle row: {name}"
    for limitation in ("#14", "80%", "#8", "individuais", "v1", "v2"):
        assert limitation in results
    assert "comparação numérica da v1 não foi executada" in results


def test_execution_order_and_gate_inputs():
    execution = section(read_document("README.md"), "Como Executar")
    commands = ("python3 -m venv", "pip install -r requirements.txt",
                "python src/pull_prompts.py", "pytest tests/test_prompts.py",
                "python src/push_prompts.py", "AVALIACAO_DATASET", "AVALIACAO_GATE",
                "python src/evaluate.py", "AVALIACAO_AUDITORIA")
    positions = [execution.index(command) for command in commands]
    assert positions == sorted(positions)
    required = ("LANGSMITH_API_KEY", "LANGSMITH_PROJECT", "USERNAME_LANGSMITH_HUB",
                "LANGSMITH_TRACING", "LLM_PROVIDER", "LLM_MODEL", "EVAL_MODEL",
                "OPENAI_API_KEY", "GOOGLE_API_KEY", "LANGSMITH_WORKSPACE_ID",
                "AVALIACAO_CICLO", "AVALIACAO_CONDICAO", "AVALIACAO_HUB_COMMIT",
                "AVALIACAO_V2_FILE_SHA256", "AVALIACAO_V2_DEFINITION_SHA256",
                "AVALIACAO_DATASET_ID", "AVALIACAO_TESTES", "AVALIACAO_DASHBOARD",
                "AVALIACAO_CUSTO_ACUMULADO_USD", "AVALIACAO_EXIT_CODE", "pipefail")
    for name in required:
        assert name in execution, f"Missing execution input: {name}"


def test_reproduction_is_identified_when_experiment_exists():
    delivery = section(read_document("docs/entrega-publica.md"), "RegistroReprodução")
    results = section(read_document("README.md"), "Resultados Finais")
    match = re.search(r"REP-006_EXPERIMENT_ID: `([0-9a-f-]{36})`", delivery)
    if match:
        assert match.group(1) in results
        assert "reprodução, não é o experimento final" in results


def test_delivery_docs_contain_no_key_patterns():
    for path in ("README.md", "docs/entrega-publica.md"):
        assert not re.search(r"sk-|lsv2_|AIza", read_document(path)), path
