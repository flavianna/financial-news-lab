import feedparser
from crewai.tools import tool

FONTES = {
    "BBC Business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "InfoMoney": "https://www.infomoney.com.br/feed/",
}


# Disponibiliza a função de coleta RSS como ferramenta do CrewAI.
@tool("Coletar notícias financeiras")
def coletar_noticias(quantidade: int = 5) -> list:
    """Coleta notícias financeiras nacionais e internacionais."""

    noticias = []

    # Distribui a coleta entre as fontes para diversificar as notícias.
    for fonte, url in FONTES.items():
        feed = feedparser.parse(url)

        # Padroniza os dados coletados para processamento pelo agente.
        for noticia in feed.entries[:quantidade]:
            dados = {
                "titulo": noticia["title"],
                "resumo": noticia["summary"],
                "link": noticia["link"],
                "data": noticia["published"],
                "fonte": fonte,
            }

            noticias.append(dados)

    return noticias


# Permite testar a coleta sem executar o agente pesquisador.
if __name__ == "__main__":
    resultado = coletar_noticias.run(quantidade=5)
    print(len(resultado))
