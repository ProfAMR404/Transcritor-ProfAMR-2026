"""Resolve caminhos de dados e de saida, funcionando tambem empacotado (PyInstaller).

Quando o app roda como executavel (sys.frozen), os arquivos de 'dados' ficam numa
pasta temporaria somente-leitura (sys._MEIPASS), e a saida NAO pode ir para la —
vai para a pasta pessoal do usuario.
"""
from __future__ import annotations

import sys
from pathlib import Path


def _base_leitura() -> Path:
    if getattr(sys, "frozen", False):  # executavel PyInstaller
        return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return Path(__file__).resolve().parent.parent


def pasta_dados() -> Path:
    return _base_leitura() / "dados"


def pasta_saida() -> Path:
    if getattr(sys, "frozen", False):
        destino = Path.home() / "TranscritorProfAMR" / "saida"
    else:
        destino = _base_leitura() / "saida"
    destino.mkdir(parents=True, exist_ok=True)
    return destino
