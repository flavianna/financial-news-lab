import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from noticias import coletar_noticias

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

tarefa_pesquisa = Task(
    description=(
        "Utilize a ferramenta de coleta para buscar cinco notícias "
        "de cada fonte disponível. "
        "Selecione até cinco notícias de maior relevância "
        "para o mercado financeiro nacional e internacional. "
        "Evite selecionar notícias sobre o mesmo acontecimento. "
        "Busque diversidade de assuntos e fontes. "
        "Não invente informações."
    ),
    expected_output=(
        "Uma lista de até cinco notícias selecionadas, "
        "contendo título, resumo original, fonte, data e link."
    ),
    agent=pesquisador,
)

# Orquestração do agente e da tarefa
equipe = Crew(agents=[pesquisador], tasks=[tarefa_pesquisa], verbose=True)

resultado = equipe.kickoff()
