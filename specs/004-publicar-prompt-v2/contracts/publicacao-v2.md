# Contrato — CLI de publicação e conferência da v2

**Feature**: [spec.md](../spec.md) | **Modelo**: [data-model.md](../data-model.md)

Interface externa: `python src/push_prompts.py`, da raiz. Sem flags novas,
sem endpoint próprio e sem chamadas a modelos. O SDK publica; HTTP anônimo
confere publicidade; CLI/interface LangSmith complementam a inspeção.

## C01 — Arquivo, identidade e leitura estável

- Usar `load_yaml` com `prompts/bug_to_user_story_v2.yml`, resolvido pela raiz
  do script. Não usar fallback para v1, fixture, outro arquivo ou definição.
- Raiz mapping com somente `bug_to_user_story_v2`, cujo valor é mapping.
- Exatamente `description`, `system_prompt`, `user_prompt`, `version`, `tags`,
  `techniques_applied`; tipos conforme o modelo. Strings não brancas; `version: v2`.
- Detectar ausente, ilegível, YAML inválido/vazio, raiz incompatível e definição
  inesperada antes de instanciar cliente ou escrever remotamente.
- Reutilizar o loader protegido com captura de sua saída: ele imprime detalhes
  de erro YAML que podem conter conteúdo sensível. Emitir categoria/etapa segura,
  sem repetir o texto bruto ou depender de `None` como único caso inválido.
- Calcular hash dos bytes antes e após o carregamento e após o push/conferência.
  Qualquer diferença impede liberação. Hash canônico corresponde ao dict
  efetivamente validado/publicado; não reabrir o YAML para montar o template.

## C02 — Validação pura e compatibilidade com a 003

`validate_prompt(prompt_data: dict) -> tuple[bool, list]` preserva assinatura e
retorna booleano mais lista de diagnósticos estáveis. Não exige ambiente, não
cria cliente, não escreve e não modifica o argumento. Dados ruins retornam
reprovação em vez de falhar incidentalmente no helper.

1. Conferir mapping e tipos antes de `validate_prompt_structure`, que pressupõe
   `.strip()` e `len()`. Chamar o helper com os dados originais quando seguro.
2. Exigir campos, versão e listas conforme C01; técnicas com pelo menos duas
   entradas distintas por `strip().casefold()`, incluindo Few-shot Learning e
   outra técnica do README realmente aplicada. A v2 atual/003 usa exatamente
   Few-shot Learning e Role Prompting; não ampliar técnicas nesta feature.
3. Verificar persona, formato e 2–3 pares completos de exemplos de entrada/saída
   conforme C03 da 003, para a execução direta também rejeitar instruções
   incompletas. Verificação sintática não substitui revisão semântica ou LLM.
4. Detectar pendências nos campos textuais, inclusive itens de listas e chaves:
   tokens maiúsculos isolados `TODO`, `FIXME`, `TBD`, ou formas entre colchetes
   sem distinção de caixa e com espaços internos. Usar limites Unicode.
5. `TODOS`, `todos` e `todo` em prosa não são pendências. Desconsiderar apenas
   `system_prompt ainda contém TODOs` se o detector não encontra marcador real
   no System. Todos os outros erros persistem. Não sanitizar texto para validar.
6. Retorno do helper deve ser tupla `(bool, list[str])`, com diagnósticos não
   brancos e booleano coerente com lista vazia. Retorno inesperado/incoerente
   reprova. Falso positivo combinado com outro defeito continua reprovando.

Conservar os seis métodos obrigatórios de `TestPrompts`. Produção não importa
helpers do módulo de testes nem altera `src/utils.py`.

## C03 — Montagem e renderização sem inferência

Usar `ChatPromptTemplate.from_messages` com System e User/Human, nesta ordem,
sem chain ou modelo. User é exatamente `{bug_report}`; input_variables é
exatamente `["bug_report"]`; nenhuma variável parcial/opcional. System não
possui variável de entrada e não interpola o relato.

Montar e formatar localmente com relato comum, vazio e JSON/chaves literais.
Human deve ser idêntico ao relato recebido e System invariável. Chaves dos
exemplos devem permanecer escapadas no template e renderizar como literais.
Rejeitar falha de montagem, chaves desequilibradas, variável adicional, variável
ausente, User decorado/repetido e mensagens extras. Comparar posteriormente
os templates brutos, e também a renderização, sem confundi-los entre si.

## C04 — Configuração e destino

