# Contrato operacional: entrega pública

**Feature**: [../spec.md](../spec.md) | **Modelo**: [../data-model.md](../data-model.md) |
**Pesquisa**: [../research.md](../research.md)

Interfaces externas: link público do dataset (LangSmith), links de prompt/traces, arquivos em
`docs/evidencias/`, o README e o fork público no GitHub. Este contrato define pré-condições,
provas e proibições; não altera avaliador, métricas, dados ou prompt.

## E01 — Pré-condições (somente leitura)

1. Entrada da 005 íntegra: v2 local com os hashes de `CIC-03`, HEAD do Hub `36a96c05…696f`
   público, experimento `d864cfbb…96fc` aprovado (reauditável pelo bloco da 005).
2. Quatro protegidos e v1 iguais ao manifesto; dataset local 15/5/7/3.
3. `git status` limpo em `dev`; nenhum segredo nos arquivos versionados.
Falha bloqueia a entrega; edição da v2 reabre a 005 (FR-010).

## E02 — Compartilhamento do dataset (uma vez)

1. Ler o estado de compartilhamento imediatamente antes; se já houver link, **reutilizá-lo**
   e registrar a origem, sem novo compartilhamento.
2. Somente com autorização explícita do autor no chat: executar uma vez o trecho do README
   (`share_dataset(dataset_name=…)["url"]`).
3. Registrar data e URL em `docs/entrega-publica.md`; reler e confirmar o mesmo token.
4. Proibido: `unshare_dataset`, novo `share_dataset`, compartilhar outro dataset.

## E03 — Conferência anônima

Em sessão sem login (navegador integrado, sem cookies do workspace; botão “Log in” visível):
o link do dataset mostra 15 exemplos e os experimentos da v2, incluindo `CIC-03` com as cinco
médias; os links do prompt e do fork abrem. Para cada alvo, registrar `visível`, `parcial` ou
`exige_login`. `parcial`/`exige_login` exige screenshot complementar (E04) e, para traces,
opcionalmente `share_run` nos três runs com autorização explícita.

## E04 — Screenshots

- Mínimo: dataset com 15 exemplos; experimento final com as cinco médias ≥ 0.8; um trace
  simples, um médio e um complexo de `CIC-03` mostrando entrada, resposta e feedbacks/juízes.
- PNG real em `docs/evidencias/avaliacao-v2-*.png`, fora de pastas ignoradas, conteúdo sem
  edição; preferir páginas públicas. Antes de versionar, inspeção de sigilo (nenhuma chave,
  e-mail, cabeçalho, configuração privada).
- Cada PNG é citado no README e em `docs/entrega-publica.md` com o alvo e o ID relacionado.

## E05 — README

- Seções do enunciado preservadas, sem edição de requisitos.
- `Técnicas Aplicadas (Fase 2)`: cada técnica (Role Prompting, Few-shot Learning), por que foi
  escolhida e trechos reais da v2 final; regras introduzidas pelos ciclos com justificativa.
- `Resultados Finais`: cinco médias e média geral de `CIC-03`, revisão `36a96c05`, tabela dos
  três ciclos, comparação qualitativa v1/v2 (o que mudou e por quê), links públicos (dataset,
  prompt, traces se houver), screenshots e limitações. Nenhuma nota ilustrativa como resultado;
  comparação numérica da v1 declarada como não executada.
- `Como Executar`: pré-requisitos, venv, dependências, variáveis (nomes, sem valores),
  provedor/modelos `COND-001`, comandos ordenados de cada fase (pull, testes, push, dataset,
  gate, avaliação, auditoria) e interpretação de sucesso/falha.

## E06 — Reprodução

Clone limpo do commit de entrega, venv novo, `.env` local copiado (nunca versionado),
comandos de `Como Executar` na ordem. Esperado: v1 com o mesmo hash; testes aprovados; push
com código 0 sem nova revisão (conteúdo idêntico); dataset `idêntico`; gate `gate_ok`;
avaliação e auditoria completas. O novo experimento é `REP-006`, não substitui `CIC-03`; seu
custo é somado. Reprovação ou divergência na reprodução é registrada como tal, sem
selecionar resultados (D09 da 005); não altera a revisão final sem novo ciclo da 005.

## E07 — Integridade e sigilo

Hashes dos protegidos e v1; 15/5/7/3; `git diff main..dev` vazio para os protegidos;
OpenAI/Gemini preservados; varredura de segredos em todos os arquivos versionados e
inspeção das PNG; `pytest -q`; `git diff --check`.

## E08 — Publicação Git

Somente com autorização explícita do autor: `git push origin dev`; atualizar `main` com
`dev` (fast-forward e push, ou PR no fork, à escolha do autor). Proibido force-push ou
reescrever histórico. Depois, conferência sem login de `main`: README, v2, código,
`docs/evidencias/` e links.

## E09 — Preservação

Nenhum experimento, dataset, commit do Hub, registro ou evidência anterior é apagado.
`results/` e `screenshots/` nunca são a única cópia de uma evidência.

## Matriz de falhas

| Situação | Ação |
| --- | --- |
| Dataset já compartilhado (link desconhecido) | Ler e reutilizar o link existente; não compartilhar de novo |
| `share_dataset` falha | Registrar categoria/status; não repetir às cegas; ler estado antes de nova tentativa autorizada |
| Link exige login ou não mostra traces | Screenshots complementares; `share_run` só com autorização |
| Screenshot com dado sensível | Descartar e recapturar sem o dado |
| Reprodução diverge do documentado | Corrigir o README ou registrar pendência; repetir a etapa afetada |
| Reprodução reprova ou fica incompleta | Registrar; não substituir `CIC-03`; decisão do autor |
| v2 precisa mudar | Reabrir a 005 (novo ciclo completo) antes de concluir a 006 |
| Push recusado ou não autorizado | Entrega fica `preparado`; nada é forçado |
