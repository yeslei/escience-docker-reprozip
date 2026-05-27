from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def salvar_graficos(
    dados: pd.DataFrame,
    resumo: pd.DataFrame,
    diretorio_figuras: Path,
    top_n_grafico: int,
) -> None:
    diretorio_figuras.mkdir(parents=True, exist_ok=True)
    salvar_grafico_tendencia(dados, resumo, diretorio_figuras, top_n_grafico)
    salvar_grafico_custo_beneficio(resumo, diretorio_figuras)


def salvar_grafico_tendencia(
    dados: pd.DataFrame,
    resumo: pd.DataFrame,
    diretorio_figuras: Path,
    top_n_grafico: int,
) -> None:
    media_mensal = (
        dados.groupby("data", as_index=False)
        .agg(preco_usado_medio_usd=("preco_usado_usd", "mean"))
        .sort_values("data")
    )
    melhores_gpus = resumo.head(top_n_grafico)["Name"].tolist()

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(
        media_mensal["data"],
        media_mensal["preco_usado_medio_usd"],
        linewidth=2.4,
        label="Média do mercado",
    )

    for nome, grupo in dados[dados["Name"].isin(melhores_gpus)].groupby("Name"):
        ax.plot(grupo["data"], grupo["preco_usado_usd"], alpha=0.35, linewidth=1, label=nome)

    ax.set_title("Evolução do preço usado de GPUs")
    ax.set_xlabel("Data")
    ax.set_ylabel("Preço usado (USD)")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(diretorio_figuras / "used_price_trend.png", dpi=150)
    plt.close(fig)


def salvar_grafico_custo_beneficio(resumo: pd.DataFrame, diretorio_figuras: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    grafico = ax.scatter(
        resumo["pontuacao_3dmark"],
        resumo["preco_usado_medio_usd"],
        c=resumo["vram_gb"],
        s=resumo["consumo_w"].astype(float) * 1.4,
        alpha=0.7,
        edgecolor="black",
        linewidth=0.4,
    )

    ax.set_title("Preço médio usado vs. desempenho 3DMARK")
    ax.set_xlabel("3DMARK")
    ax.set_ylabel("Preço médio usado (USD)")
    ax.grid(alpha=0.25)
    fig.colorbar(grafico, ax=ax).set_label("VRAM (GB)")
    fig.tight_layout()
    fig.savefig(diretorio_figuras / "performance_value_scatter.png", dpi=150)
    plt.close(fig)
