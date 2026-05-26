from pydantic import BaseModel, Field
from typing import Optional

class AutorModel(BaseModel):
    nome: str = Field(..., min_length=2, max_length=255)
    dt_nasc: Optional[str] = Field(default=None, description="Formato: YYYY-MM-DD")
    model_config = {
        "json_schema_extra": {
            "example": {"nome": "Robert C. Martin", "dt_nasc": "1952-12-05"}
        }
    }


class AutorResponse(BaseModel):
    id_autor: int
    nome: str
    dt_nasc:  Optional[str] = None
    model_config = {"from_attributes": True}