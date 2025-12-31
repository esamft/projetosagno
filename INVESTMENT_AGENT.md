# 💎 Life OS - Investment Agent

> **Gestor de Patrimônio (Wealth Manager) baseado em Rebalanceamento Matemático**

---

## 📋 Visão Geral

O **Investment Agent** é o Wealth Manager do Life OS. Sua função é **fria e matemática**: garantir que você siga sua estratégia de alocação de ativos, comprando o que está **atrasado** (abaixo da meta) e evitando o que está **adiantado** (acima da meta).

### Tom de Voz:
**Profissional, Analítico e Objetivo.**

Sem especulação. Sem dicas quentes. Apenas matemática das metas.

---

## 🎯 Características Principais

### ✅ Gestão de Patrimônio por Buckets
- **Buckets (Classes Macro)**: Ações BR, Renda Fixa, Cripto, Internacional
- **Assets (Ativos)**: Ativos específicos dentro de cada bucket
- **Metas Percentuais**: Cada bucket e ativo tem meta de alocação

### ✅ Double-Layer Rebalancing
- **Análise Macro**: Identifica o bucket mais atrasado
- **Análise Micro**: Identifica o ativo mais atrasado dentro do bucket
- **Recomendação**: Sugere onde alocar novo aporte

### ✅ Atualização de Saldos
- **Manual**: Atualizar saldo de Renda Fixa, CDB (sem cotação)
- **Automático**: Atualizar cotações de ações e cripto

### ✅ Consulta de Patrimônio
- Resumo total por buckets
- Status de alocação (atrasado/OK/adiantado)
- Gaps vs metas

---

## 💰 Estrutura de Dados

### Buckets (Classes Macro)

Representam classes de ativos com meta percentual:

```json
{
  "id": 1,
  "name": "Ações BR",
  "meta_percentual": 30.0,
  "valor_atual": 30000.0,
  "valor_percentual_atual": 20.0
}
```

**Buckets Padrão:**
- 📈 **Ações BR** (30%) - Ações brasileiras
- 🔒 **Renda Fixa** (50%) - Tesouro, CDB, fundos
- ₿ **Cripto** (10%) - Criptomoedas
- 🌎 **Internacional** (10%) - Ativos internacionais

### Assets (Ativos)

Ativos específicos dentro de cada bucket:

```json
{
  "id": 1,
  "bucket_id": 1,
  "name": "PETR4",
  "quantity": 100,
  "price": 38.50,
  "valor_atual": 3850.0,
  "meta_percentual": 40.0,
  "valor_percentual_atual": 12.8,
  "is_manual": false
}
```

**Ativos Padrão:**
- **Ações BR**: PETR4, VALE3, WEGE3
- **Renda Fixa**: Tesouro IPCA+, CDB
- **Cripto**: BTC

**Tipos de Ativos:**
- `is_manual: true` - Atualização manual (Tesouro, CDB) - informa saldo total
- `is_manual: false` - Atualização automática (Ações, Cripto) - quantidade × preço

---

## 🧮 Algoritmo de Rebalanceamento

### Double-Layer Rebalancing

Quando você tem dinheiro para investir, o Investment Agent usa este algoritmo:

#### **1. Análise Macro (Buckets)**
```
Para cada Bucket:
  Gap = % Atual - % Meta

Exemplo:
  Ações BR: 20% atual vs 30% meta → Gap: -10% (ATRASADO)
  Renda Fixa: 60% atual vs 50% meta → Gap: +10% (ADIANTADO)

Decisão: Aportar no bucket com MAIOR gap negativo (mais atrasado)
```

#### **2. Análise Micro (Assets dentro do Bucket vencedor)**
```
Dentro do Bucket escolhido:
  Para cada Ativo:
    Gap = % Atual - % Meta

Exemplo (dentro de Ações BR):
  PETR4: 15% atual vs 40% meta → Gap: -25% (ATRASADO)
  VALE3: 0% atual vs 30% meta → Gap: -30% (MAIS ATRASADO)
  WEGE3: 5% atual vs 30% meta → Gap: -25%

Decisão: Aportar no ativo com MAIOR gap negativo (VALE3)
```

#### **3. Recomendação Final**
```
Compre R$ X de [Ativo]

Justificativa matemática:
- Bucket Y está Z% atrasado
- Ativo W dentro do bucket está K% atrasado
- Esta compra aproxima a carteira do equilíbrio ideal
```

---

## 📊 Ferramentas Disponíveis

### 1. `update_asset_balance(asset_name, new_balance)`
Atualiza saldo de um ativo manual (Renda Fixa).

**Parâmetros:**
- `asset_name`: Nome do ativo (ex: "Tesouro IPCA+", "CDB")
- `new_balance`: Novo saldo total

