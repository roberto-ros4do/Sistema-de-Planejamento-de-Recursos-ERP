def cadastroProduto(n, q, v, invest, esp2, data, hora, cursor, conexao):
    cursor.execute("""
    INSERT INTO produtos (nome, quantidade, preco, especificacao, data, hora)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (n, q, v, esp2, data, hora))
    cursor.execute("""
    UPDATE SALDO
    SET valor = valor - ?
    WHERE id = 1          
    """, (invest,))
    conexao.commit()
    return
        
def filtragemProdutos(n, valorMin, valorMax, estoqMin, estoqMax, cursor):
    query = "SELECT * FROM produtos WHERE 1=1"
    parametros = []
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
    return produtos

def buscarProduto(idProd, cursor):
    cursor.execute("""
    SELECT nome, quantidade FROM produtos
    WHERE id = ?                  
    """, (idProd,))
    consulta = cursor.fetchone()
    return consulta
    
def deletarProduto(idProd, cursor):
    deletado = cursor.execute("""
    DELETE FROM produtos
    WHERE id = ?
    """, (idProd,))
    return deletado

def consultaProdutos(cursor, unidades=0):
    cursor.execute("""
    SELECT * FROM  produtos                  
    """)                  
    consulta = cursor.fetchall()
    return consulta
