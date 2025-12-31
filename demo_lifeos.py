"""
Demonstração do Life OS Financial Agent
"""
from agents.lifeos_financial_agent import create_lifeos_financial_agent
from loguru import logger
import sys

# Configurar logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <cyan>{message}</cyan>",
    level="INFO"
)

def demo():
    """Demonstração automática do agente"""

    print("\n" + "="*80)
    print("💰 DEMONSTRAÇÃO - Life OS Financial Agent")
    print("="*80 + "\n")

    # Criar agente
    agent = create_lifeos_financial_agent()

    # Cenários de demonstração
    scenarios = [
        {
            "title": "1️⃣ Registro Simples - Almoço no Pix",
            "query": "Gastei 50 reais no almoço no pix"
        },
        {
            "title": "2️⃣ Compra Parcelada - iPhone 10x",
            "query": "Comprei um iPhone de 3000 em 10x no crédito"
        },
        {
            "title": "3️⃣ Transporte - Uber",
            "query": "Gastei 25 de uber no débito"
        },
        {
            "title": "4️⃣ Consulta de Resumo Mensal",
            "query": "Quanto gastei esse mês?"
        },
        {
            "title": "5️⃣ Análise de Futuro",
            "query": "Posso fazer uma compra parcelada no próximo mês?"
        }
    ]

    for scenario in scenarios:
        print("\n" + "─"*80)
        print(f"\n{scenario['title']}")
        print(f"👤 Usuário: \"{scenario['query']}\"")
        print()

        try:
            response = agent.run(scenario['query'])
            print("🤖 Life OS:")
            print(response.content)
        except Exception as e:
            print(f"❌ Erro: {e}")

        print()

    print("\n" + "="*80)
    print("✅ Demonstração Concluída!")
    print("="*80 + "\n")

if __name__ == "__main__":
    demo()
