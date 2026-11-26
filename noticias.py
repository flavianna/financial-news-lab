import feedparser
from crewai.tools import tool


# Disponibiliza a função de coleta RSS como ferramenta do CrewAI.
@tool("Coletar notícias financeiras")
def coletar_noticias(quantidade: int = 5) -> list:
    """Coleta notícias econômicas e financeiras da BBC Business."""

    url = "https://feeds.bbci.co.uk/news/business/rss.xml"

    feed = feedparser.parse(url)

    noticias = []

    # Padroniza os dados coletados para processamento pelo agente.
    for noticia in feed.entries[:quantidade]:
        dados = {
            "titulo": noticia["title"],
            "resumo": noticia["summary"],
            "link": noticia["link"],
            "data": noticia["published"],
            "fonte": "BBC Business",
        }

        noticias.append(dados)

    return noticias
