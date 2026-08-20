import bcrypt

def verificaLogin(cursor, conexao, login, senha):
    cursor.execute("""
    SELECT login, senha, nome FROM usuario
    WHERE login = ? 
    """, (login,))
    usuario = cursor.fetchone()
    senhaBytes = senha.encode("utf-8")
    if usuario is not None:
        senhaCerta = bcrypt.checkpw(senhaBytes, usuario[1])
        if senhaCerta:
            return True, usuario[2]
        else:
            return False, None
    else:
        return False, None  

def verificaLoginRepetido(login, cursor):
    cursor.execute("""
    SELECT login FROM usuario
    WHERE login = ?
    """, (login,))
    logins = cursor.fetchall()
    if logins is not None:
        return False
    else:
        return True

    
def cadastraLogin(cursor, conexao, nome, login, senha, cargo):
    senhaBytes = senha.encode("utf-8")
    hashSenha = bcrypt.hashpw(senhaBytes, bcrypt.gensalt())
    cursor.execute("""
    INSERT INTO usuario (nome, login, senha, cargo)
    VALUES(?, ?, ?, ?)
    """, (nome, login, hashSenha, cargo))
    conexao.commit()

def verificaTentativas(maq, cursor, conexao):
    import datetime as dt
    cursor.execute("""
    SELECT identificador, tentativas, bloqueadoAte FROM tentativasLogin
    WHERE identificador = ?
    """, (maq,))
    resultado = cursor.fetchone()
    return resultado


def registraTentativa(identificador, tentativas, cursor, conexao, login=0, bloqueadoAte=None,logou=False):
    if logou:
        cursor.execute(""" 
            DELETE FROM tentativasLogin
            WHERE identificador = ?
        """, (identificador,))
        cursor.execute("""
            SELECT cargo FROM usuario
            WHERE login = ?
        """, (login,))
        cargo = cursor.fetchone()[0] #Para não retornar o resultado em uma tupla
        return cargo
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