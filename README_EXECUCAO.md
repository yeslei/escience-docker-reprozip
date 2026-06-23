# Guia de execucao dos experimentos

Este guia mostra como executar e comparar a pipeline em tres contextos:

- Python nativo no Ubuntu/WSL;
- Docker;
- ReproZip reproduzido com Docker.

Os comandos sao iniciados no Git Bash do Windows, mas o projeto e as ferramentas
ficam no Ubuntu/WSL.

## Local do projeto

Use uma unica copia do projeto dentro do Ubuntu. Substitua
`<CAMINHO_DO_REPOSITORIO>` pelo caminho onde o repositorio foi clonado:

```text
<CAMINHO_DO_REPOSITORIO>
```

Exemplo:

```text
/home/<usuario>/escience-docker-reprozip
```

Se o projeto estiver dentro do filesystem Linux do WSL, ele pode ser acessado
pelo Explorador de Arquivos do Windows em um caminho semelhante a:

```text
\\wsl.localhost\Ubuntu-22.04\home\<usuario>\escience-docker-reprozip
```

## Pre-requisitos

- Windows com WSL2;
- distribuicao `Ubuntu-22.04`;
- Docker Desktop aberto;
- integracao do Docker Desktop com `Ubuntu-22.04` habilitada;
- Git Bash.

No Docker Desktop, a integracao fica em **Settings > Resources > WSL
Integration**.

## 1. Preparar o Ubuntu

Abra o Git Bash e instale o suporte a ambientes virtuais:

```bash
wsl -d Ubuntu-22.04 -- sudo apt update
wsl -d Ubuntu-22.04 -- sudo apt install -y python3.10-venv python3-pip
```

Evite que o Git Bash converta caminhos Linux em caminhos Windows:

```bash
export MSYS_NO_PATHCONV=1
export PROJETO=<CAMINHO_DO_REPOSITORIO>
```

Essas duas variaveis precisam ser definidas novamente ao abrir outro Git Bash.

## 2. Criar o ambiente virtual

```bash
wsl -d Ubuntu-22.04 -- bash -lc "cd $PROJETO && python3 -m venv .venv-wsl"
```

Instale as dependencias da pipeline e do ReproZip:

```bash
wsl -d Ubuntu-22.04 -- bash -lc "cd $PROJETO && source .venv-wsl/bin/activate && python -m pip install --upgrade pip && pip install -r requirements.txt reprozip reprounzip reprounzip-docker setuptools"
```

## 3. Verificar o Docker

Com o Docker Desktop aberto, execute:

```bash
wsl -d Ubuntu-22.04 -- docker version
```

O comando deve mostrar informacoes de `Client` e `Server`.

## 4. Limpar uma coleta anterior

O comando abaixo remove somente os ambientes e arquivos de metricas gerados por
execucoes anteriores:

```bash
wsl -d Ubuntu-22.04 -- bash -lc "cd $PROJETO && rm -rf .reprozip-trace reprozip-run gpu-pipeline.rpz && rm -f artifacts/metrics/pipeline_runs.csv artifacts/metrics/latest_pipeline_run.json artifacts/metrics/comparison_summary.csv artifacts/metrics/comparison_summary.json"
```

## 5. Executar o baseline nativo

Execute a pipeline dez vezes no Ubuntu/WSL:

```bash
wsl -d Ubuntu-22.04 -- bash -lc "cd $PROJETO && source .venv-wsl/bin/activate && for i in {1..10}; do PIPELINE_CONTEXT=native python main.py; done"
```

## 6. Executar com Docker

Construa a imagem sem reutilizar o cache:

```bash
wsl -d Ubuntu-22.04 -- bash -lc "cd $PROJETO && docker build --no-cache -t gpu-pipeline ."
```

Execute o container dez vezes:

```bash
wsl -d Ubuntu-22.04 -- bash -lc "cd $PROJETO && for i in {1..10}; do docker run --rm -e PIPELINE_CONTEXT=docker -v $PROJETO/artifacts:/app/artifacts gpu-pipeline; done"
```

## 7. Empacotar com ReproZip

Rastreie uma execucao real da pipeline:

