# binaries — sidecar do motor

O Tauri v2 procura aqui um executável externo nomeado com o *target triple* do Rust:

    transcritor-engine-<triple>          [Linux/macOS]
    transcritor-engine-<triple>.exe      [Windows]

Exemplos de triple: `x86_64-pc-windows-msvc`, `x86_64-unknown-linux-gnu`,
`aarch64-apple-darwin`. Descubra o seu com `rustc -Vv` [linha `host:`].

O binário é **gerado** pelos scripts `../../scripts/build-sidecar.{sh,ps1}` e
**não é versionado** [ver `.gitignore`]. Cada plataforma gera o seu.
