from servicos import produtos as p
from servicos import movimentacoes as m
from servicos import relatorios as r
from servicos import saldo as s
from servicos import login as l
from servicos import filtro as f

def verificaCargo(cargo):
    from servicos import permissoes as pe
    TELAS = {
    'CADASTRAR_PRODUTOS': {
        'nome': 'CADASTRAR PRODUTOS',
        'tela': telaCadastroProduto
    },

    'LISTAGEM_DE_PRODUTOS': {
        'nome': 'LISTAGEM DE PRODUTOS',
        'tela': telaListagemProdutos
    },

    'REGISTRAR_MOVIMENTACOES': {
        'nome': 'REGISTRAR MOVIMENTAÇÕES',
        'tela': telaRegMov
    },

    'HISTORICO_DE_MOVIMENTACOES': {
        'nome': 'HISTÓRICO DE MOVIMENTAÇÕES',
        'tela': telaHistMov
    },

    'EXPORTAR_RELATORIO_CSV': {
        'nome': 'EXPORTAR RELATÓRIO CSV',
        'tela': telaRelatorio
    },

    'DELETAR_PRODUTO': {
        'nome': 'DELETAR PRODUTO',
        'tela': telaDeletar
    },

    'EDITAR_SALDO': {
        'nome': 'EDITAR SALDO',
        'tela': telaEditarSaldo
    },

    'HISTORICO_DE_TRANSACOES': {
        'nome': 'HISTÓRICO DE TRANSAÇÕES',
        'tela': telaHistSaldo
    },

    'CADASTRAR_USUARIO': {
        'nome': 'CADASTRAR USUÁRIO',
        'tela': telaCadastrarUsuario
    },

    'SAIR_DO_SISTEMA': {
        'nome': 'SAIR DO SISTEMA',
        'tela': None
    }
}

    menu = []
    telas = []
    for acao in TELAS:
        if pe.podeExecutar(cargo, acao):
            menu.append(TELAS[acao]['nome'])
            if TELAS[acao]['tela'] is not None:
                telas.append(TELAS[acao]['tela'])
    return menu, telas

def telaLogin(cursor, conexao): #OK
    try:
        login = input('Insira seu login: ')
        senha = input('Insira sua senha')
        nome, logou, cargo = l.verificaLogin(cursor, login, senha, conexao)
        return logou, cargo, nome
    except (ValueError, PermissionError) as erro:
        print(f'ERRO: {erro}')
        return False, None, None


def telaCadastrarUsuario(cursor, conexao, cargo=None, nome=None): #OK
    try:
        nomeUsuario = input('Insira nome: ')
        login = input('Insira login: ')
        senha = input('Insira senha: ')
        print('[1] ADMINISTRADOR')
        print('[2] GERENTE')
        print('[3] ESTOQUISTA')
        print('[4] FINANCEIRO')
        print('[5] CONSULTA')
        cargoUsuarioCriado = input('Qual cargo irá desempenhar? ') #adicionar verificação se cargo existe
        match cargoUsuarioCriado:
            case '1' :
                cargoUsuarioCriado = 'ADMINISTRADOR'
            case '2':
                cargoUsuarioCriado = 'GERENTE'
            case '3':
                cargoUsuarioCriado = 'ESTOQUISTA'
            case '4':
                cargoUsuarioCriado = 'FINANCEIRO'
            case '5':
                cargoUsuarioCriado = 'CONSULTA'
            case _:
                cargoUsuarioCriado = ''
        l.cadastraLogin(cursor, conexao, nomeUsuario, login, senha, cargo, cargoUsuarioCriado)
        print('USUÁRIO CADASTRADO! ')
        return
    except (ValueError, PermissionError) as erro:
        print(f'ERRO: {erro}')

def telaCadastroProduto(cursor, conexao, cargo=None, nome=None): #OK
    try:
        n = input('Insira o nome do produto: ')
        q = input('Insira a disponibilidade no estoque: ')
        invest = input('Insira o valor do investimento? ')
        v = input('Insira o valor que será cobrado pelo produto: ')
        p.cadastroProduto(n, q, v, invest, cursor, conexao, nome, cargo)
        return
    except (ValueError, PermissionError) as erro:
        print(f'ERRO: {erro}')



