# 📱 Suporte Multimodal - Agente de Custos WhatsApp

## 🎯 Tipos de Entrada Suportados

O agente de custos pode processar **3 tipos** de mensagens via WhatsApp:

| Tipo | Status | Descrição |
|------|--------|-----------|
| 📝 **TEXTO** | ✅ Nativo | Mensagens de texto normais |
| 🎤 **VOZ** | ✅ Com Whisper | Áudios transcritos automaticamente |
| 📷 **IMAGEM** | ✅ Com Vision | OCR de notas fiscais com GPT-4 Vision |

---

## 📝 1. MENSAGENS DE TEXTO

### ✅ Status: **Totalmente Implementado**

O agente está pronto para processar texto de forma natural.

### Exemplos:

```
Você: Gastei 50 no almoço
Bot: ✅ Anotado! Almoço de R$ 50,00 em Alimentação 🍽️

Você: Uber 25 reais no pix
Bot: ✅ Registrado! Uber de R$ 25,00 em Transporte 🚗
     Forma de pagamento: PIX

Você: Quanto gastei esse mês?
Bot: [Relatório mensal completo]
```

### Capacidades:
- ✅ Linguagem natural em português
- ✅ Inferência automática de categoria
- ✅ Detecção de método de pagamento
- ✅ Extração automática de valores
- ✅ Conversas contextuais

---

## 🎤 2. MENSAGENS DE VOZ

### ✅ Status: **Implementado com OpenAI Whisper**

Transcrição automática de áudio usando Whisper API.

### Como Funciona:

1. **Usuário envia áudio** no WhatsApp
2. **Webhook baixa** o arquivo de áudio
3. **Whisper transcreve** para texto
4. **Agente processa** a transcrição
5. **Responde** confirmando o que entendeu

### Exemplo de Fluxo:

```
👤 [Envia áudio: "Oi, gastei cinquenta reais no almoço hoje"]

🤖 Bot: 🎤 Entendi: "Gastei cinquenta reais no almoço hoje"

        ✅ Anotado! Almoço de R$ 50,00 em Alimentação 🍽️
```

### Arquivo Criado:
- `tools/audio_processor.py` - Transcrição com Whisper

### Tool Disponível:
```python
def transcribe_voice_message(audio_file_path: str, language: str = "pt") -> str:
    """Transcreve áudio do WhatsApp para texto"""
```

### Como Testar:

```python
from tools.audio_processor import transcribe_voice_message

# Transcrever áudio
result = transcribe_voice_message("audio.ogg", language="pt")
print(result)
# {
#   "status": "success",
#   "transcription": "Gastei cinquenta reais no almoço",
#   "audio_file": "audio.ogg"
# }
```

### Formatos Suportados:
- ✅ MP3
- ✅ M4A
- ✅ WAV
- ✅ OGG (formato padrão WhatsApp)
- ✅ Outros formatos de áudio

### Custos (OpenAI):
- **Whisper**: $0.006 por minuto de áudio
- Exemplo: 10 segundos = ~$0.001

---

## 📷 3. IMAGENS (Notas Fiscais)

### ✅ Status: **Implementado com GPT-4 Vision**

OCR inteligente de notas fiscais usando GPT-4 Vision.

### Como Funciona:

1. **Usuário envia foto** da nota fiscal
2. **Webhook baixa** a imagem
3. **GPT-4 Vision extrai** dados estruturados
4. **Opções**:
   - Apenas mostrar dados extraídos
   - Registrar automaticamente como despesa

### Exemplo de Fluxo:

#### Opção 1: Extração Simples

```
👤 [Envia foto de nota fiscal]
    Legenda: "nota fiscal"

🤖 Bot: 📄 Dados da nota fiscal extraídos:

        📍 Local: Supermercado Zona Sul
        💰 Valor: R$ 245,80
        📅 Data: 30/12/2025
        🏷️ Categoria: Alimentação

        📝 Itens: Arroz, Feijão, Carne, Leite, Ovos

        Quer que eu registre isso? Envie: "registrar nota"
```

#### Opção 2: Registro Automático

