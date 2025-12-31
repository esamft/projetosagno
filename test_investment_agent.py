"""
Teste do Life OS Investment Agent
"""
from agents.investment_agent import create_investment_agent
from loguru import logger
import sys


def setup_logging():
    """Configura logging"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <cyan>{message}</cyan>",
        level="INFO"
    )


def test_automatic():
    """Teste automático com cenários pré-definidos"""

    print("\n" + "="*80)
    print("💎 TESTE - Life OS Investment Agent")
    print("="*80 + "\n")

    # Criar agente
    agent = create_investment_agent()

    # Cenários de teste
    scenarios = [
        {
            "title": "1️⃣ Consulta de Patrimônio",
            "query": "Quanto eu tenho de patrimônio?"
        },
        {
            "title": "2️⃣ Oráculo de Aporte",
            "query": "Tenho 5 mil para investir, onde coloco?"
        },
        {
            "title": "3️⃣ Atualização de Saldo Manual",
            "query": "Atualize meu Tesouro IPCA+ para 50 mil"
        },
        {
            "title": "4️⃣ Consulta de Detalhes de Ativo",
            "query": "Como está minha carteira de ações?"
        },
        {
            "title": "5️⃣ Consulta Estratégica",
            "query": "Vale a pena investir em ações agora?"
        }
    ]

    for scenario in scenarios:
        print("\n" + "─"*80)
        print(f"\n{scenario['title']}")
        print(f"👤 Usuário: \"{scenario['query']}\"")
        print()

        try:
            response = agent.run(scenario['query'])
            print("🤖 Investment Agent:")
            print(response.content)
        except Exception as e:
            print(f"❌ Erro: {e}")

        print()

    print("\n" + "="*80)
    print("✅ Teste Concluído!")
    print("="*80 + "\n")


def test_interactive():
    """Modo interativo - conversa com o agente"""

    setup_logging()

    print("\n" + "="*80)
    print("💎 Life OS Investment Agent - Modo Interativo")
    print("="*80)
    print("\nGestor de Patrimônio e Wealth Manager")
    print("Digite suas mensagens (ou 'sair' para encerrar)")
    print("-" * 80)

    agent = create_investment_agent()

    while True:
        try:
            user_input = input("\n👤 Você: ").strip()

            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("\n👋 Encerrando Investment Agent...")
                break

            if not user_input:
                continue

            response = agent.run(user_input)
            print(f"\n🤖 Investment Agent:\n{response.content}\n")
            print("-" * 80)

        except KeyboardInterrupt:
            print("\n\n👋 Encerrando...")
            break
        except Exception as e:
            logger.error(f"❌ Erro: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        test_interactive()
    else:
        setup_logging()
        test_automatic()
