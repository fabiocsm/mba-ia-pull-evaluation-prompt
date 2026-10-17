# Plano de implementação e validação

**Projeto:** Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

**Data:** 2026-10-17

**Estado:** planejamento; as atividades de implementação e avaliação abaixo estão pendentes.

## 1. Objetivo e referências

Entregar um fork público, executável e documentado que faça pull do prompt semente,
produza uma versão otimizada, publique-a no LangSmith e demonstre, por experimentos
reais, pontuação mínima de `0.8` em cada uma das cinco métricas e na média geral.

Fontes de requisitos e contratos:

- [README do desafio](../README.md): requisitos acadêmicos e entregáveis.
- [Constituição v1.0.0](../.specify/memory/constitution.md): regras e limites do projeto.
- [AGENTS.md](../AGENTS.md): orientações operacionais e disponibilidade do LangSmith CLI.
- [Avaliador](../src/evaluate.py), [métricas](../src/metrics.py) e
  [utilitários](../src/utils.py): contratos fornecidos, que devem ser preservados.

Este documento é o plano mestre solicitado para a pasta `plan`. Na execução do SDD,
ele deve orientar a especificação e os artefatos da feature em `specs/`, gerados pelas
skills locais. Não substitui a especificação nem pressupõe que esses artefatos já existam.

**Desdobramento SDD (2026-10-17):** a avaliação e a divisão deste plano em seis specs
estão no [índice de especificações](../specs/README.md), com descrições de entrada,
dependências, contratos e cobertura de R01–R18. Cada spec tem `spec.md` e checklist de
qualidade revisados. Planos técnicos, tarefas, implementação e avaliações reais
permanecem pendentes; o conteúdo operacional deste plano continua sendo referência.

## 2. Diagnóstico do repositório

| Item | Situação observada | Trabalho necessário |
| --- | --- | --- |
| Pull | Duas funções com corpo `...` | Implementar conexão, recuperação e persistência |
| Push | Três funções com corpo `...` | Implementar validação, publicação e tratamento de falhas |
| Prompt v1 | YAML inicial presente | Recuperar do Hub e conservar o conteúdo como referência |
| Prompt v2 | Arquivo ausente | Criar e refinar o prompt otimizado |
| Testes | Seis métodos com `pass` | Implementar verificações reais sobre a v2 |
| Avaliador e métricas | Implementações fornecidas | Executar e inspecionar resultados, sem alterar arquivos |
| Dataset | 15 exemplos; 5 simples, 7 médios, 3 complexos | Preservar conteúdo e conferir a cópia remota |
| Spec Kit | Inicializado; constituição criada | Criar especificação, plano técnico e tarefas da feature |
| Configuração | `.env` existe; chave OpenAI informada pelo autor | Validar configuração sem expor valores secretos |
| LangSmith CLI | Comando `langsmith` disponível | Usar para inspeção e diagnóstico quando necessário |
| GitHub | `origin` aponta para `fabiocsm/mba-ia-pull-evaluation-prompt` | Confirmar visibilidade pública e vínculo de fork |

Os exemplos de notas do README são ilustrativos. Ainda não há, neste planejamento,
comprovação de autenticação, publicação, modelos disponíveis ou métricas aprovadas.

## 3. Escopo e decisões de implementação

### Arquivos a implementar

- `src/pull_prompts.py`.
- `src/push_prompts.py`.
- `prompts/bug_to_user_story_v2.yml`.
- `tests/test_prompts.py`.
- `README.md`, mantendo o enunciado original e acrescentando a documentação da entrega.
- Documentação de SDD e evidências necessárias à avaliação.

`prompts/bug_to_user_story_v1.yml` será atualizado exclusivamente pelo pull da semente.
Não refatorar a v1 para apresentar melhorias que pertencem à v2.

### Arquivos e comportamentos protegidos

Preservar integralmente `src/evaluate.py`, `src/metrics.py`, `src/utils.py` e
`datasets/bug_to_user_story.jsonl`, incluindo o suporte a OpenAI e Gemini.
Não alterar referências, fórmulas, agregações, limiar, juízes ou concorrência para elevar notas.

