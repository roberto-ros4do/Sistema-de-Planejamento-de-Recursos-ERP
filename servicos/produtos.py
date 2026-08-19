def cadastroProduto(n, q, v, invest, esp2, cursor, conexao, nome):
    import datetime as dt
    data = dt.date.today().strftime("%Y/%m/%d")
    hora = dt.datetime.now().time().strftime("%H:%M")
    cursor.execute("""
    INSERT INTO produtos (nome, quantidade, preco, especificacao, data, hora, quemCriou)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (n, q, v, esp2, data, hora, nome))
    cursor.execute("""
    UPDATE SALDO
    SET valor = valor - ?
    WHERE id = 1          
    """, (invest,))
    cursor.execute("""
    SELECT id FROM produtos
    WHERE nome = ?
    quantidade = ?
    preco = ?
    especificacao = ?
    data = ?
    hora = ?
    quemCriou = ?
    """, (n, q, v, esp2, data, hora, nome))
    id = cursor.fetchone()[0]
    tip = 'CADASTRO'
    cursor.execute("""
    INSERT INTO historicoMovimentacao (produto, idProduto, tipo, quantidade, data, hora, quemFez, valorEnvolvido)
    VALUES (? ,? ,? ,? ,? , ?, ?, ?)
    """, (n, id, tip, q, data, hora, nome, v ))
    conexao.commit()
    return
        

def buscarProduto(idProd, cursor):
    cursor.execute("""
    SELECT nome, quantidade FROM produtos
    WHERE id = ?                  
    """, (idProd,))
    consulta = cursor.fetchone()
    return consulta
    
def deletarProduto(idProd, cursor):
    import datetime as dt
    data = dt.date.today().strftime("%Y/%m/%d")
    hora = dt.datetime.now().time().strftime("%H:%M")
    cursor.execute("""
        SELECT nome FROM produtos
        WHERE id = ?
    """, (idProd,))
    nome = cursor.fetchone()[0]
    deletado = cursor.execute("""
    DELETE FROM produtos
    WHERE id = ?
    """, (idProd,))
    tip = 'DELETAÇÃO'
    cursor.execute("""
    INSERT INTO historicoMovimentacao (produto, idProduto, tipo, data, hora, quemFez)
    VALUES (? ,? ,? ,? ,? , ?, ?, ?)
    """, (nome, idProd, tip, data, hora, nome ))
    return deletado

def consultaProdutos(cursor):
    cursor.execute("""
    SELECT * FROM  produtos                  
    """)                  
    consulta = cursor.fetchall()
    return consulta
