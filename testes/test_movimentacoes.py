import sqlite3
import pytest

from servicos.movimentacoes import consultaMov, registroMov
from servicos.erros import NaoEncontradoError


@pytest.fixture
def banco():
    conexao = sqlite3.connect(":memory:")
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE historicoMovimentacao(
            id INTEGER PRIMARY KEY,
            produto TEXT NOT NULL,
            idProduto INTEGER NOT NULL,
            tipo TEXT DEFAULT NULL,
            quantidade INTEGER DEFAULT 0,
            data TEXT NOT NULL,
            hora TEXT NOT NULL,
            quemFez TEXT NOT NULL,
            valorEnvolvido INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE produtos(
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco INTEGER NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL,
            quemFez TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE saldo(
            id INTEGER PRIMARY KEY,
            valor INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE histSaldo(
            id INTEGER PRIMARY KEY,
            valor INTEGER NOT NULL,
            operacao TEXT NOT NULL,
            quemFez TEXT NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL
        )
    """)

    cursor.execute("""
        INSERT INTO saldo (id, valor)
        VALUES (1, 100000)
    """)

    cursor.execute("""
        INSERT INTO produtos
        (id, nome, quantidade, preco, data, hora, quemFez)
        VALUES (1, 'Coca Cola', 20, 600, '2026/10/01', '10:00', 'ROBERTO')
    """)

    conexao.commit()

    yield conexao, cursor

    conexao.close()


def testConsultaMovSemMovimentacoes(banco):
    conexao, cursor = banco

    historico = consultaMov(cursor)

    assert historico == []


def testRegistroCompra(banco):
    conexao, cursor = banco

    registroMov(
        1, 'COMPRA', 5,
        cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
        10
    )

    cursor.execute("SELECT quantidade FROM produtos WHERE id = 1")
    produto = cursor.fetchone()

    cursor.execute("SELECT valor FROM saldo WHERE id = 1")
    saldo = cursor.fetchone()[0]

    movimentacao = consultaMov(cursor)

    assert produto[0] == 25
    assert saldo == 99000
    assert movimentacao[0][0] == 'Coca Cola'
    assert movimentacao[0][1] == 1
    assert movimentacao[0][2] == 'COMPRA'
    assert movimentacao[0][3] == 5
    assert movimentacao[0][5] == 'ROBERTO'
    assert movimentacao[0][6] == 1000


def testRegistroDevolucao(banco):
    conexao, cursor = banco

    registroMov(
        1, 'DEVOLUÇÃO', 5,
        cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
        10
    )

    cursor.execute("SELECT quantidade FROM produtos WHERE id = 1")
    produto = cursor.fetchone()

    cursor.execute("SELECT valor FROM saldo WHERE id = 1")
    saldo = cursor.fetchone()[0]

    assert produto[0] == 25
    assert saldo == 99000

    movimentacao = consultaMov(cursor)
    assert movimentacao[0][2] == 'DEVOLUÇÃO'


def testRegistroVenda(banco):
    conexao, cursor = banco

    registroMov(
        1, 'VENDA', 5,
        cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
        10
    )

    cursor.execute("SELECT quantidade FROM produtos WHERE id = 1")
    produto = cursor.fetchone()

    cursor.execute("SELECT valor FROM saldo WHERE id = 1")
    saldo = cursor.fetchone()[0]

    assert produto[0] == 15
    assert saldo == 101000

    movimentacao = consultaMov(cursor)
    assert movimentacao[0][2] == 'VENDA'
    assert movimentacao[0][6] == 1000


def testRegistroPerca(banco):
    conexao, cursor = banco

    registroMov(
        1, 'PERCA', 5,
        cursor, conexao, 'ROBERTO', 'ADMINISTRADOR'
    )

    cursor.execute("SELECT quantidade FROM produtos WHERE id = 1")
    produto = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM histSaldo")
    historico_saldo = cursor.fetchone()[0]

    movimentacao = consultaMov(cursor)

    assert produto[0] == 15
    assert historico_saldo == 0
    assert movimentacao[0][2] == 'PERCA'
    assert movimentacao[0][3] == 5


def testRegistroTransferencia(banco):
    conexao, cursor = banco

    registroMov(
        1, 'TRANSFERÊNCIA', 5,
        cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
        10
    )

    cursor.execute("SELECT quantidade FROM produtos WHERE id = 1")
    produto = cursor.fetchone()

    cursor.execute("SELECT valor FROM saldo WHERE id = 1")
    saldo = cursor.fetchone()[0]

    assert produto[0] == 15
    assert saldo == 99000

    movimentacao = consultaMov(cursor)
    assert movimentacao[0][2] == 'TRANSFERÊNCIA'
    assert movimentacao[0][6] == 1000


def testRegistroIdInvalido(banco):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS!'
    ):
        registroMov(
            'ID INVÁLIDO', 'COMPRA', 5,
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            10
        )


def testRegistroIdNegativo(banco):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS!'
    ):
        registroMov(
            -1, 'COMPRA', 5,
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            10
        )


def testRegistroProdutoNaoEncontrado(banco):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='PRODUTO NÃO ENCONTRADO'):
        registroMov(
            999, 'COMPRA', 5,
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            10
        )


@pytest.mark.parametrize(
    "tipo",
    ['COMPRA', 'DEVOLUÇÃO', 'VENDA', 'PERCA', 'TRANSFERÊNCIA']
)
def testRegistroQuantidadeInvalida(banco, tipo):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO QUANTIDADE ACEITA APENAS VALORES INTEIROS E POSITIVOS'
    ):
        registroMov(
            1, tipo, 'INVÁLIDO',
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            10
        )


@pytest.mark.parametrize(
    "tipo",
    ['COMPRA', 'DEVOLUÇÃO', 'VENDA', 'PERCA', 'TRANSFERÊNCIA']
)
def testRegistroQuantidadeNegativa(banco, tipo):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO QUANTIDADE ACEITA APENAS VALORES INTEIROS E POSITIVOS'
    ):
        registroMov(
            1, tipo, -1,
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            10
        )

@pytest.mark.parametrize(
    "tipo",
    ['COMPRA', 'DEVOLUÇÃO', 'VENDA', 'TRANSFERÊNCIA']
    #.mark.parametrize é usado
)
def testRegistroValorInvalido(banco, tipo):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO VALOR ENVOLVIDO ACEITA APENAS VALORES INTEIROS E POSITIVOS!'
    ):
        registroMov(
            1, tipo, 5,
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            'INVÁLIDO'
        )

@pytest.mark.parametrize(
    "tipo",
    ['COMPRA', 'DEVOLUÇÃO', 'TRANSFERÊNCIA']
    #Podemos criar um parametro e atribuir diferentes valores para ele
    #assim podemos realizar o mesmo teste com diferentes entradas, sem precisar criar um teste para cada caso
)
def testRegistroSaldoInsuficiente(banco, tipo):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='SALDO INSUFICIENTE'):
        registroMov(
            1, tipo, 5,
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            2000
        )

@pytest.mark.parametrize(
    "tipo",
    ['VENDA', 'PERCA', 'TRANSFERÊNCIA']
)
def testRegistroEstoqueInsuficiente(banco, tipo):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='ESTOQUE INSUFICIENTE'):
        registroMov(
            1, tipo, 999,
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            10
        )

def testRegistroOperacaoInvalida(banco):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO OPERAÇÃO ACEITA APENAS OPERAÇÕES VÁLIDAS!'
    ):
        registroMov(
            1, 'OPERACAO_INVALIDA', 5,
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            10
        )


def testRegistroSemPermissao(banco):
    conexao, cursor = banco

    with pytest.raises(
        PermissionError,
        match='USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO'
    ):
        registroMov(
            1, 'COMPRA', 5,
            cursor, conexao, 'ROBERTO', 'CARGO INVÁLIDO',
            10
        )


# ---------------------------------------------------------------------------
# Casos complementares
# ---------------------------------------------------------------------------

TIPOS = ['COMPRA', 'DEVOLUÇÃO', 'VENDA', 'PERCA', 'TRANSFERÊNCIA']


@pytest.mark.parametrize("tipo", TIPOS)
def testRegistroIdInvalidoTodosTipos(banco, tipo):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS!'
    ):
        registroMov(
            'ID INVÁLIDO', tipo, 5,
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            10
        )


@pytest.mark.parametrize("tipo", TIPOS)
@pytest.mark.parametrize("idProduto", [0, -1])
def testRegistroIdZeroOuNegativoTodosTipos(banco, tipo, idProduto):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS!'
    ):
        registroMov(
            idProduto, tipo, 5,
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            10
        )


@pytest.mark.parametrize("tipo", TIPOS)
def testRegistroProdutoNaoEncontradoTodosTipos(banco, tipo):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='PRODUTO NÃO ENCONTRADO'):
        registroMov(
            999, tipo, 5,
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            10
        )


@pytest.mark.parametrize("tipo", TIPOS)
def testRegistroQuantidadeZero(banco, tipo):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO QUANTIDADE ACEITA APENAS VALORES INTEIROS E POSITIVOS'
    ):
        registroMov(
            1, tipo, 0,
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            10
        )


@pytest.mark.parametrize(
    "tipo",
    ['COMPRA', 'DEVOLUÇÃO', 'VENDA', 'TRANSFERÊNCIA']
)
def testRegistroValorNegativo(banco, tipo):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO VALOR ENVOLVIDO ACEITA APENAS VALORES INTEIROS E POSITIVOS!'
    ):
        registroMov(
            1, tipo, 5,
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            -10
        )


@pytest.mark.parametrize(
    "tipo, quantidadeFinal, saldoFinal, operacao",
    [
        ('COMPRA', 25, 99000, 'SAÍDA'),
        ('DEVOLUÇÃO', 25, 99000, 'SAÍDA'),
        ('VENDA', 15, 101000, 'ENTRADA'),
        ('TRANSFERÊNCIA', 15, 99000, 'SAÍDA'),
    ]
)
def testRegistroGeraHistoricoDeSaldo(banco, tipo, quantidadeFinal, saldoFinal, operacao):
    conexao, cursor = banco

    registroMov(
        1, tipo, 5,
        cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
        10
    )

    cursor.execute("SELECT quantidade FROM produtos WHERE id = 1")
    produto = cursor.fetchone()

    cursor.execute("SELECT valor FROM saldo WHERE id = 1")
    saldo = cursor.fetchone()[0]

    cursor.execute("SELECT valor, operacao, quemFez FROM histSaldo")
    trans = cursor.fetchall()

    assert produto[0] == quantidadeFinal
    assert saldo == saldoFinal
    assert len(trans) == 1
    assert trans[0] == (1000, operacao, 'ROBERTO')


@pytest.mark.parametrize(
    "tipo, quantidadeFinal",
    [
        ('COMPRA', 25),
        ('DEVOLUÇÃO', 25),
        ('VENDA', 15),
        ('TRANSFERÊNCIA', 15),
    ]
)
def testRegistroSemValorEnvolvido(banco, tipo, quantidadeFinal):
    conexao, cursor = banco

    registroMov(
        1, tipo, 5,
        cursor, conexao, 'ROBERTO', 'ADMINISTRADOR'
    )

    cursor.execute("SELECT quantidade FROM produtos WHERE id = 1")
    produto = cursor.fetchone()

    cursor.execute("SELECT valor FROM saldo WHERE id = 1")
    saldo = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM histSaldo")
    historico_saldo = cursor.fetchone()[0]

    movimentacao = consultaMov(cursor)

    assert produto[0] == quantidadeFinal
    assert saldo == 100000
    assert historico_saldo == 0
    assert movimentacao[0][6] == 0


def testRegistroPercaValorEnvolvidoPadrao(banco):
    conexao, cursor = banco

    registroMov(
        1, 'PERCA', 5,
        cursor, conexao, 'ROBERTO', 'ADMINISTRADOR'
    )

    cursor.execute("SELECT valor FROM saldo WHERE id = 1")
    saldo = cursor.fetchone()[0]

    movimentacao = consultaMov(cursor)

    assert saldo == 100000
    assert movimentacao[0][6] == 0


def testRegistroValorDecimal(banco):
    conexao, cursor = banco

    registroMov(
        1, 'COMPRA', 5,
        cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
        '10.55'
    )

    cursor.execute("SELECT valor FROM saldo WHERE id = 1")
    saldo = cursor.fetchone()[0]

    movimentacao = consultaMov(cursor)

    assert saldo == 98945
    assert movimentacao[0][6] == 1055


def testRegistroIdEQuantidadeComoTexto(banco):
    conexao, cursor = banco

    registroMov(
        '1', 'COMPRA', '5',
        cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
        '10'
    )

    cursor.execute("SELECT quantidade FROM produtos WHERE id = 1")
    produto = cursor.fetchone()

    assert produto[0] == 25


@pytest.mark.parametrize(
    "tipo",
    ['COMPRA', 'DEVOLUÇÃO', 'TRANSFERÊNCIA']
)
def testRegistroValorIgualAoSaldo(banco, tipo):
    conexao, cursor = banco

    registroMov(
        1, tipo, 5,
        cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
        1000
    )

    cursor.execute("SELECT valor FROM saldo WHERE id = 1")
    saldo = cursor.fetchone()[0]

    assert saldo == 0


@pytest.mark.parametrize(
    "tipo",
    ['VENDA', 'PERCA', 'TRANSFERÊNCIA']
)
def testRegistroQuantidadeIgualAoEstoque(banco, tipo):
    conexao, cursor = banco

    registroMov(
        1, tipo, 20,
        cursor, conexao, 'ROBERTO', 'ADMINISTRADOR'
    )

    cursor.execute("SELECT quantidade FROM produtos WHERE id = 1")
    produto = cursor.fetchone()

    assert produto[0] == 0


def testRegistroVendaNaoVerificaSaldo(banco):
    conexao, cursor = banco

    #venda é ENTRADA de dinheiro, então não depende do saldo atual
    registroMov(
        1, 'VENDA', 5,
        cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
        2000
    )

    cursor.execute("SELECT valor FROM saldo WHERE id = 1")
    saldo = cursor.fetchone()[0]

    assert saldo == 300000


@pytest.mark.parametrize(
    "tipo, quantidade, valor",
    [
        ('COMPRA', 5, 2000),
        ('DEVOLUÇÃO', 5, 2000),
        ('TRANSFERÊNCIA', 5, 2000),
        ('VENDA', 999, 10),
        ('PERCA', 999, 0),
    ]
)
def testRegistroComErroNaoAlteraBanco(banco, tipo, quantidade, valor):
    conexao, cursor = banco

    with pytest.raises(ValueError):
        registroMov(
            1, tipo, quantidade,
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            valor
        )

    cursor.execute("SELECT quantidade FROM produtos WHERE id = 1")
    produto = cursor.fetchone()

    cursor.execute("SELECT valor FROM saldo WHERE id = 1")
    saldo = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM historicoMovimentacao")
    movimentacoes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM histSaldo")
    historico_saldo = cursor.fetchone()[0]

    assert produto[0] == 20
    assert saldo == 100000
    assert movimentacoes == 0
    assert historico_saldo == 0


def testRegistroVariasMovimentacoes(banco):
    conexao, cursor = banco

    registroMov(1, 'COMPRA', 10, cursor, conexao, 'ROBERTO', 'ADMINISTRADOR', 50)
    registroMov(1, 'VENDA', 5, cursor, conexao, 'JOAO', 'GERENTE', 30)
    registroMov(1, 'PERCA', 2, cursor, conexao, 'MARIA', 'ESTOQUISTA')

    cursor.execute("SELECT quantidade FROM produtos WHERE id = 1")
    produto = cursor.fetchone()

    cursor.execute("SELECT valor FROM saldo WHERE id = 1")
    saldo = cursor.fetchone()[0]

    movimentacao = consultaMov(cursor)

    assert produto[0] == 23
    assert saldo == 98000
    assert len(movimentacao) == 3
    assert [m[2] for m in movimentacao] == ['COMPRA', 'VENDA', 'PERCA']
    assert [m[5] for m in movimentacao] == ['ROBERTO', 'JOAO', 'MARIA']


@pytest.mark.parametrize(
    "cargo",
    ['ADMINISTRADOR', 'GERENTE', 'ESTOQUISTA']
)
def testRegistroCargosPermitidos(banco, cargo):
    conexao, cursor = banco

    registroMov(
        1, 'COMPRA', 5,
        cursor, conexao, 'ROBERTO', cargo,
        10
    )

    movimentacao = consultaMov(cursor)
    assert len(movimentacao) == 1


@pytest.mark.parametrize(
    "cargo",
    ['FINANCEIRO', 'CONSULTA', 'CARGO INVÁLIDO', '']
)
def testRegistroCargosSemPermissao(banco, cargo):
    conexao, cursor = banco

    with pytest.raises(
        PermissionError,
        match='USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO'
    ):
        registroMov(
            1, 'COMPRA', 5,
            cursor, conexao, 'ROBERTO', cargo,
            10
        )

    cursor.execute("SELECT quantidade FROM produtos WHERE id = 1")
    produto = cursor.fetchone()
    assert produto[0] == 20

# ---------------------------------------------------------------------------
# Exceções próprias
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tipo", TIPOS)
def testRegistroProdutoNaoEncontradoLancaNaoEncontrado(banco, tipo):
    conexao, cursor = banco

    with pytest.raises(NaoEncontradoError, match='PRODUTO NÃO ENCONTRADO'):
        registroMov(
            999, tipo, 5,
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            10
        )


@pytest.mark.parametrize(
    "idProduto, tipo, quantidade, valor",
    [
        ('ID INVÁLIDO', 'COMPRA', 5, 10),
        (1, 'COMPRA', 'INVÁLIDO', 10),
        (1, 'COMPRA', 5, 'INVÁLIDO'),
        (1, 'COMPRA', 5, 2000),
        (1, 'VENDA', 999, 10),
        (1, 'OPERACAO_INVALIDA', 5, 10),
    ]
    #validação, saldo e estoque insuficientes continuam sendo 400
)
def testRegistroErrosContinuamValueError(banco, idProduto, tipo, quantidade, valor):
    conexao, cursor = banco

    with pytest.raises(ValueError) as erro:
        registroMov(
            idProduto, tipo, quantidade,
            cursor, conexao, 'ROBERTO', 'ADMINISTRADOR',
            valor
        )

    assert type(erro.value) is ValueError