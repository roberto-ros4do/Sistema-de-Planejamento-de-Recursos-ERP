#exceções próprias do sistema
#todas herdam de ValueError, então quem já trata ValueError continua funcionando
#a API usa a classe de cada uma para escolher o status HTTP da resposta

class NaoEncontradoError(ValueError): #404 - o item pedido não existe
    pass

class ConflitoError(ValueError): #409 - conflita com algo que já existe
    pass

class CredenciaisInvalidasError(ValueError): #401 - login ou senha incorretos
    pass

class BloqueioError(ValueError): #429 - tentativas de login esgotadas
    pass