def filtragemData(escolha, op, cursor, dataInicial=0, dataUltima=0):
    import datetime as dt
    from calendar import monthrange
    if escolha==1:
        hoje = dt.date.today()
        dataUltima = hoje - dt.timedelta(days=7)
        cursor.execute(f"""
        SELECT * FROM {op}
        WHERE data BETWEEN ? AND ?
        """, (dataUltima.strftime("%Y/%m/%d"), hoje.strftime("%Y/%m/%d")))
        historico = cursor.fetchall()
        return historico
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
        dataUltima = dt.date(ano, mes, dia).strftime("%Y/%m/%d")
        cursor.execute(f"""
        SELECT * FROM {op}
        WHERE data BETWEEN ? AND ?
        """, (dataUltima, hoje))
        historico = cursor.fetchall()
        return historico
    elif escolha==3:
            cursor.execute(f"""
            SELECT * FROM {op}
            WHERE data BETWEEN ? AND ?
            """, (dataInicial, dataUltima))
            historico = cursor.fetchall()
            return historico