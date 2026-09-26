import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from transcritor import llm_local, paths, pipeline


class _Ollama(BaseHTTPRequestHandler):
    modelos = ["gemma3:4b"]
    resposta = None  # funcao texto -> texto

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        dados = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self):
        if self.path == "/api/version":
            return self._json({"version": "0.0-teste"})
        if self.path == "/api/tags":
            return self._json({"models": [{"name": m} for m in self.modelos]})
        self._json({"error": "404"}, 404)

    def do_POST(self):
        corpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path == "/api/chat":
            if corpo["model"] not in self.modelos:
                return self._json({"error": f"model '{corpo['model']}' not found"}, 404)
            texto = corpo["messages"][-1]["content"]
            return self._json({"message": {"role": "assistant", "content": type(self).resposta(texto)}})
        if self.path == "/api/pull":
            self.send_response(200)
            self.end_headers()
            for ev in ({"status": "pulling manifest"},
                       {"status": "pulling x", "total": 100, "completed": 50},
                       {"status": "success"}):
                self.wfile.write((json.dumps(ev) + "\n").encode())
            type(self).modelos.append(corpo["model"])
            return None
        self._json({"error": "404"}, 404)


@pytest.fixture
def ollama(monkeypatch):
    _Ollama.modelos = ["gemma3:4b"]
    _Ollama.resposta = staticmethod(lambda t: t)
    srv = HTTPServer(("127.0.0.1", 0), _Ollama)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    monkeypatch.setenv("OLLAMA_HOST", f"127.0.0.1:{srv.server_address[1]}")
    yield _Ollama
    srv.shutdown()


def test_sem_ollama_gera_aviso_e_nao_quebra(tmp_path, monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "127.0.0.1:9")
    monkeypatch.setattr(llm_local, "localizar_executavel", lambda: (None, False))
    proc, rel, _s, _m = pipeline.executar(None, paths.pasta_dados(), tmp_path, demo=True, usar_llm=True)
    assert rel.llm_modelo is None
    assert rel.avisos and "Ollama" in rel.avisos[0]
    assert "OllamaSetup.exe" in rel.avisos[0]


def test_modelo_ausente_avisa(ollama, tmp_path):
    _p, rel, _s, _m = pipeline.executar(None, paths.pasta_dados(), tmp_path, demo=True,
                                        usar_llm=True, modelo_llm="llama9:70b")
    assert any("não está instalado" in a for a in rel.avisos)


def test_revisao_aceita_e_recusa(ollama, tmp_path):
    def resposta(t):
        if "Declaro aberta" in t:
            return "Texto corrigido: " + t.replace("julgamento", "julgamento,")
        if "art. 33" in t:
            return t.replace("33", "35")  # troca numero -> trava recusa
        return t
    ollama.resposta = staticmethod(resposta)
    proc, rel, saidas, _m = pipeline.executar(None, paths.pasta_dados(), tmp_path, demo=True,
                                              usar_llm=True, modelo_llm="gemma3:4b")
    assert rel.llm_alterados == 1 and rel.llm_recusados == 1
    assert proc[0].revisado_llm and proc[0].texto.startswith("Declaro aberta")
    assert "art. 33" in proc[2].texto
    assert "gemma3:4b" in saidas["txt"].read_text(encoding="utf-8")


def test_baixar_modelo(ollama):
    msgs = []
    llm_local.baixar_modelo("gemma3:12b", msgs.append)
    assert any("50%" in m for m in msgs)
    assert llm_local.modelo_instalado("gemma3:12b")


def test_mesmo_modelo_latest(ollama):
    ollama.modelos = ["gemma3:latest"]
    assert llm_local.modelo_instalado("gemma3")


def test_trava():
    assert llm_local.revisao_aceitavel("o réu foi preso em 2024", "O réu foi preso em 2024.")
    assert not llm_local.revisao_aceitavel("art. 33", "art. 35")
    assert not llm_local.revisao_aceitavel("uma frase curta aqui", "uma frase muito mais longa inventada pelo modelo aqui")
    assert not llm_local.revisao_aceitavel("texto", "")


