# Feature Specification: Recuperação fiel do prompt original

**Feature Branch**: `dev` (branch existente; sem branch específica criada)

**Created**: 2026-10-17

**Status**: Draft — validada para planejamento; implementação pendente

**Input**: User description: "Permitir ao autor recuperar o prompt público leonanluppi/bug_to_user_story_v1 e guardar a versão v1 local como referência fiel, com mensagens, variáveis e metadados aplicáveis preservados, informando origem, destino e falhas sem expor credenciais nem incorporar melhorias à semente."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Guardar a referência original (Priority: P1)

Como autor, quero recuperar e guardar o prompt semente para analisar o ponto de partida real da otimização.

**Why this priority**: Sem a referência fiel não existe comparação verificável entre v1 e v2.

**Independent Test**: Recuperar a semente real e comparar as mensagens da cópia local com a origem, sem depender da v2 ou dos experimentos.

**Acceptance Scenarios**:

1. **Given** acesso válido à semente, **When** o autor solicita sua recuperação, **Then** recebe uma cópia local identificada como v1, não vazia e equivalente ao conteúdo da origem (FR-001 a FR-003).
2. **Given** mensagens com espaços, acentos e variável de entrada, **When** a cópia é persistida e relida, **Then** o texto e a variável permanecem intactos, sem preenchimento ou reescrita (FR-003 e FR-004).

---

### User Story 2 - Diagnosticar recuperação malsucedida (Priority: P2)

Como autor, quero entender falhas de recuperação para corrigir o pré-requisito e tentar novamente com segurança.

**Why this priority**: Um artefato parcial ou uma mensagem de sucesso incorreta compromete o trabalho seguinte.

**Independent Test**: Verificar os cenários de credencial ausente, origem indisponível, conteúdo incompatível e destino sem permissão.

**Acceptance Scenarios**:

1. **Given** credencial ausente ou acesso negado, **When** a recuperação é solicitada, **Then** a operação falha com diagnóstico e sem segredo exposto (FR-005).
2. **Given** estrutura incompatível ou falha de gravação, **When** a recuperação não pode terminar, **Then** a operação informa falha e não apresenta cópia incompleta como referência válida (FR-005 e FR-006).

---

### Edge Cases

- Origem retorna tipo ou mensagens que não podem ser representados fielmente: falhar explicitamente, sem descartar trechos.
- Metadado não se aplica ao formato local: preservar o conteúdo integral e registrar a limitação de representação.
- Uma v1 válida já existe e uma nova recuperação falha: não substituí-la por conteúdo parcial.
- Texto contém chaves ou instruções vagas: conservá-lo como recebido; as melhorias pertencem à v2.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A recuperação DEVE usar exclusivamente a semente pública leonanluppi/bug_to_user_story_v1 e a autorização explícita de recuperação pública exigida pelo contrato.
- **FR-002**: O autor DEVE receber o artefato local v1 no destino obrigatório, identificando origem, destino e confirmação da persistência.
- **FR-003**: A cópia DEVE manter integralmente mensagens, papéis, ordem representável, texto, variável de entrada e metadados aplicáveis, sem omissões silenciosas.
- **FR-004**: A v1 DEVE ser conservada como referência, sem preencher a entrada, corrigir a redação ou antecipar melhorias da v2.
- **FR-005**: Credencial ausente, indisponibilidade, acesso negado, formato incompatível ou falha de gravação DEVEM resultar em insucesso identificável pela automação e diagnóstico sem segredos.
- **FR-006**: O sucesso DEVE ser informado somente após a persistência completa; uma recuperação malsucedida NÃO DEVE deixar uma cópia parcial apresentada como válida nem destruir a cópia válida anterior.

### Key Entities

- **Prompt semente**: identidade pública, mensagens, papéis, variável de entrada e metadados retornados.
- **Cópia de referência v1**: artefato local fiel ligado à origem, separado das futuras revisões otimizadas.
- **Resultado da recuperação**: sucesso ou falha, origem, destino e diagnóstico sem credenciais.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Uma recuperação real bem-sucedida produz uma cópia local não vazia, com 100% do conteúdo das mensagens preservado na comparação com a origem.
- **SC-002**: 100% dos cenários de falha definidos apresentam insucesso identificável e nenhuma cópia parcial é anunciada como válida.
- **SC-003**: A revisão do artefato recuperado encontra zero melhorias locais ou substituições da variável de entrada.

## Assumptions

- Origem: Fase 2 e R03/R12 do [plano mestre](../../plan/plano-implementacao.md).
- Depende da prontidão de acesso da [spec 001](../001-preparar-experimentos/spec.md); cenários de erro podem ser verificados isoladamente.
- O [README](../../README.md), a [constituição](../../.specify/memory/constitution.md) e os [contratos técnicos do índice](../README.md) fixam origem, destino, formato e autorização pública.
- O mecanismo existente de persistência será reutilizado; detalhes de representação e tratamento de erro pertencem ao planejamento.
- Otimização, publicação e medição de qualidade estão fora desta spec. A recuperação real ainda deverá ser executada e comprovada.
