def cadastro(cursor, conexao):
    n = input('Insira o nome do produto ')
    q = int(input('Insira a disponibilidade no estoque '))
    invest = float(input('Qual o valor do investimento'))

    cursor.execute("""
    SELECT valor FROM saldo
    where id = 1
    """)
    saldo = cursor.fetchone()[0]
    if invest>saldo:
        print('Você não pode cadastrar este produto pois o saldo não é suficiente ')
        return

    v = float(input('Por quanto o produto será vendido'))
    esp2 = ''
    esp = input('Possui alguma especificação? ')
    if esp.lower() == 's' or esp.lower() == 'sim':
        esp2 = input('Qual a especificação')

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
            op = int(input('Qual a movimentação realizada '))
            match op:
                case 1:
                    tip = 'ENTRADA'
                    print('[1] COMPRA')
                    print('[2] DEVOLUÇÃO')
                    tipo = int(input('Qual o tipo de entrada? '))
                    match tipo:
                        case 1:
                            stip = 'COMPRA'
                            idProduto = int(input('Qual o id do produto '))
                            cursor.execute("""
                            SELECT nome FROM produtos
                            WHERE id = ?                  
                            """, (idProduto,))
                            resultado = cursor.fetchone()
                            if resultado is None:
                                print('Produto não encontrado ')
                                return
                            produto = resultado[0]
                            q = int(input('Quantas unidades foram recebidas'))
                            invest = float(input('Qual o valor do investimento? '))
                            if invest>saldo:
                                print('Você não pode realizar esta movimentação pois o saldo não é suficiente ')
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
                            idProduto = int(input('Qual o id do produto '))
                            cursor.execute("""
                            SELECT nome FROM produtos
                            WHERE id = ?                  
                            """, (idProduto,))
                            resultado = cursor.fetchone()
                            if resultado is None:
                                print('Produto não encontrado ')
                                return
                            produto = resultado[0]
                            q = int(input('Quantas unidades foram devolvidas'))
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
                            idProduto = int(input('Qual o id do produto '))
                            cursor.execute("""
                            SELECT nome, quantidade FROM produtos
                            WHERE id = ?                   
                            """, (idProduto,))
                            resultado = cursor.fetchone()
                            if resultado is None:
                                print('Produto não encontrado ')
                                return
                            produto = resultado[0]
                            unidades = resultado[1]
                            q = int(input('Quantas unidades foram vendidas'))
                            if q>unidades:
                                print('Você não pode realizar está venda pois o estoque é insuficiente ')
                                return
                            invest = float(input('Qual o valor da venda? '))
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
                            idProduto = int(input('Qual o id do produto '))
                            cursor.execute("""
                            SELECT nome FROM produtos
                            WHERE id = ?                  
                            """, (idProduto,))
                            resultado = cursor.fetchone()
                            if resultado is None:
                                print('Produto não encontrado ')
                                return
                            produto = resultado[0]
                            q = int(input('Quantas unidades foram perdidas'))
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
                            idProduto = int(input('Qual o id do produto '))
                            cursor.execute("""
                            SELECT nome, quantidade FROM produtos
                            WHERE id = ?                   
                            """, (idProduto,))
                            resultado = cursor.fetchone()
                            if resultado is None:
                                print('Produto não encontrado ')
                                return
                            produto = resultado[0]
                            unidades = resultado[1]
                            q = int(input('Quantas unidades foram transferidas'))
                            if q>unidades:
                                print('Você não pode realizar está transgferência pois o estoque é insuficiente ')
                                return
                            invest = float(input('Quanto custou o transporte? '))
                            if invest>saldo:
                                print('Você não pode realizar esta transferência pois o saldo não é suficiente ')
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
    cursor.execute("""
    SELECT * FROM produtos                   
    """)
    

    produtos = cursor.fetchall()
    for produto in produtos:
        print(f"=========={produto[1]}===========")
        print(f"ID DO PRODUTO: [{produto[0]}]")
        print(f"DISPONIBILIDADE NO ESTOQUE: {produto[2]}")
        print(f"PREÇO: R$ {produto[3]}")
        if produto[4] != '':
            print(f"ESPECIFICAÇÃO: {produto[4]}")

def listarHistorico(cursor, conexao):
    cursor.execute("""
    SELECT * FROM  historico                  
    """)
    historico = cursor.fetchall()
    for mov in historico:
        print(f"=========={mov[1]}===========")
        print(f"TIPO DE MOVIMENTAÇÃO {mov[2]}")
        if mov[3] == 'COMPRA' or mov[3] == 'DEVOLUÇÃO':
            print(f"UNIDADES RECEBIDAS: {mov[4]}")
        else:
            print(f"UNIDADES DESFAZIDAS: {mov[4]}")

def editarSaldo(cursor, conexao):
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

