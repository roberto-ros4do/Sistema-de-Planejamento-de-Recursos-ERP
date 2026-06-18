def consultaMov(cursor):
    cursor.execute("""
        SELECT * FROM  historicoMovimentacao                  
        """) 
    historico = cursor.fetchall()
    return historico

def registroMov(produto, idProduto, op, tip, stip, q, data, hora, cursor, conexao, invest=0):
    if tip=='ENTRADA':
            if stip=='COMPRA':
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
            if stip=='DEVOLUÇÃO':
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
    else:
        if stip=='VENDA':
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
        if stip=='PERCA':
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
        if stip=='TRANSFERÊNCIA':
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