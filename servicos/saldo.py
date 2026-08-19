def verificarSaldo(cursor):
    cursor.execute("""
    SELECT valor FROM saldo
    where id = 1
    """)
    saldo = cursor.fetchone()[0]
    if saldo is None:
        cursor.execute("""
        INSERT INTO saldo (id, valor)
        VALUES (1, 0)
    """)
    return saldo

def editarSaldo(op, qtd, saldo, cursor, conexao, nome):
    import datetime as dt
    if op==1:
        cursor.execute("""
        UPDATE SALDO
        SET valor = valor + ?
        WHERE id = 1           
        """, (qtd,))
        data = dt.date.today().strftime("%Y/%m/%d")
        hora = dt.datetime.now().time().strftime("%H:%M")
        conexao.commit()
        cursor.execute("""
        INSERT  INTO histSaldo(valor, operacao, quemFez, data, hora)
        """, (qtd, op, nome, data))
        return
    else:
        cursor.execute("""
        UPDATE SALDO
            SET valor = valor - ?
        WHERE id = 1   
        """, (qtd,))
        conexao.commit()
        return

def comsultaHistSaldo(cursor):
    cursor.execute("""
    SELECT * FROM histSaldo
    """)
    historico = cursor.fetchall()
    return historico