def listarProdutos(produtos):
    for produto in produtos:
        print(f"=========={produto[1]}===========")
        print(f"ID DO PRODUTO: [{produto[0]}]")
        print(f"DISPONIBILIDADE NO ESTOQUE: {produto[3]}")
        print(f"PREÇO: R$ {(produto[2])/100}")
        print(f'CRIADO EM {produto[4]} POR {produto[5]}')
        
def telaListagemProdutos(cursor, conexao, cargo=None, nome=None): #OK
    try:
        produtos = p.consultaProdutos(cursor)
        filtro = input('Deseja utilizar filtro? ')
        if filtro.lower() in ('s', 'sim'):
            n = input('Insira o nome(ENTER para pular): ') 
            quemCad = input('Insira quem cadastrou o produto(ENTER para pular): ')
            idProd = input('Insira o ID de algum produto(ENTER para pular): ')
            valorMin = input('Insira o valor mínimo(ENTER para pular): R$')
            valorMax = input('Insira o valor máximo(ENTER para pular): ')
            estoqMin = input('Insira a disponibilidade mínima(ENTER para pular): ')
            estoqMax = input('Insira a disponibilidade máxima(ENTER para pular): ')
            produtos = f.filtragemProdutos(valorMin, valorMax, estoqMin, estoqMax, cursor, quemCad=quemCad, n=n, id=idProd)
            listarProdutos(produtos)
            return
        else:
            listarProdutos(produtos)
            return
    except (ValueError, PermissionError) as erro:
        print(f'ERRO: {erro}')
        return


def telaDeletar(cursor, conexao, cargo=None, nome=None): #OK
        try:
            idProd = input('Insira o ID do produto que deseja deletar: ') 
            p.deletarProduto(idProd, cursor, conexao, nome, cargo)
            return
        except (ValueError, PermissionError) as erro:
            print(f'ERRO: {erro}')

def listarHistMov(historico):
    for mov in historico:
                print(f"=========={mov[0]}===========")
                print(f'REALIZADA EM {mov[4]} POR {mov[5]}')
                print(f"TIPO DE MOVIMENTAÇÃO: {mov[2]}")
                if mov[2]=='CADASTRO':
                    print(f'UNIDADES CADASTRADAS: {mov[3]}')
                if mov[2] == 'COMPRA' or mov[2] == 'DEVOLUÇÃO':
                    print(f"UNIDADES RECEBIDAS: {mov[3]}")
                elif mov[2] == 'VENDA' or mov[2] == 'PERCA' or mov[2] == 'TRANSFERÊNCIA':
                    print(f"UNIDADES DESFAZIDAS: {mov[3]}")

def telaHistMov(cursor, conexao, cargo=None, nome=None): #OK
    try:
        historico = m.consultaMov(cursor)
        filtro = input('Deseja utilizar filtro?')
        if filtro.lower() in ('s', 'sim'):
            n = input('Insira o nome(ENTER para pular): ')
            quemCad = input('Insira quem cadastrou o produto(ENTER para pular): ')
            idProd = input('Insira o ID de algum produto(ENTER para pular): ')
            unidMin = input("Insira a quantidade de unidades minímas envolvidas na movimentação(ENTER para pular): ")
            unidMax = input("Insira a quantidade de unidades minímas envolvidas na movimentação(ENTER para pular): ")
            valorMin = input("Insira o valor mínimo envolvido nas movimentações(ENTER para pular): ") 
            valorMax = input("Insira o valor mínimo envolvido nas movimentações(ENTER para pular): ")
            print('QUAL O TIPO DE OPERAÇÃO?')
            print('[1] COMPRA')
            print('[2] VENDA')
            print('[3] TRANSFERÊNCIA')
            print('[4] DEVOLUÇÃO')
            print('[5] PERCA')
            print('[6] CADASTRO')
            print('[7] DELETAÇÃO')
            mov = input('Qual opção escolhida?(ENTER para pular)')
            match mov:
                case "1":
                    mov = 'COMPRA'
                case "2":
                    mov = 'VENDA'
                case "3":
                    mov = "TRANSFERÊNCIA"
                case "4":
                    mov = "DEVOLUÇÃO"
                case "5":
                    mov = "PERCA"
                case "6":
                    mov = "CADASTRO"
                case "7":
                    mov = "DELETAÇÃO"
                case _:
                    mov = ''
            dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
            dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
            historico = f.filtragemMov(n, quemCad, idProd, unidMin, unidMax, valorMin, valorMax, dataInicial, dataUltima, cursor, mov)
            if not historico:
                print('NÃO HÁ MOVIMENTAÇÕES COM ESTAS ESPECIFICAÇÕES')
                return
            else:
                listarHistMov(historico)
                return
        else:
            listarHistMov(historico)
            return
    except (ValueError, PermissionError) as erro:
        print(f'ERRO: {erro}')

