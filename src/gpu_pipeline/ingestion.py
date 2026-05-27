from pathlib import Path

import pandas as pd


def carregar_metadados(caminho: Path) -> pd.DataFrame:
    return pd.read_csv(caminho)


def carregar_historico_precos(caminho: Path) -> pd.DataFrame:
    return pd.read_csv(caminho)
