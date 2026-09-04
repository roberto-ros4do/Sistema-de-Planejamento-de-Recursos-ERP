from servicos import produtos as p
from servicos import movimentacoes as m
from servicos import relatorios as r
from servicos import saldo as s
from servicos import login as l
from servicos import filtro as f
import datetime as dt

def verificaCargo(cargo):
    from permissoes import podeExecutar
    TELAS = {
    'CADASTRAR_PRODUTOS': {
        'nome': 'CADASTRAR PRODUTOS',
        'tela': telaCadastroProduto
    },

    'LISTAGEM_DE_PRODUTOS': {
        'nome': 'LISTAGEM DE PRODUTOS',
        'tela': telaListagemProdutos
    },

    'REGISTRAR_MOVIMENTACOES': {
        'nome': 'REGISTRAR MOVIMENTAÇÕES',
        'tela': telaRegMov
    },

    'HISTORICO_DE_MOVIMENTACOES': {
        'nome': 'HISTÓRICO DE MOVIMENTAÇÕES',
        'tela': telaHistMov
    },

    'EXPORTAR_RELATORIO_CSV': {
        'nome': 'EXPORTAR RELATÓRIO CSV',
        'tela': telaRelatorio
    },

    'DELETAR_PRODUTO': {
        'nome': 'DELETAR PRODUTO',
        'tela': telaDeletar
    },

    'EDITAR_SALDO': {
        'nome': 'EDITAR SALDO',
        'tela': telaEditarSaldo
    },

    'HISTORICO_DE_TRANSACOES': {
        'nome': 'HISTÓRICO DE TRANSAÇÕES',
        'tela': telaHistSaldo
    },

    'CADASTRAR_USUARIO': {
        'nome': 'CADASTRAR USUÁRIO',
        'tela': telaCadastrarUsuario
    },

    'SAIR_DO_SISTEMA': {
        'nome': 'SAIR DO SISTEMA',
        'tela': None
    }
}

    menu = []
    telas = []
    for acao in TELAS:
        if podeExecutar(cargo, acao):
            menu.append(TELAS[acao]['nome'])
            if TELAS[acao]['tela'] is not None:
                telas.append(TELAS[acao]['tela'])
    return menu, telas

def telaLogin(cursor, conexao):
    import socket
    while True:
        try:
            maq = socket.gethostname()
            resultado = l.verificaTentativas(maq, cursor)
            if resultado is None:
                identificador = maq
                tentativas = 4
                bloqueadoAte = None
            else:
                identificador = resultado[0]
                tentativas = resultado[1]
                bloqueadoAte = resultado[2]
            if bloqueadoAte is None or bloqueadoAte <= dt.datetime.now():
                login = input('Insira seu login: ')
                senha = input('Insira sua senha')
                existe, nome = l.verificaLogin(cursor, login, senha)
                if existe:
                    tentativas = 4
                    bloqueadoAte = None
                    logou = True
                    cargo = l.registraTentativa(identificador, tentativas, cursor, conexao, login, bloqueadoAte, logou)
                    return logou, cargo, nome
                else:
                    print('USUÁRIO OU SENHA INVÁLIDOS! ')
                    tentativas -= 1
                    if tentativas > 0:
                        print(f'VOCÊ POSSUI {tentativas} TENTATIVAS ')
                        l.registraTentativa(identificador, tentativas, cursor, conexao)

                    else:
                        print(f'VCOÊ ESGOTOU SUAS TENTATIVAS, TENTE NOVAMENTE EM 5 MINUTOS! ')
                        bloqueadoAte = dt.datetime.now() + dt.timedelta(minutes=5)
                        l.registraTentativa(identificador, tentativas, cursor, conexao, bloqueadoAte=bloqueadoAte)
                        return False, None, None
            else:
                print('-='*25)
                print('VOCÊ ACABOU COM SUAS TENTATIVAS, TENTE NOVAMENTE MAIS TARDE')
                print('-='*25)
                return False, None, None
        except ValueError:
            print('INSIRA APENAS NÚMEROS!')


def telaCadastrarUsuario(cursor, conexao, nome=None):
    while True:
        nomeUsuario = input('Insira nome: ')
        login = input('Insira login: ')
        while True:
            existe = l.verificaLoginRepetido(login, cursor)
            if existe:
                print('Este login já existe! Insira um diferente')
                login = input('Insira login: ')
            else:
                break
        while True:
            senha = input('Insira senha: ')
            if len(senha)<=5:
                print('Insira uma senha de no mínimo 6 caracteres!')
            else:
                break
        print('[1] ADMINISTRADOR')
        print('[2] GERENTE')
        print('[3] ESTOQUISTA')
        print('[4] FINANCEIRO')
        print('[5] CONSULTA')
        try:
            cargo = int(input('Qual cargo irá desempenhar? '))
        except ValueError:
            print('ERRO: INSIRA APENAS NÚMEROS INTEIRO DE 1 A 5!')
            continue
        match cargo:
            case 1 :
                cargo = 'ADMINISTRADOR'
            case 2:
                cargo = 'GERENTE'
            case 3:
                cargo = 'ESTOQUISTA'
            case 4:
                cargo = 'FINANCEIRO'
            case 5:
                cargo = 'CONSULTA'
            case _:
                print('ERRO! INSIRA UM VALOR ENTRE 1 E 5 ')
                continue
        l.cadastraLogin(cursor, conexao, nomeUsuario, login, senha, cargo)
        print('USUÁRIO CADASTRADO! ')
        return

