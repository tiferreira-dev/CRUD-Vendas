from crud import criar_produto, listar_produtos, atualizar_valor, visualizar_grafico, deletar_produto

while True:
    print("\n=== Sistema de Vendas ===")
    print("1 - Cadastrar produto")
    print("2 - Listar produtos")
    print("3 - Atualizar valor")
    print("4 - Visualizar gráfico")
    print("5 - Deletar produto")
    print("0 - Sair")

    opc = input("Escolha: ")

    if opc == "1":
        nome_produto = input("Nome do produto: ").title()      
        valor = float(input("Informe o valor: "))
        criar_produto(nome_produto, valor )

    elif opc == "2":
        listar_produtos()

    elif opc == "3":
        nome_produto = input("Nome do produto: ").title()
        novo_valor = float(input("Novo valor: "))
        atualizar_valor(nome_produto, novo_valor)

    elif opc == "4":
        visualizar_grafico()


    elif opc == "5":
        nome_produto = input("Nome do produto: ").title()
        deletar_produto(nome_produto)

    elif opc == "0":
        print("Encerrando sistema...")
        break

    else:
        print("Opção inválida.")

