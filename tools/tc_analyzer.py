"""
Tool para análise de Termos e Condições de ofertas de iGaming
"""
import json
from typing import Dict, Any, List
from loguru import logger


def calculate_bonus_viability(oferta_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula a viabilidade real de um bônus baseado nos T&C

    Args:
        oferta_data: Dicionário com dados da oferta

    Returns:
        Análise de viabilidade
    """
    score = 100  # Começa com score perfeito
    avisos = []

    # Analisa rollover
    rollover_text = str(oferta_data.get("rollover", "")).lower()
    if "10x" in rollover_text or "15x" in rollover_text:
        score -= 30
        avisos.append("Rollover muito alto (≥10x)")
    elif "7x" in rollover_text or "8x" in rollover_text:
        score -= 20
        avisos.append("Rollover alto (7-8x)")
    elif "5x" in rollover_text or "6x" in rollover_text:
        score -= 10
        avisos.append("Rollover moderado (5-6x)")

    # Analisa odds mínimas
    try:
        odds = float(oferta_data.get("odds_minimas", "1.0").replace(",", "."))
        if odds >= 2.0:
            score -= 25
            avisos.append("Odds mínimas altas (≥2.0)")
        elif odds >= 1.70:
            score -= 15
            avisos.append("Odds mínimas moderadas (1.70-2.0)")
    except:
        pass

    # Analisa validade
    validade = str(oferta_data.get("validade", "")).lower()
    if "7 dias" in validade or "dias" in validade and int(validade.split()[0]) <= 7:
        score -= 20
        avisos.append("Prazo muito curto (≤7 dias)")
    elif "30 dias" in validade:
        score -= 5
        avisos.append("Prazo justo (30 dias)")

    # Analisa restrições
    restricoes = str(oferta_data.get("restricoes_pagamento", "")).lower()
    if "não válido" in restricoes or "exceto" in restricoes:
        score -= 10
        avisos.append("Possui restrições de pagamento")

    # Classificação
    if score >= 80:
        classificacao = "Excelente"
        facilidade = "Muito Fácil"
    elif score >= 60:
        classificacao = "Bom"
        facilidade = "Fácil"
    elif score >= 40:
        classificacao = "Regular"
        facilidade = "Moderado"
    else:
        classificacao = "Difícil"
        facilidade = "Difícil"

    return {
        "score": score,
        "classificacao": classificacao,
        "facilidade": facilidade,
        "avisos": avisos
    }


def analyze_terms_and_conditions(ofertas_json: str) -> str:
    """
    Analisa os termos e condições de ofertas de bônus

    Use esta ferramenta para analisar as "letras miúdas" e calcular
    a viabilidade real dos bônus oferecidos.

    Args:
        ofertas_json: JSON string com dados das ofertas a analisar

    Returns:
        JSON string com análise detalhada incluindo score de viabilidade
    """
    try:
        data = json.loads(ofertas_json)

        if "ofertas" not in data:
            return json.dumps({
                "status": "error",
                "message": "Formato inválido: esperado campo 'ofertas'"
            }, ensure_ascii=False)

        ofertas_analisadas = []

        for oferta in data["ofertas"]:
            if "error" in oferta:
                continue

            analise = calculate_bonus_viability(oferta)

            oferta_completa = {
                **oferta,
                "analise": analise
            }

            ofertas_analisadas.append(oferta_completa)

        # Ordena por score (melhores primeiro)
        ofertas_analisadas.sort(key=lambda x: x["analise"]["score"], reverse=True)

        logger.info(f"Analisadas {len(ofertas_analisadas)} ofertas")

        return json.dumps({
            "status": "success",
            "total_analisadas": len(ofertas_analisadas),
            "ofertas": ofertas_analisadas,
            "ranking": "Ordenado do mais fácil ao mais difícil"
        }, ensure_ascii=False, indent=2)

    except json.JSONDecodeError as e:
        logger.error(f"Erro ao parsear JSON: {e}")
        return json.dumps({
            "status": "error",
            "message": "JSON inválido fornecido"
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro na análise: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)


def format_comparative_table(analise_json: str) -> str:
    """
    Formata os dados analisados em uma tabela comparativa markdown

    Use esta ferramenta para gerar a tabela final de comparação
    das ofertas, ordenada por facilidade de cumprimento.

    Args:
        analise_json: JSON string com ofertas já analisadas

    Returns:
        Tabela markdown formatada
    """
    try:
        data = json.loads(analise_json)

        if data.get("status") != "success":
            return f"❌ Erro: {data.get('message', 'Dados inválidos')}"

        ofertas = data.get("ofertas", [])

        if not ofertas:
            return "⚠️ Nenhuma oferta encontrada para formatar"

        # Cabeçalho da tabela
        table = "# 📊 Comparativo de Ofertas de Bônus - iGaming Brasil\n\n"
        table += "## Ranking: Do Mais Fácil ao Mais Difícil\n\n"

        table += "| Casa | Oferta | Rollover | Odds Mín | Validade | Dep. Mín | Restrições | Score | Facilidade |\n"
        table += "|------|--------|----------|----------|----------|----------|------------|-------|------------|\n"

        # Linhas da tabela
        for oferta in ofertas:
            analise = oferta.get("analise", {})

            casa = oferta.get("casa", "N/A")
            oferta_desc = oferta.get("oferta", "N/A")
            rollover = oferta.get("rollover", "N/A")
            odds = oferta.get("odds_minimas", "N/A")
            validade = oferta.get("validade", "N/A")
            deposito = oferta.get("deposito_minimo", "N/A")
            restricoes = oferta.get("restricoes_pagamento", "N/A")
            score = analise.get("score", 0)
            facilidade = analise.get("facilidade", "N/A")

            # Emoji baseado no score
            if score >= 80:
                emoji = "🟢"
            elif score >= 60:
                emoji = "🟡"
            else:
                emoji = "🔴"

            table += f"| **{casa}** | {oferta_desc} | {rollover} | {odds} | {validade} | {deposito} | {restricoes} | {emoji} {score} | {facilidade} |\n"

        # Legenda
        table += "\n### 📌 Legenda\n"
        table += "- 🟢 **Score 80+**: Muito Fácil - Rollover baixo, odds justas, prazo adequado\n"
        table += "- 🟡 **Score 60-79**: Moderado - Alguns requisitos desafiadores\n"
        table += "- 🔴 **Score <60**: Difícil - Rollover alto, odds exigentes ou prazo curto\n\n"

        # Avisos importantes
        table += "### ⚠️ Avisos Importantes\n\n"
        for i, oferta in enumerate(ofertas, 1):
            analise = oferta.get("analise", {})
            avisos = analise.get("avisos", [])
            if avisos:
                table += f"**{oferta.get('casa')}**:\n"
                for aviso in avisos:
                    table += f"  - {aviso}\n"
                table += "\n"

        table += "\n---\n"
        table += "*Análise gerada automaticamente. Sempre verifique os T&C oficiais antes de ativar qualquer bônus.*\n"

        return table

    except Exception as e:
        logger.error(f"Erro ao formatar tabela: {e}")
        return f"❌ Erro ao formatar tabela: {str(e)}"
