# Gera o sidecar 'transcritor-engine' [motor Python] no Windows e o nomeia com
# o target triple do Rust, como o Tauri v2 exige em externalBin. Rode no PowerShell.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..\..")   # raiz do repositorio

Write-Host ">> Instalando dependencias de build do sidecar" -ForegroundColor Cyan
python -m pip install --upgrade pip pyinstaller faster-whisper

Write-Host ">> Empacotando o motor com PyInstaller [onefile]" -ForegroundColor Cyan
pyinstaller --noconfirm --clean --onefile --name transcritor-engine `
  --collect-all faster_whisper `
  --collect-all ctranslate2 `
  --collect-all av `
  --collect-all onnxruntime `
  --collect-all tokenizers `
  --collect-all huggingface_hub `
  --add-data "dados;dados" `
  engine_entry.py

$triple = (rustc -Vv | Select-String '^host: ').ToString().Replace('host: ','').Trim()
$dest = "app-tauri\src-tauri\binaries"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item "dist\transcritor-engine.exe" "$dest\transcritor-engine-$triple.exe" -Force
Write-Host ">> Sidecar: $dest\transcritor-engine-$triple.exe" -ForegroundColor Green