Registrar o commit de referência e os hashes desses quatro arquivos no início da execução.
Comparar novamente na revisão final, inclusive se houver commits intermediários.

### Abordagem técnica

- Manter scripts CLI simples, os contratos dos esqueletos e os utilitários existentes.
- Usar `langsmith.Client` para pull/push e `ChatPromptTemplate` para System/User.
- Usar YAML como artefato local versionado e Prompt Hub como origem do prompt avaliado.
- Preferir OpenAI inicialmente, aproveitando a credencial existente; preservar Gemini.
- Selecionar os modelos na preparação, após consulta à documentação oficial e confirmação
  de acesso e compatibilidade com `temperature=0`. Não fixar nomes por suposição.
- Começar com Few-shot Learning e Role Prompting. Acrescentar Skeleton of Thought para
  padronizar a estrutura da resposta; registrar as três técnicas apenas se aplicadas.
- Manter o mesmo provedor, modelos e dataset durante a comparação das revisões do prompt.
  Uma mudança de modelo exige registro e identificação de uma nova condição experimental.

## 4. Verificação da constituição

| Princípio | Aplicação neste plano | Evidência de conformidade na execução |
| --- | --- | --- |
| I. Integridade e escopo | Alterar apenas os entregáveis previstos | Diff e hashes dos arquivos protegidos |
| II. Engenharia de prompts | Few-shot, persona, formato, regras e casos de borda | YAML, testes e exemplos no README |
| III. Rastreabilidade | Publicar sob `fabiocsm` e avaliar a revisão do Hub | Commit do Hub, URL e ID de experimento |
| IV. Avaliação íntegra | Preservar dados e atingir cada métrica | Feedback completo dos 15 exemplos |
| V. Entrega reproduzível | Testes, comandos e evidências públicas | Pytest aprovado, README e inspeção sem login |

O desenho proposto não requer exceções à constituição. A confirmação de execução depende
das validações de cada fase; este quadro não declara implementação concluída.

## 5. Fases de execução

### Fase 0 — Especificação e tarefas SDD

**Dependência:** nenhuma etapa de implementação.

- [x] Usar `$speckit-specify` para especificar o fluxo completo e os critérios da seção 6,
  desdobrados nas [seis specs iniciais](../specs/README.md).
- [ ] Usar `$speckit-clarify` somente para lacunas que alterem o comportamento ou o aceite.
- [ ] Usar `$speckit-plan` para detalhar contratos YAML/CLI, decisões e guia de execução.
- [ ] Usar `$speckit-tasks` para decompor as fases em tarefas dependentes e verificáveis.
- [ ] Usar `$speckit-analyze` para conferir consistência e cobertura antes de implementar.

**Saída:** especificação, decisões técnicas e tarefas rastreáveis aos requisitos deste plano.
Não criar uma interface web, serviços ou persistência adicionais para este desafio.

### Fase 1 — Preparação, credenciais e compatibilidade

**Dependência:** Fase 0.

- [ ] Registrar a referência Git e a integridade dos quatro arquivos protegidos.
- [ ] Confirmar que o repositório remoto é um fork público do repositório base.
- [ ] Selecionar um interpretador Python 3.10+ compatível com as dependências fixadas.
- [ ] Criar/ativar `venv`, instalar `requirements.txt` e executar `python -m pip check`.
- [ ] Validar presença de `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`,
  `USERNAME_LANGSMITH_HUB=fabiocsm`, `LANGSMITH_TRACING=true`, `LLM_PROVIDER=openai`,
  `LLM_MODEL`, `EVAL_MODEL` e `OPENAI_API_KEY`, sem imprimir segredos.
- [ ] Reutilizar a chave OpenAI existente. Confirmar acesso ao workspace e ao handle
  informado; não tentar criar um novo handle.
- [ ] Consultar documentação oficial dos modelos e conferir chamadas mínimas de geração
  e avaliação com o provedor configurado, mensagens compatíveis e `temperature=0`.
- [ ] Conferir os contratos da versão instalada do SDK: retorno do pull, serialização
  das mensagens, parâmetros do push, metadados e recuperação da revisão publicada.
