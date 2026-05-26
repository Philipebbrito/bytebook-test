from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class ClienteModel(BaseModel):
    nome: str = Field(..., min_length=2, max_length=255)
    endereco: Optional[str] = Field(default=None, max_length=500)
    email: Optional[str] = Field(default=None, max_length=255)
    cpf: Optional[str] = Field(default=None, description="CPF com ou sem máscara")
    telefone: Optional[str] = Field(default=None, max_length=20)

    @field_validator("cpf")
    @classmethod
    def formatar_cpf(cls, v):
        if v is None:
            return v
        d = re.sub(r"\D", "", v)
        if len(d) != 11:
            raise ValueError("CPF deve conter 11 dígitos.")
        return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"

    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "Maria Silva",
                "endereco": "Rua das Flores, 123 - Brasilia, DF",
                "email": "maria@email.com",
                "cpf": "123.456.789-09",
                "telefone": "(61) 99999-0000"
            }
        }
    }


class ClienteResponse(BaseModel):
    id_cliente: int
    nome: str
    endereco: Optional[str] = None
    email: Optional[str] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None

    model_config = {"from_attributes": True}