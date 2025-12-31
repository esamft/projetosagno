"""
Life OS - Sistema de Roteamento Multi-Agente

Orquestra múltiplos agentes especializados usando um router central.
"""
import json
from typing import Dict, Any
from loguru import logger

from agents.orchestrator_agent import create_orchestrator_agent
from agents.lifeos_financial_agent import create_lifeos_financial_agent
from agents.productivity_agent import create_productivity_agent
from agents.investment_agent import create_investment_agent


class LifeOSRouter:
    """
    Sistema de roteamento do Life OS

    Fluxo:
    1. Usuário envia mensagem
    2. Orquestrador analisa e classifica
    3. Router direciona para agente especializado
    4. Agente processa e retorna resposta
    """

    def __init__(self):
        """Inicializa router e agentes"""
        logger.info("🚀 Iniciando Life OS Router...")

        # Criar orquestrador
        self.orchestrator = create_orchestrator_agent()
        logger.info("✅ Orquestrador criado")

        # Criar agentes especializados
        self.agents = {
            "finance_agent": create_lifeos_financial_agent(),
            "productivity_agent": create_productivity_agent(),
            "investment_agent": create_investment_agent(),
            # Outros agentes podem ser adicionados aqui
        }
        logger.info(f"✅ {len(self.agents)} agente(s) especializado(s) carregado(s)")

    def route_message(self, message: str) -> Dict[str, Any]:
        """
        Roteia mensagem para o agente apropriado

        Args:
            message: Mensagem do usuário

        Returns:
            Dict com:
            - agent_used: Nome do agente que processou
            - intent: Intenção identificada
            - response: Resposta do agente
        """
        try:
            # 1. Classificar intenção com orquestrador
            logger.info(f"📝 Analisando mensagem: '{message}'")
            orchestrator_response = self.orchestrator.run(message)

            # 2. Parsear JSON de classificação
            try:
                # Limpar possível markdown
                content = orchestrator_response.content.strip()
                if content.startswith("```json"):
                    content = content.split("```json")[1].split("```")[0].strip()
                elif content.startswith("```"):
                    content = content.split("```")[1].split("```")[0].strip()

                classification = json.loads(content)
                intent = classification.get("intent")
                reasoning = classification.get("reasoning", "")

                logger.info(f"🎯 Intent: {intent} | Reasoning: {reasoning}")

            except json.JSONDecodeError as e:
                logger.error(f"❌ Erro ao parsear JSON do orquestrador: {e}")
                logger.error(f"Resposta recebida: {orchestrator_response.content}")
                # Fallback: tentar identificar manualmente
                intent = self._fallback_classification(message)
                reasoning = "Fallback classification"

            # 3. Rotear para agente apropriado
            if intent == "finance_agent":
                agent = self.agents.get("finance_agent")
                if agent:
                    logger.info("💰 Roteando para Finance Agent...")
                    response = agent.run(message)
                    return {
                        "agent_used": "finance_agent",
                        "intent": intent,
                        "reasoning": reasoning,
                        "response": response.content
                    }

            elif intent == "productivity_agent":
                agent = self.agents.get("productivity_agent")
                if agent:
                    logger.info("📋 Roteando para Productivity Agent...")
                    response = agent.run(message)
                    return {
                        "agent_used": "productivity_agent",
                        "intent": intent,
                        "reasoning": reasoning,
                        "response": response.content
                    }

            elif intent == "investment_agent":
                agent = self.agents.get("investment_agent")
                if agent:
                    logger.info("💰 Roteando para Investment Agent...")
                    response = agent.run(message)
                    return {
                        "agent_used": "investment_agent",
                        "intent": intent,
                        "reasoning": reasoning,
                        "response": response.content
                    }

            elif intent == "ask_user":
                # Orquestrador está em dúvida e quer perguntar
                logger.info("❓ Mensagem ambígua - pedindo clarificação")
                question = classification.get("question", "Pode especificar melhor o que você precisa?")
                return {
                    "agent_used": "ask_user",
                    "intent": intent,
                    "reasoning": reasoning,
                    "response": self._ask_clarification(message, question)
                }

            elif intent == "general_chat":
                logger.info("💬 Resposta genérica")
                return {
                    "agent_used": "general_chat",
                    "intent": intent,
                    "reasoning": reasoning,
                    "response": self._general_response(message)
                }

            else:
                logger.warning(f"⚠️ Intent desconhecido: {intent}")
                return {
                    "agent_used": "unknown",
                    "intent": intent,
                    "reasoning": reasoning,
                    "response": "Desculpe, não entendi sua solicitação. Pode reformular?"
                }

        except Exception as e:
            logger.error(f"❌ Erro no roteamento: {e}")
            return {
                "agent_used": "error",
                "intent": "error",
                "reasoning": "System error",
                "response": "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente."
            }

    def _fallback_classification(self, message: str) -> str:
        """
        Classificação de fallback quando o orquestrador falha

        Args:
            message: Mensagem do usuário

        Returns:
            Intent estimado
        """
        message_lower = message.lower()

        # Palavras-chave financeiras
        finance_keywords = [
            'gastar', 'gastei', 'comprar', 'comprei', 'pagar', 'paguei',
            'r$', 'real', 'reais', 'dinheiro', 'preço', 'caro', 'barato',
            'pix', 'cartão', 'débito', 'crédito', 'parcela', 'orçamento',
            'quanto', 'saldo', 'dívida', 'economia'
        ]

        # Palavras-chave de produtividade
        productivity_keywords = [
            'tarefa', 'fazer', 'trabalho', 'estudar', 'reunião',
            'lembrar', 'lembrete', 'prazo', 'deadline', 'agenda',
            'compromisso', 'pomodoro', 'foco'
        ]

        # Palavras-chave de investimentos
        investment_keywords = [
            'investir', 'investimento', 'patrimônio', 'carteira', 'aportar', 'aporte',
            'ações', 'ação', 'tesouro', 'renda fixa', 'cripto', 'bitcoin', 'btc',
            'petr4', 'vale3', 'wege3', 'ipca', 'cdb', 'fundo', 'fundos',
            'rebalancear', 'rebalanceamento', 'alocação', 'rentabilidade',
            'cotação', 'bolsa', 'b3'
        ]

        # Palavras vagas que indicam ambiguidade
        ambiguous_keywords = [
            'quanto eu tenho', 'tenho quanto', 'meu saldo', 'atualiza', 'posso comprar'
        ]

        # Verificar se é ambíguo
        if any(keyword in message_lower for keyword in ambiguous_keywords):
            # Sem contexto suficiente para decidir
            return "ask_user"

        # Verificar investimentos (prioridade 1)
        if any(keyword in message_lower for keyword in investment_keywords):
            return "investment_agent"

        # Verificar financeiro (prioridade 2)
        if any(keyword in message_lower for keyword in finance_keywords):
            return "finance_agent"

        # Verificar produtividade (prioridade 3)
        if any(keyword in message_lower for keyword in productivity_keywords):
            return "productivity_agent"

        # Padrão: general chat
        return "general_chat"

    def _ask_clarification(self, original_message: str, question: str) -> str:
        """
        Pede clarificação ao usuário quando há ambiguidade

        Args:
            original_message: Mensagem original do usuário
            question: Pergunta de clarificação gerada pelo orquestrador

        Returns:
            Mensagem pedindo clarificação
        """
        return f"""❓ **Preciso de mais detalhes:**

{question}

**Opções:**
💰 **Finanças** - Gastos do dia a dia, compras, contas
📋 **Produtividade** - Tarefas, agenda, compromissos
💎 **Investimentos** - Patrimônio, aportes, carteira

Por favor, especifique melhor o que você precisa."""

    def _general_response(self, message: str) -> str:
        """
        Resposta para conversas gerais

        Args:
            message: Mensagem do usuário

        Returns:
            Resposta apropriada
        """
        message_lower = message.lower()

        # Saudações
        if any(word in message_lower for word in ['oi', 'olá', 'ola', 'hey', 'bom dia', 'boa tarde', 'boa noite']):
            return "👋 Olá! Sou seu assistente Life OS. Posso ajudar com:\n\n💰 **Finanças**: Registrar gastos, consultar orçamento\n📋 **Produtividade**: Gerenciar tarefas e tempo\n💎 **Investimentos**: Gestão de patrimônio e aportes\n\nComo posso ajudar?"

        # Agradecimentos
        if any(word in message_lower for word in ['obrigado', 'obrigada', 'valeu', 'thanks']):
            return "😊 Por nada! Estou aqui sempre que precisar."

        # Despedidas
        if any(word in message_lower for word in ['tchau', 'até', 'falou', 'bye']):
            return "👋 Até logo! Qualquer coisa, é só chamar."

        # Ajuda
        if any(word in message_lower for word in ['ajuda', 'help', 'como funciona']):
            return """📖 **Como usar o Life OS:**

💰 **Finanças**:
- "Gastei 50 no almoço"
- "Quanto gastei esse mês?"
- "Posso comprar X parcelado?"

📋 **Produtividade** (em breve):
- "Me lembra de..."
- "Quais minhas tarefas?"
- "Adicionar tarefa..."

Digite sua solicitação!"""

        # Padrão
        return "Não entendi muito bem. Você quer registrar um gasto ou gerenciar tarefas?"


def main():
    """Demonstração do sistema de roteamento"""
    print("\n" + "="*80)
    print("🚀 Life OS - Sistema de Roteamento Multi-Agente")
    print("="*80 + "\n")

    # Criar router
    router = LifeOSRouter()

    # Mensagens de teste
    test_messages = [
        "Oi, tudo bem?",
        "Gastei 50 no almoço no pix",
        "Quanto gastei esse mês?",
        "Preciso estudar para a prova",
        "Comprei um iPhone de 3000 em 10x",
        "Me lembra de ligar pro médico",
        "Obrigado!"
    ]

    for message in test_messages:
        print("\n" + "-"*80)
        print(f"👤 Usuário: {message}")
        print("-"*80)

        result = router.route_message(message)

        print(f"🎯 Agent: {result['agent_used']}")
        print(f"💭 Intent: {result['intent']}")
        print(f"📝 Reasoning: {result['reasoning']}")
        print(f"\n🤖 Resposta:\n{result['response']}")

    print("\n" + "="*80)
    print("✅ Demonstração Concluída")
    print("="*80 + "\n")


if __name__ == "__main__":
    import sys
    from loguru import logger

    # Configurar logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )

    main()
