"""Interface grafica desktop do Transcritor ProfAMR 2026 (Tkinter).

Janela nativa, sem navegador. Roda em Windows, macOS e Linux desde que o Python
tenha o Tkinter (no Windows/macOS ja vem embutido; no Linux: apt install python3-tk).

Identidade visual Prof. AMR: fundo branco, tinta navy (so texto), acento ouro
parco, titulos em Palatino (fonte de sistema no Windows), logo no topo.

Iniciar:
    python -m transcritor.gui      ou, apos instalar:      transcritor-gui
"""
from __future__ import annotations

import os
import subprocess
import sys
import threading
from pathlib import Path

from . import __version__, asr, atalho, llm_local, paths, pipeline

PASTA_DADOS = paths.pasta_dados()
SAIDA = paths.pasta_saida()

# --- Identidade visual (IDENTIDADE-VISUAL.md) ---
BG = "#FFFFFF"        # fundo branco, predomina
INK = "#1A1A2E"       # navy — so texto
HEAD = "#3D3D3D"      # grafite — titulos
META = "#5A5A5A"      # metadados
GOLD = "#D4A853"      # ouro solido (texto branco por cima)
GOLD_DEEP = "#B8860B" # ouro profundo — rotulos/links
RULE = "#E7E1D4"      # filete
SOFT = "#FAF6EC"      # fundo suave (dispositivo/codigo)
ERRO = "#9B2C2C"

# Palatino e fonte de sistema no Windows; Tk substitui por um serif se ausente.
F_TITLE = ("Palatino Linotype", 15, "bold")
F_UI = ("Segoe UI", 10)
F_UI_B = ("Segoe UI", 10, "bold")
F_KICKER = ("Segoe UI", 8, "bold")
F_MONO = ("Consolas", 10)

EXTENSOES = "*.mp4 *.mp3 *.wav *.m4a *.mkv *.mov *.ogg *.flac *.wma *.asf *.webm *.aac *.opus"


def _erro_tkinter() -> int:
    print(
        "Tkinter nao esta disponivel neste Python.\n"
        "  Windows/macOS: reinstale o Python oficial (ja inclui Tkinter).\n"
        "  Linux (Debian/Ubuntu): sudo apt install python3-tk",
    )
    return 1


def _abrir_pasta(pasta: Path) -> None:
    if sys.platform == "win32":
        os.startfile(str(pasta))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(pasta)])
    else:
        subprocess.Popen(["xdg-open", str(pasta)])


