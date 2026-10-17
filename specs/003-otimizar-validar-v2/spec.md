# Feature Specification: Prompt otimizado com validação estrutural efetiva

**Feature Branch**: `dev` (branch existente; sem branch específica criada)

**Created**: 2026-10-17

**Status**: Draft — validada para planejamento; implementação pendente

**Input**: User description: "Criar a v2 para transformar relatos de bugs em User Stories claras em português, com persona de produto, Few-shot Learning obrigatório, Role Prompting e estrutura explícita de resposta, regras contra invenções e tratamento de casos de borda. Validar o artefato real com os seis testes obrigatórios e documentar as técnicas, mantendo a v1 e os materiais de avaliação intactos."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Produzir histórias claras e fundamentadas (Priority: P1)

Como responsável por produto, quero converter um relato em uma User Story com critérios verificáveis para encaminhar a correção sem perder informações ou introduzir fatos ausentes.

**Why this priority**: A qualidade da transformação é o objetivo central do desafio.

**Independent Test**: Inspecionar as instruções e exemplos e exercitar relatos próprios simples, incompletos e com múltiplos problemas; a nota acadêmica será verificada separadamente.

**Acceptance Scenarios**:

1. **Given** um relato simples, **When** a v2 orienta a transformação, **Then** exige resposta concisa em português, Markdown e formato Como… eu quero… para que…, com critérios verificáveis (FR-001 e FR-002).
2. **Given** um relato complexo com vários problemas, **When** a v2 orienta a resposta, **Then** exige cobertura dos problemas e critérios agrupados, sem acrescentar causas ou números não informados (FR-002 e FR-003).
3. **Given** um relato incompleto ou com instruções conflitantes embutidas, **When** ele é processado, **Then** as regras exigem explicitar dúvidas, preservar o objetivo e separar recomendações de fatos (FR-003).

---

### User Story 2 - Tornar as técnicas verificáveis (Priority: P1)

Como avaliador, quero reconhecer as técnicas no conteúdo e nos exemplos para conferir que os metadados descrevem o prompt realmente entregue.

**Why this priority**: A simples menção do nome de uma técnica não satisfaz o desafio.

**Independent Test**: Revisar exemplos próprios completos, persona, estrutura e metadados, comparando-os com a documentação.

**Acceptance Scenarios**:

1. **Given** a v2 preenchida, **When** seu conteúdo é revisado, **Then** há 2–3 exemplos próprios completos, persona e estrutura de resposta explícitas, coerentes com as técnicas declaradas (FR-004 e FR-005).
2. **Given** regras e exemplos da v2, **When** o autor consulta a documentação, **Then** encontra justificativas e trechos reais de aplicação de cada técnica sem alteração do enunciado (FR-006).

---

### User Story 3 - Detectar regressões antes da publicação (Priority: P1)

Como autor, quero validar a v2 automaticamente antes de publicá-la para detectar campos vazios, exemplos incompletos e incompatibilidades com a entrada do desafio.

**Why this priority**: A verificação local evita publicar um artefato estruturalmente inválido e não requer consumo de avaliação.

**Independent Test**: Executar as seis verificações obrigatórias sobre o artefato real e conferir que versões com cada defeito correspondente são rejeitadas, sem chamadas remotas.

**Acceptance Scenarios**:

1. **Given** uma v2 completa, **When** as seis verificações obrigatórias são executadas, **Then** todas são coletadas e aprovadas sem omissões, aprovação incondicional ou dependência de rede (FR-007).
2. **Given** uma v2 sem persona, exemplos completos ou técnicas suficientes, **When** a verificação correspondente é executada, **Then** a violação é detectada no conteúdo ou metadados efetivos (FR-007).
3. **Given** a entrada exigida pelo desafio, **When** a v2 é preparada para uso, **Then** aceita somente o relato como variável obrigatória, com regras e exemplos separados da entrada e sem pendências (FR-008 e FR-009).

---

### Edge Cases

