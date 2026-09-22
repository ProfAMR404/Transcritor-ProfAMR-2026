<p align="center">
  <img src="docs/assets/prof_amr_logo.png" width="240" alt="Prof. AMR">
</p>

<p align="center"><sub><b>PROF. AMR</b></sub></p>

# Transcritor ProfAMR 2026

**Transcrição de audiências e depoimentos judiciais em português, 100% offline, com camada especializada em Direito Penal e Processo Penal.**

Ferramenta livre e gratuita para gabinetes, defensorias, promotorias e escritórios. O áudio **nunca sai da máquina** [requisito de sigilo e de conformidade com a LGPD]. Cópia independente inspirada no [TecJustiça Transcribe](https://github.com/marcosmarf27/tecjustica-transcribe-cli) [MIT]. Créditos em [`CREDITOS.md`](CREDITOS.md).

---

## Baixar e instalar [Windows]

1. Vá em **[Releases](../../releases)** e baixe o `TranscritorProfAMR-Windows.zip`.
2. **Descompacte a pasta inteira** [não mova só o executável].
3. Abra **`TranscritorProfAMR.exe`** com duplo clique. O atalho na Área de Trabalho é criado no primeiro uso.
4. Escolha o áudio ou vídeo da audiência, clique em transcrever, salve a ata.

Na primeira transcrição o modelo é baixado uma vez; depois o programa roda sem internet. Passo a passo completo em [`COMO-USAR.txt`](COMO-USAR.txt) e no [`tutorial`](docs/tutorial.html).

---

## O que faz

1. **Transcreve** áudio ou vídeo de audiência com o motor faster-whisper [CPU] ou WhisperX [GPU NVIDIA, com separação de falantes].
2. **Aplica a camada penal**: corrige a grafia de termos e de dispositivos de forma exata e auditável, por regras editáveis em `dados/`.
3. **Revisa [opcional]** o texto com um modelo de linguagem local [Ollama], também offline.
4. **Exporta** a ata em `.txt`, legenda `.srt` e dados `.json` com carimbos de tempo.

---

## Privacidade

O processamento é local. Nenhum trecho de depoimento sai da máquina. A revisão por modelo usa apenas o Ollama em `localhost`, nunca a nuvem. A transcrição por máquina é apoio de trabalho, não ata oficial com fé pública [a documentação audiovisual dispensa transcrição, que é faculdade do magistrado, conforme a Resolução 105/2010 do Conselho Nacional de Justiça].

---

## Rodar a partir do código [qualquer sistema]

Requer [Python](https://www.python.org/downloads/). No Linux, a janela precisa de `python3-tk`.

```
pip install ".[cpu]"
transcritor-gui
```

Links dos modelos e download manual em [`MODELOS.md`](MODELOS.md).

---

## Versão Tauri [em desenvolvimento]

A subpasta [`app-tauri/`](app-tauri/) traz uma interface desktop em Tauri v2 sobre o mesmo motor Python [sidecar], com instalador nativo. Instruções de build em [`app-tauri/README.md`](app-tauri/README.md). O aplicativo atual continua funcionando em paralelo.

---

## Licença

[MIT](LICENSE). Livre para usar, modificar e redistribuir, mantendo o aviso de copyright e os créditos.
