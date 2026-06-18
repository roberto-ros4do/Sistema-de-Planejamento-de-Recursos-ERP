from servicos import produtos as p
from servicos import saldo as s
from servicos import filtro as f
from servicos import movimentacoes as m
from servicos import relatorios as r

def telaCadastroProduto(cursor, conexao):
    import datetime as dt
    while True:
        try:
            n = input('Insira o nome do produto: ')
            q = int(input('Insira a disponibilidade no estoque: '))
            invest = float(input('Insira o valor do investimento? '))
            saldo = s.verificarSaldo(cursor)
            if invest>saldo:
                print('ERRO! SALDO INSUFICIENTE ')
                return
            v = float(input('Insira o valor que será cobrado pelo produto: '))
            esp2 = ''
            esp = input('Possui alguma especificação[S/N]? ')
            if esp.lower() in ('s', 'sim'):
                esp2 = input('Insira a especificação: ')
            data = dt.date.today().strftime("%Y/%m/%d")
            hora = dt.datetime.now().time().strftime("%H:%M")
            p.cadastroProduto(n, q, v, invest, esp2, data, hora, cursor, conexao)
            return
        except ValueError:
                print('ERRO! INSIRA APENAS NÚMEROS')

def listarProdutos(produtos):
    for produto in produtos:
        print(f"=========={produto[1]}===========")
        print(f"ID DO PRODUTO: [{produto[0]}]")
        print(f"DISPONIBILIDADE NO ESTOQUE: {produto[2]}")
        print(f"PREÇO: R$ {produto[3]}")
        if produto[4] != '':
            print(f"ESPECIFICAÇÃO: {produto[4]}")
        
def telaListagemProdutos(cursor, conexao):
     while True:
          try:
            produtos = p.consultaProdutos(cursor)
            if not produtos:
                print('AINDA NÃO HÁ PRODUTOS CADASTRADOS!')
                return
            else:
                filtro = input('Deseja utilizar filtro? ')
                if filtro.lower() in ('s', 'sim'):
                    n = input('Insira o nome(ENTER para pular): ')
                    valorMin = input('Insira o valor mínimo(ENTER para pular): ')
                    valorMax = input('Insira o valor máximo(ENTER para pular): ')
                    estoqMin = input('Insira a disponibilidade mínima(ENTER para pular): ')
                    estoqMax = input('Insira a disponibilidade máxima(ENTER para pular): ')
                    n = input('Insira o nome(ENTER para pular): ')
                    if valorMin!='':
                        valorMin = float(valorMin)
                        if valorMin<=0:
                            print('INSIRA VALORES ACIMA DE 0 REAIS!')
                            break
                    valorMax = input('Insira o valor máximo(ENTER para pular): ')
                    if valorMax!='':
                        valorMax = float(valorMax)
                        if valorMax<=0:
                            print('INSIRA VALORES ACIMA DE 0 REAIS!')
                            break
                    estoqMin = input('Insira a disponibilidade mínima(ENTER para pular): ')
                    if estoqMin!='':
                        estoqMin = int(estoqMin)
                        if estoqMin<0:
                            print('INSIRA APENAS NÚMEROS POSITIVOS')
                            break
                    estoqMax = input('Insira a disponibilidade máxima(ENTER para pular): ')
                    if estoqMax!='':
                        estoqMax=int(estoqMax)
                        if estoqMax<0:
                            print('INSIRA APENAS NÚMEROS POSITIVOS')
                            break
                    produtos = p.filtragemProdutos(n, valorMin, valorMax, estoqMin, estoqMax, cursor)
                    if not produtos:
                        print('NÃO HÁ PRODUTOS COM ESTAS ESPECIFICAÇÕES')
                    else:
                        listarProdutos(produtos)
                else:
                    listarProdutos(produtos)
          except ValueError:
              print('ERRO! INSIRA APENAS NÚMEROS NOS FILTROS DE PREÇO E ESTOQUE')  
              

def telaDeletar(cursor, conexao):
    try:
        idProd = int(input('Insira o ID do produto que deseja deletar: '))
        produto = p.buscarProduto(idProd, cursor)
        if produto is None:
                print('ERRO: PRODUTO NÃO ENCONTRADO!')
                return
        p.deletarProduto(idProd, cursor)
        print(f'[{produto}] DELETADO')
        conexao.commit()
    except ValueError:
        print('INSIRA APENAS NÚMEROS')