```bash
wsl -d Ubuntu-22.04 -- bash -lc "cd $PROJETO && source .venv-wsl/bin/activate && PIPELINE_CONTEXT=reprozip reprozip trace python main.py"
```

O rastreamento executa a pipeline uma vez. Remova essa medicao preparatoria para
que ela nao seja contabilizada como uma das dez repeticoes:

```bash
wsl -d Ubuntu-22.04 -- bash -lc "cd $PROJETO && sed -i '\$d' artifacts/metrics/pipeline_runs.csv"
```

Crie o pacote `.rpz`:

```bash
wsl -d Ubuntu-22.04 -- bash -lc "cd $PROJETO && source .venv-wsl/bin/activate && reprozip pack gpu-pipeline.rpz"
```

Prepare o pacote para reproducao com Docker:

```bash
wsl -d Ubuntu-22.04 -- bash -lc "cd $PROJETO && source .venv-wsl/bin/activate && reprounzip docker setup gpu-pipeline.rpz reprozip-run"
```

## 8. Reproduzir com ReproZip

Execute o pacote dez vezes:

```bash
wsl -d Ubuntu-22.04 -- bash -lc "cd $PROJETO && source .venv-wsl/bin/activate && for i in {1..10}; do reprounzip docker run reprozip-run; done"
```

Preserve as metricas nativas e Docker, baixe as metricas do ReproZip para outro
arquivo e depois combine os dois CSVs:

```bash
wsl -d Ubuntu-22.04 -- bash -lc "cd $PROJETO && source .venv-wsl/bin/activate && cp artifacts/metrics/pipeline_runs.csv artifacts/metrics/native_docker_runs.csv && rm -f artifacts/metrics/reprozip_runs.csv && reprounzip docker download reprozip-run pipeline_runs.csv:artifacts/metrics/reprozip_runs.csv && awk 'FNR==1 && NR!=1 {next} {print}' artifacts/metrics/native_docker_runs.csv artifacts/metrics/reprozip_runs.csv > artifacts/metrics/pipeline_runs.tmp && mv artifacts/metrics/pipeline_runs.tmp artifacts/metrics/pipeline_runs.csv"
```

## 9. Gerar a comparacao

```bash
wsl -d Ubuntu-22.04 -- bash -lc "cd $PROJETO && source .venv-wsl/bin/activate && python compare_metrics.py"
```

O resumo sera gravado em:

```text
artifacts/metrics/comparison_summary.csv
```

## 10. Validar a quantidade de execucoes

```bash
wsl -d Ubuntu-22.04 -- bash -lc "cd $PROJETO && cut -d, -f2 artifacts/metrics/pipeline_runs.csv | tail -n +2 | sort | uniq -c"
```

A saida esperada e:

```text
10 docker
10 native
10 reprozip
```

## 11. Medir tempos externos dos comandos

O tempo interno da pipeline e registrado automaticamente pelo `main.py` em
`artifacts/metrics/pipeline_runs.csv`. Para medir o tempo externo, isto e, o
tempo total percebido ao executar o comando completo no terminal, use um
cronometro externo ao script.

Entre no Ubuntu/WSL:

```bash
wsl -d Ubuntu-22.04
```

Depois execute:

```bash
cd "$PROJETO"
source .venv-wsl/bin/activate

# Preserve as 10 execucoes internas ja coletadas, pois os comandos externos
# tambem executam a pipeline e podem adicionar novas linhas a pipeline_runs.csv.
cp artifacts/metrics/pipeline_runs.csv artifacts/metrics/pipeline_runs.internal.csv

printf 'contexto,repeticao,duracao_segundos\n' > artifacts/metrics/external_run_metrics.csv

for i in {1..10}; do
  inicio=$(date +%s.%N)
  PIPELINE_CONTEXT=native python main.py > /dev/null
  fim=$(date +%s.%N)
  awk -v c="native_external" -v r="$i" -v i="$inicio" -v f="$fim" \
    'BEGIN { printf "%s,%d,%.6f\n", c, r, f-i }' >> artifacts/metrics/external_run_metrics.csv
done

for i in {1..10}; do
  inicio=$(date +%s.%N)
  docker run --rm -e PIPELINE_CONTEXT=docker -v "$PWD/artifacts:/app/artifacts" gpu-pipeline > /dev/null
  fim=$(date +%s.%N)
  awk -v c="docker_external" -v r="$i" -v i="$inicio" -v f="$fim" \
    'BEGIN { printf "%s,%d,%.6f\n", c, r, f-i }' >> artifacts/metrics/external_run_metrics.csv
done

for i in {1..10}; do
  inicio=$(date +%s.%N)
  reprounzip docker run reprozip-run > /dev/null
  fim=$(date +%s.%N)
  awk -v c="reprozip_external" -v r="$i" -v i="$inicio" -v f="$fim" \
    'BEGIN { printf "%s,%d,%.6f\n", c, r, f-i }' >> artifacts/metrics/external_run_metrics.csv
done

# Restaure a coleta interna original, mantendo os tempos externos em arquivo separado.
cp artifacts/metrics/pipeline_runs.internal.csv artifacts/metrics/pipeline_runs.csv
```

