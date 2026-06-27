import pandas as pd
import datetime as dt
from calendar import monthrange


def lerDados(rel, conexao, rel2=0, dataInicial=0, dataUltima=0 ):
    if rel==1:
        df = pd.read_sql_query("SELECT id, nome, quantidade, preco FROM produtos ", conexao)
        return df
    if rel==2:
        if rel2==1:
            hoje = dt.date.today()
            dataUltima = hoje - dt.timedelta(days=7)
            df = pd.read_sql_query("""SELECT produto, tipo, stipo, quantidade FROM historicoMovimentacao
            WHERE data BETWEEN ? AND ?""", conexao, params=(dataUltima, hoje))
            return df
        if rel2==2:
            hoje = dt.date.today().strftime("%Y/%m/%d")
            mes = int(hoje[5:7]) - 1
            dia = int(hoje[8:])
            ano = int(hoje[0:4])
            if mes == 0:
                ano -= 1
                mes = 12
            ultimoDia = monthrange(ano, mes)[1]
            if dia > ultimoDia:
                dia = ultimoDia
            dataUltima = dt.date(ano, mes, dia).strftime("%Y/%m/%d")
            df = pd.read_sql_query("""SELECT produto, tipo, stipo, quantidade FROM historicoMovimentacao
            WHERE data BETWEEN ? AND ?""", conexao, params=(dataUltima, hoje))
            return df
        if rel2==3:
            df = pd.read_sql_query("""SELECT produto, tipo, stipo, quantidade FROM historicoMovimentacao
            WHERE data BETWEEN ? AND ?""", conexao, params=(dataInicial, dataUltima))
            return df

def gerarRel(df, nomeArquivo):
    df.to_csv(f"{nomeArquivo}_{dt.datetime.now().strftime('%d.%m.%Y_%H.%M')}.csv", index=False)