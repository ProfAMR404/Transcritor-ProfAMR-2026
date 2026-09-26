"""Entrypoint do motor para o sidecar do Tauri.

Contrato maquina-a-maquina:
- stdout: um unico objeto JSON com o resultado [trechos + arquivos + relatorio].
- stderr: linhas de progresso no formato 'PROGRESSO: <mensagem>' [uma por linha].
- codigo de saida 0 em sucesso; !=0 em erro, com JSON de erro no stdout.

Uso:
    python -m transcritor.engine_json transcrever <arquivo> [--modelo small]
        [--llm] [--modelo-llm gemma3:4b] [--saida <dir>] [--dados <dir>]
    python -m transcritor.engine_json demo [--llm]
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from . import asr, llm_local, paths, pipeline


def _progresso(msg: str) -> None:
    print(f"PROGRESSO: {msg}", file=sys.stderr, flush=True)


def _saida_json(dados: dict, codigo: int = 0) -> int:
    print(json.dumps(dados, ensure_ascii=False), flush=True)
    return codigo


def _rodar(args, demo: bool) -> int:
    pasta_dados = Path(args.dados) if args.dados else paths.pasta_dados()
    pasta_saida = Path(args.saida) if args.saida else paths.pasta_saida()
    try:
        proc, rel, saidas, meta = pipeline.executar(
            None if demo else args.arquivo, pasta_dados, pasta_saida,
            modelo=getattr(args, "modelo", asr.MODELO_PADRAO),
            usar_llm=args.llm, modelo_llm=args.modelo_llm,
            progresso=_progresso, demo=demo,
        )
    except FileNotFoundError as e:
        return _saida_json({"ok": False, "erro": str(e)}, 2)
    except Exception as e:  # devolve o erro real, sem mascarar
        return _saida_json({"ok": False, "erro": str(e)}, 1)
    _progresso("Concluido")
    return _saida_json({
        "ok": True,
        "motor": meta.motor,
        "metadados": asdict(meta),
        "correcoes": rel.total,
        "ocorrencias": rel.penal.ocorrencias,
        "mapa_falantes": rel.mapa_falantes,
        "llm_alterados": rel.llm_alterados,
        "llm_recusados": rel.llm_recusados,
        "avisos": rel.avisos,
        "trechos": [asdict(t) for t in proc],
        "ata": saidas["txt"].read_text(encoding="utf-8"),
        "arquivos": {k: str(v) for k, v in saidas.items()},
    })


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="transcritor-engine")
    sub = p.add_subparsers(dest="cmd", required=True)

    def comuns(sp):
        sp.add_argument("--llm", action="store_true")
        sp.add_argument("--modelo-llm", default=llm_local.MODELO_PADRAO)
        sp.add_argument("--saida", default=None)
        sp.add_argument("--dados", default=None)

    pt = sub.add_parser("transcrever")
    pt.add_argument("arquivo")
    pt.add_argument("--modelo", default=asr.MODELO_PADRAO)
    comuns(pt)
    pt.set_defaults(func=lambda a: _rodar(a, demo=False))

    pd = sub.add_parser("demo")
    comuns(pd)
    pd.set_defaults(func=lambda a: _rodar(a, demo=True))

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
