"""Interface grafica desktop do Transcritor ProfAMR 2026 (Tkinter).

Janela nativa, sem navegador. Roda em Windows, macOS e Linux desde que o Python
tenha o Tkinter (no Windows/macOS ja vem embutido; no Linux: apt install python3-tk).

Iniciar:
    python -m transcritor.gui      ou, apos instalar:      transcritor-gui
"""
from __future__ import annotations

import threading
from pathlib import Path

from . import __version__, paths, pipeline

PASTA_DADOS = paths.pasta_dados()
SAIDA = paths.pasta_saida()

MODELOS = ["tiny", "base", "small", "medium", "large-v3"]


def _erro_tkinter() -> int:
    print(
        "Tkinter nao esta disponivel neste Python.\n"
        "  Windows/macOS: reinstale o Python oficial (ja inclui Tkinter).\n"
        "  Linux (Debian/Ubuntu): sudo apt install python3-tk",
    )
    return 1


def iniciar() -> int:
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, scrolledtext, ttk
    except Exception:
        return _erro_tkinter()

    app = tk.Tk()
    app.title(f"Transcritor ProfAMR 2026  ·  v{__version__}")
    app.geometry("820x640")
    app.minsize(720, 560)

    estado = {"arquivo": None, "trechos": None, "saidas": None}

    # ---- Cabecalho ---------------------------------------------------------
    topo = ttk.Frame(app, padding=12)
    topo.pack(fill="x")
    ttk.Label(
        topo, text="Transcritor de audiencias — penal, offline",
        font=("Segoe UI", 14, "bold"),
    ).pack(anchor="w")

    motor = pipeline.motor_disponivel()
    motor_txt = motor or "nenhum (instale faster-whisper) — usara a AMOSTRA demo"
    ttk.Label(topo, text=f"Motor detectado: {motor_txt}").pack(anchor="w")

    # ---- Controles ---------------------------------------------------------
    ctrl = ttk.Frame(app, padding=(12, 0))
    ctrl.pack(fill="x")

    lbl_arq = ttk.Label(ctrl, text="Nenhum arquivo selecionado", foreground="#666")

    def escolher():
        cam = filedialog.askopenfilename(
            title="Selecione o audio/video da audiencia",
            filetypes=[
                ("Audio/Video", "*.mp4 *.mp3 *.wav *.m4a *.mkv *.mov *.ogg *.flac"),
                ("Todos", "*.*"),
            ],
        )
        if cam:
            estado["arquivo"] = cam
            lbl_arq.config(text=Path(cam).name, foreground="#000")

    ttk.Button(ctrl, text="Escolher arquivo…", command=escolher).pack(side="left")
    lbl_arq.pack(side="left", padx=10)

    ttk.Label(ctrl, text="Modelo:").pack(side="left", padx=(16, 4))
    var_modelo = tk.StringVar(value="small")
    ttk.Combobox(
        ctrl, textvariable=var_modelo, values=MODELOS, width=10, state="readonly"
    ).pack(side="left")

    var_llm = tk.BooleanVar(value=False)
    ttk.Checkbutton(ctrl, text="Revisar com LLM local", variable=var_llm).pack(
        side="left", padx=12
    )

    # ---- Saida de texto ----------------------------------------------------
    corpo = ttk.Frame(app, padding=12)
    corpo.pack(fill="both", expand=True)
    txt = scrolledtext.ScrolledText(corpo, wrap="word", font=("Consolas", 10))
    txt.pack(fill="both", expand=True)

    barra = ttk.Frame(app, padding=(12, 0, 12, 12))
    barra.pack(fill="x")
    prog = ttk.Label(barra, text="Pronto.", foreground="#555")
    prog.pack(side="left")

    def log(msg: str):
        app.after(0, lambda: prog.config(text=msg))

    def _rodar():
        arquivo = estado["arquivo"]
        try:
            if motor and arquivo:
                log(f"Transcrevendo com {motor}…")
                trechos = pipeline.transcrever_entrada(
                    arquivo, PASTA_DADOS, motor, SAIDA, progresso=log
                )
                nome = Path(arquivo).stem
            else:
                if arquivo:
                    log("Sem motor instalado — usando a AMOSTRA demo.")
                else:
                    log("Nenhum arquivo — usando a AMOSTRA demo.")
                trechos = pipeline.carregar_segmentos(
                    PASTA_DADOS / "exemplo_whisperx.json"
                )
                nome = "demo_audiencia"

            log("Aplicando camada penal…")
            proc, rel, mapa = pipeline.processar(
                trechos, PASTA_DADOS, usar_llm=var_llm.get()
            )
            saidas = pipeline.escrever_saidas(proc, SAIDA, nome)
            estado["trechos"], estado["saidas"] = proc, saidas

            ata = saidas["txt"].read_text(encoding="utf-8")
            app.after(0, lambda: (txt.delete("1.0", "end"), txt.insert("1.0", ata)))
            log(f"Concluido — {rel.total} correcoes. Arquivos em: {SAIDA}")
        except Exception as e:  # mostra o erro real, sem travar
            app.after(0, lambda: messagebox.showerror("Erro na transcricao", str(e)))
            log(f"Erro: {e}")
        finally:
            app.after(0, lambda: btn.config(state="normal"))

    def transcrever():
        btn.config(state="disabled")
        threading.Thread(target=_rodar, daemon=True).start()

    def salvar_como():
        if not estado["saidas"]:
            messagebox.showinfo("Nada a salvar", "Transcreva primeiro.")
            return
        destino = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile="ata.txt",
            filetypes=[("Texto", "*.txt")],
        )
        if destino:
            Path(destino).write_text(
                txt.get("1.0", "end"), encoding="utf-8"
            )
            messagebox.showinfo("Salvo", f"Ata salva em:\n{destino}")

    acoes = ttk.Frame(app, padding=(12, 0, 12, 12))
    acoes.pack(fill="x")
    btn = ttk.Button(acoes, text="Transcrever", command=transcrever)
    btn.pack(side="left")
    ttk.Button(acoes, text="Salvar ata como…", command=salvar_como).pack(
        side="left", padx=8
    )
    ttk.Label(
        acoes,
        text="Offline · o audio nao sai da maquina",
        foreground="#2f7d5b",
    ).pack(side="right")

    app.mainloop()
    return 0


def main() -> int:
    return iniciar()


if __name__ == "__main__":
    raise SystemExit(main())
