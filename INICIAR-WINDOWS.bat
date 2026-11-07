@echo off
REM ============================================================
REM  Transcritor ProfAMR 2026 - rodar a partir do CODIGO-FONTE
REM  [quem baixou pelo botao verde "Code > Download ZIP"].
REM
REM  CAMINHO RECOMENDADO: o programa pronto, sem Python:
REM  https://github.com/ProfAMR404/Transcritor-ProfAMR-2026/releases/latest
REM
REM  Este arquivo exige Python 3.11, 3.12, 3.13 ou 3.14. O Python
REM  3.15 ainda nao tem o pacote onnxruntime, usado pelo motor.
REM ============================================================
setlocal EnableDelayedExpansion
cd /d "%~dp0"
title Transcritor ProfAMR 2026
set "RELEASE=https://github.com/ProfAMR404/Transcritor-ProfAMR-2026/releases/latest"
set "CHECA=import sys; sys.exit(0 if (3,11)<=sys.version_info[:2]<=(3,14) else 1)"

echo(
echo    ==========================================================
echo      P R O F .   A M R
echo      Transcritor de Audiencias  -  materia criminal
echo    ==========================================================
echo(

REM --- 1. Escolher um Python compativel [3.11 a 3.14] ----------
set "PY="
if defined TRANSCRITOR_PYTHON (
  "%TRANSCRITOR_PYTHON%" -c "%CHECA%" >nul 2>&1 && set "PY="%TRANSCRITOR_PYTHON%""
  goto :verificado
)
for %%V in (3.13 3.12 3.14 3.11) do (
  if not defined PY (
    py -%%V -c "%CHECA%" >nul 2>&1 && set "PY=py -%%V"
  )
)
if not defined PY (
  python -c "%CHECA%" >nul 2>&1 && set "PY=python"
)
:verificado
if not defined PY (
  echo  [!] Nenhum Python compativel encontrado [precisa de 3.11 a 3.14].
  echo      O Python 3.15 ainda nao e suportado pelo motor de transcricao.
  echo(
  echo      CAMINHO RECOMENDADO: baixe o programa pronto, sem Python:
  echo      %RELEASE%
  echo      [arquivo TranscritorProfAMR-Windows.zip]
  echo(
  echo      Alternativa: instale o Python 3.13 em
  echo      https://www.python.org/downloads/windows/
  echo      marcando "Add Python to PATH", e rode este arquivo de novo.
  echo(
  if not defined TRANSCRITOR_SO_TESTAR start "" "%RELEASE%"
  if not defined TRANSCRITOR_SO_TESTAR pause
  exit /b 2
)
echo  Python escolhido: !PY!

REM --- 2. Ambiente isolado [.venv]; refaz se foi criado com Python incompativel
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -c "%CHECA%" >nul 2>&1 || (
    echo  [1/3] Refazendo o ambiente [criado antes com Python incompativel]...
    rmdir /s /q ".venv"
  )
)
if not exist ".venv\Scripts\python.exe" (
  echo  [1/3] Preparando ambiente ^(primeira vez^)...
  !PY! -m venv .venv
  if errorlevel 1 goto :falhou
)
set "VPY=.venv\Scripts\python.exe"

REM --- 3. Motor de transcricao ---------------------------------
"%VPY%" -c "import faster_whisper" >nul 2>&1
if errorlevel 1 (
  echo  [2/3] Instalando o motor de transcricao ^(primeira vez, pode demorar^)...
  "%VPY%" -m pip install --upgrade pip >nul
  "%VPY%" -m pip install faster-whisper
  "%VPY%" -c "import faster_whisper" >nul 2>&1
  if errorlevel 1 goto :falhou
)

REM --- 4. Abrir [ou, em teste automatico, rodar a demonstracao] -
if defined TRANSCRITOR_SO_TESTAR (
  "%VPY%" -m transcritor.cli demo
  exit /b !errorlevel!
)
echo  [3/3] Abrindo o Transcritor...
"%VPY%" -m transcritor.gui
if errorlevel 1 (
  echo.
  echo  [!] Algo deu errado ao abrir. Copie a mensagem acima.
  pause
)
endlocal
exit /b 0

:falhou
echo(
echo  [!] A instalacao do motor de transcricao falhou [mensagem acima].
echo      Baixe o programa pronto, que nao precisa de Python:
echo      %RELEASE%
echo(
if not defined TRANSCRITOR_SO_TESTAR start "" "%RELEASE%"
if not defined TRANSCRITOR_SO_TESTAR pause
exit /b 3
