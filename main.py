import sqlite3
from interface import terminal as i
from banco import Bancos
from servicos import login as l
from servicos import saldo as s

Bancos()
conexao = sqlite3.connect("banco.db", detect_types=sqlite3.PARSE_DECLTYPES)
cursor = conexao.cursor()

print('----------------SEJA BEM VINDO!-------------------')

logou, cargo, nome = i.telaLogin(cursor, conexao)
menu, telas = l.verificaCargo(cursor, conexao, cargo)

if logou: 
    while True:
        saldo = s.verificarSaldo(cursor)
        print('------PLANEJAMENTO DE RECURSOS EMPRESARIAIS-------')
        if cargo!='ESTOQUISTA':
            print(f'SALDO: R$ {(saldo/100):.2f}')
            print('------------------------------')
        c = 1
        ultimo=0
        for item in menu:
            print(f'[{c}] {item}')
            ultimo= c
            c += 1
        try:
            funcao = int(input('QUAL FUNÇÃO DESEJA REALIZAR? '))
            if funcao<=ultimo-1 and funcao>0:
                telas[funcao-1](cursor, conexao, nome)
            elif funcao==ultimo:
                print('SAINDO...')
                break
            else:
                print(f'ERRO! INSIRA UM VALOR ENTRE 1 A {c} ')
        except ValueError:
            print(f'ERRO: INSIRA UM VALOR ENTRE 1 A {c}]')
        continuar = input('AINDA DESEJA UTILIZAR O SISTEMA[S/N]? ')
        if continuar.lower() not in ('s', 'sim'):
            break
else:
    print('SAINDO...')
conexao.close()

