def filtragemData(escolha):
    import datetime as dt
    from calendar import monthrange
    if escolha==1:
        hoje = dt.date.today()
        dataInicial = hoje - dt.timedelta(days=7)
        dataInicial = dataInicial.strftime("%Y/%m/%d")
        dataUltima = hoje
        dataUltima = dataUltima.strftime("%Y/%m/%d")
        return dataInicial, dataUltima
    elif escolha==2:
        hoje = dt.date.today().strftime("%Y/%m/%d")
        mes = int(hoje[5:7]) - 1
        dia = int(hoje[8:])
        ano = int(hoje[0:4])
        ultimoDia = monthrange(ano, mes)[1]
        if mes == 0:
            ano -= 1
            mes = 12
        if dia > ultimoDia:
            dia = ultimoDia
        dataInicial = dt.date(ano, mes, dia).strftime("%Y/%m/%d")
        dataUltima = hoje
        dataUltima = dataUltima.strftime("%Y/%m/%d")
        return dataInicial, dataUltima 

def filtragemProdutos(n, quemCad, id, valorMin, valorMax, estoqMin, estoqMax, dataInicial, dataUltima, cursor, f=0):
    parametros = []
    if id!='':
            cursor.execute("""
                SELECT * FROM produtos 
                WHERE id = ?
            """, (id,))
            produtos = cursor.fetchall()
            return produtos
    elif dataUltima!='' and dataInicial!='':
            query = " SELECT * FROM produtos WHERE data BETWEEN ? AND ?"
            parametros.append(dataInicial)
            parametros.append(dataUltima)
    else:
        query = "SELECT * FROM produtos WHERE 1=1"
    if n!='':
        query += " AND LOWER(nome) LIKE LOWER(?)"
        parametros.append(f'%{n}%')
    if quemCad != '':
        query += " AND LOWER(quemFez) LIKE LOWER(?)"
        parametros.append(quemCad)
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
    if f=='REL':
        return query, parametros
    cursor.execute(query, parametros)
    produtos = cursor.fetchall()
    return produtos

def filtragemMov(n, quemCad, id, unid, dataInicial, dataUltima, cursor, mov, f=0):
    parametros = []
    if id!='':
            cursor.execute("""
                SELECT * FROM historicoMovimentacao 
                WHERE id = ?
            """, (id,))
            historico = cursor.fetchall()
            return historico
    elif dataUltima!='' and dataInicial!='':
            query = " SELECT * FROM historicoMovimentacao WHERE data BETWEEN ? AND ?"
            parametros.append(dataInicial)
            parametros.append(dataUltima)
    else:
        query = "SELECT * FROM historicoMovimentacao WHERE 1=1"
    if unid != '':
            query += "AND unid = ? "
            parametros.append(unid)
    if n!='':
        query += " AND LOWER(produto) LIKE LOWER(?)"
        parametros.append(f'%{n}%')
    if quemCad != '':
        query += " AND LOWER(quemFez) LIKE LOWER(?)"  
        parametros.append(quemCad) 
    if mov!='':
        query += " AND stipo = ?"
        parametros.append(mov)
    if f=='REL':
        return query, parametros
    cursor.execute(query, parametros)
    historico = cursor.fetchall() 
    return historico

def filtragemSaldo(quemCad, valorMin, valorMax, dataInicial, dataUltima, cursor):
    parametros = []
    if dataUltima!='' and dataInicial!='':
        query = " SELECT * FROM produtos WHERE data BETWEEN ? AND ?"
        parametros.append(dataInicial)
        parametros.append(dataUltima)
    else:
        query = "SELECT * FROM produtos WHERE 1=1"
    if quemCad != '':
        query += " AND LOWER(quemFez) LIKE LOWER(?)"   
        parametros.append(quemCad)
    if valorMin!='' and valorMax!='':
        if valorMin > valorMax:
            valorMin, valorMax = valorMax, valorMin
    if valorMin!='':
        query += " AND preco >= ?"
        parametros.append(valorMin)
    if valorMax!='':
        query += " AND preco <= ?"
        parametros.append(valorMax)
    cursor.execute(query, parametros)
    historico = cursor.fetchall()
    return historico
