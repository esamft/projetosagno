"""
Exemplo de agente básico
"""
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from loguru import logger
from config.settings import DEFAULT_MODEL

from tools.example_tool import example_tool


def create_example_agent() -> Agent:
    """
    Cria um agente de exemplo

    Returns:
        Agent configurado e pronto para uso
    """

    agent = Agent(
        name="ExampleAgent",
        model=OpenAIChat(id=DEFAULT_MODEL),
        description="Agente de exemplo para demonstração",
        instructions=[
            "Você é um agente de exemplo do Agno Framework",
            "Sua missão é demonstrar como criar agentes",
            "Você tem acesso a ferramentas de exemplo",
            "",
            "Regras:",
            "  - Seja claro e objetivo",
            "  - Use as ferramentas disponíveis quando apropriado",
            "  - Forneça respostas úteis",
        ],
        tools=[
            example_tool,
        ],
        markdown=True,
        debug_mode=False
    )

    logger.info(f"{agent.name} criado com sucesso")
    return agent


# Para testes isolados
if __name__ == "__main__":
    agent = create_example_agent()
    response = agent.run("Olá! Teste a ferramenta de exemplo")
    print(response.content)
