"""
Script principal para executar análise de mercado iGaming
"""
from loguru import logger
from agents.igaming_agent import create_igaming_intelligence_agent


def main():
    """
    Executa análise completa do mercado de iGaming brasileiro
    """

    print("\n" + "="*80)
    print("🎰 AGENTE DE INTELIGÊNCIA DE MERCADO - iGAMING BRASIL")
    print("="*80 + "\n")

    logger.info("Inicializando agente especializado...")
    agent = create_igaming_intelligence_agent()

    # Query padrão
    query = """
    Realize uma análise completa e detalhada das ofertas de bônus
    das principais casas de apostas que operam legalmente no Brasil.

    Apresente os resultados em uma tabela comparativa ordenada
    do bônus mais fácil ao mais difícil de cumprir.
    """

    logger.info("Executando análise...")
    print("⏳ Processando análise de mercado...\n")

    # Executa o agente
    response = agent.run(query.strip())

    # Exibe resultado
    print("\n" + "="*80)
    print("📊 RESULTADO DA ANÁLISE")
    print("="*80 + "\n")
    print(response.content)
    print("\n" + "="*80)

    logger.info("✅ Análise concluída com sucesso!")


if __name__ == "__main__":
    main()
