# Ollama — revisão por modelo de linguagem local

A revisão por modelo de linguagem é **opcional** e **desligada por padrão**. O Transcritor conversa apenas com o Ollama da própria máquina [`http://127.0.0.1:11434`]; nenhum trecho de depoimento vai para a nuvem.

## Uso: um botão

Na janela do Transcritor, clique em **Preparar Ollama**:

1. o Transcritor procura o Ollama: pasta portátil, pasta escolhida em **Localizar ollama.exe…**, `PATH`, `%LOCALAPPDATA%\Programs\Ollama`, `Program Files\Ollama` e o registro de instalação do Windows;
2. se não encontrar, oferece baixar a versão oficial portátil [`ollama-windows-amd64.zip`, ≈ 1,5 GB] para `%USERPROFILE%\TranscritorProfAMR\ollama`;
3. inicia o Ollama em segundo plano, sem janela;
4. se o modelo escolhido faltar, oferece baixá-lo [`gemma3:4b`, ≈ 3,3 GB];
5. liga a revisão.

**Não abra o `ollama.exe` diretamente.** Aberto sem comando, o Ollama mostra uma tela própria de criação de conta [“Create an account … No thanks, I'll use Ollama locally”] e fecha ao recusar. O Transcritor não usa essa tela: chama o Ollama como servidor local, sem conta e sem nuvem.

O Transcritor fala com o Ollama sem passar pelo proxy do sistema [redes institucionais configuram proxy no Windows; a conexão com `127.0.0.1` é local].

## 1. Links oficiais de download

Links do repositório oficial [`github.com/ollama/ollama`](https://github.com/ollama/ollama/releases/latest). O endereço `releases/latest/download/…` sempre aponta para a versão mais recente [conferido em 26/09/2026: v0.34.4].

| Sistema | Arquivo | Tamanho aprox. | Link |
|---|---|---|---|
| **Windows — portátil** [recomendado] | `ollama-windows-amd64.zip` | 1,46 GB | https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip |
| Windows — instalador | `OllamaSetup.exe` | 1,57 GB | https://github.com/ollama/ollama/releases/latest/download/OllamaSetup.exe |
| macOS | `Ollama.dmg` | 199 MB | https://github.com/ollama/ollama/releases/latest/download/Ollama.dmg |
| Linux | script oficial | — | `curl -fsSL https://ollama.com/install.sh \| sh` |

## 2. Modo portátil montado à mão [alternativa ao botão]

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

4. Abra o Transcritor e clique em **Preparar Ollama**. O programa inicia o `ollama.exe` sozinho e oferece baixar o modelo. No modo portátil, os modelos ficam em `ollama\models\`, dentro da própria pasta: a pasta inteira pode ser copiada para outro computador, ou para um pendrive, já com o modelo.

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
| “Ollama não encontrado” | Clique em **Preparar Ollama** e aceite o download, ou use **Localizar ollama.exe…**. |
| “Encontrado, mas não respondeu” | Feche o Ollama pela bandeja do Windows e clique de novo em **Preparar Ollama**. Detalhes técnicos em `%USERPROFILE%\TranscritorProfAMR\transcritor.log`. |
| “O modelo … não está instalado” | Clique em **Preparar Ollama**. |
| Download do modelo falha | O download do modelo é feito pelo próprio Ollama e exige acesso a `registry.ollama.ai`. O Ollama não usa o proxy configurado no Windows, só a variável de ambiente `HTTPS_PROXY`. Em rede institucional com proxy obrigatório, prepare numa rede liberada; depois a revisão roda offline. |
| Revisão muito lenta | Modelo grande para a máquina. Use `gemma3:4b`, ou desligue a revisão. A camada penal continua ativa. |