def listarHisProdutos(historico):
    for mov in historico:
        print(f"=========={mov[1]}===========")
        print(f"ID DO PRODUTO: [{mov[0]}]")
        print(f'CADASTRADO EM {mov[5]} AS {mov[6]}')
        return

def telaHistoricoCadProdutos(cursor, conexao):
    import datetime as dt
    while True:
        try:
            op = "produtos"
            historico = p.consultaProdutos(cursor)
            if not historico:
                print('AINDA NÃO HÁ PRODUTOS CADASTRADOS! ')
                return
            else:
                filtro = input('Deseja utilizar filtro? ')
                if filtro.lower() in ('s', 'sim'):
                    print('[1] ÚLTIMA SEMANA')
                    print('[2] MÊS PASSADO')
                    print('[3] INTERVALO DE DATAS')
                    escolha = int(input('Qual opção escolhida? '))
                    match escolha:
                        case 1:
                            historico = f.filtragemData(escolha, op, cursor)
                            if not historico:
                                print('NÃO HÁ RESULTADOS')
                                return
                            else:
                                listarHisProdutos(historico)
                                return
                        case 2:
                            historico = f.filtragemData(escolha, op, cursor)
                            if not historico:
                                print('NÃO HÁ RESULTADOS')
                                return
                            else:
                                listarHisProdutos(historico)
                                return
                        case 3:
                            dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                            verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
                            dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                            verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
                            historico = f.filtragemData(escolha, op, cursor, dataInicial, dataUltima)
                            if not historico:
                                print('NÃO HÁ RESULTADOS')
                                return
                            else:
                                listarHisProdutos(historico)
                                return
                        case _:
                            print('INSIRA APENAS NÚMEROS ENTRE 1 E 3!')
                else:
                    p.historicoProdutos(historico, cursor)
                    return
        except ValueError:
            print('ERRO! AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!')

def listarHistMov(historico):
    for mov in historico:
                print(f"=========={mov[1]}===========")
                print(f'REALIZADA EM {mov[5]} AS {mov[6]}')
                print(f"TIPO DE MOVIMENTAÇÃO {mov[2]}")
                if mov[3] == 'COMPRA' or mov[3] == 'DEVOLUÇÃO':
                    print(f"UNIDADES RECEBIDAS: {mov[4]}")
                else:
                    print(f"UNIDADES DESFAZIDAS: {mov[4]}")

def telaHistMov(cursor, conexao):
    import datetime as dt
    op = "historicoMovimentacao"
    while True:
        try:
            historico = m.consultaMov(cursor)
            if not historico:
                print('AINDA NÃO FORAM REGISTRADAS MOVIMENTAÇÕES! ')
                return
            filtro = input('Deseja utilizar filtro?')
            if filtro.lower() in ('s', 'sim'):
                print('[1] ÚLTIMA SEMANA')
                print('[2] MÊS PASSADO')
                print('[3] INTERVALO DE DATAS')
                escolha = int(input('Qual opção escolhida? '))
                match escolha:
                    case 1:
                        historico = f.filtragemData(escolha, op, cursor)
                        if not historico:
                            print('NÃO HÁ RESULTADOS')
                            return
                        else:
                            listarHistMov(historico)
                            return
                    case 2:
                        historico = f.filtragemData(escolha, op, cursor)
                        if not historico:
                            print('NÃO HÁ RESULTADOS')
                            return
                        else:
                            listarHistMov(historico)
                            return
                    case 3:
                        dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                        verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
                        dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                        verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
                        historico = f.filtragemData(escolha, op, cursor, dataInicial, dataUltima)
                        if not historico:
                            print('NÃO HÁ RESULTADOS')
                            return
                        else:
                            listarHistMov(historico)
                            return
                    case _:
                        print('INSIRA APENAS NÚMEROS ENTRE 1 E 3!')
            else:
                listarHistMov(historico)
                return
        except ValueError:
            print('ERRO! AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!')

