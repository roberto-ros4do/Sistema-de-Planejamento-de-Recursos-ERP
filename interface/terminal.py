from servicos import produtos as p
from servicos import movimentacoes as m
from servicos import relatorios as r
from servicos import saldo as s
from servicos import login as l
from servicos import filtro as f
import datetime as dt

def telaLogin(cursor, conexao):
    import socket
    while True:
        try:
            maq = socket.gethostname()
            resultado = l.verificaTentativas(maq, cursor, conexao)
            if resultado is None:
                identificador = maq
                tentativas = 4
                bloqueadoAte = None
            else:
                identificador = resultado[0]
                tentativas = resultado[1]
                bloqueadoAte = resultado[2]
            print(type(bloqueadoAte))
            if bloqueadoAte is None or bloqueadoAte <= dt.datetime.now():
                login = input('Insira seu login: ')
                senha = input('Insira sua senha')
                existe, nome = l.verificaLogin(cursor, conexao, login, senha)
                if existe:
                    tentativas = 0
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
                        return False, None
            else:
                print('-='*25)            
                print('VOCÊ ACABOU COM SUAS TENTATIVAS, TENTE NOVAMENTE MAIS TARDE')
                print('-='*25)  
        except ValueError:
            print('INSIRA APENAS NÚMEROS!')


def telaCadastrarUsuario(cursor, conexao):
    while True:
        nome = input('Insira nome: ')
        login = input('Insira login: ')
        while True:
            existe = l.verificaLoginRepetido(login)
            if existe:
                print('Este login já existe! Insira um diferente')
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
        l.cadastraLogin(cursor, conexao, nome, login, senha, cargo)
        print('USUÁRIO CADASTRADO! ')
        return

def telaCadastroProduto(cursor, conexao, nome):
    while True:
        n = input('Insira o nome do produto: ')
        if n is None:
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
        invest = int(invest*100)
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
        v = int(v*100)
        esp2 = ''
        esp = input('Possui alguma especificação[S/N]? ')
        if esp.lower() in ('s', 'sim'):
            esp2 = input('Insira a especificação: ')
        id = p.cadastroProduto(n, q, v, invest, esp2, cursor, conexao, nome)
        m.registroMov(n,i)
        return


def listarProdutos(produtos):
    for produto in produtos:
        print(f"=========={produto[1]}===========")
        print(f"ID DO PRODUTO: [{produto[0]}]")
        print(f"DISPONIBILIDADE NO ESTOQUE: {produto[2]}")
        print(f"PREÇO: R$ {(produto[3])/100}")
        print(f'CRIADO EM {produto[5]} AS {produto[6]} POR {produto[7]}')
        if produto[4] != '':
            print(f"ESPECIFICAÇÃO: {produto[4]}")
        
def telaListagemProdutos(cursor, conexao):
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
                    id = input('Insira o ID de algum produto(ENTER para pular): ')
                    if id!='':
                        try:
                            id = int(id)
                            if id<=0:
                                print("INSIRA UM VALOR MAIOR QUE 0!")
                                continue
                        except ValueError:
                            print('ERRO! INSIRA NÚMEROS INTEIROS')
                            continue
                    valorMin = input('Insira o valor mínimo(ENTER para pular): R$')
                    if valorMin!='':
                        try:
                            valorMin = float(valorMin)
                            valorMin = int(valorMin*100)
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
                            valorMax = int(valorMax*100)
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
                    print('ESPECIFICAÇÕES POR DATA DE CADASTRO')
                    print('[1] ÚLTIMA SEMANA')
                    print('[2] MÊS PASSADO')
                    print('[3] INTERVALO DE DATAS')
                    print('(ENTER para pular)')
                    escolha = int(input('Qual opção escolhida? '))    
                    op = "produtos"
                    match escolha:
                        case "1":
                            dataInicial, dataUltima = f.filtragemData(escolha)
                        case "2":
                            dataInicial, dataUltima = f.filtragemData(escolha)
                        case "3":
                            try:
                                dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                                verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
                                dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                                verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
                            except ValueError:
                                print('ERRO! AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!')
                                continue
                        case "":
                            dataInicial = ''
                            dataUltima = ''
                        case _:
                                print('ERRO!INSIRA APENAS NÚMEROS DE 1 A 3!')
                    produtos = f.filtragemProdutos(n, quemCad, id, valorMin, valorMax, estoqMin, estoqMax, dataInicial, dataUltima, cursor)
                    if not produtos:
                            print('NÃO HÁ PRODUTOS COM ESTAS ESPECIFICAÇÕES')
                            return
                    else:
                        listarProdutos(produtos)
                        return
                else:
                    listarProdutos(produtos)
                    return

