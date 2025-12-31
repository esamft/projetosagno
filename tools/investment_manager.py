"""
Life OS - Gerenciador de Investimentos

Ferramentas para gestão de patrimônio e alocação de ativos.
Baseado em estratégia de rebalanceamento Macro/Micro.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from loguru import logger


# Diretório de dados
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

BUCKETS_FILE = DATA_DIR / "investment_buckets.json"
ASSETS_FILE = DATA_DIR / "assets.json"


def _load_buckets() -> List[Dict[str, Any]]:
    """Carrega buckets (classes macro) do arquivo JSON"""
    if not BUCKETS_FILE.exists():
        # Inicializar com buckets padrão
        default_buckets = [
            {
                "id": 1,
                "name": "Ações BR",
                "meta_percentual": 30.0,
                "valor_atual": 0.0,
                "valor_percentual_atual": 0.0
            },
            {
                "id": 2,
                "name": "Renda Fixa",
                "meta_percentual": 50.0,
                "valor_atual": 0.0,
                "valor_percentual_atual": 0.0
            },
            {
                "id": 3,
                "name": "Cripto",
                "meta_percentual": 10.0,
                "valor_atual": 0.0,
                "valor_percentual_atual": 0.0
            },
            {
                "id": 4,
                "name": "Internacional",
                "meta_percentual": 10.0,
                "valor_atual": 0.0,
                "valor_percentual_atual": 0.0
            }
        ]
        _save_buckets(default_buckets)
        return default_buckets

    try:
        with open(BUCKETS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar buckets: {e}")
        return []


def _save_buckets(buckets: List[Dict[str, Any]]) -> None:
    """Salva buckets no arquivo JSON"""
    try:
        with open(BUCKETS_FILE, 'w', encoding='utf-8') as f:
            json.dump(buckets, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Erro ao salvar buckets: {e}")


def _load_assets() -> List[Dict[str, Any]]:
    """Carrega ativos do arquivo JSON"""
    if not ASSETS_FILE.exists():
        # Inicializar com ativos padrão
        default_assets = [
            {
                "id": 1,
                "bucket_id": 1,
                "name": "PETR4",
                "quantity": 0,
                "price": 0.0,
                "valor_atual": 0.0,
                "meta_percentual": 40.0,  # Meta dentro do bucket
                "valor_percentual_atual": 0.0,
                "is_manual": False
            },
            {
                "id": 2,
                "bucket_id": 1,
                "name": "VALE3",
                "quantity": 0,
                "price": 0.0,
                "valor_atual": 0.0,
                "meta_percentual": 30.0,
                "valor_percentual_atual": 0.0,
                "is_manual": False
            },
            {
                "id": 3,
                "bucket_id": 1,
                "name": "WEGE3",
                "quantity": 0,
                "price": 0.0,
                "valor_atual": 0.0,
                "meta_percentual": 30.0,
                "valor_percentual_atual": 0.0,
                "is_manual": False
            },
            {
                "id": 4,
                "bucket_id": 2,
                "name": "Tesouro IPCA+",
                "quantity": 1,
                "price": 0.0,
                "valor_atual": 0.0,
                "meta_percentual": 60.0,
                "valor_percentual_atual": 0.0,
                "is_manual": True
            },
            {
                "id": 5,
                "bucket_id": 2,
                "name": "CDB",
                "quantity": 1,
                "price": 0.0,
                "valor_atual": 0.0,
                "meta_percentual": 40.0,
                "valor_percentual_atual": 0.0,
                "is_manual": True
            },
            {
                "id": 6,
                "bucket_id": 3,
                "name": "BTC",
                "quantity": 0,
                "price": 0.0,
                "valor_atual": 0.0,
                "meta_percentual": 100.0,
                "valor_percentual_atual": 0.0,
                "is_manual": False
            }
        ]
        _save_assets(default_assets)
        return default_assets

    try:
        with open(ASSETS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar ativos: {e}")
        return []


def _save_assets(assets: List[Dict[str, Any]]) -> None:
    """Salva ativos no arquivo JSON"""
    try:
        with open(ASSETS_FILE, 'w', encoding='utf-8') as f:
            json.dump(assets, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Erro ao salvar ativos: {e}")


def _recalculate_percentages():
    """Recalcula percentuais de buckets e ativos"""
    buckets = _load_buckets()
    assets = _load_assets()

    # Calcular total geral
    total_patrimonio = sum(asset["valor_atual"] for asset in assets)

    if total_patrimonio == 0:
        return buckets, assets

    # Atualizar percentuais dos buckets
    for bucket in buckets:
        bucket_total = sum(
            asset["valor_atual"]
            for asset in assets
            if asset["bucket_id"] == bucket["id"]
        )
        bucket["valor_atual"] = bucket_total
        bucket["valor_percentual_atual"] = (bucket_total / total_patrimonio * 100) if total_patrimonio > 0 else 0

    # Atualizar percentuais dos ativos dentro de cada bucket
    for bucket in buckets:
        bucket_assets = [a for a in assets if a["bucket_id"] == bucket["id"]]
        bucket_total = bucket["valor_atual"]

        for asset in bucket_assets:
            if bucket_total > 0:
                asset["valor_percentual_atual"] = (asset["valor_atual"] / bucket_total * 100)
            else:
                asset["valor_percentual_atual"] = 0

    _save_buckets(buckets)
    _save_assets(assets)

    return buckets, assets


def update_asset_balance(asset_name: str, new_balance: float) -> str:
    """
    Atualiza saldo de um ativo (para ativos manuais como Renda Fixa).

    Args:
        asset_name: Nome do ativo (ex: "Tesouro IPCA+", "CDB")
        new_balance: Novo saldo/valor total

    Returns:
        Mensagem de confirmação com novo patrimônio total
    """
    assets = _load_assets()

    # Encontrar ativo
    asset = next((a for a in assets if a["name"].lower() == asset_name.lower()), None)

    if not asset:
        return json.dumps({
            "success": False,
            "error": f"Ativo '{asset_name}' não encontrado"
        }, ensure_ascii=False)

    # Atualizar valor
    old_value = asset["valor_atual"]
    asset["valor_atual"] = new_balance
    asset["price"] = new_balance  # Para ativos manuais, price = valor total

    _save_assets(assets)

    # Recalcular percentuais
    buckets, assets = _recalculate_percentages()

    total_patrimonio = sum(a["valor_atual"] for a in assets)

    logger.info(f"✅ Saldo de {asset_name} atualizado: {old_value} → {new_balance}")

    return json.dumps({
        "success": True,
        "asset_name": asset_name,
        "old_value": old_value,
        "new_value": new_balance,
        "total_patrimonio": total_patrimonio
    }, ensure_ascii=False)


def get_portfolio_summary() -> str:
    """
    Retorna resumo completo do patrimônio.

    Returns:
        JSON com patrimônio total e distribuição por buckets
    """
    buckets, assets = _recalculate_percentages()

    total_patrimonio = sum(bucket["valor_atual"] for bucket in buckets)

    # Montar resumo por bucket
    buckets_summary = []
    for bucket in buckets:
        gap = bucket["valor_percentual_atual"] - bucket["meta_percentual"]

        buckets_summary.append({
            "name": bucket["name"],
            "valor_atual": bucket["valor_atual"],
            "percentual_atual": round(bucket["valor_percentual_atual"], 2),
            "percentual_meta": bucket["meta_percentual"],
            "gap": round(gap, 2),
            "status": "🔴 Atrasado" if gap < -5 else "🟢 Adiantado" if gap > 5 else "✅ OK"
        })

    return json.dumps({
        "total_patrimonio": total_patrimonio,
        "buckets": buckets_summary
    }, ensure_ascii=False, indent=2)


def calculate_rebalancing(aporte_amount: float) -> str:
    """
    Calcula onde alocar novo aporte usando algoritmo Double-Layer Rebalancing.

    Args:
        aporte_amount: Valor disponível para investir

    Returns:
        JSON com sugestão de alocação baseada em rebalanceamento
    """
    buckets, assets = _recalculate_percentages()

    # Análise Macro: Encontrar bucket mais atrasado
    bucket_gaps = []
    for bucket in buckets:
        gap = bucket["valor_percentual_atual"] - bucket["meta_percentual"]
        bucket_gaps.append({
            "bucket": bucket,
            "gap": gap
        })

    # Ordenar por gap (menor primeiro = mais atrasado)
    bucket_gaps.sort(key=lambda x: x["gap"])

    if not bucket_gaps:
        return json.dumps({
            "success": False,
            "error": "Nenhum bucket configurado"
        })

    target_bucket = bucket_gaps[0]["bucket"]
    target_bucket_gap = bucket_gaps[0]["gap"]

    # Análise Micro: Dentro do bucket, encontrar ativo mais atrasado
    bucket_assets = [a for a in assets if a["bucket_id"] == target_bucket["id"]]

    asset_gaps = []
    for asset in bucket_assets:
        gap = asset["valor_percentual_atual"] - asset["meta_percentual"]
        asset_gaps.append({
            "asset": asset,
            "gap": gap
        })

    # Ordenar por gap (menor primeiro = mais atrasado)
    asset_gaps.sort(key=lambda x: x["gap"])

    if not asset_gaps:
        return json.dumps({
            "success": False,
            "error": f"Nenhum ativo no bucket {target_bucket['name']}"
        })

    target_asset = asset_gaps[0]["asset"]
    target_asset_gap = asset_gaps[0]["gap"]

    logger.info(f"💡 Rebalanceamento: {aporte_amount} → {target_bucket['name']} → {target_asset['name']}")

    return json.dumps({
        "success": True,
        "aporte_amount": aporte_amount,
        "macro_analysis": {
            "target_bucket": target_bucket["name"],
            "current_percentage": round(target_bucket["valor_percentual_atual"], 2),
            "target_percentage": target_bucket["meta_percentual"],
            "gap": round(target_bucket_gap, 2),
            "reasoning": f"Bucket mais atrasado (-{abs(round(target_bucket_gap, 2))}%)"
        },
        "micro_analysis": {
            "target_asset": target_asset["name"],
            "current_percentage": round(target_asset["valor_percentual_atual"], 2),
            "target_percentage": target_asset["meta_percentual"],
            "gap": round(target_asset_gap, 2),
            "reasoning": f"Ativo mais atrasado dentro do bucket (-{abs(round(target_asset_gap, 2))}%)"
        },
        "recommendation": {
            "action": "BUY",
            "asset": target_asset["name"],
            "amount": aporte_amount
        }
    }, ensure_ascii=False, indent=2)


def update_asset_price(asset_name: str, new_price: float, quantity: Optional[float] = None) -> str:
    """
    Atualiza preço de um ativo (para ações/cripto).

    Args:
        asset_name: Nome do ativo (ex: "PETR4", "BTC")
        new_price: Novo preço unitário
        quantity: Nova quantidade (opcional, mantém a anterior se não informado)

    Returns:
        Mensagem de confirmação
    """
    assets = _load_assets()

    # Encontrar ativo
    asset = next((a for a in assets if a["name"].lower() == asset_name.lower()), None)

    if not asset:
        return json.dumps({
            "success": False,
            "error": f"Ativo '{asset_name}' não encontrado"
        })

    # Atualizar preço
    asset["price"] = new_price

    # Atualizar quantidade se fornecida
    if quantity is not None:
        asset["quantity"] = quantity

    # Recalcular valor atual
    asset["valor_atual"] = asset["quantity"] * asset["price"]

    _save_assets(assets)

    # Recalcular percentuais
    _recalculate_percentages()

    logger.info(f"✅ {asset_name} atualizado: {asset['quantity']} × R${new_price} = R${asset['valor_atual']}")

    return json.dumps({
        "success": True,
        "asset_name": asset_name,
        "quantity": asset["quantity"],
        "price": new_price,
        "valor_atual": asset["valor_atual"]
    }, ensure_ascii=False)


def get_asset_details(asset_name: Optional[str] = None) -> str:
    """
    Retorna detalhes de um ativo específico ou todos os ativos.

    Args:
        asset_name: Nome do ativo (opcional, retorna todos se não informado)

    Returns:
        JSON com detalhes do(s) ativo(s)
    """
    buckets, assets = _recalculate_percentages()

    if asset_name:
        # Buscar ativo específico
        asset = next((a for a in assets if a["name"].lower() == asset_name.lower()), None)

        if not asset:
            return json.dumps({
                "success": False,
                "error": f"Ativo '{asset_name}' não encontrado"
            })

        # Encontrar bucket
        bucket = next((b for b in buckets if b["id"] == asset["bucket_id"]), None)

        return json.dumps({
            "success": True,
            "asset": {
                "name": asset["name"],
                "bucket": bucket["name"] if bucket else "N/A",
                "quantity": asset["quantity"],
                "price": asset["price"],
                "valor_atual": asset["valor_atual"],
                "percentual_atual": round(asset["valor_percentual_atual"], 2),
                "percentual_meta": asset["meta_percentual"],
                "is_manual": asset["is_manual"]
            }
        }, ensure_ascii=False, indent=2)

    # Retornar todos os ativos agrupados por bucket
    result = {}
    for bucket in buckets:
        bucket_assets = [a for a in assets if a["bucket_id"] == bucket["id"]]
        result[bucket["name"]] = [
            {
                "name": a["name"],
                "valor_atual": a["valor_atual"],
                "percentual_atual": round(a["valor_percentual_atual"], 2),
                "percentual_meta": a["meta_percentual"]
            }
            for a in bucket_assets
        ]

    return json.dumps(result, ensure_ascii=False, indent=2)