Reutilizar `check_env_vars`; complementar espaços e valores inválidos. Carregar
`.env` sem sobrescrever variáveis exportadas e sem imprimir credenciais.

| Configuração | Regra de prontidão |
| --- | --- |
| `LANGSMITH_API_KEY` | presente e não branca; acesso confirmado antes da escrita |
| `LANGSMITH_PROJECT` | presente; preservar contexto da preparação; não criar projeto de avaliação aqui |
| `USERNAME_LANGSMITH_HUB` | presente, um handle sem separadores de caminho/revisão ou URL |
| `LANGSMITH_TRACING` | habilitado e efetivamente ativo no SDK, incluindo precedência de aliases |
| `LANGSMITH_ENDPOINT`, `LANGSMITH_WORKSPACE_ID` | contexto da preparação, quando configurados; sem segredo na URL |
| `LLM_PROVIDER`, `LLM_MODEL`, `EVAL_MODEL` | presentes; provider OpenAI ou Google; conferir nomes, sem executar modelos |
| `OPENAI_API_KEY` ou `GOOGLE_API_KEY` | presente conforme provider; não enviada ao objeto do prompt |

Antes de escrever, consultar `/settings` pelo `client.request_with_retries`
e conferir `tenant_handle` e `id` contra configuração/contexto da 001.
Usar cliente novo com timeout finito, sem depender de cache de settings de
outra execução. O roteiro/CLI da preparação auxilia seleção do workspace;
sem contexto inequívoco, interromper antes da escrita. Não fixar `fabiocsm`
no script: comparar handle autenticado com o configurado. No projeto este vale
`fabiocsm`; ausência, valor malformado ou divergência reprovam.

`push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool` aceita
somente `prompt_name == "bug_to_user_story_v2"`, valida o dict antes de criar
cliente e forma `f"{username}/{prompt_name}"`. Chamada direta obedece aos mesmos
gates. Modelos permanecem configuração da 005, sem nova seleção nesta feature.

## C05 — Publicação e projeção de metadados

Construir o objeto validado com `metadata` contendo apenas os metadados autorais
previstos: `version`, `techniques_applied`, `local_definition_sha256`.
O hash segue a canonicalização do modelo. Não serializar ambiente, modelo,
credencial, cliente ou headers. Preservar mensagens exatamente.

Chamar `Client.push_prompt` uma vez por execução com destino configurado,
`object=template`, `is_public=True`, `description=description_local` e `tags`
projetadas pelo modelo: união estável das tags originais e nomes das técnicas.
Não inventar parâmetro `techniques_applied`. O SDK instalado atualiza repo
existente ou cria ausente; ambos precisam ser testados. Não deletar revisão
anterior, criar prompt de teste extra ou sobrescrever o histórico deliberadamente.

Um erro pode ocorrer depois de atualizar metadados e antes de confirmar commit.
Retries internos do SDK não equivalem a autorização para loop adicional de push.
Timeout/retorno inválido não prova inexistência de escrita; investigar por leitura.

## C06 — Confirmação e resolução da revisão

No caminho normal, o retorno deve ser URL não vazia do serviço esperado e do prompt correto, sem
userinfo ou parâmetros secretos. No SDK 0.13.0, aceitar os formatos reconhecidos
`/prompts/{name}/{prefixo}` e `/hub/{owner}/{name}:{prefixo}`, validando owner
quando presente. Não imprimir retornos arbitrários. Guardar a URL válida retornada
como URL de publicação; não qualificá-la automaticamente como pública.

Extrair prefixo hexadecimal; resolver via
`pull_prompt_commit(f"{destino}:{prefixo}", include_model=False, skip_cache=True,
dangerously_pull_public_prompt=True)`. Exigir hash completo válido e correspondente
ao prefixo; prefixo ambíguo, ausente ou revisão incompatível causam insucesso.
Usar o hash completo em todas as consultas seguintes. `latest` só serve para
conferir o HEAD atual, nunca para atribuir identidade à publicação realizada.

## C07 — Conferência independente e pública

Os itens C07.1–C07.4 são verificações automatizadas do CLI. O item C07.5 é
uma inspeção posterior obrigatória para o aceite da 004 e a entrega à 005.

1. Recuperar `destino:hash_completo` com `pull_prompt`, `include_model=False`,
   `skip_cache=True`, `dangerously_pull_public_prompt=True`. Exigir
   ChatPromptTemplate com as duas mensagens, templates, variáveis e renderização
   idênticos a C03. Comparar metadados autorais; conferir separadamente
   `lc_hub_owner`, `lc_hub_repo`, `lc_hub_commit_hash` adicionados pelo SDK.
