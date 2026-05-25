# service.py
# Camada de regras de negócio.
# Contém todas as classes Service do sistema.
# Orquestra a lógica entre os controllers e os repositories.
# Equivalente ao @Service do Spring Boot.

import requests
from fastapi import HTTPException
from config.Database import get_conexao
from model.ClienteModel import (ClienteModel, ClienteResponse)
from model.AutorModel import (AutorModel, AutorResponse)
from model.EmprestimoModel import (EmprestimoModel, EmprestimoResponse,DevolucaoModel)
from model.LivroModel import (LivroModel, LivroResponse, ConfirmarLivroISBN, ResultadoISBN)
from repository.Repository import (AutorRepository, LivroRepository, ClienteRepository, EmprestimoRepository)

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"


# ══════════════════════════════════════════════════════════════
# AUTOR
# ══════════════════════════════════════════════════════════════

class AutorService:

    def criar_autor(self, autor: AutorModel) -> AutorResponse:
        conn = get_conexao()
        return AutorRepository(conn).criar_autor(autor)

    def listar_autores(self) -> list[AutorResponse]:
        conn = get_conexao()
        return AutorRepository(conn).listar_autores()

    def ver_autor(self, id_autor: int) -> AutorResponse:
        conn = get_conexao()
        return AutorRepository(conn).ver_autor(id_autor)


# ══════════════════════════════════════════════════════════════
# LIVRO
# ══════════════════════════════════════════════════════════════

class LivroService:

    def buscar_por_isbn(self, isbn: str) -> LivroResponse:
        """
        Consulta o Google Books pelo ISBN e retorna preview dos dados.
        NADA é salvo no banco neste passo.
        O sistema exibe os dados e pergunta ao usuário se deseja salvar.
        Se sim → chamar confirmar_salvamento().
        """
        isbn_limpo = isbn.replace("-", "").replace(" ", "")
        if not isbn_limpo.isdigit() or len(isbn_limpo) not in (10, 13):
            raise HTTPException(status_code=422, detail="ISBN inválido. Use ISBN-10 ou ISBN-13.")

        try:
            resp = requests.get(
                GOOGLE_BOOKS_URL,
                params={"q": f"isbn:{isbn_limpo}", "maxResults": 1},
                timeout=8
            )
            resp.raise_for_status()
        except requests.exceptions.Timeout:
            raise HTTPException(status_code=502, detail="A API do Google Books não respondeu.")
        except requests.exceptions.ConnectionError:
            raise HTTPException(status_code=502, detail="Sem conexão com a API do Google Books.")

        dados = resp.json()
        items = dados.get("items")
        if not items:
            raise HTTPException(status_code=404, detail=f"Nenhum livro encontrado para o ISBN '{isbn_limpo}'.")

        info    = items[0].get("volumeInfo", {})
        nome    = info.get("title") or "Título não disponível"
        autores = info.get("authors")
        editora = info.get("publisher") or None
        genero  = (info.get("categories") or [None])[0]
        ano     = self._extrair_ano(info.get("publishedDate"))
        isbn_f  = self._extrair_isbn(info.get("industryIdentifiers", []), isbn_limpo)

        return LivroResponse(
            id_livro=0,
            nome=nome,
            isbn=isbn_f,
            quantidade=0,
            dt_lancamento=f"{ano}-01-01" if ano else None,
            editora=editora,
            genero=genero,
            nome_autor=autores[0] if autores else None
        )

    def confirmar_salvamento(self, dados: ConfirmarLivroISBN) -> ResultadoISBN:
        """
        Usuário confirmou que quer salvar.
        O repository decide: ISBN novo → cria livro | ISBN existente → +1 no estoque.
        """
        conn = get_conexao()
        return LivroRepository(conn).confirmar_ou_adicionar(dados)

    def criar_livro(self, livro: LivroModel) -> LivroResponse:
        conn = get_conexao()
        return LivroRepository(conn).criar_livro(livro)

    def listar_livros(self) -> list[LivroResponse]:
        conn = get_conexao()
        return LivroRepository(conn).listar_livros()

    def _extrair_ano(self, published_date) -> int | None:
        if not published_date:
            return None
        try:
            return int(published_date[:4])
        except:
            return None

    def _extrair_isbn(self, identifiers, fallback) -> str:
        isbn13 = isbn10 = None
        for item in identifiers:
            if item.get("type") == "ISBN_13": isbn13 = item.get("identifier")
            elif item.get("type") == "ISBN_10": isbn10 = item.get("identifier")
        return isbn13 or isbn10 or fallback


# ══════════════════════════════════════════════════════════════
# CLIENTE
# ══════════════════════════════════════════════════════════════

class ClienteService:

    def criar_cliente(self, cliente: ClienteModel) -> ClienteResponse:
        conn = get_conexao()
        return ClienteRepository(conn).criar_cliente(cliente)

    def listar_clientes(self) -> list[ClienteResponse]:
        conn = get_conexao()
        return ClienteRepository(conn).listar_clientes()

    def ver_cliente(self, id_cliente: int) -> ClienteResponse:
        conn = get_conexao()
        return ClienteRepository(conn).ver_cliente(id_cliente)


# ══════════════════════════════════════════════════════════════
# EMPRESTIMO
# ══════════════════════════════════════════════════════════════

class EmprestimoService:

    def novo_emprestimo(self, emprestimo: EmprestimoModel) -> EmprestimoResponse:
        conn = get_conexao()
        return EmprestimoRepository(conn).novo_emprestimo(emprestimo)

    def encerrar_emprestimo(self, id_emprestimo: int) -> EmprestimoResponse:
        conn = get_conexao()
        return EmprestimoRepository(conn).encerrar_emprestimo(id_emprestimo)

    def listar_emprestimos(self) -> list[EmprestimoResponse]:
        conn = get_conexao()
        return EmprestimoRepository(conn).listar_emprestimos()