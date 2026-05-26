from pydantic import BaseModel, Field
from typing import Optional


class LivroModel(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255, description="Título do livro")
    isbn: Optional[str] = Field(default=None, min_length=10, max_length=13)
    quantidade: int = Field(default=1, ge=1, description="Quantidade de exemplares")
    dt_lancamento: Optional[str] = Field(default=None, description="Formato: YYYY-MM-DD")
    editora: Optional[str] = Field(default=None, max_length=255)
    genero: Optional[str] = Field(default=None, max_length=100)
    id_autor_fk: Optional[int] = Field(default=None, description="ID do autor já cadastrado")

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
    id_livro: int
    nome: str
    isbn: Optional[str] = None
    quantidade: int = 0
    dt_lancamento: Optional[str] = None
    editora: Optional[str] = None
    genero: Optional [str] = None
    id_autor_fk: Optional[int] = None
    nome_autor: Optional[str] = None 
    model_config = {"from_attributes": True}


class ConfirmarLivroISBN(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    isbn: str = Field(..., min_length=10, max_length=13)
    id_autor_fk: Optional[int] = Field(default=None)
    dt_lancamento: Optional[str] = Field(default=None)
    editora: Optional[str] = Field(default=None, max_length=255)
    genero: Optional[str] = Field(default=None, max_length=100)

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
    mensagem: str
    acao: str           
    livro: LivroResponse
    quantidade: int