import pandas as pd
import datetime as dt
from calendar import monthrange


def lerDados(rel, conexao, rel2=0, query=0, parametros=0):
    if rel==1:
        if query!=0 and parametros!=0:
            df = pd.read_sql_query(query, conexao, params=parametros)
            return df
        else:
            df = pd.read_sql_query("SELECT id, nome, quantidade, preco FROM produtos ", conexao)
            return df
    if rel==2:
        if query!=0 and parametros!=0:
            df = pd.read_sql_query(query, conexao, params=parametros)
            return df
        else:
            df = pd.read_sql_query("""SELECT produto, tipo, stipo, quantidade, data, hora, valorEnvolvido FROM historicoMovimentacao""", conexao)
            return df

def gerarRel(df, nomeArquivo):
    df.to_csv(f"{nomeArquivo}_{dt.datetime.now().strftime('%d.%m.%Y_%H.%M')}.csv", index=False)