def telaCadastroProduto(cursor, conexao, nome=None):
    while True:
        n = input('Insira o nome do produto: ')
        if n is False:
            print('NÃO DEIXE ESTE CAMPO VAZIO!')
            continue
        try:
            q = int(input('Insira a disponibilidade no estoque: '))
        except ValueError:
            print('ERRO! INSIRA APENAS VALORES INTEIROS!')
            continue
        if q<0:
            print('INSIRA UM VALOR MAIOR QUE 0!')
            continue
        try:
            invest = float(input('Insira o valor do investimento? '))
        except ValueError:
            print('ERRO! INSIRA APENAS NÚMEROS REAIS')
            continue
        if invest<0:
            print('INSIRA UM VALOR POSITIVO!')
            continue
        invest = round(invest*100)
        saldo = s.verificarSaldo(cursor)
        if invest>saldo:
            print('ERRO! SALDO INSUFICIENTE ')
            continue
        try:
            v = float(input('Insira o valor que será cobrado pelo produto: '))
        except ValueError:
            print('ERRO! INSIRA APENAS NÚMEROS REAIS!')
            continue
        if v<=0:
            print('INSIRA UM VALOR MAIOR QUE 0!')
            continue
        v = round(v*100)
        p.cadastroProduto(n, q, v, invest, cursor, conexao, nome)
        return


def listarProdutos(produtos):
    for produto in produtos:
        print(f"=========={produto[1]}===========")
        print(f"ID DO PRODUTO: [{produto[0]}]")
        print(f"DISPONIBILIDADE NO ESTOQUE: {produto[2]}")
        print(f"PREÇO: R$ {(produto[3])/100}")
        print(f'CRIADO EM {produto[4]} AS {produto[5]} POR {produto[6]}')
        
def telaListagemProdutos(cursor, conexao, nome=None):
     while True:
        produtos = p.consultaProdutos(cursor)
        if not produtos:
            print('AINDA NÃO HÁ PRODUTOS CADASTRADOS!')
            return
        else:
                filtro = input('Deseja utilizar filtro? ')
                if filtro.lower() in ('s', 'sim'):
                    n = input('Insira o nome(ENTER para pular): ')
                    quemCad = input('Insira quem cadastrou o produto(ENTER para pular): ')
                    idProd = input('Insira o ID de algum produto(ENTER para pular): ')
                    if idProd!='':
                        try:
                            idProd = int(idProd)
                            if idProd<=0:
                                print("INSIRA UM VALOR MAIOR QUE 0!")
                                continue
                        except ValueError:
                            print('ERRO! INSIRA NÚMEROS INTEIROS')
                            continue
                    valorMin = input('Insira o valor mínimo(ENTER para pular): R$')
                    if valorMin!='':
                        try:
                            valorMin = float(valorMin)
                            valorMin = round(valorMin*100)
                            if valorMin<0:
                                print('INSIRA UM VALOR POSITIVO!')
                                continue
                        except ValueError:
                            print('ERRO! INSIRA NÚMEROS REAIS')
                            continue
                    valorMax = input('Insira o valor máximo(ENTER para pular): ')
                    if valorMax!='':
                        try:
                            valorMax = float(valorMax)
                            valorMax = round(valorMax*100)
                            if valorMax<0:
                                print('INSIRA UM VALOR POSITIVO!')
                                continue
                        except ValueError:
                            print('ERRO! INSIRA UM NÚMERO REAL')
                            continue
                    estoqMin = input('Insira a disponibilidade mínima(ENTER para pular): ')
                    if estoqMin!='':
                        try:
                            estoqMin = int(estoqMin)
                            if estoqMin<0:
                                print('INSIRA UM VALOR INTEIRO E POSITIVO!')
                                continue
                        except ValueError:
                            print('ERRO! INSIRA UM NÚMERO INTEIRO!')
                            continue
                    estoqMax = input('Insira a disponibilidade máxima(ENTER para pular): ')
                    if estoqMax!='':
                        try:
                            estoqMax=int(estoqMax)
                            if estoqMax<0:
                                print('INSIRA UM VALOR INTEIRO E POSITIVO')
                                continue
                        except ValueError:
                            print('ERRO! INSIRA UM NÚMERO INTEIRO!')
                            continue
                    produtos = f.filtragemProdutos(valorMin, valorMax, estoqMin, estoqMax, cursor, quemCad=quemCad, n=n, id=idProd)
                    if not produtos:
                            print('NÃO HÁ PRODUTOS COM ESTAS ESPECIFICAÇÕES')
                            return
                    else:
                        listarProdutos(produtos)
                        return
                else:
                    listarProdutos(produtos)
                    return