- [ ] Consultar `langsmith --help` e a ajuda de cada subcomando usado. O CLI pode apoiar
  a inspeção de projeto, dataset, prompt, experimento e trace; seu ambiente precisa
  receber a autenticação, pois não se deve presumir leitura automática do `.env`.

**Critério de saída:** ambiente funcional, configuração válida, contratos confirmados
e modelos escolhidos e registrados. Se houver incompatibilidade, registrar o erro e
resolver o pré-requisito sem modificar silenciosamente os arquivos protegidos.

### Fase 2 — Pull real e preservação da v1

**Dependência:** Fase 1.

- [ ] Implementar `pull_prompts_from_langsmith()` e `main()` nos esqueletos existentes.
- [ ] Validar as variáveis necessárias ao pull antes da chamada remota.
- [ ] Recuperar `leonanluppi/bug_to_user_story_v1` com
  `dangerously_pull_public_prompt=True`.
- [ ] Extrair as mensagens System/User e seus templates sem interpolar `{bug_report}`.
  Validar o tipo e a estrutura recebidos, sem descartar silenciosamente mensagens.
- [ ] Persistir a definição `bug_to_user_story_v1` no YAML local usando `save_yaml`.
  Conservar os metadados retornados que forem aplicáveis ao formato do projeto.
- [ ] Informar origem, destino e sucesso; retornar código diferente de zero em falha de
  credenciais, acesso, formato ou escrita. Não registrar credenciais em mensagens.
- [ ] Executar o script e comparar as mensagens salvas com o conteúdo real recuperado.

**Critério de saída:** `python src/pull_prompts.py` termina com sucesso e produz YAML
válido, não vazio e equivalente às mensagens da semente, mantendo `{bug_report}`.

### Fase 3 — Prompt v2 e estratégia de otimização

**Dependência:** Fase 2.

- [ ] Analisar os problemas reais da v1: instruções vagas, repetição de entrada,
  ausência de exemplos, falta de critérios de resposta e de tratamento de ambiguidades.
- [ ] Criar `prompts/bug_to_user_story_v2.yml`, com a chave `bug_to_user_story_v2` e
  campos `description`, `system_prompt`, `user_prompt`, `version`, `tags` e
  `techniques_applied`; usar `version: v2`.
- [ ] Definir persona de Product Manager/analista de produto, contexto e objetivo.
- [ ] Especificar saída em português, Markdown e User Story no formato
  “Como... eu quero... para que...”, com critérios de aceitação verificáveis.
- [ ] Usar estrutura proporcional ao relato: casos simples com resposta concisa;
  relatos complexos com cobertura de todos os problemas e critérios agrupados.
- [ ] Incluir 2–3 exemplos próprios de entrada/saída, cobrindo relatos simples,
  ambíguos e/ou com múltiplos problemas. Não copiar as respostas do dataset como
  exemplos de treinamento nem inserir respostas específicas aos casos de avaliação.
- [ ] Aplicar Few-shot, Role Prompting e o esqueleto de resposta. Separar regras e
  exemplos no System e entrada no User, com `{bug_report}` como única variável exigida.
- [ ] Tratar entrada vazia, informação insuficiente, problemas múltiplos, logs e
  instruções conflitantes dentro do relato. Distinguir fatos, dúvidas e recomendações;
  não inventar métricas, causas, arquitetura ou decisões de negócio como fatos.
- [ ] Validar carregamento YAML, campos não vazios, ausência de pendências e
  `ChatPromptTemplate.input_variables == ["bug_report"]` após montar as mensagens.
  Escapar chaves literais de exemplos quando necessário para evitar variáveis espúrias.
- [ ] Documentar técnicas e exemplos na seção `Técnicas Aplicadas (Fase 2)` do README.

**Critério de saída:** v2 renderizável com um relato qualquer, com técnicas realmente
presentes e regras verificáveis, pronta para testes e publicação.

### Fase 4 — Testes estruturais e contratos de erro

**Dependência:** Fase 3; validações das Fases 2 e 5 podem reutilizar esta etapa.

Implementar os seis testes obrigatórios carregando o YAML v2 real:

| Teste | Verificação efetiva |
| --- | --- |
| `test_prompt_has_system_prompt` | Campo existe, é texto e não contém apenas espaços |
| `test_prompt_has_role_definition` | Persona explícita no conteúdo do System |
| `test_prompt_mentions_format` | Instrução explícita de Markdown ou User Story padrão |
| `test_prompt_has_few_shot_examples` | Pares completos de entrada/saída, além do nome da técnica |
| `test_prompt_no_todos` | Nenhuma pendência no texto dos prompts, incluindo `[TODO]` |
| `test_minimum_techniques` | Lista com duas ou mais técnicas distintas; inclui Few-shot |

- [ ] Remover os corpos vazios e usar fixtures/helpers para carregar o artefato correto.
- [ ] Validar também System/User, campos e variável de entrada, sem dependência de rede.
- [ ] Cobrir falhas concretas dos scripts quando necessário: YAML inválido, credencial
  ausente, template incompatível e falha do cliente ou da persistência.
- [ ] Usar dublês apenas para testar integração e erros dos scripts; notas acadêmicas
  e evidências finais devem vir de chamadas reais.
- [ ] Executar `pytest tests/test_prompts.py -v` e conferir que os seis testes foram
  coletados e executados, sem `skip`, `xfail` ou aprovação incondicional.

**Critério de saída:** seis testes obrigatórios efetivos aprovados e contratos locais
validados. Esse resultado não substitui a aprovação nas métricas.

### Fase 5 — Push público e conferência do round-trip

**Dependência:** Fases 3 e 4.

- [ ] Implementar `validate_prompt()`, `push_prompt_to_langsmith()` e `main()`.
- [ ] Reutilizar `load_yaml`, `check_env_vars` e `validate_prompt_structure`, acrescentando
  no script as verificações que o helper não cobre, sem alterar `src/utils.py`.
- [ ] Rejeitar arquivo ausente, estrutura inválida, campos vazios, técnicas insuficientes
  e variáveis inesperadas antes de publicar.
- [ ] Ler o handle do ambiente e montar `fabiocsm/bug_to_user_story_v2` sem username
  fixado no código. Montar `ChatPromptTemplate` com mensagens System e User.
- [ ] Publicar com `is_public=True`, descrição e tags. Representar também as técnicas
  nos metadados suportados pelo SDK, como tags e descrição; não inventar parâmetros
  de API para transmitir `techniques_applied`.
- [ ] Exibir URL de publicação; retornar sucesso somente após confirmação do cliente.
  Em falha, retornar código diferente de zero e diagnóstico útil.
- [ ] Executar `python src/push_prompts.py`, recuperar a revisão publicada e comparar
  suas mensagens e variáveis com o YAML local. Registrar ID/commit do Hub e hash local.
- [ ] Conferir conteúdo e visibilidade pública no dashboard; usar o CLI como apoio.

**Critério de saída:** prompt público correto, rastreável e equivalente à v2 local,
incluindo descrição, tags e técnicas. Os scripts continuam sendo os entregáveis;
operações manuais ou via CLI não substituem sua implementação.

### Fase 6 — Experimento completo e auditoria dos resultados

**Dependência:** Fase 5.

- [ ] Conferir os 15 registros locais, com `inputs.bug_report` e `outputs.reference`.
- [ ] Verificar o dataset remoto `{LANGSMITH_PROJECT}-eval`. O avaliador reutiliza
  datasets pelo nome; comparar contagem, entradas e referências com o JSONL local.
  Se houver colisão ou divergência, usar um projeto dedicado e registrar a configuração,
  preservando o dataset original e os experimentos anteriores.
- [ ] Executar `python src/evaluate.py` sem modificar sua implementação.
- [ ] Registrar URL/ID do experimento, revisão do Hub, hash do YAML, data, provedor,
  modelos e resultados agregados. Manter a revisão do Hub estável durante a execução.
- [ ] Conferir 15 respostas geradas e feedback para cada uma das cinco métricas em
  todos os exemplos: 75 notas válidas, numéricas, finitas e no intervalo `[0, 1]`.