```
👤 [Envia foto de nota fiscal]
    Legenda: "registrar"

🤖 Bot: ✅ Nota fiscal registrada automaticamente!

        📄 Supermercado Zona Sul
        💰 Valor: R$ 245,80
        📅 Data: 30/12/2025
        🏷️ Categoria: Alimentação

        📝 Itens: Arroz, Feijão, Carne

        Use "relatório mensal" para ver todos os gastos!
```

### Arquivos Criados:
- `tools/receipt_ocr.py` - OCR com GPT-4 Vision

### Tools Disponíveis:

#### 1. Apenas Extrair Dados
```python
def extract_receipt_data(image_path: str) -> str:
    """Extrai dados de nota fiscal sem registrar"""
```

#### 2. Extrair + Registrar
```python
def auto_register_receipt(image_path: str) -> str:
    """Extrai dados E registra automaticamente como despesa"""
```

### Dados Extraídos:

```json
{
  "estabelecimento": "Supermercado Zona Sul",
  "valor_total": 245.80,
  "data": "30/12/2025",
  "categoria": "Alimentação",
  "items": ["Arroz", "Feijão", "Carne", "Leite", "Ovos"],
  "observacoes": "Compra mensal"
}
```

### Formatos Suportados:
- ✅ JPG/JPEG
- ✅ PNG
- ✅ WEBP
- ✅ GIF (primeira imagem)

### Qualidade da Imagem:
- ✅ Adapta-se a diferentes qualidades
- ✅ Funciona com fotos de celular
- ⚠️ Melhor com imagens nítidas e bem iluminadas

### Custos (OpenAI):
- **GPT-4 Vision**: ~$0.01 por imagem (alta resolução)
- Exemplo: 100 notas fiscais = ~$1.00

---

## 🚀 Webhook Completo

### Arquivo: `whatsapp_webhook_complete.py`

Webhook integrado que suporta **todos os 3 tipos** de mensagem:

```python
@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    # Detecta automaticamente o tipo e processa:
    # - Texto → process_text_message()
    # - Áudio → process_voice_message()
    # - Imagem → process_image_message()
```

### Como Executar:

```bash
python whatsapp_webhook_complete.py
```

```
🚀 Webhook WhatsApp Iniciado
📱 Suporte a: Texto, Voz e Imagens
🌐 Rodando em: http://0.0.0.0:5000
```

### Endpoints:

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/webhook/whatsapp` | POST | Recebe mensagens do WhatsApp |
| `/health` | GET | Health check |

---

## 🔧 Configuração

### 1. Dependências Adicionais

Adicione ao `requirements.txt`:

```txt
# Processamento de áudio
openai>=1.0.0  # Já incluído

# Processamento de imagens
Pillow>=10.0.0  # Opcional, para manipulação
```

### 2. API Keys Necessárias

No arquivo `.env`:

```env
# Já configurado
OPENAI_API_KEY=sk-...

# A mesma chave serve para:
# - GPT-4o (texto)
# - Whisper (áudio)
# - GPT-4 Vision (imagem)
```

### 3. Estrutura de Diretórios

```bash
mkdir -p temp logs
```

- `temp/` - Arquivos temporários baixados
- `logs/` - Logs do webhook

---

## 📊 Comparação de Recursos

| Recurso | Texto | Voz | Imagem |
|---------|-------|-----|--------|
| **Registrar despesa** | ✅ | ✅ | ✅ |
| **Ver relatórios** | ✅ | ✅ | ❌ |
| **Conversação** | ✅ | ✅ | ❌ |
| **Dados estruturados** | ✅ | ✅ | ✅ |
| **Múltiplos itens** | ❌ | ❌ | ✅ |
| **Prova documental** | ❌ | ❌ | ✅ |
| **Velocidade** | ⚡ Rápido | 🐢 Médio | 🐢 Lento |
| **Custo** | 💰 Baixo | 💰 Baixo | 💰💰 Médio |

---

## 💡 Casos de Uso

### Caso 1: Usuário no Supermercado (VOZ)
```
Situação: Mãos ocupadas com sacolas
Solução: Envia áudio "Gastei 245 no mercado"
Resultado: Registrado automaticamente
```

### Caso 2: Reunião de Negócios (IMAGEM)
```
Situação: Recebeu cupom fiscal de restaurante
Solução: Foto da nota com legenda "registrar"
Resultado: Todos os itens extraídos e salvos
```

### Caso 3: Consulta Rápida (TEXTO)
```
Situação: Quer saber quanto gastou no mês
Solução: "Relatório mensal"
Resultado: Análise completa instantânea
```

---

## 🧪 Como Testar

### Teste 1: Áudio

```bash
# Criar um áudio de teste ou usar um existente
python -c "
from tools.audio_processor import transcribe_voice_message
result = transcribe_voice_message('test_audio.ogg')
print(result)
"
```

### Teste 2: Imagem

```bash
# Processar nota fiscal de teste
python -c "
from tools.receipt_ocr import extract_receipt_data
result = extract_receipt_data('nota_fiscal.jpg')
print(result)
"
```

### Teste 3: Webhook Local

```bash
# Iniciar webhook
python whatsapp_webhook_complete.py

