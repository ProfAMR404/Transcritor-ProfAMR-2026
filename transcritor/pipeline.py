"""Orquestra a transcricao: motor de ASR -> camada penal -> [LLM local] -> saidas.

Motores:
  - faster-whisper [padrao]: CPU ou GPU, sem separacao de falantes;
  - whisperx [opcional, GPU NVIDIA]: com separacao de falantes [--diarize];
  - demo: amostra ja no formato WhisperX [dados/exemplo_whisperx.json].

Cada saida registra o hash SHA-256 do arquivo de origem, o motor, o modelo e a
data, e o JSON guarda o texto bruto do ASR ao lado do texto final: toda
alteracao feita pela camada penal ou pelo LLM fica rastreavel.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

from . import __version__, llm_local, rotulos, textos
from .pos_penal import RelatorioCorrecao, carregar_correcoes, processar_texto

Progresso = Optional[Callable[[str], None]]


@dataclass
class Trecho:
    inicio: float
    fim: float
    falante: Optional[str]
    texto: str
    texto_bruto: str = ""
    revisado_llm: bool = False


@dataclass
class Relatorio:
    penal: RelatorioCorrecao = field(default_factory=RelatorioCorrecao)
    mapa_falantes: Dict[str, str] = field(default_factory=dict)
    llm_modelo: Optional[str] = None
    llm_alterados: int = 0
    llm_recusados: int = 0
    avisos: List[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.penal.total


@dataclass
class Metadados:
    arquivo: str = ""
    sha256: str = ""
    motor: str = ""
    modelo: str = ""
    data: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    versao: str = __version__


def sha256_arquivo(caminho: str | Path, bloco: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for parte in iter(lambda: f.read(bloco), b""):
            h.update(parte)
    return h.hexdigest()


def carregar_segmentos(caminho_json: str | Path) -> List[Trecho]:
    dados = json.loads(Path(caminho_json).read_text(encoding="utf-8"))
    return [
        Trecho(
            inicio=float(s.get("start", 0.0)),
            fim=float(s.get("end", 0.0)),
            falante=s.get("speaker"),
            texto=(s.get("text") or "").strip(),
        )
        for s in dados.get("segments", [])
    ]


def motor_disponivel() -> str | None:
    """Motor de ASR a usar. None => nenhum instalado.

    faster-whisper e o padrao [roda em qualquer desktop]. O WhisperX so e usado
    quando pedido por TRANSCRITOR_MOTOR=whisperx, porque exige GPU e token do
    Hugging Face para separar falantes.
    """
    from . import asr

    pedido = os.environ.get("TRANSCRITOR_MOTOR", "").strip().lower()
    if pedido == "whisperx" and shutil.which("whisperx"):
        return "whisperx"
    if asr.disponivel():
        return "faster-whisper"
    if shutil.which("whisperx"):
        return "whisperx"
    return None


def transcrever_entrada(
    entrada: str | Path,
    pasta_dados: Path,
    motor: str,
    saida_dir: Path,
    modelo: str = "small",
    progresso: Progresso = None,
) -> List[Trecho]:
    """Transcreve com o motor indicado e devolve os trechos brutos."""
    if motor == "faster-whisper":
        from . import asr

        brutos = asr.transcrever(entrada, pasta_dados, modelo=modelo, progresso=progresso)
        return [Trecho(d["start"], d["end"], d["speaker"], d["text"]) for d in brutos]
    if motor == "whisperx":
        saida_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["whisperx", str(entrada), "--model", modelo, "--language", "pt",
             "--diarize", "--output_format", "json", "--output_dir", str(saida_dir)],
            check=True,
        )
        return carregar_segmentos(saida_dir / (Path(entrada).stem + ".json"))
    raise RuntimeError(f"motor desconhecido: {motor}")


def processar(
    trechos: List[Trecho],
    pasta_dados: Path,
    usar_llm: bool = False,
    modelo_llm: str = llm_local.MODELO_PADRAO,
    progresso: Progresso = None,
) -> tuple[List[Trecho], Relatorio]:
    """Camada penal deterministica e, se pedido, revisao por LLM local."""
    avisar = progresso or (lambda _m: None)
    correcoes = carregar_correcoes(pasta_dados / "correcoes.json")
    rel = Relatorio()
    # Mapa de papeis so faz sentido quando o motor separou falantes.
    if any(t.falante for t in trechos):
        rel.mapa_falantes = rotulos.carregar_mapa(pasta_dados / "rotulos.json")

    llm_ativo = False
    if usar_llm:
        try:
            llm_local.preparar(modelo_llm, progresso)
            llm_ativo = True
            rel.llm_modelo = modelo_llm
        except llm_local.ErroLLM as e:
            rel.avisos.append(f"Revisão por LLM não aplicada: {e}")

    saida: List[Trecho] = []
    total = len(trechos)
    for i, t in enumerate(trechos, 1):
        bruto = t.texto_bruto or t.texto
        texto = processar_texto(t.texto, correcoes, rel.penal)
        revisado = False
        if llm_ativo:
            avisar(f"Revisando com {modelo_llm}… {i}/{total}")
            try:
                proposta = llm_local.revisar(texto, modelo=modelo_llm)
            except llm_local.ErroLLM as e:
                rel.avisos.append(f"Revisão por LLM interrompida no trecho {i}: {e}")
                llm_ativo = False
                proposta = texto
            if proposta != texto:
                if llm_local.revisao_aceitavel(texto, proposta):
                    texto, revisado = proposta, True
                    rel.llm_alterados += 1
                else:
                    rel.llm_recusados += 1
        falante = rotulos.aplicar(t.falante, rel.mapa_falantes) if t.falante else None
        saida.append(Trecho(t.inicio, t.fim, falante, texto, bruto, revisado))
    return saida, rel


def _fmt_ts(seg: float, sep: str = ",") -> str:
    total_ms = int(round(seg * 1000))
    h, resto = divmod(total_ms, 3_600_000)
    m, resto = divmod(resto, 60_000)
    s, ms = divmod(resto, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def linha_ata(t: Trecho) -> str:
    ts = _fmt_ts(t.inicio)[:8]
    return f"[{ts}] {t.falante}: {t.texto}" if t.falante else f"[{ts}] {t.texto}"


def cabecalho_ata(meta: Metadados, rel: Relatorio) -> str:
    linhas = [
        textos.AVISO_ATA,
        f"Arquivo de origem: {meta.arquivo}",
        f"SHA-256 do arquivo: {meta.sha256}" if meta.sha256 else "",
        f"Motor: {meta.motor} · modelo: {meta.modelo} · Transcritor ProfAMR v{meta.versao}",
        f"Gerado em: {meta.data}",
        f"Camada penal: {rel.total} ajuste(s) de grafia",
    ]
    if rel.llm_modelo:
        linhas.append(
            f"Revisão por LLM local ({rel.llm_modelo}): {rel.llm_alterados} trecho(s) "
            f"alterado(s), {rel.llm_recusados} proposta(s) recusada(s) pela trava"
        )
    if not rel.mapa_falantes and meta.motor == "faster-whisper":
        linhas.append("Falantes: não identificados [o motor não separa vozes]")
    linhas += rel.avisos
    return "\n".join(l for l in linhas if l) + "\n" + SEPARADOR


SEPARADOR = "=" * 72


def separar_corpo(ata: str) -> str:
    """Devolve so as falas da ata, sem o cabecalho tecnico [para colar em peca]."""
    antes, sep, depois = ata.partition(SEPARADOR)
    return (depois if sep else antes).strip()


def escrever_saidas(
    trechos: List[Trecho],
    destino: Path,
    nome: str,
    meta: Optional[Metadados] = None,
    rel: Optional[Relatorio] = None,
) -> Dict[str, Path]:
    meta = meta or Metadados()
    rel = rel or Relatorio()
    destino.mkdir(parents=True, exist_ok=True)
    p_txt = destino / f"{nome}.txt"
    p_srt = destino / f"{nome}.srt"
    p_json = destino / f"{nome}.json"

    corpo = "\n\n".join(linha_ata(t) for t in trechos)
    p_txt.write_text(cabecalho_ata(meta, rel) + "\n\n" + corpo + "\n", encoding="utf-8")

    srt = []
    for i, t in enumerate(trechos, 1):
        fala = f"{t.falante}: {t.texto}" if t.falante else t.texto
        srt.append(f"{i}\n{_fmt_ts(t.inicio)} --> {_fmt_ts(t.fim)}\n{fala}\n")
    p_srt.write_text("\n".join(srt), encoding="utf-8")

    p_json.write_text(
        json.dumps(
            {
                "metadados": asdict(meta),
                "relatorio": {
                    "camada_penal": rel.penal.ocorrencias,
                    "mapa_falantes": rel.mapa_falantes,
                    "llm_modelo": rel.llm_modelo,
                    "llm_alterados": rel.llm_alterados,
                    "llm_recusados": rel.llm_recusados,
                    "avisos": rel.avisos,
                },
                "segments": [asdict(t) for t in trechos],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return {"txt": p_txt, "srt": p_srt, "json": p_json}


def executar(
    entrada: Optional[str | Path],
    pasta_dados: Path,
    pasta_saida: Path,
    modelo: str = "small",
    usar_llm: bool = False,
    modelo_llm: str = llm_local.MODELO_PADRAO,
    progresso: Progresso = None,
    demo: bool = False,
) -> tuple[List[Trecho], Relatorio, Dict[str, Path], Metadados]:
    """Fluxo completo usado pela GUI, pela CLI e pelo motor JSON do Tauri."""
    avisar = progresso or (lambda _m: None)
    if demo:
        meta = Metadados(arquivo="amostra embutida [demo]", motor="demo", modelo="-")
        trechos = carregar_segmentos(pasta_dados / "exemplo_whisperx.json")
        nome = "demo_audiencia"
    else:
        if entrada is None or not Path(entrada).is_file():
            raise FileNotFoundError(f"arquivo não encontrado: {entrada}")
        motor = motor_disponivel()
        if not motor:
            raise RuntimeError(
                "Nenhum motor de transcrição instalado. Rode: pip install faster-whisper"
            )
        avisar("Calculando o hash SHA-256 do arquivo…")
        meta = Metadados(arquivo=Path(entrada).name, sha256=sha256_arquivo(entrada),
                         motor=motor, modelo=modelo)
        trechos = transcrever_entrada(entrada, pasta_dados, motor, pasta_saida,
                                      modelo=modelo, progresso=progresso)
        if not trechos:
            raise RuntimeError(
                "Nenhuma fala reconhecida no arquivo. Verifique se o áudio tem voz "
                "audível e se o arquivo não está corrompido."
            )
        nome = Path(entrada).stem
    avisar("Aplicando a camada penal…")
    proc, rel = processar(trechos, pasta_dados, usar_llm, modelo_llm, progresso)
    saidas = escrever_saidas(proc, pasta_saida, nome, meta, rel)
    return proc, rel, saidas, meta
