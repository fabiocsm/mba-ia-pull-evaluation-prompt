# Feature Specification: Preparação reproduzível e integridade dos experimentos

**Feature Branch**: `dev` (branch existente; sem branch específica criada)

**Created**: 2026-10-17

**Status**: Draft — validada para planejamento; implementação pendente

**Input**: User description: "Preparar a execução do desafio com configuração segura, acesso ao projeto e ao handle fabiocsm, ambiente reproduzível, modelos de geração e avaliação compatíveis com as regras fornecidas e referência de integridade dos materiais originais. Registrar pré-requisitos e impedimentos antes de recuperar, publicar ou avaliar prompts."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Confirmar prontidão da execução (Priority: P1)

Como autor da entrega, quero verificar as condições de execução para iniciar o trabalho sabendo quais acessos, configurações e modelos estão disponíveis.

**Why this priority**: As próximas entregas dependem de acessos válidos; disponibilidade informada não equivale a acesso comprovado.

**Independent Test**: Conferir um relatório de preparação e suas verificações, sem depender da implementação de pull, push ou do prompt otimizado.

**Acceptance Scenarios**:

1. **Given** configuração e acessos disponíveis, **When** o autor verifica a prontidão, **Then** cada pré-requisito recebe resultado comprovado e os modelos de geração e avaliação ficam identificados (FR-001 a FR-004).
2. **Given** acesso ausente ou modelo incompatível, **When** a preparação é verificada, **Then** a etapa dependente permanece impedida, com causa e ação de resolução registradas, sem divulgação de segredos (FR-005).

---

### User Story 2 - Preservar o ponto de partida (Priority: P1)

Como avaliador, quero reconhecer os materiais originais e a origem da entrega para confiar que as melhorias virão do prompt.

**Why this priority**: A integridade precisa ser verificável mesmo após mudanças e registros intermediários.

**Independent Test**: Comparar o inventário inicial com os quatro materiais protegidos e conferir a origem e visibilidade do repositório.

**Acceptance Scenarios**:

1. **Given** o repositório antes da implementação, **When** o autor registra a referência inicial, **Then** os quatro materiais protegidos e os 15 casos com referências e dificuldades ficam identificados para comparação final (FR-006).
2. **Given** o repositório da entrega, **When** sua procedência é conferida, **Then** o vínculo de fork e a visibilidade pública são comprovados ou registrados como pendência (FR-007).

---

### User Story 3 - Planejar reprodução e consumo (Priority: P2)

Como autor, quero documentar o ambiente e as condições de medição para reproduzir os experimentos e acompanhar o consumo.

**Why this priority**: Condições explícitas reduzem falhas e comparações inválidas.

**Independent Test**: Recriar a preparação a partir do registro e verificar compatibilidade e estimativa antes de rodar experimentos completos.

**Acceptance Scenarios**:

1. **Given** as dependências previstas, **When** o ambiente isolado é preparado, **Then** sua instalação e compatibilidade são verificadas sem alterar a infraestrutura fornecida (FR-008).
2. **Given** os modelos selecionados, **When** o autor planeja de 3 a 5 ciclos, **Then** registra condições de reprodução, estimativa orientada a US$ 1–5 e consumo adicional das verificações mínimas (FR-009).

---

### Edge Cases

- Credencial existe localmente, mas está inválida ou não concede acesso ao workspace correto: registrar impedimento sem expor o valor.
- Modelo disponível na documentação, mas inacessível à conta ou incompatível com a configuração exigida: escolher alternativa compatível antes da etapa dependente.
- Incompatibilidade de dependências ou material protegido já divergente: registrar o conflito e resolver o pré-requisito sem alterar o contrato.
- Handle já existente: reutilizar fabiocsm; não criar outra identidade.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O autor DEVE verificar a presença das credenciais e configurações exigidas para cada operação, registrando somente presença, validade e impedimentos, sem valores secretos.
- **FR-002**: O projeto DEVE reutilizar a identidade pública fabiocsm e comprovar acesso ao projeto e workspace corretos.
- **FR-003**: O autor DEVE selecionar explicitamente os modelos de geração e avaliação após consultar documentação oficial e comprovar acesso e compatibilidade com temperatura zero.
- **FR-004**: A preparação DEVE adotar OpenAI inicialmente e preservar a opção Gemini, registrando provedor, modelos, data e condições utilizadas.
- **FR-005**: A preparação DEVE distinguir pronto, pendente e impedido por pré-requisito; qualquer falha DEVE informar causa e próxima ação sem declarar sucesso.
- **FR-006**: O autor DEVE registrar a referência inicial e identificadores de integridade dos quatro materiais protegidos, conservando os 15 relatos, referências e distribuição 5 simples, 7 médios e 3 complexos.
- **FR-007**: O autor DEVE verificar se o repositório é um fork público do repositório base e guardar sua identificação e resultado da verificação.
- **FR-008**: O autor DEVE preparar ambiente isolado a partir das dependências fornecidas, com verificação de compatibilidade antes das operações dependentes.
- **FR-009**: O registro de preparação DEVE conter instruções reproduzíveis, estimativa de consumo para 3–5 ciclos e distinção entre estimativa de US$ 1–5 e consumo observado; verificações mínimas também DEVEM ser contabilizadas.

### Key Entities

- **Registro de preparação**: pré-requisito, estado, evidência, data e eventual impedimento.
- **Condição experimental**: provedor, modelos de geração e avaliação e configuração comparável.
- **Referência de integridade**: estado inicial dos materiais protegidos e identidade do repositório.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos pré-requisitos têm resultado documentado antes da primeira operação dependente.
- **SC-002**: Os dois papéis de modelo têm compatibilidade comprovada e identificação reproduzível, sem credenciais expostas.
- **SC-003**: Os quatro materiais protegidos e os 15 casos originais têm referência inicial verificável para a auditoria final.
- **SC-004**: Um segundo executor consegue repetir a preparação seguindo o registro; toda divergência encontrada fica identificada antes dos experimentos.

## Assumptions

- Origem: Fase 1 e R01, R02, R12, R13 e R18 do [plano mestre](../../plan/plano-implementacao.md).
- O [README](../../README.md), a [constituição](../../.specify/memory/constitution.md) e os [contratos técnicos do índice](../README.md) são vinculantes.
- Não há dependência de outra spec para executar a preparação. Planejar as próximas specs pode ocorrer antes de comprovar os acessos; sua execução depende desta prontidão.
- A chave OpenAI informada pelo autor será reutilizada sem leitura pública de seu valor; isso não comprova as demais configurações.
- Esta spec cobre preparação e registros. Recuperação da v1, criação da v2, publicação, experimentos completos e entrega de evidências pertencem às specs seguintes.
- Seleção de nomes atuais dos modelos e confirmação remota ocorrem na execução desta feature; não são resultados já obtidos nesta especificação.
