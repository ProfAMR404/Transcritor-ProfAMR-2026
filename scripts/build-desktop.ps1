# Gera o executavel desktop (.exe) para Windows com PyInstaller.
# Requer o Python oficial (com Tkinter, ja incluso). Rode no PowerShell.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

Write-Host ">> Instalando dependencias de build e execucao" -ForegroundColor Cyan
python -m pip install --upgrade pip
python -m pip install ".[cpu,build]"

Write-Host ">> Empacotando com PyInstaller (.exe)" -ForegroundColor Cyan
pyinstaller --noconfirm --clean `
  --name "TranscritorProfAMR" `
  --windowed `
  --collect-all faster_whisper `
  --collect-all ctranslate2 `
  --collect-all av `
  --collect-all onnxruntime `
  --collect-all tokenizers `
  --collect-all huggingface_hub `
  --add-data "dados;dados" `
  run_gui.py

Write-Host ""
Write-Host ">> Pronto. Executavel em: dist\TranscritorProfAMR\TranscritorProfAMR.exe" -ForegroundColor Green
Write-Host "   Distribua a pasta dist\TranscritorProfAMR\ inteira (ou gere um instalador)." -ForegroundColor Green