- [ ] Investigar erros de transporte, respostas vazias, falhas de parsing dos juízes
  e feedback ausente. A agregação fornecida ignora notas ausentes; um resumo aprovado
  não basta para atestar um experimento incompleto.
- [ ] Conferir as cinco médias e a média geral, usando a agregação fornecida.
  Inspecionar também os casos de menor nota e a distribuição por dificuldade.
- [ ] Inspecionar traces de pelo menos um caso simples, um médio e um complexo,
  incluindo entrada, prompt, resposta, chamadas dos juízes e feedback disponível.

**Critério de saída:** experimento completo e inspecionável. A aprovação final exige
que cada métrica agregada e a média geral sejam `>= 0.8`; se isso não ocorrer, seguir
para a Fase 7. Uma nota individual baixa deve orientar a análise, sem redefinir o
limiar agregado estabelecido pelo avaliador.

### Fase 7 — Iterações orientadas por evidências

**Dependência:** primeiro experimento da Fase 6.

Planejar 3–5 iterações de otimização, registrando as efetivamente realizadas:

| Ciclo previsto | Foco | Validação |
| --- | --- | --- |
| 1 | Primeira v2: persona, Few-shot e estrutura explícita | Experimento completo como referência inicial |
| 2 | Corrigir omissões e casos de borda observados | Comparação com o ciclo 1 e revisão dos casos fracos |
| 3 | Equilibrar completude, precisão e concisão | Cinco métricas e análise dos relatos complexos |
| 4–5 | Ajustar falhas residuais, conforme os resultados | Confirmação dos critérios de aprovação |

- [ ] Para cada ciclo, registrar problema, hipótese de ajuste, alteração realizada,
  revisão publicada, modelos, cinco notas, média, link e conclusão.
- [ ] Ajustar somente a v2 e sua documentação, executar testes, publicar e avaliar.
- [ ] Para F1 baixo, investigar informações relevantes omitidas; para Precision baixa,
  investigar conteúdo inventado ou excessivo; para Clarity baixa, revisar organização
  e ambiguidade. Helpfulness e Correctness são derivadas no avaliador fornecido.
- [ ] Manter exemplos Few-shot independentes do dataset e preservar os experimentos.
- [ ] Se a aprovação vier antes dos ciclos previstos, registrar o fato e evitar
  executar chamadas apenas para preencher uma contagem. Se houver reprovação após
  cinco ciclos, registrar o diagnóstico e planejar novas iterações; não declarar sucesso.
- [ ] Após qualquer alteração posterior ao experimento aprovado, testar, publicar
  e avaliar novamente para que a evidência final corresponda ao artefato entregue.

**Critério de saída:** revisão final publicada e aprovada, histórico comparável e
justificativa das mudanças. A melhoria estatística fora desse dataset não é medida
por este desafio; a documentação deve descrever o alcance real dos resultados.

### Fase 8 — Evidências, documentação e entrega pública

**Dependência:** Fase 7 com resultado aprovado.

- [ ] Completar `Técnicas Aplicadas (Fase 2)`: técnicas, justificativas e trechos reais.
- [ ] Completar `Resultados Finais`: cinco métricas e média, comparação qualitativa
  v1/v2, histórico das iterações e links de prompt, dataset e experimentos.
- [ ] Comparar v1/v2 pelo conteúdo e decisões de otimização. Caso se deseje comparação
  numérica da v1, gerar experimento real separado sob os mesmos modelos e dataset,
  reutilizando as funções fornecidas sem alterar o avaliador. Identificá-lo como
  atividade adicional, contabilizando seu custo. Não usar as notas ilustrativas do README.
- [ ] Completar `Como Executar`: Python, ambiente virtual, dependências, variáveis sem
  segredos, modelos usados, comandos de cada fase e interpretação de sucesso/falha.
- [ ] Compartilhar o dataset aprovado usando `Client.share_dataset` conforme o README.
  Guardar o link retornado e evitar novo compartilhamento que substitua o endereço.
- [ ] Capturar screenshots das cinco notas, dataset com 15 exemplos e traces dos
  três exemplos selecionados, mostrando sua relação com o experimento final.
