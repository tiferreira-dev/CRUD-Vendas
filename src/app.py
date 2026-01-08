import os
from flask import Flask, flash, redirect, render_template, request, url_for, jsonify
from database import get_connection

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

# =========================
# VENDAS (bdvendas.vendas: id, nome_produto, valor, imagem, created_at)
# =========================
def fetch_products():
    conn = get_connection()
    if not conn:
        return [], "Erro ao conectar ao banco de dados."

    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, nome_produto, valor, imagem, status FROM vendas ORDER BY id DESC")
    produtos = cur.fetchall()
    cur.close()
    conn.close()
    return produtos, ""



@app.get("/")
def index():
    produtos, erro = fetch_products()
    return render_template("index.html", produtos=produtos, erro=erro)


VALID_VENDA_STATUS = {"pendente", "pago", "cancelado", "entregue"}

@app.post("/add")
def add_product():
    nome_produto = request.form.get("nome_produto", "").strip().title()
    valor_raw = request.form.get("valor", "").strip()
    imagem = request.form.get("imagem", "").strip() or None  # URL opcional
    status = request.form.get("status", "pendente").strip()

    if not nome_produto or not valor_raw:
        flash("Informe o nome do produto e o valor.", "error")
        return redirect(url_for("index"))

    try:
        valor = float(valor_raw.replace(",", "."))
    except ValueError:
        flash("Valor inválido.", "error")
        return redirect(url_for("index"))

    if status not in VALID_VENDA_STATUS:
        flash("Status inválido.", "error")
        return redirect(url_for("index"))

    if imagem and not (imagem.startswith("http://") or imagem.startswith("https://")):
        flash("A imagem deve ser uma URL começando com http:// ou https://", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    if not conn:
        flash("Erro ao conectar ao banco de dados.", "error")
        return redirect(url_for("index"))

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO vendas (nome_produto, valor, imagem, status) VALUES (%s, %s, %s, %s)",
        (nome_produto, valor, imagem, status),
    )
    conn.commit()
    cur.close()
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

    cur = conn.cursor()
    cur.execute("UPDATE vendas SET valor=%s WHERE id=%s", (valor, produto_id))
    conn.commit()
    affected = cur.rowcount
    cur.close()
    conn.close()

    if affected == 0:
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

    cur = conn.cursor()
    cur.execute("DELETE FROM vendas WHERE id=%s", (produto_id,))
    conn.commit()
    affected = cur.rowcount
    cur.close()
    conn.close()

    if affected == 0:
        flash("Produto não encontrado.", "error")
    else:
        flash("Produto deletado com sucesso!", "success")

    return redirect(url_for("index"))


# =========================
# API - GRÁFICO (quase tempo real)
# =========================
@app.get("/api/vendas/series")
def api_vendas_series():
    """
    Retorna série temporal (últimas N horas) com:
      - qtd de vendas por hora
      - total (R$) por hora
      - resumo da janela
    """
    try:
        horas = int(request.args.get("horas", 24))
    except ValueError:
        horas = 24

    horas = max(1, min(horas, 168))  # 1h a 7 dias

    conn = get_connection()
    if not conn:
        return jsonify({"ok": False, "error": "Erro ao conectar ao banco."}), 500

    cur = conn.cursor(dictionary=True)

    # Depende de vendas.created_at existir
    cur.execute(
        """
        SELECT
          DATE_FORMAT(created_at, '%%Y-%%m-%%d %%H:00:00') AS bucket,
          COUNT(*) AS qtd,
          COALESCE(SUM(valor), 0) AS total
        FROM vendas
        WHERE created_at >= (NOW() - INTERVAL %s HOUR)
        GROUP BY bucket
        ORDER BY bucket
        """,
        (horas,),
    )
    rows = cur.fetchall()

    cur.execute(
        """
        SELECT
          COUNT(*) AS qtd_total,
          COALESCE(SUM(valor), 0) AS valor_total
        FROM vendas
        WHERE created_at >= (NOW() - INTERVAL %s HOUR)
        """,
        (horas,),
    )
    resumo = cur.fetchone()

    cur.close()
    conn.close()

    labels = [r["bucket"] for r in rows]
    qtd = [int(r["qtd"]) for r in rows]
    total = [float(r["total"]) for r in rows]

    return jsonify(
        {
            "ok": True,
            "labels": labels,
            "qtd": qtd,
            "total": total,
            "resumo": {
                "qtd_total": int(resumo["qtd_total"]),
                "valor_total": float(resumo["valor_total"]),
                "janela_horas": horas,
            },
        }
    )


# =========================
# SUPORTE (bdvendas.tickets)
# =========================
VALID_TIPO = {"venda", "assistencia"}
VALID_STATUS = {"aberto", "em_atendimento", "resolvido"}


