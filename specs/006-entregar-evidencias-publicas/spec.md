# Feature Specification: Entrega pública com evidências acessíveis e reprodução

**Feature Branch**: `dev` (branch existente; sem branch específica criada)

**Created**: 2026-10-17

**Status**: Draft — validada para planejamento; implementação pendente

**Input**: User description: "Entregar o fork público com implementação, v2 final e README preservando o enunciado, técnicas justificadas, comparação v1/v2, histórico e resultados reais. Disponibilizar o dataset e experimentos por link público estável, screenshots das cinco notas e traces de três dificuldades, validar acesso sem login, reprodução e integridade final sem expor credenciais."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inspecionar resultados sem acesso privado (Priority: P1)

Como avaliador acadêmico, quero abrir as evidências sem pertencer ao workspace do autor para confirmar o conjunto, as notas e os exemplos que sustentam a entrega.

**Why this priority**: Links privados ou arquivos somente locais não permitem avaliar a atividade.

**Independent Test**: Abrir o material em sessão sem autenticação e conferir o dataset, experimento final, screenshots e traces identificados.

**Acceptance Scenarios**:

1. **Given** experimento final aprovado, **When** o avaliador abre os links da entrega sem autenticação, **Then** encontra os 15 casos, experimento da v2 e screenshots legíveis das cinco notas (FR-001 e FR-002).
2. **Given** o link compartilhado não mostra detalhes dos traces, **When** o avaliador consulta as evidências complementares, **Then** consegue inspecionar entrada, instruções, resposta e julgamentos de pelo menos um caso simples, um médio e um complexo (FR-002 e FR-003).
3. **Given** endereço público já registrado, **When** a documentação é revisada, **Then** o endereço é reutilizado sem novo compartilhamento que invalide a referência anterior (FR-004).

---

### User Story 2 - Compreender o processo e repetir a execução (Priority: P1)

Como leitor da entrega, quero entender o que mudou da v1 para a v2 e seguir as instruções para reproduzir o trabalho com minhas credenciais.

**Why this priority**: A documentação deve comprovar tanto as técnicas aplicadas quanto a executabilidade.

**Independent Test**: Revisar as três seções obrigatórias e repetir os comandos em ambiente limpo, relacionando a configuração e a revisão utilizadas.

**Acceptance Scenarios**:

1. **Given** a documentação final, **When** o leitor revisa o processo, **Then** encontra técnicas com exemplos reais, comparação v1/v2, ciclos, cinco notas, média e links correspondentes (FR-005 e FR-006).
2. **Given** ambiente limpo e credenciais locais válidas, **When** o leitor segue Como Executar, **Then** consegue preparar, recuperar, validar, publicar e avaliar com configuração identificada e interpretação de sucesso ou falha (FR-007).
3. **Given** somente comparação qualitativa da v1 disponível, **When** os resultados são apresentados, **Then** notas ilustrativas não são usadas como baseline real e qualquer comparação numérica adicional tem experimento identificável (FR-006).

---

### User Story 3 - Conferir a entrega íntegra (Priority: P2)

Como autor, quero revisar o conteúdo público e a integridade final para entregar exatamente os artefatos avaliados e as evidências acessíveis.

**Why this priority**: A entrega deve manter a rastreabilidade mesmo após commits, reprodução e publicação dos materiais.

**Independent Test**: Conferir o fork sem autenticação, comparar materiais protegidos à referência inicial e relacionar a v2 entregue à revisão aprovada.

**Acceptance Scenarios**:

1. **Given** fork pronto, **When** o autor faz a revisão final, **Then** código, v2 funcional, documentação e evidências estão acessíveis, os materiais protegidos permanecem íntegros e não há credenciais publicadas (FR-008 e FR-009).
2. **Given** reprodução gera novo experimento ou a v2 é alterada, **When** a entrega é atualizada, **Then** o histórico permanece preservado e a revisão final só é aprovada com evidência correspondente e custo adicional registrado (FR-010).

---

### Edge Cases

