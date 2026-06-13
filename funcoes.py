def cadastro(cursor, conexao):
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
            print('Você não pode cadastrar este produto pois o saldo não é suficiente ')
            return
        v = float(input('Insira o valor que será cobrado pelo produto: '))
        esp2 = ''
        esp = input('Possui alguma especificação[S/N]? ')
        if esp.lower() == 's' or esp.lower() == 'sim':
            esp2 = input('Insira a especificação: ')

        cursor.execute("""
        INSERT INTO produtos (nome, quantidade, preco, especificacao)
        VALUES (?, ?, ?, ?)
        """, (n, q, v, esp2))

        cursor.execute("""
        UPDATE SALDO
        SET valor = valor - ?
        WHERE id = 1          
        """, (invest,))
        conexao.commit()
    except ValueError:
        print('ERRO! INSIRA APENAS NÚMEROS')

def movimentacao(cursor, conexao):
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
                            print(f'Produto selecionado >>{produto}<<')
                            q = int(input('Quantas unidades foram recebidas? '))
                            invest = float(input('Insira o valor do investimento: '))
                            if invest>saldo:
                                print('VOCÊ NÃO PODE REALIZAR ESTÁ COMPRA! ')
                                print('MOTIVO: SALDO INSUFICIENTE')
                                return
                            cursor.execute("""
                            INSERT INTO historico (produto, tipo, stipo, quantidade)
                            VALUES (?, ?, ?, ?)
                            """, (produto, tip, stip, q))
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
                            cursor.execute("""
                            INSERT INTO historico (produto, tipo, stipo, quantidade)
                            VALUES (?, ?, ?, ?)
                            """, (produto, tip, stip, q))
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
                            cursor.execute("""
                            INSERT INTO historico (produto, tipo, stipo, quantidade)
                            VALUES (?, ?, ?, ?)
                            """, (produto, tip, stip, q))
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
                            cursor.execute("""
                            INSERT INTO historico (produto, tipo, stipo, quantidade)
                            VALUES (?, ?, ?, ?)
                            """, (produto, tip, stip, q))
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
                            cursor.execute("""
                            INSERT INTO historico (produto, tipo, stipo, quantidade)
                            VALUES (?, ?, ?, ?)
                            """, (produto, tip, stip, q))
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

def listarHistorico(cursor, conexao):
    cursor.execute("""
    SELECT * FROM  historico                  
    """) 
    historico = cursor.fetchall()
    if not historico:
        print('AINDA NÃO FORAM REGISTRADAS MOVIMENTAÇÕES! ')
    for mov in historico:
        print(f"=========={mov[1]}===========")
        print(f"TIPO DE MOVIMENTAÇÃO {mov[2]}")
        if mov[3] == 'COMPRA' or mov[3] == 'DEVOLUÇÃO':
            print(f"UNIDADES RECEBIDAS: {mov[4]}")
        else:
            print(f"UNIDADES DESFAZIDAS: {mov[4]}")

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