def telaDeletar(cursor, conexao, nome=None):
    while True:
        try:
            idProd = int(input('Insira o ID do produto que deseja deletar: '))
            if idProd<=0:
                print('INSIRA APENAS NÚMEROS INTEIROS E POSITIVOS')
                continue
            produto = p.buscarProduto(idProd, cursor)
            if produto is None:
                    print('ERRO: PRODUTO NÃO ENCONTRADO!')
                    return
            p.deletarProduto(idProd, cursor, conexao, nome)
            print(f'[{produto}] DELETADO')
            return
        except ValueError:
            print('INSIRA APENAS NÚMEROS INTEIROS E POSITIVOS')

def listarHistMov(historico):
    for mov in historico:
                print(f"=========={mov[1]}===========")
                print(f'REALIZADA EM {mov[5]} AS {mov[6]} por {mov[7]}')
                print(f"TIPO DE MOVIMENTAÇÃO: {mov[3]}")
                if mov[3]=='CADASTRO':
                    print(f'UNIDADES CADASTRADAS: {mov[4]}')
                if mov[3] == 'COMPRA' or mov[3] == 'DEVOLUÇÃO':
                    print(f"UNIDADES RECEBIDAS: {mov[4]}")
                elif mov[3] == 'VENDA' or mov[3] == 'PERCA' or mov[3] == 'TRANSFERÊNCIA':
                    print(f"UNIDADES DESFAZIDAS: {mov[4]}")

def telaHistMov(cursor, conexao, nome=None):
    op = "historicoMovimentacao"
    while True:
        historico = m.consultaMov(cursor)
        if not historico:
            print('AINDA NÃO FORAM REGISTRADAS MOVIMENTAÇÕES! ')
            return
        filtro = input('Deseja utilizar filtro?')
        if filtro.lower() in ('s', 'sim'):
            n = input('Insira o nome(ENTER para pular): ')
            quemCad = input('Insira quem cadastrou o produto(ENTER para pular): ')
            idProd = input('Insira o ID de algum produto(ENTER para pular): ')
            try:
                if idProd!='':
                    idProd = int(idProd)
                    if idProd<=0:
                        print('INSIRA VALORES ACIMA DE 0 REAIS!')
                        continue
            except ValueError:
                            print("ERRO: INSIRA APENAS VALORES INTEIROS E POSITIVOS!")
                            continue
            try:
                unidMin = input("Insira a quantidade de unidades minímas envolvidas na movimentação(ENTER para pular): ")
                if unidMin!='':
                    unidMin = int(unidMin)
                    if unidMin<=0:
                        print('INSIRA VALORES ACIMA DE 0 UNIDADES! ')
                        continue
            except ValueError:
                print("ERRO: INSIRA APENAS VALORES INTEIROS E POSITIVOS!")
                continue
            try:
                unidMax = input("Insira a quantidade de unidades minímas envolvidas na movimentação(ENTER para pular): ")
                if unidMax!='':
                    unidMax = int(unidMax)
                    if unidMax<=0:
                        print('INSIRA VALORES ACIMA DE 0 UNIDADES! ')
                        continue
            except ValueError:
                print("ERRO: INSIRA APENAS VALORES INTEIROS E POSITIVOS!")
                continue
            try:
                valorMin = input("Insira o valor mínimo envolvido nas movimentações(ENTER para pular): ")
                if valorMin!='':
                    valorMin = int(valorMin)
                    valorMin = valorMin*100
                    if valorMin<=0:
                        print('INSIRA VALORES ACIMA DE 0 REAIS! ')
                        continue
            except ValueError:
                print("ERRO: INSIRA APENAS NÚMEROS POSITIVOS!")
                continue
            try:
                valorMax = input("Insira o valor mínimo envolvido nas movimentações(ENTER para pular): ")
                if valorMax!='':
                    valorMax = int(valorMax)
                    valorMax = valorMax*100
                    if valorMax<=0:
                        print('INSIRA VALORES ACIMA DE 0 REAIS! ')
                        continue
            except ValueError:
                print("ERRO: INSIRA APENAS NÚMEROS POSITIVOS!")
                continue
            print('QUAL O TIPO DE OPERAÇÃO?')
            print('[1] COMPRA')
            print('[2] VENDA')
            print('[3] TRANSFERÊNCIA')
            print('[4] DEVOLUÇÃO')
            print('[5] PERCA')
            mov = input('Qual opção escolhida?(ENTER para pular)')
            match mov:
                case "1":
                    mov = 'COMPRA'
                case "2":
                    mov = 'VENDA'
                case "3":
                    mov = "TRANSFERÊNCIA"
                case "4":
                    mov = "DEVOLUÇÃO"
                case "5":
                    mov = "PERCA"
                case "":
                    mov = ""
                case _:
                    print('ERRO! INSIRA APENAS NÚMEROS NÚMEROS ENTRE 1 E 2')
            dataInicial = ""
            dataUltima = ""
            fd = input('Insira o intervalo de datas!(ENTER para pular): ')
            if fd!="":
                try:
                    dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                    verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
                    dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                    verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
                except ValueError:
                    if dataInicial=="" or dataUltima=="":
                        pass
                    else:
                        print('ERRO! AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!')
                        continue
            else:
                dataUltima = ""
                dataInicial = ""
            historico = f.filtragemMov(n, quemCad, idProd, unidMin, unidMax, valorMin, valorMax, dataInicial, dataUltima, cursor, mov)
            if not historico:
                print('NÃO HÁ MOVIMENTAÇÕES COM ESTAS ESPECIFICAÇÕES')
                return
            else:
                listarHistMov(historico)
                return
        else:
            listarHistMov(historico)
            return

