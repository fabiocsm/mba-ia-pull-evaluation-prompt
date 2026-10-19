# Pesquisa: recuperação fiel da v1

**Data**: 2026-10-17. **Escopo**: 002/FR-001–FR-006, R03/R12.

Inspeção do repositório, SDK instalado e fontes oficiais. A pesquisa de integração
foi delegada a um agente conforme a skill; o ensaio sintético offline confirmou
as versões `langsmith=0.13.0`, `langchain-core=1.6.4` e a preservação de acentos,
espaços e quebras finais em `.prompt.template`. Nenhum acesso à semente, leitura
de `.env`, instalação, publicação ou chamada LLM ocorreu nesta pesquisa.

## 1. Cliente, opt-in e revisão — FR-001/FR-003

**Decisão**: `Client.pull_prompt` na origem obrigatória, com
`dangerously_pull_public_prompt=True`, `include_model=False`, `skip_cache=True`.
Validar retorno como `ChatPromptTemplate`; a assinatura retorna `Any`.
Guardar `lc_hub_owner`, `lc_hub_repo` e `lc_hub_commit_hash` de `prompt.metadata`;
conferir origem e revisão não vazia antes de persistir.

**Razão**: o SDK recupera `PromptCommit` e injeta esses campos no objeto carregado.
A revisão pertence à resposta recuperada, sem depender de outra leitura de latest.
Não solicitar modelo nem resolver referências explícitas a segredos.

**Alternativas consideradas**: inferir a revisão via `get_prompt().last_commit_hash`
pode ligar o arquivo a outra revisão. Usar somente o YAML fornecido não comprova
recuperação. CLI não substitui o script obrigatório.

