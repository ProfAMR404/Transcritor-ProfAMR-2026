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

## 3. Uso real
1. Peça à TI para rodar `scripts/instalar-linux.sh` (Linux) ou `scripts/instalar-windows.ps1` (Windows/WSL2) **numa máquina com placa NVIDIA**.
2. Coloque o arquivo da audiência (ex.: `audiencia.mp4`) na pasta do programa.
3. Rode:
   ```
   transcritor transcrever audiencia.mp4
   ```
4. Abra a pasta `saida/`: você terá `.txt` (ata), `.srt` (legenda) e `.json` (dados).

## 4. Ajustar quem é quem
Antes de gerar a ata final, abra `dados/rotulos.json` e diga qual falante é o Juiz, o MP, a Defesa, a Testemunha. A ordem muda a cada audiência.

## 5. Melhorar a grafia dos termos
Se você notar um erro recorrente (ex.: o programa escreveu "dosemetria"), abra `dados/correcoes.json` e acrescente a linha:
```
"dosemetria": "dosimetria"
```
Na próxima transcrição já sai certo. É assim que a ferramenta "aprende" o vocabulário do gabinete.

## 6. Limites (importante)
- A transcrição é **apoio de trabalho**, não ata oficial com fé pública — sempre revise antes de usar.
- Áudio ruim, vozes sobrepostas e muito ruído pioram o resultado. Bom microfone ajuda mais que qualquer modelo.
- Nunca ligue integrações de nuvem para material sigiloso.

## 7. Dúvidas frequentes
**Precisa de internet?** Só na instalação. Depois, não.
**Precisa de placa de vídeo?** Para uso real, sim (NVIDIA). Para o `demo`, não.
**Funciona no Mac?** O motor real, não; use uma máquina Windows (WSL2) ou Linux com NVIDIA.
