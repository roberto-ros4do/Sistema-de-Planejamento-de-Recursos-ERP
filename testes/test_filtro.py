import sqlite3
import pytest

from servicos.filtro import (
    filtragemProdutos,
    filtragemMov,
    filtragemMovRel,
    filtragemSaldo
)


@pytest.fixture
def banco():
    conexao = sqlite3.connect(":memory:")
    cursor = conexao.cursor()

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
        CREATE TABLE histSaldo(
            id INTEGER PRIMARY KEY,
            valor INTEGER NOT NULL,
            operacao TEXT NOT NULL,
            quemFez TEXT NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL
        )
    """)

    produtos = [
        (1, 'Coca Cola', 20, 600, '2026/10/01', '10:00', 'ROBERTO'),
        (2, 'Pepsi', 10, 500, '2026/10/02', '11:00', 'JOAO'),
        (3, 'Guarana', 30, 800, '2026/10/03', '12:00', 'ROBERTO'),
    ]

    cursor.executemany("""
        INSERT INTO produtos
        (id, nome, quantidade, preco, data, hora, quemFez)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, produtos)

    movimentacoes = [
        (1, 'Coca Cola', 1, 'COMPRA', 5, '2026/10/01', '10:00', 'ROBERTO', 1000),
        (2, 'Pepsi', 2, 'VENDA', 3, '2026/10/02', '11:00', 'JOAO', 1500),
        (3, 'Guarana', 3, 'PERCA', 2, '2026/10/03', '12:00', 'ROBERTO', 0),
    ]

    cursor.executemany("""
        INSERT INTO historicoMovimentacao
        (id, produto, idProduto, tipo, quantidade, data, hora, quemFez, valorEnvolvido)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, movimentacoes)

    saldo = [
        (1, 1000, 'SAÍDA', 'ROBERTO', '2026/10/01', '10:00'),
        (2, 1500, 'ENTRADA', 'JOAO', '2026/10/02', '11:00'),
    ]

    cursor.executemany("""
        INSERT INTO histSaldo
        (id, valor, operacao, quemFez, data, hora)
        VALUES (?, ?, ?, ?, ?, ?)
    """, saldo)

    conexao.commit()

    yield conexao, cursor

    conexao.close()


def testFiltragemProdutosPorId(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('', '', '', '', cursor, id='1')

    assert produtos == [(1, 'Coca Cola', 600, 20, '2026/10/01', 'ROBERTO')]


def testFiltragemProdutosIdInvalido(banco):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS'
    ):
        filtragemProdutos('', '', '', '', cursor, id='INVÁLIDO')


def testFiltragemProdutosIdNegativo(banco):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS'
    ):
        filtragemProdutos('', '', '', '', cursor, id='-1')


def testFiltragemProdutosPorNome(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('', '', '', '', cursor, n='coca')

    assert len(produtos) == 1
    assert produtos[0][1] == 'Coca Cola'


def testFiltragemProdutosPorQuemCadastrou(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('', '', '', '', cursor, quemCad='roberto')

    assert len(produtos) == 2
    assert produtos[0][5] == 'ROBERTO'
    assert produtos[1][5] == 'ROBERTO'


def testFiltragemProdutosPorFaixaDePreco(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('5', '6', '', '', cursor)

    assert len(produtos) == 2
    assert produtos[0][1] == 'Coca Cola'
    assert produtos[1][1] == 'Pepsi'


def testFiltragemProdutosTrocaFaixaDePreco(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('8', '5', '', '', cursor)

    assert len(produtos) == 3


def testFiltragemProdutosPorEstoque(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('', '', '20', '30', cursor)

    assert len(produtos) == 2
    assert produtos[0][1] == 'Coca Cola'
    assert produtos[1][1] == 'Guarana'


def testFiltragemProdutosEstoqueInvalido(banco):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO ESTOQUE ACEITA APENAS VALORES INTEIROS E POSITIVOS'
    ):
        filtragemProdutos('', '', 'INVÁLIDO', '', cursor)


def testFiltragemProdutosValorInvalido(banco):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0'
    ):
        filtragemProdutos('INVÁLIDO', '10', '', '', cursor)


def testFiltragemProdutosSemResultado(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('', '', '', '', cursor, n='ProdutoInexistente')

    assert produtos == []


def testFiltragemProdutosEstoqueRelatorio(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('', '', '', '', cursor, estoq=True)

    assert produtos[0] == (1, 'Coca Cola', 20)
    assert len(produtos[0]) == 3


def testFiltragemProdutosRetornaQueryRelatorio(banco):
    conexao, cursor = banco

    query, parametros = filtragemProdutos(
        '5', '10', '10', '30', cursor,
        n='cola',
        quemCad='roberto',
        f='REL'
    )

    assert 'preco >= ?' in query
    assert 'preco <= ?' in query
    assert 'quantidade >= ?' in query
    assert 'quantidade <= ?' in query
    assert 'LOWER(nome) LIKE LOWER(?)' in query
    assert 'LOWER(quemFez) LIKE LOWER(?)' in query
    assert len(parametros) == 6


def testFiltragemMovPorId(banco):
    conexao, cursor = banco

    historico = filtragemMov(
        '', '', '1', '', '', '', '',
        '', '', cursor, ''
    )

    assert len(historico) == 1
    assert historico[0][0] == 'Coca Cola'
    assert historico[0][2] == 'COMPRA'


def testFiltragemMovIdInvalido(banco):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS'
    ):
        filtragemMov(
            '', '', 'INVÁLIDO', '', '', '', '',
            '', '', cursor, ''
        )


def testFiltragemMovPorQuantidade(banco):
    conexao, cursor = banco

    historico = filtragemMov(
        '', '', '', '3', '5', '', '',
        '', '', cursor, ''
    )

    assert len(historico) == 2
    assert historico[0][3] == 5
    assert historico[1][3] == 3


def testFiltragemMovPorValor(banco):
    conexao, cursor = banco

    historico = filtragemMov(
        '', '', '', '', '', '10', '15',
        '', '', cursor, ''
    )

    assert len(historico) == 2


def testFiltragemMovPorNomeEUsuario(banco):
    conexao, cursor = banco

    historico = filtragemMov(
        'Coca', 'ROBERTO', '', '', '', '', '',
        '', '', cursor, ''
    )

    assert len(historico) == 1
    assert historico[0][0] == 'Coca Cola'
    assert historico[0][5] == 'ROBERTO'


def testFiltragemMovPorOperacao(banco):
    conexao, cursor = banco

    historico = filtragemMov(
        '', '', '', '', '', '', '',
        '', '', cursor, 'VENDA'
    )

    assert len(historico) == 1
    assert historico[0][2] == 'VENDA'


def testFiltragemMovOperacaoInvalida(banco):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO OPERAÇÃO ACEITA APENAS OPERAÇÕES VÁLIDAS!'
    ):
        filtragemMov(
            '', '', '', '', '', '', '',
            '', '', cursor, 'INVALIDA'
        )


def testFiltragemMovPorData(banco):
    conexao, cursor = banco

    historico = filtragemMov(
        '', '', '', '', '', '', '',
        '2026/10/01', '2026/10/02', cursor, ''
    )

    assert len(historico) == 2


def testFiltragemMovDataInvalida(banco):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!'
    ):
        filtragemMov(
            '', '', '', '', '', '', '',
            '01/10/2026', '02/10/2026', cursor, ''
        )


def testFiltragemMovRelRetornaQuery(banco):
    conexao, cursor = banco

    query, parametros = filtragemMovRel(
    'ROBERTO', '2', '5', '1', '15',
    '2026/10/01', '2026/10/03',
    cursor, 'COMPRA'
)

    assert 'data BETWEEN ? AND ?' in query
    assert 'quantidade >= ?' in query
    assert 'quantidade <= ?' in query
    assert 'valorEnvolvido >= ?' in query
    assert 'valorEnvolvido <= ?' in query
    assert 'LOWER(quemFez) LIKE LOWER(?)' in query
    assert 'tipo = ?' in query
    assert len(parametros) == 8


def testFiltragemMovRelDataInvalida(banco):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!'
    ):
        filtragemMovRel(
            '', '', '', '', '',
            '01/10/2026', '03/10/2026',
            cursor, ''
        )


def testFiltragemSaldoPorUsuario(banco):
    conexao, cursor = banco

    historico = filtragemSaldo(
        'ROBERTO', '', '', '',
        '', '', cursor
    )

    assert len(historico) == 1
    assert historico[0][2] == 'ROBERTO'


def testFiltragemSaldoPorOperacao(banco):
    conexao, cursor = banco

    historico = filtragemSaldo(
        '', 'SAÍDA', '', '',
        '', '', cursor
    )

    assert len(historico) == 1
    assert historico[0][1] == 'SAÍDA'


def testFiltragemSaldoPorValor(banco):
    conexao, cursor = banco

    historico = filtragemSaldo(
    '', '', '11', '15',
    '', '', cursor
)

    assert len(historico) == 1
    assert historico[0][0] == 1500


def testFiltragemSaldoPorData(banco):
    conexao, cursor = banco

    historico = filtragemSaldo(
        '', '', '', '',
        '2026/10/01', '2026/10/02', cursor
    )

    assert len(historico) == 2


def testFiltragemSaldoDataInvalida(banco):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!'
    ):
        filtragemSaldo(
            '', '', '', '',
            '01/10/2026', '02/10/2026', cursor
        )


def testFiltragemSaldoRetornaQueryRelatorio(banco):
    conexao, cursor = banco

    query, parametros = filtragemSaldo(
        'ROBERTO', 'SAÍDA', '5', '15',
        '2026/10/01', '2026/10/03',
        cursor, f='REL'
    )

    assert 'data BETWEEN ? AND ?' in query
    assert 'LOWER(quemFez) LIKE LOWER(?)' in query
    assert 'operacao = ?' in query
    assert 'valor >= ?' in query
    assert 'valor <= ?' in query
    assert len(parametros) == 6


# ---------------------------------------------------------------------------
# filtragemProdutos — casos complementares
# ---------------------------------------------------------------------------

def testFiltragemProdutosPorData(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos(
        '', '', '', '', cursor,
        dataInicial='2026/10/01',
        dataUltima='2026/10/02'
    )

    assert len(produtos) == 2
    assert produtos[0][1] == 'Coca Cola'
    assert produtos[1][1] == 'Pepsi'


def testFiltragemProdutosApenasUmaDataIgnoraFiltro(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('', '', '', '', cursor, dataInicial='2026/10/01')

    assert len(produtos) == 3


def testFiltragemProdutosPorDataRetornaQueryRelatorio(banco):
    conexao, cursor = banco

    query, parametros = filtragemProdutos(
        '', '', '', '', cursor,
        dataInicial='2026/10/01',
        dataUltima='2026/10/03',
        f='REL'
    )

    assert 'data BETWEEN ? AND ?' in query
    assert parametros == ['2026/10/01', '2026/10/03']


def testFiltragemProdutosIdNaoEncontrado(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('', '', '', '', cursor, id='999')

    assert produtos == []


def testFiltragemProdutosIdComEstoque(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('', '', '', '', cursor, id='1', estoq=True)

    assert produtos == [(1, 'Coca Cola', 20)]


def testFiltragemProdutosApenasValorMinimo(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('6', '', '', '', cursor)

    assert len(produtos) == 2
    assert produtos[0][1] == 'Coca Cola'
    assert produtos[1][1] == 'Guarana'


def testFiltragemProdutosApenasValorMaximo(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('', '6', '', '', cursor)

    assert len(produtos) == 2
    assert produtos[0][1] == 'Coca Cola'
    assert produtos[1][1] == 'Pepsi'


def testFiltragemProdutosApenasEstoqueMinimo(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('', '', '20', '', cursor)

    assert len(produtos) == 2
    assert produtos[0][1] == 'Coca Cola'
    assert produtos[1][1] == 'Guarana'


def testFiltragemProdutosApenasEstoqueMaximo(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('', '', '', '10', cursor)

    assert len(produtos) == 1
    assert produtos[0][1] == 'Pepsi'


def testFiltragemProdutosTrocaFaixaDeEstoque(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('', '', '30', '20', cursor)

    assert len(produtos) == 2
    assert produtos[0][1] == 'Coca Cola'
    assert produtos[1][1] == 'Guarana'


def testFiltragemProdutosTrocaFaixaRetornaParametrosOrdenados(banco):
    conexao, cursor = banco

    query, parametros = filtragemProdutos('8', '5', '30', '20', cursor, f='REL')

    assert parametros == [500, 800, 20, 30]


@pytest.mark.parametrize(
    "valorMin, valorMax, mensagem",
    [
        ('INVÁLIDO', '', 'CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0'),
        ('', 'INVÁLIDO', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('5', 'INVÁLIDO', 'CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0'),
        ('0', '', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('', '0', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('-5', '', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('', '-5', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('0', '5', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
    ]
    #cada tupla testa um caminho diferente da validação de preço (min, max ou os dois juntos)
)
def testFiltragemProdutosValorInvalidoCasos(banco, valorMin, valorMax, mensagem):
    conexao, cursor = banco

    with pytest.raises(ValueError, match=mensagem):
        filtragemProdutos(valorMin, valorMax, '', '', cursor)


@pytest.mark.parametrize(
    "estoqMin, estoqMax, mensagem",
    [
        ('', 'INVÁLIDO', 'CAMPO ESTOQUE ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS'),
        ('10', 'INVÁLIDO', 'CAMPO ESTOQUE ACEITA APENAS VALORES INTEIROS E POSITIVOS'),
        ('INVÁLIDO', '10', 'CAMPO ESTOQUE ACEITA APENAS VALORES INTEIROS E POSITIVOS'),
        ('0', '', 'CAMPO ESTOQUE ACEITA APENAS NÚMEROS INTEIROS POSITIVOS'),
        ('', '0', 'CAMPO ESTOQUE ACEITA APENAS NÚMEROS INTEIROS POSITIVOS'),
        ('-5', '', 'CAMPO ESTOQUE ACEITA APENAS NÚMEROS INTEIROS POSITIVOS'),
        ('', '-5', 'CAMPO ESTOQUE ACEITA APENAS NÚMEROS INTEIROS POSITIVOS'),
        ('2.5', '', 'CAMPO ESTOQUE ACEITA APENAS VALORES INTEIROS E POSITIVOS'),
    ]
)
def testFiltragemProdutosEstoqueInvalidoCasos(banco, estoqMin, estoqMax, mensagem):
    conexao, cursor = banco

    with pytest.raises(ValueError, match=mensagem):
        filtragemProdutos('', '', estoqMin, estoqMax, cursor)


# ---------------------------------------------------------------------------
# filtragemMov — casos complementares
# ---------------------------------------------------------------------------

def testFiltragemMovIdNaoEncontrado(banco):
    conexao, cursor = banco

    historico = filtragemMov(
        '', '', '999', '', '', '', '',
        '', '', cursor, ''
    )

    assert historico == []


def testFiltragemMovSemFiltrosRetornaTudo(banco):
    conexao, cursor = banco

    historico = filtragemMov(
        '', '', '', '', '', '', '',
        '', '', cursor, ''
    )

    assert len(historico) == 3


def testFiltragemMovSemResultado(banco):
    conexao, cursor = banco

    historico = filtragemMov(
        'ProdutoInexistente', '', '', '', '', '', '',
        '', '', cursor, ''
    )

    assert historico == []


def testFiltragemMovTrocaFaixaDeQuantidade(banco):
    conexao, cursor = banco

    historico = filtragemMov(
        '', '', '', '5', '3', '', '',
        '', '', cursor, ''
    )

    assert len(historico) == 2
    assert historico[0][3] == 5
    assert historico[1][3] == 3


def testFiltragemMovApenasQuantidadeMinima(banco):
    conexao, cursor = banco

    historico = filtragemMov(
        '', '', '', '3', '', '', '',
        '', '', cursor, ''
    )

    assert len(historico) == 2


def testFiltragemMovApenasQuantidadeMaxima(banco):
    conexao, cursor = banco

    historico = filtragemMov(
        '', '', '', '', '2', '', '',
        '', '', cursor, ''
    )

    assert len(historico) == 1
    assert historico[0][0] == 'Guarana'


def testFiltragemMovTrocaFaixaDeValor(banco):
    conexao, cursor = banco

    historico = filtragemMov(
        '', '', '', '', '', '15', '10',
        '', '', cursor, ''
    )

    assert len(historico) == 2


def testFiltragemMovApenasValorMinimo(banco):
    conexao, cursor = banco

    historico = filtragemMov(
        '', '', '', '', '', '12', '',
        '', '', cursor, ''
    )

    assert len(historico) == 1
    assert historico[0][6] == 1500


def testFiltragemMovApenasValorMaximo(banco):
    conexao, cursor = banco

    historico = filtragemMov(
        '', '', '', '', '', '', '12',
        '', '', cursor, ''
    )

    assert len(historico) == 2
    assert historico[0][6] == 1000
    assert historico[1][6] == 0


def testFiltragemMovDataEOperacao(banco):
    conexao, cursor = banco

    historico = filtragemMov(
        '', '', '', '', '', '', '',
        '2026/10/01', '2026/10/03', cursor, 'PERCA'
    )

    assert len(historico) == 1
    assert historico[0][2] == 'PERCA'


@pytest.mark.parametrize(
    "tipo",
    ['COMPRA', 'VENDA', 'TRANSFERÊNCIA', 'DEVOLUÇÃO', 'PERCA', 'CADASTRO', 'DELETAÇÃO']
)
def testFiltragemMovOperacoesValidas(banco, tipo):
    conexao, cursor = banco

    historico = filtragemMov(
        '', '', '', '', '', '', '',
        '', '', cursor, tipo
    )

    for mov in historico:
        assert mov[2] == tipo


@pytest.mark.parametrize(
    "unidMin, unidMax, mensagem",
    [
        ('INVÁLIDO', '', 'CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!'),
        ('', 'INVÁLIDO', 'CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!'),
        ('INVÁLIDO', '5', 'CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E MAIORES QUE 0'),
        ('2', 'INVÁLIDO', 'CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E MAIORES QUE 0'),
        ('0', '', 'CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!'),
        ('', '0', 'CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!'),
        ('-1', '', 'CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!'),
        ('', '-1', 'CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!'),
    ]
)
def testFiltragemMovUnidadesInvalidas(banco, unidMin, unidMax, mensagem):
    conexao, cursor = banco

    with pytest.raises(ValueError, match=mensagem):
        filtragemMov(
            '', '', '', unidMin, unidMax, '', '',
            '', '', cursor, ''
        )


@pytest.mark.parametrize(
    "valorMin, valorMax, mensagem",
    [
        ('INVÁLIDO', '', 'CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0'),
        ('', 'INVÁLIDO', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('INVÁLIDO', '10', 'CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0'),
        ('10', 'INVÁLIDO', 'CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0'),
        ('0', '', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('', '0', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('-1', '', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('', '-1', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
    ]
)
def testFiltragemMovValorInvalido(banco, valorMin, valorMax, mensagem):
    conexao, cursor = banco

    with pytest.raises(ValueError, match=mensagem):
        filtragemMov(
            '', '', '', '', '', valorMin, valorMax,
            '', '', cursor, ''
        )


@pytest.mark.parametrize(
    "dataInicial, dataUltima",
    [
        ('01/10/2026', '2026/10/02'),
        ('2026/10/01', '02/10/2026'),
        ('2026-10-01', '2026-10-02'),
        ('2026/13/01', '2026/10/02'),
    ]
)
def testFiltragemMovDataInvalidaCasos(banco, dataInicial, dataUltima):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!'):
        filtragemMov(
            '', '', '', '', '', '', '',
            dataInicial, dataUltima, cursor, ''
        )


# ---------------------------------------------------------------------------
# filtragemMovRel — casos complementares
# ---------------------------------------------------------------------------

def testFiltragemMovRelSemFiltros(banco):
    conexao, cursor = banco

    query, parametros = filtragemMovRel(
        '', '', '', '', '',
        '', '',
        cursor, ''
    )

    assert 'WHERE 1=1' in query
    assert 'BETWEEN' not in query
    assert parametros == []


def testFiltragemMovRelQueryExecutavel(banco):
    conexao, cursor = banco

    query, parametros = filtragemMovRel(
        'ROBERTO', '1', '10', '', '',
        '2026/10/01', '2026/10/03',
        cursor, 'COMPRA'
    )

    cursor.execute(query, parametros)
    historico = cursor.fetchall()

    assert len(historico) == 1
    assert historico[0][0] == 'Coca Cola'


def testFiltragemMovRelTrocaFaixaDeUnidades(banco):
    conexao, cursor = banco

    query, parametros = filtragemMovRel(
        '', '5', '2', '', '',
        '', '',
        cursor, ''
    )

    assert parametros == [2, 5]


def testFiltragemMovRelTrocaFaixaDeValores(banco):
    conexao, cursor = banco

    query, parametros = filtragemMovRel(
        '', '', '', '15', '1',
        '', '',
        cursor, ''
    )

    assert parametros == [100, 1500]


@pytest.mark.parametrize(
    "tipo",
    ['COMPRA', 'VENDA', 'TRANSFERÊNCIA', 'DEVOLUÇÃO', 'PERCA', 'CADASTRO', 'DELETAÇÃO']
)
def testFiltragemMovRelOperacoesValidas(banco, tipo):
    conexao, cursor = banco

    query, parametros = filtragemMovRel(
        '', '', '', '', '',
        '', '',
        cursor, tipo
    )

    assert 'tipo = ?' in query
    assert parametros == [tipo]


def testFiltragemMovRelOperacaoInvalida(banco):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='CAMPO OPERAÇÃO ACEITA APENAS OPERAÇÕES VÁLIDAS!'):
        filtragemMovRel(
            '', '', '', '', '',
            '', '',
            cursor, 'INVALIDA'
        )


@pytest.mark.parametrize(
    "unidMin, unidMax, mensagem",
    [
        ('INVÁLIDO', '', 'CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!'),
        ('', 'INVÁLIDO', 'CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!'),
        ('INVÁLIDO', '5', 'CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E MAIORES QUE 0'),
        ('2', 'INVÁLIDO', 'CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E MAIORES QUE 0'),
        ('0', '', 'CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!'),
        ('', '0', 'CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!'),
        ('-1', '', 'CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!'),
        ('', '-1', 'CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!'),
    ]
)
def testFiltragemMovRelUnidadesInvalidas(banco, unidMin, unidMax, mensagem):
    conexao, cursor = banco

    with pytest.raises(ValueError, match=mensagem):
        filtragemMovRel(
            '', unidMin, unidMax, '', '',
            '', '',
            cursor, ''
        )


@pytest.mark.parametrize(
    "valorMin, valorMax, mensagem",
    [
        ('INVÁLIDO', '', 'CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0'),
        ('', 'INVÁLIDO', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('INVÁLIDO', '10', 'CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0'),
        ('10', 'INVÁLIDO', 'CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0'),
        ('0', '', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('', '0', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('-1', '', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('', '-1', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
    ]
)
def testFiltragemMovRelValorInvalido(banco, valorMin, valorMax, mensagem):
    conexao, cursor = banco

    with pytest.raises(ValueError, match=mensagem):
        filtragemMovRel(
            '', '', '', valorMin, valorMax,
            '', '',
            cursor, ''
        )


# ---------------------------------------------------------------------------
# filtragemSaldo — casos complementares
# ---------------------------------------------------------------------------

def testFiltragemSaldoSemHistorico(banco):
    conexao, cursor = banco

    cursor.execute("DELETE FROM histSaldo")
    conexao.commit()

    historico = filtragemSaldo(
        '', '', '', '',
        '', '', cursor
    )

    assert historico == []


def testFiltragemSaldoSemHistoricoRelatorio(banco):
    conexao, cursor = banco

    cursor.execute("DELETE FROM histSaldo")
    conexao.commit()

    query, parametros = filtragemSaldo(
        '', '', '', '',
        '', '', cursor, f='REL'
    )

    assert 'WHERE 1=1' in query
    assert parametros == []


def testFiltragemSaldoSemFiltrosRetornaTudo(banco):
    conexao, cursor = banco

    historico = filtragemSaldo(
        '', '', '', '',
        '', '', cursor
    )

    assert len(historico) == 2


def testFiltragemSaldoSemResultado(banco):
    conexao, cursor = banco

    historico = filtragemSaldo(
        'USUARIO INEXISTENTE', '', '', '',
        '', '', cursor
    )

    assert historico == []


def testFiltragemSaldoTrocaFaixaDeValor(banco):
    conexao, cursor = banco

    historico = filtragemSaldo(
        '', '', '15', '5',
        '', '', cursor
    )

    assert len(historico) == 2


def testFiltragemSaldoApenasValorMinimo(banco):
    conexao, cursor = banco

    historico = filtragemSaldo(
        '', '', '11', '',
        '', '', cursor
    )

    assert len(historico) == 1
    assert historico[0][0] == 1500


def testFiltragemSaldoApenasValorMaximo(banco):
    conexao, cursor = banco

    historico = filtragemSaldo(
        '', '', '', '11',
        '', '', cursor
    )

    assert len(historico) == 1
    assert historico[0][0] == 1000


def testFiltragemSaldoSemFiltrosRelatorio(banco):
    conexao, cursor = banco

    query, parametros = filtragemSaldo(
        '', '', '', '',
        '', '', cursor, f='REL'
    )

    assert 'WHERE 1=1' in query
    assert parametros == []


@pytest.mark.parametrize(
    "valorMin, valorMax, mensagem",
    [
        ('INVÁLIDO', '', 'CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0'),
        ('', 'INVÁLIDO', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('INVÁLIDO', '10', 'CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0'),
        ('10', 'INVÁLIDO', 'CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0'),
        ('0', '', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('', '0', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('-1', '', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
        ('', '-1', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
    ]
)
def testFiltragemSaldoValorInvalido(banco, valorMin, valorMax, mensagem):
    conexao, cursor = banco

    with pytest.raises(ValueError, match=mensagem):
        filtragemSaldo(
            '', '', valorMin, valorMax,
            '', '', cursor
        )


# ---------------------------------------------------------------------------
# Testes das correções nos serviços
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "dataInicial, dataUltima",
    [
        ('01/10/2026', '2026/10/02'),
        ('2026/10/01', '02/10/2026'),
        ('2026-10-01', '2026-10-02'),
        ('2026/13/01', '2026/10/02'),
    ]
)
def testFiltragemProdutosDataInvalida(banco, dataInicial, dataUltima):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!'):
        filtragemProdutos(
            '', '', '', '', cursor,
            dataInicial=dataInicial,
            dataUltima=dataUltima
        )


def testFiltragemProdutosDataInvalidaRelatorio(banco):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!'):
        filtragemProdutos(
            '', '', '', '', cursor,
            dataInicial='01/10/2026',
            dataUltima='03/10/2026',
            f='REL'
        )


@pytest.mark.parametrize("idProd", ['0', '-1', '-10'])
def testFiltragemMovIdZeroOuNegativo(banco, idProd):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS'
    ):
        filtragemMov(
            '', '', idProd, '', '', '', '',
            '', '', cursor, ''
        )


@pytest.mark.parametrize(
    "tipo, esperado",
    [
        ('ENTRADA', 1),
        ('SAÍDA', 1),
        ('RETIRADA', 0),
    ]
)
def testFiltragemSaldoOperacoesValidas(banco, tipo, esperado):
    conexao, cursor = banco

    historico = filtragemSaldo(
        '', tipo, '', '',
        '', '', cursor
    )

    assert len(historico) == esperado
    for trans in historico:
        assert trans[1] == tipo


@pytest.mark.parametrize("tipo", ['INVALIDA', 'COMPRA', 'entrada'])
def testFiltragemSaldoOperacaoInvalida(banco, tipo):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='CAMPO OPERAÇÃO ACEITA APENAS OPERAÇÕES VÁLIDAS!'):
        filtragemSaldo(
            '', tipo, '', '',
            '', '', cursor
        )


def testFiltragemSaldoOperacaoInvalidaRelatorio(banco):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='CAMPO OPERAÇÃO ACEITA APENAS OPERAÇÕES VÁLIDAS!'):
        filtragemSaldo(
            '', 'INVALIDA', '', '',
            '', '', cursor, f='REL'
        )

# ---------------------------------------------------------------------------
# Filtro pelos tipos CADASTRO e DELETAÇÃO
# ---------------------------------------------------------------------------

def inserirCadastroEDelecao(cursor, conexao):
    cursor.executemany("""
        INSERT INTO historicoMovimentacao
        (id, produto, idProduto, tipo, quantidade, data, hora, quemFez, valorEnvolvido)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (4, 'Fanta', 4, 'CADASTRO', 15, '2026/10/04', '09:00', 'ROBERTO', 2000),
        (5, 'Fanta', 4, 'DELETAÇÃO', 0, '2026/10/05', '09:30', 'ROBERTO', 0),
    ])
    conexao.commit()


