from servicos import permissoes as pe
from servicos import erros as er
def consultaMov(cursor):
    cursor.execute("""
        SELECT produto, idProduto, tipo, quantidade, data, quemFez, valorEnvolvido FROM  historicoMovimentacao                  
        """) 
    historico = cursor.fetchall()
    return historico

def registroMov(idProduto, tip, q, cursor, conexao, nome, cargo, invest=0):
    from servicos import produtos as p
    from servicos import saldo as s
    if not pe.podeExecutar(cargo, 'REGISTRAR_MOVIMENTACOES'):
        raise PermissionError('USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO')
    import datetime as dt
    data = dt.date.today().strftime("%Y/%m/%d")
    hora = dt.datetime.now().time().strftime("%H:%M")
    try:
        if tip=='COMPRA':
            op = 'SAÍDA'
            try:
                idProduto = int(idProduto)
            except ValueError:
                raise ValueError('CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS!')
            if idProduto<=0:
                raise ValueError('CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS!')
            resultado = p.buscarProduto(idProduto, cursor)
            if resultado is None:
                raise er.NaoEncontradoError('PRODUTO NÃO ENCONTRADO')
            produto = resultado[0]
            try:
                q = int(q)
            except ValueError:
                raise ValueError('CAMPO QUANTIDADE ACEITA APENAS VALORES INTEIROS E POSITIVOS')
            if q<=0:
                raise ValueError('CAMPO QUANTIDADE ACEITA APENAS VALORES INTEIROS E POSITIVOS')
            try:
                invest = round(float(invest)*100)
            except ValueError:
                raise ValueError('CAMPO VALOR ENVOLVIDO ACEITA APENAS VALORES INTEIROS E POSITIVOS!')
            if invest<0:
                raise ValueError('CAMPO VALOR ENVOLVIDO ACEITA APENAS VALORES INTEIROS E POSITIVOS!')
            saldo = s.verificarSaldo(cursor)
            if invest>saldo:
                raise ValueError('SALDO INSUFICIENTE')
            
            cursor.execute("""
            INSERT INTO historicoMovimentacao (produto, idProduto, tipo, quantidade, data, hora, quemFez, valorEnvolvido)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (produto, idProduto, tip, q, data, hora, nome, invest))
            if invest!=0:
                cursor.execute("""
                UPDATE saldo
                SET valor = valor - ?
                WHERE id = 1  
                """, (invest,))
                cursor.execute("""
                INSERT INTO histSaldo (valor, operacao, quemFez, data, hora)
                VALUES (?, ?, ?, ?, ?)
                """, (invest, op, nome, data, hora))
            cursor.execute("""
            UPDATE produtos
            SET quantidade = quantidade + ?
            WHERE id = ?  
            """, (q, idProduto))
            conexao.commit()
            return
        if tip=='DEVOLUÇÃO':
            op = 'SAÍDA'
            try:
                idProduto = int(idProduto)
            except ValueError:
                raise ValueError('CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS!')
            if idProduto<=0:
                raise ValueError('CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS!')
            resultado = p.buscarProduto(idProduto, cursor)
            if resultado is None:
                raise er.NaoEncontradoError('PRODUTO NÃO ENCONTRADO')
            produto = resultado[0]
            try:
                q = int(q)
            except ValueError:
                raise ValueError('CAMPO QUANTIDADE ACEITA APENAS VALORES INTEIROS E POSITIVOS')
            if q<=0:
                raise ValueError('CAMPO QUANTIDADE ACEITA APENAS VALORES INTEIROS E POSITIVOS')
            try:
                invest = round(float(invest)*100)
            except ValueError:
                raise ValueError('CAMPO VALOR ENVOLVIDO ACEITA APENAS VALORES INTEIROS E POSITIVOS!')
            if invest<0:
                raise ValueError('CAMPO VALOR ENVOLVIDO ACEITA APENAS VALORES INTEIROS E POSITIVOS!')
            saldo = s.verificarSaldo(cursor)
            if invest>saldo:
                raise ValueError('SALDO INSUFICIENTE')
            cursor.execute("""
            INSERT INTO historicoMovimentacao (produto, idProduto, tipo, quantidade, data, hora, quemFez, valorEnvolvido)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (produto, idProduto, tip, q, data, hora, nome, invest))
            if invest!=0:
                cursor.execute("""
                UPDATE saldo
                SET valor = valor - ?
                WHERE id = 1  
                """, (invest,))
                cursor.execute("""
                INSERT INTO histSaldo (valor, operacao, quemFez, data, hora)
                VALUES (?, ?, ?, ?, ?)
                """, (invest, op, nome, data, hora))
            cursor.execute("""
            UPDATE produtos
            SET quantidade = quantidade + ?
            WHERE id = ?   
            """, (q, idProduto))
            conexao.commit()
            return
        if tip=='VENDA':
            op='ENTRADA'
            try:
                idProduto = int(idProduto)
            except ValueError:
                raise ValueError('CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS!')
            if idProduto<=0:
                raise ValueError('CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS!')
            resultado = p.buscarProduto(idProduto, cursor)
            if resultado is None:
                raise er.NaoEncontradoError('PRODUTO NÃO ENCONTRADO')
            produto = resultado[0]
            unidades = resultado[1]
            try:
                q = int(q)
            except ValueError:
                raise ValueError('CAMPO QUANTIDADE ACEITA APENAS VALORES INTEIROS E POSITIVOS')
            if q<=0:
                raise ValueError('CAMPO QUANTIDADE ACEITA APENAS VALORES INTEIROS E POSITIVOS')
            try:
                invest = round(float(invest)*100)
            except ValueError:
                raise ValueError('CAMPO VALOR ENVOLVIDO ACEITA APENAS VALORES INTEIROS E POSITIVOS!')
            if invest<0:
                raise ValueError('CAMPO VALOR ENVOLVIDO ACEITA APENAS VALORES INTEIROS E POSITIVOS!')
            if q>unidades:
                raise ValueError('ESTOQUE INSUFICIENTE')
            cursor.execute("""
            INSERT INTO historicoMovimentacao (produto, idProduto, tipo, quantidade, data, hora, quemFez, valorEnvolvido)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (produto, idProduto, tip, q, data, hora, nome, invest))
            if invest!=0:
                cursor.execute("""
                UPDATE saldo
                SET valor = valor + ?
                WHERE id = 1  
                """, (invest,))
                cursor.execute("""
                INSERT INTO histSaldo (valor, operacao, quemFez, data, hora)
                VALUES (?, ?, ?, ?, ?)
                """, (invest, op, nome, data, hora))
            cursor.execute("""
            UPDATE produtos
            SET quantidade = quantidade - ?
            WHERE id = ?           
            """, (q, idProduto))
            conexao.commit()
            return
        if tip=='PERCA':
            try:
                idProduto = int(idProduto)
            except ValueError:
                raise ValueError('CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS!')
            if idProduto<=0:
                raise ValueError('CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS!')
            resultado = p.buscarProduto(idProduto, cursor)
            if resultado is None:
                raise er.NaoEncontradoError('PRODUTO NÃO ENCONTRADO')
            produto = resultado[0]
            unidades = resultado[1]
            try:
                q = int(q)
            except ValueError:
                raise ValueError('CAMPO QUANTIDADE ACEITA APENAS VALORES INTEIROS E POSITIVOS')
            if q<=0:
                raise ValueError('CAMPO QUANTIDADE ACEITA APENAS VALORES INTEIROS E POSITIVOS')
            if q>unidades:
                raise ValueError('ESTOQUE INSUFICIENTE')
            cursor.execute("""
            INSERT INTO historicoMovimentacao (produto, idProduto, tipo, quantidade, data, hora, quemFez)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (produto, idProduto, tip, q, data, hora, nome))
            cursor.execute("""
            UPDATE produtos
            SET quantidade = quantidade - ?
            WHERE id = ?   
            """, (q, idProduto))
            conexao.commit()
            return
        if tip=='TRANSFERÊNCIA':
            op='SAÍDA'
            try:
                idProduto = int(idProduto)
            except ValueError:
                raise ValueError('CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS!')
            if idProduto<=0:
                raise ValueError('CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS!')
            resultado = p.buscarProduto(idProduto, cursor)
            if resultado is None:
                raise er.NaoEncontradoError('PRODUTO NÃO ENCONTRADO')
            produto = resultado[0]
            unidades = resultado[1]
            try:
                q = int(q)
            except ValueError:
                raise ValueError('CAMPO QUANTIDADE ACEITA APENAS VALORES INTEIROS E POSITIVOS')
            if q<=0:
                raise ValueError('CAMPO QUANTIDADE ACEITA APENAS VALORES INTEIROS E POSITIVOS')
            try:
                invest = round(float(invest)*100)
            except ValueError:
                raise ValueError('CAMPO VALOR ENVOLVIDO ACEITA APENAS VALORES INTEIROS E POSITIVOS!')
            if invest<0:
                raise ValueError('CAMPO VALOR ENVOLVIDO ACEITA APENAS VALORES INTEIROS E POSITIVOS!')
            if q>unidades:
                raise ValueError('ESTOQUE INSUFICIENTE')
            saldo = s.verificarSaldo(cursor)
            if invest>saldo:
                raise ValueError('SALDO INSUFICIENTE')
            cursor.execute("""
            INSERT INTO historicoMovimentacao (produto, idProduto, tipo, quantidade, data, hora, quemFez, valorEnvolvido)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (produto, idProduto, tip, q, data, hora, nome, invest))
            if invest!=0:
                cursor.execute("""
                UPDATE saldo
                SET valor = valor - ?
                WHERE id = 1
                """, (invest,))
                cursor.execute("""
                INSERT INTO histSaldo (valor, operacao, quemFez, data, hora)
                VALUES (?, ?, ?, ?, ?)
                """, (invest, op, nome, data, hora))
            cursor.execute("""
            UPDATE produtos
            SET quantidade = quantidade - ?
            WHERE id = ?   
            """, (q, idProduto))
            conexao.commit()
            return
        else:
            raise ValueError('CAMPO OPERAÇÃO ACEITA APENAS OPERAÇÕES VÁLIDAS!')
    except Exception:
        conexao.rollback()
        raise