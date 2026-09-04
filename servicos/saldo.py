def verificarSaldo(cursor):
    cursor.execute("""
    SELECT valor FROM saldo
    where id = 1
    """)
    saldo = cursor.fetchone()[0]
    return saldo

def editarSaldo(op, qtd, saldo, cursor, conexao, nome):
    import datetime as dt
    data = dt.date.today().strftime("%Y/%m/%d")
    hora = dt.datetime.now().time().strftime("%H:%M")
    try:
        if op==1:
            op = 'ENTRADA'
            cursor.execute("""
            UPDATE SALDO
            SET valor = valor + ?
            WHERE id = 1           
            """, (qtd,))
            cursor.execute("""
            INSERT  INTO histSaldo(valor, operacao, quemFez, data, hora)
            VALUES (?, ?, ?, ?, ?)
            """, (qtd, op, nome, data, hora))
            conexao.commit()
            return
        else:
            op = 'RETIRADA'
            cursor.execute("""
            UPDATE SALDO
                SET valor = valor - ?
            WHERE id = 1   
            """, (qtd,))
            cursor.execute("""
            INSERT  INTO histSaldo(valor, operacao, quemFez, data, hora)
            VALUES (?, ?, ?, ?, ?)
            """, (qtd, op, nome, data, hora))
            conexao.commit()
            return
    except Exception:
        conexao.rollback()
        raise

def comsultaHistSaldo(cursor):
    cursor.execute("""
    SELECT * FROM histSaldo
    """)
    historico = cursor.fetchall()
    return historico
