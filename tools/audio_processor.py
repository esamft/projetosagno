"""
Processador de áudio para mensagens de voz

Transcreve áudios do WhatsApp usando Whisper (OpenAI)
"""
import json
from pathlib import Path
from typing import Optional
from openai import OpenAI
from loguru import logger
from config.settings import OPENAI_API_KEY


def transcribe_voice_message(audio_file_path: str, language: str = "pt") -> str:
    """
    Transcreve mensagem de voz do WhatsApp

    Use esta ferramenta quando receber um arquivo de áudio do usuário
    que precisa ser convertido em texto para processamento.

    Args:
        audio_file_path: Caminho do arquivo de áudio (mp3, m4a, wav, etc)
        language: Idioma do áudio (padrão: "pt" para português)

    Returns:
        Texto transcrito do áudio
    """
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        # Verificar se arquivo existe
        audio_path = Path(audio_file_path)
        if not audio_path.exists():
            return json.dumps({
                "status": "error",
                "message": f"Arquivo de áudio não encontrado: {audio_file_path}"
            }, ensure_ascii=False)

        # Transcrever com Whisper
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="text"
            )

        logger.info(f"🎤 Áudio transcrito: {transcript[:100]}...")

        return json.dumps({
            "status": "success",
            "transcription": transcript,
            "audio_file": str(audio_path),
            "language": language
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ Erro ao transcrever áudio: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Erro ao transcrever áudio: {str(e)}"
        }, ensure_ascii=False)


# Exemplo de uso no webhook
"""
@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    data = request.json

    # Verificar se é áudio
    if 'audioMessage' in data.get('message', {}):
        audio_url = data['message']['audioMessage']['url']

        # Baixar áudio
        audio_path = download_audio(audio_url)

        # Transcrever
        from tools.audio_processor import transcribe_voice_message
        result = json.loads(transcribe_voice_message(audio_path))

        if result['status'] == 'success':
            # Processar transcrição com o agente
            message_text = result['transcription']
            response = process_message(message_text)
            return jsonify({'response': response})

    # Mensagem de texto normal
    message_text = data.get('message', {}).get('conversation', '')
    response = process_message(message_text)
    return jsonify({'response': response})
"""
