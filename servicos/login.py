def verificaLogin(cursor, conexao, login, senha):
    cursor.execute("""
    SELECT login, senha FROM usuario
    """)
    usuarios = cursor.fetchall()
    if (login, senha) in usuarios:
        return True
    else:
        return False
    
def cadastraLogin(cursor, conexao, nome, login, senha):
    cursor.execute("""
    INSERT INTO (nome, login, senha)
    VALUES(?, ?, ?)
    """, (nome, login, senha))
    conexao.commit()