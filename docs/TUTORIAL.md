# Tutorial completo — Transcritor ProfAMR 2026

Do primeiro clique à ata revisada. Uso interno em matéria criminal. Funciona em
Windows, Linux e macOS, **offline após a instalação**.

---

## 1. Instalar e abrir

### Jeito mais fácil (Windows) — o executável
1. Baixe o ZIP do executável (em **Actions → último build → Artifacts**, ou onde a TI o disponibilizou).
2. **Descompacte o ZIP inteiro** numa pasta (é uma pasta, não um arquivo solto).
3. Abra a pasta `TranscritorProfAMR` e dê **duplo clique em `TranscritorProfAMR.exe`**.

> **Guarde a pasta inteira junto.** O `.exe` usa os arquivos ao lado dele; não mova só o executável.

### Jeito alternativo (qualquer sistema) — com Python
Instale o [Python](https://www.python.org/downloads/) e dê duplo clique no lançador:
`INICIAR-WINDOWS.bat`, `INICIAR-LINUX.sh` ou `INICIAR-MAC.command`. Na primeira vez
ele instala o motor e baixa o modelo (internet **só** nessa primeira vez).

---

## 2. Transcrever uma audiência
1. Clique em **“Escolher arquivo…”** e selecione o áudio/vídeo (MP4, MP3, WAV, M4A…).
2. Escolha o **modelo**: comece com `small`; para mais precisão, `medium` ou (com GPU NVIDIA) `large-v3`.
3. Clique em **“Transcrever”**. Na primeira vez o modelo é baixado (uma vez só). O rodapé mostra o progresso.
4. Clique em **“Salvar ata como…”** para guardar.

> **Tempo:** em CPU, de 1× a 3× a duração do áudio. Com GPU NVIDIA, bem mais rápido.
> Áudio limpo e bom microfone melhoram o resultado mais que qualquer modelo.

---

## 3. Dizer quem é quem
As vozes saem como `SPEAKER_00`, `SPEAKER_01`… Para virar papéis processuais, edite `dados/rotulos.json`:

```json
{
  "mapa": {
    "SPEAKER_00": "Juiz",
    "SPEAKER_01": "Ministério Público",
    "SPEAKER_02": "Defesa",
    "SPEAKER_03": "Testemunha"
  }
}
```

A ordem muda a cada audiência — confira ouvindo os primeiros segundos. Valor em branco (`""`) mantém o rótulo original.

> A separação automática de falantes tem qualidade cheia na versão **GPU NVIDIA (WhisperX)**. No motor de CPU, ajuste os papéis por este arquivo.

---

## 4. Melhorar a grafia (camada penal)

Dois arquivos, editáveis sem programar:

| Arquivo | O que faz |
|---|---|
| `dados/glossario_penal.txt` | Enviesa o modelo para a grafia certa **antes** de transcrever. Acrescente termos, comarcas, varas, nomes recorrentes. |
| `dados/correcoes.json` | Corrige erros **depois** da transcrição, de forma exata e auditável (cada troca é contada). |

Viu um erro recorrente? Acrescente em `dados/correcoes.json`:

```json
"dosemetria": "dosimetria",
"abeas corpus": "habeas corpus"
```

Na próxima transcrição já sai certo — regra fixa e previsível, sem depender de IA.

---

## 5. Revisar com LLM Local

A caixa **“Revisar com LLM local”** na janela (ou `--llm` na linha de comando).

### O que é
Um **segundo passe opcional**: depois de transcrever e aplicar a camada penal, o
texto é enviado a um **modelo de linguagem (LLM) que roda na sua própria máquina**
para revisar **ortografia, pontuação, concordância e grafia de termos e dispositivos
legais**. O programa instrui o modelo a **não resumir, não inventar e não mudar o
sentido** — só corrigir a forma.

### Por que “Local” é a palavra-chave
O texto **não vai para a nuvem**. Ele conversa apenas com o **Ollama** rodando no
seu computador, em `localhost:11434`. Nenhum trecho de depoimento sai da máquina —
é o que mantém o sigilo e a conformidade com a LGPD.

### Camada penal × LLM Local

| | Camada penal (`correcoes.json`) | Revisar com LLM Local |
|---|---|---|
| Como corrige | Regra fixa que você escreveu | “Entende” o texto e corrige sozinho |
| Previsível? | Sim — sempre a mesma troca, auditável | Não — pode variar entre execuções |
| Alcance | Só o que está na lista | Pontuação/concordância que a lista não cobre |
| Padrão | Sempre ligada | **Desligada** — você liga se quiser |

Use a camada penal como base confiável; ligue o LLM para um acabamento mais fino.
Como todo LLM, ele pode “consertar” errado — **sempre revise o resultado**.

### Como ativar (preparação, uma vez só)
1. No Transcritor, clique em **Preparar Ollama** e responda **Sim** às perguntas. O programa usa o Ollama já instalado ou baixa a versão oficial portátil [≈ 1,5 GB], inicia o Ollama e baixa o modelo `gemma3:4b` [≈ 3,3 GB]. Tudo uma única vez.
2. Ollama instalado numa pasta incomum: **Localizar ollama.exe…**.
3. Clique em Transcrever. **Não abra o `ollama.exe` diretamente**: a tela de conta que ele mostra não é usada pelo Transcritor.

Linha de comando:
```
transcritor transcrever audiencia.mp4 --llm
```

> Se o Ollama ou o modelo faltar, o programa **não quebra**: entrega o texto com a
> camada penal e **avisa** na tela e no cabeçalho da ata que a revisão não foi aplicada.
> Uma **trava** recusa a proposta do modelo quando ela muda números [artigo, data,
> valor] ou o tamanho do trecho; o cabeçalho informa quantas propostas foram recusadas.

> **Cuidado profissional.** O LLM é apoio de redação, não autoridade. Ele pode
> reformular pontuação de um jeito que muda a ênfase de um depoimento. Para material
> sensível, trate a saída como *rascunho* e confira contra o áudio.

---

## 6. Os arquivos gerados

| Arquivo | Para quê |
|---|---|
| `.txt` | A ata: cabeçalho [arquivo, hash SHA-256, motor, modelo, data] + horário + fala. |
| `.srt` | Legenda com tempos — acompanhar sincronizado com o vídeo. |
| `.json` | Dados estruturados: tempos, texto bruto do reconhecimento, texto final e marca de revisão por LLM de cada trecho. |

---

## 7. Limites e conformidade
- **Apoio de trabalho** (estudo do depoimento, minuta de voto, memoriais), **não ata oficial com fé pública** — esta requer revisão humana (Resoluções CNJ 105/2010 e 354/2020).
- **Sigilo e LGPD:** processamento local; não ligue integrações de nuvem para material sigiloso.
- **Qualidade** cai com áudio ruim, ruído e vozes sobrepostas. Bom microfone vale mais que qualquer modelo.

---

## 8. Problemas comuns

| Sintoma | O que fazer |
|---|---|
| A janela não abre / fecha na hora | No jeito com Python: falta o Python (Windows: reinstale marcando *Add to PATH*; Linux: `sudo apt install python3-tk`). |
| Demora muito | Normal em CPU. Use modelo menor (`base`/`small`) ou máquina com GPU NVIDIA. |
| Aviso “Revisão por LLM não aplicada” | Ollama ausente ou modelo não baixado. Clique em **Preparar Ollama** [detalhes em [`OLLAMA.md`](../OLLAMA.md)]. |
| A ata não indica quem fala | O motor de CPU não separa vozes; a ata sai sem atribuição de falante. A separação exige a versão GPU (WhisperX). |
| Erro ao abrir o `.exe` | Confirme que descompactou a **pasta inteira**. Se persistir, copie a mensagem para a TI. |
