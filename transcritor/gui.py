"""Interface grafica desktop do Transcritor ProfAMR 2026 (Tkinter).

Janela nativa, sem navegador. Roda em Windows, macOS e Linux desde que o Python
tenha o Tkinter (no Windows/macOS ja vem embutido; no Linux: apt install python3-tk).

Identidade visual Prof. AMR: fundo branco, tinta navy (so texto), acento ouro
parco, titulos em Palatino (fonte de sistema no Windows), logo no topo.

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

# --- Identidade visual (IDENTIDADE-VISUAL.md) ---
BG = "#FFFFFF"        # fundo branco, predomina
INK = "#1A1A2E"       # navy — so texto
HEAD = "#3D3D3D"      # grafite — titulos
META = "#5A5A5A"      # metadados
GOLD = "#D4A853"      # ouro solido (texto branco por cima)
GOLD_DEEP = "#B8860B" # ouro profundo — rotulos/links
RULE = "#E7E1D4"      # filete
SOFT = "#FAF6EC"      # fundo suave (dispositivo/codigo)

# Palatino e fonte de sistema no Windows; Tk substitui por um serif se ausente.
F_TITLE = ("Palatino Linotype", 15, "bold")
F_H = ("Palatino Linotype", 11, "bold")
F_UI = ("Segoe UI", 10)
F_UI_B = ("Segoe UI", 10, "bold")
F_KICKER = ("Segoe UI", 8, "bold")
F_MONO = ("Consolas", 10)


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
    app.geometry("860x680")
    app.minsize(760, 580)
    app.configure(bg=BG)

    estado = {"arquivo": None, "trechos": None, "saidas": None, "logo": None}

    def lbl(parent, text, font=F_UI, fg=INK, **kw):
        return tk.Label(parent, text=text, font=font, fg=fg, bg=BG, **kw)

    # ---- Marca (logo + wordmark + filete ouro) -----------------------------
    marca = tk.Frame(app, bg=BG)
    marca.pack(fill="x", padx=22, pady=(18, 0))
    try:
        img = tk.PhotoImage(file=str(PASTA_DADOS / "prof_amr_logo.png"))
        fator = max(1, img.height() // 52)
        img = img.subsample(fator, fator)
        estado["logo"] = img  # guarda referencia (evita coleta de lixo)
        tk.Label(marca, image=img, bg=BG).pack(side="left")
    except Exception:
        pass
    lbl(marca, "PROF. AMR", font=F_KICKER, fg=GOLD_DEEP).pack(side="left", padx=12)
    tk.Frame(app, bg=GOLD, height=3).pack(fill="x", padx=22, pady=(10, 0))

    # ---- Cabecalho ---------------------------------------------------------
    topo = tk.Frame(app, bg=BG)
    topo.pack(fill="x", padx=22, pady=(14, 0))
    lbl(topo, "Transcritor de audiências — penal, offline",
        font=F_TITLE, fg=HEAD).pack(anchor="w")
    motor = pipeline.motor_disponivel()
    motor_txt = motor or "nenhum (instale faster-whisper) — usará a AMOSTRA demo"
    lbl(topo, f"Motor detectado: {motor_txt}", fg=META).pack(anchor="w", pady=(2, 0))

    # ---- Controles ---------------------------------------------------------
    ctrl = tk.Frame(app, bg=BG)
    ctrl.pack(fill="x", padx=22, pady=(16, 0))

    def botao(parent, text, cmd, primario=False):
        if primario:
            return tk.Button(parent, text=text, command=cmd, font=F_UI_B,
                             bg=GOLD, fg="#FFFFFF", activebackground=GOLD_DEEP,
                             activeforeground="#FFFFFF", relief="flat",
                             padx=16, pady=6, cursor="hand2", bd=0)
        return tk.Button(parent, text=text, command=cmd, font=F_UI,
                         bg=BG, fg=INK, activebackground=SOFT, relief="solid",
                         bd=1, highlightbackground=RULE, padx=12, pady=5,
                         cursor="hand2")

    lbl_arq = lbl(ctrl, "Nenhum arquivo selecionado", fg=META)

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
            lbl_arq.config(text=Path(cam).name, fg=INK)

    botao(ctrl, "Escolher arquivo…", escolher).pack(side="left")
    lbl_arq.pack(side="left", padx=10)

    lbl(ctrl, "Modelo:", fg=META).pack(side="left", padx=(16, 4))
    var_modelo = tk.StringVar(value="small")
    ttk.Combobox(ctrl, textvariable=var_modelo, values=MODELOS, width=10,
                 state="readonly").pack(side="left")

    var_llm = tk.BooleanVar(value=False)
    tk.Checkbutton(ctrl, text="Revisar com LLM local", variable=var_llm,
                   font=F_UI, bg=BG, fg=INK, activebackground=BG,
                   selectcolor=BG).pack(side="left", padx=12)

    # ---- Saida de texto (ata) ----------------------------------------------
    corpo = tk.Frame(app, bg=BG)
    corpo.pack(fill="both", expand=True, padx=22, pady=(14, 0))
    txt = scrolledtext.ScrolledText(corpo, wrap="word", font=F_MONO,
                                    bg="#FFFFFF", fg=INK, insertbackground=INK,
                                    relief="solid", bd=1,
                                    highlightthickness=1, highlightbackground=RULE)
    txt.pack(fill="both", expand=True)

    barra = tk.Frame(app, bg=BG)
    barra.pack(fill="x", padx=22, pady=(8, 0))
    prog = lbl(barra, "Pronto.", fg=META)
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
                log("Sem motor/arquivo — usando a AMOSTRA demo.")
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
        except Exception as e:
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
            defaultextension=".txt", initialfile="ata.txt",
            filetypes=[("Texto", "*.txt")],
        )
        if destino:
            Path(destino).write_text(txt.get("1.0", "end"), encoding="utf-8")
            messagebox.showinfo("Salvo", f"Ata salva em:\n{destino}")

    acoes = tk.Frame(app, bg=BG)
    acoes.pack(fill="x", padx=22, pady=(8, 6))
    btn = botao(acoes, "Transcrever", transcrever, primario=True)
    btn.pack(side="left")
    botao(acoes, "Salvar ata como…", salvar_como).pack(side="left", padx=8)
    lbl(acoes, "Offline · o áudio não sai da máquina", fg=GOLD_DEEP,
        font=F_UI).pack(side="right")

    # ---- Rodape com marca reduzida -----------------------------------------
    tk.Frame(app, bg=RULE, height=1).pack(fill="x", padx=22, pady=(4, 0))
    rod = tk.Frame(app, bg=BG)
    rod.pack(fill="x", padx=22, pady=(6, 12))
    lbl(rod, "Prof. AMR · Transcritor ProfAMR 2026 · uso interno, matéria criminal",
        fg=META, font=("Segoe UI", 8)).pack(side="left")

    app.mainloop()
    return 0


def main() -> int:
    return iniciar()


if __name__ == "__main__":
    raise SystemExit(main())
