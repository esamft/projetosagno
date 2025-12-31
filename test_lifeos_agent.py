"""
Script de Teste - Life OS Financial Agent

Testa todas as funcionalidades do agente financeiro.
"""
from agents.lifeos_financial_agent import create_lifeos_financial_agent
from loguru import logger
import sys


def setup_logging():
    """Configura logging"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )


def test_lifeos_agent():
    """Testa o Life OS Financial Agent"""

    setup_logging()

    logger.info("💰 Iniciando testes do Life OS Financial Agent")
    logger.info("=" * 80)

    # Criar agente
    agent = create_lifeos_financial_agent()

    # Cenários de teste
    test_scenarios = [
        {
            "name": "Registro Simples - Pix",
            "query": "Gastei 45 no almoço no pix",
            "expected": "Deve registrar R$ 45 em Alimentação via Pix"
        },
        {
            "name": "Registro Simples - Transporte",
            "query": "Uber de 25 reais",
            "expected": "Deve inferir Transporte e perguntar tipo de pagamento"
        },
        {
            "name": "Parcelamento - Compra Grande",
            "query": "Comprei um celular de 1200 em 10x no crédito",
            "expected": "Deve registrar 10 parcelas de R$ 120"
        },
        {
            "name": "Parcelamento - Formato Alternativo",
            "query": "Comprei uma TV, 12 parcelas de 100 reais no cartão",
            "expected": "Deve registrar R$ 1200 em 12x"
        },
        {
            "name": "Informação Incompleta",
            "query": "Gastei no posto",
            "expected": "Deve perguntar o valor"
        },
        {
            "name": "Consulta de Resumo",
            "query": "Quanto gastei esse mês?",
            "expected": "Deve mostrar resumo mensal"
        },
        {
            "name": "Consulta de Futuro",
            "query": "Posso fazer uma compra parcelada no mês que vem?",
            "expected": "Deve analisar compromissos futuros e dar veredito"
        },
        {
            "name": "Análise de Impacto",
            "query": "Como está meu orçamento?",
            "expected": "Deve mostrar status atual com alertas"
        }
    ]

    results = []

    for i, scenario in enumerate(test_scenarios, 1):
        logger.info(f"\n{'=' * 80}")
        logger.info(f"🧪 Teste {i}/{len(test_scenarios)}: {scenario['name']}")
        logger.info(f"📝 Query: {scenario['query']}")
        logger.info(f"✅ Esperado: {scenario['expected']}")
        logger.info(f"{'=' * 80}\n")

        try:
            response = agent.run(scenario['query'])

            logger.info("📊 RESPOSTA DO AGENTE:")
            logger.info("-" * 80)
            print(response.content)
            logger.info("-" * 80)

            results.append({
                "test": scenario['name'],
                "status": "✅ PASSOU",
                "query": scenario['query']
            })

        except Exception as e:
            logger.error(f"❌ ERRO: {e}")
            results.append({
                "test": scenario['name'],
                "status": "❌ FALHOU",
                "error": str(e)
            })

        logger.info("")

    # Resumo
    logger.info("\n" + "=" * 80)
    logger.info("📊 RESUMO DOS TESTES")
    logger.info("=" * 80)

    passed = sum(1 for r in results if "✅" in r['status'])
    failed = sum(1 for r in results if "❌" in r['status'])

    for result in results:
        logger.info(f"{result['status']} - {result['test']}")

    logger.info("-" * 80)
    logger.info(f"✅ Passou: {passed}/{len(test_scenarios)}")
    logger.info(f"❌ Falhou: {failed}/{len(test_scenarios)}")
    logger.info(f"📊 Taxa de sucesso: {(passed/len(test_scenarios)*100):.1f}%")
    logger.info("=" * 80)


def interactive_mode():
    """Modo interativo - conversa com o agente"""

    setup_logging()

    logger.info("💬 Life OS Financial Agent - Modo Interativo")
    logger.info("Digite suas mensagens (ou 'sair' para encerrar)")
    logger.info("-" * 80)

    agent = create_lifeos_financial_agent()

    while True:
        try:
            user_input = input("\n👤 Você: ").strip()

            if user_input.lower() in ['sair', 'exit', 'quit']:
                logger.info("👋 Encerrando Life OS...")
                break

            if not user_input:
                continue

            response = agent.run(user_input)

            print(f"\n🤖 Life OS:\n{response.content}\n")
            print("-" * 80)

        except KeyboardInterrupt:
            logger.info("\n👋 Encerrando...")
            break
        except Exception as e:
            logger.error(f"❌ Erro: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        test_lifeos_agent()
