import pandas as pd
from database import get_connection

conn = get_connection()

df_vendas = pd.read_sql("SELECT * FROM bdvendas.vendas", conn)
conn.close()
 

mais_vendidos = df_vendas.groupby('nome_produto')['valor'].sum().sort_values(ascending=False)




