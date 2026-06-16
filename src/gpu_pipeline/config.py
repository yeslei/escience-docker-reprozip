from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ConfiguracaoPipeline:
    caminho_metadados: Path
    caminho_precos: Path
    diretorio_saida: Path
    top_n_grafico: int = 8
    tamanho_teste: float = 0.25
    semente: int = 42

    @property
    def diretorio_processado(self) -> Path:
        return self.diretorio_saida / "processed"

    @property
    def diretorio_figuras(self) -> Path:
        return self.diretorio_saida / "figures"

    @property
    def diretorio_metricas(self) -> Path:
        return self.diretorio_saida / "metrics"


def configuracao_padrao(diretorio_saida: str | Path = "artifacts") -> ConfiguracaoPipeline:
    return ConfiguracaoPipeline(
        caminho_metadados=Path("gpu_metadata.csv"),
        caminho_precos=Path("gpu_price_history.csv"),
        diretorio_saida=Path(diretorio_saida),
    )
