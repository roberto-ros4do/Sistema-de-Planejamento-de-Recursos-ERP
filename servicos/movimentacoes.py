def consultaMov(cursor):
    cursor.execute("""
        SELECT * FROM  historicoMovimentacao                  
        """) 
    historico = cursor.fetchall()
    return historico

def registroMov(produto, idProduto, tip, q, cursor, conexao, nome, invest=0):
    import datetime as dt
    data = dt.date.today().strftime("%Y/%m/%d")
    hora = dt.datetime.now().time().strftime("%H:%M")
    try:
        if tip=='COMPRA':
            op = 'SAÍDA'
            if invest=='':
                invest=0
            cursor.execute("""
            INSERT INTO historicoMovimentacao (produto, idProduto, tipo, quantidade, data, hora, quemFez, valorEnvolvido)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (produto, idProduto, tip, q, data, hora, nome, invest))
            if invest!=0:
                cursor.execute("""
                UPDATE saldo
                SET valor = valor - ?
                WHERE id = 1  
                """, (invest,))
                cursor.execute("""
                INSERT INTO histSaldo (valor, operacao, quemFez, data, hora)
                VALUES (?, ?, ?, ?, ?)
                """, (invest, op, nome, data, hora))
            cursor.execute("""
            UPDATE produtos
            SET quantidade = quantidade + ?
            WHERE id = ?  
            """, (q, idProduto))
            conexao.commit()
        if tip=='DEVOLUÇÃO':
            op = 'SAÍDA'
            if invest=="":
                invest=0
            cursor.execute("""
            INSERT INTO historicoMovimentacao (produto, idProduto, tipo, quantidade, data, hora, quemFez, valorEnvolvido)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (produto, idProduto, tip, q, data, hora, nome, invest))
            if invest!=0:
                cursor.execute("""
                UPDATE saldo
                SET valor = valor - ?
                WHERE id = 1  
                """, (invest,))
                cursor.execute("""
                INSERT INTO histSaldo (valor, operacao, quemFez, data, hora)
                VALUES (?, ?, ?, ?, ?)
                """, (invest, op, nome, data, hora))
            cursor.execute("""
            UPDATE produtos
            SET quantidade = quantidade + ?
            WHERE id = ?   
            """, (q, idProduto))
            conexao.commit()
        if tip=='VENDA':
            op='ENTRADA'
            cursor.execute("""
            INSERT INTO historicoMovimentacao (produto, idProduto, tipo, quantidade, data, hora, quemFez, valorEnvolvido)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (produto, idProduto, tip, q, data, hora, nome, invest))
            if invest!=0:
                cursor.execute("""
                UPDATE saldo
                SET valor = valor + ?
                WHERE id = 1  
                """, (invest,))
                cursor.execute("""
                INSERT INTO histSaldo (valor, operacao, quemFez, data, hora)
                VALUES (?, ?, ?, ?, ?)
                """, (invest, op, nome, data, hora))
            cursor.execute("""
            UPDATE produtos
            SET quantidade = quantidade - ?
            WHERE id = ?           
            """, (q, idProduto))
            conexao.commit()
            return
        if tip=='PERCA':
            cursor.execute("""
            INSERT INTO historicoMovimentacao (produto, idProduto, tipo, quantidade, data, hora, quemFez)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (produto, idProduto, tip, q, data, hora, nome))
            cursor.execute("""
            UPDATE produtos
            SET quantidade = quantidade - ?
            WHERE id = ?   
            """, (q, idProduto))
            conexao.commit()
            return
        if tip=='TRANSFERÊNCIA':
            op='SAÍDA'
            cursor.execute("""
            INSERT INTO historicoMovimentacao (produto, idProduto, tipo, quantidade, data, hora, quemFez, valorEnvolvido)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (produto, idProduto, tip, q, data, hora, nome, invest))
            if invest!=0:
                cursor.execute("""
                UPDATE saldo
                SET valor = valor - ?
                WHERE id = 1
                """, (invest,))
                cursor.execute("""
                INSERT INTO histSaldo (valor, operacao, quemFez, data, hora)
                VALUES (?, ?, ?, ?, ?)
                """, (invest, op, nome, data, hora))
            cursor.execute("""
            UPDATE produtos
            SET quantidade = quantidade - ?
            WHERE id = ?   
            """, (q, idProduto))
            conexao.commit()
            return
    except Exception:
        conexao.rollback()
        raise