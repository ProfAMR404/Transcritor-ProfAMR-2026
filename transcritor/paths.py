"""Resolve caminhos de dados, de saida, de modelos e do Ollama portatil.

Funciona tambem empacotado (PyInstaller). Quando o app roda como executavel
(sys.frozen), os arquivos de 'dados' ficam na pasta interna somente-leitura
(sys._MEIPASS); a saida vai para a pasta pessoal do usuario, e as pastas
'modelos/' e 'ollama/' sao procuradas ao lado do .exe.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, List


def empacotado() -> bool:
    return bool(getattr(sys, "frozen", False))


def _base_leitura() -> Path:
    if empacotado():  # executavel PyInstaller
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent


def pasta_app() -> Path:
    """Pasta visivel ao usuario: a do .exe (empacotado) ou a raiz do projeto."""
    if empacotado():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def pasta_usuario() -> Path:
    return Path.home() / "TranscritorProfAMR"


def pasta_dados() -> Path:
    return _base_leitura() / "dados"


def pasta_saida() -> Path:
    destino = pasta_usuario() / "saida" if empacotado() else _base_leitura() / "saida"
    destino.mkdir(parents=True, exist_ok=True)
    return destino


def pastas_modelos() -> List[Path]:
    """Onde procurar modelos baixados a mao, em ordem de preferencia."""
    return [pasta_app() / "modelos", pasta_usuario() / "modelos"]


def pastas_ollama() -> List[Path]:
    """Onde procurar o Ollama portatil [conteudo do ollama-windows-amd64.zip]."""
    return [pasta_app() / "ollama", pasta_usuario() / "ollama"]


def arquivo_config() -> Path:
    return pasta_usuario() / "config.json"


def ler_config() -> dict:
    try:
        dados = json.loads(arquivo_config().read_text(encoding="utf-8"))
        return dados if isinstance(dados, dict) else {}
    except (OSError, ValueError):
        return {}


def gravar_config(chave: str, valor: Any) -> None:
    dados = ler_config()
    dados[chave] = valor
    cfg = arquivo_config()
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
