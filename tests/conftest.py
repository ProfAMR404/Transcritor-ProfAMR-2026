import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import pytest


@pytest.fixture(autouse=True)
def _pasta_usuario_isolada(tmp_path, monkeypatch):
    """Nao ler nem gravar ~/TranscritorProfAMR da maquina de quem roda os testes."""
    from transcritor import paths
    monkeypatch.setattr(paths, "pasta_usuario", lambda: tmp_path / "_usuario")
