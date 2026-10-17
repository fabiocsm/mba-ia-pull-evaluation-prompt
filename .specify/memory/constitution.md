# MBA IA — Pull, Otimização e Avaliação de Prompts Constitution

## Core Principles

### I. Integridade do desafio e escopo controlado

- O projeto DEVE implementar o fluxo de conversão de relatos de bugs em User Stories descrito
  no `README.md`: pull do prompt inicial, otimização, push público e avaliação no LangSmith.
- A implementação DEVE se concentrar em `src/pull_prompts.py`, `src/push_prompts.py`,
  `prompts/bug_to_user_story_v2.yml`, `tests/test_prompts.py` e na documentação do processo
  no `README.md`. O pull DEVE salvar o artefato inicial em `prompts/bug_to_user_story_v1.yml`.
- `src/evaluate.py`, `src/metrics.py`, `src/utils.py` e
  `datasets/bug_to_user_story.jsonl` NÃO DEVEM ser alterados. O suporte existente a OpenAI
  e Gemini DEVE ser preservado. Um impedimento nesses arquivos DEVE ser registrado e
  resolvido como conflito de requisitos antes de qualquer proposta de alteração.
- O dataset DEVE conservar seus 15 exemplos e respectivas referências: 5 bugs simples,
  7 médios e 3 complexos. É PROIBIDO remover, substituir ou editar exemplos para elevar notas.
- A v1 DEVE preservar o conteúdo recuperado do Hub como referência do ponto de partida;
  as melhorias DEVEM ser feitas na v2. A estrutura obrigatória do repositório DEVE ser mantida.

Racional: a avaliação acadêmica exige resultados comparáveis obtidos pela melhoria do prompt,
com preservação da infraestrutura e dos dados fornecidos.

### II. Engenharia de prompts explícita e verificável

- O prompt otimizado DEVE existir em `prompts/bug_to_user_story_v2.yml`, em YAML válido,
  completamente preenchido, sem marcadores de trabalho pendente.
- A definição `bug_to_user_story_v2` DEVE conter `description`, `system_prompt`,
  `user_prompt`, `version`, `tags` e `techniques_applied`, compatíveis com os scripts existentes.
- Few-shot Learning é OBRIGATÓRIO, com exemplos claros e completos de entrada e saída.
  Pelo menos uma técnica adicional DEVE ser aplicada: Chain of Thought, Tree of Thought,
  Skeleton of Thought, ReAct ou Role Prompting. Os metadados `techniques_applied` DEVEM
  listar pelo menos duas técnicas distintas efetivamente presentes no prompt.
- O prompt DEVE definir uma persona, instruções específicas, regras explícitas de
  comportamento e formato de saída em Markdown ou User Story padrão. DEVE tratar casos
  de borda, incluindo relatos incompletos ou ambíguos, sem inventar fatos ausentes.
- As mensagens System e User DEVEM ter responsabilidades distintas: contexto, regras e
  exemplos no System; relato a processar no User, usando a variável `{bug_report}` exigida
  pelo dataset. Variáveis de entrada adicionais NÃO DEVEM ser exigidas do avaliador.
- A seção `Técnicas Aplicadas (Fase 2)` do README DEVE identificar cada técnica escolhida,
  justificar sua escolha e mostrar exemplos práticos de sua aplicação.

Racional: técnicas declaradas em metadados só são evidência quando aparecem no conteúdo e
produzem instruções que os testes e a avaliação conseguem verificar.

### III. LangSmith como fonte de verdade e rastreabilidade

- O pull DEVE usar o cliente LangSmith para recuperar
  `leonanluppi/bug_to_user_story_v1` e salvar seu conteúdo em
  `prompts/bug_to_user_story_v1.yml`. Para esse prompt público do desafio, a chamada DEVE
  incluir `dangerously_pull_public_prompt=True`, conforme o contrato do repositório.
- O push DEVE ler a v2 do YAML local, montar o `ChatPromptTemplate` com System e User,
  validar sua estrutura e publicar `fabiocsm/bug_to_user_story_v2` no Prompt Hub.
  O handle DEVE ser lido de `USERNAME_LANGSMITH_HUB`, cujo valor deste projeto é `fabiocsm`.
- A publicação DEVE ser pública, usando `is_public=True` ou a opção equivalente da
  interface, e incluir descrição, tags e identificação das técnicas utilizadas.
- A avaliação DEVE executar o prompt recuperado do Hub pelo avaliador fornecido.
  Toda edição local da v2 DEVE ser publicada antes de uma nova avaliação.
- Cada execução de avaliação DEVE produzir um experimento no LangSmith, associado ao
  dataset de avaliação, com as cinco notas gravadas como feedback por exemplo.
- O histórico das iterações DEVE permitir associar a revisão publicada do prompt,
  os modelos usados, o experimento e seus resultados. A publicação DEVE ser conferida
  no dashboard e os links dos experimentos DEVEM ser guardados.