def telaEditarSaldo(cursor, conexao, nome=None):
    saldo = s.verificarSaldo(cursor)
    print('[1] APLICAÇÃO ')
    print('[2] RETIRADA')
    while True:
        try:
            op = int(input('Qual operação deseja realizar? '))
        except ValueError:
            print('INSIRA APENAS NÚMEROS DE 1 A 2!')
            continue
        try:
            match op:
                case 1:
                    ap = float(input('Quanto deseja adicionar: R$'))
                    if ap<=0:
                        print('INSIRA UM VALOR MAIOR QUE 0!')
                        continue
                    ap = round(ap*100)
                    s.editarSaldo(op, ap, saldo, cursor, conexao, nome)
                    return
                case 2:
                    ret = float(input('Quanto deseja retirar: R$'))
                    if ret<=0:
                        print('INSIRA UM VALOR MAIOR QUE 0')
                        continue
                    ret = round(ret*100)
                    if saldo<ret:
                        print('VOCÊ NÃO PODE REALIZAR ESTÁ RETIRADA!')
                        print('MOTIVO: SALDO INSUFICIENTE')
                        return
                    s.editarSaldo(op, ret, saldo, cursor, conexao, nome)
                    return
                case _:
                    print('INSIRA APENAS NÚMEROS DE 1 A 2 ')
        except ValueError:
            print('ERRO! INSIRA APENAS NÚMEROS POSITIVOS!')

