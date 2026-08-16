"""Pos-correcao penal deterministica.

Aplica, sobre o texto ja transcrito, um conjunto de regras seguras e auditaveis:
  1. mapa de correcoes ortografico-juridicas (dados/correcoes.json);
  2. normalizacao de referencias a dispositivos ("artigo 33" -> "art. 33",
     "paragrafo 4" -> "§ 4º");
  3. normalizacao de espacos e pontuacao.

Tudo aqui e reversivel e explicavel — nada de "alucinacao" de modelo. Cada
substituicao e contabilizada e pode ser exibida no relatorio (util para a ata).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict


@dataclass
class RelatorioCorrecao:
    """Contabiliza o que foi alterado, para auditoria."""

    ocorrencias: Dict[str, int] = field(default_factory=dict)

    def registrar(self, de: str, para: str, n: int = 1) -> None:
        if n <= 0:
            return
        chave = f"{de} -> {para}"
        self.ocorrencias[chave] = self.ocorrencias.get(chave, 0) + n

    @property
    def total(self) -> int:
        return sum(self.ocorrencias.values())


def carregar_correcoes(caminho: str | Path) -> Dict[str, str]:
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    return dados.get("correcoes", {})


def _preservar_caixa(original: str, novo: str) -> str:
    """Se a palavra original comecava com maiuscula, mantem no resultado."""
    if original[:1].isupper():
        return novo[:1].upper() + novo[1:]
    return novo


def aplicar_correcoes(
    texto: str, correcoes: Dict[str, str], rel: RelatorioCorrecao | None = None
) -> str:
    """Aplica o mapa de correcoes com fronteira de palavra, case-insensitive.

    Expressoes com mais de uma palavra sao aplicadas primeiro (mais especificas),
    evitando que uma correcao de palavra isolada quebre uma expressao composta.
    """
    itens = sorted(correcoes.items(), key=lambda kv: len(kv[0]), reverse=True)
    for errado, certo in itens:
        if errado.startswith("_"):
            continue
        padrao = re.compile(rf"\b{re.escape(errado)}\b", flags=re.IGNORECASE)

        def _subst(m: re.Match) -> str:
            return _preservar_caixa(m.group(0), certo)

        texto, n = padrao.subn(_subst, texto)
        if rel is not None:
            rel.registrar(errado, certo, n)
    return texto


def normalizar_dispositivos(texto: str, rel: RelatorioCorrecao | None = None) -> str:
    """'artigo 33' -> 'art. 33'; 'paragrafo 4' / 'parágrafo 4' -> '§ 4º'."""
    def _art(m: re.Match) -> str:
        return f"art. {m.group(1)}"

    texto, n1 = re.subn(r"\bartigos?\s+(\d+)", _art, texto, flags=re.IGNORECASE)

    def _par(m: re.Match) -> str:
        return f"§ {m.group(1)}º"

    texto, n2 = re.subn(
        r"\bpar[aá]grafo\s+(\d+)\b", _par, texto, flags=re.IGNORECASE
    )
    if rel is not None:
        rel.registrar("artigo N", "art. N", n1)
        rel.registrar("parágrafo N", "§ Nº", n2)
    return texto


def normalizar_espacos(texto: str) -> str:
    texto = re.sub(r"\s+([,.;:!?])", r"\1", texto)
    texto = re.sub(r"[ \t]{2,}", " ", texto)
    return texto.strip()


def processar_texto(
    texto: str, correcoes: Dict[str, str], rel: RelatorioCorrecao | None = None
) -> str:
    texto = aplicar_correcoes(texto, correcoes, rel)
    texto = normalizar_dispositivos(texto, rel)
    texto = normalizar_espacos(texto)
    return texto
