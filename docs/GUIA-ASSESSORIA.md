# Guia rápido para a assessoria

Este guia é para quem vai **usar** a ferramenta no dia a dia — não é preciso saber programar.

## 1. O que é
Um programa que transforma o **áudio/vídeo de uma audiência** em **texto organizado por falante**, com carimbo de tempo, pronto para virar ata, subsídio de voto ou memorial. Roda **no seu computador**, sem internet — o depoimento não sai da máquina.

## 2. Ver funcionando (sem instalar nada pesado)
Numa máquina com Python:
```
python3 -m transcritor.cli demo
```
Aparece um relatório das correções e a prévia da ata. Os arquivos ficam na pasta `saida/`.

## 3. O aplicativo desktop (janela, jeito mais fácil)
Se a TI gerou o executável (`TranscritorProfAMR.exe` no Windows, ou a pasta `dist/` no Linux), é só **abrir com duplo clique**. Na janela:
1. **Escolher arquivo…** e selecionar o áudio/vídeo da audiência.
2. Conferir o **modelo** (`small` é um bom padrão) e clicar em **Transcrever**.
3. Ao terminar, o texto aparece na tela. Clique em **Salvar ata como…** para guardar.

Não precisa saber programar nem digitar comandos.

## 4. Uso por linha de comando (alternativa)
1. Peça à TI para instalar o motor: `pip install ".[cpu]"` (roda em **qualquer computador**, com ou sem placa de vídeo).
2. Rode:
   ```
   transcritor transcrever audiencia.mp4
   ```
3. Abra a pasta `saida/`: você terá `.txt` (ata), `.srt` (legenda) e `.json` (dados).

> Para separar automaticamente quem é Juiz, MP, Defesa e Testemunha, é preciso uma máquina com **placa NVIDIA** e a instalação com WhisperX (`scripts/instalar-linux.sh`). Sem ela, a transcrição sai com o tempo de cada fala e os papéis podem ser ajustados à mão.

## 5. Ajustar quem é quem
Antes de gerar a ata final, abra `dados/rotulos.json` e diga qual falante é o Juiz, o MP, a Defesa, a Testemunha. A ordem muda a cada audiência.

## 6. Melhorar a grafia dos termos
Se você notar um erro recorrente (ex.: o programa escreveu "dosemetria"), abra `dados/correcoes.json` e acrescente a linha:
```
"dosemetria": "dosimetria"
```
Na próxima transcrição já sai certo. É assim que a ferramenta "aprende" o vocabulário do gabinete.

## 7. Limites (importante)
- A transcrição é **apoio de trabalho**, não ata oficial com fé pública — sempre revise antes de usar.
- Áudio ruim, vozes sobrepostas e muito ruído pioram o resultado. Bom microfone ajuda mais que qualquer modelo.
- Nunca ligue integrações de nuvem para material sigiloso.

## 8. Dúvidas frequentes
**Precisa de internet?** Só na instalação (e no primeiro uso, para baixar o modelo). Depois, não.
**Precisa de placa de vídeo?** Não para transcrever (o motor de CPU funciona em qualquer PC). A placa NVIDIA só é necessária para **separar os falantes automaticamente** e para ganhar velocidade.
**Funciona no Mac?** Sim, o aplicativo e o motor de CPU funcionam. A separação automática de falantes (WhisperX) é que pede NVIDIA.
