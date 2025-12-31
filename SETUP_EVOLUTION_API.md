# 🚀 Setup Rápido - Evolution API (GRATUITO)

## ⚡ Instalação em 5 Minutos

Evolution API é a opção **mais fácil e gratuita** para conectar WhatsApp ao seu agente de custos.

---

## 📋 Pré-requisitos

- Docker instalado OU Node.js 18+
- Seu número de WhatsApp (celular)
- 5 minutos de tempo

---

## 🐳 Opção 1: Docker (Mais Fácil) ⭐

### 1. Instalar Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verificar
docker --version
```

### 2. Iniciar Evolution API

```bash
# Criar e iniciar container
docker run -d \
  --name evolution-api \
  -p 8080:8080 \
  -e AUTHENTICATION_API_KEY=minha_chave_secreta_123 \
  -v evolution_instances:/evolution/instances \
  -v evolution_store:/evolution/store \
  atendai/evolution-api:latest

# Verificar se está rodando
docker ps
```

### 3. Acessar Interface Web

Abra no navegador:
```
http://localhost:8080/manager
```

Login padrão:
- **Usuário**: admin
- **API Key**: minha_chave_secreta_123

### 4. Criar Instância do WhatsApp

#### Via Interface Web:

1. Clique em **"+ Nova Instância"**
2. Nome: `cost-agent`
3. Clique em **"Criar"**
4. **QR Code aparecerá** na tela

#### Via API:

```bash
curl -X POST http://localhost:8080/instance/create \
  -H "apikey: minha_chave_secreta_123" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "cost-agent",
    "qrcode": true
  }'
```

### 5. Conectar WhatsApp

1. Abra WhatsApp no seu celular
2. Vá em: **⚙️ Configurações → Aparelhos Conectados**
3. Toque em: **Conectar Aparelho**
4. **Escaneie o QR Code** que apareceu

✅ **Conectado!** Você verá status "open" na interface.

### 6. Configurar Webhook

#### Via Interface Web:

1. Vá em **"Configurações"** da instância
2. Aba **"Webhook"**
3. URL: `http://localhost:5000/webhook/whatsapp`
4. Eventos: Marque **"messages.upsert"**
5. Salvar

#### Via API:

```bash
curl -X POST http://localhost:8080/webhook/set/cost-agent \
  -H "apikey: minha_chave_secreta_123" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://localhost:5000/webhook/whatsapp",
    "enabled": true,
    "events": ["messages.upsert"]
  }'
```

### 7. Iniciar Webhook do Agente

```bash
# No diretório do projeto
cd /home/user/projetosagno
python whatsapp_webhook_complete.py
```

### 8. 🎉 TESTAR!

Envie mensagem do WhatsApp para o número que você conectou:

```
Você: Oi
Bot: [responde conforme o agente]

Você: Gastei 50 no almoço
Bot: ✅ Anotado! Almoço de R$ 50,00 em Alimentação 🍽️
```

---

## 📱 Opção 2: Node.js (Sem Docker)

### 1. Instalar Node.js

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verificar
node --version
npm --version
```

### 2. Clonar e Instalar Evolution API

```bash
# Clonar repositório
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api

# Instalar dependências
npm install

# Copiar configuração
cp .env.example .env

# Editar .env
nano .env
```

### 3. Configurar `.env`

```env
# API
SERVER_PORT=8080
AUTHENTICATION_API_KEY=minha_chave_secreta_123

# Database (opcional, usa SQLite por padrão)
DATABASE_ENABLED=false

# Webhook
WEBHOOK_GLOBAL_ENABLED=true
```

### 4. Iniciar Evolution API

```bash
# Build
npm run build

# Iniciar
npm start
```

### 5. Seguir passos 4-8 da Opção 1

---

## 🔧 Código de Integração

### Arquivo: `evolution_integration.py`

```python
"""
Integração com Evolution API
"""
import requests
import json
from flask import Flask, request, jsonify
from whatsapp_cost_agent import process_message

# Configurações
EVOLUTION_API_URL = "http://localhost:8080"
EVOLUTION_API_KEY = "minha_chave_secreta_123"
INSTANCE_NAME = "cost-agent"

app = Flask(__name__)


def send_whatsapp_message(phone: str, message: str) -> dict:
    """
    Envia mensagem via Evolution API

    Args:
        phone: Número no formato 5511999999999
        message: Texto da mensagem

    Returns:
        Resposta da API
    """
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
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        return {"error": str(e)}


@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """
    Recebe mensagens do Evolution API
    """
    try:
        data = request.json
        print(f"📨 Webhook recebido: {json.dumps(data, indent=2)}")

        # Extrair dados
        event = data.get('event')

        if event == 'messages.upsert':
            message_data = data['data']
            message_info = message_data.get('message', {})

            # Ignorar mensagens próprias
            if message_data.get('key', {}).get('fromMe'):
                return jsonify({'success': True, 'ignored': 'own_message'})

            # Extrair texto
            text = (
                message_info.get('conversation') or
                message_info.get('extendedTextMessage', {}).get('text') or
                ''
            )

            # Extrair remetente
            sender = message_data.get('key', {}).get('remoteJid', '')

            if text:
                print(f"💬 Mensagem de {sender}: {text}")

                # Processar com agente
                response_text = process_message(text)

                # Enviar resposta
                send_whatsapp_message(sender, response_text)

                return jsonify({
                    'success': True,
                    'processed': True,
                    'sender': sender
                })

        return jsonify({'success': True, 'processed': False})

    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'service': 'WhatsApp Cost Agent'})


