"""Mapeia rotulos de diarizacao (SPEAKER_00...) para papeis processuais."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


def carregar_mapa(caminho: str | Path) -> Dict[str, str]:
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    mapa = dados.get("mapa", {})
    # ignora rotulos com valor vazio (mantem o original)
    return {k: v for k, v in mapa.items() if v}


def aplicar(speaker: str, mapa: Dict[str, str]) -> str:
    return mapa.get(speaker, speaker)
