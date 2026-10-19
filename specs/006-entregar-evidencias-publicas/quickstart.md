# Quickstart: validar a entrega pública

**Feature**: [spec.md](spec.md) | **Contrato**: [contracts/entrega-publica.md](contracts/entrega-publica.md)

Guia de validação, não implementação. Executar da raiz com o venv da 001, salvo na
reprodução (W07), que usa clone e venv novos. Ações externas (W03, W05 com `share_run`, W09)
exigem autorização explícita do autor no chat.

```bash
source venv/bin/activate
```

## W01 — Entrada da 005 (E01)

```bash
shasum -a 256 src/evaluate.py src/metrics.py src/utils.py datasets/bug_to_user_story.jsonl prompts/bug_to_user_story_v1.yml prompts/bug_to_user_story_v2.yml
```

Esperado: protegidos iguais ao [manifesto](../../docs/integridade-inicial.json), v1
`2cddcf8f…0d70`, v2 `692df6ae…8974`; `get_prompt` com HEAD `36a96c05…696f` público;
`git status` limpo. Opcional: reexecutar o bloco `AVALIACAO_AUDITORIA` da
[005](../../docs/avaliacao-v2.md#bloco-avaliacao_auditoria--c04c07) sobre `CIC-03` → `aprovado`.

## W02 — Testes offline da entrega

```bash
pytest tests/test_delivery.py -v
```

Esperado: seções obrigatórias e enunciado preservados; imagens citadas existem, são PNG e
não estão ignoradas; números de `Resultados Finais` iguais ao registro final; um único link
público de dataset; nenhum padrão de chave.

## W03 — Compartilhamento único do dataset (E02)

Ler o estado; se não compartilhado e com autorização, executar uma vez o trecho do README.
Esperado: URL `https://smith.langchain.com/public/<token>/d` registrada; nova leitura
devolve o mesmo token. Nunca repetir.

## W04 — Conferência anônima (E03)

No navegador integrado, sem login: link do dataset (15 exemplos, experimentos, médias de
`CIC-03`), URL pública do experimento `CIC-03` alcançada por ele, prompt público, traces com
os julgamentos (runs do avaliador). Esperado: cada alvo `visível`, ou `parcial`/`exige_login`
com complemento em W05.

## W05 — Screenshots (E04)

Esperado: PNG em `docs/evidencias/avaliacao-v2-*.png` para dataset, cinco médias e três
traces (#1 simple, #10 medium, #14 complex), legíveis, sem dado sensível, citados no README.

## W06 — README (E05)

Esperado: `Técnicas Aplicadas (Fase 2)`, `Resultados Finais` e `Como Executar` completas;
enunciado intacto; nenhuma nota ilustrativa como resultado; limitações de `CIC-03` presentes.

## W07 — Reprodução limpa (E06)

```bash
git clone . "$TMPDIR/rep-006" && git -C "$TMPDIR/rep-006" checkout "$COMMIT_ENTREGA" && cd "$TMPDIR/rep-006" && python3.11 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && pip check
```

`COMMIT_ENTREGA` é o commit registrado em T016; sem commits autorizados, usar cópia da árvore
de trabalho sem `venv/`, `.env`, `results/` e `screenshots/`. Copiar o `.env` local e seguir
`Como Executar`, incluindo o bloco `PRESERVAR_BASELINE_V1`: datas/estatísticas mudam
no pull; guardar a coleta e comparar conteúdo/revisão antes de manter a v1 auditada.
Esse ajuste foi validado em REP-006, sem mudar o script nem a referência. O push reaplica descrição/tags sem nova revisão (HEAD `36a96c05`). Esperado: todos os passos com o
código documentado; experimento `REP-006` auditado, registrado com custo e identificado no
README; divergências resolvidas ou pendentes explícitas. SC-004 exige ainda `REP-006B`: um
segundo executor segue `Como Executar` a partir do fork com credenciais próprias; sem ele, o
SC-004 fica pendente e declarado.

## W08 — Integridade final (E07)

Repetir W01, `git diff main..dev -- src/evaluate.py src/metrics.py src/utils.py datasets/`
(vazio), varredura de segredos, `pytest -q`, `git diff --check`.

## W09 — Publicação e conferência do fork (E08)

Com autorização: push de `dev` e atualização de `main`. Esperado: sem login,
`https://github.com/fabiocsm/mba-ia-pull-evaluation-prompt` mostra em `main` o README final,
`prompts/bug_to_user_story_v2.yml` igual a `692df6ae…8974`, código e `docs/evidencias/`.
