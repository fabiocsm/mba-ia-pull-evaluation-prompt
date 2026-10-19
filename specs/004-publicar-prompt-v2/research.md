# Pesquisa — publicação pública e conferência da v2

**Data**: 2026-10-18 | **Feature**: [spec.md](spec.md)

## Fontes e método

Requisitos: [README](../../README.md), [constituição](../../.specify/memory/constitution.md),
Fase 5/R07/R12 do [plano mestre](../../plan/plano-implementacao.md),
[contrato da 003](../003-otimizar-validar-v2/contracts/otimizacao-v2.md) e
[preparação](../../docs/preparacao.md). Inspecionados os esqueletos, helpers,
testes e código instalado de `langsmith==0.13.0`, `langchain-core==1.6.4` e
`requests==2.34.2`. O código instalado governa os detalhes de versão abaixo.

A pesquisa de Hub/SDK e a de validação foram delegadas conforme a skill.
Nenhum arquivo de produção foi alterado; nenhuma publicação ou chamada LLM.
Foi comprovada somente a viabilidade de leitura anônima da semente pública v1,
na revisão já registrada pela 002; isso não comprova a futura publicidade da v2.

O [guia oficial](https://docs.langchain.com/langsmith/manage-prompts-programmatically)
confirma gestão pelo SDK, retorno de URL de interface e recuperação por revisão.
A [referência de push](https://reference.langchain.com/python/langsmith/client/Client/push_prompt)
e o [código oficial](https://github.com/langchain-ai/langsmith-sdk/blob/main/python/langsmith/client.py)
são referências complementares; `main` e documentação online podem diferir do pin.

## D01 — Validação local antes de qualquer escrita

**Decision**: preservar as três assinaturas do esqueleto; `validate_prompt()` é
pura e complementa `validate_prompt_structure`. `main()` valida arquivo/raiz;
`push_prompt_to_langsmith()` repete a validação de seus argumentos para proteger
chamadas diretas. Tipos precedem o helper, que pressupõe strings e listas.

**Rationale**: o helper cobre apenas parte do esquema e usa substring para TODO.
Reproduzir C01–C04 e a correção I1 da 003: desconsiderar só o diagnóstico exato
conhecido de falso positivo quando nenhum marcador real está no System; preservar
todos os demais erros e rejeitar retorno incoerente. Nunca alterar os dados para
conseguir aprovação. Os seis testes existentes continuam independentes.

**Alternatives considered**: confiar só no helper aceita artefatos incompletos;
modificá-lo viola o escopo; importar helpers de testes cria dependência de produção
invertida; regex de substring reprova português válido.

## D02 — Configuração e identidade por operação

**Decision**: reutilizar dotenv sem sobrescrever ambiente, `check_env_vars` mais
checagem de espaços e tracing efetivo. Confirmar workspace/handle autenticado
contra o handle configurado antes da escrita, conforme o roteiro da preparação.
Não selecionar modelos nem chamar providers; registrar a configuração não secreta
para a entrega à 005. Aplicabilidade detalhada em C04 do contrato.

**Rationale**: uma chave presente não comprova autorização para aquele destino.
O comando deve falhar antes de escrever se o handle for inválido ou divergente.
Configuração dos modelos é conferida para prontidão, sem inventar uma avaliação.

**Alternatives considered**: fixar `fabiocsm` no script contraria o contrato;
aceitar valor padrão mascara erro; revalidar modelos por inferência nesta feature
consome chamadas fora do seu escopo.

## D03 — Metadados suportados e conteúdo sem modelo

**Decision**: publicar somente `ChatPromptTemplate`, System/Human separados.
`push_prompt` recebe `object`, `is_public=True`, `description` e `tags`.
Preservar descrição local exatamente; tags esperadas são a união estável das tags
locais e dos nomes das técnicas, sem duplicações. O template recebe `metadata`
com `version`, `techniques_applied` e `local_definition_sha256`.

**Rationale**: o SDK instalado não aceita argumento arbitrário
`techniques_applied` ou `metadata` em `push_prompt`. O ensaio local de
serialização confirmou `template.metadata` em `manifest.kwargs.metadata`.
Na versão 0.13.0, push atualiza os metadados do repositório existente e também
passa `is_public=True`; não é necessário workaround de atualização manual.

**Alternatives considered**: anexar texto à descrição dificulta sua igualdade;
guardar técnicas somente no YAML perde identificação pública; publicar chain
com modelo desnecessariamente acopla a condição experimental ao prompt.

## D04 — Resolver a revisão do próprio push

**Decision**: validar a URL retornada e extrair a revisão indicada. No SDK 0.13.0
o hash pode vir abreviado em oito caracteres; resolver com
`pull_prompt_commit(destino:prefixo, include_model=False, skip_cache=True,
dangerously_pull_public_prompt=True)`, exigir prefixo correspondente e guardar
`commit_hash` completo. Conferir o objeto usando `pull_prompt(destino:hash_completo)`
com os mesmos flags. Não usar `latest` para identificar a escrita realizada.

**Rationale**: a URL do dono pode ser `/prompts/nome/prefixo?organizationId=...`,
que não é prova de acesso anônimo. Outro escritor pode mudar o último commit.
O SDK adiciona `lc_hub_owner`, `lc_hub_repo` e `lc_hub_commit_hash` ao objeto
recuperado; distingui-los dos três metadados autorais ao comparar.

**Alternatives considered**: registrar somente URL/prefixo é insuficiente;
buscar `latest` após publicar pode atribuir ao push uma revisão alheia;
comparar o objeto inteiro sem distinguir metadados adicionados gera falso erro.

## D05 — Acesso público comprovado pelo conteúdo

**Decision**: sessão HTTP nova, sem credenciais, headers de autenticação ou cookies,
`trust_env=False`, timeout `(10, 30)` e `allow_redirects=False`. Consultar os
endpoints do serviço configurado `/repos/{owner}/{name}` e
`/commits/{owner}/{name}/{hash_completo}`. Exigir HTTP 200 e JSON coerente: repo
correto e público; commit completo e manifesto igual ao lido pelo SDK.
Não deserializar o manifesto anônimo. Conferir também dashboard/endereço público.

**Rationale**: a leitura da v1 em `https://api.smith.langchain.com` retornou 200
para as duas rotas, com a revisão completa da 002, sem Authorization, X-API-Key
ou Cookie. A rota de commit coincide com a implementação instalada do SDK.
Isso comprova a viabilidade da interface; repetir com a v2 real na implementação.
Um HTML com status 200 pode ser somente a estrutura da aplicação ou login.

**Alternatives considered**: SDK com chave vazia pode reutilizar ambiente/perfil;
sessão autenticada comprova só acesso do autor; `is_public=True` enviado não
prova aplicação pelo serviço; URL do workspace não comprova publicidade.

## D06 — Hash local, metadados mutáveis e estados honestos

**Decision**: registrar SHA-256 dos bytes do YAML e da definição canônica dos seis
campos. Calcular ambos sobre a mesma leitura estável, conferindo o arquivo antes
e depois. Relacionar com hash completo do commit. Descrição/tags/publicidade do
repositório são snapshot datado; mensagens e metadados autorais ficam no commit.

**Rationale**: formatação YAML pode mudar sem mudar o template; ambos os hashes
explicam essa diferença. `push_prompt` atualiza repo e cria commit em operações
separadas, sem atomicidade global. Timeout pode deixar escrita efetivada; não
apagar ou republicar automaticamente. Booleano verdadeiro só após conferência
automatizada completa; inspeção visual posterior é gate do aceite da 004.
Registrar confirmação parcial e diagnósticos por etapa sem segredos.

**Alternatives considered**: hash do arquivo lido depois não identifica conteúdo
anterior; rollback automático pode destruir histórico; exceções brutas e saída
de `load_yaml` podem expor dados. Reutilizar o padrão de captura da 002 sem alterar
`src/utils.py`.

## D07 — Entrega à avaliação sem mudar o avaliador

**Decision**: registro versionado em `docs/publicacao-v2.md`, com resumo seguro
emitido pelo script e prova visual pública. Qualquer mudança local invalida a
conferência para uso posterior; repetir testes, push e conferência. A 005 confere
HEAD antes/depois, mantendo prompt estável durante todo o experimento.

**Rationale**: o avaliador fornecido recupera `owner/name` sem fixar revisão.
A 004 não pode garantir imutabilidade futura de HEAD nem alterar o avaliador.
O registro é um pré-requisito verificável, não uma trava no script protegido.

**Alternatives considered**: modificar o avaliador ou alegar pin inexistente viola
o contrato; evidência somente em pastas ignoradas não chega ao avaliador acadêmico.

## Resultado da pesquisa

Todas as incertezas técnicas de desenho foram resolvidas. Prontidão de acesso,
permissão de escrita, igualdade e publicidade da v2 exigem execução real futura.
Plano não certifica essas condições nem métricas; não há mudança de modelo,
instalação ou exceção à constituição nesta etapa.

## Descoberta na implementação — tag técnica do serviço (2026-10-18)

A primeira escrita real acrescentou `ChatPromptTemplate` às cinco tags autorais.
Confirmado por leitura autenticada; registro PUB-004-01 em
[publicação](../../docs/publicacao-v2.md). A comparação exige o conjunto autoral
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
