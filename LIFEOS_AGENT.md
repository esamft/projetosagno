

# 💰 Life OS - Agente Financeiro

> **Auditor Financeiro Pessoal com foco em Gestão de Gastos e Disciplina Orçamentária**

---

## 🎯 Visão Geral

O **Life OS Financial Agent** é um agente de IA especializado em eliminar a fricção do registro de gastos e manter você consciente da sua saúde financeira.

### Missão Dupla:
1. **Eliminar Fricção**: Transformar texto/áudio/imagem em dados estruturados automaticamente
2. **Consciência Financeira**: Manter você informado sobre sua saúde financeira imediata e futura

### Tom de Voz:
**Profissional, Analítico, Direto** - Um auditor financeiro, não um coach motivacional.

---

## 🚀 Início Rápido

### Teste Imediato (Modo Interativo):

```bash
python test_lifeos_agent.py --interactive
```

### Exemplos de Uso:

```
👤 Você: Gastei 50 no almoço no pix

🤖 Life OS:
✅ **Salvo:** Almoço (R$ 50,00) em Alimentação.

📊 **Status de 12/2025:**
> Gasto Total: R$ 450,00
> Restante Global: R$ 4.550,00

🚨 **Atenção:**
✅ Todos os orçamentos estão saudáveis
```

---

## 🎨 Diferenças vs Agente Anterior

| Aspecto | Agente Anterior | Life OS Agent |
|---------|-----------------|---------------|
| **Tom** | Amigável, encorajador | Profissional, direto (auditor) |
| **Parcelamento** | ❌ Não suportado | ✅ Suporte completo |
| **Tipos Pagamento** | Opcional | Obrigatório (Pix/Crédito/Débito) |
| **Orçamento** | Sem tetos | Tetos por categoria + global |
| **Futuro** | Apenas histórico | Análise de compromissos futuros |
| **Alertas** | Informativos | Amarelo (80%) e Vermelho (100%) |
| **Formato Resposta** | Flexível | Formato fixo MODO 1 e 2 |

---

## 📋 Funcionalidades

### 1. **Registro Inteligente de Transações**

#### Campos Extraídos Automaticamente:
- ✅ **Descrição** - Concisa (ex: "Almoço", "Uber", "Netflix")
- ✅ **Valor** - Total da compra
- ✅ **Data** - Automática (hoje) se não informada
- ✅ **Categoria** - Inferida por contexto
- ✅ **Tipo** - Pix, Crédito ou Débito
- ✅ **Parcelamento** - Número de parcelas (se aplicável)

#### Exemplos de Entrada:

```
"Gastei 45 no almoço no pix"
→ Descrição: Almoço, Valor: 45, Categoria: Alimentação, Tipo: Pix

"Comprei um iPhone de 3000 em 10x no crédito"
→ Descrição: iPhone, Valor: 3000, Categoria: Compras, Tipo: Crédito, Parcelas: 10

"Uber 25 reais"
→ Descrição: Uber, Valor: 25, Categoria: Transporte, Tipo: [pergunta]
```

---

### 2. **Parcelamento Inteligente**

#### Como Funciona:

Quando você registra:
```
"Comprei um celular de 1200 em 12x"
```

O sistema:
1. Divide: R$ 1.200 ÷ 12 = R$ 100/mês
2. Cria 12 registros (1 para cada mês)
3. Impacta o orçamento ATUAL com R$ 100
4. Reserva R$ 100 nos próximos 11 meses

#### Análise de Futuro:

Ao perguntar sobre meses futuros, o agente mostra:
- **Já Comprometido**: Soma das parcelas fixas
- **% do Orçamento**: Percentual consumido antes do mês começar
- **Principais Vilões**: Maiores parcelas

---

### 3. **Categorização Automática**

| Categoria | Palavras-Chave |
|-----------|----------------|
| 🍽️ **Alimentação** | restaurante, almoço, mercado, delivery, café |
| 🚗 **Transporte** | uber, 99, posto, combustível, gasolina |
| 🏠 **Moradia** | aluguel, condomínio, luz, água, gás, internet |
| 💊 **Saúde** | farmácia, médico, exame, academia |
| 🎮 **Lazer** | cinema, streaming, netflix, games |
| 📚 **Educação** | curso, livro, mensalidade |
| 🛠️ **Serviços** | cabeleireiro, manicure, conserto |
| 🛒 **Compras** | roupas, eletrônicos, decoração |
| 📱 **Outros** | demais gastos |

---

### 4. **Orçamento e Alertas**

#### Tetos Padrão (Configuráveis):

```json
{
  "global_limit": 5000.00,
  "categories": {
    "Alimentação": 1200.00,
    "Transporte": 800.00,
    "Moradia": 2000.00,
    "Saúde": 500.00,
    "Lazer": 400.00,
    "Educação": 300.00,
    "Serviços": 300.00,
    "Compras": 500.00,
    "Outros": 300.00
  }
}
```