if __name__ == '__main__':
    print("🚀 Webhook Evolution API iniciado")
    print("📱 Aguardando mensagens do WhatsApp...")
    app.run(host='0.0.0.0', port=5000)
```

### Como Usar:

```bash
# Iniciar webhook
python evolution_integration.py

# Você verá:
🚀 Webhook Evolution API iniciado
📱 Aguardando mensagens do WhatsApp...
```

Agora envie mensagens do WhatsApp!

---

## 🛠️ Comandos Úteis

### Verificar Status da Instância

```bash
curl http://localhost:8080/instance/fetchInstances \
  -H "apikey: minha_chave_secreta_123"
```

### Listar Conversas

```bash
curl http://localhost:8080/chat/findContacts/cost-agent \
  -H "apikey: minha_chave_secreta_123"
```

### Enviar Mensagem Manualmente

```bash
curl -X POST http://localhost:8080/message/sendText/cost-agent \
  -H "apikey: minha_chave_secreta_123" \
  -H "Content-Type: application/json" \
  -d '{
    "number": "5511999999999",
    "text": "Teste de mensagem!"
  }'
```

### Desconectar WhatsApp

```bash
curl -X DELETE http://localhost:8080/instance/logout/cost-agent \
  -H "apikey: minha_chave_secreta_123"
```

### Deletar Instância

```bash
curl -X DELETE http://localhost:8080/instance/delete/cost-agent \
  -H "apikey: minha_chave_secreta_123"
```

---

## 🔄 Manter Rodando 24/7

### Opção 1: Docker Restart (Recomendado)

```bash
# Container reinicia automaticamente
docker update --restart=unless-stopped evolution-api
```

### Opção 2: PM2 (Node.js)

```bash
# Instalar PM2
npm install -g pm2

# Iniciar com PM2
pm2 start npm --name evolution-api -- start

# Ver status
pm2 status

# Ver logs
pm2 logs evolution-api

# Configurar para iniciar com o sistema
pm2 startup
pm2 save
```

### Opção 3: Systemd (Linux)

```bash
# Criar serviço
sudo nano /etc/systemd/system/evolution-api.service
```

Conteúdo:

```ini
[Unit]
Description=Evolution API
After=network.target

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/caminho/para/evolution-api
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Ativar serviço
sudo systemctl enable evolution-api
sudo systemctl start evolution-api
sudo systemctl status evolution-api
```

---

## 📊 Interface Web de Gerenciamento

Acesse: `http://localhost:8080/manager`

**Funcionalidades:**
- ✅ Ver QR Code
- ✅ Status da conexão
- ✅ Enviar mensagens de teste
- ✅ Configurar webhook
- ✅ Ver logs em tempo real
- ✅ Gerenciar múltiplas instâncias

---

## 🐛 Troubleshooting

### Problema: QR Code não aparece

**Solução:**
```bash
# Ver logs do container
docker logs evolution-api

# Reiniciar
docker restart evolution-api
```

### Problema: Webhook não recebe mensagens

**Checklist:**
1. ✅ Webhook configurado corretamente?
2. ✅ Seu servidor está acessível? (teste: `curl http://localhost:5000/health`)
3. ✅ Evolution API consegue alcançar seu servidor?
4. ✅ Firewall bloqueando?

**Testar webhook:**
```bash
# Simular mensagem
curl -X POST http://localhost:8080/message/sendText/cost-agent \
  -H "apikey: minha_chave_secreta_123" \
  -d '{"number": "SEU_NUMERO", "text": "teste"}'
```

### Problema: WhatsApp desconecta sozinho

**Causas comuns:**
- Celular desligado/sem internet por muito tempo
- Evolution API reiniciado sem salvar sessão
- WhatsApp no celular deslogou

**Solução:**
```bash
# Reconectar - novo QR Code
curl -X POST http://localhost:8080/instance/connect/cost-agent \
  -H "apikey: minha_chave_secreta_123"
```

---

## 💰 Custo

**Total: R$ 0,00** ✨

- Evolution API: Grátis
- Self-hosted: Grátis (usa sua internet/servidor)
- Mensagens: Ilimitadas e grátis

---

## 🎯 Resumo Rápido

```bash
# 1. Instalar Evolution API (Docker)
docker run -d --name evolution-api -p 8080:8080 \
  -e AUTHENTICATION_API_KEY=minha_chave_secreta \
  atendai/evolution-api

# 2. Criar instância (via browser)
http://localhost:8080/manager

# 3. Escanear QR Code no WhatsApp

# 4. Configurar webhook
URL: http://localhost:5000/webhook/whatsapp

# 5. Iniciar agente
python evolution_integration.py

# 6. Testar no WhatsApp!
"Gastei 50 no almoço" → Bot responde ✅
```

---

## 📚 Links Úteis

- **Documentação**: https://doc.evolution-api.com
- **GitHub**: https://github.com/EvolutionAPI/evolution-api
- **Comunidade**: https://evolution-api.com/discord

---

**Pronto! WhatsApp conectado de graça!** 🎉
