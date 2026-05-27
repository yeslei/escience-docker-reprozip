import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from gpu_pipeline.config import configuracao_padrao
from gpu_pipeline.pipeline import executar_pipeline


def main() -> None:
    configuracao = configuracao_padrao()
    arquivos = executar_pipeline(configuracao)

    print("Pipeline executada com sucesso. Arquivos gerados:")
    for nome, caminho in arquivos.items():
        print(f"- {nome}: {caminho}")


if __name__ == "__main__":
    main()