def test_portatil_tem_prioridade(tmp_path, monkeypatch):
    import sys
    exe = tmp_path / "ollama" / ("ollama.exe" if sys.platform == "win32" else "ollama")
    exe.parent.mkdir()
    exe.write_bytes(b"")
    monkeypatch.setattr(paths, "pastas_ollama", lambda: [tmp_path / "ollama"])
    assert llm_local.localizar_executavel() == (exe, True)


def test_ignora_proxy_do_sistema(ollama, monkeypatch):
    # Rede institucional: proxy configurado no sistema nao pode esconder o Ollama local.
    monkeypatch.setenv("http_proxy", "http://10.255.255.1:3128")
    monkeypatch.setenv("HTTP_PROXY", "http://10.255.255.1:3128")
    monkeypatch.setenv("no_proxy", "")
    assert llm_local.disponivel(timeout=3)
    assert llm_local.modelos_instalados() == ["gemma3:4b"]


@pytest.mark.parametrize("host,esperado", [
    ("", "http://127.0.0.1:11434"),
    ("0.0.0.0", "http://127.0.0.1:11434"),
    ("0.0.0.0:11500", "http://127.0.0.1:11500"),
    ("http://0.0.0.0:11434", "http://127.0.0.1:11434"),
    ("[::]:11434", "http://127.0.0.1:11434"),
    ("localhost", "http://localhost:11434"),
    ("192.168.0.5:8080", "http://192.168.0.5:8080"),
])
def test_url_base(monkeypatch, host, esperado):
    monkeypatch.setenv("OLLAMA_HOST", host)
    assert llm_local.url_base() == esperado


def test_caminho_escolhido_pelo_usuario(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "pasta_usuario", lambda: tmp_path)
    exe = tmp_path / "x" / "ollama.exe"
    exe.parent.mkdir()
    exe.write_bytes(b"")
    llm_local.salvar_caminho(exe)
    assert llm_local.localizar_executavel() == (exe, False)
    exe.unlink()  # caminho salvo que sumiu nao pode ser usado
    assert llm_local.caminho_salvo() is None


def test_baixar_ollama_portatil(tmp_path, monkeypatch):
    import io
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("ollama.exe", b"MZ")
        z.writestr("lib/ollama/x.dll", b"x")
    dados = buf.getvalue()

    class Zip(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Length", str(len(dados)))
            self.end_headers()
            self.wfile.write(dados)

    srv = HTTPServer(("127.0.0.1", 0), Zip)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    monkeypatch.setattr(paths, "pasta_usuario", lambda: tmp_path)
    monkeypatch.setattr(paths, "pastas_ollama", lambda: [tmp_path / "ollama"])
    monkeypatch.setitem(llm_local.LINKS_DOWNLOAD, "windows_portatil",
                        f"http://127.0.0.1:{srv.server_address[1]}/o.zip")
    monkeypatch.setattr(llm_local, "e_windows", lambda: True)
    msgs = []
    exe = llm_local.baixar_ollama_portatil(msgs.append)
    srv.shutdown()
    assert exe == tmp_path / "ollama" / "ollama.exe" and exe.read_bytes() == b"MZ"
    assert any("100%" in m for m in msgs)
    assert not list(tmp_path.glob("*.parcial"))
    assert llm_local.localizar_executavel() == (exe, True)


@pytest.mark.skipif(__import__("sys").platform != "win32", reason="so no Windows")
def test_windows_instalado_em_program_files(tmp_path, monkeypatch):
    exe = tmp_path / "Ollama" / "ollama.exe"
    exe.parent.mkdir()
    exe.write_bytes(b"")
    monkeypatch.setattr(paths, "pastas_ollama", lambda: [tmp_path / "nada"])
    monkeypatch.setattr(paths, "pasta_usuario", lambda: tmp_path / "u")
    monkeypatch.setattr(llm_local.shutil, "which", lambda _n: None)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "vazio"))
    monkeypatch.setenv("ProgramFiles", str(tmp_path))
    assert llm_local.localizar_executavel()[0] == exe
