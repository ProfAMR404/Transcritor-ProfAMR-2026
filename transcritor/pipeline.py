"""Orquestra a transcricao: motor de ASR -> camada penal -> saidas.

Dois modos:
  - real: chama o motor WhisperX (via TecJustica CLI ou whisperx instalado) para
    gerar a transcricao bruta a partir de um MP4/MP3/WAV;
  - demo/emulado: le uma amostra ja no formato WhisperX (dados/exemplo_whisperx.json),
    sem GPU, para demonstrar a camada penal ponta a ponta.

Em ambos os modos, o pos-processamento penal e identico.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from . import llm_local, rotulos
from .pos_penal import (
    RelatorioCorrecao,
    carregar_correcoes,
    processar_texto,
)


@dataclass
class Trecho:
    inicio: float
    fim: float
    falante: str
    texto: str


def carregar_segmentos(caminho_json: str | Path) -> List[Trecho]:
    dados = json.loads(Path(caminho_json).read_text(encoding="utf-8"))
    return [
        Trecho(
            inicio=float(s.get("start", 0.0)),
            fim=float(s.get("end", 0.0)),
            falante=s.get("speaker", "SPEAKER_00"),
            texto=(s.get("text") or "").strip(),
        )
        for s in dados.get("segments", [])
    ]


def motor_disponivel() -> str | None:
    """Detecta um motor de ASR real instalado. None => usar modo demo.

    Ordem de preferencia: motores de linha de comando com diarizacao
    (TecJustica/WhisperX, tipicamente GPU) e, por fim, o faster-whisper
    (Python puro, roda em CPU em qualquer desktop).
    """
    for cmd in ("tecjustica-transcribe", "whisperx"):
        if shutil.which(cmd):
            return cmd
    from . import asr

    if asr.disponivel():
        return "faster-whisper"
    return None


def transcrever_entrada(
    entrada: str | Path,
    pasta_dados: Path,
    motor: str,
    saida_dir: Path,
    progresso=None,
) -> List[Trecho]:
    """Transcreve com o motor detectado e devolve os trechos brutos."""
    if motor == "faster-whisper":
        from . import asr

        brutos = asr.transcrever(entrada, pasta_dados, progresso=progresso)
        return [
            Trecho(d["start"], d["end"], d["speaker"], d["text"]) for d in brutos
        ]
    saida_json = saida_dir / (Path(entrada).stem + ".json")
    saida_json.parent.mkdir(parents=True, exist_ok=True)
    transcrever_real(str(entrada), saida_json, motor)
    return carregar_segmentos(saida_json)


def transcrever_real(entrada: str, saida_json: Path, motor: str) -> Path:
    """Chama o motor real para produzir o JSON word-level. (Requer GPU NVIDIA.)"""
    if motor == "tecjustica-transcribe":
        subprocess.run(["tecjustica-transcribe", "transcrever", entrada], check=True)
    else:  # whisperx
        subprocess.run(
            ["whisperx", entrada, "--language", "pt", "--diarize",
             "--output_format", "json", "--output_dir", str(saida_json.parent)],
            check=True,
        )
    return saida_json


def _fmt_ts(seg: float) -> str:
    h = int(seg // 3600)
    m = int((seg % 3600) // 60)
    s = int(seg % 60)
    ms = int((seg - int(seg)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def processar(
    trechos: List[Trecho],
    pasta_dados: Path,
    usar_llm: bool = False,
    modelo_llm: str = "llama3.1",
) -> tuple[List[Trecho], RelatorioCorrecao, Dict[str, str]]:
    correcoes = carregar_correcoes(pasta_dados / "correcoes.json")
    mapa_rot = rotulos.carregar_mapa(pasta_dados / "rotulos.json")
    rel = RelatorioCorrecao()

    llm_ok = usar_llm and llm_local.disponivel()
    saida: List[Trecho] = []
    for t in trechos:
        texto = processar_texto(t.texto, correcoes, rel)
        if llm_ok:
            texto = llm_local.revisar(texto, modelo=modelo_llm)
        saida.append(
            Trecho(t.inicio, t.fim, rotulos.aplicar(t.falante, mapa_rot), texto)
        )
    return saida, rel, mapa_rot


def escrever_saidas(trechos: List[Trecho], destino: Path, nome: str) -> Dict[str, Path]:
    destino.mkdir(parents=True, exist_ok=True)
    p_txt = destino / f"{nome}.txt"
    p_srt = destino / f"{nome}.srt"
    p_json = destino / f"{nome}.json"

    linhas_txt = [
        f"[{_fmt_ts(t.inicio)}] {t.falante}: {t.texto}" for t in trechos
    ]
    p_txt.write_text("\n\n".join(linhas_txt) + "\n", encoding="utf-8")

    srt = []
    for i, t in enumerate(trechos, 1):
        srt.append(
            f"{i}\n{_fmt_ts(t.inicio)} --> {_fmt_ts(t.fim)}\n"
            f"{t.falante}: {t.texto}\n"
        )
    p_srt.write_text("\n".join(srt), encoding="utf-8")

    p_json.write_text(
        json.dumps(
            {"segments": [t.__dict__ for t in trechos]},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return {"txt": p_txt, "srt": p_srt, "json": p_json}
