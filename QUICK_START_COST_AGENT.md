# 🚀 Início Rápido - Agente de Custos WhatsApp

## ⚡ Setup em 3 Minutos

### 1. Verificar Dependências

```bash
# Já instalado no projeto
pip install -r requirements.txt
```

### 2. Configurar Variável de Ambiente

Certifique-se de que o arquivo `.env` tem sua chave OpenAI:

```env
OPENAI_API_KEY=sua_chave_aqui
```

### 3. Testar o Agente

#### Modo Teste Automático
```bash
python test_cost_agent.py
```

#### Modo Interativo (simula WhatsApp)
```bash
python test_cost_agent.py --interactive
```

ou

```bash
python whatsapp_cost_agent.py
```

---

## 📱 Exemplos de Uso Rápido

### No Modo Interativo

```
👤 Você: Gastei 50 no almoço
🤖 Agente: ✅ Anotado! Almoço de R$ 50,00 em Alimentação 🍽️

👤 Você: Uber 25 reais
🤖 Agente: ✅ Registrado! Uber de R$ 25,00 em Transporte 🚗

👤 Você: Quanto gastei esse mês?
🤖 Agente: [Relatório mensal completo]
```

---

## 🔌 Conectar ao WhatsApp

### Opção 1: Evolution API (Mais Fácil)

1. Configure uma instância do Evolution API
2. Configure webhook para: `http://seu-servidor:5000/webhook/whatsapp`
3. O agente já está pronto para receber mensagens!

### Opção 2: Código Personalizado

Veja exemplos em `whatsapp_cost_agent.py` para:
- Flask webhook
- FastAPI webhook
- Twilio integration
- Baileys integration

---

## 📊 Principais Comandos

| Comando | Resultado |
|---------|-----------|
| "Gastei 50 no almoço" | Adiciona custo de R$ 50 |
| "Uber 25" | Adiciona transporte de R$ 25 |
| "Quanto gastei esse mês?" | Relatório mensal completo |
| "Gastos de alimentação" | Lista despesas de comida |
| "Resumo por categoria" | Totais por categoria |
| "Relatório mensal" | Análise detalhada |

---

## 📁 Estrutura de Arquivos

```
projetosagno/
├── agents/cost_agent.py              # Agente principal ⭐
├── tools/cost_manager.py             # Gerenciamento de custos
├── tools/cost_reports.py             # Relatórios
├── whatsapp_cost_agent.py            # Script WhatsApp ⭐
├── test_cost_agent.py                # Testes ⭐
├── data/costs.json                   # Seus dados (criado automaticamente)
└── COST_AGENT.md                     # Documentação completa
```

---

## 🎯 Categorias Automáticas

O agente categoriza automaticamente:

- 🍽️ **Alimentação**: almoço, mercado, delivery, café
- 🚗 **Transporte**: uber, combustível, ônibus
- 🏠 **Moradia**: aluguel, luz, água, internet
- 💊 **Saúde**: farmácia, médico, academia
- 🎮 **Lazer**: cinema, streaming, viagem
- 📚 **Educação**: curso, livro
- 🛒 **Compras**: roupas, eletrônicos

---

## 🔧 Troubleshooting Rápido

### Erro: "OPENAI_API_KEY not found"
```bash
# Adicione ao .env
echo "OPENAI_API_KEY=sk-..." >> .env
```

### Erro: "Module not found"
```bash
pip install -r requirements.txt
```

### Dados não aparecem
```bash
# Verifique o arquivo
cat data/costs.json
```

---

## 📖 Documentação Completa

Para mais detalhes, veja:
- **COST_AGENT.md** - Documentação completa
- **README.md** - Guia geral do projeto Agno

---

## 💡 Próximos Passos

1. ✅ Teste localmente com `python whatsapp_cost_agent.py`
2. ✅ Adicione alguns custos de exemplo
3. ✅ Veja o relatório mensal
4. 🚀 Configure integração com WhatsApp
5. 📊 Crie seu dashboard personalizado

---

**Pronto para usar!** 🎉

Qualquer dúvida, consulte a documentação completa em `COST_AGENT.md`
