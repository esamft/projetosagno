"""
Entry point do projeto Agno
"""
from loguru import logger
from agents.example_agent import create_example_agent


def main():
    """
    Função principal
    """
    logger.info("Iniciando projeto Agno...")

    # Criar agente
    agent = create_example_agent()

    # Exemplo de uso
    query = "Olá! Como você funciona?"
    logger.info(f"Executando query: {query}")

    response = agent.run(query)

    print("\n" + "="*50)
    print("RESPOSTA DO AGENTE:")
    print("="*50)
    print(response.content)
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
