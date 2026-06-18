def verificarSaldo(cursor):
    cursor.execute("""
    SELECT valor FROM saldo
    where id = 1
    """)
    saldo = cursor.fetchone()[0]
    return saldo

def editarSaldo(op, qtd, saldo, cursor, conexao, ):
    if op==1:
        cursor.execute("""
        UPDATE SALDO
        SET valor = valor + ?
        WHERE id = 1           
        """, (qtd,))
        conexao.commit()
        return
    else:
        cursor.execute("""
        UPDATE SALDO
            SET valor = valor - ?
        WHERE id = 1   
        """, (qtd,))
        conexao.commit()
        return