def fetch_tickets(limit=50):
    conn = get_connection()
    if not conn:
        return [], "Erro ao conectar ao banco de dados."

    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tickets ORDER BY created_at DESC LIMIT %s", (int(limit),))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows, ""


def fetch_ticket(ticket_id):
    conn = get_connection()
    if not conn:
        return None, "Erro ao conectar ao banco de dados."

    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tickets WHERE id=%s", (int(ticket_id),))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row, ""


def create_ticket(cliente_nome, cliente_whatsapp, tipo, assunto, descricao):
    tipo = (tipo or "").strip()
    if tipo not in VALID_TIPO:
        raise ValueError("Tipo inválido. Use: venda ou assistencia.")

    if not (cliente_nome or "").strip():
        raise ValueError("Nome do cliente é obrigatório.")
    if not (cliente_whatsapp or "").strip():
        raise ValueError("WhatsApp é obrigatório.")
    if not (assunto or "").strip():
        raise ValueError("Assunto é obrigatório.")
    if not (descricao or "").strip():
        raise ValueError("Descrição é obrigatória.")

    conn = get_connection()
    if not conn:
        raise RuntimeError("Erro ao conectar ao banco de dados.")

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO tickets (cliente_nome, cliente_whatsapp, tipo, assunto, descricao)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (cliente_nome.strip(), cliente_whatsapp.strip(), tipo, assunto.strip(), descricao.strip()),
    )
    conn.commit()
    ticket_id = cur.lastrowid
    cur.close()
    conn.close()
    return ticket_id


def update_ticket_status(ticket_id, status):
    status = (status or "").strip()
    if status not in VALID_STATUS:
        raise ValueError("Status inválido. Use: aberto, em_atendimento ou resolvido.")

    conn = get_connection()
    if not conn:
        raise RuntimeError("Erro ao conectar ao banco de dados.")

    cur = conn.cursor()
    cur.execute("UPDATE tickets SET status=%s WHERE id=%s", (status, int(ticket_id)))
    conn.commit()
    affected = cur.rowcount
    cur.close()
    conn.close()
    return affected


@app.get("/suporte")
def suporte_lista():
    tickets, erro = fetch_tickets()
    return render_template("suporte_lista.html", tickets=tickets, erro=erro)


@app.get("/suporte/novo")
def suporte_novo_get():
    return render_template("suporte_novo.html")


@app.post("/suporte/novo")
def suporte_novo_post():
    try:
        ticket_id = create_ticket(
            cliente_nome=request.form.get("cliente_nome", ""),
            cliente_whatsapp=request.form.get("cliente_whatsapp", ""),
            tipo=request.form.get("tipo", "venda"),
            assunto=request.form.get("assunto", ""),
            descricao=request.form.get("descricao", ""),
        )
        flash(f"Ticket criado: #{ticket_id}", "success")
        return redirect(url_for("suporte_detalhe", ticket_id=ticket_id))
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("suporte_novo_get"))


@app.get("/suporte/<int:ticket_id>")
def suporte_detalhe(ticket_id):
    ticket, erro = fetch_ticket(ticket_id)
    if erro:
        flash(erro, "error")
        return redirect(url_for("suporte_lista"))
    if not ticket:
        flash("Ticket não encontrado.", "error")
        return redirect(url_for("suporte_lista"))

    return render_template("suporte_detalhe.html", ticket=ticket)


@app.post("/suporte/<int:ticket_id>/status")
def suporte_status(ticket_id):
    try:
        status = request.form.get("status", "aberto")
        affected = update_ticket_status(ticket_id, status)
        if affected == 0:
            flash("Ticket não encontrado.", "error")
        else:
            flash("Status atualizado.", "success")
    except Exception as e:
        flash(str(e), "error")

    return redirect(url_for("suporte_detalhe", ticket_id=ticket_id))

@app.get("/api/vendas/status")
def api_vendas_status():
    """
    Retorna vendas agrupadas por status (qtd e total R$) na janela das últimas N horas.
    """
    try:
        horas = int(request.args.get("horas", 24))
    except ValueError:
        horas = 24

    horas = max(1, min(horas, 168))  # 1h a 7 dias

    conn = get_connection()
    if not conn:
        return jsonify({"ok": False, "error": "Erro ao conectar ao banco."}), 500

    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT
          status,
          COUNT(*) AS qtd,
          COALESCE(SUM(valor), 0) AS total
        FROM vendas
        WHERE created_at >= (NOW() - INTERVAL %s HOUR)
        GROUP BY status
        ORDER BY FIELD(status,'pendente','pago','cancelado','entregue')
        """,
        (horas,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    labels = [r["status"] for r in rows]
    qtd = [int(r["qtd"]) for r in rows]
    total = [float(r["total"]) for r in rows]

    return jsonify({
        "ok": True,
        "labels": labels,
        "qtd": qtd,
        "total": total,
        "janela_horas": horas
    })



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
