from servicos import permissoes as pe

def verificarSaldo(cursor):
    cursor.execute("""
    SELECT valor FROM saldo
    where id = 1
    """)
    saldo = cursor.fetchone()[0]
    return saldo

def editarSaldo(op, qtd, saldo, cursor, conexao, nome, cargo):
    if not pe.podeExecutar(cargo, 'EDITAR_SALDO'):
        raise PermissionError('USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO')
    import datetime as dt
    data = dt.date.today().strftime("%Y/%m/%d")
    hora = dt.datetime.now().time().strftime("%H:%M")
    try:
        if op=='ENTRADA':
            try:
                qtd = round(float(qtd)*100)
            except ValueError:
                raise ValueError('CAMPO VALOR ACEITA APENAS VALORES REAIS')
            if qtd<0:
                raise ValueError('CAMPO VALOR ACEITA APENAS NÚMEROS REAIS POSITIVOS')
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
        elif op=='RETIRADA':
            try:
                qtd = round(float(qtd)*100)
            except ValueError:
                raise ValueError('CAMPO VALOR ACEITA APENAS VALORES REAIS')
            if qtd<0:
                raise ValueError('CAMPO VALOR ACEITA APENAS NÚMEROS REAIS POSITIVOS!')
            if saldo<qtd:
                raise ValueError('SALDO INSUFICIENTE PARA RETIRADA!')
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

def consultaHistSaldo(cursor):
    cursor.execute("""
    SELECT valor, operacao, quemFez, data, hora FROM histSaldo
    """) 
    historico = cursor.fetchall()
    if not historico:
        raise ValueError('AINDA NÃO FORAM REGISTRADAS MOVIMENTAÇÕES! ')
    return historico
