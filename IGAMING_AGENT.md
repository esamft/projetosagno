# 🎰 Agente de Inteligência de Mercado - iGaming Brasil

## 📋 Descrição

Agente especializado em análise de mercado de apostas esportivas (iGaming) focado no cenário brasileiro. Realiza levantamento detalhado de ofertas de bônus e analisa termos e condições para determinar a viabilidade real das promoções.

## 🎯 Funcionalidades

- ✅ Identifica principais casas de apostas operando legalmente no Brasil
- ✅ Busca ofertas ativas de bônus (Boas-vindas, Aposta Grátis, Sem Depósito)
- ✅ Analisa "letras miúdas" dos Termos e Condições
- ✅ Calcula score de viabilidade de cada oferta
- ✅ Gera tabela comparativa ordenada por facilidade

## 📦 Componentes

### 1. Tools (Ferramentas)

#### `tools/igaming_search.py`
- **get_major_betting_houses()**: Lista as principais casas do Brasil
- **search_betting_offers(casas)**: Busca ofertas de múltiplas casas

#### `tools/tc_analyzer.py`
- **analyze_terms_and_conditions(ofertas_json)**: Analisa T&C e calcula viabilidade
- **format_comparative_table(analise_json)**: Gera tabela markdown comparativa

### 2. Agente

#### `agents/igaming_agent.py`
- **create_igaming_intelligence_agent()**: Factory do agente especializado

### 3. Scripts de Execução

#### `igaming_main.py`
- Script principal para executar análise completa

## 🚀 Como Usar

### Opção 1: Script Standalone

```bash
python igaming_main.py
```

### Opção 2: Uso Programático

```python
from agents.igaming_agent import create_igaming_intelligence_agent

# Criar agente
agent = create_igaming_intelligence_agent()

# Executar análise
response = agent.run("""
    Analise as ofertas de bônus das casas de apostas brasileiras
    e apresente uma tabela comparativa
""")

print(response.content)
```

### Opção 3: Queries Personalizadas

```python
# Análise de casas específicas
response = agent.run("Analise apenas Bet365, Betano e Sportingbet")

# Foco em tipo específico de bônus
response = agent.run("Busque apenas ofertas de aposta grátis")

# Análise detalhada de uma casa
response = agent.run("Faça análise detalhada dos T&C da Betano")
```

## 📊 Dados Extraídos

Para cada oferta, o agente extrai:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| **Casa de Apostas** | Nome da plataforma | Bet365 |
| **Oferta** | Descrição do bônus | 100% até R$ 200,00 |
| **Rollover** | Requisito de aposta | 5x o valor do bônus |
| **Odds Mínimas** | Cotação mínima | 1.20 |
| **Validade** | Prazo para cumprir | 30 dias |
| **Depósito Mínimo** | Valor mínimo | R$ 30,00 |
| **Restrições** | Métodos excluídos | Não válido para Skrill |
| **Score** | Viabilidade (0-100) | 85 |
| **Facilidade** | Classificação | Muito Fácil |

## 🎯 Score de Viabilidade

O agente calcula um score de 0 a 100 baseado em:

### Critérios de Penalização

- **Rollover Alto**: -20 a -30 pontos
  - 10x ou mais: -30
  - 7-8x: -20
  - 5-6x: -10

- **Odds Mínimas**: -15 a -25 pontos
  - ≥2.0: -25
  - 1.70-2.0: -15

- **Validade Curta**: -20 pontos
  - ≤7 dias: -20
  - 30 dias: -5

- **Restrições de Pagamento**: -10 pontos

### Classificação Final

| Score | Classificação | Facilidade |
|-------|--------------|------------|
| 80-100 | 🟢 Excelente | Muito Fácil |
| 60-79 | 🟡 Bom | Fácil |
| 40-59 | 🟠 Regular | Moderado |
| 0-39 | 🔴 Difícil | Difícil |

## 📋 Exemplo de Saída

