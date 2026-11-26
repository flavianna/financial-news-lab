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

    # Define o intervalo de coleta utilizando o horário UTC.
    agora = datetime.now(timezone.utc)
    limite = agora - timedelta(hours=24)

    # Distribui a coleta entre as fontes para diversificar as notícias.
    for fonte, url in FONTES.items():
        feed = feedparser.parse(url)

        for noticia in feed.entries[:quantidade]:

            if not noticia.get("published_parsed"):
                continue

            # Converte a data de publicação para datetime em UTC.
            data_publicacao = datetime.fromtimestamp(
                timegm(noticia["published_parsed"]), tz=timezone.utc
            )

            if not (limite <= data_publicacao <= agora):
                continue

            # Padroniza os dados coletados para processamento pelo agente.
            dados = {
                "titulo": noticia["title"],
                "resumo": noticia["summary"],
                "link": noticia["link"],
                "data": noticia["published"],
                "fonte": fonte,
            }

            noticias.append(dados)

    return noticias


# Teste temporário para validação da coleta e do filtro temporal.
resultado = coletar_noticias.run(quantidade=5)

print("Total de notícias:", len(resultado))

for noticia in resultado:
    print(noticia["fonte"])
    print(noticia["data"])
    print(noticia["titulo"])
    print("-" * 50)
