"""
Ferramentas de Relatórios de Custos

Gera relatórios mensais, análises e insights sobre custos.
"""
import json
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger


# Caminho do arquivo de dados
DATA_DIR = Path(__file__).parent.parent / "data"
COSTS_FILE = DATA_DIR / "costs.json"


def _load_costs():
    """Carrega custos do arquivo JSON"""
    try:
        if COSTS_FILE.exists():
            with open(COSTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar custos: {e}")
    return []


def generate_monthly_report(month: Optional[int] = None, year: Optional[int] = None) -> str:
    """
    Gera relatório completo mensal de custos

    Use esta ferramenta quando o usuário solicitar um relatório mensal,
    balanço, fechamento ou análise completa de um mês.

    O relatório inclui:
    - Total gasto no mês
    - Gastos por categoria com percentuais
    - Principais despesas (top 5)
    - Métodos de pagamento utilizados
    - Média diária de gastos
    - Comparação com mês anterior
    - Insights e alertas

    Args:
        month: Mês (1-12) do relatório (opcional, padrão: mês atual)
        year: Ano do relatório (opcional, padrão: ano atual)

    Returns:
        Relatório completo em formato JSON estruturado
    """
    try:
        costs = _load_costs()

        # Usar mês/ano atual se não especificado
        now = datetime.now()
        month = month or now.month
        year = year or now.year

        # Filtrar custos do mês
        monthly_costs = []
        for cost in costs:
            try:
                cost_date = datetime.strptime(cost["date"], "%d/%m/%Y")
                if cost_date.month == month and cost_date.year == year:
                    monthly_costs.append(cost)
            except:
                continue

        if not monthly_costs:
            return json.dumps({
                "status": "success",
                "message": "Nenhum custo registrado para este período.",
                "period": f"{month:02d}/{year}",
                "data": None
            }, ensure_ascii=False, indent=2)

        # --- ANÁLISES ---

        # 1. Total gasto
        total_spent = sum(c.get("amount", 0) for c in monthly_costs)
        total_items = len(monthly_costs)

        # 2. Gastos por categoria
        categories = {}
        for cost in monthly_costs:
            cat = cost.get("category", "Outros")
            if cat not in categories:
                categories[cat] = {"total": 0, "count": 0}
            categories[cat]["total"] += cost.get("amount", 0)
            categories[cat]["count"] += 1

        # Ordenar categorias por valor
        sorted_categories = dict(sorted(
            categories.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        ))

        categories_summary = {}
        for cat, data in sorted_categories.items():
            percentage = (data["total"] / total_spent * 100) if total_spent > 0 else 0
            categories_summary[cat] = {
                "total": f"R$ {data['total']:.2f}",
                "count": data["count"],
                "percentage": f"{percentage:.1f}%"
            }

        # 3. Top 5 maiores despesas
        top_expenses = sorted(
            monthly_costs,
            key=lambda x: x.get("amount", 0),
            reverse=True
        )[:5]

        top_5 = [{
            "description": exp.get("description"),
            "amount": f"R$ {exp.get('amount', 0):.2f}",
            "category": exp.get("category"),
            "date": exp.get("date")
        } for exp in top_expenses]

        # 4. Métodos de pagamento
        payment_methods = {}
        for cost in monthly_costs:
            method = cost.get("payment_method", "Não especificado")
            if method not in payment_methods:
                payment_methods[method] = {"total": 0, "count": 0}
            payment_methods[method]["total"] += cost.get("amount", 0)
            payment_methods[method]["count"] += 1

        payment_summary = {}
        for method, data in payment_methods.items():
            payment_summary[method] = {
                "total": f"R$ {data['total']:.2f}",
                "count": data["count"]
            }

        # 5. Média diária
        days_in_month = (datetime(year, month % 12 + 1, 1) - timedelta(days=1)).day if month < 12 else 31
        daily_average = total_spent / days_in_month

        # 6. Comparação com mês anterior
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1

        prev_monthly_costs = []
        for cost in costs:
            try:
                cost_date = datetime.strptime(cost["date"], "%d/%m/%Y")
                if cost_date.month == prev_month and cost_date.year == prev_year:
                    prev_monthly_costs.append(cost)
            except:
                continue

        prev_total = sum(c.get("amount", 0) for c in prev_monthly_costs)
        variation = total_spent - prev_total
        variation_percentage = (variation / prev_total * 100) if prev_total > 0 else 0

        # 7. Insights e Alertas
        insights = []

        # Categoria com maior gasto
        if sorted_categories:
            top_category = list(sorted_categories.keys())[0]
            top_category_amount = sorted_categories[top_category]["total"]
            top_category_perc = (top_category_amount / total_spent * 100) if total_spent > 0 else 0
            insights.append(
                f"📊 {top_category} representa {top_category_perc:.1f}% dos seus gastos (R$ {top_category_amount:.2f})"
            )

        # Alerta de aumento de gastos
        if variation_percentage > 10:
            insights.append(
                f"⚠️ Seus gastos aumentaram {variation_percentage:.1f}% em relação ao mês anterior!"
            )
        elif variation_percentage < -10:
            insights.append(
                f"✅ Você economizou {abs(variation_percentage):.1f}% em relação ao mês anterior!"
            )

        # Alerta de gastos concentrados
        if len(sorted_categories) > 0:
            top_3_total = sum(data["total"] for data in list(sorted_categories.values())[:3])
            if (top_3_total / total_spent * 100) > 70:
                insights.append(
                    f"💡 70% dos seus gastos estão concentrados em apenas 3 categorias"
                )

        # --- MONTAR RELATÓRIO FINAL ---
        report = {
            "status": "success",
            "period": f"{month:02d}/{year}",
            "summary": {
                "total_spent": f"R$ {total_spent:.2f}",
                "total_items": total_items,
                "daily_average": f"R$ {daily_average:.2f}",
                "comparison_previous_month": {
                    "previous_total": f"R$ {prev_total:.2f}",
                    "variation": f"R$ {variation:.2f}",
                    "variation_percentage": f"{variation_percentage:+.1f}%"
                }
            },
            "categories": categories_summary,
            "top_5_expenses": top_5,
            "payment_methods": payment_summary,
            "insights": insights
        }

        logger.info(f"📊 Relatório mensal gerado para {month:02d}/{year}")

        return json.dumps(report, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Erro ao gerar relatório: {str(e)}"
        }, ensure_ascii=False, indent=2)


