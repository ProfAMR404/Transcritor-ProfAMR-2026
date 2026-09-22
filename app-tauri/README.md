# Transcritor ProfAMR — casca Tauri [Fase 1]

Interface desktop em Tauri v2 sobre o motor Python [faster-whisper] do repositório,
empacotado como *sidecar*. O app Tkinter atual segue funcionando em paralelo.

## Pré-requisitos [na máquina de build]
- Rust [rustup] e as dependências de build do Tauri v2 do seu sistema operacional.
- Node.js 18+.
- Python 3.10+ [para gerar o sidecar].

## Passos
1. **Gerar o sidecar** [motor Python nomeado com o *target triple*]:
   - Linux/macOS: `bash scripts/build-sidecar.sh`
   - Windows: `powershell -ExecutionPolicy Bypass -File scripts/build-sidecar.ps1`
   O binário sai em `src-tauri/binaries/transcritor-engine-<triple>[.exe]`.
2. **Instalar as dependências do frontend/CLI:** `npm install`
3. **Gerar os ícones** a partir da logo: `npm run icon`
4. **Rodar em desenvolvimento:** `npm run dev`
5. **Gerar o instalador nativo:** `npm run build`
   Saída em `src-tauri/target/release/bundle/` [`.msi`/NSIS no Windows, `.dmg`, `.AppImage`/`.deb`]. O instalador cria atalho e desinstalador.

## Notas
- O modelo de transcrição é baixado no primeiro uso e fica em cache; depois roda offline.
- A revisão por modelo local usa o Ollama em `localhost`, opcional.
- Escopo da Fase 1: transcrever, camada penal, saída `.txt` editável. Sessão em SQLite e export Markdown ficam para a Fase 2.
- Ainda **não testado em build real** neste ambiente [sem toolchain Rust nem tela]; validar na máquina do autor.
