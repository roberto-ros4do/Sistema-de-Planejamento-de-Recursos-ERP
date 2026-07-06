def verificaLogin(cursor, conexao, login, senha):
    cursor.execute("""
    SELECT login, senha FROM usuario
    WHERE login = ? 
    AND senha = ?
    """, (login, senha))
    usuario = cursor.fetchone()
    if (login, senha) == usuario:
        return True
    else:
        return False
    
def cadastraLogin(cursor, conexao, nome, login, senha):
    cursor.execute("""
    INSERT INTO usuario (nome, login, senha)
    VALUES(?, ?, ?)
    """, (nome, login, senha))
    conexao.commit()

def verificaTentativas(maq, cursor, conexao):
    import datetime as dt
    cursor.execute("""
    SELECT identificador, tentativas, bloqueadoAte FROM tentativasLogin
    WHERE identificador = ?
    """, (maq,))
    resultado = cursor.fetchone()
    return resultado


def registraTentativa(identificador, tentativas, cursor, conexao, bloqueadoAte,logou=False ):
    if logou:
        cursor.execute(""" 
            UPDATE tentativasLogin
            SET tentativas = 0,
            bloqueadoAte = NULL
            WHERE identificador = ?
        """, (identificador,))
    else:
        if tentativas==3:
            cursor.execute("""
            INSERT INTO tentativasLogin(identificador, tentativas)
            VALUES (?, ?)
            """, (identificador, tentativas))
        else:
            cursor.execute("""
            UPDATE tentativasLogin
            SET tentativas = ?,
            bloqueadoAte = ?
            WHERE identificador = ?
            """, (tentativas, bloqueadoAte, identificador))
        conexao.commit()