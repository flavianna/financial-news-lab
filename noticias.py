import feedparser
from crewai.tools import tool
from datetime import datetime, timedelta, timezone
from calendar import timegm
import logging

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
        logging.info(f"Consultando fonte: {fonte}")

        feed = feedparser.parse(url)

        if not feed.entries:
            logging.warning(f"Nenhuma notícia obtida de: {fonte}")
            continue

        for noticia in feed.entries[:quantidade]:

            # Permite continuar a coleta mesmo quando uma fonte não retorna notícias.
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

        if not noticias:
            logging.error("Nenhuma notícia válida foi coletada")

    return noticias
