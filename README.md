# ByteBook API

Sistema de Gerenciamento de Biblioteca — Projeto de Faculdade
Construido com FastAPI + Python 3.13 + SQL Server + Google Books API

---

## Arquitetura

```
byteBook/
├── config/
│   └── Database.py          # Configuracao da conexao com SQL Server
├── controller/
│   └── Controller.py        # AutorController, LivroController, ClienteController, EmprestimoController
├── model/
│   ├── AutorModel.py        # AutorModel, AutorResponse
│   ├── ClienteModel.py      # ClienteModel, ClienteResponse
│   ├── EmprestimoModel.py   # EmprestimoModel, DevolucaoModel, EmprestimoResponse
│   └── LivroModel.py        # LivroModel, LivroResponse, ConfirmarLivroISBN, ResultadoISBN
├── repository/
│   └── Repository.py        # AutorRepository, LivroRepository, ClienteRepository, EmprestimoRepository
├── service/
│   └── Service.py           # AutorService, LivroService, ClienteService, EmprestimoService
├── main.py                  # Inicializa o FastAPI e registra os controllers
├── requirements.txt
└── schema.sql
```

### Fluxo de chamada

```
main.py
  └── controller/Controller.py   (recebe a requisicao HTTP)
        └── service/Service.py   (executa a regra de negocio)
              └── repository/Repository.py   (acessa o banco de dados)
                    └── model/*Model.py      (define a estrutura dos dados)
```

---

## Setup

### 1. Criar e ativar ambiente virtual

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 3. Executar o schema.sql no SSMS

Abra o SQL Server Management Studio, conecte em localhost\SQLEXPRESS
e execute o arquivo schema.sql para criar o banco e as tabelas.

### 4. Iniciar o servidor

```powershell
python -m uvicorn main:app --reload
```

Acesse: http://localhost:8000/docs

---

## Endpoints

### Autores
| Metodo | Rota | Descricao |
|--------|------|-----------|
| POST | /autores/ | Cadastrar autor |
| GET | /autores/ | Listar autores |
| GET | /autores/{id} | Buscar por ID |

### Livros
| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | /livros/buscar-por-titulo?titulo= | Busca por titulo (Google Books + fallback Open Library) |
| GET | /livros/isbn/{isbn} | [Passo 1] Preview via Google Books |
| POST | /livros/isbn/confirmar | [Passo 2] Salvar livro — cria ou adiciona estoque |
| POST | /livros/ | Cadastro manual |
| GET | /livros/ | Listar todos |

### Clientes
| Metodo | Rota | Descricao |
|--------|------|-----------|
| POST | /clientes/ | Cadastrar cliente |
| GET | /clientes/ | Listar clientes |
| GET | /clientes/{id} | Buscar por ID |

### Emprestimos
| Metodo | Rota | Descricao |
|--------|------|-----------|
| POST | /emprestimos/ | Registrar emprestimo (reduz estoque) |
| DELETE | /emprestimos/{id} | Encerrar / registrar devolucao (restaura estoque) |
| GET | /emprestimos/ | Listar todos |

---

## Fluxo ISBN

```
1. GET  /livros/isbn/9780132350884
        Retorna preview — nada salvo ainda

2. Sistema exibe os dados e pergunta: "Deseja salvar?"

3. POST /livros/isbn/confirmar  { nome, isbn, editora, ... }
        ISBN novo?      -> { acao: "livro_criado",        quantidade: 1 }
        ISBN existente? -> { acao: "exemplar_adicionado", quantidade: N }
```