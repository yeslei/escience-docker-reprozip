# Docker vs ReproZip em uma pipeline de eScience

## Resumo

Este projeto apresenta uma analise experimental comparativa entre Docker e ReproZip no contexto da reproducibilidade computacional em eScience. O experimento consistiu na implementacao de uma pipeline de dados em Python, seguida da sua execucao em tres contextos: execucao nativa no WSL, execucao em container Docker e execucao reproduzida com ReproZip.

O objetivo foi avaliar nao apenas o tempo de execucao, mas tambem o esforco de empacotamento, o tamanho dos artefatos gerados, as intervencoes manuais necessarias e a fidelidade dos resultados produzidos. Dessa forma, a comparacao buscou observar tanto aspectos de desempenho quanto aspectos praticos de preservacao e reproducibilidade do ambiente computacional.

## Objetivo

O objetivo geral deste experimento foi comparar Docker e ReproZip como estrategias para preservar e reproduzir uma pipeline de dados. O Docker foi avaliado como uma abordagem declarativa, baseada na escrita manual de um `Dockerfile`. O ReproZip foi avaliado como uma abordagem baseada em rastreamento dinamico, na qual a execucao real do experimento e monitorada para capturar os arquivos e dependencias efetivamente utilizados.

As perguntas que orientaram a analise foram:

- qual abordagem exigiu maior esforco de preparacao;
- qual abordagem gerou o menor artefato;
- qual foi o custo de empacotamento de cada ferramenta;
- qual foi o tempo de execucao observado em cada ambiente;
- quais intervencoes manuais foram necessarias;
- se os artefatos gerados conseguiram reproduzir a pipeline com sucesso.

## Pipeline experimental

A pipeline desenvolvida utiliza dois conjuntos de dados em CSV sobre historico de precos de GPUs:

- `gpu_metadata.csv`, contendo caracteristicas tecnicas de GPUs, como `Name`, `Wattage`, `VRAM` e `3DMARK`;
- `gpu_price_history.csv`, contendo uma serie temporal mensal de precos por GPU, com `Date`, `Name`, `Retail Price` e `Used Price`.

O fluxo da pipeline foi composto por quatro etapas principais:

1. leitura dos arquivos CSV;
2. limpeza, normalizacao e juncao dos dados pela coluna `Name`;
3. calculo de estatisticas, correlacoes e indicadores de custo-beneficio;
4. geracao de arquivos CSV processados e graficos em PNG.

A estrutura principal do projeto ficou organizada da seguinte forma:

```text
main.py             # ponto de entrada da pipeline
compare_metrics.py  # consolidacao das metricas coletadas
Dockerfile          # definicao do ambiente Docker
src/gpu_pipeline/
  config.py         # configuracoes e caminhos
  ingestion.py      # leitura dos dados
  transform.py      # limpeza e transformacao
  analysis.py       # calculos estatisticos
  visualization.py  # geracao de graficos
  pipeline.py       # orquestracao do fluxo
  metrics.py        # registro e resumo das metricas
```

## Metodologia

O experimento foi conduzido comparando tres formas de executar a mesma pipeline:

| Contexto | Descricao |
| --- | --- |
| Nativo | Execucao direta no WSL com ambiente virtual Python |
| Docker | Execucao da pipeline dentro de uma imagem Docker construida a partir do `Dockerfile` |
| ReproZip | Execucao rastreada com `reprozip trace`, empacotada em `.rpz` e reproduzida com `reprounzip docker run` |

Para medir o tempo interno da pipeline, o arquivo `main.py` foi instrumentado com `perf_counter()`. Cada execucao registra automaticamente uma linha em `artifacts/metrics/pipeline_runs.csv`, contendo o contexto, o tempo em segundos, a versao do Python e o sistema operacional observado.

Tambem foram medidos tempos externos dos comandos completos, isto e, o tempo percebido ao chamar o processo pelo terminal. Essa segunda medicao inclui custos que nao aparecem no tempo interno, como inicializacao do container ou sobrecusto do `reprounzip`.

As repeticoes adotadas foram:

