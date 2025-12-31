"""
Script de teste para o Agente de Gestão de Custos

Execute este script para testar as funcionalidades do agente
sem precisar configurar o WhatsApp.
"""
from agents.cost_agent import create_cost_management_agent
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


def test_agent():
    """Testa o agente com queries de exemplo"""

    setup_logging()

    logger.info("🧪 Iniciando testes do Agente de Custos")
    logger.info("=" * 80)

    # Criar agente
    agent = create_cost_management_agent()

    # Testes
    test_cases = [
        {
            "name": "Adicionar Despesa - Alimentação",
            "query": "Gastei 45 reais no almoço",
            "expected": "deve adicionar custo de alimentação"
        },
        {
            "name": "Adicionar Despesa - Transporte",
            "query": "Uber 25 no pix",
            "expected": "deve adicionar custo de transporte com PIX"
        },
        {
            "name": "Adicionar Despesa - Lazer",
            "query": "Cinema 40 reais no cartão",
            "expected": "deve adicionar custo de lazer no cartão"
        },
        {
            "name": "Consultar Gastos do Mês",
            "query": "Quanto gastei esse mês?",
            "expected": "deve mostrar relatório mensal"
        },
        {
            "name": "Resumo por Categorias",
            "query": "Resumo de gastos por categoria",
            "expected": "deve mostrar resumo por categoria"
        },
        {
            "name": "Listar Gastos de Alimentação",
            "query": "Meus gastos com alimentação",
            "expected": "deve listar gastos de alimentação"
        },
        {
            "name": "Relatório Completo",
            "query": "Gerar relatório mensal completo",
            "expected": "deve gerar relatório detalhado"
        },
        {
            "name": "Análise de Tendências",
            "query": "Como foram meus gastos nos últimos 3 meses?",
            "expected": "deve mostrar tendências"
        }
    ]

    results = []

    for i, test in enumerate(test_cases, 1):
        logger.info(f"\n{'=' * 80}")
        logger.info(f"🧪 Teste {i}/{len(test_cases)}: {test['name']}")
        logger.info(f"📝 Query: {test['query']}")
        logger.info(f"✅ Esperado: {test['expected']}")
        logger.info(f"{'=' * 80}\n")

        try:
            response = agent.run(test['query'])

            logger.info("📊 RESPOSTA DO AGENTE:")
            logger.info("-" * 80)
            print(response.content)
            logger.info("-" * 80)

            results.append({
                "test": test['name'],
                "status": "✅ PASSOU",
                "query": test['query']
            })

        except Exception as e:
            logger.error(f"❌ ERRO: {e}")
            results.append({
                "test": test['name'],
                "status": "❌ FALHOU",
                "error": str(e)
            })

        logger.info("")

    # Resumo dos testes
    logger.info("\n" + "=" * 80)
    logger.info("📊 RESUMO DOS TESTES")
    logger.info("=" * 80)

    passed = sum(1 for r in results if "✅" in r['status'])
    failed = sum(1 for r in results if "❌" in r['status'])

    for result in results:
        logger.info(f"{result['status']} - {result['test']}")

    logger.info("-" * 80)
    logger.info(f"✅ Passou: {passed}/{len(test_cases)}")
    logger.info(f"❌ Falhou: {failed}/{len(test_cases)}")
    logger.info(f"📊 Taxa de sucesso: {(passed/len(test_cases)*100):.1f}%")
    logger.info("=" * 80)


def interactive_test():
    """Modo interativo para testes manuais"""

    setup_logging()

    logger.info("💬 Modo Teste Interativo - Agente de Custos")
    logger.info("Digite suas mensagens de teste (ou 'sair' para encerrar)")
    logger.info("-" * 80)

    agent = create_cost_management_agent()

    while True:
        try:
            user_input = input("\n👤 Você: ").strip()

            if user_input.lower() in ['sair', 'exit', 'quit']:
                logger.info("👋 Encerrando testes...")
                break

            if not user_input:
                continue

            response = agent.run(user_input)

            print(f"\n🤖 Agente:\n{response.content}\n")
            print("-" * 80)

        except KeyboardInterrupt:
            logger.info("\n👋 Encerrando...")
            break
        except Exception as e:
            logger.error(f"❌ Erro: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        test_agent()
