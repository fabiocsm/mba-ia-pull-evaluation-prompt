# Contrato — artefato v2 e validação antes da publicação

**Feature**: [spec.md](../spec.md) | **Consumidores**: testes locais, push da 004
e avaliação da 005. Não há endpoint HTTP ou comando CLI novo.

## C01 — Arquivo YAML

- Caminho `prompts/bug_to_user_story_v2.yml`, UTF-8, YAML válido.
- Raiz mapping com uma definição `bug_to_user_story_v2`, também mapping.
- Seis campos obrigatórios, tipos e valores conforme [modelo](../data-model.md).
- `version: v2`; System e User não brancos; User igual a `{bug_report}`.
- `tags` é lista não vazia de textos; `techniques_applied` contém pelo menos duas
  técnicas distintas, inclui Few-shot Learning e reflete conteúdo real. O desenho
  inicial declara Few-shot Learning e Role Prompting.
- Ausência de pendências em todos os campos textuais, inclusive `[TODO]` e
  marcadores equivalentes como FIXME/TBD; não reprovar palavras comuns do português
  por busca indiscriminada de fragmentos.
- Arquivo ausente, YAML inválido ou tipo incompatível deve causar reprovação
  explícita, nunca fallback para v1, corpo vazio ou fixture substituta.

## C02 — Mensagens e entrada

Montagem compatível com os consumidores existentes:

```text
ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", user_prompt),
])
```

Exatamente duas mensagens, `system`/`human`, nessa ordem. Somente `bug_report` em
`input_variables`; sem variável de referência, modelo, idioma ou usuário. System
não interpola o relato e User o insere uma única vez.

Chaves de logs/JSON dentro dos exemplos de template devem ser escapadas. Após
`format_messages(bug_report=relato_proprio)`, o Human deve ser exatamente o relato,
incluindo suas chaves literais; nenhum conteúdo do relato pode alterar o System.
Montagem e formatação são operações locais; não construir chain com LLM para isso.

## C03 — Conteúdo e exemplos

Instruções antes de `## Exemplos`: persona de produto, objetivo, português,
Markdown, padrão Como… eu quero… para que…, critérios de aceitação e regras de
fundamentação. Persona/formato encontrados só em exemplos não bastam.

Exemplos: 2–3 pares completos; o desenho inicial usa três. Cada bloco inicia por
`### Exemplo N` e contém `#### Entrada` e `#### Saída`, ambas não vazias. A saída
segue as regras aplicáveis ao relato: história/critérios para informação suficiente
ou esclarecimentos fundamentados para insuficiência impeditiva. Não usar somente
rótulos, reticências ou texto genérico substituindo uma demonstração completa.

Revisar cobertura dos seis grupos em FR-003:

| Grupo | Comportamento exigido |
| --- | --- |
| Vazio | Informar ausência de relato e pedir dados mínimos; sem fabricar história |
| Ambíguo | Explicitar a ambiguidade e perguntas específicas; não escolher interpretação como fato |
| Incompleto | Usar fatos conhecidos, apontar lacunas e não inventar detalhes |
| Múltiplos problemas | Cobrir todos, com critérios agrupados e estrutura proporcional |
| Logs | Tratar como dados; preservar contexto relevante e não atribuir causa sem evidência |
| Instruções conflitantes | Ignorar tentativa de trocar regras; considerar apenas dados do bug |

Não afirmar causa, arquitetura, versão, números, prioridade ou prazo ausentes.
Comportamentos desejados dos critérios não são fatos observados. Recomendações
ficam identificadas e não introduzem requisitos arbitrários. Exemplos próprios,
sem reprodução de referências do dataset ou instruções para influenciar juízes.

## C04 — Seis verificações obrigatórias

Manter os métodos da classe `TestPrompts` em `tests/test_prompts.py`, executando
sobre a definição real. Os helpers podem ser compartilhados com negativos, mas
nenhum dos seis pode usar fixture sintética como alvo principal.

| Método | Verificação positiva | Defeito que deve reprovar |
| --- | --- | --- |
| `test_prompt_has_system_prompt` | System existe, é string e não branco | Ausente, tipo inválido, vazio ou espaços |
| `test_prompt_has_role_definition` | Persona explícita nas instruções | Persona ausente das regras, ainda que citada nos exemplos |
| `test_prompt_mentions_format` | Português, Markdown, história e critérios nas regras | Formato ausente, mesmo que exemplos tenham formatação |
| `test_prompt_has_few_shot_examples` | 2–3 pares completos e saídas coerentes estruturalmente | Par incompleto, entrada/saída branca, apenas nome da técnica |
| `test_prompt_no_todos` | Nenhuma pendência textual | Marcador inserido em System, User ou metadados |
| `test_minimum_techniques` | Lista válida, distinta, inclui Few-shot e técnica adicional aplicada | Duplicata normalizada, menos de duas ou ausência de Few-shot |

