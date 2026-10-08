import pytest

from servicos.erros import (
    NaoEncontradoError,
    ConflitoError,
    CredenciaisInvalidasError,
    BloqueioError
)

ERROS = [NaoEncontradoError, ConflitoError, CredenciaisInvalidasError, BloqueioError]


@pytest.mark.parametrize("erro", ERROS)
def testErroHerdaDeValueError(erro):
    #quem já trata ValueError continua capturando as exceções novas
    assert issubclass(erro, ValueError)


@pytest.mark.parametrize("erro", ERROS)
def testErroMantemMensagem(erro):
    with pytest.raises(erro, match='MENSAGEM DE TESTE'):
        raise erro('MENSAGEM DE TESTE')


def testErrosSaoIndependentes():
    #nenhuma exceção é filha de outra, senão a API poderia escolher o status errado
    for erro in ERROS:
        for outro in ERROS:
            if erro is not outro:
                assert not issubclass(erro, outro)