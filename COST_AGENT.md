# 💰 Agente de Gestão de Custos via WhatsApp

> **Agente Agno para controle financeiro pessoal através de conversas naturais no WhatsApp**

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Funcionalidades](#funcionalidades)
3. [Instalação e Configuração](#instalação-e-configuração)
4. [Como Usar](#como-usar)
5. [Exemplos de Conversas](#exemplos-de-conversas)
6. [Categorias de Gastos](#categorias-de-gastos)
7. [Relatórios Disponíveis](#relatórios-disponíveis)
8. [Integração com WhatsApp](#integração-com-whatsapp)
9. [Painel de Custos](#painel-de-custos)
10. [Estrutura Técnica](#estrutura-técnica)

---

## 🎯 Visão Geral

O **Agente de Gestão de Custos** é um assistente pessoal de finanças que conversa naturalmente via WhatsApp. Ele registra suas despesas, categoriza automaticamente seus gastos e gera relatórios detalhados sobre suas finanças pessoais.

### Por que usar?

✅ **Simplicidade**: Basta enviar uma mensagem como "Gastei 50 no almoço"
✅ **Automático**: Categorização inteligente de despesas
✅ **Insights**: Relatórios mensais com análises e tendências
✅ **WhatsApp**: Interface que você já usa todos os dias
✅ **Privacidade**: Seus dados ficam armazenados localmente

---

## 🚀 Funcionalidades

### 1. Registro de Despesas
- Adiciona gastos através de mensagens naturais
- Categorização automática baseada em contexto
- Detecção de método de pagamento
- Registro de data automático

### 2. Consulta de Gastos
- Lista despesas por período (mês/ano)
- Filtra por categoria específica
- Mostra resumo por categorias
- Exibe totais e percentuais

### 3. Relatórios Inteligentes
- Relatório mensal completo
- Análise de tendências (3+ meses)
- Top 5 maiores despesas
- Comparação com mês anterior
- Insights e alertas personalizados

### 4. Exportação de Dados
- Exporta dados para dashboard
- Formato JSON estruturado
- Integração com painéis externos

### 5. Gestão de Registros
- Deletar despesas por ID
- Editar categorias (em desenvolvimento)
- Histórico completo

---

## ⚙️ Instalação e Configuração

### 1. Pré-requisitos

```bash
# Python 3.9+
python --version

# Dependências do projeto
agno>=2.3.0
openai>=1.0.0
python-dotenv>=1.0.0
loguru>=0.7.0
```

### 2. Configurar Variáveis de Ambiente

Crie ou edite o arquivo `.env`:

```env
# API Keys
OPENAI_API_KEY=sua_chave_openai_aqui

# Configurações
LOG_LEVEL=INFO
DEBUG_MODE=False
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Testar Localmente (Modo Interativo)

```bash
python whatsapp_cost_agent.py
```

Isso abrirá um modo de chat interativo para testar o agente antes de integrar com WhatsApp.

---

## 💬 Como Usar

### Adicionar Despesas

Envie mensagens naturais mencionando seus gastos:

```
Você: Gastei 50 no almoço
Agente: ✅ Anotado! Almoço de R$ 50,00 em Alimentação 🍽️

Você: Uber 25 reais
Agente: ✅ Registrado! Uber de R$ 25,00 em Transporte 🚗

Você: Academia 120
Agente: ✅ Anotado! Academia de R$ 120,00 em Saúde 💪
```

### Ver Gastos

```
Você: Quanto gastei esse mês?
Agente: [Gera relatório mensal completo]

Você: Meus gastos de alimentação
Agente: [Lista todas despesas de alimentação]

Você: Resumo por categoria
Agente: [Mostra total e percentual por categoria]
```

### Relatórios

```
Você: Relatório mensal
Agente: [Relatório completo com insights]

Você: Como foram meus gastos nos últimos 3 meses?
Agente: [Análise de tendências]

Você: Estou gastando muito?
Agente: [Análise + comparação + recomendações]
```

---

## 📊 Exemplos de Conversas

### Exemplo 1: Registrando Gastos ao Longo do Dia

```
09:30 - Você: Café da manhã 15 reais
        Agente: ✅ Anotado! Café da manhã de R$ 15,00 em Alimentação ☕

12:45 - Você: Almoço restaurante 45
        Agente: ✅ Registrado! Almoço restaurante de R$ 45,00 em Alimentação 🍽️
                💡 Seus gastos com Alimentação hoje: R$ 60,00

18:00 - Você: Uber 22 no pix
        Agente: ✅ Anotado! Uber de R$ 22,00 em Transporte 🚗
                Forma de pagamento: PIX

20:30 - Você: Cinema 40 no cartão
        Agente: ✅ Registrado! Cinema de R$ 40,00 em Lazer 🎬
                Forma de pagamento: Cartão de Crédito
```

### Exemplo 2: Consultando Gastos

```
Você: Quanto gastei com alimentação esse mês?

Agente: 🍽️ **Gastos com Alimentação em Dezembro/2025**

📊 Total: R$ 1.250,00
📝 15 registros
📈 32% do total de gastos

**Principais despesas:**
1. Mercado - R$ 450,00 (15/12)
2. Restaurante - R$ 150,00 (20/12)
3. Delivery - R$ 85,00 (18/12)

💡 Sua média diária: R$ 40,32
```

### Exemplo 3: Relatório Mensal

```
Você: Relatório do mês

Agente: 📊 **Relatório Financeiro - Dezembro/2025**

💰 **Resumo Geral**
Total gasto: R$ 3.890,00
Total de registros: 45
Média diária: R$ 125,48

📊 **Gastos por Categoria**
1. 🏠 Moradia - R$ 1.500,00 (38.6%)
2. 🍽️ Alimentação - R$ 1.250,00 (32.1%)
3. 🚗 Transporte - R$ 580,00 (14.9%)
4. 🎮 Lazer - R$ 320,00 (8.2%)
5. 💊 Saúde - R$ 240,00 (6.2%)

🏆 **Top 5 Despesas**
1. Aluguel - R$ 1.200,00
2. Mercado - R$ 450,00
3. Conta de luz - R$ 180,00
4. Academia - R$ 120,00
5. Restaurante - R$ 150,00

📈 **Comparação com Novembro**
Mês anterior: R$ 3.650,00
Variação: +R$ 240,00 (+6.6%)

⚠️ **Insights**
- 📊 Moradia representa 38.6% dos seus gastos
- ⚠️ Seus gastos aumentaram 6.6% em relação ao mês anterior
- 💡 70% dos seus gastos estão concentrados em 3 categorias
```

---

## 🏷️ Categorias de Gastos

O agente categoriza automaticamente seus gastos baseado em palavras-chave:

| Categoria | Emoji | Exemplos de Palavras-Chave |
|-----------|-------|----------------------------|
| **Alimentação** | 🍽️ | restaurante, almoço, mercado, delivery, café, padaria |
| **Transporte** | 🚗 | uber, 99, combustível, gasolina, ônibus, metrô |
| **Moradia** | 🏠 | aluguel, condomínio, luz, água, gás, internet |
| **Saúde** | 💊 | farmácia, médico, exame, academia, remédio |
| **Lazer** | 🎮 | cinema, streaming, games, viagem, bar |
| **Educação** | 📚 | curso, livro, material escolar, mensalidade |
| **Serviços** | 🛠️ | cabeleireiro, manicure, conserto, lavanderia |
| **Compras** | 🛒 | roupas, eletrônicos, decoração, presentes |
| **Outros** | 📱 | tudo que não se encaixa acima |

---

## 📈 Relatórios Disponíveis

### 1. Relatório Mensal Completo

**Quando usar**: Fechamento do mês, análise geral

**Inclui**:
- Total gasto no período
- Gastos por categoria com percentuais
- Top 5 maiores despesas
- Métodos de pagamento utilizados
- Média diária de gastos
- Comparação com mês anterior
- Insights e alertas personalizados

### 2. Resumo por Categorias

**Quando usar**: Ver onde está gastando mais

**Inclui**:
- Total por categoria
- Quantidade de registros
- Percentual do total
- Lista de itens da categoria

### 3. Análise de Tendências

**Quando usar**: Entender padrões ao longo do tempo

**Inclui**:
- Evolução dos gastos (3+ meses)
- Tendência (crescente/decrescente/estável)
- Comparação mês a mês
- Média por período

### 4. Exportação para Dashboard

**Quando usar**: Visualizar em painel externo

**Formato**: JSON estruturado com:
- Dados do mês atual
- Totais acumulados
- Categorias
- Despesas recentes

---

## 📱 Integração com WhatsApp

### Opções de Integração

#### 1. **Evolution API** (Recomendado)
```bash
# Configurar Evolution API
# URL do webhook: https://seu-servidor.com/webhook/whatsapp

# O agente receberá mensagens neste formato:
{
  "message": {
    "conversation": "Gastei 50 no almoço"
  }
}
```

#### 2. **Twilio WhatsApp API**
```python
# Exemplo de integração com Twilio
from twilio.rest import Client

client = Client(account_sid, auth_token)
message = client.messages.create(
    from_='whatsapp:+14155238886',
    body=response_text,
    to='whatsapp:+5511999999999'
)
```

#### 3. **Baileys (Node.js)**
```javascript
// Exemplo com Baileys
const { makeWASocket } = require('@whiskeysockets/baileys');

sock.ev.on('messages.upsert', async ({ messages }) => {
    const msg = messages[0];
    const text = msg.message.conversation;

    // Chamar API Python do agente
    const response = await fetch('http://localhost:5000/process', {
        method: 'POST',
        body: JSON.stringify({ message: text })
    });
});
```

### Servidor Webhook (Flask)

```python
from flask import Flask, request, jsonify
from whatsapp_cost_agent import process_message

app = Flask(__name__)

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    message = data['message']['conversation']
    response = process_message(message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 🎨 Painel de Custos

### Exportar Dados para Dashboard

```python
# O agente pode exportar dados estruturados:
from agents.cost_agent import create_cost_management_agent

agent = create_cost_management_agent()
response = agent.run("Exportar dados para dashboard")

# Retorna JSON com:
{
  "current_month": {
    "period": "12/2025",
    "total": 3890.00,
    "categories": {...},
    "recent_expenses": [...]
  },
  "all_time": {
    "total": 45600.00,
    "items_count": 523
  }
}
```

### Exemplo de Dashboard HTML Simples

```html
<!DOCTYPE html>
<html>
<head>
    <title>Painel de Custos</title>
</head>
<body>
    <h1>💰 Meus Gastos</h1>
    <div id="dashboard"></div>

    <script>
        // Carregar dados do agente
        fetch('/api/dashboard')
            .then(r => r.json())
            .then(data => {
                document.getElementById('dashboard').innerHTML = `
                    <h2>Mês Atual: ${data.current_month.period}</h2>
                    <p>Total: R$ ${data.current_month.total.toFixed(2)}</p>
                `;
            });
    </script>
</body>
</html>
```

---

## 🛠️ Estrutura Técnica

### Arquivos do Projeto

```
projetosagno/
├── agents/
│   └── cost_agent.py              # Agente principal de custos
├── tools/
│   ├── cost_manager.py            # Gerenciamento de custos
│   └── cost_reports.py            # Geração de relatórios
├── data/
│   └── costs.json                 # Armazenamento de dados
├── whatsapp_cost_agent.py         # Script principal WhatsApp
└── COST_AGENT.md                  # Esta documentação
```

### Tools Disponíveis

#### `cost_manager.py`
- `add_cost()` - Adiciona nova despesa
- `list_costs()` - Lista despesas filtradas
- `get_categories_summary()` - Resumo por categoria
- `delete_cost()` - Remove despesa

#### `cost_reports.py`
- `generate_monthly_report()` - Relatório mensal completo
- `get_expense_trends()` - Análise de tendências
- `export_to_dashboard_json()` - Exportação para painel

### Armazenamento de Dados

Os dados são armazenados em `data/costs.json`:

```json
[
  {
    "id": 1,
    "description": "Almoço",
    "amount": 50.00,
    "category": "Alimentação",
    "date": "31/12/2025",
    "payment_method": "Cartão de Crédito",
    "notes": "",
    "created_at": "2025-12-31T12:30:00"
  }
]
```

---

## 🔧 Configurações Avançadas

### Customizar Categorias

Edite `agents/cost_agent.py` na seção de instruções:

```python
instructions=[
    # ...
    "📝 MinhaCategoria: palavra1, palavra2, palavra3",
    # ...
]
```

### Alterar Modelo LLM

Edite `config/settings.py`:

```python
# Para economia
DEFAULT_MODEL = "gpt-4o-mini"

# Para melhor performance
DEFAULT_MODEL = "gpt-4o"
```

### Adicionar Novos Métodos de Pagamento

Edite a seção de métodos de pagamento em `agents/cost_agent.py`.

---

## 📝 Exemplos de Uso Avançado

### Deletar Despesa

```
Você: Lista meus gastos de hoje

Agente:
1. ID: 42 - Almoço R$ 50,00
2. ID: 43 - Uber R$ 25,00

Você: Deletar despesa 42

Agente: ✅ Custo ID 42 removido com sucesso!
```

### Filtros Específicos

```
Você: Gastos de janeiro com alimentação

Agente: [Lista filtrada por mês E categoria]

Você: Quanto gastei em 2024?

Agente: [Relatório anual completo]
```

---

## 🚀 Próximos Passos

- [ ] Implementar autenticação multi-usuário
- [ ] Adicionar suporte a anexos (fotos de notas fiscais)
- [ ] OCR para extrair valores de imagens
- [ ] Integração com bancos (Open Banking)
- [ ] Lembretes automáticos de gastos recorrentes
- [ ] Metas de economia e alertas
- [ ] Exportação para Excel/PDF
- [ ] Dashboard web interativo
- [ ] Análise preditiva de gastos
- [ ] Categorias personalizáveis por usuário

---

## 💡 Dicas de Uso

1. **Registre imediatamente**: Anote gastos assim que acontecem
2. **Seja consistente**: Use descrições claras
3. **Revise semanalmente**: Peça resumos semanais
4. **Configure alertas**: Peça ao agente para alertar sobre gastos altos
5. **Use categorias**: Respeite as categorias para relatórios precisos

---

## 🤝 Contribuindo

Sugestões de melhorias são bem-vindas!

- Reportar bugs
- Sugerir novas funcionalidades
- Melhorar documentação
- Adicionar novos métodos de pagamento
- Criar novos tipos de relatórios

---

## 📄 Licença

Este projeto faz parte do **Agno Framework** e segue as práticas do framework.

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique esta documentação
2. Teste no modo interativo primeiro
3. Revise os logs em `logs/cost_agent.log`
4. Confira a configuração do `.env`

---

**Desenvolvido com Agno Framework 🚀**

*Gerencie suas finanças conversando naturalmente via WhatsApp* 💰📊
