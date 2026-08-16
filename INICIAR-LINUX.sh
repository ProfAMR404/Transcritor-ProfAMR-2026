#!/usr/bin/env bash
# ============================================================
#  Transcritor ProfAMR 2026 - abrir no Linux
#  Rode:  bash INICIAR-LINUX.sh   (ou duplo clique -> Executar)
#  Primeira vez: instala tudo e baixa o modelo (precisa de
#  internet SO nesta primeira vez). Depois roda offline.
# ============================================================
cd "$(dirname "$0")"

# Cabecalho de marca (ouro discreto se o terminal suportar cor)
G=$'\033[1;33m'; R=$'\033[0m'
printf '\n  %s==========================================================%s\n' "$G" "$R"
printf '    %sP R O F .   A M R%s\n' "$G" "$R"
printf '    Transcritor de Audiencias  -  materia criminal\n'
printf '  %s==========================================================%s\n\n' "$G" "$R"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[!] Python3 nao encontrado. Instale com: sudo apt install python3 python3-venv python3-tk"
  read -rp "Enter para sair..." _; exit 1
fi

if ! python3 -c "import tkinter" >/dev/null 2>&1; then
  echo "[!] A janela precisa do Tkinter. Instale com:  sudo apt install python3-tk"
  echo "    (depois rode este arquivo de novo)"
  read -rp "Enter para sair..." _; exit 1
fi

if [ ! -d ".venv" ]; then
  echo "[1/3] Preparando ambiente (primeira vez)..."
  python3 -m venv --system-site-packages .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

if ! python -c "import faster_whisper" >/dev/null 2>&1; then
  echo "[2/3] Instalando o motor de transcricao (primeira vez, pode demorar)..."
  python -m pip install --upgrade pip >/dev/null
  python -m pip install faster-whisper
fi

echo "[3/3] Abrindo o Transcritor..."
python -m transcritor.gui
