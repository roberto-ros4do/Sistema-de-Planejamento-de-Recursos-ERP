def filtragemProdutos(valorMin, valorMax, estoqMin, estoqMax, cursor, dataInicial=0, dataUltima=0, quemCad=0, f=0, n=0, id=0, estoq=False): #OK
    import datetime as dt
    parametros = []
    if estoq:
        colunas = "id, nome, quantidade"
    else: 
        colunas = 'id, nome, preco, quantidade, data, quemFez'
    if id!='' and id!=0:
        try:
            id = int(id)
        except ValueError:
            raise ValueError('CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS')
        if id<=0:
            raise ValueError('CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS')
        cursor.execute(f"""
            SELECT {colunas} FROM produtos 
            WHERE id = ?
        """, (id,))
        produtos = cursor.fetchall()
        return produtos
    elif dataUltima!='' and dataUltima!=0 and dataInicial!='' and dataInicial!=0:
        try:
            verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
            verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
        except ValueError:
            raise ValueError('AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!')
        query = f" SELECT {colunas} FROM produtos WHERE data BETWEEN ? AND ?"
        parametros.append(dataInicial)
        parametros.append(dataUltima)
    else:
        query = f"SELECT {colunas} FROM produtos WHERE 1=1"
    if n!='' and n!=0:
        query += " AND LOWER(nome) LIKE LOWER(?)"
        parametros.append(f'%{n}%')
    if quemCad != '' and quemCad!=0:
        query += " AND LOWER(quemFez) LIKE LOWER(?)"
        parametros.append(f'%{quemCad}%')
    if valorMin!='' and valorMax!='':
        try:
            valorMin = round(float(valorMin)*100)
            valorMax = round(float(valorMax)*100)
        except ValueError:
            raise ValueError('CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0')
        if valorMin > valorMax:
            valorMin, valorMax = valorMax, valorMin
    if valorMin!='':
        try:
            if valorMax=='':
                valorMin = round(float(valorMin)*100)
        except ValueError:
            raise ValueError("CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0")
        if valorMin<=0:
            raise ValueError('CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS')
        query += " AND preco >= ?"
        parametros.append(valorMin)
    if valorMax!='':
        try:
            if valorMin=='':
                valorMax = round(float(valorMax)*100)
        except ValueError:
            raise ValueError('CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS')
        if valorMax<=0:
            raise ValueError('CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS')
        query += " AND preco <= ?"
        parametros.append(valorMax)
    if estoqMin!='' and estoqMax!='':
        try:
            estoqMin = int(estoqMin)
            estoqMax = int(estoqMax)
        except ValueError:
            raise ValueError('CAMPO ESTOQUE ACEITA APENAS VALORES INTEIROS E POSITIVOS')
        if estoqMin > estoqMax:
            estoqMin, estoqMax = estoqMax, estoqMin
    if estoqMin!='':
        try:
            estoqMin = int(estoqMin)
        except ValueError:
            raise ValueError('CAMPO ESTOQUE ACEITA APENAS VALORES INTEIROS E POSITIVOS')
        if estoqMin<=0:
            raise ValueError('CAMPO ESTOQUE ACEITA APENAS NÚMEROS INTEIROS POSITIVOS')
        query += " AND quantidade >= ?"
        parametros.append(estoqMin)
    if estoqMax!='':
        try:
            estoqMax = int(estoqMax)
        except ValueError:
            raise ValueError('CAMPO ESTOQUE ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS')
        if estoqMax<=0:
            raise ValueError('CAMPO ESTOQUE ACEITA APENAS NÚMEROS INTEIROS POSITIVOS')
        query += " AND quantidade <= ?"
        parametros.append(estoqMax)
    if f=='REL':
        return query, parametros
    cursor.execute(query, parametros)
    produtos = cursor.fetchall()
    if not produtos:
        raise ValueError('NÃO HÁ PRODUTOS COM ESTAS ESPECIFICAÇÕES!')
    return produtos

