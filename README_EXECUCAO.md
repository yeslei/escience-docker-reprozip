# Guia de execucao dos experimentos

Este guia mostra como executar e comparar a pipeline em tres contextos:

- Python nativo no Ubuntu/WSL;
- Docker;
- ReproZip reproduzido com Docker.

Os comandos sao iniciados no Git Bash do Windows, mas o projeto e as ferramentas
ficam no Ubuntu/WSL.

## Local do projeto

Use uma unica copia do projeto dentro do Ubuntu:

```text
/home/danil/escience-trabfinal/escience-docker-reprozip
```

Ela pode ser acessada pelo Explorador de Arquivos do Windows em:

```text
\\wsl.localhost\Ubuntu-22.04\home\danil\escience-trabfinal\escience-docker-reprozip
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
export PROJETO=/home/danil/escience-trabfinal/escience-docker-reprozip
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

## Observacao sobre desempenho

Manter o projeto em `/home/danil` utiliza o filesystem Linux do WSL. Os tempos
podem ser diferentes dos resultados do README principal, que foram coletados com
o projeto armazenado em `/mnt/c`. Use os novos resultados para comparar as tres
abordagens entre si no mesmo computador e sob as mesmas condicoes.