- Link funciona no workspace, mas exige login fora dele: substituir pela referência pública apropriada e complementar detalhes com evidência legível.
- Screenshots guardadas apenas em pastas ignoradas: disponibilizá-las em local incluído na entrega ou endereço público estável.
- Screenshot mostra chave, configuração secreta ou dado pessoal de acesso: remover a exposição antes da publicação.
- Experimento completo ainda reprovado: documentar pendências sem preencher Resultados Finais com números simulados.
- Link público existente desconhecido: inspecionar o estado e registros antes de compartilhar novamente; não regenerar o link por conveniência.
- Reprodução altera a revisão final: verificar novamente a correspondência e repetir a avaliação quando o conteúdo do prompt mudar.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O avaliador DEVE ter acesso público ao dataset com 15 exemplos e aos experimentos correspondentes da v2, com relação explícita à revisão final aprovada.
- **FR-002**: As evidências DEVEM incluir screenshots legíveis das cinco métricas aprovadas, dataset com 15 casos e tracing detalhado de pelo menos três casos, cobrindo dificuldades simples, média e complexa.
- **FR-003**: Os links DEVEM ser conferidos sem autenticação; detalhes não visíveis publicamente DEVEM ter screenshots complementares acessíveis na entrega, jamais apenas arquivos locais ignorados.
- **FR-004**: O endereço retornado pelo primeiro compartilhamento público DEVE ser guardado e reutilizado; novo compartilhamento que substitua o link registrado DEVE ser evitado.
- **FR-005**: O README DEVE preservar os requisitos originais e conter Técnicas Aplicadas (Fase 2), Resultados Finais e Como Executar, com justificativas e exemplos reais de aplicação.
- **FR-006**: Resultados Finais DEVE apresentar cinco médias, média geral, revisão avaliada, histórico de ciclos, comparação qualitativa v1/v2 e links de prompt, dataset e experimentos; comparação numérica da v1 só DEVE usar experimento real identificado.
- **FR-007**: Como Executar DEVE conter pré-requisitos, dependências, configuração sem segredos, provedor e modelos usados, comandos ordenados e interpretação dos resultados; o roteiro DEVE ser conferido em ambiente limpo com credenciais locais.
- **FR-008**: A entrega DEVE estar em fork público do repositório base, com código implementado, v2 funcional e documentação; conteúdo e links DEVEM ser conferidos sem login.
- **FR-009**: A revisão final DEVE comprovar integridade dos quatro materiais protegidos, dos 15 exemplos e suas referências, preservação de OpenAI/Gemini e ausência de credenciais em código, documentação, logs e screenshots publicados.
- **FR-010**: A reprodução DEVE preservar os experimentos anteriores e identificar novos resultados e consumo; alteração da v2 exige testes, nova publicação e avaliação, com atualização da evidência final antes da conclusão.

### Key Entities

- **Pacote de entrega**: fork público, código, v2, documentação e conjunto de evidências acessíveis.
- **Evidência pública**: endereço ou screenshot, item comprovado, revisão e experimento correspondentes, resultado da conferência sem login.
- **Registro de reprodução**: configuração sem segredos, comandos, resultado, novos experimentos e consumo adicional.
- **Conferência de integridade**: comparação final com referência inicial e conclusão sobre artefatos protegidos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos links exigidos abrem sem login e permitem conferir os 15 exemplos e o experimento final correspondente, com complementos legíveis quando necessários.
- **SC-002**: As cinco notas e pelo menos três traces de dificuldades distintas têm evidência pública legível ligada ao experimento final.
- **SC-003**: As três seções obrigatórias contêm todas as informações exigidas, sem alterar o enunciado ou apresentar números ilustrativos como resultados.
- **SC-004**: Um segundo executor com credenciais válidas consegue completar o roteiro documentado em ambiente limpo; divergências ficam resolvidas ou explicitamente pendentes antes da conclusão.
- **SC-005**: Os quatro materiais protegidos permanecem iguais à referência inicial, nenhum segredo aparece nos materiais publicados e a v2 entregue corresponde à revisão aprovada.

## Assumptions

- Origem: Fase 8, seção 9 e R12 a R18 do [plano mestre](../../plan/plano-implementacao.md).
- Depende da referência da [spec 001](../001-preparar-experimentos/spec.md) e de resultados aprovados da [spec 005](../005-avaliar-iterar-v2/spec.md) para concluir a entrega. A estrutura documental pode ser preparada antes, com resultados pendentes explicitados.
- O [README](../../README.md), a [constituição](../../.specify/memory/constitution.md) e os [contratos técnicos do índice](../README.md) determinam evidências e compartilhamento obrigatório.
- A comparação obrigatória entre v1 e v2 é qualitativa. Experimento numérico adicional da v1 é opcional, com custo e condições próprios registrados.
- A entrega não inclui nova interface, novos serviços ou outra avaliação. Arquivos de evidência precisam estar efetivamente acessíveis fora das pastas ignoradas.
- A aprovação desta especificação não comprova que existam links públicos, screenshots ou resultados reais; sua execução e conferência continuam pendentes.
