from src.database import get_connection

VALID_STATUS = {"aberto", "em_atendimento", "resolvido"}
VALID_TIPO = {"venda", "assistencia"}


def _conn_or_raise():
    conn = get_connection()
    if conn is None:
        raise RuntimeError("Falha ao conectar no banco. Verifique DB_HOST/DB_USER/DB_PASSWORD/DB_NAME no .env.")
    return conn


def ticket_criar(cliente_nome, cliente_whatsapp, tipo, assunto, descricao):
    if tipo not in VALID_TIPO:
        raise ValueError("Tipo inválido.")
    if not cliente_nome.strip() or not cliente_whatsapp.strip() or not assunto.strip() or not descricao.strip():
        raise ValueError("Campos obrigatórios vazios.")

    conn = _conn_or_raise()
    cur = conn.cursor()
    sql = """
        INSERT INTO tickets (cliente_nome, cliente_whatsapp, tipo, assunto, descricao)
        VALUES (%s, %s, %s, %s, %s)
    """
    cur.execute(sql, (cliente_nome.strip(), cliente_whatsapp.strip(), tipo, assunto.strip(), descricao.strip()))
    conn.commit()
    ticket_id = cur.lastrowid
    cur.close()
    conn.close()
    return ticket_id


def tickets_listar(limit=50):
    conn = _conn_or_raise()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tickets ORDER BY created_at DESC LIMIT %s", (int(limit),))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def ticket_por_id(ticket_id):
    conn = _conn_or_raise()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tickets WHERE id=%s", (int(ticket_id),))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def ticket_atualizar_status(ticket_id, status):
    if status not in VALID_STATUS:
        raise ValueError("Status inválido.")

    conn = _conn_or_raise()
    cur = conn.cursor()
    cur.execute("UPDATE tickets SET status=%s WHERE id=%s", (status, int(ticket_id)))
    conn.commit()
    cur.close()
    conn.close()
