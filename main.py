import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from noticias import coletar_noticias
from schemas import Boletim
import logging

load_dotenv()

# Configura o registro de eventos e erros da aplicação.
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)

logging.info("Aplicação iniciada")

api_key = os.getenv("OPENAI_API_KEY")

llm = LLM(model="gpt-4o-mini", temperature=0.2)

# Executa a coleta RSS diretamente pelo Python, sem depender do agente.
noticias = coletar_noticias(5)


# Impede a execução dos agentes quando não existem dados reais disponíveis.
if not noticias:
    logging.error("Nenhuma notícia disponível")
    print("Não foi possível coletar notícias.")
    exit()

# Agente responsável pela seleção das notícias previamente coletadas.
pesquisador = Agent(
    role="Pesquisador de notícias financeiras",
    goal="Selecionar notícias relevantes do mercado financeiro nacional e internacional",
    backstory="Você é um pesquisador especializado em economia global e mercados financeiros, comprometido com a confiabilidade das fontes de informação.",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# Agente responsável pela tradução e síntese das notícias.
analista = Agent(
    role="Analista de notícias financeiras",
    goal="Produzir resumos claros e objetivos sobre notícias financeiras",
    backstory="Você é um especialista em economia e comunicação financeira.",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# Fornece as notícias previamente coletadas como contexto para a seleção.
tarefa_pesquisa = Task(
    description=(
        f"Analise as seguintes notícias coletadas: {noticias}. "
        "Selecione até cinco notícias de maior relevância "
        "para o mercado financeiro nacional e internacional. "
        "Evite notícias sobre o mesmo acontecimento. "
        "Busque diversidade de assuntos e fontes. "
        "Não invente informações."
    ),
    expected_output=(
        "Uma lista de até cinco notícias selecionadas, "
        "contendo título, resumo original, fonte, data e link."
    ),
    agent=pesquisador,
)

tarefa_analise = Task(
    description=(
        "Analise as notícias selecionadas pelo pesquisador. "
        "Traduza os títulos para português do Brasil. "
        "Utilize linguagem natural e terminologia financeira "
        "adequada ao português do Brasil, evitando traduções literais. "
        "Preserve a seleção de notícias realizada pelo pesquisador. "
        "Produza resumos claros de até três frases. "
        "Não invente informações nem faça recomendações de investimentos. "
        "Preserve a fonte, a data e o link original."
        "Se o pesquisador não retornar notícias, "
        "retorne uma lista vazia. "
    ),
    expected_output=(
        "Um boletim em português com até cinco notícias, "
        "contendo título, resumo, fonte, data e link."
    ),
    agent=analista,
    # Utiliza o resultado da pesquisa como contexto para a análise.
    context=[tarefa_pesquisa],
    # Define o modelo de saída estruturada da tarefa.
    output_pydantic=Boletim,
)

# Orquestração sequencial dos agentes e suas respectivas tarefas.
equipe = Crew(
    agents=[pesquisador, analista],
    tasks=[tarefa_pesquisa, tarefa_analise],
    verbose=True,
)


# Executa o fluxo de geração do boletim com tratamento de exceções.
try:
    logging.info("Iniciando execução dos agentes")

    resultado = equipe.kickoff()
    # Impede o armazenamento de um boletim sem notícias.
    if not resultado.pydantic.noticias:
        raise ValueError("Não existem notícias para gerar o boletim")

    logging.info("Execução dos agentes concluída")

    boletim_json = resultado.pydantic.model_dump_json(indent=4)

    print(boletim_json)

    with open("boletim.json", "w", encoding="utf-8") as arquivo:
        arquivo.write(boletim_json)

    logging.info("Boletim salvo com sucesso")

except Exception as erro:
    logging.exception("Erro ao gerar o boletim")
    print(f"Erro ao gerar o boletim: {erro}")
