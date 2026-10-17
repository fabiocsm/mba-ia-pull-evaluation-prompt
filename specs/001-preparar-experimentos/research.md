# Pesquisa: preparação dos experimentos

**Data da consulta**: 2026-10-17. **Escopo**: spec 001, FR-001–FR-009.

Pesquisa de contratos locais e fontes oficiais, sem ler credenciais, instalar pacotes,
executar LLMs ou autenticar no LangSmith. Modelos e integração foram pesquisados por
agentes em paralelo; a pesquisa OpenAI seguiu também a skill `openai-docs`.

## 1. Ambiente e dependências — FR-008

**Decisão**: manter os oito pins de `requirements.txt`; tentar Python 3.11 em `venv`,
com ativação antes de instalar. Aceitar outro Python 3.10+ se a resolução e imports
forem comprovados. Registrar versões transitivas e hash do arquivo de requisitos.

**Razão**: o contrato exige isolamento e compatibilidade da infraestrutura existente.
Metadados de pacotes não substituem instalação, `pip check` e imports reais.

**Alternativas**: instalar globalmente prejudica reprodução; atualizar pins para
contornar erro pode alterar o contrato. Falha de dependência deve ser diagnosticada,
com interpretador compatível ou resolução explícita da divergência.

Fontes: [requirements.txt](../../requirements.txt),
[metadados LangSmith 0.13.0](https://pypi.org/pypi/langsmith/0.13.0/json) e
[metadados LangChain Core 1.6.4](https://pypi.org/pypi/langchain-core/1.6.4/json).

## 2. Configuração segura e identidade — FR-001, FR-002, FR-004, FR-005

**Decisão**: validar com `load_dotenv` e a precedência real de variáveis exportadas.
Registrar somente presença/validade das chaves e valores não secretos permitidos.
Usar `openai` inicialmente; a alternativa implementada chama-se `google`, não `gemini`.
`EVAL_MODEL` deve estar preenchido mesmo que coincida com `LLM_MODEL`.

**Razão**: `.env.example` usa `google` e não comprova a configuração local; o helper
`get_eval_llm` permite fallback se o modelo estiver vazio, insuficiente para FR-003.
A chave OpenAI existente deve ser reutilizada sem cópia para documentos ou terminal.

**Alternativas**: `cat .env`, exportação por `source` e dump de ambiente foram rejeitados
como mecanismos de diagnóstico. Dar acesso a um prompt público não comprova que a
chave pertence ao workspace/handle esperado.

**Integração escolhida**: combinar contexto autenticado de workspace/handle obtido
pela interface ou CLI com o `tenant_id` do projeto retornado pelo SDK. Quando não
houver uma interface pública adequada para settings, usar a interface autenticada;
não presumir métodos inexistentes ou depender de métodos privados.

Fonte local: [utils.py](../../src/utils.py) e [.env.example](../../.env.example).

## 3. Contratos LangSmith e CLI — FR-002, FR-008

**Decisão**: inspecionar a versão instalada antes de executar integrações. O SDK
0.13.0 oferece `read_project(project_name=...)`, `get_prompt(...)` e
`pull_prompt_commit(...)`. `get_prompt` fornece `last_commit_hash`; `push_prompt`
aceita descrição, tags e `is_public`, mas não parâmetro arbitrário `metadata`.
Não existem `Client.get_settings()` nem `Client.list_workspaces()` nessa versão.
[Cliente oficial v0.13.0](https://github.com/langchain-ai/langsmith-sdk/blob/v0.13.0/python/langsmith/client.py).

**Razão**: preservar os contratos da infraestrutura e evitar código apoiado em
assinaturas supostas. Recuperar e serializar a semente cabe à 002; publicar e provar
escrita cabe à 004. Nesta feature, basta confirmar assinaturas e tipos esperados.

**Alternativas**: não usar APIs privadas como contrato; evitar publicar prompt de
teste ou criar dataset para validar acesso. CLI complementa, não substitui scripts.
Consultar ajuda raiz e de cada subcomando, autenticar o subprocesso via ambiente
carregado com dotenv e filtrar os campos antes de guardar sua saída. Não usar comandos
que revelem token. Guardar versão e seleção de workspace/endpoint sem credenciais.

## 4. Modelos candidatos — FR-003, FR-004

**Decisão de planejamento**: candidato `gpt-4.1-2025-04-14` para geração e avaliação,
via utilitários existentes. A página oficial lista Chat Completions e snapshot.
[GPT-4.1](https://developers.openai.com/api/docs/models/gpt-4.1).
O guia oficial contém uso de GPT-4.1 com temperatura zero em Chat Completions.
[Exemplo oficial](https://developers.openai.com/api/docs/guides/speech-to-text).

**Razão**: reduzir variáveis iniciais e usar um modelo sem configuração adicional de
raciocínio no wrapper protegido. É candidato para o desafio, sem acesso da conta
comprovado. Snapshot identifica a versão; não garante respostas idênticas.

**Validade temporal**: a família GPT-4.1 está depreciada, com desligamento anunciado
para 14/01/2027. Reconsultar antes da execução; selecionar alternativa compatível
se necessário, registrando nova condição. [Depreciações oficiais](https://developers.openai.com/api/docs/deprecations).

**Alternativas**: `gpt-4.1-mini-2025-04-14` na geração reduz custo; acesso, qualidade e
compatibilidade ainda exigem prova. Sua página publica US$ 0,40 de entrada e US$ 1,60
de saída por milhão de tokens. [GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini).
Não escolher automaticamente modelo mais recente que exija opções ausentes em
`utils.py`. Preservar Google como alternativa, consultando documentação oficial e
provando temperatura zero caso seja efetivamente selecionado.

**Prova na implementação**: uma chamada curta por papel com `get_llm(temperature=0)`
e `get_eval_llm(temperature=0)`, mensagens System/User e texto sem dados sensíveis.
Registrar resposta não vazia, uso disponível e trace no projeto correto. Mesmo modelo
em ambos os papéis não elimina uma das duas verificações. Não modificar os helpers.

## 5. Integridade e origem — FR-006, FR-007

**Decisão**: manifesto com commit Git completo, estado inicial, revisão do repositório
base, hashes SHA-256 dos quatro arquivos e inventário dos casos por linha física,
complexidade e hashes de conteúdo. Comparar bytes com a origem e repetir comparação
antes de encerrar. Divergência existente é impedimento, não baseline aprovado.

**Razão**: hash relativo apenas ao checkout não comprova que o material fornecido foi
preservado. O JSONL atual contém `inputs.bug_report`, `outputs.reference` e
`metadata.complexity`: 15 registros, `simple=5`, `medium=7`, `complex=3`.
O arquivo completo protege também referências e demais metadados.

**Alternativas**: apenas contar linhas não detecta edição de referências; depender
só do diff final perde modificações já commitadas. Conferir no GitHub `fork`,
visibilidade e `parent.full_name`; remote local sozinho não prova fork público.

**Contrato transversal**: o avaliador envia ao dataset remoto somente `inputs` e
`outputs`, e reutiliza dataset pelo nome sem comparar seu conteúdo. A 005 deve auditar
os pares de entrada/referência contra o manifesto; não exigir complexidade remota nem
alterar o avaliador para incluí-la. Fonte: [evaluate.py](../../src/evaluate.py).

## 6. Custo e condições comparáveis — FR-009

**Decisão**: planejar 3–5 ciclos, separando estimativa de tokens/preços, consumo reportado
e cobrança efetiva quando disponível. São 15 gerações e três juízes por exemplo:
60 chamadas/ciclo, 180–300 nos ciclos, mais duas verificações mínimas, retries e extras.
Helpfulness e Correctness são derivadas; não acrescentar dois juízes ao cálculo.
Fonte: [plano mestre, seção 7](../../plan/plano-implementacao.md).

Para preços de entrada/saída por milhão `Pg_in`, `Pg_out`, `Pj_in`, `Pj_out`, e tokens
médios estimados por chamada `Ig`, `Og`, `Ij`, `Oj`:

```text
C_ciclo = (15 × (Ig × Pg_in + Og × Pg_out)
         + 45 × (Ij × Pj_in + Oj × Pj_out)) / 1.000.000
C_total_estimado = ciclos × C_ciclo + C_verificacoes + C_retries + C_extras
```

Hipóteses ilustrativas, não medidas: geração 4.000 tokens de entrada/700 de saída;
juiz 2.500/200; sem desconto de cache ou Batch. GPT-4.1 custa US$ 2/8 por milhão
(entrada/saída). [Preço oficial do modelo](https://developers.openai.com/api/docs/models/gpt-4.1).
Resultado calculado: US$ 0,501/ciclo; US$ 1,503–2,505 para 3–5 ciclos. Reserva de
30%: US$ 1,954–3,257, antes das chamadas mínimas e extras. Recalcular com o tamanho
real da v2, relatos e referências, especialmente os complexos. Os juízes diferem em
tamanho: o valor médio deve ser refinado por juiz na execução.

**Alternativas**: baseline numérica da v1 é opcional e adiciona chamadas; não está
incluída nesta estimativa. Testes estruturais não usam rede. Não executar ciclos
redundantes apenas para preencher contagem, nem omitir falhas/retries do consumo.
US$ 1–5 é orientação, não teto automático nem gasto observado.

## Resolução das incertezas

As escolhas de desenho estão resolvidas. Permanecem para execução: instalação real,
validade de chaves, identidade/workspace, fork público, acesso aos modelos, traces,
compatibilidade das chamadas e consumo efetivo. Esses itens são resultados a medir,
não lacunas de requisitos. Nenhum é declarado comprovado por este planejamento.
