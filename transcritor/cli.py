"""Interface de linha de comando do Transcritor ProfAMR 2026.

Uso:
    transcritor demo                      # emula o pipeline com a amostra
    transcritor transcrever audiencia.mp4 # transcricao real (requer GPU + motor)
    transcritor transcrever a.mp4 --llm   # + revisao por LLM local (Ollama)

Sem GPU/motor instalado, "transcrever" cai automaticamente no modo demo.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, pipeline

RAIZ = Path(__file__).resolve().parent.parent
PASTA_DADOS = RAIZ / "dados"


def _relatorio(rel, mapa_rot) -> None:
    print("\n" + "=" * 60)
    print(f"  CAMADA PENAL — {rel.total} correcao(oes) aplicada(s)")
    print("=" * 60)
    if not rel.ocorrencias:
        print("  (nenhuma)")
    for chave, n in sorted(rel.ocorrencias.items(), key=lambda kv: -kv[1]):
        if n:
            print(f"  {n:>3}x  {chave}")
    if mapa_rot:
        print("\n  Falantes renomeados:")
        for k, v in mapa_rot.items():
            print(f"        {k} -> {v}")
    print("=" * 60 + "\n")


def _executar(trechos, destino: Path, nome: str, usar_llm: bool) -> None:
    processados, rel, mapa_rot = pipeline.processar(
        trechos, PASTA_DADOS, usar_llm=usar_llm
    )
    saidas = pipeline.escrever_saidas(processados, destino, nome)
    _relatorio(rel, mapa_rot)
    print("Arquivos gerados:")
    for tipo, caminho in saidas.items():
        print(f"  {tipo.upper():>4}: {caminho}")
    print("\nPrevia da ata:\n")
    print(saidas["txt"].read_text(encoding="utf-8"))


def cmd_demo(args) -> int:
    print(">> Modo DEMO (emulado, sem GPU) — amostra dados/exemplo_whisperx.json")
    trechos = pipeline.carregar_segmentos(PASTA_DADOS / "exemplo_whisperx.json")
    _executar(trechos, RAIZ / "saida", "demo_audiencia", args.llm)
    return 0


def cmd_transcrever(args) -> int:
    entrada = Path(args.arquivo)
    if not entrada.exists():
        print(f"ERRO: arquivo nao encontrado: {entrada}", file=sys.stderr)
        return 2
    motor = pipeline.motor_disponivel()
    if not motor:
        print(
            "AVISO: nenhum motor de ASR (WhisperX/TecJustica) encontrado nem GPU.\n"
            "       Rodando em modo DEMO com a amostra. Instale o motor para uso real.",
            file=sys.stderr,
        )
        return cmd_demo(args)
    print(f">> Transcrevendo '{entrada.name}' com motor: {motor}")
    saida_json = RAIZ / "saida" / (entrada.stem + ".json")
    saida_json.parent.mkdir(parents=True, exist_ok=True)
    pipeline.transcrever_real(str(entrada), saida_json, motor)
    trechos = pipeline.carregar_segmentos(saida_json)
    _executar(trechos, RAIZ / "saida", entrada.stem, args.llm)
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="transcritor",
        description="Transcricao de audiencias penais em portugues, offline, com camada penal.",
    )
    p.add_argument("--versao", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    pd = sub.add_parser("demo", help="emula o pipeline com a amostra embutida")
    pd.add_argument("--llm", action="store_true", help="revisar com Ollama local")
    pd.set_defaults(func=cmd_demo)

    pt = sub.add_parser("transcrever", help="transcreve um arquivo de audio/video")
    pt.add_argument("arquivo", help="caminho do MP4/MP3/WAV")
    pt.add_argument("--llm", action="store_true", help="revisar com Ollama local")
    pt.set_defaults(func=cmd_transcrever)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
