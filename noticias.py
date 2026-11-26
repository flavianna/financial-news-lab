import feedparser
from crewai.tools import tool
from datetime import datetime, timedelta, timezone
from calendar import timegm

FONTES = {
    "BBC Business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "InfoMoney": "https://www.infomoney.com.br/feed/",
}


# Disponibiliza a função de coleta RSS como ferramenta do CrewAI.
@tool("Coletar notícias financeiras")
def coletar_noticias(quantidade: int = 5) -> list:
    """Coleta notícias financeiras nacionais e internacionais
    publicadas nas últimas 24 horas."""

    noticias = []

    agora = datetime.now(timezone.utc)
    limite = agora - timedelta(hours=24)

    # Distribui a coleta entre as fontes para diversificar as notícias.
    for fonte, url in FONTES.items():
        feed = feedparser.parse(url)

    # Padroniza os dados coletados para processamento pelo agente.
    for noticia in feed.entries[:quantidade]:

        if not noticia.get("published_parsed"):
            continue

        data_publicacao = datetime.fromtimestamp(
            timegm(noticia["published_parsed"]), tz=timezone.utc
        )

        if not (limite <= data_publicacao <= agora):
            continue

        dados = {
            "titulo": noticia["title"],
            "resumo": noticia["summary"],
            "link": noticia["link"],
            "data": noticia["published"],
            "fonte": fonte,
        }

        noticias.append(dados)

    return noticias


# TESTE TEMPORÁRIO DE DATAS
feed = feedparser.parse(FONTES["BBC Business"])

noticia = feed.entries[0]

data_publicacao = datetime.fromtimestamp(
    timegm(noticia["published_parsed"]), tz=timezone.utc
)

print("Data original:", noticia["published"])
print("Data convertida:", data_publicacao)

agora = datetime.now(timezone.utc)

limite = agora - timedelta(hours=24)

if limite <= data_publicacao <= agora:
    print("Notícia dentro das últimas 24 horas")
else:
    print("Notícia fora do intervalo")
