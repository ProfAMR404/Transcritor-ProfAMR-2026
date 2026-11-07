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

RELEASE="https://github.com/ProfAMR404/Transcritor-ProfAMR-2026/releases/latest"
CHECA='import sys; sys.exit(0 if (3,11)<=sys.version_info[:2]<=(3,14) else 1)'

# Python compativel: 3.11 a 3.14 [o 3.15 ainda nao tem o pacote onnxruntime].
PY=""
CANDIDATOS="python3.13 python3.12 python3.14 python3.11 python3"
[ -n "${TRANSCRITOR_PYTHON:-}" ] && CANDIDATOS="$TRANSCRITOR_PYTHON"
for c in $CANDIDATOS; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "$CHECA" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  echo "[!] Nenhum Python compativel encontrado [precisa de 3.11 a 3.14]."
  echo "    Instale o Python 3.13 e rode este arquivo de novo."
  echo "    No Windows, prefira o programa pronto: $RELEASE"
  [ -n "${TRANSCRITOR_SO_TESTAR:-}" ] || read -rp "Enter para sair..." _
  exit 2
fi
echo "Python escolhido: $PY"

if [ -z "${TRANSCRITOR_SO_TESTAR:-}" ] && ! "$PY" -c "import tkinter" >/dev/null 2>&1; then
  echo "[!] A janela precisa do Tkinter. Instale com:  sudo apt install python3-tk"
  echo "    (depois rode este arquivo de novo)"
  read -rp "Enter para sair..." _; exit 1
fi

falhou() {
  echo
  echo "[!] A instalacao do motor de transcricao falhou [mensagem acima]."
  echo "    No Windows, use o programa pronto: $RELEASE"
  [ -n "${TRANSCRITOR_SO_TESTAR:-}" ] || read -rp "Enter para sair..." _
  exit 3
}

# Refaz o ambiente se foi criado com Python incompativel.
if [ -x .venv/bin/python ] && ! .venv/bin/python -c "$CHECA" >/dev/null 2>&1; then
  echo "[1/3] Refazendo o ambiente [criado antes com Python incompativel]..."
  rm -rf .venv
fi
if [ ! -x .venv/bin/python ]; then
  echo "[1/3] Preparando ambiente (primeira vez)..."
  "$PY" -m venv --system-site-packages .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

if ! python -c "import faster_whisper" >/dev/null 2>&1; then
  echo "[2/3] Instalando o motor de transcricao (primeira vez, pode demorar)..."
  python -m pip install --upgrade pip >/dev/null
  python -m pip install faster-whisper
  python -c "import faster_whisper" >/dev/null 2>&1 || falhou
fi

if [ -n "${TRANSCRITOR_SO_TESTAR:-}" ]; then exec python -m transcritor.cli demo; fi
echo "[3/3] Abrindo o Transcritor..."
python -m transcritor.gui
