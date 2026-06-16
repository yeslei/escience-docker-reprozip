import csv
import json
import os
import platform
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class RegistroExecucao:
    timestamp_utc: str
    contexto: str
    duracao_segundos: float
    python: str
    sistema: str


@dataclass(frozen=True)
class ResumoComparativo:
    contexto: str
    execucoes: int
    media_segundos: float
    mediana_segundos: float
    desvio_padrao_segundos: float
    minimo_segundos: float
    maximo_segundos: float
    overhead_percentual: float | None


def contexto_execucao_padrao() -> str:
    return os.environ.get("PIPELINE_CONTEXT", "native")


def criar_registro_execucao(
    duracao_segundos: float,
    contexto: str | None = None,
) -> RegistroExecucao:
    return RegistroExecucao(
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        contexto=contexto or contexto_execucao_padrao(),
        duracao_segundos=round(duracao_segundos, 6),
        python=platform.python_version(),
        sistema=platform.platform(),
    )


def salvar_registro_execucao(
    registro: RegistroExecucao,
    diretorio_metricas: Path,
) -> dict[str, Path]:
    diretorio_metricas.mkdir(parents=True, exist_ok=True)

    caminho_csv = diretorio_metricas / "pipeline_runs.csv"
    caminho_json = diretorio_metricas / "latest_pipeline_run.json"
    dados = asdict(registro)

    escrever_cabecalho = not caminho_csv.exists()
    with caminho_csv.open("a", newline="", encoding="utf-8") as arquivo_csv:
        escritor = csv.DictWriter(arquivo_csv, fieldnames=dados.keys())
        if escrever_cabecalho:
            escritor.writeheader()
        escritor.writerow(dados)

    caminho_json.write_text(
        json.dumps(dados, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "metricas_execucao_csv": caminho_csv,
        "metricas_execucao_json": caminho_json,
    }


def carregar_registros_execucao(caminho_csv: Path) -> list[RegistroExecucao]:
    with caminho_csv.open(newline="", encoding="utf-8") as arquivo_csv:
        leitor = csv.DictReader(arquivo_csv)
        return [
            RegistroExecucao(
                timestamp_utc=linha["timestamp_utc"],
                contexto=linha["contexto"],
                duracao_segundos=float(linha["duracao_segundos"]),
                python=linha["python"],
                sistema=linha["sistema"],
            )
            for linha in leitor
        ]


def resumir_execucoes(
    registros: list[RegistroExecucao],
    contexto_base: str = "native",
) -> list[ResumoComparativo]:
    duracoes_por_contexto: dict[str, list[float]] = {}
    for registro in registros:
        duracoes_por_contexto.setdefault(registro.contexto, []).append(
            registro.duracao_segundos
        )

    duracoes_base = duracoes_por_contexto.get(contexto_base, [])
    media_base = sum(duracoes_base) / len(duracoes_base) if duracoes_base else None

    resumos: list[ResumoComparativo] = []
    for contexto, duracoes in sorted(duracoes_por_contexto.items()):
        media = sum(duracoes) / len(duracoes)
        desvio_padrao = statistics.stdev(duracoes) if len(duracoes) > 1 else 0.0
        overhead = None
        if media_base and contexto != contexto_base:
            overhead = ((media - media_base) / media_base) * 100

        resumos.append(
            ResumoComparativo(
                contexto=contexto,
                execucoes=len(duracoes),
                media_segundos=round(media, 6),
                mediana_segundos=round(statistics.median(duracoes), 6),
                desvio_padrao_segundos=round(desvio_padrao, 6),
                minimo_segundos=round(min(duracoes), 6),
                maximo_segundos=round(max(duracoes), 6),
                overhead_percentual=round(overhead, 2)
                if overhead is not None
                else None,
            )
        )

    return resumos


def salvar_resumo_comparativo(
    resumos: list[ResumoComparativo],
    diretorio_metricas: Path,
) -> dict[str, Path]:
    diretorio_metricas.mkdir(parents=True, exist_ok=True)

    caminho_csv = diretorio_metricas / "comparison_summary.csv"
    caminho_json = diretorio_metricas / "comparison_summary.json"
    linhas = [asdict(resumo) for resumo in resumos]

    if linhas:
        with caminho_csv.open("w", newline="", encoding="utf-8") as arquivo_csv:
            escritor = csv.DictWriter(arquivo_csv, fieldnames=linhas[0].keys())
            escritor.writeheader()
            escritor.writerows(linhas)
    else:
        caminho_csv.write_text("", encoding="utf-8")

    caminho_json.write_text(
        json.dumps(linhas, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "resumo_comparativo_csv": caminho_csv,
        "resumo_comparativo_json": caminho_json,
    }