#### Sistema de Alertas:

| Status | Condição | Símbolo |
|--------|----------|---------|
| **Verde** | < 80% do teto | ✅ |
| **Amarelo** | 80% - 100% | ⚠️ |
| **Vermelho** | > 100% | 🚨 |

---

## 📊 Modos de Resposta

### MODO 1: Pós-Registro (Feedback Imediato)

**Formato Fixo:**

```
✅ **Salvo:** [Descrição] (R$ [Valor]) em [Categoria] [em Xx se parcelado].

📊 **Status de [Mês Atual]:**
> Gasto Total: R$ [Total]
> Restante Global: R$ [Restante]

🚨 **Atenção:**
[Alertas de categorias em Amarelo/Vermelho OU "✅ Todos os orçamentos estão saudáveis"]
```

**Exemplo Real:**

```
✅ **Salvo:** iPhone (R$ 3.000,00) em Compras em 10x.

📊 **Status de 12/2025:**
> Gasto Total: R$ 3.200,00
> Restante Global: R$ 1.800,00

🚨 **Atenção:**
🚨 Compras: 110% do teto usado (Vermelho)
⚠️ Transporte: 85% do teto usado (Amarelo)
```

---

### MODO 2: Consulta de Futuro (Previsibilidade)

**Gatilhos:**
- "mês que vem"
- "posso gastar?"
- "futuro"
- "próximo mês"

**Formato Fixo:**

```
🔮 **Visão de [Mês]:**
Você já começa o mês devendo **R$ [Comprometido]**.

📉 **Impacto:**
Isso consome [X]% do seu orçamento total antes mesmo do mês começar.
Seus principais vilões são:
- [Item 1]: R$ [Valor] ([Parcela X/Y])
- [Item 2]: R$ [Valor] ([Parcela X/Y])

💡 **Veredito:**
[Opinião direta e firme sobre fazer ou não novas dívidas]
```

**Exemplo Real:**

```
🔮 **Visão de 01/2026:**
Você já começa o mês devendo **R$ 1.450,00**.

📉 **Impacto:**
Isso consome 29% do seu orçamento total antes mesmo do mês começar.
Seus principais vilões são:
- iPhone: R$ 300,00 (2/10)
- Notebook: R$ 450,00 (5/12)
- Academia: R$ 200,00 (3/6)

💡 **Veredito:**
Você ainda tem margem para pequenas compras, mas evite novos parcelamentos longos.
Seu comprometimento futuro já é significativo.
```

---

## 🔧 Configuração de Tetos Orçamentários

### Arquivo: `data/budgets.json`

```json
{
  "global_limit": 5000.00,
  "categories": {
    "Alimentação": 1200.00,
    "Transporte": 800.00,
    "Moradia": 2000.00,
    "Saúde": 500.00,
    "Lazer": 400.00,
    "Educação": 300.00,
    "Serviços": 300.00,
    "Compras": 500.00,
    "Outros": 300.00
  }
}
```

**Personalizar:**
1. Edite o arquivo `data/budgets.json`
2. Ajuste valores conforme sua realidade
3. O agente usará os novos limites automaticamente

---

## 💻 Estrutura de Dados

### Modelo de Transação:

```json
{
  "id": 1,
  "description": "Almoço",
  "total_amount": 50.00,
  "installment_amount": 50.00,
  "installment_number": 1,
  "total_installments": 1,
  "category": "Alimentação",
  "payment_type": "Pix",
  "date": "31/12/2025",
  "month_year": "12/2025",
  "notes": "",
  "created_at": "2025-12-31T12:00:00"
}
```

### Campos Especiais para Parcelamento:

```json
{
  "total_amount": 1200.00,        // Valor TOTAL da compra
  "installment_amount": 100.00,   // Valor DESTA parcela
  "installment_number": 1,         // Parcela atual
  "total_installments": 12         // Total de parcelas
}
```

---

## 🧪 Testes

### Teste Automático (8 Cenários):

```bash
python test_lifeos_agent.py
```

**Cenários Testados:**
1. ✅ Registro Simples - Pix
2. ✅ Registro Simples - Transporte
3. ✅ Parcelamento - Compra Grande
4. ✅ Parcelamento - Formato Alternativo
5. ✅ Informação Incompleta
6. ✅ Consulta de Resumo
7. ✅ Consulta de Futuro
8. ✅ Análise de Impacto

### Modo Interativo:

```bash
python test_lifeos_agent.py --interactive
```

Permite conversar livremente com o agente.

---

## 📱 Integração com WhatsApp

O Life OS Agent pode ser usado via WhatsApp através das mesmas integrações do agente anterior:

### Opção 1: Evolution API