def telaEditarSaldo(cursor, conexao, cargo=None, nome=None): #OK
    saldo = s.verificarSaldo(cursor)
    print('[1] APLICAÇÃO ')
    print('[2] RETIRADA')
    try:
        op = input('Qual operação deseja realizar? ')
        match op:
            case '1':
                op = 'ENTRADA'
                ap = input('Quanto deseja adicionar: R$')
                s.editarSaldo(op, ap, saldo, cursor, conexao, nome, cargo)
                return
            case '2':
                op = 'RETIRADA'
                ret = input('Quanto deseja retirar: R$')
                s.editarSaldo(op, ret, saldo, cursor, conexao, nome, cargo)
                return
            case _:
                op = ''
    except (ValueError, PermissionError) as erro:
        print(f'ERRO: {erro}')
        return

def telaRegMov(cursor, conexao, cargo=None, nome=None): #OK
    try:
        print('[1] COMPRA')
        print('[2] VENDA')
        print('[3] TRANSFERÊNCIA')
        print('[4] DEVOLUÇÃO')
        print('[5] PERCA')
        op = input('Qual a movimentação realizada? ')
        match op:
            case '1':
                tip = 'COMPRA'
                idProduto = input('Insira o ID do produto: ')
                q = input('Quantas unidades foram recebidas? ')
                invest = input('Insira o valor do investimento: ')
                m.registroMov(idProduto, tip, q, cursor, conexao, nome, cargo, invest)
                return
            case '2':
                tip = 'VENDA'
                idProduto = int(input('Insira o ID do produto: '))
                q = input('Quantas unidades foram vendidas? ')
                invest = input('insira o valor da venda: ')
                m.registroMov(idProduto, tip, q, cursor, conexao, nome, cargo, invest)
                return
            case '3':
                tip = 'TRANSFERÊNCIA'
                idProduto = input('Insira o ID do produto: ')
                q = input('Quantas unidades foram transferidas? ')
                invest = input('Quanto custou o transporte? ')
                m.registroMov(idProduto, tip, q, cursor, conexao, nome, cargo, invest)
                return
            case '4':
                tip = 'DEVOLUÇÃO'
                idProduto = input('Insira o ID do produto: ')
                q = input('Quantas unidades foram devolvidas? ')
                invest = input('Qual o valor do reembolso? ')
                m.registroMov(idProduto, tip, q, cursor, conexao, nome, cargo, invest)
                return
            case '5':
                tip = 'PERCA'
                idProduto = input('Insira o ID do produto: ')
                q = input('Quantas unidades foram perdidas? ')
                m.registroMov(idProduto, tip, q, cursor, conexao, nome, cargo)
                return
            case _:
                op = ''
    except (ValueError, PermissionError) as erro:
        print(f'ERRO: {erro}')    