def telaRegMov(cursor, conexao, nome=None):
    saldo = s.verificarSaldo(cursor)
    while True:
        print('[1] COMPRA')
        print('[2] VENDA')
        print('[3] TRANSFERÊNCIA')
        print('[4] DEVOLUÇÃO')
        print('[5] PERCA')
        try:
            op = int(input('Qual a movimentação realizada? '))
        except ValueError:
            print('ERRO! INSIRA APENAS números de 1 a 5!')
            continue
        match op:
            case 1:
                tip = 'COMPRA'
                try:
                    idProduto = int(input('Insira o ID do produto: '))
                except ValueError:
                    print('ERRO! INSIRA VALORES INTEIROS!')
                    continue
                if idProduto<=0:
                    print('INSIRA UM VALOR MAIOR QUE 0!')
                    continue
                resultado = p.buscarProduto(idProduto, cursor)
                if resultado is None:
                    print('ERRO: PRODUTO NÃO ENCONTRADO!')
                    return
                produto = resultado[0]
                print(f'Produto selecionado >>{produto}<<')
                try:
                    q = int(input('Quantas unidades foram recebidas? '))
                except ValueError:
                    print('ERRO! INSIRA VALORES INTEIROS')
                    continue
                if q<=0:
                    print('INSIRA UM VALOR MAIOR QUE 0')
                    continue
                try:
                    invest = float(input('Insira o valor do investimento: '))
                except ValueError:
                    print('ERRO! INSIRA NÚMEROS REAIS!')
                    continue
                if invest<0:
                    print('INSIRA UM VALOR POSITIVO')
                    continue
                invest = round(invest*100)
                if invest>saldo:
                    print('VOCÊ NÃO PODE REALIZAR ESTÁ COMPRA! ')
                    print('MOTIVO: SALDO INSUFICIENTE')
                    return
                m.registroMov(produto, idProduto, tip, q, cursor, conexao, nome, invest)
                return
            case 2:
                tip = 'VENDA'
                try:
                    idProduto = int(input('Insira o ID do produto: '))
                except ValueError:
                    print('ERRO! INSIRA NÚMEROS INTEIROS')
                    continue
                if idProduto<=0:
                    print('INSIRA UM VALOR MAIOR QUE 0!')
                    continue
                resultado = p.buscarProduto(idProduto, cursor)
                if resultado is None:
                    print('ERRO: PRODUTO NÃO ENCONTRADO!')
                    return
                produto = resultado[0]
                unidades = resultado[1]
                print(f'Produto selecionado >>{produto}<<')
                try:
                    q = int(input('Quantas unidades foram vendidas? '))
                except ValueError:
                    print('ERRO! INSIRA NÚMEROS INTEIROS!')
                    continue
                if q<=0:
                    print("INSIRA UM VALOR INTEIRO MAIOR QUE 0!")
                    continue
                if q>unidades:
                    print('VOCÊ NÃO PODE REALIZAR ESTÁ VENDA! ')
                    print('MOTIVO: ESTOQUE INSUFICIENTE')
                    return
                try:
                    invest = float(input('insira o valor da venda: '))
                except ValueError:
                    print('ERRO! INSIRA NÚMEROS REAIS!')
                    continue
                if invest<0:
                    print('INSIRA UM VALOR MAIOR QUE 0')
                    continue
                invest = round(invest*100)
                m.registroMov(produto, idProduto, tip, q, cursor, conexao, nome, invest)
                return
            case 3:
                tip = 'TRANSFERÊNCIA'
                try:
                    idProduto = int(input('Insira o ID do produto: '))
                except ValueError:
                    print('ERRO! INSIRA NÚMEROS INTEIROS')
                    continue
                if idProduto<=0:
                    print('INSIRA UM VALOR MAIOR QUE 0!')
                    continue
                resultado = p.buscarProduto(idProduto, cursor)
                if resultado is None:
                    print('ERRO: PRODUTO NÃO ENCONTRADO!')
                    return
                produto = resultado[0]
                unidades = resultado[1]
                print(f'Produto selecionado >>{produto}<<')
                try:
                    q = int(input('Quantas unidades foram transferidas? '))
                except ValueError:
                    print('ERRO! INSIRA NÚMEROS INTEIROS')
                    continue
                if q<=0:
                    print('INSIRA UM VALOR MAIOR QUE 0!')
                    continue
                if q>unidades:
                    print('VOCÊ NÃO PODE REALIZAR ESTÁ MOVIMENTAÇÃO! ')
                    print('MOTIVO: ESTOQUE INSUFICIENTE')
                    return
                try:
                    invest = float(input('Quanto custou o transporte? '))
                except ValueError:
                    print('ERRO! INSIRA NÚMEROS REAIS')
                    continue
                if invest<0:
                    print('INSIRA UM VALOR MAIOR QUE 0')
                    continue
                invest = round(invest*100)
                if invest>saldo:
                    print('VOCÊ NÃO PODE REALIZAR ESTÁ TRANSFERÊNCIA! ')
                    print('MOTIVO: SALDO INSUFICIENTE')
                    return
                m.registroMov(produto, idProduto, tip, q, cursor, conexao, nome, invest)
                return
            case 4:
                tip = 'DEVOLUÇÃO'
                try:
                    idProduto = int(input('Insira o ID do produto: '))
                except ValueError:
                    print('ERRO! INSIRA NÚMEROS INTEIROS')
                    continue
                if idProduto<=0:
                    print('INSIRA UM VALOR MAIOR QUE 0!')
                    continue
                resultado = p.buscarProduto(idProduto, cursor)
                if resultado is None:
                    print('ERRO: PRODUTO NÃO ENCONTRADO!')
                    return
                produto = resultado[0]
                print(f'Produto selecionado >>{produto}<<')
                try:
                    q = int(input('Quantas unidades foram devolvidas? '))
                except ValueError:
                    print('ERRO! INSIRA NÚMEROS INTEIROS')
                    continue
                if q<=0:
                    print('INSIRA UM VALOR MAIOR QUE 0!')
                    continue
                try:
                    invest = float(input('Qual o valor do reembolso? '))
                except ValueError:
                    print('ERRO! INSIRA NÚMEROS REAIS')
                    continue
                if invest<0:
                    print('INSIRA UM VALOR POSITIVO')
                    continue
                invest = round(invest*100)
                m.registroMov(produto, idProduto, tip, q, cursor, conexao, nome, invest)
                return
            case 5:
                tip = 'PERCA'
                try:
                    idProduto = int(input('Insira o ID do produto: '))
                except ValueError:
                    print('ERRO! INSIRA NÚMEROS INTEIROS')
                    continue
                if idProduto<=0:
                    print('INSIRA UM VALOR MAIOR QUE 0!')
                    continue
                resultado = p.buscarProduto(idProduto, cursor)
                if resultado is None:
                    print('ERRO: PRODUTO NÃO ENCONTRADO!')
                    return
                produto = resultado[0]
                print(f'Produto selecionado >>{produto}<<')
                try:
                    q = int(input('Quantas unidades foram perdidas? '))
                except ValueError:
                    print('ERRO! INSIRA NÚMEROS INTEIROS!')
                    continue
                if q <= 0:
                    print("INSIRA UM VALOR MAIOR QUE 0!")
                    continue
                m.registroMov(produto, idProduto, tip, q, cursor, conexao, nome)
                return
            case _:
                print('ERRO! INSIRA APENAS VALORES ENTRE 1 E 5!')
