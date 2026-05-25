# main.py — ByteBook
# Arquivo principal — inicializa o FastAPI e registra os controllers.
# Não contém rotas nem regras de negócio.
#
# Execute com: python -m uvicorn main:app --reload

from fastapi import FastAPI
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

app.include_router(AutorController().router)
app.include_router(LivroController().router)
app.include_router(ClienteController().router)
app.include_router(EmprestimoController().router)


@app.get("/", tags=["Status"], summary="Verificar se a API está online")
def testar_conexao():
    return {"mensagem": "ByteBook API online!", "docs": "/docs"}