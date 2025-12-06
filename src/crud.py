from database import get_connection
import matplotlib.pyplot as plt
import seaborn as sns
from processamento import mais_vendidos

def criar_produto(nome_produto, valor):
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()
    comando = """
        INSERT INTO vendas (nome_produto, valor)
        VALUES (%s, %s)
    """
    cursor.execute(comando, (nome_produto, valor))
    conn.commit()

    print(f"Produto '{nome_produto}' cadastrado com sucesso!")
    cursor.close()
    conn.close()


def listar_produtos():
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vendas")
    resultado = cursor.fetchall()

    if not resultado:
        print("Nenhum produto encontrado.")
    else:
        for linha in resultado:
            print(linha)

    cursor.close()
    conn.close()


def atualizar_valor(nome_produto, novo_valor):
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()
    comando = """
        UPDATE vendas
        SET valor = %s
        WHERE nome_produto= %s
    """
    cursor.execute(comando, (novo_valor, nome_produto))
    conn.commit()

    if cursor.rowcount == 0:
        print("Produto não encontrado.")
    else:
        print("Valor atualizado com sucesso!")

    cursor.close()
    conn.close()


def visualizar_grafico():    
    print('\nGerando gráficos...: ')

    plt.figure(figsize=(8,5))
    plt.xticks(rotation=90)
    x = mais_vendidos.head(5).index
    y = mais_vendidos.head(5).values
    sns.barplot(x=x, y=y, palette='viridis')
    plt.title('Top 5 produtos mais vendidos')
    plt.ylabel('Valor do produto (R$)')
    plt.show()
   

def deletar_produto(nome_produto):
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()
    comando = "DELETE FROM vendas WHERE nome_produto = %s"
    cursor.execute(comando, (nome_produto,))
    conn.commit()

    if cursor.rowcount == 0:
        print("Produto não encontrado.")
    else:
        print("Produto deletado com sucesso!")

    cursor.close()
    conn.close()