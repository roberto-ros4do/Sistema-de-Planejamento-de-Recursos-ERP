def cadastro(cursor, conexao):
        import datetime as dt
        while True:
            try:
                n = input('Insira o nome do produto: ')
                q = int(input('Insira a disponibilidade no estoque: '))
                invest = float(input('Insira o valor do investimento? '))

                cursor.execute("""
                SELECT valor FROM saldo
                where id = 1
                """)
                saldo = cursor.fetchone()[0]
                if invest>saldo:
                    print('ERRO! SALDO INSUFICIENTE ')
                    return
                v = float(input('Insira o valor que será cobrado pelo produto: '))
                esp2 = ''
                esp = input('Possui alguma especificação[S/N]? ')
                if esp.lower() == 's' or esp.lower() == 'sim':
                    esp2 = input('Insira a especificação: ')
                data = dt.date.today().strftime("%m/%d/%Y")
                hora = dt.datetime.now().time().strftime("%H:%M")
                cursor.execute("""
                INSERT INTO produtos (nome, quantidade, preco, especificacao, dataCad, horaCad)
                VALUES (?, ?, ?, ?)
                """, (n, q, v, esp2, data, hora))
                cursor.execute("""
                UPDATE SALDO
                SET valor = valor - ?
                WHERE id = 1          
                """, (invest,))
                conexao.commit()
            except ValueError:
                print('ERRO! INSIRA APENAS NÚMEROS')

def movimentacao(cursor, conexao):
    import datetime as dt
    cursor.execute("""
    SELECT valor FROM saldo
    where id = 1
    """)
    saldo = cursor.fetchone()[0]
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
                            cursor.execute("""
                            SELECT nome FROM produtos
                            WHERE id = ?                  
                            """, (idProduto,))
                            resultado = cursor.fetchone()
                            if resultado is None:
                                print('ERRO: PRODUTO NÃO ENCONTRADO!')
                                return
                            produto = resultado[0]
                            data = dt.date.today().strftime("%d/%m/%Y")
                            hora = dt.datetime.now().time().strftime("%H:%M")
                            print(f'Produto selecionado >>{produto}<<')
                            q = int(input('Quantas unidades foram recebidas? '))
                            invest = float(input('Insira o valor do investimento: '))
                            if invest>saldo:
                                print('VOCÊ NÃO PODE REALIZAR ESTÁ COMPRA! ')
                                print('MOTIVO: SALDO INSUFICIENTE')
                                return
                            cursor.execute("""
                            INSERT INTO historicoMovimentacao (produto, tipo, stipo, quantidade, data, hora)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """, (produto, tip, stip, q, data, hora))
                            cursor.execute("""
                            UPDATE SALDO
                            SET valor = valor - ?
                            WHERE id = 1  
                            """, (invest,))
                            cursor.execute("""
                            UPDATE produtos
                            SET quantidade = quantidade + ?
                            WHERE id = ?  
                            """, (q, idProduto))
                            conexao.commit()
                            return
                        case 2:
                            stip = 'DEVOLUÇÃO'
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
                            q = int(input('Quantas unidades foram devolvidas? '))
                            invest = float(input('Qual o valor do reembolso? '))
                            data = dt.date.today().strftime("%d/%m/%Y")
                            hora = dt.datetime.now().time().strftime("%H:%M")
                            cursor.execute("""
                            INSERT INTO historicoMovimentacao (produto, tipo, stipo, quantidade, data, hora)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """, (produto, tip, stip, q, data, hora))
                            cursor.execute("""
                            UPDATE SALDO
                            SET valor = valor - ?
                            WHERE id = 1  
                            """, (invest,))
                            cursor.execute("""
                            UPDATE produtos
                            SET quantidade = quantidade + ?
                            WHERE id = ?   
                            """, (q, idProduto))
                            conexao.commit()
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
                            q = int(input('Quantas unidades foram vendidas? '))
                            if q>unidades:
                                print('VOCÊ NÃO PODE REALIZAR ESTPÁ VENDA! ')
                                print('MOTIVO: ESTOQUE INSUFICIENTE')
                                return
                            invest = float(input('insira o valor da venda: '))
                            data = dt.date.today().strftime("%d/%m/%Y")
                            hora = dt.datetime.now().time().strftime("%H:%M")
                            cursor.execute("""
                            INSERT INTO historicoMovimentacao (produto, tipo, stipo, quantidade, data, hora)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """, (produto, tip, stip, q, data, hora))
                            cursor.execute("""
                            UPDATE SALDO
                            SET valor = valor + ?
                            WHERE id = 1  
                            """, (invest,))
                            cursor.execute("""
                            UPDATE produtos
                            SET quantidade = quantidade - ?
                            WHERE id = ?           
                            """, (q, idProduto))
                            conexao.commit()
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
                            cursor.execute("""
                            INSERT INTO historicoMovimentacao (produto, tipo, stipo, quantidade, data, hora)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """, (produto, tip, stip, q, data, hora))
                            cursor.execute("""
                            UPDATE produtos
                            SET quantidade = quantidade - ?
                            WHERE id = ?   
                            """, (q, idProduto))
                            conexao.commit()
                            return
                           
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
                            cursor.execute("""
                            INSERT INTO historicoMovimentacao (produto, tipo, stipo, quantidade, data, hora)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """, (produto, tip, stip, q, data, hora))
                            cursor.execute("""
                            UPDATE SALDO
                            SET valor = valor - ?
                            WHERE id = 1  
                            """, (invest,))
                            cursor.execute("""
                            UPDATE produtos
                            SET quantidade = quantidade - ?
                            WHERE id = ?   
                            """, (q, idProduto))
                            conexao.commit()
                            return
                        case _:
                            print('INSIRA SOMENTE NÚMEROS DE 1 A 3 ')
                case _:
                    print('INSIRA SOMENTE NÚMEROS DE 1 A 2 ')
        except ValueError:
            print('INSIRA APENAS NÚMEROS')

