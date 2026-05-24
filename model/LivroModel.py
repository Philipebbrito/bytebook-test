from pydantic import BaseModel, Field
from typing import Optional


class LivroModel(BaseModel):
    """Cadastro manual de livro — preenchido pelo usuário."""
    nome:          str           = Field(..., min_length=1, max_length=255, description="Título do livro")
    isbn:          Optional[str] = Field(default=None, min_length=10, max_length=13)
    quantidade:    int           = Field(default=1, ge=1, description="Quantidade de exemplares")
    dt_lancamento: Optional[str] = Field(default=None, description="Formato: YYYY-MM-DD")
    editora:       Optional[str] = Field(default=None, max_length=255)
    genero:        Optional[str] = Field(default=None, max_length=100)
    id_autor_fk:   Optional[int] = Field(default=None, description="ID do autor já cadastrado")

    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "Clean Code",
                "isbn": "9780132350884",
                "quantidade": 3,
                "dt_lancamento": "2008-08-01",
                "editora": "Prentice Hall",
                "genero": "Tecnologia",
                "id_autor_fk": 1
            }
        }
    }


class LivroResponse(BaseModel):
    """Retorno do livro com ID e quantidade atual no estoque."""
    id_livro:      int
    nome:          str
    isbn:          Optional[str] = None
    quantidade:    int           = 0
    dt_lancamento: Optional[str] = None
    editora:       Optional[str] = None
    genero:  Optional[str] = None
    id_autor_fk:   Optional[int] = None
    nome_autor:    Optional[str] = None   # Enriquecido via JIN com tabela autor

    model_config = {"from_attributes": True}


class ConfirmarLivroISBN(BaseModel):
    """
    Enviado após o usuário visualizar o preview da busca por ISBN
    e confirmar que deseja salvar.

    O sistema decide automaticamente:
    - ISBN novo      → cria o livro com quantidade = 1
    - ISBN existente → incrementa +1 na quantidade
    """
    nome:          str           = Field(..., min_length=1, max_length=255)
    isbn:          str           = Field(..., min_length=10, max_length=13)
    id_autor_fk:   Optional[int] = Field(default=None)
    dt_lancamento: Optional[str] = Field(default=None)
    editora:       Optional[str] = Field(default=None, max_length=255)
    genero:        Optional[str] = Field(default=None, max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "Clean Code",
                "isbn": "9780132350884",
                "id_autor_fk": 1,
                "dt_lancamento": "2008-01-01",
                "editora": "Prentice Hall",
                "genero": "Tecnologia"
            }
        }
    }


class ResultadoISBN(BaseModel):
    """
    Resposta após confirmar o salvamento via ISBN.
    O campo 'acao' informa o que foi feito:
      'livro_criado'       → livro novo inserido no banco
      'exemplar_adicionado' → +1 no estoque de livro já existente
    """
    mensagem:   str
    acao:       str           # 'livro_criado' | 'exemplar_adicionado'
    livro:      LivroResponse
    quantidade: int