def filtragemMov(n, quemCad, idProd, unidMin, unidMax, valorMin, valorMax, dataInicial, dataUltima, cursor, mov): #OK
    import datetime as dt
    parametros = []
    if idProd!="" and idProd!=0:
        try:
            idProd = int(idProd)
        except ValueError:
            raise ValueError('CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS')
        if idProd<=0:
            raise ValueError('CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS')
        cursor.execute("""
            SELECT produto, idProduto, tipo, quantidade, data, quemFez, valorEnvolvido FROM historicoMovimentacao 
            WHERE idProduto = ?
        """, (idProd,))
        historico = cursor.fetchall()
        return historico
    elif dataUltima!='' and dataInicial!='':
        try:
            verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
            verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
        except ValueError:
            raise ValueError('AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!')
        query = " SELECT produto, idProduto, tipo, quantidade, data, quemFez, valorEnvolvido FROM historicoMovimentacao WHERE data BETWEEN ? AND ?"
        parametros.append(dataInicial)
        parametros.append(dataUltima)
    else:
        query = "SELECT produto, idProduto, tipo, quantidade, data, quemFez, valorEnvolvido FROM historicoMovimentacao WHERE 1=1"
    if unidMin!='' and unidMax!='':
        try:
            unidMin = int(unidMin)
            unidMax = int(unidMax)
        except ValueError:
            raise ValueError('CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E MAIORES QUE 0')
        if unidMin > unidMax:
            unidMin, unidMax = unidMax, unidMin
    if unidMin!='':
        try:
            unidMin = int(unidMin)
        except ValueError:
            raise ValueError('CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!')
        if unidMin<=0:
            raise ValueError('CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!')
        query += " AND quantidade >= ?"
        parametros.append(unidMin)
    if unidMax!='':
        try:
            unidMax = int(unidMax)
        except ValueError:
            raise ValueError('CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!')
        if unidMax<=0:
            raise ValueError('CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!')
        query += " AND quantidade <= ?"
        parametros.append(unidMax)
    if valorMin!='' and valorMax!='':
        try:
            valorMin = round(float(valorMin)*100)
            valorMax = round(float(valorMax)*100)
        except ValueError:
            raise ValueError('CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0')
        if valorMin > valorMax:
            valorMin, valorMax = valorMax, valorMin
    if valorMin!='':
        try:
            if valorMax=='':
                valorMin = round(float(valorMin)*100)
        except ValueError:
            raise ValueError('CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0')
        if valorMin<=0:
            raise ValueError('CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS')
        query += " AND valorEnvolvido >= ?"
        parametros.append(valorMin)
    if valorMax!='':
        try:
            if valorMin=='':
                valorMax = round(float(valorMax)*100)
        except ValueError:
            raise ValueError('CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS')
        if valorMax<=0:
            raise ValueError('CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS')
        query += " AND valorEnvolvido <= ?"
        parametros.append(valorMax)
    if n!='':
        query += " AND LOWER(produto) LIKE LOWER(?)"
        parametros.append(f'%{n}%')
    if quemCad != '':
        query += " AND LOWER(quemFez) LIKE LOWER(?)"  
        parametros.append(f'%{quemCad}%') 
    if mov!='':
        if mov not in ('COMPRA', 'VENDA', 'TRANSFERÊNCIA', 'DEVOLUÇÃO', 'PERCA'):
            raise ValueError('CAMPO OPERAÇÃO ACEITA APENAS OPERAÇÕES VÁLIDAS!')
        query += " AND tipo = ?"
        parametros.append(mov)
    cursor.execute(query, parametros)
    historico = cursor.fetchall() 
    return historico

