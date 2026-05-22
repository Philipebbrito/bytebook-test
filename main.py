"""
main.py — ByteBook v3
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controller.livro_controller      import router as livro_router
from controller.usuario_controller    import router as usuario_router
from controller.emprestimo_controller import router as emprestimo_router

app = FastAPI(
    title="ByteBook API",
    description="""
## Sistema de Gerenciamento de Biblioteca

### Fluxo de cadastro de livros via ISBN
1. `GET /api/v1/livros/buscar/{isbn}` — busca no Google Books e retorna preview
2. O sistema exibe os dados e pergunta se deseja salvar
3. `POST /api/v1/livros/confirmar` — confirma e o sistema decide:
   - ISBN novo → cria livro + primeiro exemplar
   - ISBN existente → adiciona novo exemplar ao estoque

### Módulos
- **Livros & Exemplares** — cada livro tem N cópias físicas com status individual
- **Usuários** — cadastro completo com CPF validado
- **Empréstimos** — vincula usuário a um exemplar específico
""",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

app.include_router(livro_router,      prefix="/api/v1")
app.include_router(usuario_router,    prefix="/api/v1")
app.include_router(emprestimo_router, prefix="/api/v1")

@app.get("/", tags=["Status"])
def root():
    return {"status": "online", "versao": "3.0.0", "docs": "/docs"}