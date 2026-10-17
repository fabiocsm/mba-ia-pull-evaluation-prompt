# Orientações para agentes

## Contexto e fontes de requisitos

Este repositório é a base de uma entrega acadêmica de pós-graduação. O objetivo é
recuperar um prompt de baixa qualidade, otimizá-lo e demonstrar a melhoria por
experimentos reais no LangSmith.

- Leia o [README.md](README.md), que contém o contrato de avaliação, e a
  [constituição](.specify/memory/constitution.md) antes de planejar ou implementar mudanças.
- Preserve os requisitos originais ao atualizar a documentação do processo.
- Trabalhe com SDD usando as skills locais em `.agents/skills/`: especificação,
  esclarecimentos quando necessários, plano, tarefas, análise e implementação.
  Consulte os artefatos existentes da feature antes de executar suas tarefas.
- Mantenha rastreabilidade entre requisitos, tarefas, alterações e evidências.
- Em conflitos entre uma solução técnica e o enunciado, registre o impedimento e
  resolva a divergência antes de alterar o que o desafio exige preservar.

## Escopo de implementação

Concentre a implementação nos artefatos previstos pelo desafio:

- `src/pull_prompts.py`: recuperar a v1 e salvá-la localmente.
- `prompts/bug_to_user_story_v2.yml`: criar e iterar o prompt otimizado.
- `src/push_prompts.py`: validar e publicar a v2 com seus metadados.
- `tests/test_prompts.py`: implementar os seis testes obrigatórios.
- `README.md`: documentar técnicas, execução, iterações e resultados.

Não altere os arquivos fornecidos como prontos:

- `src/evaluate.py`
- `src/metrics.py`
- `src/utils.py`
- `datasets/bug_to_user_story.jsonl`

Preserve os 15 exemplos do dataset, suas referências e a distribuição de dificuldade
(5 simples, 7 médios e 3 complexos). Preserve também o suporte existente a OpenAI e
Gemini. A v1 deve refletir o conteúdo recuperado; as melhorias pertencem à v2.

## Stack e configuração

- Use Python 3.10+, LangChain, LangSmith, Prompt Hub, YAML e pytest.
- Reutilize `langsmith.Client`, `ChatPromptTemplate` e os utilitários existentes.
- Crie e ative um ambiente virtual antes de instalar `requirements.txt`.
- O handle público deste projeto é `fabiocsm`; use
  `USERNAME_LANGSMITH_HUB=fabiocsm` na configuração, sem fixá-lo no código dos scripts.
- A chave OpenAI já está no `.env`, conforme informado pelo autor. Reutilize-a sem
  expor seu valor. Não versione credenciais nem as inclua em logs ou evidências.
