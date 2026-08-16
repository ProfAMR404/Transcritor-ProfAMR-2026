# Instalador para Windows via WSL2 (PowerShell, como administrador).
# O WhisperX NAO roda em Windows nativo; usamos o subsistema Linux.

Write-Host ">> Transcritor ProfAMR 2026 - preparacao no Windows (WSL2)" -ForegroundColor Cyan

# 1) Verifica/instala o WSL2 com Ubuntu
$wsl = (wsl --version) 2>$null
if (-not $wsl) {
    Write-Host ">> Instalando o WSL2 + Ubuntu (reinicie o PC ao final e rode de novo)..." -ForegroundColor Yellow
    wsl --install -d Ubuntu
    Write-Host "Reinicie o computador e execute este script novamente." -ForegroundColor Yellow
    exit 0
}

Write-Host ">> WSL2 detectado. Rodando o instalador Linux dentro do Ubuntu..." -ForegroundColor Green
# Executa o instalador Linux dentro do WSL, na pasta atual do projeto
wsl bash -lc "cd \$(wslpath '$PWD') && bash scripts/instalar-linux.sh"

Write-Host ""
Write-Host ">> Pronto. Para usar, abra o Ubuntu (WSL) e rode:  transcritor demo" -ForegroundColor Cyan
Write-Host ">> Para GPU NVIDIA no WSL2, instale o driver CUDA para WSL no Windows." -ForegroundColor Cyan
