from transcritor.pos_penal import RelatorioCorrecao, aplicar_correcoes, normalizar_dispositivos, processar_texto


def test_ordinal_ate_nono_cardinal_depois():
    assert normalizar_dispositivos("artigo 1 e parágrafo 4") == "art. 1º e § 4º"
    assert normalizar_dispositivos("artigo 33, paragrafo 10") == "art. 33, § 10"
    assert normalizar_dispositivos("artigos 33 e 35") == "arts. 33 e 35"
    assert normalizar_dispositivos("parágrafos 1 e 2") == "§§ 1º e 2"


def test_nao_duplica_ordinal_nem_quebra_letra():
    assert normalizar_dispositivos("artigo 1º") == "artigo 1º"
    assert normalizar_dispositivos("artigo 217-A") == "art. 217-A"


def test_identidade_nao_conta_como_correcao():
    rel = RelatorioCorrecao()
    aplicar_correcoes("a materialidade", {"materialidade": "materialidade"}, rel)
    assert rel.total == 0


def test_preserva_maiuscula_inicial():
    assert aplicar_correcoes("Reu presente", {"reu": "réu"}) == "Réu presente"


def test_verbo_denuncia_nao_vira_substantivo(tmp_path):
    import json
    from transcritor import paths
    corr = json.loads((paths.pasta_dados() / "correcoes.json").read_text(encoding="utf-8"))["correcoes"]
    assert processar_texto("O Ministério Público denuncia o réu.", corr) == "O Ministério Público denuncia o réu."
    assert processar_texto("reitera a denuncia", corr) == "reitera a denúncia"
    assert processar_texto("eu tava lá", corr) == "eu tava lá"