def telaDeletar(cursor, conexao):
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
            p.deletarProduto(idProd, cursor)
            print(f'[{produto}] DELETADO')
            conexao.commit()
            return
        except ValueError:
            print('INSIRA APENAS NÚMEROS INTEIROS E POSITIVOS')

def listarHistMov(historico):
    for mov in historico:
                print(f"=========={mov[1]}===========")
                print(f'REALIZADA EM {mov[6]} AS {mov[7]} por {mov[8]}')
                print(f"TIPO DE MOVIMENTAÇÃO {mov[3]}")
                if mov[3]=='CADASTRO':
                    print(f'UNIDADES CADASTRADAS: {mov[5]}')
                if mov[4] == 'COMPRA' or mov[4] == 'DEVOLUÇÃO':
                    print(f"UNIDADES RECEBIDAS: {mov[5]}")
                elif mov[4] == 'VENDA' or mov[4] == 'PERCA' or mov[4] == 'TRANSFERÊNCIA':
                    print(f"UNIDADES DESFAZIDAS: {mov[5]}")

def telaHistMov(cursor, conexao):
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
            id = input('Insira o ID de algum produto(ENTER para pular): ')
            try:
                if id!='':
                    id = int(id)
                    if id<=0:
                        print('INSIRA VALORES ACIMA DE 0 REAIS!')
                        continue
                unid = input("Insira a quantidade de unidades envolvidas na movimentação(ENTER para pular): ")
                if unid!='':
                    unid = int(id)
                    if unid<=0:
                        print('INSIRA VALORES ACIMA DE 0 UNIDADES! ')
                        continue
            except ValueError:
                print("ERRO: INSIRA APENAS VALORES INTEIROS E POSITIVOS!")
                continue
            print('QUAL O TIPO DE OPERAÇÃO?')
            print('[1] ENTRADA')
            print('[2] SAÍDA')
            print('(ENTER para pular)')
            mov = input('Qual opção escolhida?')
            match mov:
                case "1":
                    mov = 'ENTRADA'
                case "2":
                    mov = 'SAÍDA'
                case "":
                    mov = ""
                case _:
                    print('ERRO! INSIRA APENAS NÚMEROS NÚMEROS ENTRE 1 E 2')
            print('ESPECIFICAÇÕES POR DATA DE CADASTRO')
            print('[1] ÚLTIMA SEMANA')
            print('[2] MÊS PASSADO')
            print('[3] INTERVALO DE DATAS')
            print('ENTER para pular!')
            escolha = input('Qual opção escolhida? ')
            match escolha:
                case "1":
                    dataInicial, dataUltima = f.filtragemData(escolha)
                case "2":
                    dataInicial, dataUltima = f.filtragemData(escolha)
                case "3":
                    try:
                        dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                        verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
                        dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                        verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
                    except ValueError:
                        print('ERRO! AS DATAS ESTÃO NO FORMATO ERRADO')
                        continue
                case "":
                    dataInicial = ""
                    dataUltima = ""
                case _:
                    print('INSIRA APENAS NÚMEROS ENTRE 1 E 3!')
            historico = f.filtragemMov(n, quemCad, id, unid, dataInicial, dataUltima, cursor, mov)
            if not historico:
                print('NÃO HÁ MOVIMENTAÇÕES COM ESTAS ESPECIFICAÇÕES')
                return
            else:
                listarHistMov(historico)
                return
        else:
            listarHistMov(historico)
            return

