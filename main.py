import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from noticias import coletar_noticias
from schemas import Boletim

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

llm = LLM(model="gpt-4o-mini", temperature=0.2)

# Agente pesquisador com acesso à ferramenta de coleta RSS
pesquisador = Agent(
    role="Pesquisador de notícias financeiras",
    goal="Coletar e selecionar notícias relevantes do mercado financeiro nacional e internacional",
    backstory="Você é um pesquisador especializado em economia global e mercados financeiros, comprometido com a confiabilidade das fontes de informação.",
    llm=llm,
    tools=[coletar_noticias],
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

tarefa_pesquisa = Task(
    description=(
        "Utilize a ferramenta de coleta para buscar cinco notícias "
        "de cada fonte disponível. "
        "Selecione até cinco notícias de maior relevância "
        "para o mercado financeiro nacional e internacional. "
        "Não selecione notícias que descrevam o mesmo acontecimento, "
        "mesmo quando publicadas por fontes diferentes. "
        "Revise a seleção antes de entregar o resultado. "
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

resultado = equipe.kickoff()


boletim_json = resultado.pydantic.model_dump_json(indent=4)

print(boletim_json)

with open("boletim.json", "w", encoding="utf-8") as arquivo:
    arquivo.write(boletim_json)
