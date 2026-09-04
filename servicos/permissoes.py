
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