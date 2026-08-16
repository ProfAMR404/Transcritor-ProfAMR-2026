"""Pos-correcao opcional por LLM LOCAL (Ollama), 100% offline.

DESLIGADO por padrao. So e usado com a flag --llm. Nunca envia audio ou texto
para a nuvem: fala apenas com um servidor Ollama em http://localhost:11434.

Motivo do cuidado: depoimentos contem dado pessoal sensivel (LGPD). A regra do
projeto e que nenhum conteudo de audiencia saia da maquina.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"

PROMPT_SISTEMA = (
    "Voce e um revisor de atas de audiencia criminal em portugues do Brasil. "
    "Corrija APENAS ortografia, pontuacao, concordancia e a grafia de termos "
    "juridicos e de dispositivos legais. NAO resuma, NAO invente, NAO altere o "
    "sentido, NAO acrescente informacao. Devolva somente o texto corrigido."
)


def disponivel(timeout: float = 1.5) -> bool:
    """Retorna True se houver um Ollama respondendo localmente."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=timeout):
            return True
    except (urllib.error.URLError, OSError):
        return False


def revisar(texto: str, modelo: str = "llama3.1", timeout: float = 60.0) -> str:
    """Envia o texto ao Ollama local para revisao. Em falha, devolve o original."""
    payload = {
        "model": modelo,
        "prompt": f"{PROMPT_SISTEMA}\n\nTEXTO:\n{texto}\n\nTEXTO CORRIGIDO:",
        "stream": False,
        "options": {"temperature": 0.0},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            corpo = json.loads(resp.read().decode("utf-8"))
            return (corpo.get("response") or texto).strip()
    except (urllib.error.URLError, OSError, json.JSONDecodeError):
        return texto
