import sqlite3
import pytest
from servicos.saldo import verificarSaldo, editarSaldo, consultaHistSaldo

@pytest.fixture #declara que a função abaixo prepara algo que será utilizado para realizar os testes
#fixture = prepara o ambiente que o pytest executa quando um teste precisa daquele ambiente.
def banco():
    conexao = sqlite3.connect(":memory:")
    cursor = conexao.cursor()

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

def testVerificarSaldo(banco):
    conexao, cursor = banco
    saldo = verificarSaldo(cursor)

    assert saldo== 100000

def testEditarSaldoEntrada(banco):
    conexao, cursor = banco

    editarSaldo(
        'ENTRADA',
        200,
        100000,
        cursor,
        conexao,
        'Roberto',
        'ADMINISTRADOR'
    )
    saldo = verificarSaldo(cursor)
    historico = consultaHistSaldo(cursor)
    assert saldo == 120000
    assert historico[0][0] == 20000
    assert historico[0][1] == 'ENTRADA'
    assert historico[0][2] == 'Roberto'

def testRetirarValorSuficiente(banco):
    conexao, cursor = banco

    editarSaldo(
        'RETIRADA',
            900, 
        100000,
        cursor,
        conexao,
        'Roberto',
        'ADMINISTRADOR'
    )

    saldo = verificarSaldo(cursor)
    historico = consultaHistSaldo(cursor)
    assert saldo == 10000
    assert historico[0][0] == 90000
    assert historico[0][1] == 'RETIRADA'
    assert historico[0][2] == 'Roberto'

def testRetiradoValorInsuficiente(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match='SALDO INSUFICIENTE PARA RETIRADA!'):
        editarSaldo(
            'RETIRADA',
             1200, 
            100000,
            cursor,
            conexao,
            'Roberto',
            'ADMINISTRADOR'
        )

def testValorNegativo(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match='CAMPO VALOR ACEITA APENAS NÚMEROS REAIS POSITIVOS!'):
            editarSaldo(
                'RETIRADA',
                 -1200, 
                100000,
                cursor,
                conexao,
                'Roberto',
                'ADMINISTRADOR'
            )

def testValorInvalido(banco):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='CAMPO VALOR ACEITA APENAS VALORES REAIS'):
        editarSaldo(
            'RETIRADA',
            "VALOR INVÁLIDO", 
            100000,
            cursor,
            conexao,
            'Roberto',
            'ADMINISTRADOR'
        )

def testCargoSemPermissao(banco):
    conexao, cursor = banco

    with pytest.raises(PermissionError, match='USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO'):
        editarSaldo(
            'RETIRADA',
            50000, 
            100000,
            cursor,
            conexao,
            'Roberto',
            'CARGO INVÁLIDO'
        )

def testOperacaoInvalida(banco):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='CAMPO OPERAÇÃO ACEITA APENAS VALORES RETIRADA E ENTRADA!'):
            editarSaldo(
                'OPERAÇÃO INVÁLIDA',
                50000, 
                100000,
                cursor,
                conexao,
                'Roberto',
                'ADMINISTRADOR'
            )


# ---------------------------------------------------------------------------
# Casos complementares
# ---------------------------------------------------------------------------

def testConsultaHistSaldoVazio(banco):
    conexao, cursor = banco

    historico = consultaHistSaldo(cursor)

    assert historico == []

def testEntradaValorNegativo(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match='CAMPO VALOR ACEITA APENAS NÚMEROS REAIS POSITIVOS'):
        editarSaldo(
            'ENTRADA',
            -200,
            100000,
            cursor,
            conexao,
            'Roberto',
            'ADMINISTRADOR'
        )

def testEntradaValorInvalido(banco):
    conexao, cursor = banco
    with pytest.raises(ValueError, match='CAMPO VALOR ACEITA APENAS VALORES REAIS'):
        editarSaldo(
            'ENTRADA',
            "VALOR INVÁLIDO",
            100000,
            cursor,
            conexao,
            'Roberto',
            'ADMINISTRADOR'
        )

@pytest.mark.parametrize(
    "op, valor, saldoFinal, valorHistorico",
    [
        ('ENTRADA', '10.55', 101055, 1055),
        ('RETIRADA', '10.55', 98945, 1055),
        ('ENTRADA', '0.01', 100001, 1),
    ]
)
def testEditarSaldoValorDecimal(banco, op, valor, saldoFinal, valorHistorico):
    conexao, cursor = banco

    editarSaldo(
        op,
        valor,
        100000,
        cursor,
        conexao,
        'Roberto',
        'ADMINISTRADOR'
    )

    saldo = verificarSaldo(cursor)
    historico = consultaHistSaldo(cursor)
    assert saldo == saldoFinal
    assert historico[0][0] == valorHistorico
    assert historico[0][1] == op

def testRetirarValorIgualAoSaldo(banco):
    conexao, cursor = banco

    editarSaldo(
        'RETIRADA',
        1000,
        100000,
        cursor,
        conexao,
        'Roberto',
        'ADMINISTRADOR'
    )

    saldo = verificarSaldo(cursor)
    assert saldo == 0

@pytest.mark.parametrize(
    "op, valor",
    [
        ('RETIRADA', 1200),
        ('RETIRADA', -1),
        ('RETIRADA', 'INVÁLIDO'),
        ('ENTRADA', -1),
        ('ENTRADA', 'INVÁLIDO'),
        ('OPERAÇÃO INVÁLIDA', 10),
    ]
)
def testEditarSaldoComErroNaoAlteraBanco(banco, op, valor):
    conexao, cursor = banco

    with pytest.raises(ValueError):
        editarSaldo(
            op,
            valor,
            100000,
            cursor,
            conexao,
            'Roberto',
            'ADMINISTRADOR'
        )

    saldo = verificarSaldo(cursor)
    cursor.execute("SELECT COUNT(*) FROM histSaldo")
    trans = cursor.fetchone()[0]
    assert saldo == 100000
    assert trans == 0

def testEditarSaldoVariasOperacoes(banco):
    conexao, cursor = banco

    editarSaldo('ENTRADA', 500, verificarSaldo(cursor), cursor, conexao, 'Roberto', 'ADMINISTRADOR')
    editarSaldo('RETIRADA', 200, verificarSaldo(cursor), cursor, conexao, 'Maria', 'FINANCEIRO')

    saldo = verificarSaldo(cursor)
    historico = consultaHistSaldo(cursor)
    assert saldo == 130000
    assert len(historico) == 2
    assert historico[0][:3] == (50000, 'ENTRADA', 'Roberto')
    assert historico[1][:3] == (20000, 'RETIRADA', 'Maria')

@pytest.mark.parametrize(
    "cargo",
    ['ADMINISTRADOR', 'FINANCEIRO']
)
def testEditarSaldoCargosPermitidos(banco, cargo):
    conexao, cursor = banco

    editarSaldo(
        'ENTRADA',
        100,
        100000,
        cursor,
        conexao,
        'Roberto',
        cargo
    )

    assert verificarSaldo(cursor) == 110000

@pytest.mark.parametrize(
    "cargo",
    ['GERENTE', 'ESTOQUISTA', 'CONSULTA', '']
)
def testEditarSaldoCargosSemPermissao(banco, cargo):
    conexao, cursor = banco

    with pytest.raises(PermissionError, match='USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO'):
        editarSaldo(
            'ENTRADA',
            100,
            100000,
            cursor,
            conexao,
            'Roberto',
            cargo
        )

    assert verificarSaldo(cursor) == 100000