def get_expense_trends(months: int = 3) -> str:
    """
    Analisa tendências de gastos nos últimos meses

    Use esta ferramenta quando o usuário quiser ver evolução,
    tendências ou padrões de gastos ao longo do tempo.

    Args:
        months: Número de meses para analisar (padrão: 3 meses)

    Returns:
        Análise de tendências em formato JSON
    """
    try:
        costs = _load_costs()
        now = datetime.now()

        # Coletar dados dos últimos N meses
        monthly_data = {}

        for i in range(months):
            target_date = now - timedelta(days=30 * i)
            month = target_date.month
            year = target_date.year
            period_key = f"{month:02d}/{year}"

            monthly_costs = []
            for cost in costs:
                try:
                    cost_date = datetime.strptime(cost["date"], "%d/%m/%Y")
                    if cost_date.month == month and cost_date.year == year:
                        monthly_costs.append(cost)
                except:
                    continue

            total = sum(c.get("amount", 0) for c in monthly_costs)
            monthly_data[period_key] = {
                "total": total,
                "count": len(monthly_costs),
                "average": total / len(monthly_costs) if len(monthly_costs) > 0 else 0
            }

        # Analisar tendência
        totals = [data["total"] for data in monthly_data.values()]
        if len(totals) >= 2:
            trend = "crescente" if totals[0] > totals[-1] else "decrescente" if totals[0] < totals[-1] else "estável"
        else:
            trend = "insuficiente para análise"

        # Formatar resultado
        formatted_data = {}
        for period, data in monthly_data.items():
            formatted_data[period] = {
                "total": f"R$ {data['total']:.2f}",
                "count": data["count"],
                "average_per_item": f"R$ {data['average']:.2f}"
            }

        result = {
            "status": "success",
            "analyzed_months": months,
            "trend": trend,
            "monthly_breakdown": formatted_data
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ Erro ao analisar tendências: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Erro ao analisar tendências: {str(e)}"
        }, ensure_ascii=False, indent=2)


def export_to_dashboard_json() -> str:
    """
    Exporta dados formatados para painel de custos

    Use esta ferramenta quando precisar exportar os dados para
    visualização em dashboard ou painel externo.

    Returns:
        Dados formatados para dashboard em JSON
    """
    try:
        costs = _load_costs()
        now = datetime.now()

        # Dados do mês atual
        current_month_costs = []
        for cost in costs:
            try:
                cost_date = datetime.strptime(cost["date"], "%d/%m/%Y")
                if cost_date.month == now.month and cost_date.year == now.year:
                    current_month_costs.append(cost)
            except:
                continue

        # Preparar dados para dashboard
        dashboard_data = {
            "last_update": now.isoformat(),
            "current_month": {
                "period": f"{now.month:02d}/{now.year}",
                "total": sum(c.get("amount", 0) for c in current_month_costs),
                "items_count": len(current_month_costs),
                "categories": {},
                "recent_expenses": []
            },
            "all_time": {
                "total": sum(c.get("amount", 0) for c in costs),
                "items_count": len(costs),
                "first_record": costs[0].get("date") if costs else None,
                "last_record": costs[-1].get("date") if costs else None
            }
        }

        # Categorias do mês atual
        categories = {}
        for cost in current_month_costs:
            cat = cost.get("category", "Outros")
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += cost.get("amount", 0)

        dashboard_data["current_month"]["categories"] = {
            k: f"R$ {v:.2f}" for k, v in categories.items()
        }

        # Últimas 10 despesas
        recent = sorted(costs, key=lambda x: x.get("created_at", ""), reverse=True)[:10]
        dashboard_data["current_month"]["recent_expenses"] = [
            {
                "description": c.get("description"),
                "amount": f"R$ {c.get('amount', 0):.2f}",
                "category": c.get("category"),
                "date": c.get("date")
            }
            for c in recent
        ]

        logger.info("📤 Dados exportados para dashboard")

        return json.dumps(dashboard_data, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ Erro ao exportar para dashboard: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Erro ao exportar dados: {str(e)}"
        }, ensure_ascii=False, indent=2)