Gere o resumo estatistico dos tempos externos:

```bash
python - <<'PY'
import csv
import statistics
from collections import defaultdict
from pathlib import Path

entrada = Path("artifacts/metrics/external_run_metrics.csv")
saida = Path("artifacts/metrics/external_run_summary.csv")

duracoes = defaultdict(list)
with entrada.open(newline="", encoding="utf-8") as arquivo:
    for linha in csv.DictReader(arquivo):
        duracoes[linha["contexto"]].append(float(linha["duracao_segundos"]))

campos = [
    "contexto",
    "execucoes",
    "media_segundos",
    "mediana_segundos",
    "desvio_padrao_segundos",
    "minimo_segundos",
    "maximo_segundos",
]

with saida.open("w", newline="", encoding="utf-8") as arquivo:
    escritor = csv.DictWriter(arquivo, fieldnames=campos)
    escritor.writeheader()
    for contexto, valores in sorted(duracoes.items()):
        escritor.writerow({
            "contexto": contexto,
            "execucoes": len(valores),
            "media_segundos": round(sum(valores) / len(valores), 6),
            "mediana_segundos": round(statistics.median(valores), 6),
            "desvio_padrao_segundos": round(statistics.stdev(valores), 6) if len(valores) > 1 else 0.0,
            "minimo_segundos": round(min(valores), 6),
            "maximo_segundos": round(max(valores), 6),
        })
PY
```

## 12. Medir tempo de empacotamento

Para registrar o custo de preparacao dos artefatos reprodutiveis, cronometre as
etapas de build, trace, pack e setup. Esses tempos nao medem a pipeline em si,
mas sim a preparacao dos ambientes/artefatos.

```bash
printf 'ferramenta,operacao,repeticao,duracao_segundos\n' > artifacts/metrics/packaging_metrics.csv

medir() {
  ferramenta="$1"
  operacao="$2"
  repeticao="$3"
  shift 3
  inicio=$(date +%s.%N)
  "$@"
  fim=$(date +%s.%N)
  awk -v f="$ferramenta" -v o="$operacao" -v r="$repeticao" -v i="$inicio" -v e="$fim" \
    'BEGIN { printf "%s,%s,%d,%.6f\n", f, o, r, e-i }' >> artifacts/metrics/packaging_metrics.csv
}

for i in {1..3}; do
  medir docker build "$i" docker build --no-cache -t gpu-pipeline .
done

rm -rf .reprozip-trace
medir reprozip trace 1 reprozip trace python main.py
sed -i '$d' artifacts/metrics/pipeline_runs.csv

for i in {1..3}; do
  rm -f gpu-pipeline.rpz
  medir reprozip pack "$i" reprozip pack gpu-pipeline.rpz
done

rm -rf reprozip-run
medir reprozip reprounzip-docker-setup 1 reprounzip docker setup gpu-pipeline.rpz reprozip-run
```

Gere o resumo estatistico:

