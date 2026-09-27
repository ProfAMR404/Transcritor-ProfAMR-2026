"""Textos fixos exibidos ao usuario: aviso de uso e instrucoes."""
from __future__ import annotations

from . import paths

SITE = "www.profamr.org"
SITE_URL = "https://www.profamr.org"

AVISO_TITULO = "Aviso de uso"

AVISO = (
    "A transcrição é gerada automaticamente por modelo de reconhecimento de fala "
    "e, quando ativada, revisada por modelo de linguagem local. O resultado pode "
    "conter omissões, palavras trocadas, erros de pontuação e falas atribuídas de "
    "forma incorreta.\n\n"
    "O texto não substitui a gravação audiovisual, que permanece a fonte oficial do "
    "ato. Toda citação em voto, decisão, parecer ou petição deve ser conferida com "
    "o áudio ou o vídeo original, no minuto indicado entre colchetes.\n\n"
    "A responsabilidade pelo conteúdo cabe a quem assina o documento. O "
    "processamento ocorre no próprio computador: nenhum áudio ou texto é enviado "
    "a terceiros."
)

# Primeira linha do cabecalho da ata.
AVISO_ATA = (
    "TRANSCRIÇÃO AUTOMÁTICA — sujeita a erro: conferir com a gravação original "
    "antes de citar em qualquer peça"
)

# Versao curta: rodape da janela.
AVISO_CURTO = (
    "Transcrição automática, sujeita a erro: conferir com a gravação original "
    "antes de citar em qualquer peça."
)


def instrucoes() -> str:
    """Instrucoes ao usuario [dados/INSTRUCOES-AO-USUARIO.txt]."""
    caminho = paths.pasta_dados() / "INSTRUCOES-AO-USUARIO.txt"
    try:
        return caminho.read_text(encoding="utf-8")
    except OSError:
        return f"Instruções não encontradas em {caminho}."