@pytest.mark.parametrize(
    "tipo, quantidade",
    [
        ('CADASTRO', 15),
        ('DELETAÇÃO', 0),
    ]
)
def testFiltragemMovPorCadastroEDelecao(banco, tipo, quantidade):
    conexao, cursor = banco
    inserirCadastroEDelecao(cursor, conexao)

    historico = filtragemMov(
        '', '', '', '', '', '', '',
        '', '', cursor, tipo
    )

    assert len(historico) == 1
    assert historico[0][0] == 'Fanta'
    assert historico[0][2] == tipo
    assert historico[0][3] == quantidade


@pytest.mark.parametrize("tipo", ['CADASTRO', 'DELETAÇÃO'])
def testFiltragemMovRelCadastroEDelecaoExecutavel(banco, tipo):
    conexao, cursor = banco
    inserirCadastroEDelecao(cursor, conexao)

    query, parametros = filtragemMovRel(
        '', '', '', '', '',
        '', '',
        cursor, tipo
    )

    cursor.execute(query, parametros)
    historico = cursor.fetchall()

    assert len(historico) == 1
    assert historico[0][2] == tipo


@pytest.mark.parametrize("tipo", ['cadastro', 'DELETACAO', 'EXCLUSÃO'])
def testFiltragemMovTipoParecidoInvalido(banco, tipo):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='CAMPO OPERAÇÃO ACEITA APENAS OPERAÇÕES VÁLIDAS!'):
        filtragemMov(
            '', '', '', '', '', '', '',
            '', '', cursor, tipo
        )

