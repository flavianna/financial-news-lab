from typing import Literal
from pydantic import BaseModel, Field, field_validator


# define a estrutura de uma notícia individual
class Noticia(BaseModel):
    titulo: str
    resumo: str
    fonte: Literal["BBC Business", "CNBC", "InfoMoney"]
    data: str
    link: str

    @field_validator("link")
    @classmethod
    def validar_link(cls, valor):
        if not valor.startswith(("http://", "https://")):
            raise ValueError("Link inválido")

        return valor


# define uma lista de notícias.
class Boletim(BaseModel):
    noticias: list[Noticia] = Field(max_length=5)
