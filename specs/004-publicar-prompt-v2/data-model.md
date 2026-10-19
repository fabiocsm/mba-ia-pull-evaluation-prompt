# Modelo de dados — publicação e correspondência local/remota

**Feature**: [spec.md](spec.md) | **Interfaces**: [contrato](contracts/publicacao-v2.md)

Entidades conceituais para validação e evidência; não exigem classes, banco,
migrações ou novo formato de prompt.

## 1. Artefato local validado

| Campo | Tipo/regra | Origem |
| --- | --- | --- |
| `definition_name` | constante `bug_to_user_story_v2`, raiz única | YAML |
| `description` | string não branca, preservada sem alterações | definição |
| `system_prompt` | string com regras, persona e exemplos completos | definição |
| `user_prompt` | string exatamente `{bug_report}` | definição |
| `version` | string exatamente `v2` | definição |
| `tags` | lista não vazia de strings não brancas | definição |
| `techniques_applied` | lista distinta por strip/casefold, inclui Few-shot e outra aplicada | definição |
| `local_file_sha256` | SHA-256 hexadecimal dos bytes UTF-8 do arquivo | leitura estável |
| `local_definition_sha256` | SHA-256 hexadecimal da definição canônica | seis campos |

Os seis campos da definição seguem o [contrato da 003](../003-otimizar-validar-v2/contracts/otimizacao-v2.md).
Identificadores derivados não são novos campos YAML. JSON canônico da definição:
`ensure_ascii=False`, `sort_keys=True`, `separators=(',', ':')`, codificado em
UTF-8 sem newline final; manter listas e textos originais. Não incluir hashes,
data, URL ou metadados injetados pelo SDK no cálculo, evitando circularidade.

Validações: tipos antes do helper; sem marcadores de pendência em campos textuais;
duas mensagens System/Human, única variável `bug_report`, sem opcionais/parciais,
System invariável e Human idêntico ao relato renderizado. A v2 atual declara
Few-shot Learning e Role Prompting; não alterar técnicas nesta feature.

## 2. Contexto de publicação

| Campo | Tipo/regra |
| --- | --- |
| `configured_handle` | texto não branco, um segmento válido, sem `/`, `:` ou URL |
| `authenticated_handle` | handle do workspace confirmado pelo serviço |
| `destination` | `{configured_handle}/bug_to_user_story_v2` |
| `workspace_id`, `endpoint` | contexto confirmado conforme preparação; sem credenciais na URL |
| `project`, `tracing` | configuração não secreta e tracing efetivo |

`configured_handle == authenticated_handle` antes da escrita. Nesta entrega o
ambiente usa `fabiocsm`; não há fallback fixo no script. Chaves são pré-requisitos
do processo e nunca campos do registro ou objeto serializado.

## 3. Objeto publicado e revisão imutável

| Campo | Tipo/regra |
| --- | --- |
| `messages` | exatamente System/Human, nesta ordem; templates idênticos aos locais |
| `input_variables` | lista exatamente `["bug_report"]` |
| `metadata.version` | `v2` |
| `metadata.techniques_applied` | lista igual à local, inclusive ordem e texto |
| `metadata.local_definition_sha256` | hash canônico local |
| `commit_hash` | hash completo retornado em `PromptCommit`, 64 caracteres hexadecimais no pin atual |
| `returned_url` | URL válida do serviço retornada pelo push, pode ser privada/de workspace |
| `public_url` | endereço público de conteúdo/revisão efetivamente conferido sem credenciais |

Há uma relação de uma definição para muitas tentativas de publicação; commits
podem ser reutilizados pelo serviço para conteúdo idêntico. Não exigir hash novo
por execução. Validar o hash completo fornecido pelo SDK; prefixo da URL deve
corresponder, nunca servir como identificador final.

Campos `lc_hub_owner`, `lc_hub_repo`, `lc_hub_commit_hash` são acrescentados pelo
SDK no pull: conferir identidade/revisão, mas não tratá-los como dados locais
autorais nem comparar objetos integrais sem essa distinção.

## 4. Snapshot de metadados do repositório

| Campo | Regra |
| --- | --- |
| `owner`, `repo_handle`, `full_name` | destino configurado, sem identidade inesperada |
| `description` | igualdade exata com descrição local |
| `tags` | conjunto igual à união estável de tags locais + nomes das técnicas |
| `is_public` | booleano `True` observado, não apenas solicitado |
| `last_commit_hash` | igual à revisão conferida no momento da liberação |
| `observed_at` | ISO 8601 com fuso/UTC explícito |

Tags projetadas: percorrer tags locais e depois técnicas, mantendo o primeiro
texto e removendo duplicações por `strip().casefold()`. Comparar conjunto remoto,
sem exigir ordem de armazenamento; não perder tags locais ou técnicas. Metadados
de repositório são mutáveis e ficam datados separadamente do commit.

## 5. Resultado e relação local/publicada

Registro versionado por tentativa em `docs/publicacao-v2.md`:

- Data/hora com fuso, destino, workspace/endpoint não secretos e versões SDK/core.
- Caminho e hashes do artefato; revisão completa, URL retornada e URL pública.
- Publicação: não iniciada, não confirmada ou confirmada; nunca deduzir ausência
  de escrita após timeout.
- Conferência automatizada: pendente, divergente, falhou ou conferida; resultados separados
  para mensagens/variáveis, metadados do commit, snapshot do repo e acesso anônimo.
- Inspeção visual posterior: pendente, falhou ou conferida, com data e evidência
  disponível; obrigatória para o aceite da 004 e a entrega à 005.
- Código de saída do CLI e etapa/diagnóstico seguro, independentes do estado
  posterior de inspeção visual.
- Identificação do registro anterior quando nova edição o substitui para avaliação.

Não registrar valores de chaves, headers, cookies, perfis, respostas brutas de
erro ou stack traces sensíveis. Ausência de uma prova não equivale a aprovação.

## 6. Transições e invariantes

```text
não validado -> validado -> publicação confirmada -> revisão conferida
     |              |                |
     v              v                v
 rejeitado    não confirmada    pendente/divergente/falhou
                                     |
                                     v
                       conferência posterior, sem repetir push por reflexo
```

`True` em `push_prompt_to_langsmith()` exige revisão conferida automaticamente
por C07.1–C07.4 do contrato. `main()` retorna zero somente se também comprovar
arquivo local estável. Esse retorno pode coexistir com inspeção visual pendente;
o aceite da 004 e a entrega à 005 exigem também C07.5 e registro de evidência.
Qualquer alteração local posterior torna o registro anterior inaplicável ao
artefato atual para avaliação.
Um arquivo alterado e depois restaurado byte a byte volta a ter o mesmo hash;
ainda se exige revalidar revisão remota/HEAD antes do experimento.

Novo HEAD ou metadados divergentes não apagam a prova histórica da revisão
fixada; impedem usá-la como estado atual sem nova conferência. A 005 registra o
experimento correspondente e verifica estabilidade, pois seu avaliador usa HEAD.