```bash
python - <<'PY'
import csv
import statistics
from collections import defaultdict
from pathlib import Path

entrada = Path("artifacts/metrics/packaging_metrics.csv")
saida = Path("artifacts/metrics/packaging_summary.csv")

duracoes = defaultdict(list)
with entrada.open(newline="", encoding="utf-8") as arquivo:
    for linha in csv.DictReader(arquivo):
        chave = f'{linha["ferramenta"]}:{linha["operacao"]}'
        duracoes[chave].append(float(linha["duracao_segundos"]))

campos = [
    "chave",
    "execucoes",
    "media_segundos",
    "mediana_segundos",
    "desvio_padrao_segundos",
    "minimo_segundos",
    "maximo_segundos",
]

with saida.open("w", newline="", encoding="utf-8") as arquivo:
    escritor = csv.DictWriter(arquivo, fieldnames=campos)
    escritor.writeheader()
    for chave, valores in sorted(duracoes.items()):
        escritor.writerow({
            "chave": chave,
            "execucoes": len(valores),
            "media_segundos": round(sum(valores) / len(valores), 6),
            "mediana_segundos": round(statistics.median(valores), 6),
            "desvio_padrao_segundos": round(statistics.stdev(valores), 6) if len(valores) > 1 else 0.0,
            "minimo_segundos": round(min(valores), 6),
            "maximo_segundos": round(max(valores), 6),
        })
PY
```

## 13. Medir tamanho dos artefatos

Registre o tamanho da imagem Docker e do pacote ReproZip:

```bash
python - <<'PY'
import csv
import json
import subprocess
from pathlib import Path

linhas = []

tamanho_docker = int(subprocess.check_output([
    "docker",
    "image",
    "inspect",
    "gpu-pipeline",
    "--format",
    "{{.Size}}",
], text=True).strip())

linhas.append({
    "artefato": "docker_image_gpu-pipeline",
    "bytes": tamanho_docker,
    "mb": round(tamanho_docker / 1024 / 1024, 2),
})

pacote = Path("gpu-pipeline.rpz")
tamanho_reprozip = pacote.stat().st_size
linhas.append({
    "artefato": "reprozip_package_gpu-pipeline.rpz",
    "bytes": tamanho_reprozip,
    "mb": round(tamanho_reprozip / 1024 / 1024, 2),
})

saida_csv = Path("artifacts/metrics/artifact_sizes.csv")
saida_json = Path("artifacts/metrics/artifact_sizes.json")

with saida_csv.open("w", newline="", encoding="utf-8") as arquivo:
    escritor = csv.DictWriter(arquivo, fieldnames=["artefato", "bytes", "mb"])
    escritor.writeheader()
    escritor.writerows(linhas)

saida_json.write_text(json.dumps(linhas, indent=2, ensure_ascii=False), encoding="utf-8")
PY
```

## 14. Gerar hashes dos artefatos finais

Os hashes SHA-256 permitem verificar se uma nova execucao gerou arquivos finais
identicos aos artefatos registrados.

```bash
python - <<'PY'
import csv
import hashlib
import json
from pathlib import Path

arquivos = [
    Path("artifacts/processed/basic_statistics.csv"),
    Path("artifacts/processed/gpu_price_enriched.csv"),
    Path("artifacts/processed/gpu_summary.csv"),
    Path("artifacts/processed/monthly_market_average.csv"),
    Path("artifacts/processed/price_correlations.csv"),
    Path("artifacts/figures/performance_value_scatter.png"),
    Path("artifacts/figures/used_price_trend.png"),
]

linhas = []
for caminho in arquivos:
    conteudo = caminho.read_bytes()
    linhas.append({
        "arquivo": str(caminho),
        "sha256": hashlib.sha256(conteudo).hexdigest(),
        "bytes": len(conteudo),
    })

saida_csv = Path("artifacts/metrics/output_hashes.csv")
saida_json = Path("artifacts/metrics/output_hashes.json")

with saida_csv.open("w", newline="", encoding="utf-8") as arquivo:
    escritor = csv.DictWriter(arquivo, fieldnames=["arquivo", "sha256", "bytes"])
    escritor.writeheader()
    escritor.writerows(linhas)

saida_json.write_text(json.dumps(linhas, indent=2, ensure_ascii=False), encoding="utf-8")
PY
```

## Observacao sobre desempenho

Manter o projeto dentro do filesystem Linux do WSL, por exemplo em
`/home/<usuario>/...`, tende a produzir tempos diferentes de uma execucao feita
em `/mnt/c`, que acessa arquivos do Windows. Use os novos resultados para
comparar as tres abordagens entre si no mesmo computador e sob as mesmas
condicoes.
