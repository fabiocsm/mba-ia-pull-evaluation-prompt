# Feature Specification: Publicação pública e rastreável da v2

**Feature Branch**: `dev` (branch existente; sem branch específica criada)

**Created**: 2026-10-17

**Status**: Draft — validada para planejamento; implementação pendente

**Input**: User description: "Permitir ao autor validar e publicar a v2 local como fabiocsm/bug_to_user_story_v2, com descrição, tags, técnicas e mensagens corretas; rejeitar artefatos inválidos antes da publicação, confirmar equivalência entre a revisão publicada e a local e registrar revisão e endereço público para os experimentos."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Publicar uma revisão válida (Priority: P1)

Como autor, quero publicar a v2 com seus metadados para que o avaliador recupere a versão correta e terceiros possam inspecioná-la.

**Why this priority**: A avaliação utiliza a revisão publicada, portanto a cópia local não basta.

**Independent Test**: Publicar uma v2 estruturalmente válida, conferir o destino e seus metadados e abrir o endereço público sem executar avaliações.

**Acceptance Scenarios**:

1. **Given** v2 aprovada localmente e configuração válida, **When** a publicação é solicitada, **Then** a revisão aparece publicamente na identidade configurada com descrição, tags e técnicas correspondentes (FR-001 a FR-003).
2. **Given** falha de acesso ou publicação, **When** o serviço não confirma sucesso, **Then** a operação informa insucesso identificável e diagnóstico sem segredos (FR-004).

---

### User Story 2 - Rejeitar artefatos incompatíveis (Priority: P1)

Como autor, quero rejeitar inconsistências antes de publicar para impedir que o avaliador receba instruções incompletas ou variáveis incompatíveis.

**Why this priority**: Falhar antes da publicação evita substituir uma revisão utilizável por um artefato inválido.

**Independent Test**: Solicitar publicação com arquivo ausente, ilegível ou com campos, técnicas ou entrada inválidos e conferir que nenhuma publicação ocorre.

**Acceptance Scenarios**:

1. **Given** artefato ausente, ilegível ou com campos vazios, **When** a publicação é solicitada, **Then** a validação rejeita a operação antes de qualquer publicação (FR-005).
2. **Given** mensagens incompatíveis, pendências, técnicas insuficientes ou variável adicional, **When** a validação é executada, **Then** identifica as violações e impede publicar (FR-005).

---

### User Story 3 - Relacionar a versão local à publicada (Priority: P2)

Como avaliador, quero identificar qual revisão publicada corresponde ao artefato local para auditar os resultados da avaliação.

**Why this priority**: Um endereço sem revisão não comprova qual conteúdo sustentou o experimento.

**Independent Test**: Recuperar a revisão recém-publicada e comparar mensagens, variável e metadados com a cópia local, registrando os identificadores.

**Acceptance Scenarios**:

1. **Given** uma publicação confirmada, **When** o conteúdo publicado é conferido, **Then** a equivalência com a v2 local, a revisão, o identificador local e a visibilidade pública ficam registrados (FR-006).
2. **Given** alteração local posterior, **When** o autor prepara novo experimento, **Then** publica e confere novamente a revisão antes de avaliar (FR-007).

---

### Edge Cases

- O handle configurado está ausente ou incorreto: rejeitar o destino e informar o pré-requisito sem inserir identidade fixa no comportamento.
- Publicação retorna sucesso, mas revisão recuperada diverge do artefato local: registrar divergência e impedir seu uso como revisão conferida.
- As técnicas não têm campo próprio no serviço: mantê-las identificáveis nos metadados suportados, sem perder a relação com a definição local.
- Falha na confirmação ou inspeção pública: distinguir publicação confirmada de equivalência ou acesso ainda não comprovados.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A publicação DEVE usar a v2 local validada e manter mensagens System e User separadas, com {bug_report} como única variável obrigatória.
- **FR-002**: O destino DEVE ser formado pela identidade lida da configuração, cujo valor neste projeto é fabiocsm, e pelo nome bug_to_user_story_v2.
- **FR-003**: A revisão DEVE ser pública e preservar descrição, tags e identificação das técnicas efetivamente presentes no artefato local.
- **FR-004**: A operação DEVE confirmar publicação antes de informar sucesso, fornecer endereço e sinalizar falhas para automação com diagnóstico sem credenciais.
- **FR-005**: A validação DEVE rejeitar, antes de publicar, arquivo ausente ou ilegível, definição incompatível, campos vazios, pendências, técnicas insuficientes ou duplicadas e variáveis de entrada inesperadas.
- **FR-006**: A conferência posterior DEVE comparar conteúdo e entrada recuperados com a cópia local, verificar metadados e visibilidade pública e registrar revisão publicada, identificação do artefato local e endereço.
- **FR-007**: Toda alteração local DEVE exigir nova publicação e conferência antes de outro experimento; a documentação DEVE distinguir publicação confirmada de revisão ainda não conferida.

### Key Entities

- **Revisão publicada**: identidade pública, revisão, mensagens, entrada, descrição, tags e técnicas.
- **Relação local/publicada**: identificação do artefato local, revisão remota, data, resultado da comparação e endereço.
- **Resultado de publicação**: validação, confirmação do serviço e eventual divergência ou impedimento.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Uma publicação válida resulta em revisão acessível sem autenticação, com conteúdo e metadados equivalentes ao artefato local.
- **SC-002**: 100% das categorias de artefato inválido descritas são rejeitadas antes de publicar.
- **SC-003**: Cada revisão liberada para avaliação tem identificação local, revisão publicada e endereço registrados, sem dúvidas sobre sua correspondência.
- **SC-004**: 100% das falhas de publicação ou conferência são distinguíveis do sucesso e preservam o sigilo das credenciais.

## Assumptions

- Origem: Fase 5 e R07/R12 do [plano mestre](../../plan/plano-implementacao.md).
- Depende da [preparação](../001-preparar-experimentos/spec.md) e da [v2 e testes](../003-otimizar-validar-v2/spec.md). Validações de erro podem usar casos próprios sem acesso remoto.
- O [README](../../README.md), a [constituição](../../.specify/memory/constitution.md) e os [contratos técnicos do índice](../README.md) definem identidade, publicidade e metadados obrigatórios.
- A verificação de equivalência será detalhada no planejamento; ela não autoriza modificar os utilitários ou o avaliador fornecidos.
- Esta spec cobre publicação e conferência. Notas, iterações de qualidade e compartilhamento do dataset pertencem às specs 005 e 006.
- Falha no serviço externo não é publicação concluída; o script obrigatório não será substituído por procedimento exclusivamente manual.
