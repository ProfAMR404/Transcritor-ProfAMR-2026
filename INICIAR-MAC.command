#!/bin/bash
# ============================================================
#  Transcritor ProfAMR 2026 - abrir no macOS (duplo clique)
#  Se o Mac bloquear: clique com o botao direito -> Abrir.
#  Primeira vez: instala tudo e baixa o modelo (precisa de
#  internet SO nesta primeira vez). Depois roda offline.
# ============================================================
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[!] Python3 nao encontrado. Instale em https://www.python.org/downloads/"
  read -rp "Enter para sair..." _; exit 1
fi

if [ ! -d ".venv" ]; then
  echo "[1/3] Preparando ambiente (primeira vez)..."
  python3 -m venv .venv
fi
source .venv/bin/activate

if ! python -c "import faster_whisper" >/dev/null 2>&1; then
  echo "[2/3] Instalando o motor de transcricao (primeira vez, pode demorar)..."
  python -m pip install --upgrade pip >/dev/null
  python -m pip install faster-whisper
fi

echo "[3/3] Abrindo o Transcritor..."
python -m transcritor.gui
