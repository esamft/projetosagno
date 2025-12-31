#!/bin/bash

# 🚀 Script de Instalação Automática - Evolution API
# Para o Agente de Gestão de Custos via WhatsApp

set -e  # Para se houver erro

echo "🚀 =========================================="
echo "   Setup Automático - Evolution API"
echo "   Agente de Gestão de Custos WhatsApp"
echo "=========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para printar com cor
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Verificar se Docker está instalado
echo ""
print_info "Verificando Docker..."

if ! command -v docker &> /dev/null; then
    print_warning "Docker não encontrado. Instalando..."

    # Detectar sistema operacional
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
        print_success "Docker instalado!"
    else
        print_warning "Por favor, instale o Docker manualmente: https://docs.docker.com/get-docker/"
        exit 1
    fi
else
    print_success "Docker já instalado!"
fi

# Parar container antigo se existir
if docker ps -a | grep -q evolution-api; then
    print_info "Parando container antigo..."
    docker stop evolution-api 2>/dev/null || true
    docker rm evolution-api 2>/dev/null || true
fi

# Gerar API Key aleatória
API_KEY="agno_$(openssl rand -hex 16)"

# Criar volumes
print_info "Criando volumes Docker..."
docker volume create evolution_instances
docker volume create evolution_store

# Iniciar Evolution API
print_info "Iniciando Evolution API..."

docker run -d \
  --name evolution-api \
  --restart unless-stopped \
  -p 8080:8080 \
  -e AUTHENTICATION_API_KEY="$API_KEY" \
  -e SERVER_PORT=8080 \
  -e WEBHOOK_GLOBAL_ENABLED=true \
  -v evolution_instances:/evolution/instances \
  -v evolution_store:/evolution/store \
  atendai/evolution-api:latest

# Aguardar API iniciar
print_info "Aguardando Evolution API iniciar (30 segundos)..."
sleep 30

# Verificar se está rodando
if docker ps | grep -q evolution-api; then
    print_success "Evolution API rodando!"
else
    print_warning "Erro ao iniciar Evolution API. Verifique os logs:"
    echo "docker logs evolution-api"
    exit 1
fi

# Criar instância do WhatsApp
print_info "Criando instância do WhatsApp..."

