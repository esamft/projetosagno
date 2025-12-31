"""
Demonstração do Sistema Multi-Agente Life OS

Mostra o orquestrador direcionando mensagens para agentes especializados.
"""
from lifeos_router import LifeOSRouter
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


def demo_automatic():
    """Demonstração automática com cenários pré-definidos"""

    print("\n" + "="*80)
    print("🎯 DEMONSTRAÇÃO - Sistema Multi-Agente Life OS")
    print("="*80)
    print("\n📋 Cenários de Teste:\n")

    # Criar router
    router = LifeOSRouter()

    # Cenários organizados por categoria
    scenarios = {
        "💰 Finanças": [
            "Gastei 50 reais no almoço no pix",
            "Comprei um notebook de 2400 em 12x no crédito",
            "Quanto gastei esse mês?",
            "Posso fazer uma compra parcelada no próximo mês?",
        ],
        "📋 Produtividade": [
            "Preciso estudar matemática hoje",
            "Me lembra de ligar pro médico",
            "O que tenho para hoje?",
        ],
        "💬 Conversa Geral": [
            "Oi, tudo bem?",
            "Obrigado pela ajuda!",
            "Como você funciona?",
        ]
    }

    for category, messages in scenarios.items():
        print(f"\n{'─'*80}")
        print(f"{category}")
        print(f"{'─'*80}\n")

        for message in messages:
            print(f"👤 Usuário: \"{message}\"")
            print()

            try:
                result = router.route_message(message)

                print(f"   🎯 Roteado para: {result['agent_used']}")
                print(f"   💭 Raciocínio: {result['reasoning']}")
                print(f"\n   🤖 Life OS:")

                # Indentar resposta
                response_lines = result['response'].split('\n')
                for line in response_lines:
                    print(f"   {line}")

                print()

            except Exception as e:
                print(f"   ❌ Erro: {e}\n")

    print("\n" + "="*80)
    print("✅ Demonstração Concluída!")
    print("="*80 + "\n")


def demo_interactive():
    """Modo interativo - conversa com o sistema"""

    setup_logging()

    print("\n" + "="*80)
    print("💬 Life OS - Modo Interativo Multi-Agente")
    print("="*80)
    print("\nO sistema vai rotear automaticamente para o agente certo!")
    print("Digite suas mensagens (ou 'sair' para encerrar)")
    print("-" * 80)

    router = LifeOSRouter()

    while True:
        try:
            user_input = input("\n👤 Você: ").strip()

            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("\n👋 Encerrando Life OS...")
                break

            if not user_input:
                continue

            result = router.route_message(user_input)

            print(f"\n🎯 [{result['agent_used']}] {result['reasoning']}")
            print(f"\n🤖 Life OS:\n{result['response']}\n")
            print("-" * 80)

        except KeyboardInterrupt:
            print("\n\n👋 Encerrando...")
            break
        except Exception as e:
            logger.error(f"❌ Erro: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        demo_interactive()
    else:
        setup_logging()
        demo_automatic()