Racional: o resultado entregue precisa corresponder ao prompt publicado e permitir inspeção
das execuções que sustentam as notas apresentadas.

### IV. Aprovação por métricas reais e avaliação íntegra

- A aprovação DEVE seguir o cálculo do avaliador fornecido sobre o dataset completo.
  Cada uma das cinco métricas agregadas do experimento DEVE atingir pelo menos `0.8`:
  Helpfulness, Correctness, F1-Score, Clarity e Precision. A média das cinco também
  DEVE ser pelo menos `0.8`.
- A média geral NÃO DEVE compensar uma métrica individual abaixo de `0.8`.
  Os feedbacks por exemplo DEVEM permanecer disponíveis para análise dos resultados.
- As métricas base F1-Score, Clarity e Precision, as fórmulas derivadas de Helpfulness
  e Correctness, a agregação e o limiar de aprovação NÃO DEVEM ser modificados.
- É PROIBIDO fabricar notas, substituir chamadas reais por resultados simulados nas
  evidências finais, alterar referências ou inserir instruções no prompt destinadas a
  manipular o avaliador. Falhas e resultados insuficientes DEVEM ser registrados como tais.
- O trabalho DEVE planejar de 3 a 5 iterações, conforme a expectativa do desafio, e
  registrar as efetivamente realizadas. Cada ciclo DEVE analisar as métricas baixas,
  ajustar a v2, publicar novamente e avaliar. A quantidade prevista NÃO substitui o
  critério de aprovação; novas iterações são necessárias enquanto houver métrica insuficiente.
- As alterações entre iterações DEVEM ter justificativa ligada às falhas observadas.
  Resultados anteriores DEVEM ser preservados para comparação no LangSmith.

Racional: a otimização deve demonstrar melhoria de qualidade por evidências reais,
mantendo as mesmas regras de medição durante todo o desafio.

### V. Validação automatizada e entrega reproduzível

- `tests/test_prompts.py` DEVE implementar, no mínimo, os seis testes obrigatórios:
  `test_prompt_has_system_prompt`, `test_prompt_has_role_definition`,
  `test_prompt_mentions_format`, `test_prompt_has_few_shot_examples`,
  `test_prompt_no_todos` e `test_minimum_techniques`.
- Os testes DEVEM carregar o YAML otimizado e verificar, respectivamente: System não
  vazio, persona, formato de saída, exemplos de entrada/saída, ausência de marcadores
  de pendência e pelo menos duas técnicas nos metadados. Corpos vazios ou verificações
  que aprovam incondicionalmente NÃO atendem ao requisito.
- `pytest tests/test_prompts.py` DEVE passar antes da entrega. A aprovação dos testes
  estruturais e a aprovação das métricas reais são requisitos independentes e cumulativos.
- O README DEVE conter `Técnicas Aplicadas (Fase 2)`, `Resultados Finais` e
  `Como Executar`, incluindo justificativas, exemplos, comparação v1/v2, pré-requisitos,
  dependências e comandos de cada fase.
- A entrega DEVE ocorrer em repositório público no GitHub, fork do repositório base,
  com o código implementado, o YAML v2 funcional e a documentação atualizada.
- As evidências DEVEM incluir screenshots com as cinco notas mínimas atingidas,
  dataset com 15 exemplos, execuções da v2 e tracing detalhado de pelo menos 3 exemplos.
  O README DEVE oferecer acesso público verificável ao dataset e experimentos, ou
  screenshots do dashboard que comprovem esses itens quando usadas como alternativa
  permitida pelo enunciado. URLs privadas de workspace NÃO constituem evidência pública.

Racional: o avaliador acadêmico precisa conseguir executar o projeto e conferir a entrega
sem depender de credenciais pessoais do autor.

## Restrições técnicas e configuração

- A stack obrigatória é Python 3.10+, LangChain, LangSmith, LangSmith Prompt Hub e
  prompts em YAML. O projeto DEVE reutilizar `langchain_core.prompts.ChatPromptTemplate`
  e o cliente `langsmith.Client`, conforme os contratos dos esqueletos.
- As dependências DEVEM ser instaladas a partir de `requirements.txt` em ambiente
  virtual criado e ativado antes da instalação. Não é necessário adotar outro framework
  de aplicação para cumprir o desafio.
- Credenciais DEVEM ser carregadas do ambiente ou do `.env` local. Valores secretos
  NÃO DEVEM entrar no código, nos prompts, no Git, no README, nos logs ou nas screenshots.
  O `.env.example` DEVE continuar sendo um template de configuração sem credenciais reais.
- A chave OpenAI já existente no `.env`, informada pelo autor, DEVE ser reutilizada
  para a configuração correspondente, sem solicitar sua exposição ou gerar outra chave.
  Isso NÃO comprova que as credenciais LangSmith ou os modelos estejam configurados.
