"""Entrypoint do motor para o sidecar do Tauri.

Contrato maquina-a-maquina:
- stdout: um unico objeto JSON com o resultado [trechos + arquivos + relatorio].
- stderr: linhas de progresso no formato 'PROGRESSO: <mensagem>' [uma por linha].
- codigo de saida 0 em sucesso; !=0 em erro, com JSON de erro no stdout.

Uso:
    python -m transcritor.engine_json transcrever <arquivo> [--modelo small]
        [--llm] [--saida <dir>] [--dados <dir>]
    python -m transcritor.engine_json demo [--llm]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import paths, pipeline


def _progresso(msg: str) -> None:
    print(f"PROGRESSO: {msg}", file=sys.stderr, flush=True)


def _saida_json(dados: dict, codigo: int = 0) -> int:
    print(json.dumps(dados, ensure_ascii=False), flush=True)
    return codigo


def _executar(trechos, pasta_dados: Path, pasta_saida: Path, nome: str, usar_llm: bool) -> dict:
    proc, rel, mapa = pipeline.processar(trechos, pasta_dados, usar_llm=usar_llm)
    saidas = pipeline.escrever_saidas(proc, pasta_saida, nome)
    return {
        "ok": True,
        "correcoes": rel.total,
        "ocorrencias": rel.ocorrencias,
        "mapa_falantes": mapa,
        "trechos": [t.__dict__ for t in proc],
        "arquivos": {k: str(v) for k, v in saidas.items()},
    }


def cmd_transcrever(args) -> int:
    entrada = Path(args.arquivo)
    if not entrada.exists():
        return _saida_json({"ok": False, "erro": f"arquivo nao encontrado: {entrada}"}, 2)
    pasta_dados = Path(args.dados) if args.dados else paths.pasta_dados()
    pasta_saida = Path(args.saida) if args.saida else paths.pasta_saida()
    pasta_saida.mkdir(parents=True, exist_ok=True)

    motor = pipeline.motor_disponivel()
    if not motor:
        return _saida_json(
            {"ok": False, "erro": "nenhum motor de ASR instalado",
             "dica": "instale o motor de CPU: pip install faster-whisper"}, 3)

    _progresso(f"Motor: {motor}")
    try:
        trechos = pipeline.transcrever_entrada(
            entrada, pasta_dados, motor, pasta_saida, progresso=_progresso
        )
        _progresso("Aplicando camada penal")
        res = _executar(trechos, pasta_dados, pasta_saida, entrada.stem, args.llm)
        res["motor"] = motor
        _progresso("Concluido")
        return _saida_json(res)
    except Exception as e:  # devolve o erro real, sem mascarar
        return _saida_json({"ok": False, "erro": str(e)}, 1)


def cmd_demo(args) -> int:
    pasta_dados = paths.pasta_dados()
    pasta_saida = paths.pasta_saida()
    _progresso("Modo demo [amostra embutida]")
    trechos = pipeline.carregar_segmentos(pasta_dados / "exemplo_whisperx.json")
    res = _executar(trechos, pasta_dados, pasta_saida, "demo_audiencia", args.llm)
    res["motor"] = "demo"
    _progresso("Concluido")
    return _saida_json(res)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="transcritor-engine")
    sub = p.add_subparsers(dest="cmd", required=True)

    pt = sub.add_parser("transcrever")
    pt.add_argument("arquivo")
    pt.add_argument("--modelo", default="small")
    pt.add_argument("--llm", action="store_true")
    pt.add_argument("--saida", default=None)
    pt.add_argument("--dados", default=None)
    pt.set_defaults(func=cmd_transcrever)

    pd = sub.add_parser("demo")
    pd.add_argument("--llm", action="store_true")
    pd.set_defaults(func=cmd_demo)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