```bash
# Usar script de integração
python evolution_integration.py
```

### Opção 2: Twilio

Veja `INTEGRATION_GUIDE.md` para detalhes.

### Webhook Completo:

O agente funciona com `whatsapp_webhook_complete.py` que suporta:
- ✅ Texto
- ✅ Voz (transcrição via Whisper)
- ✅ Imagem (OCR de notas fiscais via GPT-4 Vision)

---

## 🎯 Tom de Voz - Exemplos

### ❌ ERRADO (Muito Amigável):

```
"Poxa, parece que você gastou bastante! Mas tudo bem, mês que vem é outro! 😊"
"Que legal que você está planejando o futuro! 🎉"
```

### ✅ CORRETO (Auditor Profissional):

```
"Você estourou o orçamento em 15%. Isso impacta negativamente seus objetivos."
"Você já comprometeu 70% do orçamento de janeiro. Evite novas dívidas."
```

---

## 🔄 Comparação: Agente Antigo vs Life OS

### Registro de Gasto:

**Agente Antigo:**
```
👤: Gastei 50 no almoço
🤖: ✅ Anotado! Almoço de R$ 50,00 em Alimentação 🍽️
```

**Life OS:**
```
👤: Gastei 50 no almoço no pix
🤖: ✅ **Salvo:** Almoço (R$ 50,00) em Alimentação.

📊 **Status de 12/2025:**
> Gasto Total: R$ 2.450,00
> Restante Global: R$ 2.550,00

🚨 **Atenção:**
⚠️ Alimentação: 82% do teto usado (Amarelo)
```

---

## 📊 Dashboard / Painel (Integração)

O Life OS foi projetado para alimentar um painel externo.

### Endpoints de Dados:

#### 1. Resumo Mensal:
```python
from tools.lifeos_cost_manager import get_month_summary

summary = get_month_summary(month=12, year=2025)
# Retorna JSON com totais, categorias, alertas
```

#### 2. Compromissos Futuros:
```python
from tools.lifeos_cost_manager import get_future_commitments

future = get_future_commitments(months_ahead=3)
# Retorna JSON com parcelas dos próximos 3 meses
```

#### 3. Todas as Transações:
```python
from tools.lifeos_cost_manager import _load_transactions

transactions = _load_transactions()
# Lista completa para análises customizadas
```

---

## 🚀 Próximos Passos

### Para Usar Agora:

```bash
# 1. Testar localmente
python test_lifeos_agent.py --interactive

# 2. Registrar alguns gastos
"Gastei 50 no almoço no pix"
"Comprei um notebook de 2400 em 12x no crédito"

# 3. Consultar status
"Quanto gastei esse mês?"
"Posso fazer uma compra no mês que vem?"
```

### Para Integrar com WhatsApp:

```bash
# Seguir guia anterior
./setup_evolution.sh
python evolution_integration.py
```

### Para Integrar com Painel:

1. Use `lifeos_cost_manager.py` como backend
2. Crie endpoints REST/GraphQL se necessário
3. Consuma JSONs retornados pelas tools

---

## 📁 Arquivos do Projeto

### Agente Life OS:
```
✅ agents/lifeos_financial_agent.py    # Agente principal
✅ tools/lifeos_cost_manager.py        # Backend de dados
✅ test_lifeos_agent.py                # Testes
✅ LIFEOS_AGENT.md                     # Esta documentação
```

### Dados:
```
📊 data/transactions.json              # Todas as transações
📊 data/budgets.json                   # Tetos orçamentários
```

---

## 💡 Dicas de Uso

1. **Seja específico**: Inclua tipo de pagamento sempre
2. **Parcelamento**: Mencione número de parcelas em compras no crédito
3. **Consulte o futuro**: Antes de parcelar, pergunte sobre compromissos
4. **Ajuste tetos**: Personalize os limites na sua realidade
5. **Tom firme**: O agente será direto - aceite a crítica construtiva

---

## 🔧 Troubleshooting

### Problema: Agente não pergunta tipo de pagamento

**Solução**: Mencione explicitamente ("no pix", "no crédito")

### Problema: Parcelamento não funciona

**Solução**: Use formato claro: "em 10x" ou "10 parcelas"

### Problema: Categoria errada

**Solução**: Após registro, pode editar `data/transactions.json` diretamente

### Problema: Teto muito baixo

**Solução**: Edite `data/budgets.json` com valores realistas

---

## 📞 Suporte

- **Documentação Geral**: `COST_AGENT.md`
- **Integração WhatsApp**: `INTEGRATION_GUIDE.md`
- **Suporte Multimodal**: `MULTIMODAL_SUPPORT.md`

---

**Desenvolvido com Agno Framework para Life OS** 🚀

*Gestão financeira profissional, direta e sem rodeios.*