def telaEditarSaldo(cursor, conexao, nome):
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
                    ap = int(ap*100)
                    s.editarSaldo(op, ap, saldo, cursor, conexao, nome)
                    return
                case 2:
                    ret = float(input('Quanto deseja retirar: R$'))
                    if ret<=0:
                        print('INSIRA UM VALOR MAIOR QUE 0')
                        continue
                    ret = int(ret*100)
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

def telaRegMov(cursor, conexao, nome):
    saldo = s.verificarSaldo(cursor)
    while True:

            print('[1] ENTRADA ')
            print('[2] SAÍDA ')
            try:
                op = int(input('Qual a movimentação realizada? '))
            except ValueError:
                print('ERRO! INSIRA APENAS números de 1 a 2!')
                continue
            match op:
                case 1:
                    tip = 'ENTRADA'
                    print('[1] COMPRA')
                    print('[2] DEVOLUÇÃO')
                    try:
                        tipo = int(input('Qual o tipo de entrada? '))
                    except ValueError:
                        print('ERRO! INSIRA APENAS NÚMEROS DE 1 A 2!')
                        continue
                    match tipo:
                        case 1:
                            stip = 'COMPRA'
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
                            invest = int(invest*100)
                            if invest>saldo:
                                print('VOCÊ NÃO PODE REALIZAR ESTÁ COMPRA! ')
                                print('MOTIVO: SALDO INSUFICIENTE')
                                return
                            m.registroMov(produto, idProduto, tip, q, cursor, conexao, nome, stip, invest)
                            return
                        case 2:
                            stip = 'DEVOLUÇÃO'
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
                            invest = int(invest*100)
                            m.registroMov(produto, idProduto, tip, q, cursor, conexao, nome, stip, invest)
                            return
                        case _:
                            print('INSIRA APENAS NÚMEROS DE 1 A 2 ')
                case 2:
                    tip = 'SAÍDA'
                    print('[1] VENDA')
                    print('[2] PERCA')
                    print('[3] TRANSFERÊNCIA')
                    try:
                        tipo = int(input('Qual o tipo de saida? '))
                    except ValueError:
                        print('ERRO! INSIRA NÚMEROS DE 1 A 3!')
                        continue
                    match tipo:
                        case 1:
                            stip = 'VENDA'
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
                            invest = int(invest*100)
                            m.registroMov(produto, idProduto, tip, q, cursor, conexao, nome, stip, invest)
                            return
                        case 2:
                            stip = 'PERCA'
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
                            m.registroMov(produto, idProduto, tip, q, cursor, conexao, nome, stip)
                           
                        case 3:
                            stip = 'TRANSFERÊNCIA'
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
                            invest = int(invest*100)
                            if invest>saldo:
                                print('VOCÊ NÃO PODE REALIZAR ESTÁ TRANSFERÊNCIA! ')
                                print('MOTIVO: SALDO INSUFICIENTE')
                                return
                            m.registroMov(produto, idProduto, tip, q, cursor, conexao, nome, stip, invest)
                            return
                        case _:
                            print('INSIRA SOMENTE NÚMEROS DE 1 A 3 ')
                case _:
                    print('INSIRA SOMENTE NÚMEROS DE 1 A 2 ')
        
