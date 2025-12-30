🚀 Guia Completo: Desenvolvendo com Agno Framework



> **Guia de Referência Atualizado** - Baseado em projeto real com Agno 2.3.21+



Este documento serve como template e referência para criar projetos com o **Agno Framework** (anteriormente Phidata), incluindo todas as mudanças de API e boas práticas descobertas.



---



## 📋 Índice



1. [Mudanças Importantes da API](#mudanças-importantes-da-api)

2. [Estrutura de Projeto Recomendada](#estrutura-de-projeto-recomendada)

3. [Setup Inicial](#setup-inicial)

4. [Criando Agentes](#criando-agentes)

5. [Implementando Tools](#implementando-tools)

6. [Problemas Comuns e Soluções](#problemas-comuns-e-soluções)

7. [Boas Práticas](#boas-práticas)

8. [Checklist de Projeto](#checklist-de-projeto)



---



## 🔄 Mudanças Importantes da API



### ⚠️ CRÍTICO: Importações Corretas



**❌ ERRADO (documentação antiga):**

```python

from agno import Agent

from agno.storage.sqlite import SqliteStorage

from agno.knowledge.embedder import Embedder

```



**✅ CORRETO (Agno 2.3+):**

```python

from agno.agent import Agent

from agno.models.openai import OpenAIChat

# Storage e Knowledge foram REMOVIDOS/ALTERADOS

```



### 📦 Módulos Removidos/Alterados



| Módulo Antigo | Status | Alternativa |

|---------------|--------|-------------|

| `agno.storage.sqlite` | ❌ Removido | Não usar storage |

| `agno.knowledge.embedder` | ❌ Removido | Não usar knowledge base |

| `agno.Agent` | ✅ Mudou | `agno.agent.Agent` |

| `team` parameter | ⚠️ Removido | Usar apenas `tools` |



### 🛠️ Parâmetros do Agent



**Parâmetros VÁLIDOS (Agno 2.3+):**

```python

Agent(

    name="AgentName",                    # ✅ Nome do agente

    model=OpenAIChat(id="gpt-4o"),      # ✅ Modelo LLM

    description="...",                   # ✅ Descrição

    instructions=[...],                  # ✅ Lista de instruções

    tools=[func1, func2],               # ✅ Lista de ferramentas

    markdown=True,                       # ✅ Output em markdown

    debug_mode=False,                    # ✅ Modo debug



    # Parâmetros REMOVIDOS:

    # storage=SqliteStorage(...)        # ❌ NÃO USAR

    # knowledge=Knowledge(...)           # ❌ NÃO USAR

    # team=[agent1, agent2]             # ❌ NÃO USAR

)

```



### 🔧 Tools: Async vs Sync



**PROBLEMA CRÍTICO**: Agentes síncronos (`agent.run()`) **NÃO** aceitam tools async.



**❌ ERRADO:**

```python

async def minha_tool(param: str) -> str:

    result = await alguma_operacao_async()

    return result



agent = Agent(

    tools=[minha_tool]  # ❌ ERRO: Async function can't be used with sync agent.run()

)



agent.run("Execute algo")  # ❌ FALHA

```



**✅ CORRETO - Opção 1: Wrapper Síncrono**

```python

import asyncio



# Versão async interna

async def _minha_tool_async(param: str) -> str:

    result = await alguma_operacao_async()

    return result



# Wrapper síncrono para o agente

def minha_tool(param: str) -> str:

    """Tool síncrona que envelopa a versão async"""

    return asyncio.run(_minha_tool_async(param))



agent = Agent(

    tools=[minha_tool]  # ✅ OK: Função síncrona

)



agent.run("Execute algo")  # ✅ FUNCIONA

```



**✅ CORRETO - Opção 2: Usar arun()**

```python

async def minha_tool(param: str) -> str:

    result = await alguma_operacao_async()

    return result



agent = Agent(

    tools=[minha_tool]

)



# Use arun() para tools async

await agent.arun("Execute algo")  # ✅ FUNCIONA

```



---



## 📁 Estrutura de Projeto Recomendada



```

seu-projeto/

├── .env                        # API keys (NÃO commitar!)

├── .env.example                # Template de variáveis

├── .gitignore                  # Ignorar .env, __pycache__, etc

├── README.md                   # Documentação do projeto

├── requirements.txt            # Dependências

├── main.py                     # Entry point

│

├── config/                     # Configurações

│   ├── __init__.py

│   └── settings.py             # Configurações centralizadas

│

├── agents/                     # Agentes de IA

│   ├── __init__.py

│   ├── main_agent.py           # Agente principal

│   └── sub_agent.py            # Sub-agentes especializados

│

├── tools/                      # Ferramentas (functions)

│   ├── __init__.py

│   ├── tool_1.py               # Tool específica

│   └── tool_2.py               # Outra tool

│

├── models/                     # Modelos de dados (opcional)

│   ├── __init__.py

│   └── schemas.py              # Pydantic models

│

└── knowledge/                  # Base de conhecimento (opcional)

    └── data.json               # Dados estáticos

```



---



## 🚀 Setup Inicial



### 1. Criar Estrutura



```bash

# Criar diretórios

mkdir -p agents tools config models knowledge



# Criar arquivos vazios

touch agents/__init__.py tools/__init__.py config/__init__.py

touch .env.example .gitignore README.md

```



### 2. requirements.txt



```txt

# Agno Framework

agno>=2.3.0



# LLM Providers

openai>=1.0.0

anthropic>=0.8.0          # Opcional



# Utilities

python-dotenv>=1.0.0

pydantic>=2.5.0

loguru>=0.7.0



# Async (se necessário)

aiohttp>=3.9.0

asyncio>=3.4.3



# Adicione suas dependências específicas aqui

```



### 3. .env.example



```env

# API Keys para LLMs

OPENAI_API_KEY=your_openai_api_key_here

ANTHROPIC_API_KEY=your_anthropic_api_key_here



# Configurações

LOG_LEVEL=INFO

DEBUG_MODE=False

```



### 4. .gitignore



```gitignore

# Python

__pycache__/

*.py[cod]

*$py.class

*.so

.Python

venv/

env/



# Environment

.env

.env.local



# IDE

.vscode/

.idea/

*.swp



# Logs

*.log



# OS

.DS_Store

```



### 5. config/settings.py



```python

"""

Configurações centralizadas do projeto

"""

import os

from pathlib import Path

from dotenv import load_dotenv



# Carregar variáveis de ambiente

load_dotenv()



# Diretórios

BASE_DIR = Path(__file__).parent.parent

TOOLS_DIR = BASE_DIR / "tools"

AGENTS_DIR = BASE_DIR / "agents"



# API Keys

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")



# Configurações de modelo

DEFAULT_MODEL = "gpt-4o"  # ou "gpt-4o-mini" para economia

TEMPERATURE = 0.7



# Configurações de log

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"



# Suas configurações específicas aqui

# ...

```



---



## 🤖 Criando Agentes



### Template Básico de Agente



```python

"""

agents/my_agent.py

"""

from agno.agent import Agent

from agno.models.openai import OpenAIChat

from loguru import logger

from config.settings import DEFAULT_MODEL



# Importe suas tools

from tools.my_tool import my_tool_function





def create_my_agent() -> Agent:

    """

    Cria um agente especializado



    Returns:

        Agent configurado

    """



    agent = Agent(

        name="MySpecializedAgent",

        model=OpenAIChat(id=DEFAULT_MODEL),

        description="Breve descrição do que este agente faz",

        instructions=[

            "Você é um especialista em...",

            "Sua missão é...",

            "Você deve sempre...",

            "",

            "Regras importantes:",

            "  - Regra 1",

            "  - Regra 2",

            "  - Regra 3",

            "",

            "Ao responder:",

            "  - Formato específico",

            "  - Informações obrigatórias",

        ],

        tools=[

            my_tool_function,

            # adicione mais tools aqui

        ],

        markdown=True,

        debug_mode=False

    )



    logger.info(f"{agent.name} criado com sucesso")

    return agent





# Para testes isolados

if __name__ == "__main__":

    agent = create_my_agent()

    response = agent.run("Teste o agente aqui")

    print(response.content)

```



### Agente Orquestrador com Multiple Tools



```python

"""

agents/orchestrator.py

"""

from agno.agent import Agent

from agno.models.openai import OpenAIChat

from tools.tool_1 import tool_1_func

from tools.tool_2 import tool_2_func

from tools.tool_3 import tool_3_func





class OrchestratorAgent:

    """Agente principal que coordena múltiplas tools"""



    def __init__(self):

        self.agent = self._create_agent()



    def _create_agent(self) -> Agent:

        return Agent(

            name="Orchestrator",

            model=OpenAIChat(id="gpt-4o"),

            description="Orquestra múltiplas ferramentas",

            instructions=[

                "Você coordena várias ferramentas especializadas",

                "Analise a solicitação do usuário",

                "Escolha as ferramentas apropriadas",

                "Consolide os resultados",

            ],

            tools=[

                tool_1_func,

                tool_2_func,

                tool_3_func,

            ],

            markdown=True

        )



    def execute(self, query: str) -> str:

        """Executa uma query"""

        response = self.agent.run(query)

        return response.content





def create_orchestrator() -> OrchestratorAgent:

    """Factory function"""

    return OrchestratorAgent()

```



---



## 🛠️ Implementando Tools



### Tool Síncrona Simples



```python

"""

tools/simple_tool.py

"""

from typing import Optional



def simple_tool(param: str, optional_param: Optional[str] = None) -> str:

    """

    Descrição clara do que a tool faz



    Esta docstring é importante! O agente a usa para entender

    quando e como usar esta ferramenta.



    Args:

        param: Descrição do parâmetro obrigatório

        optional_param: Descrição do parâmetro opcional



    Returns:

        Descrição do retorno

    """

    result = f"Processando {param}"



    if optional_param:

        result += f" com {optional_param}"



    return result

```



### Tool com Operações Async (Wrapper Pattern)



```python

"""

tools/async_tool.py

"""

import asyncio

import httpx

from typing import Dict, Any





# Versão async interna (não exposta ao agente)

async def _fetch_data_async(url: str) -> Dict[str, Any]:

    """Implementação async interna"""

    async with httpx.AsyncClient() as client:

        response = await client.get(url)

        return response.json()





# Wrapper síncrono para o agente

def fetch_data(url: str) -> str:

    """

    Busca dados de uma URL



    Args:

        url: URL para fazer request



    Returns:

        JSON string com os dados

    """

    import json

    result = asyncio.run(_fetch_data_async(url))

    return json.dumps(result, ensure_ascii=False, indent=2)

```



### Tool com Playwright/Scraping



```python

"""

tools/web_scraper.py

"""

import asyncio

import json

from playwright.async_api import async_playwright

from typing import Dict





async def _scrape_async(url: str) -> Dict:

    """Scraping async interno"""

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.goto(url)



        # Seu scraping aqui

        title = await page.title()



        await browser.close()

        return {"title": title, "url": url}





def scrape_website(url: str) -> str:

    """

    Faz scraping de um website



    Args:

        url: URL do site



    Returns:

        JSON com dados extraídos

    """

    result = asyncio.run(_scrape_async(url))

    return json.dumps(result, ensure_ascii=False, indent=2)

```



### Tool com Validação Pydantic



```python

"""

tools/validated_tool.py

"""

from pydantic import BaseModel, Field, validator

from typing import Optional

import json





class InputData(BaseModel):

    """Schema de validação"""

    name: str = Field(..., min_length=1, max_length=100)

    age: int = Field(..., ge=0, le=150)

    email: Optional[str] = None



    @validator('email')

    def validate_email(cls, v):

        if v and '@' not in v:

            raise ValueError('Email inválido')

        return v





def process_user_data(name: str, age: int, email: Optional[str] = None) -> str:

    """

    Processa dados do usuário com validação



    Args:

        name: Nome do usuário

        age: Idade do usuário

        email: Email opcional



    Returns:

        Resultado do processamento

    """

    try:

        # Valida os dados

        data = InputData(name=name, age=age, email=email)



        # Processa

        result = {

            "status": "success",

            "data": data.dict(),

            "message": f"Processado {name} com sucesso"

        }



        return json.dumps(result, ensure_ascii=False, indent=2)



    except Exception as e:

        return json.dumps({

            "status": "error",

            "message": str(e)

        }, ensure_ascii=False, indent=2)

```



---



## 🐛 Problemas Comuns e Soluções



### 1. ImportError: cannot import name 'Agent'



**Erro:**

```

ImportError: cannot import name 'Agent' from 'agno'

```



**Solução:**

```python

# ❌ ERRADO

from agno import Agent



# ✅ CORRETO

from agno.agent import Agent

```



### 2. Async function can't be used with sync agent.run()



**Erro:**

```

Error in Agent run: Async function my_tool can't be used with synchronous agent.run()

```



**Solução:** Use wrapper síncrono (veja seção de Tools)



### 3. ModuleNotFoundError: No module named 'agno.storage'



**Erro:**

```

ModuleNotFoundError: No module named 'agno.storage'

```



**Solução:** Remova uso de storage - não está disponível em Agno 2.3+



### 4. Agent não usa as tools



**Problema:** Agente não chama as ferramentas disponíveis



**Causas Comuns:**

1. Docstring da tool mal escrita ou ausente

2. Instruções do agente não mencionam as tools

3. Tools com nomes confusos



**Solução:**

```python

def my_tool(param: str) -> str:

    """

    ✅ DOCSTRING CLARA E DESCRITIVA



    Explique claramente:

    - O que a tool faz

    - Quando usar

    - O que retorna



    Args:

        param: Seja específico sobre o parâmetro



    Returns:

        Descreva o formato do retorno

    """

    pass



# Nas instruções do agente:

instructions=[

    "Você tem acesso à ferramenta my_tool",

    "Use my_tool quando precisar fazer X",

    "A ferramenta retorna Y",

]

```



### 5. JSON Parse Errors



**Problema:** Agente retorna JSON malformado



**Solução:** Use `json.dumps()` com configurações adequadas

```python

import json



result = json.dumps(

    data,

    ensure_ascii=False,  # Mantém caracteres UTF-8

    indent=2,            # Formatação legível

    default=str          # Fallback para tipos não-serializáveis

)

```



---



## ✅ Boas Práticas



### 1. Organização de Código



```python

# ✅ BOM: Factory functions para agentes

def create_my_agent() -> Agent:

    return Agent(...)



# ✅ BOM: Classes para agentes complexos

class MyComplexAgent:

    def __init__(self):

        self.agent = self._create_agent()



    def execute(self, query: str) -> str:

        return self.agent.run(query).content

```



### 2. Logging



```python

from loguru import logger



# Configure no início

logger.add(

    "logs/app.log",

    rotation="500 MB",

    level="INFO"

)



# Use em todo o código

logger.info("Agente inicializado")

logger.error(f"Erro ao processar: {e}")

logger.debug(f"Debug info: {data}")

```



### 3. Type Hints



```python

from typing import List, Dict, Optional, Any



# ✅ Use type hints sempre

def my_function(

    param1: str,

    param2: int,

    optional: Optional[str] = None

) -> Dict[str, Any]:

    return {"result": "data"}

```



### 4. Documentação de Tools



```python

def excellent_tool(param: str) -> str:

    """

    ✅ EXCELENTE DOCSTRING



    [O QUE FAZ]

    Esta ferramenta busca informações sobre X no sistema Y.



    [QUANDO USAR]

    Use quando o usuário perguntar sobre X ou precisar de dados de Y.



    [EXEMPLO]

    Input: "computador"

    Output: {"name": "Computador", "price": 1000}



    Args:

        param: Nome do item para buscar (string, case-insensitive)



    Returns:

        JSON string com informações do item encontrado



    Raises:

        ValueError: Se o item não for encontrado

    """

    pass

```



### 5. Tratamento de Erros



```python

def safe_tool(param: str) -> str:

    """Tool com tratamento robusto de erros"""

    try:

        # Operação principal

        result = process_something(param)



        return json.dumps({

            "status": "success",

            "data": result

        })



    except ValueError as e:

        logger.warning(f"Valor inválido: {e}")

        return json.dumps({

            "status": "error",

            "error_type": "ValueError",

            "message": str(e)

        })



    except Exception as e:

        logger.error(f"Erro inesperado: {e}")

        return json.dumps({

            "status": "error",

            "error_type": "UnexpectedError",

            "message": "Erro ao processar solicitação"

        })

```



### 6. Configuração de Modelos



```python

# ✅ Centralize configurações

from config.settings import DEFAULT_MODEL



# Para tarefas simples: use modelo mais barato

agent_simple = Agent(

    model=OpenAIChat(id="gpt-4o-mini"),

    # ...

)



# Para tarefas complexas: use modelo mais potente

agent_complex = Agent(

    model=OpenAIChat(id="gpt-4o"),

    # ...

)

```



---



## 📝 Checklist de Projeto



### Setup Inicial

- [ ] Estrutura de diretórios criada

- [ ] `requirements.txt` com dependências corretas

- [ ] `.env.example` criado

- [ ] `.gitignore` configurado

- [ ] `config/settings.py` implementado



### Agentes

- [ ] Imports corretos (`from agno.agent import Agent`)

- [ ] Modelo especificado (`OpenAIChat(id=...)`)

- [ ] `description` clara

- [ ] `instructions` detalhadas e específicas

- [ ] `tools` listadas corretamente

- [ ] Factory function ou classe implementada

- [ ] Logging adicionado



### Tools

- [ ] Docstrings completas e descritivas

- [ ] Type hints em todos os parâmetros

- [ ] Retorno sempre em formato consistente (JSON string)

- [ ] Tools async têm wrapper síncrono

- [ ] Tratamento de erros robusto

- [ ] Testes isolados funcionando



### Testes

- [ ] Cada tool testada isoladamente

- [ ] Agente testado com queries reais

- [ ] Edge cases considerados

- [ ] Erros tratados graciosamente



### Documentação

- [ ] README.md com instruções de uso

- [ ] Comentários em código complexo

- [ ] Exemplos de uso fornecidos

- [ ] Variáveis de ambiente documentadas



### Produção

- [ ] API keys não commitadas

- [ ] Logs configurados adequadamente

- [ ] Error handling em todos os pontos críticos

- [ ] Performance otimizada (modelos adequados)



---



## 🎯 Exemplo Completo Mínimo



```

minimal-agno-project/

├── .env

├── .env.example

├── requirements.txt

├── main.py

├── config/

│   └── settings.py

├── tools/

│   └── my_tool.py

└── agents/

    └── my_agent.py

```



**requirements.txt:**

```txt

agno>=2.3.0

openai>=1.0.0

python-dotenv>=1.0.0

loguru>=0.7.0

```



**main.py:**

```python

from agents.my_agent import create_my_agent



def main():

    agent = create_my_agent()

    response = agent.run("Execute tarefa X")

    print(response.content)



if __name__ == "__main__":

    main()

```



---



## 📚 Recursos Adicionais



- **Documentação Oficial Agno**: https://docs.agno.com (se disponível)

- **Exemplos de Código**: Ver diretório `examples/` deste projeto

- **Issues Comuns**: Ver seção "Problemas Comuns" acima



---



## 🔄 Histórico de Versões deste Guia



- **v1.0** (2025-12-30): Versão inicial baseada em Agno 2.3.21

  - Documentadas mudanças críticas de API

  - Padrões async/sync estabelecidos

  - Template completo de projeto



---



## 📞 Suporte



Se encontrar problemas não documentados aqui:

1. Verifique a versão do Agno: `pip show agno`

2. Revise todos os imports

3. Confirme que tools são síncronas ou têm wrappers

4. Verifique logs para mensagens de erro detalhadas



---



**Este guia é baseado em experiência real de projeto e será atualizado conforme novas descobertas.**



💡 **Dica Final**: Sempre teste seus agentes e tools isoladamente antes de integrar ao projeto completo!