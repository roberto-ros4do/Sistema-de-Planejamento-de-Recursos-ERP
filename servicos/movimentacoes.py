def consultaMov(cursor):
    cursor.execute("""
        SELECT * FROM  historicoMovimentacao                  
        """) 
    historico = cursor.fetchall()
    return historico

def registroMov(produto, idProduto, tip, q, cursor, conexao, nome, stip=0, invest=0):
    import datetime as dt
    data = dt.date.today().strftime("%d/%m/%Y")
    hora = dt.datetime.now().time().strftime("%H:%M")
    if tip=='ENTRADA':
            if stip=='COMPRA':
                cursor.execute("""
                INSERT INTO historicoMovimentacao (produto, idProduto, tipo, stipo, quantidade, data, hora, quemFez, valorEnvolvido)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (produto, idProduto, tip, stip, q, data, hora, nome, invest))
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
            if stip=='DEVOLUÇÃO':
                cursor.execute("""
                INSERT INTO historicoMovimentacao (produto, idProduto, tipo, stipo, quantidade, data, hora, quemFez, valorEnvolvido)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (produto, idProduto, tip, stip, q, data, hora, nome, invest))
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
    elif tip=='SAÍDA':
        if stip=='VENDA':
            cursor.execute("""
            INSERT INTO historicoMovimentacao (produto, idProduto, tipo, stipo, quantidade, data, hora, quemFez, valorEnvolvido)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (produto, idProduto, tip, stip, q, data, hora, nome, invest))
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
        if stip=='PERCA':
            cursor.execute("""
            INSERT INTO historicoMovimentacao (produto, idProduto, tipo, stipo, quantidade, data, hora, quemFez)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (produto, idProduto, tip, stip, q, data, hora, nome))
            cursor.execute("""
            UPDATE produtos
            SET quantidade = quantidade - ?
            WHERE id = ?   
            """, (q, idProduto))
            conexao.commit()
            return
        if stip=='TRANSFERÊNCIA':
            cursor.execute("""
            INSERT INTO historicoMovimentacao (produto, idProduto, tipo, stipo, quantidade, data, hora, quemFez, valorEnvolvido)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (produto, idProduto, tip, stip, q, data, hora, nome, invest))
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