def telaRelatorio(cursor, conexao):
    while True:
        try:
            print('[1] PRODUTOS')
            print('[2] ATIVIDADE')
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
                        n = input('Insira o nome(ENTER para pular): ')
                        quemCad = input('Insira quem cadastrou o produto(ENTER para pular): ')
                        id = input('Insira o ID de algum produto(ENTER para pular): ')
                        if id!='':
                            try:
                                id = int(id)
                                if id<=0:
                                    print("INSIRA UM VALOR MAIOR QUE 0!")
                                    continue
                            except ValueError:
                                print('ERRO! INSIRA NÚMEROS INTEIROS')
                                continue
                        valorMin = input('Insira o valor mínimo(ENTER para pular): R$')
                        if valorMin!='':
                            try:
                                valorMin = float(valorMin)
                                valorMin = int(valorMin*100)
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
                                valorMax = int(valorMax*100)
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
                        print('ESPECIFICAÇÕES POR DATA DE CADASTRO')
                        print('[1] ÚLTIMA SEMANA')
                        print('[2] MÊS PASSADO')
                        print('[3] INTERVALO DE DATAS')
                        print('(ENTER para pular)')
                        escolha = input('Qual opção escolhida? ')
                        op = "produtos"
                        match escolha:
                            case "1":
                                dataInicial, dataUltima = f.filtragemData(escolha)
                            case "2":
                                dataInicial, dataUltima = f.filtragemData(escolha)
                            case "3":
                                try:
                                    dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                                    verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
                                    dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                                    verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
                                except ValueError:
                                    print('ERRO! AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!')
                                    continue
                            case "":
                                dataInicial = ""
                                dataUltima = ""
                            case _:
                                print('ERRO! INSIRA APENAS NÚMEROS DE 1 A 3!')
                        f = 'REL'
                        query, parametros = f.filtragemProdutos(n, quemCad, id, valorMin, valorMax, estoqMin, estoqMax, dataInicial, dataUltima, cursor, f)
                        df = s.lerDados(rel, conexao, query=query, parametros=parametros)
                        if df.empty:
                            print('NÃO HÁ PRODUTOS CADASTRADOS COM ESTAS ESPECIFICAÇÕES!')
                            return
                        else:
                            r.geralRel(df, nomeArquivo)
                            print('RELATÓRIO EXPORTADO COM SUCESSO!')
                            return
                    else:
                        df = s.lerDados(rel, conexao)
                        if df.empty:
                            print('NÃO HÁ PRODUTOS CADASTRADOS!')
                            return
                        else:
                            r.geralRel(df, nomeArquivo)
                            print('RELATÓRIO EXPORTADO COM SUCESSO!')
                            return
                case 2:
                    filtro = input('Deseja utilizar filtro?')
                    if filtro.lower() in ('s', 'sim'):
                        n = input('Insira o nome do produto(ENTER para pular): ')
                        quemCad = input('Insira quem realizou (ENTER para pular): ')
                        id = input('Insira o ID de algum produto(ENTER para pular): ')
                        try:
                            if id!='':
                                id = int(id)
                                if id<=0:
                                    print('INSIRA VALORES ACIMA DE 0 REAIS!')
                                    continue
                            unid = input("Insira a quantidade de unidades envolvidas na movimentação(ENTER para pular): ")
                            if unid!='':
                                unid = int(id)
                                if unid<=0:
                                    print('INSIRA VALORES ACIMA DE 0 UNIDADES! ')
                                    continue
                        except ValueError:
                            print("ERRO: INSIRA APENAS VALORES INTEIROS E POSITIVOS!")
                            continue
                        print('QUAL O TIPO DE OPERAÇÃO?')
                        print('[1] ENTRADA')
                        print('[2] SAÍDA')
                        print('(ENTER para pular)')
                        mov = input('Qual opção escolhida?')
                        match mov:
                            case "1":
                                mov = 'ENTRADA'
                            case "2":
                                mov = 'SAÍDA'
                            case "":
                                mov = ""
                            case _:
                                print('ERRO! INSIRA APENAS NÚMEROS NÚMEROS ENTRE 1 E 2')
                        print('ESPECIFICAÇÕES POR DATA DE CADASTRO')
                        print('[1] ÚLTIMA SEMANA')
                        print('[2] MÊS PASSADO')
                        print('[3] INTERVALO DE DATAS')
                        print('ENTER para pular!')
                        escolha = input('Qual opção escolhida? ')
                        match escolha:
                            case "1":
                                dataInicial, dataUltima = f.filtragemData(escolha)
                            case "2":
                                dataInicial, dataUltima = f.filtragemData(escolha)
                            case "3":
                                try:
                                    dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                                    verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
                                    dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                                    verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
                                except ValueError:
                                    print('ERRO! AS DATAS ESTÃO NO FORMATO ERRADO')
                                    continue
                            case "":
                                dataInicial = ''
                                dataUltima = ''
                            case _:
                                print('ERRO! INSIRA APENAS NÚMEROS ENTRE 1 E 3!')
                        f = 'REL'
                        query, parametros = f.filtragemMov(n, quemCad, id, unid, dataInicial, dataUltima, cursor, mov, f)
                        df = s.lerDados(rel, conexao, query=query, parametros=parametros)
                        if df.empty:
                            print('NÃO HÁ PRODUTOS CADASTRADOS')
                            return
                        else:
                            r.geralRel(df, nomeArquivo)
                            print('RELATÓRIO EXPORTADO COM SUCESSO!')
                            return
                    else:
                        df = s.lerDados(rel, conexao)
                        if df.empty:
                            print('NÃO HÁ PRODUTOS CADASTRADOS!')
                            return
                        else:
                            r.geralRel(df, nomeArquivo)
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
                print(f'REALIZADA EM {mov[5]} AS {mov[6]} por {mov[7]}')
                

