# 📚 ByteBook API

Sistema de Gerenciamento de Biblioteca — Projeto de Faculdade  
Construído com **FastAPI + Python 3.12 + SQL Server + Google Books API**

---

## 🏗️ Arquitetura

```
byteBook/
├── config/
│   └── Database.py
├── controller/
│   └── Controller.py
├── model/
│   ├── AutorModel.py
│   ├── ClienteModel.py
│   ├── EmprestimoModel.py
│   └── LivroModel.py
├── repository/
│   └── Repository.py
├── service/
│   └── Service.py
├── main.py
├── README.md
├── requirements.txt
└── schema.sql
```

| Camada | Python (FastAPI) | 
|---|---|---|
| Apresentação | `APIRouter` | 
| Negócio | `Service class` | 
| Dados | `Repository class` | 
| DTO | `Pydantic BaseModel` | 

---

## ⚙️ Setup do Ambiente

### 1. Criar e ativar o ambiente virtual (PEP 668)

```bash
# Criar venv
python3.12 -m venv .venv

# Ativar (Linux/macOS)
source .venv/bin/activate

# Ativar (Windows)
.venv\Scripts\activate
```

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 3. Criar a tabela no SQL Server

Execute o script abaixo no seu banco **ByteBook**:

```sql
CREATE TABLE Livros (
    id             INT IDENTITY(1,1) PRIMARY KEY,
    titulo         NVARCHAR(255)  NOT NULL,
    autor          NVARCHAR(255)  NOT NULL,
    isbn           NVARCHAR(13)   NOT NULL UNIQUE,
    ano_publicacao INT            NULL
);
```

### 4. Configurar a conexão

Edite `database.py` e ajuste as variáveis em `DB_CONFIG`:

```python
DB_CONFIG = {
    "driver":   "{ODBC Driver 17 for SQL Server}",
    "server":   "localhost",      # ou "localhost\\SQLEXPRESS"
    "database": "ByteBook",
    "username": "sa",
    "password": "SuaSenhaAqui",
}
```

### 5. Iniciar o servidor

```bash
uvicorn main:app --reload --port 8000
```

---

## 🔄 Fluxo Principal — Cadastro de Livro

```
1. GET  /api/v1/livros/buscar/{isbn}  →  Busca na API do Google Books
2. Usuário visualiza o JSON retornado no Swagger
3. POST /api/v1/livros/               →  Salva os dados no SQL Server
```

---

## 📖 Documentação Interativa

Com o servidor rodando, acesse:

| Interface | URL |
|---|---|
| **Swagger UI** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |
| **Health Check** | http://localhost:8000/ |

---

## 🧪 Exemplo de Uso

### Passo 1 — Buscar pelo ISBN

```http
GET /api/v1/livros/buscar/9780132350884
```

**Resposta:**
```json
{
  "id": null,
  "titulo": "Clean Code",
  "autor": "Robert C. Martin",
  "isbn": "9780132350884",
  "ano_publicacao": 2008
}
```

### Passo 2 — Salvar no banco

```http
POST /api/v1/livros/
Content-Type: application/json

{
  "titulo": "Clean Code",
  "autor": "Robert C. Martin",
  "isbn": "9780132350884",
  "ano_publicacao": 2008
}
```

**Resposta (201 Created):**
```json
{
  "mensagem": "Livro cadastrado com sucesso!",
  "livro": {
    "id": 1,
    "titulo": "Clean Code",
    "autor": "Robert C. Martin",
    "isbn": "9780132350884",
    "ano_publicacao": 2008
  }
}
```
