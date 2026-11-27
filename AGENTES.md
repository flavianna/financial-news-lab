# Arquitetura de agentes de IA --- Financial News Lab

## 1. Objetivo

O Financial News Lab utiliza inteligência artificial generativa para selecionar e sintetizar notícias do mercado financeiro nacional e internacional, produzindo um boletim informativo em português do Brasil.

A aplicação utiliza o CrewAI para organizar dois agentes especializados, enquanto o Python controla a coleta das informações e o Pydantic define o contrato de saída do boletim.

## 2. Arquitetura

``` mermaid
flowchart TD
    A[Fontes RSS] --> B[Coleta e filtro temporal em Python]
    B --> C{Existem notícias?}
    C -->|Não| D[Registro de erro e encerramento]
    C -->|Sim| E[Agente pesquisador]
    E --> F[Agente analista]
    F --> G[Saída estruturada com Pydantic]
    G --> H[Verificação de boletim não vazio]
    H --> I[Serialização e armazenamento JSON]
    I --> J[Script de envio HTTP POST]
    J --> K[Make]
```

A geração do boletim e seu envio ao Make são etapas distintas. O script de integração lê o arquivo JSON produzido pela aplicação. A distribuição é detalhada em [MAKE.md](MAKE.md).

## 3. Modelo de linguagem

Os dois agentes compartilham uma instância de LLM configurada no CrewAI:

``` python
llm = LLM(model="gpt-4o-mini", temperature=0.2)
```

  Configuração              Valor
  ------------------------- -------------
  Modelo                    GPT-4o mini
  Temperatura               0.2
  Framework                 CrewAI
  Verbose                   True
  Delegação entre agentes   False

A temperatura reduzida busca favorecer respostas mais consistentes e adequadas à natureza informativa do boletim, sem garantir determinismo ou exatidão factual. A chave de API é disponibilizada por meio da variável de ambiente `OPENAI_API_KEY`, carregada com `python-dotenv`.

## 4. Coleta e preparação dos dados

