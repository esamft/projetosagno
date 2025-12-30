"""
Teste das tools do agente iGaming sem necessidade de API key
"""
import json
from loguru import logger

# Configurar logger
logger.remove()
logger.add(lambda msg: print(msg, end=""), colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")

print("\n" + "="*80)
print("🎰 TESTE DAS FERRAMENTAS DO AGENTE iGAMING")
print("="*80 + "\n")

# Teste 1: Listar principais casas
print("📋 TESTE 1: Obtendo lista de casas de apostas brasileiras")
print("-" * 80)

from tools.igaming_search import get_major_betting_houses

casas_json = get_major_betting_houses()
casas_data = json.loads(casas_json)

print(f"✅ Encontradas {casas_data['total']} casas de apostas:")
for casa in casas_data['casas'][:5]:  # Mostra apenas 5
    print(f"  {casa['ranking']}. {casa['nome']} - Status: {casa['status']}")

# Teste 2: Buscar ofertas
print("\n📊 TESTE 2: Buscando ofertas de bônus")
print("-" * 80)

from tools.igaming_search import search_betting_offers

ofertas_json = search_betting_offers("Bet365, Betano, Sportingbet, Betfair, Betway")
ofertas_data = json.loads(ofertas_json)

print(f"✅ Coletadas {ofertas_data['total_casas']} ofertas:")
for i, oferta in enumerate(ofertas_data['ofertas'], 1):
    if 'error' not in oferta:
        print(f"  {i}. {oferta['casa']}: {oferta['oferta']}")

# Teste 3: Analisar T&C
print("\n🔍 TESTE 3: Analisando Termos e Condições")
print("-" * 80)

from tools.tc_analyzer import analyze_terms_and_conditions

analise_json = analyze_terms_and_conditions(ofertas_json)
analise_data = json.loads(analise_json)

print(f"✅ Analisadas {analise_data['total_analisadas']} ofertas:")
for oferta in analise_data['ofertas'][:3]:  # Top 3
    analise = oferta['analise']
    print(f"\n  🏆 {oferta['casa']}")
    print(f"     Oferta: {oferta['oferta']}")
    print(f"     Score: {analise['score']}/100 - {analise['facilidade']}")
    if analise['avisos']:
        print(f"     Avisos: {', '.join(analise['avisos'])}")

# Teste 4: Formatar tabela
print("\n📈 TESTE 4: Gerando tabela comparativa")
print("-" * 80)

from tools.tc_analyzer import format_comparative_table

tabela = format_comparative_table(analise_json)

print("\n" + tabela)

print("\n" + "="*80)
print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
print("="*80 + "\n")

print("💡 PRÓXIMOS PASSOS:")
print("  1. Configure a API key da OpenAI no arquivo .env")
print("  2. Execute: python igaming_main.py")
print("  3. O agente usará as tools de forma autônoma!\n")
