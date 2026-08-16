"""Motor de transcricao REAL em CPU, via faster-whisper (CTranslate2).

Roda em qualquer desktop, sem GPU NVIDIA. Em maquina com GPU, o mesmo pacote usa
CUDA automaticamente. Import e "preguicoso": este modulo carrega mesmo sem o
faster-whisper instalado (o erro so aparece quando se tenta transcrever de fato),
para nao quebrar o modo demo nem a GUI.

Instalacao na maquina de uso:
    pip install faster-whisper            # CPU
    # (GPU: instale tambem o CUDA/cuDNN correspondente)
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, List, Optional

# Tamanhos uteis (equilibrio qualidade x velocidade em CPU):
#   tiny/base  -> rapidos, para triagem
#   small      -> bom padrao em portugues
#   medium     -> melhor, porem lento em CPU
#   large-v3   -> maxima qualidade, so vale com GPU
MODELO_PADRAO = "small"


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


def _detectar_device() -> tuple[str, str]:
    """Escolhe GPU se houver; senao CPU int8 (rapido e leve)."""
    try:
        import ctranslate2

        if ctranslate2.get_cuda_device_count() > 0:
            return "cuda", "float16"
    except Exception:
        pass
    return "cpu", "int8"


def resolver_modelo(modelo: str, pasta_dados: Path) -> str:
    """Se houver o modelo baixado a mao em 'modelos/<nome>', usa a pasta local
    (funciona 100% offline, sem baixar nada). Senao, devolve o nome, e o
    faster-whisper baixa do Hugging Face na primeira vez.

    Tambem aceita a variavel de ambiente TRANSCRITOR_MODELO_DIR apontando para
    uma pasta de modelo ja baixada, ou um caminho direto passado em 'modelo'.
    """
    import os

    env = os.environ.get("TRANSCRITOR_MODELO_DIR")
    if env and Path(env).exists():
        return env
    if Path(modelo).exists():  # ja e um caminho para uma pasta de modelo
        return str(modelo)
    local = pasta_dados.parent / "modelos" / modelo
    if local.exists():
        return str(local)
    return modelo


def transcrever(
    entrada: str | Path,
    pasta_dados: Path,
    modelo: str = MODELO_PADRAO,
    idioma: str = "pt",
    progresso: Optional[Callable[[str], None]] = None,
) -> List[dict]:
    """Transcreve um audio/video REAL e devolve segmentos {start,end,speaker,text}.

    Sem diarizacao (o faster-whisper sozinho nao separa falantes): todos os
    trechos saem como SPEAKER_00. A separacao por falante fica na trilha WhisperX
    (GPU) ou numa etapa pyannote opcional. Os rotulos ainda podem ser ajustados
    manualmente em dados/rotulos.json.
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:  # pragma: no cover - depende do ambiente
        raise RuntimeError(
            "faster-whisper nao esta instalado. Rode: pip install faster-whisper"
        ) from e

    device, compute = _detectar_device()
    modelo_final = resolver_modelo(modelo, pasta_dados)
    origem = "pasta local" if modelo_final != modelo else "download automatico do HF"
    if progresso:
        progresso(f"Carregando modelo '{modelo}' ({device}/{compute}) — {origem}...")
    model = WhisperModel(modelo_final, device=device, compute_type=compute)

    initial_prompt = carregar_glossario(pasta_dados)
    if progresso:
        progresso("Transcrevendo (isso pode levar alguns minutos em CPU)...")

    segmentos_iter, info = model.transcribe(
        str(entrada),
        language=idioma,
        initial_prompt=initial_prompt,
        vad_filter=True,  # ignora silencios: mais rapido e limpo
        beam_size=5,
    )

    trechos: List[dict] = []
    for seg in segmentos_iter:
        trechos.append(
            {
                "start": float(seg.start),
                "end": float(seg.end),
                "speaker": "SPEAKER_00",
                "text": (seg.text or "").strip(),
            }
        )
        if progresso:
            progresso(f"  {seg.end:6.1f}s transcrito...")
    return trechos
