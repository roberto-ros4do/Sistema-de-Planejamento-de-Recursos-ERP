import json
from funcoes import cadastro, movimentacao, listarProdutos, listarHistorico, editarSaldo

try:
    with open("dados.json", "r") as arquivo:
        dados = json.load(arquivo)
        saldo = dados["saldo"]
        produtos = dados["produtos"]
        historico = dados["historico"]
except (FileNotFoundError, json.JSONDecodeError):
    saldo = 0.0
    produtos = []
    historico = []


def salvar(saldo, produtos, historico):
    with open("dados.json", "w") as arquivo:
        json.dump({
            "saldo": saldo,
            "produtos": produtos,
            "historico": historico
            },arquivo)
while True:
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
                saldo = cadastro(produtos,saldo)
                salvar(saldo, produtos, historico)
            case 2:
                saldo = movimentacao(historico, produtos, saldo)
                salvar(saldo, produtos, historico)
            case 3:
                print('AINDA NÃO IMPLEMENTADA!')
            case 4:
                listarProdutos(produtos)
            case 5:
                listarHistorico(historico)
            case 6:
                saldo = editarSaldo(saldo)
                salvar(saldo, produtos, historico)
            case 7:
                print('SAINDO...')
                break
            case _:
                print('INSIRA SOMENTE NÚMEROS ENTRE 1 E 7 ')
    except ValueError:
        print('INVÁLIDO, INSIRA UM VALOR DE 1 A 7')
    continuar = input('AINDA DESEJA UTILIZAR O SISTEMA? ')
    if continuar.lower() != 's' and continuar.lower() != 'sim':
        break