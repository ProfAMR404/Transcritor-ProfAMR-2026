"""Ponto de entrada do sidecar do Tauri [empacotado pelo PyInstaller].

Vira o binario 'transcritor-engine' chamado pela casca Tauri. Delega ao
motor JSON [transcritor.engine_json]: stdout = JSON, stderr = progresso.
"""
import multiprocessing

from transcritor.engine_json import main

if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
