"""Revisao opcional por modelo de linguagem LOCAL [Ollama], 100% offline.

DESLIGADA por padrao. Fala apenas com o servidor Ollama da propria maquina
[http://127.0.0.1:11434, ou OLLAMA_HOST]. Nenhum texto vai para a nuvem.

O modulo tambem:
  - localiza o Ollama instalado ou PORTATIL [pasta 'ollama/' ao lado do
    programa, com o conteudo do ollama-windows-amd64.zip] e o inicia sozinho;
  - baixa o modelo escolhido pela API do proprio Ollama [/api/pull], com
    progresso, sem terminal;
  - recusa a revisao de um trecho quando o modelo muda numeros [artigos,
    datas, valores] ou altera o tamanho do texto alem do tolerado: nesses
    casos mantem o texto da camada penal. O modelo corrige grafia; nao reescreve
    depoimento.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, List, Optional

from . import paths

MODELO_PADRAO = "gemma3:4b"
# Nome, descricao curta. Tamanhos conforme a biblioteca do Ollama.
MODELOS_SUGERIDOS = [
    ("gemma3:4b", "≈3,3 GB · padrão, 8 GB de RAM"),
    ("gemma3:12b", "≈8,1 GB · melhor, 16 GB de RAM"),
]

LINKS_DOWNLOAD = {
    "windows_instalador": "https://github.com/ollama/ollama/releases/latest/download/OllamaSetup.exe",
    "windows_portatil": "https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip",
    "macos": "https://github.com/ollama/ollama/releases/latest/download/Ollama.dmg",
    "linux": "https://ollama.com/install.sh",
    "pagina": "https://github.com/ollama/ollama/releases/latest",
}

PROMPT_SISTEMA = (
    "Você revisa trechos de transcrição de audiência criminal em português do "
    "Brasil. Corrija SOMENTE ortografia, acentuação, pontuação e a grafia de "
    "termos jurídicos. É proibido resumir, completar, reformular, trocar "
    "palavras por sinônimos, corrigir a gramática da fala do depoente, alterar "
    "números, nomes ou o sentido. Responda apenas com o trecho revisado, sem "
    "comentários, sem aspas e sem prefixos."
)

Progresso = Optional[Callable[[str], None]]


class ErroLLM(RuntimeError):
    """Falha de preparo ou de chamada ao Ollama, com mensagem para o usuario."""


# ---------------------------------------------------------------- servidor

def url_base() -> str:
    host = os.environ.get("OLLAMA_HOST", "").strip() or "127.0.0.1:11434"
    if not host.startswith("http"):
        host = "http://" + host
    return host.rstrip("/")


def _requisicao(caminho: str, payload: dict | None = None, timeout: float = 5.0):
    dados = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url_base() + caminho, data=dados,
        headers={"Content-Type": "application/json"} if dados else {},
    )
    return urllib.request.urlopen(req, timeout=timeout)


def disponivel(timeout: float = 1.5) -> bool:
    """True se houver um Ollama respondendo localmente."""
    try:
        with _requisicao("/api/version", timeout=timeout):
            return True
    except (urllib.error.URLError, OSError, ValueError):
        return False


def modelos_instalados(timeout: float = 5.0) -> List[str]:
    try:
        with _requisicao("/api/tags", timeout=timeout) as resp:
            corpo = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError):
        return []
    return sorted(m.get("name", "") for m in corpo.get("models", []) if m.get("name"))


def _mesmo_modelo(a: str, b: str) -> bool:
    """'gemma3' e 'gemma3:latest' sao o mesmo modelo para o Ollama."""
    norm = lambda n: n if ":" in n else n + ":latest"  # noqa: E731
    return norm(a.strip()) == norm(b.strip())


def modelo_instalado(nome: str) -> bool:
    return any(_mesmo_modelo(nome, m) for m in modelos_instalados())


def localizar_executavel() -> tuple[Optional[Path], bool]:
    """Devolve [caminho do ollama, e_portatil]. Portatil tem prioridade."""
    exe = "ollama.exe" if sys.platform == "win32" else "ollama"
    for base in paths.pastas_ollama():
        for cand in (base / exe, base / "bin" / exe):
            if cand.is_file():
                return cand, True
    no_path = shutil.which("ollama")
    if no_path:
        return Path(no_path), False
    candidatos = []
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA", "")
        if local:
            candidatos.append(Path(local) / "Programs" / "Ollama" / "ollama.exe")
    elif sys.platform == "darwin":
        candidatos.append(Path("/Applications/Ollama.app/Contents/Resources/ollama"))
    else:
        candidatos += [Path("/usr/local/bin/ollama"), Path("/usr/bin/ollama")]
    for cand in candidatos:
        if cand.is_file():
            return cand, False
    return None, False


def iniciar_servidor(progresso: Progresso = None, espera: float = 30.0) -> bool:
    """Garante um Ollama respondendo. Inicia 'ollama serve' se preciso."""
    if disponivel():
        return True
    exe, portatil = localizar_executavel()
    if exe is None:
        return False
    avisar = progresso or (lambda _m: None)
    avisar("Iniciando o Ollama local…")
    env = dict(os.environ)
    if portatil and "OLLAMA_MODELS" not in env:
        # Modo portatil: os modelos ficam junto do Ollama, nao no perfil.
        base = exe.parent.parent if exe.parent.name == "bin" else exe.parent
        env["OLLAMA_MODELS"] = str(base / "models")
    opcoes: dict = {"env": env, "stdin": subprocess.DEVNULL,
                    "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if sys.platform == "win32":
        opcoes["creationflags"] = (getattr(subprocess, "CREATE_NO_WINDOW", 0)
                                   | getattr(subprocess, "DETACHED_PROCESS", 0))
    else:
        opcoes["start_new_session"] = True
    try:
        subprocess.Popen([str(exe), "serve"], **opcoes)
    except OSError:
        return False
    limite = time.monotonic() + espera
    while time.monotonic() < limite:
        if disponivel():
            return True
        time.sleep(0.5)
    return False


def baixar_modelo(nome: str, progresso: Progresso = None) -> None:
    """Baixa o modelo pelo proprio Ollama [/api/pull], com progresso."""
    avisar = progresso or (lambda _m: None)
    if not iniciar_servidor(progresso):
        raise ErroLLM(mensagem_sem_ollama())
    try:
        with _requisicao("/api/pull", {"model": nome, "stream": True},
                         timeout=3600) as resp:
            ultimo = ""
            for linha in resp:
                if not linha.strip():
                    continue
                ev = json.loads(linha.decode("utf-8"))
                if ev.get("error"):
                    raise ErroLLM(f"O Ollama recusou o download de '{nome}': {ev['error']}")
                status = ev.get("status", "")
                total, feito = ev.get("total"), ev.get("completed")
                if total and feito:
                    msg = (f"Baixando {nome}: {100 * feito // total}% "
                           f"[{feito / 1e9:.2f} de {total / 1e9:.2f} GB]")
                else:
                    msg = f"{nome}: {status}"
                if msg != ultimo:
                    avisar(msg)
                    ultimo = msg
    except urllib.error.HTTPError as e:
        raise ErroLLM(f"Falha ao baixar '{nome}': HTTP {e.code}") from e
    except (urllib.error.URLError, OSError) as e:
        raise ErroLLM(f"Falha ao baixar '{nome}': {e}") from e
    if not modelo_instalado(nome):
        raise ErroLLM(f"O download de '{nome}' terminou sem o modelo instalado.")
    avisar(f"Modelo {nome} pronto.")


def mensagem_sem_ollama() -> str:
    return (
        "O Ollama não foi encontrado nesta máquina.\n\n"
        "Opção 1 [instalador Windows]: " + LINKS_DOWNLOAD["windows_instalador"] + "\n"
        "Opção 2 [portátil, sem instalar]: baixe " + LINKS_DOWNLOAD["windows_portatil"]
        + " e descompacte numa pasta chamada 'ollama' ao lado do TranscritorProfAMR.exe.\n"
        "macOS: " + LINKS_DOWNLOAD["macos"] + "\n"
        "Linux: curl -fsSL " + LINKS_DOWNLOAD["linux"] + " | sh"
    )


def preparar(modelo: str, progresso: Progresso = None) -> None:
    """Verifica servidor e modelo antes de transcrever. Levanta ErroLLM."""
    if not iniciar_servidor(progresso):
        raise ErroLLM(mensagem_sem_ollama())
    if not modelo_instalado(modelo):
        raise ErroLLM(
            f"O modelo '{modelo}' não está instalado no Ollama. "
            "Use o botão 'Baixar modelo' ou rode: ollama pull " + modelo
        )


# ---------------------------------------------------------------- revisao

_PREFIXOS = re.compile(
    r"^\s*(?:texto\s+(?:corrigido|revisado)|trecho\s+revisado|revis[aã]o)\s*:\s*",
    flags=re.IGNORECASE,
)
_NUMEROS = re.compile(r"\d+")


def _limpar_resposta(texto: str) -> str:
    texto = _PREFIXOS.sub("", texto.strip())
    if len(texto) >= 2 and texto[0] == texto[-1] and texto[0] in "\"'“”":
        texto = texto[1:-1].strip()
    return texto


def revisao_aceitavel(original: str, revisado: str, tolerancia: float = 0.25) -> bool:
    """Trava contra reescrita: mesmos numeros e tamanho proximo do original."""
    if not revisado.strip():
        return False
    if sorted(_NUMEROS.findall(original)) != sorted(_NUMEROS.findall(revisado)):
        return False
    a, b = len(original.split()), len(revisado.split())
    if a == 0:
        return b == 0
    return abs(b - a) / a <= tolerancia


def revisar(texto: str, modelo: str = MODELO_PADRAO, timeout: float = 180.0) -> str:
    """Envia o trecho ao Ollama local e devolve a resposta bruta limpa."""
    payload = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": PROMPT_SISTEMA},
            {"role": "user", "content": texto},
        ],
        "stream": False,
        "keep_alive": "15m",
        "options": {"temperature": 0.0},
    }
    try:
        with _requisicao("/api/chat", payload, timeout=timeout) as resp:
            corpo = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detalhe = e.read().decode("utf-8", "replace")[:300]
        raise ErroLLM(f"Ollama respondeu HTTP {e.code}: {detalhe}") from e
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise ErroLLM(f"Falha ao falar com o Ollama: {e}") from e
    conteudo = (corpo.get("message") or {}).get("content") or ""
    # Modelos com raciocinio podem devolver <think>…</think> antes da resposta.
    conteudo = re.sub(r"<think>.*?</think>", "", conteudo, flags=re.DOTALL)
    return _limpar_resposta(conteudo)