| Medicao | Repeticoes |
| --- | ---: |
| Execucao nativa | 10 |
| Execucao Docker | 10 |
| Execucao ReproZip | 10 |
| Build Docker | 3 |
| Pack ReproZip | 3 |
| Trace ReproZip | 1 |
| Setup ReproZip via Docker | 1 |

As metricas resumidas foram media, mediana, desvio padrao, menor tempo, maior tempo e overhead percentual em relacao ao baseline nativo.

## Ambiente de teste

Os testes foram executados em 16 de junho de 2026, em WSL2/Ubuntu sobre Windows 11. O Docker utilizado foi Docker Desktop 28.4.0.

Um aspecto importante do ambiente foi que a execucao nativa no WSL acessou o projeto pelo caminho `/mnt/c/Users/yeslei/Desktop/escience-docker-reprozip`. Esse detalhe influencia os resultados de desempenho, pois o acesso ao filesystem do Windows via `/mnt/c` costuma ser mais lento do que o filesystem Linux interno do WSL ou o filesystem interno dos containers.

Por esse motivo, os tempos devem ser interpretados como resultados do ambiente observado, e nao como uma conclusao universal de que uma ferramenta e sempre mais rapida do que outra.

## Resultados gerados

Durante o experimento, foram gerados arquivos de dados, graficos e metricas em `artifacts/`:

```text
artifacts/
  processed/              # CSVs finais da pipeline
  figures/                # graficos PNG
  metrics/                # CSVs e JSONs com metricas experimentais
```

Os principais arquivos de metricas foram:

| Arquivo | Conteudo |
| --- | --- |
| `artifacts/metrics/pipeline_runs.csv` | Tempos internos de execucao da pipeline |
| `artifacts/metrics/comparison_summary.csv` | Resumo estatistico dos tempos internos |
| `artifacts/metrics/external_run_metrics.csv` | Tempos externos dos comandos completos |
| `artifacts/metrics/external_run_summary.csv` | Resumo estatistico dos tempos externos |
| `artifacts/metrics/packaging_metrics.csv` | Tempos de build, trace, pack e setup |
| `artifacts/metrics/packaging_summary.csv` | Resumo das metricas de empacotamento |
| `artifacts/metrics/artifact_sizes.csv` | Tamanho da imagem Docker e do pacote ReproZip |
| `artifacts/metrics/output_hashes.csv` | Hashes SHA-256 dos artefatos finais |

## Resultados de execucao

A primeira analise considerou o tempo interno da pipeline, ou seja, o tempo medido dentro do proprio script Python apos o processo ja estar em execucao.

| Metrica | Nativo | Docker | ReproZip |
| --- | ---: | ---: | ---: |
| Numero de execucoes | 10 | 10 | 10 |
| Media de execucao | 2.184550 s | 0.431649 s | 0.356324 s |
| Mediana de execucao | 2.136380 s | 0.396230 s | 0.349363 s |
| Desvio padrao | 0.216556 s | 0.086732 s | 0.020986 s |
| Menor tempo | 1.916267 s | 0.352501 s | 0.337091 s |
| Maior tempo | 2.579507 s | 0.635541 s | 0.403735 s |
| Overhead vs nativo | 0% | -80.24% | -83.69% |

Docker e ReproZip apresentaram tempos internos menores do que a execucao nativa. Entretanto, esse resultado foi influenciado pelo fato de a execucao nativa ter sido feita no WSL acessando arquivos em `/mnt/c`. Assim, o overhead negativo nao foi interpretado como superioridade geral de desempenho das ferramentas, mas como um efeito do ambiente especifico usado no teste.

Tambem foi calculado o tempo externo dos comandos completos:

| Contexto | Execucoes | Media | Mediana | Desvio padrao | Minimo | Maximo |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Nativo externo | 10 | 6.299583 s | 6.317538 s | 0.138478 s | 6.061777 s | 6.464093 s |
| Docker externo | 10 | 1.683756 s | 1.675242 s | 0.085077 s | 1.577491 s | 1.862200 s |
| ReproZip externo | 10 | 5.989189 s | 5.834730 s | 0.701595 s | 5.501319 s | 7.809983 s |

Essa segunda medicao mostrou uma diferenca importante: embora o ReproZip tenha apresentado baixo tempo interno da pipeline, o tempo externo do comando foi maior, pois cada reproducao passou pela camada `reprounzip docker run`. O Docker teve o menor tempo externo medio entre os contextos testados.

