#!/usr/bin/env bash
# Gera o sidecar 'transcritor-engine' [motor Python] e o nomeia com o target
# triple do Rust, como o Tauri v2 exige em externalBin. Rode na RAIZ do repo
# ou deixe o script achar a raiz. Linux/macOS.
set -euo pipefail
cd "$(dirname "$0")/../.."   # raiz do repositorio

echo ">> Instalando dependencias de build do sidecar"
python3 -m pip install --upgrade pip pyinstaller faster-whisper

echo ">> Empacotando o motor com PyInstaller [onefile]"
pyinstaller --noconfirm --clean --onefile --name transcritor-engine \
  --collect-all faster_whisper \
  --collect-all ctranslate2 \
  --collect-all av \
  --collect-all onnxruntime \
  --collect-all tokenizers \
  --collect-all huggingface_hub \
  --add-data "dados:dados" \
  engine_entry.py

TRIPLE="$(rustc -Vv | sed -n 's/^host: //p')"
DEST="app-tauri/src-tauri/binaries"
mkdir -p "$DEST"
if [ -f "dist/transcritor-engine" ]; then
  cp "dist/transcritor-engine" "$DEST/transcritor-engine-$TRIPLE"
  chmod +x "$DEST/transcritor-engine-$TRIPLE"
  echo ">> Sidecar: $DEST/transcritor-engine-$TRIPLE"
else
  echo "ERRO: dist/transcritor-engine nao encontrado" >&2
  exit 1
fi
