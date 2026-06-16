import sys
from pathlib import Path
from time import perf_counter

sys.path.append(str(Path(__file__).parent / "src"))

from gpu_pipeline.config import configuracao_padrao
from gpu_pipeline.metrics import criar_registro_execucao, salvar_registro_execucao
from gpu_pipeline.pipeline import executar_pipeline


def main() -> None:
    configuracao = configuracao_padrao()
    inicio = perf_counter()
    arquivos = executar_pipeline(configuracao)
    duracao = perf_counter() - inicio
    registro = criar_registro_execucao(duracao)
    arquivos.update(
        salvar_registro_execucao(registro, configuracao.diretorio_metricas)
    )

    print("Pipeline executada com sucesso. Arquivos gerados:")
    for nome, caminho in arquivos.items():
        print(f"- {nome}: {caminho}")
    print(
        f"Tempo de execucao registrado: {registro.duracao_segundos:.6f}s "
        f"({registro.contexto})"
    )


if __name__ == "__main__":
    main()
