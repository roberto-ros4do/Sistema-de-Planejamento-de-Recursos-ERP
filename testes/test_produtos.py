import sqlite3
import pytest
from servicos.produtos import cadastroProduto, buscarProduto, deletarProduto, consultaProdutos
from servicos.saldo import verificarSaldo
'''
Checklist de como ralizar os testes:
1- Declarar uma fixture para criar o banco de dados em memória e as tabelas necessárias.(ambiente)
2- Analisar os cenários de teste
3-Criar os testes com base nos possíveis erros que podemns er retornados e nos cenários válidos
EX: função que recebe numero em string e tenta convertter para inteiro, se não conseguir, retorna erro. Então o teste deve verificar se o erro é retornado corretamente.
mesma coisa com cargos(válido pu invalido), tipos de movimentacoes, operaçoes, etc
'''

@pytest.fixture
def banco():
    conexao = sqlite3.connect(":memory:")
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historicoMovimentacao(
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
        CREATE TABLE IF NOT EXISTS produtos(
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
        CREATE TABLE IF NOT EXISTS saldo(
        id INTEGER PRIMARY KEY,
        valor INTEGER DEFAULT 0 
        )      
        """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS histSaldo(
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

    conexao.commit()

    yield conexao, cursor

    conexao.close()

def testCadastroValido(banco):
    conexao, cursor = banco
    cadastroProduto(
    "Coca Cola",
    '20',
    '6',
    '100', 
    cursor, 
    conexao, 
    "ROBERTO", 
    "ADMINISTRADOR")

    cursor.execute("""
    SELECT * FROM produtos
    WHERE id = 1
    """)
    produto = cursor.fetchone()

    saldo = verificarSaldo(cursor)
    assert saldo == 90000
    assert produto[1] == 'Coca Cola'
    assert produto[2] == 20
    assert produto[3] == 600
    assert produto[6] == 'ROBERTO'

    cursor.execute("""
    SELECT * FROM historicoMovimentacao
    WHERE id = 1
    """)
    mov = cursor.fetchone()
    assert mov[1] == 'Coca Cola'
    assert mov[2] == 1
    assert mov[3] == 'CADASTRO'
    assert mov[4] == 20
    assert mov[7] == 'ROBERTO'
    assert mov[8] == 10000 

    cursor.execute("""
    SELECT * FROM histSaldo
    WHERE id = 1
    """)
    trans = cursor.fetchone()
    assert trans[1] == 10000
    assert trans[2] == 'SAÍDA'
    assert trans[3] == 'ROBERTO'

def testCadastroEstoqNaoInteiro(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match='CAMPO ESTOQUE ACEITA APENAS NÚMEROS INTEIROS POSITIVOS!'):
        cadastroProduto(
        "Coca Cola",
        'NÃO INTEIRO',
        '6',
        '100', 
        cursor, 
        conexao, 
        "ROBERTO", 
        "ADMINISTRADOR")

def testCadastroEstoqNegativo(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match='CAMPO ESTOQUE ACEITA APENAS NÚMEROS INTEIROS POSITIVOS!'):
        cadastroProduto(
        "Coca Cola",
        '-1',
        '6',
        '100', 
        cursor, 
        conexao, 
        "ROBERTO", 
        "ADMINISTRADOR")

def testCadastroPrecoInvalido(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match='CAMPO VALOR COBRADO ACEITA APENAS VALORES REAIS POSITIVOS!'):
        cadastroProduto(
        "Coca Cola",
        '20',
        'VALOR INVÁLIDO',
        '100', 
        cursor, 
        conexao, 
        "ROBERTO", 
        "ADMINISTRADOR")

def testCadastroPrecoNegativo(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match='CAMPO VALOR COBRADO ACEITA APENAS VALORES REAIS E POSITIVOS'):
        cadastroProduto(
        "Coca Cola",
        '20',
        '-1',
        '100', 
        cursor, 
        conexao, 
        "ROBERTO", 
        "ADMINISTRADOR")

def testCadastroInvestInvalido(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match='CAMPO VALOR ACEITA APENAS NÚMEROS REAIS POSITIVOS!'):
        cadastroProduto(
        "Coca Cola",
        '20',
        '6',
        'INVÁLIDO', 
        cursor, 
        conexao, 
        "ROBERTO", 
        "ADMINISTRADOR")

def testCadastroInvestNegativo(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match='CAMPO INVESTIMENTO ACEITA APENAS NÚMEROS REAIS E MAIORES QUE 0!'):
        cadastroProduto(
        "Coca Cola",
        '20',
        '6',
        '-1', 
        cursor, 
        conexao, 
        "ROBERTO", 
        "ADMINISTRADOR")

def testCadastroInvestMaiorQueSaldo(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match='SALDO INSUFICIENTE!'):
        cadastroProduto(
        "Coca Cola",
        '20',
        '6',
        '200000', 
        cursor, 
        conexao, 
        "ROBERTO", 
        "ADMINISTRADOR")

def testCadastroNomeVazio(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match="CAMPO NOME DE PRODUTO OBRIGATÓRIO!"):
        cadastroProduto(
        "",
        '20',
        '6',
        '100', 
        cursor, 
        conexao, 
        "ROBERTO", 
        "ADMINISTRADOR")

def testCadastroCargoInvalido(banco):
    conexao, cursor = banco
    with pytest.raises(PermissionError, match='USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO'):
        cadastroProduto(
        "Coca Cola",
        '20',
        '6',
        '100', 
        cursor, 
        conexao, 
        "ROBERTO", 
        "CARGO INVÁLIDO")

def testBuscarProduto(banco):
    conexao, cursor = banco

    cadastroProduto(
        "Coca Cola",
        '20',
        '6',
        '100',
        cursor,
        conexao,
        "ROBERTO",
        "ADMINISTRADOR"
    )

    produto = buscarProduto(1, cursor)

    assert produto == ('Coca Cola', 20)

def testBuscarProdutoNaoEncontrado(banco):
    conexao, cursor = banco

    produto = buscarProduto(999, cursor)

    assert produto is None

def testConsultaProdutos(banco):
    conexao, cursor = banco

    cadastroProduto(
        "Coca Cola",
        '20',
        '6',
        '100',
        cursor,
        conexao,
        "ROBERTO",
        "ADMINISTRADOR"
    )

    cadastroProduto(
        "Pepsi",
        '10',
        '5',
        '50',
        cursor,
        conexao,
        "ROBERTO",
        "ADMINISTRADOR"
    )

    produtos = consultaProdutos(cursor)

    assert len(produtos) == 2

    assert produtos[0][0] == 1
    assert produtos[0][1] == "Coca Cola"
    assert produtos[0][2] == 600
    assert produtos[0][3] == 20

    assert produtos[1][0] == 2
    assert produtos[1][1] == "Pepsi"
    assert produtos[1][2] == 500
    assert produtos[1][3] == 10

def testConsultaProdutosSemProdutos(banco):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='AINDA NÃO HÁ PRODUTOS CADASTRADOS!'):
        consultaProdutos(cursor)

def testDeletarProdutoValido(banco):
    conexao, cursor = banco
    cadastroProduto(
            "Coca Cola",
            '20',
            '6',
            '100',
            cursor,
            conexao,
            "ROBERTO",
            "ADMINISTRADOR"
        )

    deletarProduto(
        "1",
        cursor,
        conexao,
        "ROBERTO",
        "ADMINISTRADOR"
    )
    produto = buscarProduto(1, cursor)

    cursor.execute("""
    SELECT * FROM historicoMovimentacao
    WHERE id = 2
    """)

    mov = cursor.fetchone()

    assert produto is None
    assert mov[1] == 'Coca Cola'
    assert mov[2] == 1
    assert mov[3] == 'DELETAÇÃO'
    assert mov[7] == 'ROBERTO'

def testDeletarCargoInvalido(banco):
    conexao, cursor = banco

    cadastroProduto(
        "Coca Cola",
        '20',
        '6',
        '100',
        cursor,
        conexao,
        "ROBERTO",
        "ADMINISTRADOR"
    )
    with pytest.raises(PermissionError, match='USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO'):
        deletarProduto(
                "1",
                cursor,
                conexao,
                "ROBERTO",
                "CARGO INVÁLIDO"
            )

def testDeletarIdInvalido(banco):
    conexao, cursor = banco

    cadastroProduto(
        "Coca Cola",
        '20',
        '6',
        '100',
        cursor,
        conexao,
        "ROBERTO",
        "ADMINISTRADOR"
    )
    with pytest.raises(ValueError, match='CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS'):
        deletarProduto(
                "ID INVÁLIDO",
                cursor,
                conexao,
                "ROBERTO",
                "ADMINISTRADOR"
            )  

def testDeletarIdNaoExiste(banco):
    conexao, cursor = banco

    cadastroProduto(
        "Coca Cola",
        '20',
        '6',
        '100',
        cursor,
        conexao,
        "ROBERTO",
        "ADMINISTRADOR"
    )
    with pytest.raises(ValueError, match='PRODUTO NÃO ENCONTRADO'):
        deletarProduto(
                "999",
                cursor,
                conexao,
                "ROBERTO",
                "ADMINISTRADOR"
            )  

def testDeletarIdNegativo(banco):
    conexao, cursor = banco
    cadastroProduto(
        "Coca Cola",
        '20',
        '6',
        '100',
        cursor,
        conexao,
        "ROBERTO",
        "ADMINISTRADOR"
    )
    with pytest.raises(ValueError, match='CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS'):
        deletarProduto(
                "-1",
                cursor,
                conexao,
                "ROBERTO",
                "ADMINISTRADOR"
            )  

# ---------------------------------------------------------------------------
# Casos complementares
# ---------------------------------------------------------------------------

def testCadastroEstoqZero(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match='CAMPO ESTOQUE ACEITA APENAS NÚMEROS INTEIROS POSITIVOS!'):
        cadastroProduto(
        "Coca Cola",
        '0',
        '6',
        '100',
        cursor,
        conexao,
        "ROBERTO",
        "ADMINISTRADOR")

def testCadastroEstoqDecimal(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match='CAMPO ESTOQUE ACEITA APENAS NÚMEROS INTEIROS POSITIVOS!'):
        cadastroProduto(
        "Coca Cola",
        '2.5',
        '6',
        '100',
        cursor,
        conexao,
        "ROBERTO",
        "ADMINISTRADOR")

def testCadastroValoresDecimais(banco):
    conexao, cursor = banco
    cadastroProduto(
    "Coca Cola",
    '20',
    '6.99',
    '100.50',
    cursor,
    conexao,
    "ROBERTO",
    "ADMINISTRADOR")

    produto = buscarProduto(1, cursor)
    cursor.execute("SELECT preco FROM produtos WHERE id = 1")
    preco = cursor.fetchone()[0]

    saldo = verificarSaldo(cursor)
    assert produto == ('Coca Cola', 20)
    assert preco == 699
    assert saldo == 89950

def testCadastroPrecoZero(banco):
    conexao, cursor = banco
    cadastroProduto(
    "Brinde",
    '20',
    '0',
    '100',
    cursor,
    conexao,
    "ROBERTO",
    "ADMINISTRADOR")

    cursor.execute("SELECT preco FROM produtos WHERE id = 1")
    preco = cursor.fetchone()[0]
    assert preco == 0

def testCadastroInvestIgualAoSaldo(banco):
    conexao, cursor = banco
    cadastroProduto(
    "Coca Cola",
    '20',
    '6',
    '1000',
    cursor,
    conexao,
    "ROBERTO",
    "ADMINISTRADOR")

    saldo = verificarSaldo(cursor)
    assert saldo == 0

def testCadastroComErroNaoAlteraBanco(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match='SALDO INSUFICIENTE!'):
        cadastroProduto(
        "Coca Cola",
        '20',
        '6',
        '200000',
        cursor,
        conexao,
        "ROBERTO",
        "ADMINISTRADOR")

    cursor.execute("SELECT COUNT(*) FROM produtos")
    produtos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM historicoMovimentacao")
    movimentacoes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM histSaldo")
    trans = cursor.fetchone()[0]

    assert produtos == 0
    assert movimentacoes == 0
    assert trans == 0
    assert verificarSaldo(cursor) == 100000

@pytest.mark.parametrize(
    "cargo",
    ['ADMINISTRADOR', 'GERENTE', 'ESTOQUISTA']
)
def testCadastroCargosPermitidos(banco, cargo):
    conexao, cursor = banco
    cadastroProduto(
    "Coca Cola",
    '20',
    '6',
    '100',
    cursor,
    conexao,
    "ROBERTO",
    cargo)

    assert buscarProduto(1, cursor) == ('Coca Cola', 20)

@pytest.mark.parametrize(
    "cargo",
    ['FINANCEIRO', 'CONSULTA', '']
)
def testCadastroCargosSemPermissao(banco, cargo):
    conexao, cursor = banco
    with pytest.raises(PermissionError, match='USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO'):
        cadastroProduto(
        "Coca Cola",
        '20',
        '6',
        '100',
        cursor,
        conexao,
        "ROBERTO",
        cargo)

    assert buscarProduto(1, cursor) is None

def testBuscarProdutoIdComoTexto(banco):
    conexao, cursor = banco
    cadastroProduto(
        "Coca Cola",
        '20',
        '6',
        '100',
        cursor,
        conexao,
        "ROBERTO",
        "ADMINISTRADOR"
    )

    produto = buscarProduto('1', cursor)

    assert produto == ('Coca Cola', 20)

def testDeletarIdZero(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match='CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS'):
        deletarProduto(
                "0",
                cursor,
                conexao,
                "ROBERTO",
                "ADMINISTRADOR"
            )

@pytest.mark.parametrize(
    "cargo",
    ['GERENTE', 'ESTOQUISTA', 'FINANCEIRO', 'CONSULTA']
)
def testDeletarCargosSemPermissao(banco, cargo):
    conexao, cursor = banco
    cadastroProduto(
        "Coca Cola",
        '20',
        '6',
        '100',
        cursor,
        conexao,
        "ROBERTO",
        "ADMINISTRADOR"
    )
    with pytest.raises(PermissionError, match='USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO'):
        deletarProduto(
                "1",
                cursor,
                conexao,
                "ROBERTO",
                cargo
            )

    assert buscarProduto(1, cursor) == ('Coca Cola', 20)

def testDeletarNaoAfetaOutrosProdutos(banco):
    conexao, cursor = banco
    cadastroProduto("Coca Cola", '20', '6', '100', cursor, conexao, "ROBERTO", "ADMINISTRADOR")
    cadastroProduto("Pepsi", '10', '5', '50', cursor, conexao, "ROBERTO", "ADMINISTRADOR")

    deletarProduto("1", cursor, conexao, "ROBERTO", "ADMINISTRADOR")

    produtos = consultaProdutos(cursor)
    assert len(produtos) == 1
    assert produtos[0][1] == 'Pepsi'

def testDeletarUltimoProdutoConsultaVazia(banco):
    conexao, cursor = banco
    cadastroProduto("Coca Cola", '20', '6', '100', cursor, conexao, "ROBERTO", "ADMINISTRADOR")

    deletarProduto("1", cursor, conexao, "ROBERTO", "ADMINISTRADOR")

    with pytest.raises(ValueError, match='AINDA NÃO HÁ PRODUTOS CADASTRADOS!'):
        consultaProdutos(cursor)

def testDeletarComErroNaoRegistraMovimentacao(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match='PRODUTO NÃO ENCONTRADO'):
        deletarProduto("999", cursor, conexao, "ROBERTO", "ADMINISTRADOR")

    cursor.execute("SELECT COUNT(*) FROM historicoMovimentacao")
    movimentacoes = cursor.fetchone()[0]
    assert movimentacoes == 0

def testCadastroInvestZeroNaoRegistraSaldo(banco):
    conexao, cursor = banco
    cadastroProduto(
    "Coca Cola",
    '20',
    '6',
    '0',
    cursor,
    conexao,
    "ROBERTO",
    "ADMINISTRADOR")

    cursor.execute("SELECT COUNT(*) FROM histSaldo")
    trans = cursor.fetchone()[0]

    cursor.execute("""
    SELECT * FROM historicoMovimentacao
    WHERE id = 1
    """)
    mov = cursor.fetchone()

    assert verificarSaldo(cursor) == 100000
    assert trans == 0
    assert buscarProduto(1, cursor) == ('Coca Cola', 20)
    assert mov[3] == 'CADASTRO'
    assert mov[8] == 0

def testCadastroInvestZeroComSaldoZerado(banco):
    conexao, cursor = banco
    cursor.execute("UPDATE saldo SET valor = 0 WHERE id = 1")
    conexao.commit()

    cadastroProduto(
    "Coca Cola",
    '20',
    '6',
    '0',
    cursor,
    conexao,
    "ROBERTO",
    "ADMINISTRADOR")

    assert verificarSaldo(cursor) == 0
    assert buscarProduto(1, cursor) == ('Coca Cola', 20)