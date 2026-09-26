"""Interface de linha de comando do Transcritor ProfAMR 2026.

Uso:
    transcritor demo                                  # amostra embutida
    transcritor transcrever audiencia.mp4             # transcricao real
    transcritor transcrever a.mp4 --modelo medium --llm
    transcritor ollama status                         # servidor e modelos
    transcritor ollama baixar gemma3:4b               # baixa modelo de revisao
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, asr, llm_local, paths, pipeline


def _mostrar(proc, rel, saidas) -> None:
    print("\n" + "=" * 60)
    print(f"  CAMADA PENAL — {rel.total} ajuste(s)")
    for chave, n in sorted(rel.penal.ocorrencias.items(), key=lambda kv: -kv[1]):
        print(f"  {n:>3}x  {chave}")
    if rel.llm_modelo:
        print(f"  LLM {rel.llm_modelo}: {rel.llm_alterados} alterado(s), "
              f"{rel.llm_recusados} recusado(s) pela trava")
    for aviso in rel.avisos:
        print(f"  AVISO: {aviso}")
    print("=" * 60)
    print("Arquivos gerados:")
    for tipo, caminho in saidas.items():
        print(f"  {tipo.upper():>4}: {caminho}")
    print("\nPrevia da ata:\n")
    print(saidas["txt"].read_text(encoding="utf-8"))


def _rodar(args, demo: bool) -> int:
    try:
        proc, rel, saidas, _meta = pipeline.executar(
            None if demo else args.arquivo,
            paths.pasta_dados(),
            Path(args.saida) if args.saida else paths.pasta_saida(),
            modelo=getattr(args, "modelo", asr.MODELO_PADRAO),
            usar_llm=args.llm,
            modelo_llm=args.modelo_llm,
            progresso=lambda m: print(m, flush=True),
            demo=demo,
        )
    except Exception as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1
    _mostrar(proc, rel, saidas)
    return 0


def cmd_ollama(args) -> int:
    if args.acao == "status":
        exe, portatil = llm_local.localizar_executavel()
        print(f"Executavel: {exe or 'nao encontrado'}{' [portatil]' if portatil else ''}")
        ok = llm_local.iniciar_servidor(lambda m: print(m))
        print(f"Servidor em {llm_local.url_base()}: {'respondendo' if ok else 'fora do ar'}")
        if not ok and exe is None:
            print(llm_local.mensagem_sem_ollama())
        for m in llm_local.modelos_instalados():
            print(f"  modelo instalado: {m}")
        return 0 if ok else 1
    try:
        llm_local.baixar_modelo(args.nome, lambda m: print(m, flush=True))
    except llm_local.ErroLLM as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="transcritor",
        description="Transcricao de audiencias penais em portugues, offline, com camada penal.",
    )
    p.add_argument("--versao", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    def comuns(sp):
        sp.add_argument("--llm", action="store_true", help="revisar com Ollama local")
        sp.add_argument("--modelo-llm", default=llm_local.MODELO_PADRAO,
                        help=f"modelo do Ollama [padrao {llm_local.MODELO_PADRAO}]")
        sp.add_argument("--saida", default=None, help="pasta de saida")

    pd = sub.add_parser("demo", help="roda o pipeline com a amostra embutida")
    comuns(pd)
    pd.set_defaults(func=lambda a: _rodar(a, demo=True))

    pt = sub.add_parser("transcrever", help="transcreve um arquivo de audio/video")
    pt.add_argument("arquivo", help="caminho do MP4/MP3/WAV/M4A…")
    pt.add_argument("--modelo", default=asr.MODELO_PADRAO, help="modelo Whisper")
    comuns(pt)
    pt.set_defaults(func=lambda a: _rodar(a, demo=False))

    po = sub.add_parser("ollama", help="gerencia o Ollama local")
    so = po.add_subparsers(dest="acao", required=True)
    so.add_parser("status", help="localiza/inicia o Ollama e lista modelos")
    pb = so.add_parser("baixar", help="baixa um modelo de revisao")
    pb.add_argument("nome", nargs="?", default=llm_local.MODELO_PADRAO)
    po.set_defaults(func=cmd_ollama)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