O módulo `noticias.py` utiliza `feedparser` para consultar três fontes RSS:

  ----------------------------------------------------------------------------------------------------
  Fonte                                                            Abrangência
  ---------------------------------------------------------------- -----------------------------------
  [BBC Business](https://feeds.bbci.co.uk/news/business/rss.xml)   Internacional

  [CNBC](https://www.cnbc.com/id/100003114/device/rss/rss.html)    Internacional

  [InfoMoney](https://www.infomoney.com.br/feed/)                  Nacional e internacional
  ----------------------------------------------------------------------------------------------------

A função `coletar_noticias(5)` examina até cinco entradas de cada fonte, totalizando até quinze candidatas antes da seleção pelos agentes.

O processamento considera somente publicações com data disponível e situada nas últimas 24 horas, utilizando UTC como referência. Os dados são padronizados em dicionários com os campos `titulo`, `resumo`, `fonte`, `data` e `link`.

Quando uma fonte não retorna entradas, a aplicação registra um aviso e continua consultando as demais. Caso a coleta termine sem notícias válidas, o fluxo principal é encerrado antes da execução dos agentes.

## 5. Agentes e responsabilidades

### 5.1. Agente pesquisador

Responsável pela curadoria das notícias previamente coletadas.

  ------------------------------------------------------------------------------------------------------------------------------------------
  Propriedade                         Descrição
  ----------------------------------- ------------------------------------------------------------------------------------------------------
  Role                                Pesquisador de notícias financeiras

  Goal                                Selecionar notícias relevantes do mercado financeiro nacional e internacional

  Backstory                           Especialista em economia global e mercados financeiros, comprometido com a confiabilidade das fontes

  Entrada                             Lista de notícias coletadas pelo Python

  Saída esperada                      Até cinco notícias selecionadas, preservando os dados originais
  ------------------------------------------------------------------------------------------------------------------------------------------

A tarefa de pesquisa orienta o agente a priorizar relevância, diversidade de assuntos e fontes, evitar notícias sobre o mesmo acontecimento e não inventar informações. A seleção semântica é realizada pelo modelo de linguagem.

### 5.2. Agente analista

Responsável pela tradução e síntese das notícias selecionadas.

  ----------------------------------------------------------------------------------------------------
  Propriedade                         Descrição
  ----------------------------------- ----------------------------------------------------------------
  Role                                Analista de notícias financeiras

  Goal                                Produzir resumos claros e objetivos sobre notícias financeiras

  Backstory                           Especialista em economia e comunicação financeira

  Entrada                             Resultado da tarefa de pesquisa

  Saída esperada                      Boletim estruturado em português do Brasil
  ----------------------------------------------------------------------------------------------------

As instruções orientam o analista a preservar a seleção do pesquisador, traduzir títulos com terminologia financeira natural, produzir resumos de até três frases, manter fonte, data e link originais e evitar informações inventadas ou recomendações de investimento. Na ausência de notícias selecionadas, a instrução prevê uma lista vazia.

## 6. Orquestração com CrewAI

A arquitetura utiliza `Agent` para definir papéis e objetivos, `Task` para estabelecer instruções e resultados esperados e `Crew` para coordenar a execução sequencial.

``` python
equipe = Crew(
    agents=[pesquisador, analista],
    tasks=[tarefa_pesquisa, tarefa_analise],
    verbose=True,
)

resultado = equipe.kickoff()
```

O compartilhamento de contexto é definido na tarefa do analista por `context=[tarefa_pesquisa]`. Dessa forma, o resultado da pesquisa é disponibilizado à etapa de análise. A delegação está desabilitada nos dois agentes, mantendo as responsabilidades definidas pela aplicação.

## 7. Engenharia de prompts

Os prompts são organizados em papel (`role`), objetivo (`goal`), contexto profissional (`backstory`), descrição da tarefa (`description`) e resultado esperado (`expected_output`).

Durante o desenvolvimento, as instruções foram refinadas para estabelecer critérios de relevância, diversidade, deduplicação semântica, tradução natural, concisão e preservação das informações originais.

Esses critérios orientam o comportamento do modelo. As verificações estruturais e as condições de execução são realizadas separadamente pelo código Python.

## 8. Evolução arquitetural: tool calling e confiabilidade

Na implementação inicial, a função de coleta RSS era disponibilizada ao agente pesquisador por meio do decorator `@tool` do CrewAI. O agente podia solicitar a execução da ferramenta para obter informações externas.

Durante testes manuais de indisponibilidade total das fontes RSS, foram observadas respostas contendo notícias sem respaldo nos dados coletados, mesmo após o refinamento das instruções e a inclusão de validações estruturais.

A arquitetura foi modificada para transferir o controle da coleta ao Python:

``` python
noticias = coletar_noticias(5)

if not noticias:
    logging.error("Nenhuma notícia disponível")
    print("Não foi possível coletar notícias.")
    exit()
```

Na arquitetura atual, a coleta ocorre antes da execução dos agentes. As notícias são fornecidas diretamente na descrição da tarefa de pesquisa. O tool calling pertence à etapa experimental anterior, registrada no histórico de desenvolvimento.

Essa decisão estabelece uma condição determinística de entrada e impede a execução dos agentes quando nenhuma notícia foi coletada. Ela mitiga o cenário de alucinação identificado nos testes, sem depender exclusivamente de instruções ao modelo. A presença de dados reais não garante, por si só, a fidelidade factual de toda resposta gerada.

## 9. Saída estruturada com Pydantic

O módulo `schemas.py` define os modelos `Noticia` e `Boletim`.

  Campo de Noticia   Tipo / validação
  ------------------ ------------------------------------------
  titulo             str
  resumo             str
  fonte              Literal: BBC Business, CNBC ou InfoMoney
  data               str
  link               str com prefixo http:// ou https://

O modelo `Boletim` contém uma lista de objetos `Noticia`, limitada a cinco elementos por `Field(max_length=5)`.

A tarefa do analista utiliza `output_pydantic=Boletim` para definir a estrutura esperada. O fluxo principal verifica se a lista retornada contém notícias antes de armazenar o resultado.

A validação estabelece um contrato de dados para a integração externa. Ela verifica tipos, fontes permitidas, prefixo dos links e limite de elementos, não a veracidade das notícias ou a correspondência dos links com os dados originais.

### Serialização e persistência

``` python
boletim_json = resultado.pydantic.model_dump_json(indent=4)

with open("boletim.json", "w", encoding="utf-8") as arquivo:
    arquivo.write(boletim_json)
```

O JSON armazenado pode ser consumido pelo script de integração sem uma nova execução dos agentes.

Exemplo ilustrativo:

``` json
{
    "noticias": [
        {
            "titulo": "Título da notícia",
            "resumo": "Resumo em português.",
            "fonte": "BBC Business",
            "data": "Fri, 27 Nov 2026 10:00:00 GMT",
            "link": "https://example.com/noticia"
        }
    ]
}
```

## 10. Observabilidade e tratamento de falhas

A aplicação utiliza o módulo `logging` para registrar eventos em `app.log`, com data, hora, nível e mensagem. O nível configurado é `INFO`.

  ---------------------------------------------------------------------------------------------------------------------------------
  Nível                               Eventos registrados
  ----------------------------------- ---------------------------------------------------------------------------------------------
  INFO                                Inicialização, consulta às fontes, início e conclusão dos agentes, armazenamento do boletim

  WARNING                             Fonte RSS sem entradas

  ERROR                               Ausência de notícias válidas e falhas na geração do boletim
  ---------------------------------------------------------------------------------------------------------------------------------

O bloco `try/except` do fluxo principal abrange a execução da equipe, a verificação da saída, a serialização e a gravação do arquivo. `logging.exception()` registra a exceção e seu traceback. A coleta RSS ocorre antes desse bloco e possui verificações próprias de disponibilidade de entradas.

### Validação manual durante o desenvolvimento

  ----------------------------------------------------------------------------------------------------------------------------------------
  Cenário                                          Comportamento observado
  ------------------------------------------------ ---------------------------------------------------------------------------------------
  Falha simulada na execução dos agentes           Exceção e traceback registrados no log

  Fonte RSS indisponível                           Aviso registrado e consulta às demais fontes mantida

  Indisponibilidade total na arquitetura inicial   Identificação de conteúdo sem respaldo nas fontes, motivando a alteração arquitetural
  ----------------------------------------------------------------------------------------------------------------------------------------

Na implementação atual, a verificação da lista coletada impede o início da equipe quando não existem notícias. Os testes descritos são manuais, não uma suíte automatizada.

## 11. Integração e execução

Com as dependências instaladas e a variável `OPENAI_API_KEY` configurada no `.env`, executar:

``` bash
python main.py
```

O resultado é exibido no terminal e armazenado em `boletim.json`. O script de envio lê esse arquivo e realiza uma requisição HTTP POST ao webhook definido em `MAKE_WEBHOOK_URL`, com timeout de 30 segundos, exibindo o status HTTP e o corpo da resposta.

A configuração do cenário, a formatação HTML e a distribuição personalizada são descritas em [MAKE.md](MAKE.md).

## 12. Decisão de projeto

A solução separa a coleta determinística, a curadoria e síntese por IA, a validação estrutural e a distribuição do conteúdo. O CrewAI coordena as tarefas especializadas, o Python controla as condições de execução e o Pydantic estabelece o formato de comunicação com a camada de automação.
