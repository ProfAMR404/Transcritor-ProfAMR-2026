@echo off
REM Cria um atalho do Transcritor na Area de Trabalho. Rode dentro da pasta do app.
setlocal
cd /d "%~dp0"
if not exist "TranscritorProfAMR.exe" (
  echo [!] Rode este arquivo DENTRO da pasta que contem TranscritorProfAMR.exe
  pause
  exit /b 1
)
powershell -NoProfile -Command "$d=[Environment]::GetFolderPath('Desktop'); $s=(New-Object -ComObject WScript.Shell).CreateShortcut($d+'\Transcritor ProfAMR.lnk'); $s.TargetPath='%~dp0TranscritorProfAMR.exe'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%~dp0TranscritorProfAMR.exe'; $s.Description='Transcritor de audiencias penais - Prof. AMR'; $s.Save()"
echo Atalho "Transcritor ProfAMR" criado na Area de Trabalho.
pause
