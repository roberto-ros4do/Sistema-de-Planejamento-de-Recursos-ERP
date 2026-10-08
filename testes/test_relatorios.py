import sqlite3
import pytest
import pandas as pd

from servicos.relatorios import lerDados, gerarRel, gerarCsv, formatarRelatorio
from servicos.erros import NaoEncontradoError


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

    df = lerDados('1', conexao, 'ADMINISTRADOR')

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == [
        'id', 'nome', 'preco', 'quantidade', 'data', 'quemFez'
    ]
    assert df.iloc[0]['nome'] == 'Coca Cola'


def testLerDadosMovimentacoes(banco):
    conexao, cursor = banco

    df = lerDados('2', conexao, 'ADMINISTRADOR')

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert 'produto' in df.columns
    assert 'tipo' in df.columns
    assert df.iloc[0]['tipo'] == 'COMPRA'


def testLerDadosSaldo(banco):
    conexao, cursor = banco

    df = lerDados('3', conexao, 'ADMINISTRADOR')

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == [
        'valor', 'operacao', 'quemFez', 'data', 'hora'
    ]


def testLerDadosEstoque(banco):
    conexao, cursor = banco

    df = lerDados('4', conexao, 'ADMINISTRADOR')

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ['id', 'nome', 'quantidade']


def testLerDadosComQuery(banco):
    conexao, cursor = banco

    query = "SELECT id, nome FROM produtos WHERE id = ?"
    df = lerDados('1', conexao, 'ADMINISTRADOR', query, (1,))

    assert len(df) == 1
    assert df.iloc[0]['id'] == 1
    assert df.iloc[0]['nome'] == 'Coca Cola'


def testLerDadosRelatorioInvalido(banco):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='TIPO DE RELATÓRIO INVÁLIDO'):
        lerDados('99', conexao, 'ADMINISTRADOR')


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
        match='NÃO HÁ DADOS PARA GERAR O RELATÓRIO COM ESTAS ESPECIFICAÇÕES!'
    ):
        lerDados('1', conexao, 'ADMINISTRADOR')

    conexao.close()


def testGerarRelatorioCSV(tmp_path):
    df = pd.DataFrame({
        'id': [1],
        'nome': ['Coca Cola'],
        'quantidade': [20]
    })

    nome_arquivo = str(tmp_path / 'relatorio_produtos')

    gerarRel(df, nome_arquivo)

    arquivos = list(tmp_path.glob('relatorio_produtos_*.csv'))

    assert len(arquivos) == 1

    conteudo = arquivos[0].read_text(encoding='utf-8-sig')
    assert 'id;nome;quantidade' in conteudo
    assert '1;Coca Cola;20' in conteudo


def testLerDadosSemPermissao(banco):
    conexao, cursor = banco

    with pytest.raises(
        PermissionError,
        match='USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO'
    ):
        lerDados('1', conexao, 'CARGO INVÁLIDO')

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

    df = lerDados(rel, conexao, 'ADMINISTRADOR', query, parametros)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0][coluna] == esperado


@pytest.mark.parametrize("rel", ['1', '2', '3', '4'])
def testLerDadosQuerySemParametrosUsaPadrao(banco, rel):
    conexao, cursor = banco

    #sem parametros a função ignora a query recebida e usa a consulta padrão
    df = lerDados(rel, conexao, 'ADMINISTRADOR', "SELECT 1 AS coluna_que_nao_deve_aparecer")

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
        match='NÃO HÁ DADOS PARA GERAR O RELATÓRIO COM ESTAS ESPECIFICAÇÕES!'
    ):
        lerDados(rel, conexao, 'ADMINISTRADOR', query, parametros)


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
        match='NÃO HÁ DADOS PARA GERAR O RELATÓRIO COM ESTAS ESPECIFICAÇÕES!'
    ):
        lerDados(rel, conexao, 'ADMINISTRADOR')


@pytest.mark.parametrize("rel", ['', '0', '5', 1, 'RELATORIO'])
def testLerDadosTiposInvalidos(banco, rel):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='TIPO DE RELATÓRIO INVÁLIDO'):
        lerDados(rel, conexao, 'ADMINISTRADOR')


