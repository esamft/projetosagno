# 🎯 Life OS - Sistema Multi-Agente

> **Arquitetura de Orquestração com Router Inteligente**

---

## 📋 Visão Geral

O **Life OS Multi-Agent System** é uma arquitetura escalável que utiliza um **Agente Orquestrador (Router)** para direcionar mensagens do usuário para agentes especializados.

### Arquitetura:

```
Usuário
  ↓
📝 Mensagem
  ↓
🎯 Orquestrador (Router)
  ├→ Classifica intenção
  └→ Retorna JSON com intent
     ↓
💰 Finance Agent  |  📋 Productivity Agent  |  💬 General Chat
     ↓                      ↓                        ↓
  Resposta              Resposta                 Resposta
     ↓                      ↓                        ↓
  Usuário                Usuário                  Usuário
```

---

## 🧩 Componentes

### 1. **Orquestrador (Router)**

**Arquivo:** `agents/orchestrator_agent.py`

**Responsabilidades:**
- ✅ Analisar mensagem do usuário
- ✅ Identificar intenção
- ✅ Retornar JSON com classificação
- ❌ NÃO responde ao usuário
- ❌ NÃO executa ações

**Modelo:** `gpt-4o-mini` (mais barato para roteamento)

**Saída:**
```json
{
  "intent": "finance_agent" | "productivity_agent" | "general_chat",
  "reasoning": "Breve explicação de 5 palavras"
}
```

---

### 2. **Agentes Especializados**

#### **Finance Agent** ✅ Implementado

**Arquivo:** `agents/lifeos_financial_agent.py`

**Acionado quando:**
- Gastos, compras, pagamentos
- Saldo, orçamento, limites
- Parcelamento, crédito, dívidas
- Análise de notas fiscais
- Decisões de compra

**Palavras-chave:**
gastar, comprar, pagar, R$, reais, dinheiro, preço, pix, cartão, orçamento

**Modelo:** `gpt-4o`

---

#### **Productivity Agent** 🚧 Em Desenvolvimento

**Arquivo:** `agents/productivity_agent.py` (TODO)

**Será acionado quando:**
- Tarefas, compromissos, lembretes
- Trabalho, estudos, projetos
- Gestão de tempo, prazos
- Pomodoros, Deep Work

**Palavras-chave:**
tarefa, fazer, trabalho, estudar, reunião, lembrar, prazo

---

#### **General Chat** ✅ Implementado

**Tratamento:** Resposta direta no router (sem agente especializado)

**Acionado quando:**
- Saudações: "Oi", "Bom dia"
- Agradecimentos: "Obrigado", "Valeu"
- Ajuda: "Como funciona?"
- Despedidas: "Tchau", "Até"

---

### 3. **Sistema de Roteamento**

**Arquivo:** `lifeos_router.py`

**Classe:** `LifeOSRouter`

**Métodos:**

```python
router = LifeOSRouter()

# Rotear mensagem
result = router.route_message("Gastei 50 no almoço")

# Retorna:
{
    "agent_used": "finance_agent",
    "intent": "finance_agent",
    "reasoning": "Usuário mencionou gasto e valor",
    "response": "✅ **Salvo:** Almoço (R$ 50,00)..."
}
```

---

## 🔄 Fluxo Completo

### Exemplo: "Gastei 50 no almoço no pix"

```
1. Usuário envia mensagem
   ↓
2. Router recebe e chama Orquestrador
   ↓
3. Orquestrador analisa:
   "Mensagem menciona 'gastei' + valor → finance_agent"
   ↓
4. Orquestrador retorna JSON:
   {
     "intent": "finance_agent",
     "reasoning": "Usuário mencionou gasto e valor"
   }
   ↓
5. Router parseia JSON e roteia para Finance Agent
   ↓
6. Finance Agent processa:
   - Extrai: description="Almoço", amount=50, payment_type="Pix"
   - Registra no banco de dados
   - Gera resposta formatada (MODO 1)
   ↓
7. Router retorna resposta ao usuário:
   "✅ **Salvo:** Almoço (R$ 50,00) em Alimentação.
    📊 **Status de 12/2025:**
    > Gasto Total: R$ 450,00
    ..."
```

