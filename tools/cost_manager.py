"""
Ferramentas de Gerenciamento de Custos

Este módulo contém ferramentas para adicionar, listar, categorizar e gerenciar
custos mensais através de conversas no WhatsApp.
"""
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
from loguru import logger


# Caminho do arquivo de dados
DATA_DIR = Path(__file__).parent.parent / "data"
COSTS_FILE = DATA_DIR / "costs.json"


def _ensure_data_file() -> None:
    """Garante que o arquivo de dados existe"""
    DATA_DIR.mkdir(exist_ok=True)
    if not COSTS_FILE.exists():
        COSTS_FILE.write_text("[]")


def _load_costs() -> List[Dict[str, Any]]:
    """Carrega custos do arquivo JSON"""
    _ensure_data_file()
    try:
        with open(COSTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar custos: {e}")
        return []


def _save_costs(costs: List[Dict[str, Any]]) -> None:
    """Salva custos no arquivo JSON"""
    _ensure_data_file()
    with open(COSTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(costs, f, ensure_ascii=False, indent=2)


def add_cost(
    description: str,
    amount: float,
    category: str,
    date: Optional[str] = None,
    payment_method: Optional[str] = None,
    notes: Optional[str] = None
) -> str:
    """
    Adiciona um novo custo ao sistema

    Use esta ferramenta quando o usuário mencionar uma despesa, gasto ou custo.
    A ferramenta registra automaticamente data/hora e organiza por categorias.

    Categorias disponíveis:
    - Alimentação
    - Transporte
    - Moradia
    - Saúde
    - Lazer
    - Educação
    - Serviços
    - Compras
    - Outros

    Args:
        description: Descrição do custo (ex: "Almoço no restaurante")
        amount: Valor em reais (ex: 45.50)
        category: Categoria do custo (ex: "Alimentação")
        date: Data no formato DD/MM/YYYY (opcional, usa data atual se não informado)
        payment_method: Forma de pagamento (ex: "Cartão de Crédito", "PIX", "Dinheiro")
        notes: Observações adicionais sobre o custo

    Returns:
        Mensagem de confirmação em JSON com os dados registrados
    """
    try:
        costs = _load_costs()

        # Se data não fornecida, usa data atual
        if not date:
            date = datetime.now().strftime("%d/%m/%Y")

        # Cria novo custo
        new_cost = {
            "id": len(costs) + 1,
            "description": description,
            "amount": float(amount),
            "category": category,
            "date": date,
            "payment_method": payment_method or "Não especificado",
            "notes": notes or "",
            "created_at": datetime.now().isoformat()
        }

        costs.append(new_cost)
        _save_costs(costs)

        logger.info(f"✅ Custo adicionado: {description} - R$ {amount}")

        return json.dumps({
            "status": "success",
            "message": "Custo registrado com sucesso!",
            "data": {
                "id": new_cost["id"],
                "description": description,
                "amount": f"R$ {amount:.2f}",
                "category": category,
                "date": date,
                "payment_method": new_cost["payment_method"]
            }
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ Erro ao adicionar custo: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Erro ao registrar custo: {str(e)}"
        }, ensure_ascii=False, indent=2)


def list_costs(
    month: Optional[int] = None,
    year: Optional[int] = None,
    category: Optional[str] = None
) -> str:
    """
    Lista custos filtrados por mês, ano e/ou categoria

    Use esta ferramenta quando o usuário quiser ver seus gastos, despesas ou custos.
    Pode filtrar por período (mês/ano) e/ou categoria específica.

    Args:
        month: Mês (1-12) para filtrar (opcional)
        year: Ano (ex: 2025) para filtrar (opcional)
        category: Categoria específica para filtrar (opcional)

    Returns:
        Lista de custos em formato JSON organizado
    """
    try:
        costs = _load_costs()

        if not costs:
            return json.dumps({
                "status": "success",
                "message": "Nenhum custo registrado ainda.",
                "total_costs": 0,
                "data": []
            }, ensure_ascii=False, indent=2)

        # Filtrar por mês/ano se especificado
        if month or year:
            filtered_costs = []
            for cost in costs:
                try:
                    cost_date = datetime.strptime(cost["date"], "%d/%m/%Y")
                    if month and cost_date.month != month:
                        continue
                    if year and cost_date.year != year:
                        continue
                    filtered_costs.append(cost)
                except:
                    continue
            costs = filtered_costs

        # Filtrar por categoria se especificado
        if category:
            costs = [c for c in costs if c.get("category", "").lower() == category.lower()]

        # Calcular total
        total = sum(c.get("amount", 0) for c in costs)

        return json.dumps({
            "status": "success",
            "message": f"Encontrados {len(costs)} custo(s)",
            "total_costs": len(costs),
            "total_amount": f"R$ {total:.2f}",
            "filters": {
                "month": month,
                "year": year,
                "category": category
            },
            "data": costs
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ Erro ao listar custos: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Erro ao listar custos: {str(e)}"
        }, ensure_ascii=False, indent=2)


def get_categories_summary(month: Optional[int] = None, year: Optional[int] = None) -> str:
    """
    Gera resumo de gastos por categoria

    Use esta ferramenta quando o usuário quiser ver um resumo, análise ou
    total de gastos por categoria (ex: "quanto gastei com alimentação?").

    Args:
        month: Mês (1-12) para filtrar (opcional, padrão: mês atual)
        year: Ano para filtrar (opcional, padrão: ano atual)

    Returns:
        Resumo organizado por categoria em formato JSON
    """
    try:
        costs = _load_costs()

        # Usar mês/ano atual se não especificado
        now = datetime.now()
        month = month or now.month
        year = year or now.year

        # Filtrar por período
        filtered_costs = []
        for cost in costs:
            try:
                cost_date = datetime.strptime(cost["date"], "%d/%m/%Y")
                if cost_date.month == month and cost_date.year == year:
                    filtered_costs.append(cost)
            except:
                continue

        # Agrupar por categoria
        categories = {}
        for cost in filtered_costs:
            cat = cost.get("category", "Outros")
            if cat not in categories:
                categories[cat] = {
                    "total": 0,
                    "count": 0,
                    "items": []
                }
            categories[cat]["total"] += cost.get("amount", 0)
            categories[cat]["count"] += 1
            categories[cat]["items"].append({
                "description": cost.get("description"),
                "amount": cost.get("amount"),
                "date": cost.get("date")
            })

        # Ordenar por total (maior para menor)
        sorted_categories = dict(sorted(
            categories.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        ))

        total_geral = sum(cat["total"] for cat in categories.values())

        # Formatar resultado
        result = {
            "status": "success",
            "period": f"{month:02d}/{year}",
            "total_amount": f"R$ {total_geral:.2f}",
            "categories": {}
        }

        for cat_name, cat_data in sorted_categories.items():
            percentage = (cat_data["total"] / total_geral * 100) if total_geral > 0 else 0
            result["categories"][cat_name] = {
                "total": f"R$ {cat_data['total']:.2f}",
                "count": cat_data["count"],
                "percentage": f"{percentage:.1f}%",
                "items": cat_data["items"]
            }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ Erro ao gerar resumo: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Erro ao gerar resumo: {str(e)}"
        }, ensure_ascii=False, indent=2)


def delete_cost(cost_id: int) -> str:
    """
    Remove um custo do sistema

    Use esta ferramenta quando o usuário quiser apagar, deletar ou
    remover um registro de custo.

    Args:
        cost_id: ID do custo a ser removido

    Returns:
        Mensagem de confirmação
    """
    try:
        costs = _load_costs()

        # Encontrar e remover custo
        original_length = len(costs)
        costs = [c for c in costs if c.get("id") != cost_id]

        if len(costs) == original_length:
            return json.dumps({
                "status": "error",
                "message": f"Custo com ID {cost_id} não encontrado."
            }, ensure_ascii=False, indent=2)

        _save_costs(costs)

        logger.info(f"✅ Custo ID {cost_id} removido")

        return json.dumps({
            "status": "success",
            "message": f"Custo ID {cost_id} removido com sucesso!"
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ Erro ao deletar custo: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Erro ao deletar custo: {str(e)}"
        }, ensure_ascii=False, indent=2)
