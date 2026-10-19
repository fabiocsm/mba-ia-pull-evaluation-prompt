# Guia de validação — publicação pública e rastreável da v2

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md)

Este roteiro é para a implementação posterior. O planejamento não executou push
ou avaliação. Não execute a etapa remota enquanto o script ainda contiver os
esqueletos: primeiro gerar tarefas, analisar e implementar. O comando remoto
publica a v2 real no handle configurado, sem criar prompt descartável.

## Pré-requisitos e ambiente

Executar da raiz, com dependências e contexto da 001 e aceite local da 003.
Os contratos detalhados estão em [contracts/publicacao-v2.md](contracts/publicacao-v2.md)
e os hashes/estados em [data-model.md](data-model.md). Não copiar template sobre
`.env` existente, não imprimir chaves e não usar `set -x`.

Reutilize o ambiente já preparado:

```bash
source venv/bin/activate
python --version
python -m pip check
```

Se o ambiente não existir, selecione Python 3.10+ compatível com os pins (3.11.14
foi comprovado), crie e ative antes de instalar:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
```

Esperado: dependências compatíveis, sem necessidade de alteração de requirements.
Não reinstalar por rotina se o ambiente existente estiver íntegro.

## Matriz de verificações

| ID | Cenário | Resultado esperado | Requisito |
| --- | --- | --- | --- |
| V01 | Integridade da preparação/v1 | quatro protegidos e v1 intactos; 15 exemplos 5/7/3 | R12/R13 |
| V02 | Seis testes obrigatórios | seis nomes coletados e aprovados, sem skip/xfail | FR-001/FR-005 |
| V03 | Validação do YAML e conteúdo | arquivo/raiz/seis campos, persona, formato, exemplos e técnicas aceitos | FR-001/FR-005 |
| V04 | Mensagens e renderização | System/Human e entrada única; chaves preservadas | FR-001/FR-005 |
| V05 | Configuração/identidade negativa | ausência, espaços, handle/tenant incorretos bloqueiam escrita | FR-002/FR-004 |
| V06 | Matriz C09 offline | defeitos rejeitados, sentinelas não expostas, nenhum modelo/rede | FR-003–FR-005 |
| V07 | Publicação real pelo script | confirmação correta; destino do ambiente; saída 0 apenas com conferência | FR-002–FR-004 |
| V08 | Revisão fixa e equivalência | hash completo; mensagens, variável e metadata iguais | FR-001/FR-003/FR-006 |
| V09 | Snapshot do repo | identidade, descrição, tags, público e HEAD corretos | FR-003/FR-006 |
| V10 | Leitura anônima e inspeção visual | repo e mesmo commit acessíveis sem autenticação; prova disponível | FR-003/FR-006 |
| V11 | Registro e falha parcial | dois hashes, revisão/URLs/data e estados separados no registro | FR-004/FR-006/FR-007 |
| V12 | Entrega à 005 e revisão final | nova edição exige novo ciclo; hashes/protegidos preservados | FR-007/R12/R13 |

## V01 — Conferir a baseline preservada

```bash
python - <<'PY'
from pathlib import Path
import hashlib
import json
root = Path.cwd()
manifest = json.loads((root / 'docs/integridade-inicial.json').read_text())
for name, info in manifest['files'].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == info['sha256'], name
assert hashlib.sha256((root / 'prompts/bug_to_user_story_v1.yml').read_bytes()).hexdigest() == (
    '2cddcf8f8183b4d29a5bca4d4efca17601962aa98ac75323f7dabbfa905c0d70'
)
rows = [json.loads(line) for line in (root / 'datasets/bug_to_user_story.jsonl').read_text().splitlines() if line.strip()]
assert len(rows) == 15
print('Integridade OK: quatro protegidos, v1 e 15 exemplos; hash do JSONL preserva referências e distribuição 5/7/3.')
PY
git diff --exit-code -- src/evaluate.py src/metrics.py src/utils.py datasets/bug_to_user_story.jsonl prompts/bug_to_user_story_v1.yml
```

O hash do dataset idêntico ao manifesto preserva todo o conteúdo e a distribuição.
Não repetir pull nem regravar v1 para passar no check.

## V02–V06 — Testes locais e negativos

Após implementar, executar:

```bash
python -m pytest tests/test_prompts.py --collect-only -q
python -m pytest tests/test_prompts.py::TestPrompts -v
python -m pytest tests/test_prompts.py -v
python -m pytest tests/test_pull_prompts.py tests/test_preparation_checks.py -q
```

Esperado: coleta inclui os seis métodos obrigatórios documentados no README;
todos passam, sem skip/xfail. A suíte ampliada verifica C01–C09: arquivo ausente/
ilegível/inválido, raiz/campos/técnicas/pendências, helper incoerente, templates,
configuração, serviço, conferência, acesso anônimo, corridas e sigilo. Casos
anteriores ao push verificam nenhuma escrita; casos posteriores verificam estado
parcial honesto. A quantidade de testes deve ser registrada somente após execução.

Dublês e arquivos temporários são exclusivos dos negativos; não editar o YAML
versionado ou o `.env` para simular erro. Testes bloqueiam rede, LLM e dotenv
real, com ambiente isolado. Verificar dados de entrada intactos. A sentinela
secreta sintética não pode aparecer em stdout/stderr ou no resumo. Regressão
comprova que o isolamento de imports dos novos casos não afeta pull/preparação.

## Configuração antes de V07

Conferir presença e consistência sem revelar valores:

```bash
python - <<'PY'
import os
from dotenv import load_dotenv
from langsmith.utils import get_env_var, tracing_is_enabled
load_dotenv('.env', override=False)
get_env_var.cache_clear()
required = ['LANGSMITH_API_KEY', 'LANGSMITH_PROJECT', 'USERNAME_LANGSMITH_HUB',
            'LANGSMITH_TRACING', 'LLM_PROVIDER', 'LLM_MODEL', 'EVAL_MODEL']