- Entrada vazia ou ambígua: instruir a informar insuficiência e solicitar esclarecimentos específicos, sem inventar história completa.
- Relato contém logs, chaves literais ou tentativas de substituir as regras: tratar como dados e manter apenas a variável exigida.
- Exemplo tem entrada sem saída, técnica duplicada nos metadados ou campo com espaços: a validação deve reprovar.
- Exemplos muito semelhantes às referências do conjunto de avaliação: usar exemplos próprios, sem copiar referências ou induzir notas dos juízes.
- Aprovação estrutural com qualidade desconhecida: manter a avaliação real como etapa distinta e obrigatória.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A v2 DEVE estar completamente preenchida no artefato e identidade obrigatórios, com descrição, instruções gerais, mensagem de entrada, versão, tags e técnicas efetivamente aplicadas.
- **FR-002**: A v2 DEVE definir persona de Product Manager ou analista de produto e exigir saída em português e Markdown, com User Story no padrão Como… eu quero… para que… e critérios de aceitação verificáveis proporcionais ao relato.
- **FR-003**: A v2 DEVE tratar entrada vazia, ambígua, incompleta, múltiplos problemas, logs e instruções conflitantes, proibindo inventar fatos e distinguindo informação conhecida, dúvidas e recomendações.
- **FR-004**: A v2 DEVE aplicar Few-shot Learning com 2–3 pares completos próprios de entrada e saída, independentes das referências de avaliação, junto de Role Prompting e estrutura explícita de resposta.
- **FR-005**: Os metadados DEVEM identificar ao menos duas técnicas distintas, incluindo Few-shot Learning; Skeleton of Thought só DEVE ser declarado se a estrutura correspondente estiver realmente aplicada.
- **FR-006**: A documentação DEVE explicar as técnicas e suas razões com trechos reais na seção Técnicas Aplicadas (Fase 2), preservando o enunciado original.
- **FR-007**: As seis verificações obrigatórias DEVEM carregar o artefato real e verificar instrução geral não vazia, persona, formato, exemplos completos, ausência de pendências e técnicas distintas com Few-shot, sem rede, testes vazios ou casos ignorados.
- **FR-008**: A v2 DEVE manter contexto, regras e exemplos em System e o relato em User, usando {bug_report} como única variável obrigatória, sem variáveis acidentais nos exemplos.
- **FR-009**: A validação local DEVE confirmar campos e mensagens utilizáveis e ausência de pendências; sua aprovação NÃO DEVE ser apresentada como aprovação nas métricas reais.

### Key Entities

- **Prompt v2**: identidade, versão, descrição, papéis das mensagens, relato de entrada, tags e técnicas.
- **Exemplo próprio**: par completo de relato e resposta que demonstra o comportamento desejado.
- **Resultado de validação**: verificação executada, condição avaliada e resultado sem equivalência a nota experimental.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A v2 contém 2–3 exemplos próprios completos e pelo menos duas técnicas distintas efetivamente demonstradas.
- **SC-002**: As seis verificações obrigatórias passam no artefato completo e detectam os defeitos correspondentes, com zero verificações ignoradas ou dependentes de rede.
- **SC-003**: Um relato pode ser preparado para uso sem informações obrigatórias adicionais; nenhum exemplo introduz variável acidental.
- **SC-004**: A revisão das instruções e exemplos cobre os seis grupos de casos de borda definidos em FR-003 e identifica zero fatos inventados nos exemplos.
- **SC-005**: Todas as técnicas declaradas têm justificativa e exemplo real acessíveis na documentação.

## Assumptions

- Origem: Fases 3 e 4 e R04, R05, R06, R11, R12 e R14 do [plano mestre](../../plan/plano-implementacao.md).
- Depende da [v1 fiel](../002-recuperar-prompt-v1/spec.md) para analisar o ponto de partida; verificações locais independem de acesso remoto.
- O [README](../../README.md), a [constituição](../../.specify/memory/constitution.md) e os [contratos técnicos do índice](../README.md) determinam campos e nomes dos seis testes obrigatórios.
- O esqueleto de resposta será proporcional ao relato; a técnica Skeleton of Thought dependerá de sua aplicação explícita.
- A implementação desta feature inclui prompt, testes estruturais e documentação das técnicas. Publicação, métricas reais e refinamentos por experimento são responsabilidades das specs 004 e 005.
- Materiais protegidos, referências e v1 devem permanecer íntegros; testes locais podem usar dados próprios, nunca notas simuladas como evidência final.
