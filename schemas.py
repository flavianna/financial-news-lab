from pydantic import BaseModel


# define a estrutura de uma notícia individual
class Noticia(BaseModel):
    titulo: str
    resumo: str
    fonte: str
    data: str
    link: str


# define uma lista de notícias.
class Boletim(BaseModel):
    noticias: list[Noticia]