# Em outro terminal, testar com curl
curl -X POST http://localhost:5000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "conversation": "Gastei 50 no almoço"
    },
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net"
    }
  }'
```

---

## 📈 Melhorias Futuras

### Próximas Features:

- [ ] **Documentos PDF**: Extrair dados de extratos bancários
- [ ] **Vídeos**: Processar vídeos curtos com informações de compras
- [ ] **Múltiplas imagens**: Processar várias notas de uma vez
- [ ] **Edição via voz**: "Deletar última despesa"
- [ ] **Relatórios por voz**: Responder relatórios em áudio
- [ ] **QR Code**: Ler QR codes de notas fiscais eletrônicas
- [ ] **Tabelas**: Extrair tabelas de planilhas fotografadas

---

## ⚠️ Limitações Atuais

### Áudio:
- ⚠️ Máximo 25MB por arquivo (limite OpenAI)
- ⚠️ Qualidade depende do ambiente (ruído)
- ⚠️ Sotaques fortes podem afetar precisão

### Imagem:
- ⚠️ Notas muito apagadas podem falhar
- ⚠️ Funciona melhor com notas brasileiras
- ⚠️ Não suporta múltiplas páginas (por enquanto)
- ⚠️ Custos maiores que texto/voz

### Geral:
- ⚠️ Requer conexão com internet
- ⚠️ Depende de APIs externas (OpenAI)
- ⚠️ Arquivos temporários precisam ser limpos periodicamente

---

## 💰 Estimativa de Custos (OpenAI)

### Uso Típico Mensal:

```
Cenário: Usuário ativo com 100 despesas/mês

Texto (70%):   70 mensagens  × $0.0001 = $0.007
Voz (20%):     20 áudios     × $0.001  = $0.020
Imagem (10%):  10 notas      × $0.010  = $0.100
                                Total:    ~$0.13/mês
```

**Custo médio por usuário: ~$0.15/mês** 💰

---

## 🎯 Resumo

| Pergunta | Resposta |
|----------|----------|
| **Recebe texto?** | ✅ Sim, nativamente |
| **Recebe voz?** | ✅ Sim, com Whisper |
| **Recebe imagem?** | ✅ Sim, com GPT-4 Vision |
| **Pronto para produção?** | ✅ Sim, todos implementados |
| **Precisa de config extra?** | ⚠️ Só a mesma API key OpenAI |
| **Funciona offline?** | ❌ Não, precisa internet |

---

## 📞 Como Integrar

### Passo 1: Configure o Webhook

```bash
python whatsapp_webhook_complete.py
```

### Passo 2: Configure sua API de WhatsApp

Aponte o webhook para: `http://seu-servidor:5000/webhook/whatsapp`

### Passo 3: Envie mensagens!

```
📝 Texto:  "Gastei 50 no almoço"
🎤 Áudio:  [Grava áudio falando a despesa]
📷 Imagem: [Foto da nota com legenda "registrar"]
```

**Tudo funcionando!** ✨

---

**Criado com Agno Framework** 🚀
*Processamento inteligente de texto, voz e imagem para gestão financeira*
