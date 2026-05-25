# model/emprestimo_model.py
# DTOs da entidade Emprestimo.

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date


class EmprestimoModel(BaseModel):
    """Dados de entrada para registrar um novo empréstimo."""
    id_livro_fk:       int  = Field(..., gt=0, description="ID do livro")
    id_cliente_fk:     int  = Field(..., gt=0, description="ID do cliente")
    dt_devolucao_prev: date = Field(..., description="Prazo de devolução (YYYY-MM-DD)")

    @field_validator("dt_devolucao_prev")
    @classmethod
    def data_deve_ser_futura(cls, v):
        if v <= date.today():
            raise ValueError("A data de devolução deve ser uma data futura.")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "id_livro_fk": 1,
                "id_cliente_fk": 1,
                "dt_devolucao_prev": "2025-07-01"
            }
        }
    }


class DevolucaoModel(BaseModel):
    """Dados de entrada para registrar a devolução de um empréstimo."""
    id_emprestimo: int = Field(..., gt=0, description="ID do empréstimo a ser encerrado")

    model_config = {
        "json_schema_extra": {"example": {"id_emprestimo": 1}}
    }


class EmprestimoResponse(BaseModel):
    """Dados de saída do empréstimo, com nome do cliente e título do livro via JOIN."""
    id_emprestimo:     int
    id_livro_fk:       int
    id_cliente_fk:     int
    dt_emprestimo:     Optional[str] = None
    dt_devolucao_prev: Optional[str] = None
    dt_devolucao_real: Optional[str] = None
    status:   str   = "ativo"
    nome_cliente:      Optional[str] = None   # enriquecido via JOIN
    nome_livro:  Optional[str] = None   # enriquecido via JOIN

    model_config = {"from_attributes": True}