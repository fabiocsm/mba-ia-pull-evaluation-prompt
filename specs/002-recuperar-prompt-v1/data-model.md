# Modelo de dados: recuperação da v1

**Escopo**: arquivo YAML e resultado do CLI; sem banco de dados.
Contrato normativo de representação: [recuperacao-v1.md](contracts/recuperacao-v1.md).

## Prompt semente — remoto/transitório

| Campo | Tipo | Regra |
| --- | --- | --- |
| identifier | string | Sempre `leonanluppi/bug_to_user_story_v1` |
| commit_hash | string | Obtido de `metadata.lc_hub_commit_hash`, não vazio |
| messages | sequência de 2 templates | System, depois Human; texto `f-string` |
| input_variables | lista de strings | Exatamente `bug_report` neste contrato |
| metadata | mapping ou null | Preservar como dados simples; contém identidade/revisão do SDK |
| tags | lista ou null | Tags do template, separadas de tags do repositório |
| repository_metadata | mapping | Snapshot `Prompt.model_dump(mode="json")` de `get_prompt` |

Textos são valores exatos, incluindo espaços, quebras finais e duplicação da
variável no System/User. Não chamar formatação/inferência para extrair o texto.
Bindings, parsers, templates internos com opções não representadas ou mensagens
fora do contrato tornam o objeto incompatível, sem omissão ou conversão silenciosa.

## Cópia de referência v1 — local/persistente

Uma execução bem-sucedida produz um documento com uma única definição raiz
`bug_to_user_story_v1`. Campos:

| Campo | Tipo | Origem/validação |
| --- | --- | --- |
| system_prompt | string | Valor literal de `messages[0].prompt.template`, não vazio |
| user_prompt | string | Valor literal de `messages[1].prompt.template`, não vazio |
| version | string | `v1`, rótulo local da entrega |
| input_variables | lista de strings | Cópia exata da lista retornada, igual a `[bug_report]` |
| description | string ou null | Descrição do repositório, sem fallback inventado |
| tags | lista de strings | Tags do repositório retornadas |
| created_at | string opcional | ISO 8601 retornado no snapshot, se disponível |
| source | mapping | Proveniência e metadados abaixo |

`source` contém `identifier`, `commit_hash`, `retrieved_at` (instante local UTC do
retorno do pull), `template_metadata`, `template_tags`, `repository_observed_at`
e `repository_metadata`. Instantes locais são explicitamente observações, nunca
datas atribuídas ao conteúdo original. Hash SHA-256 do arquivo fica no registro
externo, evitando autorreferência.

Valores opcionais ausentes são omitidos ou mantidos como null conforme contrato;
não copiar `created_at`, descrição ou tags do YAML ilustrativo existente.
Dados suportados: mappings com chaves string, listas, strings, bool, números
finitos e null. Outros tipos exigem falha identificável antes da escrita.

## Resultado da recuperação — processo

| Campo lógico | Sucesso | Falha |
| --- | --- | --- |
| exit_code | 0 | 1 |
| origem/destino | Identificadores conhecidos | Identificadores conhecidos |
| revision | Hash da revisão persistida | Apenas se já recuperado; sem declarar persistência |
| stage | Persistido | Configuração, acesso/rede, representação ou persistência |
| diagnostic | Confirmação do arquivo completo | Categoria sanitizada e próxima ação |

Não é necessário criar classe ou serializar este resultado: é contrato de retorno
e mensagens do comando. A função `pull_prompts_from_langsmith()` retorna bool;
`main()` converte para 0/1. Falhas esperadas não propagam traceback ao terminal.

## Relacionamentos e estados

- Uma cópia local corresponde a exatamente uma revisão da semente.
- Um snapshot de metadados do repositório é observado separadamente dessa revisão;
  seu `last_commit_hash` não redefine a revisão da cópia.
- `inicial → configurado → recuperado → validado → temporário conferido → persistido`.
- Qualquer falha antes de `persistido` termina em `falha`, conserva a cópia anterior
  byte a byte e tenta remover o temporário; sem arquivo anterior, destino permanece
  ausente. Resíduo temporário cuja limpeza falhar nunca é anunciado como v1 válida.
- `os.replace` concluído é o ponto de commit. Hash/comparação remota posteriores
  pertencem à validação documentada e podem apontar pendência sem desfazer a cópia.
- Nova execução bem-sucedida pode substituir a referência por nova revisão real;
  registrar alteração de revisão/hash na evidência, sem tratá-la como edição local.