def telaEditarSaldo(cursor, conexao):
    saldo = s.verificarSaldo(cursor)
    print('[1] APLICAÇÃO ')
    print('[2] RETIRADA')
    while True:
        try:
            op = int(input('Qual operação deseja realizar? '))
            match op:
                case 1:
                    ap = float(input('Quanto deseja adicionar '))
                    s.editarSaldo(op, ap, saldo, cursor, conexao)
                    return
                case 2:
                    ret = float(input('Quanto deseja retirar '))
                    if saldo<ret:
                        print('VOCÊ NÃO PODE REALIZAR ESTÁ RETIRADA!')
                        print('MOTIVO: SALDO INSUFICIENTE')
                        return
                    s.editarSaldo(op, ret, saldo, cursor, conexao)
                    return
                case _:
                    print('INSIRA APENAS NÚMEROS DE 1 A 2 ')
        except ValueError:
            print('ERRO! INSIRA APENAS NÚMEROS!')

def telaRegMov(cursor, conexao):
    import datetime as dt
    saldo = s.verificarSaldo(cursor)
    while True:
        try:
            print('[1] ENTRADA ')
            print('[2] SAÍDA ')
            op = int(input('Qual a movimentação realizada? '))
            match op:
                case 1:
                    tip = 'ENTRADA'
                    print('[1] COMPRA')
                    print('[2] DEVOLUÇÃO')
                    tipo = int(input('Qual o tipo de entrada? '))
                    match tipo:
                        case 1:
                            stip = 'COMPRA'
                            idProduto = int(input('Insira o ID do produto: '))
                            resultado = p.buscarProduto(idProduto, cursor)
                            if resultado is None:
                                print('ERRO: PRODUTO NÃO ENCONTRADO!')
                                return
                            produto = resultado[0]
                            print(f'Produto selecionado >>{produto}<<')
                            data = dt.date.today().strftime("%d/%m/%Y")
                            hora = dt.datetime.now().time().strftime("%H:%M")
                            print(f'Produto selecionado >>{produto}<<')
                            q = int(input('Quantas unidades foram recebidas? '))
                            invest = float(input('Insira o valor do investimento: '))
                            if invest>saldo:
                                print('VOCÊ NÃO PODE REALIZAR ESTÁ COMPRA! ')
                                print('MOTIVO: SALDO INSUFICIENTE')
                                return
                            m.registroMov(produto, idProduto, op, tip, stip, q, data, hora, cursor, conexao, invest)
                            return
                        case 2:
                            stip = 'DEVOLUÇÃO'
                            idProduto = int(input('Insira o ID do produto: '))
                            resultado = p.buscarProduto(idProduto, cursor)
                            if resultado is None:
                                print('ERRO: PRODUTO NÃO ENCONTRADO!')
                                return
                            produto = resultado[0]
                            print(f'Produto selecionado >>{produto}<<')
                            q = int(input('Quantas unidades foram devolvidas? '))
                            invest = float(input('Qual o valor do reembolso? '))
                            data = dt.date.today().strftime("%d/%m/%Y")
                            hora = dt.datetime.now().time().strftime("%H:%M")
                            m.registroMov(produto, idProduto, op, tip, stip, q, data, hora, cursor, conexao, invest)
                            return
                        case _:
                            print('INSIRA APENAS NÚMEROS DE 1 A 2 ')
                case 2:
                    tip = 'SAÍDA'
                    print('[1] VENDA')
                    print('[2] PERCA')
                    print('[3] TRANSFERÊNCIA')
                    tipo = int(input('Qual o tipo de saida? '))
                    match tipo:
                        case 1:
                            stip = 'VENDA'
                            idProduto = int(input('Insira o ID do produto: '))
                            resultado = p.buscarProduto(idProduto, cursor)
                            if resultado is None:
                                print('ERRO: PRODUTO NÃO ENCONTRADO!')
                                return
                            produto = resultado[0]
                            unidades = resultado[1]
                            print(f'Produto selecionado >>{produto}<<')
                            q = int(input('Quantas unidades foram vendidas? '))
                            if q>unidades:
                                print('VOCÊ NÃO PODE REALIZAR ESTPÁ VENDA! ')
                                print('MOTIVO: ESTOQUE INSUFICIENTE')
                                return
                            invest = float(input('insira o valor da venda: '))
                            data = dt.date.today().strftime("%d/%m/%Y")
                            hora = dt.datetime.now().time().strftime("%H:%M")
                            m.registroMov(produto, idProduto, op, tip, stip, q, data, hora, cursor, conexao, invest)
                            return
                        case 2:
                            stip = 'PERCA'
                            idProduto = int(input('Insira o ID do produto: '))
                            cursor.execute("""
                            SELECT nome FROM produtos
                            WHERE id = ?                  
                            """, (idProduto,))
                            resultado = cursor.fetchone()
                            if resultado is None:
                                print('ERRO: PRODUTO NÃO ENCONTRADO!')
                                return
                            produto = resultado[0]
                            print(f'Produto selecionado >>{produto}<<')
                            q = int(input('Quantas unidades foram perdidas? '))
                            data = dt.date.today().strftime("%d/%m/%Y")
                            hora = dt.datetime.now().time().strftime("%H:%M")
                            m.registroMov(produto, idProduto, op, tip, stip, q, data, hora, cursor, conexao)
                           
                        case 3:
                            stip = 'TRANSFERÊNCIA'
                            idProduto = int(input('Insira o ID do produto: '))
                            cursor.execute("""
                            SELECT nome, quantidade FROM produtos
                            WHERE id = ?                   
                            """, (idProduto,))
                            resultado = cursor.fetchone()
                            if resultado is None:
                                print('ERRO: PRODUTO NÃO ENCONTRADO!')
                                return
                            produto = resultado[0]
                            unidades = resultado[1]
                            print(f'Produto selecionado >>{produto}<<')
                            q = int(input('Quantas unidades foram transferidas? '))
                            if q>unidades:
                                print('VOCÊ NÃO PODE REALIZAR ESTÁ MOVIMENTAÇÃO! ')
                                print('MOTIVO: ESTOQUE INSUFICIENTE')
                                return
                            invest = float(input('Quanto custou o transporte? '))
                            if invest>saldo:
                                print('VOCÊ NÃO PODE REALIZAR ESTÁ TRANSFERÊNCIA! ')
                                print('MOTIVO: SALDO INSUFICIENTE')
                                return
                            data = dt.date.today().strftime("%d/%m/%Y")
                            hora = dt.datetime.now().time().strftime("%H:%M")
                            m.registroMov(produto, idProduto, op, tip, stip, q, data, hora, cursor, conexao)
                            return
                        case _:
                            print('INSIRA SOMENTE NÚMEROS DE 1 A 3 ')
                case _:
                    print('INSIRA SOMENTE NÚMEROS DE 1 A 2 ')
        except ValueError:
            print('INSIRA APENAS NÚMEROS')
        