**Retorna:**
```json
{
  "success": true,
  "asset_name": "Tesouro IPCA+",
  "old_value": 45000.0,
  "new_value": 80000.0,
  "total_patrimonio": 185000.0
}
```

**Exemplo de Uso:**
- Usuário: "Atualize meu Tesouro IPCA+ para 80 mil"
- Agent: Chama `update_asset_balance("Tesouro IPCA+", 80000)`

---

### 2. `get_portfolio_summary()`
Retorna resumo completo do patrimônio.

**Retorna:**
```json
{
  "total_patrimonio": 150000.0,
  "buckets": [
    {
      "name": "Ações BR",
      "valor_atual": 30000.0,
      "percentual_atual": 20.0,
      "percentual_meta": 30.0,
      "gap": -10.0,
      "status": "🔴 Atrasado"
    },
    {
      "name": "Renda Fixa",
      "valor_atual": 90000.0,
      "percentual_atual": 60.0,
      "percentual_meta": 50.0,
      "gap": 10.0,
      "status": "🟢 Adiantado"
    }
  ]
}
```

**Exemplo de Uso:**
- Usuário: "Quanto eu tenho investido?"
- Agent: Chama `get_portfolio_summary()`

---

### 3. `calculate_rebalancing(aporte_amount)`
Calcula onde alocar novo aporte usando Double-Layer Rebalancing.

**Parâmetros:**
- `aporte_amount`: Valor disponível para investir

**Retorna:**
```json
{
  "success": true,
  "aporte_amount": 5000.0,
  "macro_analysis": {
    "target_bucket": "Ações BR",
    "current_percentage": 20.0,
    "target_percentage": 30.0,
    "gap": -10.0,
    "reasoning": "Bucket mais atrasado (-10%)"
  },
  "micro_analysis": {
    "target_asset": "VALE3",
    "current_percentage": 0.0,
    "target_percentage": 30.0,
    "gap": -30.0,
    "reasoning": "Ativo mais atrasado dentro do bucket (-30%)"
  },
  "recommendation": {
    "action": "BUY",
    "asset": "VALE3",
    "amount": 5000.0
  }
}
```

**Exemplo de Uso:**
- Usuário: "Tenho 5 mil para investir, onde coloco?"
- Agent: Chama `calculate_rebalancing(5000)`

---

### 4. `update_asset_price(asset_name, new_price, quantity?)`
Atualiza preço de um ativo automático (ações/cripto).

**Parâmetros:**
- `asset_name`: Nome do ativo (ex: "PETR4", "BTC")
- `new_price`: Novo preço unitário
- `quantity`: Nova quantidade (opcional)

**Retorna:**
```json
{
  "success": true,
  "asset_name": "PETR4",
  "quantity": 100,
  "price": 38.50,
  "valor_atual": 3850.0
}
```

**Exemplo de Uso:**
- Usuário: "PETR4 está em R$ 38,50"
- Agent: Chama `update_asset_price("PETR4", 38.50)`

---

### 5. `get_asset_details(asset_name?)`
Retorna detalhes de um ativo específico ou todos.

**Parâmetros:**
- `asset_name`: Nome do ativo (opcional, retorna todos se omitido)

**Retorna (ativo específico):**
```json
{
  "success": true,
  "asset": {
    "name": "PETR4",
    "bucket": "Ações BR",
    "quantity": 100,
    "price": 38.50,
    "valor_atual": 3850.0,
    "percentual_atual": 12.8,
    "percentual_meta": 40.0,
    "is_manual": false
  }
}
```

---

## 💬 Modos de Operação

### 1️⃣ Modo Consulta de Patrimônio

**Você:** "Quanto eu tenho investido?"

**Investment Agent:**
```
💰 **Patrimônio Total: R$ 150.000**

📊 **Distribuição por Classe:**

📈 **Ações BR:** R$ 30k (20% vs Meta 30%)
Status: 🔴 Atrasado (-10%)

🔒 **Renda Fixa:** R$ 90k (60% vs Meta 50%)
Status: 🟢 Adiantado (+10%)

₿ **Cripto:** R$ 15k (10% vs Meta 10%)
Status: ✅ OK

🌎 **Internacional:** R$ 15k (10% vs Meta 10%)
Status: ✅ OK

💡 **Análise:**
Sua carteira de Ações BR está atrasada em 10%.
Considere aportar nessa classe nos próximos meses para rebalancear.
```

---

### 2️⃣ Modo Oráculo de Aportes (Rebalanceamento)

**Você:** "Tenho 5 mil para investir, onde coloco?"

