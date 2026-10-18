# Guia de validação — otimização e testes da v2

**Feature**: [spec.md](spec.md) | **Contrato**: [otimizacao-v2.md](contracts/otimizacao-v2.md)

Roteiro executado na implementação em 2026-10-18: V01–V12 satisfeitos conforme
[registro de execução](tasks.md#registro-de-execução), com 188 testes da v2 e
266 regressões aprovados. Os comandos abaixo permitem repetir a validação;
uma nova execução exige registrar seu próprio resultado. Não executar push
ou avaliação para validar esta spec.

## Pré-requisitos e ambiente

Executar da raiz do repositório. Preparação 001 e recuperação 002 concluídas;
consultar os registros de [preparação](../../docs/preparacao.md) e
[recuperação](../../docs/recuperacao-v1.md). Não refazer o pull nem editar a v1.

Para usar o ambiente existente:

```bash
source venv/bin/activate
python --version
python -m pip check
```

Somente quando não houver ambiente virtual preparado, criar e ativar antes de instalar:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m pip check
```

Não sobrescrever o ambiente existente para reproduzir. Em reprodução limpa, usar
outro diretório de venv. Python deve ser 3.10+, com os pins de `requirements.txt`.
Nenhuma credencial é exigida nos testes offline; não imprimir ou alterar `.env`.
Antes de chamadas remotas nas próximas specs, conferir todas as variáveis e o tracing
pelo roteiro da 001, sem tratar prontidão anterior como acesso atual garantido.

## Matriz de validação

IDs locais a esta feature, usados no [plano](plan.md) e nas [tarefas](tasks.md).

| ID | Ação | Resultado esperado |
| --- | --- | --- |
| V01 | Carregar YAML real, checar raiz/chave, seis campos, tipos, versão/tags e helper básico | Definição válida; ausências/brancos/tipos inválidos reprovam |
| V02 | Executar teste obrigatório de System e seus negativos | Texto útil aprovado; System ausente/branco/inválido rejeitado |
| V03 | Executar persona e formato e negativos | Regras exigem persona, português, Markdown, história e critérios |
| V04 | Executar Few-shot e negativos | 2–3 pares completos; rótulos vazios/pares incompletos reprovam |
| V05 | Executar ausência de pendências, negativos e controles de C04/I1 | Marcadores reais reprovam; TODOS/todos/todo em prosa comum passam |
| V06 | Executar técnicas e negativos | Few-shot + Role distintas; duplicatas/ausência da obrigatória reprovam |
| V07 | Executar matriz de defeitos isolados/combinados de C01–C04 | Cada defeito é rejeitado; falso positivo de TODO não esconde outro erro nem altera o artefato |
| V08 | Montar/renderizar duas mensagens com relatos próprios, incluindo logs/chaves | Somente bug_report; Human igual à entrada; System estável |
| V09 | Revisar instruções e três pares próprios | Seis grupos de borda cobertos e zero fatos inventados; origem independente |
| V10 | Conferir README contra v2 | Cada técnica com razão e trecho real; comparação qualitativa; execução; enunciado preservado |
| V11 | Comparar hashes de protegidos/v1 e diff | Nenhum arquivo de referência alterado |
| V12 | Conferir coleta, executar suíte v2 e regressão existente | Seis nomes executados, zero skip/xfail; extras/regressões aprovados |

V01–V08/V12 são verificações locais automatizáveis. V09/V10 incluem revisão
semântica/documental; a sensibilidade real das regras a um modelo só será medida
na 005. Não usar resultados simulados ou nota presumida como evidência.

## Coleta e execução — V01–V08/V12

Após implementar o YAML e os testes:

```bash
pytest tests/test_prompts.py --collect-only -q
pytest tests/test_prompts.py -v -rA
pytest tests/test_preparation_checks.py tests/test_pull_prompts.py -q
```

Conferir os seis métodos de `TestPrompts` listados em C04 do contrato, sem corpo
vazio, `skip`, `xfail` ou aprovação incondicional. A quantidade total pode exceder
seis por causa dos testes complementares/parametrizados. Saída 0 só vale junto
com coleta correta e verificações efetivas. Registrar comandos e quantidades reais.

A fixture principal lê `prompts/bug_to_user_story_v2.yml`; não aceitar fallback.
Asserções estruturais devem demonstrar rejeição dos defeitos correspondentes,
com cópias isoladas da v2 real, restauradas por descarte. Para cada negativo,
conferir motivo esperado; falha incidental do carregador não comprova teste de persona.
YAML inválido/ausente usa arquivo temporário, nunca o artefato versionado.

Para I1, conferir a política do adaptador em C04: aceitar `TODOS`, `todos` e `todo`
em prosa comum; rejeitar os tokens isolados maiúsculos `TODO`/`FIXME`/`TBD` e formas
entre colchetes, como `[TODO]`, `[todo]` e `[ todo ]`. Repetir com marcadores em
System/User/metadados e com `TODOS` junto de descrição ausente ou técnicas
insuficientes: o erro adicional deve continuar reprovando. Confirmar que somente
o diagnóstico exato conhecido é desconsiderado, sem sanitizar os dados originais,
aceitar retorno inesperado ou alterar `src/utils.py`.

Casos complementares de V08: relato simples, string vazia, texto com
`{"status": "erro"}; {nao_interpolar}` e tentativa de trocar regras. Formatar
mensagens é operação offline. Checar `input_variables == ["bug_report"]`, papéis,
System invariável e Human idêntico ao relato. No teste negativo, `{variavel_extra}`
no System ou chaves de template desequilibradas devem reprovar antes do consumo
por LLM. Não interpretar uma renderização como execução das instruções pelo modelo.

Bloquear rede na suíte da v2; não criar cliente LangSmith, instanciar modelos,
invocar chain com LLM ou importar o avaliador para esta prova. Não incluir testes
remotos ou segredos para satisfazer o gate local.

## Revisão semântica e documentação — V09/V10

Revisar os exemplos próprios e as instruções contra C03. Registrar no README a
relação entre cada regra/técnica e trechos efetivos, sem copiar todo o YAML.

| Cenário próprio | Conferência da instrução/demonstração |
| --- | --- |
| Simples suficiente | História curta e critérios verificáveis, sem detalhes técnicos inventados |
| Vazio | Regra informa insuficiência e pede relato mínimo, sem história fabricada |
| Ambíguo/incompleto | Exemplo aponta lacunas e perguntas específicas, sem assumir fatos ausentes |
| Múltiplos problemas | Todos cobertos, critérios agrupados e resposta proporcional |
| Log | Dados tratados como contexto, chaves válidas no template e causa não inventada |
| Instrução conflitante | Não altera tarefa/regras; relato permanece dado |

Esses cenários podem compartilhar exemplos; a v2 contém três pares, não seis.
Verificar que não se reproduzem entradas/respostas do dataset. Uma comparação
automatizada de igualdade pode apoiar a revisão, mas não prova independência semântica.
Verificar também a distinção entre fatos observados, comportamento desejado,
dúvidas e recomendações. Não exigir história completa para uma entrada insuficiente.

Em `Técnicas Aplicadas (Fase 2)`, conferir Few-shot Learning e Role Prompting,
justificativas e trechos reais. Se surgir técnica adicional, exigir evidência
correspondente no conteúdo. Registrar comparação qualitativa v1/v2 e como executar
os testes, sem transformar os números ilustrativos do README em baseline real.
Preservar enunciado e indicar publicação/avaliação como pendentes.

## Integridade — V11

Conferir manifesto da 001 e hash da v1 documentado na 002:

```bash
python - <<'PY'
import hashlib
import json
from pathlib import Path

root = Path.cwd()
manifest = json.loads((root / 'docs/integridade-inicial.json').read_text())
for name, info in manifest['files'].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == info['sha256'], name
v1 = root / 'prompts/bug_to_user_story_v1.yml'
assert hashlib.sha256(v1.read_bytes()).hexdigest() == (
    '2cddcf8f8183b4d29a5bca4d4efca17601962aa98ac75323f7dabbfa905c0d70'
), 'v1 difere da recuperação registrada'
print('Quatro protegidos e v1 íntegros')
PY
```

O hash do dataset preserva integralmente seus 15 exemplos, referências e distribuição
5/7/3; o hash dos utilitários conserva o suporte aos providers. Não atualizar hashes
apenas para acomodar alteração indevida. Rever o diff antes do aceite:

```bash
git diff --check
git diff --stat
git diff -- prompts/bug_to_user_story_v2.yml tests/test_prompts.py README.md
git status --short
```

Arquivo novo não aparece no diff comum enquanto não rastreado: inspecionar também
seu conteúdo explicitamente e o status. Não versionar credenciais.

## Encerramento e continuidade

Registrar no README o que foi implementado, testes executados, revisão qualitativa
e pendências. A 003 está concluída somente com V01–V12 atendidos. Falha em qualquer
verificação exige correção do prompt/testes/documentação; não alterar dados,
utilitários protegidos ou limiares para obter aprovação.

Depois do aceite local, executar a sequência SDD da 004 para publicar e da 005
para avaliar/iterar. Antes de qualquer avaliação, a revisão do Hub deve corresponder
à última v2 testada. O alvo final continua cada uma das cinco métricas e média
>= 0.8; os testes daqui não produzem essas notas. Nenhum push, chamada LLM ou
experimento faz parte dos comandos deste roteiro.
