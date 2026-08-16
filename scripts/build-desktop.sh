#!/usr/bin/env bash
# Gera um executavel desktop (binario unico) para Linux/macOS com PyInstaller.
# Requer: python3-tk (Linux) e as deps do projeto instaladas.
set -euo pipefail
cd "$(dirname "$0")/.."

echo ">> Instalando dependencias de build e execucao"
python3 -m pip install --upgrade pip
python3 -m pip install ".[cpu,build]"

echo ">> Empacotando com PyInstaller"
pyinstaller --noconfirm --clean \
  --name "TranscritorProfAMR" \
  --windowed \
  --add-data "dados:dados" \
  run_gui.py

echo ""
echo ">> Pronto. Binario em: dist/TranscritorProfAMR/"
echo "   (o modelo de transcricao e baixado no primeiro uso e fica em cache)"
