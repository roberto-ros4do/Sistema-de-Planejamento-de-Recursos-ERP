def cadastroProduto(n, q, v, invest, cursor, conexao, nome):
    import datetime as dt
    data = dt.date.today().strftime("%Y/%m/%d")
    hora = dt.datetime.now().time().strftime("%H:%M")
    try:
        cursor.execute("""
        INSERT INTO produtos (nome, quantidade, preco, data, hora, quemFez)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (n, q, v, data, hora, nome))
        idProd = cursor.lastrowid
        if invest=='':
            invest=0
        cursor.execute("""
        UPDATE saldo
        SET valor = valor - ?
        WHERE id = 1  
        """, (invest,))
        tip = 'CADASTRO'
        cursor.execute("""
        INSERT INTO historicoMovimentacao (produto, idProduto, tipo, quantidade, data, hora, quemFez, valorEnvolvido)
        VALUES (? ,? ,? ,? ,? , ?, ?, ?)
        """, (n, idProd, tip, q, data, hora, nome, invest ))
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    return
        

def buscarProduto(idProd, cursor):
    cursor.execute("""
    SELECT nome, quantidade FROM produtos
    WHERE id = ?                  
    """, (idProd,))
    consulta = cursor.fetchone()
    return consulta
    
def deletarProduto(idProd, cursor, conexao, quemFez):
    import datetime as dt
    data = dt.date.today().strftime("%Y/%m/%d")
    hora = dt.datetime.now().time().strftime("%H:%M")
    try:
        cursor.execute("""
            SELECT nome FROM produtos
            WHERE id = ?
        """, (idProd,))
        nome = cursor.fetchone()[0]
        cursor.execute("""
        DELETE FROM produtos
        WHERE id = ?
        """, (idProd,))
        tip = 'DELETAÇÃO'
        cursor.execute("""
        INSERT INTO historicoMovimentacao (produto, idProduto, tipo, data, hora, quemFez)
        VALUES (? ,? ,? ,? ,? , ?)
        """, (nome, idProd, tip, data, hora, quemFez ))
    except Exception:
        cursor.connection.rollback()
        raise
    conexao.commit()
    return

def consultaProdutos(cursor):
    cursor.execute("""
    SELECT * FROM  produtos                  
    """)                  
    consulta = cursor.fetchall()
    return consulta