def iniciar() -> int:
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, scrolledtext, ttk
    except Exception:
        return _erro_tkinter()

    app = tk.Tk()
    app.title(f"Transcritor ProfAMR 2026  ·  v{__version__}")
    app.geometry("940x740")
    app.minsize(820, 620)
    app.configure(bg=BG)

    estado = {"arquivo": None, "saidas": None, "logo": None, "ocupado": False}

    def na_ui(func, *a):
        """Agenda 'func' na thread da interface [Tk nao e thread-safe]."""
        app.after(0, lambda: func(*a))

    def lbl(parent, text, font=F_UI, fg=INK, **kw):
        return tk.Label(parent, text=text, font=font, fg=fg, bg=BG, **kw)

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

    # ---- Marca (logo + wordmark + filete ouro) -----------------------------
    marca = tk.Frame(app, bg=BG)
    marca.pack(fill="x", padx=22, pady=(16, 0))
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
    topo.pack(fill="x", padx=22, pady=(12, 0))
    lbl(topo, "Transcritor de audiências — penal, offline",
        font=F_TITLE, fg=HEAD).pack(anchor="w")
    motor = pipeline.motor_disponivel()
    lbl(topo, f"Motor de transcrição: {motor or 'NENHUM — instale faster-whisper'}",
        fg=META if motor else ERRO).pack(anchor="w", pady=(2, 0))

    # ---- Linha 1: arquivo + modelo ----------------------------------------
    ctrl = tk.Frame(app, bg=BG)
    ctrl.pack(fill="x", padx=22, pady=(14, 0))
    lbl_arq = lbl(ctrl, "Nenhum arquivo selecionado", fg=META)

    def escolher():
        cam = filedialog.askopenfilename(
            title="Selecione o áudio/vídeo da audiência",
            filetypes=[("Áudio/Vídeo", EXTENSOES), ("Todos", "*.*")],
        )
        if cam:
            estado["arquivo"] = cam
            lbl_arq.config(text=Path(cam).name, fg=INK)

    botao(ctrl, "Escolher arquivo…", escolher).pack(side="left")
    lbl_arq.pack(side="left", padx=10)
    var_modelo = tk.StringVar(value=asr.MODELO_PADRAO)
    ttk.Combobox(ctrl, textvariable=var_modelo, values=asr.MODELOS, width=15,
                 state="readonly").pack(side="right")
    lbl(ctrl, "Modelo de transcrição:", fg=META).pack(side="right", padx=(16, 4))

    # ---- Linha 2: revisao por LLM local [Ollama] ---------------------------
    caixa = tk.Frame(app, bg=SOFT, highlightthickness=1, highlightbackground=RULE)
    caixa.pack(fill="x", padx=22, pady=(12, 0))
    l1 = tk.Frame(caixa, bg=SOFT)
    l1.pack(fill="x", padx=10, pady=(8, 2))
    var_llm = tk.BooleanVar(value=False)
    tk.Checkbutton(l1, text="Revisar com modelo de linguagem local [Ollama]",
                   variable=var_llm, font=F_UI_B, bg=SOFT, fg=INK,
                   activebackground=SOFT, selectcolor=BG,
                   command=lambda: var_llm.get() and atualizar_ollama()).pack(side="left")
    var_llm_modelo = tk.StringVar(value=llm_local.MODELO_PADRAO)
    cb_llm = ttk.Combobox(l1, textvariable=var_llm_modelo, width=18,
                          values=[m for m, _ in llm_local.MODELOS_SUGERIDOS])
    cb_llm.pack(side="right")
    tk.Label(l1, text="Modelo:", font=F_UI, fg=META, bg=SOFT).pack(side="right", padx=4)

    l2 = tk.Frame(caixa, bg=SOFT)
    l2.pack(fill="x", padx=10, pady=(2, 8))
    lbl_ollama = tk.Label(l2, text="Ollama: verificando…", font=F_UI, fg=META, bg=SOFT)
    lbl_ollama.pack(side="left")

    def perguntar(titulo: str, msg: str) -> bool:
        """askyesno chamado de thread de trabalho: executa na UI e espera."""
        pronto, resp = threading.Event(), {}

        def _p():
            resp["v"] = messagebox.askyesno(titulo, msg)
            pronto.set()
        na_ui(_p)
        pronto.wait()
        return bool(resp.get("v"))

    def atualizar_ollama(iniciar_servidor: bool = True):
        def trabalho():
            ok = llm_local.iniciar_servidor() if iniciar_servidor else llm_local.disponivel()
            exe, portatil = llm_local.localizar_executavel()
            instalados = llm_local.modelos_instalados() if ok else []
            if ok and instalados:
                tipo = " [portátil]" if portatil else ""
                txt = f"Ollama{tipo}: pronto · modelos: {', '.join(instalados)}"
                cor = INK
            elif ok:
                txt, cor = "Ollama ativo, sem modelo — clique em ‘Preparar Ollama’.", ERRO
            elif exe:
                txt = f"Ollama encontrado [{exe}] — clique em ‘Preparar Ollama’."
                cor = META
            else:
                txt, cor = "Ollama não encontrado — clique em ‘Preparar Ollama’.", META
            sugeridos = [m for m, _ in llm_local.MODELOS_SUGERIDOS]
            valores = instalados + [m for m in sugeridos if m not in instalados]

            def aplicar():
                lbl_ollama.config(text=txt, fg=cor)
                cb_llm.config(values=valores)
                if instalados and not llm_local.modelo_instalado(var_llm_modelo.get()):
                    var_llm_modelo.set(instalados[0])
            na_ui(aplicar)
        threading.Thread(target=trabalho, daemon=True).start()

    def preparar_ollama():
        """Um clique: encontra ou baixa o Ollama, inicia, baixa o modelo."""
        nome = var_llm_modelo.get().strip() or llm_local.MODELO_PADRAO
        ocupar(True)

        def trabalho():
            try:
                log("Procurando o Ollama…")
                if not llm_local.iniciar_servidor(log):
                    exe, _ = llm_local.localizar_executavel()
                    if exe is not None:
                        raise llm_local.ErroLLM(
                            f"O Ollama foi encontrado em {exe}, mas não respondeu. "
                            "Feche o Ollama pela bandeja do Windows e clique de novo "
                            "em ‘Preparar Ollama’.")
                    if not llm_local.e_windows():
                        raise llm_local.ErroLLM(llm_local.mensagem_sem_ollama())
                    if not perguntar(
                        "Baixar o Ollama",
                        "O Ollama não foi encontrado neste computador.\n\n"
                        "Baixar agora a versão oficial portátil [cerca de 1,5 GB, "
                        "uma única vez] para a pasta\n"
                        f"{paths.pasta_usuario() / 'ollama'} ?\n\n"
                        "Se o Ollama já está instalado em outro lugar, responda Não "
                        "e use ‘Localizar ollama.exe…’."):
                        log("Preparação cancelada.")
                        return
                    llm_local.baixar_ollama_portatil(log)
                    if not llm_local.iniciar_servidor(log):
                        raise llm_local.ErroLLM(
                            "O Ollama foi baixado, mas não iniciou. Veja o arquivo "
                            f"{paths.pasta_usuario() / 'transcritor.log'}.")
                if not llm_local.modelo_instalado(nome):
                    tam = dict(llm_local.MODELOS_SUGERIDOS).get(nome, "alguns GB")
                    if not perguntar(
                        "Baixar o modelo",
                        f"Baixar o modelo de revisão ‘{nome}’ [{tam}], uma única vez? "
                        "Depois a revisão roda sem internet."):
                        log("Preparação cancelada.")
                        return
                    llm_local.baixar_modelo(nome, log)
                na_ui(var_llm.set, True)
                log(f"Ollama pronto com {nome}. A revisão está ligada.")
                na_ui(messagebox.showinfo, "Ollama pronto",
                      f"Ollama pronto com o modelo {nome}.\n"
                      "A revisão por modelo local está ligada.")
            except llm_local.ErroLLM as e:
                msg = str(e)
                log("Ollama: " + msg.splitlines()[0])
                na_ui(messagebox.showerror, "Ollama", msg)
            except Exception as e:  # erro inesperado: mostra e registra
                msg = f"{e.__class__.__name__}: {e}"
                print(f"[ollama] erro inesperado: {msg}", file=sys.stderr, flush=True)
                log("Ollama: " + msg)
                na_ui(messagebox.showerror, "Ollama", msg)
            finally:
                na_ui(ocupar, False)
                atualizar_ollama(iniciar_servidor=False)
        threading.Thread(target=trabalho, daemon=True).start()

    def localizar_ollama():
        cam = filedialog.askopenfilename(
            title="Selecione o ollama.exe",
            filetypes=[("Ollama", "ollama.exe ollama"), ("Todos", "*.*")],
        )
        if not cam:
            return
        exe = Path(cam)
        if exe.name.lower() not in ("ollama.exe", "ollama"):
            messagebox.showerror("Ollama", "Selecione o arquivo ollama.exe "
                                 "[não o ‘ollama app.exe’].")
            return
        llm_local.salvar_caminho(exe)
        log(f"Ollama registrado: {exe}")
        atualizar_ollama(iniciar_servidor=True)

    btn_baixar = botao(l2, "Preparar Ollama", preparar_ollama)
    btn_baixar.pack(side="right")
    botao(l2, "Localizar ollama.exe…", localizar_ollama).pack(side="right", padx=6)

    # ---- Ata ---------------------------------------------------------------
    corpo = tk.Frame(app, bg=BG)
    corpo.pack(fill="both", expand=True, padx=22, pady=(12, 0))
    txt = scrolledtext.ScrolledText(corpo, wrap="word", font=F_MONO, height=12,
                                    bg="#FFFFFF", fg=INK, insertbackground=INK,
                                    relief="solid", bd=1,
                                    highlightthickness=1, highlightbackground=RULE)
    txt.pack(fill="both", expand=True)

    barra = tk.Frame(app, bg=BG)
    barra.pack(fill="x", padx=22, pady=(8, 0))
    pbar = ttk.Progressbar(barra, mode="indeterminate", length=160)
    prog = lbl(barra, "Pronto.", fg=META, anchor="w")
    prog.pack(side="left", fill="x", expand=True)

    def log(msg: str):
        na_ui(lambda: prog.config(text=msg))

    # ---- Acoes -------------------------------------------------------------
    acoes = tk.Frame(app, bg=BG)
    acoes.pack(fill="x", padx=22, pady=(8, 6))

    def ocupar(sim: bool):
        estado["ocupado"] = sim
        for b in (btn, btn_demo, btn_baixar):
            b.config(state="disabled" if sim else "normal")
        if sim:
            pbar.pack(side="right")
            pbar.start(12)
        else:
            pbar.stop()
            pbar.pack_forget()

    def _rodar(demo: bool):
        try:
            proc, rel, saidas, _meta = pipeline.executar(
                None if demo else estado["arquivo"], PASTA_DADOS, SAIDA,
                modelo=var_modelo.get(), usar_llm=var_llm.get(),
                modelo_llm=var_llm_modelo.get().strip() or llm_local.MODELO_PADRAO,
                progresso=log, demo=demo,
            )
            estado["saidas"] = saidas
            ata = saidas["txt"].read_text(encoding="utf-8")

            def mostrar():
                txt.delete("1.0", "end")
                txt.insert("1.0", ata)
            na_ui(mostrar)
            resumo = f"Concluído — {len(proc)} trechos, {rel.total} ajustes da camada penal"
            if rel.llm_modelo:
                resumo += f", {rel.llm_alterados} revisados pelo LLM"
            log(f"{resumo}. Arquivos em: {SAIDA}")
            if rel.avisos:
                avisos = "\n\n".join(rel.avisos)
                na_ui(messagebox.showwarning, "Aviso", avisos)
        except Exception as e:
            msg = str(e) or e.__class__.__name__
            na_ui(messagebox.showerror, "Erro na transcrição", msg)
            log(f"Erro: {msg.splitlines()[0]}")
        finally:
            na_ui(ocupar, False)

    def transcrever():
        if estado["ocupado"]:
            return
        if not motor:
            messagebox.showerror(
                "Sem motor", "Nenhum motor de transcrição instalado nesta cópia. "
                "Use o pacote do Windows [Releases] ou rode: pip install faster-whisper")
            return
        if not estado["arquivo"]:
            messagebox.showinfo("Arquivo", "Escolha primeiro o áudio ou vídeo da audiência.")
            return
        ocupar(True)
        threading.Thread(target=_rodar, args=(False,), daemon=True).start()

    def demonstrar():
        if estado["ocupado"]:
            return
        ocupar(True)
        threading.Thread(target=_rodar, args=(True,), daemon=True).start()

    def salvar_como():
        if not estado["saidas"]:
            messagebox.showinfo("Nada a salvar", "Transcreva primeiro.")
            return
        base = Path(estado["saidas"]["txt"]).stem
        destino = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile=f"{base}.txt",
            filetypes=[("Texto", "*.txt")],
        )
        if destino:
            Path(destino).write_text(txt.get("1.0", "end-1c"), encoding="utf-8")
            messagebox.showinfo("Salvo", f"Ata salva em:\n{destino}")

    def criar_atalho():
        alvo = atalho.criar_atalho_windows()
        if alvo:
            messagebox.showinfo("Atalho criado", f"Atalho criado na Área de Trabalho:\n{alvo}")
        else:
            messagebox.showinfo(
                "Atalho", "A criação de atalho está disponível na versão executável "
                "(.exe) no Windows.")

    btn = botao(acoes, "Transcrever", transcrever, primario=True)
    btn.pack(side="left")
    botao(acoes, "Salvar ata como…", salvar_como).pack(side="left", padx=8)
    botao(acoes, "Abrir pasta de saída", lambda: _abrir_pasta(SAIDA)).pack(side="left")
    btn_demo = botao(acoes, "Demonstração", demonstrar)
    btn_demo.pack(side="left", padx=8)
    botao(acoes, "Criar atalho", criar_atalho).pack(side="left")

    # Cria o atalho na Area de Trabalho no primeiro uso (Windows/.exe), silencioso.
    def _atalho_inicial():
        alvo = atalho.criar_no_primeiro_uso()
        if alvo:
            log(f"Atalho criado na Área de Trabalho: {alvo.name}")
    threading.Thread(target=_atalho_inicial, daemon=True).start()
    atualizar_ollama(iniciar_servidor=False)

    # ---- Rodape com marca reduzida -----------------------------------------
    tk.Frame(app, bg=RULE, height=1).pack(fill="x", padx=22, pady=(4, 0))
    rod = tk.Frame(app, bg=BG)
    rod.pack(fill="x", padx=22, pady=(6, 12))
    lbl(rod, "Prof. AMR · Transcritor ProfAMR 2026 · offline · o áudio não sai da "
        "máquina · a transcrição é apoio, a conferência é humana",
        fg=META, font=("Segoe UI", 8)).pack(side="left")

    app.mainloop()
    return 0


def main() -> int:
    return iniciar()


if __name__ == "__main__":
    raise SystemExit(main())