2. Consultar `get_prompt(destino)`: conferir owner/nome, descrição, conjunto de
   tags autorais esperado (mais somente a tag técnica opcional `ChatPromptTemplate`), `is_public is True` e `last_commit_hash == hash_completo`.
   Retorno `None` ou acesso negado não são confirmação. Guardar snapshot datado.
3. Em nova `requests.Session`, definir `trust_env=False`, sem auth/cookies ou
   headers secretos; GET no endpoint configurado `/repos/{owner}/{name}` e
   `/commits/{owner}/{name}/{hash_completo}`, com timeout `(10, 30)` e redirects
   desabilitados. Não reutilizar sessão do Client. Validar ausência de
   Authorization/X-API-Key/Cookie no request efetivo.
4. Exigir 200 e JSON: `repo` com identidade/publicidade/metadados equivalentes;
   commit com hash completo e `manifest` idêntico ao de `PromptCommit` autenticado.
   Comparar JSON estruturalmente, sem deserializar o objeto anônimo. HTML/login,
   3xx, 401/403/404, manifesto diferente ou falta de campos não comprovam publicidade.
5. Após o sucesso automatizado do CLI, abrir o Hub/dashboard para conferir
   apresentação e endereço público em sessão sem autenticação; registrar prova
   visual acessível em `docs/evidencias/`
   ou URL pública estável. Um HTML 200 isolado não substitui a prova de conteúdo.

O script guarda as URLs anônimas de repo/commit efetivamente conferidas nos
itens automatizados. Inspeção visual e registro de evidência ficam em estado
próprio; enquanto C07.5 estiver pendente ou falhar, o aceite da 004 e a entrega
à 005 permanecem bloqueados, mesmo que o CLI tenha retornado zero.

Sem espera indefinida: falha transitória nas leituras automatizadas fica como
conferência pendente, com diagnóstico seguro e saída diferente de zero. Reconsulta posterior não precisa
republicar. Alteração concorrente de HEAD/metadados impede liberação atual, mesmo
que o commit histórico coincida com a cópia local.

## C08 — Estados, saída e documentação

- `validate_prompt`: `(True, [])` só após validação completa; caso contrário
  `(False, erros_seguro)`.
- `push_prompt_to_langsmith`: `True` só após C04, C05, C06 e C07.1–C07.4;
  `False` em falha dessas verificações, com etapa.
- `main()`: código `0` só após leitura/validação, push/conferência automatizada
  e estabilidade final do arquivo; código `1` em falhas esperadas. Exceção
  inesperada não vira sucesso; seu diagnóstico também é seguro.
- O CLI conclui sem aguardar C07.5. Seu retorno zero comprova o sucesso
  automatizado; a inspeção visual e o registro das evidências são conferidos
  posteriormente para concluir o aceite da 004 antes da entrega à 005.
- Separar mensagens identificáveis de validação rejeitada, publicação não
  confirmada, publicação confirmada com conferência pendente/divergente e revisão
  conferida automaticamente. Não emitir sucesso final do CLI logo após `push_prompt`
  nem apresentar seu retorno zero como aceite completo da 004.
- Após escrita parcial, deixar explícito que o remoto pode ter mudado. Não
  prometer rollback nem alegar que nenhuma publicação ocorreu.
- Resumo seguro inclui data com fuso, destino, dois hashes locais, commit completo,
  URLs válidas e resultados de conteúdo/metadados/publicidade. Não emitir YAML
  completo, valores de env, payload bruto de erro ou `str(exception)` sem controle.
- Copiar a comprovação para o registro versionado `docs/publicacao-v2.md`, uma
  entrada por tentativa, preservando histórico. O script fornece resumo; o registro
  e sua ligação no README são parte do aceite da implementação, sem obrigar o
  script a editar Markdown automaticamente.

## C09 — Matriz obrigatória de falhas offline

Cada caso exige diagnóstico pertinente, argumento intacto e nenhum push quando
anterior à escrita. Dublês só testam contratos; não são evidência final de serviço.