def telaHistSaldo(cursor, conexao, nome): 
    op = "histSaldo"
    while True:
        historico = s.consultaHistSaldo(cursor)
        if not historico:
            print('AINDA NÃO FORAM REGISTRADAS MOVIMENTAÇÕES! ')
            return
        filtro = input('Deseja utilizar filtro?')
        if filtro.lower() in ('s', 'sim'):
            try:
                quemCad = input('Insira quem realizou a modificação(ENTER para pular): ')
                valorMin = input('Insira o valor mínimo(ENTER para pular): R$')
                if valorMin!='':
                    valorMin = float(valorMin)
                    valorMin = int(valorMin*100)
                    if valorMin<0:
                        print('INSIRA UM VALOR POSITIVO!')
                        continue
                valorMax = input('Insira o valor máximo(ENTER para pular): R$')
                if valorMax!='':
                    valorMax = float(valorMax)
                    valorMax = int(valorMax*100)
                    if valorMax<0:
                        print('INSIRA UM VALOR POSITIVO!')
                        continue
            except ValueError:
                print('INSIRA NÚMEROS REAIS E POSITIVOS')
                continue
            print('ESPECIFICAÇÕES POR DATA DE CADASTRO')
            print('[1] ÚLTIMA SEMANA')
            print('[2] MÊS PASSADO')
            print('[3] INTERVALO DE DATAS')
            print('ENTER para pular!')
            escolha = input('Qual opção escolhida? ')
            match escolha:
                case "1":
                    dataInicial, dataUltima = f.filtragemData(escolha)
                case "2":
                    dataInicial, dataUltima = f.filtragemData(escolha)
                case "3":
                    try:
                        dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                        verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
                        dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                        verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
                    except ValueError:
                        print('ERRO! AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!')
                        continue
                case "":
                    dataInicial = ''
                    dataUltima = ''
                case _:
                    print('INSIRA APENAS NÚMEROS ENTRE 1 E 3!')
            historico = f.filtragemSaldo(quemCad, valorMin, valorMax, dataInicial, dataUltima, cursor)
            if not historico:
                print('NÃO HÁ MOVIMENTAÇÕES COM ESTAS ESPECIFICAÇÕES')
                return
            else:
                listarHistMov(historico)
                return
        else:
            listarHistSaldo(historico)
            return