## Resultados de empacotamento

A etapa de empacotamento avaliou o custo para criar os artefatos reprodutiveis de cada ferramenta. No Docker, essa etapa corresponde ao `docker build`. No ReproZip, o processo foi separado entre rastreamento (`reprozip trace`), empacotamento (`reprozip pack`) e preparacao para reproducao (`reprounzip docker setup`).

| Operacao | Execucoes | Media | Mediana | Desvio padrao | Minimo | Maximo |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `docker build --no-cache` | 3 | 22.691876 s | 21.001921 s | 3.193074 s | 20.698939 s | 26.374769 s |
| `reprozip trace` | 1 | 113.892919 s | 113.892919 s | 0.000000 s | 113.892919 s | 113.892919 s |
| `reprozip pack` | 3 | 29.921944 s | 29.901962 s | 0.391002 s | 29.541316 s | 30.322554 s |
| `reprounzip docker setup` | 1 | 20.288977 s | 20.288977 s | 0.000000 s | 20.288977 s | 20.288977 s |

O Docker apresentou menor custo de preparacao do artefato principal. O ReproZip exigiu mais tempo, especialmente na etapa de `trace`, porque precisou monitorar a execucao real da pipeline para identificar os arquivos e dependencias efetivamente utilizados.

## Tamanho dos artefatos

Apesar do maior custo de rastreamento e empacotamento, o ReproZip gerou um artefato menor que a imagem Docker.

| Artefato | Tamanho |
| --- | ---: |
| Imagem Docker `gpu-pipeline` | 114.19 MB |
| Pacote ReproZip `gpu-pipeline.rpz` | 49.57 MB |

Esse resultado e coerente com a proposta do ReproZip: em vez de reconstruir um ambiente completo a partir de uma imagem base, ele empacota os arquivos observados durante a execucao. Por outro lado, o Docker inclui a imagem base e as dependencias instaladas no ambiente do container.

## Reprodutibilidade observada

Ambas as abordagens conseguiram executar a pipeline e gerar os artefatos esperados. No entanto, o processo de preparacao apresentou diferencas praticas relevantes.

| Criterio | Docker | ReproZip |
| --- | --- | --- |
| Artefato gerado com sucesso | Sim | Sim |
| Execucao reproduzida com sucesso | Sim | Sim |
| Repeticoes executadas | 10 | 10 |
| Dependencia de internet na preparacao | Sim, para imagem base e pacotes `pip` | Sim, para plugin e montagem da imagem do `reprounzip` |
| Intervencoes manuais observadas | Iniciar Docker Desktop | Instalar `reprounzip-docker` e `setuptools` no WSL |
| Abordagem principal | Receita declarativa no `Dockerfile` | Captura dinamica com `reprozip trace` |

Durante a execucao do ReproZip, o `reprounzip` inicialmente nao possuia o subcomando `docker`. Foi necessario instalar o plugin `reprounzip-docker`. Tambem foi necessario instalar `setuptools`, pois a versao usada do ReproZip ainda dependia de `distutils`, modulo removido do Python 3.12.

Outro ponto observado foi que o `reprounzip docker setup` emitiu um aviso indicando o uso de Ubuntu 19.04 como imagem base em vez de Ubuntu 24.04. Esse comportamento foi registrado como uma limitacao do ambiente e da ferramenta no teste realizado.

## Fidelidade dos resultados

Os artefatos finais da pipeline foram gerados com sucesso. Para documentar a fidelidade dos resultados, foram calculados hashes SHA-256 dos arquivos finais.

