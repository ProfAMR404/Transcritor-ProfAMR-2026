"""Autoteste do pacote empacotado [usado pelo CI e pelo suporte].

    TranscritorProfAMR.exe --autoteste relatorio.txt [--audio fala.wav] [--modelo tiny]

Verifica, dentro do proprio executavel: imports do motor [faster-whisper,
CTranslate2, PyAV, onnxruntime], camada penal na amostra embutida e, se houver
--audio, uma transcricao real. Grava o relatorio no arquivo indicado [o .exe de
janela nao tem console] e sai com codigo 0 [ok] ou 1 [falha].
"""
from __future__ import annotations

import argparse
import tempfile
import traceback
from pathlib import Path

from . import __version__, paths, pipeline


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="autoteste")
    p.add_argument("--autoteste", required=True, metavar="RELATORIO")
    p.add_argument("--audio", default=None)
    p.add_argument("--modelo", default="tiny")
    args = p.parse_args(argv)

    linhas = [f"Transcritor ProfAMR v{__version__} — autoteste"]
    ok = True

    def etapa(nome, func):
        nonlocal ok
        try:
            det = func()
            linhas.append(f"[OK]   {nome}{': ' + str(det) if det else ''}")
        except Exception:
            ok = False
            linhas.append(f"[FALHA] {nome}\n{traceback.format_exc()}")

    def imports():
        import av
        import ctranslate2
        import faster_whisper
        import onnxruntime
        return (f"faster-whisper {faster_whisper.__version__}, ctranslate2 "
                f"{ctranslate2.__version__}, av {av.__version__}, onnxruntime "
                f"{onnxruntime.__version__}")

    def demo():
        with tempfile.TemporaryDirectory() as tmp:
            proc, rel, _s, _m = pipeline.executar(
                None, paths.pasta_dados(), Path(tmp), demo=True)
            assert proc and rel.total > 0, "camada penal sem efeito na amostra"
            return f"{len(proc)} trechos, {rel.total} ajustes"

    def real():
        with tempfile.TemporaryDirectory() as tmp:
            proc, _r, saidas, meta = pipeline.executar(
                args.audio, paths.pasta_dados(), Path(tmp), modelo=args.modelo)
            texto = " ".join(t.texto for t in proc)
            assert texto.strip(), "transcricao vazia"
            return f"{len(proc)} trechos, sha256 {meta.sha256[:12]}…: {texto[:160]}"

    def motor():
        nome = pipeline.motor_disponivel()
        if not nome:
            raise RuntimeError("nenhum motor de transcricao no pacote")
        return nome

    etapa("motor instalado", motor)
    etapa("imports do motor", imports)
    etapa("pipeline demo + camada penal", demo)
    if args.audio:
        etapa(f"transcricao real [{args.modelo}] de {args.audio}", real)

    linhas.append("RESULTADO: " + ("SUCESSO" if ok else "FALHA"))
    Path(args.autoteste).write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
