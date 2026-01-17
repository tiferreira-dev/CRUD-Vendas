from werkzeug.security import generate_password_hash
from database import get_connection

def criar_usuario():
    nome = input("Nome do usuário: ").strip()
    email = input("Email: ").strip().lower()
    senha = input("Senha: ").strip()

    if not nome or not email or not senha:
        print("❌ Todos os campos são obrigatórios.")
        return

    senha_hash = generate_password_hash(senha)

    conn = get_connection()
    if not conn:
        print("❌ Erro ao conectar ao banco.")
        return

    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO usuarios (nome, email, senha_hash) VALUES (%s, %s, %s)",
            (nome, email, senha_hash)
        )
        conn.commit()
        print("✅ Usuário criado com sucesso!")
    except Exception as e:
        print("❌ Erro ao criar usuário:", e)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    criar_usuario()