@pytest.mark.parametrize(
    "rel, cargo",
    [
        ('1', 'ADMINISTRADOR'), ('1', 'GERENTE'), ('1', 'ESTOQUISTA'), ('1', 'FINANCEIRO'), ('1', 'CONSULTA'),
        ('2', 'ADMINISTRADOR'), ('2', 'GERENTE'), ('2', 'ESTOQUISTA'), ('2', 'FINANCEIRO'), ('2', 'CONSULTA'),
        ('3', 'ADMINISTRADOR'), ('3', 'FINANCEIRO'), ('3', 'CONSULTA'),
        ('4', 'ADMINISTRADOR'), ('4', 'GERENTE'), ('4', 'ESTOQUISTA'), ('4', 'FINANCEIRO'), ('4', 'CONSULTA'),
    ]
    #cada tipo de relatório usa a sua própria permissão
)
def testLerDadosCargosPermitidos(banco, rel, cargo):
    conexao, cursor = banco

    df = lerDados(rel, conexao, cargo)

    assert len(df) == 2


def testGerarRelatorioAPartirDeLerDados(banco, tmp_path):
    conexao, cursor = banco

    df = lerDados('3', conexao, 'ADMINISTRADOR')
    nome_arquivo = str(tmp_path / 'relatorio_saldo')

    gerarRel(df, nome_arquivo)

    arquivos = list(tmp_path.glob('relatorio_saldo_*.csv'))
    assert len(arquivos) == 1

    conteudo = arquivos[0].read_text(encoding='utf-8-sig')
    assert 'valor;operacao;quemFez;data;hora' in conteudo
    assert '10,00;SAÍDA;ROBERTO;2026-10-01;10:00' in conteudo

# ---------------------------------------------------------------------------
# Formatação do CSV (valores em reais, datas AAAA-MM-DD, padrão Excel BR)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "coluna, centavos, reais",
    [
        ('preco', 699, 6.99),
        ('valorEnvolvido', 1500, 15.0),
        ('valor', 1, 0.01),
        ('valor', 0, 0.0),
    ]
)
def testFormatarRelatorioConverteCentavos(coluna, centavos, reais):
    df = pd.DataFrame({coluna: [centavos]})

    formatado = formatarRelatorio(df)

    assert formatado.iloc[0][coluna] == pytest.approx(reais)


def testFormatarRelatorioConverteData():
    df = pd.DataFrame({'data': ['2026/10/01', '2026/12/31']})

    formatado = formatarRelatorio(df)

    assert list(formatado['data']) == ['2026-10-01', '2026-12-31']


def testFormatarRelatorioNaoAlteraOutrasColunas():
    df = pd.DataFrame({
        'id': [1],
        'nome': ['Coca Cola'],
        'quantidade': [20],
        'quemFez': ['ROBERTO']
    })

    formatado = formatarRelatorio(df)

    assert formatado.iloc[0]['id'] == 1
    assert formatado.iloc[0]['nome'] == 'Coca Cola'
    assert formatado.iloc[0]['quantidade'] == 20
    assert formatado.iloc[0]['quemFez'] == 'ROBERTO'


def testFormatarRelatorioNaoAlteraOriginal():
    df = pd.DataFrame({'preco': [600], 'data': ['2026/10/01']})

    formatarRelatorio(df)

    assert df.iloc[0]['preco'] == 600
    assert df.iloc[0]['data'] == '2026/10/01'


@pytest.mark.parametrize(
    "rel, cabecalho, linha",
    [
        ('1', 'id;nome;preco;quantidade;data;quemFez', '1;Coca Cola;6,00;20;2026-10-01;ROBERTO'),
        ('2', 'produto;idProduto;tipo;quantidade;data;quemFez;valorEnvolvido', 'Pepsi;2;VENDA;3;2026-10-02;JOAO;15,00'),
        ('3', 'valor;operacao;quemFez;data;hora', '15,00;ENTRADA;JOAO;2026-10-02;11:00'),
        ('4', 'id;nome;quantidade', '2;Pepsi;10'),
    ]
    #os 4 relatórios saem no mesmo padrão
)
def testGerarCsvTodosRelatorios(banco, rel, cabecalho, linha):
    conexao, cursor = banco

    df = lerDados(rel, conexao, 'ADMINISTRADOR')
    conteudo = gerarCsv(df)
    linhas = conteudo.splitlines()

    assert linhas[0] == cabecalho
    assert linha in linhas


