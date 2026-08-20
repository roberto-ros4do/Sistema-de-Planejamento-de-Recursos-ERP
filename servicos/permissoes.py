
PERMISSOES = {
    'CADASTRAR_PRODUTOS': [
        'ADMINISTRADOR',
        'GERENTE',
        'ESTOQUISTA'],

    'LISTAGEM_DE_PRODUTOS': [
        'ADMINISTRADOR',
        'GERENTE',
        'ESTOQUISTA',
        'FINANCEIRO',
        'CONSULTA'],

    'REGISTRAR_MOVIMENTACOES': [
        'ADMINISTRADOR',
        'GERENTE',
        'ESTOQUISTA'],

    'HISTORICO_DE_MOVIMENTACOES': [
        'ADMINISTRADOR',
        'GERENTE',
        'ESTOQUISTA',
        'FINANCEIRO',
        'CONSULTA'],

    'EXPORTAR_RELATORIO_CSV': [
        'ADMINISTRADOR',
        'GERENTE',
        'ESTOQUISTA',
        'FINANCEIRO',
        'CONSULTA'],

    'DELETAR_PRODUTO': [
        'ADMINISTRADOR'],

    'EDITAR_SALDO': [
        'ADMINISTRADOR',
        'FINANCEIRO'],

    'HISTORICO_DE_TRANSACOES': [
        'ADMINISTRADOR',
        'CONSULTA'],

    'CADASTRAR_USUARIO': [
        'ADMINISTRADOR'],

    'SAIR_DO_SISTEMA': [
        'ADMINISTRADOR',
        'GERENTE',
        'ESTOQUISTA',
        'FINANCEIRO',
        'CONSULTA']
}

def podeExecutar(cargo, acao):
    if acao in PERMISSOES: #veridica se acao EXISTE nas permissões
        return cargo in PERMISSOES[acao] #se a ação existir verifica se o cargo está "dentro" da ação

    return False

def verificaCargo(cargo):
    from interface import terminal as i
    TELAS = {
    'CADASTRAR_PRODUTOS': {
        'nome': 'CADASTRAR PRODUTOS',
        'tela': i.telaCadastroProduto
    },

    'LISTAGEM_DE_PRODUTOS': {
        'nome': 'LISTAGEM DE PRODUTOS',
        'tela': i.telaListagemProdutos
    },

    'REGISTRAR_MOVIMENTACOES': {
        'nome': 'REGISTRAR MOVIMENTAÇÕES',
        'tela': i.telaRegMov
    },

    'HISTORICO_DE_MOVIMENTACOES': {
        'nome': 'HISTÓRICO DE MOVIMENTAÇÕES',
        'tela': i.telaHistMov
    },

    'EXPORTAR_RELATORIO_CSV': {
        'nome': 'EXPORTAR RELATÓRIO CSV',
        'tela': i.telaRelatorio
    },

    'DELETAR_PRODUTO': {
        'nome': 'DELETAR PRODUTO',
        'tela': i.telaDeletar
    },

    'EDITAR_SALDO': {
        'nome': 'EDITAR SALDO',
        'tela': i.telaEditarSaldo
    },

    'HISTORICO_DE_TRANSACOES': {
        'nome': 'HISTÓRICO DE TRANSAÇÕES',
        'tela': i.telaHistSaldo
    },

    'CADASTRAR_USUARIO': {
        'nome': 'CADASTRAR USUÁRIO',
        'tela': i.telaCadastrarUsuario
    },

    'SAIR_DO_SISTEMA': {
        'nome': 'SAIR DO SISTEMA',
        'tela': None
    }
}

    menu = []
    telas = []
    for acao in TELAS:
        if podeExecutar(cargo, acao):
            menu.append(TELAS[acao]['nome'])
            if TELAS[acao]['tela'] is not None:
                telas.append(TELAS[acao]['tela'])
    return menu, telas