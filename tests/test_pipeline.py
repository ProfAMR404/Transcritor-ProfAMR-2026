import json
import sys
import types

import pytest

from transcritor import asr, paths, pipeline


def test_demo_ponta_a_ponta(tmp_path):
    proc, rel, saidas, meta = pipeline.executar(None, paths.pasta_dados(), tmp_path, demo=True)
    assert rel.total > 10
    ata = saidas["txt"].read_text(encoding="utf-8")
    assert "Ministério Público: Excelência" in ata
    dados = json.loads(saidas["json"].read_text(encoding="utf-8"))
    assert dados["segments"][1]["texto_bruto"].startswith("Excelencia, o ministerio publico")
    assert "-->" in saidas["srt"].read_text(encoding="utf-8")


class _Seg:
    def __init__(self, start, end, text):
        self.start, self.end, self.text = start, end, text


class _Info:
    duration = 10.0


def _instalar_whisper_falso(monkeypatch, falha_cuda=False, registro=None):
    registro = registro if registro is not None else []

    class WhisperModel:
        def __init__(self, modelo, device, compute_type):
            registro.append((modelo, device, compute_type))
            self.device = device

        def transcribe(self, caminho, **kw):
            registro.append(("prompt", bool(kw.get("initial_prompt"))))

            def gerar():
                if falha_cuda and self.device == "cuda":
                    raise RuntimeError("Library cublas64_12.dll is not found")
                yield _Seg(0.0, 4.0, " O reu foi presso. ")
                yield _Seg(4.0, 5.0, "   ")
                yield _Seg(5.0, 9.5, "Artigo 33, paragrafo 4.")
            return gerar(), _Info()

    mod = types.ModuleType("faster_whisper")
    mod.WhisperModel = WhisperModel
    mod.__version__ = "falso"
    monkeypatch.setitem(sys.modules, "faster_whisper", mod)
    return registro


def test_transcricao_real_usa_modelo_escolhido_e_nao_inventa_falante(tmp_path, monkeypatch):
    reg = _instalar_whisper_falso(monkeypatch)
    monkeypatch.setenv("TRANSCRITOR_DEVICE", "cpu")
    audio = tmp_path / "aud.wav"
    audio.write_bytes(b"RIFF....fake")
    proc, rel, saidas, meta = pipeline.executar(audio, paths.pasta_dados(), tmp_path, modelo="medium")
    assert reg[0] == ("medium", "cpu", "int8")
    assert ("prompt", True) in reg
    assert [t.texto for t in proc] == ["O réu foi preso.", "art. 33, § 4º."]
    assert all(t.falante is None for t in proc)
    ata = saidas["txt"].read_text(encoding="utf-8")
    assert "Juiz" not in ata
    assert len(meta.sha256) == 64 and meta.sha256 in ata


def test_fallback_gpu_para_cpu(tmp_path, monkeypatch):
    reg = _instalar_whisper_falso(monkeypatch, falha_cuda=True)
    monkeypatch.delenv("TRANSCRITOR_DEVICE", raising=False)
    monkeypatch.setattr(asr, "_dispositivos", lambda: [("cuda", "float16"), ("cpu", "int8")])
    trechos = asr.transcrever(tmp_path / "x.wav", paths.pasta_dados(), modelo="tiny")
    assert [r[1] for r in reg if r[0] == "tiny"] == ["cuda", "cpu"]
    assert len(trechos) == 2


def test_modelo_local_ao_lado_do_programa(tmp_path, monkeypatch):
    (tmp_path / "modelos" / "small").mkdir(parents=True)
    (tmp_path / "modelos" / "small" / "model.bin").write_bytes(b"x")
    monkeypatch.setattr(paths, "pastas_modelos", lambda: [tmp_path / "modelos"])
    monkeypatch.delenv("TRANSCRITOR_MODELO_DIR", raising=False)
    assert asr.resolver_modelo("small") == str(tmp_path / "modelos" / "small")
    assert asr.resolver_modelo("large-v3-turbo").startswith("deepdml/")


def test_arquivo_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        pipeline.executar(tmp_path / "nao.mp4", paths.pasta_dados(), tmp_path)