def testGerarCsvComFiltro(banco):
    conexao, cursor = banco

    query = "SELECT valor, operacao FROM histSaldo WHERE operacao = ?"
    df = lerDados('3', conexao, 'ADMINISTRADOR', query, ('SAÍDA',))

    conteudo = gerarCsv(df)

    assert conteudo.splitlines() == ['valor;operacao', '10,00;SAÍDA']


@pytest.mark.parametrize(
    "rel, cargo",
    [
        ('3', 'GERENTE'),
        ('3', 'ESTOQUISTA'),
        ('1', 'CARGO INVÁLIDO'),
        ('2', 'CARGO INVÁLIDO'),
        ('3', 'CARGO INVÁLIDO'),
        ('4', 'CARGO INVÁLIDO'),
        ('1', ''),
    ]
    #GERENTE e ESTOQUISTA não veem o histórico de transações, então não exportam o extrato
)
def testLerDadosCargosSemPermissao(banco, rel, cargo):
    conexao, cursor = banco

    with pytest.raises(
        PermissionError,
        match='USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO'
    ):
        lerDados(rel, conexao, cargo)


def testLerDadosTipoInvalidoAntesDaPermissao(banco):
    conexao, cursor = banco

    #tipo inválido não tem ação associada, então o erro de tipo vem primeiro
    with pytest.raises(ValueError, match='TIPO DE RELATÓRIO INVÁLIDO'):
        lerDados('99', conexao, 'CARGO INVÁLIDO')


def testGerarRelatorioArquivoComMarcadorUtf8(banco, tmp_path):
    conexao, cursor = banco

    df = lerDados('3', conexao, 'ADMINISTRADOR')
    nome_arquivo = str(tmp_path / 'relatorio_extrato')

    gerarRel(df, nome_arquivo)

    arquivo = list(tmp_path.glob('relatorio_extrato_*.csv'))[0]
    bytes_arquivo = arquivo.read_bytes()

    #o marcador UTF-8 (BOM) faz o Excel reconhecer os acentos
    assert bytes_arquivo.startswith(b'\xef\xbb\xbf')
    assert 'SAÍDA'.encode('utf-8') in bytes_arquivo


def testLerDadosContinuaEmCentavos(banco):
    conexao, cursor = banco

    #a formatação só acontece no CSV; lerDados devolve os dados do banco
    df = lerDados('2', conexao, 'ADMINISTRADOR')

    assert df.iloc[0]['valorEnvolvido'] == 1000
    assert df.iloc[0]['data'] == '2026/10/01'

# ---------------------------------------------------------------------------
# Exceções próprias
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rel", ['', '0', '5', 1, 'RELATORIO'])
def testLerDadosTipoInvalidoLancaNaoEncontrado(banco, rel):
    conexao, cursor = banco

    with pytest.raises(NaoEncontradoError, match='TIPO DE RELATÓRIO INVÁLIDO'):
        lerDados(rel, conexao, 'ADMINISTRADOR')


@pytest.mark.parametrize(
    "rel, tabela",
    [
        ('1', 'produtos'),
        ('2', 'historicoMovimentacao'),
        ('3', 'histSaldo'),
        ('4', 'produtos'),
    ]
)
def testLerDadosVazioLancaNaoEncontrado(banco, rel, tabela):
    conexao, cursor = banco

    cursor.execute(f"DELETE FROM {tabela}")
    conexao.commit()

    with pytest.raises(
        NaoEncontradoError,
        match='NÃO HÁ DADOS PARA GERAR O RELATÓRIO COM ESTAS ESPECIFICAÇÕES!'
    ):
        lerDados(rel, conexao, 'ADMINISTRADOR')


def testLerDadosSemPermissaoContinuaPermissionError(banco):
    conexao, cursor = banco

    #falta de permissão continua sendo 403, mesmo com o relatório vazio
    cursor.execute("DELETE FROM histSaldo")
    conexao.commit()

    with pytest.raises(PermissionError):
        lerDados('3', conexao, 'GERENTE')