def telaRelatorio(cursor, conexao, nome=None):
    while True:
        try:
            print('[1] PRODUTOS')
            print('[2] ATIVIDADE')
            print('[3] EXTRATO')
            print('[4] ESTOQUE')
            try:
                rel = int(input('Qual relatório deseja gerar? '))
            except ValueError:
                print('ERRO! INSIRA NÚMEROS DE 1 A 2!')
                continue
            match rel:
                case 1:
                    nomeArquivo = 'produtos' 
                    filtro = input('Deseja utilizar filtro? ')
                    if filtro.lower() in ('s', 'sim'):
                        valorMin = input('Insira o valor mínimo(ENTER para pular): R$')
                        if valorMin!='':
                            try:
                                valorMin = float(valorMin)
                                valorMin = round(valorMin*100)
                                if valorMin<0:
                                    print('INSIRA UM VALOR POSITIVO!')
                                    continue
                            except ValueError:
                                print('ERRO! INSIRA NÚMEROS REAIS')
                                continue
                        valorMax = input('Insira o valor máximo(ENTER para pular): ')
                        if valorMax!='':
                            try:
                                valorMax = float(valorMax)
                                valorMax = round(valorMax*100)
                                if valorMax<0:
                                    print('INSIRA UM VALOR POSITIVO!')
                                    continue
                            except ValueError:
                                print('ERRO! INSIRA UM NÚMERO REAL')
                                continue
                        estoqMin = input('Insira a disponibilidade mínima(ENTER para pular): ')
                        if estoqMin!='':
                            try:
                                estoqMin = int(estoqMin)
                                if estoqMin<0:
                                    print('INSIRA UM VALOR INTEIRO E POSITIVO!')
                                    continue
                            except ValueError:
                                print('ERRO! INSIRA UM NÚMERO INTEIRO!')
                                continue
                        estoqMax = input('Insira a disponibilidade máxima(ENTER para pular): ')
                        if estoqMax!='':
                            try:
                                estoqMax=int(estoqMax)
                                if estoqMax<0:
                                    print('INSIRA UM VALOR INTEIRO E POSITIVO')
                                    continue
                            except ValueError:
                                print('ERRO! INSIRA UM NÚMERO INTEIRO!')
                        dataInicial = ""
                        dataUltima = ""
                        fd = input('Insira o intervalo de datas!(ENTER para pular): ')
                        if fd!="":
                            try:
                                dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                                verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
                                dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                                verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
                            except ValueError:
                                if dataInicial=="" or dataUltima=="":
                                    pass
                                else:
                                    print('ERRO! AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!')
                                    continue
                        else:
                            dataUltima = ""
                            dataInicial = ""
                        funcao = 'REL'
                        query, parametros = f.filtragemProdutos(valorMin, valorMax, estoqMin, estoqMax, cursor, dataInicial=dataInicial, dataUltima=dataUltima, f=funcao)
                        df = r.lerDados(rel, conexao, query=query, parametros=parametros)
                        if df.empty:
                            print('NÃO HÁ PRODUTOS CADASTRADOS COM ESTAS ESPECIFICAÇÕES!')
                            return
                        else:
                            r.gerarRel(df, nomeArquivo)
                            print('RELATÓRIO EXPORTADO COM SUCESSO!')
                            return
                    else:
                        df = r.lerDados(rel, conexao)
                        if df.empty:
                            print('NÃO HÁ PRODUTOS CADASTRADOS!')
                            return
                        else:
                            r.gerarRel(df, nomeArquivo)
                            print('RELATÓRIO EXPORTADO COM SUCESSO!')
                            return
                case 2:
                    nomeArquivo = 'atividade'
                    filtro = input('Deseja utilizar filtro?')
                    if filtro.lower() in ('s', 'sim'):
                        quemCad = input('Insira quem realizou (ENTER para pular): ')
                        try:
                            unidMin = input("Insira a quantidade de unidades minímas envolvidas na movimentação(ENTER para pular): ")
                            if unidMin!='':
                                unidMin = int(unidMin)
                                if unidMin<=0:
                                    print('INSIRA VALORES ACIMA DE 0 UNIDADES! ')
                                    continue
                        except ValueError:
                            print("ERRO: INSIRA APENAS VALORES INTEIROS E POSITIVOS!")
                            continue
                        try:
                            unidMax = input("Insira a quantidade de unidades minímas envolvidas na movimentação(ENTER para pular): ")
                            if unidMax!='':
                                unidMax = int(unidMax)
                                if unidMax<=0:
                                    print('INSIRA VALORES ACIMA DE 0 UNIDADES! ')
                                    continue
                        except ValueError:
                            print("ERRO: INSIRA APENAS VALORES INTEIROS E POSITIVOS!")
                            continue
                        try:
                            valorMin = input("Insira o valor mínimo envolvido nas movimentações(ENTER para pular): ")
                            if valorMin!='':
                                valorMin = int(valorMin)
                                valorMin = valorMin*100
                                if valorMin<=0:
                                    print('INSIRA VALORES ACIMA DE 0 REAIS! ')
                                    continue
                        except ValueError:
                            print("ERRO: INSIRA APENAS NÚMEROS POSITIVOS!")
                            continue
                        try:
                            valorMax = input("Insira o valor mínimo envolvido nas movimentações(ENTER para pular): ")
                            if valorMax!='':
                                valorMax = int(valorMax)
                                valorMax = valorMax*100
                                if valorMax<=0:
                                    print('INSIRA VALORES ACIMA DE 0 REAIS! ')
                                    continue
                        except ValueError:
                            print("ERRO: INSIRA APENAS NÚMEROS POSITIVOS!")
                            continue
                        print('Qual o tipo de operação!(ENTER para pular!)')
                        print('[1] COMPRA')
                        print('[2] VENDA')
                        print('[3] TRANSFERÊNCIA')
                        print('[4] DEVOLUÇÃO')
                        print('[5] PERCA')
                        mov = input('Qual a movimentação realizada? ')
                        match mov:
                            case "1":
                                mov = "COMPRA"
                            case "2":
                                mov = "VENDA"
                            case "3":
                                mov = "TRANSFERÊNCIA"
                            case "4":  
                                mov = "DEVOLUÇÃO" 
                            case "5":
                                mov = "PERCA"
                            case "":
                                mov = ""
                            case _:
                                print('ERRO! INSIRA APENAS VALORES ENTRE 1 E 5!')
                                continue
                        dataInicial = ""
                        dataUltima = ""
                        fd = input('Insira o intervalo de datas!(ENTER para pular): ')
                        if fd!="":
                            try:
                                dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                                verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
                                dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                                verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
                            except ValueError:
                                if dataInicial=="" or dataUltima=="":
                                    pass
                                else:
                                    print('ERRO! AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!')
                                    continue
                        else:
                            dataUltima = ""
                            dataInicial = ""
                        query, parametros = f.filtragemMovRel(quemCad, unidMin, unidMax, valorMin, valorMax, dataInicial, dataUltima, cursor, mov)
                        df = r.lerDados(rel, conexao, query=query, parametros=parametros)
                        if df.empty:
                            print('NÃO HÁ PRODUTOS CADASTRADOS')
                            return
                        else:
                            r.gerarRel(df, nomeArquivo)
                            print('RELATÓRIO EXPORTADO COM SUCESSO!')
                            return
                    else:
                        df = r.lerDados(rel, conexao)
                        if df.empty:
                            print('NÃO HÁ PRODUTOS CADASTRADOS!')
                            return
                        else:
                            r.gerarRel(df, nomeArquivo)
                            print('RELATÓRIO EXPORTADO COM SUCESSO!')
                            return
                case 3:
                    nomeArquivo = 'extrato'
                    filtro = input('Deseja utilizar filtro? ')
                    if filtro.lower() in ('s', 'sim'):
                        try:
                            quemCad = input('Insira quem realizou a modificação(ENTER para pular): ')
                            print('Qual o tipo de operação!(ENTER para pular!)')
                            print('[1] ENTRADA')
                            print('[2] SAÍDA')
                            tip = input('Qual o tipo de operação? ')
                            match tip:
                                case "1":
                                    tip = "ENTRADA"
                                case "2":
                                    tip = "SAÍDA"
                                case "":
                                    tip = ""
                                case _:
                                    print('ERRO! INSIRA APENAS VALORES ENTRE 1 E 2!')
                                    continue
                            valorMin = input('Insira o valor mínimo(ENTER para pular): R$')
                            if valorMin!='':
                                valorMin = float(valorMin)
                                valorMin = round(valorMin*100)
                                if valorMin<0:
                                    print('INSIRA UM VALOR POSITIVO!')
                                    continue
                            valorMax = input('Insira o valor máximo(ENTER para pular): R$')
                            if valorMax!='':
                                valorMax = float(valorMax)
                                valorMax = round(valorMax*100)
                                if valorMax<0:
                                    print('INSIRA UM VALOR POSITIVO!')
                                    continue
                        except ValueError:
                            print('INSIRA NÚMEROS REAIS E POSITIVOS')
                            continue
                        dataInicial = ""
                        dataUltima = ""
                        fd = input('Insira o intervalo de datas!(ENTER para pular): ')
                        if fd!="":
                            try:
                                dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                                verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
                                dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                                verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
                            except ValueError:
                                if dataInicial=="" or dataUltima=="":
                                    pass
                                else:
                                    print('ERRO! AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!')
                                    continue
                        else:
                            dataUltima = ""
                            dataInicial = ""
                        funcao = 'REL'
                        query, parametros = f.filtragemSaldo(quemCad, tip, valorMin, valorMax,  dataInicial, dataUltima, cursor, f=funcao)
                        df = r.lerDados(rel, conexao, query=query, parametros=parametros)
                        if df.empty:
                            print('NÃO HÁ PRODUTOS CADASTRADOS COM ESTAS ESPECIFICAÇÕES!')
                            return
                        else:
                            r.gerarRel(df, nomeArquivo)
                            print('RELATÓRIO EXPORTADO COM SUCESSO!')
                            return
                    else:
                        df = r.lerDados(rel, conexao)
                        if df.empty:
                            print('NÃO HÁ PRODUTOS CADASTRADOS!')
                            return
                        else:
                            r.gerarRel(df, nomeArquivo)
                            print('RELATÓRIO EXPORTADO COM SUCESSO!')
                            return

                case 4:
                    nomeArquivo = 'estoque'
                    filtro = input('Deseja utilizar filtro? ')
                    if filtro.lower() in ('s', 'sim'):
                        quemCad = input('Insira quem cadastrou o produto(ENTER para pular): ')
                        valorMin = input('Insira o valor mínimo(ENTER para pular): R$')
                        if valorMin!='':
                            try:
                                valorMin = float(valorMin)
                                valorMin = round(valorMin*100)
                                if valorMin<0:
                                    print('INSIRA UM VALOR POSITIVO!')
                                    continue
                            except ValueError:
                                print('ERRO! INSIRA NÚMEROS REAIS')
                                continue
                        valorMax = input('Insira o valor máximo(ENTER para pular): ')
                        if valorMax!='':
                            try:
                                valorMax = float(valorMax)
                                valorMax = round(valorMax*100)
                                if valorMax<0:
                                    print('INSIRA UM VALOR POSITIVO!')
                                    continue
                            except ValueError:
                                print('ERRO! INSIRA UM NÚMERO REAL')
                                continue
                        estoqMin = input('Insira a disponibilidade mínima(ENTER para pular): ')
                        if estoqMin!='':
                            try:
                                estoqMin = int(estoqMin)
                                if estoqMin<0:
                                    print('INSIRA UM VALOR INTEIRO E POSITIVO!')
                                    continue
                            except ValueError:
                                print('ERRO! INSIRA UM NÚMERO INTEIRO!')
                                continue
                        estoqMax = input('Insira a disponibilidade máxima(ENTER para pular): ')
                        if estoqMax!='':
                            try:
                                estoqMax=int(estoqMax)
                                if estoqMax<0:
                                    print('INSIRA UM VALOR INTEIRO E POSITIVO')
                                    continue
                            except ValueError:
                                print('ERRO! INSIRA UM NÚMERO INTEIRO!')
                                continue
                        dataInicial = ""
                        dataUltima = ""
                        fd = input('Insira o intervalo de datas!(ENTER para pular): ')
                        if fd!="":
                            try:
                                dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                                verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
                                dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                                verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
                            except ValueError:
                                if dataInicial=="" or dataUltima=="":
                                    pass
                                else:
                                    print('ERRO! AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!')
                                    continue
                        else:
                            dataUltima = ""
                            dataInicial = ""
                        funcao = 'REL'
                        query, parametros = f.filtragemProdutos(valorMin, valorMax, estoqMin, estoqMax, cursor, dataInicial=dataInicial, dataUltima=dataUltima, quemCad=quemCad, f=funcao)
                        df = r.lerDados(rel, conexao, query=query, parametros=parametros)
                        if df.empty:
                            print('NÃO HÁ PRODUTOS CADASTRADOS COM ESTAS ESPECIFICAÇÕES!')
                            return
                        else:
                            r.gerarRel(df, nomeArquivo)
                            print('RELATÓRIO EXPORTADO COM SUCESSO!')
                            return
                    else:
                        df = r.lerDados(rel, conexao)
                        if df.empty:
                            print('NÃO HÁ PRODUTOS CADASTRADOS!')
                            return
                        else:
                            r.gerarRel(df, nomeArquivo)
                            print('RELATÓRIO EXPORTADO COM SUCESSO!')
                            return
                case _:
                    print('ERRO! INSIRA APENAS NÚMEROS DE 1 A 3!')
        except ValueError:
            print('ERRO! INSIRA APENAS NÚMEROS DE 1 A 3!')
    

