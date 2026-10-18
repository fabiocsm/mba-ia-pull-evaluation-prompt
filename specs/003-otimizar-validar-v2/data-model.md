# Modelo de dados — prompt v2 e validação

**Feature**: [spec.md](spec.md) | **Contrato**: [otimizacao-v2.md](contracts/otimizacao-v2.md)

Modelo documental de arquivos e resultados de teste; não introduz banco de dados,
classes de produção ou novos campos obrigatórios para os scripts.

## Prompt v2

Raiz YAML: mapping com a definição `bug_to_user_story_v2`. Não aceitar raiz nula,
lista, escalar ou definição ausente/não mapping. Este arquivo contém somente a v2.

| Campo | Tipo / cardinalidade | Regra |
| --- | --- | --- |
| `description` | string não branca | Explica conversão e objetivo; não declara notas não obtidas |
| `system_prompt` | string não branca | Persona, contexto, regras, formato e três exemplos completos |
| `user_prompt` | string | Valor `{bug_report}`; sem regras/exemplos adicionais |
| `version` | string | Exatamente `v2` |
| `tags` | lista não vazia de strings não brancas | Classificação do prompt, sem segredos |
| `techniques_applied` | lista de strings não brancas | Duas técnicas distintas efetivas: Few-shot Learning e Role Prompting |

Comparar técnicas após `strip()` e `casefold()`; rejeitar duplicatas mesmo que a
lista também contenha duas técnicas válidas. A técnica obrigatória não pode ser
substituída por outra; não usar aliases inconsistentes nos metadados/documentação.
O artefato inteiro deve estar livre de marcadores de pendência.

## Mensagens derivadas

| Ordem | Papel no SDK | Origem | Variáveis |
| --- | --- | --- | --- |
| 1 | `system` | `system_prompt` | Nenhuma |
| 2 | `human` (User) | `user_prompt` | `bug_report` |

A montagem gera `ChatPromptTemplate.input_variables == ["bug_report"]`, sem
variáveis opcionais/partials usadas para encobrir dependências adicionais. Chaves
literais nos templates usam escape `{{`/`}}`; chaves contidas no relato já são
valor de entrada e permanecem intactas após uma formatação.

## Exemplo próprio

Entidade lógica embutida em `system_prompt`, sem chave YAML nova.

| Campo lógico | Representação | Validação |
| --- | --- | --- |
| Identificador | `### Exemplo 1` a `### Exemplo 3` | Único e sequencial |
| Entrada | Texto após `#### Entrada` | Relato próprio, não vazio |
| Saída | Texto após `#### Saída` | Resposta completa coerente com a entrada |
| Perfil | Evidenciado no conteúdo | Simples; insuficiente/ambíguo; múltiplos problemas/log/conflito |
| Origem | Revisão documental | Não copiar entradas ou respostas do dataset |

O contrato de aceitação permite 2–3 exemplos; o desenho inicial escolhe três para
cobertura. Remover um exige manter toda a cobertura semântica e atualizar README.
Um exemplo insuficiente demonstra a resposta de esclarecimento completa; não
precisa fingir uma User Story viável quando faltam informações essenciais.

## Resposta orientada pelo prompt

Entidade textual esperada, sem parser obrigatório nem novo campo no dataset:

- User Story em português no padrão “Como… eu quero… para que…”, quando houver
  informação suficiente; papel genérico se a identidade específica não foi informada.
- Critérios de aceitação verificáveis, ligados ao comportamento desejado e aos
  problemas relatados, sem apresentá-los como fatos já observados.
- Contexto técnico/impacto somente quando informado; lacunas e perguntas específicas
  quando impedirem clareza; recomendações opcionais rotuladas como tais.
- Entrada vazia/insuficiente: indicar insuficiência e esclarecimentos necessários,
  sem inventar persona específica, causa, prioridade, prazo, métrica ou solução.

Uma resposta pode agrupar critérios de problemas relacionados; todos devem ser
cobertos. A concisão não elimina informação relevante e a estrutura não obriga
seções vazias ou recomendações sem fundamento.

## Resultado de validação

Registro lógico produzido pelo pytest e pela revisão documental, não feedback
LangSmith nem score de qualidade.

| Campo lógico | Origem | Significado |
| --- | --- | --- |
| Verificação / ID | Nome pytest ou V01–V12 do guia | Condição rastreável |
| Alvo | YAML real ou cópia negativa isolada | Distingue artefato e defeito controlado |
| Resultado | Status pytest/revisão | Aprovado, reprovado ou pendente |
| Diagnóstico | Asserção e condição avaliada | Qual regra falhou, sem segredo |
| Evidência | Comando, saída resumida e diff | Registrar na implementação, sem criar score artificial |

## Relações e estados

Uma definição v2 contém três exemplos e gera duas mensagens. Cada verificação
positiva avalia a definição real; cada negativo deriva dela com um defeito e deve
ser rejeitado pela asserção correspondente.

Fluxo: `ausente → redigido → validado localmente → pronto para publicação na 004`.
Qualquer alteração retorna a `redigido`. Falha de validação impede avanço.
`publicado`, `avaliado` e `aprovado nas métricas` são estados posteriores das
specs 004/005, nunca consequência automática dos testes da 003.
