# Pipeline de dados para experimento Docker vs ReproZip

Este repositório implementa o experimento-modelo descrito no PDF: uma pipeline Python reprodutível com extração de CSV, transformação, análise estatística básica e geração de artefatos.

## Dados

O dataset veio do Kaggle em dois arquivos:

- `gpu_metadata.csv`: características técnicas por GPU (`Name`, `Wattage`, `VRAM`, `3DMARK`).
- `gpu_price_history.csv`: série temporal mensal de preços por GPU (`Date`, `Name`, `Retail Price`, `Used Price`).

A pipeline usa os dois arquivos. O histórico de preços é limpo e enriquecido com os metadados por meio da chave `Name`.

## O que a pipeline faz

A pipeline transforma os dois CSVs originais em resultados prontos para análise. Primeiro, ela lê os arquivos de metadados e de histórico de preços. Depois, limpa os dados, converte datas e valores numéricos, remove registros sem preço usado e junta os dois arquivos pela coluna `Name`.

Com os dados unidos, a pipeline calcula indicadores de custo-benefício, como preço usado por ponto no 3DMARK, preço por GB de VRAM e relação entre preço de varejo e preço usado. Em seguida, gera um resumo por GPU, uma média mensal do mercado, estatísticas descritivas e correlações com o preço usado.

Por fim, a pipeline gera gráficos em PNG para visualizar a evolução dos preços e a relação entre desempenho e preço.

## Arquitetura

```text
main.py             # arquivo principal para executar a pipeline
src/gpu_pipeline/
  config.py         # caminhos e parametros
  ingestion.py      # leitura dos CSVs
  transform.py      # limpeza, normalizacao e juncao dos dados
  analysis.py       # estatisticas e agregacoes analiticas
  visualization.py  # graficos PNG
  pipeline.py       # orquestracao do fluxo
```

## Execução local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```


## Saídas geradas

Por padrão, os resultados são escritos em `artifacts/`:

- `processed/gpu_price_enriched.csv`: dataset limpo e enriquecido.
- `processed/gpu_summary.csv`: métricas agregadas por GPU.
- `processed/monthly_market_average.csv`: média mensal de preços do mercado.
- `processed/basic_statistics.csv`: estatísticas descritivas das principais variáveis.
- `processed/price_correlations.csv`: correlações das variáveis com o preço usado.
- `figures/used_price_trend.png`: evolução do preço usado médio.
- `figures/performance_value_scatter.png`: relação entre performance, VRAM, consumo e preço.

## Docker

```bash
docker build -t gpu-pipeline .
docker run --rm -v "$(pwd)/artifacts:/app/artifacts" gpu-pipeline
```

## ReproZip

Exemplo de rastreamento para comparação com Docker:

```bash
reprozip trace python main.py
reprozip pack gpu-pipeline.rpz
```

Depois disso, o pacote `.rpz` pode ser desempacotado com `reprounzip` para medir tamanho, overhead e capacidade de reprodução.
