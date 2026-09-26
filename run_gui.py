"""Ponto de entrada para empacotamento com PyInstaller (janela desktop).

No .exe de janela [--windowed], sys.stdout e sys.stderr sao None: qualquer
biblioteca que escreva neles [barra de progresso do download do modelo, avisos]
derruba o programa. Redireciona ambos para um log antes de importar o motor.
"""
import sys


def _garantir_saidas() -> None:
    if sys.stdout is not None and sys.stderr is not None:
        return
    from pathlib import Path

    try:
        pasta = Path.home() / "TranscritorProfAMR"
        pasta.mkdir(parents=True, exist_ok=True)
        log = open(pasta / "transcritor.log", "a", encoding="utf-8", buffering=1)
    except OSError:
        import os
        log = open(os.devnull, "w", encoding="utf-8")
    if sys.stdout is None:
        sys.stdout = log
    if sys.stderr is None:
        sys.stderr = log


_garantir_saidas()

if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()
    if "--autoteste" in sys.argv:
        from transcritor.autoteste import main as autoteste

        raise SystemExit(autoteste(sys.argv[1:]))
    from transcritor.gui import main

    raise SystemExit(main())
