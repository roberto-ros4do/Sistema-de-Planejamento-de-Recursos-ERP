import sqlite3
import pytest
import pandas as pd

from servicos.relatorios import lerDados, gerarRel


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

    cursor.execute("""
        INSERT INTO produtos
        (id, nome, quantidade, preco, data, hora, quemFez)
        VALUES
        (1, 'Coca Cola', 20, 600, '2026/10/01', '10:00', 'ROBERTO'),
        (2, 'Pepsi', 10, 500, '2026/10/02', '11:00', 'JOAO')
    """)

    cursor.execute("""
        INSERT INTO historicoMovimentacao
        (id, produto, idProduto, tipo, quantidade, data, hora, quemFez, valorEnvolvido)
        VALUES
        (1, 'Coca Cola', 1, 'COMPRA', 5, '2026/10/01', '10:00', 'ROBERTO', 1000),
        (2, 'Pepsi', 2, 'VENDA', 3, '2026/10/02', '11:00', 'JOAO', 1500)
    """)

    cursor.execute("""
        INSERT INTO histSaldo
        (id, valor, operacao, quemFez, data, hora)
        VALUES
        (1, 1000, 'SAÍDA', 'ROBERTO', '2026/10/01', '10:00'),
        (2, 1500, 'ENTRADA', 'JOAO', '2026/10/02', '11:00')
    """)

    conexao.commit()

    yield conexao, cursor

    conexao.close()


def testLerDadosProdutos(banco):
    conexao, cursor = banco

    df = lerDados('1', conexao)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == [
        'id', 'nome', 'preco', 'quantidade', 'data', 'quemFez'
    ]
    assert df.iloc[0]['nome'] == 'Coca Cola'


def testLerDadosMovimentacoes(banco):
    conexao, cursor = banco

    df = lerDados('2', conexao)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert 'produto' in df.columns
    assert 'tipo' in df.columns
    assert df.iloc[0]['tipo'] == 'COMPRA'


def testLerDadosSaldo(banco):
    conexao, cursor = banco

    df = lerDados('3', conexao)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == [
        'valor', 'operacao', 'quemFez', 'data', 'hora'
    ]


def testLerDadosEstoque(banco):
    conexao, cursor = banco

    df = lerDados('4', conexao)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ['id', 'nome', 'quantidade']


def testLerDadosComQuery(banco):
    conexao, cursor = banco

    query = "SELECT id, nome FROM produtos WHERE id = ?"
    df = lerDados('1', conexao, query, (1,))

    assert len(df) == 1
    assert df.iloc[0]['id'] == 1
    assert df.iloc[0]['nome'] == 'Coca Cola'


def testLerDadosRelatorioInvalido(banco):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='TIPO DE RELATÓRIO INVÁLIDO'):
        lerDados('99', conexao)


def testLerDadosSemProdutos(banco):
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

    conexao.commit()

    with pytest.raises(
        ValueError,
        match='NÃO HÁ PRODUTOS CADASTRADOS COM ESTAS ESPECIFICAÇÕES!'
    ):
        lerDados('1', conexao)

    conexao.close()


def testGerarRelatorioCSV(tmp_path):
    df = pd.DataFrame({
        'id': [1],
        'nome': ['Coca Cola'],
        'quantidade': [20]
    })

    nome_arquivo = str(tmp_path / 'relatorio_produtos')

    gerarRel(df, nome_arquivo, 'ADMINISTRADOR')

    arquivos = list(tmp_path.glob('relatorio_produtos_*.csv'))

    assert len(arquivos) == 1

    conteudo = arquivos[0].read_text(encoding='utf-8')
    assert 'id,nome,quantidade' in conteudo
    assert '1,Coca Cola,20' in conteudo


def testGerarRelatorioSemPermissao(tmp_path):
    df = pd.DataFrame({
        'id': [1],
        'nome': ['Coca Cola']
    })

    nome_arquivo = str(tmp_path / 'relatorio_produtos')

    with pytest.raises(
        PermissionError,
        match='USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO'
    ):
        gerarRel(df, nome_arquivo, 'CARGO INVÁLIDO')

    arquivos = list(tmp_path.glob('relatorio_produtos_*.csv'))
    assert len(arquivos) == 0