---

## 🚀 Como Usar

### Modo Automático (Demonstração):

```bash
python demo_multi_agent.py
```

**Testa automaticamente:**
- 💰 Finanças (4 cenários)
- 📋 Produtividade (3 cenários)
- 💬 Conversa Geral (3 cenários)

---

### Modo Interativo:

```bash
python demo_multi_agent.py --interactive
```

**Permite conversar** livremente e ver o roteamento acontecendo.

---

### Programaticamente:

```python
from lifeos_router import LifeOSRouter

# Criar router
router = LifeOSRouter()

# Processar mensagem
result = router.route_message("Gastei 50 no almoço")

print(f"Agent usado: {result['agent_used']}")
print(f"Resposta: {result['response']}")
```

---

## 📊 Exemplos de Roteamento

### ✅ Roteamento Correto

| Mensagem | Intent | Agente | Razão |
|----------|--------|--------|-------|
| "Gastei 50 no almoço" | `finance_agent` | Finance | Gasto + valor |
| "Quanto gastei esse mês?" | `finance_agent` | Finance | Consulta financeira |
| "Posso comprar iPhone 3000?" | `finance_agent` | Finance | Decisão de compra |
| "Preciso estudar matemática" | `productivity_agent` | Productivity* | Tarefa/ação |
| "Me lembra de ligar" | `productivity_agent` | Productivity* | Lembrete |
| "Oi, tudo bem?" | `general_chat` | General | Saudação |
| "Obrigado!" | `general_chat` | General | Agradecimento |

\* *Em desenvolvimento*

---

## 🛡️ Fallback e Tratamento de Erros

### Se o Orquestrador falhar:

O router tem **classificação de fallback** baseada em palavras-chave:

```python
def _fallback_classification(message: str) -> str:
    # Analisa palavras-chave financeiras
    if 'gastar' in message or 'R$' in message:
        return "finance_agent"

    # Analisa palavras-chave de produtividade
    if 'tarefa' in message or 'fazer' in message:
        return "productivity_agent"

    # Padrão: general_chat
    return "general_chat"
```

---

## 🔧 Adicionar Novos Agentes

### Passo 1: Criar Agente Especializado

```python
# agents/new_agent.py

from agno.agent import Agent
from agno.models.openai import OpenAIChat

def create_new_agent() -> Agent:
    return Agent(
        name="New Agent",
        model=OpenAIChat(id="gpt-4o"),
        instructions=[...],
        tools=[...],
        markdown=True
    )
```

---

### Passo 2: Registrar no Router

```python
# lifeos_router.py

class LifeOSRouter:
    def __init__(self):
        self.agents = {
            "finance_agent": create_lifeos_financial_agent(),
            "productivity_agent": create_productivity_agent(),
            "new_agent": create_new_agent(),  # ← Adicionar aqui
        }
```

---

### Passo 3: Atualizar Orquestrador

```python
# agents/orchestrator_agent.py

instructions=[
    # ...
    "## 4. NEW AGENT (`new_agent`)",
    "Acione quando o usuário falar sobre:",
    "- [Descrição do escopo]",
    "- Palavras-chave: [lista]",
    # ...
]
```

---

## 📱 Integração com WhatsApp

O sistema multi-agente funciona **transparentemente** com WhatsApp:

```python
# whatsapp_integration.py

from lifeos_router import LifeOSRouter

router = LifeOSRouter()

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    message = data['message']['conversation']

    # Router cuida de tudo automaticamente
    result = router.route_message(message)

    # Enviar resposta ao usuário
    send_whatsapp_message(sender, result['response'])

    return jsonify({'success': True})
```

**Usuário não percebe** que existem múltiplos agentes - é tudo transparente!

---

## 🎨 Vantagens da Arquitetura

### ✅ Escalabilidade
- Adicionar novos agentes é simples
- Não precisa modificar código existente
- Cada agente é independente

### ✅ Manutenibilidade
- Lógica separada por domínio
- Fácil de testar individualmente
- Código organizado

### ✅ Eficiência
- Orquestrador usa modelo barato (gpt-4o-mini)
- Agentes usam modelos apropriados
- Otimização de custos