- Confira `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `USERNAME_LANGSMITH_HUB`,
  `LANGSMITH_TRACING`, `LLM_PROVIDER`, `LLM_MODEL`, `EVAL_MODEL` e a chave do provedor
  escolhido (`OPENAI_API_KEY` ou `GOOGLE_API_KEY`) antes das execuções correspondentes.
- OpenAI é a opção inicial. Consulte a documentação oficial ao selecionar os modelos;
  ambos devem aceitar `temperature=0`, usado pela infraestrutura fornecida.
- Registre os modelos e o provedor usados nos experimentos. Considere a estimativa
  de US$ 1–5 do enunciado ao planejar as avaliações.

## Contratos dos prompts e do Hub

- Origem obrigatória: `leonanluppi/bug_to_user_story_v1`.
- Destino local do pull: `prompts/bug_to_user_story_v1.yml`.
- Use `dangerously_pull_public_prompt=True` para o pull público previsto no desafio.
- Prompt otimizado: `prompts/bug_to_user_story_v2.yml`, definição
  `bug_to_user_story_v2`, com `description`, `system_prompt`, `user_prompt`,
  `version`, `tags` e `techniques_applied`.
- Use `{bug_report}` como entrada, com mensagens System e User separadas.
- Inclua persona, instruções específicas, formato de saída, regras de comportamento,
  casos de borda e exemplos completos de entrada/saída.
- Few-shot Learning é obrigatório, junto de pelo menos outra técnica prevista no
  README. Liste pelo menos duas técnicas realmente aplicadas em `techniques_applied`.
- Publique `fabiocsm/bug_to_user_story_v2` como público (`is_public=True`), com descrição,
  tags e técnicas. Refaça o push após cada alteração local antes de avaliar.
- O avaliador recupera o prompt do Hub. Guarde a revisão publicada e os links dos
  experimentos para relacionar cada resultado à versão efetivamente executada.

## LangSmith CLI disponível

O **LangSmith CLI está instalado e disponível pelo comando `langsmith`**. O agente
pode usá-lo quando necessário para consultar prompts, datasets, experimentos,
execuções e traces, investigar falhas e conferir as evidências do trabalho.

Consulte a ajuda da versão instalada antes de usar um subcomando ou suas opções:

```bash
langsmith --help
langsmith prompt --help
langsmith dataset list
langsmith experiment list --dataset "${LANGSMITH_PROJECT}-eval"
langsmith trace list --project "$LANGSMITH_PROJECT" --limit 5
```

- Use `--format json` quando precisar processar a saída programaticamente.
- O CLI aceita `LANGSMITH_API_KEY` e perfis de autenticação; confira também o workspace
  e o projeto selecionados. Não suponha que ele carregue o `.env` automaticamente.
- Use o CLI dentro do escopo da tarefa. Preserve os dados, as referências, os
  avaliadores e o histórico dos experimentos exigidos para a entrega.
- O CLI complementa o desenvolvimento e a inspeção. Os scripts Python de pull,
  push e avaliação continuam sendo entregáveis obrigatórios e devem funcionar.

## Execução e validação

Execute os comandos a partir da raiz, após implementar as respectivas etapas e
configurar o ambiente:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/pull_prompts.py
# Criar/refinar a v2 e implementar os testes antes das próximas etapas.
pytest tests/test_prompts.py
python src/push_prompts.py
python src/evaluate.py
```

- Implemente os testes `test_prompt_has_system_prompt`, `test_prompt_has_role_definition`,
  `test_prompt_mentions_format`, `test_prompt_has_few_shot_examples`,
  `test_prompt_no_todos` e `test_minimum_techniques`, com verificações efetivas do YAML v2.
- A aprovação exige cada métrica agregada do experimento e a média geral em pelo
  menos `0.8`: Helpfulness, Correctness, F1-Score, Clarity e Precision.
- Os testes estruturais e a avaliação real são verificações independentes. Não altere
  métricas, limiares ou dados para obter aprovação e não apresente resultados simulados
  como evidência final.
- Planeje de 3 a 5 iterações. Analise as notas, ajuste a v2, teste, publique e avalie
  novamente, registrando o motivo das mudanças e os resultados efetivamente obtidos.
- Ao encerrar uma tarefa, informe o que mudou, as verificações executadas e as pendências.
  Diferencie implementação concluída de resultado ainda não verificado no LangSmith.

## Documentação e entrega

- Mantenha no README as seções `Técnicas Aplicadas (Fase 2)`, `Resultados Finais` e
  `Como Executar`, com justificativas, exemplos, comparação v1/v2 e comandos reproduzíveis.
- Entregue o fork público no GitHub com o código, o prompt v2 funcional e a documentação.
- Disponibilize as evidências exigidas: dataset com 15 exemplos, experimentos da v2,
  screenshots das cinco notas e tracing detalhado de pelo menos 3 exemplos.
- Confira o acesso público ao dataset e aos experimentos compartilhados; links privados
  do workspace não bastam. Guarde o link gerado por `Client.share_dataset` e evite
  compartilhá-lo novamente, pois o endereço muda conforme o README.
- `screenshots/` e `results/` estão ignorados no Git. Garanta que as evidências usadas
  no README estejam de fato acessíveis ao avaliador, além das cópias locais.