**Investment Agent:**
```
🧠 **Racionalização do Aporte (R$ 5.000)**

📊 **Análise Macro:**
> Sua carteira de **Ações BR** está atrasada (20% vs Meta 30%).
> Gap: -10%

🔍 **Análise Micro:**
> Dentro de Ações BR, **VALE3** é o ativo mais descontado.
> Atual: 0% | Meta: 30% | Gap: -30%

🎯 **Sugestão de Compra:**
**Compre R$ 5.000 de VALE3**

💡 **Por quê?**
Isso vai aproximar sua carteira do equilíbrio ideal, comprando o que está
'barato' (abaixo da meta) e respeitando sua estratégia de alocação.
```

---

### 3️⃣ Modo Atualização de Saldo

**Você:** "Atualize meu Tesouro IPCA+ para 80 mil"

**Investment Agent:**
```
✅ **Saldo Atualizado**

📊 **Tesouro IPCA+:** R$ 80.000
💰 **Patrimônio Total:** R$ 185.000

📈 **Impacto na Alocação:**
Renda Fixa agora representa 54% do patrimônio (Meta: 50%)
Status: 🟢 Levemente adiantado (+4%)
```

---

### 4️⃣ Modo Consulta de Ativo Específico

**Você:** "Como está minha PETR4?"

**Investment Agent:**
```
📊 **PETR4 - Detalhes:**

🪣 **Bucket:** Ações BR
💵 **Quantidade:** 100 ações
💰 **Preço Atual:** R$ 38,50
📈 **Valor Total:** R$ 3.850

🎯 **Meta:** 40% do bucket Ações BR
📊 **Atual:** 12,8% do bucket
⚖️ **Status:** 🔴 Atrasado (-27,2%)

💡 **Análise:**
PETR4 está muito abaixo da meta dentro de Ações BR.
Considere aumentar a posição nos próximos aportes.
```

---

## 🎨 Tom de Voz do Investment Agent

**"Profissional, Analítico e Objetivo"**

O Investment Agent **NÃO especula** sobre preços futuros. Ele baseia-se **estritamente na matemática das metas**.

### Exemplos de Tom Correto:

✅ **CORRETO:**
```
"Sua carteira de Ações BR está atrasada em -10%.
PETR4 é o ativo mais descontado dentro dessa classe (-25%).
Compre para rebalancear."
```

❌ **INCORRETO:**
```
"PETR4 vai subir! Compre agora!
É uma ótima oportunidade de mercado!"
```

---

✅ **CORRETO:**
```
"Cripto representa 5% do seu patrimônio, contra meta de 10%.
Considere aportar em BTC para rebalancear a alocação."
```

❌ **INCORRETO:**
```
"Bitcoin é o futuro! Invista tudo nele!
Vai valorizar 1000%!"
```

---

## 🚨 Sistema de Alertas

### Alertas de Desbalanceamento:

| Condição | Alerta |
|----------|--------|
| Gap > 15% em qualquer bucket | ⚠️ **ALERTA DE DESBALANCEAMENTO**<br>Classe X está Y% longe da meta. Isso aumenta o risco. |
| Bucket zerado | 🔴 **ATENÇÃO**<br>Você não tem exposição em X (meta: Y%). |
| Bucket muito concentrado | 🟡 **CONCENTRAÇÃO**<br>X representa Y% do patrimônio (meta: Z%). |

### Exemplo de Alerta:

```
⚠️ **ALERTA DE DESBALANCEAMENTO**

Ações BR está -18% longe da meta (12% vs 30%).
Isso aumenta o risco da sua carteira.

💡 Considere rebalancear nos próximos aportes.
Sugiro aportar R$ 15.000 em Ações BR para normalizar.
```

---

## 📁 Arquivos de Dados

### Buckets: `data/investment_buckets.json`

```json
[
  {
    "id": 1,
    "name": "Ações BR",
    "meta_percentual": 30.0,
    "valor_atual": 30000.0,
    "valor_percentual_atual": 20.0
  },
  {
    "id": 2,
    "name": "Renda Fixa",
    "meta_percentual": 50.0,
    "valor_atual": 90000.0,
    "valor_percentual_atual": 60.0
  }
]
```

### Assets: `data/assets.json`

```json
[
  {
    "id": 1,
    "bucket_id": 1,
    "name": "PETR4",
    "quantity": 100,
    "price": 38.50,
    "valor_atual": 3850.0,
    "meta_percentual": 40.0,
    "valor_percentual_atual": 12.8,
    "is_manual": false
  },
  {
    "id": 4,
    "bucket_id": 2,
    "name": "Tesouro IPCA+",
    "quantity": 1,
    "price": 80000.0,
    "valor_atual": 80000.0,
    "meta_percentual": 60.0,
    "valor_percentual_atual": 88.9,
    "is_manual": true
  }
]
```

