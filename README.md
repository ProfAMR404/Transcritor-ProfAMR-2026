<p align="center">
  <img src="docs/assets/prof_amr_logo.png" width="240" alt="Prof. AMR">
</p>

<p align="center"><sub><b>PROF. AMR</b></sub></p>

# Transcritor ProfAMR 2026

**Transcrição de audiências e depoimentos judiciais em português, 100% offline, com camada especializada em Direito Penal e Processo Penal.**

Ferramenta livre e gratuita para gabinetes, defensorias, promotorias e escritórios. O áudio **nunca sai da máquina** [requisito de sigilo e de conformidade com a LGPD]. Cópia independente inspirada no [TecJustiça Transcribe](https://github.com/marcosmarf27/tecjustica-transcribe-cli) [MIT]. Créditos em [`CREDITOS.md`](CREDITOS.md).

<p align="center"><img src="docs/assets/tela-principal.png" width="720" alt="Tela principal do Transcritor ProfAMR"></p>

---

## Baixar e instalar [Windows 10/11, 64 bits]

1. Baixe o **[`TranscritorProfAMR-Windows.zip`](../../releases/latest/download/TranscritorProfAMR-Windows.zip)** na página de **[Releases](../../releases/latest)**.
2. **Descompacte a pasta inteira** [não mova só o executável].
3. Abra **`TranscritorProfAMR.exe`** com duplo clique. O atalho na Área de Trabalho é criado no primeiro uso.
4. Clique em **Escolher arquivo…**, selecione o áudio ou vídeo da audiência, clique em **Transcrever** e salve a ata.

Na primeira transcrição o modelo Whisper escolhido é baixado uma vez [`small` ≈ 484 MB]; depois o programa roda sem internet. Para máquina sem internet, veja [`MODELOS.md`](MODELOS.md). Passo a passo em [`COMO-USAR.txt`](COMO-USAR.txt) e no [`tutorial`](docs/TUTORIAL.md).

### Revisão por modelo local [Ollama, opcional]

| Opção | Link oficial |
|---|---|
| **Portátil** [descompacte numa pasta `ollama` ao lado do `.exe`; o Transcritor inicia o Ollama sozinho] | [`ollama-windows-amd64.zip`](https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip) [≈ 1,46 GB] |
| Instalador Windows | [`OllamaSetup.exe`](https://github.com/ollama/ollama/releases/latest/download/OllamaSetup.exe) [≈ 1,57 GB] |
| macOS | [`Ollama.dmg`](https://github.com/ollama/ollama/releases/latest/download/Ollama.dmg) |
| Linux | `curl -fsSL https://ollama.com/install.sh \| sh` |

Depois, na janela do Transcritor: marque **“Revisar com modelo de linguagem local”** e clique em **“Baixar modelo”** [`gemma3:4b`, ≈ 3,3 GB, uma única vez]. Detalhes em [`OLLAMA.md`](OLLAMA.md).

---

## O que faz

1. **Transcreve** áudio ou vídeo com o faster-whisper [CPU em qualquer computador; GPU NVIDIA quando houver, com retorno automático à CPU se a GPU falhar].
2. **Aplica a camada penal**: corrige a grafia de termos jurídicos e normaliza dispositivos [`artigo 33` → `art. 33`; `parágrafo 4` → `§ 4º`; `parágrafo 10` → `§ 10`, ordinal até o nono e cardinal a partir do décimo, conforme a LC 95/1998, art. 10], por regras editáveis em `dados/`.
3. **Revisa [opcional]** com modelo de linguagem local [Ollama], com trava que recusa a proposta quando o modelo altera números ou o tamanho do trecho.
4. **Exporta** `.txt` [ata], `.srt` [legenda] e `.json` [dados], com **hash SHA-256 do arquivo de origem**, motor, modelo e data no cabeçalho; o `.json` guarda o texto bruto do reconhecimento ao lado do texto final.

### Limites conhecidos

- **Falantes:** o motor de CPU não separa vozes. A ata sai sem atribuição de falante, em vez de atribuir todas as falas a um único papel processual. A separação exige o motor WhisperX [GPU NVIDIA e token do Hugging Face; `TRANSCRITOR_MOTOR=whisperx`].
- **Velocidade:** depende do processador e do modelo. `base` é o mais rápido dos úteis, `small` é o padrão, `medium` é mais preciso e mais lento; `large-v3` só compensa com GPU.
- **Qualidade:** cai com ruído, eco e vozes sobrepostas.

---

## Privacidade

O processamento é local. Nenhum trecho de depoimento sai da máquina. A revisão por modelo usa apenas o Ollama em `localhost`, nunca a nuvem. A transcrição por máquina é apoio de trabalho, não ata oficial com fé pública [a documentação audiovisual dispensa transcrição, que é faculdade do magistrado, conforme a Resolução 105/2010 do Conselho Nacional de Justiça].

---

## Rodar a partir do código [qualquer sistema]

Requer [Python](https://www.python.org/downloads/). No Linux, a janela precisa de `python3-tk`.

```
pip install -e ".[cpu]"                # -e: usa a pasta dados/ do projeto
transcritor-gui                      # janela
transcritor transcrever audiencia.mp4 --modelo small [--llm]
transcritor ollama status
python -m pytest -q tests            # testes
```

Links dos modelos e download manual em [`MODELOS.md`](MODELOS.md).

---

## Versão Tauri [em desenvolvimento]

A subpasta [`app-tauri/`](app-tauri/) traz uma interface desktop em Tauri v2 sobre o mesmo motor Python [sidecar], com instalador nativo. Instruções de build em [`app-tauri/README.md`](app-tauri/README.md). Experimental e sem Release: o pacote oficial é o aplicativo Windows acima.

---

## Licença

[MIT](LICENSE). Livre para usar, modificar e redistribuir, mantendo o aviso de copyright e os créditos.