def telaRelatorio(conexao):
    while True:
        try:
            print('[1] PRODUTOS')
            print('[2] MOVIMENTAÇÃO')
            rel = int(input('Qual relatório deseja gerar? '))
            match rel:
                case 1:
                    df = r.lerDados(rel, conexao)
                    if df.empty:
                        print('NÃO HÁ PRODUTOS CADASTRADOS')
                        return
                    else:
                        r.geralRel(df)
                        print('RELATÓRIO EXPORTADO COM SUCESSO!')
                        return
                case 2:
                    print('FILTRAR POR:')
                    print('[1] ÚLTIMA SEMANA')
                    print('[2] ÚLTIMO MÊS')
                    print('[3] INTERVALO DE DATAS')
                    rel2 = int(input('Escolha uma opção: '))
                    match rel2:
                        case 1:
                            df = r.lerDados(rel, conexao, rel2)
                            if df.empty:
                                print('NÃO HÁ PRODUTOS CADASTRADOS')
                                return
                            else:
                                r.geralRel(df)
                                print('RELATÓRIO EXPORTADO COM SUCESSO!')
                                return
                        case 2:
                            df = r.lerDados(rel, conexao, rel2)
                            if df.empty:
                                print('NÃO HÁ PRODUTOS CADASTRADOS')
                                return
                            else:
                                r.geralRel(df)
                                print('RELATÓRIO EXPORTADO COM SUCESSO!')
                                return
                        case 3:
                            try:
                                dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                                verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
                                dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                                verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
                                df = r.lerDados(rel, conexao, rel2, dataInicial, dataUltima )
                                if df.empty:
                                    print('NÃO HÁ PRODUTOS CADASTRADOS')
                                    return
                                else:
                                    r.geralRel(df)
                                    print('RELATÓRIO EXPORTADO COM SUCESSO!')
                                    return
                            except ValueError:
                                print('ERRO! AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!')
                        case _:
                            print('ERRO! INSIRA APENAS NÚMEROS DE 1 A 3!')
                case _:
                    print('ERRO! INSIRA APENAS NÚMEROS DE 1 A 3!')
        except ValueError:
            print('ERRO! INSIRA APENAS NÚMEROS DE 1 A 3!')