def listarProdutos(cursor, conexao):
    while True:
        try:
            cursor.execute("""
                SELECT * FROM produtos                   
                """)
            produtos = cursor.fetchall()
            if not produtos:
                print('AINDA NÃO HÁ PRODUTOS CADASTRADOS!')
                return
            else:
                filtro = input('Deseja utilizar filtro? ')
                if filtro.lower() in ('s', 'sim'):
                    query = "SELECT * FROM produtos WHERE 1=1"
                    parametros = []
                    n = input('Insira o nome(ENTER para pular): ')
                    valorMin = input('Insira o valor mínimo(ENTER para pular): ')
                    if valorMin!='':
                        valorMin = float(valorMin)
                        if valorMin<=0:
                            print('INSIRA VALORES ACIMA DE 0 REAIS!')
                    valorMax = input('Insira o valor máximo(ENTER para pular): ')
                    if valorMax!='':
                        valorMax = float(valorMax)
                        if valorMax<=0:
                            print('INSIRA VALORES ACIMA DE 0 REAIS!')
                    estoqMin = input('Insira a disponibilidade mínima(ENTER para pular): ')
                    if estoqMin!='':
                        estoqMin = int(estoqMin)
                        if estoqMin<0:
                            print('INSIRA APENAS NÚMEROS POSITIVOS')
                    estoqMax = input('Insira a disponibilidade máxima(ENTER para pular): ')
                    if estoqMax!='':
                        estoqMax=int(estoqMax)
                        if estoqMax<0:
                            print('INSIRA APENAS NÚMEROS POSITIVOS')
                    if n!='':
                        query += " AND LOWER(nome) LIKE LOWER(?)"
                        parametros.append(f'%{n}%')
                    if valorMin!='' and valorMax!='':
                        if valorMin > valorMax:
                            valorMin, valorMax = valorMax, valorMin
                    if estoqMin!='' and estoqMax!='':
                        if estoqMin>estoqMax:
                            estoqMin, estoqMax = estoqMax, estoqMin
                    if valorMin!='':
                        query += " AND preco >= ?"
                        parametros.append(valorMin)
                    if valorMax!='':
                        query += " AND preco <= ?"
                        parametros.append(valorMax)
                    if estoqMin!='':
                        query += " AND quantidade >= ?"
                        parametros.append(estoqMin)
                    if estoqMax!='':
                        query += " AND quantidade <= ? "
                        parametros.append(estoqMax)
                    cursor.execute(query, parametros)
                    produtos = cursor.fetchall()
                    if not produtos:
                        print('NÃO HÁ PRODUTOS COM ESTAS ESPECIFICAÇÕES')
                    else:
                        for produto in produtos:
                            print(f"=========={produto[1]}===========")
                            print(f"ID DO PRODUTO: [{produto[0]}]")
                            print(f"DISPONIBILIDADE NO ESTOQUE: {produto[2]}")
                            print(f"PREÇO: R$ {produto[3]}")
                            if produto[4] != '':
                                print(f"ESPECIFICAÇÃO: {produto[4]}")
                else:
                    for produto in produtos:
                        print(f"=========={produto[1]}===========")
                        print(f"ID DO PRODUTO: [{produto[0]}]")
                        print(f"DISPONIBILIDADE NO ESTOQUE: {produto[2]}")
                        print(f"PREÇO: R$ {produto[3]}")
                        if produto[4] != '':
                            print(f"ESPECIFICAÇÃO: {produto[4]}")
        except ValueError:
                  print('ERRO! INSIRA APENAS NÚMEROS NOS FILTROS DE PREÇO E ESTOQUE')    

