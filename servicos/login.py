import bcrypt
import datetime as dt
from servicos import permissoes as pe

def verificaLogin(cursor, login, senha, conexao): #OK
    import socket
    maq = socket.gethostname()
    resultado = verificaTentativas(maq, cursor, conexao)
    if resultado is None:
        identificador = maq
        tentativas = 4
        bloqueadoAte = None
    else:
        identificador = resultado[0]
        tentativas = resultado[1]
        bloqueadoAte = resultado[2]
    if bloqueadoAte is None or bloqueadoAte <= dt.datetime.now():
        cursor.execute("""
        SELECT login, senha, nome FROM usuario
        WHERE login = ? 
        """, (login,))
        usuario = cursor.fetchone()
        senhaBytes = senha.encode("utf-8")
        if usuario is not None:
            senhaCerta = bcrypt.checkpw(senhaBytes, usuario[1])
            if senhaCerta:
                existe = True
                nome = usuario[2]
            else:
                existe = False 
                nome = None
        else:
            existe = False
            nome = None
        if existe:
            tentativas = 4
            bloqueadoAte = None
            logou = True
            cargo = registraTentativa(identificador, tentativas, cursor, conexao, login, bloqueadoAte, logou)
        else:
            tentativas -= 1
            if tentativas > 0:
                registraTentativa(identificador, tentativas, cursor, conexao)
                raise ValueError(f'USUÁRIO OU SENHA INVÁLIDOS! VOCÊ POSSUI {tentativas} TENTATIVAS RESTANTES')
            else:
                bloqueadoAte = dt.datetime.now() + dt.timedelta(minutes=5)
                registraTentativa(identificador, tentativas, cursor, conexao, bloqueadoAte=bloqueadoAte)
                logou = False
                cargo = None
                nome = None
                raise ValueError('VOCÊ ESGOTOU SUAS TENTATIVAS, TENTE NOVAMENTE EM 5 MINUTOS!')
        return nome, logou, cargo
    else:
        raise  ValueError('VOCÊ ACABOU COM SUAS TENTATIVAS! TENTE NOVAMENTE MAIS TARDE!')

def verificaLoginRepetido(login, cursor):
    cursor.execute("""
    SELECT login FROM usuario
    WHERE login = ?
    """, (login,))
    logins = cursor.fetchone()
    if logins is not None:
        return True
    else:
        return False

    
def cadastraLogin(cursor, conexao, nome, login, senha, cargo, cargoUsuarioCriado): #OK
    if not pe.podeExecutar(cargo, 'CADASTRAR_USUARIO'):
            raise PermissionError('USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO')
    senhaBytes = senha.encode("utf-8")
    hashSenha = bcrypt.hashpw(senhaBytes, bcrypt.gensalt())
    if verificaLoginRepetido(login, cursor):
        raise ValueError('LOGIN JÁ EXISTE NO SISTEMA!')
    if len(senha) <= 5:
        raise ValueError('INSIRA UMA SENHA MAIOR QUE 5 CARACTERES!')
    if cargoUsuarioCriado not in ('ADMINISTRADOR', 'GERENTE', 'ESTOQUISTA', 'FINANCEIRO', 'CONSULTA'):
        raise ValueError('CAMPO DE CARGO ACEITA APENAS CARGOS EXISTENTES!')
    try:
        cursor.execute("""
        INSERT INTO usuario (nome, login, senha, cargo)
        VALUES(?, ?, ?, ?)
        """, (nome, login, hashSenha, cargoUsuarioCriado))
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise

def verificaTentativas(maq, cursor, conexao):
    cursor.execute("""
    SELECT identificador, tentativas, bloqueadoAte FROM tentativasLogin
    WHERE identificador = ?
    """, (maq,))
    resultado = cursor.fetchone()
    if resultado is not None and resultado[2] is not None and resultado[2] <= dt.datetime.now():
        cursor.execute("""
        DELETE FROM tentativasLogin
        WHERE identificador = ?
        """, (maq,))
        conexao.commit()
        return None
    return resultado


def registraTentativa(identificador, tentativas, cursor, conexao, login=0, bloqueadoAte=None,logou=False):
    try:
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
            conexao.commit()
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
    except Exception:
        conexao.rollback()
        raise