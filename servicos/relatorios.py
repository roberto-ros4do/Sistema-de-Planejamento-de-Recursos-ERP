import pandas as pd
import datetime as dt
from servicos import permissoes as pe
from servicos import erros as er

ACOES_RELATORIO = {
    '1': 'EXPORTAR_RELATORIO_PRODUTOS',
    '2': 'EXPORTAR_RELATORIO_MOVIMENTACOES',
    '3': 'EXPORTAR_RELATORIO_TRANSACOES',
    '4': 'EXPORTAR_RELATORIO_ESTOQUE'
}

def lerDados(rel, conexao, cargo, query=0, parametros=0):
    if rel not in ACOES_RELATORIO:
        raise er.NaoEncontradoError('TIPO DE RELATÓRIO INVÁLIDO')
    if not pe.podeExecutar(cargo, ACOES_RELATORIO[rel]): #a ação é definida pelo tipo de relatório
        raise PermissionError('USUÁRIO NÃO POSSUI PERMISSÃO PARA REALIZAR ESTA AÇÃO')
    if rel=='1':
        if query!=0 and parametros!=0:
            df = pd.read_sql_query(query, conexao, params=parametros)
        else:
            df = pd.read_sql_query("SELECT id, nome, preco, quantidade, data, quemFez  FROM produtos ", conexao)
    elif rel=='2':
        if query!=0 and parametros!=0:
            df = pd.read_sql_query(query, conexao, params=parametros)
        else:
            df = pd.read_sql_query("""SELECT produto, idProduto, tipo, quantidade, data, quemFez, valorEnvolvido FROM historicoMovimentacao""", conexao)
    elif rel=='3':
        if query!=0 and parametros!=0:
            df = pd.read_sql_query(query, conexao, params=parametros)
        else:
           df = pd.read_sql_query("""SELECT valor, operacao, quemFez, data, hora FROM histSaldo""", conexao) 
    elif rel=='4':
        if query!=0 and parametros!=0:
            df = pd.read_sql_query(query, conexao, params=parametros)
        else:
            df = pd.read_sql_query("SELECT id, nome, quantidade FROM produtos ", conexao)
    else:
        raise er.NaoEncontradoError('TIPO DE RELATÓRIO INVÁLIDO')
    if df.empty:
        raise er.NaoEncontradoError('NÃO HÁ DADOS PARA GERAR O RELATÓRIO COM ESTAS ESPECIFICAÇÕES!')
    return df
COLUNAS_DINHEIRO = ('preco', 'valorEnvolvido', 'valor')

def formatarRelatorio(df):
    df = df.copy() #não altera o DataFrame recebido
    for coluna in COLUNAS_DINHEIRO:
        if coluna in df.columns:
            df[coluna] = df[coluna] / 100 #centavos -> reais
    if 'data' in df.columns:
        df['data'] = df['data'].str.replace('/', '-') #AAAA/MM/DD -> AAAA-MM-DD
    return df

def gerarCsv(df):
    df = formatarRelatorio(df)
    #separador ; e decimal , para o Excel em português abrir as colunas certas
    return df.to_csv(index=False, sep=';', decimal=',', float_format='%.2f')

def gerarRel(df, nomeArquivo):
    conteudo = gerarCsv(df)
    #utf-8-sig grava o marcador que faz o Excel mostrar os acentos corretamente
    with open(f"{nomeArquivo}_{dt.datetime.now().strftime('%d.%m.%Y_%H.%M')}.csv", 'w', encoding='utf-8-sig', newline='') as arquivo:
        arquivo.write(conteudo)