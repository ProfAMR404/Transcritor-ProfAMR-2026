// Frontend do Transcritor ProfAMR [Tauri v2, API global window.__TAURI__].
const { invoke } = window.__TAURI__.core;
const { listen } = window.__TAURI__.event;
const dialog = window.__TAURI__.dialog;
const fs = window.__TAURI__.fs;

const el = (id) => document.getElementById(id);
const estado = { arquivo: null, nome: null };

function hms(seg) {
  const s = Math.max(0, Math.floor(seg));
  const h = String(Math.floor(s / 3600)).padStart(2, "0");
  const m = String(Math.floor((s % 3600) / 60)).padStart(2, "0");
  const x = String(s % 60).padStart(2, "0");
  return `${h}:${m}:${x}`;
}

function montarAta(trechos) {
  return trechos
    .map((t) => `[${hms(t.inicio)}] ${t.falante}: ${t.texto}`)
    .join("\n\n");
}

async function escolherArquivo() {
  const escolha = await dialog.open({
    multiple: false,
    filters: [
      { name: "Áudio/Vídeo", extensions: ["mp4", "mp3", "wav", "m4a", "mkv", "mov", "ogg", "flac"] },
      { name: "Todos", extensions: ["*"] },
    ],
  });
  if (escolha) {
    estado.arquivo = escolha;
    estado.nome = escolha.replace(/^.*[\\/]/, "");
    el("arquivo").textContent = estado.nome;
  }
}

async function transcrever() {
  if (!estado.arquivo) {
    el("progresso").textContent = "Escolha um arquivo primeiro.";
    return;
  }
  el("btn-transcrever").disabled = true;
  el("btn-salvar").disabled = true;
  el("progresso").textContent = "Iniciando…";

  const parar = await listen("progresso", (ev) => {
    el("progresso").textContent = ev.payload;
  });

  try {
    const res = await invoke("transcrever", {
      caminho: estado.arquivo,
      modelo: el("modelo").value,
      llm: el("llm").checked,
    });
    if (!res.ok) {
      el("progresso").textContent = "Erro: " + (res.erro || "desconhecido");
      return;
    }
    el("ata").value = montarAta(res.trechos);
    el("btn-salvar").disabled = false;
    el("progresso").textContent = `Concluído · ${res.correcoes} correções · motor ${res.motor}`;
  } catch (e) {
    el("progresso").textContent = "Falha: " + e;
  } finally {
    parar();
    el("btn-transcrever").disabled = false;
  }
}

async function salvarAta() {
  const destino = await dialog.save({
    defaultPath: (estado.nome ? estado.nome.replace(/\.[^.]+$/, "") : "ata") + ".txt",
    filters: [{ name: "Texto", extensions: ["txt"] }],
  });
  if (destino) {
    await fs.writeTextFile(destino, el("ata").value);
    el("progresso").textContent = "Ata salva em: " + destino;
  }
}

el("btn-arquivo").addEventListener("click", escolherArquivo);
el("btn-transcrever").addEventListener("click", transcrever);
el("btn-salvar").addEventListener("click", salvarAta);