Fonte: [cliente oficial v0.13.0](https://github.com/langchain-ai/langsmith-sdk/blob/v0.13.0/python/langsmith/client.py),
funções `pull_prompt`, `pull_prompt_commit`, `_process_prompt_manifest` e `get_prompt`.
Código instalado correspondente inspecionado; não depender de métodos privados.

## 2. Representação fiel — FR-003/FR-004

**Decisão**: aceitar somente `ChatPromptTemplate` com exatamente uma mensagem
`SystemMessagePromptTemplate` seguida de uma `HumanMessagePromptTemplate`, ambas
com `PromptTemplate` textual `f-string`. Extrair o valor de `.prompt.template`
sem normalizar ou preencher; preservar inclusive `{bug_report}` repetido.
Usar `system_prompt`, `user_prompt` e `input_variables` no YAML.

**Razão**: corresponde ao formato local System/User. Estruturas diferentes são
um caso de erro explicitamente previsto pela spec. Validar mensagens inteiras,
não apenas filtrar as de tipos conhecidos.

**Alternativas consideradas**: selecionar a primeira mensagem de cada papel,
concatenar mensagens ou converter valores por `str()` perderia informação.
Um exportador universal de objetos LangChain excede esta feature. Se a semente
real não couber na representação, registrar o impedimento e rever o desenho antes
de ampliar o formato; não adaptar a semente para fazê-la caber.

**Validações adicionais**: rejeitar mensagens extras, placeholders, conteúdo
multimodal, formatos diferentes, parser de saída e bindings parciais/opcionais
não vazios. Campos não triviais de mensagens e templates internos, como
`additional_kwargs`, metadados, tags ou tipos especiais, precisam ser preservados
no contrato ou resultar em incompatibilidade; nunca ignorados.
Metadados/tags do template externo têm campos explícitos no contrato.

Fonte: [código oficial de ChatPromptTemplate](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/prompts/chat.py),
referência de implementação atual; decisões de versão comprovadas nos arquivos
instalados da 1.6.4 `langchain_core/prompts/chat.py`,
`prompt.py` e `base.py`. O formato aceito e as restrições são decisão local,
não uma limitação geral do LangChain.

## 3. Metadados da origem e dados locais — FR-002/FR-003

**Decisão**: consultar `get_prompt` e guardar seu `model_dump(mode="json")` em
`source.repository_metadata`, com `repository_observed_at`. Projetar descrição,
tags e data de criação nos campos compatíveis, somente quando retornadas.
Preservar separadamente `prompt.metadata` e `prompt.tags` em tipos JSON/YAML
simples. Identificar `version: v1` como rótulo local, não versão declarada no Hub.

**Razão**: `PromptCommit` e `Prompt` são entidades diferentes. `get_prompt` ignora
sufixo de revisão e retorna metadados atuais do repositório. Descrição/tags/datas
não têm garantia de snapshot transacional com o commit das mensagens.
O registro separado permite explicitar essa limitação sem perder conteúdo.

**Alternativas consideradas**: copiar data, descrição e tags do YAML de exemplo
inventaria proveniência. Tratar metadados atuais como históricos do commit seria
incorreto. Não reutilizar `validate_prompt_structure`, que exige técnicas da v2.

Fonte: [schemas oficiais v0.13.0](https://github.com/langchain-ai/langsmith-sdk/blob/v0.13.0/python/langsmith/schemas.py),
`PromptCommit`/`Prompt`, e `get_prompt` no cliente citado. Campos desconhecidos
não serializáveis provocam erro; não usar `default=str` nem tags Python no YAML.

## 4. Persistência sem destruir a referência — FR-006

**Decisão**: gerar mapeamento completo antes de escrever; usar temporário único
adjacente, chamar `save_yaml`, conferir retorno, reler com `yaml.safe_load` e
comparar dados/templates. Fechar arquivos antes de `os.replace`. Só então sucesso.
Limpar temporário nas falhas anteriores ao commit local.

**Razão**: o utilitário local abre com `w`; não deve receber o caminho final antes
da validação. Temporário no mesmo filesystem permite substituição atômica.
O carregador seguro restringe a releitura a dados YAML simples.

**Alternativas consideradas**: alterar `utils.py` viola a proteção do desafio;
escrever direto pode truncar a v1. Backup/restauração adiciona mais pontos de falha.
Não prometer durabilidade contra queda de energia ou coordenação de escritores
concorrentes: o contrato é execução única e proteção contra falhas antes da troca.

Fontes: [utils.py](../../src/utils.py),
[os.replace](https://docs.python.org/3.11/library/os.html#os.replace) e
[documentação PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation).

## 5. Configuração, diagnóstico e prova — FR-005/FR-006

**Decisão**: reutilizar dotenv sem sobrescrever ambiente e `check_env_vars` para
presença, acrescentando detecção de valores em branco. Conferir a configuração
transversal da 001 antes da execução correspondente. A dependência remota do pull
é LangSmith; não autenticar OpenAI/Google nem iniciar inferência nesta feature.
Usar códigos 0/1 e mensagens por etapa, sem reproduzir corpo HTTP, headers,
credenciais, ambiente ou exceções externas integrais.

**Razão**: exceções podem incluir informação sensível. Categoria, origem, destino
e ação recomendada bastam para diagnosticar ausência de configuração, acesso,
indisponibilidade, estrutura e escrita. `save_yaml` já imprime sua exceção:
encapsular a chamada com captura de saída e emitir diagnóstico sanitizado se falhar,
sem editar o utilitário. Só dados da semente entram no mapeamento persistido.

**Alternativas consideradas**: traceback automático e `print(exception)` expõem
dados não controlados. Credencial inválida pode ser testada com cliente simulado;
não há necessidade de alterar o `.env` ou fazer chamadas inválidas reais.

**Prova planejada**: casos isolados para falhas de configuração/rede/estrutura e
cada etapa da escrita; sentinela e hashes da cópia anterior; um pull real com
comparação de mensagens na mesma revisão. Registrar resultados verdadeiros em
`docs/recuperacao-v1.md`, fora de diretórios ignorados.

## Resolução das incertezas

Não restam decisões técnicas abertas. A forma e os metadados efetivos da semente,
a validade atual das credenciais e o sucesso da persistência permanecem resultados
para a implementação, sem constituir lacunas de requisitos ou provas já obtidas.