- [ ] Disponibilizar evidências em `docs/evidencias/` ou em URLs públicas estáveis,
  com links no README. `screenshots/` e `results/` são ignorados e não bastam como entrega.
- [ ] Testar links em sessão sem autenticação. Se o link compartilhado não expuser
  traces ou detalhes necessários, incluir screenshots legíveis desses itens.
- [ ] Repetir os comandos documentados em ambiente virtual limpo, com credenciais
  locais, mantendo o projeto/artefatos de avaliação identificados e sem sobrescrever
  acidentalmente evidências aprovadas. Contabilizar novas chamadas no custo.
- [ ] Conferir os arquivos protegidos, a ausência de segredos e a disponibilidade
  pública do fork, do prompt e das evidências. Revisar o diff antes da entrega.

**Critério de saída:** todos os itens da seção 9 comprovados e material acessível ao avaliador.

## 6. Matriz de rastreabilidade

| ID | Requisito do README | Fase | Comprovação |
| --- | --- | --- | --- |
| R01 | Python 3.10+, LangChain, LangSmith e YAML | 1 | Versão Python, dependências e instalação limpa |
| R02 | Credenciais e handle configurados | 1 | Validação sem segredos e acesso sob `fabiocsm` |
| R03 | Pull da semente e persistência local | 2 | Script real, YAML e comparação com mensagens do Hub |
| R04 | V2 preenchida, clara e específica | 3 | YAML funcional e renderização do template |
| R05 | Few-shot e outra técnica avançada | 3–4 | Exemplos, persona, metadados e testes |
| R06 | Regras, edge cases e System/User corretos | 3–4 | Revisão do conteúdo e contratos do template |
| R07 | Push versionado com metadados e acesso público | 5 | URL, revisão, round-trip e dashboard |
| R08 | Experimentos reais e cinco feedbacks por exemplo | 6 | 15 execuções e 75 notas verificadas |
| R09 | Cinco métricas e média geral >= 0.8 | 6–7 | Resumo e resultados completos do experimento final |
| R10 | Iterar e analisar melhorias | 7 | Histórico de hipóteses, revisões e resultados |
| R11 | Seis testes pytest implementados | 4 | Coleta e execução dos seis testes obrigatórios |
| R12 | Preservar dataset, avaliador, métricas e utilitários | Todas | Diff e hashes sem alteração |
| R13 | Preservar suporte OpenAI/Gemini | 1 e 8 | Arquivos protegidos e contratos de configuração preservados |
| R14 | Documentar técnicas e sua aplicação | 3 e 8 | Seção `Técnicas Aplicadas (Fase 2)` |
| R15 | Resultados, screenshots e comparação v1/v2 | 8 | Seção `Resultados Finais` e evidências reais |
| R16 | Instruções detalhadas e reproduzíveis | 8 | Seção `Como Executar` e execução limpa |
| R17 | Dataset público com 15 exemplos e três traces | 6 e 8 | Link público conferido e screenshots complementares |
| R18 | Fork público com código e v2 funcional | 1 e 8 | URL do GitHub e conferência dos arquivos entregues |

## 7. Estratégia de medição e custo

Conforme o código fornecido, por exemplo:

- F1-Score é calculado a partir de Precision/Recall produzidos pelo juiz.
- Clarity e Precision são avaliadas por seus respectivos juízes.
- Helpfulness = `(Clarity + Precision) / 2`.
- Correctness = `(F1-Score + Precision) / 2`.

O resumo agrega cada métrica sobre os exemplos. Todos os cinco valores agregados
e sua média devem atingir `0.8`. Conferir os 75 feedbacks evita aceitar uma média
calculada apenas sobre um subconjunto com avaliações ausentes.

No caminho de sucesso, cada exemplo usa uma geração e três chamadas de juiz:
aproximadamente 60 chamadas para 15 exemplos por experimento, ou 180–300 para 3–5 ciclos.
Essa contagem não inclui testes mínimos de modelo, retries, eventual baseline da v1
ou repetição de execução. São cinco notas, mas três juízes; as duas demais são derivadas.

