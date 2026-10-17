# Feature Specification: Avaliação íntegra e otimização guiada por evidências

**Feature Branch**: `dev` (branch existente; sem branch específica criada)

**Created**: 2026-10-17

**Status**: Draft — validada para planejamento; implementação pendente

**Input**: User description: "Avaliar a revisão publicada da v2 com a infraestrutura e os 15 exemplos originais, auditar 15 respostas e 75 feedbacks válidos, analisar casos fracos e executar ciclos planejados de otimização até cada métrica agregada e a média geral atingirem 0.8. Preservar histórico, condições de comparação e vínculo entre revisão local, revisão publicada e experimento, sem fabricar notas ou modificar avaliadores e referências."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Obter um experimento completo e auditável (Priority: P1)

Como autor, quero executar e conferir a avaliação completa para saber se as notas representam todos os relatos do desafio.

**Why this priority**: Médias favoráveis podem ocultar respostas ou feedbacks ausentes.

**Independent Test**: Executar um primeiro experimento real com revisão publicada estável e auditar respostas e feedbacks, sem depender de ciclos posteriores ou da entrega pública.

**Acceptance Scenarios**:

1. **Given** revisão publicada e conjunto remoto idêntico aos 15 casos originais, **When** a avaliação é executada, **Then** um experimento real registra 15 respostas e 75 feedbacks válidos associados aos exemplos (FR-001 a FR-003).
2. **Given** dataset remoto divergente ou uma nota ausente, **When** a integridade é conferida, **Then** o experimento não é declarado completo ou aprovado, mesmo com médias aparentes acima do limiar (FR-001, FR-003 e FR-004).
3. **Given** experimento completo, **When** o autor analisa suas notas e traces, **Then** consegue relacionar entradas, respostas e julgamentos aos resultados e às condições usadas (FR-005 e FR-006).

---

### User Story 2 - Aprovar pela regra integral (Priority: P1)

Como avaliador, quero conferir as cinco métricas e a média para reconhecer apenas resultados que atendem ao critério acadêmico.

**Why this priority**: A média geral não pode compensar uma métrica insuficiente.

**Independent Test**: Conferir as cinco médias do experimento completo e sua média geral com a agregação fornecida e registrar a decisão.

**Acceptance Scenarios**:

1. **Given** 15 respostas e 75 notas válidas, **When** as cinco métricas agregadas e a média são pelo menos 0.8, **Then** a revisão correspondente pode ser declarada aprovada (FR-004).
2. **Given** qualquer métrica agregada abaixo de 0.8, **When** a decisão é registrada, **Then** o resultado é reprovado ainda que a média geral seja suficiente, e orienta o próximo ajuste (FR-004 e FR-007).
3. **Given** nota baixa de um exemplo e todas as médias suficientes, **When** o autor analisa o caso, **Then** registra a limitação sem impor um novo limiar por exemplo (FR-004).

---

### User Story 3 - Melhorar a v2 com histórico comparável (Priority: P2)

Como autor, quero relacionar falhas, hipóteses e alterações a cada revisão avaliada para demonstrar a melhoria real sem perder resultados anteriores.

**Why this priority**: A justificativa das mudanças é parte da evidência acadêmica.

**Independent Test**: Conferir a sequência de registros de ciclos reais, com revisões e experimentos acessíveis e condições de comparação declaradas.

**Acceptance Scenarios**:

1. **Given** falhas observadas no primeiro experimento, **When** o autor refina a v2, **Then** registra hipótese, alteração, testes, nova publicação e experimento antes de comparar as notas (FR-007 e FR-008).
2. **Given** modelos ou condições alterados entre ciclos, **When** os resultados são documentados, **Then** a mudança é identificada como nova condição experimental e o histórico anterior é preservado (FR-005 e FR-008).
3. **Given** aprovação antecipada ou reprovação após cinco ciclos, **When** o autor registra o estado, **Then** justifica os ciclos efetivos e as pendências sem chamadas artificiais para completar contagem ou declaração indevida de aprovação (FR-009).
4. **Given** nova edição após uma aprovação, **When** essa edição se torna candidata final, **Then** passa novamente por testes, publicação e avaliação completa antes de herdar qualquer conclusão (FR-010).

---

### Edge Cases

