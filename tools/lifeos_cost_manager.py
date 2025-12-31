"""
Life OS - Gerenciamento de Custos com Parcelamento e Tipos de Pagamento

Ferramentas para registro de transações com suporte a:
- Parcelamento (impacto em meses futuros)
- Tipos de pagamento (Pix, Crédito, Débito)
- Tetos orçamentários por categoria
"""
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger


# Caminhos de dados
DATA_DIR = Path(__file__).parent.parent / "data"
TRANSACTIONS_FILE = DATA_DIR / "transactions.json"
BUDGETS_FILE = DATA_DIR / "budgets.json"


def _ensure_data_files() -> None:
    """Garante que os arquivos de dados existem"""
    DATA_DIR.mkdir(exist_ok=True)
    if not TRANSACTIONS_FILE.exists():
        TRANSACTIONS_FILE.write_text("[]")
    if not BUDGETS_FILE.exists():
        # Tetos padrão (exemplo)
        default_budgets = {
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
        BUDGETS_FILE.write_text(json.dumps(default_budgets, ensure_ascii=False, indent=2))


def _load_transactions() -> List[Dict[str, Any]]:
    """Carrega transações"""
    _ensure_data_files()
    try:
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar transações: {e}")
        return []


def _save_transactions(transactions: List[Dict[str, Any]]) -> None:
    """Salva transações"""
    _ensure_data_files()
    with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(transactions, f, ensure_ascii=False, indent=2)


def _load_budgets() -> Dict[str, Any]:
    """Carrega tetos orçamentários"""
    _ensure_data_files()
    try:
        with open(BUDGETS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar budgets: {e}")
        return {"global_limit": 5000.00, "categories": {}}


def add_transaction(
    description: str,
    amount: float,
    category: str,
    payment_type: str,  # "Pix", "Crédito", "Débito"
    date: Optional[str] = None,
    installments: int = 1,  # Número de parcelas (padrão: 1 = à vista)
    notes: Optional[str] = None
) -> str:
    """
    Adiciona uma transação financeira ao Life OS

    Use esta ferramenta quando o usuário mencionar um gasto.

    IMPORTANTE - Tipos de Pagamento:
    - "Pix": Pagamento instantâneo
    - "Débito": Débito em conta corrente
    - "Crédito": Cartão de crédito (pode ser parcelado)

    IMPORTANTE - Parcelamento:
    - Se o usuário disser "R$ 300 em 3x", use: amount=300, installments=3
    - Isso criará 3 registros: 1 para cada mês (R$ 100 cada)
    - O total da compra é distribuído ao longo dos meses

    Args:
        description: Descrição concisa (ex: "Almoço", "Uber", "Netflix")
        amount: Valor TOTAL da compra (não da parcela)
        category: Categoria do gasto
        payment_type: "Pix", "Crédito" ou "Débito"
        date: Data no formato DD/MM/YYYY (opcional, usa hoje se não informado)
        installments: Número de parcelas (padrão: 1)
        notes: Observações adicionais

    Returns:
        JSON com confirmação e análise de impacto no orçamento
    """
    try:
        transactions = _load_transactions()
        budgets = _load_budgets()

        # Data base
        if not date:
            base_date = datetime.now()
            date = base_date.strftime("%d/%m/%Y")
        else:
            base_date = datetime.strptime(date, "%d/%m/%Y")

        # Calcular valor da parcela
        installment_amount = amount / installments

        # Criar registros de parcelas
        created_transactions = []
        for i in range(installments):
            # Calcular data de cada parcela
            parcel_date = base_date + timedelta(days=30 * i)

            transaction = {
                "id": len(transactions) + i + 1,
                "description": description,
                "total_amount": amount,  # Valor total da compra
                "installment_amount": installment_amount,  # Valor desta parcela
                "installment_number": i + 1,  # Parcela X de Y
                "total_installments": installments,
                "category": category,
                "payment_type": payment_type,
                "date": parcel_date.strftime("%d/%m/%Y"),
                "month_year": parcel_date.strftime("%m/%Y"),
                "notes": notes or "",
                "created_at": datetime.now().isoformat()
            }

            transactions.append(transaction)
            created_transactions.append(transaction)

        _save_transactions(transactions)

        # Análise de impacto no mês atual
        current_month = datetime.now().strftime("%m/%Y")
        month_transactions = [t for t in transactions if t.get("month_year") == current_month]

        # Total gasto no mês
        month_total = sum(t.get("installment_amount", 0) for t in month_transactions)

        # Gastos por categoria no mês
        category_totals = {}
        for t in month_transactions:
            cat = t.get("category", "Outros")
            category_totals[cat] = category_totals.get(cat, 0) + t.get("installment_amount", 0)

        # Verificar alertas
        global_limit = budgets.get("global_limit", 5000)
        category_limits = budgets.get("categories", {})

        alerts = []

        # Alerta global
        global_percent = (month_total / global_limit * 100) if global_limit > 0 else 0
        if global_percent > 100:
            alerts.append(f"🚨 VERMELHO: Orçamento global estourado ({global_percent:.0f}%)")
        elif global_percent > 80:
            alerts.append(f"⚠️ AMARELO: Orçamento global em {global_percent:.0f}%")

        # Alertas por categoria
        for cat, spent in category_totals.items():
            limit = category_limits.get(cat, 0)
            if limit > 0:
                percent = (spent / limit * 100)
                if percent > 100:
                    alerts.append(f"🚨 {cat}: {percent:.0f}% do teto usado (Vermelho)")
                elif percent > 80:
                    alerts.append(f"⚠️ {cat}: {percent:.0f}% do teto usado (Amarelo)")

        # Formatar resposta no padrão Life OS
        installment_text = f" em {installments}x" if installments > 1 else ""

        response = {
            "status": "success",
            "message": f"✅ **Salvo:** {description} (R$ {amount:.2f}) em {category}{installment_text}.",
            "data": {
                "description": description,
                "total_amount": f"R$ {amount:.2f}",
                "installment_amount": f"R$ {installment_amount:.2f}",
                "installments": installments,
                "category": category,
                "payment_type": payment_type,
                "date": date
            },
            "budget_status": {
                "current_month": current_month,
                "total_spent": f"R$ {month_total:.2f}",
                "remaining": f"R$ {(global_limit - month_total):.2f}",
                "global_limit": f"R$ {global_limit:.2f}",
                "percent_used": f"{global_percent:.1f}%"
            },
            "alerts": alerts if alerts else ["✅ Todos os orçamentos estão saudáveis"]
        }

        logger.info(f"✅ Transação registrada: {description} - R$ {amount:.2f} ({installments}x)")

        return json.dumps(response, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ Erro ao adicionar transação: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Erro ao registrar transação: {str(e)}"
        }, ensure_ascii=False, indent=2)


def get_month_summary(month: Optional[int] = None, year: Optional[int] = None) -> str:
    """
    Obtém resumo financeiro de um mês específico

    Args:
        month: Mês (1-12)
        year: Ano (ex: 2025)

    Returns:
        JSON com resumo do mês
    """
    try:
        transactions = _load_transactions()
        budgets = _load_budgets()

        # Usar mês/ano atual se não especificado
        now = datetime.now()
        month = month or now.month
        year = year or now.year
        month_key = f"{month:02d}/{year}"

        # Filtrar transações do mês
        month_transactions = [t for t in transactions if t.get("month_year") == month_key]

        if not month_transactions:
            return json.dumps({
                "status": "success",
                "message": "Nenhuma transação neste mês",
                "month": month_key,
                "data": None
            }, ensure_ascii=False, indent=2)

        # Calcular totais
        total_spent = sum(t.get("installment_amount", 0) for t in month_transactions)

        # Por categoria
        category_totals = {}
        for t in month_transactions:
            cat = t.get("category", "Outros")
            category_totals[cat] = category_totals.get(cat, 0) + t.get("installment_amount", 0)

        # Por tipo de pagamento
        payment_totals = {}
        for t in month_transactions:
            ptype = t.get("payment_type", "Outros")
            payment_totals[ptype] = payment_totals.get(ptype, 0) + t.get("installment_amount", 0)

        # Calcular alertas
        global_limit = budgets.get("global_limit", 5000)
        category_limits = budgets.get("categories", {})

        alerts = []
        for cat, spent in category_totals.items():
            limit = category_limits.get(cat, 0)
            if limit > 0:
                percent = (spent / limit * 100)
                if percent > 100:
                    alerts.append({"category": cat, "percent": percent, "status": "red"})
                elif percent > 80:
                    alerts.append({"category": cat, "percent": percent, "status": "yellow"})

        return json.dumps({
            "status": "success",
            "month": month_key,
            "summary": {
                "total_spent": total_spent,
                "global_limit": global_limit,
                "remaining": global_limit - total_spent,
                "percent_used": (total_spent / global_limit * 100) if global_limit > 0 else 0
            },
            "by_category": category_totals,
            "by_payment_type": payment_totals,
            "alerts": alerts,
            "transaction_count": len(month_transactions)
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ Erro ao gerar resumo: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Erro ao gerar resumo: {str(e)}"
        }, ensure_ascii=False, indent=2)


def get_future_commitments(months_ahead: int = 3) -> str:
    """
    Analisa compromissos futuros (parcelas a vencer)

    Use quando o usuário perguntar sobre "mês que vem", "futuro", "posso gastar?"

    Args:
        months_ahead: Número de meses à frente para analisar

    Returns:
        JSON com análise de compromissos futuros
    """
    try:
        transactions = _load_transactions()
        budgets = _load_budgets()

        now = datetime.now()
        future_analysis = []

        for i in range(1, months_ahead + 1):
            future_date = now + timedelta(days=30 * i)
            month_key = future_date.strftime("%m/%Y")

            # Filtrar parcelas que caem neste mês
            future_transactions = [t for t in transactions if t.get("month_year") == month_key]

            # Separar parcelas já comprometidas (de compras anteriores)
            committed = [t for t in future_transactions if t.get("installment_number", 1) > 1]
            committed_total = sum(t.get("installment_amount", 0) for t in committed)

            # Total geral
            total = sum(t.get("installment_amount", 0) for t in future_transactions)

            global_limit = budgets.get("global_limit", 5000)
            percent_committed = (committed_total / global_limit * 100) if global_limit > 0 else 0

            # Principais vilões (maiores parcelas)
            top_villains = sorted(
                committed,
                key=lambda x: x.get("installment_amount", 0),
                reverse=True
            )[:3]

            future_analysis.append({
                "month": month_key,
                "already_committed": committed_total,
                "percent_of_budget": percent_committed,
                "total_projected": total,
                "top_commitments": [
                    {
                        "description": v.get("description"),
                        "amount": v.get("installment_amount"),
                        "installment": f"{v.get('installment_number')}/{v.get('total_installments')}"
                    }
                    for v in top_villains
                ]
            })

        return json.dumps({
            "status": "success",
            "future_months": future_analysis,
            "global_limit": budgets.get("global_limit", 5000)
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ Erro ao analisar futuro: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Erro ao analisar compromissos futuros: {str(e)}"
        }, ensure_ascii=False, indent=2)
