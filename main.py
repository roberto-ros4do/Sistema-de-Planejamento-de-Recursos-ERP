import sqlite3
from funcoes import cadastro, movimentacao, listarHistorico, listarProdutos, editarSaldo
from banco import Bancos

Bancos()

conexao = sqlite3.connect("banco.db")
cursor = conexao.cursor()

while True:
    cursor.execute("""
    SELECT valor FROM saldo 
    WHERE id = 1
    """)
    saldo = cursor.fetchone()[0]

    print('------PLANEJAMENTO DE RECURSOS EMPRESARIAIS-------')
    print('------------------------------')
    print(f'SALDO: R$ {saldo:.2f}')
    print('------------------------------')
    print('[1] CADASTRO DE PRODUTOS')
    print('[2] REGISTRAR MOVIMENTAÇÃO')
    print('[3] RELATÓRIO GERENCIAL')
    print('[4] LISTAGEM DE PRODUTOS')
    print('[5] HISTÓRICO DE MOVIMENTAÇÕES')
    print('[6] EDITAR SALDO')
    print('[7] SAIR DO SISTEMA')
    try:
        funcao = int(input('QUAL FUNÇÃO DESEJA REALIZAR? '))
        match funcao:
            case 1:
                cadastro(cursor, conexao)
            case 2:
                movimentacao(cursor, conexao)
            case 3:
                print('AINDA NÃO IMPLEMENTADA!')
            case 4:
               listarProdutos(cursor, conexao)
            case 5:
               listarHistorico(cursor, conexao)
            case 6:
               editarSaldo(cursor, conexao)
            case 7:
                print('SAINDO...')
                conexao.close()
                break
            case _:
                print('ERRO: INSIRA UM VALOR ENTRE 1 E 7 ')
    except ValueError:
        print('ERRO: INSIRA UM VALOR ENTRE 1 A 7')
    continuar = input('AINDA DESEJA UTILIZAR O SISTEMA[S/N]? ')
    if continuar.lower() != 's' and continuar.lower() != 'sim':
        conexao.close()
        break

