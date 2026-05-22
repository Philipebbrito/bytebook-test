from pydantic import BaseModel, Field, field_validator
from typing import Optional
import typing
import re

class UsuarioCreate(BaseModel):
    nome:     str           = Field(..., min_length=2, max_length=255)
    email:    str           = Field(..., max_length=255)
    cpf:      str           = Field(..., description="CPF com ou sem mascara")
    telefone: typing.Optional[str] = Field(default=None, max_length=20)
    endereco: typing.Optional[str] = Field(default=None, max_length=500)
 
    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, v: str) -> str:
        d = re.sub(r"\D", "", v)
        if len(d) != 11:
            raise ValueError("CPF deve conter 11 digitos.")
        return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
 
    @field_validator("email")
    @classmethod
    def validar_email(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("E-mail invalido.")
        return v.lower().strip()
 
    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "Maria Silva",
                "email": "maria@email.com",
                "cpf": "123.456.789-09",
                "telefone": "(61) 99999-0000",
                "endereco": "Rua das Flores, 123 - Brasilia, DF"
            }
        }
    }
 
 
class UsuarioResponse(BaseModel):
    id:       typing.Optional[int]  = None
    nome:     str
    email:    str
    cpf:      str
    telefone: typing.Optional[str]  = None
    endereco: typing.Optional[str]  = None
    ativo:    typing.Optional[bool] = True
 
    model_config = {"from_attributes": True}