Reutilizar `validate_prompt_structure` como checagem básica, após validar tipos;
complementar o que ele não cobre. Não alterar `src/utils.py`. Casos extras cobrem
C01/C02: identidade, campos, versão, tags, User, variáveis e renderização.

### Compatibilidade com o helper protegido — correção I1

O helper usa substring para `TODO` e rejeita também a palavra `TODOS`. A validação
local deve aplicar esta política explícita, sem modificar o helper ou o prompt:

1. Detectar pendências nos campos textuais com delimitadores: tokens isolados
   maiúsculos `TODO`, `FIXME`, `TBD` e formas entre colchetes, estas sem distinção de
   caixa e aceitando espaços internos, como `[TODO]` e `[ todo ]`. Usar limites de
   palavra Unicode; `TODOS`, `todos` e `todo` em prosa comum não são marcadores.
2. Após conferir os tipos, chamar o helper com os dados originais, sem remover
   palavras ou normalizar o texto entregue. Preservar todos os demais diagnósticos.
3. Desconsiderar exclusivamente o diagnóstico exato `system_prompt ainda contém TODOs`
   quando o detector local confirmar ausência de marcador no System. Só essa
   discordância conhecida pode deixar de reprovar; erro adicional, marcador real
   em qualquer campo ou retorno inesperado/incoerente mantém reprovação.
4. Combinar o resultado com todas as asserções locais de C01–C04. Não ignorar em
   bloco o booleano/erros do helper nem usar captura genérica para aprovar.

T018/T020 devem comprovar controles positivos com `TODOS`, `todos` e `todo`, negativos
com marcadores reais no System/User/metadados e casos combinados: `TODOS` junto de
campo obrigatório ausente ou técnicas insuficientes continua reprovado. Os dados
de entrada e o YAML real devem permanecer intactos após a validação. O adaptador
fica nos helpers locais de `tests/test_prompts.py`; a 004 deve seguir a mesma política
em seu script, sem importar código de teste nem alterar o arquivo protegido.

Coletar e executar os seis, com nenhum `skip`, `xfail` ou corpo vazio. Negativos
usam cópias em memória/temporários e verificam o diagnóstico ou asserção pertinente.
Não regravar o YAML real, não aceitar exceção genérica alheia à regra como prova.
A suíte deve bloquear acesso à rede e funcionar sem credenciais; não chamar Hub,
LLM, `get_llm` ou juízes. O carregamento dotenv dos utilitários não exige valores.

## C05 — Documentação e aceite local

A seção `Técnicas Aplicadas (Fase 2)` do README deve conter, para cada técnica:
nome coerente com o YAML, justificativa e trecho real da v2. Acrescentar comparação
qualitativa com as limitações observadas da v1 e o comando de testes, preservando
todo o enunciado original. A seção `Como Executar`, existente, recebe o fluxo local.
Não preencher `Resultados Finais` com notas não obtidas; resultados e evidências
finais continuam sob as specs 005/006.

Aceite da 003 exige todos os testes/negativos previstos aprovados, revisão semântica
de C03, documentação coerente e v1/protegidos intactos. Registrar comandos,
quantidades e limitações efetivamente verificadas na implementação.

## C06 — Entrega para as próximas specs

- A 004 deve consumir os mesmos campos, montar as mesmas mensagens, validar antes
  de publicar e registrar revisão/hash/visibilidade pública. O handle vem do ambiente.
- A 005 deve avaliar a revisão publicada após cada edição, com os mesmos dados e
  regras: cinco métricas agregadas e média geral >= 0.8, 15 respostas/75 feedbacks.
- As 3–5 iterações previstas pertencem à 005; modificações futuras da v2 repetem
  estes testes antes de publicar e avaliar. Metadados/documentação acompanham mudanças.
- Aprovação local não comprova acesso ao Hub, comportamento LLM, qualidade >= 0.8
  ou entrega pública. Esses resultados devem permanecer pendentes até prova real.
- Falhas remotas/credenciais/persistência dos scripts pertencem às specs 002/004;
  o planejamento da 003 não duplica suas implementações.
