from servicos import permissoes as pe

def cadastroProduto(n, q, v, invest, cursor, conexao, nome, cargo): #OK
    import datetime as dt
    from servicos import saldo as s
    if not pe.podeExecutar(cargo, 'CADASTRAR_PRODUTOS'):
            raise PermissionError('USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO')
    try:
        q = int(q)
    except ValueError:
        raise ValueError('CAMPO ESTOQUE ACEITA APENAS NÚMEROS INTEIROS POSITIVOS!')
    if q<0:
        raise ValueError('CAMPO ESTOQUE ACEITA APENAS NÚMEROS INTEIROS POSITIVOS!')
    try:
        v = round(float(v)*100)
    except ValueError:
        raise ValueError('CAMPO VALOR COBRADO ACEITA APENAS VALORES REAIS POSITIVOS!')
    if v<0:
            raise ValueError('CAMPO VALOR COBRADO ACEITA APENAS VALORES REAIS E POSITIVOS')
    try:
        invest = round(float(invest)*100)
    except ValueError:
        raise ValueError('CAMPO VALOR ACEITA APENAS NÚMEROS REAIS POSITIVOS!')
    if invest<0:
        raise ValueError('CAMPO INVESTIMENTO ACEITA APENAS NÚMEROS REAIS E MAIORES QUE 0!')
    saldo = s.verificarSaldo(cursor) 
    if invest>saldo:
            raise ValueError('SALDO INSUFICIENTE!')
    if q<=0:
        raise ValueError('CAMPO ESTOQUE ACEITA APENAS NÚMEROS INTEIROS POSITIVOS!')
    data = dt.date.today().strftime("%Y/%m/%d")
    hora = dt.datetime.now().time().strftime("%H:%M")
    if n == '':
        raise ValueError("CAMPO NOME DE PRODUTO OBRIGATÓRIO!")
    try:
        cursor.execute("""
        INSERT INTO produtos (nome, quantidade, preco, data, hora, quemFez)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (n, q, v, data, hora, nome))
        idProd = cursor.lastrowid
        if invest!=0:
            cursor.execute("""
            INSERT INTO histSaldo (valor, operacao, quemFez, data, hora)
            VALUES (?, ? ,? ,? ,?)
            """, (invest, 'SAÍDA', nome, data, hora))
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
    
def deletarProduto(idProd, cursor, conexao, quemFez, cargo):
    if not pe.podeExecutar(cargo, 'DELETAR_PRODUTO'):
        raise PermissionError('USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO')
    import datetime as dt
    data = dt.date.today().strftime("%Y/%m/%d")
    hora = dt.datetime.now().time().strftime("%H:%M")
    try:
        try:
            idProd = int(idProd)
        except ValueError:
            raise ValueError('CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS')
        if idProd<=0:
            raise ValueError('CAMPO ID ACEITA APENAS NÚMEROS INTEIROS E POSITIVOS')
        produto = buscarProduto(idProd, cursor)
        if produto is None:
            raise ValueError('PRODUTO NÃO ENCONTRADO')
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
        conexao.commit()
        return
    except Exception:
        conexao.rollback()
        raise


def consultaProdutos(cursor):
    cursor.execute("""
    SELECT id, nome, preco, quantidade, data, quemFez FROM  produtos                  
    """)                  
    consulta = cursor.fetchall()
    if not consulta:
        raise ValueError('AINDA NÃO HÁ PRODUTOS CADASTRADOS!')
    return consulta