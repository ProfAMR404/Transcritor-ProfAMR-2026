@echo off
REM ============================================================
REM  Transcritor ProfAMR 2026 - abrir no Windows (duplo clique)
REM  Na primeira vez instala tudo e baixa o modelo (precisa de
REM  internet SO nesta primeira vez). Depois roda offline.
REM ============================================================
setlocal
cd /d "%~dp0"
title Transcritor ProfAMR 2026

where python >nul 2>&1
if errorlevel 1 (
  echo.
  echo  [!] Python nao encontrado.
  echo      Baixe em https://www.python.org/downloads/ e, na instalacao,
  echo      MARQUE a opcao "Add Python to PATH". Depois rode este arquivo de novo.
  echo.
  pause
  exit /b 1
)

if not exist ".venv" (
  echo  [1/3] Preparando ambiente ^(primeira vez^)...
  python -m venv .venv
)
call ".venv\Scripts\activate.bat"

python -m pip show faster-whisper >nul 2>&1
if errorlevel 1 (
  echo  [2/3] Instalando o motor de transcricao ^(primeira vez, pode demorar^)...
  python -m pip install --upgrade pip >nul
  python -m pip install faster-whisper
)

echo  [3/3] Abrindo o Transcritor...
python -m transcritor.gui
if errorlevel 1 (
  echo.
  echo  [!] Algo deu errado ao abrir. Copie a mensagem acima.
  pause
)
endlocal
