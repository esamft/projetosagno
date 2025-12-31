"""
Webhook Completo para WhatsApp
Suporta: TEXTO, VOZ e IMAGENS (notas fiscais)

Integração com Evolution API, Twilio ou similar
"""
from flask import Flask, request, jsonify
from pathlib import Path
import json
import requests
from loguru import logger
from agents.cost_agent import create_cost_management_agent

# Tools especiais
from tools.audio_processor import transcribe_voice_message
from tools.receipt_ocr import auto_register_receipt, extract_receipt_data

app = Flask(__name__)


# Diretório para downloads temporários
TEMP_DIR = Path(__file__).parent / "temp"
TEMP_DIR.mkdir(exist_ok=True)


def download_file(url: str, filename: str) -> Path:
    """
    Baixa arquivo (áudio/imagem) do WhatsApp

    Args:
        url: URL do arquivo
        filename: Nome do arquivo para salvar

    Returns:
        Caminho do arquivo baixado
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        file_path = TEMP_DIR / filename
        file_path.write_bytes(response.content)

        logger.info(f"📥 Arquivo baixado: {filename}")
        return file_path

    except Exception as e:
        logger.error(f"❌ Erro ao baixar arquivo: {e}")
        raise


def process_text_message(text: str, sender: str) -> str:
    """
    Processa mensagem de texto com o agente

    Args:
        text: Texto da mensagem
        sender: ID do remetente

    Returns:
        Resposta do agente
    """
    try:
        logger.info(f"💬 Texto de {sender}: {text}")

        agent = create_cost_management_agent()
        response = agent.run(text)

        return response.content

    except Exception as e:
        logger.error(f"❌ Erro ao processar texto: {e}")
        return "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente."


def process_voice_message(audio_url: str, sender: str) -> str:
    """
    Processa mensagem de voz (transcreve + processa)

    Args:
        audio_url: URL do arquivo de áudio
        sender: ID do remetente

    Returns:
        Resposta do agente baseada na transcrição
    """
    try:
        logger.info(f"🎤 Áudio recebido de {sender}")

        # Baixar áudio
        audio_path = download_file(audio_url, f"audio_{sender}_{int(time.time())}.ogg")

        # Transcrever
        transcription_result = json.loads(transcribe_voice_message(str(audio_path)))

        if transcription_result['status'] != 'success':
            return "❌ Não consegui entender o áudio. Pode enviar como texto?"

        # Processar transcrição com o agente
        transcribed_text = transcription_result['transcription']
        logger.info(f"📝 Transcrito: {transcribed_text}")

        agent = create_cost_management_agent()
        response = agent.run(transcribed_text)

        # Adicionar nota sobre transcrição
        return f"🎤 Entendi: \"{transcribed_text}\"\n\n{response.content}"

    except Exception as e:
        logger.error(f"❌ Erro ao processar áudio: {e}")
        return "Desculpe, não consegui processar o áudio. Tente enviar como texto."


def process_image_message(image_url: str, caption: str, sender: str) -> str:
    """
    Processa imagem (extrai nota fiscal se aplicável)

    Args:
        image_url: URL da imagem
        caption: Legenda da imagem
        sender: ID do remetente

    Returns:
        Resposta com dados extraídos ou erro
    """
    try:
        logger.info(f"📷 Imagem recebida de {sender} - Legenda: {caption}")

        # Baixar imagem
        image_path = download_file(image_url, f"image_{sender}_{int(time.time())}.jpg")

        # Verificar se é nota fiscal (pela legenda ou processar sempre)
        keywords = ['nota', 'recibo', 'cupom', 'fiscal', 'compra', 'nf']
        is_receipt = any(keyword in caption.lower() for keyword in keywords) if caption else True

        if is_receipt:
            # Perguntar se quer registrar automaticamente
            if 'registrar' in caption.lower() or 'adicionar' in caption.lower():
                result = json.loads(auto_register_receipt(str(image_path)))

                if result['status'] == 'success':
                    data = result['extracted_data']
                    return f"""✅ **Nota fiscal registrada automaticamente!**

📄 **{data['estabelecimento']}**
💰 Valor: R$ {data['valor_total']:.2f}
📅 Data: {data['data']}
🏷️ Categoria: {data['categoria']}

📝 Itens: {', '.join(data.get('items', [])[:3])}

Use "relatório mensal" para ver todos os gastos!"""
                else:
                    return f"⚠️ Recebi a imagem mas não consegui processar automaticamente. {result.get('message', '')}"

            else:
                # Apenas extrair dados sem registrar
                result = json.loads(extract_receipt_data(str(image_path)))

                if result['status'] == 'success':
                    data = result['data']
                    return f"""📄 **Dados da nota fiscal extraídos:**

📍 Local: {data['estabelecimento']}
💰 Valor: R$ {data['valor_total']:.2f}
📅 Data: {data['data']}
🏷️ Categoria: {data['categoria']}

Quer que eu registre isso? Envie: "registrar nota"
Ou envie outra foto com legenda "registrar" para adicionar automaticamente."""
                else:
                    return "⚠️ Não consegui ler a nota fiscal. Tente tirar outra foto mais clara ou me diga os valores."

        else:
            return "🤔 Recebi a imagem. É uma nota fiscal? Se sim, envie com a legenda 'registrar' para adicionar automaticamente aos seus gastos!"

    except Exception as e:
        logger.error(f"❌ Erro ao processar imagem: {e}")
        return "Desculpe, não consegui processar a imagem. Você pode me dizer os valores manualmente?"


@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """
    Endpoint principal do webhook
    Recebe mensagens do WhatsApp e processa de acordo com o tipo
    """
    try:
        data = request.json
        logger.info(f"📨 Webhook recebido: {json.dumps(data, indent=2)}")

        # Extrair informações básicas
        message = data.get('message', {})
        sender = data.get('key', {}).get('remoteJid', 'unknown')

        # === MENSAGEM DE TEXTO ===
        if 'conversation' in message:
            text = message['conversation']
            response = process_text_message(text, sender)
            return jsonify({
                'success': True,
                'type': 'text',
                'response': response
            })

        # === MENSAGEM DE VOZ ===
        elif 'audioMessage' in message:
            audio_url = message['audioMessage'].get('url')
            response = process_voice_message(audio_url, sender)
            return jsonify({
                'success': True,
                'type': 'audio',
                'response': response
            })

        # === MENSAGEM DE IMAGEM ===
        elif 'imageMessage' in message:
            image_url = message['imageMessage'].get('url')
            caption = message['imageMessage'].get('caption', '')
            response = process_image_message(image_url, caption, sender)
            return jsonify({
                'success': True,
                'type': 'image',
                'response': response
            })

        # === TIPO NÃO SUPORTADO ===
        else:
            logger.warning(f"⚠️ Tipo de mensagem não suportado: {message.keys()}")
            return jsonify({
                'success': False,
                'message': 'Tipo de mensagem não suportado. Envie texto, áudio ou imagem.'
            })

    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'WhatsApp Cost Agent',
        'capabilities': ['text', 'voice', 'image']
    })


if __name__ == '__main__':
    import time
    from loguru import logger
    import sys

    # Configurar logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
    logger.add("logs/webhook.log", rotation="10 MB")

    logger.info("🚀 Webhook WhatsApp Iniciado")
    logger.info("📱 Suporte a: Texto, Voz e Imagens")
    logger.info("🌐 Rodando em: http://0.0.0.0:5000")

    app.run(host='0.0.0.0', port=5000, debug=False)
