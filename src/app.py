import os
from flask import Flask, flash, redirect, render_template, request, url_for
from database import get_connection


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")


def fetch_products():
    conn = get_connection()
    if not conn:
        return [], "Erro ao conectar ao banco de dados."

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT idvendas AS id, nome_produto, valor FROM vendas ORDER BY idvendas")
    produtos = cursor.fetchall()
    cursor.close()
    conn.close()
    return produtos, ""


@app.get("/")
def index():
    produtos, erro = fetch_products()
    return render_template("index.html", produtos=produtos, erro=erro)


@app.post("/add")
def add_product():
    nome_produto = request.form.get("nome_produto", "").strip().title()
    valor_raw = request.form.get("valor", "").strip()

    if not nome_produto or not valor_raw:
        flash("Informe o nome do produto e o valor.", "error")
        return redirect(url_for("index"))

    try:
        valor = float(valor_raw.replace(",", "."))
    except ValueError:
        flash("Valor inválido.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    if not conn:
        flash("Erro ao conectar ao banco de dados.", "error")
        return redirect(url_for("index"))

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO vendas (nome_produto, valor) VALUES (%s, %s)",
        (nome_produto, valor),
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Produto cadastrado com sucesso!", "success")
    return redirect(url_for("index"))


@app.post("/update/<int:produto_id>")
def update_product(produto_id):
    valor_raw = request.form.get("valor", "").strip()
    if not valor_raw:
        flash("Informe o novo valor.", "error")
        return redirect(url_for("index"))

    try:
        valor = float(valor_raw.replace(",", "."))
    except ValueError:
        flash("Valor inválido.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    if not conn:
        flash("Erro ao conectar ao banco de dados.", "error")
        return redirect(url_for("index"))

    cursor = conn.cursor()
    cursor.execute("UPDATE vendas SET valor = %s WHERE id = %s", (valor, produto_id))
    conn.commit()
    cursor.close()
    conn.close()

    if cursor.rowcount == 0:
        flash("Produto não encontrado.", "error")
    else:
        flash("Valor atualizado com sucesso!", "success")

    return redirect(url_for("index"))


@app.post("/delete/<int:produto_id>")
def delete_product(produto_id):
    conn = get_connection()
    if not conn:
        flash("Erro ao conectar ao banco de dados.", "error")
        return redirect(url_for("index"))

    cursor = conn.cursor()
    cursor.execute("DELETE FROM vendas WHERE id = %s", (produto_id,))
    conn.commit()
    cursor.close()
    conn.close()

    if cursor.rowcount == 0:
        flash("Produto não encontrado.", "error")
    else:
        flash("Produto deletado com sucesso!", "success")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