```markdown
# 📊 Comparativo de Ofertas de Bônus - iGaming Brasil

## Ranking: Do Mais Fácil ao Mais Difícil

| Casa | Oferta | Rollover | Odds Mín | Validade | Dep. Mín | Restrições | Score | Facilidade |
|------|--------|----------|----------|----------|----------|------------|-------|------------|
| **Betfair** | Aposta grátis de R$ 50,00 | 1x (aposta grátis) | 1.50 | 7 dias | R$ 25,00 | Todos os métodos aceitos | 🟢 85 | Muito Fácil |
| **Bet365** | 100% até R$ 200,00 | 5x o valor do bônus | 1.20 | 30 dias | R$ 30,00 | Não válido para Skrill e Neteller | 🟢 80 | Muito Fácil |
| **Betano** | 100% até R$ 500,00 | 5x (depósito + bônus) | 1.65 | 60 dias | R$ 50,00 | Todos os métodos aceitos | 🟡 70 | Fácil |
| **Sportingbet** | 100% até R$ 750,00 | 7x o valor do bônus | 2.00 | 30 dias | R$ 20,00 | Não válido para criptomoedas | 🔴 45 | Difícil |
```

## 🔧 Personalização

### Adicionar Novas Casas

Edite `tools/igaming_search.py`:

```python
ofertas_exemplo = {
    # ... ofertas existentes ...
    "nova_casa": {
        "casa": "Nova Casa",
        "oferta": "100% até R$ 300,00",
        "rollover": "5x o valor do bônus",
        # ... outros campos ...
    }
}
```

### Ajustar Critérios de Score

Edite `tools/tc_analyzer.py` na função `calculate_bonus_viability()`:

```python
# Exemplo: penalizar mais rollover alto
if "10x" in rollover_text:
    score -= 40  # Era 30, agora 40
```

## ⚙️ Configuração

### Requisitos

```bash
pip install agno>=2.3.0 openai>=1.0.0 python-dotenv loguru
```

### Variáveis de Ambiente

Crie arquivo `.env`:

```env
OPENAI_API_KEY=sua_chave_aqui
LOG_LEVEL=INFO
DEBUG_MODE=False
```

## 🔄 Integração com Web Real

Por padrão, o agente usa dados simulados. Para integrar com scraping real:

1. **Instale dependências adicionais:**

```bash
pip install playwright httpx beautifulsoup4
playwright install chromium
```

2. **Substitua a função `_search_betting_offers_async()`**:

```python
async def _search_betting_offers_async(casa: str) -> Dict[str, Any]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navegue até a página de promoções
        url = f"https://www.{casa.lower()}.com/br/promocoes"
        await page.goto(url)

        # Extraia os dados (exemplo genérico)
        oferta_text = await page.locator(".promo-title").inner_text()
        # ... mais scraping ...

        await browser.close()

        return {
            "casa": casa,
            "oferta": oferta_text,
            # ... dados extraídos ...
        }
```

## 🧪 Testes

### Teste Isolado de Tools

```python
# Testar busca
from tools.igaming_search import search_betting_offers

result = search_betting_offers("Bet365, Betano")
print(result)

# Testar análise
from tools.tc_analyzer import analyze_terms_and_conditions

analysis = analyze_terms_and_conditions(result)
print(analysis)
```

### Teste do Agente

```bash
python agents/igaming_agent.py
```

## 📝 Notas Importantes

1. **Dados Simulados**: A versão atual usa dados de exemplo. Para produção, implemente scraping real.

2. **Legalidade**: Sempre verifique se a casa de apostas opera legalmente no Brasil.

3. **Atualização**: Os termos mudam frequentemente. Implemente cache com TTL curto.

4. **Responsabilidade**: Este agente é apenas informativo. Usuários devem ler T&C oficiais.

## 🐛 Troubleshooting

### Erro: "Async function can't be used"

- ✅ As tools usam o padrão wrapper síncrono (asyncio.run)
- ✅ Use `agent.run()` (não `agent.arun()`)

### Agente não usa as tools

- Verifique se as docstrings das tools estão completas
- Confirme que as tools estão listadas no parâmetro `tools=[]`
- Use `debug_mode=True` para ver logs detalhados

### JSON Parse Error

- Verifique se está usando `json.dumps()` com `ensure_ascii=False`
- Confirme que os dados têm estrutura esperada

## 📚 Recursos

- **Documentação Agno**: Ver `README.md`
- **Guia de Tools**: Ver seção "Implementando Tools" no README principal
- **Boas Práticas**: Ver seção "Boas Práticas" no README principal

---

**Desenvolvido com Agno Framework 2.3+**

*Para dúvidas ou melhorias, consulte a documentação completa no README.md*
