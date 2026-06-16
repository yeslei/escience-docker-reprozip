import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from gpu_pipeline.metrics import (
    carregar_registros_execucao,
    resumir_execucoes,
    salvar_resumo_comparativo,
)


def main() -> None:
    diretorio_metricas = Path("artifacts") / "metrics"
    caminho_execucoes = diretorio_metricas / "pipeline_runs.csv"

    if not caminho_execucoes.exists():
        raise SystemExit(
            "Nenhum registro encontrado em artifacts/metrics/pipeline_runs.csv. "
            "Execute a pipeline pelo menos uma vez em cada contexto."
        )

    registros = carregar_registros_execucao(caminho_execucoes)
    resumos = resumir_execucoes(registros)
    arquivos = salvar_resumo_comparativo(resumos, diretorio_metricas)

    print("Resumo comparativo gerado:")
    for resumo in resumos:
        overhead = (
            "baseline"
            if resumo.overhead_percentual is None
            else f"{resumo.overhead_percentual:.2f}%"
        )
        print(
            f"- {resumo.contexto}: media={resumo.media_segundos:.6f}s, "
            f"mediana={resumo.mediana_segundos:.6f}s, "
            f"desvio_padrao={resumo.desvio_padrao_segundos:.6f}s, "
            f"execucoes={resumo.execucoes}, overhead={overhead}"
        )

    for nome, caminho in arquivos.items():
        print(f"- {nome}: {caminho}")


if __name__ == "__main__":
    main()