Estimar custo pelos modelos selecionados e volume de tokens, incluindo os relatos
complexos e os exemplos Few-shot. Usar a referência de US$ 1–5 do README para o
planejamento, registrar consumo disponível e eliminar avaliações redundantes.
Testes estruturais devem rodar sem chamadas pagas. Manter `max_concurrency=1`, já
definido no avaliador, e investigar limites antes de repetir experimentos com falha.

## 8. Riscos e tratamento

| Risco | Tratamento planejado |
| --- | --- |
| Dependências fixadas incompatíveis com o Python escolhido | Validar instalação e selecionar interpretador compatível antes de implementar |
| Modelo sem suporte a `temperature=0` ou sem acesso | Conferir documentação e chamada mínima; selecionar modelo compatível |
| Nome de técnica presente, mas sem exemplos reais | Validar pares de entrada/saída e revisar conteúdo, além dos metadados |
| Exemplos com chaves interpretadas como variáveis | Renderizar o template e exigir apenas `bug_report` como variável |
| Dataset remoto existente e divergente | Comparar entradas/referências; usar projeto dedicado preservando os dados |
| Experimento parcial com média aparentemente aprovada | Exigir 15 respostas e 75 notas válidas, inspecionando erros e traces |
| Referências complexas exigem mais detalhes que o relato informa | Analisar omissões e julgamentos; separar recomendações de fatos, sem inventar dados nem copiar referências |
| V2 local diferente da avaliada no Hub | Conferir round-trip e registrar revisão/hash em cada ciclo |
| Rate limit, erros de API ou parsing do juiz | Registrar e diagnosticar; repetir somente após resolver a causa, sem alterar as métricas |
| Oscilação das notas apesar de temperatura zero | Preservar configuração, registrar resultados e evitar escolher apenas execuções favoráveis |
| Links do workspace inacessíveis ao avaliador | Compartilhar dataset e testar sem login; complementar com screenshots |
| Screenshots apenas em pastas ignoradas | Entregar em `docs/evidencias/` ou URLs públicas e conferir os links |

## 9. Checklist de conclusão

- [ ] Especificação, plano técnico e tarefas SDD consistentes com o README e a constituição.
- [ ] Ambiente reproduzível e modelos compatíveis registrados.
- [ ] Pull implementado, executado e v1 preservada.
- [ ] V2 funcional, sem pendências e com Few-shot e pelo menos outra técnica aplicada.
- [ ] System/User e entrada `{bug_report}` compatíveis com o avaliador.
- [ ] Seis testes obrigatórios efetivos aprovados.
- [ ] Push implementado e `fabiocsm/bug_to_user_story_v2` público, com metadados.
- [ ] Revisão final local, revisão do Hub e experimento aprovado correspondentes.
- [ ] Dataset completo e íntegro: 15 exemplos e respectivas referências.
- [ ] Experimento final com 15 respostas e 75 feedbacks válidos.
- [ ] Helpfulness, Correctness, F1-Score, Clarity e Precision individualmente >= 0.8.
- [ ] Média geral >= 0.8.
- [ ] Iterações e decisões registradas com resultados reais e links.
- [ ] Tracing detalhado de pelo menos três exemplos disponível nas evidências.
- [ ] README com as três seções obrigatórias, comparação v1/v2 e screenshots legíveis.
- [ ] Acesso público ao dataset/experimentos e demais evidências conferido sem login.
- [ ] Fork público contém código, YAML v2 e documentação da entrega.
- [ ] Arquivos protegidos íntegros e nenhuma credencial nos artefatos publicados.

## 10. Ordem operacional resumida

Após a especificação e implementação das etapas correspondentes, executar da raiz:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m pip check
python src/pull_prompts.py
# Criar/refinar a v2 e implementar os testes e o push.
pytest tests/test_prompts.py -v
python src/push_prompts.py
python src/evaluate.py
```

Para cada revisão seguinte: editar v2 → testar → publicar → avaliar → conferir
completude → registrar resultado. Após a aprovação: publicar evidências, revisar
documentação, conferir integridade e validar acesso público.

Este plano organiza a execução; sua criação não realiza publicações, chamadas de LLM,
instalações de dependências ou implementação dos esqueletos.
