// Casca Tauri v2 do Transcritor ProfAMR.
// Chama o motor Python [sidecar 'transcritor-engine'], transmite o progresso
// [eventos 'progresso'] e devolve o JSON do resultado ao frontend.

use tauri::{Emitter, Manager};
use tauri_plugin_shell::process::CommandEvent;
use tauri_plugin_shell::ShellExt;

#[tauri::command]
async fn transcrever(
    app: tauri::AppHandle,
    caminho: String,
    modelo: String,
    llm: bool,
) -> Result<serde_json::Value, String> {
    // Pasta de saida gravavel [dados do app do usuario].
    let saida = app
        .path()
        .app_local_data_dir()
        .map_err(|e| e.to_string())?
        .join("saida");
    std::fs::create_dir_all(&saida).map_err(|e| e.to_string())?;

    let mut args: Vec<String> = vec![
        "transcrever".into(),
        caminho,
        "--modelo".into(),
        modelo,
        "--saida".into(),
        saida.to_string_lossy().into_owned(),
    ];
    if llm {
        args.push("--llm".into());
    }

    let sidecar = app
        .shell()
        .sidecar("transcritor-engine")
        .map_err(|e| e.to_string())?
        .args(args);
    let (mut rx, _child) = sidecar.spawn().map_err(|e| e.to_string())?;

    let mut stdout_buf = String::new();
    let mut code: Option<i32> = None;

    while let Some(event) = rx.recv().await {
        match event {
            CommandEvent::Stderr(bytes) => {
                let texto = String::from_utf8_lossy(&bytes);
                for linha in texto.lines() {
                    if let Some(msg) = linha.strip_prefix("PROGRESSO: ") {
                        let _ = app.emit("progresso", msg.trim().to_string());
                    }
                }
            }
            CommandEvent::Stdout(bytes) => {
                stdout_buf.push_str(&String::from_utf8_lossy(&bytes));
            }
            CommandEvent::Terminated(payload) => {
                code = payload.code;
            }
            _ => {}
        }
    }

    if stdout_buf.trim().is_empty() {
        return Err(format!("o motor nao retornou dados [codigo {:?}]", code));
    }
    serde_json::from_str::<serde_json::Value>(stdout_buf.trim())
        .map_err(|e| format!("saida invalida do motor: {e}"))
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .invoke_handler(tauri::generate_handler![transcrever])
        .run(tauri::generate_context!())
        .expect("erro ao iniciar o Transcritor ProfAMR");
}
