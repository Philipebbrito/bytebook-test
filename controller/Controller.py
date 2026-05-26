from fastapi import APIRouter
from model.AutorModel import (AutorModel, AutorResponse)
from model.EmprestimoModel import (EmprestimoModel, EmprestimoResponse, DevolucaoModel)
from model.LivroModel import (LivroModel, LivroResponse, ConfirmarLivroISBN, ResultadoISBN)
from model.ClienteModel import (ClienteModel, ClienteResponse) 
from service.Service import (AutorService, LivroService, ClienteService, EmprestimoService)


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



class LivroController:

    def __init__(self):
        self.router  = APIRouter(prefix="/livros", tags=["Livros"])
        self.service = LivroService()
        self._registrar_rotas()

    def _registrar_rotas(self):
        
        @self.router.get("/buscar-por-titulo", response_model=list[LivroResponse],
                         summary="",
                         description=())
        async def buscar_por_titulo(titulo: str):
            return self.service.buscar_por_titulo(titulo)

        @self.router.get("/isbn/{isbn}", response_model=LivroResponse,
                         summary="",
                         description=())
        async def buscar_por_isbn(isbn: str):
            return self.service.buscar_por_isbn(isbn)

        @self.router.post("/isbn/confirmar", response_model=ResultadoISBN, status_code=201,
                          summary="",
                          description=())
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
                            summary="",
                            description="")
        async def encerrar_emprestimo(id_emprestimo: int):
            return self.service.encerrar_emprestimo(id_emprestimo)

        @self.router.get("/", response_model=list[EmprestimoResponse],
                         summary="Listar todos os empréstimos")
        async def listar_emprestimos():
            return self.service.listar_emprestimos()