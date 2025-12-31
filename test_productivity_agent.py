"""
Teste do Life OS Productivity Agent
"""
from agents.productivity_agent import create_productivity_agent
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
    print("📋 TESTE - Life OS Productivity Agent")
    print("="*80 + "\n")

    # Criar agente
    agent = create_productivity_agent()

    # Cenários de teste
    scenarios = [
        {
            "title": "1️⃣ Captura Simples - Deep Work",
            "query": "Preciso estudar matemática hoje"
        },
        {
            "title": "2️⃣ Múltiplas Tarefas",
            "query": "Tenho que finalizar o relatório, ligar pro cliente e comprar um presente"
        },
        {
            "title": "3️⃣ Tarefa no Inbox",
            "query": "Me lembra de agendar consulta no médico"
        },
        {
            "title": "4️⃣ Consulta de Agenda",
            "query": "O que tenho para hoje?"
        },
        {
            "title": "5️⃣ Visão Semanal",
            "query": "Como está minha semana?"
        }
    ]

    for scenario in scenarios:
        print("\n" + "─"*80)
        print(f"\n{scenario['title']}")
        print(f"👤 Usuário: \"{scenario['query']}\"")
        print()

        try:
            response = agent.run(scenario['query'])
            print("🤖 Productivity Agent:")
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
    print("📋 Life OS Productivity Agent - Modo Interativo")
    print("="*80)
    print("\nGestão de Tarefas e Deep Work")
    print("Digite suas mensagens (ou 'sair' para encerrar)")
    print("-" * 80)

    agent = create_productivity_agent()

    while True:
        try:
            user_input = input("\n👤 Você: ").strip()

            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("\n👋 Encerrando Productivity Agent...")
                break

            if not user_input:
                continue

            response = agent.run(user_input)
            print(f"\n🤖 Productivity Agent:\n{response.content}\n")
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
