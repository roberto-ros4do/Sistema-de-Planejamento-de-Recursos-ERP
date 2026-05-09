def cadastro(produtos, saldo):
    produto = input('Adicione o produto ')
    produtos.append({'nome': produto, 'valor': 0.0, 'estoque': 0, 'especificacao': '', 'id': 0})
    numero = len(produtos)-1
    while True:
        try:
            produtos[numero]['id'] = numero
            valor = float(input('Por quanto o produto será vendido '))
            produtos[numero]['valor'] = valor
            esp = input('Possui alguma especificação? ')
            if esp.lower() == 's' or esp.lower() == 'sim':
                esp2 = input("Qual a especificação? ")
                produtos[numero]['especificacao'] = esp2
            estoq = int(input('Qual a disponibilidade no estoque '))
            produtos[numero]['estoque'] = estoq
            invest = float(input('Quanto custou o investimento '))
            saldo -= invest
            print('Cadastrado com sucesso! ')
            print(f"=========={produtos[numero]['nome']}===========")
            print(f"ID DO PRODUTO: [{produtos[numero]['id']}]")
            print(f"DISPONIBILIDADE NO ESTOQUE: {produtos[numero]['estoque']}")
            print(f"PREÇO: R$ {produtos[numero]['valor']}")
            return saldo
            break
        except ValueError:
            print('INSIRA APENAS NÚMEROS')


def movimentacao(historico,produtos, saldo):
    while True:
        try:
            print('[1] ENTRADA ')
            print('[2] SAÍDA ')
            op = int(input('Qual a movimentação realizada '))
            match op:
                case 1:
                    print('[1] COMPRA')
                    print('[2] DEVOLUÇÃO')
                    tipo = int(input('Qual o tipo de entrada? '))
                    match tipo:
                        case 1:
                            tip = 'COMPRA'
                            historico.append({'movimentacao': tip, 'produto': '', 'unidades': 0})
                            numero = len(historico)-1
                            id = int(input('Qual o ID do produto recebido '))
                            unid = int(input('Quantas unidades foram recebidas'))
                            historico[numero]['unidades'] = unid
                            invest = float(input('Qual o valor do investimento? '))
                            for produto in produtos:
                                if produto['id'] == id:
                                    prod = produto['nome']
                                    historico[numero]['produto'] = prod
                                    produto['estoque'] += unid
                            saldo -= invest
                            return saldo
                        case 2:
                            tip = 'DEVOLUÇÃO'
                            historico.append({'movimentacao': tip, 'produto': '', 'unidades': 0})
                            numero = len(historico)-1
                            id = int(input('Qual o ID do produto devolvido '))
                            unid = int(input('Quantas unidades foram devolvidas'))
                            historico[numero]['unidades'] = unid
                            remb = float(input('Qual o valor do reembolso? '))
                            for produto in produtos:
                                if produto['id'] == id:
                                    prod = produto['nome']
                                    historico[numero]['produto'] = prod
                                    produto['estoque'] += unid
                            saldo -= remb
                            return saldo
                        case _:
                            print('INSIRA APENAS NÚMEROS DE 1 A 2 ')
                case 2:
                    print('[1] VENDA')
                    print('[2] PERCA')
                    print('[3] TRANSFERÊNCIA')
                    tipo = int(input('Qual o tipo de saida? '))
                    match tipo:
                        case 1:
                            tip = 'VENDA'
                            historico.append({'movimentacao': tip, 'produto': '', 'unidades': 0})
                            numero = len(historico)-1
                            id = int(input('Qual o ID do produto vendido '))
                            unid = int(input('Quantas unidades foram vendidas '))
                            historico[numero]['unidades'] = unid
                            venda = float(input('Qual o valor da venda? '))
                            for produto in produtos:
                                if produto['id'] == id:
                                    prod = produto['nome']
                                    historico[numero]['produto'] = prod
                                    produto['estoque'] -= unid
                            saldo += venda
                            return saldo
                        
                        case 2:
                            tip = 'PERCA'
                            historico.append({'movimentacao': tip, 'produto': '', 'unidades': 0})
                            numero = len(historico)-1
                            id = int(input('Qual o ID do produto perdido '))
                            unid = int(input('Quantas unidades foram perdidas'))
                            historico[numero]['unidades'] = unid
                            for produto in produtos:
                                if produto['id'] == id:
                                    prod = produto['nome']
                                    historico[numero]['produto'] = prod
                                    produto['estoque'] -= unid
                            break
                        case 3:
                            tip = 'TRANSFERÊNCIA'
                            historico.append({'movimentacao': tip, 'produto': '', 'unidades': 0})
                            numero = len(historico)-1
                            id = int(input('Qual o ID do produto transferido '))
                            unid = int(input('Quantas unidades foram transferidas'))
                            historico[numero]['unidades'] = unid
                            custo = input('Houve custo de trsnaferencia? ')
                            if custo.lower() == 's' or custo.lower() == 'sim':
                                custo2 = float(input('Quanto custou o transporte? '))
                                saldo -= custo2 
                            for produto in produtos:
                                if produto['id'] == id:
                                    prod = produto['nome']
                                    historico[numero]['produto'] = prod
                                    produto['estoque'] -= unid
                            return saldo
                        case _:
                            print('INSIRA SOMENTE NÚMEROS DE 1 A 3 ')
                case _:
                    print('INSIRA SOMENTE NÚMEROS DE 1 A 2 ')
        except ValueError:
            print('INSIRA APENAS NÚMEROS')

def listarProdutos(produtos):
    for produto in produtos:
        print(f"=========={produto['nome']}===========")
        print(f"ID DO PRODUTO: [{produto['id']}]")
        print(f"DISPONIBILIDADE NO ESTOQUE: {produto['estoque']}")
        print(f"PREÇO: R$ {produto['valor']}")
        if produto['especificacao'] != '':
            print(f"ESPECIFICAÇÃO: {produto['especificacao']}")

def listarHistorico(historico):
    for mov in historico:
        print(f"=========={mov['produto']}===========")
        print(f"TIPO DE MOVIMENTAÇÃO {mov['movimentacao']}")
        if mov['movimentacao'] == 'COMPRA' or mov['movimentacao'] == 'DEVOLUÇÃO':
            print(f"UNIDADES RECEBIDAS: {mov['unidades']}")
        else:
            print(f"UNIDADES DESFAZIDAS: {mov['unidades']}")

def editarSaldo(saldo):
    print('[1] APLICAÇÃO ')
    print('[2] RETIRADA')
    while True:
        try:
            op = int(input('Qual operação deseja realizar? '))
            match op:
                case 1:
                    ap = float(input('Quanto deseja adicionar '))
                    saldo += ap
                    return saldo
                    break
                case 2:
                    ret = float(input('Quanto deseja retirar '))
                    saldo -= ret
                    return saldo
                    break
                case _:
                    print('INSIRA APENAS NÚMEROS DE 1 A 2 ')
        except ValueError:
            print('INSIRA APENAS NÚMEROS')

