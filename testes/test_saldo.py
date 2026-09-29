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
