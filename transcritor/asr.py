"""Motor de transcricao REAL via faster-whisper (CTranslate2).

Roda em CPU em qualquer desktop. Com GPU NVIDIA e CUDA/cuDNN instalados, usa a
GPU; se a GPU falhar [DLL do CUDA ausente, memoria insuficiente], cai para a
CPU sozinho, em vez de abortar a transcricao.

Import "preguicoso": o modulo carrega mesmo sem o faster-whisper instalado; o
erro so aparece quando se tenta transcrever de fato.

Variaveis de ambiente:
    TRANSCRITOR_DEVICE=cpu|cuda     forca o dispositivo
    TRANSCRITOR_MODELO_DIR=<pasta>  usa uma pasta de modelo ja baixada
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, List, Optional

from . import paths

# Tamanhos uteis (equilibrio qualidade x velocidade em CPU):
#   tiny/base  -> rapidos, para triagem
#   small      -> bom padrao em portugues
#   medium     -> melhor, porem lento em CPU
#   large-v3   -> maxima qualidade, so vale com GPU
MODELOS = ["tiny", "base", "small", "medium", "large-v3", "large-v3-turbo"]
MODELO_PADRAO = "small"

# Nomes curtos que o faster-whisper nao conhece por conta propria.
_REPOS_EXTRA = {"large-v3-turbo": "deepdml/faster-whisper-large-v3-turbo-ct2"}

Progresso = Optional[Callable[[str], None]]


def carregar_glossario(pasta_dados: Path) -> Optional[str]:
    """Le dados/glossario_penal.txt e devolve o texto de vies (initial_prompt)."""
    caminho = pasta_dados / "glossario_penal.txt"
    if not caminho.exists():
        return None
    linhas = [
        ln.strip()
        for ln in caminho.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    ]
    texto = " ".join(linhas)
    return texto or None


def disponivel() -> bool:
    """True se o faster-whisper puder ser importado nesta maquina."""
    try:
        import faster_whisper  # noqa: F401
        return True
    except Exception:
        return False


def _dispositivos() -> List[tuple[str, str]]:
    """Ordem de tentativa [dispositivo, tipo de computacao]."""
    forcado = os.environ.get("TRANSCRITOR_DEVICE", "").strip().lower()
    if forcado == "cpu":
        return [("cpu", "int8")]
    if forcado == "cuda":
        return [("cuda", "float16")]
    try:
        import ctranslate2

        if ctranslate2.get_cuda_device_count() > 0:
            return [("cuda", "float16"), ("cpu", "int8")]
    except Exception:
        pass
    return [("cpu", "int8")]


def resolver_modelo(modelo: str) -> str:
    """Devolve a pasta local do modelo, se houver; senao o nome/repo para download.

    Ordem: TRANSCRITOR_MODELO_DIR; caminho direto em 'modelo'; 'modelos/<nome>'
    ao lado do programa; ~/TranscritorProfAMR/modelos/<nome>; download do
    Hugging Face na primeira vez [fica em cache, depois roda offline].
    """
    env = os.environ.get("TRANSCRITOR_MODELO_DIR")
    if env and Path(env).is_dir():
        return env
    if Path(modelo).is_dir():
        return str(modelo)
    for base in paths.pastas_modelos():
        local = base / modelo
        if (local / "model.bin").exists():
            return str(local)
    return _REPOS_EXTRA.get(modelo, modelo)


def _carregar(modelo_final: str, device: str, compute: str):
    from faster_whisper import WhisperModel

    try:
        return WhisperModel(modelo_final, device=device, compute_type=compute)
    except Exception as e:
        if Path(modelo_final).is_dir():
            raise
        raise RuntimeError(
            f"Nao foi possivel obter o modelo '{modelo_final}'. Na primeira vez o "
            "modelo e baixado da internet [Hugging Face]; verifique a conexao, ou "
            "baixe o modelo a mao para a pasta 'modelos' [ver MODELOS.md].\n"
            f"Detalhe tecnico: {e}"
        ) from e


def transcrever(
    entrada: str | Path,
    pasta_dados: Path,
    modelo: str = MODELO_PADRAO,
    idioma: str = "pt",
    progresso: Progresso = None,
) -> List[dict]:
    """Transcreve um audio/video e devolve segmentos {start,end,speaker,text}.

    O faster-whisper nao separa falantes: 'speaker' sai None. A ata, entao, nao
    atribui fala a ninguem [atribuir tudo a um unico papel processual seria
    registro falso]. A separacao por falante exige o motor WhisperX [GPU].
    """
    try:
        import faster_whisper  # noqa: F401
    except ImportError as e:  # pragma: no cover - depende do ambiente
        raise RuntimeError(
            "faster-whisper nao esta instalado. Rode: pip install faster-whisper"
        ) from e

    avisar = progresso or (lambda _m: None)
    modelo_final = resolver_modelo(modelo)
    origem = "pasta local" if Path(modelo_final).is_dir() else "cache/download"
    initial_prompt = carregar_glossario(pasta_dados)

    tentativas = _dispositivos()
    ultimo_erro: Exception | None = None
    for i, (device, compute) in enumerate(tentativas):
        try:
            avisar(f"Carregando modelo '{modelo}' [{device}/{compute}, {origem}]…")
            model = _carregar(modelo_final, device, compute)
            avisar("Transcrevendo…")
            segmentos_iter, info = model.transcribe(
                str(entrada),
                language=idioma,
                initial_prompt=initial_prompt,
                vad_filter=True,  # ignora silencios: mais rapido e limpo
                beam_size=5,
            )
            duracao = float(getattr(info, "duration", 0.0) or 0.0)
            trechos: List[dict] = []
            for seg in segmentos_iter:
                texto = (seg.text or "").strip()
                if not texto:
                    continue
                trechos.append(
                    {"start": float(seg.start), "end": float(seg.end),
                     "speaker": None, "text": texto}
                )
                if duracao > 0:
                    pct = min(100, int(100 * seg.end / duracao))
                    avisar(f"Transcrevendo… {pct}% [{_mmss(seg.end)} de {_mmss(duracao)}]")
                else:
                    avisar(f"Transcrevendo… {_mmss(seg.end)}")
            return trechos
        except Exception as e:
            ultimo_erro = e
            ha_proxima = i + 1 < len(tentativas)
            if device == "cuda" and ha_proxima:
                avisar(f"GPU indisponivel [{e}]. Repetindo em CPU…")
                continue
            raise
    raise RuntimeError(str(ultimo_erro))  # pragma: no cover


def _mmss(seg: float) -> str:
    s = int(seg)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"
