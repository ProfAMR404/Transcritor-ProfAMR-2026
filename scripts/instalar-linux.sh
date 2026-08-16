#!/usr/bin/env bash
# Instalador para Ubuntu/Debian (nativo ou WSL2).
# Nucleo + modo demo nao exigem nada disto; isto prepara o MOTOR REAL (GPU NVIDIA).
set -euo pipefail

echo ">> Transcritor ProfAMR 2026 — instalacao (Linux)"

if ! command -v python3 >/dev/null; then
  echo "Instalando python3..."; sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip
fi
if ! command -v ffmpeg >/dev/null; then
  echo "Instalando ffmpeg..."; sudo apt-get install -y ffmpeg
fi

echo ">> Criando ambiente virtual em .venv"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip

echo ">> Instalando o pacote (nucleo + camada penal)"
pip install -e .

cat <<'MSG'

>> Nucleo instalado. Teste agora, sem GPU:
     transcritor demo

>> Para TRANSCRICAO REAL (precisa de GPU NVIDIA + CUDA), edite requirements.txt,
   descomente as linhas do whisperx/torch/pyannote e rode:
     pip install -r requirements.txt
   Depois obtenha um token gratuito em https://huggingface.co e aceite os termos
   do modelo de diarizacao pyannote.

MSG