def filtragemMovRel(quemCad, unidMin, unidMax, valorMin, valorMax, dataInicial, dataUltima, cursor, mov): #OK
    import datetime as dt
    parametros = []
    if dataUltima!='' and dataInicial!='':
        try:
            verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
            verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
        except ValueError:
            raise ValueError('AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!')
        query = " SELECT produto, idProduto, tipo, quantidade, data, quemFez, valorEnvolvido FROM historicoMovimentacao WHERE data BETWEEN ? AND ?"
        parametros.append(dataInicial)
        parametros.append(dataUltima)
    else:
        query = "SELECT produto, idProduto, tipo, quantidade, data, quemFez, valorEnvolvido FROM historicoMovimentacao WHERE 1=1"
    if unidMin!='' and unidMax!='':
        try:
            unidMin = int(unidMin)
            unidMax = int(unidMax)
        except ValueError:
            raise ValueError('CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E MAIORES QUE 0')
        if unidMin > unidMax:
            unidMin, unidMax = unidMax, unidMin
    if unidMin!='':
        try:
            unidMin = int(unidMin)
        except ValueError:
            raise ValueError('CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!')
        if unidMin<=0:
            raise ValueError('CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!')
        query += " AND quantidade >= ?"
        parametros.append(unidMin)
    if unidMax!='':
        try:
            unidMax = int(unidMax)
        except ValueError:
            raise ValueError('CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!')
        if unidMax<=0:
            raise ValueError('CAMPO UNIDADES ACEITA APENAS VALORES INTEIROS E POSITIVOS!')
        query += " AND quantidade <= ?"
        parametros.append(unidMax)
    if valorMin!='' and valorMax!='':
        try:
            valorMin = round(float(valorMin)*100)
            valorMax = round(float(valorMax)*100)
        except ValueError:
            raise ValueError('CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0')
        if valorMin > valorMax:
            valorMin, valorMax = valorMax, valorMin
    if valorMin!='':
        try:
            if valorMax=='':
                valorMin = round(float(valorMin)*100)
        except ValueError:
            raise ValueError('CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0')
        if valorMin<=0:
            raise ValueError('CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS')
        query += " AND valorEnvolvido >= ?"
        parametros.append(valorMin)
    if valorMax!='':
        try:
            if valorMin=='':
                valorMax = round(float(valorMax)*100)
        except ValueError:
            raise ValueError('CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS')
        if valorMax<=0:
            raise ValueError('CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS')
        query += " AND valorEnvolvido <= ?"
        parametros.append(valorMax)
    if quemCad != '':
        query += " AND LOWER(quemFez) LIKE LOWER(?)"  
        parametros.append(f'%{quemCad}%') 
    if mov!='':
        if mov not in ('COMPRA', 'VENDA', 'TRANSFERÊNCIA', 'DEVOLUÇÃO', 'PERCA'):
            raise ValueError('CAMPO OPERAÇÃO ACEITA APENAS OPERAÇÕES VÁLIDAS!')
        query += " AND tipo = ?"
        parametros.append(mov)
    return query, parametros

def filtragemSaldo(quemCad, tip, valorMin, valorMax, dataInicial, dataUltima, cursor, f=0): #OK
    from servicos import saldo as s
    import datetime as dt
    parametros = []
    s.consultaHistSaldo(cursor)
    if dataUltima!='' and dataInicial!='':
        try:
            verificData = dt.datetime.strptime(dataInicial, "%Y/%m/%d")
            verificData = dt.datetime.strptime(dataUltima, "%Y/%m/%d")
        except ValueError:
            raise ValueError('AS DATAS NÃO ESTÃO NO FORMATO ESPERADO!')
        query = " SELECT valor, operacao, quemFez, data, hora FROM histSaldo WHERE data BETWEEN ? AND ?"
        parametros.append(dataInicial)
        parametros.append(dataUltima)
    else:
        query = "SELECT valor, operacao, quemFez, data, hora FROM histSaldo WHERE 1=1"
    if quemCad != '':
        query += " AND LOWER(quemFez) LIKE LOWER(?)"   
        parametros.append(f'%{quemCad}%')
    if tip!='':
        if tip not in ('ENTRADA', 'SAÍDA', 'RETIRADA'):
            raise ValueError('CAMPO OPERAÇÃO ACEITA APENAS OPERAÇÕES VÁLIDAS!')
        query+= " AND operacao = ?"
        parametros.append(tip)
    if valorMin!='' and valorMax!='':
        try:
            valorMin = round(float(valorMin)*100)
            valorMax = round(float(valorMax)*100)
        except ValueError:
            raise ValueError('CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0')
        if valorMin > valorMax:
            valorMin, valorMax = valorMax, valorMin
    if valorMin!='':
        try:
            if valorMax=='':
                valorMin = round(float(valorMin)*100)
        except ValueError:
            raise ValueError('CAMPO VALOR ACEITA APENAS VALORES REAIS E MAIORES QUE 0')
        if valorMin<=0:
            raise ValueError('CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS')
        query += " AND valor >= ?"
        parametros.append(valorMin)
    if valorMax!='':
        try:
            if valorMin=='':
                valorMax = round(float(valorMax)*100)
        except ValueError:
            raise ValueError('CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS')
        if valorMax<=0:
            raise ValueError('CAMPO VALOR ACEITA APENAS NÚMEROS REAIS E POSITIVOS')
        query += " AND valor <= ?"
        parametros.append(valorMax)
    if f=='REL':
            return query, parametros
    cursor.execute(query, parametros)
    historico = cursor.fetchall() 
    return historico