def listarHistSaldo(historico):
    for mov in historico:
                print(f"=====================")
                print(f"{mov[2]} DE R${(mov[1])/100}")
                print(f'REALIZADA EM {mov[4]} AS {mov[5]} por {mov[3]}')
                

def telaHistSaldo(cursor, conexao, nome=None): 
    while True:
        historico = s.comsultaHistSaldo(cursor)
        if not historico:
            print('AINDA NÃO FORAM REGISTRADAS MOVIMENTAÇÕES! ')
            return
        filtro = input('Deseja utilizar filtro?')
        if filtro.lower() in ('s', 'sim'):
            try:
                quemCad = input('Insira quem realizou a modificação(ENTER para pular): ')
                print('Qual o tipo de operação!(ENTER para pular!)')
                print('[1] ENTRADA')
                print('[2] SAÍDA')
                tip = input('Qual o tipo de operação? ')
                match tip:
                    case "1":
                        tip = "ENTRADA"
                    case "2":
                        tip = "SAÍDA"
                    case "":
                        tip = ""
                    case _:
                        print('ERRO! INSIRA APENAS VALORES ENTRE 1 E 2!')
                        continue
                valorMin = input('Insira o valor mínimo(ENTER para pular): R$')
                if valorMin!='':
                    valorMin = float(valorMin)
                    valorMin = round(valorMin*100)
                    if valorMin<0:
                        print('INSIRA UM VALOR POSITIVO!')
                        continue
                valorMax = input('Insira o valor máximo(ENTER para pular): R$')
                if valorMax!='':
                    valorMax = float(valorMax)
                    valorMax = round(valorMax*100)
                    if valorMax<0:
                        print('INSIRA UM VALOR POSITIVO!')
                        continue
            except ValueError:
                print('INSIRA NÚMEROS REAIS E POSITIVOS')
                continue
            dataInicial = ""
            dataUltima = ""
            fd = input('Insira o intervalo de datas!(ENTER para pular): ')
            if fd!="":
                try:
                    dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                    verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
                    dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                    verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
                except ValueError:
                    if dataInicial=="" or dataUltima=="":
                        pass
                    else:
                        print('ERRO! AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!')
                        continue
            else:
                dataUltima = ""
                dataInicial = ""
            historico = f.filtragemSaldo(quemCad, tip, valorMin, valorMax, dataInicial, dataUltima, cursor)
            if not historico:
                print('NÃO HÁ MOVIMENTAÇÕES COM ESTAS ESPECIFICAÇÕES')
                return
            else:
                listarHistSaldo(historico)
                return
        else:
            listarHistSaldo(historico)
            return