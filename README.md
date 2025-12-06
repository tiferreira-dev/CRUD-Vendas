# CRUD de Vendas com Python e MySQL

Este projeto implementa um sistema CRUD (Create, Read, Update, Delete) para gerenciar vendas utilizando Python, MySQL e boas práticas de desenvolvimento — incluindo conexão segura, variáveis de ambiente, SQL parametrizado e estrutura modular.

---

## 🚀 Tecnologias Utilizadas
- Python 3
- MySQL
- mysql-connector-python
- python-dotenv
- pandas
- matplotlib + seaborn
- Programação modular

---

## 📂 Estrutura do Projeto
CRUD-Vendas/
│
├── src/
│   ├── database.py        # Conexão com o banco via variáveis de ambiente (.env)
│   ├── crud.py            # Funções CRUD (Create, Read, Update, Delete)
│   ├── processamento.py   # Leitura da base + agrupamentos e cálculos
│   ├── views.py           # Gráfico dos produtos mais vendidos
│   ├── main.py            # Interface de menu no terminal
│
├── .env                   # Credenciais do MySQL (não subir para o GitHub)
├── .gitignore
├── requirements.txt
└── README.md

---

## 🔧 Instalação

### Clone o repositório: git clone https://github.com/tiferreira-dev/CRUD-Vendas

### Instale as dependências: pip install -r requirements.txt

### Configure o arquivo `.env`: 
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=SUA_SENHA_AQUI
DB_NAME=bdvendas

### Crie o banco e a tabela no MySQL:
```sql
CREATE DATABASE bdvendas;

USE bdvendas;

CREATE TABLE vendas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_produto VARCHAR(100),   
    valor FLOAT
);

python src/main.py

Funcionalidades

CRUD Completo
	•	Cadastrar produto
	•	Listar produtos
	•	Atualizar valor
	•	Deletar produto

Gráfico Analítico

Gerado com Seaborn + Matplotlib:
	•	Top 5 produtos mais vendidos
	•	Visualização clara para análise rápida
	•	Ideal para evoluir para dashboard, API ou interface gráfica

Boas Práticas Implementadas
	•	SQL seguro com placeholders (%s)
	•	Variáveis de ambiente (sem expor senha no código)
	•	Arquitetura limpa e modular
	•	Separação entre CRUD, visualização e processamento
	•	Tratamento básico de erros
	•	Projeto preparado para evoluir para:
	•	API (FastAPI / Flask)
	•	Interface gráfica
	•	Dashboard profissional

    Autor

Ygor Barros Ferreira
GitHub: https://github.com/tiferreira-dev


