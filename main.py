import sqlite3
from funcoes import cadastro, movimentacao, historicoMovimentacao, listarProdutos, editarSaldo, deletar, historicoCadastro, exportarCsv
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
    print('[6] EXPORTAR RELATÓRIO CSV')
    print('[7] DELETAR PRODUTO')
    print('[8] EDITAR SALDO')
    print('[9] SAIR DO SISTEMA')
    try:
        funcao = int(input('QUAL FUNÇÃO DESEJA REALIZAR? '))
        match funcao:
            case 1:
                cadastro(cursor, conexao)
            case 2:
                listarProdutos(cursor)
            case 3:
                historicoCadastro(cursor)
            case 4:
                movimentacao(cursor, conexao)
            case 5:
               historicoMovimentacao(cursor)
            case 6:
                exportarCsv(cursor)
            case 7:
                deletar(cursor, conexao)
            case 8:
               editarSaldo(cursor, conexao)
            case 9:
                print('SAINDO...')
                break
            case _:
                print('ERRO: INSIRA UM VALOR ENTRE 1 E 7 ')
    except ValueError:
        print('ERRO: INSIRA UM VALOR ENTRE 1 A 7')
    continuar = input('AINDA DESEJA UTILIZAR O SISTEMA[S/N]? ')
    if continuar.lower() in ('s', 'sim'):
        break
conexao.close()