def historicoMovimentacao(cursor, conexao):
    import datetime as dt
    from calendar import monthrange
    while True:
        try:
            cursor.execute("""
            SELECT * FROM  historico                  
            """) 
            historico = cursor.fetchall()
            if not historico:
                print('AINDA NÃO FORAM REGISTRADAS MOVIMENTAÇÕES! ')
            filtro = input('Deseja utilizar filtro?')
            if filtro.lower in ('s', 'sim'):
                print('[1] ÚLTIMA SEMANA')
                print('[2] MÊS PASSADO')
                print('[3] INTERVALO DE DATAS')
                escolha = int(input('Qual opção escolhida? '))
                match escolha:
                    case 1:
                        hoje = dt.date.today().strftime("%d/%m/%Y")
                        us = int(hoje[1]) - 7 
                        if us <= 0:
                            mes = int(hoje[3]) - 1
                            ano = int(hoje[5])
                            diasMes = monthrange(ano, mes)[1]
                            dia= diasMes + us
                            dataUltima = dt.date(ano, mes, dia).strftime("%d/%m/%Y")
                        else:
                            mes = int(hoje[3])
                            ano = int(hoje[5])
                            dataUltima = dt.date(ano, mes, us).strftime("%d/%m/%Y")
                        cursor.execute("""
                        SELECT * FROM historicoMovimentacao
                        WHERE data BETWEEN ? AND ?
                        """, (dataUltima, hoje))
                        historico = cursor.fecthall()
                        if not historico:
                            print('NÃO HÁ MOVIMENTAÇÕES NESSA FAIXA DE TEMPO!')
                            return
                        else:   
                            for mov in historico:
                                print(f"=========={mov[1]}===========")
                                print(f'REALIZADA EM {5} AS {6}')
                                print(f"TIPO DE MOVIMENTAÇÃO {mov[2]}")
                                if mov[3] == 'COMPRA' or mov[3] == 'DEVOLUÇÃO':
                                    print(f"UNIDADES RECEBIDAS: {mov[4]}")
                                else:
                                    print(f"UNIDADES DESFAZIDAS: {mov[4]}")
                            return
                    case 2:
                        hoje = dt.date.today().strftime("%d/%m/%Y")
                        mes = int(hoje[3]) - 1
                        dia = int(hoje[1])
                        if mes <= 0:
                            ano = int(hoje[5]) - 1
                            mes = 12 + mes
                            dataUltima = dt.date(ano, mes, dia).strftime("%d/%m/%Y")
                        else:
                            ano = int(hoje[5])
                            dataUltima = dt.date(ano, mes, dia).strftime("%d/%m/%Y")
                        cursor.execute("""
                        SELECT * FROM historicoMovimentacao
                        WHERE data BETWEEN ? AND ?
                        """, (dataUltima, hoje))
                        historico = cursor.fecthall()
                        if not historico:
                            print('NÃO HÁ MOVIMENTAÇÕES NESSA FAIXA DE TEMPO!')
                            return
                        else:   
                            for mov in historico:
                                print(f"=========={mov[1]}===========")
                                print(f'REALIZADA EM {5} AS {6}')
                                print(f"TIPO DE MOVIMENTAÇÃO {mov[2]}")
                                if mov[3] == 'COMPRA' or mov[3] == 'DEVOLUÇÃO':
                                    print(f"UNIDADES RECEBIDAS: {mov[4]}")
                                else:
                                    print(f"UNIDADES DESFAZIDAS: {mov[4]}")
                            return
                    case 3:
                        dataInicial = input('Insira a data mais antiga(NO FORMATO DD/MM/AA): ')
                        verificData = dt.datetime.strptime(dataInicial, "%d/%m/%Y")
                        dataUltima = input('Insira a data mais recente(NO FORMATO DD/MM/AA): ')
                        verificData = dt.datetime.strptime(dataUltima, "%d/%m/%Y")
                        cursor.execute("""
                        SELECT * FROM historicoMovimentacao
                        WHERE data BETWEEN ? AND ?
                        """, (dataInicial, dataUltima))
                        historico = cursor.fecthall()
                        if not historico:
                            print('NÃO HÁ MOVIMENTAÇÕES NESSA FAIXA DE TEMPO!')
                            return
                        else:
                            for mov in historico:
                                print(f"=========={mov[1]}===========")
                                print(f'REALIZADA EM {5} AS {6}')
                                print(f"TIPO DE MOVIMENTAÇÃO {mov[2]}")
                                if mov[3] == 'COMPRA' or mov[3] == 'DEVOLUÇÃO':
                                    print(f"UNIDADES RECEBIDAS: {mov[4]}")
                                else:
                                    print(f"UNIDADES DESFAZIDAS: {mov[4]}")
                            return
                    case _:
                        print('ERRO! INSIRA APENAS NÚMEROS DE 1 A 3')
            else:
                for mov in historico:
                    print(f"=========={mov[1]}===========")
                    print(f'REALIZADA EM {5} AS {6}')
                    print(f"TIPO DE MOVIMENTAÇÃO {mov[2]}")
                    if mov[3] == 'COMPRA' or mov[3] == 'DEVOLUÇÃO':
                        print(f"UNIDADES RECEBIDAS: {mov[4]}")
                    else:
                        print(f"UNIDADES DESFAZIDAS: {mov[4]}")
                return
        except ValueError:
            print('ERRO! AS DATAS INSERIDAS NÃO ESTÃO NO FORMATO ESPERADO!')

