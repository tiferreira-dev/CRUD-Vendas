from processamento import mais_vendidos
import matplotlib.pyplot as plt
import seaborn as sns


def visualizar_grafico():
    plt.figure(figsize=(8,5))
    plt.xticks(rotation=45)
    x = mais_vendidos.head(5).index
    y = mais_vendidos.hrad(5).values
    sns.barplot(x=x, y=y, palette='viridis')
    plt.title('Top 5 produtos mais vendidos')
    plt.ylabel('Valor total vendido (R$)')
    plt.show()
      