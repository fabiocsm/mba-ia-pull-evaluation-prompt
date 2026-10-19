# Contrato: CLI de recuperação e YAML v1

**Requisitos**: 002/FR-001–FR-006. **Versão do contrato**: 1.
Este documento define comportamento futuro; não registra execução realizada.

## Interface CLI

Executar da raiz, com venv ativado:

```bash
python src/pull_prompts.py
```

Sem argumentos novos. Origem fixa `leonanluppi/bug_to_user_story_v1`; destino
`prompts/bug_to_user_story_v1.yml`, resolvido a partir da raiz do projeto pelo script.
O cliente usa a configuração do ambiente/`.env`, com precedência do ambiente.
Não fixar o handle do autor no código; ele não substitui o owner da semente.

| Resultado | Exit code | Saída mínima |
| --- | --- | --- |
| Completo | 0 | Origem, revisão, destino e confirmação da persistência |
| Configuração ausente/branca | 1 | Nome da variável, sem valor, e ação de configurar |
| Acesso negado/credencial inválida | 1 | Categoria de acesso e ação de conferir configuração |
| Origem ausente | 1 | Origem indisponível/não encontrada, sem alegar arquivo válido |
| Rede/serviço indisponível | 1 | Categoria de indisponibilidade e orientação de nova tentativa |
| Estrutura incompatível | 1 | Categoria e campo/tipo incompatível, sem conteúdo do prompt |
| Escrita/releitura/substituição falhou | 1 | Etapa, destino conhecido e conservação da cópia anterior |

Usar `check_env_vars` e rejeitar também valores só com espaços antes de instanciar
`Client`. Conferir os valores não secretos da condição e presença das variáveis da
001; somente a infraestrutura LangSmith é chamada nesta operação. Não validar
chaves de provedor por inferência nem exigir existência do dataset para o pull.

Mensagens externas e stdout/stderr de `save_yaml` em falha devem ser capturados e
substituídos por diagnóstico controlado. Não imprimir `repr(exception)`, traceback,
headers, resposta HTTP bruta, configuração do cliente ou conteúdo do ambiente.
Classificar exceções conhecidas; erro inesperado também termina em 1 com categoria
sanitizada. Warnings de metadados podem identificar campos, nunca segredos.

## Interface LangSmith

1. `Client.pull_prompt("leonanluppi/bug_to_user_story_v1", include_model=False,
   skip_cache=True, dangerously_pull_public_prompt=True)`.
2. Validar `ChatPromptTemplate` e metadados `lc_hub_owner`, `lc_hub_repo`,
   `lc_hub_commit_hash` correspondentes à origem.
3. `Client.get_prompt("leonanluppi/bug_to_user_story_v1")` para snapshot de metadados.
   Retorno ausente ou falha impede conclusão; não preencher campos por suposição.

O segundo método não consulta uma revisão histórica. Guardar seu snapshot e instante
separados: uma mudança de latest entre leituras não invalida mensagens da revisão
já recuperada, mas `repository_metadata.last_commit_hash` não é a revisão da cópia.
Para comprovar fidelidade depois, usar `pull_prompt` com o identificador
`leonanluppi/bug_to_user_story_v1:<source.commit_hash>` e o mesmo opt-in.

Nenhuma chamada de push, LLM, criação/compartilhamento de dataset ou avaliação.

## Representação suportada

- Exatamente duas mensagens: `SystemMessagePromptTemplate`, seguida de
  `HumanMessagePromptTemplate`; ambas contendo `PromptTemplate` textual `f-string`.
- `input_variables == ["bug_report"]`; `{bug_report}` permanece literal em todos
  os lugares onde aparece. Os dois textos são não vazios, sem alteração de valor.
- Ausência de parser, `partial_variables`, `optional_variables` ou `input_types`
  não vazios que não possam ser expressos pelo formato local.
- Validar também opções dos templates internos e `additional_kwargs` das mensagens.
  Dados não triviais fora dos campos preservados exigem erro explícito, sem descarte.
- Metadados e tags do template externo são preservados em `source`; não confundir
  com descrição/tags de repositório. Não aplicar validador de qualidade da v2 à v1.

Sequência diferente, mensagens adicionais/assistant, placeholders, multimodalidade,
formatos Jinja/Mustache ou conteúdo não serializável são incompatíveis neste
contrato. Se encontrados na semente real, registrar o impedimento e rever a
representação antes de continuar; não converter, truncar ou melhorar o prompt.

## YAML persistido

Raiz com a chave única `bug_to_user_story_v1`; campos conforme
[data-model.md](../data-model.md). O exemplo abaixo é esquemático, sem valores de
origem presumidos e sem servir como evidência real:

```yaml
bug_to_user_story_v1:
  system_prompt: "texto original contendo {bug_report}"
  user_prompt: "{bug_report}"
  version: v1
  input_variables: [bug_report]
  description: null
  tags: []
  source:
    identifier: leonanluppi/bug_to_user_story_v1
    commit_hash: hash_retornado_pelo_pull
    retrieved_at: instante_local_utc
    template_metadata: {}
    template_tags: null
    repository_observed_at: instante_local_utc
    repository_metadata: {}
```

`template_metadata` real inclui os campos de proveniência injetados pelo SDK;
`repository_metadata` real contém o snapshot retornado, não um mapping vazio
fabricado. `description` preserva null se assim retornada; `tags` copia a lista;
`created_at` é incluído quando retornado, em ISO 8601. `version: v1` é classificação
local. Outros metadados ficam no snapshot; a limitação de projeção/historicidade é
registrada na evidência e em aviso sanitizado, sem perder mensagens.

Somente valores simples definidos no modelo de dados. YAML válido UTF-8, legível
por `yaml.safe_load`, sem tags de objetos Python. Não há exigência de manter a
mesma apresentação visual do YAML anterior; a igualdade é dos valores textuais,
variáveis, papéis/ordem representados e metadados, sem normalização de conteúdo.

## Protocolo de persistência

1. Validar todos os dados em memória antes de tocar no destino final.
2. Criar temporário único no diretório `prompts/`, com arquivos fechados quando
   necessário para compatibilidade com Windows; destino anterior permanece intacto.
3. Chamar `save_yaml` com o caminho temporário, conferir bool e capturar diagnóstico
   bruto. Em falha, encerrar e limpar temporário, sem anunciar sucesso.
4. Reler com `yaml.safe_load`, exigir igualdade integral com dados esperados e
   conferir reconstrução System/Human e variáveis. Corrupção exige falha.
5. Fechar arquivos e chamar `os.replace(temporário, destino)`. Este é o commit local.
6. Confirmar persistência. Falhas anteriores conservam os bytes antigos; sem cópia
   anterior, destino final permanece ausente. Tentar limpeza em `finally`.

Se a limpeza falhar, informar resíduo temporário sem anunciá-lo como referência
válida. Execução concorrente e durabilidade contra queda de energia não integram
esta garantia. Depois do commit, a comparação remota e o registro documental são
verificações separadas; sua falha é uma pendência de evidência, sem falsa alegação
de que a recuperação conservou o arquivo anterior.

## Evidência de execução

Na implementação, criar `docs/recuperacao-v1.md`: data/fuso, comando/exit code,
identificador, revisão retornada, destino/hash SHA-256, versões relevantes,
comparação das duas mensagens/variáveis, metadados projetados e suas limitações,
resumo dos cenários offline e hashes dos quatro protegidos contra a baseline.
README aponta para esse registro. Não usar apenas `results/`/`screenshots/`
ignorados nem declarar notas/experimentos como resultado desta feature.
