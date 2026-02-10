"""
Ferramenta de scoring de relacionamentos.

Calcula a saude de cada relacionamento com base em frequencia
de contato, qualidade das interacoes, tempo sem comunicacao
e prioridade do perfil do usuario.
"""
import json
from datetime import datetime, timedelta
from loguru import logger

from storage.crm_store import (
    load_contacts,
    load_interactions,
    load_profile,
    get_interactions_for_contact,
)
from config.crm_profiles import get_profile_defaults


def _calculate_relationship_score(contact: dict, interactions: list[dict], profile: dict) -> dict:
    """Calcula o score de um relacionamento individual"""
    now = datetime.now()
    categoria = contact.get("categoria", "outro")

    # Frequencia ideal baseada no perfil
    tipo_perfil = profile.get("tipo", "custom")
    defaults = get_profile_defaults(tipo_perfil)
    freq_ideal = defaults.get("frequencia_contato_dias", {}).get(categoria, 30)

    # Ordenar interacoes por data
    sorted_ints = sorted(interactions, key=lambda x: x.get("data", ""), reverse=True)

    # Dias sem contato
    if sorted_ints:
        try:
            last_date = datetime.fromisoformat(sorted_ints[0]["data"])
            dias_sem_contato = (now - last_date).days
        except (ValueError, KeyError):
            dias_sem_contato = 999
    else:
        dias_sem_contato = 999

    # Interacoes no ultimo mes
    um_mes_atras = now - timedelta(days=30)
    ints_ultimo_mes = [
        i for i in interactions
        if _parse_date(i.get("data", "")) and _parse_date(i.get("data", "")) > um_mes_atras
    ]

    # Sentimento medio
    sentimentos = [i.get("sentimento", "neutro") for i in interactions if i.get("sentimento")]
    sent_scores = {"positivo": 1, "neutro": 0, "negativo": -1}
    if sentimentos:
        avg_sent = sum(sent_scores.get(s, 0) for s in sentimentos) / len(sentimentos)
        if avg_sent > 0.3:
            sentimento_medio = "positivo"
        elif avg_sent < -0.3:
            sentimento_medio = "negativo"
        else:
            sentimento_medio = "neutro"
    else:
        sentimento_medio = "neutro"

    # Calcular score (0-100)
    score = 50.0  # Base

    # Fator frequencia: +30 se dentro do ideal, -30 se muito acima
    if dias_sem_contato <= freq_ideal:
        score += 30
    elif dias_sem_contato <= freq_ideal * 2:
        score += 15
    elif dias_sem_contato <= freq_ideal * 3:
        score -= 5
    else:
        score -= 25

    # Fator volume: +20 se tem interacoes recentes
    if len(ints_ultimo_mes) >= 4:
        score += 20
    elif len(ints_ultimo_mes) >= 2:
        score += 10
    elif len(ints_ultimo_mes) == 1:
        score += 5
    else:
        score -= 10

    # Fator sentimento: +10/-10
    if sentimento_medio == "positivo":
        score += 10
    elif sentimento_medio == "negativo":
        score -= 10

    # Fator variedade de interacoes
    tipos = set(i.get("tipo", "") for i in ints_ultimo_mes)
    if len(tipos) >= 3:
        score += 10
    elif len(tipos) >= 2:
        score += 5

    # Limitar entre 0 e 100
    score = max(0, min(100, score))

    # Determinar forca
    if score >= 80:
        forca = "forte"
    elif score >= 60:
        forca = "moderado"
    elif score >= 40:
        forca = "fraco"
    elif score >= 20:
        forca = "esfriando"
    else:
        forca = "perdido"

    # Tendencia (compara ultimo mes com mes anterior)
    dois_meses_atras = now - timedelta(days=60)
    ints_mes_anterior = [
        i for i in interactions
        if _parse_date(i.get("data", ""))
        and dois_meses_atras < _parse_date(i.get("data", "")) <= um_mes_atras
    ]
    if len(ints_ultimo_mes) > len(ints_mes_anterior):
        tendencia = "melhorando"
    elif len(ints_ultimo_mes) < len(ints_mes_anterior):
        tendencia = "piorando"
    else:
        tendencia = "estavel"

    # Prioridade baseada no perfil
    cats_prioritarias = defaults.get("categorias_prioritarias", [])
    if categoria in cats_prioritarias[:2]:
        prioridade = "alta"
    elif categoria in cats_prioritarias:
        prioridade = "media"
    else:
        prioridade = "baixa"

    # Se score baixo e prioridade alta, elevar para critica
    if score < 40 and prioridade == "alta":
        prioridade = "critica"

    # Gerar alerta
    alerta = None
    if dias_sem_contato > freq_ideal * 3:
        alerta = f"Sem contato ha {dias_sem_contato} dias! Frequencia ideal: {freq_ideal} dias"
    elif dias_sem_contato > freq_ideal * 2:
        alerta = f"Contato atrasado: {dias_sem_contato} dias sem comunicacao"
    elif sentimento_medio == "negativo":
        alerta = "Relacionamento com sentimento predominantemente negativo"

    # Gerar sugestao
    sugestao = None
    if dias_sem_contato > freq_ideal * 2:
        sugestao = f"Entre em contato com {contact['nome']} o mais breve possivel"
    elif dias_sem_contato > freq_ideal:
        sugestao = f"Hora de falar com {contact['nome']}. Que tal uma mensagem ou ligacao?"
    elif tendencia == "piorando":
        sugestao = f"Frequencia de contato com {contact['nome']} esta diminuindo. Mantenha o ritmo!"
    elif sentimento_medio == "negativo":
        sugestao = f"Considere uma conversa mais cuidadosa com {contact['nome']} para melhorar o relacionamento"

    return {
        "contato_id": contact["id"],
        "contato_nome": contact["nome"],
        "categoria": categoria,
        "score": round(score, 1),
        "forca": forca,
        "dias_sem_contato": dias_sem_contato,
        "total_interacoes": len(interactions),
        "interacoes_ultimo_mes": len(ints_ultimo_mes),
        "sentimento_medio": sentimento_medio,
        "tendencia": tendencia,
        "alerta": alerta,
        "sugestao": sugestao,
        "prioridade": prioridade,
        "frequencia_ideal_dias": freq_ideal,
    }


