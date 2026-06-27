import sqlite3
from interface import terminal as i
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
                i.telaCadastroProduto(cursor, conexao)
            case 2:
                i.telaListagemProdutos(cursor, conexao)
            case 3:
                i.telaHistoricoCadProdutos(cursor, conexao)
            case 4:
                i.telaRegMov(cursor, conexao)
            case 5:
               i.telaHistMov(cursor, conexao)
            case 6:
                i.telaRel(conexao)
            case 7:
                i.telaDeletar(cursor, conexao)
            case 8:
               i.telaEditarSaldo(cursor, conexao)
            case 9:
                print('SAINDO...')
                break
            case _:
                print('ERRO: INSIRA UM VALOR ENTRE 1 E 7 ')
    except ValueError:
        print('ERRO: INSIRA UM VALOR ENTRE 1 A 7')
    continuar = input('AINDA DESEJA UTILIZAR O SISTEMA[S/N]? ')
    if continuar.lower() not in ('s', 'sim'):
        break
conexao.close()