INSTANCE_RESPONSE=$(curl -s -X POST http://localhost:8080/instance/create \
  -H "apikey: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "cost-agent",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }')

echo "$INSTANCE_RESPONSE" | jq . 2>/dev/null || echo "$INSTANCE_RESPONSE"

# Aguardar QR Code
sleep 5

# Buscar QR Code
print_info "Gerando QR Code..."

QR_RESPONSE=$(curl -s http://localhost:8080/instance/connect/cost-agent \
  -H "apikey: $API_KEY")

# Extrair QR Code base64
QR_CODE=$(echo "$QR_RESPONSE" | jq -r '.qrcode.base64' 2>/dev/null)

# Salvar configurações
cat > .evolution_config <<EOF
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=$API_KEY
INSTANCE_NAME=cost-agent
EOF

print_success "Configurações salvas em .evolution_config"

# Criar arquivo de integração Python
cat > evolution_integration.py <<'PYEOF'
"""
Integração Evolution API - Gerado automaticamente
"""
import os
import requests
import json
from flask import Flask, request, jsonify
from pathlib import Path

# Carregar configurações
config_file = Path(__file__).parent / '.evolution_config'
if config_file.exists():
    with open(config_file) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL', 'http://localhost:8080')
EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY')
INSTANCE_NAME = os.getenv('INSTANCE_NAME', 'cost-agent')

app = Flask(__name__)


def send_whatsapp_message(phone: str, message: str) -> dict:
    """Envia mensagem via Evolution API"""
    url = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"

    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "number": phone,
        "text": message
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        return response.json()
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return {"error": str(e)}


@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Recebe mensagens do Evolution API"""
    try:
        data = request.json
        print(f"\n📨 Webhook recebido:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        event = data.get('event')

        if event == 'messages.upsert':
            message_data = data.get('data', {})
            key = message_data.get('key', {})

            # Ignorar mensagens próprias
            if key.get('fromMe'):
                return jsonify({'success': True, 'ignored': 'own_message'})

            # Extrair mensagem
            message_info = message_data.get('message', {})
            text = (
                message_info.get('conversation') or
                message_info.get('extendedTextMessage', {}).get('text') or
                ''
            )

            sender = key.get('remoteJid', '')

            if text:
                print(f"\n💬 Mensagem de {sender}:")
                print(f"   '{text}'")

                # Processar com agente
                from whatsapp_cost_agent import process_message
                response_text = process_message(text)

                print(f"\n🤖 Resposta do agente:")
                print(f"   {response_text[:200]}...")

                # Enviar resposta
                result = send_whatsapp_message(sender, response_text)
                print(f"\n📤 Mensagem enviada: {result.get('key', 'ok')}")

                return jsonify({'success': True, 'processed': True})

        return jsonify({'success': True, 'processed': False})

    except Exception as e:
        print(f"\n❌ Erro no webhook: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'service': 'WhatsApp Cost Agent',
        'evolution_api': EVOLUTION_API_URL,
        'instance': INSTANCE_NAME
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Webhook Evolution API Iniciado")
    print("="*60)
    print(f"📱 Evolution API: {EVOLUTION_API_URL}")
    print(f"💬 Instância: {INSTANCE_NAME}")
    print(f"🌐 Webhook: http://0.0.0.0:5000/webhook/whatsapp")
    print("="*60)
    print("\n✅ Aguardando mensagens do WhatsApp...\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
PYEOF

print_success "Arquivo de integração criado: evolution_integration.py"

# Configurar webhook
print_info "Configurando webhook..."

sleep 2

WEBHOOK_RESPONSE=$(curl -s -X POST "http://localhost:8080/webhook/set/cost-agent" \
  -H "apikey: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://localhost:5000/webhook/whatsapp",
    "webhook_by_events": false,
    "webhook_base64": false,
    "events": [
      "MESSAGES_UPSERT",
      "SEND_MESSAGE"
    ]
  }')

echo "$WEBHOOK_RESPONSE" | jq . 2>/dev/null || echo "$WEBHOOK_RESPONSE"

# Instruções finais
echo ""
echo "=================================================="
print_success "INSTALAÇÃO CONCLUÍDA!"
echo "=================================================="
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo ""
echo "1️⃣  Conectar WhatsApp:"
echo "    Acesse: http://localhost:8080/manager"
echo "    Login: API Key = $API_KEY"
echo ""
echo "2️⃣  OU veja o QR Code no terminal:"
echo "    curl http://localhost:8080/instance/connect/cost-agent \\"
echo "      -H 'apikey: $API_KEY' | jq -r '.qrcode.base64' | base64 -d"
echo ""
echo "3️⃣  Iniciar webhook do agente:"
echo "    python evolution_integration.py"
echo ""
echo "4️⃣  Testar enviando mensagem do WhatsApp:"
echo "    'Gastei 50 no almoço'"
echo ""
echo "=================================================="
echo ""
print_info "🔧 Comandos úteis:"
echo ""
echo "  Ver logs Evolution API:"
echo "    docker logs -f evolution-api"
echo ""
echo "  Parar Evolution API:"
echo "    docker stop evolution-api"
echo ""
echo "  Reiniciar Evolution API:"
echo "    docker restart evolution-api"
echo ""
echo "  Status da instância:"
echo "    curl http://localhost:8080/instance/fetchInstances \\"
echo "      -H 'apikey: $API_KEY'"
echo ""
echo "=================================================="
echo ""
print_success "✨ Tudo pronto! Boa gestão de custos! ✨"
echo ""
