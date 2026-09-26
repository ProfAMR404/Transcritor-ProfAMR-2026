# Ollama — revisão por modelo de linguagem local

A revisão por modelo de linguagem é **opcional** e **desligada por padrão**. O Transcritor conversa apenas com o Ollama da própria máquina [`http://127.0.0.1:11434`]; nenhum trecho de depoimento vai para a nuvem.

O Transcritor **não embute o Ollama no pacote**: o Ollama para Windows tem cerca de 1,5 GB e é atualizado com frequência. O programa, porém, **roda o Ollama por dentro**: localiza o executável, inicia o servidor sozinho em segundo plano e baixa o modelo pela própria janela, sem terminal.

## 1. Links oficiais de download

Links do repositório oficial [`github.com/ollama/ollama`](https://github.com/ollama/ollama/releases/latest). O endereço `releases/latest/download/…` sempre aponta para a versão mais recente [conferido em 26/09/2026: v0.34.4].

| Sistema | Arquivo | Tamanho aprox. | Link |
|---|---|---|---|
| **Windows — portátil** [recomendado] | `ollama-windows-amd64.zip` | 1,46 GB | https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip |
| Windows — instalador | `OllamaSetup.exe` | 1,57 GB | https://github.com/ollama/ollama/releases/latest/download/OllamaSetup.exe |
| macOS | `Ollama.dmg` | 199 MB | https://github.com/ollama/ollama/releases/latest/download/Ollama.dmg |
| Linux | script oficial | — | `curl -fsSL https://ollama.com/install.sh \| sh` |

## 2. Modo portátil [Ollama rodando dentro da pasta do Transcritor]

1. Baixe `ollama-windows-amd64.zip`.
2. Crie uma pasta chamada **`ollama`** dentro da pasta do Transcritor, ao lado do `TranscritorProfAMR.exe`.
3. Descompacte o zip **dentro** dessa pasta. Deve ficar assim:

```
TranscritorProfAMR\
├── TranscritorProfAMR.exe
├── modelos\
└── ollama\
    ├── ollama.exe
    └── lib\ …
```

4. Abra o Transcritor e marque **“Revisar com modelo de linguagem local”**. O programa inicia o `ollama.exe` sozinho.
5. Clique em **“Baixar modelo”** [uma única vez]. No modo portátil, os modelos ficam em `ollama\models\`, dentro da própria pasta: a pasta inteira pode ser copiada para outro computador, ou para um pendrive, já com o modelo.

Alternativa: a pasta `ollama` também é procurada em `%USERPROFILE%\TranscritorProfAMR\ollama`.

## 3. Modo instalado

Com o `OllamaSetup.exe` [Windows], o `Ollama.dmg` [macOS] ou o script [Linux], o Transcritor encontra o Ollama no caminho padrão de instalação e o inicia se não estiver aberto. Os modelos ficam na pasta do usuário [`~/.ollama/models`].

## 4. Modelo de revisão

| Modelo | Tamanho | Memória sugerida | Uso |
|---|---|---|---|
| **`gemma3:4b`** | ≈ 3,3 GB | 8 GB de RAM | padrão |
| `gemma3:12b` | ≈ 8,1 GB | 16 GB de RAM | revisão melhor, mais lenta |

O campo “Modelo” da janela aceita qualquer nome da [biblioteca do Ollama](https://ollama.com/library). Pela linha de comando:

```
transcritor ollama status            # localiza/inicia o Ollama e lista os modelos
transcritor ollama baixar gemma3:4b  # baixa o modelo
transcritor transcrever audiencia.mp4 --llm --modelo-llm gemma3:4b
```

## 5. Trava contra reescrita

O modelo recebe a instrução de corrigir só ortografia, acentuação, pontuação e grafia de termos jurídicos. Além da instrução, o programa **recusa** a proposta do modelo e mantém o texto da camada penal quando:

- algum número muda, some ou aparece [artigo, parágrafo, data, valor, placa];
- o número de palavras varia mais de 25% em relação ao trecho original;
- a resposta vem vazia.

O cabeçalho da ata informa quantos trechos o modelo alterou e quantas propostas a trava recusou. O `.json` guarda, para cada trecho, o **texto bruto** do reconhecimento de fala, o texto final e a marca `revisado_llm`. Toda alteração fica rastreável e confrontável com o áudio.

## 6. Problemas comuns

| Sintoma | Causa e solução |
|---|---|
| “O Ollama não foi encontrado” | Nenhum Ollama instalado nem pasta `ollama\` ao lado do `.exe`. Siga a seção 2 ou 3. |
| “O modelo … não está instalado” | Clique em “Baixar modelo” ou rode `ollama pull gemma3:4b`. |
| Download do modelo falha | O download [só nessa etapa] exige internet e acesso a `registry.ollama.ai`. Redes corporativas podem bloquear: baixe numa rede liberada, no modo portátil, e copie a pasta `ollama\` inteira. |
| Revisão muito lenta | Modelo grande para a máquina. Use `gemma3:4b`, ou desligue a revisão. A camada penal continua ativa. |
