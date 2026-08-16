# Transcritor ProfAMR 2026

**Transcrição de audiências e depoimentos judiciais em português, 100% offline, com camada especializada em Direito Penal e Processo Penal.**

Ferramenta livre e gratuita para gabinetes, defensorias, promotorias e escritórios. O áudio **nunca sai da máquina** — requisito de sigilo e de conformidade com a LGPD.

> Cópia independente (não é *fork*), inspirada no [TecJustiça Transcribe](https://github.com/marcosmarf27/tecjustica-transcribe-cli) (MIT). Reescrita para uso próprio, com melhorias e uma **camada penal** editável. Créditos em [`CREDITOS.md`](CREDITOS.md).

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

## Instalação para uso real

O motor de transcrição (WhisperX) exige **GPU NVIDIA** (mín. 6 GB de VRAM, CUDA). Em CPU funciona, porém ~10× mais lento.

- **Linux (Ubuntu/Debian):** `bash scripts/instalar-linux.sh`
- **Windows:** via **WSL2** + `scripts/instalar-windows.ps1` (o WhisperX não roda em Windows nativo).

Depois:

```bash
transcritor transcrever audiencia.mp4          # transcrição + camada penal
transcritor transcrever audiencia.mp4 --llm    # + revisão por LLM local (Ollama)
```

Sem motor/GPU, o comando `transcrever` avisa e cai automaticamente no modo demo.

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
