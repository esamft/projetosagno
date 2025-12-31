# 🚀 Guia de Integração - WhatsApp Real

## 📱 Como Conectar o Agente ao WhatsApp

Este guia mostra como integrar o agente de custos com APIs reais de WhatsApp.

---

## 🎯 Escolha sua Plataforma

| Plataforma | Dificuldade | Custo | Recomendado Para |
|------------|-------------|-------|------------------|
| **Evolution API** | ⭐ Fácil | 💰 Grátis/Baixo | Desenvolvimento |
| **Twilio** | ⭐⭐ Médio | 💰💰 Médio | Produção |
| **Baileys** | ⭐⭐⭐ Difícil | 💰 Grátis | Avançado |

---

## 1️⃣ Evolution API (Mais Fácil) ⭐

### O que é?
Evolution API é uma API WhatsApp de código aberto, fácil de configurar.

### Passo a Passo:

#### 1. Instalar Evolution API

```bash
# Opção A: Docker (Recomendado)
docker run -d \
  --name evolution-api \
  -p 8080:8080 \
  -e AUTHENTICATION_API_KEY=sua_chave_secreta \
  atendai/evolution-api:latest

# Opção B: NPM
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api
npm install
npm run build
npm start
```

#### 2. Criar Instância do WhatsApp

```bash
# Criar nova instância
curl -X POST http://localhost:8080/instance/create \
  -H "apikey: sua_chave_secreta" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "cost-agent",
    "qrcode": true
  }'

# Resposta incluirá QR Code para conectar seu WhatsApp
```

#### 3. Escanear QR Code

- Abra WhatsApp no celular
- Vá em: Configurações → Aparelhos Conectados → Conectar Aparelho
- Escaneie o QR Code retornado pela API

#### 4. Configurar Webhook

```bash
# Configurar webhook para receber mensagens
curl -X POST http://localhost:8080/webhook/set/cost-agent \
  -H "apikey: sua_chave_secreta" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://SEU_SERVIDOR:5000/webhook/whatsapp",
    "webhook_by_events": false,
    "events": [
      "MESSAGES_UPSERT"
    ]
  }'
```

#### 5. Iniciar Webhook do Agente

```bash
# Terminal 1: Seu webhook
python whatsapp_webhook_complete.py

# Agora mensagens do WhatsApp chegarão em:
# http://localhost:5000/webhook/whatsapp
```

#### 6. Testar

Envie mensagem para o número conectado:
```
Você: Gastei 50 no almoço
Bot: ✅ Anotado! Almoço de R$ 50,00 em Alimentação 🍽️
```

### Código de Integração Evolution API

```python
# whatsapp_evolution_integration.py
import requests
import json

EVOLUTION_API_URL = "http://localhost:8080"
EVOLUTION_API_KEY = "sua_chave_secreta"
INSTANCE_NAME = "cost-agent"

def send_message(phone: str, message: str):
    """Envia mensagem via Evolution API"""
    url = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"

    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "number": phone,  # Ex: "5511999999999"
        "text": message
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Usar no webhook:
@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    data = request.json

    # Processar mensagem
    message_text = data['message']['conversation']
    sender = data['key']['remoteJid']

    response = process_message(message_text)

    # Enviar resposta
    send_message(sender, response)

    return jsonify({'success': True})
```

---

## 2️⃣ Twilio (Produção)

### O que é?
Plataforma empresarial para WhatsApp Business API.

### Passo a Passo:

#### 1. Criar Conta Twilio

- Acesse: https://www.twilio.com/whatsapp
- Crie conta (trial grátis com $15 de crédito)
- Ative WhatsApp Sandbox ou solicite número Business

#### 2. Configurar Sandbox (Desenvolvimento)

```
1. No Twilio Console → Messaging → Try it out → WhatsApp
2. Envie mensagem no WhatsApp para o número indicado
3. Envie o código de ativação (ex: "join <code>")
```

#### 3. Configurar Webhook

No Twilio Console:
```
Messaging → Settings → WhatsApp Sandbox Settings
When a message comes in: https://SEU_SERVIDOR/webhook/twilio
```

#### 4. Código de Integração

```python
# whatsapp_twilio_integration.py
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

# Credenciais (do Twilio Console)
ACCOUNT_SID = 'seu_account_sid'
AUTH_TOKEN = 'seu_auth_token'
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'  # Número sandbox

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_message(to_number: str, message: str):
    """Envia mensagem via Twilio"""
    message = client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        body=message,
        to=f'whatsapp:{to_number}'  # Ex: whatsapp:+5511999999999
    )
    return message.sid

# Webhook
from flask import Flask, request
app = Flask(__name__)

@app.route('/webhook/twilio', methods=['POST'])
def twilio_webhook():
    # Extrair mensagem
    incoming_msg = request.values.get('Body', '')
    sender = request.values.get('From', '')

    # Processar com agente
    from whatsapp_cost_agent import process_message
    response_text = process_message(incoming_msg)

    # Responder
    resp = MessagingResponse()
    resp.message(response_text)

    return str(resp)

if __name__ == '__main__':
    app.run(port=5000)
```

#### 5. Testar

Envie mensagem para o número Twilio:
```
Você: Gastei 100 na farmácia
Bot: ✅ Anotado! Farmácia de R$ 100,00 em Saúde 💊
```

### Custos Twilio:
- **Sandbox**: Grátis para desenvolvimento
- **Business**: ~$0.005 por mensagem (mínimo de volume)
- **Número WhatsApp Business**: Varia por país

---

