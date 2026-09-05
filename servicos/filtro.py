def filtragemProdutos(valorMin, valorMax, estoqMin, estoqMax, cursor, dataInicial=0, dataUltima=0, quemCad=0, f=0, n=0, id=0):
    parametros = []
    if id!='' and id!=0:
            cursor.execute("""
                SELECT id, nome, preco, quantidade, data, quemFez FROM produtos 
                WHERE id = ?
            """, (id,))
            produtos = cursor.fetchall()
            return produtos
    elif dataUltima!='' and dataUltima!=0 and dataInicial!='' and dataInicial!=0:
        if f=='REL':
            query = " SELECT id, nome, preco, quantidade, data, quemFez FROM produtos WHERE data BETWEEN ? AND ?"
            parametros.append(dataInicial)
            parametros.append(dataUltima)
        else:
            query = "SELECT id, nome, preco, quantidade, data, quemFez FROM produtos WHERE 1=1"
    else:
        query = "SELECT id, nome, preco, quantidade, data, quemFez FROM produtos WHERE 1=1"
    if n!='' and n!=0:
        query += " AND LOWER(nome) LIKE LOWER(?)"
        parametros.append(f'%{n}%')
    if quemCad != '' and quemCad!=0:
        query += " AND LOWER(quemFez) LIKE LOWER(?)"
        parametros.append(quemCad)
    if valorMin!='' and valorMax!='':
        if valorMin > valorMax:
            valorMin, valorMax = valorMax, valorMin
    if valorMin!='':
        query += " AND preco >= ?"
        parametros.append(valorMin)
    if valorMax!='':
        query += " AND  preco  <= ?"
        parametros.append(valorMax)
    if estoqMin!='' and estoqMax!='':
            if estoqMin > estoqMax:
                estoqMin, estoqMax = estoqMax, estoqMin
    if estoqMin!='':
        query += " AND quantidade >= ?"
        parametros.append(estoqMin)
    if estoqMax!='':
        query += " AND quantidade <= ?"
        parametros.append(estoqMax)
    if f=='REL':
        return query, parametros
    cursor.execute(query, parametros)
    produtos = cursor.fetchall()
    return produtos

def filtragemMov(n, quemCad, idProd, unidMin, unidMax, valorMin, valorMax, dataInicial, dataUltima, cursor, mov):
    parametros = []
    if idProd!="" and idProd!=0:
        cursor.execute("""
            SELECT produto, idProduto, tipo, quantidade, data, quemFez, valorEnvolvido FROM historicoMovimentacao 
            WHERE id = ?
        """, (idProd,))
        historico = cursor.fetchall()
        return historico
    elif dataUltima!='' and dataInicial!='':
            query = " SELECT produto, idProduto, tipo, quantidade, data, quemFez, valorEnvolvido FROM historicoMovimentacao WHERE data BETWEEN ? AND ?"
            parametros.append(dataInicial)
            parametros.append(dataUltima)
    else:
        query = "SELECT produto, idProduto, tipo, quantidade, data, quemFez, valorEnvolvido FROM historicoMovimentacao WHERE 1=1"
    if unidMin!='' and unidMax!='':
        if unidMin > unidMax:
            unidMin, unidMax = unidMax, unidMin
    if unidMin!='':
        query += " AND quantidade >= ?"
        parametros.append(unidMin)
    if unidMax!='':
        query += " AND quantidade <= ?"
        parametros.append(unidMax)
    if valorMin!='' and valorMax!='':
        if valorMin > valorMax:
            valorMin, valorMax = valorMax, valorMin
    if valorMin!='':
        query += " AND valorEnvolvido >= ?"
        parametros.append(valorMin)
    if valorMax!='':
        query += " AND  valorEnvolvido  <= ?"
        parametros.append(valorMax)
    if n!='':
        query += " AND LOWER(produto) LIKE LOWER(?)"
        parametros.append(f'%{n}%')
    if quemCad != '':
        query += " AND LOWER(quemFez) LIKE LOWER(?)"  
        parametros.append(quemCad) 
    if mov!='':
        query += " AND tipo = ?"
        parametros.append(mov)
    cursor.execute(query, parametros)
    historico = cursor.fetchall() 
    return historico

def filtragemMovRel(quemCad, unidMin, unidMax, valorMin, valorMax, dataInicial, dataUltima, cursor, mov):
    parametros = []
    if dataUltima!='' and dataInicial!='':
            query = " SELECT produto, idProduto, tipo, quantidade, data, quemFez, valorEnvolvido FROM historicoMovimentacao WHERE data BETWEEN ? AND ?"
            parametros.append(dataInicial)
            parametros.append(dataUltima)
    else:
        query = "SELECT produto, idProduto, tipo, quantidade, data, quemFez, valorEnvolvido FROM historicoMovimentacao WHERE 1=1"
    if unidMin!='':
        query += " AND quantidade >= ?"
        parametros.append(unidMin)
    if unidMax!='':
        query += " AND quantidade <= ?"
        parametros.append(unidMax)
    if valorMin!='' and valorMax!='':
        if valorMin > valorMax:
            valorMin, valorMax = valorMax, valorMin
    if valorMin!='':
        query += " AND valorEnvolvido >= ?"
        parametros.append(valorMin)
    if valorMax!='':
        query += " AND  valorEnvolvido  <= ?"
        parametros.append(valorMax)
    if quemCad != '':
        query += " AND LOWER(quemFez) LIKE LOWER(?)"  
        parametros.append(quemCad) 
    if mov!='':
        query += " AND tipo = ?"
        parametros.append(mov)
    return query, parametros

def filtragemSaldo(quemCad, tip, valorMin, valorMax, dataInicial, dataUltima, cursor, f=0):
    parametros = []
    if dataUltima!='' and dataInicial!='':
        query = " SELECT valor, operacao, quemFez, data, hora FROM histSaldo WHERE data BETWEEN ? AND ?"
        parametros.append(dataInicial)
        parametros.append(dataUltima)
    else:
        query = "SELECT valor, operacao, quemFez, data, hora FROM histSaldo WHERE 1=1"
    if quemCad != '':
        query += " AND LOWER(quemFez) LIKE LOWER(?)"   
        parametros.append(quemCad)
    if tip!='':
        query+= " AND operacao = ?"
        parametros.append(tip)
    if valorMin!='' and valorMax!='':
        if valorMin > valorMax:
            valorMin, valorMax = valorMax, valorMin
    if valorMin!='':
        query += " AND valor >= ?"
        parametros.append(valorMin)
    if valorMax!='':
        query += " AND valor <= ?"
        parametros.append(valorMax)
    if f=='REL':
            return query, parametros
    cursor.execute(query, parametros)
    historico = cursor.fetchall() 
    return historico