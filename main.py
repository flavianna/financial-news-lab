import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from noticias import coletar_noticias

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

llm = LLM(model="gpt-4o-mini", temperature=0.2)

pesquisador = Agent(
    role="Pesquisador de notícias financeiras",
    goal="Coletar e selecionar notícias relevantes do mercado financeiro nacional e internacional",
    backstory="Você é um pesquisador especializado em economia global e mercados financeiros, comprometido com a confiabilidade das fontes de informação.",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

tarefa_pesquisa = Task(
    description="Identifique cinco temas relevantes para acompanhar no mercado financeiro nacional e internacional.",
    expected_output="Uma lista com cinco temas e uma breve descrição de cada um.",
    agent=pesquisador,
)

equipe = Crew(agents=[pesquisador], tasks=[tarefa_pesquisa], verbose=True)

resultado = equipe.kickoff()

resultado_noticias = coletar_noticias(3)

print(resultado_noticias)