- Antes de executar o fluxo, DEVEM ser validados `LANGSMITH_API_KEY`,
  `LANGSMITH_PROJECT`, `USERNAME_LANGSMITH_HUB=fabiocsm`, `LLM_PROVIDER`, `LLM_MODEL`,
  `EVAL_MODEL` e a chave do provedor escolhido. O tracing DEVE estar habilitado.
- OpenAI é a opção inicial de provedor, considerando a credencial informada.
  O suporte existente a Gemini DEVE permanecer disponível. Os nomes dos modelos
  NÃO são fixados nesta constituição: no planejamento, a seleção DEVE consultar a
  documentação oficial do provedor e registrar modelos disponíveis e compatíveis
  com `temperature=0`, usado pelo avaliador e pelos utilitários fornecidos.
- Geração e avaliação DEVEM ter modelos configurados explicitamente; podem usar
  o mesmo modelo ou um modelo mais capaz na avaliação. A configuração usada em cada
  experimento DEVE ser registrada para permitir reprodução e comparação.
- A estimativa de US$ 1–5 do README DEVE orientar o planejamento de custo; é uma
  estimativa do desafio, sem constituir garantia de preço ou limite automático de gastos.
- O dataset remoto DEVE seguir o nome `{LANGSMITH_PROJECT}-eval`, conforme o avaliador.
  Se for usado compartilhamento público, o link retornado por `Client.share_dataset`
  DEVE ser guardado e conferido sem acesso ao workspace. Novo compartilhamento DEVE
  ser evitado após documentar o link, pois o README informa que o endereço muda.
- Screenshots usadas como evidência DEVEM estar acessíveis na entrega. Como
  `screenshots/` e `results/` estão ignorados no Git, arquivos existentes apenas nessas
  pastas locais NÃO satisfazem a exigência de disponibilização ao avaliador.

## Fluxo SDD, revisão e critérios de entrega

1. **Especificação:** registrar os requisitos do README, o fluxo pull → otimização →
   push → avaliação, os critérios mensuráveis e os artefatos entregáveis. Cada requisito
   DEVE ter um critério de aceitação rastreável, inclusive evidências e documentação.
2. **Planejamento:** conferir esta constituição, delimitar arquivos permitidos,
   selecionar modelos compatíveis, validar pré-requisitos de configuração e planejar
   os experimentos e o custo. Impedimentos DEVEM ser explicitados antes da execução afetada.
3. **Tarefas:** decompor o trabalho em pull, prompt v2, testes, push, avaliação,
   iterações e documentação/evidências, preservando a ordem e as dependências.
4. **Implementação e execução:** criar/ativar o ambiente virtual, instalar dependências
   e executar `python src/pull_prompts.py`; criar a v2 e implementar os testes;
   executar `pytest tests/test_prompts.py`, `python src/push_prompts.py` e
   `python src/evaluate.py`. Repetir otimização, testes, push e avaliação nas iterações.
5. **Revisão de conformidade:** conferir o diff dos arquivos protegidos, os seis testes,
   os resultados das cinco métricas, a integridade dos 15 exemplos, a publicação sob
   `fabiocsm`, o acesso às evidências e a ausência de segredos.
6. **Entrega:** concluir apenas com testes aprovados, cada métrica e média geral
   atingindo `0.8`, prompt v2 público e documentação/evidências disponíveis.
   Pendências DEVEM permanecer registradas; nenhuma etapa pode declarar resultados
   ainda não obtidos como concluídos.

## Governance

- O README original contém o contrato acadêmico. Esta constituição o operacionaliza
  e governa especificações, planos, tarefas, implementação e revisão. Nenhum artefato
  posterior pode relaxar seus requisitos. Divergências DEVEM ser registradas e
  resolvidas contra o enunciado antes de executar trabalho incompatível.
- Alterações no README para documentar o processo DEVEM preservar os requisitos e
  as limitações do desafio. Uma emenda à constituição NÃO autoriza descumprir o enunciado
  nem alterar arquivos protegidos.
- Emendas DEVEM registrar motivação, regras afetadas, impacto em artefatos existentes,
  migração necessária e aprovação do responsável pelo projeto antes da adoção.
- O versionamento DEVE seguir SemVer: MAJOR para remoção ou redefinição incompatível
  de princípios; MINOR para novos princípios, seções ou ampliação material de regras;
  PATCH para esclarecimentos sem mudança de obrigação. A data de ratificação original
  DEVE ser preservada e a data da última emenda DEVE refletir a alteração mais recente.
- Cada especificação, plano e revisão de entrega DEVE verificar conformidade com esta
  constituição. Desvios DEVEM indicar a regra afetada e a resolução; conveniência técnica
  ou melhora aparente nas notas não justificam exceções aos requisitos acadêmicos.
- A versão `1.0.0` é a primeira adoção: o arquivo anterior continha apenas placeholders
  do template. Esta criação não altera templates, código, testes, configuração ou
  publicações externas; esses artefatos serão tratados nas respectivas etapas do SDD.

**Version**: 1.0.0 | **Ratified**: 2026-10-17 | **Last Amended**: 2026-10-17