---

## 🧪 Como Testar

### Teste no Sistema Multi-Agente:

```bash
# Demonstração automática (inclui Investment Agent)
python demo_multi_agent.py

# Modo interativo
python demo_multi_agent.py --interactive
```

### Mensagens de Teste:

**✅ Consulta de Patrimônio:**
- "Quanto eu tenho investido?"
- "Qual meu patrimônio total?"
- "Como está minha carteira?"

**✅ Oráculo de Aportes:**
- "Tenho 5 mil para investir, onde coloco?"
- "Recebi R$ 10 mil, onde devo aportar?"
- "Onde investir 3 mil?"

**✅ Atualização de Saldo:**
- "Atualize meu Tesouro IPCA+ para 80 mil"
- "Meu CDB agora tem 50 mil"
- "Atualiza Renda Fixa para 100 mil"

**✅ Atualização de Cotação:**
- "PETR4 está em 38,50"
- "BTC está em 350 mil"
- "Comprei 50 ações de VALE3 a R$ 65"

**✅ Consulta de Ativo:**
- "Como está minha PETR4?"
- "Detalhes do meu Tesouro IPCA+"
- "Quanto tenho em BTC?"

---

## 📱 Integração com WhatsApp

O Investment Agent funciona **transparentemente** através do sistema multi-agente:

```python
# whatsapp_webhook.py
from lifeos_router import LifeOSRouter

router = LifeOSRouter()

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    message = data['message']['conversation']

    # Router direciona automaticamente para Investment Agent
    result = router.route_message(message)

    send_whatsapp_message(sender, result['response'])
    return jsonify({'success': True})
```

**Palavras-chave que acionam Investment Agent:**
- investir, investimento, patrimônio, carteira
- ações, tesouro, renda fixa, cripto, BTC
- aportar, aporte, rebalancear, alocação

**O usuário não percebe** que existem múltiplos agentes!

---

## 🎯 Diferenças dos Outros Agentes

| Aspecto | Finance Agent | Productivity Agent | Investment Agent |
|---------|---------------|-------------------|------------------|
| **Foco** | Gastos de consumo | Tarefas e tempo | Patrimônio |
| **Unidade** | Reais (R$) | Pomodoros (🍅) | % Alocação |
| **Alertas** | Teto de orçamento | Sobrecarga de tempo | Desbalanceamento |
| **Tom** | Auditor financeiro | Guardião do foco | Gestor matemático |
| **Dados** | transactions.json | tasks.json | buckets.json + assets.json |
| **Conceitos** | Parcelamento, categorias | Deep Work, energia | Rebalanceamento, metas |
| **Horizonte** | Curto prazo (mês) | Curto prazo (dia/semana) | Longo prazo (anos) |

---

## 💡 Boas Práticas

### 1. **Defina Metas Realistas**
- Baseie as metas percentuais no seu perfil de risco
- Conservador: mais Renda Fixa (60-70%)
- Moderado: balanceado (50/40/10)
- Agressivo: mais Ações (40-50%)

### 2. **Atualize Regularmente**
- Atualize cotações semanalmente
- Atualize saldos de Renda Fixa mensalmente
- Rebalanceie trimestralmente ou quando gap > 15%

### 3. **Respeite a Matemática**
- Não tente "acertar o timing do mercado"
- Siga as recomendações do rebalanceamento
- Compre o que está atrasado, mesmo que não pareça "atraente"

### 4. **Diversifique Dentro dos Buckets**
- Não concentre tudo em um único ativo
- Respeite as metas percentuais dentro de cada bucket
- Ações BR: diversifique setores (petróleo, mineração, varejo, etc)

---

## 🚀 Próximas Features

- [ ] Integração com APIs de cotação (B3, CoinGecko)
- [ ] Atualização automática de preços
- [ ] Histórico de aportes e rebalanceamentos
- [ ] Gráficos de evolução patrimonial
- [ ] Simulação de aportes futuros
- [ ] Sugestão de rebalanceamento por venda (não só compra)
- [ ] Multi-moeda (USD, EUR)
- [ ] Importação de extratos (CSV)

---

## 📊 Status

| Componente | Status |
|-----------|--------|
| **Agente** | ✅ Implementado |
| **Ferramentas** | ✅ 5 tools criadas |
| **Integração Multi-Agente** | ✅ Completa |
| **Documentação** | ✅ Completa |
| **Testes** | ⚠️ Pendente test_investment_agent.py |
| **WhatsApp** | ✅ Compatível (via router) |

---

**Desenvolvido com Agno Framework para Life OS** 🚀

*Profissional. Analítico. Objetivo. Sem especulação. Apenas matemática.*