def editarSaldo(cursor, conexao):
    cursor.execute("""
    SELECT valor
    FROM SALDO
    WHERE id = 1
    """)
    saldo = cursor.fetchone()[0]
    print('[1] APLICAÇÃO ')
    print('[2] RETIRADA')
    while True:
        try:
            op = int(input('Qual operação deseja realizar? '))
            match op:
                case 1:
                    ap = float(input('Quanto deseja adicionar '))
                    cursor.execute("""
                    UPDATE SALDO
                     SET valor = valor + ?
                    WHERE id = 1           
                     """, (ap,))
                    conexao.commit()
                    break
                case 2:
                    ret = float(input('Quanto deseja retirar '))
                    if saldo<ret:
                        print('VOCÊ NÃO PODE REALIZAR ESTÁ RETIRADA!')
                        print('MOTIVO: SALDO INSUFICIENTE')
                        return
                    cursor.execute("""
                    UPDATE SALDO
                     SET valor = valor - ?
                    WHERE id = 1   
                    """, (ret,))
                    conexao.commit()
                    break
                case _:
                    print('INSIRA APENAS NÚMEROS DE 1 A 2 ')
        except ValueError:
            print('INSIRA APENAS NÚMEROS')

def deletar(cursor, conexao):
    try:
        idProd = int(input('Insira o ID do produto que deseja deletar: '))
        cursor.execute("""
        SELECT nome FROM produtos
        WHERE id = ?                  
        """, (idProd,))
        resultado = cursor.fetchone()
        if resultado is None:
            print('ERRO: PRODUTO NÃO ENCONTRADO!')
            return
        produto = resultado[0]
        cursor.execute("""
        DELETE FROM produtos
        WHERE id = ?
        """, (idProd,))
        print(f'[{produto}] DELETADO')
    except ValueError:
        print('INSIRA APENAS NÚMEROS')

def historicoCadastro(cursor, conexao):
    cursor.execute("""
    SELECT * FROM  produtos                  
    """) 
    historico = cursor.fetchall()
    if not historico:
        print('AINDA NÃO HÁ PRODUTOS REGISTRADOS! ')
        return
    for mov in historico:
        print(f"=========={mov[1]}===========")
        print(f"ID DO PRODUTO: [{mov[0]}]")
        print(f'CADASTRADO EM {mov[5]} AS {mov[6]}')