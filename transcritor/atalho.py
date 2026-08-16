"""Cria um atalho na Area de Trabalho (Windows), sem dependencias externas.

Usa o PowerShell (WScript.Shell) para gerar um .lnk apontando para o executavel.
So faz sentido quando o app roda como .exe empacotado (sys.frozen); rodando do
codigo-fonte, o alvo seria o python.exe — entao nesse caso nao cria.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

NOME_ATALHO = "Transcritor ProfAMR"


def _exe_alvo() -> Path | None:
    """Caminho do executavel a apontar. None se nao estiver empacotado."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable)
    return None


def suportado() -> bool:
    return sys.platform == "win32" and _exe_alvo() is not None


def caminho_atalho() -> Path:
    desktop = Path(os.path.join(os.path.expanduser("~"), "Desktop"))
    return desktop / f"{NOME_ATALHO}.lnk"


def criar_atalho_windows(nome: str = NOME_ATALHO) -> Path | None:
    """Cria (ou atualiza) o atalho. Retorna o caminho, ou None se nao aplicavel."""
    exe = _exe_alvo()
    if sys.platform != "win32" or exe is None:
        return None
    # PowerShell resolve a Area de Trabalho de forma robusta (mesmo com OneDrive).
    ps = (
        "$d=[Environment]::GetFolderPath('Desktop');"
        f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut($d+'\\{nome}.lnk');"
        f"$s.TargetPath='{exe}';"
        f"$s.WorkingDirectory='{exe.parent}';"
        f"$s.IconLocation='{exe}';"
        "$s.Description='Transcritor de audiencias penais - Prof. AMR';"
        "$s.Save()"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    return caminho_atalho()


def criar_no_primeiro_uso() -> Path | None:
    """Cria o atalho uma unica vez (marca com um arquivo-sentinela). Silencioso."""
    if not suportado():
        return None
    marcador = _exe_alvo().parent / ".atalho_criado"
    try:
        if marcador.exists():
            return None
        alvo = criar_atalho_windows()
        try:
            marcador.write_text("ok", encoding="utf-8")
        except OSError:
            # pasta do programa somente-leitura: usa a pasta pessoal
            alt = Path(os.path.expanduser("~")) / ".transcritor_atalho_criado"
            alt.write_text("ok", encoding="utf-8")
        return alvo
    except Exception:
        return None