## 3️⃣ Baileys (Avançado)

### O que é?
Biblioteca Node.js que conecta diretamente ao WhatsApp Web.

### Passo a Passo:

#### 1. Setup do Baileys

```bash
# Criar projeto Node.js
mkdir whatsapp-baileys-bridge
cd whatsapp-baileys-bridge
npm init -y

# Instalar Baileys
npm install @whiskeysockets/baileys qrcode-terminal
```

#### 2. Código Baileys

```javascript
// index.js
const { makeWASocket, useMultiFileAuthState } = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const AGENT_API = 'http://localhost:5000/process';

async function startBot() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info');

    const sock = makeWASocket({
        auth: state,
        printQRInTerminal: true
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('messages.upsert', async ({ messages }) => {
        const msg = messages[0];

        if (!msg.message || msg.key.fromMe) return;

        const text = msg.message.conversation ||
                    msg.message.extendedTextMessage?.text;

        if (text) {
            // Enviar para API Python do agente
            const response = await axios.post(AGENT_API, {
                message: text,
                sender: msg.key.remoteJid
            });

            // Responder
            await sock.sendMessage(msg.key.remoteJid, {
                text: response.data.response
            });
        }
    });
}

startBot();
```

#### 3. API Python Bridge

```python
# api_bridge.py
from flask import Flask, request, jsonify
from whatsapp_cost_agent import process_message

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    message = data['message']
    sender = data['sender']

    response = process_message(message)

    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(port=5000)
```

#### 4. Executar

```bash
# Terminal 1: API Python
python api_bridge.py

# Terminal 2: Bot Baileys
node index.js

# Escanear QR Code que aparece
```

---

## 🔐 Segurança em Produção

### 1. HTTPS Obrigatório

```bash
# Usar nginx + certbot para SSL
sudo apt install nginx certbot python3-certbot-nginx

# Configurar SSL
sudo certbot --nginx -d seu-dominio.com

# nginx.conf
server {
    listen 443 ssl;
    server_name seu-dominio.com;

    location /webhook/whatsapp {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
    }
}
```

### 2. Autenticação do Webhook

```python
# Adicionar verificação de token
WEBHOOK_SECRET = "seu_token_secreto"

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    # Verificar token
    token = request.headers.get('X-Webhook-Token')
    if token != WEBHOOK_SECRET:
        return jsonify({'error': 'Unauthorized'}), 401

    # Processar normalmente...
```

### 3. Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)

@app.route('/webhook/whatsapp', methods=['POST'])
@limiter.limit("10 per minute")
def whatsapp_webhook():
    # ...
```

---

## 🚀 Deploy em Produção

### Opção 1: Railway.app (Fácil)

```bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Deploy
railway init
railway up

# Copiar URL fornecida e configurar como webhook
```

### Opção 2: DigitalOcean/AWS

```bash
# 1. Criar servidor
# 2. Instalar dependências
sudo apt update
sudo apt install python3-pip nginx

# 3. Clonar projeto
git clone seu-repo.git
cd seu-repo
pip3 install -r requirements.txt

# 4. Configurar systemd
sudo nano /etc/systemd/system/cost-agent.service

# Conteúdo:
[Unit]
Description=WhatsApp Cost Agent
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/projetosagno
ExecStart=/usr/bin/python3 whatsapp_webhook_complete.py
Restart=always

[Install]
WantedBy=multi-user.target

# 5. Iniciar serviço
sudo systemctl enable cost-agent
sudo systemctl start cost-agent
```

---

## 📊 Monitoramento

### Logs

```python
# Adicionar logging estruturado
import logging
from datetime import datetime

logging.basicConfig(
    filename=f'logs/webhook_{datetime.now():%Y%m%d}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    logging.info(f"Mensagem recebida: {request.json}")
    # ...
```

### Métricas

```python
# Contar mensagens processadas
from prometheus_client import Counter, Histogram

messages_total = Counter('messages_total', 'Total de mensagens')
processing_time = Histogram('processing_seconds', 'Tempo de processamento')

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    messages_total.inc()

    with processing_time.time():
        # processar mensagem
        pass
```

---

## 🧪 Testar Integração

### Script de Teste

```python
# test_webhook.py
import requests
import json

def test_webhook():
    """Testa webhook com mensagem simulada"""

    webhook_url = "http://localhost:5000/webhook/whatsapp"

    # Mensagem de teste (formato Evolution API)
    test_message = {
        "message": {
            "conversation": "Gastei 50 no almoço"
        },
        "key": {
            "remoteJid": "5511999999999@s.whatsapp.net"
        }
    }

    response = requests.post(
        webhook_url,
        json=test_message,
        headers={"Content-Type": "application/json"}
    )

    print("Status:", response.status_code)
    print("Resposta:", response.json())

if __name__ == '__main__':
    test_webhook()
```

---

## ✅ Checklist de Produção

- [ ] Webhook respondendo corretamente
- [ ] HTTPS configurado
- [ ] Autenticação de webhook implementada
- [ ] Rate limiting ativo
- [ ] Logs estruturados
- [ ] Monitoramento configurado
- [ ] Backup de dados automatizado
- [ ] Testes de carga realizados
- [ ] Documentação atualizada
- [ ] Plano de rollback definido

---

## 📞 Suporte

- **Evolution API**: https://doc.evolution-api.com/
- **Twilio**: https://www.twilio.com/docs/whatsapp
- **Baileys**: https://github.com/WhiskeySockets/Baileys

---

**Desenvolvido com Agno Framework** 🚀
