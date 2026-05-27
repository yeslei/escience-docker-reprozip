import pandas as pd


def _remover_sufixo_numerico(coluna: pd.Series, sufixo: str) -> pd.Series:
    return (
        coluna.astype(str)
        .str.replace(sufixo, "", regex=False)
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA})
        .astype("Float64")
    )


def limpar_metadados(metadados: pd.DataFrame) -> pd.DataFrame:
    dados = metadados.copy()
    dados.columns = dados.columns.str.strip()
    dados["Name"] = dados["Name"].str.strip()
    dados["consumo_w"] = _remover_sufixo_numerico(dados["Wattage"], "W")
    dados["vram_gb"] = _remover_sufixo_numerico(dados["VRAM"], "GB")
    dados["pontuacao_3dmark"] = pd.to_numeric(dados["3DMARK"], errors="coerce")
    return dados[["Name", "consumo_w", "vram_gb", "pontuacao_3dmark"]]


def limpar_historico_precos(historico_precos: pd.DataFrame) -> pd.DataFrame:
    dados = historico_precos.copy()
    dados.columns = dados.columns.str.strip()
    dados["Name"] = dados["Name"].str.strip()
    dados["data"] = pd.to_datetime(dados["Date"], format="%d-%m-%y", errors="coerce")
    dados["preco_varejo_usd"] = pd.to_numeric(dados["Retail Price"], errors="coerce")
    dados["preco_usado_usd"] = pd.to_numeric(dados["Used Price"], errors="coerce")
    dados[["preco_varejo_usd", "preco_usado_usd"]] = dados[
        ["preco_varejo_usd", "preco_usado_usd"]
    ].replace(0, pd.NA)
    dados = dados.dropna(subset=["data", "Name", "preco_usado_usd"])
    dados["ano"] = dados["data"].dt.year
    dados["mes"] = dados["data"].dt.month
    return dados[["data", "ano", "mes", "Name", "preco_varejo_usd", "preco_usado_usd"]]


def juntar_dados(historico_precos: pd.DataFrame, metadados: pd.DataFrame) -> pd.DataFrame:
    dados = limpar_historico_precos(historico_precos).merge(
        limpar_metadados(metadados), on="Name", how="left", validate="many_to_one"
    )
    dados["preco_por_ponto_3dmark"] = dados["preco_usado_usd"] / dados["pontuacao_3dmark"]
    dados["preco_por_gb_vram"] = dados["preco_usado_usd"] / dados["vram_gb"]
    dados["relacao_varejo_usado"] = dados["preco_varejo_usd"] / dados["preco_usado_usd"]
    return dados.sort_values(["Name", "data"]).reset_index(drop=True)
