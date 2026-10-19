# Pesquisa — otimização e validação local da v2

**Data**: 2026-10-18 | **Feature**: [spec.md](spec.md)

## Escopo e fontes

Pesquisa por inspeção dos requisitos e da instalação existente, incluindo pesquisa
delegada de validação conforme `speckit-plan`. Sem consultas ao Hub, credenciais,
chamadas de modelo ou experimentos. Não houve nova seleção de modelos; a condição
comprovada da 001 continua referência para a futura avaliação.

Fontes locais verificadas:

- [README](../../README.md), [constituição](../../.specify/memory/constitution.md),
  [Fases 3–4 do plano mestre](../../plan/plano-implementacao.md#fase-3--prompt-v2-e-estratégia-de-otimização)
  e [spec 003](spec.md).
- [v1 recuperada](../../prompts/bug_to_user_story_v1.yml) e
  [prova da recuperação](../../docs/recuperacao-v1.md).
- [Esqueleto de testes](../../tests/test_prompts.py),
  [utilitários protegidos](../../src/utils.py),
  [consumidor de publicação](../../src/push_prompts.py) e
  [avaliador protegido](../../src/evaluate.py).
- [Pins](../../requirements.txt); implementação instalada de
  `ChatPromptTemplate.from_messages` em
  `venv/lib/python3.11/site-packages/langchain_core/prompts/chat.py`, e extração
  de variáveis em `prompts/string.py` do mesmo pacote. O caminho de instalação
  serve à pesquisa local, não deve ser fixado na implementação.

## D01 — Diagnóstico baseado na v1 real

**Decision**: usar a semente da revisão
`2950c33dbd7ffaed2e440b50adfd7769d183f90faf0bae5aa4864354f88e4073`
como referência qualitativa, sem editá-la. Ela possui persona genérica, instrução
vaga e relato repetido em System/User; não contém exemplos, formato de resposta,
critérios de aceitação ou regras para informação ausente.

**Rationale**: as melhorias devem atacar limitações observáveis, sem atribuir notas
ilustrativas à semente ou reescrever o ponto de partida já recuperado.

**Alternatives considered**: novo pull desnecessário mudaria a referência se latest
avançasse; baseline numérica consumiria avaliação e pertence à 005, como opcional.

## D02 — Duas técnicas demonstráveis e estrutura proporcional

**Decision**: declarar `Few-shot Learning` e `Role Prompting`. Definir persona de
Product Manager/analista de produto, objetivo, limites e três pares completos no
System. Exigir português, Markdown, User Story e critérios verificáveis; contexto,
dúvidas e recomendações aparecem quando necessários, devidamente identificados.

**Rationale**: satisfaz o mínimo com técnicas realmente presentes. Uma estrutura
explícita organiza a resposta, mas títulos sozinhos não comprovam Skeleton of
Thought. Casos simples pedem concisão; múltiplos problemas exigem cobertura agrupada.

**Alternatives considered**: declarar três técnicas sem aplicação correspondente;
exigir raciocínio detalhado público; usar ReAct sem ferramentas. Acrescentariam
complexidade ou metadados sem evidência. Skeleton of Thought pode ser adotado depois
se houver aplicação explícita e documentação/testes coerentes.

## D03 — Exemplos completos dentro do System

**Decision**: usar três blocos com `### Exemplo 1`, `### Exemplo 2`, `### Exemplo 3`
e subseções `#### Entrada` e `#### Saída`. As instruções vêm antes de `## Exemplos`.
Cobrir simples suficiente, insuficiente/ambíguo e múltiplos problemas com log e
instrução conflitante. Exemplos próprios de domínios distintos dos casos avaliados,
sem copiar respostas de referência; não reproduzir o dataset no prompt.

**Rationale**: delimitadores permitem verificar pares completos, quantidade e
conteúdo real. O caso insuficiente demonstra esclarecimentos, em vez de fabricar
uma história completa. A cobertura semântica exige revisão, além do teste sintático.

**Alternatives considered**: campo YAML extra de exemplos não consumido pelos scripts;
mensagens few-shot extras que divergiriam do contrato System/User; verificar apenas
a palavra “exemplo”; copiar referências para facilitar notas. Todos foram rejeitados.

## D04 — Variável única e chaves literais

**Decision**: montar duas mensagens com `ChatPromptTemplate.from_messages`, System
primeiro e User/Human depois, no formato padrão `f-string`. Usar `{bug_report}`
apenas em User; chaves literais em exemplos do template são duplicadas. Conferir
`input_variables == ["bug_report"]` e renderizar relatos próprios com chaves/logs.

**Rationale**: o avaliador passa diretamente os inputs do dataset. Variáveis
acidentais quebrariam a execução ou exigiriam dados inexistentes. Texto inserido
como valor de `bug_report` não recebe uma segunda interpolação.

**Evidência local de pesquisa**: com langchain-core 1.6.4, System contendo
`{{"status": "erro"}}` e User `{bug_report}` resultou em `['bug_report']`.
A formatação preservou chaves do relato `{"id": "A"}; {nao_interpolar}`.
`{codigo}` não escapado no System criou variável extra e `KeyError` ao fornecer
somente o relato. O ensaio é prova do SDK, não do prompt v2 ainda inexistente.

**Alternatives considered**: escape global apagaria o placeholder obrigatório;
`partial` ou variáveis extras mascarariam incompatibilidade. Não são necessários.

## D05 — Helper existente mais asserções locais efetivas

**Decision**: reutilizar `load_yaml` e `validate_prompt_structure`, com checagem de
tipos antes de chamar o helper. Complementar em `tests/test_prompts.py`: raiz/chave,
seis campos, textos não brancos, listas válidas, versão, técnica obrigatória e
unicidade, exemplos e contrato de mensagens. Preservar os seis nomes obrigatórios.
Aplicar o adaptador restrito de C04: detector local de marcadores delimitados e
desconsideração apenas do diagnóstico exato de TODO do helper quando não há marcador
real no System. Demais erros, marcador em outro campo e retorno inesperado reprovam;
não modificar o texto para chamar o helper nem ignorar seus erros em bloco.

**Rationale**: o helper verifica só três campos, System/TODO e quantidade bruta de
técnicas; tipos incorretos podem gerar exceção e listas duplicadas podem passar.
Ele não cobre User, entrada única, exemplos ou coerência entre metadados e conteúdo.
A validação adicional não justifica editar o arquivo protegido.
Na análise I1, um ensaio offline confirmou que `TODOS` produz o mesmo diagnóstico
do helper que `[TODO]`. Controles com `TODOS`/`todos`/`todo`, marcadores reais e
falso positivo combinado com outro erro devem provar a distinção em T018/T020.

**Alternatives considered**: alterar `utils.py`; criar pacote de validação novo;
validar fixture fixa em vez do artefato entregue. São desnecessários ou contrários
aos requisitos. A 004 implementará a validação de push em seu script, sem importar testes.
Também foram rejeitados remover todas as ocorrências de `TODO` antes da chamada ou
aceitar qualquer erro de pendência: essas opções alterariam a entrada validada ou
ocultariam defeitos reais. A exceção é somente o diagnóstico conhecido, condicionado
ao detector independente e à aprovação das demais regras.

## D06 — Testes positivos e rejeição dos defeitos correspondentes

**Decision**: carregar o YAML real por caminho derivado de `Path(__file__)`, sem
fallback para v1 ou dados sintéticos. Compartilhar asserções com testes negativos
que modificam cópias isoladas e esperam rejeição específica. Usar temporários para
arquivo ausente/YAML inválido, sem regravar o prompt real. Bloquear rede durante
os testes; não instanciar cliente LangSmith, LLM ou avaliadores.

**Rationale**: cada teste precisa demonstrar sensibilidade à regressão pertinente.
Metadados com duas strings iguais não são duas técnicas; rótulo de saída vazio não
é Few-shot. Persona/formato só nos exemplos não substituem instruções explícitas.

**Alternatives considered**: simular notas, usar rede, `skip`/`xfail` ou aceitar
exceção genérica como prova da rejeição esperada. Essas alternativas não atendem
SC-002 e confundiriam qualidade estrutural com comportamento do modelo.

## D07 — Limite do aceite e continuidade

**Decision**: documentar diagnóstico, duas técnicas e trechos reais no README,
registrar execução dos testes na implementação e manter publicação/notas pendentes.
A revisão semântica cobre as seis bordas, origem própria dos exemplos e ausência de
fatos inventados. A 004 publica; a 005 testa o comportamento por métricas reais.

**Rationale**: é possível comprovar estrutura sem inferência e custo. A aprovação
acadêmica exige cada métrica e a média >= 0.8 em experimento real completo; isso
não decorre de pytest verde. Exemplos redigidos são demonstrações, não saídas LLM.

**Alternatives considered**: antecipar push/avaliação neste planejamento ou declarar
prontidão acadêmica com testes locais. Extrapolariam a feature e a evidência disponível.

## Resolução de lacunas

Decisões técnicas resolvidas por requisitos e inspeção local. Nenhuma dúvida de
escopo ou aceite exige esclarecimento; não há gate reprovado ou pesquisa pendente.
