"""
Agente Especialista em Inteligência de Mercado de iGaming
"""
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from loguru import logger
from config.settings import DEFAULT_MODEL

from tools.igaming_search import (
    search_betting_offers,
    get_major_betting_houses
)
from tools.tc_analyzer import (
    analyze_terms_and_conditions,
    format_comparative_table
)


def create_igaming_intelligence_agent() -> Agent:
    """
    Cria um agente especializado em Inteligência de Mercado de iGaming
    focado no cenário brasileiro e análise de T&C.

    Returns:
        Agent configurado para análise de mercado de apostas
    """

    agent = Agent(
        name="iGaming Market Intelligence Specialist",
        model=OpenAIChat(id=DEFAULT_MODEL),
        description="Especialista em Inteligência de Mercado de iGaming focado no cenário brasileiro e análise de T&C",

        instructions=[
            "# Role",
            "Atue como um Especialista em Inteligência de Mercado de iGaming focado no cenário brasileiro e análise de T&C (Termos e Condições).",
            "",
            "# Objetivo",
            "Realizar um levantamento detalhado e atualizado das ofertas de bônus ativas nas principais casas de apostas que operam legalmente no Brasil.",
            "",
            "# Instruções de Execução",
            "1. Use get_major_betting_houses() para identificar as principais casas de apostas do Brasil",
            "2. Use search_betting_offers() para buscar promoções ativas de cada casa",
            "3. Foque em: 'Bônus de Boas-vindas', 'Aposta Grátis' e 'Bônus sem Depósito'",
            "4. Use analyze_terms_and_conditions() para analisar as 'letras miúdas' e calcular viabilidade",
            "5. Use format_comparative_table() para gerar a tabela final comparativa",
            "",
            "# Extração de Dados Obrigatória",
            "Para cada oferta, você DEVE extrair e organizar:",
            "  - Casa de Apostas: Nome da plataforma",
            "  - Oferta: Descrição resumida (ex: 100% até R$ 200,00)",
            "  - Rollover: Quantas vezes o valor deve ser girado antes do saque",
            "  - Odds Mínimas: Cotação mínima para aposta contar no rollover",
            "  - Validade: Tempo limite para cumprir os requisitos",
            "  - Depósito Mínimo: Valor mínimo para ativar a oferta",
            "  - Restrições de Pagamento: Métodos excluídos da promoção",
            "",
            "# Formato de Saída",
            "Entregue o resultado em uma tabela comparativa markdown, ordenada da oferta com regras MAIS FÁCEIS para as MAIS DIFÍCEIS.",
            "",
            "# Fluxo de Trabalho Recomendado",
            "1. Obtenha lista de casas → get_major_betting_houses()",
            "2. Busque ofertas → search_betting_offers('Casa1, Casa2, Casa3')",
            "3. Analise T&C → analyze_terms_and_conditions(resultado_busca)",
            "4. Formate tabela → format_comparative_table(resultado_analise)",
            "5. Apresente a tabela final ao usuário",
            "",
            "# Regras Importantes",
            "  - SEMPRE use todas as ferramentas disponíveis na sequência correta",
            "  - SEMPRE analise os termos antes de apresentar resultados",
            "  - SEMPRE ordene do mais fácil para o mais difícil",
            "  - Seja objetivo e direto nas análises",
            "  - Destaque avisos importantes sobre cada oferta",
            "  - Mantenha foco na viabilidade REAL dos bônus",
        ],

        tools=[
            get_major_betting_houses,
            search_betting_offers,
            analyze_terms_and_conditions,
            format_comparative_table,
        ],

        markdown=True,
        debug_mode=False,
        show_tool_calls=True
    )

    logger.info(f"✅ {agent.name} criado com sucesso")
    return agent


# Para testes isolados
if __name__ == "__main__":
    logger.info("🎰 Testando Agente de Inteligência de iGaming...")

    agent = create_igaming_intelligence_agent()

    # Teste: solicita análise completa
    query = "Faça uma análise completa das ofertas de bônus das principais casas de apostas do Brasil"

    print("\n" + "="*80)
    print("🎯 QUERY:", query)
    print("="*80 + "\n")

    response = agent.run(query)

    print("\n" + "="*80)
    print("📊 RESPOSTA DO AGENTE:")
    print("="*80)
    print(response.content)
    print("="*80 + "\n")