### ✅ Flexibilidade
- Agentes podem ter diferentes modelos
- Diferentes sets de ferramentas
- Tom de voz específico por domínio

---

## 💰 Custos Estimados

### Por Mensagem:

```
Orquestrador (classificação):
- gpt-4o-mini: ~$0.00001 por mensagem

Agentes Especializados:
- Finance Agent (gpt-4o): ~$0.001 por mensagem
- Productivity Agent (gpt-4o): ~$0.001 por mensagem

Total médio: ~$0.001 por mensagem
```

### Usuário Típico (100 mensagens/mês):

```
100 mensagens × $0.001 = $0.10/mês
```

**Muito eficiente!** 💰

---

## 🧪 Testes

### Teste do Orquestrador Isolado:

```bash
python agents/orchestrator_agent.py
```

Testa classificação de 10 mensagens diferentes.

---

### Teste do Sistema Completo:

```bash
python demo_multi_agent.py
```

Demonstra roteamento automático.

---

### Teste Interativo:

```bash
python demo_multi_agent.py --interactive
```

Conversa livre com o sistema.

---

## 📊 Métricas e Logging

O sistema loga **todo o fluxo** de roteamento:

```
14:30:15 | 📝 Analisando mensagem: 'Gastei 50 no almoço'
14:30:16 | 🎯 Intent: finance_agent | Reasoning: Usuário mencionou gasto
14:30:16 | 💰 Roteando para Finance Agent...
14:30:18 | ✅ Resposta gerada com sucesso
```

**Útil para:**
- Debugging
- Análise de uso
- Otimização de roteamento

---

## 🚧 Roadmap

### Curto Prazo:
- [ ] Implementar Productivity Agent
- [ ] Adicionar métricas de acurácia do router
- [ ] Dashboard de uso por agente

### Médio Prazo:
- [ ] Health & Wellness Agent
- [ ] Learning & Knowledge Agent
- [ ] Social Agent (mensagens, contatos)

### Longo Prazo:
- [ ] Multi-modal routing (voz, imagem)
- [ ] Context-aware routing (histórico)
- [ ] Auto-scaling de agentes

---

## 📁 Estrutura de Arquivos

```
projetosagno/
├── agents/
│   ├── orchestrator_agent.py      # 🎯 Router (classificador)
│   ├── lifeos_financial_agent.py  # 💰 Finance Agent
│   ├── productivity_agent.py      # 📋 Productivity (TODO)
│   └── __init__.py
├── lifeos_router.py               # 🔀 Sistema de roteamento
├── demo_multi_agent.py            # 🎬 Demonstração
└── MULTI_AGENT_SYSTEM.md          # 📖 Esta documentação
```

---

## 💡 Boas Práticas

### 1. **Orquestrador Leve**
- Use modelo barato (gpt-4o-mini)
- Instruções concisas
- Apenas classificação (sem tools)

### 2. **Agentes Especializados**
- Modelos apropriados para complexidade
- Tools específicas do domínio
- Instruções detalhadas

### 3. **Fallback Robusto**
- Sempre tenha classificação de backup
- Trate erros graciosamente
- Nunca deixe usuário sem resposta

### 4. **Logging Completo**
- Logue todo o fluxo de roteamento
- Facilita debugging
- Permite análise de uso

---

## 🔗 Links Relacionados

- `LIFEOS_AGENT.md` - Finance Agent completo
- `COST_AGENT.md` - Agente original
- `INTEGRATION_GUIDE.md` - WhatsApp
- `RESUMO_FINAL.md` - Visão geral do projeto

---

## ✅ Status

| Componente | Status |
|-----------|--------|
| Orquestrador | ✅ Implementado |
| Finance Agent | ✅ Implementado |
| Productivity Agent | 🚧 TODO |
| Router System | ✅ Implementado |
| Testes | ✅ Funcionando |
| Documentação | ✅ Completa |
| WhatsApp Integration | ✅ Compatível |

---

**Desenvolvido com Agno Framework para Life OS** 🚀

*Arquitetura escalável, modular e eficiente.*
