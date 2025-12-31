"""
WhatsApp Cost Management Agent

Script principal para executar o agente de gestão de custos.
Pode ser integrado com APIs de WhatsApp como Twilio, Evolution API, etc.
"""
from agents.cost_agent import create_cost_management_agent
from loguru import logger
import sys


def setup_logging():
    """Configura logging para o agente"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
    logger.add(
        "logs/cost_agent.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG"
    )


def process_message(message: str) -> str:
    """
    Processa uma mensagem e retorna a resposta do agente

    Args:
        message: Mensagem do usuário (do WhatsApp)

    Returns:
        Resposta formatada do agente
    """
    try:
        agent = create_cost_management_agent()
        response = agent.run(message)
        return response.content

    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem: {e}")
        return f"Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente."


def interactive_mode():
    """
    Modo interativo para testes locais (simula WhatsApp)
    """
    logger.info("💬 Modo Interativo - Agente de Custos WhatsApp")
    logger.info("Digite suas mensagens (ou 'sair' para encerrar)")
    logger.info("-" * 60)

    agent = create_cost_management_agent()

    while True:
        try:
            # Simula mensagem do WhatsApp
            user_message = input("\n👤 Você: ").strip()

            if user_message.lower() in ['sair', 'exit', 'quit']:
                logger.info("👋 Encerrando...")
                break

            if not user_message:
                continue

            # Processa mensagem
            logger.info(f"🤖 Processando: {user_message}")
            response = agent.run(user_message)

            # Exibe resposta
            print(f"\n🤖 Agente:\n{response.content}\n")
            print("-" * 60)

        except KeyboardInterrupt:
            logger.info("\n👋 Encerrando...")
            break
        except Exception as e:
            logger.error(f"❌ Erro: {e}")


def webhook_handler(request_data: dict) -> dict:
    """
    Handler para webhook de WhatsApp (exemplo para APIs como Twilio, Evolution, etc.)

    Exemplo de uso com Evolution API:
    {
        "key": {
            "remoteJid": "5511999999999@s.whatsapp.net",
            "fromMe": false
        },
        "message": {
            "conversation": "Gastei 50 no almoço"
        }
    }

    Args:
        request_data: Dados do webhook

    Returns:
        Resposta formatada para enviar de volta
    """
    try:
        # Extrair mensagem (adapte para sua API de WhatsApp)
        message_text = request_data.get("message", {}).get("conversation", "")
        sender = request_data.get("key", {}).get("remoteJid", "unknown")

        logger.info(f"📱 Mensagem recebida de {sender}: {message_text}")

        # Processar com o agente
        response = process_message(message_text)

        logger.info(f"📤 Resposta enviada: {response[:100]}...")

        return {
            "success": True,
            "response": response,
            "sender": sender
        }

    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# EXEMPLO: Integração com Flask (API Webhook)
# ============================================
"""
Para criar um servidor webhook com Flask:

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    result = webhook_handler(data)
    return jsonify(result)

if __name__ == '__main__':
    setup_logging()
    app.run(host='0.0.0.0', port=5000)
"""


# ============================================
# EXEMPLO: Integração com FastAPI (API Webhook)
# ============================================
"""
Para criar um servidor webhook com FastAPI:

from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class WhatsAppMessage(BaseModel):
    key: dict
    message: dict

@app.post('/webhook/whatsapp')
async def whatsapp_webhook(data: WhatsAppMessage):
    result = webhook_handler(data.dict())
    return result

if __name__ == '__main__':
    import uvicorn
    setup_logging()
    uvicorn.run(app, host='0.0.0.0', port=8000)
"""


# ============================================
# EXEMPLO: Integração com Evolution API
# ============================================
"""
Para integração com Evolution API (https://evolution-api.com):

1. Configure sua instância do Evolution API
2. Configure o webhook para apontar para este servidor
3. O Evolution API enviará mensagens neste formato:

{
    "key": {
        "remoteJid": "5511999999999@s.whatsapp.net",
        "fromMe": false,
        "id": "..."
    },
    "message": {
        "conversation": "texto da mensagem"
    },
    "messageTimestamp": 1234567890,
    "pushName": "Nome do Usuário"
}

4. Use webhook_handler() para processar
5. Envie resposta de volta via API do Evolution
"""


def main():
    """Função principal"""
    setup_logging()

    logger.info("💰 Agente de Gestão de Custos - WhatsApp")
    logger.info("=" * 60)

    # Modo interativo para testes
    interactive_mode()


if __name__ == "__main__":
    main()