- Dataset remoto com mesmo nome e conteúdo diferente: usar condição isolada de projeto, preservando os dados e experimentos anteriores.
- Nota ausente, não numérica, infinita ou fora de [0,1], resposta vazia ou erro de parsing: registrar falha e não aceitar experimento incompleto.
- A revisão publicada muda durante a avaliação: a correspondência fica comprometida e precisa ser restabelecida antes de aceitar a evidência.
- Oscilação de notas com configuração constante: preservar todos os resultados e evitar seleção exclusiva de execuções favoráveis.
- Referência contém detalhes que não estão no relato: investigar o julgamento sem copiar respostas ou introduzir fatos para agradar ao avaliador.
- Rate limit ou falha de transporte: diagnosticar antes de repetir e contabilizar chamadas adicionais, mantendo as regras originais.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Antes da avaliação, o autor DEVE conferir igualdade entre os 15 casos remotos e originais, incluindo entradas, referências e distribuição 5/7/3; divergências DEVEM ser resolvidas por isolamento do projeto sem alterar o conjunto original.
- **FR-002**: O experimento DEVE avaliar a revisão efetivamente publicada e conferida da v2, mantida estável durante sua execução, usando a infraestrutura fornecida sem alterações.
- **FR-003**: Um experimento completo DEVE conter 15 respostas não vazias e cinco feedbacks por exemplo, totalizando 75 notas numéricas, finitas e no intervalo [0,1]; falhas DEVEM permanecer identificadas.
- **FR-004**: A aprovação DEVE exigir experimento completo, Helpfulness, Correctness, F1-Score, Clarity e Precision agregadas individualmente >= 0.8 e média das cinco >= 0.8, conforme a agregação original; notas por exemplo orientam análise, sem substituir o critério agregado.
- **FR-005**: Cada ciclo DEVE registrar data, provedor, modelos, conjunto usado, identificação local da v2, revisão publicada, identificação e endereço do experimento, cinco médias, média geral, completude e decisão.
- **FR-006**: O autor DEVE inspecionar os casos de menor nota e pelo menos um trace simples, um médio e um complexo, relacionando entrada, instruções, resposta, julgamentos e feedback disponível.
- **FR-007**: Cada ajuste DEVE ter problema observado e hipótese explícitos, restringindo as mudanças de comportamento à v2; documentação e verificações DEVEM acompanhar a revisão.
- **FR-008**: O histórico DEVE preservar todos os ciclos e manter condições comparáveis; mudanças de modelo, provedor ou conjunto isolado DEVEM ser registradas como nova condição antes da comparação.
- **FR-009**: O trabalho DEVE planejar 3–5 ciclos e registrar os realizados; aprovação antecipada exige justificativa, reprovação após cinco exige diagnóstico e planejamento de continuidade, sem relaxar o critério de aprovação.
- **FR-010**: Qualquer edição posterior à aprovação DEVE ser testada, publicada e avaliada novamente; resultados simulados, cópia das referências, manipulação do juiz ou alteração de métricas, dados e limiares são proibidos.

### Key Entities

- **Experimento**: revisão avaliada, condições, conjunto de casos, respostas, feedbacks, médias, endereço e decisão.
- **Ciclo de otimização**: problema, hipótese, alteração, validação, revisão publicada e experimento correspondente.
- **Evidência de trace**: entrada, instruções, resposta, julgamentos e feedback de um exemplo identificado.
- **Condição de comparação**: modelos, provedor, identidade do conjunto e integridade dos materiais originais.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O experimento final contém 15 respostas e 75 notas válidas, sem casos omitidos ou substituídos.
- **SC-002**: Cada uma das cinco médias e a média geral da revisão final atinge pelo menos 0.8 segundo a regra original.
- **SC-003**: 100% dos ciclos realizados têm registro completo da hipótese, alteração quando aplicável, revisão, condições, resultados e endereço; resultados insuficientes continuam visíveis.
- **SC-004**: Ao menos três traces, cobrindo um caso de cada dificuldade, permitem inspecionar a origem das notas.
- **SC-005**: A revisão final local e publicada coincide com a revisão do experimento aprovado; qualquer edição posterior exige nova evidência.

## Assumptions

- Origem: Fases 6–7, estratégia de custo da seção 7 e R08, R09, R10, R12 e R17 do [plano mestre](../../plan/plano-implementacao.md).
- Depende da [preparação](../001-preparar-experimentos/spec.md), dos [testes da v2](../003-otimizar-validar-v2/spec.md) e da [publicação conferida](../004-publicar-prompt-v2/spec.md).
- O [README](../../README.md), a [constituição](../../.specify/memory/constitution.md) e os [contratos técnicos do índice](../README.md) vinculam avaliação, dataset, feedbacks e limiar.
- Não há promessa de aprovação em quantidade fixa de ciclos. A estimativa de US$ 1–5 orienta o consumo, sem ser garantia de custo; testes e chamadas adicionais serão contabilizados.
- Comparação numérica da v1 é opcional e exige experimento real adicional sob as mesmas condições. Comparação qualitativa será obrigatória na entrega.
- Esta spec cobre execução, análise e iteração; não implementa outro avaliador. Compartilhamento público e documentação final são da spec 006.
- Não existem notas comprovadas nesta especificação. Aprovação estrutural e aprovação experimental são verificações cumulativas e independentes.