def _parse_date(date_str: str):
    """Parse ISO date string para datetime, retorna None se falhar"""
    try:
        return datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None


def crm_score_all_relationships() -> str:
    """
    Calcula o score de saude de TODOS os relacionamentos do CRM.

    Analisa cada contato ativo e retorna um ranking completo com:
    - Score de 0 a 100
    - Forca do relacionamento
    - Dias sem contato
    - Tendencia (melhorando, estavel, piorando)
    - Alertas e sugestoes

    Returns:
        JSON com ranking de todos os relacionamentos ordenados por prioridade
    """
    try:
        contacts = load_contacts()
        interactions = load_interactions()
        profile = load_profile()

        active_contacts = [c for c in contacts if c.get("ativo", True)]

        if not active_contacts:
            return json.dumps({
                "status": "success",
                "message": "Nenhum contato cadastrado ainda. Adicione contatos primeiro!",
                "scores": [],
            }, ensure_ascii=False, indent=2)

        scores = []
        for contact in active_contacts:
            contact_interactions = [
                i for i in interactions if i["contato_id"] == contact["id"]
            ]
            score = _calculate_relationship_score(contact, contact_interactions, profile)
            scores.append(score)

        # Ordenar: critica > alta > media > baixa, depois por score ascendente
        priority_order = {"critica": 0, "alta": 1, "media": 2, "baixa": 3}
        scores.sort(key=lambda x: (priority_order.get(x["prioridade"], 4), x["score"]))

        # Resumo
        alertas = [s for s in scores if s.get("alerta")]
        criticos = [s for s in scores if s["prioridade"] == "critica"]

        return json.dumps({
            "status": "success",
            "total_contatos": len(scores),
            "contatos_criticos": len(criticos),
            "total_alertas": len(alertas),
            "score_medio": round(sum(s["score"] for s in scores) / len(scores), 1),
            "scores": scores,
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao calcular scores: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


def crm_score_contact(contact_id: str) -> str:
    """
    Calcula o score de saude de um relacionamento especifico.

    Faz uma analise detalhada de um contato individual.

    Args:
        contact_id: ID do contato para analisar

    Returns:
        JSON com score detalhado do relacionamento
    """
    try:
        from storage.crm_store import get_contact, get_interactions_for_contact

        contact = get_contact(contact_id)
        if not contact:
            return json.dumps({
                "status": "error",
                "message": f"Contato nao encontrado: {contact_id}"
            }, ensure_ascii=False)

        interactions = get_interactions_for_contact(contact_id)
        profile = load_profile()

        score = _calculate_relationship_score(contact, interactions, profile)

        return json.dumps({
            "status": "success",
            "score": score,
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao calcular score: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


def crm_get_neglected_contacts(days_threshold: str = "30") -> str:
    """
    Retorna contatos que estao sendo negligenciados.

    Identifica contatos que nao recebem atencao ha mais tempo
    que o ideal para sua categoria, ordenados por urgencia.

    Args:
        days_threshold: Minimo de dias sem contato para considerar negligenciado (padrao: 30)

    Returns:
        JSON com lista de contatos negligenciados e sugestoes
    """
    try:
        threshold = int(days_threshold) if days_threshold.strip() else 30
        contacts = load_contacts()
        interactions = load_interactions()
        profile = load_profile()

        active_contacts = [c for c in contacts if c.get("ativo", True)]
        neglected = []

        for contact in active_contacts:
            contact_interactions = [
                i for i in interactions if i["contato_id"] == contact["id"]
            ]
            score_data = _calculate_relationship_score(contact, contact_interactions, profile)

            if score_data["dias_sem_contato"] >= threshold:
                neglected.append(score_data)

        neglected.sort(key=lambda x: x["dias_sem_contato"], reverse=True)

        return json.dumps({
            "status": "success",
            "threshold_dias": threshold,
            "total_negligenciados": len(neglected),
            "contatos": neglected,
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao buscar negligenciados: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)