# ---------------------------------------------------------------------------
# Casos complementares
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "rel, query, parametros, coluna, esperado",
    [
        ('1', "SELECT id, nome FROM produtos WHERE id = ?", (1,), 'nome', 'Coca Cola'),
        ('2', "SELECT produto, tipo FROM historicoMovimentacao WHERE idProduto = ?", (2,), 'produto', 'Pepsi'),
        ('3', "SELECT valor, operacao FROM histSaldo WHERE operacao = ?", ('SAÍDA',), 'operacao', 'SAÍDA'),
        ('4', "SELECT id, nome, quantidade FROM produtos WHERE id = ?", (2,), 'nome', 'Pepsi'),
    ]
    #testa o caminho de query personalizada nos 4 tipos de relatório
)
def testLerDadosComQueryTodosRelatorios(banco, rel, query, parametros, coluna, esperado):
    conexao, cursor = banco

    df = lerDados(rel, conexao, query, parametros)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0][coluna] == esperado


@pytest.mark.parametrize("rel", ['1', '2', '3', '4'])
def testLerDadosQuerySemParametrosUsaPadrao(banco, rel):
    conexao, cursor = banco

    #sem parametros a função ignora a query recebida e usa a consulta padrão
    df = lerDados(rel, conexao, "SELECT 1 AS coluna_que_nao_deve_aparecer")

    assert 'coluna_que_nao_deve_aparecer' not in df.columns
    assert len(df) == 2


@pytest.mark.parametrize(
    "rel, query, parametros",
    [
        ('1', "SELECT id, nome FROM produtos WHERE id = ?", (999,)),
        ('2', "SELECT produto FROM historicoMovimentacao WHERE idProduto = ?", (999,)),
        ('3', "SELECT valor FROM histSaldo WHERE operacao = ?", ('INEXISTENTE',)),
        ('4', "SELECT id, nome, quantidade FROM produtos WHERE id = ?", (999,)),
    ]
)
def testLerDadosComQuerySemResultado(banco, rel, query, parametros):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='NÃO HÁ PRODUTOS CADASTRADOS COM ESTAS ESPECIFICAÇÕES!'
    ):
        lerDados(rel, conexao, query, parametros)


@pytest.mark.parametrize(
    "rel, tabela",
    [
        ('1', 'produtos'),
        ('2', 'historicoMovimentacao'),
        ('3', 'histSaldo'),
        ('4', 'produtos'),
    ]
)
def testLerDadosTabelaVazia(banco, rel, tabela):
    conexao, cursor = banco

    cursor.execute(f"DELETE FROM {tabela}")
    conexao.commit()

    with pytest.raises(
        ValueError,
        match='NÃO HÁ PRODUTOS CADASTRADOS COM ESTAS ESPECIFICAÇÕES!'
    ):
        lerDados(rel, conexao)


@pytest.mark.parametrize("rel", ['', '0', '5', 1, 'RELATORIO'])
def testLerDadosTiposInvalidos(banco, rel):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='TIPO DE RELATÓRIO INVÁLIDO'):
        lerDados(rel, conexao)


@pytest.mark.parametrize(
    "cargo",
    ['ADMINISTRADOR', 'GERENTE', 'ESTOQUISTA', 'FINANCEIRO', 'CONSULTA']
)
def testGerarRelatorioTodosCargosPermitidos(tmp_path, cargo):
    df = pd.DataFrame({
        'id': [1],
        'nome': ['Coca Cola']
    })

    nome_arquivo = str(tmp_path / 'relatorio_produtos')

    gerarRel(df, nome_arquivo, cargo)

    arquivos = list(tmp_path.glob('relatorio_produtos_*.csv'))
    assert len(arquivos) == 1


def testGerarRelatorioAPartirDeLerDados(banco, tmp_path):
    conexao, cursor = banco

    df = lerDados('3', conexao)
    nome_arquivo = str(tmp_path / 'relatorio_saldo')

    gerarRel(df, nome_arquivo, 'ADMINISTRADOR')

    arquivos = list(tmp_path.glob('relatorio_saldo_*.csv'))
    assert len(arquivos) == 1

    conteudo = arquivos[0].read_text(encoding='utf-8')
    assert 'valor,operacao,quemFez,data,hora' in conteudo
    assert '1000,SAÍDA,ROBERTO' in conteudo