provider = os.getenv('LLM_PROVIDER', '').strip().lower()
assert provider in {'openai', 'google'}, 'Provider inválido'
required.append('OPENAI_API_KEY' if provider == 'openai' else 'GOOGLE_API_KEY')
missing = [name for name in required if not os.getenv(name, '').strip()]
print('Variáveis ausentes:', missing)
assert not missing, 'Resolver configuração antes do push'
assert os.environ['USERNAME_LANGSMITH_HUB'] == 'fabiocsm', 'Handle desta entrega divergente'
assert os.environ['LANGSMITH_TRACING'].strip().lower() == 'true'
assert tracing_is_enabled() is True, 'Tracing efetivo desabilitado'
print('Configuração presente; contexto autenticado será conferido antes da escrita.')
PY
```

O check específico do handle neste roteiro comprova a configuração da entrega;
o script usa valor configurado e comparação com identidade autenticada, sem
hardcode. Não executar a dupla de chamadas mínimas da 001 para validar o push.
O roteiro de [contexto da preparação](../../docs/preparacao.md#roteiro-executavel)
permite revalidar acesso, projeto e traces existentes sem novas chamadas LLM.
Não usar o modo de novas chamadas nesta feature.

Se usar CLI, consultar primeiro `langsmith --help` e `langsmith prompt --help`.
Autenticação/workspace devem ser passados conforme a ajuda instalada: não presumir
dotenv automático nem colar credencial em argumento visível. CLI é apoio; não
substitui a execução do script obrigatório.

## V07–V10 — Publicação, revisão fixa e acesso público

Somente após os checks locais e a implementação:

```bash
python src/push_prompts.py
```

Esperado: código zero, destino `fabiocsm/bug_to_user_story_v2`, publicação
confirmada e revisão conferida automaticamente por C07.1–C07.4. O script fornece
os hashes locais, commit completo, URL retornada e URLs públicas efetivamente
lidas, com resultados separados.
Conferir a saída conforme C06–C08, sem tratar URL do workspace como prova pública.
O retorno zero encerra o CLI sem aguardar inspeção visual; enquanto C07.5 e seu
registro estiverem pendentes, o aceite da 004 e a entrega à 005 continuam bloqueados.

O script deve executar a sequência do contrato: prefixo do retorno → hash completo
sem cache → pull fixado → igualdade das mensagens/entrada/metadata → snapshot do
repo → GET anônimo do repo e mesmo commit. Publicidade exige JSON coerente,
manifesto equivalente e requests sem auth/cookies; HTML 200 ou flag enviada não
bastam. O SDK não deve instanciar modelos durante essa sequência.

Abrir a revisão no dashboard e conferir descrição, tags/técnicas, mensagens e
visibilidade. Abrir o endereço público em sessão sem autenticação e registrar
prova visual. Guardar evidência em `docs/evidencias/` ou URL pública estável; não
conservar a única cópia em `screenshots/` ou `results/`. Esta prova visual
complementa a leitura anônima de conteúdo feita pelo script e atende a C07.5,
etapa posterior ao sucesso automatizado, obrigatória para o aceite da 004.
Registrar seu resultado separadamente do código de saída já obtido no CLI.

Se publicação falhar, o código deve ser não zero e indicar a etapa. Se já houver
escrita mas a conferência falhar, registrar esse estado e investigar por leitura
da revisão identificada. Não executar avaliação ou republicar automaticamente
para encobrir timeout, divergência, falta de permissão ou acesso público pendente.

## V11 — Registrar a comprovação sem fabricar resultados

Criar/atualizar `docs/publicacao-v2.md` durante a implementação, com uma entrada
datada por tentativa seguindo a entidade 5 do modelo. Incluir hashes, revisão
completa, URLs, snapshot do repo e resultados separados de publicação, equivalência,
acesso público e inspeção visual. Preservar falhas e tentativas anteriores.

Atualizar no README a seção `Como Executar` com o comando e interpretação de
estados, e linkar o registro. Atualizar V15 no registro da 001 somente após prova
real de escrita pública. Não preencher `Resultados Finais` com notas ainda não
obtidas; `share_dataset` e experimentos não são executados nesta feature.

## V12 — Encerrar a 004 e entregar à 005

- Repetir V01, conferir diff, ausência de segredos e acessibilidade das provas.
- Demonstrar em teste temporário que mudança local invalida a associação anterior,
  e que HEAD concorrente não é confundido com a revisão do próprio push.
- Registrar que nova edição exige teste → push → conferência antes de avaliar.
- Entregar hashes, commit/URLs e estado à 005. Ela deve conferir HEAD e snapshot
  novamente antes/depois do experimento e manter a revisão estável durante a execução.
- Confirmar que nenhum arquivo protegido ou provider foi modificado. Um registro
  antigo prova histórico, sem garantir estado remoto futuro.

```bash
git diff --check
git status --short --branch
```

Aceite: V01–V12 comprovados e FR-001–FR-007/SC-001–SC-004 atendidos. Código/testes
concluídos com serviço externo impedido devem permanecer como implementação
concluída e prova remota pendente. Publicação aprovada não significa aprovação
acadêmica: cinco métricas e média `>= 0.8`, 15 respostas/75 feedbacks e evidências
finais continuam nas specs 005/006.

## Compatibilidade observada na execução da 004

O serviço acrescenta a tag técnica `ChatPromptTemplate`: a conferência aceita
somente essa tag extra conhecida e conserva todas as autorais. Reenvio idêntico
pode gerar `LangSmithConflictError`; nesse caso o script não repete push e confere
uma revisão existente por hash completo/manifesto e todos os gates. O resumo tem
`returned_url: null` e procedência `existing_after_conflict`, sem atribuir o HEAD
a uma nova escrita própria. O caminho normal continua resolvendo a URL retornada.
Consulte o histórico de tentativas em `docs/publicacao-v2.md` e os complementos
C05–C08 no contrato. Uma divergência continua retornando 1.
