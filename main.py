from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controller.Controller import AutorController, LivroController, ClienteController, EmprestimoController

app = FastAPI(
    title="ByteBook API",
    description="""
## Sistema de Gerenciamento de Biblioteca

### Como cadastrar livros via ISBN
1. `GET /livros/isbn/{isbn}` — busca no Google Books e exibe preview
2. O sistema pergunta: **"Deseja salvar?"**
3. `POST /livros/isbn/confirmar` — confirma o salvamento:
   - ISBN novo → cadastra o livro (quantidade = 1)
   - ISBN já existente → adiciona +1 no estoque do livro
""",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite que o seu arquivo HTML local acesse a API
    allow_credentials=True,
    allow_methods=["*"],  # Libera GET, POST, DELETE, etc.
    allow_headers=["*"],  # Libera todos os cabeçalhos
)

app.include_router(AutorController().router)
app.include_router(LivroController().router)
app.include_router(ClienteController().router)
app.include_router(EmprestimoController().router)


@app.get("/", tags=["Status"], summary="Verificar se a API está online")
def testar_conexao():
    return {"mensagem": "ByteBook API online!", "docs": "/docs"}