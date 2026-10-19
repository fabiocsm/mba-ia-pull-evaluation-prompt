# Implementation Plan: Recuperação fiel do prompt original

**Branch**: `dev` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

**Input**: `specs/002-recuperar-prompt-v1/spec.md`, Fase 2 e R03/R12 do
[plano mestre](../../plan/plano-implementacao.md).

**Estado**: planejamento concluído; implementação e pull real pendentes.
O setup retornou `BRANCH=002-recuperar-prompt-v1` como identificador da feature;
a branch Git é `dev`. O ponteiro local `.specify/feature.json` seleciona a 002.
Nenhuma branch foi criada ou trocada.

## Summary

Implementar as funções existentes de `src/pull_prompts.py` para recuperar
`leonanluppi/bug_to_user_story_v1` com `langsmith.Client`, conferir sua representação
e persistir `prompts/bug_to_user_story_v1.yml`. Preservar texto, espaços, quebras,
papéis, ordem, variável e metadados aplicáveis; nenhuma melhoria pertence à v1.

Reutilizar `save_yaml` em arquivo temporário no diretório de destino, reler e
comparar antes da substituição atômica. Retornar sucesso somente após persistência;
falhas devem ser identificáveis pela automação, sem expor credenciais ou destruir
a cópia anterior. Registrar revisão do objeto recuperado, hash local e comparação
em documentação versionada. O YAML fornecido atualmente não comprova um pull real.

