# Transcritor ProfAMR 2026

**Transcrição de audiências e depoimentos judiciais em português, 100% offline, com camada especializada em Direito Penal e Processo Penal.**

Ferramenta livre e gratuita para gabinetes, defensorias, promotorias e escritórios. O áudio **nunca sai da máquina** — requisito de sigilo e de conformidade com a LGPD.

> Cópia independente (não é *fork*), inspirada no [TecJustiça Transcribe](https://github.com/marcosmarf27/tecjustica-transcribe-cli) (MIT). Reescrita para uso próprio, com melhorias e uma **camada penal** editável. Créditos em [`CREDITOS.md`](CREDITOS.md).

---

## ▶ Usar no desktop, sem programar

1. Botão verde **Code → Download ZIP** e descompacte a pasta.
2. **Duplo clique** no lançador do seu sistema:
   - **Windows:** `INICIAR-WINDOWS.bat`
   - **Linux:** `INICIAR-LINUX.sh`
   - **macOS:** `INICIAR-MAC.command`
3. Na janela: **Escolher arquivo… → Transcrever → Salvar ata como…**

Na primeira vez ele instala o motor e baixa o modelo (precisa de internet **só** nessa primeira vez); depois roda offline. Requisito: ter o [Python](https://www.python.org/downloads/) instalado (no Windows, marque *Add Python to PATH*; no Linux, `sudo apt install python3-tk`). Passo a passo completo em [`COMO-USAR.txt`](COMO-USAR.txt).

---

## O que faz

1. **Transcreve** áudio/vídeo de audiência (MP4/MP3/WAV) com **WhisperX** (modelo `large-v3`).
2. **Separa os falantes** (diarização) e os renomeia para papéis processuais — *Juiz*, *Ministério Público*, *Defesa*, *Testemunha*.
3. **Aplica a camada penal**: corrige a grafia de termos e dispositivos (`artigo 33` → `art. 33`, `abeas corpus` → `habeas corpus`, `dosemetria` → `dosimetria`), de forma **determinística e auditável** — cada correção é contada e registrada.
4. **(Opcional)** Revisa o texto com um **LLM local** (Ollama), também offline.
5. **Exporta** ata em `.txt`, legendas `.srt` e dados `.json` com carimbos de tempo.

### Sobre a métrica
Transcrição se mede por **WER** (taxa de erro por palavra — quanto menor, melhor), não por F1. O "F1" faz sentido na etapa de **análise** do depoimento (extração de teses, entidades, contradições), no roteiro futuro. Ver o [plano/benchmark](docs/GUIA-ASSESSORIA.md).

---

## Experimente em 30 segundos (sem GPU, sem áudio)

O modo **demo** emula todo o pipeline sobre uma amostra embutida:

```bash
python3 -m transcritor.cli demo
```

Ele mostra o relatório de correções, renomeia os falantes e gera os arquivos em `saida/`. É a melhor forma de entender o que a ferramenta entrega antes de instalar o motor pesado.

---

## Aplicativo desktop (janela, roda em qualquer máquina)

Interface gráfica nativa (Tkinter): escolher arquivo → transcrever → salvar ata.

```bash
pip install ".[cpu]"      # instala o motor de CPU (faster-whisper)
transcritor-gui           # abre a janela
```

O motor de **CPU (faster-whisper)** roda em **qualquer desktop, sem GPU** — usa CUDA automaticamente se houver placa NVIDIA. Modelos: `tiny`/`base`/`small` (rápidos) até `large-v3` (só compensa com GPU). No Linux, a janela exige `sudo apt install python3-tk`.

### Gerar um executável (`.exe`) para a assessoria

Empacota tudo num aplicativo que a equipe abre com duplo clique, sem instalar Python:

- **Windows:** `powershell -ExecutionPolicy Bypass -File scripts/build-desktop.ps1` → `dist\TranscritorProfAMR\TranscritorProfAMR.exe`
- **Linux/macOS:** `bash scripts/build-desktop.sh` → `dist/TranscritorProfAMR/`

O modelo de transcrição é baixado no primeiro uso e fica em cache (offline depois).

## Linha de comando

```bash
transcritor demo                            # emula com a amostra (sem GPU)
transcritor transcrever audiencia.mp4       # transcrição real + camada penal
transcritor transcrever audiencia.mp4 --llm # + revisão por LLM local (Ollama)
```

Sem motor instalado, o comando avisa e cai automaticamente no modo demo.

### Alternativa GPU com diarização de falantes

Para separar automaticamente Juiz/MP/Defesa/Testemunha, use a trilha **WhisperX** numa máquina com **GPU NVIDIA** (`scripts/instalar-linux.sh`, ou Windows via WSL2 com `scripts/instalar-windows.ps1`). O motor de CPU transcreve com carimbos de tempo, mas não separa falantes por conta própria — os rótulos podem ser ajustados em `dados/rotulos.json`.

---

## A camada penal é sua

Três arquivos em `dados/` controlam a qualidade jurídica — **edite à vontade**, sem tocar no código:

| Arquivo | Para quê |
|---|---|
| `dados/glossario_penal.txt` | Enviesa o WhisperX para a grafia certa **antes** de transcrever (maior ganho por menor esforço). Acrescente nomes de comarcas, varas, juízes, promotores. |
| `dados/correcoes.json` | Mapa de correções aplicadas **depois** da transcrição. Adicione os erros que você vir na prática. |
| `dados/rotulos.json` | Mapeia `SPEAKER_00…` para os papéis da audiência. Ajuste a cada sessão. |

---

## Privacidade e conformidade

- **Offline após a instalação.** Nenhum depoimento é enviado à nuvem.
- A revisão por LLM usa **apenas** um Ollama em `localhost` — nunca uma API externa.
- **Uso como apoio interno** (estudo do depoimento, minuta de voto, memoriais). A ata oficial com fé pública ainda requer revisão humana (Resoluções CNJ 105/2010 e 354/2020).

---

## Licença

[MIT](LICENSE). Livre para usar, modificar e redistribuir, mantendo o aviso de copyright e os créditos.
