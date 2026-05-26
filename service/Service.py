import requests
from fastapi import HTTPException
from config.Database import get_conexao
from model.ClienteModel import (ClienteModel, ClienteResponse)
from model.AutorModel import (AutorModel, AutorResponse)
from model.EmprestimoModel import (EmprestimoModel, EmprestimoResponse, DevolucaoModel)
from model.LivroModel import (LivroModel, LivroResponse, ConfirmarLivroISBN, ResultadoISBN)
from repository.Repository import (AutorRepository, LivroRepository, ClienteRepository, EmprestimoRepository)

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"


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


class LivroService:

    def buscar_por_isbn(self, isbn: str) -> LivroResponse:
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

        info = items[0].get("volumeInfo", {})
        nome = info.get("title") or "Título não disponível"
        autores = info.get("authors")
        editora = info.get("publisher") or None
        genero = (info.get("categories") or [None])[0]
        ano = self._extrair_ano(info.get("publishedDate"))
        isbn_f = self._extrair_isbn(info.get("industryIdentifiers", []), isbn_limpo)

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
    
    
    
    def buscar_por_titulo(self, titulo: str) -> list[LivroResponse]:
        titulo_limpo = titulo.strip()
        if not titulo_limpo:
            raise HTTPException(status_code=422, detail="O título não pode estar vazio.")

                
        try:
            resp = requests.get(
                GOOGLE_BOOKS_URL,
                params={"q": f"intitle:{titulo_limpo}", "maxResults": 5, "langRestrict": "pt"},
                timeout=6
            )
            resp.raise_for_status()
            
            
            dados = resp.json()
            items = dados.get("items", [])
            if items:
                return self._processar_resultados_google(items)
                
        except Exception as e:
            
            print(f"[AVISO] Google Books falhou ({e}). Iniciando fallback na Open Library...")

        
        try:
            resp_fallback = requests.get(
                OPEN_LIBRARY_URL,
                params={"title": titulo_limpo, "limit": 5},
                timeout=12
            )
            resp_fallback.raise_for_status()
            
            dados_fallback = resp_fallback.json()
            docs = dados_fallback.get("docs", [])
            if not docs:
                raise HTTPException(status_code=404, detail=f"Nenhum livro encontrado para o título '{titulo_limpo}'.")
                
            return self._processar_resultados_open_library(docs)

        except HTTPException:
            raise  
        except Exception as err_fallback:
            raise HTTPException(
                status_code=502, 
                detail=f"Todas as APIs de livros estão indisponíveis no momento. Detalhes: {err_fallback}"
            )

    
    def _processar_resultados_google(self, items: list) -> list[LivroResponse]:
        resultados = []
        for item in items:
            info = item.get("volumeInfo", {})
            nome = info.get("title") or "Título não disponível"
            autores = info.get("authors")
            editora = info.get("publisher") or None
            genero = (info.get("categories") or [None])[0]
            ano = self._extrair_ano(info.get("publishedDate"))
            isbn_f = self._extrair_isbn(info.get("industryIdentifiers", []), "0000000000000")

            resultados.append(
                LivroResponse(
                    id_livro=0,
                    nome=nome,
                    isbn=isbn_f,
                    quantidade=0,
                    dt_lancamento=f"{ano}-01-01" if ano else None,
                    editora=editora,
                    genero=genero,
                    nome_autor=autores[0] if autores else None
                )
            )
        return resultados

    def _processar_resultados_open_library(self, docs: list) -> list[LivroResponse]:
        resultados = []
        for doc in docs:
            nome = doc.get("title") or "Título não disponível"
            autores = doc.get("author_name", [None])
            editoras = doc.get("publisher", [None])
            generos = doc.get("subject", [None])
            ano = doc.get("first_publish_year")
            
            isbns = doc.get("isbn", [])
            isbn_f = isbns[0] if isbns else "0000000000000"

            resultados.append(
                LivroResponse(
                    id_livro=0,
                    nome=nome,
                    isbn=isbn_f,
                    quantidade=0,
                    dt_lancamento=f"{ano}-01-01" if ano else None,
                    editora=editoras[0],
                    genero=generos[0],
                    nome_autor=autores[0]
                )
            )
        return resultados


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