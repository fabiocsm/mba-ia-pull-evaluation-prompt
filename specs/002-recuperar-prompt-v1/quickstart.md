# Validação: recuperação fiel da v1

**Estado**: roteiro planejado. Executar após implementação e tarefas/análise da 002.
Não executar o esqueleto atual esperando comprovar recuperação.

## Pré-requisitos e preparação

Executar da raiz do repositório. Consultar a
[matriz atual da 001](../../docs/preparacao.md#matriz-atual): ambiente/integridade,
configuração e contexto LangSmith comprovados; acesso à semente ainda pendente.
Não sobrescrever `.env` nem expor chaves. Usar os modelos/provedor da condição
registrada na 001; este roteiro não faz seleção ou chamadas a modelos.

Ambiente já preparado:

```bash
source venv/bin/activate
python -m pip check
```

Em outro ambiente, criar e ativar venv antes de instalar os pins:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
```

Em PowerShell, ativar com `venv\Scripts\Activate.ps1`. Não recriar o ambiente existente
para um teste de falha. Conferir configuração sem imprimir valores:

```bash
python - <<'PY'
import os
from dotenv import load_dotenv
load_dotenv('.env', override=False)
required = ('LANGSMITH_API_KEY', 'LANGSMITH_PROJECT', 'USERNAME_LANGSMITH_HUB',
            'LANGSMITH_TRACING', 'LLM_PROVIDER', 'LLM_MODEL', 'EVAL_MODEL')
missing = [name for name in required if not os.getenv(name, '').strip()]
provider = os.getenv('LLM_PROVIDER', '').lower()
assert provider in ('openai', 'google'), 'Provedor não configurado'
key = 'OPENAI_API_KEY' if provider == 'openai' else 'GOOGLE_API_KEY'
if not os.getenv(key, '').strip():
    missing.append(key)
print('Variáveis ausentes:', missing)
assert not missing, 'Resolver configuração antes da execução'
assert os.getenv('USERNAME_LANGSMITH_HUB') == 'fabiocsm'
assert os.getenv('LANGSMITH_TRACING', '').lower() == 'true'
PY
```

## Verificações offline — V01–V11

Seguir a entrega incremental de `tasks.md`: na US1, escrever e aprovar V01–V03
em T005/T011 antes do primeiro pull real (T012–T013, V12). Na US2, acrescentar
V04–V11 em T014–T016 e aprovar a suíte completa em T020 antes do aceite final.
O MVP da US1 ainda não comprova SC-002 nem conclui a feature. Se as correções da
US2 afetarem o fluxo de sucesso ou a serialização, repetir T012–T013; caso
contrário, conservar a evidência real já obtida, conforme T020.

Na implementação, criar `tests/test_pull_prompts.py` e executar:

```bash
pytest tests/test_pull_prompts.py -v
```

Usar cliente simulado, caminhos temporários e falhas controladas; nunca alterar
credenciais locais ou tornar o diretório real sem permissão. Os mocks são prova
somente dos cenários controlados, não da recuperação real exigida em V12.

| ID | Cenário | Resultado esperado e requisito |
| --- | --- | --- |
| V01 | Duas mensagens válidas, cliente controlado | Origem/opt-in corretos, saída 0, destino/definição corretos; FR-001/002 |
| V02 | Acentos, espaços, quebras finais, chaves literais e variável duplicada | Valores idênticos após releitura, sem `format`/`strip`; FR-003/004 |
| V03 | Revisão e metadados distintos do YAML fornecido; latest muda entre leituras | Revisão do objeto preservada, snapshot separado, sem data/tags inventadas; FR-003/004 |
| V04 | Tipo, ordem ou quantidade incompatível; placeholder, multimodal, parser, binding ou formato não suportado | Saída 1, campo diagnosticado e sem omissões; FR-003/005 |
| V05 | Metadado não serializável ou opção interna não representada | Saída 1 antes de gravar; metadado simples sem projeção preservado no snapshot e limitação registrada; FR-003/005 |
| V06 | Credencial ausente/branca, inclusive ambiente exportado vazio sobre dotenv | Saída 1 antes do cliente; diagnóstico sem valores; FR-005/006 |
| V07 | Credencial inválida/acesso negado, origem ausente ou indisponibilidade/rede; falha/None em get_prompt | Saída 1 por categoria, sem segredo/corpo HTTP; FR-005/006 |
| V08 | Criação do diretório/temporário sem permissão | Saída 1, sem confirmação; destino anterior intacto; FR-005/006 |
| V09 | save_yaml retorna False ou falha após escrever parcialmente | Saída 1, temporário limpo e diagnóstico capturado/sanitizado; FR-005/006 |
| V10 | Releitura falha ou dados relidos divergem; falha da reconstrução | Saída 1, nenhuma substituição do destino; FR-005/006 |
| V11 | os.replace falha; limpeza falha em cenário separado | Saída 1 antes do commit, cópia preservada; resíduo não apresentado como válido; FR-005/006 |

Para V04–V11, parametrizar com destino ausente e destino com sentinela/cópia válida;
comparar bytes/hash antes e depois. Confirmar ausência de mensagem de sucesso e
nenhum arquivo parcial no destino final. Injetar marcador secreto nas exceções e
na saída simulada do helper para provar que não aparece em stdout/stderr/artefatos.
Não repetir testes estruturais da v2 ou rodar seus esqueletos como prova do pull.

## Recuperação real e comparação — V12

Após V01–V03 passarem em T011, executar o primeiro pull da US1 (T012).
V04–V11 serão comprovados na US2 antes do aceite final, conforme a sequência acima:

```bash
python src/pull_prompts.py
```

Esperar status 0 e confirmação com origem, revisão e destino. Se retornar 1,
registrar a categoria e corrigir o pré-requisito; não prosseguir à 003 como se a v1
estivesse pronta. Comparar o YAML à mesma revisão, não a latest:

```bash
python - <<'PY'
from pathlib import Path
import hashlib
import yaml
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import (
    SystemMessagePromptTemplate, HumanMessagePromptTemplate,
)
load_dotenv('.env', override=False)
path = Path('prompts/bug_to_user_story_v1.yml')
data = yaml.safe_load(path.read_text(encoding='utf-8'))['bug_to_user_story_v1']
source = data['source']
assert source['identifier'] == 'leonanluppi/bug_to_user_story_v1'
assert source['commit_hash']
prompt = Client().pull_prompt(
    source['identifier'] + ':' + source['commit_hash'],
    include_model=False, skip_cache=True, dangerously_pull_public_prompt=True,
)
assert isinstance(prompt, ChatPromptTemplate)
assert len(prompt.messages) == 2
assert isinstance(prompt.messages[0], SystemMessagePromptTemplate)
assert isinstance(prompt.messages[1], HumanMessagePromptTemplate)
assert prompt.metadata['lc_hub_commit_hash'] == source['commit_hash']
assert prompt.messages[0].prompt.template == data['system_prompt']
assert prompt.messages[1].prompt.template == data['user_prompt']
assert prompt.input_variables == data['input_variables'] == ['bug_report']
assert prompt.metadata == source['template_metadata']
assert prompt.tags == source['template_tags']
assert data['version'] == 'v1'
assert '{bug_report}' in data['system_prompt'] + data['user_prompt']
print('Comparação da revisão: OK; mensagens 2/2 idênticas')
print('Revisão:', source['commit_hash'])
print('SHA-256 local:', hashlib.sha256(path.read_bytes()).hexdigest())
PY
```

A comparação não executa o prompt ou o modelo. Uma indisponibilidade posterior à
persistência pode impedir esta prova: manter a cópia, registrar a pendência e
repetir a leitura da mesma revisão. Não relatar SC-001 como atendido sem comparação.
Conferir a projeção de descrição/tags/created_at contra o snapshot salvo; os demais
metadados devem permanecer em `source`, sem atribuir-lhes historicidade de commit.

## Integridade e documentação

```bash
git diff -- src/evaluate.py src/metrics.py src/utils.py datasets/bug_to_user_story.jsonl
git diff --check
```

Esperar diff vazio nos protegidos. Comparar também SHA-256 com
`docs/integridade-inicial.json` para detectar mudanças já commitadas; confirmar
15 exemplos/referências e distribuição 5/7/3. Revisar diff da v1 para assegurar zero
melhorias locais: somente conteúdo recuperado e proveniência rotulada.

Registrar data/fuso, versões, comando/exit code, revisão, destino/hash, resultado
V01–V12 e comparação de integridade em `docs/recuperacao-v1.md`. Acrescentar ligação
e comando à seção `Como Executar` do README preservando o contrato acadêmico.
Uma mudança de revisão na origem deve ser explicada no registro; não omitir falhas.

**Aceite**: SC-001 = recuperação real, YAML não vazio e duas mensagens 100% idênticas;
SC-002 = todos os cenários de falha com status 1 e nenhuma referência parcial;
SC-003 = zero melhorias/substituições após comparação/revisão. Métricas e experimentos
LangSmith permanecem nas specs seguintes.