def telaRelatorio(cursor, conexao, cargo=None, nome=None):
        try:
            print('[1] PRODUTOS')
            print('[2] ATIVIDADE')
            print('[3] EXTRATO')
            print('[4] ESTOQUE')
            rel = input('Qual relatório deseja gerar? ')
            match rel:
                case '1':
                    nomeArquivo = 'produtos' 
                    filtro = input('Deseja utilizar filtro? ')
                    if filtro.lower() in ('s', 'sim'):
                        valorMin = input('Insira o valor mínimo(ENTER para pular): R$') 
                        valorMax = input('Insira o valor máximo(ENTER para pular): ')
                        estoqMin = input('Insira a disponibilidade mínima(ENTER para pular): ')
                        estoqMax = input('Insira a disponibilidade máxima(ENTER para pular): ')
                        dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                        dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                        funcao = 'REL'
                        query, parametros = f.filtragemProdutos(valorMin, valorMax, estoqMin, estoqMax, cursor, dataInicial=dataInicial, dataUltima=dataUltima, f=funcao)
                        df = r.lerDados(rel, conexao, query=query, parametros=parametros)
                        r.gerarRel(df, nomeArquivo, cargo)
                        print('RELATÓRIO EXPORTADO COM SUCESSO!')
                    else:
                        df = r.lerDados(rel, conexao)
                        r.gerarRel(df, nomeArquivo, cargo)
                        print('RELATÓRIO EXPORTADO COM SUCESSO!')
                        return
                case '2':
                    nomeArquivo = 'atividade'
                    filtro = input('Deseja utilizar filtro?')
                    if filtro.lower() in ('s', 'sim'):
                        quemCad = input('Insira quem realizou (ENTER para pular): ')
                        unidMin = input("Insira a quantidade de unidades minímas envolvidas na movimentação(ENTER para pular): ")
                        unidMax = input("Insira a quantidade de unidades minímas envolvidas na movimentação(ENTER para pular): ")
                        valorMin = input("Insira o valor mínimo envolvido nas movimentações(ENTER para pular): ")
                        valorMax = input("Insira o valor mínimo envolvido nas movimentações(ENTER para pular): ")

                        print('Qual o tipo de operação!(ENTER para pular!)')
                        print('[1] COMPRA')
                        print('[2] VENDA')
                        print('[3] TRANSFERÊNCIA')
                        print('[4] DEVOLUÇÃO')
                        print('[5] PERCA')
                        print('[6] CADASTRO')
                        print('[7] DELETAÇÃO')
                        mov = input('Qual a movimentação realizada? ')
                        match mov:
                            case "1":
                                mov = "COMPRA"
                            case "2":
                                mov = "VENDA"
                            case "3":
                                mov = "TRANSFERÊNCIA"
                            case "4":  
                                mov = "DEVOLUÇÃO" 
                            case "5":
                                mov = "PERCA"
                            case "6":
                                mov = "CADASTRO"
                            case "7":
                                mov = "DELETAÇÃO"
                            case _:
                                mov = ''
                        dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                        dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                        
                        query, parametros = f.filtragemMovRel(quemCad, unidMin, unidMax, valorMin, valorMax, dataInicial, dataUltima, cursor, mov)
                        df = r.lerDados(rel, conexao, query=query, parametros=parametros)
                        r.gerarRel(df, nomeArquivo, cargo)
                        print('RELATÓRIO EXPORTADO COM SUCESSO!')
                        return
                    else:
                        df = r.lerDados(rel, conexao)
                        r.gerarRel(df, nomeArquivo, cargo)
                        print('RELATÓRIO EXPORTADO COM SUCESSO!')
                        return
                case '3':
                    nomeArquivo = 'extrato'
                    filtro = input('Deseja utilizar filtro? ')
                    if filtro.lower() in ('s', 'sim'):
                            quemCad = input('Insira quem realizou a modificação(ENTER para pular): ')
                            print('Qual o tipo de operação!(ENTER para pular!)')
                            print('[1] ENTRADA')
                            print('[2] SAÍDA')
                            tip = input('Qual o tipo de operação? ')
                            match tip:
                                case "1":
                                    tip = "ENTRADA"
                                case "2":
                                    tip = "SAÍDA"
                                case _:
                                    tip = ""
                            valorMin = input('Insira o valor mínimo(ENTER para pular): R$')
                            
                            valorMax = input('Insira o valor máximo(ENTER para pular): R$')
                            dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                            dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')

                            funcao = 'REL'
                            query, parametros = f.filtragemSaldo(quemCad, tip, valorMin, valorMax,  dataInicial, dataUltima, cursor, f=funcao)
                            df = r.lerDados(rel, conexao, query=query, parametros=parametros)
                            r.gerarRel(df, nomeArquivo, cargo)
                            print('RELATÓRIO EXPORTADO COM SUCESSO!')
                            return
                    else:
                        df = r.lerDados(rel, conexao)
                        r.gerarRel(df, nomeArquivo, cargo)
                        print('RELATÓRIO EXPORTADO COM SUCESSO!')
                        return

                case '4':
                    nomeArquivo = 'estoque'
                    filtro = input('Deseja utilizar filtro? ')
                    if filtro.lower() in ('s', 'sim'):
                        quemCad = input('Insira quem cadastrou o produto(ENTER para pular): ')
                        valorMin = input('Insira o valor mínimo(ENTER para pular): R$')
                        valorMax = input('Insira o valor máximo(ENTER para pular): ')
                        estoqMin = input('Insira a disponibilidade mínima(ENTER para pular): ')
                        estoqMax = input('Insira a disponibilidade máxima(ENTER para pular): ')
                        dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
                        dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ')
                        funcao = 'REL'
                        estoq = True
                        query, parametros = f.filtragemProdutos(valorMin, valorMax, estoqMin, estoqMax, cursor, dataInicial=dataInicial, dataUltima=dataUltima, quemCad=quemCad, f=funcao, estoq=estoq)
                        df = r.lerDados(rel, conexao, query=query, parametros=parametros)
                        r.gerarRel(df, nomeArquivo, cargo)
                        print('RELATÓRIO EXPORTADO COM SUCESSO!')
                        return
                    else:
                        df = r.lerDados(rel, conexao)
                        r.gerarRel(df, nomeArquivo, cargo)
                        print('RELATÓRIO EXPORTADO COM SUCESSO!')
                        return
                case _:
                    rel = ''
        except (ValueError, PermissionError) as erro:
            print(f'ERRO: {erro}')
    

