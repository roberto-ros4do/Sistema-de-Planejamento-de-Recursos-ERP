import sqlite3
def Bancos():
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuario(
                   id INTEGER PRIMARY KEY,
                   nome TEXT NOT NULL,
                   login TEXT NOT NULL,
                   senha TEXT NOT NULL
                   )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tentativasLogin(
                   identificador TEXT PRIMARY KEY,
                   tentativas INTEGER NOT NULL,
                   bloqueadoAte TEXT DEFAULT NULL
                   )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos(
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco REAL NOT NULL,
                especificacao TEXT NOT NULL,
                data TEXT NOT NULL,
                hora TEXT NOT NULL
                    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historicoMovimentacao(
                    id INTEGER PRIMARY KEY,
                    produto TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    stipo TEXT NOT NULL,
                    quantidade INTEGER NOT NULL,
                    data TEXT NOT NULL,
                    hora TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saldo(
                id INTEGER PRIMARY KEY,
                valor REAL NOT NULL   
)      
""")
    cursor.execute("""
    SELECT * FROM saldo WHERE id = 1
    """)

    if cursor.fetchone() is None:
        cursor.execute("""
        INSERT INTO saldo (id, valor)
        VALUES (1, 0)
        """)

    conexao.commit()
    conexao.close()
