from servicos.permissoes import podeExecutar, PERMISSOES, CARGOS

def testPodeExecutar():
    for acao in PERMISSOES:
        for cargo in PERMISSOES[acao]:
            assert podeExecutar(cargo, acao) is True

def testNaoPodeExecutar():
    for acao in PERMISSOES:
            for cargo in CARGOS:
                if cargo not in PERMISSOES[acao]:
                    assert podeExecutar(cargo, acao) is False


def testAcaoInvalida():
    for cargo in CARGOS:
        assert podeExecutar(cargo, "ACAO_INEXISTENTE") is False
            
def testCargoInvalido():
    for acao in PERMISSOES:
        assert podeExecutar("CARGO_INEXISTENTE", acao) is False