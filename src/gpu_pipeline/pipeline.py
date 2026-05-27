from pathlib import Path

from gpu_pipeline.analysis import (
    correlacoes_com_preco,
    estatisticas_gerais,
    media_mensal_mercado,
    resumir_por_gpu,
)
from gpu_pipeline.config import ConfiguracaoPipeline
from gpu_pipeline.ingestion import carregar_historico_precos, carregar_metadados
from gpu_pipeline.transform import juntar_dados
from gpu_pipeline.visualization import salvar_graficos


def executar_pipeline(configuracao: ConfiguracaoPipeline) -> dict[str, Path]:
    configuracao.diretorio_processado.mkdir(parents=True, exist_ok=True)
    configuracao.diretorio_figuras.mkdir(parents=True, exist_ok=True)

    metadados = carregar_metadados(configuracao.caminho_metadados)
    historico_precos = carregar_historico_precos(configuracao.caminho_precos)
    dados = juntar_dados(historico_precos, metadados)
    resumo = resumir_por_gpu(dados)
    media_mensal = media_mensal_mercado(dados)
    estatisticas = estatisticas_gerais(dados)
    correlacoes = correlacoes_com_preco(dados)

    caminho_dados = configuracao.diretorio_processado / "gpu_price_enriched.csv"
    caminho_resumo = configuracao.diretorio_processado / "gpu_summary.csv"
    caminho_media = configuracao.diretorio_processado / "monthly_market_average.csv"
    caminho_estatisticas = configuracao.diretorio_processado / "basic_statistics.csv"
    caminho_correlacoes = configuracao.diretorio_processado / "price_correlations.csv"

    dados.to_csv(caminho_dados, index=False)
    resumo.to_csv(caminho_resumo, index=False)
    media_mensal.to_csv(caminho_media, index=False)
    estatisticas.to_csv(caminho_estatisticas, index=False)
    correlacoes.to_csv(caminho_correlacoes, index=False)
    salvar_graficos(
        dados,
        resumo,
        configuracao.diretorio_figuras,
        configuracao.top_n_grafico,
    )

    return {
        "dados_tratados": caminho_dados,
        "resumo": caminho_resumo,
        "media_mensal": caminho_media,
        "estatisticas": caminho_estatisticas,
        "correlacoes": caminho_correlacoes,
        "grafico_tendencia": configuracao.diretorio_figuras / "used_price_trend.png",
        "grafico_dispersao": configuracao.diretorio_figuras / "performance_value_scatter.png",
    }
