import sqlite3
from funcoes import cadastro, movimentacao, listarHistorico, listarProdutos, editarSaldo, deletar, historicoCadastro
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
    print('[1] CADASTRAR PRODUTOS')
    print('[2] LISTAGEM DE PRODUTOS')
    print('[3] HISTÓRICO DE CADASTRO')
    print('[4] REGISTRAR MOVIMENTAÇÃO')
    print('[5] HISTÓRICO DE MOVIMENTAÇÕES')
    print('[6] DELETAR PRODUTO')
    print('[7] EDITAR SALDO')
    print('[8] SAIR DO SISTEMA')
    try:
        funcao = int(input('QUAL FUNÇÃO DESEJA REALIZAR? '))
        match funcao:
            case 1:
                cadastro(cursor, conexao)
            case 2:
                listarProdutos(cursor, conexao)
            case 3:
                historicoCadastro(cursor, conexao)
            case 4:
                movimentacao(cursor, conexao)
            case 5:
               listarHistorico(cursor, conexao)
            case 6:
                deletar(cursor, conexao)
            case 7:
               editarSaldo(cursor, conexao)
            case 8:
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

