"""
Tool para buscar ofertas de casas de apostas no Brasil
"""
import asyncio
import json
from typing import Dict, List, Any
from loguru import logger


async def _search_betting_offers_async(casa: str) -> Dict[str, Any]:
    """
    Busca ofertas de uma casa de apostas específica

    Args:
        casa: Nome da casa de apostas

    Returns:
        Dados da oferta encontrada
    """
    # Simulação de busca web - em produção, usar Playwright ou API real
    # Por enquanto, retorna dados estruturados de exemplo

    ofertas_exemplo = {
        "bet365": {
            "casa": "Bet365",
            "oferta": "100% até R$ 200,00",
            "rollover": "5x o valor do bônus",
            "odds_minimas": "1.20",
            "validade": "30 dias",
            "deposito_minimo": "R$ 30,00",
            "restricoes_pagamento": "Não válido para Skrill e Neteller"
        },
        "betano": {
            "casa": "Betano",
            "oferta": "100% até R$ 500,00",
            "rollover": "5x (depósito + bônus)",
            "odds_minimas": "1.65",
            "validade": "60 dias",
            "deposito_minimo": "R$ 50,00",
            "restricoes_pagamento": "Todos os métodos aceitos"
        },
        "sportingbet": {
            "casa": "Sportingbet",
            "oferta": "100% até R$ 750,00",
            "rollover": "7x o valor do bônus",
            "odds_minimas": "2.00",
            "validade": "30 dias",
            "deposito_minimo": "R$ 20,00",
            "restricoes_pagamento": "Não válido para criptomoedas"
        },
        "betfair": {
            "casa": "Betfair",
            "oferta": "Aposta grátis de R$ 50,00",
            "rollover": "1x (aposta grátis)",
            "odds_minimas": "1.50",
            "validade": "7 dias",
            "deposito_minimo": "R$ 25,00",
            "restricoes_pagamento": "Todos os métodos aceitos"
        },
        "betway": {
            "casa": "Betway",
            "oferta": "100% até R$ 200,00 + R$ 50 grátis",
            "rollover": "10x (depósito + bônus)",
            "odds_minimas": "1.75",
            "validade": "90 dias",
            "deposito_minimo": "R$ 30,00",
            "restricoes_pagamento": "Não válido para PayPal"
        },
    }

    casa_lower = casa.lower().strip()

    # Simula delay de network
    await asyncio.sleep(0.5)

    if casa_lower in ofertas_exemplo:
        logger.info(f"Oferta encontrada para {casa}")
        return ofertas_exemplo[casa_lower]
    else:
        logger.warning(f"Nenhuma oferta encontrada para {casa}")
        return {
            "casa": casa,
            "oferta": "Não encontrado",
            "error": "Casa de apostas não mapeada"
        }


def search_betting_offers(casas: str) -> str:
    """
    Busca ofertas de bônus de múltiplas casas de apostas brasileiras

    Use esta ferramenta para coletar informações sobre promoções ativas
    de casas de apostas que operam legalmente no Brasil.

    Args:
        casas: Lista de casas de apostas separadas por vírgula
               (ex: "Bet365, Betano, Sportingbet")

    Returns:
        JSON string com dados estruturados das ofertas encontradas
    """
    try:
        # Parseia a lista de casas
        lista_casas = [c.strip() for c in casas.split(",")]
        logger.info(f"Buscando ofertas para: {lista_casas}")

        # Busca assíncrona para todas as casas
        async def buscar_todas():
            tasks = [_search_betting_offers_async(casa) for casa in lista_casas]
            return await asyncio.gather(*tasks)

        resultados = asyncio.run(buscar_todas())

        return json.dumps({
            "status": "success",
            "total_casas": len(resultados),
            "ofertas": resultados
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao buscar ofertas: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False, indent=2)


def get_major_betting_houses() -> str:
    """
    Retorna lista das principais casas de apostas operando no Brasil

    Use esta ferramenta para obter a lista atualizada das casas
    de apostas mais relevantes no mercado brasileiro.

    Returns:
        JSON string com lista de casas de apostas
    """
    casas = [
        {"nome": "Bet365", "ranking": 1, "status": "legal"},
        {"nome": "Betano", "ranking": 2, "status": "legal"},
        {"nome": "Sportingbet", "ranking": 3, "status": "legal"},
        {"nome": "Betfair", "ranking": 4, "status": "legal"},
        {"nome": "Betway", "ranking": 5, "status": "legal"},
        {"nome": "1xBet", "ranking": 6, "status": "legal"},
        {"nome": "Rivalo", "ranking": 7, "status": "legal"},
        {"nome": "KTO", "ranking": 8, "status": "legal"},
    ]

    return json.dumps({
        "status": "success",
        "total": len(casas),
        "casas": casas,
        "nota": "Lista atualizada com casas operando legalmente no Brasil"
    }, ensure_ascii=False, indent=2)