| Grupo | Casos | Critério |
| --- | --- | --- |
| Arquivo/raiz | ausente, ilegível, YAML inválido/vazio, escalar/lista, definição ausente/nula/extra | reprovar antes de cliente |
| Campos | cada obrigatório ausente, tipo errado, vazio/espaços, campo extra, versão diversa | apontar campo e reprovar |
| Técnicas/tags | listas inválidas, item branco, menos de duas técnicas, duplicatas normalizadas, sem Few-shot ou técnica sem demonstração | não publicar |
| Pendências | TODO/FIXME/TBD e formas entre colchetes em texto/metadados | detector reprova |
| I1 | TODOS/todos/todo; falso positivo com campo ausente ou outra falha; retorno helper inválido/incoerente | aceitar só prosa válida; outros defeitos continuam bloqueando |
| Mensagens | User decorado/repetido, variável extra/ausente, chaves inválidas, falha de renderização | não publicar |
| Configuração | ausência/espaços, handle inválido/divergente, tenant errado, tracing desabilitado | não escrever |
| Serviço | autenticação, acesso, conexão, timeout, retorno vazio/URL inválida, create/update falhando | insucesso correto; sem push extra automático |
| Revisão | prefixo inválido, hash divergente, erro de pull, tipo/conteúdo/variável/metadados divergentes | publicação pode existir, conferência não liberada |
| Público | privado, HTTP anônimo negado/redirecionado, HTML/JSON incompatível, manifesto diferente | não declarar acesso público |
| Concorrência | YAML alterado durante operação, HEAD/repo alterado por outro escritor | não atribuir hash incorreto ou liberar revisão velha |
| Sigilo | sentinela secreta em exceção/URL/loader/HTTP | ausente de stdout, stderr e resumo; diagnóstico ainda útil |

Testar positivos com YAML real, prosa comum, renderização com chaves, create e
update, commit reutilizado e retorno completo conferido. Bloquear rede, LLM,
dotenv real e credenciais externas no escopo dos testes; isolar import/module
cache para não interferir nos testes do pull/preparação. Preservar os seis nomes
obrigatórios e rodar regressão existente.

## C10 — Entrega à 005 e invalidação

Qualquer edição local exige testes, nova publicação e nova conferência antes
do próximo experimento, inclusive se apenas metadados mudarem. Registro anterior
permanece histórico e não libera os novos bytes. Não exigir commit remoto novo
quando o serviço deduplicar conteúdo; exigir igualdade comprovada e datas reais.

A 005 verifica hashes locais, metadados e HEAD novamente antes de avaliar, mantém
prompt estável durante execução e confere depois. Isso é um gate operacional,
pois o avaliador protegido usa o identificador sem pin. Não alterar o avaliador
para impor esse gate. Cada experimento liga-se ao registro desta feature.

Conclusão da 004 exige escrita pública real, equivalência e documentação; não
comprova 15 respostas, 75 feedbacks, métricas `>= 0.8`, 3–5 iterações ou dataset
compartilhado. Essas provas pertencem às specs 005/006.

## Descoberta na implementação — tag técnica do serviço (2026-10-18)

A primeira escrita real acrescentou `ChatPromptTemplate` às cinco tags autorais.
Confirmado por leitura autenticada; registro PUB-004-01 em
[publicação](../../../docs/publicacao-v2.md). A comparação exige o conjunto autoral
integral e admite somente essa tag técnica opcional adicional; desconhecidas
continuam divergentes. O snapshot registra todas as tags observadas. A projeção
no push permanece inalterada. Esta correção operacional não altera o YAML nem
requisitos acadêmicos de descrição, técnicas e tags. Complementa a regra de
igualdade de tags acima, que não previa metadados derivados pelo serviço.

## Descoberta na implementação — conflito no reuso de commit (2026-10-18)

O SDK/serviço retornou `LangSmithConflictError` ao reenviar conteúdo já existente
(PUB-004-02/03). Complemento excepcional a C05/C06/C08: depois de uma única
chamada de push, esse conflito permite somente leitura para conferir uma revisão
existente. O HEAD serve como candidato existente, nunca como identidade de escrita
própria. Exigir hash completo e todos os gates C07/estabilidade; o manifesto
precisa ser exatamente igual ao local antes de desserializar. Outra exceção ou
qualquer divergência reprova. Sem retry de escrita ou sucesso pelo conflito em si.

O resumo registra `returned_url: null`, `revision_source: existing_after_conflict`
e `publication: revisão existente conferida; push em conflito`. Não se fabrica
URL devolvida pelo SDK nem se alega nova revisão criada. URLs anônimas continuam
sendo as efetivamente verificadas. O fluxo normal mantém a regra prefixo do
retorno → hash completo. Materializa C10 (reuso permitido) sem relaxar o enunciado.
