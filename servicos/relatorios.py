import pandas as pd
import datetime as dt


def lerDados(rel, conexao, query=0, parametros=0):
    if rel==1:
        if query!=0 and parametros!=0:
            df = pd.read_sql_query(query, conexao, params=parametros)
            return df
        else:
            df = pd.read_sql_query("SELECT id, nome, preco, quantidade, data, quemFez  FROM produtos ", conexao)
            return df
    if rel==2:
        if query!=0 and parametros!=0:
            df = pd.read_sql_query(query, conexao, params=parametros)
            return df
        else:
            df = pd.read_sql_query("""SELECT produto, idProduto, tipo, quantidade, data, quemFez, valorEnvolvido FROM historicoMovimentacao""", conexao)
            return df
    if rel==3:
        if query!=0 and parametros!=0:
            df = pd.read_sql_query(query, conexao, params=parametros)
            return df
        else:
            df = pd.read_sql_query("""SELECT valor, operacao, quemFez, data, hora FROM histSaldo""", conexao)
            return df
    if rel==4:
        if query!=0 and parametros!=0:
            df = pd.read_sql_query(query, conexao, params=parametros)
            return df
        else:
            df = pd.read_sql_query("SELECT id, nome, quantidade FROM produtos ", conexao)
            return df
def gerarRel(df, nomeArquivo):
    df.to_csv(f"{nomeArquivo}_{dt.datetime.now().strftime('%d.%m.%Y_%H.%M')}.csv", index=False)