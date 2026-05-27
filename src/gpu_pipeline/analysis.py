import pandas as pd


COLUNAS_ESTATISTICAS = [
    "preco_usado_usd",
    "preco_varejo_usd",
    "consumo_w",
    "vram_gb",
    "pontuacao_3dmark",
    "preco_por_ponto_3dmark",
]


def resumir_por_gpu(dados: pd.DataFrame) -> pd.DataFrame:
    resumo = (
        dados.groupby("Name", as_index=False)
        .agg(
            observacoes=("preco_usado_usd", "size"),
            primeira_data=("data", "min"),
            ultima_data=("data", "max"),
            preco_usado_medio_usd=("preco_usado_usd", "mean"),
            preco_usado_minimo_usd=("preco_usado_usd", "min"),
            preco_usado_maximo_usd=("preco_usado_usd", "max"),
            preco_varejo_medio_usd=("preco_varejo_usd", "mean"),
            consumo_w=("consumo_w", "first"),
            vram_gb=("vram_gb", "first"),
            pontuacao_3dmark=("pontuacao_3dmark", "first"),
            preco_por_ponto_3dmark=("preco_por_ponto_3dmark", "mean"),
        )
        .sort_values("preco_por_ponto_3dmark")
        .reset_index(drop=True)
    )
    resumo["ranking_custo_beneficio"] = resumo.index + 1
    return resumo


def media_mensal_mercado(dados: pd.DataFrame) -> pd.DataFrame:
    return (
        dados.groupby("data", as_index=False)
        .agg(
            preco_usado_medio_usd=("preco_usado_usd", "mean"),
            preco_varejo_medio_usd=("preco_varejo_usd", "mean"),
            quantidade_gpus=("Name", "nunique"),
        )
        .sort_values("data")
    )


def estatisticas_gerais(dados: pd.DataFrame) -> pd.DataFrame:
    dados_numericos = dados[COLUNAS_ESTATISTICAS].apply(pd.to_numeric, errors="coerce")
    estatisticas = dados_numericos.describe().T
    estatisticas = estatisticas.reset_index().rename(columns={"index": "variavel"})
    return estatisticas


def correlacoes_com_preco(dados: pd.DataFrame) -> pd.DataFrame:
    dados_numericos = dados[COLUNAS_ESTATISTICAS].apply(pd.to_numeric, errors="coerce")
    correlacoes = (
        dados_numericos.corr()["preco_usado_usd"]
        .drop("preco_usado_usd")
        .reset_index()
    )
    correlacoes.columns = ["variavel", "correlacao_com_preco_usado"]
    return correlacoes.sort_values("correlacao_com_preco_usado", ascending=False)
