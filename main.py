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
        "Utilize a ferramenta de coleta de notícias para buscar "
        "cinco notícias financeiras e econômicas recentes. "
        "Traduza obrigatoriamente os títulos e resumos "
        "para português do Brasil. "
        "Preserve as informações originais, sem inventar dados. "
        "Mantenha os links e as datas originais."
    ),
    expected_output=(
        "Uma lista de cinco notícias contendo: "
        "título em português, resumo em português, "
        "fonte, data e link original."
    ),
    agent=pesquisador,
)

# Orquestração do agente e da tarefa
equipe = Crew(agents=[pesquisador], tasks=[tarefa_pesquisa], verbose=True)

resultado = equipe.kickoff()


resultado_noticias = coletar_noticias.run(quantidade=3)

print(resultado_noticias)
