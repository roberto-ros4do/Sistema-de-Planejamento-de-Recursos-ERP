import sqlite3
import datetime as dt
import bcrypt
import pytest

from servicos.login import (
    verificaLogin,
    verificaLoginRepetido,
    cadastraLogin,
    verificaTentativas,
    registraTentativa
)
from servicos.erros import ConflitoError, CredenciaisInvalidasError, BloqueioError

MAQUINA = 'MAQUINA_TESTE'

#o Python 3.12+ avisa que o conversor padrão de datas do sqlite está depreciado;
#o aviso não afeta o resultado dos testes, então é ignorado apenas neste arquivo
pytestmark = pytest.mark.filterwarnings(
    "ignore:The default (datetime adapter|timestamp converter) is deprecated:DeprecationWarning"
)


@pytest.fixture
def banco():
    #detect_types faz o sqlite devolver bloqueadoAte como datetime (e não texto),
    #necessário porque o serviço compara bloqueadoAte com dt.datetime.now()
    conexao = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE usuario(
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            login TEXT NOT NULL UNIQUE,
            senha BLOB NOT NULL,
            cargo TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE tentativasLogin(
            identificador TEXT PRIMARY KEY,
            tentativas INTEGER NOT NULL,
            bloqueadoAte TIMESTAMP DEFAULT NULL
        )
    """)

    senha = bcrypt.hashpw('senha123'.encode('utf-8'), bcrypt.gensalt())

    cursor.execute("""
        INSERT INTO usuario (nome, login, senha, cargo)
        VALUES (?, ?, ?, ?)
    """, ('Roberto', 'roberto', senha, 'ADMINISTRADOR'))

    conexao.commit()

    yield conexao, cursor

    conexao.close()


def buscarTentativa(cursor, identificador=MAQUINA):
    cursor.execute("""
        SELECT identificador, tentativas, bloqueadoAte FROM tentativasLogin
        WHERE identificador = ?
    """, (identificador,))
    return cursor.fetchone()


def errarLogin(cursor, conexao, vezes):
    for _ in range(vezes):
        with pytest.raises(ValueError):
            verificaLogin(cursor, 'roberto', 'senhaErrada', conexao, MAQUINA)


# ---------------------------------------------------------------------------
# cadastraLogin
# ---------------------------------------------------------------------------

def testCadastraLoginValido(banco):
    conexao, cursor = banco

    cadastraLogin(
        cursor, conexao,
        'Maria', 'maria', 'senha456',
        'ADMINISTRADOR', 'FINANCEIRO'
    )

    cursor.execute("""
        SELECT nome, login, senha, cargo FROM usuario
        WHERE login = 'maria'
    """)
    usuario = cursor.fetchone()

    assert usuario[0] == 'Maria'
    assert usuario[1] == 'maria'
    assert usuario[3] == 'FINANCEIRO'


def testCadastraLoginSenhaCriptografada(banco):
    conexao, cursor = banco

    cadastraLogin(
        cursor, conexao,
        'Maria', 'maria', 'senha456',
        'ADMINISTRADOR', 'FINANCEIRO'
    )

    cursor.execute("SELECT senha FROM usuario WHERE login = 'maria'")
    senha = cursor.fetchone()[0]

    assert senha != 'senha456'
    assert senha != b'senha456'
    assert bcrypt.checkpw('senha456'.encode('utf-8'), senha)


@pytest.mark.parametrize(
    "cargoUsuarioCriado",
    ['ADMINISTRADOR', 'GERENTE', 'ESTOQUISTA', 'FINANCEIRO', 'CONSULTA']
)
def testCadastraLoginTodosCargosValidos(banco, cargoUsuarioCriado):
    conexao, cursor = banco

    cadastraLogin(
        cursor, conexao,
        'Maria', 'maria', 'senha456',
        'ADMINISTRADOR', cargoUsuarioCriado
    )

    cursor.execute("SELECT cargo FROM usuario WHERE login = 'maria'")
    cargo = cursor.fetchone()[0]

    assert cargo == cargoUsuarioCriado


@pytest.mark.parametrize(
    "cargo",
    ['GERENTE', 'ESTOQUISTA', 'FINANCEIRO', 'CONSULTA', 'CARGO INVÁLIDO', '']
    #apenas ADMINISTRADOR possui a permissão CADASTRAR_USUARIO
)
def testCadastraLoginSemPermissao(banco, cargo):
    conexao, cursor = banco

    with pytest.raises(
        PermissionError,
        match='USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO'
    ):
        cadastraLogin(
            cursor, conexao,
            'Maria', 'maria', 'senha456',
            cargo, 'FINANCEIRO'
        )

    assert verificaLoginRepetido('maria', cursor) is False


def testCadastraLoginRepetido(banco):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='LOGIN JÁ EXISTE NO SISTEMA!'):
        cadastraLogin(
            cursor, conexao,
            'Outro Roberto', 'roberto', 'senha456',
            'ADMINISTRADOR', 'CONSULTA'
        )

    cursor.execute("SELECT COUNT(*) FROM usuario")
    usuarios = cursor.fetchone()[0]
    assert usuarios == 1


def testCadastraLoginRepetidoVerificadoAntesDaSenha(banco):
    conexao, cursor = banco

    #login repetido E senha curta: o serviço valida o login primeiro
    with pytest.raises(ValueError, match='LOGIN JÁ EXISTE NO SISTEMA!'):
        cadastraLogin(
            cursor, conexao,
            'Outro Roberto', 'roberto', '123',
            'ADMINISTRADOR', 'CONSULTA'
        )


@pytest.mark.parametrize("senha", ['', '1', '12345', 'abcde'])
def testCadastraLoginSenhaCurta(banco, senha):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='INSIRA UMA SENHA MAIOR QUE 5 CARACTERES!'):
        cadastraLogin(
            cursor, conexao,
            'Maria', 'maria', senha,
            'ADMINISTRADOR', 'FINANCEIRO'
        )

    assert verificaLoginRepetido('maria', cursor) is False


def testCadastraLoginSenhaNoLimiteMinimo(banco):
    conexao, cursor = banco

    #6 caracteres é o menor tamanho aceito
    cadastraLogin(
        cursor, conexao,
        'Maria', 'maria', '123456',
        'ADMINISTRADOR', 'FINANCEIRO'
    )

    assert verificaLoginRepetido('maria', cursor) is True


@pytest.mark.parametrize(
    "cargoUsuarioCriado",
    ['CARGO INVÁLIDO', '', 'administrador', 'VENDEDOR']
)
def testCadastraLoginCargoInvalido(banco, cargoUsuarioCriado):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='CAMPO DE CARGO ACEITA APENAS CARGOS EXISTENTES!'):
        cadastraLogin(
            cursor, conexao,
            'Maria', 'maria', 'senha456',
            'ADMINISTRADOR', cargoUsuarioCriado
        )

    assert verificaLoginRepetido('maria', cursor) is False


def testCadastraLoginPermiteLogar(banco):
    conexao, cursor = banco

    cadastraLogin(
        cursor, conexao,
        'Maria', 'maria', 'senha456',
        'ADMINISTRADOR', 'ESTOQUISTA'
    )

    nome, logou, cargo = verificaLogin(cursor, 'maria', 'senha456', conexao, MAQUINA)

    assert nome == 'Maria'
    assert logou is True
    assert cargo == 'ESTOQUISTA'


# ---------------------------------------------------------------------------
# verificaLoginRepetido
# ---------------------------------------------------------------------------

def testVerificaLoginRepetidoExiste(banco):
    conexao, cursor = banco

    assert verificaLoginRepetido('roberto', cursor) is True


@pytest.mark.parametrize("login", ['maria', '', 'ROBERTO', 'roberto '])
def testVerificaLoginRepetidoNaoExiste(banco, login):
    conexao, cursor = banco

    assert verificaLoginRepetido(login, cursor) is False


# ---------------------------------------------------------------------------
# verificaTentativas
# ---------------------------------------------------------------------------

def testVerificaTentativasSemRegistro(banco):
    conexao, cursor = banco

    assert verificaTentativas(MAQUINA, cursor, conexao) is None


def testVerificaTentativasSemBloqueio(banco):
    conexao, cursor = banco

    cursor.execute("""
        INSERT INTO tentativasLogin (identificador, tentativas)
        VALUES (?, ?)
    """, (MAQUINA, 2))
    conexao.commit()

    resultado = verificaTentativas(MAQUINA, cursor, conexao)

    assert resultado == (MAQUINA, 2, None)


def testVerificaTentativasBloqueioAtivo(banco):
    conexao, cursor = banco

    bloqueadoAte = dt.datetime.now() + dt.timedelta(minutes=5)
    cursor.execute("""
        INSERT INTO tentativasLogin (identificador, tentativas, bloqueadoAte)
        VALUES (?, ?, ?)
    """, (MAQUINA, 0, bloqueadoAte))
    conexao.commit()

    resultado = verificaTentativas(MAQUINA, cursor, conexao)

    assert resultado[0] == MAQUINA
    assert resultado[1] == 0
    assert resultado[2] == bloqueadoAte


def testVerificaTentativasBloqueioExpiradoRemoveRegistro(banco):
    conexao, cursor = banco

    bloqueadoAte = dt.datetime.now() - dt.timedelta(minutes=1)
    cursor.execute("""
        INSERT INTO tentativasLogin (identificador, tentativas, bloqueadoAte)
        VALUES (?, ?, ?)
    """, (MAQUINA, 0, bloqueadoAte))
    conexao.commit()

    resultado = verificaTentativas(MAQUINA, cursor, conexao)

    assert resultado is None
    assert buscarTentativa(cursor) is None


def testVerificaTentativasOutraMaquina(banco):
    conexao, cursor = banco

    cursor.execute("""
        INSERT INTO tentativasLogin (identificador, tentativas)
        VALUES (?, ?)
    """, ('OUTRA_MAQUINA', 1))
    conexao.commit()

    assert verificaTentativas(MAQUINA, cursor, conexao) is None


# ---------------------------------------------------------------------------
# registraTentativa
# ---------------------------------------------------------------------------

def testRegistraPrimeiraTentativaInsere(banco):
    conexao, cursor = banco

    registraTentativa(MAQUINA, 3, cursor, conexao)

    assert buscarTentativa(cursor) == (MAQUINA, 3, None)


@pytest.mark.parametrize("tentativas", [2, 1])
def testRegistraTentativaAtualiza(banco, tentativas):
    conexao, cursor = banco

    registraTentativa(MAQUINA, 3, cursor, conexao)
    registraTentativa(MAQUINA, tentativas, cursor, conexao)

    assert buscarTentativa(cursor) == (MAQUINA, tentativas, None)


def testRegistraTentativaComBloqueio(banco):
    conexao, cursor = banco

    bloqueadoAte = dt.datetime.now() + dt.timedelta(minutes=5)
    registraTentativa(MAQUINA, 3, cursor, conexao)
    registraTentativa(MAQUINA, 0, cursor, conexao, bloqueadoAte=bloqueadoAte)

    assert buscarTentativa(cursor) == (MAQUINA, 0, bloqueadoAte)


def testRegistraTentativaLogouRetornaCargoELimpa(banco):
    conexao, cursor = banco

    registraTentativa(MAQUINA, 3, cursor, conexao)

    cargo = registraTentativa(
        MAQUINA, 4, cursor, conexao,
        login='roberto', logou=True
    )

    assert cargo == 'ADMINISTRADOR'
    assert buscarTentativa(cursor) is None


def testRegistraTentativaLogouLoginInexistente(banco):
    conexao, cursor = banco

    #sem usuário, fetchone() retorna None e o [0] gera TypeError (com rollback)
    with pytest.raises(TypeError):
        registraTentativa(
            MAQUINA, 4, cursor, conexao,
            login='inexistente', logou=True
        )


# ---------------------------------------------------------------------------
# verificaLogin
# ---------------------------------------------------------------------------

def testVerificaLoginValido(banco):
    conexao, cursor = banco

    nome, logou, cargo = verificaLogin(cursor, 'roberto', 'senha123', conexao, MAQUINA)

    assert nome == 'Roberto'
    assert logou is True
    assert cargo == 'ADMINISTRADOR'
    assert buscarTentativa(cursor) is None


@pytest.mark.parametrize(
    "login, senha",
    [
        ('roberto', 'senhaErrada'),
        ('roberto', 'SENHA123'),
        ('roberto', ''),
        ('inexistente', 'senha123'),
        ('ROBERTO', 'senha123'),
        ('', ''),
    ]
    #senha errada e usuário inexistente devem gerar a MESMA mensagem
)
def testVerificaLoginInvalido(banco, login, senha):
    conexao, cursor = banco

    with pytest.raises(
        ValueError,
        match='USUÁRIO OU SENHA INVÁLIDOS! VOCÊ POSSUI 3 TENTATIVAS RESTANTES'
    ):
        verificaLogin(cursor, login, senha, conexao, MAQUINA)

    assert buscarTentativa(cursor) == (MAQUINA, 3, None)


@pytest.mark.parametrize(
    "erros, restantes",
    [
        (0, 3),
        (1, 2),
        (2, 1),
    ]
)
def testVerificaLoginContagemDeTentativas(banco, erros, restantes):
    conexao, cursor = banco

    errarLogin(cursor, conexao, erros)

    with pytest.raises(
        ValueError,
        match=f'USUÁRIO OU SENHA INVÁLIDOS! VOCÊ POSSUI {restantes} TENTATIVAS RESTANTES'
    ):
        verificaLogin(cursor, 'roberto', 'senhaErrada', conexao, MAQUINA)

    assert buscarTentativa(cursor) == (MAQUINA, restantes, None)


def testVerificaLoginEsgotaTentativas(banco):
    conexao, cursor = banco

    errarLogin(cursor, conexao, 3)

    antes = dt.datetime.now()
    with pytest.raises(
        ValueError,
        match='VOCÊ ESGOTOU SUAS TENTATIVAS, TENTE NOVAMENTE EM 5 MINUTOS!'
    ):
        verificaLogin(cursor, 'roberto', 'senhaErrada', conexao, MAQUINA)
    depois = dt.datetime.now()

    tentativa = buscarTentativa(cursor)

    assert tentativa[1] == 0
    assert antes + dt.timedelta(minutes=5) <= tentativa[2] <= depois + dt.timedelta(minutes=5)


def testVerificaLoginBloqueadoMesmoComSenhaCorreta(banco):
    conexao, cursor = banco

    errarLogin(cursor, conexao, 4)

    with pytest.raises(
        ValueError,
        match='VOCÊ ACABOU COM SUAS TENTATIVAS! TENTE NOVAMENTE MAIS TARDE!'
    ):
        verificaLogin(cursor, 'roberto', 'senha123', conexao, MAQUINA)


def testVerificaLoginBloqueadoNaoAlteraRegistro(banco):
    conexao, cursor = banco

    errarLogin(cursor, conexao, 4)
    registroAntes = buscarTentativa(cursor)

    with pytest.raises(
        ValueError,
        match='VOCÊ ACABOU COM SUAS TENTATIVAS! TENTE NOVAMENTE MAIS TARDE!'
    ):
        verificaLogin(cursor, 'roberto', 'senhaErrada', conexao, MAQUINA)

    assert buscarTentativa(cursor) == registroAntes


def testVerificaLoginAposBloqueioExpirado(banco):
    conexao, cursor = banco

    errarLogin(cursor, conexao, 4)

    #simula a passagem dos 5 minutos
    cursor.execute("""
        UPDATE tentativasLogin
        SET bloqueadoAte = ?
        WHERE identificador = ?
    """, (dt.datetime.now() - dt.timedelta(seconds=1), MAQUINA))
    conexao.commit()

    nome, logou, cargo = verificaLogin(cursor, 'roberto', 'senha123', conexao, MAQUINA)

    assert nome == 'Roberto'
    assert logou is True
    assert cargo == 'ADMINISTRADOR'
    assert buscarTentativa(cursor) is None


def testVerificaLoginErroAposBloqueioExpiradoReiniciaContagem(banco):
    conexao, cursor = banco

    errarLogin(cursor, conexao, 4)

    cursor.execute("""
        UPDATE tentativasLogin
        SET bloqueadoAte = ?
        WHERE identificador = ?
    """, (dt.datetime.now() - dt.timedelta(seconds=1), MAQUINA))
    conexao.commit()

    with pytest.raises(
        ValueError,
        match='USUÁRIO OU SENHA INVÁLIDOS! VOCÊ POSSUI 3 TENTATIVAS RESTANTES'
    ):
        verificaLogin(cursor, 'roberto', 'senhaErrada', conexao, MAQUINA)

    assert buscarTentativa(cursor) == (MAQUINA, 3, None)


def testVerificaLoginSucessoZeraTentativas(banco):
    conexao, cursor = banco

    errarLogin(cursor, conexao, 2)
    assert buscarTentativa(cursor) == (MAQUINA, 2, None)

    verificaLogin(cursor, 'roberto', 'senha123', conexao, MAQUINA)

    assert buscarTentativa(cursor) is None

    #depois do sucesso a contagem recomeça do início
    with pytest.raises(
        ValueError,
        match='USUÁRIO OU SENHA INVÁLIDOS! VOCÊ POSSUI 3 TENTATIVAS RESTANTES'
    ):
        verificaLogin(cursor, 'roberto', 'senhaErrada', conexao, MAQUINA)


def testVerificaLoginBloqueioPorMaquina(banco):
    conexao, cursor = banco

    errarLogin(cursor, conexao, 4)

    #outra máquina não é afetada pelo bloqueio
    nome, logou, cargo = verificaLogin(cursor, 'roberto', 'senha123', conexao, 'OUTRA_MAQUINA')

    assert logou is True
    assert buscarTentativa(cursor)[1] == 0
    assert buscarTentativa(cursor, 'OUTRA_MAQUINA') is None


def testVerificaLoginTentativasContamParaQualquerUsuario(banco):
    conexao, cursor = banco

    cadastraLogin(
        cursor, conexao,
        'Maria', 'maria', 'senha456',
        'ADMINISTRADOR', 'CONSULTA'
    )

    #o controle é por máquina, então erros com logins diferentes somam
    with pytest.raises(ValueError, match='3 TENTATIVAS RESTANTES'):
        verificaLogin(cursor, 'roberto', 'senhaErrada', conexao, MAQUINA)
    with pytest.raises(ValueError, match='2 TENTATIVAS RESTANTES'):
        verificaLogin(cursor, 'maria', 'senhaErrada', conexao, MAQUINA)
    with pytest.raises(ValueError, match='1 TENTATIVAS RESTANTES'):
        verificaLogin(cursor, 'inexistente', 'qualquer', conexao, MAQUINA)

# ---------------------------------------------------------------------------
# Identificador recebido por parâmetro
# ---------------------------------------------------------------------------

def testVerificaLoginRegistraIdentificadorRecebido(banco):
    conexao, cursor = banco

    #na API o identificador será o IP de quem fez a requisição
    with pytest.raises(ValueError, match='3 TENTATIVAS RESTANTES'):
        verificaLogin(cursor, 'roberto', 'senhaErrada', conexao, '192.168.0.10')

    assert buscarTentativa(cursor, '192.168.0.10') == ('192.168.0.10', 3, None)
    assert buscarTentativa(cursor) is None


def testVerificaLoginIdentificadoresTemContagensSeparadas(banco):
    conexao, cursor = banco

    with pytest.raises(ValueError, match='3 TENTATIVAS RESTANTES'):
        verificaLogin(cursor, 'roberto', 'senhaErrada', conexao, '192.168.0.10')
    with pytest.raises(ValueError, match='2 TENTATIVAS RESTANTES'):
        verificaLogin(cursor, 'roberto', 'senhaErrada', conexao, '192.168.0.10')

    #outro identificador começa a contagem do início
    with pytest.raises(ValueError, match='3 TENTATIVAS RESTANTES'):
        verificaLogin(cursor, 'roberto', 'senhaErrada', conexao, '192.168.0.20')

    assert buscarTentativa(cursor, '192.168.0.10')[1] == 2
    assert buscarTentativa(cursor, '192.168.0.20')[1] == 3


# ---------------------------------------------------------------------------
# Exceções próprias
# ---------------------------------------------------------------------------

def testCadastraLoginRepetidoLancaConflito(banco):
    conexao, cursor = banco

    with pytest.raises(ConflitoError, match='LOGIN JÁ EXISTE NO SISTEMA!'):
        cadastraLogin(
            cursor, conexao,
            'Outro Roberto', 'roberto', 'senha456',
            'ADMINISTRADOR', 'CONSULTA'
        )


@pytest.mark.parametrize(
    "senha, cargoUsuarioCriado",
    [
        ('123', 'FINANCEIRO'),
        ('senha456', 'CARGO INVÁLIDO'),
    ]
    #senha curta e cargo inexistente continuam sendo 400
)
def testCadastraLoginValidacaoContinuaValueError(banco, senha, cargoUsuarioCriado):
    conexao, cursor = banco

    with pytest.raises(ValueError) as erro:
        cadastraLogin(
            cursor, conexao,
            'Maria', 'maria', senha,
            'ADMINISTRADOR', cargoUsuarioCriado
        )

    assert type(erro.value) is ValueError


@pytest.mark.parametrize(
    "login, senha",
    [
        ('roberto', 'senhaErrada'),
        ('inexistente', 'senha123'),
    ]
)
def testVerificaLoginInvalidoLancaCredenciaisInvalidas(banco, login, senha):
    conexao, cursor = banco

    with pytest.raises(CredenciaisInvalidasError, match='USUÁRIO OU SENHA INVÁLIDOS!'):
        verificaLogin(cursor, login, senha, conexao, MAQUINA)


def testVerificaLoginEsgotaTentativasLancaBloqueio(banco):
    conexao, cursor = banco

    errarLogin(cursor, conexao, 3)

    with pytest.raises(BloqueioError, match='VOCÊ ESGOTOU SUAS TENTATIVAS'):
        verificaLogin(cursor, 'roberto', 'senhaErrada', conexao, MAQUINA)


def testVerificaLoginBloqueadoLancaBloqueio(banco):
    conexao, cursor = banco

    errarLogin(cursor, conexao, 4)

    with pytest.raises(BloqueioError, match='VOCÊ ACABOU COM SUAS TENTATIVAS'):
        verificaLogin(cursor, 'roberto', 'senha123', conexao, MAQUINA)