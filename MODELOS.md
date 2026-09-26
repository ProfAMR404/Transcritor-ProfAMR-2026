# Modelos de transcrição — links e download

O aplicativo usa, por padrão, os modelos **faster-whisper (formato CTranslate2)**. Você **não precisa baixar nada à mão**: na primeira transcrição, o modelo escolhido é baixado automaticamente do Hugging Face e fica em cache. As seções abaixo servem para quem quer **baixar manualmente** (uso offline/sigiloso, sem deixar a máquina buscar na internet).

## 1. Modelos recomendados (faster-whisper / CTranslate2)

Tamanho = arquivo do modelo (`model.bin`). Escolha pelo equilíbrio velocidade × qualidade.

| Modelo | Link (Hugging Face) | Tamanho | Quando usar |
|---|---|---|---|
| `tiny` | https://huggingface.co/Systran/faster-whisper-tiny | ≈ 75 MB | Triagem muito rápida, máquina fraca |
| `base` | https://huggingface.co/Systran/faster-whisper-base | ≈ 145 MB | Rápido, qualidade razoável |
| **`small`** | https://huggingface.co/Systran/faster-whisper-small | ≈ 484 MB | **Padrão recomendado em CPU** |
| `medium` | https://huggingface.co/Systran/faster-whisper-medium | ≈ 1,5 GB | Melhor qualidade; lento em CPU |
| `large-v3` | https://huggingface.co/Systran/faster-whisper-large-v3 | ≈ 3,1 GB | Máxima qualidade; recomendado só com GPU |
| `large-v3-turbo` | https://huggingface.co/deepdml/faster-whisper-large-v3-turbo-ct2 | ≈ 1,6 GB | Quase a qualidade do large-v3, bem mais rápido |

## 2. Baixar manualmente (uso offline)

Escolha **um** dos jeitos e salve numa pasta `modelos/<nome>` **ao lado do
`TranscritorProfAMR.exe`** [ou na raiz do projeto, rodando do código; ou em
`%USERPROFILE%\TranscritorProfAMR\modelos\<nome>`]. Ex.: `modelos/small/model.bin`.
O app usa a pasta local automaticamente e não baixa nada.

**A) Pelo huggingface-cli (mais simples):**
```bash
pip install huggingface_hub
huggingface-cli download Systran/faster-whisper-small --local-dir modelos/small
```

**B) Por git + git-lfs:**
```bash
git lfs install
git clone https://huggingface.co/Systran/faster-whisper-small modelos/small
```

**C) Pelo navegador:** abra o link do modelo → aba **Files and versions** → baixe
todos os arquivos (`config.json`, `model.bin`, `tokenizer.json`, `vocabulary.txt`)
para a pasta `modelos/small`.

> Também dá para apontar qualquer pasta de modelo pela variável de ambiente
> `TRANSCRITOR_MODELO_DIR=/caminho/da/pasta`.

## 3. Alternativas de motor (do plano/benchmark)

Não estão no formato do faster-whisper — exigem outro runtime ou conversão, mas
são as opções citadas no plano:

| Uso | Modelo / projeto | Link |
|---|---|---|
| GPU + separação de falantes | WhisperX | https://github.com/m-bain/whisperX |
| Base do WhisperX | openai/whisper-large-v3 | https://huggingface.co/openai/whisper-large-v3 |
| CPU rápido, pt-BR | Parakeet pt-BR (TAGARELA, ONNX) | https://huggingface.co/alefiury/parakeet-tdt-0.6b-v3-ptBR-TAGARELA-onnx |
| Base do Parakeet | nvidia/parakeet-tdt-0.6b-v3 | https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3 |
| Fine-tune pt | freds0/whisper-large-v3-portuguese | https://huggingface.co/freds0/whisper-large-v3-portuguese |
| Fine-tune pt (leve) | pierreguillou/whisper-medium-portuguese | https://huggingface.co/pierreguillou/whisper-medium-portuguese |

> Para usar um Whisper comum (não-CTranslate2) com o faster-whisper, converta com:
> `pip install ctranslate2 transformers` e
> `ct2-transformers-converter --model openai/whisper-large-v3 --output_dir modelos/large-v3 --quantization int8`.

## 4. Revisão por modelo de linguagem [Ollama]

Os modelos de revisão [`gemma3:4b` padrão] são de outro tipo e rodam no Ollama. Links e instruções em [`OLLAMA.md`](OLLAMA.md).