Fora do escopo: criar v2, implementar seus seis testes, publicar prompts, executar
LLMs/experimentos ou compartilhar dataset. A spec 001 comprova os pré-requisitos
na [matriz atual](../../docs/preparacao.md#matriz-atual); acesso efetivo à semente
e fidelidade da exportação ainda precisam ser comprovados nesta feature.

## Technical Context

**Language/Version**: Python 3.10+; ambiente existente CPython 3.11.14 em `venv/`.

**Primary Dependencies**: pins existentes `langsmith==0.13.0`,
`langchain-core==1.6.4`, `python-dotenv==1.2.3`, `pyyaml==6.0.3`, `pytest==9.1.1`.
Reutilizar `Client`, tipos de `ChatPromptTemplate`, `save_yaml`, `check_env_vars`
e `print_section_header`; `pathlib`, `tempfile`, `os` e `hashlib` da biblioteca padrão.
Não modificar requisitos nem utilitários protegidos.

**Storage**: YAML UTF-8 com definição `bug_to_user_story_v1`; temporário adjacente
removido em falha anterior à substituição; registro em `docs/recuperacao-v1.md`,
ligado pelo README e produzido na implementação, sem credenciais.

**Testing**: cenários offline em `tests/test_pull_prompts.py`, com cliente e falhas
de I/O controlados, mais um pull real e comparação com a mesma revisão remota.
Os seis testes de `tests/test_prompts.py` continuam reservados à 003.

Validação incremental: V01–V03 aprovados antes do primeiro pull/comparação real
da US1; V04–V11 e suíte completa aprovados na US2 antes do aceite final. Repetir
a prova real se as correções posteriores afetarem sucesso/serialização; o MVP
da US1 não comprova SC-002 nem conclui a feature.

**Target Platform**: CLI local, executado da raiz; validação inicial em macOS/POSIX.
Usar APIs portáveis, sem alegar reprodução em outro sistema operacional.

**Project Type**: script CLI existente; sem serviço, banco ou framework adicional.

**Performance Goals**: sem meta de latência; uma semente por execução. Nenhuma
chamada a modelo, custo de inferência esperado zero nesta etapa. As 3–5 iterações
com estimativa de US$ 1–5 continuam no planejamento da 001/005.

**Constraints**: origem/destino obrigatórios; opt-in público explícito;
sem interpolação ou normalização do texto; nenhuma omissão silenciosa;
falha antes do commit local conserva o arquivo anterior. Quatro arquivos protegidos,
15 exemplos/referências (5/7/3) e suporte OpenAI/Google permanecem intactos.

**Scale/Scope**: duas funções existentes, um YAML, testes do pull e documentação.
Aceitar a representação System/Human textual descrita no contrato; rejeitar
estruturas não representáveis, sem converter arbitrariamente seu conteúdo.

## Constitution Check

Gate antes da Fase 0 e revisto após a Fase 1. PASS é conformidade do desenho,
não comprovação de acesso ao Hub ou de execução da implementação.

| Regra | Antes da pesquisa | Após o desenho |
| --- | --- | --- |
| I — Integridade e escopo | PASS: somente recuperação da v1 | PASS: arquivos permitidos, rejeição sem reescrita, hashes protegidos |
| II — Engenharia verificável | PASS: melhorias reservadas à v2 | PASS: variável literal, nenhum requisito de qualidade da v2 aplicado à v1 |
| III — Fonte e rastreabilidade | PASS: cliente e origem obrigatórios | PASS: opt-in, revisão do objeto, metadados separados e comparação da mesma revisão |
| IV — Avaliação íntegra | PASS: sem notas nesta feature | PASS: sem LLM, dataset, métrica ou resultado presumido |
| V — Reprodução | PASS: comando existente e falhas verificáveis | PASS: contrato CLI/YAML, matriz de falhas e evidência versionada |
| Stack/configuração | PASS: ambiente da 001, pins preservados | PASS: dotenv e utilitários reutilizados, temporário sem editar `utils.py` |

Não há violação ou esclarecimento de requisito pendente. Modelos já selecionados
na 001 não são reescolhidos nem invocados aqui. Credenciais/acesso e forma real da
semente são verificações de execução: incompatibilidade bloqueia o pull e deve ser
registrada antes de qualquer mudança de contrato.

## Project Structure

### Documentation (this feature)

```text
specs/002-recuperar-prompt-v1/
├── spec.md
├── checklists/requirements.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/recuperacao-v1.md
├── quickstart.md
└── tasks.md
```

`tasks.md` foi gerado por `$speckit-tasks` em 2026-10-18, após este planejamento;
suas atividades e a implementação continuam pendentes.

### Source Code (repository root)

```text
src/pull_prompts.py                 # implementar as funções existentes
prompts/bug_to_user_story_v1.yml     # substituir somente após pull validado
tests/test_pull_prompts.py          # regressões de fidelidade e falhas
docs/recuperacao-v1.md               # evidência real, produzida na implementação
README.md                          # acrescentar execução/ligação ao registro
```

**Structure Decision**: manter scripts e formato existentes. Auxiliares locais
podem morar em `pull_prompts.py`; não criar camada genérica de persistência ou SDK.
Não alterar `src/utils.py`, `src/evaluate.py`, `src/metrics.py`, dataset ou v2.

## Phase 0 — Pesquisa e decisões

[research.md](research.md) resolve contratos do SDK, representação sem perdas,
metadados, escrita segura e diagnóstico. Pesquisa do SDK delegada conforme a skill;
inspeção local e documentação oficial, sem consultar a semente ou ler `.env`.

Decisões: revisão extraída de `prompt.metadata`; metadados de repositório tratados
como snapshot separado; representação estrita System/Human; validação antes de
escrever; `save_yaml` no temporário seguido de releitura e `os.replace`.

## Phase 1 — Desenho e sequência de execução

1. Conferir integridade e prontidão da 001. Carregar configuração sem sobrescrever
   variáveis exportadas; checar presença/validade sem imprimir valores secretos.
2. Criar `Client` e recuperar a origem com `include_model=False`, `skip_cache=True`
   e `dangerously_pull_public_prompt=True`. Validar tipo, mensagens e revisão.
3. Obter `get_prompt` para metadados do repositório, registrando instante da leitura.
   Falha de consulta impede sucesso; campos opcionais ausentes não são inventados.
4. Extrair `.prompt.template` sem `format`, `invoke`, `strip` ou concatenação;
   validar toda a estrutura antes de construir o mapeamento descrito no contrato.
5. Criar temporário único no mesmo diretório, chamar `save_yaml`, reler com
   `yaml.safe_load` e comparar integralmente com o mapeamento esperado. Comparar
   também templates e variáveis após reconstrução offline do formato suportado.
6. Substituir destino com `os.replace`, ponto de commit. Não executar validação
   falível obrigatória após esse ponto: diagnósticos/evidência posteriores não
   devem converter persistência concluída em falsa falha da recuperação.
7. Informar origem, revisão, destino e persistência; retornar 0. Antes do commit,
   qualquer erro retorna 1 e conserva os bytes antigos; limpar o temporário.
8. Na validação real, reler a revisão explicitamente fixada, comparar o YAML e
   registrar resultado/hash/limitações no README e em `docs/recuperacao-v1.md`.
   Conferir hashes dos protegidos contra o manifesto da 001.

Campos em [data-model.md](data-model.md), interfaces em
[contracts/recuperacao-v1.md](contracts/recuperacao-v1.md) e validação em
[quickstart.md](quickstart.md). Artefatos de evidência serão produzidos na execução;
nenhum hash remoto, sucesso de pull ou teste é presumido neste plano.

## Rastreabilidade e aceite

| Requisito | Plano mestre | Decisão/artefato | Verificação |
| --- | --- | --- | --- |
| FR-001 | R03 | Origem fixa, `Client.pull_prompt` com opt-in | V01/V02/V12; SC-001 |
| FR-002 | R03 | YAML obrigatório e resultado CLI | V01/V08/V12; SC-001 |
| FR-003 | R03 | Templates intactos e metadados identificados | V02–V05/V12; SC-001 |
| FR-004 | R12 | Sem interpolação, normalização ou melhorias | V02/V03/V12; SC-003 |
| FR-005 | R03 | Falhas categorizadas e código 1 | V04–V11; SC-002 |
| FR-006 | R03/R12 | Temporário, round-trip e substituição atômica | V06–V11; SC-002 |

Os IDs V01–V12 são locais ao [quickstart](quickstart.md), distintos dos IDs da 001.
Testes offline comprovam cenários controlados; SC-001 exige recuperação real.
SC-002 só é atendido com todos os cenários de falha exercitados; SC-003 exige
comparação das mensagens e revisão do diff. Nenhum deles é nota acadêmica.

## Complexity Tracking

Sem violações a justificar. Temporário adjacente é necessário para FR-006 porque
o utilitário existente abre com `w`; não exige alterar o arquivo protegido.

## Conferência do planejamento

`.specify/extensions.yml` ausente nas verificações antes/depois: nenhum hook
registrado para executar. Scripts de pré-requisitos e resolução de paths confirmam
a 002 ativa. Links locais, sintaxe dos dois blocos Python do guia e ausência de
placeholders conferidos; `git diff --check` aprovado. Os quatro hashes protegidos
permanecem iguais ao manifesto da 001. Essas conferências validam os documentos;
testes da futura implementação e recuperação real continuam pendentes.