def listarHistSaldo(historico):
    for mov in historico:
            print(f"=====================")
            print(f"{mov[1]} DE R${(mov[0])/100}")
            print(f'REALIZADA EM {mov[3]} AS {mov[4]} por {mov[2]}')
                

def telaHistSaldo(cursor, conexao, cargo=None, nome=None): 
    try:
        historico = s.consultaHistSaldo(cursor)
        filtro = input('Deseja utilizar filtro?')
        if filtro.lower() in ('s', 'sim'):
            quemCad = input('Insira quem realizou a modificação(ENTER para pular): ')
            print('Qual o tipo de operação!(ENTER para pular!)')
            print('[1] ENTRADA')
            print('[2] SAÍDA')
            tip = input('Qual o tipo de operação? ')
            match tip:
                case "1":
                    tip = "ENTRADA"
                case "2":
                    tip = "SAÍDA"
                case "":
                    tip = ""
                case _:
                    tip = ''
            valorMin = input('Insira o valor mínimo(ENTER para pular): R$')
            valorMax = input('Insira o valor máximo(ENTER para pular): R$')
            dataInicial = ""
            dataUltima = ""
            dataInicial = input('Insira a data mais antiga(NO FORMATO AAAA/MM/DD): ')
            dataUltima = input('Insira a data mais recente(NO FORMATO AAAA/MM/DD): ') 
            historico = f.filtragemSaldo(quemCad, tip, valorMin, valorMax, dataInicial, dataUltima, cursor)
            if not historico:
                print('NÃO HÁ MOVIMENTAÇÕES COM ESTAS ESPECIFICAÇÕES')
                return
            else:
                listarHistSaldo(historico)
                return
        else:
            listarHistSaldo(historico)
            return
    except (ValueError, PermissionError) as erro:
        print(f'ERRO: {erro}')