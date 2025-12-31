"""
Processador OCR de Notas Fiscais

Extrai informações de notas fiscais usando GPT-4 Vision
"""
import json
import base64
from pathlib import Path
from typing import Optional
from openai import OpenAI
from loguru import logger
from config.settings import OPENAI_API_KEY


def extract_receipt_data(image_path: str) -> str:
    """
    Extrai dados de nota fiscal a partir de uma imagem

    Use esta ferramenta quando o usuário enviar uma foto de nota fiscal,
    cupom ou recibo que precisa ser registrado como despesa.

    A ferramenta extrai automaticamente:
    - Descrição do estabelecimento/produto
    - Valor total
    - Data da compra
    - Categoria provável

    Args:
        image_path: Caminho da imagem da nota fiscal

    Returns:
        JSON com dados extraídos da nota fiscal
    """
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        # Verificar se arquivo existe
        img_path = Path(image_path)
        if not img_path.exists():
            return json.dumps({
                "status": "error",
                "message": f"Imagem não encontrada: {image_path}"
            }, ensure_ascii=False)

        # Ler e converter para base64
        with open(img_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        # Usar GPT-4 Vision para extrair dados
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em extrair dados de notas fiscais e recibos."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analise esta nota fiscal e extraia as seguintes informações:

1. ESTABELECIMENTO: Nome da loja/restaurante
2. VALOR_TOTAL: Valor total da compra (apenas o número)
3. DATA: Data da compra no formato DD/MM/YYYY
4. CATEGORIA: Classifique em uma destas categorias:
   - Alimentação (mercado, restaurante, delivery)
   - Transporte (combustível, estacionamento)
   - Moradia (material de construção, utilidades)
   - Saúde (farmácia, produtos de saúde)
   - Lazer (entretenimento, hobbies)
   - Educação (livros, cursos)
   - Serviços (serviços em geral)
   - Compras (roupas, eletrônicos, etc)
   - Outros

5. ITEMS: Liste os principais itens comprados (até 5)

Retorne APENAS um JSON válido neste formato exato:
{
  "estabelecimento": "Nome do Local",
  "valor_total": 123.45,
  "data": "DD/MM/YYYY",
  "categoria": "Categoria",
  "items": ["item1", "item2", "item3"],
  "observacoes": "qualquer informação adicional relevante"
}"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.1
        )

        # Extrair resposta
        extracted_text = response.choices[0].message.content

        # Tentar parsear JSON da resposta
        try:
            # Remover markdown se houver
            if "```json" in extracted_text:
                extracted_text = extracted_text.split("```json")[1].split("```")[0].strip()
            elif "```" in extracted_text:
                extracted_text = extracted_text.split("```")[1].split("```")[0].strip()

            receipt_data = json.loads(extracted_text)

            logger.info(f"📄 Nota fiscal processada: {receipt_data.get('estabelecimento')} - R$ {receipt_data.get('valor_total')}")

            return json.dumps({
                "status": "success",
                "data": receipt_data,
                "image_processed": str(img_path)
            }, ensure_ascii=False, indent=2)

        except json.JSONDecodeError as je:
            logger.warning(f"⚠️ Resposta não é JSON válido: {extracted_text}")
            return json.dumps({
                "status": "partial_success",
                "raw_text": extracted_text,
                "message": "Dados extraídos mas não estruturados. Revise manualmente."
            }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ Erro ao processar nota fiscal: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Erro ao processar imagem: {str(e)}"
        }, ensure_ascii=False)


def auto_register_receipt(image_path: str) -> str:
    """
    Extrai dados da nota fiscal E registra automaticamente como despesa

    Use esta ferramenta quando o usuário enviar uma nota fiscal e quiser
    que ela seja automaticamente registrada no sistema.

    Args:
        image_path: Caminho da imagem da nota fiscal

    Returns:
        Confirmação do registro com dados extraídos
    """
    try:
        # Extrair dados
        extraction_result = json.loads(extract_receipt_data(image_path))

        if extraction_result['status'] != 'success':
            return json.dumps(extraction_result, ensure_ascii=False, indent=2)

        data = extraction_result['data']

        # Registrar como despesa
        from tools.cost_manager import add_cost

        registration_result = add_cost(
            description=data['estabelecimento'],
            amount=float(data['valor_total']),
            category=data['categoria'],
            date=data.get('data'),
            notes=f"Itens: {', '.join(data.get('items', []))}\n{data.get('observacoes', '')}"
        )

        registration = json.loads(registration_result)

        if registration['status'] == 'success':
            return json.dumps({
                "status": "success",
                "message": "✅ Nota fiscal registrada automaticamente!",
                "extracted_data": data,
                "registration": registration['data']
            }, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "status": "error",
                "message": "Dados extraídos mas falha ao registrar",
                "extracted_data": data,
                "error": registration.get('message')
            }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ Erro ao auto-registrar nota fiscal: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Erro no registro automático: {str(e)}"
        }, ensure_ascii=False)


# Exemplo de uso no webhook
"""
@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    data = request.json

    # Verificar se é imagem
    if 'imageMessage' in data.get('message', {}):
        image_url = data['message']['imageMessage']['url']
        caption = data['message']['imageMessage'].get('caption', '')

        # Baixar imagem
        image_path = download_image(image_url)

        # Verificar se é nota fiscal (pela legenda ou automático)
        if 'nota' in caption.lower() or 'recibo' in caption.lower():
            from tools.receipt_ocr import auto_register_receipt
            result = auto_register_receipt(image_path)
            return jsonify({'response': result})

    # Processar normalmente
    message_text = data.get('message', {}).get('conversation', '')
    response = process_message(message_text)
    return jsonify({'response': response})
"""
