# controller.py
# Camada de apresentação — define todas as rotas HTTP do sistema.
# Cada classe usa um APIRouter próprio e delega ao Service correspondente.


from fastapi import APIRouter
from model.AutorModel import (AutorModel, AutorResponse)
from model.EmprestimoModel import (EmprestimoModel, EmprestimoResponse, DevolucaoModel)
from model.LivroModel import (LivroModel, LivroResponse, ConfirmarLivroISBN, ResultadoISBN)
from model.ClienteModel import (ClienteModel, ClienteResponse) 
from service.Service import (AutorService, LivroService, ClienteService, EmprestimoService)


# ══════════════════════════════════════════════════════════════
# AUTOR
# ══════════════════════════════════════════════════════════════

class AutorController:

    def __init__(self):
        self.router  = APIRouter(prefix="/autores", tags=["Autores"])
        self.service = AutorService()
        self._registrar_rotas()

    def _registrar_rotas(self):

        @self.router.post("/", response_model=AutorResponse, status_code=201,
                          summary="Cadastrar autor")
        async def criar_autor(autor: AutorModel):
            return self.service.criar_autor(autor)

        @self.router.get("/", response_model=list[AutorResponse],
                         summary="Listar todos os autores")
        async def listar_autores():
            return self.service.listar_autores()

        @self.router.get("/{id_autor}", response_model=AutorResponse,
                         summary="Buscar autor por ID")
        async def ver_autor(id_autor: int):
            return self.service.ver_autor(id_autor)


# ══════════════════════════════════════════════════════════════
# LIVRO
# ══════════════════════════════════════════════════════════════

class LivroController:

    def __init__(self):
        self.router  = APIRouter(prefix="/livros", tags=["Livros"])
        self.service = LivroService()
        self._registrar_rotas()

    def _registrar_rotas(self):
        
        @self.router.get("/buscar-por-titulo", response_model=list[LivroResponse],
                         summary="[Passo 1 Alternativo] Buscar livros por título via Google Books",
                         description=(
                             "Consulta o Google Books por nome/título e retorna uma lista de até 5 opções. **Nada é salvo.** "
                             "O front-end exibirá a lista e o usuário poderá escolher qual deseja salvar "
                             "clicando no botão correspondente, que disparará o `POST /livros/isbn/confirmar`."
                         ))
        async def buscar_por_titulo(titulo: str):
            return self.service.buscar_por_titulo(titulo)

        @self.router.get("/isbn/{isbn}", response_model=LivroResponse,
                         summary="[Passo 1] Buscar livro por ISBN via Google Books",
                         description=(
                             "Consulta o Google Books e retorna preview. **Nada é salvo.** "
                             "Após exibir, o sistema pergunta se deseja salvar. "
                             "Se sim → `POST /livros/isbn/confirmar`."
                         ))
        async def buscar_por_isbn(isbn: str):
            return self.service.buscar_por_isbn(isbn)

        @self.router.post("/isbn/confirmar", response_model=ResultadoISBN, status_code=201,
                          summary="[Passo 2] Confirmar salvamento após busca por ISBN",
                          description=(
                              "- **ISBN novo** → cadastra o livro com `quantidade = 1`\n"
                              "- **ISBN existente** → soma `+1` no estoque"
                          ))
        async def confirmar_salvamento(dados: ConfirmarLivroISBN):
            return self.service.confirmar_salvamento(dados)

        @self.router.post("/", response_model=LivroResponse, status_code=201,
                          summary="Cadastrar livro manualmente")
        async def criar_livro(livro: LivroModel):
            return self.service.criar_livro(livro)

        @self.router.get("/", response_model=list[LivroResponse],
                         summary="Listar todos os livros")
        async def listar_livros():
            return self.service.listar_livros()


# ══════════════════════════════════════════════════════════════
# CLIENTE
# ══════════════════════════════════════════════════════════════

class ClienteController:

    def __init__(self):
        self.router  = APIRouter(prefix="/clientes", tags=["Clientes"])
        self.service = ClienteService()
        self._registrar_rotas()

    def _registrar_rotas(self):

        @self.router.post("/", response_model=ClienteResponse, status_code=201,
                          summary="Cadastrar cliente")
        async def criar_cliente(cliente: ClienteModel):
            return self.service.criar_cliente(cliente)

        @self.router.get("/", response_model=list[ClienteResponse],
                         summary="Listar todos os clientes")
        async def listar_clientes():
            return self.service.listar_clientes()

        @self.router.get("/{id_cliente}", response_model=ClienteResponse,
                         summary="Buscar cliente por ID")
        async def ver_cliente(id_cliente: int):
            return self.service.ver_cliente(id_cliente)


# ══════════════════════════════════════════════════════════════
# EMPRESTIMO
# ══════════════════════════════════════════════════════════════

class EmprestimoController:

    def __init__(self):
        self.router  = APIRouter(prefix="/emprestimos", tags=["Empréstimos"])
        self.service = EmprestimoService()
        self._registrar_rotas()

    def _registrar_rotas(self):

        @self.router.post("/", response_model=EmprestimoResponse, status_code=201,
                          summary="Registrar novo empréstimo",
                          description="Valida estoque do livro e existência do cliente. Reduz 1 do estoque.")
        async def novo_emprestimo(emprestimo: EmprestimoModel):
            return self.service.novo_emprestimo(emprestimo)

        @self.router.delete("/{id_emprestimo}", response_model=EmprestimoResponse,
                            summary="Encerrar empréstimo / registrar devolução",
                            description="Muda status para 'devolvido', registra data real e restaura +1 no estoque.")
        async def encerrar_emprestimo(id_emprestimo: int):
            return self.service.encerrar_emprestimo(id_emprestimo)

        @self.router.get("/", response_model=list[EmprestimoResponse],
                         summary="Listar todos os empréstimos")
        async def listar_emprestimos():
            return self.service.listar_emprestimos()