| Arquivo | SHA-256 |
| --- | --- |
| `artifacts/processed/basic_statistics.csv` | `cf6d1b025142c10e06156d9a0114e0d031ae6c053b2d1a62cf89d710af07370f` |
| `artifacts/processed/gpu_price_enriched.csv` | `852003ea81ca309ee66eff292c0ce0a544c4e41e5dd913dc633fa68a01c6a850` |
| `artifacts/processed/gpu_summary.csv` | `e13a9ee3839a2a182a8e3029972672d70afc1ec401b503542920df8ee17dd5a9` |
| `artifacts/processed/monthly_market_average.csv` | `66343cee3972241551e7ba3a9c5d760599503ba35e981679fa42e974aab1805b` |
| `artifacts/processed/price_correlations.csv` | `bc7ef1c5f7a7e7ea02496ead8bac5c3fdc03447e2ca83c6871ee6069721aa526` |
| `artifacts/figures/performance_value_scatter.png` | `2fdee38069463baed9f013d91f07584991177ef46c123a17e1e8f57b16aa7cad` |
| `artifacts/figures/used_price_trend.png` | `4ef05bc67c8fd702500765c9dba7205d6237cded7ed3d0c4e36088c2bed8a962` |

Os hashes foram armazenados em `artifacts/metrics/output_hashes.csv`, permitindo verificar posteriormente se uma nova execucao produz os mesmos arquivos.

## Discussao

Os resultados indicaram uma diferenca clara entre as duas abordagens. O Docker foi mais direto para preparar e executar o ambiente, pois a pipeline dependia apenas de Python, pandas e matplotlib. A escrita do `Dockerfile` foi suficiente para reconstruir o ambiente e executar o experimento de forma repetida.

O ReproZip, por outro lado, gerou um pacote menor e registrou a execucao real da pipeline. Essa caracteristica e importante para reproducibilidade cientifica, pois reduz a necessidade de o pesquisador listar manualmente todas as dependencias usadas. Entretanto, no ambiente testado, a ferramenta exigiu mais intervencoes manuais e apresentou maior custo inicial, especialmente na etapa de rastreamento.

Assim, a comparacao mostrou um trade-off. O Docker foi mais simples e rapido para este caso controlado, enquanto o ReproZip ofereceu uma abordagem mais orientada a proveniencia, capturando o que foi efetivamente usado durante a execucao. Para pipelines maiores, com dependencias menos evidentes, essa captura automatica pode se tornar uma vantagem mais expressiva.

Tambem foi observado que a comparacao de desempenho precisa ser feita com cuidado. O baseline nativo foi afetado pelo uso de `/mnt/c` no WSL, o que tornou a execucao nativa mais lenta. Portanto, os resultados de tempo foram usados como evidencia do ambiente experimental, mas a conclusao principal do trabalho nao se baseou apenas em velocidade.

## Conclusao

Neste experimento, Docker e ReproZip conseguiram reproduzir a pipeline e gerar os artefatos esperados. O Docker apresentou menor tempo de preparacao e menor tempo externo medio de execucao. O ReproZip gerou um pacote menor, mas exigiu maior custo de rastreamento, maior tempo de preparacao e mais ajustes manuais no ambiente usado.

Com base nos resultados obtidos, o Docker se mostrou mais pratico para uma pipeline simples e bem declarada. O ReproZip, por sua vez, se mostrou relevante como ferramenta de captura automatica de proveniencia, especialmente para cenarios em que as dependencias reais do experimento nao sao totalmente conhecidas ou sao dificeis de documentar manualmente.

A conclusao geral e que as duas ferramentas contribuem para a reproducibilidade, mas seguem estrategias diferentes. O Docker favorece a padronizacao do ambiente por meio de uma receita explicita. O ReproZip favorece a preservacao da execucao observada, reduzindo a necessidade de descoberta manual de dependencias, ainda que com maior custo operacional no teste realizado.

## Como reproduzir a coleta

Os comandos abaixo resumem a coleta realizada. Eles foram mantidos apenas para possibilitar a reproducao do experimento.

Execucao nativa:

```bash
for i in {1..10}; do
  PIPELINE_CONTEXT=native python main.py
done
```

Docker:

```bash
docker build --no-cache -t gpu-pipeline .
for i in {1..10}; do
  docker run --rm -e PIPELINE_CONTEXT=docker -v "$PWD/artifacts:/app/artifacts" gpu-pipeline
done
```

ReproZip:

```bash
PIPELINE_CONTEXT=reprozip reprozip trace python main.py
reprozip pack gpu-pipeline.rpz
reprounzip docker setup gpu-pipeline.rpz reprozip-run
for i in {1..10}; do
  reprounzip docker run reprozip-run
done
```

Consolidacao:

```bash
python compare_metrics.py
```
