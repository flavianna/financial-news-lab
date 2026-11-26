import feedparser


def coletar_noticias(quantidade=5):
    url = "https://feeds.bbci.co.uk/news/business/rss.xml"

    feed = feedparser.parse(url)

    noticias = []

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