# ---------------------------------------------------------------------------
# Listas vazias em vez de erro
# ---------------------------------------------------------------------------

def testFiltragemProdutosTabelaVazia(banco):
    conexao, cursor = banco

    cursor.execute("DELETE FROM produtos")
    conexao.commit()

    produtos = filtragemProdutos('', '', '', '', cursor)

    assert produtos == []


def testFiltragemProdutosSemResultadoComEstoque(banco):
    conexao, cursor = banco

    produtos = filtragemProdutos('', '', '100', '', cursor, estoq=True)

    assert produtos == []


def testFiltragemSaldoSemHistoricoComFiltros(banco):
    conexao, cursor = banco

    cursor.execute("DELETE FROM histSaldo")
    conexao.commit()

    historico = filtragemSaldo(
        'ROBERTO', 'SAÍDA', '5', '15',
        '2026/10/01', '2026/10/03', cursor
    )

    assert historico == []


@pytest.mark.parametrize(
    "tip, valorMin, dataInicial, dataUltima, mensagem",
    [
        ('', '', '01/10/2026', '02/10/2026', 'AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!'),
        ('INVALIDA', '', '', '', 'CAMPO OPERAÇÃO ACEITA APENAS OPERAÇÕES VÁLIDAS!'),
        ('', '0', '', '', 'CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS'),
    ]
    #com o histórico vazio, os erros de validação continuam sendo lançados
)
def testFiltragemSaldoSemHistoricoContinuaValidando(banco, tip, valorMin, dataInicial, dataUltima, mensagem):
    conexao, cursor = banco

    cursor.execute("DELETE FROM histSaldo")
    conexao.commit()

    with pytest.raises(ValueError, match=mensagem):
        filtragemSaldo(
            '', tip, valorMin, '',
            dataInicial, dataUltima, cursor
        )